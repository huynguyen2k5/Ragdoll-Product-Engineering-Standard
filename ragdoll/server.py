"""Authenticated local HTTP adapter for Ragdoll Core."""

from __future__ import annotations

import argparse
import json
import logging
import re
import signal
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

from ragdoll.core import RagdollCore, RagdollError
from ragdoll.core.errors import SecurityPolicyError, ValidationError
from ragdoll.history.security import sanitize

from . import __version__
from .config import Settings
from .local_security import get_or_create_api_token, origin_is_local, token_matches
from .observability import configure_logging, log_event
from .storage.migrations import ensure_home_schema

_PROJECT_RE = re.compile(r"^/v1/projects/([^/]+)$")
_CONTEXT_RE = re.compile(r"^/v1/projects/([^/]+)/context$")
_CONTEXT_GENERATE_RE = re.compile(r"^/v1/projects/([^/]+)/context/generate$")
_CONTEXT_VALIDATE_RE = re.compile(r"^/v1/projects/([^/]+)/context/validate$")
_CONTEXT_COMPILE_RE = re.compile(r"^/v1/projects/([^/]+)/context/compile$")
_CONVERSATIONS_RE = re.compile(r"^/v1/projects/([^/]+)/conversations$")
_CONVERSATION_RE = re.compile(r"^/v1/projects/([^/]+)/conversations/([^/]+)$")
_EVENTS_RE = re.compile(r"^/v1/projects/([^/]+)/conversations/([^/]+)/events$")
_VERIFY_RE = re.compile(r"^/v1/projects/([^/]+)/conversations/([^/]+)/verify$")
_SEARCH_RE = re.compile(r"^/v1/projects/([^/]+)/history/search$")
_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")


class RagdollHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 128

    def __init__(self, address: tuple[str, int], settings: Settings):
        ensure_home_schema(settings.home)
        self.settings = settings
        self.api_token = get_or_create_api_token(settings.home, settings.api_token)
        self.core = RagdollCore(settings)
        self.core.bootstrap()
        self.logger = configure_logging(settings.log_level)
        super().__init__(address, RagdollHandler)


class RagdollHandler(BaseHTTPRequestHandler):
    server_version = f"RagdollLocal/{__version__}"
    sys_version = ""

    @property
    def ragdoll_server(self) -> RagdollHTTPServer:
        return self.server  # type: ignore[return-value]

    @property
    def settings(self) -> Settings:
        return self.ragdoll_server.settings

    @property
    def core(self) -> RagdollCore:
        return self.ragdoll_server.core

    def log_message(self, format: str, *args: object) -> None:
        # Access logs are emitted once per request in _dispatch with request IDs.
        return

    def _request_id(self) -> str:
        supplied = (self.headers.get("X-Request-ID") or "").strip()
        if supplied and _REQUEST_ID_RE.fullmatch(supplied):
            return supplied
        return f"req_{uuid4().hex}"

    def _security_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("Pragma", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")

    def _json(self, status: int, value: object, *, request_id: str) -> None:
        payload = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("X-Request-ID", request_id)
        self._security_headers()
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    def _error(self, error: RagdollError, *, request_id: str) -> None:
        safe = sanitize(error.as_dict(request_id))
        self._json(error.http_status, safe, request_id=request_id)

    def _authorized(self) -> None:
        if not origin_is_local(self.headers.get("Origin")):
            raise SecurityPolicyError("Browser origin is not local", code="origin_denied")
        if not token_matches(self.ragdoll_server.api_token, self.headers.get("Authorization")):
            error = RagdollError("Missing or invalid local API token", "unauthorized", 401)
            raise error

    def _read_json(self) -> dict[str, Any]:
        if self.headers.get("Transfer-Encoding"):
            raise ValidationError("Transfer-Encoding is not supported")
        raw_length = self.headers.get("Content-Length")
        try:
            length = int(raw_length or "0")
        except ValueError:
            raise ValidationError("invalid Content-Length") from None
        if length < 0 or length > self.settings.max_request_bytes:
            raise ValidationError(
                "request body is too large",
                details={"max_request_bytes": self.settings.max_request_bytes},
            )
        if length == 0:
            return {}
        content_type = (self.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            raise RagdollError("Content-Type must be application/json", "unsupported_media_type", 415)
        raw = self.rfile.read(length)
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValidationError("request body must be a JSON object") from None
        if not isinstance(value, dict):
            raise ValidationError("request body must be a JSON object")
        return value

    def _query_int(self, query: dict[str, list[str]], key: str, default: int, minimum: int, maximum: int) -> int:
        raw = query.get(key, [str(default)])[0]
        try:
            value = int(raw)
        except ValueError:
            raise ValidationError(f"query parameter {key} must be an integer") from None
        if value < minimum or value > maximum:
            raise ValidationError(f"query parameter {key} must be between {minimum} and {maximum}")
        return value

    def _dispatch(self) -> None:
        request_id = self._request_id()
        started = time.monotonic()
        status = 500
        parsed = urlsplit(self.path)
        path = parsed.path.rstrip("/") or "/"
        try:
            if len(path) > 4096:
                raise ValidationError("request path is too long")
            method = "GET" if self.command == "HEAD" else self.command
            if method == "GET" and path == "/v1/health":
                status = 200
                self._json(status, self.core.health(), request_id=request_id)
                return
            if method == "GET" and path == "/v1/ready":
                ready = self.core.readiness()
                status = 200 if ready.get("ok") else 503
                self._json(status, ready, request_id=request_id)
                return

            self._authorized()
            if self.command in {"PUT", "PATCH"}:
                raise RagdollError(
                    "Method not allowed",
                    "method_not_allowed",
                    405,
                    {"allow": ["GET", "HEAD", "POST", "DELETE", "OPTIONS"]},
                )
            query = parse_qs(parsed.query, keep_blank_values=False)
            body = self._read_json() if method in {"POST", "DELETE"} else {}
            status, payload = self._route(method, path, query, body)
            self._json(status, payload, request_id=request_id)
        except RagdollError as exc:
            status = exc.http_status
            self._error(exc, request_id=request_id)
        except FileNotFoundError as exc:
            error = RagdollError(str(exc), "not_found", 404)
            status = 404
            self._error(error, request_id=request_id)
        except ValueError as exc:
            error = ValidationError(str(exc))
            status = 400
            self._error(error, request_id=request_id)
        except Exception as exc:
            status = 500
            log_event(
                self.ragdoll_server.logger,
                logging.ERROR,
                "request_failed",
                request_id=request_id,
                method=self.command,
                path=path,
                status=500,
                exception_type=type(exc).__name__,
            )
            error = RagdollError("Internal Ragdoll error", "internal_error", 500)
            self._error(error, request_id=request_id)
        finally:
            duration_ms = round((time.monotonic() - started) * 1000, 2)
            log_event(
                self.ragdoll_server.logger,
                logging.INFO,
                "request_completed",
                request_id=request_id,
                method=self.command,
                path=path,
                status=status,
                duration_ms=duration_ms,
            )

    def _route(
        self,
        method: str,
        path: str,
        query: dict[str, list[str]],
        body: dict[str, Any],
    ) -> tuple[int, object]:
        if method == "GET":
            if path == "/v1/status":
                return 200, self.core.status()
            if path == "/v1/providers":
                return 200, self.core.providers()
            if path == "/v1/projects":
                return 200, self.core.projects()
            if path == "/v1/history/index/status":
                return 200, self.core.history_index_status()
            match = _PROJECT_RE.match(path)
            if match:
                return 200, self.core.project(match.group(1))
            match = _CONVERSATIONS_RE.match(path)
            if match:
                limit = self._query_int(query, "limit", 100, 1, 1000)
                before = query.get("before", [None])[0]
                return 200, self.core.conversations(match.group(1), limit=limit, before=before)
            match = _CONVERSATION_RE.match(path)
            if match:
                return 200, self.core.conversation(match.group(1), match.group(2))
            match = _EVENTS_RE.match(path)
            if match:
                after_seq = self._query_int(query, "after_seq", 0, 0, 2_000_000_000)
                limit = self._query_int(query, "limit", 200, 1, 1000)
                return 200, self.core.events(match.group(1), match.group(2), after_seq=after_seq, limit=limit)
            match = _VERIFY_RE.match(path)
            if match:
                return 200, self.core.verify_conversation(match.group(1), match.group(2))
            match = _CONTEXT_RE.match(path)
            if match:
                return 200, self.core.context_manifest(match.group(1))

        if method == "POST":
            if path == "/v1/projects":
                return 201, self.core.register_project(body)
            # rebuild-index is a blocking O(N) operation proportional to history size.
            # Callers should not expect it to complete instantly on large datasets.
            if path == "/v1/history/rebuild-index":
                return 200, self.core.rebuild_history_index()
            if path == "/v1/chat":
                return 200, self.core.chat(body)
            match = _CONVERSATIONS_RE.match(path)
            if match:
                return 201, self.core.create_conversation(match.group(1), body)
            match = _EVENTS_RE.match(path)
            if match:
                return 201, self.core.append_event(match.group(1), match.group(2), body)
            match = _SEARCH_RE.match(path)
            if match:
                return 200, self.core.history_search(match.group(1), body)
            match = _CONTEXT_GENERATE_RE.match(path)
            if match:
                return 201, self.core.generate_context(match.group(1), body)
            match = _CONTEXT_VALIDATE_RE.match(path)
            if match:
                return 200, self.core.validate_context(match.group(1))
            match = _CONTEXT_COMPILE_RE.match(path)
            if match:
                return 200, self.core.compile_context(match.group(1), body)

        if method == "DELETE":
            match = _PROJECT_RE.match(path)
            if match:
                return 200, self.core.purge_project(match.group(1), body)

        raise RagdollError("Unknown endpoint", "not_found", 404)

    def do_OPTIONS(self) -> None:
        request_id = self._request_id()
        started = time.monotonic()
        self.send_response(204)
        self.send_header("Allow", "GET, HEAD, POST, DELETE, OPTIONS")
        self.send_header("X-Request-ID", request_id)
        self._security_headers()
        self.end_headers()
        duration_ms = round((time.monotonic() - started) * 1000, 2)
        log_event(
            self.ragdoll_server.logger,
            logging.INFO,
            "request_completed",
            request_id=request_id,
            method="OPTIONS",
            path=self.path,
            status=204,
            duration_ms=duration_ms,
        )

    def do_GET(self) -> None:
        self._dispatch()

    def do_HEAD(self) -> None:
        self._dispatch()

    def do_POST(self) -> None:
        self._dispatch()

    def do_DELETE(self) -> None:
        self._dispatch()

    def do_PUT(self) -> None:
        self._dispatch()

    def do_PATCH(self) -> None:
        self._dispatch()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local Ragdoll HTTP backend")
    parser.add_argument("--env-file")
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    return parser


def serve(settings: Settings) -> None:
    settings.home.mkdir(parents=True, exist_ok=True)
    server = RagdollHTTPServer((settings.host, settings.port), settings)
    logger = server.logger
    shutdown_started = threading.Event()

    def request_shutdown(signum: int, frame: object) -> None:
        _ = frame
        if shutdown_started.is_set():
            return
        shutdown_started.set()
        log_event(logger, logging.INFO, "shutdown_requested", signal=signum)
        threading.Thread(target=server.shutdown, daemon=True).start()

    previous_handlers: dict[int, Any] = {}
    if threading.current_thread() is threading.main_thread():
        for signum in (signal.SIGINT, signal.SIGTERM):
            previous_handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, request_shutdown)

    log_event(
        logger,
        logging.INFO,
        "server_started",
        bind=f"{settings.host}:{settings.port}",
        home=str(settings.home),
        telemetry=False,
        cloud_sync=False,
    )
    try:
        server.serve_forever(poll_interval=0.25)
    finally:
        server.server_close()
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)
        log_event(logger, logging.INFO, "server_stopped")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings.load(args.env_file)
    settings = settings.with_server_override(host=args.host, port=args.port)
    serve(settings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

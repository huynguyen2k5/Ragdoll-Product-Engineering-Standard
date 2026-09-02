"""Transport-neutral Ragdoll application core.

CLI, HTTP, and future MCP adapters must call this layer instead of duplicating
project/history/context business rules.
"""

from __future__ import annotations

import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ragdoll.config import Settings
from ragdoll.context_runtime import (
    compile_runtime_context,
    generate_context_for_project,
    read_context_manifest,
    validate_context_for_project,
)
from ragdoll.history.identity import get_project, list_projects, register_project
from ragdoll.history.maintenance import get_index_status, rebuild_index
from ragdoll.history.retrieval import compile_evidence, comprehensive_search, focused_search, forensic_search
from ragdoll.history.store import (
    append_event,
    iter_conversation_events,
    list_conversations,
    purge_project,
    read_conversation,
    start_conversation,
    verify_conversation,
)
from ragdoll.providers import ProviderError, provider_status
from ragdoll.service import chat_once
from ragdoll.storage.migrations import CURRENT_HOME_SCHEMA, ensure_home_schema, read_home_schema_version

from .errors import ConflictError, NotFoundError, ProviderGatewayError, ValidationError
from .validation import bounded_int, optional_bool, optional_int, optional_string, required_string


class RagdollCore:
    """Single application boundary shared by all transports."""

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def home(self) -> Path:
        return self.settings.home

    def bootstrap(self) -> dict[str, Any]:
        result = ensure_home_schema(self.home)
        return {
            "home_schema": result.current_version,
            "migrated": result.changed,
            "previous_home_schema": result.previous_version,
        }

    def health(self) -> dict[str, Any]:
        from ragdoll import __version__

        return {"ok": True, "service": "ragdoll-local", "version": __version__}

    def readiness(self) -> dict[str, Any]:
        current_version = read_home_schema_version(self.home)
        writable = os.access(self.home, os.W_OK)
        index = get_index_status(self.home)
        ok = writable and index.get("integrity") == "ok" and current_version == CURRENT_HOME_SCHEMA
        # This payload is safe for the unauthenticated loopback readiness probe:
        # never expose filesystem paths or project metadata here.
        safe_index = {
            key: index.get(key)
            for key in ("index_schema_version", "current_index_schema_version", "fts5", "integrity", "dirty")
        }
        return {
            "ok": ok,
            "home_writable": writable,
            "home_schema": current_version,
            "history_index": safe_index,
            "provider_required": False,
        }

    def status(self) -> dict[str, Any]:
        from ragdoll import __version__

        return {
            "ok": True,
            "version": __version__,
            "python": sys.version.split()[0],
            "settings": self.settings.safe_status(),
            "history_index": get_index_status(self.home),
        }

    def providers(self) -> dict[str, Any]:
        return {"providers": provider_status(self.settings)}

    def register_project(self, body: dict[str, Any]) -> dict[str, Any]:
        raw_path = optional_string(body, "path", max_length=32_000) or "."
        workspace = Path(raw_path).expanduser().resolve()
        name = optional_string(body, "name", max_length=500)
        try:
            return register_project(workspace, name, self.home)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

    def projects(self) -> dict[str, Any]:
        return {"projects": list_projects(self.home)}

    def project(self, project_id: str) -> dict[str, Any]:
        try:
            return get_project(project_id, self.home)
        except (KeyError, ValueError) as exc:
            raise NotFoundError(f"unknown project: {project_id}") from exc

    def conversations(self, project_id: str, *, limit: int = 100, before: str | None = None) -> dict[str, Any]:
        self.project(project_id)
        return {"conversations": list_conversations(self.home, project_id, limit=limit, before=before)}

    def conversation(self, project_id: str, conversation_id: str) -> dict[str, Any]:
        self.project(project_id)
        try:
            return read_conversation(self.home, project_id, conversation_id)
        except (FileNotFoundError, ValueError) as exc:
            raise NotFoundError(f"unknown conversation: {conversation_id}") from exc

    def create_conversation(self, project_id: str, body: dict[str, Any]) -> dict[str, Any]:
        self.project(project_id)
        try:
            forked_at = optional_int(body, "forked_at_seq", minimum=1, maximum=2_000_000_000)
            return start_conversation(
                project_id,
                title=optional_string(body, "title", max_length=500) or "",
                workspace=optional_string(body, "workspace", max_length=32_000),
                ide=optional_string(body, "ide", max_length=200),
                provider=optional_string(body, "provider", max_length=100),
                parent_conversation_id=optional_string(body, "parent_conversation_id", max_length=100),
                forked_at_seq=forked_at,
                home=self.home,
            )
        except (ValueError, FileNotFoundError) as exc:
            raise ValidationError(str(exc)) from exc

    def events(
        self,
        project_id: str,
        conversation_id: str,
        *,
        after_seq: int = 0,
        limit: int = 200,
    ) -> dict[str, Any]:
        self.conversation(project_id, conversation_id)
        events = list(
            iter_conversation_events(
                self.home,
                project_id,
                conversation_id,
                after_seq=max(0, after_seq),
                limit=max(1, min(limit, 1000)),
            )
        )
        next_after_seq = int(events[-1]["seq"]) if events else after_seq
        return {"events": events, "next_after_seq": next_after_seq, "limit": max(1, min(limit, 1000))}

    def append_event(self, project_id: str, conversation_id: str, body: dict[str, Any]) -> dict[str, Any]:
        self.conversation(project_id, conversation_id)
        event_type = required_string(body, "type", max_length=200)
        payload = body.get("payload", {})
        if not isinstance(payload, dict):
            raise ValidationError("payload must be an object")
        idempotency_key = optional_string(body, "idempotency_key", max_length=200)
        try:
            return append_event(
                project_id,
                conversation_id,
                event_type,
                payload,
                idempotency_key=idempotency_key,
                home=self.home,
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

    def verify_conversation(self, project_id: str, conversation_id: str) -> dict[str, Any]:
        self.conversation(project_id, conversation_id)
        errors = verify_conversation(self.home, project_id, conversation_id)
        return {"ok": not errors, "errors": errors}

    def history_search(self, project_id: str, body: dict[str, Any]) -> dict[str, Any]:
        self.project(project_id)
        query = optional_string(body, "query", max_length=100_000) or ""
        mode = (optional_string(body, "mode", max_length=32) or "focused").lower()
        limit = bounded_int(body, "limit", default=20, minimum=1, maximum=1000)
        token_budget = bounded_int(
            body,
            "token_budget",
            default=self.settings.history_token_budget,
            minimum=200,
            maximum=100000,
        )
        filters = {
            "file_path": optional_string(body, "file_path", max_length=32_000),
            "commit_sha": optional_string(body, "commit_sha", max_length=200),
            "event_type": optional_string(body, "event_type", max_length=200),
            "conversation_id": optional_string(body, "conversation_id", max_length=100),
        }
        if mode == "comprehensive":
            results = comprehensive_search(self.home, project_id, query, limit=limit)
        elif mode == "forensic":
            results = forensic_search(self.home, project_id, query, limit=limit, **filters)
        elif mode == "focused":
            results = focused_search(self.home, project_id, query, limit=limit, **filters)
        else:
            raise ValidationError("mode must be focused, comprehensive, or forensic")
        compiled = compile_evidence(results, token_budget)
        compiled["mode"] = mode
        return compiled

    def rebuild_history_index(self) -> dict[str, Any]:
        return {"indexed_events": rebuild_index(self.home), "status": get_index_status(self.home)}

    def history_index_status(self) -> dict[str, Any]:
        return get_index_status(self.home)

    def context_manifest(self, project_id: str) -> dict[str, Any]:
        self.project(project_id)
        return read_context_manifest(self.home, project_id)

    def generate_context(self, project_id: str, body: dict[str, Any]) -> dict[str, Any]:
        self.project(project_id)
        try:
            output = generate_context_for_project(
                self.home,
                project_id,
                force=optional_bool(body, "force", default=False),
                project_name=optional_string(body, "project_name", max_length=500),
            )
        except FileExistsError as exc:
            raise ConflictError(str(exc)) from exc
        return {"context_root": str(output), "status": "DRAFT_REQUIRES_REVIEW"}

    def validate_context(self, project_id: str) -> dict[str, Any]:
        self.project(project_id)
        errors = validate_context_for_project(self.home, project_id)
        return {"ok": not errors, "errors": errors}

    def compile_context(self, project_id: str, body: dict[str, Any]) -> dict[str, Any]:
        self.project(project_id)
        prompt = required_string(body, "prompt")
        runtime = compile_runtime_context(
            home=self.home,
            project_id=project_id,
            prompt=prompt,
            project_context_token_budget=bounded_int(
                body,
                "project_context_token_budget",
                default=self.settings.project_context_token_budget,
                minimum=200,
                maximum=100000,
            ),
            history_token_budget=bounded_int(
                body,
                "history_token_budget",
                default=self.settings.history_token_budget,
                minimum=200,
                maximum=100000,
            ),
            use_project_context=optional_bool(body, "use_project_context", default=True),
            use_history=optional_bool(body, "use_history", default=True),
            history_mode=(optional_string(body, "history_mode", max_length=32) or "focused").lower(),
        )
        return asdict(runtime)

    def chat(self, body: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {
            "project_id": required_string(body, "project_id", max_length=100),
            "prompt": required_string(body, "prompt", max_length=200_000),
            "conversation_id": optional_string(body, "conversation_id", max_length=100),
            "provider": optional_string(body, "provider", max_length=100),
            "model": optional_string(body, "model", max_length=300),
            "ide": optional_string(body, "ide", max_length=200) or "ragdoll-local",
            "title": optional_string(body, "title", max_length=500),
            "idempotency_key": optional_string(body, "idempotency_key", max_length=160),
            "use_history": optional_bool(body, "use_history", default=True),
            "use_project_context": optional_bool(body, "use_project_context", default=True),
            "history_mode": (optional_string(body, "history_mode", max_length=32) or "focused").lower(),
            "history_token_budget": bounded_int(
                body, "history_token_budget", default=self.settings.history_token_budget, minimum=200, maximum=100000
            ),
            "project_context_token_budget": bounded_int(
                body, "project_context_token_budget", default=self.settings.project_context_token_budget, minimum=200, maximum=100000
            ),
            "max_output_tokens": bounded_int(
                body, "max_output_tokens", default=self.settings.max_output_tokens, minimum=64, maximum=100000
            ),
        }
        if normalized["history_mode"] not in {"focused", "comprehensive", "forensic"}:
            raise ValidationError("history_mode must be focused, comprehensive, or forensic")
        try:
            return chat_once(self.settings, normalized)
        except ProviderError as exc:
            raise ProviderGatewayError(str(exc)) from exc
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        except KeyError as exc:
            raise NotFoundError(str(exc)) from exc

    def purge_project(self, project_id: str, body: dict[str, Any]) -> dict[str, Any]:
        confirmation = required_string(body, "confirm", max_length=100)
        try:
            purge_project(self.home, project_id, confirmation)
        except FileNotFoundError as exc:
            raise NotFoundError(f"unknown project: {project_id}") from exc
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        return {"purged_project": project_id}

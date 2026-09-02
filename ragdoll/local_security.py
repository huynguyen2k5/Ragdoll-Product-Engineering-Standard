"""Security helpers for the loopback-only local API."""

from __future__ import annotations

import hmac
import secrets
from pathlib import Path
from urllib.parse import urlsplit

from .storage.atomic import atomic_write_text
from .storage.locks import exclusive_file_lock


def api_token_path(home: Path) -> Path:
    return home / "api-token"


def get_or_create_api_token(home: Path, configured: str | None = None) -> str:
    if configured:
        if len(configured) < 32:
            raise ValueError("RAGDOLL_API_TOKEN must contain at least 32 characters")
        return configured
    path = api_token_path(home)
    path.parent.mkdir(parents=True, exist_ok=True)
    with exclusive_file_lock(home / ".api-token.lock", timeout_seconds=5.0):
        if path.exists():
            token = path.read_text(encoding="utf-8", errors="replace").strip()
            if len(token) >= 32:
                return token
        token = secrets.token_urlsafe(48)
        atomic_write_text(path, token + "\n", mode=0o600)
        return token


def token_matches(expected: str, authorization: str | None) -> bool:
    if not authorization or not authorization.startswith("Bearer "):
        return False
    supplied = authorization[7:].strip()
    return bool(supplied) and hmac.compare_digest(expected, supplied)


def origin_is_local(origin: str | None) -> bool:
    if not origin:
        return True
    try:
        parsed = urlsplit(origin.strip())
        host = (parsed.hostname or "").lower()
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and host in {"127.0.0.1", "localhost", "::1"}

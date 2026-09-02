"""Canonical event helpers for Ragdoll Project History."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

SCHEMA_VERSION = 1
EVENT_TYPE_RE = re.compile(r"^[a-z][a-z0-9]*(?:\.[a-z0-9][a-z0-9_-]*){1,7}$")
IDEMPOTENCY_KEY_RE = re.compile(r"^[A-Za-z0-9._:-]{8,200}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def event_hash(event_without_hash: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(event_without_hash).encode("utf-8")).hexdigest()


def validate_event_type(event_type: str) -> str:
    value = str(event_type).strip().lower()
    if not EVENT_TYPE_RE.fullmatch(value):
        raise ValueError("event type must use dot-separated lowercase namespaces, for example user.message")
    return value


def validate_idempotency_key(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    key = str(value).strip()
    if not IDEMPOTENCY_KEY_RE.fullmatch(key):
        raise ValueError("invalid idempotency_key")
    return key


def build_event(
    *,
    project_id: str,
    conversation_id: str,
    seq: int,
    event_type: str,
    payload: dict[str, Any],
    prev_hash: str,
    ts: str | None = None,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "event_id": f"evt_{uuid4().hex}",
        "project_id": project_id,
        "conversation_id": conversation_id,
        "seq": seq,
        "ts": ts or utc_now(),
        "type": validate_event_type(event_type),
        "payload": payload,
        "prev_hash": prev_hash,
    }
    validated_key = validate_idempotency_key(idempotency_key)
    if validated_key:
        event["idempotency_key"] = validated_key
    event["event_hash"] = event_hash(event)
    return event


def verify_event_hash(event: dict[str, Any]) -> bool:
    stored = event.get("event_hash")
    copy = dict(event)
    copy.pop("event_hash", None)
    return isinstance(stored, str) and stored == event_hash(copy)

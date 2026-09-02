"""Canonical append-only local Project History store."""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

from ragdoll.storage.atomic import atomic_write_json
from ragdoll.storage.locks import exclusive_file_lock

from .identity import get_project, ragdoll_home, validate_project_id
from .index import (
    connect,
    conversation_max_seq,
    idempotent_event_ref,
    index_conversation,
    index_event,
    list_conversations_indexed,
)
from .model import build_event, utc_now, validate_idempotency_key, verify_event_hash
from .security import sanitize


def index_path(home: Path) -> Path:
    return home / "indexes" / "history.sqlite3"


def index_dirty_path(home: Path) -> Path:
    return home / "indexes" / "history.dirty"


def _mark_index_dirty(home: Path) -> None:
    path = index_dirty_path(home)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.touch(exist_ok=True)
    except OSError:
        pass


def _validate_conversation_id(conversation_id: str) -> str:
    value = str(conversation_id).strip()
    if not value.startswith("conv_") or len(value) != 37:
        raise ValueError("invalid conversation_id")
    suffix = value[5:]
    if any(ch not in "0123456789abcdef" for ch in suffix):
        raise ValueError("invalid conversation_id")
    return value


def project_dir(home: Path, project_id: str) -> Path:
    return home / "projects" / validate_project_id(project_id)


def conversation_dir(home: Path, project_id: str, conversation_id: str) -> Path:
    return project_dir(home, project_id) / "conversations" / _validate_conversation_id(conversation_id)


def read_conversation(home: Path, project_id: str, conversation_id: str) -> dict[str, Any]:
    get_project(project_id, home)
    path = conversation_dir(home, project_id, conversation_id) / "conversation.json"
    if not path.exists():
        raise FileNotFoundError(conversation_id)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"conversation metadata is corrupt: {conversation_id}") from exc
    if not isinstance(value, dict) or value.get("project_id") != project_id:
        raise RuntimeError(f"conversation metadata is invalid: {conversation_id}")
    return value


def list_conversations(
    home: Path,
    project_id: str,
    *,
    limit: int = 100,
    before: str | None = None,
) -> list[dict[str, Any]]:
    """List conversations from the derived SQLite index when healthy.

    Canonical metadata remains on disk. If the disposable index is marked dirty
    or SQLite cannot be read, fall back to the filesystem scan so correctness
    wins over performance during recovery.
    """
    get_project(project_id, home)
    if not index_dirty_path(home).exists():
        try:
            db = connect(index_path(home))
            try:
                return list_conversations_indexed(db, project_id=project_id, limit=limit, before=before)
            finally:
                db.close()
        except sqlite3.Error:
            _mark_index_dirty(home)
    return _list_conversations_from_filesystem(home, project_id, limit=limit, before=before)


def _list_conversations_from_filesystem(
    home: Path,
    project_id: str,
    *,
    limit: int = 100,
    before: str | None = None,
) -> list[dict[str, Any]]:
    get_project(project_id, home)
    root = project_dir(home, project_id) / "conversations"
    if not root.exists():
        return []
    result: list[dict[str, Any]] = []
    for directory in root.iterdir():
        if not directory.is_dir():
            continue
        path = directory / "conversation.json"
        if not path.exists():
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(value, dict):
            continue
        updated_at = str(value.get("updated_at", ""))
        if before and updated_at >= before:
            continue
        result.append(value)
    result.sort(key=lambda item: str(item.get("updated_at", "")), reverse=True)
    return result[: max(1, min(limit, 1000))]


def start_conversation(
    project_id: str,
    *,
    title: str = "",
    workspace: str | None = None,
    ide: str | None = None,
    provider: str | None = None,
    parent_conversation_id: str | None = None,
    forked_at_seq: int | None = None,
    home: Path | None = None,
) -> dict[str, Any]:
    home = home or ragdoll_home()
    get_project(project_id, home)
    if parent_conversation_id:
        read_conversation(home, project_id, parent_conversation_id)
        if forked_at_seq is not None and forked_at_seq < 1:
            raise ValueError("forked_at_seq must be >= 1")
    conversation_id = f"conv_{uuid4().hex}"
    now = utc_now()
    metadata = {
        "schema_version": 1,
        "conversation_id": conversation_id,
        "project_id": project_id,
        "created_at": now,
        "updated_at": now,
        "title": title[:500],
        "workspace": workspace,
        "ide": ide,
        "provider": provider,
        "parent_conversation_id": parent_conversation_id,
        "forked_at_seq": forked_at_seq,
    }
    directory = conversation_dir(home, project_id, conversation_id)
    directory.mkdir(parents=True, exist_ok=False)
    atomic_write_json(directory / "conversation.json", metadata, mode=0o600)
    append_event(
        project_id,
        conversation_id,
        "conversation.started",
        {"title": title[:500], "workspace": workspace, "ide": ide, "provider": provider},
        home=home,
    )
    return metadata


def _last_event(path: Path) -> dict[str, Any] | None:
    """Read only the final non-empty JSONL record instead of scanning history."""
    if not path.exists() or path.stat().st_size == 0:
        return None
    with path.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        position = handle.tell()
        buffer = b""
        while position > 0:
            read_size = min(8192, position)
            position -= read_size
            handle.seek(position)
            buffer = handle.read(read_size) + buffer
            lines = [line for line in buffer.splitlines() if line.strip()]
            if len(lines) >= 2:
                try:
                    return json.loads(lines[-1].decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return None
            if position == 0 and lines:
                try:
                    return json.loads(lines[-1].decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return None
    return None


def _find_idempotent_event(path: Path, key: str) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("idempotency_key") == key:
                return event
    return None


def _event_by_seq(path: Path, seq: int) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            current = int(event.get("seq", 0))
            if current == seq:
                return event
            if current > seq:
                return None
    return None


def append_event(
    project_id: str,
    conversation_id: str,
    event_type: str,
    payload: dict[str, Any],
    *,
    idempotency_key: str | None = None,
    home: Path | None = None,
) -> dict[str, Any]:
    home = home or ragdoll_home()
    directory = conversation_dir(home, project_id, conversation_id)
    metadata = read_conversation(home, project_id, conversation_id)
    key = validate_idempotency_key(idempotency_key)
    events_path = directory / "events.jsonl"

    with exclusive_file_lock(directory / ".append.lock"):
        previous = _last_event(events_path)
        previous_seq = int(previous["seq"]) if previous else 0
        if key:
            # Use the disposable SQLite index as the fast path only when it is
            # demonstrably caught up with the canonical JSONL tail. If a crash
            # or prior index failure left it behind, fall back to the canonical
            # scan so retry idempotency remains correct.
            index_synchronized = False
            if not index_dirty_path(home).exists():
                try:
                    db = connect(index_path(home))
                    try:
                        reference = idempotent_event_ref(db, project_id, conversation_id, key)
                        indexed_seq = conversation_max_seq(db, project_id, conversation_id)
                    finally:
                        db.close()
                    if reference is not None:
                        existing = _event_by_seq(events_path, reference[0])
                        if existing is not None and existing.get("event_hash") == reference[1]:
                            return existing
                    index_synchronized = indexed_seq == previous_seq
                except sqlite3.Error:
                    _mark_index_dirty(home)
            if not index_synchronized:
                existing = _find_idempotent_event(events_path, key)
                if existing is not None:
                    return existing
        seq = previous_seq + 1
        prev_hash = str(previous["event_hash"]) if previous else ""
        safe_payload = sanitize(payload)
        event = build_event(
            project_id=project_id,
            conversation_id=conversation_id,
            seq=seq,
            event_type=event_type,
            payload=safe_payload,
            prev_hash=prev_hash,
            idempotency_key=key,
        )
        with events_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

        metadata["updated_at"] = event["ts"]
        atomic_write_json(directory / "conversation.json", metadata, mode=0o600)

    # Canonical JSONL is authoritative. A derived-index failure must not make a
    # durable append look failed and tempt clients to append a duplicate event.
    try:
        db = connect(index_path(home))
        try:
            index_conversation(db, metadata)
            index_event(db, event)
            db.commit()
        finally:
            db.close()
    except sqlite3.Error:
        _mark_index_dirty(home)
    return event


def iter_conversation_events(
    home: Path,
    project_id: str,
    conversation_id: str,
    *,
    after_seq: int = 0,
    limit: int | None = None,
) -> Iterator[dict[str, Any]]:
    path = conversation_dir(home, project_id, conversation_id) / "events.jsonl"
    if not path.exists():
        return
    yielded = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if int(event.get("seq", 0)) <= after_seq:
                continue
            yield event
            yielded += 1
            if limit is not None and yielded >= limit:
                break


def iter_all_conversations(home: Path, project_id: str | None = None) -> Iterator[dict[str, Any]]:
    projects_root = home / "projects"
    if not projects_root.exists():
        return
    project_dirs = (
        [projects_root / validate_project_id(project_id)]
        if project_id
        else [p for p in projects_root.iterdir() if p.is_dir() and p.name.startswith("prj_")]
    )
    for pdir in sorted(project_dirs):
        conversations = pdir / "conversations"
        if not conversations.exists():
            continue
        for cdir in sorted(conversations.iterdir()):
            path = cdir / "conversation.json"
            if not path.exists():
                continue
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(value, dict):
                yield value


def iter_all_events(home: Path, project_id: str | None = None) -> Iterator[dict[str, Any]]:
    projects_root = home / "projects"
    if not projects_root.exists():
        return
    project_dirs = [projects_root / validate_project_id(project_id)] if project_id else [p for p in projects_root.iterdir() if p.is_dir() and p.name.startswith("prj_")]
    for pdir in sorted(project_dirs):
        conversations = pdir / "conversations"
        if not conversations.exists():
            continue
        for cdir in sorted(conversations.iterdir()):
            path = cdir / "events.jsonl"
            if not path.exists():
                continue
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            continue


def verify_conversation(home: Path, project_id: str, conversation_id: str) -> list[str]:
    errors: list[str] = []
    expected_seq = 1
    expected_prev = ""
    seen_ids: set[str] = set()
    seen_idempotency: set[str] = set()
    for event in iter_conversation_events(home, project_id, conversation_id):
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or event_id in seen_ids:
            errors.append(f"seq {expected_seq}: duplicate or invalid event_id")
        elif event_id:
            seen_ids.add(event_id)
        idem = event.get("idempotency_key")
        if idem:
            if idem in seen_idempotency:
                errors.append(f"seq {event.get('seq')}: duplicate idempotency_key")
            seen_idempotency.add(str(idem))
        if event.get("project_id") != project_id:
            errors.append(f"seq {expected_seq}: project_id mismatch")
        if event.get("conversation_id") != conversation_id:
            errors.append(f"seq {expected_seq}: conversation_id mismatch")
        if event.get("seq") != expected_seq:
            errors.append(f"expected seq {expected_seq}, found {event.get('seq')}")
        if event.get("prev_hash") != expected_prev:
            errors.append(f"seq {event.get('seq')}: previous hash mismatch")
        if not verify_event_hash(event):
            errors.append(f"seq {event.get('seq')}: event hash mismatch")
        expected_seq += 1
        expected_prev = str(event.get("event_hash", ""))
    return errors


def purge_project(home: Path, project_id: str, confirmation: str) -> None:
    project_id = validate_project_id(project_id)
    if confirmation != project_id:
        raise ValueError("confirmation must exactly match project_id")
    directory = project_dir(home, project_id)
    if not directory.exists():
        raise FileNotFoundError(project_id)

    registry_path = home / "projects" / "registry.json"
    lock = home / "projects" / ".registry.lock"
    with exclusive_file_lock(lock):
        registry = json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else {"schema_version": 1, "projects": {}}
        if isinstance(registry.get("projects"), dict):
            registry["projects"].pop(project_id, None)
        atomic_write_json(registry_path, registry, mode=0o600)
    shutil.rmtree(directory)

    try:
        db = connect(index_path(home))
        try:
            hashes = [row[0] for row in db.execute("SELECT event_hash FROM events WHERE project_id = ?", (project_id,))]
            db.execute("DELETE FROM conversations WHERE project_id = ?", (project_id,))
            db.execute("DELETE FROM events WHERE project_id = ?", (project_id,))
            try:
                for event_hash in hashes:
                    db.execute("DELETE FROM events_fts WHERE event_hash = ?", (event_hash,))
            except sqlite3.OperationalError:
                pass
            db.commit()
        finally:
            db.close()
    except sqlite3.Error:
        _mark_index_dirty(home)

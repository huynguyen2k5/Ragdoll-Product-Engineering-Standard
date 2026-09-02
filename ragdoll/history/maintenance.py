"""Index verification and rebuild operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .index import clear, connect, index_conversation, index_event, index_status, integrity_check
from .store import index_dirty_path, index_path, iter_all_conversations, iter_all_events


def rebuild_index(home: Path) -> int:
    dirty_path = index_dirty_path(home)
    db = connect(index_path(home))
    count = 0
    try:
        clear(db)
        for metadata in iter_all_conversations(home):
            index_conversation(db, metadata)
        for event in iter_all_events(home):
            index_event(db, event)
            count += 1
        db.commit()
        dirty_path.unlink(missing_ok=True)
    except Exception:
        try:
            dirty_path.parent.mkdir(parents=True, exist_ok=True)
            dirty_path.touch(exist_ok=True)
        except OSError:
            pass
        raise
    finally:
        db.close()
    return count


def get_index_status(home: Path) -> dict[str, Any]:
    path = index_path(home)
    db = connect(path)
    try:
        status = index_status(db)
        status["integrity"] = integrity_check(db)
        status["fts5_active"] = status.get("fts5", False)
    finally:
        db.close()
    status.update(
        {
            "exists": path.exists(),
            "path": str(path),
            "bytes": path.stat().st_size if path.exists() else 0,
            "dirty": index_dirty_path(home).exists(),
        }
    )
    return status

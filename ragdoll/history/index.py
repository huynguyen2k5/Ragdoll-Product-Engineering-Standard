"""Disposable SQLite/FTS index for canonical Project History JSONL.

The SQLite database is derived state: it may be deleted and rebuilt at any time
from canonical JSONL. Migrations are therefore intentionally simple and never
mutate canonical history.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

INDEX_SCHEMA_VERSION = 3


def _column_exists(db: sqlite3.Connection, table: str, column: str) -> bool:
    return any(row[1] == column for row in db.execute(f"PRAGMA table_info({table})"))


def _migrate(db: sqlite3.Connection) -> None:
    db.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
    )
    applied = {int(row[0]) for row in db.execute("SELECT version FROM schema_migrations")}

    if 1 not in applied:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_hash TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                conversation_id TEXT NOT NULL,
                seq INTEGER NOT NULL,
                ts TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                file_path TEXT,
                commit_sha TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_events_project_ts ON events(project_id, ts);
            CREATE INDEX IF NOT EXISTS idx_events_project_conversation ON events(project_id, conversation_id, seq);
            CREATE INDEX IF NOT EXISTS idx_events_project_file ON events(project_id, file_path);
            CREATE INDEX IF NOT EXISTS idx_events_project_commit ON events(project_id, commit_sha);
            """
        )
        db.execute("INSERT OR IGNORE INTO schema_migrations(version) VALUES (1)")

    if 2 not in applied:
        if not _column_exists(db, "events", "idempotency_key"):
            db.execute("ALTER TABLE events ADD COLUMN idempotency_key TEXT")
        db.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_events_idempotency ON events(project_id, conversation_id, idempotency_key) WHERE idempotency_key IS NOT NULL"
        )
        db.execute("INSERT OR IGNORE INTO schema_migrations(version) VALUES (2)")

    if 3 not in applied:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                title TEXT NOT NULL,
                workspace TEXT,
                ide TEXT,
                provider TEXT,
                parent_conversation_id TEXT,
                forked_at_seq INTEGER
            );
            CREATE INDEX IF NOT EXISTS idx_conversations_project_updated
                ON conversations(project_id, updated_at DESC, conversation_id);
            """
        )
        db.execute("INSERT OR IGNORE INTO schema_migrations(version) VALUES (3)")

    try:
        db.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS events_fts USING fts5(event_hash UNINDEXED, project_id UNINDEXED, content, tokenize='unicode61')"
        )
    except sqlite3.OperationalError:
        pass
    db.commit()


def connect(index_path: Path) -> sqlite3.Connection:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(index_path, timeout=10.0)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=NORMAL")
    db.execute("PRAGMA busy_timeout=10000")
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA temp_store=MEMORY")
    _migrate(db)
    return db


def flatten_payload(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        return "\n".join(f"{key}: {flatten_payload(value)}" for key, value in payload.items())
    if isinstance(payload, (list, tuple)):
        return "\n".join(flatten_payload(value) for value in payload)
    if payload is None:
        return ""
    return str(payload)


def index_conversation(db: sqlite3.Connection, metadata: dict[str, Any]) -> None:
    db.execute(
        """
        INSERT INTO conversations(
            conversation_id, project_id, created_at, updated_at, title, workspace, ide, provider,
            parent_conversation_id, forked_at_seq
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(conversation_id) DO UPDATE SET
            project_id=excluded.project_id,
            created_at=excluded.created_at,
            updated_at=excluded.updated_at,
            title=excluded.title,
            workspace=excluded.workspace,
            ide=excluded.ide,
            provider=excluded.provider,
            parent_conversation_id=excluded.parent_conversation_id,
            forked_at_seq=excluded.forked_at_seq
        """,
        (
            metadata["conversation_id"],
            metadata["project_id"],
            str(metadata.get("created_at", "")),
            str(metadata.get("updated_at", "")),
            str(metadata.get("title", "")),
            metadata.get("workspace"),
            metadata.get("ide"),
            metadata.get("provider"),
            metadata.get("parent_conversation_id"),
            metadata.get("forked_at_seq"),
        ),
    )


def list_conversations_indexed(
    db: sqlite3.Connection, *, project_id: str, limit: int, before: str | None = None
) -> list[dict[str, Any]]:
    params: list[Any] = [project_id]
    where = "project_id = ?"
    if before:
        where += " AND updated_at < ?"
        params.append(before)
    params.append(max(1, min(limit, 1000)))
    rows = db.execute(
        f"""
        SELECT conversation_id, project_id, created_at, updated_at, title, workspace, ide, provider,
               parent_conversation_id, forked_at_seq
        FROM conversations
        WHERE {where}
        ORDER BY updated_at DESC, conversation_id DESC
        LIMIT ?
        """,
        params,
    )
    return [dict(row) | {"schema_version": 1} for row in rows]


def index_event(db: sqlite3.Connection, event: dict[str, Any]) -> None:
    payload = event.get("payload", {})
    content = flatten_payload(payload)
    file_path = payload.get("file_path") if isinstance(payload, dict) else None
    commit_sha = payload.get("commit_sha") if isinstance(payload, dict) else None
    idempotency_key = event.get("idempotency_key")
    db.execute(
        """
        INSERT INTO events(event_hash, project_id, conversation_id, seq, ts, type, content, file_path, commit_sha, idempotency_key)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(event_hash) DO UPDATE SET
            content=excluded.content,
            file_path=excluded.file_path,
            commit_sha=excluded.commit_sha,
            idempotency_key=excluded.idempotency_key
        """,
        (
            event["event_hash"],
            event["project_id"],
            event["conversation_id"],
            event["seq"],
            event["ts"],
            event["type"],
            content,
            file_path,
            commit_sha,
            idempotency_key,
        ),
    )
    try:
        db.execute("DELETE FROM events_fts WHERE event_hash = ?", (event["event_hash"],))
        db.execute(
            "INSERT INTO events_fts(event_hash, project_id, content) VALUES (?, ?, ?)",
            (event["event_hash"], event["project_id"], content),
        )
    except sqlite3.OperationalError:
        pass


def clear(db: sqlite3.Connection) -> None:
    db.execute("DELETE FROM conversations")
    db.execute("DELETE FROM events")
    try:
        db.execute("DELETE FROM events_fts")
    except sqlite3.OperationalError:
        pass
    db.commit()


def has_fts(db: sqlite3.Connection) -> bool:
    row = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='events_fts'").fetchone()
    return row is not None


def index_status(db: sqlite3.Connection) -> dict[str, Any]:
    version_row = db.execute("SELECT MAX(version) FROM schema_migrations").fetchone()
    events = int(db.execute("SELECT COUNT(*) FROM events").fetchone()[0])
    conversations = int(db.execute("SELECT COUNT(*) FROM conversations").fetchone()[0])
    return {
        "index_schema_version": int(version_row[0] or 0),
        "current_index_schema_version": INDEX_SCHEMA_VERSION,
        "fts5": has_fts(db),
        "events": events,
        "conversations": conversations,
    }


def integrity_check(db: sqlite3.Connection) -> str:
    row = db.execute("PRAGMA quick_check").fetchone()
    return str(row[0]) if row else "unknown"


def _fts_expression(query: str) -> str:
    tokens = [token for token in query.replace('"', " ").split() if token]
    return " OR ".join('"' + token.replace('"', '""') + '"' for token in tokens)


def conversation_max_seq(db: sqlite3.Connection, project_id: str, conversation_id: str) -> int:
    row = db.execute(
        "SELECT MAX(seq) FROM events WHERE project_id = ? AND conversation_id = ?",
        (project_id, conversation_id),
    ).fetchone()
    return int(row[0] or 0) if row else 0


def idempotent_event_ref(
    db: sqlite3.Connection, project_id: str, conversation_id: str, idempotency_key: str
) -> tuple[int, str] | None:
    row = db.execute(
        """
        SELECT seq, event_hash
        FROM events
        WHERE project_id = ? AND conversation_id = ? AND idempotency_key = ?
        LIMIT 1
        """,
        (project_id, conversation_id, idempotency_key),
    ).fetchone()
    if row is None:
        return None
    return int(row["seq"]), str(row["event_hash"])


def search(
    db: sqlite3.Connection,
    *,
    project_id: str,
    query: str,
    limit: int = 20,
    file_path: str | None = None,
    commit_sha: str | None = None,
    event_type: str | None = None,
    conversation_id: str | None = None,
) -> list[sqlite3.Row]:
    filters = ["e.project_id = ?"]
    params: list[Any] = [project_id]
    if file_path:
        filters.append("e.file_path = ?")
        params.append(file_path)
    if commit_sha:
        filters.append("e.commit_sha = ?")
        params.append(commit_sha)
    if event_type:
        filters.append("e.type = ?")
        params.append(event_type)
    if conversation_id:
        filters.append("e.conversation_id = ?")
        params.append(conversation_id)

    where = " AND ".join(filters)
    if query and has_fts(db):
        expression = _fts_expression(query)
        if expression:
            sql = f"""
                SELECT e.*
                FROM events_fts f
                JOIN events e ON e.event_hash = f.event_hash
                WHERE events_fts MATCH ? AND {where}
                ORDER BY bm25(events_fts), e.ts DESC
                LIMIT ?
            """
            return list(db.execute(sql, [expression, *params, limit]))

    if query:
        where += " AND lower(e.content) LIKE ?"
        params.append("%" + query.lower() + "%")
    sql = f"SELECT e.* FROM events e WHERE {where} ORDER BY e.ts DESC LIMIT ?"
    params.append(limit)
    return list(db.execute(sql, params))

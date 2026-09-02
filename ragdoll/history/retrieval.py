"""Project-scoped retrieval with token-aware evidence compilation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ragdoll.utils import estimate_tokens

from .index import connect, search
from .store import index_path, iter_all_events, iter_conversation_events


def _row_to_result(row: Any) -> dict[str, Any]:
    return {
        "project_id": row["project_id"],
        "conversation_id": row["conversation_id"],
        "seq": row["seq"],
        "ts": row["ts"],
        "type": row["type"],
        "content": row["content"],
        "file_path": row["file_path"],
        "commit_sha": row["commit_sha"],
        "event_hash": row["event_hash"],
    }


def focused_search(
    home: Path,
    project_id: str,
    query: str,
    *,
    limit: int = 20,
    file_path: str | None = None,
    commit_sha: str | None = None,
    event_type: str | None = None,
    conversation_id: str | None = None,
) -> list[dict[str, Any]]:
    db = connect(index_path(home))
    try:
        rows = search(
            db,
            project_id=project_id,
            query=query,
            limit=max(1, min(limit, 1000)),
            file_path=file_path,
            commit_sha=commit_sha,
            event_type=event_type,
            conversation_id=conversation_id,
        )
        return [_row_to_result(row) for row in rows]
    finally:
        db.close()


def comprehensive_search(
    home: Path,
    project_id: str,
    query: str,
    *,
    limit: int = 500,
    max_scan: int = 50_000,
) -> list[dict[str, Any]]:
    terms = [term.casefold() for term in query.split() if term.strip()]
    matches: list[dict[str, Any]] = []
    scanned = 0
    for event in iter_all_events(home, project_id):
        scanned += 1
        if scanned > max_scan:
            break
        payload = event.get("payload", {})
        content = _payload_text(payload)
        text = content.casefold()
        if not terms or all(term in text for term in terms):
            matches.append(_event_to_result(event, content))
            if len(matches) >= max(1, min(limit, 10_000)):
                break
    return matches


def forensic_search(
    home: Path,
    project_id: str,
    query: str,
    *,
    limit: int = 50,
    neighbor_events: int = 2,
    file_path: str | None = None,
    commit_sha: str | None = None,
    event_type: str | None = None,
    conversation_id: str | None = None,
) -> list[dict[str, Any]]:
    """Search indexed evidence then expand exact neighboring raw events.

    This mode is designed for provenance/debugging questions. It remains
    project-scoped and bounded, unlike an unrestricted raw replay.
    """
    hits = focused_search(
        home,
        project_id,
        query,
        limit=max(1, min(limit, 200)),
        file_path=file_path,
        commit_sha=commit_sha,
        event_type=event_type,
        conversation_id=conversation_id,
    )
    if not hits:
        return []
    wanted: dict[tuple[str, int], None] = {}
    radius = max(0, min(neighbor_events, 10))
    by_conversation: dict[str, set[int]] = {}
    for hit in hits:
        cid = str(hit["conversation_id"])
        seq = int(hit["seq"])
        by_conversation.setdefault(cid, set()).update(range(max(1, seq - radius), seq + radius + 1))
    for cid, seqs in by_conversation.items():
        for event in iter_conversation_events(home, project_id, cid):
            seq = int(event.get("seq", 0))
            if seq in seqs:
                wanted[(cid, seq)] = None
    results: list[dict[str, Any]] = []
    for cid, seq in sorted(wanted, key=lambda item: (item[0], item[1])):
        for event in iter_conversation_events(home, project_id, cid, after_seq=seq - 1, limit=1):
            results.append(_event_to_result(event, _payload_text(event.get("payload", {}))))
            break
    max_results = len(hits) * (radius * 2 + 1)
    return results[:max_results]


def _payload_text(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        parts: list[str] = []
        for key, value in payload.items():
            if isinstance(value, (dict, list, tuple)):
                parts.append(f"{key}: {_payload_text(value)}")
            else:
                parts.append(f"{key}: {value}")
        return "\n".join(parts)
    if isinstance(payload, (list, tuple)):
        return "\n".join(_payload_text(item) for item in payload)
    return "" if payload is None else str(payload)


def _event_to_result(event: dict[str, Any], content: str) -> dict[str, Any]:
    payload = event.get("payload", {})
    return {
        "project_id": event["project_id"],
        "conversation_id": event["conversation_id"],
        "seq": event["seq"],
        "ts": event["ts"],
        "type": event["type"],
        "content": content,
        "file_path": payload.get("file_path") if isinstance(payload, dict) else None,
        "commit_sha": payload.get("commit_sha") if isinstance(payload, dict) else None,
        "event_hash": event["event_hash"],
    }


def compile_evidence(results: list[dict[str, Any]], token_budget: int = 2500) -> dict[str, Any]:
    budget = max(200, min(int(token_budget), 100_000))
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    used = 0
    for original in results:
        event_hash = str(original.get("event_hash") or "")
        if event_hash and event_hash in seen:
            continue
        result = dict(original)
        text = str(result.get("content", ""))
        cost = estimate_tokens(text) + 48
        if selected and used + cost > budget:
            continue
        if cost > budget and not selected:
            clipped_chars = max(200, (budget - 80) * 3)
            result["content"] = text[:clipped_chars] + "\n[TRUNCATED FOR TOKEN BUDGET]"
            cost = estimate_tokens(str(result["content"])) + 48
        if used + cost > budget and selected:
            continue
        selected.append(result)
        used += cost
        if event_hash:
            seen.add(event_hash)
        if used >= budget:
            break
    return {
        "token_budget": budget,
        "estimated_tokens": used,
        "result_count": len(selected),
        "results": selected,
    }

"""Command-line entrypoint for durable local Project History."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .identity import list_projects, ragdoll_home, register_project
from .maintenance import get_index_status, rebuild_index
from .retrieval import compile_evidence, comprehensive_search, focused_search, forensic_search
from .store import append_event, purge_project, start_conversation, verify_conversation


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Ragdoll local-first Project History utility")
    p.add_argument("--home", help="Override RAGDOLL_HOME for this command")
    sub = p.add_subparsers(dest="command", required=True)

    reg = sub.add_parser("register-project")
    reg.add_argument("path", nargs="?", default=".")
    reg.add_argument("--name")
    sub.add_parser("list-projects")

    start = sub.add_parser("start-conversation")
    start.add_argument("--project", required=True)
    start.add_argument("--title", default="")
    start.add_argument("--workspace")
    start.add_argument("--ide")
    start.add_argument("--provider")
    start.add_argument("--parent")
    start.add_argument("--forked-at-seq", type=int)

    app = sub.add_parser("append")
    app.add_argument("--project", required=True)
    app.add_argument("--conversation", required=True)
    app.add_argument("--type", required=True)
    app.add_argument("--text")
    app.add_argument("--payload-json")
    app.add_argument("--file")
    app.add_argument("--commit")
    app.add_argument("--idempotency-key")

    search = sub.add_parser("search")
    search.add_argument("--project", required=True)
    search.add_argument("--query", default="")
    search.add_argument("--mode", choices=("focused", "comprehensive", "forensic"), default="focused")
    search.add_argument("--limit", type=int, default=20)
    search.add_argument("--token-budget", type=int, default=2500)
    search.add_argument("--file")
    search.add_argument("--commit")
    search.add_argument("--type")
    search.add_argument("--conversation")

    verify = sub.add_parser("verify")
    verify.add_argument("--project", required=True)
    verify.add_argument("--conversation", required=True)

    sub.add_parser("index-status")
    sub.add_parser("rebuild-index")

    purge = sub.add_parser("purge-project")
    purge.add_argument("--project", required=True)
    purge.add_argument("--confirm", required=True)
    return p


def _home(value: str | None) -> Path:
    return Path(value).expanduser().resolve() if value else ragdoll_home()


def _print(value: object) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    home = _home(args.home)

    if args.command == "register-project":
        _print(register_project(Path(args.path), args.name, home))
        return 0
    if args.command == "list-projects":
        _print(list_projects(home))
        return 0
    if args.command == "start-conversation":
        _print(
            start_conversation(
                args.project,
                title=args.title,
                workspace=args.workspace,
                ide=args.ide,
                provider=args.provider,
                parent_conversation_id=args.parent,
                forked_at_seq=args.forked_at_seq,
                home=home,
            )
        )
        return 0
    if args.command == "append":
        payload: dict[str, object] = {}
        if args.payload_json:
            parsed = json.loads(args.payload_json)
            if not isinstance(parsed, dict):
                raise ValueError("--payload-json must be a JSON object")
            payload.update(parsed)
        if args.text is not None:
            payload["text"] = args.text
        if args.file:
            payload["file_path"] = args.file
        if args.commit:
            payload["commit_sha"] = args.commit
        _print(
            append_event(
                args.project,
                args.conversation,
                args.type,
                payload,
                idempotency_key=args.idempotency_key,
                home=home,
            )
        )
        return 0
    if args.command == "search":
        if args.mode == "comprehensive":
            results = comprehensive_search(home, args.project, args.query, limit=max(args.limit, 1))
        elif args.mode == "forensic":
            results = forensic_search(
                home,
                args.project,
                args.query,
                limit=max(args.limit, 1),
                file_path=args.file,
                commit_sha=args.commit,
                event_type=args.type,
                conversation_id=args.conversation,
            )
        else:
            results = focused_search(
                home,
                args.project,
                args.query,
                limit=max(args.limit, 1),
                file_path=args.file,
                commit_sha=args.commit,
                event_type=args.type,
                conversation_id=args.conversation,
            )
        _print(compile_evidence(results, max(args.token_budget, 200)))
        return 0
    if args.command == "verify":
        errors = verify_conversation(home, args.project, args.conversation)
        _print({"ok": not errors, "errors": errors})
        return 0 if not errors else 1
    if args.command == "index-status":
        _print(get_index_status(home))
        return 0
    if args.command == "rebuild-index":
        _print({"indexed_events": rebuild_index(home)})
        return 0
    if args.command == "purge-project":
        purge_project(home, args.project, args.confirm)
        _print({"purged_project": args.project})
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

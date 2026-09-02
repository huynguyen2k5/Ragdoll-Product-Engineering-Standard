"""Ragdoll command-line adapter."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from ragdoll.core import RagdollCore, RagdollError
from ragdoll.history.cli import main as history_main
from ragdoll.storage.atomic import atomic_write_text
from ragdoll.storage.migrations import ensure_home_schema

from . import __version__
from .config import Settings
from .env_template import ENV_TEMPLATE
from .local_security import api_token_path, get_or_create_api_token
from .runtime import health, read_pid, start_background, stop_background
from .server import serve


def _json(value: object) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def _init(settings: Settings) -> dict[str, object]:
    migration = ensure_home_schema(settings.home)
    env_path = settings.home / ".env"
    created_env = False
    if not env_path.exists():
        atomic_write_text(env_path, ENV_TEMPLATE, mode=0o600)
        created_env = True
    token = get_or_create_api_token(settings.home, settings.api_token)
    return {
        "home": str(settings.home),
        "home_schema": migration.current_version,
        "env_file": str(env_path),
        "created_env": created_env,
        "api_token_file": str(api_token_path(settings.home)),
        "api_token_ready": bool(token),
    }


def _doctor(settings: Settings, core: RagdollCore) -> dict[str, object]:
    ensure_home_schema(settings.home)
    writable = os.access(settings.home, os.W_OK)
    readiness = core.readiness()
    return {
        "ok": sys.version_info >= (3, 11) and writable and bool(readiness.get("ok")),
        "version": __version__,
        "python": sys.version.split()[0],
        "python_supported": sys.version_info >= (3, 11),
        "home": str(settings.home),
        "home_writable": writable,
        "env_file": str(settings.env_file) if settings.env_file else None,
        "configured_providers": settings.configured_providers(),
        "provider_required_for_history": False,
        "telemetry": False,
        "cloud_sync": False,
        "bind": f"{settings.host}:{settings.port}",
        "remote_bind_allowed": settings.allow_remote_bind,
        "server_healthy": bool(health(settings)),
        "history_index": readiness.get("history_index"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ragdoll", description="Ragdoll local-first engineering backend")
    parser.add_argument("--env-file", help="Explicit Ragdoll .env file")
    parser.add_argument("--version", action="version", version=f"ragdoll {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Initialize ~/.ragdoll and a local .env template")
    sub.add_parser("doctor", help="Check local installation/config without making provider calls")
    sub.add_parser("providers", help="Show configured provider status without exposing keys")
    sub.add_parser("token", help="Print the local API token for IDE/API clients")

    start = sub.add_parser("start", help="Start the local backend")
    start.add_argument("--foreground", action="store_true")
    sub.add_parser("stop", help="Stop a background backend started by Ragdoll")
    sub.add_parser("status", help="Show backend/config status")
    sub.add_parser("serve", help="Run the local backend in the foreground")

    project = sub.add_parser("project", help="Manage project identities")
    project_sub = project.add_subparsers(dest="project_command", required=True)
    register = project_sub.add_parser("register")
    register.add_argument("path", nargs="?", default=".")
    register.add_argument("--name")
    project_sub.add_parser("list")
    show = project_sub.add_parser("show")
    show.add_argument("project_id")

    history = sub.add_parser("history", help="Use the durable local history CLI")
    history.add_argument("history_args", nargs=argparse.REMAINDER)

    context = sub.add_parser("context", help="Generate, validate, inspect, or compile Project Context")
    context_sub = context.add_subparsers(dest="context_command", required=True)
    generate = context_sub.add_parser("generate")
    generate.add_argument("--project", required=True)
    generate.add_argument("--force", action="store_true")
    generate.add_argument("--project-name")
    validate = context_sub.add_parser("validate")
    validate.add_argument("--project", required=True)
    inspect = context_sub.add_parser("inspect")
    inspect.add_argument("--project", required=True)
    compile_cmd = context_sub.add_parser("compile")
    compile_cmd.add_argument("--project", required=True)
    compile_cmd.add_argument("--prompt", required=True)
    compile_cmd.add_argument("--history-mode", choices=("focused", "comprehensive", "forensic"), default="focused")
    compile_cmd.add_argument("--no-history", action="store_true")
    compile_cmd.add_argument("--no-project-context", action="store_true")

    chat = sub.add_parser("chat", help="Call a configured provider using local Ragdoll context/history")
    chat.add_argument("prompt")
    chat.add_argument("--project", required=True)
    chat.add_argument("--conversation")
    chat.add_argument("--provider", choices=("openai", "anthropic", "gemini"))
    chat.add_argument("--model")
    chat.add_argument("--ide", default="ragdoll-cli")
    chat.add_argument("--idempotency-key")
    chat.add_argument("--no-history", action="store_true")
    chat.add_argument("--no-project-context", action="store_true")
    chat.add_argument("--history-mode", choices=("focused", "comprehensive", "forensic"), default="focused")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        settings = Settings.load(args.env_file)
        core = RagdollCore(settings)
        if args.command == "init":
            _json(_init(settings))
            return 0
        core.bootstrap()
        if args.command == "doctor":
            result = _doctor(settings, core)
            _json(result)
            return 0 if result["ok"] else 1
        if args.command == "providers":
            _json(core.providers())
            return 0
        if args.command == "token":
            print(get_or_create_api_token(settings.home, settings.api_token))
            return 0
        if args.command == "serve" or (args.command == "start" and args.foreground):
            serve(settings)
            return 0
        if args.command == "start":
            _json(start_background(settings))
            return 0
        if args.command == "stop":
            _json(stop_background(settings))
            return 0
        if args.command == "status":
            _json({"health": health(settings), "pid": read_pid(settings), "core": core.status()})
            return 0
        if args.command == "project":
            if args.project_command == "register":
                _json(core.register_project({"path": args.path, "name": args.name}))
            elif args.project_command == "list":
                _json(core.projects())
            elif args.project_command == "show":
                _json(core.project(args.project_id))
            return 0
        if args.command == "history":
            return history_main(["--home", str(settings.home), *args.history_args])
        if args.command == "context":
            if args.context_command == "generate":
                _json(core.generate_context(args.project, {"force": args.force, "project_name": args.project_name}))
            elif args.context_command == "validate":
                result = core.validate_context(args.project)
                _json(result)
                return 0 if result["ok"] else 1
            elif args.context_command == "inspect":
                _json(core.context_manifest(args.project))
            elif args.context_command == "compile":
                _json(
                    core.compile_context(
                        args.project,
                        {
                            "prompt": args.prompt,
                            "history_mode": args.history_mode,
                            "use_history": not args.no_history,
                            "use_project_context": not args.no_project_context,
                        },
                    )
                )
            return 0
        if args.command == "chat":
            _json(
                core.chat(
                    {
                        "project_id": args.project,
                        "conversation_id": args.conversation,
                        "prompt": args.prompt,
                        "provider": args.provider,
                        "model": args.model,
                        "ide": args.ide,
                        "idempotency_key": args.idempotency_key,
                        "use_history": not args.no_history,
                        "use_project_context": not args.no_project_context,
                        "history_mode": args.history_mode,
                    }
                )
            )
            return 0
    except RagdollError as exc:
        print(f"ragdoll[{exc.code}]: {exc.message}", file=sys.stderr)
        return 1
    except (ValueError, KeyError, FileNotFoundError, FileExistsError, RuntimeError) as exc:
        print(f"ragdoll: {exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

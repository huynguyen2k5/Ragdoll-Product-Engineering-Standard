"""Stable local project identity without a hosted account."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from uuid import uuid4

from ragdoll.storage.atomic import atomic_write_json, read_json
from ragdoll.storage.locks import exclusive_file_lock

from .model import utc_now

PROJECT_ID_RE = re.compile(r"^prj_[0-9a-f]{32}$")
REGISTRY_SCHEMA_VERSION = 1


def validate_project_id(project_id: str) -> str:
    value = str(project_id).strip()
    if not PROJECT_ID_RE.fullmatch(value):
        raise ValueError("invalid project_id")
    return value


def ragdoll_home() -> Path:
    configured = os.environ.get("RAGDOLL_HOME")
    return Path(configured).expanduser().resolve() if configured else (Path.home() / ".ragdoll").resolve()


def _git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def normalize_remote(remote: str | None) -> str | None:
    if not remote:
        return None
    value = remote.strip()
    scp = re.match(r"^[^/@\s]+@([^:\s]+):(.+)$", value)
    if scp:
        host = scp.group(1).lower()
        path = scp.group(2).strip("/")
        if path.endswith(".git"):
            path = path[:-4]
        return f"{host}/{path}".lower()
    try:
        parts = urlsplit(value)
        if parts.scheme and parts.netloc:
            host = (parts.hostname or "").lower()
            port = f":{parts.port}" if parts.port else ""
            path = parts.path.strip("/")
            if path.endswith(".git"):
                path = path[:-4]
            return f"{host}{port}/{path}".lower()
    except ValueError:
        pass
    value = re.sub(r"^[^@/]+@", "", value).strip("/")
    if value.endswith(".git"):
        value = value[:-4]
    return value.lower()


def inspect_repository(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_dir():
        raise ValueError("project path must be an existing directory")
    root_text = _git(path, "rev-parse", "--show-toplevel")
    root = Path(root_text).resolve() if root_text else path.resolve()
    remote = normalize_remote(_git(root, "remote", "get-url", "origin"))
    root_commit = _git(root, "rev-list", "--max-parents=0", "HEAD")
    branch = _git(root, "branch", "--show-current")
    head = _git(root, "rev-parse", "HEAD")
    return {
        "workspace": str(root),
        "remote": remote,
        "root_commit": root_commit,
        "branch": branch,
        "head": head,
    }


def _registry_path(home: Path) -> Path:
    return home / "projects" / "registry.json"


def _load_registry(home: Path) -> dict[str, Any]:
    path = _registry_path(home)
    if not path.exists():
        return {"schema_version": REGISTRY_SCHEMA_VERSION, "projects": {}}
    data = read_json(path, default=None)
    if not isinstance(data, dict) or not isinstance(data.get("projects"), dict):
        raise RuntimeError(f"project registry is corrupt: {path}")
    version = data.get("schema_version")
    if version != REGISTRY_SCHEMA_VERSION:
        raise RuntimeError(f"unsupported project registry schema: {version}")
    return data


def _save_registry(home: Path, registry: dict[str, Any]) -> None:
    atomic_write_json(_registry_path(home), registry, mode=0o600)


def register_project(path: Path, name: str | None = None, home: Path | None = None) -> dict[str, Any]:
    home = home or ragdoll_home()
    repo = inspect_repository(path)
    lock = home / "projects" / ".registry.lock"
    with exclusive_file_lock(lock):
        registry = _load_registry(home)
        projects: dict[str, Any] = registry["projects"]

        match_id: str | None = None
        for project_id, record in projects.items():
            remotes = set(record.get("git_remotes", []))
            workspaces = set(record.get("workspaces", []))
            if repo["remote"] and repo["remote"] in remotes:
                match_id = project_id
                break
            if not repo["remote"] and repo["workspace"] in workspaces:
                match_id = project_id
                break
            if not repo["remote"] and repo["root_commit"] and record.get("git_root_commit") == repo["root_commit"] and not remotes:
                match_id = project_id
                break

        now = utc_now()
        if match_id is None:
            match_id = f"prj_{uuid4().hex}"
            record = {
                "schema_version": 1,
                "project_id": match_id,
                "name": name or Path(repo["workspace"]).name,
                "created_at": now,
                "updated_at": now,
                "workspaces": [],
                "git_remotes": [],
                "git_root_commit": repo["root_commit"],
            }
            projects[match_id] = record
        else:
            record = projects[match_id]
            record["updated_at"] = now
            if name:
                record["name"] = name

        if repo["workspace"] not in record["workspaces"]:
            record["workspaces"].append(repo["workspace"])
        if repo["remote"] and repo["remote"] not in record["git_remotes"]:
            record["git_remotes"].append(repo["remote"])
        if not record.get("git_root_commit") and repo["root_commit"]:
            record["git_root_commit"] = repo["root_commit"]

        _save_registry(home, registry)
        project_directory = home / "projects" / match_id
        project_directory.mkdir(parents=True, exist_ok=True)
        atomic_write_json(project_directory / "project.json", record, mode=0o600)
    return {**record, "current_workspace": repo}


def get_project(project_id: str, home: Path | None = None) -> dict[str, Any]:
    home = home or ragdoll_home()
    project_id = validate_project_id(project_id)
    registry = _load_registry(home)
    record = registry.get("projects", {}).get(project_id)
    if not isinstance(record, dict):
        raise KeyError(f"unknown project_id: {project_id}")
    return record


def list_projects(home: Path | None = None) -> list[dict[str, Any]]:
    home = home or ragdoll_home()
    registry = _load_registry(home)
    return sorted(registry.get("projects", {}).values(), key=lambda item: item.get("updated_at", ""), reverse=True)

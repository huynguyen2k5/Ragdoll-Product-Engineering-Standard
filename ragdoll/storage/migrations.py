"""Versioned Ragdoll home-directory schema bootstrap.

The canonical history format has its own event schema. This module versions the
surrounding local data layout so future releases can migrate user state without
requiring a hosted control plane. Existing migration metadata is treated as
canonical local state: malformed metadata fails closed instead of being reset.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .atomic import atomic_write_json

CURRENT_HOME_SCHEMA = 1


@dataclass(frozen=True)
class HomeMigrationResult:
    previous_version: int
    current_version: int
    changed: bool


def _state_path(home: Path) -> Path:
    return home / "state.json"


def _read_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Ragdoll home migration state is corrupt: {path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"Ragdoll home migration state is invalid: {path}")
    return value


def read_home_schema_version(home: Path) -> int:
    state_path = _state_path(home)
    if not state_path.exists():
        return 0
    state = _read_state(state_path)
    try:
        return int(state.get("schema_version", 0))
    except (TypeError, ValueError):
        return 0


def ensure_home_schema(home: Path) -> HomeMigrationResult:
    home.mkdir(parents=True, exist_ok=True)
    for directory in ("projects", "indexes", "runtime", "logs", "backups"):
        (home / directory).mkdir(parents=True, exist_ok=True)

    state_path = _state_path(home)
    state = _read_state(state_path)
    raw_version = state.get("schema_version", 0)
    try:
        previous = int(raw_version)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Ragdoll home schema_version is invalid: {raw_version!r}") from exc
    if previous < 0:
        raise RuntimeError(f"Ragdoll home schema_version is invalid: {previous}")
    if previous > CURRENT_HOME_SCHEMA:
        raise RuntimeError(
            f"Ragdoll data schema {previous} is newer than this runtime supports ({CURRENT_HOME_SCHEMA})"
        )

    changed = previous != CURRENT_HOME_SCHEMA
    if changed:
        new_state: dict[str, Any] = dict(state)
        new_state["schema_version"] = CURRENT_HOME_SCHEMA
        atomic_write_json(state_path, new_state, mode=0o600)
    return HomeMigrationResult(previous, CURRENT_HOME_SCHEMA, changed)

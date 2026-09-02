"""Crash-resistant local file writes.

Ragdoll keeps canonical project state on the user's machine. Small metadata files
are written with write-fsync-replace semantics so a process crash cannot leave a
partially-written JSON document as the only copy.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def _fsync_directory(path: Path) -> None:
    """Best-effort fsync of a directory after rename on POSIX."""
    if os.name == "nt":
        return
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def atomic_write_text(path: Path, text: str, *, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        if mode is not None and os.name != "nt":
            try:
                os.chmod(temp_path, mode)
            except OSError:
                pass
        os.replace(temp_path, path)
        _fsync_directory(path.parent)
    except Exception:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def atomic_write_json(path: Path, value: Any, *, mode: int | None = None) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", mode=mode)


def read_json(path: Path, *, default: Any = None) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default

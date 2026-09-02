"""Dependency-free cross-platform lock files for small local transactions.

Ragdoll uses these locks only for metadata/file operations. SQLite keeps its own
transactional locking. A lock is removed as stale only when it is old *and* its
recorded owner process is no longer alive; this favors data safety over forcing
progress when ownership is ambiguous.
"""

from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def _process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _stale_owner_is_dead(path: Path, stale_after_seconds: float) -> bool:
    try:
        stat = path.stat()
    except OSError:
        return False
    if time.time() - stat.st_mtime <= stale_after_seconds:
        return False

    try:
        value = json.loads(path.read_text(encoding="ascii"))
        pid = int(value.get("pid", 0)) if isinstance(value, dict) else 0
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        # An old malformed lock cannot prove a live owner. Removing it is safer
        # than permanently deadlocking future Ragdoll processes.
        return True
    return not _process_alive(pid)


@contextmanager
def exclusive_file_lock(
    path: Path,
    *,
    timeout_seconds: float = 10.0,
    stale_after_seconds: float = 60.0,
) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout_seconds
    while True:
        fd: int | None = None
        try:
            mode = 0o666 if os.name == "nt" else 0o600
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, mode)
            payload = json.dumps({"pid": os.getpid(), "created_at": time.time()}).encode("ascii")
            os.write(fd, payload)
            os.fsync(fd)
            os.close(fd)
            fd = None
            break
        except FileExistsError:
            if _stale_owner_is_dead(path, stale_after_seconds):
                try:
                    path.unlink()
                    continue
                except OSError:
                    pass
            if time.monotonic() >= deadline:
                raise TimeoutError(f"timed out waiting for local lock: {path}")
            time.sleep(0.05)
        finally:
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
    try:
        yield
    finally:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass

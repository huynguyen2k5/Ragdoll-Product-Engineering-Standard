"""Local backend process lifecycle used by the CLI installer experience."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .config import Settings
from .storage.atomic import atomic_write_json, read_json

_STARTUP_TIMEOUT_SECONDS = 10.0
_STARTUP_POLL_INTERVAL_SECONDS = 0.2


def pid_path(settings: Settings) -> Path:
    return settings.home / "runtime" / "server.pid.json"


def legacy_pid_path(settings: Settings) -> Path:
    return settings.home / "runtime" / "server.pid"


def log_path(settings: Settings) -> Path:
    return settings.home / "logs" / "server.log"


def process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def health(settings: Settings, timeout: float = 1.0) -> dict[str, Any] | None:
    url = f"http://{settings.host}:{settings.port}/v1/health"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            value = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) and value.get("service") == "ragdoll-local" else None


def read_pid(settings: Settings) -> int | None:
    value = read_json(pid_path(settings), default=None)
    if isinstance(value, dict):
        try:
            return int(value.get("pid"))
        except (TypeError, ValueError):
            pass
    legacy = legacy_pid_path(settings)
    if legacy.exists():
        try:
            return int(legacy.read_text(encoding="ascii").strip())
        except (OSError, ValueError):
            return None
    return None


def _write_pid(settings: Settings, pid: int) -> None:
    atomic_write_json(
        pid_path(settings),
        {
            "pid": pid,
            "host": settings.host,
            "port": settings.port,
            "python": sys.executable,
            "started_at_epoch": time.time(),
        },
        mode=0o600,
    )
    legacy_pid_path(settings).unlink(missing_ok=True)


def _clear_pid(settings: Settings) -> None:
    pid_path(settings).unlink(missing_ok=True)
    legacy_pid_path(settings).unlink(missing_ok=True)


def start_background(settings: Settings) -> dict[str, Any]:
    current_health = health(settings)
    if current_health:
        return {"started": False, "already_running": True, "health": current_health}

    existing_pid = read_pid(settings)
    if existing_pid and process_alive(existing_pid):
        raise RuntimeError(
            f"PID {existing_pid} is alive but the configured Ragdoll endpoint is not healthy; refusing to replace or kill it"
        )
    _clear_pid(settings)

    output = log_path(settings)
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-m", "ragdoll.server"]
    if settings.env_file:
        command.extend(["--env-file", str(settings.env_file)])

    kwargs: dict[str, Any] = {
        "stdin": subprocess.DEVNULL,
        "cwd": str(Path.cwd()),
    }
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
    else:
        kwargs["start_new_session"] = True

    with output.open("ab") as log_handle:
        process = subprocess.Popen(command, stdout=log_handle, stderr=subprocess.STDOUT, **kwargs)
    _write_pid(settings, process.pid)

    deadline = time.monotonic() + _STARTUP_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if process.poll() is not None:
            _clear_pid(settings)
            raise RuntimeError(f"Ragdoll backend exited during startup. See {output}")
        current_health = health(settings, 0.5)
        if current_health:
            return {"started": True, "pid": process.pid, "health": current_health, "log": str(output)}
        time.sleep(_STARTUP_POLL_INTERVAL_SECONDS)
    try:
        process.terminate()
    except OSError:
        pass
    _clear_pid(settings)
    raise RuntimeError(f"Ragdoll backend did not become healthy. See {output}")


def stop_background(settings: Settings) -> dict[str, Any]:
    pid = read_pid(settings)
    if not pid:
        return {"stopped": False, "reason": "no_pid_file"}
    if not process_alive(pid):
        _clear_pid(settings)
        return {"stopped": False, "reason": "stale_pid", "pid": pid}

    # Never kill a live PID solely because a stale file points at it. Require the
    # Ragdoll endpoint to identify itself first.
    current_health = health(settings)
    if not current_health:
        raise RuntimeError(
            f"PID {pid} is alive but the configured endpoint is not Ragdoll; refusing to terminate the process"
        )

    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False, capture_output=True)
    else:
        os.kill(pid, signal.SIGTERM)
        deadline = time.monotonic() + 7.0
        while time.monotonic() < deadline and process_alive(pid):
            time.sleep(0.1)
        if process_alive(pid):
            os.kill(pid, signal.SIGKILL)
    _clear_pid(settings)
    return {"stopped": True, "pid": pid}

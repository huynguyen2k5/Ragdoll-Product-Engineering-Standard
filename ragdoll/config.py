"""Strict configuration loading for the local Ragdoll backend.

Ragdoll intentionally avoids python-dotenv at runtime. Only the Ragdoll-owned
.env file is loaded automatically; target-repository .env files are never read
implicitly because they commonly contain unrelated product secrets.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Mapping

DEFAULT_MODELS = {
    "openai": "gpt-4o",
    "anthropic": "claude-3-5-sonnet-20241022",
    "gemini": "gemini-1.5-flash",
}

PROVIDER_KEY_NAMES = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}

PROVIDER_MODEL_NAMES = {
    "openai": "OPENAI_MODEL",
    "anthropic": "ANTHROPIC_MODEL",
    "gemini": "GEMINI_MODEL",
}

_TRUTHY = {"1", "true", "yes", "on"}
_FALSY = {"0", "false", "no", "off"}


def _parse_bool(value: str | None, *, default: bool, name: str) -> bool:
    if value is None or value.strip() == "":
        return default
    normalized = value.strip().lower()
    if normalized in _TRUTHY:
        return True
    if normalized in _FALSY:
        return False
    raise ValueError(f"{name} must be one of true/false, 1/0, yes/no, on/off")


def _parse_int(value: str | None, *, default: int, minimum: int, maximum: int, name: str) -> int:
    if value is None or value.strip() == "":
        return default
    try:
        parsed = int(value)
    except ValueError:
        raise ValueError(f"{name} must be an integer") from None
    if parsed < minimum or parsed > maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return parsed


def _parse_float(value: str | None, *, default: float, minimum: float, maximum: float, name: str) -> float:
    if value is None or value.strip() == "":
        return default
    try:
        parsed = float(value)
    except ValueError:
        raise ValueError(f"{name} must be a number") from None
    if parsed < minimum or parsed > maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return parsed


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists() or not path.is_file():
        return values
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or not key.replace("_", "").isalnum():
            raise ValueError(f"invalid environment key at {path}:{line_number}")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        else:
            comment_pos = value.find(" #")
            if comment_pos != -1:
                value = value[:comment_pos].strip()
        values[key] = value
    return values


def resolve_env_file(explicit: str | None = None, cwd: Path | None = None) -> Path | None:
    # Reserved for a future explicit workspace-relative config policy. Ragdoll
    # intentionally does not discover arbitrary workspace .env files today.
    _ = cwd
    if explicit:
        return Path(explicit).expanduser().resolve()
    from_process = os.environ.get("RAGDOLL_ENV_FILE")
    if from_process:
        return Path(from_process).expanduser().resolve()
    configured_home = os.environ.get("RAGDOLL_HOME", "").strip()
    home = Path(configured_home).expanduser().resolve() if configured_home else (Path.home() / ".ragdoll").resolve()
    global_env = home / ".env"
    return global_env if global_env.exists() else None


def load_environment(explicit_env_file: str | None = None, cwd: Path | None = None) -> tuple[dict[str, str], Path | None]:
    env_file = resolve_env_file(explicit_env_file, cwd)
    merged: dict[str, str] = {}
    if env_file:
        merged.update(parse_env_file(env_file))
    # The actual process environment intentionally wins over file configuration.
    merged.update(os.environ)
    return merged, env_file


def _home_from(values: Mapping[str, str]) -> Path:
    configured = values.get("RAGDOLL_HOME", "").strip()
    return Path(configured).expanduser().resolve() if configured else (Path.home() / ".ragdoll").resolve()


@dataclass(frozen=True)
class Settings:
    home: Path
    env_file: Path | None
    provider: str
    host: str
    port: int
    allow_remote_bind: bool
    history_token_budget: int
    project_context_token_budget: int
    max_output_tokens: int
    outbound_secret_policy: str
    telemetry: bool
    cloud_sync: bool
    max_request_bytes: int
    max_provider_response_bytes: int
    provider_timeout_seconds: float
    log_level: str
    api_token: str | None
    api_keys: dict[str, str]
    models: dict[str, str]

    @classmethod
    def load(cls, env_file: str | None = None, cwd: Path | None = None) -> "Settings":
        values, resolved_env_file = load_environment(env_file, cwd)
        provider = values.get("RAGDOLL_PROVIDER", "auto").strip().lower() or "auto"
        if provider not in {"auto", "openai", "anthropic", "gemini"}:
            raise ValueError("RAGDOLL_PROVIDER must be auto, openai, anthropic, or gemini")

        secret_policy = values.get("RAGDOLL_OUTBOUND_SECRET_POLICY", "redact").strip().lower() or "redact"
        if secret_policy not in {"redact", "block"}:
            raise ValueError("RAGDOLL_OUTBOUND_SECRET_POLICY must be redact or block")

        log_level = values.get("RAGDOLL_LOG_LEVEL", "INFO").strip().upper() or "INFO"
        if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("RAGDOLL_LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")

        api_keys = {name: values.get(key_name, "").strip() for name, key_name in PROVIDER_KEY_NAMES.items()}
        models = {
            name: values.get(PROVIDER_MODEL_NAMES[name], "").strip() or DEFAULT_MODELS[name]
            for name in DEFAULT_MODELS
        }

        settings = cls(
            home=_home_from(values),
            env_file=resolved_env_file,
            provider=provider,
            host=values.get("RAGDOLL_HOST", "127.0.0.1").strip() or "127.0.0.1",
            port=_parse_int(values.get("RAGDOLL_PORT"), default=8765, minimum=1, maximum=65535, name="RAGDOLL_PORT"),
            allow_remote_bind=_parse_bool(values.get("RAGDOLL_ALLOW_REMOTE_BIND"), default=False, name="RAGDOLL_ALLOW_REMOTE_BIND"),
            history_token_budget=_parse_int(values.get("RAGDOLL_HISTORY_TOKEN_BUDGET"), default=1500, minimum=200, maximum=100000, name="RAGDOLL_HISTORY_TOKEN_BUDGET"),
            project_context_token_budget=_parse_int(values.get("RAGDOLL_PROJECT_CONTEXT_TOKEN_BUDGET"), default=2200, minimum=200, maximum=100000, name="RAGDOLL_PROJECT_CONTEXT_TOKEN_BUDGET"),
            max_output_tokens=_parse_int(values.get("RAGDOLL_MAX_OUTPUT_TOKENS"), default=4096, minimum=64, maximum=100000, name="RAGDOLL_MAX_OUTPUT_TOKENS"),
            outbound_secret_policy=secret_policy,
            telemetry=_parse_bool(values.get("RAGDOLL_TELEMETRY"), default=False, name="RAGDOLL_TELEMETRY"),
            cloud_sync=_parse_bool(values.get("RAGDOLL_CLOUD_SYNC"), default=False, name="RAGDOLL_CLOUD_SYNC"),
            max_request_bytes=_parse_int(values.get("RAGDOLL_MAX_REQUEST_BYTES"), default=2 * 1024 * 1024, minimum=1024, maximum=50 * 1024 * 1024, name="RAGDOLL_MAX_REQUEST_BYTES"),
            max_provider_response_bytes=_parse_int(values.get("RAGDOLL_MAX_PROVIDER_RESPONSE_BYTES"), default=8 * 1024 * 1024, minimum=1024, maximum=64 * 1024 * 1024, name="RAGDOLL_MAX_PROVIDER_RESPONSE_BYTES"),
            provider_timeout_seconds=_parse_float(values.get("RAGDOLL_PROVIDER_TIMEOUT_SECONDS"), default=90.0, minimum=1.0, maximum=600.0, name="RAGDOLL_PROVIDER_TIMEOUT_SECONDS"),
            log_level=log_level,
            api_token=values.get("RAGDOLL_API_TOKEN", "").strip() or None,
            api_keys=api_keys,
            models=models,
        )
        settings.validate_security_defaults()
        return settings

    def with_server_override(self, *, host: str | None = None, port: int | None = None) -> "Settings":
        result = replace(self, host=host if host is not None else self.host, port=port if port is not None else self.port)
        result.validate_security_defaults()
        return result

    def validate_security_defaults(self) -> None:
        loopback_names = {"127.0.0.1", "localhost", "::1"}
        if self.host not in loopback_names:
            raise ValueError(
                "Ragdoll Core is loopback-only. Remote HTTP bind is not supported because the local bearer token must not cross an unencrypted network."
            )
        if self.allow_remote_bind:
            raise ValueError(
                "RAGDOLL_ALLOW_REMOTE_BIND is reserved for a future authenticated TLS transport and must remain false."
            )
        if self.telemetry:
            raise ValueError("Ragdoll Core has no telemetry transport; RAGDOLL_TELEMETRY must remain false")
        if self.cloud_sync:
            raise ValueError("Ragdoll Core has no hosted sync; RAGDOLL_CLOUD_SYNC must remain false")

    def configured_providers(self) -> list[str]:
        return [name for name in ("openai", "anthropic", "gemini") if self.api_keys.get(name)]

    def resolve_provider(self, requested: str | None = None) -> str:
        value = (requested or self.provider or "auto").strip().lower()
        if value != "auto":
            if value not in PROVIDER_KEY_NAMES:
                raise ValueError(f"unsupported provider: {value}")
            if not self.api_keys.get(value):
                raise ValueError(f"{PROVIDER_KEY_NAMES[value]} is not configured")
            return value
        configured = self.configured_providers()
        if not configured:
            raise ValueError("No provider API key configured in the Ragdoll .env or process environment")
        return configured[0]

    def model_for(self, provider: str, requested: str | None = None) -> str:
        if requested and requested.strip():
            return requested.strip()
        return self.models[provider]

    def safe_status(self) -> dict[str, object]:
        return {
            "home": str(self.home),
            "env_file": str(self.env_file) if self.env_file else None,
            "provider_mode": self.provider,
            "configured_providers": self.configured_providers(),
            "models": {name: self.models[name] for name in self.configured_providers()},
            "host": self.host,
            "port": self.port,
            "telemetry": False,
            "cloud_sync": False,
            "outbound_secret_policy": self.outbound_secret_policy,
            "provider_timeout_seconds": self.provider_timeout_seconds,
            "max_request_bytes": self.max_request_bytes,
            "log_level": self.log_level,
        }

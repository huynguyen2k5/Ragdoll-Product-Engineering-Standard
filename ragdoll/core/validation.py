"""Strict request validation helpers without third-party runtime dependencies."""

from __future__ import annotations

from typing import Any

from .errors import ValidationError


def required_string(body: dict[str, Any], key: str, *, max_length: int = 100_000) -> str:
    value = body.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{key} is required")
    value = value.strip()
    if len(value) > max_length:
        raise ValidationError(f"{key} exceeds maximum length", details={"max_length": max_length})
    return value


def optional_string(body: dict[str, Any], key: str, *, max_length: int = 10_000) -> str | None:
    value = body.get(key)
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ValidationError(f"{key} must be a string")
    value = value.strip()
    if len(value) > max_length:
        raise ValidationError(f"{key} exceeds maximum length", details={"max_length": max_length})
    return value or None


def bounded_int(
    body: dict[str, Any],
    key: str,
    *,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    value = body.get(key, default)
    if isinstance(value, bool):
        raise ValidationError(f"{key} must be an integer")
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{key} must be an integer") from None
    if parsed < minimum or parsed > maximum:
        raise ValidationError(
            f"{key} must be between {minimum} and {maximum}",
            details={"minimum": minimum, "maximum": maximum},
        )
    return parsed


def optional_bool(body: dict[str, Any], key: str, *, default: bool) -> bool:
    value = body.get(key, default)
    if not isinstance(value, bool):
        raise ValidationError(f"{key} must be a boolean")
    return value


def optional_int(
    body: dict[str, Any],
    key: str,
    *,
    minimum: int,
    maximum: int,
) -> int | None:
    value = body.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"{key} must be an integer")
    if value < minimum or value > maximum:
        raise ValidationError(
            f"{key} must be between {minimum} and {maximum}",
            details={"minimum": minimum, "maximum": maximum},
        )
    return value

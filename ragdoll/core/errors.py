"""Stable, transport-neutral error contract for Ragdoll Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(eq=False)
class RagdollError(Exception):
    message: str
    code: str = "ragdoll_error"
    http_status: int = 500
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__init__(self.message)

    def as_dict(self, request_id: str | None = None) -> dict[str, Any]:
        error: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details:
            error["details"] = self.details
        if request_id:
            error["request_id"] = request_id
        return {"error": error}


class ValidationError(RagdollError):
    def __init__(self, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message, "validation_error", 400, details or {})


class NotFoundError(RagdollError):
    def __init__(self, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message, "not_found", 404, details or {})


class ConflictError(RagdollError):
    def __init__(self, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message, "conflict", 409, details or {})


class SecurityPolicyError(RagdollError):
    def __init__(self, message: str, *, code: str = "security_policy_denied"):
        super().__init__(message, code, 403)


class ProviderGatewayError(RagdollError):
    def __init__(self, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message, "provider_error", 502, details or {})

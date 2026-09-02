"""Local secret redaction utilities.

This module intentionally has no network dependencies. Pattern matching is defense in
 depth and must never be treated as proof that arbitrary content is non-sensitive.
"""

from __future__ import annotations

import re
from typing import Any

REDACTED = "[REDACTED]"

_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?i)(\b(?:api[_-]?key|access[_-]?token|refresh[_-]?token|token|secret|password|passwd|pwd)\b\s*[:=]\s*)[^\s,;#]+"), r"\1" + REDACTED),
    (re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+\-/=]{12,}"), "Bearer " + REDACTED),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), REDACTED),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"), REDACTED),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), REDACTED),
    (re.compile(r"(?is)-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----.*?-----END (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), REDACTED),
    (re.compile(r"(?i)\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^\s]+"), REDACTED),
)

SENSITIVE_BASENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    "secrets.json",
}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}


def redact_text(text: str) -> str:
    result = text
    for pattern, replacement in _PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def sanitize(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize(item) for item in value]
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if re.search(r"(?i)(password|passwd|secret|token|api[_-]?key|authorization|cookie)", key_text):
                clean[key_text] = REDACTED
            else:
                clean[key_text] = sanitize(item)
        return clean
    return value


def is_sensitive_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    base = normalized.rsplit("/", 1)[-1].lower()
    if base in SENSITIVE_BASENAMES or base.startswith(".env."):
        return True
    return any(base.endswith(suffix) for suffix in SENSITIVE_SUFFIXES)

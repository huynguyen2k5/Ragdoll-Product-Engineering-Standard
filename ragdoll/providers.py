"""Direct provider adapters for user-supplied cloud API keys.

Provider calls are explicit, HTTPS-only, host-allowlisted, non-redirecting, and
never fall back to another provider after selection. Ragdoll operates no model
proxy and does not store provider credentials in history.
"""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlsplit

from ragdoll.history.security import REDACTED, redact_text

from . import __version__
from .config import Settings

PROVIDER_HOSTS = {
    "openai": "api.openai.com",
    "anthropic": "api.anthropic.com",
    "gemini": "generativelanguage.googleapis.com",
}

PROVIDER_URLS = {
    "openai": "https://api.openai.com/v1/responses",
    "anthropic": "https://api.anthropic.com/v1/messages",
}


class ProviderError(RuntimeError):
    """Safe provider error that never intentionally contains an API key."""


@dataclass(frozen=True)
class ProviderResponse:
    provider: str
    model: str
    text: str
    usage: dict[str, int | None]
    response_id: str | None = None


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[override]
        return None


def _safe_error_text(value: str, limit: int = 1000) -> str:
    return redact_text(value)[:limit]


def _read_bounded(response: Any, max_bytes: int) -> bytes:
    raw = response.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ProviderError("provider response exceeded local safety limit")
    return raw


def _post_json(
    url: str,
    headers: dict[str, str],
    body: dict[str, Any],
    timeout: float = 90.0,
    max_response_bytes: int = 8 * 1024 * 1024,
) -> dict[str, Any]:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ProviderError("provider endpoint must use HTTPS")
    if parsed.hostname not in set(PROVIDER_HOSTS.values()):
        raise ProviderError(f"provider host is not allowlisted: {parsed.hostname}")

    payload = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(url=url, data=payload, method="POST")
    request.add_header("Content-Type", "application/json")
    request.add_header("Accept", "application/json")
    request.add_header("User-Agent", f"ragdoll-local/{__version__}")
    for key, value in headers.items():
        request.add_header(key, value)

    context = ssl.create_default_context()
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context), _NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            final = urlsplit(response.geturl())
            if final.scheme != "https" or final.hostname != parsed.hostname:
                raise ProviderError("provider endpoint changed unexpectedly")
            raw = _read_bounded(response, max_response_bytes).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        try:
            raw_bytes = exc.read(max_response_bytes + 1) if exc.fp else str(exc).encode()
        except OSError:
            raw_bytes = str(exc).encode()
        raw = raw_bytes[:max_response_bytes].decode("utf-8", errors="replace")
        if 300 <= exc.code < 400:
            raise ProviderError("provider redirects are denied") from None
        raise ProviderError(f"provider HTTP {exc.code}: {_safe_error_text(raw)}") from None
    except urllib.error.URLError as exc:
        raise ProviderError(f"provider network error: {_safe_error_text(str(exc.reason))}") from None
    except TimeoutError:
        raise ProviderError("provider request timed out") from None

    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError:
        raise ProviderError("provider returned invalid JSON") from None
    if not isinstance(decoded, dict):
        raise ProviderError("provider returned an unexpected response shape")
    return decoded


def _sanitize_outbound(text: str, policy: str) -> tuple[str, bool]:
    sanitized = redact_text(text)
    changed = sanitized != text
    if changed and policy == "block":
        raise ProviderError("outbound request blocked because secret-like content was detected")
    return sanitized, changed


def _request(
    settings: Settings,
    provider: str,
    headers: dict[str, str],
    body: dict[str, Any],
    *,
    url: str | None = None,
) -> dict[str, Any]:
    return _post_json(
        url or PROVIDER_URLS[provider],
        headers,
        body,
        timeout=settings.provider_timeout_seconds,
        max_response_bytes=settings.max_provider_response_bytes,
    )


def _openai(settings: Settings, model: str, prompt: str, system: str, max_output_tokens: int) -> ProviderResponse:
    body: dict[str, Any] = {
        "model": model,
        "input": prompt,
        "max_output_tokens": max_output_tokens,
        "store": False,
    }
    if system:
        body["instructions"] = system
    data = _request(settings, "openai", {"Authorization": f"Bearer {settings.api_keys['openai']}"}, body)
    text = str(data.get("output_text") or "")
    if not text:
        parts: list[str] = []
        for item in data.get("output", []) if isinstance(data.get("output"), list) else []:
            if not isinstance(item, dict):
                continue
            for content in item.get("content", []) if isinstance(item.get("content"), list) else []:
                if isinstance(content, dict) and content.get("type") in {"output_text", "text"}:
                    value = content.get("text")
                    if isinstance(value, str):
                        parts.append(value)
        text = "\n".join(parts)
    if not text:
        raise ProviderError("OpenAI response contained no text output")
    usage_raw = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    usage = {
        "input_tokens": usage_raw.get("input_tokens"),
        "output_tokens": usage_raw.get("output_tokens"),
        "total_tokens": usage_raw.get("total_tokens"),
    }
    return ProviderResponse("openai", str(data.get("model") or model), text, usage, data.get("id"))


def _anthropic(settings: Settings, model: str, prompt: str, system: str, max_output_tokens: int) -> ProviderResponse:
    body: dict[str, Any] = {
        "model": model,
        "max_tokens": max_output_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system
    data = _request(
        settings,
        "anthropic",
        {"x-api-key": settings.api_keys["anthropic"], "anthropic-version": "2023-06-01"},
        body,
    )
    parts: list[str] = []
    content = data.get("content") if isinstance(data.get("content"), list) else []
    for item in content:
        if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str):
            parts.append(item["text"])
    text = "\n".join(parts)
    if not text:
        raise ProviderError("Anthropic response contained no text output")
    usage_raw = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    input_tokens = usage_raw.get("input_tokens")
    output_tokens = usage_raw.get("output_tokens")
    total_tokens = input_tokens + output_tokens if isinstance(input_tokens, int) and isinstance(output_tokens, int) else None
    usage = {"input_tokens": input_tokens, "output_tokens": output_tokens, "total_tokens": total_tokens}
    return ProviderResponse("anthropic", str(data.get("model") or model), text, usage, data.get("id"))


def _gemini(settings: Settings, model: str, prompt: str, system: str, max_output_tokens: int) -> ProviderResponse:
    # Gemini generateContent places the model identifier in the request path.
    # Quote it as one path segment so user-provided model overrides cannot alter
    # the allowlisted host or endpoint structure.
    encoded_model = quote(model, safe="")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{encoded_model}:generateContent"
    body: dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_output_tokens},
        "store": False,
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    data = _request(
        settings,
        "gemini",
        {"x-goog-api-key": settings.api_keys["gemini"]},
        body,
        url=url,
    )
    parts: list[str] = []
    candidates = data.get("candidates") if isinstance(data.get("candidates"), list) else []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        content = candidate.get("content") if isinstance(candidate.get("content"), dict) else {}
        candidate_parts = content.get("parts") if isinstance(content.get("parts"), list) else []
        for item in candidate_parts:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
    text = "\n".join(parts)
    if not text:
        raise ProviderError("Gemini response contained no text output")
    usage_raw = data.get("usageMetadata") if isinstance(data.get("usageMetadata"), dict) else {}
    usage = {
        "input_tokens": usage_raw.get("promptTokenCount"),
        "output_tokens": usage_raw.get("candidatesTokenCount"),
        "total_tokens": usage_raw.get("totalTokenCount"),
    }
    return ProviderResponse("gemini", model, text, usage, data.get("responseId"))


def generate_text(
    settings: Settings,
    *,
    prompt: str,
    system: str = "",
    provider: str | None = None,
    model: str | None = None,
    max_output_tokens: int | None = None,
) -> tuple[ProviderResponse, dict[str, bool]]:
    selected = settings.resolve_provider(provider)
    selected_model = settings.model_for(selected, model)
    safe_prompt, prompt_redacted = _sanitize_outbound(prompt, settings.outbound_secret_policy)
    safe_system, system_redacted = _sanitize_outbound(system, settings.outbound_secret_policy)
    max_tokens = max_output_tokens or settings.max_output_tokens
    max_tokens = min(max(int(max_tokens), 64), 100000)

    if selected == "openai":
        response = _openai(settings, selected_model, safe_prompt, safe_system, max_tokens)
    elif selected == "anthropic":
        response = _anthropic(settings, selected_model, safe_prompt, safe_system, max_tokens)
    elif selected == "gemini":
        response = _gemini(settings, selected_model, safe_prompt, safe_system, max_tokens)
    else:
        raise ProviderError(f"unsupported provider: {selected}")

    return response, {"prompt_redacted": prompt_redacted, "system_redacted": system_redacted}


def provider_status(settings: Settings) -> list[dict[str, Any]]:
    configured = set(settings.configured_providers())
    return [
        {
            "provider": name,
            "configured": name in configured,
            "model": settings.models[name] if name in configured else None,
            "host": PROVIDER_HOSTS[name],
            "api_key": REDACTED if name in configured else None,
        }
        for name in ("openai", "anthropic", "gemini")
    ]

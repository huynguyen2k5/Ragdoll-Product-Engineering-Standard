"""Chat application service retained as a compatibility surface.

New transports should call :class:`ragdoll.core.RagdollCore`. This module keeps
the direct chat operation small and independently testable.
"""

from __future__ import annotations

from typing import Any

from ragdoll.history.identity import get_project
from ragdoll.history.store import append_event, start_conversation

from .config import Settings
from .context_runtime import compile_runtime_context
from .providers import ProviderError, generate_text


def _bounded_int(body: dict[str, Any], key: str, *, default: int, minimum: int, maximum: int) -> int:
    value = body.get(key, default)
    if isinstance(value, bool):
        raise ValueError(f"{key} must be an integer")
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{key} must be an integer") from None
    if parsed < minimum or parsed > maximum:
        raise ValueError(f"{key} must be between {minimum} and {maximum}")
    return parsed


def chat_once(settings: Settings, body: dict[str, Any]) -> dict[str, Any]:
    project_id = str(body.get("project_id") or "").strip()
    prompt = str(body.get("prompt") or "").strip()
    if not project_id:
        raise ValueError("project_id is required")
    if not prompt:
        raise ValueError("prompt is required")
    if len(prompt) > 200_000:
        raise ValueError("prompt exceeds maximum length")
    get_project(project_id, settings.home)

    provider = settings.resolve_provider(str(body.get("provider")) if body.get("provider") else None)
    model = settings.model_for(provider, str(body.get("model")) if body.get("model") else None)
    history_mode = str(body.get("history_mode") or "focused")
    if history_mode not in {"focused", "comprehensive", "forensic"}:
        raise ValueError("history_mode must be focused, comprehensive, or forensic")
    runtime = compile_runtime_context(
        home=settings.home,
        project_id=project_id,
        prompt=prompt,
        project_context_token_budget=_bounded_int(
            body, "project_context_token_budget", default=settings.project_context_token_budget, minimum=200, maximum=100000
        ),
        history_token_budget=_bounded_int(
            body, "history_token_budget", default=settings.history_token_budget, minimum=200, maximum=100000
        ),
        use_project_context=bool(body.get("use_project_context", True)),
        use_history=bool(body.get("use_history", True)),
        history_mode=history_mode,
    )

    conversation_id = str(body.get("conversation_id") or "").strip()
    if not conversation_id:
        meta = start_conversation(
            project_id,
            title=str(body.get("title") or prompt[:100]),
            workspace=None,
            ide=str(body.get("ide") or "ragdoll-local"),
            provider=provider,
            home=settings.home,
        )
        conversation_id = meta["conversation_id"]

    request_key = str(body.get("idempotency_key") or "").strip() or None
    append_event(
        project_id,
        conversation_id,
        "user.message",
        {"text": prompt, "provider": provider, "model": model},
        idempotency_key=f"{request_key}:user" if request_key else None,
        home=settings.home,
    )
    try:
        response, security = generate_text(
            settings,
            prompt=prompt,
            system=runtime.system_text,
            provider=provider,
            model=model,
            max_output_tokens=_bounded_int(
                body, "max_output_tokens", default=settings.max_output_tokens, minimum=64, maximum=100000
            ),
        )
    except ProviderError as exc:
        append_event(
            project_id,
            conversation_id,
            "provider.error",
            {"provider": provider, "model": model, "error": str(exc)},
            idempotency_key=f"{request_key}:error" if request_key else None,
            home=settings.home,
        )
        raise

    append_event(
        project_id,
        conversation_id,
        "assistant.message",
        {
            "text": response.text,
            "provider": response.provider,
            "model": response.model,
            "usage": response.usage,
            "response_id": response.response_id,
        },
        idempotency_key=f"{request_key}:assistant" if request_key else None,
        home=settings.home,
    )
    return {
        "conversation_id": conversation_id,
        "provider": response.provider,
        "model": response.model,
        "text": response.text,
        "usage": response.usage,
        "context": {
            "project_context_tokens": runtime.project_context_tokens,
            "history_tokens": runtime.history_tokens,
            "history_results": runtime.history_results,
            "project_context_sections": runtime.project_context_sections,
        },
        "security": security,
    }

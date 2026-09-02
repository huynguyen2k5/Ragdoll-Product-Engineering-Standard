"""Shared lightweight utilities with no heavy dependencies."""
from __future__ import annotations


def estimate_tokens(text: str) -> int:
    """Conservative dependency-free token estimator (~3.5 chars/token average).

    Tokenizers are provider-specific. This budgets conservatively rather than
    claiming precision. Uses ceil division of 3.5 chars/token.
    """
    return max(1, (len(text) * 2 + 6) // 7)

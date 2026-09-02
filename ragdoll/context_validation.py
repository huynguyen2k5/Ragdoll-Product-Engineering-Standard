#!/usr/bin/env python3
"""Validate the structure and basic provenance contract of Project Context."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DOMAIN = "software-engineering"
CANONICAL_FILES = (
    "project-overview.md",
    "architecture.md",
    "code-standards.md",
    "ai-workflow-rules.md",
    "progress-tracker.md",
    "ui-context.md",
)
PROVENANCE_LABELS = ("OBSERVED", "DECLARED", "INFERRED", "UNDECIDED")
TEMPLATE_TOKEN = re.compile(r"\{\{[^{}]+\}\}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a Ragdoll Project Context instance.")
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Repository root or project-context directory (default: current directory)",
    )
    return parser.parse_args()


def locate_context(path: Path) -> Path:
    if (path / "context-manifest.yaml").exists():
        return path
    candidate = path / "project-context"
    if (candidate / "context-manifest.yaml").exists():
        return candidate
    return candidate


def validate(context_root: Path) -> list[str]:
    errors: list[str] = []
    manifest = context_root / "context-manifest.yaml"
    if not manifest.exists():
        return [f"missing Project Context manifest: {manifest}"]

    manifest_text = manifest.read_text(encoding="utf-8", errors="replace")
    required_manifest_markers = (
        "schema_version:",
        "project:",
        "context_standard:",
        "active_domains:",
        "software-engineering:",
        "provenance_policy:",
    )
    for marker in required_manifest_markers:
        if marker not in manifest_text:
            errors.append(f"context-manifest.yaml missing required marker: {marker}")

    domain_dir = context_root / DOMAIN
    if not domain_dir.is_dir():
        errors.append(f"missing context domain directory: {domain_dir}")
        return errors

    for name in CANONICAL_FILES:
        path = domain_dir / name
        if not path.exists():
            errors.append(f"missing canonical Software Engineering context file: {path}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not text.lstrip().startswith("# "):
            errors.append(f"context file must begin with an H1 heading: {path}")
        tokens = TEMPLATE_TOKEN.findall(text)
        if tokens:
            errors.append(f"unresolved template token in {path}: {tokens[0]}")
        if "## Context Provenance" not in text:
            errors.append(f"missing Context Provenance section: {path}")
        for label in PROVENANCE_LABELS:
            if f"**{label}:**" not in text:
                errors.append(f"missing provenance label {label} in {path}")

    return errors


def main() -> int:
    args = parse_args()
    supplied = Path(args.path).expanduser().resolve()
    context_root = locate_context(supplied)
    errors = validate(context_root)
    if errors:
        print("Project Context validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Project Context validation passed: {context_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

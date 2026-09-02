"""Token-aware Project Context and Project History compilation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ragdoll.history.identity import get_project
from ragdoll.history.retrieval import compile_evidence, comprehensive_search, focused_search, forensic_search
from ragdoll.storage.locks import exclusive_file_lock
from ragdoll.utils import estimate_tokens

from .context_generation import build_context
from .context_validation import locate_context, validate

CONTEXT_FILES = (
    "project-overview.md",
    "architecture.md",
    "code-standards.md",
    "ai-workflow-rules.md",
    "progress-tracker.md",
    "ui-context.md",
)

_MAX_CONTEXT_FILE_CHARS = 500_000

UI_TERMS = {
    "ui", "ux", "css", "style", "layout", "component", "frontend", "react", "vue",
    "svelte", "design", "responsive", "screen", "page", "button", "form",
}


@dataclass(frozen=True)
class RuntimeContext:
    system_text: str
    project_context_tokens: int
    history_tokens: int
    history_results: int
    project_context_sections: int
    project_context_available: bool


def project_workspace(project_id: str, home: Path) -> Path:
    record = get_project(project_id, home)
    workspaces = record.get("workspaces", [])
    if not isinstance(workspaces, list) or not workspaces:
        raise FileNotFoundError(f"project has no registered workspace: {project_id}")
    for raw in reversed(workspaces):
        path = Path(str(raw)).expanduser().resolve()
        if path.exists() and path.is_dir():
            return path
    return Path(str(workspaces[-1])).expanduser().resolve()


def _sections(text: str) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    heading = "Document"
    current: list[str] = []
    for line in text.splitlines():
        stripped = line.lstrip("#")
        depth = len(line) - len(stripped)
        if 1 <= depth <= 3 and stripped.startswith(" "):
            if current:
                chunks.append((heading, "\n".join(current).strip()))
            heading = stripped.strip()
            current = [line]
        else:
            current.append(line)
    if current:
        chunks.append((heading, "\n".join(current).strip()))
    return [(h, c) for h, c in chunks if c]


def _query_terms(prompt: str) -> set[str]:
    return {term for term in re.findall(r"[a-zA-Z0-9_.-]{3,}", prompt.lower()) if not term.isdigit()}


def _context_candidates(workspace: Path, prompt: str) -> tuple[list[tuple[int, str, str]], bool]:
    root = workspace / "project-context" / "software-engineering"
    if not root.is_dir():
        return [], False
    terms = _query_terms(prompt)
    wants_ui = bool(terms & UI_TERMS)
    base = {
        "project-overview.md": 20,
        "progress-tracker.md": 18,
        "architecture.md": 16,
        "code-standards.md": 14,
        "ai-workflow-rules.md": 12,
        "ui-context.md": 10 if wants_ui else -10,
    }
    candidates: list[tuple[int, str, str]] = []
    for name in CONTEXT_FILES:
        path = root / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")[:_MAX_CONTEXT_FILE_CHARS]
        for heading, section in _sections(text):
            lower = section.lower()
            overlap = sum(1 for term in terms if term in lower)
            score = base[name] + min(overlap, 20) * 5
            if "undecided" in lower and overlap == 0:
                score -= 3
            candidates.append((score, f"{name} :: {heading}", section))
    candidates.sort(key=lambda item: (-item[0], item[1]))
    return candidates, True


def compile_project_context(workspace: Path, prompt: str, token_budget: int) -> tuple[str, int, int, bool]:
    candidates, available = _context_candidates(workspace, prompt)
    if not candidates:
        return "", 0, 0, available
    selected: list[str] = []
    used = 0
    for score, label, section in candidates:
        if score < 0:
            continue
        rendered = f"### {label}\n{section}"
        cost = estimate_tokens(rendered) + 10
        if selected and used + cost > token_budget:
            continue
        if not selected and cost > token_budget:
            chars = max(200, token_budget * 4 - 200)
            rendered = rendered[:chars] + "\n[PROJECT CONTEXT TRUNCATED]"
            cost = estimate_tokens(rendered) + 10
        if used + cost > token_budget and selected:
            continue
        selected.append(rendered)
        used += cost
        if used >= token_budget:
            break
    return "\n\n".join(selected), used, len(selected), available


def compile_history_context(
    home: Path,
    project_id: str,
    prompt: str,
    token_budget: int,
    mode: str = "focused",
) -> dict[str, Any]:
    if mode == "comprehensive":
        results = comprehensive_search(home, project_id, prompt, limit=200)
    elif mode == "forensic":
        results = forensic_search(home, project_id, prompt, limit=30)
    elif mode == "focused":
        results = focused_search(home, project_id, prompt, limit=30)
    else:
        raise ValueError("history_mode must be focused, comprehensive, or forensic")
    return compile_evidence(results, token_budget)


def compile_runtime_context(
    *,
    home: Path,
    project_id: str,
    prompt: str,
    project_context_token_budget: int,
    history_token_budget: int,
    use_project_context: bool = True,
    use_history: bool = True,
    history_mode: str = "focused",
) -> RuntimeContext:
    workspace = project_workspace(project_id, home)
    context_text = ""
    context_tokens = 0
    context_sections = 0
    context_available = (workspace / "project-context").exists()
    if use_project_context:
        context_text, context_tokens, context_sections, context_available = compile_project_context(
            workspace, prompt, project_context_token_budget
        )

    history = {"estimated_tokens": 0, "result_count": 0, "results": []}
    if use_history:
        history = compile_history_context(home, project_id, prompt, history_token_budget, history_mode)

    history_lines: list[str] = []
    for item in history.get("results", []):
        history_lines.append(
            "- "
            f"[{item.get('ts')}] {item.get('type')} "
            f"conversation={item.get('conversation_id')} seq={item.get('seq')}: "
            f"{item.get('content')}"
        )

    parts = [
        "You are working inside a Ragdoll-managed project. Treat current repository and reviewed Project Context as current authority. Treat Project History as evidence of past work, not automatic current truth. Never expose secrets or claim facts that are not supported by supplied evidence.",
    ]
    if context_text:
        parts.append("## Selected Project Context\n" + context_text)
    if history_lines:
        parts.append("## Relevant Project History\n" + "\n".join(history_lines))

    return RuntimeContext(
        system_text="\n\n".join(parts),
        project_context_tokens=context_tokens,
        history_tokens=int(history.get("estimated_tokens", 0)),
        history_results=int(history.get("result_count", 0)),
        project_context_sections=context_sections,
        project_context_available=context_available,
    )


def generate_context_for_project(home: Path, project_id: str, *, force: bool = False, project_name: str | None = None) -> Path:
    workspace = project_workspace(project_id, home)
    output = workspace / "project-context"
    lock_path = home / "runtime" / f"{project_id}.generate.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with exclusive_file_lock(lock_path, timeout_seconds=30.0):
        if output.exists() and any(output.iterdir()) and not force:
            raise FileExistsError("project-context already exists; pass force=true to replace it")
        if output.exists() and force:
            import shutil
            from datetime import datetime, timezone

            # Force never means silent destruction. Preserve the complete previous
            # canonical context under user-owned Ragdoll data before regeneration.
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            backup = home / "backups" / project_id / f"project-context-{stamp}"
            backup.parent.mkdir(parents=True, exist_ok=True)
            suffix = 1
            candidate = backup
            while candidate.exists():
                candidate = backup.with_name(f"{backup.name}-{suffix}")
                suffix += 1
            shutil.copytree(output, candidate)
            shutil.rmtree(output)
        build_context(workspace, output, project_name)
    return output


def validate_context_for_project(home: Path, project_id: str) -> list[str]:
    workspace = project_workspace(project_id, home)
    return validate(locate_context(workspace))


def read_context_manifest(home: Path, project_id: str) -> dict[str, Any]:
    workspace = project_workspace(project_id, home)
    context_root = workspace / "project-context"
    manifest = context_root / "context-manifest.yaml"
    files: list[dict[str, Any]] = []
    domain = context_root / "software-engineering"
    if domain.is_dir():
        for name in CONTEXT_FILES:
            path = domain / name
            if path.exists():
                files.append({"name": name, "bytes": path.stat().st_size})
    return {
        "workspace": str(workspace),
        "context_root": str(context_root),
        "exists": manifest.exists(),
        "manifest": manifest.read_text(encoding="utf-8", errors="replace") if manifest.exists() else None,
        "files": files,
    }

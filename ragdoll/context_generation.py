#!/usr/bin/env python3
"""Generate a conservative Software Engineering Project Context draft.

The generator intentionally records deterministic repository observations and leaves
material unknowns UNDECIDED. It must not infer architecture or product semantics
from suggestive names alone.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

GENERATOR_VERSION = "1.0.0"
DOMAIN_ID = "software-engineering"
CANONICAL_FILES = (
    "project-overview.md",
    "architecture.md",
    "code-standards.md",
    "ai-workflow-rules.md",
    "progress-tracker.md",
    "ui-context.md",
)

IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "target",
    "coverage",
    ".next",
    ".turbo",
    ".cache",
    "__pycache__",
}

LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".pyi": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".cs": "C#",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".dart": "Dart",
    ".scala": "Scala",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".lua": "Lua",
    ".sh": "Shell",
    ".ps1": "PowerShell",
}

PACKAGE_MANAGER_MARKERS = {
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "Yarn",
    "package-lock.json": "npm",
    "bun.lockb": "Bun",
    "bun.lock": "Bun",
    "uv.lock": "uv",
    "poetry.lock": "Poetry",
    "Pipfile.lock": "Pipenv",
    "requirements.txt": "pip/requirements",
    "Cargo.lock": "Cargo",
    "go.sum": "Go modules",
    "Gemfile.lock": "Bundler",
    "composer.lock": "Composer",
}

CONFIG_MARKERS = {
    "pyproject.toml": "Python project configuration",
    "package.json": "Node.js package manifest",
    "tsconfig.json": "TypeScript configuration",
    "biome.json": "Biome configuration",
    "biome.jsonc": "Biome configuration",
    "ruff.toml": "Ruff configuration",
    ".ruff.toml": "Ruff configuration",
    "pyrightconfig.json": "Pyright configuration",
    "mypy.ini": "mypy configuration",
    "pytest.ini": "pytest configuration",
    "vitest.config.ts": "Vitest configuration",
    "vitest.config.js": "Vitest configuration",
    "jest.config.js": "Jest configuration",
    "jest.config.ts": "Jest configuration",
    "Cargo.toml": "Rust package manifest",
    "go.mod": "Go module manifest",
    "pom.xml": "Maven project manifest",
    "build.gradle": "Gradle build file",
    "build.gradle.kts": "Gradle build file",
    "Gemfile": "Ruby dependency manifest",
    "composer.json": "PHP dependency manifest",
    "Dockerfile": "Container build definition",
    "docker-compose.yml": "Docker Compose definition",
    "docker-compose.yaml": "Docker Compose definition",
    "compose.yml": "Docker Compose definition",
    "compose.yaml": "Docker Compose definition",
}

UI_DEPENDENCY_HINTS = {
    "react",
    "next",
    "vue",
    "nuxt",
    "svelte",
    "@sveltejs/kit",
    "angular",
    "@angular/core",
    "solid-js",
    "astro",
    "vite",
}

FRAMEWORK_HINTS = {
    "next": "Next.js",
    "react": "React",
    "vue": "Vue",
    "nuxt": "Nuxt",
    "svelte": "Svelte",
    "@sveltejs/kit": "SvelteKit",
    "@angular/core": "Angular",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "pytest": "pytest",
    "vitest": "Vitest",
    "jest": "Jest",
    "express": "Express",
    "nestjs": "NestJS",
    "@nestjs/core": "NestJS",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a conservative Ragdoll Software Engineering Project Context draft."
    )
    parser.add_argument("repository", nargs="?", default=".", help="Repository root to inspect")
    parser.add_argument(
        "--output",
        help="Output Project Context root (default: <repository>/project-context)",
    )
    parser.add_argument("--project-name", help="Explicit project display name")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing generated Project Context root",
    )
    return parser.parse_args()


def iter_files(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".ragdoll-tmp")]
        current_path = Path(current)
        for name in files:
            path = current_path / name
            try:
                if path.is_symlink():
                    continue
            except OSError:
                continue
            yield path


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path, max_bytes: int = 1_000_000) -> str:
    try:
        if path.stat().st_size > max_bytes:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def detect_languages(files: list[Path]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in files:
        language = LANGUAGE_EXTENSIONS.get(path.suffix.lower())
        if language:
            counts[language] += 1
    return counts


def load_package_json(root: Path) -> dict:
    path = root / "package.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def load_pyproject(root: Path) -> dict:
    path = root / "pyproject.toml"
    if not path.exists():
        return {}
    try:
        import tomllib

        with path.open("rb") as fh:
            data = tomllib.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def collect_dependencies(package_json: dict, pyproject: dict) -> set[str]:
    deps: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        section = package_json.get(key, {})
        if isinstance(section, dict):
            deps.update(str(name).lower() for name in section)

    project = pyproject.get("project", {}) if isinstance(pyproject, dict) else {}
    if isinstance(project, dict):
        for item in project.get("dependencies", []) or []:
            if isinstance(item, str):
                name = re.split(r"[<>=!~;\s\[]", item, maxsplit=1)[0].strip().lower()
                if name:
                    deps.add(name)

    poetry = pyproject.get("tool", {}).get("poetry", {}) if isinstance(pyproject.get("tool", {}), dict) else {}
    if isinstance(poetry, dict):
        for key in ("dependencies", "group"):
            value = poetry.get(key, {})
            if isinstance(value, dict):
                if key == "dependencies":
                    deps.update(str(name).lower() for name in value)
                else:
                    for group in value.values():
                        if isinstance(group, dict):
                            group_deps = group.get("dependencies", {})
                            if isinstance(group_deps, dict):
                                deps.update(str(name).lower() for name in group_deps)
    return deps


def detect_frameworks(deps: set[str]) -> list[str]:
    found = []
    for dep, label in FRAMEWORK_HINTS.items():
        if dep in deps and label not in found:
            found.append(label)
    return found


def detect_package_managers(root: Path) -> list[tuple[str, str]]:
    found = []
    for marker, manager in PACKAGE_MANAGER_MARKERS.items():
        path = root / marker
        if path.exists():
            found.append((manager, marker))
    return found


def detect_configs(root: Path) -> list[tuple[str, str]]:
    found = []
    for marker, description in CONFIG_MARKERS.items():
        path = root / marker
        if path.exists():
            found.append((marker, description))
    github_workflows = root / ".github" / "workflows"
    if github_workflows.exists() and any(github_workflows.glob("*.y*ml")):
        found.append((".github/workflows/", "GitHub Actions workflows"))
    return found


def detect_commands(package_json: dict, pyproject: dict, managers: list[tuple[str, str]]) -> dict[str, list[str]]:
    result = {"format": [], "lint": [], "typecheck": [], "test": [], "build": []}
    scripts = package_json.get("scripts", {}) if isinstance(package_json, dict) else {}
    js_manager = next((manager for manager, _ in managers if manager in {"pnpm", "Yarn", "npm", "Bun"}), None)
    if js_manager == "pnpm":
        script_prefix = "pnpm"
    elif js_manager == "Yarn":
        script_prefix = "yarn"
    elif js_manager == "Bun":
        script_prefix = "bun run"
    else:
        script_prefix = "npm run"
    if isinstance(scripts, dict):
        for name in scripts:
            lname = name.lower()
            cmd = f"{script_prefix} {name}"
            if lname in {"format", "fmt", "format:check", "format-check"}:
                result["format"].append(cmd)
            if "lint" in lname:
                result["lint"].append(cmd)
            if "typecheck" in lname or "type-check" in lname or lname == "types":
                result["typecheck"].append(cmd)
            if lname == "test" or lname.startswith("test:"):
                result["test"].append(cmd)
            if lname == "build":
                result["build"].append(cmd)

    tool = pyproject.get("tool", {}) if isinstance(pyproject, dict) else {}
    if isinstance(tool, dict):
        if "ruff" in tool:
            result["lint"].append("ruff check .")
            result["format"].append("ruff format --check .")
        if "pytest" in tool:
            result["test"].append("pytest")
        if "mypy" in tool:
            result["typecheck"].append("mypy .")
        if "pyright" in tool:
            result["typecheck"].append("pyright")

    for key in result:
        result[key] = list(dict.fromkeys(result[key]))
    return result


def first_readme_summary(root: Path) -> tuple[str, str | None]:
    candidates = [root / "README.md", root / "README.rst", root / "README.txt", root / "README"]
    for path in candidates:
        if not path.exists():
            continue
        text = read_text(path, 200_000)
        if not text:
            continue
        lines = [line.strip() for line in text.splitlines()]
        paragraphs: list[str] = []
        current: list[str] = []
        for line in lines:
            if line.startswith("#"):
                continue
            if not line:
                if current:
                    paragraphs.append(" ".join(current))
                    current = []
                continue
            if line.startswith(("```", "[!", "<", "![]")):
                continue
            current.append(line)
            if len(" ".join(current)) > 500:
                paragraphs.append(" ".join(current))
                current = []
                break
        if current:
            paragraphs.append(" ".join(current))
        for paragraph in paragraphs:
            cleaned = re.sub(r"\s+", " ", paragraph).strip()
            if 40 <= len(cleaned) <= 800:
                return cleaned, relative(path, root)
    return "UNDECIDED - no reliable project overview was extracted automatically.", None


def project_name(root: Path, package_json: dict, pyproject: dict, explicit: str | None) -> tuple[str, str]:
    if explicit:
        return explicit.strip(), "DECLARED: --project-name argument"
    package_name = package_json.get("name") if isinstance(package_json, dict) else None
    if isinstance(package_name, str) and package_name.strip():
        return package_name.strip(), "OBSERVED: package.json name"
    project = pyproject.get("project", {}) if isinstance(pyproject, dict) else {}
    py_name = project.get("name") if isinstance(project, dict) else None
    if isinstance(py_name, str) and py_name.strip():
        return py_name.strip(), "OBSERVED: pyproject.toml project.name"
    readme = root / "README.md"
    if readme.exists():
        for line in read_text(readme, 200_000).splitlines():
            stripped = line.strip()
            if stripped.startswith("# ") and len(stripped) > 2:
                return stripped[2:].strip(), "OBSERVED: README.md H1"
    return root.name, "INFERRED: repository directory name"


def list_top_level(root: Path) -> list[str]:
    entries = []
    try:
        for path in sorted(root.iterdir(), key=lambda p: p.name.lower()):
            if path.name in IGNORED_DIRS or path.name in {"project-context"}:
                continue
            suffix = "/" if path.is_dir() else ""
            entries.append(f"`{path.name}{suffix}`")
    except OSError:
        pass
    return entries[:30]


def as_bullets(items: Iterable[str], empty: str = "- UNDECIDED") -> str:
    values = [str(item) for item in items if str(item).strip()]
    if not values:
        return empty
    return "\n".join(f"- {item}" for item in values)


def command_text(commands: list[str]) -> str:
    return "\n".join(commands) if commands else "UNDECIDED"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def build_context(root: Path, output: Path, explicit_name: str | None) -> None:
    files = list(iter_files(root))
    languages = detect_languages(files)
    package_json = load_package_json(root)
    pyproject = load_pyproject(root)
    deps = collect_dependencies(package_json, pyproject)
    frameworks = detect_frameworks(deps)
    managers = detect_package_managers(root)
    configs = detect_configs(root)
    commands = detect_commands(package_json, pyproject, managers)
    overview, overview_source = first_readme_summary(root)
    name, name_provenance = project_name(root, package_json, pyproject, explicit_name)
    top_level = list_top_level(root)
    has_ui_hint = bool(UI_DEPENDENCY_HINTS & deps) or any(
        path.suffix.lower() in {".tsx", ".jsx", ".vue", ".svelte"} for path in files
    )

    language_rows = []
    for language, count in languages.most_common(12):
        language_rows.append(f"| {language} | OBSERVED | {count} source files by extension |")
    language_table = "\n".join(language_rows) if language_rows else "| UNDECIDED | UNDECIDED | No recognized source files found |"

    framework_bullets = as_bullets(
        [f"{label} - OBSERVED from dependency manifests" for label in frameworks],
        "- UNDECIDED - no supported framework dependency was detected automatically.",
    )
    manager_bullets = as_bullets(
        [f"{manager} - OBSERVED from `{marker}`" for manager, marker in managers],
        "- UNDECIDED - no recognized package-manager marker was detected.",
    )
    config_bullets = as_bullets(
        [f"`{marker}` - {description}" for marker, description in configs],
        "- No recognized root-level engineering configuration markers detected.",
    )
    top_level_bullets = as_bullets(top_level, "- UNDECIDED")
    language_names = ", ".join(language for language, _ in languages.most_common(8)) or "UNDECIDED"

    evidence = []
    if overview_source:
        evidence.append(f"README summary from `{overview_source}`")
    if languages:
        evidence.append("source file extensions")
    if managers:
        evidence.extend(f"`{marker}`" for _, marker in managers)
    if configs:
        evidence.extend(f"`{marker}`" for marker, _ in configs[:10])
    if name_provenance.startswith("OBSERVED"):
        evidence.insert(0, name_provenance.removeprefix("OBSERVED: "))
    observed_evidence = ", ".join(dict.fromkeys(evidence)) or "repository path only"
    declared_name_evidence = (
        name_provenance.removeprefix("DECLARED: ")
        if name_provenance.startswith("DECLARED")
        else "None captured by the generator."
    )
    inferred_name_evidence = (
        name_provenance.removeprefix("INFERRED: ")
        if name_provenance.startswith("INFERRED")
        else "None captured by the generator."
    )

    domain_dir = output / DOMAIN_ID
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    manifest = f"""schema_version: 1
project:
  name: {yaml_quote(name)}
  repository_path: {yaml_quote(str(root))}
context_standard:
  id: ragdoll-context-standard
  domain: software-engineering
  domain_version: 1.1.0
status: DRAFT_REQUIRES_REVIEW
generator:
  name: ragdoll-project-context-generator
  version: {GENERATOR_VERSION}
  generated_at_utc: {yaml_quote(now)}
active_domains:
  software-engineering:
    path: software-engineering
    status: draft
provenance_policy:
  classes:
    - OBSERVED
    - DECLARED
    - INFERRED
    - UNDECIDED
  rule: Inferred claims must not silently become observed or declared.
"""
    write_file(output / "context-manifest.yaml", manifest)

    project_overview = f"""# {name}

## Overview

{overview}

## Primary Users

- UNDECIDED - requires project/product confirmation.

## Goals

1. UNDECIDED - derive from canonical requirements or user confirmation.

## Core User / System Flow

1. UNDECIDED - repository inspection does not prove product behavior.

## Observed Technology Surface

- Languages by source extension: {language_names}
{framework_bullets}

## Scope

### In Scope

- UNDECIDED - requires project/product source of truth.

### Out of Scope

- UNDECIDED - requires project/product source of truth.

## Success Criteria

1. UNDECIDED - requires canonical acceptance criteria.

## Non-Goals / Constraints

- UNDECIDED.

## Terminology

- UNDECIDED - add domain terms only when supported by project sources.

## Context Provenance

- **OBSERVED:** {observed_evidence}.
- **DECLARED:** {declared_name_evidence}
- **INFERRED:** {inferred_name_evidence}
- **UNDECIDED:** Users, goals, product scope, system flow, success criteria, and product terminology require review.
"""
    write_file(domain_dir / "project-overview.md", project_overview)

    architecture = f"""# Architecture Context

## Architectural Goal

UNDECIDED - the generator does not infer architecture style from folder names or dependencies alone.

## Observed Repository Shape

{top_level_bullets}

## Observed Stack Signals

### Languages

| Language | Evidence class | Evidence |
| --- | --- | --- |
{language_table}

### Framework / Tool Dependencies

{framework_bullets}

### Configuration Markers

{config_bullets}

## System Boundaries

UNDECIDED - identify ownership boundaries from canonical architecture docs, code dependencies, and maintainer confirmation.

## Dependency Direction

UNDECIDED - do not claim Clean Architecture, Hexagonal Architecture, DDD, MVC, microservices, or another style without stronger evidence.

## Storage and State Model

UNDECIDED - inspect actual persistence configuration and domain ownership before recording a canonical model.

## External Integrations

UNDECIDED - dependency presence alone does not prove runtime integration ownership.

## Authentication and Access Model

- Authentication: UNDECIDED
- Authorization: UNDECIDED
- Ownership/tenancy: UNDECIDED

## Deployment Shape

UNDECIDED - build/container/workflow files are evidence inputs, not proof of production deployment topology.

## Architecture Invariants

1. UNDECIDED - must come from accepted architecture decisions or verified repository constraints.

## Architecture Decisions / ADR Links

- UNDECIDED - locate accepted ADRs or decision records if present.

## Context Provenance

- **OBSERVED:** {observed_evidence}.
- **DECLARED:** None captured automatically unless present in reviewed canonical documentation.
- **INFERRED:** Framework/tool labels above are limited dependency-manifest interpretations, not architecture claims.
- **UNDECIDED:** Architecture style, boundaries, dependency direction, state ownership, auth model, deployment topology, and invariants.
"""
    write_file(domain_dir / "architecture.md", architecture)

    code_standards = f"""# Code Standards

This draft records repository-specific evidence only. Generic engineering advice should come from the shared Ragdoll engineering standard rather than being duplicated here.

## Languages

| Language | Evidence class | Evidence |
| --- | --- | --- |
{language_table}

## Package / Dependency Management

{manager_bullets}

## Framework / Tool Signals

{framework_bullets}

## Formatting, Linting, Types, Tests, and Build

### Observed configuration

{config_bullets}

### Candidate commands discovered from manifests/config

- Format:

```text
{command_text(commands['format'])}
```

- Lint:

```text
{command_text(commands['lint'])}
```

- Typecheck:

```text
{command_text(commands['typecheck'])}
```

- Test:

```text
{command_text(commands['test'])}
```

- Build:

```text
{command_text(commands['build'])}
```

Commands are observations/candidates. Run and verify them before treating them as canonical quality gates.

## Naming

- Files/directories: UNDECIDED - inspect dominant repository convention.
- Variables/functions: UNDECIDED.
- Types/classes/components: UNDECIDED.
- Constants: UNDECIDED.

## API / Interface Conventions

UNDECIDED - no API convention is inferred automatically.

## Data and Storage Conventions

UNDECIDED - no persistence convention is inferred automatically.

## UI / Styling Conventions

See `ui-context.md`. UI applicability is {'INFERRED from source/dependency signals' if has_ui_hint else 'UNDECIDED'}.

## File Organization

Observed top-level repository entries:

{top_level_bullets}

Ownership responsibilities remain UNDECIDED until verified.

## Required Quality Gate

UNDECIDED - promote commands above only after they are verified as repository policy.

## Context Provenance

- **OBSERVED:** {observed_evidence}.
- **DECLARED:** None captured automatically.
- **INFERRED:** UI applicability signal is {'present' if has_ui_hint else 'not established'}; detected framework labels come from dependencies only.
- **UNDECIDED:** Naming policy, canonical commands, API/data conventions, path ownership, and quality-gate requirements.
"""
    write_file(domain_dir / "code-standards.md", code_standards)

    workflow_rules = f"""# AI Workflow Rules

## Status

`DRAFT_REQUIRES_REVIEW`

## Default Approach

Until project-specific workflow rules are confirmed, use a conservative context-first loop:

```text
Read Project Context
  -> inspect repository
  -> frame task and unknowns
  -> implement the smallest coherent change
  -> validate with actual repository tooling
  -> review diff
  -> update Project Context when material facts changed
  -> record/retrieve prior Project History only when available and relevant
  -> report verified evidence and uncertainty
```

## Required Context Read

Before substantial Software Engineering changes, read:

1. `project-context/context-manifest.yaml`
2. `project-context/software-engineering/project-overview.md`
3. `project-context/software-engineering/architecture.md`
4. `project-context/software-engineering/code-standards.md`
5. `project-context/software-engineering/progress-tracker.md`

Read `ui-context.md` for UI work and this file for workflow/process changes.

## Default Source-of-Truth Priority

1. Explicit current user/task instruction.
2. Safety, security, privacy, legal, and data-integrity constraints.
3. Accepted ADRs and explicit project invariants.
4. Reviewed Project Context.
5. Deterministic repository configuration and current repository state.
6. Shared Ragdoll engineering defaults, when installed.
7. Existing implementation detail.
8. Model preference.

Project maintainers may replace this order with a stronger valid repository policy.

## Status Vocabulary

- **IMPLEMENTED** — implementation exists and applicable validation passes.
- **SPECIFIED** — behavior is documented but may not exist yet.
- **PLANNED** — future intended work.
- **UNDECIDED** — intentionally unresolved.
- **BLOCKED** — a prerequisite prevents safe progress.
- **DEPRECATED** — retained for compatibility/history only.

Never report SPECIFIED or PLANNED work as IMPLEMENTED.

## Protected Areas

UNDECIDED - inspect repository policy before listing protected generated/vendor/migration paths.

Never weaken tests, lint/type/security checks, CI policy, or canonical context merely to make a failing change appear correct.

## Prior Project History

If a Ragdoll Project History store is enabled, treat it as historical evidence rather than automatic current truth. Scope retrieval to this project and load only relevant evidence instead of replaying all prior conversations.

## Keeping Context in Sync

Update the owning Project Context file when product scope, architecture, repository-specific conventions, workflow rules, implementation state, or UI context materially changes.

## Before Completion

1. Acceptance criteria are satisfied or remaining gaps are explicit.
2. Applicable architecture invariants remain true.
3. Direct tests/checks actually executed are reported.
4. Full applicable repository quality gates are run when known.
5. `git diff` is reviewed for unrelated changes when Git is available.
6. Project Context is synchronized when required.
7. Unrun checks and uncertainty are stated explicitly.

## Context Provenance

- **OBSERVED:** {observed_evidence}.
- **DECLARED:** No project-specific AI workflow policy was captured automatically.
- **INFERRED:** The default workflow above is a conservative Ragdoll bootstrap, not proof of existing repository policy.
- **UNDECIDED:** Project-specific precedence, protected paths, merge policy, branch policy, and mandatory completion gates.
"""
    write_file(domain_dir / "ai-workflow-rules.md", workflow_rules)

    progress = f"""# Progress Tracker

## Current Phase

- Phase: Project Context bootstrap
- Status: DRAFT_REQUIRES_REVIEW

## Current Goal

Review generated Software Engineering Project Context against actual repository requirements, architecture, and implementation state before using it as canonical project knowledge.

## Status Vocabulary

- **IMPLEMENTED** — implementation exists and applicable validation passes.
- **SPECIFIED** — documented but not necessarily implemented.
- **PLANNED** — future intended work.
- **UNDECIDED** — intentionally unresolved.
- **BLOCKED** — a prerequisite prevents safe progress.
- **DEPRECATED** — retained for compatibility/history only.

## Completed

- IMPLEMENTED — repository evidence scan completed at {now}.
- IMPLEMENTED — six Software Engineering context draft files generated.

## In Progress

- Review OBSERVED evidence.
- Confirm or reject INFERRED statements.
- Resolve material UNDECIDED project/product/architecture facts.

## Next Up

1. Compare this draft with canonical README/docs/ADRs and current code.
2. Confirm product goals and scope.
3. Confirm architecture boundaries and invariants.
4. Run candidate validation commands before making them canonical.
5. Update this tracker with actual implementation milestones.

## Open Questions

- Project goals and acceptance criteria: UNDECIDED.
- Canonical architecture and subsystem ownership: UNDECIDED.
- Mandatory repository quality gates: UNDECIDED.
- Current feature/milestone state: UNDECIDED.

## Architecture / Product Decisions

- None recorded automatically. Add accepted decisions only after verification.

## Validation Evidence

- Context generation completed successfully.
- No source/build/test command is marked successful unless it was actually executed separately.

## Session Notes

- Generator version: {GENERATOR_VERSION}
- Repository inspected: `{root}`
- Project name source: {name_provenance}

## Context Provenance

- **OBSERVED:** {observed_evidence}.
- **DECLARED:** {declared_name_evidence}
- **INFERRED:** Repository-name/project-name interpretation where explicitly labeled.
- **UNDECIDED:** Real implementation milestone, feature status, open decisions, and verified test/build state.
"""
    write_file(domain_dir / "progress-tracker.md", progress)

    ui_status = "UNDECIDED"
    ui_evidence = "No supported UI signal was strong enough to determine applicability."
    if has_ui_hint:
        ui_status = "UNDECIDED"
        ui_evidence = "UI-related dependency/source signals exist, but a design system and product UI contract are not established automatically."

    ui_context = f"""# UI Context

## Status

`{ui_status}`

{ui_evidence}

Use `APPLICABLE`, `NOT_APPLICABLE`, or `UNDECIDED` only after repository/product review.

## Product / Design Intent

UNDECIDED.

## Theme and Tokens

UNDECIDED - do not invent colors, typography, spacing, radius, or motion tokens.

## Component Library

UNDECIDED - detected package dependencies do not automatically define project ownership/protection rules.

## Layout Patterns

UNDECIDED.

## Interaction States

When UI becomes confirmed as applicable, define default, hover, pressed, focus, selected, loading, empty, error, success, disabled, permission-restricted, overflow, and offline states as relevant.

## Accessibility

UNDECIDED - record project accessibility requirements and actual tooling before treating them as canonical.

## Responsive Behavior

UNDECIDED.

## Design Assets / References

UNDECIDED.

## Context Provenance

- **OBSERVED:** {observed_evidence}.
- **DECLARED:** No design system was captured automatically.
- **INFERRED:** UI-related signal {'exists' if has_ui_hint else 'is not established'} based on dependencies/source extensions.
- **UNDECIDED:** UI applicability, design language, tokens, component system, accessibility policy, responsive behavior, and design references.
"""
    write_file(domain_dir / "ui-context.md", ui_context)


def main() -> int:
    args = parse_args()
    root = Path(args.repository).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"error: repository directory not found: {root}", file=sys.stderr)
        return 2

    output = Path(args.output).expanduser().resolve() if args.output else root / "project-context"
    try:
        output.relative_to(root)
    except ValueError:
        pass

    if output.exists():
        if not args.force:
            print(f"error: output already exists: {output}", file=sys.stderr)
            print("use --force only when replacing a draft intentionally", file=sys.stderr)
            return 2
        if output == root:
            print("error: refusing to remove the repository root", file=sys.stderr)
            return 2
        shutil.rmtree(output)

    build_context(root, output, args.project_name)
    print(f"Generated DRAFT_REQUIRES_REVIEW Project Context: {output}")
    print("Review INFERRED and UNDECIDED claims before treating the context as canonical.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "ragdoll-product-engineering-standard"
RELEASE_VERSION = "1.0.0"
SOFTWARE_CONTEXT_FILES = {
    "project-overview.md",
    "architecture.md",
    "code-standards.md",
    "ai-workflow-rules.md",
    "progress-tracker.md",
    "ui-context.md",
}

REQUIRED = [
    ROOT / "SKILL.md",
    ROOT / "README.md",
    ROOT / "PRIVACY.md",
    ROOT / "SECURITY.md",
    ROOT / "CHANGELOG.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "ROADMAP.md",
    ROOT / "agents" / "openai.yaml",
    ROOT / ".env.example",
    ROOT / "pyproject.toml",
    ROOT / "install.sh",
    ROOT / "uninstall.sh",
    ROOT / "install.ps1",
    ROOT / "uninstall.ps1",
    ROOT / "references" / "core-principles.md",
    ROOT / "references" / "coding-standard.md",
    ROOT / "references" / "architecture-api-data.md",
    ROOT / "references" / "testing-quality.md",
    ROOT / "references" / "security-reliability.md",
    ROOT / "references" / "privacy-security.md",
    ROOT / "references" / "git-release.md",
    ROOT / "references" / "agent-behavior.md",
    ROOT / "references" / "llm-execution-policy.md",
    ROOT / "references" / "active-intelligence.md",
    ROOT / "references" / "tool-selection.md",
    ROOT / "references" / "tool-catalog.md",
    ROOT / "references" / "evolution-governance.md",
    ROOT / "references" / "sources.md",
    ROOT / "references" / "context-standard.md",
    ROOT / "references" / "project-history.md",
    ROOT / "references" / "local-first-architecture.md",
    ROOT / "references" / "local-backend.md",
    ROOT / "references" / "integration.md",
    ROOT / "references" / "antigravity.md",
    ROOT / "context-standard" / "README.md",
    ROOT / "context-standard" / "registry.yaml",
    ROOT / "context-standard" / "context-domains" / "software-engineering" / "domain.yaml",
    ROOT / "context-standard" / "context-domains" / "software-engineering" / "README.md",
    ROOT / "project-context" / "context-manifest.yaml",
    ROOT / "project-history-standard" / "README.md",
    ROOT / "project-history-standard" / "default-policy.json",
    ROOT / "project-history-standard" / "event-types.md",
    ROOT / "project-history-standard" / "schema" / "event.schema.json",
    ROOT / "project-history-standard" / "schema" / "project.schema.json",
    ROOT / "project-history-standard" / "schema" / "conversation.schema.json",
    ROOT / "docs" / "backend" / "LOCAL_BACKEND.md",
    ROOT / "docs" / "backend" / "CORE_ARCHITECTURE.md",
    ROOT / "docs" / "backend" / "API.md",
    ROOT / "docs" / "backend" / "INSTALLATION.md",
    ROOT / "docs" / "security" / "THREAT_MODEL.md",
    ROOT / "docs" / "security" / "DATA_FLOW.md",
    ROOT / "docs" / "security" / "NETWORK_POLICY.md",
    ROOT / "docs" / "security" / "SECRET_HANDLING.md",
    ROOT / "docs" / "security" / "PROVIDER_EGRESS.md",
    ROOT / "docs" / "product" / "OPEN_SOURCE_PRINCIPLES.md",
    ROOT / "docs" / "release" / "PRODUCTION_WORKFLOW.md",
    ROOT / "ragdoll" / "__init__.py",
    ROOT / "ragdoll" / "__main__.py",
    ROOT / "ragdoll" / "cli.py",
    ROOT / "ragdoll" / "config.py",
    ROOT / "ragdoll" / "context_runtime.py",
    ROOT / "ragdoll" / "env_template.py",
    ROOT / "ragdoll" / "local_security.py",
    ROOT / "ragdoll" / "providers.py",
    ROOT / "ragdoll" / "server.py",
    ROOT / "ragdoll" / "service.py",
    ROOT / "ragdoll" / "runtime.py",
    ROOT / "ragdoll" / "observability.py",
    ROOT / "ragdoll" / "py.typed",
    ROOT / "ragdoll" / "core" / "__init__.py",
    ROOT / "ragdoll" / "core" / "app.py",
    ROOT / "ragdoll" / "core" / "errors.py",
    ROOT / "ragdoll" / "core" / "validation.py",
    ROOT / "ragdoll" / "storage" / "atomic.py",
    ROOT / "ragdoll" / "storage" / "locks.py",
    ROOT / "ragdoll" / "storage" / "migrations.py",
    ROOT / "ragdoll" / "history" / "cli.py",
    ROOT / "ragdoll" / "history" / "identity.py",
    ROOT / "ragdoll" / "history" / "index.py",
    ROOT / "ragdoll" / "history" / "maintenance.py",
    ROOT / "ragdoll" / "history" / "model.py",
    ROOT / "ragdoll" / "history" / "retrieval.py",
    ROOT / "ragdoll" / "history" / "security.py",
    ROOT / "ragdoll" / "history" / "store.py",
    ROOT / "tools" / "project_history" / "cli.py",
    ROOT / "tools" / "project_history" / "store.py",
    ROOT / "tools" / "project_history" / "index.py",
    ROOT / "tools" / "project_history" / "retrieval.py",
    ROOT / "tools" / "project_history" / "security.py",
    ROOT / "scripts" / "ragdoll_history.py",
    ROOT / "scripts" / "generate_project_context.py",
    ROOT / "scripts" / "validate_project_context.py",
    ROOT / "tests" / "test_project_history.py",
    ROOT / "tests" / "test_privacy_defaults.py",
    ROOT / "tests" / "test_config.py",
    ROOT / "tests" / "test_providers.py",
    ROOT / "tests" / "test_local_server.py",
    ROOT / "tests" / "test_installer.py",
    ROOT / "tests" / "test_core_production.py",
]

errors: list[str] = []

for path in REQUIRED:
    if not path.exists():
        errors.append(f"missing required file: {path.relative_to(ROOT)}")

for retired in (ROOT / "context", ROOT / "context-system"):
    if retired.exists():
        errors.append(f"retired ambiguous path must not exist: {retired.relative_to(ROOT)}")

skill_path = ROOT / "SKILL.md"
skill = skill_path.read_text(encoding="utf-8") if skill_path.exists() else ""
if not skill.startswith("---\n"):
    errors.append("SKILL.md must start with YAML frontmatter")
if f"name: {SKILL_NAME}" not in skill:
    errors.append("SKILL.md has unexpected skill name")
frontmatter = re.match(r"^---\n(.*?)\n---", skill, re.DOTALL)
if frontmatter:
    keys = {
        line.split(":", 1)[0].strip()
        for line in frontmatter.group(1).splitlines()
        if line.strip() and not line.lstrip().startswith("#") and ":" in line
    }
    if keys != {"name", "description"}:
        errors.append(f"SKILL.md frontmatter must contain only name/description, found {sorted(keys)}")
for required_ref in (
    "references/context-standard.md",
    "references/project-history.md",
    "references/privacy-security.md",
    "references/local-first-architecture.md",
    "references/local-backend.md",
):
    if required_ref not in skill:
        errors.append(f"SKILL.md must link {required_ref}")

for ref in re.findall(r"`(references/[^`]+\.md)`", skill):
    if not (ROOT / ref).exists():
        errors.append(f"SKILL.md references missing file: {ref}")

standard_template_dir = ROOT / "context-standard" / "context-domains" / "software-engineering" / "templates"
if standard_template_dir.exists():
    actual = {p.name for p in standard_template_dir.glob("*.md")}
    if actual != SOFTWARE_CONTEXT_FILES:
        errors.append(
            "software-engineering template contract mismatch: "
            f"expected {sorted(SOFTWARE_CONTEXT_FILES)}, found {sorted(actual)}"
        )

project_context_dir = ROOT / "project-context" / "software-engineering"
if project_context_dir.exists():
    actual = {p.name for p in project_context_dir.glob("*.md")}
    if actual != SOFTWARE_CONTEXT_FILES:
        errors.append(
            "Ragdoll self-context contract mismatch: "
            f"expected {sorted(SOFTWARE_CONTEXT_FILES)}, found {sorted(actual)}"
        )

registry = ROOT / "context-standard" / "registry.yaml"
if registry.exists():
    text = registry.read_text(encoding="utf-8")
    for marker in (
        "standard_id: ragdoll-context-standard",
        "project_context_root: project-context",
        "software-engineering:",
        "version: 1.1.0",
        "context-standard/context-domains/software-engineering/domain.yaml",
    ):
        if marker not in text:
            errors.append(f"context registry missing marker: {marker}")

domain = ROOT / "context-standard" / "context-domains" / "software-engineering" / "domain.yaml"
if domain.exists():
    text = domain.read_text(encoding="utf-8")
    for filename in sorted(SOFTWARE_CONTEXT_FILES):
        if filename not in text:
            errors.append(f"software-engineering domain contract missing file: {filename}")

policy_path = ROOT / "project-history-standard" / "default-policy.json"
if policy_path.exists():
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid project history default policy JSON: {exc}")
    else:
        expected = {
            "retention": "indefinite",
            "storage": "local",
            "auto_delete": False,
            "cloud_sync": False,
            "telemetry": False,
            "network_default": "deny",
            "project_scope_default": "current_project",
            "secret_persistence": "redact",
            "uninstall_preserves_history": True,
        }
        for key, value in expected.items():
            if policy.get(key) != value:
                errors.append(f"unsafe Project History default: {key}={policy.get(key)!r}, expected {value!r}")

env_example = ROOT / ".env.example"
if env_example.exists():
    text = env_example.read_text(encoding="utf-8")
    for marker in (
        "RAGDOLL_HOST=127.0.0.1",
        "RAGDOLL_ALLOW_REMOTE_BIND=false",
        "RAGDOLL_TELEMETRY=false",
        "RAGDOLL_CLOUD_SYNC=false",
        "RAGDOLL_OUTBOUND_SECRET_POLICY=redact",
        "RAGDOLL_MAX_PROVIDER_RESPONSE_BYTES=",
        "RAGDOLL_PROVIDER_TIMEOUT_SECONDS=",
        "OPENAI_API_KEY=",
        "ANTHROPIC_API_KEY=",
        "GEMINI_API_KEY=",
    ):
        if marker not in text:
            errors.append(f".env.example missing safe/default marker: {marker}")

pyproject = ROOT / "pyproject.toml"
if pyproject.exists():
    text = pyproject.read_text(encoding="utf-8")
    for marker in (
        f'version = "{RELEASE_VERSION}"',
        'requires-python = ">=3.11"',
        'ragdoll = "ragdoll.cli:main"',
        'ragdoll-server = "ragdoll.server:main"',
    ):
        if marker not in text:
            errors.append(f"pyproject missing release/runtime marker: {marker}")

init_py = ROOT / "ragdoll" / "__init__.py"
if init_py.exists() and RELEASE_VERSION not in init_py.read_text(encoding="utf-8"):
    errors.append(f"ragdoll package version must be {RELEASE_VERSION}")

sources = ROOT / "references" / "sources.md"
if sources.exists():
    text = sources.read_text(encoding="utf-8")
    url_count = len(re.findall(r"https://", text))
    if url_count < 17:
        errors.append(f"source registry is too small for v1.0: found {url_count} https URLs")
    for source_name in (
        "OpenAI Codex",
        "OpenHands",
        "Continue CLI sessions",
        "Cline tasks",
        "Roo Code",
        "Block Braindump",
        "OpenAI Responses API",
        "Anthropic Messages API",
        "Gemini GenerateContent API",
    ):
        if source_name not in text:
            errors.append(f"reference source missing: {source_name}")

history_code = "\n".join(
    path.read_text(encoding="utf-8", errors="replace")
    for path in (ROOT / "ragdoll" / "history").glob("*.py")
) if (ROOT / "ragdoll" / "history").exists() else ""
for forbidden in ("import requests", "import httpx", "import socket", "urllib.request", "aiohttp"):
    if forbidden in history_code:
        errors.append(f"Project History implementation contains network dependency/import: {forbidden}")

provider_path = ROOT / "ragdoll" / "providers.py"
if provider_path.exists():
    text = provider_path.read_text(encoding="utf-8")
    for marker in (
        "api.openai.com",
        "api.anthropic.com",
        "generativelanguage.googleapis.com",
        '"store": False',
    ):
        if marker not in text:
            errors.append(f"provider adapter missing security/privacy marker: {marker}")

server_path = ROOT / "ragdoll" / "server.py"
if server_path.exists():
    text = server_path.read_text(encoding="utf-8")
    for marker in ("Authorization", "/v1/health", "/v1/ready", "X-Request-ID", "ThreadingHTTPServer"):
        if marker not in text:
            errors.append(f"local server missing expected marker: {marker}")

canonical_repo = "huynguyen2k5/Ragdoll-Product-Engineering-Standard"
for path in (ROOT / "install.sh", ROOT / "install.ps1", ROOT / "pyproject.toml"):
    if path.exists() and canonical_repo not in path.read_text(encoding="utf-8", errors="replace"):
        errors.append(f"canonical GitHub repository missing from {path.relative_to(ROOT)}")

config_path = ROOT / "ragdoll" / "config.py"
if config_path.exists():
    text = config_path.read_text(encoding="utf-8")
    for marker in (
        "Ragdoll Core is loopback-only",
        "RAGDOLL_ALLOW_REMOTE_BIND is reserved",
        "RAGDOLL_TELEMETRY must remain false",
        "RAGDOLL_CLOUD_SYNC must remain false",
    ):
        if marker not in text:
            errors.append(f"config missing fail-closed security marker: {marker}")

core_path = ROOT / "ragdoll" / "core" / "app.py"
if core_path.exists():
    text = core_path.read_text(encoding="utf-8")
    for marker in ("class RagdollCore", "def readiness", "def history_search", "def compile_context"):
        if marker not in text:
            errors.append(f"transport-neutral core missing marker: {marker}")

gitignore = ROOT / ".gitignore"
if gitignore.exists():
    text = gitignore.read_text(encoding="utf-8")
    if not re.search(r"(?m)^\.env$", text):
        errors.append(".gitignore must ignore .env")
else:
    errors.append("missing .gitignore")

for installer in (ROOT / "install.sh", ROOT / "uninstall.sh"):
    if installer.exists():
        first = installer.read_text(encoding="utf-8", errors="replace").splitlines()[:1]
        if not first or "sh" not in first[0]:
            errors.append(f"POSIX installer missing shell shebang: {installer.name}")

text_suffixes = {".md", ".py", ".yaml", ".yml", ".json", ".toml", ".sh", ".ps1"}
for path in ROOT.rglob("*"):
    if path.resolve() == Path(__file__).resolve():
        continue
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
        continue
    if path.suffix.lower() not in text_suffixes:
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    if "TODO" in text and path.name != "CHANGELOG.md":
        errors.append(f"unresolved TODO in {path.relative_to(ROOT)}")
    if "context-system/" in text:
        errors.append(f"stale context-system path in {path.relative_to(ROOT)}")
    if re.search(r"(?<!project-)context/manifest\.json", text):
        errors.append(f"stale context manifest path in {path.relative_to(ROOT)}")
    if re.search(r"(?<!ragdoll-)product-engineering-standard", text):
        errors.append(f"stale unbranded skill slug in {path.relative_to(ROOT)}")

if errors:
    print("Validation failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("Ragdoll Product Engineering Standard validation passed.")

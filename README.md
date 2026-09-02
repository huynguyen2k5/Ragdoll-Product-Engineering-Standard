# Ragdoll Product Engineering Standard

**Ragdoll Product Engineering Standard** is a local-first, vendor-neutral engineering standard plus a practical local backend for AI-assisted product engineering.

Ragdoll `v1.0.0` is the first production baseline. Ragdoll is dogfood-first: it is being built to make one engineer's real multi-project workflow more reliable before optimizing for broad adoption. The goal is to keep each project understandable, preserve project-specific decisions/history, reduce repeated prompting, keep AI agents aligned with repository reality, and make privacy/security behavior explicit.

Ragdoll is intended to be formally released as open source after the project owner selects an explicit license.

## What Ragdoll provides

- Universal engineering rules for coding, architecture, APIs, data, testing, security, reliability, Git, release, and AI-agent behavior.
- A domain-oriented **Ragdoll Context Standard** for durable project knowledge.
- **Project Context** instances generated and maintained per codebase.
- Six canonical Software Engineering context files as the first stable context domain.
- A conservative Project Context generator and deterministic validator.
- A local-first **Project History System** with stable project identity, append-only JSONL canonical history, hash-chain integrity, and rebuildable SQLite/FTS indexing.
- Focused/comprehensive/forensic Project History retrieval with token-budgeted evidence compilation.
- A loopback-only **Ragdoll Local Backend** exposing project/context/history/model APIs to IDE adapters and local tools.
- A transport-neutral **Ragdoll Core** shared by CLI/HTTP/future MCP adapters, with versioned local migrations, atomic metadata writes, stable errors, idempotent history append, pagination, structured local logs, and readiness checks.
- Direct BYO provider adapters for OpenAI, Anthropic, and Gemini configured through `.env`.
- Privacy/security defaults: local storage, local API token, no telemetry, no cloud sync, no Ragdoll server requirement, provider-host allowlisting, secret redaction/blocking, and no silent provider fallback.
- POSIX shell and Windows PowerShell installers that preserve local Project History on normal reinstall/uninstall.
- **Active Intelligence** for evidence-governed OSS/tool discovery.
- Google Antigravity as the first IDE evaluation target.

## What Ragdoll is not

Ragdoll is not a general-purpose coding harness. It does not own arbitrary tool execution, sandbox orchestration, multi-agent scheduling, worktree management, autonomous retries, or hidden provider reasoning.

The local backend provides context/history/model plumbing so IDE adapters can use Ragdoll consistently without requiring hosted Ragdoll infrastructure.

```text
Ragdoll engineering standard
  -> how engineering should be performed

Ragdoll Context + History
  -> what the project is and what happened while working on it

Ragdoll Local Backend
  -> local API for context/history/retrieval/direct BYO model calls

General-purpose harness
  -> agent/tool orchestration beyond Ragdoll's current scope
```

## Install

Ragdoll requires **Python 3.11+** and intentionally has no third-party Python runtime dependency in v1.0.

### One-line install from GitHub Releases

Ragdoll supports the same bootstrap style used by modern developer CLIs. The canonical installer resolves a GitHub Release, downloads the Ragdoll source artifact, verifies it against the release `SHA256SUMS`, and only then runs the local installer.

Linux / macOS / POSIX shell:

```bash
curl -fsSL https://raw.githubusercontent.com/huynguyen2k5/Ragdoll-Product-Engineering-Standard/main/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/huynguyen2k5/Ragdoll-Product-Engineering-Standard/main/install.ps1 | iex
```

Install a specific release instead of `latest` by setting `RAGDOLL_VERSION`, for example `v1.0.0`. Re-running the installer acts as an upgrade: runtime files are replaced, while the user's `.env`, API token, indexes, projects, and Project History are preserved.

### Install from a cloned repository

Linux / macOS:

```bash
./install.sh
```

Windows PowerShell:

```powershell
.\install.ps1
```

The installer creates a local runtime plus:

```text
~/.ragdoll/.env
~/.ragdoll/api-token
~/.ragdoll/projects/
~/.ragdoll/indexes/
```

On POSIX systems the command shim defaults to `~/.local/bin/ragdoll`. On Windows it defaults to `%LOCALAPPDATA%\Ragdoll\bin\ragdoll.cmd` and the installer adds that directory to the user PATH when necessary.

Normal reinstall/uninstall preserves Project History and configuration. Permanent deletion requires an explicit purge option. Read `docs/backend/INSTALLATION.md` for install, upgrade, checksum, and uninstall details.

## Configure `.env`

Edit the Ragdoll-owned `~/.ragdoll/.env`. Ragdoll intentionally does **not** auto-read a project workspace's generic `.env`, because that file often contains unrelated application secrets. Use `--env-file` or `RAGDOLL_ENV_FILE` only when you explicitly want a different file. Process environment variables override loaded file values.

Only the provider key you actually use is required:

```env
RAGDOLL_PROVIDER=auto

OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
```

Optional model overrides:

```env
OPENAI_MODEL=gpt-5.6
ANTHROPIC_MODEL=claude-sonnet-5
GEMINI_MODEL=gemini-3.6-flash
```

These aliases are the v1.0.0 release defaults verified against primary provider documentation. They are configuration, not hard requirements: override them in the Ragdoll-owned `.env` when your account, region, or production pinning policy requires another model.

Security defaults:

```env
RAGDOLL_HOST=127.0.0.1
RAGDOLL_ALLOW_REMOTE_BIND=false
RAGDOLL_OUTBOUND_SECRET_POLICY=redact
RAGDOLL_TELEMETRY=false
RAGDOLL_CLOUD_SYNC=false
```

`RAGDOLL_PROVIDER=auto` chooses the first configured provider deterministically. Ragdoll does not silently retry a failed request through a different provider.

## Start the local backend

```text
ragdoll init
ragdoll doctor
ragdoll start
ragdoll status
```

Foreground mode:

```text
ragdoll start --foreground
```

or:

```text
ragdoll serve
```

Default API:

```text
http://127.0.0.1:8765
```

`GET /v1/health` and `GET /v1/ready` are the only unauthenticated loopback probes. Other endpoints require the random local token stored at `~/.ragdoll/api-token`. IDE adapters can obtain it with:

```text
ragdoll token
```

Read `docs/backend/LOCAL_BACKEND.md` and `docs/backend/API.md`.

## First project

Register the workspace:

```text
ragdoll project register . --name "My Project"
```

The result contains a stable `project_id` such as:

```text
prj_...
```

Generate a conservative Project Context draft:

```text
ragdoll context generate --project prj_...
ragdoll context validate --project prj_...
```

Project Context is created inside the target repository:

```text
project-context/
├── context-manifest.yaml
└── software-engineering/
    ├── project-overview.md
    ├── architecture.md
    ├── code-standards.md
    ├── ai-workflow-rules.md
    ├── progress-tracker.md
    └── ui-context.md
```

Generated claims use:

- `OBSERVED` - verified from repository/config/tool output;
- `DECLARED` - explicitly established by the user or accepted canonical docs;
- `INFERRED` - supported interpretation, not canonical fact;
- `UNDECIDED` - insufficient evidence or intentionally open.

Generated context starts as `DRAFT_REQUIRES_REVIEW`.

## Project History

Project History is separate from Project Context.

```text
Project Context
  = what the project currently is

Project History
  = what happened while humans and AI worked on it
```

Default storage:

```text
~/.ragdoll/
├── projects/
│   ├── registry.json
│   └── <project-id>/
│       ├── project.json
│       └── conversations/
│           └── <conversation-id>/
│               ├── conversation.json
│               └── events.jsonl
└── indexes/
    └── history.sqlite3
```

Canonical `events.jsonl` is append-only and hash-chained. SQLite/FTS is derived and rebuildable.

The default policy is:

```text
retention: indefinite
storage: local
cloud_sync: false
telemetry: false
project_scope_default: current_project
secret_persistence: redact
uninstall_preserves_history: true
```

The compatibility history CLI remains available:

```text
ragdoll history register-project . --name "My Project"
ragdoll history start-conversation --project prj_... --title "Implement auth"
ragdoll history append --project prj_... --conversation conv_... --type decision.recorded --text "Use local SQLite indexing"
ragdoll history search --project prj_... --query "SQLite indexing" --mode focused --token-budget 2500
ragdoll history verify --project prj_... --conversation conv_...
ragdoll history rebuild-index
```

## Token-efficient runtime context

Ragdoll follows:

> **Store durable history locally; load only the minimum sufficient evidence.**

For a model call, Ragdoll locally compiles selected Project Context plus relevant Project History under independent token budgets. It does not replay years of chat history for routine tasks.

```text
full local Project History
          |
          v
project-scoped retrieval
          |
          v
selected evidence under token budget
          |
          + selected Project Context sections
          |
          v
outbound secret gate
          |
          v
user-selected provider
```

Inspect what Ragdoll would compile without making a provider call:

```text
ragdoll context compile --project prj_... --prompt "Review the authentication architecture"
```

## Production Core architecture

Ragdoll v1.0 separates transport from business logic:

```text
CLI             HTTP             future MCP
 |               |                   |
 +---------------+-------------------+
                 |
                 v
           RagdollCore
                 |
     +-----------+-----------+
     |           |           |
  Project     Context      History
                             |
                      canonical JSONL
                             |
                      derived SQLite/FTS
```

Key production contracts:

- canonical history is durable before derived indexing;
- failed indexing marks the index dirty and remains rebuildable;
- local home and SQLite schemas are versioned and fail closed on unsupported/corrupt migration state;
- event writers can use idempotency keys so transport retries do not duplicate history;
- Project Context `--force` regeneration backs up the previous maintained context first;
- HTTP uses bounded requests, stable JSON errors, request IDs, security headers, and local structured logs;
- provider egress is HTTPS-only, fixed-host allowlisted, redirect-denied, timeout-bounded, and response-size-bounded;
- the built-in HTTP transport is loopback-only; remote bind is reserved for a future authenticated TLS transport.

See `docs/backend/CORE_ARCHITECTURE.md`.

## Direct model call

Once one provider key is configured:

```text
ragdoll chat "Explain the current architecture decision" --project prj_...
```

The request flow is:

```text
prompt
  -> local Project Context selection
  -> local Project History retrieval
  -> token-budgeted runtime context
  -> secret redaction/blocking
  -> selected provider only
  -> observable response persisted to the same project's history
```

OpenAI requests use the Responses API with `store=false`. Gemini requests use the `models.generateContent` API with `store=false`. Anthropic requests use the Messages API. Provider calls go directly from the user's machine to the selected provider; Ragdoll operates no model proxy.

## Local API surface

Core endpoints include:

```text
GET  /v1/health
GET  /v1/ready
GET  /v1/status
GET  /v1/providers
POST /v1/projects
GET  /v1/projects
POST /v1/projects/{id}/conversations
POST /v1/projects/{id}/conversations/{conversation}/events
POST /v1/projects/{id}/history/search
POST /v1/projects/{id}/context/generate
POST /v1/projects/{id}/context/validate
POST /v1/projects/{id}/context/compile
POST /v1/history/rebuild-index
POST /v1/chat
```

See `docs/backend/API.md` for the complete current surface.

## Privacy and security

Core posture:

> **Local by default. Network by permission. User data remains user-owned.**

Ragdoll does not require a Ragdoll-operated backend, account, storage service, vector database, or model proxy.

Provider egress is restricted to the built-in provider hosts:

```text
api.openai.com
api.anthropic.com
generativelanguage.googleapis.com
```

Provider adapters reject non-HTTPS/non-allowlisted hosts. Common secret-like values are redacted before persistence and before provider egress by default. `RAGDOLL_OUTBOUND_SECRET_POLICY=block` can reject an outbound request instead.

Cloud-model permission is not authorization for arbitrary browser access, package installation, Git push, telemetry, or history synchronization.

Read `PRIVACY.md`, `SECURITY.md`, `docs/security/`, and `references/privacy-security.md`.

## Four different kinds of context

Do not mix these concepts:

```text
references/
  = reusable engineering rules

context-standard/
  = public protocol/templates for project knowledge

project-context/
  = maintained canonical context of one project

Project History (~/.ragdoll)
  = durable local evidence of previous work

Runtime context
  = minimum selected information for the current model invocation
```

## Context Standard

```text
context-standard/
├── registry.yaml
└── context-domains/
    └── software-engineering/
        ├── domain.yaml
        └── templates/
            ├── project-overview.md
            ├── architecture.md
            ├── code-standards.md
            ├── ai-workflow-rules.md
            ├── progress-tracker.md
            └── ui-context.md
```

`software-engineering` is only the first domain. Future real use cases may introduce different contracts without forcing these six files on every discipline.

## Sustainable open-source architecture

Ragdoll intentionally distributes storage/compute to user-owned environments:

```text
more OSS users
!=
more mandatory Ragdoll infrastructure bills
```

Defaults favor local files, SQLite, local retrieval, BYO model providers, and no mandatory account.

Future paid capabilities, if ever justified by real demand, should monetize hosted convenience, collaboration, organization-scale knowledge, governance, or managed services rather than intentionally crippling local ownership of Project Context/History.

## Antigravity-first dogfooding

Google Antigravity remains the first IDE evaluation target.

The local backend now provides the endpoint needed for an IDE adapter to register projects, append observable conversation/tool events, retrieve history, compile context, and call a configured provider. **Automatic full Antigravity conversation capture is not yet claimed as implemented** because that requires a verified Antigravity event/hook source.

See `integrations/antigravity/README.md`.

## Active Intelligence

When an external tool/repository could materially improve a task:

```text
Discover
  -> Evaluate
  -> Experiment
  -> Adopt
  -> Codify
  -> Re-evaluate
```

Trending status and stars are discovery signals only. Evaluate fit, maintenance, security/supply-chain risk, license, compatibility, documentation/tests, integration cost, adoption, and reversibility.

## Repository layout

```text
.
├── ragdoll/                         # production Core + local adapters
│   ├── core/                        # transport-neutral application boundary
│   ├── history/                     # canonical local history implementation
│   └── storage/                     # atomic IO, locks, local migrations
├── tools/project_history/           # legacy compatibility wrappers retained for v1.0
├── scripts/                         # validators/generator/compat utilities
├── tests/
├── docs/release/                  # protected-main PR/release workflow
├── install.sh
├── install.ps1
├── uninstall.sh
├── uninstall.ps1
├── .env.example
├── pyproject.toml
├── context-standard/
├── project-context/
├── project-history-standard/
├── references/
├── docs/
│   ├── backend/
│   ├── security/
│   └── product/
├── integrations/antigravity/
├── assets/adapters/
├── SKILL.md
└── agents/openai.yaml
```

## Validate Ragdoll

```text
python scripts/validate_skill_pack.py
python scripts/validate_project_context.py .
python scripts/evaluate_candidate.py scripts/candidate.example.json
python -m unittest discover -s tests -v
python -m compileall -q ragdoll scripts tools tests
sh -n install.sh
sh -n uninstall.sh
```

The test suite covers Core/storage migrations, Project History isolation/integrity/idempotency/retrieval, privacy defaults, strict `.env` loading, provider request contracts, loopback API authentication/error behavior, Project Context backup/regeneration, and installer preservation behavior.

PowerShell installation is included but should still be validated on a clean Windows machine before broad promotion.

## Current development priority

1. Dogfood the local backend on real product work.
2. Connect Antigravity observable events to the local API when a stable hook/event source is verified.
3. Measure where Project Context and Project History reduce repeated prompting or architecture drift.
4. Harden retrieval only from observed misses/false positives.
5. Validate clean Windows installation and real provider calls with user-owned keys.
6. Select an explicit open-source license.
7. Push the validated v1.0 source/tag to the canonical GitHub repository and exercise release installation.
8. Add MCP only after Core dogfooding confirms the service contracts are stable enough; keep IDE plugins deferred.
9. Defer hosted/team/commercial infrastructure until real demand exists.

## License status

An explicit open-source license remains a release blocker and has not been selected silently because license choice is a legal/project-governance decision. Select and add the license before presenting Ragdoll as formally licensed open source.

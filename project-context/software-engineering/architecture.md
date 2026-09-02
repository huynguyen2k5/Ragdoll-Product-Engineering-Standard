# Architecture Context

## Architectural Goal

Ragdoll provides a vendor-neutral engineering standard plus local-first project knowledge infrastructure that can be used from multiple IDEs/agents without requiring Ragdoll-operated cloud infrastructure. The production Core must remain transport-neutral so CLI, HTTP, and future MCP adapters share one set of business rules.

## System Shape

```text
CLI              HTTP              future MCP
 |                |                    |
 +----------------+--------------------+
                  |
                  v
             RagdollCore
                  |
     +------------+-------------+----------------+
     |                          |                |
     v                          v                v
 Project identity/context   Project History   Provider edge
                               |
                         canonical JSONL
                               |
                         derived SQLite/FTS
                  |
            Runtime Context Compiler
                  |
             security/egress gate
```

The runtime is user-operated local software, not a Ragdoll-hosted service.

## Core Repository Components

- `SKILL.md` - compact agent control plane.
- `references/` - canonical reusable engineering behavior.
- `context-standard/` - reusable context-domain protocol/templates.
- `project-context/` - canonical context for this Ragdoll repository.
- `project-history-standard/` - durable per-project history contract.
- `ragdoll/core/` - transport-neutral application boundary and stable error/validation contracts.
- `ragdoll/history/` - production local history identity/storage/index/retrieval implementation.
- `ragdoll/storage/` - atomic metadata I/O, local lock files, and local data migrations.
- `ragdoll/` top-level adapters - CLI, HTTP server, provider edge, runtime lifecycle, config, context compiler, and observability.
- `tools/project_history/` - legacy compatibility wrappers retained for v1.0; new code must not treat this as the canonical implementation.
- `scripts/` - validators/generator/release tooling and compatibility entrypoints.
- `install.sh` / `install.ps1` - local runtime installers and GitHub Release bootstrap.
- `uninstall.sh` / `uninstall.ps1` - runtime removal with data preservation by default.
- `integrations/` and `assets/adapters/` - thin IDE/agent-specific integration material.
- `tests/` - deterministic unit/integration/contract tests.

## Local Data Model

```text
~/.ragdoll/
├── .env
├── api-token
├── state.json
├── backups/
├── indexes/
│   ├── history.sqlite3
│   └── history.dirty         # exists only when derived indexing needs rebuild
├── logs/
├── projects/
│   ├── registry.json
│   └── <project-id>/
│       ├── project.json
│       └── conversations/
│           └── <conversation-id>/
│               ├── conversation.json
│               └── events.jsonl
└── runtime/
    ├── app/                  # replaceable installed runtime
    └── server.pid.json
```

Runtime code is replaceable. Project/history/configuration data is outside the replaceable runtime so normal upgrade/uninstall cannot destroy it.

## Canonical and Derived State

Project History `events.jsonl` is canonical append-only evidence. SQLite/FTS is derived state and may be deleted/rebuilt from canonical event logs.

Canonical event append is flushed/fsynced before derived indexing. If indexing fails after durable append, the request remains successful and `history.dirty` is written so the index can be rebuilt without inducing duplicate retries.

Small Ragdoll-owned metadata files use temp-write + fsync + atomic replace. Existing migration/registry metadata that is malformed fails closed rather than silently resetting user state.

## Migration Model

`~/.ragdoll/state.json` versions the Ragdoll home layout. A runtime refuses to operate on a newer schema it cannot understand.

SQLite has an independent migration table and current derived-index schema version. Derived migrations must never rewrite canonical history. Conversation metadata is indexed separately for normal pagination; filesystem scans are recovery fallbacks when the derived index is dirty or unavailable.

## Project Identity

A project has a stable local `project_id` independent of a single workspace path. Identity uses normalized Git remote when available and tracks known workspaces/root-commit evidence. Moving a checkout must not silently create unrelated project history when identity evidence matches.

## Project History Storage

Canonical history is append-only JSONL with a per-conversation hash chain. Event writers may supply an `idempotency_key`; a transport retry with the same key in the same project/conversation returns the original event instead of duplicating canonical history.

History is retained indefinitely by default. Purge requires an explicit action and exact project-ID confirmation.

## Retrieval

- `focused` - token-efficient default retrieval.
- `comprehensive` - broad search when the user asks for all matching history.
- `forensic` - indexed matches expanded with neighboring canonical events for traceability.

All Core retrieval is scoped to one project. Runtime context uses a token budget after retrieval and never treats summaries/indexes as replacements for raw history.

## Local HTTP Backend

Default endpoint:

```text
http://127.0.0.1:8765
```

Security boundary:

- `/v1/health` is public loopback liveness;
- `/v1/ready` is public loopback readiness with no project/path disclosure;
- all other endpoints require a random local bearer token;
- browser origins must be local;
- CORS is not enabled;
- request path/body sizes are bounded;
- non-empty request bodies require JSON;
- transfer-encoded request bodies are rejected;
- responses use no-store/security headers and request IDs;
- built-in HTTP is loopback-only; remote bind is not supported by Core.

`RAGDOLL_ALLOW_REMOTE_BIND=true` is reserved for a future authenticated TLS transport and currently fails closed.

## Error and Observability Model

Core raises stable machine-readable errors independent of transport. HTTP maps them to a consistent JSON envelope. Unexpected errors return generic client text rather than arbitrary exception details.

Backend logs are local structured JSON and contain request/lifecycle metadata such as request ID, method, path, status, duration, and safe exception type. They must not intentionally log credentials, bearer tokens, prompt/source/history bodies, or provider response bodies.

## Provider Boundary

Ragdoll never bundles or subsidizes model credentials.

v1.0 built-in provider adapters:

- OpenAI Responses API;
- Anthropic Messages API;
- Gemini `models.generateContent` API.

Provider requests are direct from the user's machine, HTTPS-only, fixed-host allowlisted, redirect-denied, timeout-bounded, and response-size-bounded. A failed provider request never silently falls back to another provider.

OpenAI and Gemini requests use `store=false`; provider-hosted conversation state is not canonical Project History.

Provider keys come from the Ragdoll-owned `.env` or process environment and are excluded from history/status output.

## Dependency Direction

- Engineering rules do not depend on an IDE/provider.
- Project Context does not depend on Project History.
- Canonical Project History does not depend on SQLite availability.
- Derived index/retrieval depends on canonical history, never the reverse.
- `RagdollCore` owns application-level orchestration; CLI/HTTP/future MCP are adapters.
- Installable runtime modules must depend only on modules inside the `ragdoll` package (or declared runtime packages); top-level `scripts/` are CLI/development wrappers, never runtime dependencies.
- Adapters must not reach around Core to redefine storage/security semantics.
- Provider adapters are optional egress edges; local context/history remains usable with no provider key.
- No component requires Ragdoll-operated hosted infrastructure.

## Architecture Invariants

1. **Ragdoll is independent.** Do not couple identity/scope to unrelated projects.
2. **Ragdoll is not a general-purpose harness.** Context/history/provider plumbing does not own arbitrary agent/tool orchestration.
3. **One Core, many thin adapters.** CLI/HTTP/future MCP must share transport-neutral business logic.
4. **Project Context != Project History.** Current truth and historical evidence have distinct authority/lifecycle.
5. **Context Standard != Project Context.** Reusable protocol and project instance are distinct.
6. **Canonical History != index.** Indexes are disposable/rebuildable.
7. **Durable append before derived indexing.** Index failure must not invite duplicate canonical writes.
8. **Retry-safe observable events.** Idempotency keys are supported when adapters can retry.
9. **Version local state.** Unsupported/corrupt migration metadata fails closed.
10. **Retention is indefinite by default.** Normal lifecycle actions do not delete canonical history.
11. **Project isolation is default.** No silent cross-project retrieval.
12. **Local-first.** Core storage/retrieval/context compilation require no Ragdoll-operated infrastructure.
13. **Loopback-only HTTP.** Plaintext remote bearer-token transport is not supported.
14. **Network by permission.** Cloud-model permission does not authorize unrelated network activity.
15. **No telemetry/cloud sync by default.** v1.0 implements neither transport.
16. **Provider neutrality.** No bundled/subsidized credentials and no silent fallback.
17. **Minimum necessary disclosure.** Cloud context is selected/sanitized locally.
18. **Secrets are not status/log data.** Credentials/tokens are never exposed via safe status and must not be intentionally logged.
19. **No speculative infrastructure.** Hosted/vector/team systems require demonstrated need.
20. **Protocol before plugins.** Prefer Core/API/MCP-level integrations; IDE plugins remain deferred until necessary.
21. **No fake history support.** Automatic IDE capture is IMPLEMENTED only when observable adapter behavior exists and is tested.

## Current Implementation Boundary

Implemented:

- Engineering/Context Standard and self Project Context;
- conservative context generator/validator with backup before forced regeneration;
- production `RagdollCore` application boundary;
- versioned home/index schemas and atomic metadata writes;
- stable project identity and Project History storage/index/retrieval;
- hash-chain verification, event pagination, idempotent append, dirty-index recovery;
- loopback authenticated HTTP adapter with readiness, request IDs, stable errors, local structured logs;
- CLI/runtime lifecycle and installers;
- direct BYO OpenAI/Anthropic/Gemini adapters with outbound safeguards;
- GitHub Actions validation/release contracts;
- cross-platform test matrix configuration.

Not yet implemented/verified as a complete integration:

- automatic full Antigravity conversation/tool capture;
- MCP adapter (planned after Core dogfooding; plugin work deferred);
- real provider calls in CI (CI does not consume private keys/quota);
- clean Windows runtime verification outside CI until the GitHub matrix runs on the canonical repository;
- hosted sync/team/commercial backend;
- mandatory semantic/vector index.

## Context Provenance

- **OBSERVED:** production Core/storage/history modules, compatibility wrappers, local HTTP/CLI adapters, migrations, installers, tests, and CI/release workflows exist in the repository.
- **DECLARED:** local-first privacy, indefinite history, token efficiency, project isolation, zero mandatory hosted infrastructure, Core-first architecture, MCP-before-plugin direction, and dogfood-first development are required constraints.
- **INFERRED:** MCP is the next high-leverage generic integration after v1.0 Core stability is proven in daily use.
- **UNDECIDED:** explicit OSS license, future local-model adapter contract, encrypted exact-secret history mode, optional semantic retrieval, sync format, and second Context Standard domain.

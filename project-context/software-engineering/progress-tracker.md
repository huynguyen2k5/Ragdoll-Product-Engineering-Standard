# Progress Tracker

## Current Phase

- Phase: v1.0 - Production baseline
- Status: VERIFIED locally; awaiting canonical GitHub PR/CI publication

## Current Goal

Make the Ragdoll Core safe and maintainable enough for daily dogfooding and future protocol adapters: one transport-neutral application boundary, crash-resistant local state, explicit migrations, retry-safe Project History, stable API errors, bounded provider egress, deterministic tests, cross-platform CI, and no mandatory hosted dependency.

## Status Vocabulary

- **IMPLEMENTED** - artifact/code exists and applicable checks pass.
- **VERIFIED** - implemented behavior has direct passing evidence from applicable checks/environment.
- **SPECIFIED** - contract exists but runtime/integration behavior may not.
- **PLANNED** - intended future work.
- **UNDECIDED** - intentionally unresolved.
- **BLOCKED** - prerequisite prevents safe progress.
- **DEPRECATED** - retained only for history/compatibility.

## Completed

- IMPLEMENTED - reusable Ragdoll Engineering Standard and Context Standard.
- IMPLEMENTED - Software Engineering Project Context generator/validator and Ragdoll self-context.
- IMPLEMENTED - Project History Standard separated from Project Context.
- IMPLEMENTED - stable project registry and project-scoped conversations.
- IMPLEMENTED - append-only JSONL history with event hash chains and verification.
- IMPLEMENTED - rebuildable SQLite/FTS index with schema migrations/integrity status.
- IMPLEMENTED - focused/comprehensive/forensic retrieval and token-budgeted evidence compilation.
- IMPLEMENTED - transport-neutral `RagdollCore` shared by CLI/HTTP and intended for future MCP.
- IMPLEMENTED - stable Core error/validation contract.
- IMPLEMENTED - versioned Ragdoll home schema with fail-closed newer/corrupt-state behavior.
- IMPLEMENTED - atomic fsync/replace metadata writes and guarded metadata lock files.
- IMPLEMENTED - idempotent Project History event append for retrying adapters.
- IMPLEMENTED - paginated event/conversation APIs.
- IMPLEMENTED - canonical-append-before-index behavior and dirty-index marker/rebuild path.
- IMPLEMENTED - forced Project Context regeneration backs up prior maintained context.
- IMPLEMENTED - loopback-only HTTP backend with local bearer authentication and local-origin guard.
- IMPLEMENTED - public liveness/readiness probes without project/path disclosure.
- IMPLEMENTED - bounded JSON requests, request IDs, stable JSON errors, no-store/security headers.
- IMPLEMENTED - local structured request/lifecycle logging with privacy-safe fields.
- IMPLEMENTED - strict Ragdoll-owned `.env` parsing/config precedence with fail-closed unsafe settings.
- IMPLEMENTED - direct BYO OpenAI/Anthropic/Gemini provider adapters.
- IMPLEMENTED - HTTPS/fixed-host allowlist, redirect denial, provider timeout, response-size bound, outbound secret gate, no silent fallback.
- IMPLEMENTED - CLI lifecycle/project/context/history/direct-chat operations.
- IMPLEMENTED - POSIX + PowerShell installer/uninstaller source with persistent-data preservation.
- IMPLEMENTED - canonical one-line GitHub bootstrap defaults to `huynguyen2k5/Ragdoll-Product-Engineering-Standard` and verifies SHA-256 release assets.
- IMPLEMENTED - deterministic release ZIP/SHA256SUMS builder.
- IMPLEMENTED - GitHub Actions validation matrix for Ubuntu/Windows/macOS and Python 3.11/3.12/3.13.
- IMPLEMENTED - tag/version-gated GitHub Release workflow, Dependabot config, and CODEOWNERS.
- IMPLEMENTED - `tools/project_history` compatibility wrappers while production implementation lives under `ragdoll.history`.
- IMPLEMENTED - production Core/API/installation/security documentation.

## Specified / not yet fully verified

- SPECIFIED - automatic Antigravity observable conversation/tool capture into Project History.
- PLANNED - MCP adapter after Core daily dogfooding proves service contracts; plugins deferred.
- SPECIFIED - clean Windows PowerShell runtime behavior; source/tests/CI matrix exist, but current Linux execution environment cannot itself run a clean Windows install.
- SPECIFIED - future outbound-data audit/egress ledger beyond safe local request metadata.

## In Progress

- Prepare the verified v1.0 source as short-lived production PR changes for the canonical GitHub repository.
- Run canonical GitHub cross-platform CI after each merged PR.
- Create the `v1.0.0` release tag only from validated `main` after the intended PRs are merged.

## Next Up

1. Land the v1.0 production changes through numbered GitHub PRs into protected `main`, then create/push `v1.0.0` and let the cross-platform release workflow run.
2. Install the published release on the maintainer's actual Windows development machine with the PowerShell one-liner.
3. Configure one user-owned provider key and run a real low-cost provider smoke request.
4. Dogfood Ragdoll across multiple independent real projects and record friction/retrieval misses.
5. Verify an observable Antigravity hook/event source before implementing automatic capture.
6. Build an MCP adapter only after Core contracts survive dogfooding; keep IDE plugins deferred until a concrete need appears.
7. Select an explicit open-source license before presenting Ragdoll as formally licensed OSS.

## Open Questions

### Open-source license

- Status: UNDECIDED / blocker for formally licensed OSS.
- Candidates remain owner-selected; do not silently choose a legal license.

### Automatic Antigravity history capture

- Status: SPECIFIED.
- Core capture API exists; verified Antigravity event source/hook is still required.

### MCP

- Status: PLANNED.
- Direction: thin protocol adapter over `RagdollCore`, no duplicate history/context/security implementation.

### IDE plugins

- Status: DEFERRED.
- Build only if protocol-level integrations cannot provide required UX/hooks.

### Local-model adapter / exact encrypted history / second domain

- Status: UNDECIDED.
- Add only after actual dogfooding creates a concrete requirement.

## Architecture / Product Decisions

### DEC-001 - Ragdoll is not a general-purpose harness

Local context/history/provider plumbing is in scope; arbitrary agent/tool orchestration is out of scope.

### DEC-002 - Domain-oriented Context Standard

Software Engineering's six files are not universal across future domains.

### DEC-003 - Project Context and Project History are separate

Current project truth and historical evidence have different authority/lifecycle.

### DEC-004 - Canonical history is append-only local data

SQLite/search/summaries are derived and rebuildable.

### DEC-005 - History retention is indefinite by default

No age-based auto-delete. Normal upgrades/uninstall preserve data; explicit purge is separate.

### DEC-006 - Project isolation is default

No silent cross-project retrieval.

### DEC-007 - Local-first privacy and sustainable OSS cost

No mandatory Ragdoll backend, telemetry, hosted sync, provider subsidy, or maintainer-funded user storage/compute.

### DEC-008 - Dogfood before commercialization

Do not build SaaS/billing/team infrastructure before the local workflow creates recurring value.

### DEC-009 - One Core, many thin adapters

CLI/HTTP/future MCP call `RagdollCore`. Plugin-specific logic must not fork business rules.

### DEC-010 - Canonical append wins over derived indexing

Once JSONL is durable, an index failure marks derived state dirty instead of converting success into a retryable append failure.

### DEC-011 - Explicit local migrations

Home/index schema versions are machine-readable; newer/corrupt migration state fails closed.

### DEC-012 - Idempotency is part of the adapter contract

Adapters that may retry event delivery should send stable idempotency keys; Ragdoll does not deduplicate by fuzzy content.

### DEC-013 - Loopback-only Core HTTP

Plaintext remote bearer-token transport is rejected. Future remote access requires an explicit authenticated TLS design.

### DEC-014 - Provider calls are direct, explicit, and bounded

HTTPS allowlist, redirect denial, timeout/response limits, outbound secret policy, and no silent provider fallback are required.

### DEC-015 - Remote install is release-verified

One-line installation verifies the downloaded canonical release ZIP against `SHA256SUMS`; reinstall updates runtime without deleting user data.

### DEC-016 - Protocol before plugins

MCP is the next generic integration candidate after Core dogfooding. IDE-specific plugins remain deferred until clearly necessary.

## Validation Evidence Target for v1.0.0

- repository validator;
- self Project Context validator;
- generator + candidate evaluator smoke checks;
- complete Python test suite;
- Python compileall;
- POSIX shell syntax checks;
- install/doctor/start/status/stop/uninstall preservation lifecycle from release artifact;
- provider request-contract tests without real API quota;
- deterministic release ZIP + SHA256SUMS verification;
- Skill Creator validation/package;
- Git clean-tree/diff review before commit/tag.

Windows runtime behavior is intended to be exercised by the GitHub Windows CI matrix and then by maintainer dogfooding on a real Windows machine.

## Session Notes

- Canonical repo: `https://github.com/huynguyen2k5/Ragdoll-Product-Engineering-Standard.git`.
- Current target: maintainer's own multi-project product engineering workflow.
- Public Context protocol: `context-standard/`.
- Current repository context: `project-context/`.
- Local Project History contract: `project-history-standard/`.
- Production history implementation: `ragdoll/history/`.
- Transport-neutral application boundary: `ragdoll/core/`.
- User data root: `~/.ragdoll` by default.
- Replaceable runtime: `~/.ragdoll/runtime/app`.
- Local API default: `127.0.0.1:8765`.
- API/model keys remain user-owned; Ragdoll operates no required model proxy/server.

## Context Provenance

- **OBSERVED:** v1.0 Core/storage/history/adapter/installer/test/CI artifacts exist; repository/context validators, 47 automated tests (1 Windows-only skip in Linux), compile checks, deterministic release checksum verification, and release-artifact install/start/status/stop smoke tests pass locally.
- **DECLARED:** Core quality, daily dogfooding, local-first privacy, indefinite history, token efficiency, low maintainer infrastructure cost, MCP-before-plugin direction, and canonical GitHub publication are current priorities.
- **INFERRED:** cross-platform GitHub CI and real Windows dogfooding are the most useful next verification after local v1.0 checks.
- **UNDECIDED:** license, local-model adapter, encrypted exact-history mode, second context domain, and future commercial services.

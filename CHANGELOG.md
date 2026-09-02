# Changelog

## 1.0.0 - 2026-09-02

- Declared `v1.0.0` as the first production baseline for the public Ragdoll Core contract and SemVer line.
- Formalized the protected-`main` production workflow: one coherent change per short-lived branch/PR, GitHub-assigned PR numbers, required validation, Squash-and-merge, and release tags only from validated `main`.
- Introduced transport-neutral `RagdollCore` so CLI, HTTP, and future MCP adapters share one application/business-rule boundary.
- Moved the production Project History implementation under `ragdoll.history`; retained `tools/project_history` only as a legacy compatibility layer across the v1.0 production boundary.
- Added `ragdoll.storage` primitives for fsync + atomic-replace metadata writes, guarded local lock files, and versioned Ragdoll home migrations.
- Added fail-closed behavior for newer/corrupt local migration metadata and corrupt project registry metadata instead of silently resetting user state.
- Added versioned SQLite derived-index migrations, integrity status, WAL/busy-timeout settings, and a rebuildable dirty-index marker.
- Changed history durability ordering so canonical JSONL append succeeds independently of derived-index availability; index failure marks derived state dirty instead of encouraging duplicate retries.
- Added event idempotency keys for retry-safe adapter delivery and paginated conversation/event API reads.
- Implemented forensic retrieval expansion against neighboring canonical raw events while preserving project scope and token budgets.
- Added automatic backup of maintained `project-context/` before forced regeneration.
- Added stable transport-neutral errors/validation and hardened HTTP behavior with request IDs, readiness probe, bounded JSON bodies, security headers, local-origin checks, generic internal errors, and structured privacy-safe local logs.
- Made built-in HTTP strictly loopback-only; `RAGDOLL_ALLOW_REMOTE_BIND=true` is reserved for a future authenticated TLS transport and currently fails closed.
- Hardened provider egress with HTTPS/fixed-host allowlisting, redirect denial, configurable timeout and response-size bounds, safe errors, outbound secret policy, and no silent fallback.
- Hardened local runtime lifecycle with atomic PID metadata and stale-PID kill protection.
- Added production Core architecture/API/install documentation and updated self Project Context to reflect canonical/derived state boundaries.
- Pointed one-line POSIX/PowerShell installers at the canonical GitHub repository while retaining repository/version override support for forks/tests.
- Expanded GitHub validation to Ubuntu/Windows/macOS across Python 3.11/3.12/3.13, added deterministic repository-contract checks, Dependabot, CODEOWNERS, and tag/version-gated release validation.
- Expanded regression coverage for migration safety, idempotency, pagination, forensic retrieval, index integrity, context backup, HTTP contracts, and installer behavior.
- Kept automatic Antigravity capture unclaimed and deferred IDE plugins; MCP remains a later thin adapter after Core dogfooding.
- Completed pre-release code-review hardening: moved Project Context runtime logic inside the installable `ragdoll` package, added HEAD/405 HTTP handling, tightened direct service validation, stopped mapping arbitrary `KeyError` exceptions to 404, and fixed log-event timestamp fidelity.
- Added a rebuildable SQLite conversation-metadata index so normal conversation pagination does not scan every conversation file; filesystem scanning is retained only as a correctness fallback while the derived index is dirty/unavailable.
- Updated default provider aliases and Gemini request/response handling against current primary provider documentation while preserving `.env` model overrides and direct BYO-provider egress.

## 0.7.0 - 2026-09-02

- Added the installable **Ragdoll Local Backend** as a loopback-only user-owned HTTP service and CLI rather than a hosted Ragdoll dependency.
- Added `pyproject.toml` console entrypoints for `ragdoll` and `ragdoll-server` with a Python 3.11+ standard-library runtime.
- Added `.env` configuration for user-owned OpenAI, Anthropic, and Gemini API keys, model overrides, token budgets, local API settings, and outbound secret policy.
- Added direct built-in provider adapters for OpenAI, Anthropic, and Gemini; the Gemini transport was subsequently aligned to the official `models.generateContent` contract during v1.0 pre-release hardening.
- Added deterministic provider selection with no silent fallback and fixed HTTPS provider-host allowlisting.
- Added local bearer-token authentication, loopback-origin checks, request-size limits, and remote-bind denial by default.
- Added authenticated APIs for projects, conversations/events, history search/verification/index rebuild, Project Context generation/validation/compilation, provider status, and direct chat.
- Added token-budgeted runtime context compilation that combines selected Project Context with project-scoped history before outbound secret filtering.
- Added POSIX `install.sh`/`uninstall.sh` and Windows `install.ps1`/`uninstall.ps1`; normal reinstall/uninstall preserves `~/.ragdoll` user data and destructive deletion remains explicit.
- Added GitHub-Release bootstrap mode for `curl | sh` and `irm | iex`, with release discovery, SHA-256 verification via `SHA256SUMS`, safe source extraction, version pinning, and the same data-preserving install semantics.
- Added deterministic `scripts/build_release.py` plus a tag-triggered GitHub Release workflow so installer-consumable source ZIP/checksum assets are generated from the canonical repository.
- Added configuration, provider-contract, local-server, context/API, and installer regression tests without making billable live provider calls in CI.
- Expanded privacy/security documentation for provider egress and Local Backend data flow.
- Clarified that the Local Backend is integration plumbing, not a general-purpose agent harness, and that automatic full Antigravity event capture remains specified but not implemented.
- Kept the open-source economic invariant: Ragdoll Core requires no maintainer-operated backend, storage, vector database, model proxy, or subsidized provider access.

## 0.6.0 - 2026-09-02

- Added the **Ragdoll Project History Standard** as a first-class local-first subsystem separate from Project Context.
- Added indefinite history retention defaults with no automatic deletion, no telemetry, no cloud sync, and normal-uninstall preservation.
- Added a standard-library-first local Project History reference implementation under `tools/project_history/` with `scripts/ragdoll_history.py`.
- Added stable local project registration, per-project conversation storage, append-only JSONL canonical events, event hash chains, and corruption verification.
- Added rebuildable SQLite/FTS indexing and project-scoped focused/comprehensive/forensic retrieval behavior.
- Added token-budgeted history evidence compilation so routine work does not replay full project history.
- Added common secret redaction before Project History persistence and explicit exact-ID project purge semantics.
- Added `PRIVACY.md` and public security design documentation for threat model, data flow, network boundaries, and secret handling.
- Defined local-by-default/network-by-permission security invariants and separated LLM-provider access from general network/tool permissions.
- Added a sustainable open-source architecture principle: user-owned storage/compute and BYO model providers by default so adoption does not create proportional maintainer infrastructure cost.
- Added dogfood-first product principles and explicitly deferred SaaS accounts, billing, hosted vector databases, managed model proxies, and other premature commercial infrastructure.
- Clarified that automatic Antigravity conversation capture is not yet implemented; the storage/retrieval contract is implemented and IDE capture requires an observable adapter.
- Added Project History/privacy regression tests and expanded repository validation/CI.
- Kept Ragdoll independent from unrelated projects and kept the current scope separate from a general-purpose coding harness.


## 0.5.0 - 2026-09-02

- Renamed the public project and skill to **Ragdoll Product Engineering Standard** (`ragdoll-product-engineering-standard`).
- Added the **Ragdoll Context Standard** as a first-class, domain-oriented public protocol under `context-standard/`.
- Added `context-standard/registry.yaml` and the first stable context domain: `software-engineering`.
- Standardized the Software Engineering domain around six canonical templates: project overview, architecture, code standards, AI workflow rules, progress tracker, and UI context.
- Renamed instantiated repository context from ambiguous `context/` to explicit `project-context/` and added `context-manifest.yaml`.
- Added Ragdoll's own maintained Software Engineering Project Context to dogfood the protocol.
- Added provenance classes `OBSERVED`, `DECLARED`, `INFERRED`, and `UNDECIDED` and prohibited silent promotion of inferred claims.
- Added conservative `generate_project_context.py` bootstrap tooling that detects repository evidence but does not invent architecture or product semantics.
- Added `validate_project_context.py` and expanded CI/repository validation to cover Context Standard and Project Context contracts.
- Kept the six-file contract scoped only to Software Engineering so future domains can define different information models.
- Kept terminal/PowerShell installer automation deferred until after GitHub publication and real Antigravity evaluation.

## 0.4.0 - 2026-09-02

- Added Google Antigravity as the first native IDE/agent evaluation target.
- Added a thin Antigravity workspace-rule adapter and workspace-scoped evaluation protocol.
- Added GitHub-ready repository documentation, contribution governance, security policy, issue templates, PR template, and CI validation.
- Kept the canonical standard provider-neutral and prevented Antigravity integration from forking the core rules.
- Deferred automatic terminal/PowerShell installation to a later milestone after real-project evaluation.

## 0.3.0 - 2026-09-02

- Added provider-neutral LLM execution policy with user-selected cloud, local, or explicitly enabled hybrid inference.
- Separated LLM inference locality from network/tool access so local models can operate with either online discovery or fully offline restrictions.
- Prohibited silent provider switching, local-to-cloud fallback, implicit multi-provider routing, and unauthorized context egress.
- Added fully local/offline behavior, cloud privacy boundaries, hybrid data-sharing boundaries, and capability-degradation rules.
- Updated Active Intelligence and all cross-agent adapters to honor the selected provider, privacy, and network policy.

## 0.2.0 - 2026-09-02

- Added Active Intelligence mode for runtime discovery of current OSS repositories, tools, specifications, and senior-engineer guidance.
- Added evidence-gated discovery -> evaluate -> experiment -> adopt -> codify -> re-evaluate workflow.
- Added OSS/tool selection framework covering fit, maintenance, security/supply-chain, license, compatibility, operational cost, adoption, and reversibility.
- Added curated cross-domain tool catalog for coding quality, testing, security, UI/design/accessibility, performance, Git/release, documentation, and architecture analysis.
- Added deterministic candidate scoring helper for decision support.
- Updated cross-agent adapters to permit active discovery without treating popularity as approval.

## 0.1.0 - 2026-09-02

- Established portable Product Engineering Standard for AI coding agents.
- Added rule precedence and systematic engineering workflow.
- Added standards for coding, architecture, APIs, data, tests, security, reliability, observability, Git, commits, versioning, PRs and releases.
- Added AI-agent anti-patterns and explicit no-fake-success requirements.
- Added evidence-governed evolution process and source registry.
- Added cross-IDE/agent adapters.

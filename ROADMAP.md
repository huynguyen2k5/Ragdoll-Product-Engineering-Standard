# Roadmap

Ragdoll is dogfood-first. Prioritize work that makes the maintainer's own multi-project engineering workflow more reliable while preserving local-first privacy, user-owned data, protocol portability, and near-zero mandatory maintainer infrastructure cost.

## v1.0 - Production baseline

Implemented milestone:

- transport-neutral `RagdollCore` for shared CLI/HTTP/future protocol behavior;
- production history implementation under `ragdoll.history` with compatibility wrappers for old imports;
- atomic local metadata writes and guarded lock files;
- versioned/fail-closed Ragdoll-home and SQLite derived-index migrations;
- canonical JSONL durability independent of disposable index success;
- idempotency keys for retry-safe history capture;
- bounded event/conversation pagination;
- focused/comprehensive/forensic retrieval with canonical-neighbor expansion;
- Project Context backup before forced regeneration;
- stable errors/validation, readiness, request IDs, defensive HTTP headers, bounded JSON requests, and privacy-safe structured local logs;
- strict loopback-only HTTP Core;
- bounded/allowlisted/non-redirecting provider egress;
- hardened background-process lifecycle;
- canonical GitHub installer defaults and checksum-verified release contract;
- multi-OS/multi-Python GitHub CI configuration plus release version/tag gates;
- production architecture/API/install documentation and expanded regression tests.

The Core remains local and does not become a general-purpose agent harness.

## Immediate dogfooding milestone

1. Land the v1.0 production changes through numbered GitHub PRs into protected `main`, then tag/publish `v1.0.0` and let cross-platform CI/release checks run.
2. Install the published release on the maintainer's real Windows development machine using the PowerShell one-liner.
3. Configure one user-owned provider key and perform a real low-cost provider request.
4. Use Ragdoll during real product work across multiple independent projects.
5. Measure repeated-prompt reduction, context drift, retrieval misses, token usage, and any reason the maintainer bypasses Ragdoll.
6. Harden only failures observed in real use instead of adding speculative infrastructure.

Success signal:

> Working without Ragdoll becomes noticeably less reliable, less private, or more repetitive than working with it.

## MCP milestone - after Core contracts survive dogfooding

Prefer protocol-level integration before IDE plugins.

A future MCP adapter should be thin over `RagdollCore` and may expose project/context/history/retrieval capabilities without creating another source of truth. It must preserve:

- current-project isolation;
- local-first storage;
- canonical history semantics;
- outbound security policy;
- idempotent event capture;
- no hidden model reasoning claims;
- no duplicate provider/config implementation.

Do not begin broad plugin work merely because an IDE exists. Add an IDE-specific plugin only when protocol/local-API integration cannot meet a demonstrated workflow need.

## Antigravity integration milestone

Antigravity remains the first real IDE dogfood target. Before claiming automatic history capture:

- identify a verified observable event/hook mechanism;
- normalize only observable user/assistant/tool/file/Git events;
- send stable idempotency keys when delivery may retry;
- preserve current-project isolation;
- test restart/resume/duplicate delivery;
- never claim hidden provider reasoning is captured.

Automatic full Antigravity capture remains **SPECIFIED, NOT IMPLEMENTED** until proven.

## Public OSS readiness

Before broad promotion:

- owner selects and adds an explicit open-source license;
- canonical `main` and release tags are public and protected by working CI;
- private vulnerability-reporting path is enabled;
- release checksums/integrity flow works from a clean installation;
- PowerShell/POSIX install/update/uninstall are exercised on real clean environments;
- at least one real request per advertised provider is tested or honestly marked unverified;
- known limitations remain explicit.

## Later, only from demonstrated need

- richer observable IDE adapters;
- session/resume UX;
- cold-history compression without auto-delete;
- optional local semantic retrieval if structured/FTS search shows real misses;
- second Context Standard domain based on real non-SE work;
- optional user-owned sync adapters;
- stronger signed releases/SBOM/supply-chain controls;
- richer egress inspection/audit UX;
- hosted collaboration/governance features only after actual demand.

## Explicitly deferred

Do not prioritize now:

- mandatory accounts;
- Ragdoll-hosted backend required for Core;
- billing/subscriptions;
- team/enterprise admin console;
- managed vector database;
- hosted model proxy;
- maintainer-subsidized LLM access;
- cross-project retrieval by default;
- broad IDE plugin matrix.

Future commercial services, if justified later, should monetize managed scale, collaboration, hosting, governance, or convenience rather than restricting local ownership of Project Context or Project History.

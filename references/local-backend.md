# Local Backend and Installation

Use this reference when installing/running Ragdoll, configuring `.env`, calling the loopback API, or connecting a thin protocol/IDE adapter.

## Core and transport contract

- Python 3.11+.
- Standard-library-only runtime in v1.0.
- `RagdollCore` owns project/context/history/provider application behavior.
- CLI/HTTP/future MCP are adapters and MUST NOT duplicate Core business/storage/security rules.
- Default bind `127.0.0.1:8765`.
- Built-in HTTP is loopback-only; `RAGDOLL_ALLOW_REMOTE_BIND=true` is reserved for a future authenticated TLS transport and currently fails closed.
- Random local bearer token in `~/.ragdoll/api-token`.
- `/v1/health` and `/v1/ready` are public loopback probes; other API endpoints require the token.
- No telemetry/cloud-sync transport.

## Durability contract

- `ragdoll.history` is the production history implementation.
- Canonical JSONL is durable before derived SQLite indexing.
- SQLite/FTS is disposable/rebuildable; indexing failure marks derived state dirty.
- Local home/index schemas are versioned; unsupported/corrupt migration state fails closed.
- Small metadata uses atomic-replace writes.
- Retrying adapters SHOULD use event `idempotency_key` values.
- Forced Project Context regeneration backs up the previous context root first.

## `.env`

Provider keys are user-owned:

```text
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
```

Only one key is needed. `RAGDOLL_PROVIDER=auto` selects the first configured provider deterministically; it does not implement fallback after a provider failure.

Precedence: explicit `--env-file` -> `RAGDOLL_ENV_FILE` -> Ragdoll-owned `$RAGDOLL_HOME/.env` (default `~/.ragdoll/.env`), then process environment overrides loaded file values. Generic project workspace `.env` files are not auto-read.

## Provider calls

Before a provider call:

```text
project scope
  -> selected Project Context
  -> relevant Project History
  -> token budgets
  -> secret redaction/blocking
  -> selected provider only
```

Built-in provider egress is HTTPS-only, fixed-host allowlisted, redirect-denied, timeout-bounded, and response-size-bounded. OpenAI Responses and Gemini Interactions calls use `store=false`.

## Install/uninstall

Canonical one-line bootstrap repository:

```text
huynguyen2k5/Ragdoll-Product-Engineering-Standard
```

Remote bootstrap resolves a release source ZIP plus `SHA256SUMS`, verifies SHA-256 before extraction/execution, and supports `RAGDOLL_VERSION` pinning. `RAGDOLL_REPO` remains overridable for forks/tests.

The installed runtime lives below `~/.ragdoll/runtime`; user data lives outside replaceable runtime code. Re-running the installer upgrades runtime without deleting `.env`, API token, projects, indexes, backups, or canonical Project History.

Normal uninstall preserves data. Permanent deletion requires `--purge-data` (POSIX) or `-PurgeData` (PowerShell).

## Adapter boundary

Adapters call `RagdollCore` directly in-process or use a supported local transport. They may append only observable events and SHOULD provide idempotency keys when delivery can retry. Do not claim automatic IDE capture until a verified event source and integration tests exist. Plugins remain deferred; prefer protocol-level adapters first.

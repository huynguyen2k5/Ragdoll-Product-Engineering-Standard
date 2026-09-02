# Ragdoll Local Backend

Ragdoll v1.0 establishes the local runtime around a transport-neutral Core. The CLI and loopback HTTP server call the same `RagdollCore` application boundary; future adapters should do the same rather than duplicating business logic.

## Runtime shape

```text
CLI / HTTP / future protocol adapter
                 |
                 v
            RagdollCore
                 |
      +----------+----------+
      |          |          |
      v          v          v
   Project     Context    History
                           |
                    canonical JSONL
                           |
                    derived SQLite/FTS
                 |
            Context Compiler
                 |
          outbound secret gate
                 |
       optional selected provider
```

Project storage/search/context operations remain local and work without any provider key. Ragdoll operates no model proxy or mandatory backend.

Read `CORE_ARCHITECTURE.md` for durability, migrations, idempotency, error contracts, and adapter rules.

## Start

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

The background process writes local structured logs and maintains PID metadata under `~/.ragdoll/runtime/`. Start/stop logic verifies that a live endpoint identifies itself as Ragdoll before terminating a recorded PID, reducing stale-PID risk.

## Local API authentication

The service generates a random token at:

```text
~/.ragdoll/api-token
```

`/v1/health` and `/v1/ready` are public loopback probes. All other endpoints require:

```text
Authorization: Bearer <local-token>
```

Use `ragdoll token` when a local adapter needs the token. Never commit it.

## Bind policy

The built-in Core HTTP transport is **loopback-only**:

```text
127.0.0.1
localhost
::1
```

`RAGDOLL_ALLOW_REMOTE_BIND=true` is intentionally rejected and reserved for a future authenticated TLS transport. Ragdoll does not send its bearer token over plaintext LAN HTTP.

Requests carrying a non-local browser `Origin` are rejected. CORS is not enabled.

## Durability

Canonical Project History is append-only JSONL. Appends are flushed and fsynced before the disposable SQLite/FTS index is updated. If the index update fails after the canonical append succeeds, Ragdoll marks the index dirty rather than telling the caller the durable event failed.

Small metadata files use atomic replace semantics. Local home/index schemas are versioned. A newer or corrupt migration state fails closed instead of being silently reset.

Adapters may supply event idempotency keys to make retries safe.

## Provider behavior

`.env` supports direct user-owned OpenAI, Anthropic, and Gemini credentials. `RAGDOLL_PROVIDER=auto` selects the first configured provider deterministically. Once selected, Ragdoll does not silently fall back to another provider.

Provider egress is HTTPS-only, fixed-host allowlisted, redirect-denied, timeout-bounded, and response-size-bounded. Outbound prompt/system text passes through the secret redaction/block policy before the request.

Context/history operations do not require a provider.

## History capture boundary

The local backend exposes stable APIs for adapters to append **observable** events. It does not have access to hidden provider chain-of-thought. Automatic Antigravity capture remains a separate integration milestone until a verified event/hook source is implemented and tested.


## Startup health deadline

The background launcher waits up to 10 seconds for the loopback health endpoint and polls at 200 ms intervals. These are named runtime constants in v1.0.0 and may become explicit configuration if real dogfooding shows a need; startup failure never silently replaces a live PID.

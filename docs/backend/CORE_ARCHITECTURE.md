# Core Architecture

Ragdoll Core is the transport-neutral application boundary shared by the CLI, the loopback HTTP API, and future protocol adapters such as MCP. Transport code must stay thin and must not reimplement project, context, history, retrieval, security, or provider business rules.

## Dependency shape

```text
CLI                HTTP                 future MCP
 |                  |                       |
 +------------------+-----------------------+
                    |
                    v
              RagdollCore
                    |
       +------------+-------------+----------------+
       |                          |                |
       v                          v                v
 Project identity/context     Project History   Provider edge
       |                          |                |
       |                    canonical JSONL       |
       |                          |                |
       |                    derived SQLite/FTS    |
       +------------+-------------+----------------+
                    |
                    v
              user-owned disk
```

The core does not require a Ragdoll-operated service. Provider egress is an optional edge used only for an explicit model call.

## Canonical versus derived state

Canonical local state includes project identity metadata, Project Context maintained in the target repository, and append-only Project History event logs. SQLite/FTS is a derived search index. If the index is missing or corrupt, it can be rebuilt from canonical event logs.

Small Ragdoll-owned metadata files use write/fync/atomic-replace semantics. Canonical history appends are fsynced before the derived index is updated. If indexing fails after a durable append, Ragdoll marks the index dirty instead of reporting the canonical append as failed and inviting a duplicate retry.

## Versioned local data

`~/.ragdoll/state.json` records the local home schema. The runtime applies explicit local migrations and refuses to run against a newer schema it does not understand. Corrupt migration metadata fails closed rather than being silently reset.

SQLite has a separate migration table and schema version. SQLite migrations may change derived data only; they must never rewrite canonical JSONL to make an index migration pass.

## Retry and idempotency contract

Event append accepts an optional `idempotency_key`. A retry with the same key in the same project/conversation returns the original canonical event rather than appending another event. IDE/protocol adapters should provide stable idempotency keys when their transport can retry delivery.

Idempotency is a retry-safety mechanism, not a deduplication heuristic. Ragdoll does not merge distinct events merely because their text is similar.

## Retrieval contract

Ragdoll supports three project-scoped modes:

- `focused`: routine token-efficient retrieval;
- `comprehensive`: broad matching when the user explicitly asks for all relevant history;
- `forensic`: indexed matching plus neighboring canonical raw events for traceability.

Every mode remains scoped to one stable `project_id` unless a future explicit cross-project capability is authorized. Runtime context compilation applies a token budget after retrieval; summaries/index hits never replace canonical history.

## Error contract

Core operations raise stable `RagdollError` subclasses with a machine-readable code, safe message, HTTP-equivalent status, and optional details. HTTP maps the same error contract to JSON and adds a request ID. Unexpected internal exceptions are logged by type and returned as a generic internal error; raw exception text is not exposed to local API callers by default.

Example:

```json
{
  "error": {
    "code": "validation_error",
    "message": "token_budget must be between 200 and 100000",
    "request_id": "req_..."
  }
}
```

## Local HTTP boundary

The built-in HTTP adapter is deliberately loopback-only. `RAGDOLL_ALLOW_REMOTE_BIND` is reserved for a future authenticated TLS transport and currently must remain false. This prevents the local bearer token from becoming a plaintext LAN credential.

`GET /v1/health` is a minimal liveness probe. `GET /v1/ready` verifies local schema/index readiness without returning project names or filesystem paths. Other API operations require the local bearer token and reject non-local browser origins.

Requests are bounded, JSON content type is enforced for non-empty bodies, transfer encoding is rejected, redirects are denied on provider egress, and responses include no-store/security headers.

## Observability

The backend emits structured JSON logs with request IDs, route, status, duration, lifecycle events, and safe exception type where needed. Logs are local. They must not include API keys, bearer tokens, full prompts, source contents, conversation contents, or provider response bodies by default.

## Compatibility boundary

`ragdoll.history` is the production history implementation. `tools/project_history` remains a legacy compatibility wrapper across the v1.0 production boundary. New code must import from `ragdoll.history` or call `RagdollCore`.

Public transports may evolve before 1.0, but canonical user history, migration safety, project isolation, explicit purge semantics, and local-first privacy are compatibility priorities.

## Extension rule

New adapters must call Core services rather than reaching directly into storage. In particular, future MCP or IDE adapters must not:

- define a second history schema;
- bypass project isolation;
- bypass outbound secret policy;
- manage provider credentials independently;
- treat SQLite as canonical history;
- silently enable network access, telemetry, or sync.

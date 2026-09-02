# Local API

Default base URL:

```text
http://127.0.0.1:8765
```

`GET /v1/health` and `GET /v1/ready` are unauthenticated loopback probes. Every other endpoint requires:

```text
Authorization: Bearer <local-api-token>
```

Obtain the token locally with `ragdoll token`. Do not commit or transmit it over a non-loopback network.

## HTTP contract

- Non-empty request bodies must use `Content-Type: application/json`.
- `Transfer-Encoding` request bodies are rejected.
- Request size is bounded by `RAGDOLL_MAX_REQUEST_BYTES`.
- Successful and error responses include `X-Request-ID`.
- A valid client-supplied `X-Request-ID` may be echoed; otherwise Ragdoll generates `req_...`.
- Responses include `Cache-Control: no-store` and defensive browser headers.
- Browser requests with a non-local `Origin` are rejected.
- The built-in transport is loopback-only; remote HTTP bind is not supported in the Core runtime.

Stable error envelope:

```json
{
  "error": {
    "code": "validation_error",
    "message": "query parameter limit must be between 1 and 1000",
    "request_id": "req_..."
  }
}
```

Do not parse human error text as an API contract; use `error.code`.

## Health and readiness

### `GET /v1/health`

Minimal liveness probe. Does not expose project/configuration paths.

### `GET /v1/ready`

Checks local data schema writability and derived history-index integrity. Returns HTTP `200` when ready or `503` when the local runtime cannot safely serve normal operations. The public readiness payload deliberately excludes project metadata and filesystem paths.

### Authenticated status

- `GET /v1/status` - runtime/config/index status; never returns provider key values or the local bearer token.
- `GET /v1/providers` - configured provider/model/host status; key values are redacted.
- `GET /v1/history/index/status` - SQLite schema, integrity, FTS availability, dirty marker, and indexed event count.
- `POST /v1/history/rebuild-index` - rebuild derived SQLite/FTS state from canonical event logs.

## Projects

- `POST /v1/projects` - register a workspace path and optional display name.
- `GET /v1/projects` - list local project identities.
- `GET /v1/projects/{project_id}` - inspect one registered project.
- `DELETE /v1/projects/{project_id}` - permanently purge only when JSON `confirm` exactly matches `project_id`.

Registration example:

```json
{
  "path": "/path/to/project",
  "name": "My Project"
}
```

## Project Context

- `GET /v1/projects/{project_id}/context`
- `POST /v1/projects/{project_id}/context/generate`
- `POST /v1/projects/{project_id}/context/validate`
- `POST /v1/projects/{project_id}/context/compile`

Generation is conservative. `force: true` is required to replace an existing context root; before replacement Ragdoll backs up the previous `project-context/` under the local Ragdoll backup area.

Compile example:

```json
{
  "prompt": "Review the authentication architecture",
  "use_project_context": true,
  "use_history": true,
  "history_mode": "focused"
}
```

## Project History

### Conversations

- `GET /v1/projects/{project_id}/conversations?limit=100&before=<timestamp>`
- `POST /v1/projects/{project_id}/conversations`
- `GET /v1/projects/{project_id}/conversations/{conversation_id}`

`before` is a time cursor for conversation listing. Results are returned newest first.

### Events

- `GET /v1/projects/{project_id}/conversations/{conversation_id}/events?after_seq=0&limit=200`
- `POST /v1/projects/{project_id}/conversations/{conversation_id}/events`
- `GET /v1/projects/{project_id}/conversations/{conversation_id}/verify`

Event-page responses include `next_after_seq`. Continue with that value to fetch later canonical events.

Adapters that may retry delivery should provide an idempotency key:

```json
{
  "type": "user.message",
  "idempotency_key": "adapter-session-42-turn-7-user",
  "payload": {
    "text": "Implement the migration"
  }
}
```

The same idempotency key in the same project/conversation returns the original event instead of appending a duplicate.

### Search

`POST /v1/projects/{project_id}/history/search`

Example:

```json
{
  "query": "why did we choose SQLite",
  "mode": "focused",
  "limit": 20,
  "token_budget": 1500,
  "file_path": null,
  "commit_sha": null,
  "event_type": null,
  "conversation_id": null
}
```

Modes:

- `focused` - routine low-token work;
- `comprehensive` - broad matching when completeness matters;
- `forensic` - matching plus neighboring canonical raw events for traceability.

Search is always scoped to the supplied project ID in the current Core API.

## Model call

`POST /v1/chat`

Example:

```json
{
  "project_id": "prj_...",
  "prompt": "Explain the current storage decision",
  "provider": "openai",
  "use_project_context": true,
  "use_history": true,
  "history_mode": "focused",
  "idempotency_key": "ide-request-..."
}
```

If `conversation_id` is omitted, Ragdoll creates a conversation. Observable user/provider result or safe provider-error events are persisted in the same project. The provider request is compiled locally from selected Project Context and relevant Project History, then passes through the outbound secret gate.

API keys are never returned by this API. A provider failure does not silently fall back to another provider.

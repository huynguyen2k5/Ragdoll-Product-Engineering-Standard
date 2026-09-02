# Data Flow

## Default local flow

```text
Repository + Project Context + Project History
        -> local inspection/retrieval
        -> local context compilation
        -> local validation/API
        -> local response
```

No Ragdoll-operated server is required.

## Local HTTP flow

```text
IDE / CLI
  -> 127.0.0.1 local API
  -> local bearer-token check
  -> project-scoped operation
  -> local files / SQLite
```

Only `/v1/health` is unauthenticated.

## Cloud LLM flow

When the user explicitly invokes a configured provider:

```text
Local sources
  -> project-scoped retrieval
  -> token-budgeted minimum selection
  -> secret redaction/blocking
  -> one selected allowlisted provider
  -> response
  -> sanitized observable response persisted locally
```

OpenAI and Gemini API requests disable provider resource storage with `store=false`. Provider-side processing/retention otherwise remains governed by the user's provider terms/account configuration.

## Active Intelligence flow

Network research is a separate capability. Private repository content MUST NOT be attached to a research request merely because cloud-model access is configured.

## History flow

Observable conversation/tool events are sanitized and appended to local canonical JSONL. The SQLite index is derived and may be deleted/rebuilt without modifying canonical history.

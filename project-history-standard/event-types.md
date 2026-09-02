# Project History Event Types

Event types are extensible strings. The initial vocabulary is intentionally small.

| Event type | Purpose |
| --- | --- |
| `conversation.started` | Conversation metadata became active. |
| `conversation.ended` | Conversation was intentionally closed. |
| `user.message` | Observable user message. |
| `assistant.message` | Observable assistant response. |
| `tool.call` | Observable tool invocation metadata. |
| `tool.result` | Observable tool result or summarized output. |
| `file.changed` | File change evidence. |
| `git.commit` | Git commit linkage. |
| `decision.recorded` | Accepted project or engineering decision. |
| `validation.result` | Test/lint/type/build/security evidence. |
| `summary.created` | Derived summary. Raw source events remain canonical. |
| `artifact.recorded` | Artifact metadata/reference. |

Hidden provider reasoning that is not exposed to the user or adapter is not an event and MUST NOT be fabricated.

## Retry-safe delivery

An observable event MAY include an `idempotency_key` when the adapter or transport can retry delivery. The key is scoped to one project/conversation. Reusing the same key MUST return the already-durable event rather than append another canonical event.

Idempotency keys are delivery identifiers, not semantic deduplication. Distinct user/tool events MUST NOT be merged merely because their text or payload is similar.

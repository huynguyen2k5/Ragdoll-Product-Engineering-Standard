# Ragdoll Project History Standard

The Project History Standard defines how Ragdoll retains observable AI-assisted engineering history for each project without requiring Ragdoll-operated infrastructure.

## Goals

- Retain project history indefinitely by default until the user explicitly deletes it.
- Keep canonical history local and user-owned.
- Isolate history by stable project identity.
- Preserve raw observable events while allowing summaries and compact runtime context.
- Make search indexes disposable and fully rebuildable from canonical history.
- Retrieve the minimum sufficient evidence for routine work instead of replaying complete conversations.
- Support focused, comprehensive, and forensic retrieval modes.
- Avoid mandatory hosted databases, vector services, accounts, telemetry, or Ragdoll cloud storage.

## Non-goals

This subsystem is not a general-purpose coding harness. It does not orchestrate agents, route models, grant tool permissions, or expose hidden model chain-of-thought. It stores only events that Ragdoll or an IDE adapter can actually observe.

## Canonical layout

The default data root is `~/.ragdoll` and may be overridden by `RAGDOLL_HOME`.

```text
~/.ragdoll/
├── projects/
│   ├── registry.json
│   └── <project-id>/
│       ├── project.json
│       └── conversations/
│           └── <conversation-id>/
│               ├── conversation.json
│               └── events.jsonl
└── indexes/
    └── history.sqlite3
```

`events.jsonl` is canonical append-only history. SQLite is a local search/index layer and MUST be rebuildable.

## Event model

Events may represent:

- user and assistant messages;
- tool calls and observable tool results;
- file changes;
- Git commits and branch metadata;
- decisions and accepted requirements;
- summaries;
- artifacts and validation evidence.

Each event has a monotonically increasing sequence number and a hash chain so corruption or tampering can be detected during verification.

## Retention

Default retention is `indefinite`. Summarization, compaction, index rebuilds, model context limits, IDE restarts, Git resets, and normal Ragdoll upgrades MUST NOT delete canonical history.

Normal uninstall SHOULD preserve `~/.ragdoll`. A future installer may offer a separate explicit purge action.

## Retrieval

- `focused`: fast project-scoped retrieval for normal coding work.
- `comprehensive`: wider lexical scan when the user asks for all relevant history.
- `forensic`: identifier-driven investigation using conversation, file, commit, type, or exact event references.

Routine runtime context SHOULD be token-budgeted. Full history remains available on disk and is expanded only when relevant.

## Privacy

Project history is local-only by default. The reference implementation performs no network requests and has no telemetry. Common secret patterns are redacted before persistence by default. Project A history MUST NOT be returned for Project B unless a future cross-project feature is explicitly requested and authorized.

See `PRIVACY.md`, `docs/security/`, and `references/project-history.md`.

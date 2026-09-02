# Project History

Use this reference when retaining, searching, resuming, importing, or reasoning from prior AI-assisted work on a project.

## Core principle

Store losslessly enough for later investigation, but load only the minimum sufficient history for the current task.

```text
Observable project history
  -> canonical local append-only store
  -> disposable local search index
  -> project-scoped retrieval
  -> token-aware context compilation
  -> AI agent
```

## Invariants

1. Retention is indefinite by default.
2. Canonical history is local and user-owned by default.
3. Summarization and context compaction MUST NOT delete canonical history.
4. Search indexes MUST be rebuildable from canonical history.
5. Retrieval is scoped to the current project by default.
6. Hidden provider reasoning that is not observable MUST NOT be fabricated or claimed as stored.
7. A normal uninstall SHOULD preserve history; deletion requires an explicit purge action.
8. History is evidence, not automatic current authority.

## Project identity

Do not use only a workspace path as project identity. A path can move and a repository can have multiple worktrees.

Prefer a stable local `project_id` associated with observed Git remote/root identity and known workspaces. When a Git remote changes to a distinct repository, do not silently merge histories.

## Conversation model

Distinguish:

```text
Project
  -> Workspace
  -> Conversation
  -> Event
```

A conversation may survive IDE restarts. A future adapter may model finer session/turn structure, but storage MUST preserve project/conversation lineage.

Forked conversations SHOULD reference a parent conversation and fork sequence rather than copying all parent events.

## Observable event history

Persist only what an adapter can actually observe, such as:

- user/assistant messages;
- tool calls and results;
- file-change metadata;
- commits/branches;
- accepted decisions;
- validation results;
- summaries and artifact references.

Large terminal/build outputs SHOULD be summarized or stored as optional compressed artifacts instead of duplicating huge payloads in the searchable event stream.

## Retrieval modes

### Focused

Use for normal product work. Prefer structured metadata and SQLite FTS within the current project, then compile a small evidence set under a token budget.

### Comprehensive

Use when the user asks for all occurrences or explicitly prioritizes completeness. Scan wider project history and expand neighboring evidence as required. Report that lexical completeness does not imply semantic omniscience.

### Forensic

Use for questions such as why a file, symbol, commit, or decision exists. Follow identifiers where available:

```text
file/symbol -> commit -> conversation -> exact event -> decision/evidence
```

## Authority

Old conversation history MUST NOT override newer canonical project truth merely because it is detailed.

Default authority:

1. current explicit user instruction;
2. safety/privacy/legal/data-integrity rules;
3. current accepted Project Context/ADR;
4. current repository evidence;
5. accepted recorded decisions;
6. prior conversation history;
7. derived summaries/inferences.

Use history to explain evolution and recover evidence. Promote a historical decision into current Project Context only after reconciling it with current authority.

## Reference implementation

The production implementation lives under `ragdoll.history` and is exposed through `RagdollCore`/the `ragdoll` CLI. `scripts/ragdoll_history.py` and `tools/project_history/` are legacy compatibility entrypoints only.

It currently provides local project registration, append-only event storage, secret redaction, hash-chain verification, SQLite/FTS indexing, project-scoped retrieval, index rebuild, token-budgeted evidence compilation, and explicit project purge.

This local implementation is not a claim that every IDE can already stream all conversation events into Ragdoll. IDE adapters must expose observable events before automatic capture can be considered IMPLEMENTED.

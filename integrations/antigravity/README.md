# Google Antigravity Integration

Antigravity is the first real dogfooding target for Ragdoll Product Engineering Standard.

Ragdoll now has an installable Local Backend and CLI. The remaining Antigravity-specific work is a thin adapter/event bridge: automatic full conversation/tool capture is intentionally not claimed until a verified observable Antigravity hook exists.

## Install Ragdoll

POSIX:

```bash
./install.sh
ragdoll doctor
ragdoll start
```

Windows PowerShell:

```powershell
.\install.ps1
ragdoll doctor
ragdoll start
```

The default Local API is `http://127.0.0.1:8765`. All non-health endpoints require the local token available with `ragdoll token`.

## Workspace layout

For workspace-scoped rule/Skill evaluation:

```text
<workspace-root>/
  project-context/                 # maintained canonical context for the codebase
    context-manifest.yaml
    software-engineering/
  .agents/
    skills/
      ragdoll-product-engineering-standard/
        SKILL.md
        references/
        scripts/
        context-standard/
        project-history-standard/
        tools/
    rules/
      ragdoll-product-engineering-standard.md
```

Use this repository as the canonical source. Use `assets/adapters/antigravity-rule.md` as the thin workspace rule.

## Register the project

```text
ragdoll project register . --name "My Project"
ragdoll context generate --project prj_...
ragdoll context validate --project prj_...
```

Generated Project Context is a `DRAFT_REQUIRES_REVIEW`; review it before treating inferred/undecided content as canonical.

## Project History location

Project History is not stored inside the Git repository by default. The local implementation uses:

```text
~/.ragdoll/
```

This prevents raw conversation history from being accidentally committed and allows the same logical project to retain history across known workspaces.

## Current integration support status

### IMPLEMENTED

- installable local CLI/backend;
- stable local project registration;
- per-project conversation/event storage;
- append-only/hash-chained JSONL canonical history;
- SQLite/FTS indexing and rebuild;
- project-scoped search and token-budgeted evidence compilation;
- Project Context generate/validate/compile APIs;
- direct BYO provider calls after local context compilation;
- secret redaction/blocking and local API authentication.

### SPECIFIED, NOT YET IMPLEMENTED

- automatic capture of every Antigravity user/assistant/tool/file event.

Do not fake this integration. A future adapter must consume an actual observable Antigravity event source and normalize only observable data into Ragdoll Project History.

Until then, the Local API/CLI can be used by verified hooks, external scripts, or manual dogfooding without claiming automatic IDE capture.

## Evaluation behavior

For non-trivial work:

```text
Resolve project
  -> read relevant Project Context
  -> retrieve relevant Project History only when needed
  -> inspect repository
  -> frame task
  -> design minimally
  -> implement
  -> validate
  -> review diff/privacy/security
  -> synchronize context/history evidence
  -> report
```

## Privacy

- Project Context/history/retrieval remain local by default.
- No Ragdoll telemetry or cloud sync is enabled.
- Provider keys remain user-owned and are not exposed by status APIs.
- Cloud-model access does not authorize uploading full history.
- Current-project history is the default retrieval scope.
- Network research and model-provider access are separate permissions.
- Local API remote binding is denied by default.

## Activation test

Ask Antigravity to inspect the repository before changes and identify:

- repository instructions/conventions;
- relevant Project Context;
- architecture and analogous implementations;
- lint/test/type/build tools;
- security/privacy/data risks;
- validation plan;
- whether prior Project History is actually needed.

A useful activation test should not modify files.

## Real-task scorecard

Score 0-2 for each:

- repository/context inspection before edits;
- correct problem framing;
- minimal/reversible design;
- respect for project conventions;
- deterministic validation;
- honest uncertainty/reporting;
- security/privacy awareness;
- correct project-history scoping when used;
- OSS/tool evaluation quality when relevant;
- diff/regression review and useful final handoff.

Interpretation:

- 17-20: strong behavior;
- 13-16: useful, tune weak areas;
- 9-12: inconsistent influence;
- 0-8: integration is not reliably helping.

## Global promotion

Keep IDE-specific rules thin until repeated real work proves the behavior. Do not globally install rules merely because one workspace test looks good.

See `references/antigravity.md`, `references/local-backend.md`, `references/project-history.md`, `references/privacy-security.md`, and `references/llm-execution-policy.md`.

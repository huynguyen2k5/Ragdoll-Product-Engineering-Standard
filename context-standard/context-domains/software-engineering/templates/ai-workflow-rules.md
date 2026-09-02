# AI Workflow Rules

## Approach

Work incrementally using a context-first, repository-inspection workflow. Treat the files in `project-context/software-engineering/` as canonical project context, but verify current repository reality before assuming implementation status.

## Required Context Read

Before substantial changes, read at minimum:

1. `project-context/software-engineering/project-overview.md`
2. `project-context/software-engineering/architecture.md`
3. `project-context/software-engineering/code-standards.md`
4. `project-context/software-engineering/progress-tracker.md`

For UI/design work also read:

5. `project-context/software-engineering/ui-context.md`

For workflow/process changes also read:

6. `project-context/software-engineering/ai-workflow-rules.md`

Also inspect repository-local agent instructions, tests, configuration, and analogous implementation relevant to the task.

## Source-of-Truth Priority

Use the project-defined order below and customize it if the repository has stronger governance:

1. Explicit current user/task instruction.
2. Safety, security, privacy, legal, and data-integrity constraints.
3. Accepted architecture invariants / ADRs.
4. `project-overview.md`.
5. `architecture.md`.
6. `code-standards.md`.
7. `ai-workflow-rules.md`.
8. `ui-context.md` when applicable.
9. `progress-tracker.md` for implementation state.
10. Existing implementation details.

Do not silently resolve material contradictions. Surface and reconcile them in the appropriate canonical source.

## Implementation Status Vocabulary

- **IMPLEMENTED** — code/configuration exists and applicable verification passes.
- **SPECIFIED** — behavior is documented but may not exist yet.
- **PLANNED** — future work without complete implementation evidence.
- **UNDECIDED** — decision intentionally remains open.
- **BLOCKED** — a prerequisite prevents safe progress.
- **DEPRECATED** — retained for history/compatibility but not intended for new work.

Never report `SPECIFIED` or `PLANNED` work as `IMPLEMENTED`.

## Scoping Rules

- Work on one coherent feature/fix/refactor unit at a time.
- Prefer small, verifiable increments over large speculative changes.
- Do not combine unrelated system boundaries in one implementation step.
- Avoid unrelated cleanup during focused feature work.
- Split work when parts can be reviewed, validated, or rolled back independently.

## Feature / Change Frame

Before non-trivial work, establish when applicable:

- Goal
- User/business outcome
- Inputs and outputs
- Affected subsystem
- Acceptance criteria
- API/data impact
- Security/privacy impact
- Failure/retry behavior
- Tests/validation
- Context/docs that must change

## Handling Missing Requirements

- Do not invent material product behavior not defined by requirements/context.
- Resolve ambiguity in the relevant project-context/ADR when it affects correctness or compatibility.
- Record blocking unknowns under **Open Questions** in `progress-tracker.md`.
- Use simple reversible defaults only for internal details that do not change product semantics or safety boundaries.

## Protected Areas

Do not weaken or bypass:

- tests and assertions;
- lint/type/security checks;
- CI/policy rules;
- migration history;
- generated third-party internals;
- secret-management boundaries;
- canonical context merely to make incomplete code appear correct.

Add project-specific protected paths here:

- `{{PROTECTED_PATH_1}}` — {{PROTECTED_REASON_1}}

## Required Work Loop

```text
Read context
  -> Inspect repository
  -> Frame task
  -> Design minimally
  -> Implement
  -> Validate
  -> Review diff
  -> Update context
  -> Report evidence
```

## Prior Project History

If Ragdoll Project History is enabled, use it only when prior decisions/evidence materially help the current task. Scope retrieval to the current project, prefer minimum sufficient evidence over full replay, and reconcile historical claims against current Project Context and repository reality.

Do not claim hidden model reasoning or unsupported IDE events were captured.

## Keeping Context in Sync

Update:

- `project-overview.md` when goals/scope/product behavior change;
- `architecture.md` when boundaries, stack, state model, or deployment change;
- `code-standards.md` when repository-specific conventions change;
- `ai-workflow-rules.md` when agent workflow/precedence changes;
- `progress-tracker.md` after meaningful implementation progress;
- `ui-context.md` when the design system or UI contract changes.

## Before Moving to the Next Unit

1. Acceptance criteria for the current unit are satisfied.
2. Applicable architecture invariants remain true.
3. Direct tests/checks pass.
4. Full applicable repository quality gates pass.
5. No secret or unsafe credential was committed.
6. Context reflects repository reality.
7. `git diff` has been reviewed for unrelated changes.
8. Checks not executed are reported explicitly.

## Context Provenance

- **OBSERVED:** {{OBSERVED_WORKFLOW_EVIDENCE}}
- **DECLARED:** {{DECLARED_WORKFLOW_EVIDENCE}}
- **INFERRED:** {{INFERRED_WORKFLOW_EVIDENCE}}
- **UNDECIDED:** {{UNDECIDED_WORKFLOW_ITEMS}}

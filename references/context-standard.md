# Context Standard and Project Context

Use this reference when creating, loading, updating, reviewing, or extending Ragdoll context.

## Purpose

Ragdoll separates universal engineering guidance from project-specific truth.

```text
Ragdoll engineering rules (`references/`)
        +
Project Context (`project-context/<domain>/`)
        +
Current repository reality
        =
Effective guidance for the current task
```

The reusable protocol and templates live under `context-standard/`.

## Terminology

- **Context Standard** — public Ragdoll specification that defines context domains, manifests, templates, provenance, loading, and lifecycle.
- **Context Domain** — a coherent knowledge scope such as `software-engineering`, `product-design`, or `research`.
- **Project Context** — the instantiated, maintained context of one specific project.
- **Context Manifest** — the project-level index of active domains and provenance policy.
- **Context Template** — reusable domain template used to bootstrap Project Context.

## Software Engineering domain

The first stable domain is `software-engineering`. Its six canonical files are:

1. `project-overview.md` — project purpose, users, goals, scope, constraints, success criteria.
2. `architecture.md` — system shape, boundaries, dependencies, state/storage, integrations, deployment, invariants.
3. `code-standards.md` — repository-specific languages, tooling, naming, organization, testing, and validation commands.
4. `ai-workflow-rules.md` — project-specific context loading, precedence, scoping, protected areas, and synchronization rules.
5. `progress-tracker.md` — current implementation state, next work, open decisions, and actual validation evidence.
6. `ui-context.md` — UI/design implementation context when applicable; otherwise `NOT_APPLICABLE` or `UNDECIDED`.

Future domains MAY define different files in their own `domain.yaml`. Never assume the six Software Engineering files are universal across all domains.

## Project Context layout

```text
project-context/
├── context-manifest.yaml
└── software-engineering/
    ├── project-overview.md
    ├── architecture.md
    ├── code-standards.md
    ├── ai-workflow-rules.md
    ├── progress-tracker.md
    └── ui-context.md
```

Read `project-context/context-manifest.yaml` first when it exists. Load only the domains and files relevant to the task.

## Provenance classes

Classify material claims as:

- **OBSERVED** — verified from repository/configuration/command output/deterministic tooling.
- **DECLARED** — explicitly established by current user requirements, accepted ADRs, or canonical project documentation.
- **INFERRED** — interpretation supported by evidence but not canonical.
- **UNDECIDED** — insufficient evidence or intentional open choice.

Rules:

1. Never silently upgrade `INFERRED` to `OBSERVED` or `DECLARED`.
2. Never invent a provider, framework, architecture style, deployment target, or product behavior merely to complete a template.
3. When code and context disagree, inspect freshness and authority; do not silently choose whichever is convenient.
4. Update Project Context when a meaningful repository change makes a canonical claim stale.
5. Keep evidence concise. Project Context is a decision/navigation layer, not a repository dump.

## Context generation

Use `scripts/generate_project_context.py` to bootstrap a conservative Software Engineering Project Context from an existing repository.

```text
repository evidence
  -> deterministic observations
  -> limited labeled inference
  -> six context drafts
  -> DRAFT_REQUIRES_REVIEW
```

The generator MUST NOT claim that architecture, workflows, test coverage, or product behavior are canonical merely because suggestive files or folders exist.

Validate an instantiated Project Context with:

```text
python scripts/validate_project_context.py <repository-or-project-context-path>
```

## Default precedence

For software-engineering work, use this default order unless the project explicitly defines a stronger valid policy:

1. Current explicit user/task instruction.
2. Safety, security, privacy, legal, and data-integrity constraints.
3. Accepted ADRs and explicit project invariants.
4. Relevant canonical `project-context/<domain>/` files.
5. Repository-local agent instructions and deterministic configuration not already represented above.
6. Universal Ragdoll engineering defaults in `references/`.
7. Existing implementation detail.
8. Model preference.

Existing code is evidence, not automatic authority.

## Cross-domain ownership

When multiple domains are active:

- use `context-manifest.yaml` as the index;
- load only relevant domains;
- assign each durable fact to one owning domain where practical;
- cross-reference the owner instead of duplicating contradictory copies;
- surface conflicts rather than resolving them silently;
- keep domain-independent governance in the Context Standard, not in one domain template.

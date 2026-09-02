# Ragdoll Context Standard

The **Ragdoll Context Standard** defines how durable project knowledge is organized so humans and AI agents can understand a codebase before changing it.

It is a public, reusable protocol. It is intentionally separate from both the universal engineering rules in `references/` and the instantiated knowledge of a specific repository in `project-context/`.

## Three different layers

```text
references/
  = reusable engineering rules

context-standard/
  = reusable context protocol, domain registry, and canonical templates

project-context/
  = instantiated canonical context for one specific project/repository
```

Do not merge these layers. A technology or rule that belongs only to one repository must not leak into the reusable standard.

## Why context domains exist

A flat context model would incorrectly assume that every professional field needs the same information. Ragdoll therefore organizes context by **domain**.

```text
context-standard/
├── registry.yaml
└── context-domains/
    └── software-engineering/
        ├── domain.yaml
        └── templates/
            ├── project-overview.md
            ├── architecture.md
            ├── code-standards.md
            ├── ai-workflow-rules.md
            ├── progress-tracker.md
            └── ui-context.md
```

`software-engineering` is the first domain. Future domains may define different file contracts, for example:

```text
product-design/
research/
data-engineering/
operations/
security/
legal/
```

Adding a domain does not require changing the six-file Software Engineering contract.

## Project Context

A project using Ragdoll receives or maintains a **Project Context** instance:

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

When additional domains are active, they become siblings under `project-context/`.

```text
project-context/
├── context-manifest.yaml
├── software-engineering/
├── product-design/
├── research/
└── operations/
```

`context-manifest.yaml` is the index. Agents SHOULD read it before loading domain context and SHOULD load only the domain files relevant to the current task.

## Software Engineering Context contract

The initial Software Engineering domain uses six canonical files:

| File | Question answered |
| --- | --- |
| `project-overview.md` | What are we building, for whom, and why? |
| `architecture.md` | How is the system organized and what boundaries must hold? |
| `code-standards.md` | How does this repository specifically write and validate code? |
| `ai-workflow-rules.md` | How should an AI agent work safely inside this repository? |
| `progress-tracker.md` | What is actually implemented, in progress, blocked, or undecided? |
| `ui-context.md` | What UI/design implementation rules apply, if UI exists? |

The six files are a **domain-specific standard**. They are not a universal file set for every future Ragdoll domain.

## Evidence and provenance

Material project claims should be classified as:

- **OBSERVED** — verified directly from repository files, configuration, command output, or deterministic tooling.
- **DECLARED** — explicitly established by the user, accepted ADR, canonical documentation, or another authoritative project source.
- **INFERRED** — a reasonable interpretation supported by evidence but not yet canonical.
- **UNDECIDED** — insufficient evidence or an intentionally open decision.

An `INFERRED` statement MUST NOT silently become `OBSERVED` or `DECLARED`.

The context generator is conservative by design. Detecting a folder called `domain/`, for example, does not prove that the repository follows Domain-Driven Design or Clean Architecture.

## Context lifecycle

```text
Inspect repository
  -> collect evidence
  -> select applicable context domains
  -> generate/curate a draft
  -> review important INFERRED and UNDECIDED items
  -> use Project Context during work
  -> synchronize it after meaningful changes
  -> re-verify when repository reality changes
```

Generated context is not disposable build output. After review, `project-context/` becomes durable project knowledge and must evolve with the codebase.

## Domain registration

Every public domain MUST:

1. have a stable identifier under `context-standard/context-domains/`;
2. provide a `domain.yaml` contract;
3. declare its canonical files and load policy;
4. define provenance expectations;
5. be registered in `context-standard/registry.yaml`;
6. avoid redefining facts clearly owned by another domain.

## Current scope

Only `software-engineering` is stable in this milestone. New domains should be introduced only when there is a real use case and a coherent information model, not pre-created as empty folders.

## Relationship to Project History

Project Context and Project History are intentionally separate.

- `project-context/` describes current canonical project knowledge.
- `~/.ragdoll/...` Project History records observable work that happened over time.
- Historical conversation is evidence and may explain decisions, but it does not automatically override current Project Context.
- Runtime model context should select only the relevant fragments from either source.

The public history contract lives under `project-history-standard/`, not inside a context domain.

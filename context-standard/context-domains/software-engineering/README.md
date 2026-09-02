# Software Engineering Context Domain

This domain defines the durable project knowledge needed by humans and AI agents when working on a software codebase.

Its scope is **software engineering only**. The six files in this domain are not a universal Ragdoll context schema for other fields.

## Canonical files

| File | Ownership |
| --- | --- |
| `project-overview.md` | Product/project purpose, users, goals, scope, constraints, success criteria |
| `architecture.md` | System structure, boundaries, dependencies, state, integrations, deployment, invariants |
| `code-standards.md` | Repository-specific language/tooling/naming/testing/quality conventions |
| `ai-workflow-rules.md` | AI context-loading, precedence, scoping, protection, and synchronization rules |
| `progress-tracker.md` | Verified implementation state, current goal, next work, blockers, open decisions |
| `ui-context.md` | UI/design implementation context when applicable |

The public templates live in `templates/`. A target codebase maintains its instantiated version under:

```text
project-context/software-engineering/
```

## Important boundary

Do not put generic software-engineering best practices into a target repository's `code-standards.md` simply because Ragdoll recommends them. Reusable rules belong in Ragdoll's `references/`; Project Context records facts and conventions specific to the codebase.

Do not infer architecture labels from directory names alone. Unknown material decisions remain `UNDECIDED` until stronger evidence exists.

## Project History

Project History is not a seventh Software Engineering context file. It is a separate local historical-evidence subsystem. When available, `ai-workflow-rules.md` may tell agents how to retrieve relevant prior work without replaying or duplicating all history into Project Context.

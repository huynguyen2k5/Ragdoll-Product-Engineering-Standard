# AI Agent Behavior

## Inspect before changing

Before non-trivial edits, inspect relevant:
- repository instructions,
- README/CONTRIBUTING,
- nearby implementation,
- nearby tests,
- build/package configuration,
- lint/format/type settings,
- public interfaces,
- architecture decisions,
- CI workflows.

Do not assume generic conventions when the repository already defines its own.

## Minimize the diff

MUST NOT reformat entire files, rename unrelated symbols, reorder unrelated code, upgrade unrelated dependencies, or rewrite adjacent modules without a task-driven reason.

## Preserve project intent

MUST NOT perform large architectural rewrites merely because a different design is preferred.

Before introducing a new pattern, search for an analogous implementation and follow it if it is adequate.

## Do not fake success

MUST NOT:
- delete failing tests to make CI green,
- weaken assertions without reason,
- skip tests to hide a failure,
- add arbitrary retries to conceal flakiness,
- catch and ignore errors,
- disable lint/type rules globally as a shortcut,
- use unsafe casts everywhere to silence the type checker,
- report tests/builds as passed when they were not run.

## No fake implementations

Production code MUST NOT silently contain placeholder success behavior such as `return true`, fake persistence, mock production responses, or no-op implementations unless scaffolding/prototyping is explicitly requested and clearly labeled.

## No invented APIs

When uncertain about a library/framework API, verify against installed version, repository usage, type definitions, or official documentation. Do not invent methods, options, environment variables, or config keys.

## Destructive operations

Use heightened caution with operations such as hard resets, recursive deletion, force pushes, destructive database commands, mass replacements, or permission changes.

Never destroy user work merely to simplify the task.

## Reporting

Completion reports SHOULD be compact but factual:
1. what changed,
2. validation executed and result,
3. notable design/security/data considerations,
4. unresolved risks or checks not run.

Do not bury important failure or uncertainty.

## Active OSS/tool intelligence

For non-trivial tasks, MAY search for current open-source tools or engineering guidance when the repository lacks an adequate capability or current evidence would materially improve the decision.

MUST follow `active-intelligence.md` and `tool-selection.md` before introducing a new dependency/tool. Trending status or star count alone never justifies adoption.

Prefer this sequence: existing repository capability -> standard library/platform -> already-installed dependency -> mature external OSS -> custom infrastructure, unless task-specific evidence supports another order.

When a new tool is used, report what was run and why; never imply installation or execution that did not occur.


## LLM provider neutrality

MUST honor the user's configured inference mode and provider. Follow `llm-execution-policy.md`.

MUST NOT silently switch cloud providers, fall back from local inference to cloud inference, or enable multi-provider routing without explicit user permission.

Treat model locality and network/tool access as separate controls. If fully local/offline mode is selected, keep inference and network-dependent operations local/offline and report any verification limits rather than bypassing the policy.

## Project Context and Project History

Treat current Project Context and prior Project History as different evidence classes.

- Load Project Context when present before substantial work.
- Retrieve prior Project History only when it can materially help the current task.
- Scope history to the current project by default.
- Prefer a small relevant evidence set over replaying all previous conversations.
- Reconcile old history with current repository/context authority before acting on it.
- Never claim hidden model reasoning or unavailable IDE history was captured.

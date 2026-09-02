# Testing, Review, and Quality Gates

## Test strategy

Tests are executable product expectations. Choose test depth proportional to risk.

Prefer a broad base of fast deterministic tests, supported by focused integration tests and a smaller number of end-to-end tests for critical journeys.

Tests SHOULD validate observable behavior rather than brittle implementation trivia.

## Determinism

Avoid uncontrolled sources of flakiness:
- arbitrary sleeps,
- real external network calls in unit tests,
- wall-clock dependence without clock control,
- shared mutable test state,
- test ordering assumptions,
- uncontrolled randomness.

Do not hide flaky tests with endless retries.

## Bug fixes

When practical:
`reproduce -> failing regression test -> fix -> passing test`

A bug-fix test SHOULD capture the user-visible or contract-level regression, not merely the current implementation.

## Edge and failure cases

Consider according to risk:
- empty/missing/invalid values,
- min/max boundaries,
- duplicates/idempotency,
- permission failures,
- concurrency/races,
- timeouts,
- retries,
- partial dependency failure,
- malformed external responses,
- rollback/recovery.

## Code review checklist

Review beyond CI status:
- correctness and acceptance criteria,
- design and unnecessary complexity,
- readability/naming/local reasoning,
- tests and failure behavior,
- security/privacy/data integrity,
- public compatibility,
- performance/concurrency implications,
- observability/operability,
- documentation,
- rollback/migration risk.

## Machine-enforced rules

Automate what can be checked reliably:
- formatting -> formatter,
- style/static bugs -> linter,
- types -> type checker,
- commit format -> commitlint or equivalent,
- tests -> test runner,
- security/dependencies -> scanners where appropriate,
- architecture boundaries -> dependency/static rules,
- build/deploy safety -> CI.

Documentation should explain rules; CI should enforce deterministic ones.

## Definition of Done

Before declaring a task complete, confirm applicable items:

- [ ] Requested behavior is implemented.
- [ ] Unrelated behavior is preserved.
- [ ] Relevant existing patterns/instructions were inspected.
- [ ] The solution is no more complex than necessary.
- [ ] Naming and structure are clear.
- [ ] Errors and failure paths are handled.
- [ ] Security/privacy/data boundaries were considered.
- [ ] Tests were added/updated where appropriate.
- [ ] Relevant existing tests pass.
- [ ] Format/lint/typecheck/build pass where available.
- [ ] Docs/config/API notes were updated when needed.
- [ ] Public compatibility was preserved or explicitly handled.
- [ ] Data migrations are safe where applicable.
- [ ] Sensitive information is not logged or committed.
- [ ] Diff contains no unrelated changes.
- [ ] Rollback/recovery is reasonable for the risk level.

If any applicable check was not executed, report it explicitly.

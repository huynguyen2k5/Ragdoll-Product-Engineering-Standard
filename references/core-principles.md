# Core Principles

## 1. Product correctness before code cleverness

- MUST optimize for correct product behavior, not maximum code generation.
- MUST preserve explicit acceptance criteria and public contracts.
- SHOULD prefer boring, obvious implementation over cleverness, hidden magic, or compressed one-liners.
- SHOULD optimize for the next engineer's ability to reason locally about the change.

## 2. Simplicity and scope discipline

- MUST solve the requested problem, not adjacent hypothetical problems.
- SHOULD apply YAGNI: do not build extensibility without a real requirement or evidence of near-term need.
- SHOULD tolerate small, understandable duplication until the shared concept is stable enough to name correctly.
- MUST NOT introduce a framework, service, abstraction layer, or dependency solely because it might be useful later.

A useful sequence is:

`concrete need -> simplest correct design -> observe repetition/change -> extract stable abstraction`

## 3. Evidence-based engineering

Use an engineering-scientific loop when uncertainty matters:

1. Define the question or failure precisely.
2. Collect observations from code, logs, tests, metrics, traces, docs, or reproducible behavior.
3. Form the smallest falsifiable hypothesis.
4. Change one meaningful variable when practical.
5. Validate with tests/measurements.
6. Compare expected vs actual outcome.
7. Keep, revise, or reject the hypothesis.

MUST NOT claim causality from correlation alone when the distinction matters.
MUST NOT optimize performance without a measurement or concrete constraint.
MUST prefer reproducible evidence over intuition for disputed technical decisions.

## 4. Explicit over implicit

- SHOULD make important dependencies, state transitions, side effects, failure modes, and permissions visible.
- SHOULD avoid hidden global mutation, action-at-a-distance, automatic registration, and ambient state unless required by the framework.
- SHOULD keep state ownership clear.

## 5. Small coherent changes

- SHOULD keep a change self-contained and focused on one concern.
- MUST NOT mix unrelated cleanup, reformatting, dependency upgrades, renaming, and feature behavior into one change without a concrete reason.
- SHOULD keep the repository buildable/testable after each meaningful commit when practical.
- SHOULD choose changes that are easy to review and roll back.

## 6. Reversibility

Before an expensive-to-reverse decision, consider:

- rollback path,
- migration path,
- compatibility window,
- data preservation,
- feature flag or staged rollout,
- observability needed to detect failure.

Prefer reversible decisions when two options are otherwise comparable.

## 7. Consistency vs local purity

Repository consistency normally beats introducing a new local style. Before creating a new pattern:

`search analogous code -> understand why it exists -> reuse if adequate -> introduce novelty only with a clear benefit`

## 8. Separation of concerns

- Business/domain logic SHOULD remain as independent as practical from UI, transport, persistence, vendor SDKs, and deployment concerns.
- Do not add layers mechanically. Add a boundary when it improves change isolation, testability, ownership, or contract clarity.

## 9. Decision records

Create or update an ADR for significant, long-lived, expensive-to-reverse decisions such as major storage, deployment, authentication, service-boundary, public API, or framework choices.

An ADR SHOULD include context, options, decision, rationale, consequences, migration/rollback, and references.
Never rewrite historical rationale silently; supersede it with a new decision.

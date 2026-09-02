# Coding Standard

## Naming

Names MUST communicate domain intent.

Avoid vague names such as `data`, `info`, `obj`, `thing`, `manager`, `helper`, `utils`, `misc`, `process`, or `doStuff` unless the domain makes them precise.

Prefer:
- action-oriented function names: `calculateShippingFee`, `refreshAccessToken`;
- predicate booleans: `isExpired`, `hasPermission`, `canRetry`;
- domain nouns for types/classes: `Invoice`, `PaymentAttempt`, `UserRepository`.

MUST follow repository/language casing conventions. Do not encode type information redundantly when the type system already carries it. Avoid ambiguous abbreviations.

## Functions and modules

A function SHOULD perform one coherent operation and expose clear inputs, outputs, side effects, and failure behavior.

A module SHOULD have a reason to change that can be described clearly. Avoid dumping unrelated code into `utils/`, `helpers/`, `common/`, `misc/`, or `shared/`.

Prefer domain-oriented organization when it matches the product.

## Comments and documentation

Comments SHOULD explain why, constraints, non-obvious trade-offs, invariants, or external quirks. Do not narrate obvious syntax.

Update relevant docs when behavior, configuration, public API, operational procedure, or architecture changes.

## Errors

- MUST NOT swallow errors silently.
- MUST preserve actionable context when transforming or propagating an error.
- MUST NOT expose secrets or sensitive internals to untrusted users.
- SHOULD distinguish failure classes only when callers benefit from different handling.
- SHOULD avoid exceptions/errors as ordinary control flow when clearer constructs exist.

## State and mutability

- SHOULD minimize mutable shared state.
- SHOULD define a clear owner for state.
- SHOULD prefer immutable values and controlled mutation boundaries where practical.

## Dependencies

Before adding a dependency, check:
1. Does the repository already provide the capability?
2. Can the language/platform standard library solve it safely?
3. Can an existing dependency solve it?
4. Is the new dependency maintained and appropriately licensed?
5. What transitive, security, bundle/runtime, and upgrade costs does it add?

MUST NOT upgrade unrelated dependencies opportunistically.

## Configuration and secrets

- MUST NOT commit real passwords, API keys, access tokens, private keys, or production credentials.
- SHOULD fail fast on invalid required configuration.
- SHOULD keep deployment-varying configuration outside hard-coded business logic.

## Compatibility

Treat public APIs, schemas, CLI contracts, configuration names, events, and persisted data formats more conservatively than private implementation.

Potentially breaking changes include removing/renaming fields, changing defaults or semantics, tightening accepted inputs, altering error behavior, or changing ordering/idempotency guarantees.

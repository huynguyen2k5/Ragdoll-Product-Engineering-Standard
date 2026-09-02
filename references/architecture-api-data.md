# Architecture, APIs, and Data

## Architecture

- MUST start from current product constraints rather than an idealized architecture.
- SHOULD prefer the simplest deployment/topology that meets scale, ownership, reliability, security, and delivery needs.
- MUST NOT introduce distributed systems or microservices without a concrete reason.
- SHOULD keep module/service boundaries aligned with meaningful business or operational boundaries.
- SHOULD keep high-level business rules from depending unnecessarily on low-level infrastructure details.

Before a major architecture change, record:
- current constraint/problem,
- evidence,
- viable alternatives,
- trade-offs,
- migration cost,
- compatibility impact,
- rollback plan.

## API contracts

APIs MUST be consistent, predictable, documented where public, and explicit about compatibility.

For REST-style HTTP APIs, prefer resource-oriented nouns and standard method semantics unless RPC/action semantics are intentional.

Use HTTP status codes to describe outcomes accurately; do not encode every failure as success.

API design SHOULD consider:
- pagination,
- filtering/sorting,
- idempotency,
- retries,
- concurrency/version conflicts,
- error schema,
- rate limits,
- authentication/authorization,
- deprecation/versioning.

## Data models

Domain models SHOULD represent business concepts rather than blindly mirror storage tables.

Enforce invariants at the strongest appropriate layer, using database constraints where they protect data integrity.

Be explicit about nullability, uniqueness, foreign keys, indexes, timestamps, deletion semantics, and retention.

## Database migrations

Production migrations MUST consider existing data and rolling deployment behavior.

For destructive or high-risk changes, prefer staged migration:

`add compatible schema -> deploy compatible app -> backfill -> switch reads/writes -> verify -> remove legacy later`

MUST NOT casually drop tables/columns, truncate data, rewrite applied migration history, remove integrity constraints, or reset a persistent environment.

Evaluate:
- lock duration,
- table size,
- index creation cost,
- backfill load,
- forward/backward compatibility,
- rollback limitations,
- mixed-version deployment window.

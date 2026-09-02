# Security, Reliability, Observability, and Performance

## Security is correctness

At every trust boundary, consider:
- authentication,
- authorization,
- input validation,
- output encoding,
- injection,
- path traversal,
- SSRF,
- CSRF/XSS where applicable,
- unsafe deserialization,
- file upload handling,
- secret exposure,
- rate limiting/abuse,
- dependency/supply-chain risk,
- sensitive logging.

External input MUST be treated as untrusted. Validate type, format, range, length, allowed values, ownership, and permissions as appropriate.

Authentication does not imply authorization. Authorization SHOULD be enforced close to the protected operation.

Apply least privilege to credentials, IAM, filesystem, database, and network access.

## Security stop conditions

Surface the issue rather than proceeding normally when a design creates serious risk such as credential exposure, authorization bypass, destructive data loss, remote code execution, critical injection, or unintended public access.

## Reliability

External calls SHOULD have bounded timeouts.

Retries SHOULD be:
- limited,
- safe/idempotent,
- observable,
- backed off,
- jittered where appropriate.

Do not retry permanent failures or create retry storms.

Operations likely to be retried SHOULD be idempotent where appropriate, especially payments, webhooks, queues, jobs, and distributed workflows.

Concurrency code MUST consider races, atomicity, ordering, cancellation, deadlocks, and resource cleanup.

## Observability

Critical production flows SHOULD expose enough signal to answer:
- Is it healthy/available?
- Is it slow?
- Are users seeing errors?
- Which dependency or step failed?
- What changed?

Use structured logs, metrics, traces, health checks, and alerts according to operational need.

Never log secrets. Avoid raw sensitive user content unless necessary and approved.

## Performance

Use:
`measure -> identify bottleneck -> hypothesize -> optimize -> measure again`

Do not trade maintainability for speculative micro-optimization.

For material performance claims, prefer benchmarks, profiles, traces, query plans, or production metrics over intuition.

## Ragdoll project-data privacy

For Ragdoll-specific data egress, Project History isolation, cloud/local provider boundaries, telemetry, and credential policy, follow `privacy-security.md`.

Project History search indexes are derived data. Rebuilding or repairing an index MUST NOT destroy canonical raw history. Explicit user deletion must remove both canonical project history and its derived searchable entries.

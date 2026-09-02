# Security Policy

Ragdoll is designed around local-first project data, explicit network boundaries, and deterministic checks. Security/privacy are architecture concerns, not optional post-release features.

## Security invariants

1. User project data remains local by default.
2. Ragdoll Core does not require Ragdoll-operated infrastructure.
3. Telemetry and cloud sync are disabled by default.
4. Network access and cloud-model access are separate permissions.
5. Cloud models receive token-budgeted, locally selected context rather than full Project History by default.
6. Project histories are isolated by stable project identity by default.
7. Search indexes are derived/rebuildable; canonical history is not destroyed by index operations.
8. Credentials are never bundled with Ragdoll and must not be serialized into Project Context/History metadata.
9. Local HTTP API access is authenticated; only loopback liveness/readiness probes are public and they exclude project/path data.
10. Provider egress is HTTPS-only and host-allowlisted in built-in adapters.
11. A selected provider failure must not trigger silent fallback to another provider.
12. Security-sensitive behavior should be transparent, auditable, and testable.

## Local API security

Default bind:

```text
127.0.0.1:8765
```

A non-loopback bind is rejected. `RAGDOLL_ALLOW_REMOTE_BIND=true` is reserved for a future authenticated TLS transport and currently fails closed.

A random token is stored at `~/.ragdoll/api-token`. All API endpoints except `/v1/health` and `/v1/ready` require `Authorization: Bearer <token>`. The readiness payload intentionally excludes project metadata and filesystem paths.

Requests with non-local browser origins are rejected. CORS is not enabled by default. Request bodies are capped by `RAGDOLL_MAX_REQUEST_BYTES`; non-empty bodies require JSON and transfer-encoded request bodies are rejected. Responses carry request IDs and defensive no-store/browser headers.

## Data handled by Ragdoll

Potentially sensitive data includes private source code, Project Context, Project History, terminal/tool output, Git metadata, credentials, repository identities, and generated artifacts.

See `PRIVACY.md` and `docs/security/THREAT_MODEL.md`.

## Network behavior

Project History storage/indexing, Project Context generation/validation, and local runtime-context compilation perform no required network requests.

A model request may contact only the selected built-in provider host. Built-in provider HTTP redirects are denied, requests have a bounded timeout, and provider responses have a local size limit. Active Intelligence/web research is a separate permission/integration and is not implied by provider access.

OpenAI Responses and Gemini Interactions requests disable provider-side API resource storage using `store=false`. Anthropic provider-side data handling remains governed by the user's Anthropic account/terms.

See `docs/security/NETWORK_POLICY.md` and `docs/security/PROVIDER_EGRESS.md`.

## Secrets

Common secret patterns are redacted before Project History persistence. Outbound provider context uses the same defense-in-depth secret detection with configurable behavior:

```text
RAGDOLL_OUTBOUND_SECRET_POLICY=redact
```

or stricter:

```text
RAGDOLL_OUTBOUND_SECRET_POLICY=block
```

Known sensitive paths should not be collected automatically for outbound model context. Pattern matching cannot prove arbitrary content safe.

## Installer/uninstaller security

Installers copy verified source into `~/.ragdoll/runtime/app` and do not require a Ragdoll-operated installer service. Normal reinstall/uninstall preserves Project History and `.env`. Explicit purge is separate.

Remote terminal/PowerShell bootstrap resolves a canonical GitHub Release, requires exactly one Ragdoll source ZIP plus `SHA256SUMS`, verifies SHA-256 before extraction/execution, and supports explicit version pinning. Local archive bootstrap also requires an expected SHA-256. Release signatures remain a future hardening option in addition to checksums.

## Supply chain

Ragdoll v1.0 local runtime intentionally uses Python's standard library only. New runtime dependencies require problem-fit, maintenance, security, license, and transitive-cost review.

CI actions and release artifacts should be pinned/verified more strongly as distribution matures.

## Reporting vulnerabilities

Do not publish credentials, private repository content, personal data, or working exploit payloads against third parties in public issues.

For non-sensitive concerns, open an issue with the smallest reproducible description and affected component. Before wider public adoption, configure a private security-reporting channel and document it here.

## Supported versions

Until the project reaches a stable public release line, security fixes target the current `main` branch and latest tagged development release.

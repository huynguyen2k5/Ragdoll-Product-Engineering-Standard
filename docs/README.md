# Ragdoll Documentation

Quick navigation for all documentation in this directory.

## Backend

| Document | Purpose |
|----------|---------|
| [API.md](backend/API.md) | Full HTTP API reference — endpoints, request/response shapes, error codes |
| [CORE_ARCHITECTURE.md](backend/CORE_ARCHITECTURE.md) | Internal module structure, layering constraints, and design decisions |
| [INSTALLATION.md](backend/INSTALLATION.md) | System requirements, installer scripts (Unix and Windows), upgrade path |
| [LOCAL_BACKEND.md](backend/LOCAL_BACKEND.md) | Loopback-only server rationale, lifecycle, PID management, and health checks |

## Security

| Document | Purpose |
|----------|---------|
| [THREAT_MODEL.md](security/THREAT_MODEL.md) | In-scope threats, trust boundaries, and accepted risks |
| [DATA_FLOW.md](security/DATA_FLOW.md) | How user data moves from editor to provider and what Ragdoll never touches |
| [SECRET_HANDLING.md](security/SECRET_HANDLING.md) | Redaction patterns, outbound secret policy, and key storage rules |
| [PROVIDER_EGRESS.md](security/PROVIDER_EGRESS.md) | Outbound HTTPS allowlist, redirect denial, and response size limits |
| [NETWORK_POLICY.md](security/NETWORK_POLICY.md) | Loopback bind enforcement, CORS origin validation, and API token policy |

## Product

| Document | Purpose |
|----------|---------|
| [OPEN_SOURCE_PRINCIPLES.md](product/OPEN_SOURCE_PRINCIPLES.md) | Governance, contribution model, and release philosophy |

## Release

| Document | Purpose |
|----------|---------|
| [PRE_RELEASE_REVIEW.md](release/PRE_RELEASE_REVIEW.md) | Checklist for every release: tests, security review, changelog, artifact signing |
| [PRODUCTION_WORKFLOW.md](release/PRODUCTION_WORKFLOW.md) | End-to-end release workflow from branch to published artifact |

---

> See also: [README.md](../README.md), [SECURITY.md](../SECURITY.md), [PRIVACY.md](../PRIVACY.md), [CHANGELOG.md](../CHANGELOG.md)

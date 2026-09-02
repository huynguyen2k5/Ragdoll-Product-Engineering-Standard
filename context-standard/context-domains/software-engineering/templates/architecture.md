# Architecture Context

## Architectural Goal

{{ARCHITECTURAL_GOAL}}

## System Context

```text
{{SYSTEM_CONTEXT_DIAGRAM_OR_FLOW}}
```

## Stack

| Layer | Technology | Role |
| --- | --- | --- |
| {{LAYER_1}} | {{TECHNOLOGY_1}} | {{ROLE_1}} |
| {{LAYER_2}} | {{TECHNOLOGY_2}} | {{ROLE_2}} |
| {{LAYER_3}} | {{TECHNOLOGY_3}} | {{ROLE_3}} |

Only list technologies actually selected by the project. Keep unresolved choices explicitly `UNDECIDED`.

## System Boundaries

- `{{PATH_OR_COMPONENT_1}}` — {{OWNERSHIP_AND_RESPONSIBILITY_1}}
- `{{PATH_OR_COMPONENT_2}}` — {{OWNERSHIP_AND_RESPONSIBILITY_2}}
- `{{PATH_OR_COMPONENT_3}}` — {{OWNERSHIP_AND_RESPONSIBILITY_3}}

For each important boundary, document what it owns and what it must not own.

## Dependency Direction

```text
{{DEPENDENCY_DIRECTION}}
```

## Storage and State Model

- **{{STORAGE_TYPE_1}}** — {{STORAGE_RESPONSIBILITY_1}}
- **{{STORAGE_TYPE_2}}** — {{STORAGE_RESPONSIBILITY_2}}

If the project has no persistent storage, state that explicitly.

## External Integrations

| Integration | Purpose | Trust Boundary / Ownership |
| --- | --- | --- |
| {{INTEGRATION_1}} | {{PURPOSE_1}} | {{BOUNDARY_1}} |

## Authentication and Access Model

- Authentication: {{AUTHENTICATION_MODEL}}
- Authorization: {{AUTHORIZATION_MODEL}}
- Ownership/tenancy: {{OWNERSHIP_MODEL}}

If not applicable or undecided, record `NOT_APPLICABLE` or `UNDECIDED` rather than inventing a provider.

## Deployment Shape

{{DEPLOYMENT_SHAPE}}

## Architecture Invariants

1. {{INVARIANT_1}}
2. {{INVARIANT_2}}
3. {{INVARIANT_3}}
4. {{INVARIANT_4}}

Invariants are rules implementation must never silently violate.

## Architecture Decisions / ADR Links

- {{ADR_OR_DECISION_1}}
- {{ADR_OR_DECISION_2}}

## Context Provenance

- **OBSERVED:** {{OBSERVED_ARCHITECTURE_EVIDENCE}}
- **DECLARED:** {{DECLARED_ARCHITECTURE_EVIDENCE}}
- **INFERRED:** {{INFERRED_ARCHITECTURE_EVIDENCE}}
- **UNDECIDED:** {{UNDECIDED_ARCHITECTURE_ITEMS}}

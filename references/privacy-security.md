# Privacy and Security Boundaries

Use this reference for data egress, project isolation, cloud/local model boundaries, history privacy, credentials, telemetry, plugins/tools, or sensitive codebases.

## Default posture

```text
Local by default.
Network by permission.
User data remains user-owned.
```

Ragdoll Core MUST NOT require a Ragdoll-operated server for Project Context, Project History, local retrieval, local validation, or the loopback Local Backend.

## Separate inference and network permissions

Treat model inference and general network access as independent permissions.

Valid profiles include:

- Local LLM + network denied;
- Local LLM + explicitly allowed web research;
- Cloud LLM + other network denied;
- Cloud LLM + controlled web access.

Permission to invoke a cloud model MUST NOT imply permission to upload arbitrary files, query arbitrary hosts, install packages, or sync history.

## Minimum necessary disclosure

For a cloud model:

```text
local repository/history
  -> project-scoped retrieval
  -> relevant selection
  -> secret/sensitivity filtering
  -> minimum sufficient context
  -> user-selected provider
```

Never replay the entire repository or entire Project History when a smaller verified context can answer the task.

## Secrets

Before persistence or outbound use, detect common credentials and sensitive material. Block or redact by default where safe to do so.

Never store bundled shared provider credentials. Use user-supplied credentials from local configuration such as `.env` or the process environment; a future OS credential-store adapter may be added as an optional stronger storage mechanism.

Known sensitive paths such as `.env`, private keys, and credential exports MUST NOT be collected automatically for cloud context.

Secret detection is defense in depth and cannot guarantee that arbitrary text is safe.

## Telemetry

Telemetry is disabled by default. A future telemetry feature must be explicit opt-in and document exactly what it collects. Source code, prompts, conversation content, file names, repository identity, credentials, and terminal output are excluded by default.

## Project isolation

Project A context/history MUST NOT be retrieved for Project B by default. Cross-project knowledge retrieval requires an explicit future policy and user intent.

## Workspace scope

Agents SHOULD default filesystem reads/writes to the current workspace and explicitly approved paths. Do not treat access to the user's home directory or other projects as implicit.

## Transparency

Security-sensitive behavior should be auditable. Future outbound integrations SHOULD expose enough metadata for the user to understand destination, purpose, and categories of project-derived data sent.

See `PRIVACY.md` and `docs/security/` in the source repository.

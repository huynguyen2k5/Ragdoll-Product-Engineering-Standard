# Privacy

Ragdoll is local-first. Core project registration, Project Context, Project History, retrieval, validation, and the local API do not require source code or history to be uploaded to Ragdoll-operated infrastructure.

## Default data behavior

| Data | Default location | Sent to Ragdoll-operated infrastructure? |
| --- | --- | --- |
| Source code | User machine | No |
| Project Context | User machine/repository | No |
| Project History | User machine under `~/.ragdoll` | No |
| Git metadata | User machine | No |
| Search/index data | Local SQLite | No |
| Local API token | `~/.ragdoll/api-token` | No |
| Provider API keys | User `.env` / environment | No |
| Telemetry | Disabled | No |
| Cloud sync | Disabled | No |

Ragdoll v1.0 has no telemetry transport, cloud-sync service, model proxy, mandatory account, or hosted Ragdoll data plane.

## Local backend

The built-in HTTP backend is loopback-only at `127.0.0.1:8765` by default. Non-loopback bind is rejected; `RAGDOLL_ALLOW_REMOTE_BIND=true` is reserved for a future authenticated TLS transport and currently fails closed.

All endpoints except `/v1/health` and `/v1/ready` require a random local bearer token generated on the user's machine. The public readiness probe excludes project metadata and filesystem paths. Non-local browser origins are rejected and CORS is not enabled by default.

## Cloud models

When a user explicitly invokes a configured cloud model, Ragdoll performs Project Context selection and Project History retrieval locally, applies a token budget, then applies the outbound secret policy before sending the resulting minimum context directly to the selected provider.

Built-in provider egress is allowlisted to the provider hosts documented in `docs/security/PROVIDER_EGRESS.md`.

OpenAI Responses requests are sent with `store=false`. Gemini Interactions requests are sent with `store=false`. Anthropic Messages requests are stateless from Ragdoll's perspective; provider-side retention/processing remains governed by the user's provider account and terms.

Ragdoll does not silently fall back from one provider to another.

## `.env`

Ragdoll does **not** auto-read a target project's generic `.env`. By default it reads only the Ragdoll-owned `$RAGDOLL_HOME/.env` (normally `~/.ragdoll/.env`), unless the user explicitly selects another file with `--env-file` or `RAGDOLL_ENV_FILE`. Process environment variables override loaded file values. `.env` and `.env.*` are ignored by Git in this repository.

API keys are not returned by `ragdoll status`, `ragdoll providers`, `/v1/status`, or `/v1/providers`.

## Local models

The architecture remains compatible with a Local Strict configuration where model inference, Project Context, Project History, retrieval, and tool execution remain local while external network access is denied. The v1.0 built-in provider adapters cover direct cloud APIs; richer local-model adapters remain separate integrations.

## Project isolation

Project History retrieval is scoped to the current `project_id` by default. Cross-project retrieval must not happen silently.

## Retention

Project History is retained indefinitely by default. Ragdoll does not automatically delete canonical history because of age, summarization, context compaction, index rebuild, IDE restart, reinstall, or normal uninstall.

`uninstall.sh` and `uninstall.ps1` preserve user data by default. Permanent deletion requires explicit purge options.

## Telemetry

Telemetry and analytics are disabled by default. Any future telemetry must be opt-in and documented before collection.

## Security limitations

No pattern-based scanner can prove arbitrary content is non-sensitive. Secret scanning/redaction is defense in depth. Users remain responsible for provider selection, provider account/privacy settings, machine security, repository permissions, and explicitly authorized external tools.

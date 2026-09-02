# Threat Model

## Assets to protect

- private source code and repository metadata;
- Project Context and architecture decisions;
- Project History and tool outputs;
- provider API keys and the local API bearer token;
- database URLs, environment secrets, private keys, cookies, and credentials;
- local file paths and user identity metadata;
- Git history and private remote information.

## Primary threats

1. Accidental disclosure to a cloud LLM or external tool.
2. Cross-project history leakage.
3. Secret persistence in local history/logs or outbound prompts.
4. A malicious browser page attempting to call the localhost API.
5. A local process attempting to call privileged Ragdoll endpoints without authorization.
6. Misconfiguration exposing the local API on a non-loopback interface.
7. Malicious or compromised dependency/tool behavior.
8. Prompt-induced access outside intended project scope.
9. Silent provider fallback, telemetry, sync, or background upload.
10. History corruption or derived-index loss.
11. Installer/release artifact tampering.

## Trust boundaries

Ragdoll treats these as separate boundaries:

- local Ragdoll data store;
- local HTTP API clients/IDE adapters;
- selected LLM provider;
- external web/research tools;
- source-control remotes;
- future optional sync services.

Permission to cross one boundary does not imply permission to cross another.

## Implemented controls

- loopback-only backend by default;
- random local bearer token for non-health API calls;
- non-local browser-origin rejection and no default CORS;
- request body size cap;
- HTTPS and provider-host allowlisting;
- no silent provider fallback;
- local retrieval/context compilation before outbound calls;
- secret redaction or block policy before provider egress;
- project-scoped history retrieval;
- append-only hash-chained canonical history;
- rebuildable SQLite/FTS index;
- no telemetry/cloud sync implementation;
- exact-ID confirmation for Project History purge;
- standard-library-only runtime in v1.0;
- GitHub Release bootstrap verifies the source ZIP against `SHA256SUMS` before executing extracted installer code.

## Limitations

Pattern-based secret detection cannot guarantee discovery of every secret. A malicious local process running as the same user may be able to read user-owned files, including `.env` or the local API token, depending on OS permissions. A compromised IDE/provider/OS is outside Ragdoll's ability to fully isolate. Security claims must preserve these boundaries rather than promise absolute confidentiality.

# Network Policy

## Default

Ragdoll local project/context/history operations are designed for `network_default = deny`.

Project Context validation/generation, Project History persistence, SQLite/FTS retrieval, Git inspection, local API handling, and runtime-context compilation MUST NOT require a network connection.

## Separate permissions

Treat these permissions separately:

- selected LLM provider access;
- web/repository research access;
- package download/install access;
- source-control push access;
- optional sync access;
- telemetry/analytics access.

Enabling one MUST NOT silently enable another.

## Local backend

The default backend binds to loopback only. Remote bind requires explicit opt-in. The local API does not provide a general HTTP proxy.

## Built-in provider egress

A `ragdoll chat` or `/v1/chat` request explicitly authorizes one call to the selected configured provider. Built-in adapters allow only HTTPS requests to:

- `api.openai.com`
- `api.anthropic.com`
- `generativelanguage.googleapis.com`

A provider failure MUST NOT silently switch to another provider.

## Outbound data principle

Retrieve locally and disclose minimally. Before sending project-derived content outside the machine, apply project scope, token budgets, sensitivity checks, and the configured secret policy.

## Telemetry and sync

Telemetry and cloud sync are disabled and have no transport implementation in v1.0. A future implementation must be explicit opt-in and separately authorized.

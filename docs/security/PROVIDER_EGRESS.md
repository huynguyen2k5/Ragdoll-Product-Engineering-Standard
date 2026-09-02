# Provider Egress

Ragdoll separates local project processing from explicit cloud-model egress.

## Default path

```text
Repository / Project Context / Project History
  -> local project-scoped retrieval
  -> token-budgeted context compilation
  -> secret redaction or blocking
  -> selected provider host only
```

## Allowlisted provider hosts

The built-in cloud adapters are limited to:

- `api.openai.com`
- `api.anthropic.com`
- `generativelanguage.googleapis.com`

Provider adapters reject non-HTTPS and non-allowlisted hosts.

## Server-side provider state

Ragdoll sends OpenAI Responses requests with `store=false` and Gemini `models.generateContent` requests with `store=false`. Ragdoll does not use provider-hosted conversation IDs as the canonical Project History store.

Anthropic Messages requests are stateless from Ragdoll's perspective; provider-side handling remains governed by the user's Anthropic account/terms.

## Secret policy

`RAGDOLL_OUTBOUND_SECRET_POLICY=redact` is the default. Common secret-like values are replaced before outbound context is sent. `block` rejects the provider request if secret-like content is detected.

Pattern-based secret detection is defense in depth, not proof that arbitrary context is safe.

# Secret Handling

## Defaults

- Do not bundle shared API keys or provider credentials.
- Load user-owned provider keys from `.env` or process environment.
- Never return configured API-key values from status/provider endpoints.
- Never serialize provider credentials into Project Context or Project History metadata.
- Redact common secret patterns before Project History persistence.
- Redact common secret patterns before provider egress by default.
- Allow a stricter outbound `block` policy.
- Do not automatically load known sensitive files into model context.

## `.env` precedence

1. explicit `--env-file`;
2. `RAGDOLL_ENV_FILE`;
3. Ragdoll-owned `$RAGDOLL_HOME/.env` (default `~/.ragdoll/.env`);
4. process environment variables override loaded file values.

Ragdoll intentionally does not auto-read a project workspace's generic `.env`, because application repositories commonly keep unrelated secrets there. Real `.env` files are Git-ignored; `.env.example` is a committed placeholder template with no credentials.

## Local API token

`~/.ragdoll/api-token` is generated with cryptographically secure randomness. On POSIX, Ragdoll attempts mode `0600`. Windows security also depends on the user's profile/filesystem ACLs.

## Sensitive path examples

- `.env` and `.env.*`
- private key files such as `*.pem`, `*.key`, and `id_rsa`
- credential exports
- browser/session cookies
- cloud-provider credential files

## Redaction is defense in depth

Pattern matching is imperfect. Never interpret successful redaction as proof that arbitrary content is safe to publish or send to a provider.

A future OS credential-store adapter may be added without making it mandatory; `.env` remains a supported local configuration path because it is simple and user-controlled.

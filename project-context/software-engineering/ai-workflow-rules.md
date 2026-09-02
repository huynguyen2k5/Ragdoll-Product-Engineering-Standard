# AI Workflow Rules

## Approach

Work context-first and evidence-first. Ragdoll is dogfooded on itself, so changes must keep the engineering standard, Project Context, Project History contract, Local Backend, provider/privacy/security behavior, implementation, tests, installers, and changelog coherent.

## Required Read

Before substantial changes to Ragdoll, read:

1. `project-context/context-manifest.yaml`;
2. relevant files in `project-context/software-engineering/`;
3. `SKILL.md`;
4. the owning reference/spec for the subsystem being changed;
5. nearby implementation and tests.

For history/privacy/backend/provider work additionally read:

- `project-history-standard/README.md`;
- `references/project-history.md`;
- `references/local-backend.md`;
- `references/privacy-security.md`;
- `references/llm-execution-policy.md`;
- `PRIVACY.md`, `SECURITY.md`, and relevant `docs/security/` files.

## Source-of-Truth Priority

1. Current explicit user requirement.
2. Safety, privacy, security, legal, and data-integrity constraints.
3. Accepted Ragdoll architecture/product decisions in current Project Context.
4. Current Project Context.
5. Public Ragdoll standards/contracts.
6. Deterministic implementation/tests/configuration.
7. Prior Project History.
8. Old summaries/inferences.
9. Model preference.

Do not use old conversation detail to override a newer canonical decision.

## Status Vocabulary

- **IMPLEMENTED** - code/artifact exists and relevant checks pass.
- **SPECIFIED** - contract/documentation exists but runtime behavior may not.
- **PLANNED** - intended future work.
- **UNDECIDED** - intentionally unresolved.
- **BLOCKED** - cannot safely proceed without prerequisite/decision.
- **DEPRECATED** - retained for compatibility/history but not intended for new work.

Never report automatic IDE conversation capture as IMPLEMENTED until an adapter can observe/capture it and tests prove behavior.

## Required Work Loop

```text
Read current context
  -> inspect implementation/history evidence
  -> frame exact problem
  -> choose smallest local-first solution
  -> implement
  -> run direct tests
  -> run full applicable validation
  -> review diff/security/privacy
  -> update Project Context/changelog
  -> report verified state
```

## Local Backend / Provider Rules

- Keep backend binding loopback-only by default.
- Preserve bearer-token protection for every non-health endpoint.
- Never expose provider-key values in API/CLI status output.
- Never persist provider keys into Project Context or Project History.
- Keep built-in provider egress in the explicit HTTPS host allowlist.
- Never silently fall back to another provider when the selected provider fails.
- Apply outbound secret filtering before model egress.
- Keep local Project Context/history retrieval functional without any API key.
- Do not introduce a mandatory model proxy, hosted Ragdoll service, telemetry collector, vector DB, or account system to solve a local problem.
- When current provider API behavior matters, verify against current primary documentation before changing the adapter.

## Installer Rules

- Preserve user data/configuration on normal install/reinstall/uninstall.
- Require an explicit destructive purge action to delete `~/.ragdoll` user data.
- Do not download or execute unverified remote code as a hidden installation step.
- Keep source/release artifacts as the canonical runtime source.
- Test POSIX lifecycle behavior when installer code changes.
- Do not claim Windows runtime verification unless a clean Windows/PowerShell environment was actually exercised.

## History Rules

- Retrieve only current-project history by default.
- Use focused retrieval during normal work.
- Use comprehensive/forensic modes only when needed.
- Do not load all history into the model merely because it exists.
- Raw canonical history must survive summary/context compaction.
- Never weaken retention or project isolation silently.
- Never add a mandatory hosted/vector service without explicit evidence and architecture approval.

## Privacy Rules

- No silent telemetry.
- No silent cloud sync.
- No silent local-to-cloud or provider-to-provider fallback.
- No bundled credentials.
- Do not automatically expose known sensitive files.
- Minimize outbound project-derived context.
- Networked behavior must document destination, purpose, permission boundary, and data categories.

## OSS / Sustainability Rules

Before introducing a hosted dependency or paid managed service, ask whether local files/SQLite/stdlib/user-owned infrastructure can solve the demonstrated problem. The maintainer must not inherit proportional infrastructure cost merely because open-source adoption grows.

## Protected Areas

Do not weaken these merely to make checks pass:

- `scripts/validate_skill_pack.py`;
- `scripts/validate_project_context.py`;
- Project History integrity/project-isolation/security tests;
- Local Backend authentication/remote-bind/provider-egress tests;
- install/uninstall data-preservation tests;
- `PRIVACY.md`/security invariants;
- canonical Context Standard/history contracts;
- CI validation;
- retention and explicit-delete semantics.

## Before Completion

1. Scope is focused.
2. Architecture invariants remain true.
3. Applicable validators/tests compile and pass.
4. History changes preserve canonical raw data across index rebuild.
5. Backend/provider/install changes have direct regression coverage where feasible.
6. Privacy/security behavior has regression coverage when feasible.
7. Project Context/changelog are synchronized.
8. Final diff is reviewed.
9. Unrun checks and limitations are reported.

## Context Provenance

- **OBSERVED:** The repository has deterministic Project History tests, Local Backend/API tests, provider request-contract tests, configuration tests, and installer safety tests.
- **DECLARED:** Dogfooding, local-first privacy, low token use, project isolation, BYO providers, safe install/uninstall, and low maintainer infrastructure cost are primary workflow constraints.
- **INFERRED:** Real IDE usage will reveal which observable events, summaries, and adapter hooks deserve richer support.
- **UNDECIDED:** Exact automatic Antigravity capture mechanism, future encrypted-at-rest history UX, and future hosted commercial capabilities.

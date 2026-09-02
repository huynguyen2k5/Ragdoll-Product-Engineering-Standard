---
name: ragdoll-product-engineering-standard
description: Apply Ragdoll's local-first, vendor-neutral Product Engineering Standard to AI-assisted software/product work. Use for coding, debugging, refactoring, testing, review, architecture, APIs, data, Git, CI/CD, security, reliability, OSS/tool evaluation, Project Context generation/maintenance, or per-project AI conversation/history retrieval. Respect project-specific rules, user-selected cloud/local LLM boundaries, local privacy defaults, and token-efficient history retrieval; never fabricate project facts, silently mix histories across projects, bypass validation, or treat popularity as engineering evidence.
---

# Ragdoll Product Engineering Standard

Use Ragdoll as a control plane for disciplined engineering plus local project knowledge/evidence. Keep changes evidence-based, minimal, testable, reversible, private by default, and consistent with current repository reality.

Ragdoll is not a general-purpose coding harness. It provides deterministic local utilities plus a loopback Local Backend for Project Context, Project History, token-aware retrieval, and direct user-key provider calls without taking over arbitrary tool orchestration, retries, sandboxes, or multi-agent scheduling.

## Rule precedence

Apply rules in this order:

1. Explicit current user/product requirements.
2. Safety, security, privacy, legal, and data-integrity constraints.
3. Accepted architecture decisions and explicit project invariants.
4. Reviewed Project Context and repository-local instructions.
5. Deterministic repository configuration and established codebase conventions.
6. Language/framework conventions.
7. Ragdoll reusable defaults.
8. Model preference.

Never replace a valid project convention merely because another convention is more familiar.

## Load Project Context first

When `project-context/context-manifest.yaml` exists:

1. read the manifest;
2. identify active domains relevant to the task;
3. load only required domain files;
4. verify implementation-status claims against current repository reality;
5. synchronize the owning Project Context file when a meaningful change makes it stale.

Use `references/context-standard.md` for the Software Engineering six-file contract, provenance, precedence, generation, and cross-domain rules.

When Project Context is missing and the user wants it, use `scripts/generate_project_context.py` to create a conservative `DRAFT_REQUIRES_REVIEW`. Never promote `INFERRED` or `UNDECIDED` claims to canonical fact without evidence.

## Use Project History without replaying everything

Project History is evidence of what happened, not automatic current authority.

When prior work matters:

1. scope retrieval to the current `project_id`;
2. prefer structured/file/commit/conversation identifiers when available;
3. use focused retrieval for routine work;
4. use comprehensive retrieval when the user explicitly asks for all matching history;
5. use forensic retrieval for traceability questions;
6. compile only the minimum sufficient evidence under a token budget;
7. expand to raw events only when summaries/index hits are insufficient;
8. reconcile old history against current Project Context/repository reality before acting on it.

Use `references/project-history.md` and the public contract under `project-history-standard/`.

Do not claim automatic IDE conversation capture unless the active adapter actually exposes observable events. Never claim hidden provider reasoning was stored.


## Use the Local Backend when installed

When the local `ragdoll` command is available, prefer it over ad-hoc scripts for project registration, context generation/validation, history retrieval, backend lifecycle, and direct configured-provider calls.

Use `.env`/process environment for user-owned provider keys. Never request that credentials be committed to the repository, written into Project Context, or persisted into Project History. Do not expose API-key values through status/reporting output.

The default Local API must remain loopback-only and bearer-token protected. Treat provider access as explicit egress to the selected allowlisted provider only; never silently fall back to another provider.

Keep `RagdollCore` transport-neutral. CLI, HTTP, future MCP, and later IDE adapters must reuse Core services instead of reimplementing project/context/history/storage/security behavior. Treat `ragdoll.history` as the production history implementation; `tools/project_history` is compatibility-only.

Use `references/local-backend.md` for Core boundaries, installation, `.env`, API, provider, and adapter behavior.

## Required operating loop

For non-trivial work:

1. **Inspect** - read relevant Project Context, instructions, nearby code, tests, configs, public interfaces, recent patterns, and relevant history only when needed.
2. **Frame** - state the actual problem, constraints, unknowns, and acceptance criteria. Separate observation, declaration, inference, and uncertainty.
3. **Design minimally** - choose the smallest coherent solution; avoid speculative abstractions and hosted infrastructure without demonstrated need.
4. **Implement** - keep the diff focused and preserve unrelated behavior.
5. **Validate** - format, lint, typecheck, test, build, and run targeted security/data checks as available.
6. **Review the diff** - inspect correctness, complexity, naming, failure modes, compatibility, security, privacy, performance, observability, and context drift.
7. **Synchronize** - update Project Context and record durable decisions/evidence when materially changed.
8. **Report** - say what changed, what was actually validated, what remains uncertain, and any risk/follow-up.

For bug fixes, prefer reproduce -> failing regression test -> fix -> passing test.
For performance work, prefer measure -> hypothesize -> change -> measure again.
For architecture changes, prefer evidence -> alternatives -> trade-offs -> reversible decision.

## Never hide uncertainty

Classify important project claims as:

- **OBSERVED** - verified directly from repository/configuration/tool output;
- **DECLARED** - explicitly established by user requirements, accepted ADRs, or canonical docs;
- **INFERRED** - supported interpretation that is not yet canonical;
- **UNDECIDED** - insufficient evidence or intentionally open.

Do not invent library APIs, repository conventions, test results, benchmarks, architecture styles, product behavior, successful executions, or history completeness that was not verified.

## Privacy and security defaults

Use the principle:

```text
Local by default.
Network by permission.
User data remains user-owned.
```

Treat cloud-model access and general network access as separate permissions. Never silently switch providers, fall back from local to cloud, enable telemetry, sync Project History, or send unrelated repository/history data outside the permitted boundary.

For cloud models, retrieve locally and disclose the minimum necessary sanitized context. Project A history must not be retrieved for Project B by default.

Use `references/privacy-security.md` and `references/llm-execution-policy.md`.

## Sustainable open-source architecture

Before adding mandatory hosted infrastructure, managed databases, vector services, or maintainer-funded model access, consult `references/local-first-architecture.md`.

Prefer user-owned local files/SQLite/compute/storage and BYO providers. More open-source users should not require proportionally larger Ragdoll infrastructure bills.

Do not build commercial infrastructure before dogfooding proves real value. Future commercial features may monetize managed sync, collaboration, organization-scale knowledge, governance, or convenience without intentionally crippling local ownership of Project Context/History.

## Active Intelligence

When external discovery can materially improve a non-trivial task, MAY search current primary sources and mature OSS candidates. Follow `references/active-intelligence.md` and `references/tool-selection.md`.

Popularity is discovery input only. Prefer existing repository capabilities unless a new tool has clear net benefit. Never install or execute a newly discovered tool without checking scope, provenance, permissions, dependency/security cost, compatibility, and license where relevant.

## Load references selectively

Read only what the current task needs:

- `references/core-principles.md` - decision method and core engineering principles.
- `references/coding-standard.md` - naming, code structure, errors, dependencies.
- `references/architecture-api-data.md` - architecture, APIs, data, migrations.
- `references/testing-quality.md` - testing, review, CI, Definition of Done.
- `references/security-reliability.md` - secure coding, reliability, observability, performance.
- `references/privacy-security.md` - data egress, project isolation, credentials, telemetry, network boundaries.
- `references/git-release.md` - Git, commits, versioning, PRs, releases.
- `references/agent-behavior.md` - AI-agent behavior and anti-patterns.
- `references/llm-execution-policy.md` - cloud/local/hybrid inference and network boundaries.
- `references/context-standard.md` - Context Standard and Project Context.
- `references/project-history.md` - persistent per-project history and retrieval.
- `references/local-first-architecture.md` - sustainable local-first infrastructure/economics.
- `references/local-backend.md` - installation, `.env`, loopback API, provider calls, and IDE adapter surface.
- `references/active-intelligence.md` - current OSS/standards discovery.
- `references/tool-selection.md` - candidate evaluation/adoption.
- `references/tool-catalog.md` - curated discovery categories.
- `references/evolution-governance.md` - evidence-gated rule evolution.
- `references/sources.md` - source registry/evidence tiers.
- `references/antigravity.md` - Google Antigravity integration/evaluation.
- `references/integration.md` - cross-IDE/agent adapters.

## Normative keywords

Interpret MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY in the RFC 2119 sense.

## Evolution rule

Do not silently rewrite Ragdoll from a new article or trending repository. New normative rules require provenance, scope, evidence strength, conflict analysis, and changelog updates.

Do not force the six Software Engineering context files onto future non-software domains. Do not treat one IDE's conversation format as the universal history schema; adapters normalize observable events into the Project History contract.

## Completion contract

Before declaring work complete:

1. run applicable repository checks;
2. review the final diff;
3. synchronize Project Context if canonical facts changed;
4. verify Project History/security changes when relevant;
5. state checks that could not run instead of implying success.

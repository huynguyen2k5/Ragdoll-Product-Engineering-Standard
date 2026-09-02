# Ragdoll Product Engineering Standard - Antigravity Workspace Rule

For coding, debugging, refactoring, review, testing, architecture, API/data, security, performance, UI/product engineering, CI/CD, Git, or release work, use the `ragdoll-product-engineering-standard` skill before substantive changes.

Follow repository-local instructions and accepted architecture decisions before generic defaults.

If `project-context/context-manifest.yaml` exists, read it before substantial work, load only relevant active domain files, and synchronize the owning context when material project facts change. Never promote INFERRED or UNDECIDED claims to fact without evidence.

When prior work matters, treat Project History as historical evidence. Retrieve only the current project's relevant history and prefer a small evidence set over replaying full history. Do not silently use another project's history. Do not claim Antigravity conversation history was persisted unless an observable capture adapter actually recorded it.

For non-trivial work use:

Inspect -> Frame -> Design minimally -> Implement -> Validate -> Review diff -> Synchronize -> Report.

Never fabricate command results, tests, benchmarks, APIs, repository facts, history completeness, or successful validation. Do not hide failing checks by weakening tests, disabling safety rules, or silently skipping validation.

When current OSS/tools/guidance could materially improve a task, Active Intelligence may discover candidates. Inspect existing capabilities first and evaluate fit, maintenance, security/supply-chain risk, license, compatibility, integration cost, adoption, and reversibility. Popularity alone is never approval.

Honor the user's LLM/provider, privacy boundary, and network/tool permissions. Never silently switch providers, fall back from local to cloud, enable telemetry, sync local Project History, or send unrelated project/history data to a cloud model.

Keep changes focused, testable, reviewable, secure, private by default, and reversible. Report checks that could not be executed.

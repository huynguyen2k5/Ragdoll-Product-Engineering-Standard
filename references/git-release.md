# Git, Commits, Versioning, PRs, and Releases

## Branches

If the repository has no branch convention, prefer short lowercase kebab-case with a meaningful type prefix:

- `feat/<description>`
- `fix/<description>`
- `refactor/<description>`
- `docs/<description>`
- `test/<description>`
- `chore/<description>`
- `perf/<description>`
- `security/<description>`
- `build/<description>`
- `ci/<description>`

Repository-specific trunk-based or other workflow overrides this default.

## Conventional Commits

If no repository-specific commit convention exists, use:

`<type>[optional scope]: <description>`

Recommended types: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`, `ci`, `chore`, `revert`.

Descriptions SHOULD be concise and explain the actual change. Avoid `update stuff`, `fix bug`, `final`, `misc`, and similar non-semantic messages.

Commits SHOULD be logically atomic and leave the repository in a valid state when practical.

## Semantic Versioning

Use SemVer when the software exposes a versioned public contract and SemVer fits the ecosystem:

- MAJOR: incompatible public API change,
- MINOR: backward-compatible functionality,
- PATCH: backward-compatible bug fix.

Do not modify the contents of an already published version; release a new version.

Use prerelease identifiers such as `alpha`, `beta`, or `rc` consistently when appropriate.

## Pull requests / change lists

When the repository declares a protected-trunk workflow, treat the Pull Request as the production change unit: one coherent change -> one short-lived branch -> one PR -> required checks -> merge -> delete branch. Do not invent PR numbers locally; GitHub assigns real `#N` values when PRs are created.

For Ragdoll itself, prefer Squash and merge so `main` receives one traceable commit per PR and release tags are created only from validated `main`. See `docs/release/PRODUCTION_WORKFLOW.md`.

A change description SHOULD answer:
- What changed?
- Why?
- How was it implemented?
- How was it validated?
- What risks/compatibility concerns exist?
- How can it be rolled back?

Prefer small self-contained changes that reviewers can understand thoroughly. Include related tests in the same logical change.

## Releases

A release SHOULD have:
- clear version/tag,
- generated or curated change summary,
- migration/breaking-change notes,
- validated artifacts,
- rollback/recovery plan appropriate to risk,
- traceability to source commits and CI.

Do not bypass required CI gates or failing tests simply to ship faster without an explicit, documented exception process.

# Production GitHub Workflow

Ragdoll uses a protected-trunk workflow: `main` is the only long-lived production branch, and every logical change reaches `main` through a GitHub Pull Request.

## Invariants

1. Do not push implementation changes directly to `main`.
2. Create one short-lived branch for one coherent change.
3. Keep commits inside the branch logically atomic and buildable when practical.
4. Open one Pull Request for that change and let GitHub assign its real `#N` number.
5. Require the repository validation checks to pass before merge.
6. Resolve review conversations before merge.
7. Prefer **Squash and merge** so `main` gets one traceable change commit ending in the GitHub PR number, for example `feat(history): add durable migration recovery (#42)`.
8. Delete the head branch after merge.
9. Create release tags only from the validated `main` commit after all intended release PRs are merged.
10. Never rewrite an already published release tag or published `main` history.

GitHub Issues and Pull Requests share the repository number sequence. Therefore PR numbers are not planned or generated locally; GitHub assigns them when the PR is created.

## Branch names

Use lowercase kebab-case with a change-type prefix:

```text
feat/<description>
fix/<description>
refactor/<description>
security/<description>
perf/<description>
test/<description>
docs/<description>
build/<description>
ci/<description>
chore/<description>
release/<version>
```

A `release/<version>` branch is only for final release metadata or narrowly scoped release preparation. It must not become a second long-lived development branch.

## Change lifecycle

```text
main
  -> branch from current main
  -> implement + local validation
  -> push branch
  -> GitHub PR #N
  -> CI / review / conversation resolution
  -> squash merge
  -> delete branch
  -> update local main with --ff-only
```

Start the next logical change from the newly merged `main`, not from the previous feature branch.

## Release lifecycle

For `v1.0.0` and later:

```text
planned PRs merged
  -> main CI green
  -> release-level validation
  -> annotated tag vX.Y.Z on main
  -> push tag
  -> GitHub Release workflow verifies tag == package version
  -> deterministic source ZIP + SHA256SUMS
```

Use Semantic Versioning:

- MAJOR for incompatible public-contract changes;
- MINOR for backward-compatible functionality;
- PATCH for backward-compatible fixes.

The canonical production tag is the complete SemVer tag, for example `v1.0.0`. A floating major alias such as `v1` may be added later only if an integration needs it; it is not the canonical release identity.

## Recommended repository rules for `main`

Configure a GitHub Ruleset or branch protection policy that:

- requires Pull Requests before merge;
- requires the repository CI checks;
- requires branches to be up to date when necessary for safe validation;
- requires conversation resolution;
- blocks force pushes;
- blocks branch deletion;
- disables direct implementation pushes to `main`;
- enables automatic deletion of merged head branches.

For a solo maintainer, required reviewer count may remain zero while the PR and CI gates still protect `main` from accidental direct changes.

## Pull Request content

Every production PR should state:

- what changed;
- why the change is needed;
- the implementation boundary;
- validation evidence;
- compatibility/security/privacy risk;
- rollback or recovery considerations when relevant;
- whether Project Context, changelog, API contract, or release notes must change.

Do not split tests into a later PR when the tests are required to prove the behavior of the current change. A logical PR should carry the tests necessary for its own correctness.

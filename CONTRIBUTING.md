# Contributing

Ragdoll is a living engineering standard plus small local-first reference utilities. Contributions should improve real reliability, clarity, privacy, portability, or evidence quality rather than add speculative features.

## Development priority

Prefer changes backed by observed dogfooding pain. Avoid building SaaS, enterprise, multi-agent, or hosted infrastructure simply because it may be useful later.

## Normative rule proposals

Classify source/evidence strength. Prefer:

1. formal specifications and standards;
2. primary documentation from mature engineering organizations;
3. maintained OSS with demonstrated use;
4. well-reasoned senior engineering guidance;
5. community discussion as discovery input only.

Popularity, stars, or trending status are not approval.

A normative proposal should include problem, scope, provenance, evidence strength, alternatives, trade-offs, exceptions, conflicts, and intended MUST/SHOULD/MAY strength.

## Context Standard changes

Follow `references/context-standard.md`. Keep the registry, domain contract, templates, validators, self-context, and changelog synchronized. Do not generalize Software Engineering's six-file contract to unrelated domains.

## Project History changes

Follow `project-history-standard/README.md` and `references/project-history.md`.

Required properties include:

- local-first defaults;
- project isolation;
- no automatic retention expiry;
- canonical history independent from disposable indexes;
- no hidden network behavior;
- token-aware retrieval;
- explicit deletion semantics;
- migrations that preserve existing canonical history.

Security/privacy changes should include deterministic tests where practical.

## Production Git workflow

`main` is the only long-lived production branch. Do not push implementation changes directly to it. Use one short-lived branch and one GitHub Pull Request for each coherent change. GitHub assigns the real PR `#N` number; Issues and Pull Requests share that repository sequence, so numbers must not be fabricated locally.

Prefer **Squash and merge** for production PRs so `main` contains one traceable change commit with the GitHub PR number. Delete the head branch after merge and start the next change from the newly merged `main`. Release tags are created only from validated `main` after all intended release PRs have merged.

See `docs/release/PRODUCTION_WORKFLOW.md` for branch naming, PR gates, branch protection, and release sequencing.

## Engineering checks

Before opening a pull request run:

```text
python scripts/validate_skill_pack.py
python scripts/validate_project_context.py .
python scripts/evaluate_candidate.py scripts/candidate.example.json
python -m unittest discover -s tests -v
python -m compileall -q ragdoll scripts tools tests
```

Smoke-test Project Context generation when its generator/domain contract changes. Exercise `scripts/ragdoll_history.py` when Project History behavior changes.

Keep pull requests focused, inspect the final diff, and update `CHANGELOG.md` for user-visible changes. Use Conventional Commits.

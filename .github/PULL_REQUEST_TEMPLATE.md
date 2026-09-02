## What changed

Describe the change and why it is needed.

## Change boundary

State the single coherent change owned by this PR and any intentionally excluded follow-up work.

## Evidence / rationale

For normative rule changes, include source provenance, evidence strength, scope, alternatives, and trade-offs.

## Validation

- [ ] `python scripts/validate_skill_pack.py`
- [ ] `python scripts/validate_project_context.py .`
- [ ] Project Context generator smoke test if context contracts/generation changed
- [ ] Candidate evaluator smoke test if relevant
- [ ] Final diff reviewed
- [ ] Tests needed to prove this change are included in this PR
- [ ] Project Context synchronized when canonical facts changed
- [ ] `CHANGELOG.md` updated when user-visible behavior changed

## Risk / compatibility

Describe any behavior, portability, privacy, security, or integration risk.


## Release impact

State `none`, `patch`, `minor`, or `major`, and explain any public-contract impact.

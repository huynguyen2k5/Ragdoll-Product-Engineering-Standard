# Evolution Governance

This standard is intentionally a living system. It may improve as software engineering practice evolves, but it MUST NOT drift based on hype, popularity, or a single author's preference.

## Evidence hierarchy

Treat sources approximately in this order, adjusted for context:

1. **Normative specification / security standard / language specification**
2. **Official project or vendor engineering guidance with active maintenance**
3. **Widely adopted open-source engineering practice with demonstrated longevity**
4. **Engineering handbooks from organizations operating comparable systems**
5. **Detailed writing from recognized senior/principal engineers with explicit reasoning and examples**
6. **Empirical study, benchmark, incident/postmortem, or reproducible experiment**
7. **Community convention / popularity signal**
8. **Unverified opinion**

Popularity and GitHub stars are discovery signals, not evidence that a rule is universally correct.

## Relationship to Active Intelligence

`active-intelligence.md` governs runtime discovery during a product task. This file governs promotion of durable learning into the canonical standard. A tool may be useful in one task without becoming a universal recommendation.

## Source intake workflow

When asked to update this skill from repos/blogs or when researching a new rule:

1. Define the engineering problem the proposed rule addresses.
2. Prefer the primary source; record URL, author/maintainer, date/version if available, and access date.
3. Determine evidence tier and whether the source is actively maintained.
4. Extract the principle, not wording to copy.
5. Search for corroborating or conflicting guidance when the rule is broad or controversial.
6. Test against real product scenarios and known trade-offs.
7. Classify scope: universal, ecosystem-specific, language-specific, architecture-specific, or contextual.
8. Assign normative strength: MUST / SHOULD / MAY.
9. Record exceptions and known counterexamples.
10. Update the relevant reference file and `sources.md`.
11. Add a concise entry to `CHANGELOG.md`.
12. Run `scripts/validate_skill_pack.py` before packaging.

## Rule admission criteria

A candidate rule SHOULD be admitted only if it improves one or more of:
- correctness,
- maintainability,
- security/privacy,
- reliability,
- reviewability,
- testability,
- operability,
- delivery safety,
- developer/agent reasoning quality.

A rule MUST NOT be promoted to universal MUST solely because:
- a famous engineer prefers it,
- a trending repository uses it,
- one company uses it internally,
- it is aesthetically appealing,
- it reduces lines of code without improving outcomes.

## Conflict resolution

When credible sources disagree:
- document the competing goals,
- identify contextual variables,
- prefer repository evidence and explicit product constraints,
- downgrade the rule from MUST to SHOULD/MAY if universality is not justified,
- encode decision criteria rather than pretending there is one universal answer.

Example: microservices vs modular monolith should be a decision framework, not a universal architecture mandate.

## Deprecating rules

A rule may be weakened or removed when:
- underlying technology changes,
- strong evidence shows harm,
- the rule is replaced by better automation,
- the ecosystem's standard changes,
- the rule was over-generalized.

Do not delete history. Record the change in `CHANGELOG.md` with rationale.

## Periodic review

When performing a standards refresh, review high-impact domains separately:
- code/readability,
- testing,
- security,
- API/data,
- reliability/observability,
- Git/release/CI,
- AI-agent workflow.

Prefer a small number of well-supported changes over large speculative rewrites.

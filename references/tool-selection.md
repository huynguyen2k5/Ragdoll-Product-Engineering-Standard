# Open-Source Tool and Repository Selection

Use this framework when evaluating a new OSS repository, tool, library, design system, coding utility, or engineering practice.

## Gate 1: Problem fit

Answer first:

- What concrete problem does this solve?
- Does the repository already solve it?
- Can the language/platform standard library solve it adequately?
- Is this a recurring problem or a one-off task?
- Does the tool reduce total complexity, not just implementation lines?

If the problem is vague, do not adopt a tool yet.

## Gate 2: Technical fit

Evaluate:

- compatibility with the current language/framework/runtime;
- supported operating systems and CI environment;
- integration with existing formatter/linter/test/build tooling;
- configuration and migration cost;
- performance/runtime footprint;
- deterministic/headless operation for AI and CI;
- ability to remove or replace the tool later.

## Gate 3: Project health

Prefer evidence such as:

- active maintainers and recent meaningful commits/releases;
- clear release/version policy;
- resolved or constructively handled issues;
- documented breaking changes and upgrade guidance;
- meaningful automated tests and CI;
- security policy/advisories where appropriate;
- stable documentation;
- non-trivial adoption outside the maintainer's own demos.

Do not use star count as a proxy for these properties.

## Gate 4: Security and supply chain

Check when material:

- license compatibility;
- maintainer/repository authenticity;
- package provenance and canonical registry package;
- known vulnerabilities/advisories;
- install/postinstall scripts;
- transitive dependency footprint;
- required permissions/secrets/network access;
- release artifact/signing/provenance support when relevant.

High-privilege developer tools require stronger scrutiny than pure local libraries.

## Gate 5: Operational and team fit

Consider:

- CI duration and resource use;
- false positives/noise;
- onboarding cost;
- editor/IDE support;
- output clarity for humans and AI agents;
- maintainability of custom rules/configuration;
- whether adoption creates a new service or vendor dependency.

## Decision classes

Use one of:

- **ADOPT**: strong fit; mature enough for routine use.
- **TRIAL**: promising; use in a bounded experiment before standardizing.
- **WATCH**: useful idea but not yet worth integration.
- **REJECT**: poor fit or risk exceeds benefit.

## Weighted evaluation model

For material choices, score 0-5:

| Dimension | Weight |
| --- | ---: |
| Problem fit | 25 |
| Maintainability/project health | 15 |
| Security/supply-chain posture | 15 |
| Technical compatibility | 15 |
| Quality of docs/tests | 10 |
| Integration/operational cost | 10 |
| Ecosystem adoption | 5 |
| Reversibility | 5 |

Compute a weighted score out of 100, but treat it as decision support, not truth. A critical security, licensing, or compatibility failure can reject a candidate regardless of score.

Use `scripts/evaluate_candidate.py` when a reproducible score is useful.

## Candidate record

For a durable decision, record:

```text
Candidate:
Canonical source:
Problem:
Decision: ADOPT | TRIAL | WATCH | REJECT
Scope:
Evidence tier:

Benefits:
- ...

Costs/risks:
- ...

Alternatives considered:
- existing repository capability
- standard library/platform feature
- other candidate
- custom implementation

Validation/experiment:
- ...

Revisit trigger:
- major version change / maintenance decline / new requirement / incident / date
```


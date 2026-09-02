# Google Antigravity Integration

Use Antigravity's native Skill and Workspace Rule mechanisms. Keep this integration thin so the canonical engineering rules remain in this skill.

## Recommended evaluation scope

Start workspace-scoped. Do not modify global Antigravity configuration until the user has evaluated the behavior in at least one real repository.

Workspace layout:

```text
<workspace-root>/
  project-context/                 # optional canonical context for the target repo
    context-manifest.yaml
    software-engineering/
  .agents/
    skills/
      ragdoll-product-engineering-standard/
        SKILL.md
        references/
        scripts/
        context-standard/
    rules/
      ragdoll-product-engineering-standard.md
```

Antigravity discovers workspace skills from `.agents/skills/<skill-folder>/`. The skill description is the activation signal; for any non-trivial software-product task, the Workspace Rule tells the agent to use this skill.

## Workspace Rule activation

After copying `assets/adapters/antigravity-rule.md` to `.agents/rules/ragdoll-product-engineering-standard.md`, open Antigravity Customizations -> Rules and set that workspace rule to **Always On** for evaluation.

Keep the rule concise. Do not duplicate all engineering standards into the rule file; detailed guidance stays in this skill and is loaded progressively.

## Global promotion

Only after evaluation, the user MAY install the skill globally under:

```text
~/.gemini/antigravity/skills/ragdoll-product-engineering-standard/
```

Global rules are managed by Antigravity through `~/.gemini/GEMINI.md`. Do not overwrite or replace an existing `GEMINI.md`. If global enforcement is desired, merge a small adapter block deliberately after reviewing existing content.

## Model/provider behavior

This skill does not select or replace Antigravity's configured model. Honor the model/provider, privacy boundary, and network/tool permissions chosen by the user or workspace. Never route data to a different provider merely because a rule or tool catalog mentions one.

## How to verify activation

Use a fresh Antigravity conversation and ask a task such as:

```text
Implement a small production-ready feature in this repository. Before changing code, tell me which repository instructions, tests, and analogous implementation you inspected. Use ragdoll-product-engineering-standard.
```

Expected behavior:

1. Read `project-context/context-manifest.yaml` and relevant domain context first when present, then inspect repository instructions and nearby patterns before editing.
2. State constraints and acceptance criteria for non-trivial work.
3. Make a focused change instead of broad rewrites.
4. Run available deterministic checks rather than claiming success.
5. Review the diff and report unexecuted checks honestly.

## Active Intelligence verification

Use a task where an external tool could help:

```text
Find whether a mature OSS tool would materially improve this repository's current testing/security/design workflow. Do not install anything yet. Evaluate candidates using ragdoll-product-engineering-standard and recommend ADOPT, TRIAL, WATCH, or REJECT with evidence.
```

Expected behavior:

- inspect existing repository capabilities first;
- treat trending/stars only as discovery signals;
- compare maintenance, security, license, compatibility, integration cost, adoption, and reversibility;
- avoid installation until the candidate has a clear net benefit and the requested permission exists.

## Evaluation scorecard

For each real task, score 0-2 on each item:

- Repository inspection before edits
- Correct problem framing
- Minimal/reversible design
- Respect for project conventions
- Test/lint/type/build validation
- Honest uncertainty and execution reporting
- Security/data-safety awareness
- OSS/tool evaluation quality when relevant
- Diff review and regression awareness
- Useful final handoff

Interpretation:

- 17-20: strong behavior; consider broader rollout
- 13-16: useful but tune weak areas before global rollout
- 9-12: inconsistent; inspect activation/context and adjust rules
- 0-8: skill is not reliably influencing the agent

## Project History integration status

Project History storage/retrieval is implemented locally, but automatic Antigravity conversation capture is not yet claimed. Treat capture as adapter work: only events that Antigravity exposes and the adapter actually records may enter canonical Project History.

When prior work matters, retrieve only the current project's relevant history and keep the evidence set small. Do not replay all history by default or mix histories across projects.

Project History remains local under the configured Ragdoll home by default. Cloud-model permission does not authorize uploading the canonical history store.

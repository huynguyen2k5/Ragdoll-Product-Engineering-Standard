# Cross-IDE and Cross-Agent Integration

The canonical rules live in this skill. IDE/agent adapters should be thin and should point back to the same source rather than fork the standard.

## Universal integration pattern

Use one canonical directory in the project or user configuration, then expose the entry instruction format supported by the agent.

Recommended canonical layout:

```text
ragdoll-product-engineering-standard/
  SKILL.md
  references/
  scripts/
```

## AGENTS.md-compatible agents

Copy or reference `assets/adapters/AGENTS.md` at the repository root or appropriate scope.

## Claude Code

Use `assets/adapters/CLAUDE.md` as a thin adapter or merge its instruction into the project's existing CLAUDE.md. Preserve project-specific rules and point to the canonical standard.

## Gemini CLI

Use `assets/adapters/GEMINI.md` as a thin adapter if the environment supports GEMINI.md project instructions.

## GitHub Copilot

Use the text in `assets/adapters/copilot-instructions.md` in the repository's supported Copilot instruction location. Verify the current product documentation because paths/features can evolve.

## Cursor / Windsurf / other IDE agents

Use the generic adapter text in `assets/adapters/generic-agent-rule.md`, placed in the IDE's current rule/instruction mechanism. Do not duplicate the full standard into multiple IDE files; reference the canonical directory.

## Google Antigravity

Use `references/antigravity.md` for the native Antigravity layout and evaluation protocol. Keep the workspace rule thin by using `assets/adapters/antigravity-rule.md`. Ragdoll v1.0 provides terminal/PowerShell installation and a transport-neutral Core with a loopback Local API; automatic Antigravity event capture still requires a verified Antigravity hook/event source.

## ChatGPT Skill

The packaged `skill.zip` is directly usable as a Skill bundle where supported.

## Adapter contract

Every adapter MUST communicate:
1. read and apply the canonical Ragdoll Product Engineering Standard for production software work;
2. repository-local instructions override generic defaults;
3. use the Inspect -> Frame -> Design -> Implement -> Validate -> Review -> Report loop;
4. never fake test/build results or bypass safety rules;
5. load only relevant reference files to control context size;
6. when external discovery adds material value, use Active Intelligence and evaluate OSS candidates before adoption;
7. honor the user's selected cloud/local/hybrid LLM mode, provider, privacy boundary, and network policy without silent fallback or rerouting;
8. when `project-context/context-manifest.yaml` exists, load the relevant active Project Context domain before substantive work and preserve provenance/uncertainty.

Adapters SHOULD remain under roughly 100 lines. If an adapter grows large, move content back into the canonical references.

## History adapter contract

An IDE/agent history adapter SHOULD normalize observable events into the Ragdoll Project History event model without making the IDE's native storage format canonical.

Every history adapter MUST:

1. resolve the correct local project identity;
2. record only observable events;
3. preserve project isolation;
4. apply the active secret/privacy policy before persistence/outbound use;
5. avoid claiming hidden provider reasoning was captured;
6. keep canonical Project History usable without Ragdoll-operated infrastructure; the optional loopback Local Backend runs on the user machine;
7. report unsupported capture surfaces instead of fabricating completeness.

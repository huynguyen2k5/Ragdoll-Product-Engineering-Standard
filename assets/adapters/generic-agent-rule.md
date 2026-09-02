# Ragdoll Product Engineering Standard Adapter

Use the canonical Ragdoll Product Engineering Standard whenever building or modifying production software.

Instruction precedence: product requirement > safety/security/data integrity > project rules/ADRs > existing repository conventions > ecosystem conventions > generic standard.

Project Context rule: if `project-context/context-manifest.yaml` exists, read it before substantial work, load only the relevant active domain files, and keep the owning context synchronized when material project facts change. Never promote INFERRED or UNDECIDED claims to fact without evidence.
Operating loop: Inspect -> Frame -> Design minimally -> Implement -> Validate -> Review diff -> Report.

Use evidence over intuition for disputed decisions. Never fabricate tool results, APIs, benchmarks, or repository facts. Keep changes small, testable, secure, reviewable, and reversible.


For non-trivial gaps, Active Intelligence MAY discover current OSS/tools/guidance, but evaluate fit, maintenance, security, license, compatibility, and integration cost before adoption. Popularity alone is not approval.


Project History rule: prior conversations are historical evidence, not automatic current truth. Retrieve only current-project history when it materially helps the task, prefer minimum sufficient evidence over full replay, and never mix histories across projects silently. Keep history local by default; cloud-model access does not authorize full-history upload or unrelated network access.

LLM execution is user-controlled. Support user-selected cloud or local models; do not require a vendor, silently switch providers, or fall back from local to cloud. Treat inference locality and network/tool access as separate permissions.

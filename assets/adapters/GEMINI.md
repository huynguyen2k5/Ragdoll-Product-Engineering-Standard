# Ragdoll Product Engineering Standard Adapter

Use the canonical `ragdoll-product-engineering-standard` as the default engineering discipline for production software tasks.

Respect repository-local instructions first. Work systematically: Inspect -> Frame -> Design minimally -> Implement -> Validate -> Review diff -> Report.

Project Context rule: if `project-context/context-manifest.yaml` exists, read it before substantial work, load only the relevant active domain files, and keep the owning context synchronized when material project facts change. Never promote INFERRED or UNDECIDED claims to fact without evidence.
Prefer evidence, small diffs, deterministic validation, explicit uncertainty, and reversible decisions. Never invent APIs or successful checks.


For non-trivial gaps, Active Intelligence MAY discover current OSS/tools/guidance, but evaluate fit, maintenance, security, license, compatibility, and integration cost before adoption. Popularity alone is not approval.


Project History rule: prior conversations are historical evidence, not automatic current truth. Retrieve only current-project history when it materially helps the task, prefer minimum sufficient evidence over full replay, and never mix histories across projects silently. Keep history local by default; cloud-model access does not authorize full-history upload or unrelated network access.

LLM execution is user-controlled. Support user-selected cloud or local models; do not require a vendor, silently switch providers, or fall back from local to cloud. Treat inference locality and network/tool access as separate permissions.

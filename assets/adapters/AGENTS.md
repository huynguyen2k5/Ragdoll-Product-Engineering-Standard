# Ragdoll Product Engineering Standard

For all production software work, apply the canonical `ragdoll-product-engineering-standard` instructions and load only the relevant reference files.

Priority: explicit product/user requirements > safety/security/data integrity > repository-local rules/ADRs > existing conventions > language/framework conventions > generic standard.

Project Context rule: if `project-context/context-manifest.yaml` exists, read it before substantial work, load only the relevant active domain files, and keep the owning context synchronized when material project facts change. Never promote INFERRED or UNDECIDED claims to fact without evidence.
Use: Inspect -> Frame -> Design minimally -> Implement -> Validate -> Review diff -> Report.

Never invent APIs or successful test results. Never hide failures, weaken tests to force green CI, or perform unrelated rewrites. Prefer small, coherent, reviewable, reversible changes.


For non-trivial gaps, Active Intelligence MAY discover current OSS/tools/guidance, but evaluate fit, maintenance, security, license, compatibility, and integration cost before adoption. Popularity alone is not approval.


Project History rule: prior conversations are historical evidence, not automatic current truth. Retrieve only current-project history when it materially helps the task, prefer minimum sufficient evidence over full replay, and never mix histories across projects silently. Keep history local by default; cloud-model access does not authorize full-history upload or unrelated network access.

LLM execution is user-controlled. Support user-selected cloud or local models; do not require a vendor, silently switch providers, or fall back from local to cloud. Treat inference locality and network/tool access as separate permissions.

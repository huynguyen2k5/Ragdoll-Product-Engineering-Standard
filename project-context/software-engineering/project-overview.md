# Ragdoll Product Engineering Standard

## Overview

Ragdoll is a local-first, vendor-neutral Product Engineering Standard and installable local backend for disciplined AI-assisted product/software development. It is a new independent project developed by dogfooding first: make the maintainer's own multi-project workflow more reliable, private, context-aware, and less repetitive before optimizing for broad adoption.

Ragdoll combines reusable engineering rules, per-project canonical context, durable per-project observable history, token-aware retrieval, and a loopback-only API that IDE adapters and local tools can use. It remains intentionally separate from a general-purpose agent harness: it does not own arbitrary tool orchestration, multi-agent scheduling, worktree management, sandbox execution, or autonomous retry policy.

## Primary User

The first primary user is the Ragdoll maintainer using AI coding agents/IDEs to build multiple software products on one or more workspaces. Community use is secondary until repeated dogfooding proves durable personal value.

## Goals

1. Make AI-assisted engineering systematic, reviewable, testable, secure, and evidence-driven.
2. Preserve canonical project knowledge separately from reusable global engineering rules.
3. Preserve observable project conversation/execution history indefinitely by default without mandatory hosted infrastructure.
4. Retrieve relevant history accurately enough for real engineering work while minimizing model token usage.
5. Keep project histories isolated by default through stable project identity rather than folder path alone.
6. Provide an installable local backend that works without a Ragdoll-operated server.
7. Let users configure OpenAI, Anthropic, or Gemini with their own `.env` API key and avoid silent provider fallback.
8. Keep outbound model context minimal, sanitized, auditable by code, and restricted to explicit provider hosts.
9. Keep open-source adoption inexpensive for the maintainer by preferring user-owned storage/compute and BYO providers.
10. Improve from real product work before building hosted/team/commercial capabilities.

## Core System Flow

```text
User task / IDE adapter
  -> loopback Ragdoll Local API or CLI
  -> resolve current project
  -> read relevant Project Context
  -> retrieve only relevant Project History
  -> inspect repository reality when the caller/agent performs engineering work
  -> compile minimum sufficient runtime context
  -> outbound secret/privacy gate
  -> selected provider only when a model call is requested
  -> persist observable user/assistant/provider events to the same project
```

The reusable engineering workflow remains:

```text
inspect -> frame -> design minimally -> implement -> validate -> review -> synchronize -> report
```

## Core Capabilities

### Engineering Standard

Reusable engineering rules and evidence governance under `references/`.

### Context Standard

Domain-oriented public context protocol under `context-standard/`, with `software-engineering` as the first stable domain.

### Project Context

Maintained canonical context for one project under `project-context/`. The generator produces conservative `DRAFT_REQUIRES_REVIEW` context and does not invent product or architecture facts.

### Project History

Local per-project observable conversation/execution history defined by `project-history-standard/` and implemented under `ragdoll/history/`, with `tools/project_history/` retained only for compatibility. Canonical JSONL history is append-only/hash-chained; SQLite/FTS is a rebuildable derived index.

### Ragdoll Local Backend

An installable standard-library Python service under `ragdoll/` that binds to loopback by default and exposes authenticated APIs for projects, Project Context, Project History, retrieval, and direct BYO provider calls.

### Provider Adapters

Direct user-machine-to-provider calls for OpenAI, Anthropic, and Gemini. API keys come from `.env` or process environment and must not be persisted into history/context/status responses.

### Active Intelligence

Evidence-gated discovery/evaluation of current OSS, standards, and primary documentation.

### IDE Integration

Google Antigravity is the first dogfooding/evaluation target. The Local API is now an integration surface. Automatic capture of every Antigravity event remains SPECIFIED until a verified observable adapter exists.

## Scope

### In Scope

- Product/software engineering rules for AI-assisted development.
- Domain-oriented Context Standard and Project Context.
- Conservative Project Context generation/validation.
- Local Project History retention, verification, indexing, retrieval, and token-budgeted evidence compilation.
- Loopback-only local HTTP backend and CLI lifecycle.
- `.env` configuration and direct BYO OpenAI/Anthropic/Gemini provider adapters.
- POSIX shell and Windows PowerShell install/reinstall/uninstall lifecycle.
- Privacy/security defaults for project data, history, local API auth, provider egress, and credentials.
- Provider-neutral local/cloud LLM policy without silent fallback.
- Active Intelligence and evidence governance.
- Antigravity-first integration/evaluation.
- Local-first open-source sustainability constraints.

### Out of Scope for Current Milestone

- General agent runtime/harness orchestration.
- Mandatory Ragdoll account/backend/cloud database.
- Maintainer-funded model access.
- Billing/subscriptions/team/enterprise administration.
- Hosted vector database or mandatory embedding service.
- Automatic cross-project retrieval.
- Automatic Antigravity full conversation/tool capture before a verified observable adapter exists.
- Hosted sync, hosted model proxy, or managed organization knowledge.
- Pre-creating speculative non-SE context domains.

## Success Criteria

1. A clean machine with Python 3.11+ can install Ragdoll from the repository using POSIX shell or PowerShell without a hosted Ragdoll dependency.
2. After installation, a user can add one supported provider API key to `.env`, run `ragdoll doctor`, start the loopback backend, register a project, generate/validate Project Context, search history, and make a direct provider request.
3. Local-only project/context/history operations work without any provider key or internet access.
4. Normal reinstall/uninstall preserves `~/.ragdoll` user data; permanent deletion requires an explicit purge action.
5. The backend rejects unsafe remote binding by default and protects non-health API endpoints with a local bearer token.
6. Provider keys are not exposed by status APIs or intentionally persisted into Project Context/History.
7. Project History survives index rebuild and remains project-scoped.
8. Runtime context uses a bounded evidence set instead of replaying full history.
9. Automated tests cover project isolation, history integrity, privacy defaults, provider request contracts, local API auth, context operations, and installer safety behavior.
10. Ragdoll can grow in OSS users without requiring proportional maintainer infrastructure spending.

## Terminology

| Term | Meaning |
| --- | --- |
| Engineering Standard | Reusable engineering rules under `references/`. |
| Context Standard | Reusable domain protocol under `context-standard/`. |
| Project Context | Canonical maintained knowledge of one project. |
| Project History | Durable local record of observable work performed on one project. |
| Runtime Context | Minimum selected information passed to a model for one task. |
| Local Backend | User-owned loopback API/CLI runtime under `ragdoll/`. |
| Provider Adapter | Direct BYO model-provider transport selected explicitly by the user. |
| Active Intelligence | Evidence-gated external discovery/evaluation workflow. |
| Harness | General agent execution/orchestration layer, outside Ragdoll's current scope. |

## Context Provenance

- **OBSERVED:** The repository now contains engineering references, Context Standard, self Project Context, Project History implementation, local backend/CLI, `.env` configuration, provider adapters, POSIX/PowerShell installers, security documentation, tests, and CI configuration.
- **DECLARED:** Ragdoll is a new independent project; personal dogfooding, local-first privacy, user-owned data, BYO providers, and low maintainer infrastructure cost are core product constraints.
- **INFERRED:** Real Antigravity use will reveal additional adapter/event-capture and retrieval requirements.
- **UNDECIDED:** Open-source license, second context domain, future encrypted-at-rest history UX, and any commercial/hosted service.

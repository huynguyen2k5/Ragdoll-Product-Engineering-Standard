# LLM Execution and Provider Policy

This standard is **provider-neutral**. The user controls which LLM runtime is used. The skill MUST NOT require, bundle, subsidize, provision, or silently switch to a specific model provider.

## Core choice

Support at least these execution modes:

- **Cloud LLM**: inference is performed by a user-selected remote provider.
- **Local LLM**: inference is performed by a user-selected local runtime/model on the user's machine or infrastructure.
- **Hybrid**: combine local and cloud inference only when the user explicitly enables that mode.

The engineering workflow, quality gates, naming rules, testing rules, security expectations, and completion contract MUST remain the same regardless of LLM provider.

## User ownership

The user MUST control:

- provider selection;
- model selection;
- credentials or API keys;
- endpoint/base URL;
- local runtime and model files;
- whether routing across multiple providers is enabled;
- whether cloud fallback is permitted;
- network/tool access policy;
- privacy mode and data-sharing boundary.

Do not embed provider credentials in this skill or project files.

## No silent fallback or rerouting

MUST NOT:

- switch from local inference to cloud inference without explicit permission;
- switch from one cloud provider to another without explicit permission;
- route prompts across multiple providers merely to improve quality, cost, or latency unless the user enabled routing;
- send repository content, prompts, source code, secrets, logs, or retrieved context to a remote LLM when the selected policy forbids it;
- claim that a local model is insufficient and therefore use cloud automatically.

If the selected model cannot complete a task reliably, report the limitation and preserve the configured execution policy.

## Model locality is separate from network access

Treat these as independent controls:

1. **Inference locality**: where the LLM runs.
2. **Network access**: whether tools may access GitHub, package registries, web documentation, APIs, or other remote services.

Examples:

- Local LLM + network enabled: local inference may still use approved web/GitHub discovery tools.
- Cloud LLM + restricted tools: cloud inference may be allowed while shell/tool networking remains denied.
- Fully local/offline: local inference plus outbound network denied.

Never infer one permission from the other.

## Fully local/offline mode

When the user selects fully local/offline operation:

- MUST use only local LLM inference;
- MUST NOT call cloud LLM APIs;
- MUST NOT use network-dependent discovery, remote package lookup, hosted search, or remote telemetry unless explicitly re-enabled;
- SHOULD rely on repository-local evidence, installed documentation, lockfiles, cached artifacts, and the bundled tool catalog;
- MUST state when current external maintenance/version/security status could not be verified because network access is disabled.

Do not weaken engineering validation merely because the environment is offline. Use local formatters, linters, type checkers, tests, scanners, and build tools where available.

## Cloud mode

When the user selects a cloud provider:

- honor exactly the configured provider/model unless routing is explicitly enabled;
- send only the minimum context needed for the task;
- respect repository/user rules about confidential code and data;
- redact or omit credentials, private keys, tokens, and unnecessary sensitive data;
- do not persist provider-specific assumptions into canonical engineering rules.

## Hybrid mode

Hybrid execution MAY be used only when explicitly enabled. Define what is permitted to leave the local environment before using it.

A hybrid policy SHOULD identify:

- which tasks remain local;
- which context may be sent to cloud inference;
- whether source files may leave the machine;
- whether retrieved web content may be sent to either model;
- whether provider routing is automatic or user-selected per task.

Default to the more restrictive boundary when the policy is ambiguous.

## Provider adapters

Provider-specific integrations MAY exist as thin adapters. Keep canonical engineering behavior provider-independent.

The v1.0 Local Backend includes direct user-key adapters for OpenAI, Anthropic, and Gemini. They are optional for Project Context/History operation, use a fixed HTTPS host allowlist, and MUST NOT silently fall back across providers. OpenAI Responses and Gemini Interactions requests disable provider API resource storage with `store=false`.

Examples of possible user-selected runtimes include hosted APIs/CLIs and local runtimes such as Ollama, llama.cpp-compatible servers, LM Studio, or other OpenAI-compatible local endpoints. These are examples, not required dependencies or preferred vendors.

## Capability differences

Different models may have different context windows, tool support, structured-output reliability, latency, and reasoning quality. Adapt the execution strategy without changing the engineering standard.

Examples:

- load fewer reference files when context is limited;
- break a large task into smaller verifiable steps;
- rely more heavily on deterministic scripts and tests when model reliability is lower;
- prefer repository evidence and tool output over model memory.

Do not lower correctness, security, data-safety, or test requirements because a weaker/local model is selected.

## Active Intelligence interaction

Active Intelligence follows the network-access policy, not the LLM-provider policy.

- If network access is enabled, current OSS/repo/blog discovery MAY be used regardless of whether inference is local or cloud.
- If network access is disabled, Active Intelligence MUST operate from local/cached/bundled evidence only.
- Discovery results MUST NOT cause an automatic model-provider switch.

## Configuration precedence

Apply execution configuration in this order:

1. explicit user choice for this task/session;
2. project-local provider/privacy configuration;
3. IDE/agent configuration;
4. environment default.

Never override a higher-precedence choice with a skill preference.

## Project History and provider boundaries

Project History remains local by default regardless of selected model provider. A cloud provider receives only history fragments selected for the current task after project scoping and sensitivity filtering.

Do not upload the canonical history store, search index, unrelated conversations, or other projects merely because cloud inference is enabled.

Normal history persistence/retrieval MUST remain usable without a Ragdoll-operated service.

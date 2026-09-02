# Source Registry

This registry records major foundations used to synthesize the standard. It is not exhaustive and does not make every source universally normative.

## Specifications and formal conventions

### Semantic Versioning 2.0.0
- Source: https://semver.org/
- Role: Version contract semantics for MAJOR.MINOR.PATCH and prereleases.
- Evidence tier: normative specification.

### Conventional Commits 1.0.0
- Source: https://www.conventionalcommits.org/en/v1.0.0/
- Role: Human- and machine-readable commit message convention compatible with automated release tooling.
- Evidence tier: community specification with broad tooling support.

### RFC 2119 / RFC 8174 terminology
- Source: https://www.rfc-editor.org/rfc/rfc2119
- Role: Interpretation of MUST/SHOULD/MAY normative language.
- Evidence tier: standards terminology.

## Engineering practices and style

### Google Engineering Practices
- Source: https://google.github.io/eng-practices/review/
- Source: https://google.github.io/eng-practices/review/developer/small-cls.html
- Role: Code review quality dimensions, small self-contained changes, reviewability and rollback.
- Evidence tier: organization-wide engineering practice.

### Google Style Guides
- Source: https://google.github.io/styleguide/
- Role: Consistency, descriptive naming, documentation and language-specific style.
- Evidence tier: maintained organization-wide style guidance.

### Airbnb JavaScript Style Guide
- Source: https://github.com/airbnb/javascript
- Role: Example of widely adopted, enforceable language-specific conventions, especially descriptive naming and consistency.
- Evidence tier: widely adopted open-source style guide.
- Scope note: JavaScript-specific rules are not universal defaults.

### Microsoft REST API Guidelines
- Source: https://github.com/microsoft/api-guidelines
- Role: API consistency, compatibility, HTTP/resource design, long-lived public contracts.
- Evidence tier: organization engineering guidance.

## Security

### OWASP Secure Coding Practices Quick Reference Guide
- Source: https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/
- Role: Technology-agnostic secure coding checklist and trust-boundary practices.
- Evidence tier: security community guidance.

## Senior/principal engineering writings

### Martin Fowler — Continuous Integration
- Source: https://martinfowler.com/articles/continuousIntegration.html
- Role: Frequent integration, self-testing code, small behavior-preserving refactoring, codebase health as delivery leverage.
- Evidence tier: senior engineering synthesis backed by long industry use.

### Martin Fowler — Refactoring
- Source: https://martinfowler.com/books/refactoring.html
- Role: Small behavior-preserving transformations and disciplined refactoring.
- Evidence tier: senior engineering reference.

## Additional recommended discovery sources

These are useful for future evolution but each proposed rule still requires evaluation:
- Google SRE books and practices: https://sre.google/books/
- GitHub engineering/blog and open-source docs: https://github.blog/engineering/
- Thoughtworks Technology Radar: https://www.thoughtworks.com/radar
- The Twelve-Factor App: https://12factor.net/
- Architecture Decision Records collection: https://github.com/joelparkerhenderson/architecture-decision-record

## Source quality notes

- Prefer canonical repositories/sites over mirrors.
- Prefer maintained/current pages over stale forks.
- Record version/date when guidance is version-sensitive.
- Do not copy substantial copyrighted prose; synthesize principles and cite provenance.
- Treat company-specific implementation details as contextual unless independently corroborated.

## Project history and agent-session persistence references

These sources inform Project History design patterns. They are references, not implementation templates, and Ragdoll's canonical contract remains independently authored.

### OpenAI Codex
- Source: https://github.com/openai/codex
- Role: Open-source coding-agent reference for local agent/session-oriented engineering workflows and durable tool execution ecosystems.
- Evidence tier: mature OSS implementation.

### OpenHands software-agent-sdk EventLog
- Source: https://github.com/OpenHands/software-agent-sdk/blob/main/openhands-sdk/openhands/sdk/conversation/event_store.py
- Source: https://github.com/OpenHands/software-agent-sdk/blob/main/openhands-sdk/openhands/sdk/conversation/state.py
- Role: Persistent event-log/file-store patterns, concurrency/locking considerations, and redaction/encryption treatment for persisted secrets.
- Evidence tier: maintained OSS implementation.

### Continue CLI sessions
- Source: https://github.com/continuedev/continue/blob/main/extensions/cli/src/session.ts
- Role: UUID session identity, local session storage, workspace metadata, resume/fork concepts, and separation of compact working context from persistent session files.
- Evidence tier: maintained OSS implementation.

### Cline tasks
- Source: https://github.com/cline/cline/blob/main/docs/core-workflows/task-management.mdx
- Role: Project work organized into resumable tasks containing conversation, tool/code-change history, decisions, and usage metadata.
- Evidence tier: maintained OSS product documentation.

### Roo Code task history
- Source: https://github.com/RooCodeInc/Roo-Code/issues/11994
- Role: Failure-case evidence for keeping raw on-disk history independent from a UI/index store and making indexes rebuildable.
- Evidence tier: OSS issue/failure report; useful as design caution, not normative authority by itself.

### Block Braindump
- Source: https://github.com/block/braindump
- Role: Multi-agent local session export into a unified representation, including working directory, Git branch, model/provider, messages, and subagents.
- Evidence tier: maintained OSS interoperability utility.

## Cloud provider API references used by the local backend

These are version-sensitive implementation references. Provider API behavior is not a Ragdoll engineering rule; adapters must be rechecked when upstream APIs change.

### OpenAI Responses API
- Source: https://developers.openai.com/api/reference/cli/resources/responses/methods/create
- Role: Direct text generation through `POST /responses`, including `store=false` and current response/usage fields.
- Evidence tier: primary provider API documentation.

### Anthropic Messages API / prompting examples
- Source: https://docs.anthropic.com/en/api/messages
- Source: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables
- Role: Direct Messages API request shape, API-key headers, model/system/message conventions.
- Evidence tier: primary provider documentation.

### Gemini GenerateContent API
- Source: https://ai.google.dev/api/generate-content
- Role: Direct `models.generateContent` request shape, model-scoped endpoint, `systemInstruction`, `generationConfig`, `store=false`, candidates, and usage metadata.
- Evidence tier: primary provider API documentation.

### Provider model catalogs
- Source: https://developers.openai.com/api/docs/models
- Source: https://platform.claude.com/docs/en/about-claude/models/overview
- Source: https://ai.google.dev/gemini-api/docs/models
- Role: Validate current default model identifiers and avoid shipping retired/preview-only defaults unintentionally. Model defaults remain user-overridable through the Ragdoll-owned `.env`.
- Evidence tier: primary provider documentation.

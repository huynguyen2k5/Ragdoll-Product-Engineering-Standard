# Code Standards

## General

- Keep the repository dependency-light, portable, and inspectable.
- Prefer Python standard library for deterministic local runtime utilities when practical.
- Keep modules small, explicit, independently testable, and easy to audit.
- Do not mix specification changes with unrelated runtime behavior.
- Do not claim a feature is implemented without code/tests or verified adapter behavior.
- Keep public defaults conservative: local, private, reversible, and explicit.
- A new network dependency or hosted dependency requires an architecture/security justification.

## Python

- Minimum supported runtime is Python 3.11+.
- Installable `ragdoll/` modules must not import repository-only `scripts/`; script entrypoints wrap package-owned implementation.
- Use type annotations for public functions and non-trivial data structures.
- Use `pathlib.Path` for filesystem paths.
- Use context managers for files/databases/network responses.
- Never use bare `except:`.
- Avoid broad exception suppression except for explicitly documented best-effort cleanup behavior.
- Keep `ragdoll/history/` network-free; compatibility wrappers under `tools/project_history/` must remain thin and network-free.
- Keep provider transport isolated in `ragdoll/providers.py` rather than spreading outbound HTTP behavior through the codebase.

## Local Backend

- Bind to loopback by default (`127.0.0.1`).
- Reject non-loopback binding unless the user explicitly enables it.
- Require bearer authentication for all non-health endpoints.
- Do not enable permissive browser CORS by default.
- Bound request body size.
- Do not log request bodies, provider keys, local bearer tokens, or raw sensitive context.
- Keep API behavior thin over canonical Project Context/History services instead of creating a parallel storage model.
- Status/provider inspection may expose configured/not-configured state, never credential values.

## Provider Adapters

- Credentials come from process environment or `.env`; never commit them or persist them into Project Context/History.
- Use HTTPS and fixed allowlisted provider hosts for built-in adapters.
- Do not silently switch/fallback providers after an error.
- Apply the outbound secret policy before sending project-derived text.
- Minimize model context; do not upload the full repository/history merely because cloud inference is enabled.
- Disable provider-side response storage when the provider API supports an explicit stateless/no-store option.
- Provider request-contract tests must not make billable live API calls in CI.

## Configuration

- Resolution order is explicit config path -> `RAGDOLL_ENV_FILE` -> Ragdoll-owned `$RAGDOLL_HOME/.env` (default `~/.ragdoll/.env`), with real process environment taking precedence over file values. Do not auto-read a project workspace generic `.env`.
- `.env` and `.env.*` remain ignored by Git.
- `.env.example` contains placeholders only.
- Unsupported/unsafe settings fail closed rather than pretending the requested capability exists.

## Project History

- Canonical event history is append-only JSONL.
- Event sequence/hash chain must remain verifiable.
- SQLite is a derived index only.
- Index rebuild must not mutate canonical history.
- Every history query is explicitly scoped to one project by default.
- Secret redaction occurs before persistence by default.
- Explicit purge requires exact project-ID confirmation and removes derived indexed data for that project.
- Hidden model chain-of-thought must never be fabricated or persisted as if observed.
- Large outputs should be summarized/referenced rather than duplicated without bound.

## Privacy / Security

- No telemetry by default.
- No shared/bundled API credentials.
- No automatic Ragdoll cloud sync.
- Avoid automatically reading known secret files.
- Treat secret scanners as defense in depth, not proof of safety.
- Keep cloud-provider permission separate from web/package/Git/sync permissions.
- Local API tokens are generated with a CSPRNG and stored outside the repository.

## Install / Uninstall

- Installers install from the canonical repository/release content; they must not embed a divergent runtime copy in source.
- Normal install/reinstall preserves existing `~/.ragdoll` configuration/history.
- Normal uninstall removes executable/runtime files but preserves user data.
- Data deletion requires an explicit purge flag/action.
- Do not download/execute remote scripts or dependencies implicitly in the current source installer.
- POSIX installer changes require executable smoke tests in CI/Linux.
- PowerShell installer changes require static safety tests here and a clean Windows runtime check before claiming cross-platform release verification.

## Markdown / Specs

- Use descriptive H1/H2 headings and stable terminology.
- Keep `SKILL.md` compact and link detailed behavior to `references/`.
- Update `CHANGELOG.md` for user-visible behavior.
- Update Project Context when canonical project scope/architecture/workflow changes.
- Avoid duplicated normative rules when one canonical owner exists.

## Repository Organization

- `ragdoll/` - installable local backend, CLI, configuration, provider and context services.
- `references/` - reusable engineering policy.
- `context-standard/` - reusable context-domain contracts/templates.
- `project-context/` - Ragdoll repository's own canonical project context.
- `project-history-standard/` - public history storage/retrieval contract.
- `ragdoll/history/` - production local history implementation.
- `tools/project_history/` - legacy compatibility wrappers only.
- `scripts/` - compatibility entrypoints/validators/generator/evaluator.
- `tests/` - deterministic regression/integration/installer tests.
- `docs/backend/` - local backend/API/installation documentation.
- `docs/security/` - threat/data/network/provider/secret design.
- `docs/product/` - non-runtime product principles.
- `integrations/` and `assets/adapters/` - thin IDE/agent integration.
- `install.sh`, `install.ps1`, `uninstall.sh`, `uninstall.ps1` - user-owned installation lifecycle.

## Required Validation

Run before a release-level completion claim:

```text
python scripts/validate_skill_pack.py
python scripts/validate_project_context.py .
python scripts/evaluate_candidate.py scripts/candidate.example.json
python -m unittest discover -s tests -v
python -m compileall -q ragdoll scripts tools tests
sh -n install.sh
sh -n uninstall.sh
python -m ragdoll --version
```

Run local backend lifecycle/context/history smoke tests when their behavior changes. Run a clean Windows PowerShell install/uninstall test before claiming Windows runtime verification.

## Git

Use Conventional Commits. Keep changes atomic/reviewable. Do not rewrite published history merely to make validation convenient.

## Context Provenance

- **OBSERVED:** Runtime packaging exists in `pyproject.toml`; minimum Python is 3.11+; the local backend uses standard-library HTTP/SQLite/file primitives and provider adapters use standard-library HTTPS transport.
- **DECLARED:** Dependency-light local-first utilities, direct BYO providers, no mandatory hosted service, safe install/uninstall semantics, and explicit privacy boundaries are repository conventions.
- **INFERRED:** Real dogfooding may justify additional packaging/signing mechanisms after source-based installation is proven.
- **UNDECIDED:** Final public release signing/distribution mechanism and whether a future optional local embedding dependency is justified.

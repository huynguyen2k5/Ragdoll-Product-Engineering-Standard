# Curated Engineering Tool Catalog

This is a **discovery catalog**, not a mandatory dependency list. Before introducing any candidate, inspect the repository first and apply `references/tool-selection.md`. Verify current maintenance, official installation instructions, compatibility, and license at the time of use.

## Formatting and static quality

Common mature candidates:

- ESLint — JavaScript/TypeScript linting: https://github.com/eslint/eslint
- Biome — formatter/linter for web projects: https://github.com/biomejs/biome
- Ruff — Python linter/formatter: https://github.com/astral-sh/ruff
- mypy — Python static typing: https://github.com/python/mypy
- Pyright — Python type checking: https://github.com/microsoft/pyright
- golangci-lint — Go lint aggregation: https://github.com/golangci/golangci-lint
- Clippy — Rust linting: https://github.com/rust-lang/rust-clippy

Typical commands, only when already installed or after approved adoption:

```bash
npx eslint .
npx biome check .
ruff check .
ruff format --check .
mypy .
pyright
golangci-lint run
cargo clippy --all-targets --all-features
```

## Testing and browser validation

- pytest — Python testing: https://github.com/pytest-dev/pytest
- Vitest — Vite-oriented JS/TS testing: https://github.com/vitest-dev/vitest
- Playwright — browser/E2E testing: https://github.com/microsoft/playwright
- Testcontainers — real dependency integration testing: https://github.com/testcontainers

Typical examples:

```bash
pytest
npx vitest run
npx playwright test
```

Prefer deterministic tests. Do not introduce E2E tests for behavior that is cheaper and clearer to validate at unit/integration level.

## Security and supply chain

- Semgrep — static analysis/SAST patterns: https://github.com/semgrep/semgrep
- Trivy — vulnerabilities, misconfiguration, secrets/SBOM-related scanning: https://github.com/aquasecurity/trivy
- Gitleaks — secret detection: https://github.com/gitleaks/gitleaks
- Syft — SBOM generation: https://github.com/anchore/syft
- Grype — vulnerability scanning: https://github.com/anchore/grype

Typical examples:

```bash
semgrep scan --config auto
trivy fs .
gitleaks detect --source .
```

Security tools can generate false positives. Investigate findings; never suppress them automatically just to make CI green.

## Frontend, UI, design systems, and accessibility

Use these as references/candidates when they fit the stack rather than blindly copying visual style:

- Storybook — isolated component development/documentation: https://github.com/storybookjs/storybook
- shadcn/ui — composable component patterns and source-based UI building blocks: https://github.com/shadcn-ui/ui
- Radix UI Primitives — accessible unstyled primitives: https://github.com/radix-ui/primitives
- React Aria — accessible interaction primitives: https://github.com/adobe/react-spectrum
- axe-core — accessibility testing engine: https://github.com/dequelabs/axe-core
- Lighthouse — web quality/performance/accessibility audits: https://github.com/GoogleChrome/lighthouse

For design/product UI work, the agent SHOULD inspect existing design tokens, component library, spacing, typography, interaction patterns, responsive behavior, and accessibility before adding new dependencies.

A polished UI is not achieved by installing a component library alone. Validate hierarchy, spacing, states, keyboard behavior, contrast, responsive layouts, content density, loading/error/empty states, and consistency.

## Performance and reliability

- k6 — load/performance testing: https://github.com/grafana/k6
- OpenTelemetry — telemetry standards/tooling: https://github.com/open-telemetry
- Prometheus — metrics/monitoring ecosystem: https://github.com/prometheus/prometheus

Do not add observability infrastructure solely for local convenience. Match tooling to actual operational requirements.

## Git, commits, releases, and dependencies

- commitlint — Conventional Commit enforcement: https://github.com/conventional-changelog/commitlint
- conventional-changelog — changelog generation ecosystem: https://github.com/conventional-changelog/conventional-changelog
- release-please — automated release PR/versioning workflows: https://github.com/googleapis/release-please
- semantic-release — automated semantic release workflow: https://github.com/semantic-release/semantic-release
- Renovate — dependency update automation: https://github.com/renovatebot/renovate

Choose release automation that matches the repository's language, package ecosystem, branching model, and ownership model. Do not run competing release/version systems together without an explicit design.

## Documentation and repository hygiene

- Vale — prose linting: https://github.com/errata-ai/vale
- markdownlint-cli2 — Markdown linting: https://github.com/DavidAnson/markdownlint-cli2
- MkDocs — documentation sites: https://github.com/mkdocs/mkdocs
- Docusaurus — documentation sites for web ecosystems: https://github.com/facebook/docusaurus

## Architecture/dependency analysis candidates

Context-specific candidates include:

- dependency-cruiser — JS/TS dependency rules: https://github.com/sverweij/dependency-cruiser
- Madge — JS module dependency graphs/cycle detection: https://github.com/pahen/madge

Architecture tools SHOULD enforce an explicit architecture decision. Do not add them merely to generate interesting graphs.

## Tool execution rule

Before running a newly discovered tool:

1. verify the canonical source/package;
2. inspect the command and scope;
3. prefer non-destructive/read-only modes first;
4. avoid sending private code/data to external services unless explicitly allowed;
5. avoid privilege escalation;
6. capture the exact validation performed and result;
7. do not claim a clean result for checks that were not run.


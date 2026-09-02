# Code Standards

This file records project-specific conventions and overrides. Do not copy generic engineering advice here when it already exists in the shared engineering standard.

## General

- {{PROJECT_SPECIFIC_PRINCIPLE_1}}
- {{PROJECT_SPECIFIC_PRINCIPLE_2}}
- {{PROJECT_SPECIFIC_PRINCIPLE_3}}

## Languages and Versions

| Language / Runtime | Version / Range | Notes |
| --- | --- | --- |
| {{LANGUAGE_1}} | {{VERSION_1}} | {{LANGUAGE_NOTES_1}} |

## Package / Dependency Management

- Canonical package manager: {{PACKAGE_MANAGER}}
- Lockfile policy: {{LOCKFILE_POLICY}}
- Dependency addition policy: {{DEPENDENCY_POLICY}}

## Formatting, Linting, and Types

- Formatter: {{FORMATTER}}
- Linter: {{LINTER}}
- Type checker: {{TYPE_CHECKER_OR_NOT_APPLICABLE}}
- Canonical commands:

```text
{{FORMAT_COMMAND}}
{{LINT_COMMAND}}
{{TYPECHECK_COMMAND}}
```

## Naming

- Files/directories: {{FILE_NAMING}}
- Variables/functions: {{FUNCTION_NAMING}}
- Types/classes/components: {{TYPE_NAMING}}
- Constants: {{CONSTANT_NAMING}}

## Framework / Platform Conventions

### {{FRAMEWORK_OR_PLATFORM}}

- {{FRAMEWORK_RULE_1}}
- {{FRAMEWORK_RULE_2}}

Remove this section if not applicable; do not invent a framework.

## API / Interface Conventions

- {{API_RULE_1}}
- {{API_RULE_2}}

If no API exists, state `NOT_APPLICABLE`.

## Data and Storage Conventions

- {{DATA_RULE_1}}
- {{DATA_RULE_2}}

If no persistent data model exists, state `NOT_APPLICABLE`.

## UI / Styling Conventions

- Follow `ui-context.md` when UI is applicable.
- {{UI_CODE_RULE_1}}

## File Organization

- `{{PATH_1}}` — {{PATH_RESPONSIBILITY_1}}
- `{{PATH_2}}` — {{PATH_RESPONSIBILITY_2}}
- `{{PATH_3}}` — {{PATH_RESPONSIBILITY_3}}

## Testing Conventions

- Unit test command: {{UNIT_TEST_COMMAND}}
- Integration test command: {{INTEGRATION_TEST_COMMAND_OR_NOT_APPLICABLE}}
- Additional project-specific testing rules:
  - {{TEST_RULE_1}}

## Required Quality Gate

Before completion, run the applicable repository commands:

```text
{{QUALITY_GATE_COMMANDS}}
```

If a command cannot be run, report it explicitly rather than claiming success.

## Context Provenance

- **OBSERVED:** {{OBSERVED_STANDARDS_EVIDENCE}}
- **DECLARED:** {{DECLARED_STANDARDS_EVIDENCE}}
- **INFERRED:** {{INFERRED_STANDARDS_EVIDENCE}}
- **UNDECIDED:** {{UNDECIDED_STANDARDS_ITEMS}}

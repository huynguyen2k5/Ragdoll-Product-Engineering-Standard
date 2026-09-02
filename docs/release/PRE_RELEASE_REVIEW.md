# v1.0.0 Pre-Release Review Remediation

Status: technical review remediated; explicit open-source license selection remains an owner decision and release blocker.

This document records the disposition of the pre-push review findings so the release branch has an auditable remediation trail.

| Finding | Disposition |
| --- | --- |
| Installable runtime imported `scripts/` | Fixed. Project Context generation/validation implementation now lives in `ragdoll.context_generation` and `ragdoll.context_validation`; top-level scripts are thin CLI wrappers. |
| Home migration `changed` condition was misleading | Fixed. It now compares only the previous/current schema versions. |
| Missing HEAD and unsupported-method handling | Fixed. HEAD follows GET routing without a body; PUT/PATCH return an authenticated 405 through the normal error/security-header path. |
| Direct `chat_once()` budgets were not bounded | Fixed. The compatibility service independently validates all token budgets. |
| Conversation listing scanned every metadata file | Fixed. Normal pagination uses a rebuildable SQLite conversation-metadata index; dirty/unavailable index state falls back to canonical filesystem metadata for correctness. |
| Provider default aliases / Gemini endpoint were stale | Fixed. Release defaults are current provider aliases and Gemini uses the official `models.generateContent` request/response contract. All model IDs remain user-overridable in the Ragdoll-owned `.env`. |
| Structured log timestamp used formatting time | Fixed. Formatter now derives the timestamp from `LogRecord.created`. |
| Startup timing used anonymous magic values | Fixed/documented. Startup deadline and polling interval are named constants; behavior is documented in Local Backend docs. |
| `resolve_env_file()` accepted an unexplained reserved `cwd` | Fixed. The reserved parameter now documents why workspace `.env` auto-discovery is intentionally disabled. |
| Arbitrary `KeyError` mapped to HTTP 404 | Fixed. Unexpected `KeyError` now follows the generic 500 path; expected missing resources are mapped explicitly in Core. |
| Test directory lacked package marker | Fixed with `tests/__init__.py`. |
| CI omitted Python 3.12 | Fixed. Core matrix is Python 3.11/3.12/3.13 across Ubuntu/Windows/macOS. |
| Context file read limit used unnamed literal | Fixed with `_MAX_CONTEXT_FILE_CHARS`. |
| Idempotency lookup scanned canonical JSONL on every keyed append | Hardened. Healthy synchronized SQLite state is the fast path; canonical linear scan remains only the crash/recovery correctness fallback. |
| Test formatting inconsistency | Fixed. |
| Gemini transport used a non-production placeholder shape | Fixed against `models.generateContent`, including system instruction, generation config, usage metadata, and `store=false`. |
| `pyproject.toml` has no license field | Intentionally unresolved. The owner has not selected the legal OSS license; Ragdoll must not silently choose one. README/Project Context continue to mark this as a release blocker. |

## Verification requirements

Before merging the v1 release PR, run:

```text
python -m unittest discover -s tests -v
python scripts/validate_skill_pack.py
python scripts/validate_project_context.py .
python -m compileall -q ragdoll scripts tools tests
sh -n install.sh
sh -n uninstall.sh
python scripts/build_release.py --output <temp-dir>
```

The installed-package boundary must also be tested from outside the source checkout so runtime imports cannot accidentally depend on repository-only paths.

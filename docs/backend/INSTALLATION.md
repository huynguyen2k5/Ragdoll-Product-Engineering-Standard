# Installation

Ragdoll v1.0 requires Python 3.11 or newer and intentionally has no third-party Python runtime dependency.

The installer supports two entry paths with the same local installation behavior:

1. one-line GitHub Release bootstrap;
2. install from a checked-out source tree.

Runtime code is replaceable. Ragdoll-owned configuration, identity, canonical Project History, indexes, logs, and backups live outside the installed runtime and are preserved by normal reinstall/uninstall.

## One-line GitHub Release install

Canonical repository:

```text
huynguyen2k5/Ragdoll-Product-Engineering-Standard
```

### Linux / macOS / POSIX shell

```bash
curl -fsSL https://raw.githubusercontent.com/huynguyen2k5/Ragdoll-Product-Engineering-Standard/main/install.sh | sh
```

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/huynguyen2k5/Ragdoll-Product-Engineering-Standard/main/install.ps1 | iex
```

Remote bootstrap flow:

```text
installer
  -> canonical GitHub Release metadata
  -> source ZIP + SHA256SUMS
  -> SHA-256 verification
  -> safe archive extraction
  -> local installer
```

The release contract uses an asset named like:

```text
ragdoll-product-engineering-standard-vX.Y.Z.zip
```

and `SHA256SUMS` containing that ZIP digest.

Pin v1.0.0:

POSIX:

```bash
curl -fsSL https://raw.githubusercontent.com/huynguyen2k5/Ragdoll-Product-Engineering-Standard/main/install.sh | RAGDOLL_VERSION=v1.0.0 sh
```

PowerShell:

```powershell
$env:RAGDOLL_VERSION="v1.0.0"; irm https://raw.githubusercontent.com/huynguyen2k5/Ragdoll-Product-Engineering-Standard/main/install.ps1 | iex
```

`RAGDOLL_REPO` remains overridable for forks/testing, but the canonical repository is the default.

## Install from a clone

POSIX:

```bash
./install.sh
```

PowerShell:

```powershell
.\install.ps1
```

## Installed layout

Default POSIX command:

```text
~/.local/bin/ragdoll
```

Default Windows command:

```text
%LOCALAPPDATA%\Ragdoll\bin\ragdoll.cmd
```

Persistent data home:

```text
~/.ragdoll/
├── .env
├── api-token
├── state.json
├── backups/
├── indexes/
├── logs/
├── projects/
└── runtime/
    └── app/
```

The Windows installer adds its command directory to the user PATH when needed.

## Configure providers

Edit only the Ragdoll-owned file:

```text
~/.ragdoll/.env
```

A project workspace's generic `.env` is not auto-loaded because it commonly contains unrelated application credentials.

Only the provider you use needs a key:

```env
RAGDOLL_PROVIDER=auto
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
```

Then:

```text
ragdoll init
ragdoll doctor
ragdoll start
ragdoll status
```

Project Context/History operations need no model key.

## Upgrade / reinstall

Run the same installer again. Runtime code is replaced while local data remains.

Normal upgrades preserve at least:

```text
~/.ragdoll/.env
~/.ragdoll/api-token
~/.ragdoll/state.json
~/.ragdoll/projects/
~/.ragdoll/indexes/
~/.ragdoll/logs/
~/.ragdoll/backups/
```

Core uses versioned local schema metadata so future data-layout changes can be migrated explicitly.

## Build release assets

```text
python scripts/build_release.py --output dist
```

The deterministic builder emits the source ZIP and `SHA256SUMS` consumed by the installer. The tag-triggered release workflow validates version/tag consistency before publication.

## Uninstall

POSIX:

```text
./uninstall.sh
```

PowerShell:

```powershell
.\uninstall.ps1
```

Normal uninstall removes installed runtime/command files and preserves user data.

Permanent deletion is separate:

```text
./uninstall.sh --purge-data
```

or:

```powershell
.\uninstall.ps1 -PurgeData
```

Purge is the destructive boundary. Upgrades, compaction, summaries, index rebuilds, and normal uninstall must never behave as implicit history deletion.

#!/bin/sh
set -eu

# Ragdoll installer.
# - From a checked-out repository: ./install.sh
# - Remote bootstrap: pipe this script to sh; the canonical GitHub repo is the default.
# Remote bootstrap downloads a GitHub Release asset, verifies SHA-256 from the
# release's SHA256SUMS file, then runs the installer from the verified archive.

PYTHON_BIN=${PYTHON:-}
RAGDOLL_DATA_HOME=${RAGDOLL_HOME:-"$HOME/.ragdoll"}
RUNTIME_DIR="$RAGDOLL_DATA_HOME/runtime"
APP_DIR="$RUNTIME_DIR/app"
BIN_DIR=${RAGDOLL_BIN_DIR:-"$HOME/.local/bin"}
COMMAND_PATH="$BIN_DIR/ragdoll"
BOOTSTRAP_TMP=""

cleanup() {
  if [ -n "$BOOTSTRAP_TMP" ] && [ -d "$BOOTSTRAP_TMP" ]; then
    rm -rf "$BOOTSTRAP_TMP"
  fi
}
trap cleanup EXIT HUP INT TERM

find_python() {
  if [ -n "$PYTHON_BIN" ]; then
    command -v "$PYTHON_BIN" >/dev/null 2>&1 || {
      echo "Configured PYTHON executable was not found: $PYTHON_BIN" >&2
      exit 1
    }
    return
  fi
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN=python3
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN=python
  else
    echo "Ragdoll requires Python 3.11 or newer." >&2
    echo "Install Python first, or set PYTHON=/path/to/python." >&2
    exit 1
  fi
}

check_python() {
  find_python
  "$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' || {
    echo "Ragdoll requires Python 3.11 or newer." >&2
    exit 1
  }
}

script_source_dir() {
  candidate=$(CDPATH= cd -- "$(dirname -- "$0")" 2>/dev/null && pwd || true)
  if [ -n "$candidate" ] && [ -d "$candidate/ragdoll" ] && [ -f "$candidate/pyproject.toml" ]; then
    printf '%s\n' "$candidate"
  fi
}

safe_extract_zip() {
  archive=$1
  destination=$2
  "$PYTHON_BIN" - "$archive" "$destination" <<'PY'
import sys
import zipfile
from pathlib import Path

archive = Path(sys.argv[1]).resolve()
destination = Path(sys.argv[2]).resolve()
destination.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(archive) as zf:
    for member in zf.infolist():
        target = (destination / member.filename).resolve()
        try:
            target.relative_to(destination)
        except ValueError:
            raise SystemExit(f"unsafe archive path: {member.filename}")
    zf.extractall(destination)
PY
}

verify_archive() {
  archive=$1
  sums=$2
  asset_name=$(basename "$archive")
  expected=$("$PYTHON_BIN" - "$sums" "$asset_name" <<'PY'
import sys
from pathlib import Path

sums = Path(sys.argv[1])
asset = sys.argv[2]
for line in sums.read_text(encoding="utf-8", errors="replace").splitlines():
    parts = line.strip().split()
    if len(parts) >= 2 and parts[-1].lstrip("*") == asset:
        digest = parts[0].lower()
        if len(digest) == 64 and all(ch in "0123456789abcdef" for ch in digest):
            print(digest)
            raise SystemExit(0)
raise SystemExit(1)
PY
  ) || {
    echo "Could not find a valid SHA-256 entry for $asset_name." >&2
    exit 1
  }
  actual=$("$PYTHON_BIN" - "$archive" <<'PY'
import hashlib
import sys
from pathlib import Path

path = Path(sys.argv[1])
h = hashlib.sha256()
with path.open("rb") as handle:
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
        h.update(chunk)
print(h.hexdigest())
PY
  )
  if [ "$actual" != "$expected" ]; then
    echo "Ragdoll release checksum verification failed." >&2
    echo "Expected: $expected" >&2
    echo "Actual:   $actual" >&2
    exit 1
  fi
}

bootstrap_from_local_archive() {
  archive=$1
  expected=${RAGDOLL_INSTALL_SHA256:-}
  if [ ! -f "$archive" ]; then
    echo "RAGDOLL_INSTALL_ARCHIVE does not exist: $archive" >&2
    exit 1
  fi
  if [ -z "$expected" ]; then
    echo "RAGDOLL_INSTALL_SHA256 is required with RAGDOLL_INSTALL_ARCHIVE." >&2
    exit 1
  fi
  actual=$("$PYTHON_BIN" - "$archive" <<'PY'
import hashlib
import sys
from pathlib import Path

path = Path(sys.argv[1])
h = hashlib.sha256()
with path.open("rb") as handle:
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
        h.update(chunk)
print(h.hexdigest())
PY
  )
  if [ "$actual" != "$expected" ]; then
    echo "Local Ragdoll archive checksum verification failed." >&2
    exit 1
  fi
  BOOTSTRAP_TMP=$(mktemp -d "${TMPDIR:-/tmp}/ragdoll-install.XXXXXX")
  safe_extract_zip "$archive" "$BOOTSTRAP_TMP/src"
}

bootstrap_from_github() {
  repo=${RAGDOLL_REPO:-huynguyen2k5/Ragdoll-Product-Engineering-Standard}
  requested=${RAGDOLL_VERSION:-latest}
  BOOTSTRAP_TMP=$(mktemp -d "${TMPDIR:-/tmp}/ragdoll-install.XXXXXX")
  metadata="$BOOTSTRAP_TMP/release.json"
  "$PYTHON_BIN" - "$repo" "$requested" "$metadata" <<'PY'
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

repo, requested, output = sys.argv[1:4]
if "/" not in repo or repo.startswith("/") or repo.endswith("/"):
    raise SystemExit("RAGDOLL_REPO must be owner/repository")
if requested == "latest":
    url = f"https://api.github.com/repos/{repo}/releases/latest"
else:
    tag = urllib.parse.quote(requested, safe="")
    url = f"https://api.github.com/repos/{repo}/releases/tags/{tag}"
request = urllib.request.Request(
    url,
    headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "ragdoll-installer",
        "X-GitHub-Api-Version": "2022-11-28",
    },
)
try:
    with urllib.request.urlopen(request, timeout=30) as response:
        release = json.load(response)
except urllib.error.HTTPError as exc:
    raise SystemExit(f"GitHub release lookup failed with HTTP {exc.code}") from None
except urllib.error.URLError as exc:
    raise SystemExit(f"GitHub release lookup failed: {exc.reason}") from None

tag = str(release.get("tag_name") or "")
assets = release.get("assets") if isinstance(release.get("assets"), list) else []
zip_assets = [
    item for item in assets
    if isinstance(item, dict)
    and str(item.get("name") or "").startswith("ragdoll-product-engineering-standard-")
    and str(item.get("name") or "").endswith(".zip")
    and item.get("browser_download_url")
]
sums = next(
    (
        item for item in assets
        if isinstance(item, dict)
        and str(item.get("name") or "") == "SHA256SUMS"
        and item.get("browser_download_url")
    ),
    None,
)
if not tag:
    raise SystemExit("GitHub release has no tag_name")
if len(zip_assets) != 1:
    raise SystemExit("Release must contain exactly one Ragdoll source ZIP asset")
if sums is None:
    raise SystemExit("Release must contain SHA256SUMS")
Path(output).write_text(
    json.dumps(
        {
            "tag": tag,
            "asset_name": zip_assets[0]["name"],
            "asset_url": zip_assets[0]["browser_download_url"],
            "sums_url": sums["browser_download_url"],
        }
    ),
    encoding="utf-8",
)
PY

  asset_name=$("$PYTHON_BIN" -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["asset_name"])' "$metadata")
  asset_url=$("$PYTHON_BIN" -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["asset_url"])' "$metadata")
  sums_url=$("$PYTHON_BIN" -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["sums_url"])' "$metadata")
  tag=$("$PYTHON_BIN" -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["tag"])' "$metadata")

  archive="$BOOTSTRAP_TMP/$asset_name"
  sums="$BOOTSTRAP_TMP/SHA256SUMS"
  "$PYTHON_BIN" - "$asset_url" "$archive" "$sums_url" "$sums" <<'PY'
import sys
import urllib.error
import urllib.request
from pathlib import Path

pairs = ((sys.argv[1], Path(sys.argv[2])), (sys.argv[3], Path(sys.argv[4])))
for url, path in pairs:
    request = urllib.request.Request(url, headers={"User-Agent": "ragdoll-installer"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response, path.open("wb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"download failed with HTTP {exc.code}: {url}") from None
    except urllib.error.URLError as exc:
        raise SystemExit(f"download failed: {exc.reason}") from None
PY
  verify_archive "$archive" "$sums"
  safe_extract_zip "$archive" "$BOOTSTRAP_TMP/src"
  printf '%s\n' "Verified Ragdoll release $tag from $repo."
}

locate_bootstrapped_source() {
  "$PYTHON_BIN" - "$BOOTSTRAP_TMP/src" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
candidates = []
for pyproject in root.rglob("pyproject.toml"):
    parent = pyproject.parent
    if (parent / "install.sh").is_file() and (parent / "ragdoll").is_dir():
        candidates.append(parent)
if len(candidates) != 1:
    raise SystemExit(f"expected exactly one Ragdoll source tree in archive; found {len(candidates)}")
print(candidates[0])
PY
}

install_from_source() {
  SOURCE_DIR=$1
  mkdir -p "$RUNTIME_DIR" "$BIN_DIR" "$RAGDOLL_DATA_HOME"
  rm -rf "$APP_DIR"
  mkdir -p "$APP_DIR"

  for item in ragdoll tools scripts references context-standard project-history-standard assets integrations project-context; do
    if [ -e "$SOURCE_DIR/$item" ]; then
      cp -R "$SOURCE_DIR/$item" "$APP_DIR/"
    fi
  done
  for file in SKILL.md README.md PRIVACY.md SECURITY.md CHANGELOG.md ROADMAP.md pyproject.toml .env.example; do
    if [ -f "$SOURCE_DIR/$file" ]; then
      cp "$SOURCE_DIR/$file" "$APP_DIR/$file"
    fi
  done

  if [ ! -f "$RAGDOLL_DATA_HOME/.env" ]; then
    cp "$SOURCE_DIR/.env.example" "$RAGDOLL_DATA_HOME/.env"
    chmod 600 "$RAGDOLL_DATA_HOME/.env" 2>/dev/null || true
  fi

  cat > "$COMMAND_PATH" <<EOF_WRAPPER
#!/bin/sh
export PYTHONPATH="$APP_DIR\${PYTHONPATH:+:\$PYTHONPATH}"
export RAGDOLL_HOME="\${RAGDOLL_HOME:-$RAGDOLL_DATA_HOME}"
exec "$PYTHON_BIN" -m ragdoll "\$@"
EOF_WRAPPER
  chmod +x "$COMMAND_PATH"

  PYTHONPATH="$APP_DIR${PYTHONPATH:+:$PYTHONPATH}" RAGDOLL_HOME="$RAGDOLL_DATA_HOME" "$PYTHON_BIN" -m ragdoll init >/dev/null

  printf '%s\n' "Ragdoll installed successfully." \
    "Command: $COMMAND_PATH" \
    "Data: $RAGDOLL_DATA_HOME" \
    "Config: $RAGDOLL_DATA_HOME/.env" \
    "History is preserved across reinstall/uninstall unless explicitly purged."

  case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *) printf '%s\n' "Add $BIN_DIR to PATH, then open a new terminal." ;;
  esac

  printf '%s\n' "Next:" \
    "  1. Edit $RAGDOLL_DATA_HOME/.env and add one provider API key." \
    "  2. Run: ragdoll doctor" \
    "  3. Run: ragdoll start"
}

check_python
SOURCE_DIR=$(script_source_dir || true)
if [ -z "$SOURCE_DIR" ]; then
  if [ -n "${RAGDOLL_INSTALL_ARCHIVE:-}" ]; then
    bootstrap_from_local_archive "$RAGDOLL_INSTALL_ARCHIVE"
  else
    bootstrap_from_github
  fi
  SOURCE_DIR=$(locate_bootstrapped_source)
fi
install_from_source "$SOURCE_DIR"

#!/usr/bin/env python3
"""Build the GitHub Release source ZIP expected by Ragdoll installers.

The archive name is stable and the ZIP contents are deterministic for the same
worktree bytes. SHA256SUMS is emitted next to the archive so remote installers
can verify the downloaded release before executing its installer.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_SLUG = "ragdoll-product-engineering-standard"
EXCLUDED_PREFIXES = (".git/", ".ragdoll/", "dist/", "build/", ".venv/", "venv/")
EXCLUDED_SUFFIXES = (".pyc", ".pyo", ".zip", ".bundle")


def project_version() -> str:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def worktree_files() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        paths = [Path(raw.decode("utf-8")) for raw in result.stdout.split(b"\0") if raw]
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError):
        paths = [path.relative_to(ROOT) for path in ROOT.rglob("*") if path.is_file()]

    selected: list[Path] = []
    for relative in paths:
        posix = relative.as_posix()
        if posix.startswith(EXCLUDED_PREFIXES) or relative.suffix in EXCLUDED_SUFFIXES:
            continue
        if posix == ".env" or posix.startswith(".env.") and posix != ".env.example":
            continue
        absolute = ROOT / relative
        if absolute.is_file():
            selected.append(relative)
    return sorted(set(selected), key=lambda item: item.as_posix())


def add_file(zf: zipfile.ZipFile, source: Path, arcname: str) -> None:
    info = zipfile.ZipInfo(arcname)
    info.date_time = (1980, 1, 1, 0, 0, 0)
    info.compress_type = zipfile.ZIP_DEFLATED
    mode = 0o755 if source.name in {"install.sh", "uninstall.sh"} or source.suffix == ".sh" else 0o644
    info.external_attr = (mode & 0xFFFF) << 16
    zf.writestr(info, source.read_bytes())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(output_dir: Path) -> tuple[Path, Path]:
    version = project_version()
    tag = f"v{version}"
    root_name = f"{PROJECT_SLUG}-{tag}"
    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"{root_name}.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for relative in worktree_files():
            add_file(zf, ROOT / relative, f"{root_name}/{relative.as_posix()}")
    sums = output_dir / "SHA256SUMS"
    sums.write_text(f"{sha256(archive)}  {archive.name}\n", encoding="ascii")
    return archive, sums


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dist", help="Output directory")
    args = parser.parse_args()
    archive, sums = build(Path(args.output).expanduser().resolve())
    print(archive)
    print(sums)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

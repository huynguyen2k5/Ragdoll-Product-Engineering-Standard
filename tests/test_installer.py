from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InstallerTests(unittest.TestCase):
    def _install_env(self, base: Path) -> tuple[dict[str, str], Path, Path]:
        home = base / "home"
        home.mkdir()
        data = base / "data"
        bin_dir = base / "bin"
        env = os.environ.copy()
        env.update(
            {
                "HOME": str(home),
                "RAGDOLL_HOME": str(data),
                "RAGDOLL_BIN_DIR": str(bin_dir),
                "PYTHON": sys.executable,
            }
        )
        return env, data, bin_dir

    def test_unix_install_and_uninstall_preserve_data(self) -> None:
        if os.name == "nt":
            self.skipTest("Unix installer test")
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            env, data, bin_dir = self._install_env(base)
            installed = subprocess.run(["sh", str(ROOT / "install.sh")], env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(0, installed.returncode, installed.stderr)
            command = bin_dir / "ragdoll"
            self.assertTrue(command.exists())
            doctor = subprocess.run([str(command), "doctor"], env=env, capture_output=True, text=True, timeout=15)
            self.assertEqual(0, doctor.returncode, doctor.stderr)
            self.assertTrue((data / ".env").exists())
            marker = data / "projects" / "keep-me.txt"
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text("keep", encoding="utf-8")
            removed = subprocess.run(["sh", str(ROOT / "uninstall.sh")], env=env, capture_output=True, text=True, timeout=15)
            self.assertEqual(0, removed.returncode, removed.stderr)
            self.assertTrue(marker.exists())
            self.assertFalse((data / "runtime").exists())

    def test_unix_remote_bootstrap_path_verifies_archive(self) -> None:
        if os.name == "nt":
            self.skipTest("Unix installer test")
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            env, data, bin_dir = self._install_env(base)
            archive = base / "ragdoll-product-engineering-standard-v1.0.0.zip"
            source_root = "ragdoll-product-engineering-standard-v1.0.0"
            include_roots = {
                "ragdoll",
                "tools",
                "scripts",
                "references",
                "context-standard",
                "project-history-standard",
                "assets",
                "integrations",
                "project-context",
            }
            include_files = {
                "install.sh",
                "install.ps1",
                "uninstall.sh",
                "uninstall.ps1",
                "SKILL.md",
                "README.md",
                "PRIVACY.md",
                "SECURITY.md",
                "CHANGELOG.md",
                "ROADMAP.md",
                "pyproject.toml",
                ".env.example",
            }
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
                for path in ROOT.rglob("*"):
                    if not path.is_file():
                        continue
                    relative = path.relative_to(ROOT)
                    if relative.parts[0] in include_roots or relative.as_posix() in include_files:
                        zf.write(path, Path(source_root) / relative)
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            standalone = base / "install.sh"
            shutil.copy2(ROOT / "install.sh", standalone)
            env.update({"RAGDOLL_INSTALL_ARCHIVE": str(archive), "RAGDOLL_INSTALL_SHA256": digest})
            installed = subprocess.run(["sh", str(standalone)], env=env, capture_output=True, text=True, timeout=45)
            self.assertEqual(0, installed.returncode, installed.stderr)
            command = bin_dir / "ragdoll"
            self.assertTrue(command.exists())
            doctor = subprocess.run([str(command), "doctor"], env=env, capture_output=True, text=True, timeout=15)
            self.assertEqual(0, doctor.returncode, doctor.stderr)
            self.assertTrue((data / ".env").exists())

    def test_unix_remote_bootstrap_rejects_wrong_checksum(self) -> None:
        if os.name == "nt":
            self.skipTest("Unix installer test")
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            env, _, _ = self._install_env(base)
            archive = base / "fake.zip"
            archive.write_bytes(b"not-a-release")
            standalone = base / "install.sh"
            shutil.copy2(ROOT / "install.sh", standalone)
            env.update({"RAGDOLL_INSTALL_ARCHIVE": str(archive), "RAGDOLL_INSTALL_SHA256": "0" * 64})
            installed = subprocess.run(["sh", str(standalone)], env=env, capture_output=True, text=True, timeout=15)
            self.assertNotEqual(0, installed.returncode)
            self.assertIn("checksum verification failed", installed.stderr.lower())

    def test_windows_powershell_install_and_uninstall_preserve_data(self) -> None:
        if os.name != "nt":
            self.skipTest("Windows PowerShell installer test")
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            env, data, bin_dir = self._install_env(base)
            installed = subprocess.run(
                [
                    "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                    "-File", str(ROOT / "install.ps1"),
                    "-Python", sys.executable,
                    "-BinDir", str(bin_dir),
                ],
                env=env, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(0, installed.returncode, installed.stderr)
            command = bin_dir / "ragdoll.cmd"
            self.assertTrue(command.exists())
            doctor = subprocess.run([str(command), "doctor"], env=env, capture_output=True, text=True, timeout=20)
            self.assertEqual(0, doctor.returncode, doctor.stderr)
            marker = data / "projects" / "keep-me.txt"
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text("keep", encoding="utf-8")
            removed = subprocess.run(
                [
                    "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                    "-File", str(ROOT / "uninstall.ps1"),
                    "-BinDir", str(bin_dir),
                ],
                env=env, capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(0, removed.returncode, removed.stderr)
            self.assertTrue(marker.exists())
            self.assertFalse((data / "runtime").exists())

    def test_powershell_installer_contains_remote_and_local_first_contracts(self) -> None:
        text = (ROOT / "install.ps1").read_text(encoding="utf-8")
        uninstall = (ROOT / "uninstall.ps1").read_text(encoding="utf-8")
        self.assertIn("RAGDOLL_HOME", text)
        self.assertIn(".env.example", text)
        self.assertIn("ragdoll.cmd", text)
        self.assertIn("RAGDOLL_REPO", text)
        self.assertIn("huynguyen2k5/Ragdoll-Product-Engineering-Standard", text)
        self.assertIn("SHA256SUMS", text)
        self.assertIn("Get-FileHash", text)
        self.assertIn("PurgeData", uninstall)
        self.assertIn("User data preserved", uninstall)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.project_history.security import is_sensitive_path, redact_text

ROOT = Path(__file__).resolve().parents[1]


class PrivacyDefaultsTests(unittest.TestCase):
    def test_history_default_policy_is_local_private_and_indefinite(self) -> None:
        policy = json.loads((ROOT / "project-history-standard" / "default-policy.json").read_text(encoding="utf-8"))
        self.assertEqual("indefinite", policy["retention"])
        self.assertEqual("local", policy["storage"])
        self.assertFalse(policy["auto_delete"])
        self.assertFalse(policy["cloud_sync"])
        self.assertFalse(policy["telemetry"])
        self.assertEqual("deny", policy["network_default"])
        self.assertTrue(policy["uninstall_preserves_history"])

    def test_sensitive_paths_are_recognized(self) -> None:
        for path in (".env", ".env.production", "keys/private.pem", "id_rsa", "client.key"):
            self.assertTrue(is_sensitive_path(path), path)
        self.assertFalse(is_sensitive_path("src/main.py"))

    def test_common_secret_text_is_redacted(self) -> None:
        self.assertNotIn("secret123456789", redact_text("prefix password=secret123456789 suffix"))
        self.assertNotIn("abcdefghijklmnop", redact_text("Bearer abcdefghijklmnop"))
        self.assertNotIn("generic123456789", redact_text("token=generic123456789"))

    def test_reference_history_code_has_no_network_imports(self) -> None:
        forbidden = ("import requests", "import httpx", "import socket", "urllib.request", "aiohttp")
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "tools" / "project_history").glob("*.py"))
        for marker in forbidden:
            self.assertNotIn(marker, combined)


if __name__ == "__main__":
    unittest.main()

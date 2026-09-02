from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ragdoll.config import Settings, parse_env_file


class ConfigTests(unittest.TestCase):
    def test_env_file_supports_api_key_only_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = root / ".env"
            env.write_text("OPENAI_API_KEY=test-key\n", encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                settings = Settings.load(str(env), root)
            self.assertEqual(["openai"], settings.configured_providers())
            self.assertEqual("openai", settings.resolve_provider())
            self.assertEqual("gpt-5.6", settings.model_for("openai"))
            self.assertNotIn("test-key", str(settings.safe_status()))

    def test_process_environment_overrides_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = Path(tmp) / ".env"
            env.write_text("RAGDOLL_PORT=8765\nOPENAI_API_KEY=file-key\n", encoding="utf-8")
            with patch.dict(os.environ, {"RAGDOLL_PORT": "9999", "OPENAI_API_KEY": "process-key"}, clear=True):
                settings = Settings.load(str(env), Path(tmp))
            self.assertEqual(9999, settings.port)
            self.assertEqual("process-key", settings.api_keys["openai"])

    def test_remote_bind_is_denied_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = Path(tmp) / ".env"
            env.write_text("RAGDOLL_HOST=0.0.0.0\n", encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(ValueError):
                    Settings.load(str(env), Path(tmp))

    def test_env_parser_handles_quotes_and_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = Path(tmp) / ".env"
            env.write_text("export OPENAI_API_KEY='abc'\nGEMINI_API_KEY=xyz\n", encoding="utf-8")
            values = parse_env_file(env)
            self.assertEqual("abc", values["OPENAI_API_KEY"])
            self.assertEqual("xyz", values["GEMINI_API_KEY"])



    def test_env_parser_strips_inline_comments(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = Path(tmp) / ".env"
            env.write_text(
                "OPENAI_API_KEY=my-secret-key # production key\n"
                "QUOTED_KEY='secret # not a comment'\n"
                "URL=https://example.com/api?a=1&b=2 # api url\n",
                encoding="utf-8",
            )
            values = parse_env_file(env)
            self.assertEqual("my-secret-key", values["OPENAI_API_KEY"])
            self.assertEqual("secret # not a comment", values["QUOTED_KEY"])
            self.assertEqual("https://example.com/api?a=1&b=2", values["URL"])

    def test_with_server_override_preserves_port_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = root / ".env"
            env.write_text("OPENAI_API_KEY=key\n", encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                settings = Settings.load(str(env), root)
            overridden = settings.with_server_override(port=9000)
            self.assertEqual(9000, overridden.port)

    def test_default_env_is_ragdoll_owned_not_workspace_dotenv(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "ragdoll-home"
            workspace = root / "workspace"
            home.mkdir()
            workspace.mkdir()
            (home / ".env").write_text("OPENAI_API_KEY=global-key\n", encoding="utf-8")
            (workspace / ".env").write_text("OPENAI_API_KEY=workspace-secret\n", encoding="utf-8")
            with patch.dict(os.environ, {"RAGDOLL_HOME": str(home)}, clear=True):
                settings = Settings.load(cwd=workspace)
            self.assertEqual(settings.api_keys["openai"], "global-key")
            self.assertEqual(settings.env_file, home / ".env")

if __name__ == "__main__":
    unittest.main()

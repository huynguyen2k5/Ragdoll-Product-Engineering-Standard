from __future__ import annotations

import io
import os
import tempfile
import urllib.error
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from ragdoll.config import Settings
from ragdoll.providers import ProviderError, _post_json, generate_text


class ProviderTests(unittest.TestCase):
    def settings(self, text: str) -> Settings:
        self.tmp = tempfile.TemporaryDirectory()
        path = Path(self.tmp.name) / ".env"
        path.write_text(text, encoding="utf-8")
        with patch.dict(os.environ, {}, clear=True):
            return Settings.load(str(path), Path(self.tmp.name))

    def tearDown(self) -> None:
        tmp = getattr(self, "tmp", None)
        if tmp:
            tmp.cleanup()

    def test_openai_uses_stateless_responses_request(self) -> None:
        settings = self.settings("OPENAI_API_KEY=sk-test-abcdefghijklmnop\n")
        captured = {}

        def fake(url, headers, body, timeout=90.0, max_response_bytes=None):
            captured.update(url=url, headers=headers, body=body)
            return {
                "id": "resp_1",
                "model": "gpt-5.6",
                "output": [{"content": [{"type": "output_text", "text": "ok"}]}],
                "usage": {"input_tokens": 3, "output_tokens": 1, "total_tokens": 4},
            }

        with patch("ragdoll.providers._post_json", side_effect=fake):
            response, security = generate_text(settings, prompt="hello", system="rules")
        self.assertEqual("openai", response.provider)
        self.assertFalse(captured["body"]["store"])
        self.assertEqual("rules", captured["body"]["instructions"])
        self.assertTrue(captured["headers"]["Authorization"].startswith("Bearer "))
        self.assertFalse(security["prompt_redacted"])

    def test_gemini_uses_generate_content_api(self) -> None:
        settings = self.settings("GEMINI_API_KEY=gemini-test\n")
        captured = {}

        def fake(url, headers, body, timeout=90.0, max_response_bytes=None):
            captured.update(url=url, headers=headers, body=body)
            return {
                "responseId": "gemini-response-1",
                "candidates": [{"content": {"parts": [{"text": "ok"}]}}],
                "usageMetadata": {"promptTokenCount": 3, "candidatesTokenCount": 1, "totalTokenCount": 4},
            }

        with patch("ragdoll.providers._post_json", side_effect=fake):
            response, _ = generate_text(settings, prompt="hello", system="rules")
        self.assertEqual("gemini", response.provider)
        self.assertTrue(captured["url"].endswith("/v1beta/models/gemini-3.6-flash:generateContent"))
        self.assertEqual("rules", captured["body"]["systemInstruction"]["parts"][0]["text"])
        self.assertEqual("hello", captured["body"]["contents"][0]["parts"][0]["text"])
        self.assertFalse(captured["body"]["store"])
        self.assertEqual(4096, captured["body"]["generationConfig"]["maxOutputTokens"])


    def test_anthropic_request_uses_messages_api(self) -> None:
        settings = self.settings("ANTHROPIC_API_KEY=anthropic-test\n")
        captured = {}

        def fake(url, headers, body, timeout=90.0, max_response_bytes=None):
            captured.update(url=url, headers=headers, body=body)
            return {
                "id": "msg_1",
                "model": "claude-sonnet-5",
                "content": [{"type": "text", "text": "ok"}],
                "usage": {"input_tokens": 3, "output_tokens": 1},
            }

        with patch("ragdoll.providers._post_json", side_effect=fake):
            response, _ = generate_text(settings, prompt="hello", system="rules")
        self.assertEqual("anthropic", response.provider)
        self.assertTrue(captured["url"].endswith("/v1/messages"))
        self.assertEqual("2023-06-01", captured["headers"]["anthropic-version"])

    def test_block_policy_rejects_secret_like_prompt(self) -> None:
        settings = self.settings("OPENAI_API_KEY=key\nRAGDOLL_OUTBOUND_SECRET_POLICY=block\n")
        with self.assertRaises(ProviderError):
            generate_text(settings, prompt="password=supersecretvalue", system="")

    def test_provider_redirect_is_denied(self) -> None:
        error = urllib.error.HTTPError(
            "https://api.openai.com/v1/responses",
            302,
            "Found",
            {"Location": "https://example.com/steal"},
            io.BytesIO(b"redirect"),
        )
        opener = MagicMock()
        opener.open.side_effect = error
        with patch("ragdoll.providers.urllib.request.build_opener", return_value=opener):
            with self.assertRaisesRegex(ProviderError, "redirects are denied"):
                _post_json(
                    "https://api.openai.com/v1/responses",
                    {"Authorization": "Bearer secret"},
                    {"model": "test"},
                    timeout=1,
                    max_response_bytes=1024,
                )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch

from ragdoll.config import Settings
from ragdoll.server import RagdollHTTPServer


class LocalServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.home = self.base / "home"
        self.repo = self.base / "repo"
        self.repo.mkdir()
        (self.repo / "README.md").write_text("# Test Project\n\nA project used to test Ragdoll local APIs.\n", encoding="utf-8")
        env = self.base / ".env"
        env.write_text(f"RAGDOLL_HOME={self.home}\nRAGDOLL_PORT=8765\n", encoding="utf-8")
        with patch.dict(os.environ, {}, clear=True):
            self.settings = Settings.load(str(env), self.base)
        self.server = RagdollHTTPServer(("127.0.0.1", 0), self.settings)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.token = self.server.api_token

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.tmp.cleanup()

    def request(self, method: str, path: str, body=None, auth=True, origin=None):
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(self.base_url + path, data=data, method=method)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        if auth:
            req.add_header("Authorization", f"Bearer {self.token}")
        if origin:
            req.add_header("Origin", origin)
        with urllib.request.urlopen(req, timeout=3) as response:
            return response.status, json.loads(response.read().decode("utf-8"))

    def test_health_is_public_but_status_requires_local_token(self) -> None:
        status, health = self.request("GET", "/v1/health", auth=False)
        self.assertEqual(200, status)
        self.assertTrue(health["ok"])
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.request("GET", "/v1/status", auth=False)
        self.assertEqual(401, caught.exception.code)

    def test_project_conversation_event_and_search_flow(self) -> None:
        _, project = self.request("POST", "/v1/projects", {"path": str(self.repo), "name": "Test"})
        project_id = project["project_id"]
        _, conversation = self.request("POST", f"/v1/projects/{project_id}/conversations", {"title": "Work"})
        conversation_id = conversation["conversation_id"]
        self.request(
            "POST",
            f"/v1/projects/{project_id}/conversations/{conversation_id}/events",
            {"type": "decision.recorded", "payload": {"text": "Use SQLite for the local history index"}},
        )
        _, search = self.request(
            "POST",
            f"/v1/projects/{project_id}/history/search",
            {"query": "SQLite local history", "mode": "focused", "token_budget": 800},
        )
        self.assertGreaterEqual(search["result_count"], 1)
        _, verify = self.request("GET", f"/v1/projects/{project_id}/conversations/{conversation_id}/verify")
        self.assertTrue(verify["ok"])

    def test_context_generate_validate_and_compile_flow(self) -> None:
        _, project = self.request("POST", "/v1/projects", {"path": str(self.repo)})
        project_id = project["project_id"]
        status, generated = self.request("POST", f"/v1/projects/{project_id}/context/generate", {})
        self.assertEqual(201, status)
        self.assertEqual("DRAFT_REQUIRES_REVIEW", generated["status"])
        _, validated = self.request("POST", f"/v1/projects/{project_id}/context/validate", {})
        self.assertTrue(validated["ok"])
        _, compiled = self.request(
            "POST",
            f"/v1/projects/{project_id}/context/compile",
            {"prompt": "What is the architecture?", "use_history": False},
        )
        self.assertTrue(compiled["project_context_available"])
        self.assertGreater(compiled["project_context_sections"], 0)

    def test_non_local_browser_origin_is_denied(self) -> None:
        for origin in ("https://evil.example", "http://localhost.evil.example"):
            with self.subTest(origin=origin):
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    self.request("GET", "/v1/status", origin=origin)
                self.assertEqual(403, caught.exception.code)

    def test_request_id_security_headers_and_readiness(self) -> None:
        req = urllib.request.Request(self.base_url + "/v1/ready", method="GET")
        with urllib.request.urlopen(req, timeout=3) as response:
            payload = json.loads(response.read().decode("utf-8"))
            self.assertTrue(payload["ok"])
            self.assertTrue(response.headers.get("X-Request-ID", "").startswith("req_"))
            self.assertEqual("no-store", response.headers.get("Cache-Control"))
            self.assertEqual("DENY", response.headers.get("X-Frame-Options"))

    def test_head_health_has_security_headers_and_no_body(self) -> None:
        req = urllib.request.Request(self.base_url + "/v1/health", method="HEAD")
        with urllib.request.urlopen(req, timeout=3) as response:
            self.assertEqual(200, response.status)
            self.assertEqual(b"", response.read())
            self.assertEqual("no-store", response.headers.get("Cache-Control"))
            self.assertEqual("nosniff", response.headers.get("X-Content-Type-Options"))

    def test_unsupported_put_and_patch_return_405_with_security_headers(self) -> None:
        for method in ("PUT", "PATCH"):
            req = urllib.request.Request(
                self.base_url + "/v1/status",
                data=b"{}",
                method=method,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
            )
            with self.subTest(method=method):
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    urllib.request.urlopen(req, timeout=3)
                self.assertEqual(405, caught.exception.code)
                self.assertEqual("no-store", caught.exception.headers.get("Cache-Control"))
                self.assertEqual("DENY", caught.exception.headers.get("X-Frame-Options"))

    def test_unexpected_keyerror_is_not_misreported_as_404(self) -> None:
        with patch.object(self.server.core, "status", side_effect=KeyError("programming bug")):
            with self.assertRaises(urllib.error.HTTPError) as caught:
                self.request("GET", "/v1/status")
        self.assertEqual(500, caught.exception.code)

    def test_event_api_is_paginated_and_idempotent(self) -> None:
        _, project = self.request("POST", "/v1/projects", {"path": str(self.repo)})
        pid = project["project_id"]
        _, conversation = self.request("POST", f"/v1/projects/{pid}/conversations", {})
        cid = conversation["conversation_id"]
        body = {"type": "user.message", "payload": {"text": "once"}, "idempotency_key": "http-request-0001"}
        _, first = self.request("POST", f"/v1/projects/{pid}/conversations/{cid}/events", body)
        _, second = self.request("POST", f"/v1/projects/{pid}/conversations/{cid}/events", body)
        self.assertEqual(first["event_hash"], second["event_hash"])
        _, page = self.request("GET", f"/v1/projects/{pid}/conversations/{cid}/events?after_seq=1&limit=1")
        self.assertEqual(1, len(page["events"]))
        self.assertEqual(2, page["next_after_seq"])

    def test_json_content_type_is_required_for_nonempty_body(self) -> None:
        req = urllib.request.Request(
            self.base_url + "/v1/projects",
            data=b"{}",
            method="POST",
            headers={"Authorization": f"Bearer {self.token}", "Content-Type": "text/plain"},
        )
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(req, timeout=3)
        self.assertEqual(415, caught.exception.code)


if __name__ == "__main__":
    unittest.main()

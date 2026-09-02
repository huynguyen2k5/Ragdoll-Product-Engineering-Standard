from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from tools.project_history.identity import normalize_remote, register_project
from tools.project_history.maintenance import rebuild_index
from tools.project_history.retrieval import compile_evidence, comprehensive_search, focused_search
from tools.project_history.store import append_event, conversation_dir, list_conversations, purge_project, start_conversation, verify_conversation


class ProjectHistoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.home = self.base / "ragdoll-home"
        self.repo_a = self.base / "project-a"
        self.repo_b = self.base / "project-b"
        self.repo_a.mkdir()
        self.repo_b.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _project(self, repo: Path, name: str) -> dict:
        return register_project(repo, name, self.home)

    def test_git_remote_normalization_is_protocol_independent(self) -> None:
        self.assertEqual(
            "github.com/example/repo",
            normalize_remote("git@github.com:Example/Repo.git").lower(),
        )
        self.assertEqual(
            "github.com/example/repo",
            normalize_remote("https://user:token@github.com/Example/Repo.git").lower(),
        )

    def test_project_histories_are_isolated(self) -> None:
        a = self._project(self.repo_a, "A")
        b = self._project(self.repo_b, "B")
        conv_a = start_conversation(a["project_id"], title="A", home=self.home)
        conv_b = start_conversation(b["project_id"], title="B", home=self.home)
        append_event(a["project_id"], conv_a["conversation_id"], "user.message", {"text": "alpha private architecture"}, home=self.home)
        append_event(b["project_id"], conv_b["conversation_id"], "user.message", {"text": "beta private architecture"}, home=self.home)

        results_a = focused_search(self.home, a["project_id"], "architecture", limit=20)
        results_b = focused_search(self.home, b["project_id"], "architecture", limit=20)
        self.assertTrue(results_a)
        self.assertTrue(results_b)
        self.assertTrue(all(item["project_id"] == a["project_id"] for item in results_a))
        self.assertTrue(all(item["project_id"] == b["project_id"] for item in results_b))
        self.assertFalse(any("beta" in item["content"] for item in results_a))

    def test_secrets_are_redacted_before_persistence(self) -> None:
        project = self._project(self.repo_a, "A")
        conv = start_conversation(project["project_id"], home=self.home)
        append_event(
            project["project_id"],
            conv["conversation_id"],
            "tool.result",
            {"text": "api_key=SUPER_SECRET_VALUE\nAuthorization: Bearer abcdefghijklmnopqrstuvwxyz", "password": "dont-store-me"},
            home=self.home,
        )
        events = conversation_dir(self.home, project["project_id"], conv["conversation_id"]) / "events.jsonl"
        text = events.read_text(encoding="utf-8")
        self.assertNotIn("SUPER_SECRET_VALUE", text)
        self.assertNotIn("dont-store-me", text)
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz", text)
        self.assertIn("[REDACTED]", text)

    def test_hash_chain_detects_tampering(self) -> None:
        project = self._project(self.repo_a, "A")
        conv = start_conversation(project["project_id"], home=self.home)
        append_event(project["project_id"], conv["conversation_id"], "user.message", {"text": "hello"}, home=self.home)
        self.assertEqual([], verify_conversation(self.home, project["project_id"], conv["conversation_id"]))

        path = conversation_dir(self.home, project["project_id"], conv["conversation_id"]) / "events.jsonl"
        lines = path.read_text(encoding="utf-8").splitlines()
        event = json.loads(lines[-1])
        event["payload"]["text"] = "tampered"
        lines[-1] = json.dumps(event, sort_keys=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.assertTrue(verify_conversation(self.home, project["project_id"], conv["conversation_id"]))

    def test_rebuild_index_does_not_modify_canonical_history(self) -> None:
        project = self._project(self.repo_a, "A")
        conv = start_conversation(project["project_id"], home=self.home)
        append_event(project["project_id"], conv["conversation_id"], "decision.recorded", {"text": "Use local SQLite indexing"}, home=self.home)
        path = conversation_dir(self.home, project["project_id"], conv["conversation_id"]) / "events.jsonl"
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        count = rebuild_index(self.home)
        after = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertGreaterEqual(count, 2)
        self.assertEqual(before, after)
        results = focused_search(self.home, project["project_id"], "SQLite", limit=10)
        self.assertTrue(any("SQLite" in item["content"] for item in results))

    def test_conversation_listing_uses_rebuildable_index_and_paginates(self) -> None:
        project = self._project(self.repo_a, "A")
        pid = project["project_id"]
        conversations = [start_conversation(pid, title=f"Conversation {i}", home=self.home) for i in range(5)]
        listed = list_conversations(self.home, pid, limit=2)
        self.assertEqual(2, len(listed))
        self.assertTrue(all(item["project_id"] == pid for item in listed))
        rebuild_index(self.home)
        listed_after_rebuild = list_conversations(self.home, pid, limit=5)
        self.assertEqual(5, len(listed_after_rebuild))
        self.assertEqual(
            {item["conversation_id"] for item in conversations},
            {item["conversation_id"] for item in listed_after_rebuild},
        )

    def test_comprehensive_search_scans_raw_project_history(self) -> None:
        project = self._project(self.repo_a, "A")
        conv = start_conversation(project["project_id"], home=self.home)
        append_event(project["project_id"], conv["conversation_id"], "assistant.message", {"text": "Architecture decision uses deterministic local storage"}, home=self.home)
        results = comprehensive_search(self.home, project["project_id"], "deterministic storage", limit=100)
        self.assertEqual(1, len(results))
        self.assertEqual(conv["conversation_id"], results[0]["conversation_id"])

    def test_compile_evidence_respects_small_budget(self) -> None:
        results = [
            {"content": "x" * 4000, "project_id": "p", "conversation_id": "c", "seq": 1},
            {"content": "y" * 4000, "project_id": "p", "conversation_id": "c", "seq": 2},
        ]
        compiled = compile_evidence(results, token_budget=400)
        self.assertEqual(1, compiled["result_count"])
        self.assertLessEqual(compiled["estimated_tokens"], 400)

    def test_purge_rejects_path_traversal_project_id(self) -> None:
        self.home.mkdir(parents=True, exist_ok=True)
        sentinel = self.home / "sentinel.txt"
        sentinel.write_text("keep", encoding="utf-8")
        with self.assertRaises(ValueError):
            purge_project(self.home, "..", "..")
        self.assertTrue(sentinel.exists())

    def test_purge_requires_exact_confirmation_and_removes_indexed_history(self) -> None:
        project = self._project(self.repo_a, "A")
        pid = project["project_id"]
        conv = start_conversation(pid, home=self.home)
        append_event(pid, conv["conversation_id"], "user.message", {"text": "delete marker"}, home=self.home)
        with self.assertRaises(ValueError):
            purge_project(self.home, pid, "wrong")
        purge_project(self.home, pid, pid)
        self.assertFalse((self.home / "projects" / pid).exists())
        self.assertEqual([], focused_search(self.home, pid, "delete marker", limit=10))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from ragdoll.config import Settings
from ragdoll.core import RagdollCore
from ragdoll.history.identity import register_project
from ragdoll.history.maintenance import get_index_status
from ragdoll.history.retrieval import forensic_search
from ragdoll.history.store import append_event, conversation_dir, iter_conversation_events, start_conversation
from ragdoll.storage.locks import exclusive_file_lock
from ragdoll.storage.migrations import CURRENT_HOME_SCHEMA, ensure_home_schema


class ProductionCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.home = self.base / "home"
        self.repo = self.base / "repo"
        self.repo.mkdir()
        (self.repo / "README.md").write_text("# Production Core Test\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def settings(self, extra: str = "") -> Settings:
        env = self.base / ".env"
        env.write_text(f"RAGDOLL_HOME={self.home}\n{extra}", encoding="utf-8")
        with patch.dict(os.environ, {}, clear=True):
            return Settings.load(str(env), self.base)

    def test_home_schema_is_versioned_and_idempotent(self) -> None:
        first = ensure_home_schema(self.home)
        second = ensure_home_schema(self.home)
        self.assertTrue(first.changed)
        self.assertFalse(second.changed)
        state = json.loads((self.home / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(CURRENT_HOME_SCHEMA, state["schema_version"])

    def test_newer_home_schema_fails_closed(self) -> None:
        self.home.mkdir(parents=True)
        (self.home / "state.json").write_text('{"schema_version":999}\n', encoding="utf-8")
        with self.assertRaises(RuntimeError):
            ensure_home_schema(self.home)

    def test_corrupt_home_schema_state_fails_closed(self) -> None:
        self.home.mkdir(parents=True)
        (self.home / "state.json").write_text("{broken", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            ensure_home_schema(self.home)

    def test_corrupt_project_registry_does_not_silently_reset(self) -> None:
        projects = self.home / "projects"
        projects.mkdir(parents=True)
        (projects / "registry.json").write_text("{broken", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            register_project(self.repo, home=self.home)

    def test_event_append_is_idempotent_when_key_is_supplied(self) -> None:
        project = register_project(self.repo, home=self.home)
        conversation = start_conversation(project["project_id"], home=self.home)
        first = append_event(
            project["project_id"],
            conversation["conversation_id"],
            "decision.recorded",
            {"text": "Use immutable canonical history"},
            idempotency_key="client-request-0001",
            home=self.home,
        )
        second = append_event(
            project["project_id"],
            conversation["conversation_id"],
            "decision.recorded",
            {"text": "This retry must not duplicate"},
            idempotency_key="client-request-0001",
            home=self.home,
        )
        self.assertEqual(first["event_hash"], second["event_hash"])
        events = list(iter_conversation_events(self.home, project["project_id"], conversation["conversation_id"]))
        self.assertEqual(2, len(events))  # conversation.started + one decision

    def test_event_pagination_is_bounded_and_cursor_like(self) -> None:
        project = register_project(self.repo, home=self.home)
        conversation = start_conversation(project["project_id"], home=self.home)
        for i in range(5):
            append_event(
                project["project_id"],
                conversation["conversation_id"],
                "user.message",
                {"text": f"message {i}"},
                home=self.home,
            )
        page = list(iter_conversation_events(self.home, project["project_id"], conversation["conversation_id"], after_seq=2, limit=2))
        self.assertEqual([3, 4], [item["seq"] for item in page])

    def test_forensic_search_expands_neighboring_raw_events(self) -> None:
        project = register_project(self.repo, home=self.home)
        conversation = start_conversation(project["project_id"], home=self.home)
        append_event(project["project_id"], conversation["conversation_id"], "user.message", {"text": "before"}, home=self.home)
        append_event(project["project_id"], conversation["conversation_id"], "decision.recorded", {"text": "choose SQLite WAL"}, home=self.home)
        append_event(project["project_id"], conversation["conversation_id"], "assistant.message", {"text": "after"}, home=self.home)
        results = forensic_search(self.home, project["project_id"], "SQLite", limit=10, neighbor_events=1)
        seqs = {item["seq"] for item in results}
        self.assertTrue({2, 3, 4}.issubset(seqs))

    def test_core_readiness_checks_index_integrity(self) -> None:
        core = RagdollCore(self.settings())
        core.bootstrap()
        ready = core.readiness()
        self.assertTrue(ready["ok"])
        self.assertEqual("ok", ready["history_index"]["integrity"])
        self.assertEqual(3, ready["history_index"]["index_schema_version"])

    def test_config_limits_are_strict_not_silently_clamped(self) -> None:
        with self.assertRaises(ValueError):
            self.settings("RAGDOLL_PORT=99999\n")
        with self.assertRaises(ValueError):
            self.settings("RAGDOLL_MAX_REQUEST_BYTES=not-a-number\n")
        with self.assertRaises(ValueError):
            self.settings("RAGDOLL_ALLOW_REMOTE_BIND=true\n")

    def test_direct_chat_service_validates_token_budgets(self) -> None:
        from ragdoll.service import chat_once

        settings = self.settings("OPENAI_API_KEY=test-key\n")
        project = register_project(self.repo, home=self.home)
        with self.assertRaisesRegex(Exception, "history_token_budget must be between"):
            chat_once(
                settings,
                {
                    "project_id": project["project_id"],
                    "prompt": "hello",
                    "history_token_budget": 1,
                    "use_project_context": False,
                },
            )

    def test_forced_context_regeneration_backs_up_previous_context(self) -> None:
        core = RagdollCore(self.settings())
        core.bootstrap()
        project = core.register_project({"path": str(self.repo)})
        pid = project["project_id"]
        core.generate_context(pid, {})
        overview = self.repo / "project-context" / "software-engineering" / "project-overview.md"
        overview.write_text(overview.read_text(encoding="utf-8") + "\nHUMAN DECISION MARKER\n", encoding="utf-8")
        core.generate_context(pid, {"force": True})
        backups = list((self.home / "backups" / pid).glob("project-context-*/software-engineering/project-overview.md"))
        self.assertEqual(1, len(backups))
        self.assertIn("HUMAN DECISION MARKER", backups[0].read_text(encoding="utf-8"))

    def test_index_exposes_migration_and_integrity_status(self) -> None:
        ensure_home_schema(self.home)
        status = get_index_status(self.home)
        self.assertEqual(3, status["index_schema_version"])
        self.assertEqual("ok", status["integrity"])
        self.assertFalse(status["dirty"])

    def test_old_lock_owned_by_live_process_is_not_stolen(self) -> None:
        lock = self.home / "live.lock"
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text(json.dumps({"pid": os.getpid(), "created_at": 0}), encoding="ascii")
        old = time.time() - 120
        os.utime(lock, (old, old))
        with self.assertRaises(TimeoutError):
            with exclusive_file_lock(lock, timeout_seconds=0.1, stale_after_seconds=0.01):
                pass

    def test_last_event_handles_large_payload(self) -> None:
        project = register_project(self.repo, home=self.home)
        conversation = start_conversation(project["project_id"], home=self.home)
        large_text = "x" * 20_000
        event = append_event(
            project["project_id"],
            conversation["conversation_id"],
            "user.message",
            {"text": large_text},
            home=self.home,
        )
        next_event = append_event(
            project["project_id"],
            conversation["conversation_id"],
            "assistant.message",
            {"text": "ok"},
            home=self.home,
        )
        self.assertEqual(event["seq"] + 1, next_event["seq"])

    def test_corrupt_jsonl_line_resilience(self) -> None:
        project = register_project(self.repo, home=self.home)
        conversation = start_conversation(project["project_id"], home=self.home)
        c_dir = conversation_dir(self.home, project["project_id"], conversation["conversation_id"])
        events_path = c_dir / "events.jsonl"
        with events_path.open("a", encoding="utf-8") as h:
            h.write("{not valid json\n")
        # Appending new event should still succeed despite corrupted line
        event = append_event(
            project["project_id"],
            conversation["conversation_id"],
            "user.message",
            {"text": "after corruption"},
            home=self.home,
        )
        self.assertIsNotNone(event["event_hash"])

if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
Unit tests for dreamtoosa.dreamer module.
"""

import tempfile
import unittest
from pathlib import Path

from dreamtoosa.dreamer import Dreamer, MemoryStore


class TestMemoryStore(unittest.TestCase):
    """Test MemoryStore operations."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_dir = Path(self.temp_dir.name)
        self.store = MemoryStore(store_id="test_store", storage_dir=self.storage_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_write_and_list_memories(self):
        self.store.write_memory("User prefers pytest", category="preferences")
        self.store.write_memory("Database is SQLite", category="infrastructure")

        memories = self.store.list_memories()
        self.assertEqual(len(memories), 2)

        pref = self.store.list_memories(category="preferences")
        self.assertEqual(len(pref), 1)
        self.assertEqual(pref[0]["content"], "User prefers pytest")

    def test_save_and_load(self):
        self.store.write_memory("Persisted memory", category="test")
        saved_path = self.store.save()

        loaded = MemoryStore.load(saved_path)
        self.assertEqual(loaded.id, self.store.id)
        self.assertEqual(len(loaded.memories), 1)
        self.assertEqual(loaded.memories[0]["content"], "Persisted memory")


class TestDreamer(unittest.TestCase):
    """Test Dreamer curation engine."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_dir = Path(self.temp_dir.name)
        self.dreamer = Dreamer(storage_dir=self.storage_dir)
        self.store = MemoryStore(store_id="raw_store", storage_dir=self.storage_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_deduplicate(self):
        memories = [
            {"id": "1", "content": "Prefer Python over Go"},
            {"id": "2", "content": "prefer python over go!"},  # normalized duplicate
            {"id": "3", "content": "Database is Postgres"},
        ]
        deduped, removed = self.dreamer.deduplicate(memories)
        self.assertEqual(len(deduped), 2)
        self.assertEqual(removed, 1)

    def test_curate_conflict_resolution(self):
        self.store.write_memory("Team standup Monday 10am", timestamp="2026-08-01T10:00:00")
        self.store.write_memory("Team standup Tuesday 9:30am", timestamp="2026-09-01T10:00:00")

        output_store = self.dreamer.curate(self.store)
        workflow_mems = output_store.list_memories(category="workflow")

        self.assertEqual(len(workflow_mems), 1)
        self.assertIn("Tuesday 9:30am", workflow_mems[0]["content"])
        self.assertIn("superseded", workflow_mems[0]["content"])

    def test_curate_synthesis_and_compare(self):
        self.store.write_memory("Preference for fast tests", category="preferences")
        self.store.write_memory("CI/CD on GitHub Actions", category="infrastructure")

        output_store = self.dreamer.curate(self.store)
        insights = output_store.list_memories(category="synthesized_insights")
        self.assertEqual(len(insights), 1)
        self.assertIn("System Synthesis", insights[0]["content"])

        stats = Dreamer.compare(self.store, output_store)
        self.assertIn("input_count", stats)
        self.assertIn("output_count", stats)
        self.assertEqual(stats["input_id"], "raw_store")


if __name__ == "__main__":
    unittest.main()

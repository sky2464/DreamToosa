#!/usr/bin/env python3
"""Heartbeat job gating for .github/workflows/control-plane.yml (DEV-005b TRI-B-018, 031, 032)."""
import unittest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
_raw = (ROOT / ".github/workflows/control-plane.yml").read_text(encoding="utf-8").replace("\non:\n", "\n'on':\n", 1)
WF = yaml.safe_load(_raw)
README = (ROOT / "dreamtoosa/README.md").read_text(encoding="utf-8")

class TestHeartbeatGating(unittest.TestCase):
    def test_schedule_and_dispatch_exist_and_jobs_are_gated(self):
        self.assertEqual(WF["on"]["schedule"][0]["cron"], "30 16 * * *")
        self.assertIn("workflow_dispatch", WF["on"])
        self.assertIn("schedule", WF["jobs"]["heartbeat"]["if"])
        self.assertIn("workflow_dispatch", WF["jobs"]["heartbeat"]["if"])
        self.assertNotIn("pull_request", WF["jobs"]["heartbeat"]["if"])
        self.assertNotIn("push", WF["jobs"]["heartbeat"]["if"])
        self.assertIn("schedule", WF["jobs"]["validate"]["if"])
        self.assertIn("!=", WF["jobs"]["validate"]["if"])

class TestHeartbeatPermissions(unittest.TestCase):
    def test_read_only_python_and_no_network_tools(self):
        job = WF["jobs"]["heartbeat"]
        self.assertEqual(job["permissions"], {"contents": "read"})
        self.assertEqual(job["timeout-minutes"], 5)
        blob = yaml.safe_dump(job)
        self.assertNotIn("secrets.", blob)
        for banned in ("gh ", "curl ", "mcp"):
            self.assertNotIn(banned, blob)
        self.assertIn("3.12", blob)
        self.assertIn("pyyaml", blob.lower())
        self.assertIn("actions/setup-python", blob)

class TestStepSummaryFixed(unittest.TestCase):
    def test_summary_line_uses_fixed_keys_only(self):
        blob = yaml.safe_dump(WF["jobs"]["heartbeat"])
        self.assertIn("ref=${ref} date=${date} age_days=${age}", blob)
        self.assertIn("GITHUB_STEP_SUMMARY", blob)

class TestValidateMatrix(unittest.TestCase):
    def test_validate_matrix_includes_312_floor(self):
        matrix = WF["jobs"]["validate"]["strategy"]["matrix"]["python-version"]
        self.assertIn("3.12", matrix)

class TestRunbookPresent(unittest.TestCase):
    def test_readme_names_the_60_day_disable_and_the_failure_meaning(self):
        self.assertIn("Ownership matrix", README)
        self.assertIn("60 days", README)
        self.assertIn("Re-enable", README)
        self.assertIn("failing heartbeat", README.lower())
        for col in ("Artifact", "Writer", "Gate", "Test"):
            self.assertIn(col, README)

if __name__ == "__main__":
    unittest.main()

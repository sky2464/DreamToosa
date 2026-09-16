#!/usr/bin/env python3
"""
Unit tests for the DreamToosa control plane validator (dreamtoosa/validate.py).
"""

import json
import tempfile
import unittest
from pathlib import Path
import yaml

from dreamtoosa.validate import (
    DEFAULT_MANIFEST,
    DEFAULT_PROFILES,
    DEFAULT_STATE,
    validate_control_plane,
)


class TestValidateControlPlane(unittest.TestCase):
    """Tests for validate_control_plane invariant assertions."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)

        # Base clean fixtures copied from repository defaults
        self.manifest_data = yaml.safe_load(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
        self.state_data = json.loads(DEFAULT_STATE.read_text(encoding="utf-8"))
        self.profiles_dir = DEFAULT_PROFILES

    def tearDown(self):
        self.tmp_dir.cleanup()

    def _write_fixtures(self, manifest_data, state_data):
        m_file = self.tmp_path / "repos.yml"
        s_file = self.tmp_path / "state.json"
        m_file.write_text(yaml.safe_dump(manifest_data), encoding="utf-8")
        s_file.write_text(json.dumps(state_data), encoding="utf-8")
        return m_file, s_file

    def test_clean_configuration_passes(self):
        """Current repository control plane must pass all 19 checks cleanly."""
        checks_run, failures = validate_control_plane(
            manifest_path=DEFAULT_MANIFEST,
            state_path=DEFAULT_STATE,
            profiles_dir=DEFAULT_PROFILES,
            verbose=False,
        )
        self.assertEqual(failures, [])
        self.assertGreaterEqual(checks_run, 19)

    def test_invalid_yaml_fails(self):
        """Malformed YAML must trigger a YAML parse failure."""
        m_file = self.tmp_path / "repos.yml"
        s_file = self.tmp_path / "state.json"
        m_file.write_text("repos: [unclosed list", encoding="utf-8")
        s_file.write_text(json.dumps(self.state_data), encoding="utf-8")

        checks_run, failures = validate_control_plane(
            manifest_path=m_file,
            state_path=s_file,
            profiles_dir=self.profiles_dir,
            verbose=False,
        )
        self.assertIn("repos.yml parses as YAML", failures)

    def test_invalid_json_fails(self):
        """Malformed JSON in state.json must fail cleanly."""
        m_file = self.tmp_path / "repos.yml"
        s_file = self.tmp_path / "state.json"
        m_file.write_text(yaml.safe_dump(self.manifest_data), encoding="utf-8")
        s_file.write_text("{ unquoted_key: 123 ", encoding="utf-8")

        checks_run, failures = validate_control_plane(
            manifest_path=m_file,
            state_path=s_file,
            profiles_dir=self.profiles_dir,
            verbose=False,
        )
        self.assertIn("state.json parses as JSON", failures)

    def test_unsupported_pr_strategy_fails(self):
        """Unrecognized pr_strategy value must be rejected."""
        self.manifest_data["hub"]["pr_strategy"] = "invalid_strategy_foo"
        m_file, s_file = self._write_fixtures(self.manifest_data, self.state_data)

        checks_run, failures = validate_control_plane(
            manifest_path=m_file,
            state_path=s_file,
            profiles_dir=self.profiles_dir,
            verbose=False,
        )
        self.assertIn("hub.pr_strategy is a supported strategy", failures)

    def test_negative_hub_max_unmerged_report_prs_fails(self):
        """Zero or negative hub max_unmerged_report_prs must be rejected."""
        self.manifest_data["hub"]["max_unmerged_report_prs"] = 0
        m_file, s_file = self._write_fixtures(self.manifest_data, self.state_data)

        checks_run, failures = validate_control_plane(
            manifest_path=m_file,
            state_path=s_file,
            profiles_dir=self.profiles_dir,
            verbose=False,
        )
        self.assertIn("hub.max_unmerged_report_prs is a positive integer", failures)

    def test_invalid_clone_root_env_fails(self):
        """Invalid environment variable name in defaults.clone_root_env must be rejected."""
        self.manifest_data["defaults"]["clone_root_env"] = "INVALID-ENV NAME WITH SPACES"
        m_file, s_file = self._write_fixtures(self.manifest_data, self.state_data)

        checks_run, failures = validate_control_plane(
            manifest_path=m_file,
            state_path=s_file,
            profiles_dir=self.profiles_dir,
            verbose=False,
        )
        self.assertIn("defaults.clone_root_env is a valid environment variable name", failures)

    def test_missing_budget_cap_fails(self):
        """Omission of required budget keys must be caught."""
        del self.manifest_data["budget"]["max_prs_per_run"]
        m_file, s_file = self._write_fixtures(self.manifest_data, self.state_data)

        checks_run, failures = validate_control_plane(
            manifest_path=m_file,
            state_path=s_file,
            profiles_dir=self.profiles_dir,
            verbose=False,
        )
        self.assertIn("budget declares all required caps", failures)

    def test_manifest_and_state_repo_mismatch_fails(self):
        """State file tracking repos not declared in manifest must be caught."""
        self.state_data["repos"]["sky2464/OrphanRepo"] = {
            "last_reviewed_sha": None,
            "last_report_date": None,
            "issues_filed": [],
            "prs_opened": [],
            "last_skip_reason": None,
        }
        m_file, s_file = self._write_fixtures(self.manifest_data, self.state_data)

        checks_run, failures = validate_control_plane(
            manifest_path=m_file,
            state_path=s_file,
            profiles_dir=self.profiles_dir,
            verbose=False,
        )
        self.assertIn("state.json tracks exactly the manifest's repos", failures)


if __name__ == "__main__":
    unittest.main()

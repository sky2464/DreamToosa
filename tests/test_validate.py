#!/usr/bin/env python3
"""
Unit tests for the DreamToosa control plane validator (dreamtoosa/validate.py).
"""

import ast
import contextlib
import copy
import io
import json
import os
import shutil
import subprocess
import sys
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
        """Current repository control plane (triage block included) must pass all 35 checks cleanly."""
        checks_run, failures = validate_control_plane(
            manifest_path=DEFAULT_MANIFEST,
            state_path=DEFAULT_STATE,
            profiles_dir=DEFAULT_PROFILES,
            verbose=False,
        )
        self.assertEqual(failures, [])
        self.assertGreaterEqual(checks_run, 35)  # 19 original + 16 guarded triage checks

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

    def test_real_manifest_declares_triage_block(self):
        """The committed manifest carries the Fleet Triage keys with a visibility per repo."""
        self.assertIn("triage", self.manifest_data)
        for entry in self.manifest_data["repos"]:
            self.assertIn(entry.get("visibility"), {"public", "private"}, entry["repo"])


# --- Fleet Triage keys (DEV-005a) -----------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATE_PY = REPO_ROOT / "dreamtoosa" / "validate.py"
BASELINE_CHECKS = 19  # checks that run with no triage block

TRIAGE_DEFAULTS = ("stale_after_days", "dormant_after_days")
TRIAGE_REPO_KEYS = ("visibility", "backlog", "product_workflows", "watch_workflows", "dependabot_scope")
DEL = object()  # sentinel: remove the key


def strip_triage(manifest):
    """Copy of manifest with every key the triage story added removed."""
    m = copy.deepcopy(manifest)
    m.pop("triage", None)
    for key in TRIAGE_DEFAULTS:
        m["defaults"].pop(key, None)
    m["hub"].pop("force_read_only", None)
    m["budget"].pop("soft_time_box_minutes_fleet_triage", None)
    for entry in m["repos"]:
        for key in TRIAGE_REPO_KEYS:
            entry.pop(key, None)
    return m


def with_triage(manifest):
    """Copy of manifest extended with a complete, valid triage configuration (test-only values)."""
    m = strip_triage(manifest)
    m["defaults"].update(stale_after_days=14, dormant_after_days=45)
    m["hub"]["force_read_only"] = False
    m["budget"]["soft_time_box_minutes_fleet_triage"] = 10
    m["triage"] = {
        "max_items_total": 8,
        "max_items_per_repo": 3,
        "pr_idle_days": 7,
        "routine_gap_days": 2,
        "heartbeat_max_age_days": 3,
        "trusted_logins": ["owner-login", "helper[bot]"],
    }
    for entry in m["repos"]:
        entry.update(
            visibility="public",
            backlog={
                "path": "docs/Plan.md",
                "header_all": ["ID", "Title", "Priority", "Status"],
                "columns": {"id": "ID", "title": "Title", "priority": "Priority", "status": "Status"},
                "p0_values": ["P0"],
                "done_values": ["Shipped"],
                "done_sections": ["Completed This Cycle"],
            },
            product_workflows=["ci.yml"],
            watch_workflows=[{"file": "scan.yml", "kind": "security"}],
            dependabot_scope="runtime",
        )
    return m


def edit(*pairs):
    """Mutator applying (dotted.path, value) pairs; a numeric segment indexes a list; DEL removes the key."""

    def apply(m):
        for dotted, value in pairs:
            *parents, leaf = dotted.split(".")
            node = m
            for part in parents:
                node = node[int(part)] if isinstance(node, list) else node[part]
            if value is DEL:
                del node[leaf]
            else:
                node[leaf] = value

    return apply


def run_validator(tmp_path, manifest, state, verbose=False):
    """Write manifest and state under tmp_path and run the validator on them."""
    m_file = tmp_path / "repos.yml"
    s_file = tmp_path / "state.json"
    m_file.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    s_file.write_text(json.dumps(state), encoding="utf-8")
    return validate_control_plane(
        manifest_path=m_file, state_path=s_file, profiles_dir=DEFAULT_PROFILES, verbose=verbose
    )


L_MAPPING = "triage block is a mapping"
L_CAPS = "triage caps are positive integers"
L_CAPS_ORDER = "triage.max_items_total is at least triage.max_items_per_repo"
L_WINDOWS = "triage idle, gap and heartbeat windows are positive integers"
L_LOGINS = "triage.trusted_logins is a non-empty list of logins"
L_DEF_POS = "defaults stale and dormant windows are positive integers"
L_DEF_ORDER = "defaults.stale_after_days is less than defaults.dormant_after_days"
L_TIMEBOX = "budget.soft_time_box_minutes_fleet_triage is a positive integer"
L_FORCE = "hub.force_read_only is a boolean when present"
L_VIS = "every repo declares visibility public or private"
L_PATH = "every repo's backlog path is relative with no '..'"
L_HEADER = "every repo's backlog header_all is a non-empty list"
L_COLS = "every repo's backlog columns id, title, priority are names and status is a name or null"
L_LISTS = "every repo's backlog p0_values, done_values and done_sections are lists"
L_WF = "every repo's workflow filenames and watch kinds are valid"
L_SCOPE = "every repo's dependabot_scope is runtime, dev or unknown when present"

BL = "repos.0.backlog."
NEGATIVES = [
    (L_MAPPING, edit(("triage", None))),
    (L_MAPPING, edit(("triage", ["x"]))),
    (L_CAPS, edit(("triage.max_items_total", 0))),
    (L_CAPS, edit(("triage.max_items_per_repo", True))),
    (L_CAPS, edit(("triage.max_items_per_repo", "3"))),
    (L_CAPS, edit(("triage.max_items_total", DEL))),
    (L_CAPS_ORDER, edit(("triage.max_items_total", 2), ("triage.max_items_per_repo", 3))),
    (L_WINDOWS, edit(("triage.pr_idle_days", 0))),
    (L_WINDOWS, edit(("triage.routine_gap_days", "2"))),
    (L_WINDOWS, edit(("triage.heartbeat_max_age_days", DEL))),
    (L_LOGINS, edit(("triage.trusted_logins", []))),
    (L_LOGINS, edit(("triage.trusted_logins", "owner-login"))),
    (L_LOGINS, edit(("triage.trusted_logins", ["owner-login", ""]))),
    (L_LOGINS, edit(("triage.trusted_logins", ["not a login"]))),
    (L_DEF_POS, edit(("defaults.stale_after_days", 0))),
    (L_DEF_POS, edit(("defaults.dormant_after_days", DEL))),
    (L_DEF_POS, edit(("defaults.dormant_after_days", "45"))),
    (L_DEF_ORDER, edit(("defaults.stale_after_days", 45))),
    (L_DEF_ORDER, edit(("defaults.stale_after_days", 50))),
    (L_TIMEBOX, edit(("budget.soft_time_box_minutes_fleet_triage", 0))),
    (L_TIMEBOX, edit(("budget.soft_time_box_minutes_fleet_triage", DEL))),
    (L_TIMEBOX, edit(("budget.soft_time_box_minutes_fleet_triage", "10"))),
    (L_FORCE, edit(("hub.force_read_only", "false"))),
    (L_FORCE, edit(("hub.force_read_only", 1))),
    (L_VIS, edit(("repos.0.visibility", "internal"))),
    (L_VIS, edit(("repos.0.visibility", "Public"))),
    (L_VIS, edit(("repos.0.visibility", ["public"]))),
    (L_VIS, edit(("repos.0.visibility", DEL))),
    (L_PATH, edit((BL + "path", "../secrets.md"))),
    (L_PATH, edit((BL + "path", "docs/../../x.md"))),
    (L_PATH, edit((BL + "path", "/etc/passwd"))),
    (L_PATH, edit((BL + "path", "C:/plan.md"))),
    (L_PATH, edit((BL + "path", "docs\\Plan.md"))),
    (L_PATH, edit((BL + "path", ""))),
    (L_PATH, edit((BL + "path", DEL))),
    (L_HEADER, edit((BL + "header_all", []))),
    (L_HEADER, edit((BL + "header_all", "ID"))),
    (L_HEADER, edit((BL + "header_all", ["ID", 1]))),
    (L_HEADER, edit((BL + "header_all", DEL))),
    (L_COLS, edit((BL + "columns.id", DEL))),
    (L_COLS, edit((BL + "columns.title", ""))),
    (L_COLS, edit((BL + "columns.priority", 3))),
    (L_COLS, edit((BL + "columns", DEL))),
    (L_COLS, edit((BL + "columns.status", 5))),
    (L_COLS, edit((BL + "columns.status", ""))),
    (L_LISTS, edit((BL + "p0_values", "P0"))),
    (L_LISTS, edit((BL + "p0_values", DEL))),
    (L_LISTS, edit((BL + "done_sections", [1]))),
    (L_LISTS, edit((BL + "done_sections", DEL))),
    (L_LISTS, edit((BL + "done_values", "Shipped"))),
    (L_LISTS, edit((BL + "done_values", DEL))),
    (L_WF, edit(("repos.0.product_workflows", ["../ci.yml"]))),
    (L_WF, edit(("repos.0.product_workflows", ["ci.txt"]))),
    (L_WF, edit(("repos.0.product_workflows", ["ci.yml\n"]))),
    (L_WF, edit(("repos.0.product_workflows", "ci.yml"))),
    (L_WF, edit(("repos.0.watch_workflows", [{"file": "a/b.yml", "kind": "sync"}]))),
    (L_WF, edit(("repos.0.watch_workflows", ["scan.yml"]))),
    (L_WF, edit(("repos.0.watch_workflows", "scan.yml"))),
    (L_WF, edit(("repos.0.watch_workflows.0.kind", "other"))),
    (L_WF, edit(("repos.0.watch_workflows.0.kind", DEL))),
    (L_SCOPE, edit(("repos.0.dependabot_scope", "prod"))),
    (L_SCOPE, edit(("repos.0.dependabot_scope", 7))),
    (L_SCOPE, edit(("repos.0.dependabot_scope", ["runtime"]))),
]


class TestTriageChecks(unittest.TestCase):
    """VA-1 and VA-2: the guarded Fleet Triage checks."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)
        real = yaml.safe_load(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
        self.base = strip_triage(real)
        self.valid = with_triage(real)
        self.state = json.loads(DEFAULT_STATE.read_text(encoding="utf-8"))

    def tearDown(self):
        self.tmp_dir.cleanup()

    def _labels(self, manifest):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            run_validator(self.tmp_path, manifest, self.state, verbose=True)
        return [
            line[8:].split(" \u2014 ")[0]
            for line in buf.getvalue().splitlines()
            if line.startswith(("  ok    ", "  FAIL  "))
        ]

    def test_valid_triage_configuration_passes(self):
        checks_run, failures = run_validator(self.tmp_path, self.valid, self.state)
        self.assertEqual(failures, [])
        self.assertEqual(checks_run, BASELINE_CHECKS + len({label for label, _ in NEGATIVES}))

    def test_each_negative_fails_exactly_its_check(self):
        """VA-1: every malformed value trips the one check that owns it, and no other."""
        for index, (label, mutate) in enumerate(NEGATIVES):
            with self.subTest(label=label, case=index):
                manifest = copy.deepcopy(self.valid)
                mutate(manifest)
                _, failures = run_validator(self.tmp_path, manifest, self.state)
                self.assertEqual(failures, [label])

    def test_every_new_check_has_a_negative(self):
        """VA-1: the checks added for triage are exactly the ones the negatives cover."""
        new = set(self._labels(self.valid)) - set(self._labels(self.base))
        self.assertEqual(new, {label for label, _ in NEGATIVES})

    def test_manifest_without_triage_block_adds_no_checks(self):
        """VA-2: a pre-triage manifest runs the original 19 checks and passes."""
        checks_run, failures = run_validator(self.tmp_path, self.base, self.state)
        self.assertEqual(failures, [])
        self.assertEqual(checks_run, BASELINE_CHECKS)

    def test_new_keys_are_ignored_without_triage_block(self):
        """VA-2: the triage checks are guarded by the block, not by the individual keys."""
        manifest = copy.deepcopy(self.base)
        manifest["defaults"].update(stale_after_days=0, dormant_after_days=-1)
        manifest["hub"]["force_read_only"] = "maybe"
        manifest["repos"][0].update(visibility="internal", backlog="nonsense", dependabot_scope=7)
        checks_run, failures = run_validator(self.tmp_path, manifest, self.state)
        self.assertEqual(failures, [])
        self.assertEqual(checks_run, BASELINE_CHECKS)


class TestValidateSubprocess(unittest.TestCase):
    """VA-3 and VA-4: script mode and exit codes, always in a subprocess."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def _run(self, script, env=None, cwd=None):
        return subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
            cwd=cwd,
        )

    def _tree(self, manifest_text=None, state_data=None):
        """A throwaway copy of the control plane: the script resolves its data next to itself."""
        pkg = self.tmp_path / "tree" / "dreamtoosa"
        pkg.mkdir(parents=True)
        shutil.copy(VALIDATE_PY, pkg / "validate.py")
        shutil.copytree(DEFAULT_PROFILES, pkg / "profiles")
        if manifest_text is None:
            manifest_text = DEFAULT_MANIFEST.read_text(encoding="utf-8")
        if state_data is None:
            state_data = json.loads(DEFAULT_STATE.read_text(encoding="utf-8"))
        (pkg / "repos.yml").write_text(manifest_text, encoding="utf-8")
        (pkg / "state.json").write_text(json.dumps(state_data), encoding="utf-8")
        return pkg / "validate.py"

    def test_script_mode_from_repo_root_exits_zero(self):
        result = self._run(Path("dreamtoosa") / "validate.py", cwd=REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASSED", result.stdout)

    def test_validate_source_has_no_triage_import(self):
        tree = ast.parse(VALIDATE_PY.read_text(encoding="utf-8"))
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported += [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                imported += [node.module or ""] + [alias.name for alias in node.names]
        self.assertEqual([name for name in imported if "triage" in name.lower()], [])
        self.assertNotIn("importlib", imported)
        self.assertNotIn("__import__", VALIDATE_PY.read_text(encoding="utf-8"))

    def test_missing_pyyaml_exits_two(self):
        stub = self.tmp_path / "stub"
        stub.mkdir()
        (stub / "yaml.py").write_text('raise ImportError("simulated missing PyYAML")\n', encoding="utf-8")
        env = dict(os.environ, PYTHONPATH=str(stub))
        result = self._run(VALIDATE_PY, env=env, cwd=REPO_ROOT)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("PyYAML", result.stderr)

    def test_uncaught_exception_exits_two(self):
        """A manifest that parses but has the wrong top-level type crashes a check, not the exit code."""
        script = self._tree(manifest_text="- not\n- a mapping\n")
        result = self._run(script)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unexpected error", result.stderr)

    def test_check_failure_exits_one(self):
        state = json.loads(DEFAULT_STATE.read_text(encoding="utf-8"))
        state["repos"]["sky2464/OrphanRepo"] = {}
        script = self._tree(state_data=state)
        result = self._run(script)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("FAILED", result.stdout)

    def test_copied_tree_passes_untouched(self):
        """Guards the harness: the throwaway tree is valid until a test breaks it."""
        result = self._run(self._tree())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()

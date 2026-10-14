#!/usr/bin/env python3
"""CLI tests for dreamtoosa/triage_report.py (DEV-005a CL-1..CL-7, plus a guard against drift between the fixture manifest and the real repos.yml).

Everything is offline. Git behaviour runs against throw-away repositories in temp dirs, never this repository: a $CLONE_ROOT holding the four
clones (the DreamToosa clone doubles as the hub whose dreamtoosa/ directory is the integrity subject), origin/* refs made with update-ref, and
the frozen snapshot patched to the real SHAs of those repos. Exit codes: 0 ok, 1 fixed codes on stdout, 2 usage error or cannot run (E_RUN).
Secret-shaped strings are assembled at run time so that no literal token sits in this file.
"""
import copy
import datetime
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

import dreamtoosa.triage_report as tr

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "dreamtoosa" / "triage_report.py"
FX = ROOT / "tests" / "fixtures" / "triage"
MANIFEST = FX / "repos-2026-10-13.yml"
GENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
TODAY = "2026-10-13"
SECRETS = ["gh" + "p_" + "a" * 20, "github" + "_pat_" + "a" * 20, "gh" + "s_" + "a" * 10, "sk-" + "ant-" + "a" * 10, "AK" + "IA" + "A" * 16,
           "AI" + "za" + "a" * 35, "xo" + "xb-" + "1" * 10, "-----" + "BEGIN KEY", "ey" + "Jaaa.bbb.ccc"]
TAMPER = "E_ENGINE_TAMPERED"


def jload(name): return json.loads((FX / name).read_text(encoding="utf-8"))
def day(n): return (datetime.date.fromisoformat(TODAY) - datetime.timedelta(days=n)).isoformat()


def git(d, *args, date=None):
    env = dict(GENV)
    if date:
        env.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    r = subprocess.run(["git", "-c", "user.name=fx", "-c", "user.email=fx@example.invalid", "-c", "commit.gpgsign=false", "-C", str(d), *args],
                       capture_output=True, text=True, env=env)
    if r.returncode:
        raise AssertionError(f"git {args}: {r.stderr}")
    return r.stdout.strip()


def commit(d, files, msg, date):
    for rel, text in files.items():
        p = Path(d) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", msg, date=date)
    return git(d, "rev-parse", "HEAD")


def init(d):
    Path(d).mkdir(parents=True, exist_ok=True)
    git(d, "init", "-q")
    git(d, "symbolic-ref", "HEAD", "refs/heads/main")


def run(*args, cwd=None):
    r = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout, r.stderr


def build_world(root):
    """Four clones under root with the frozen snapshot's dates, origin refs and hub state; returns the snapshot patched to what git holds."""
    snap, man = jload("snapshot-2026-10-13.json"), yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    for s in snap["repos"]:
        d, m = root / s["name"], next(m for m in man["repos"] if m["repo"] == s["repo"])
        init(d)
        files = {m["backlog"]["path"]: (FX / "backlogs" / (s["name"].lower() + ".md")).read_text(encoding="utf-8")}
        if s["name"] == "AgToosa":
            files[".github/workflows/security-scan.yml"] = "on:\n  schedule:\n    - cron: '23 4 * * 1'\njobs: {}\n"
        if s["name"] == "DreamToosa":
            files["dreamtoosa/state.json"] = json.dumps({"last_run": {"date": "2026-09-18"}})
        first = commit(d, files, "synthetic first commit", s["tip"]["prev_committer_date"])
        tip = commit(d, {"README.md": "synthetic\n"}, "synthetic fixes #11" if s["name"] == "AgToosa" else "synthetic tip commit", s["tip"]["committer_date"])
        git(d, "update-ref", "refs/remotes/origin/main", tip)
        s["tip"]["sha"], s["fix_links"] = tip, ([{"issue": 11, "sha": tip}] if s["name"] == "AgToosa" else [])
        if s["name"] == "DreamToosa":
            git(d, "checkout", "-q", "-b", "tmp", first)
            rpt = commit(d, {"dreamtoosa/state.json": json.dumps({"last_run": {"date": "2026-09-17"}})}, "synthetic report branch", "2026-09-17T09:00:00+00:00")
            git(d, "update-ref", "refs/remotes/origin/dreamtoosa/report-2026-09-17", rpt)
            git(d, "checkout", "-q", "main")
            git(d, "branch", "-q", "-D", "tmp")
    return snap


_SHARED = {}


def shared_world():
    """One set of throw-away repos for the whole module; every test that touches them puts them back."""
    if not _SHARED:
        tmp = tempfile.TemporaryDirectory()
        unittest.addModuleCleanup(tmp.cleanup)
        root = Path(tmp.name) / "clones"
        _SHARED.update(tmp=tmp, root=root, base=build_world(root), hub=root / "DreamToosa")
    return _SHARED


class World(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for k, v in shared_world().items():
            setattr(cls, k, v)

    def setUp(self): self.snap = copy.deepcopy(self.base)

    def write(self, snap=None, name="snap.json"):
        p = Path(self.tmp.name) / name
        p.write_text(json.dumps(self.snap if snap is None else snap), encoding="utf-8")
        return p

    def check(self, snap=None, clone=True):
        rc, out, _ = run("check", "--snapshot", self.write(snap), "--manifest", MANIFEST, *(["--clone-root", self.root] if clone else []))
        return rc, out.split()

    def repo(self, name): return next(r for r in self.snap["repos"] if r["name"] == name)


class TestExitCodesAndSchema(unittest.TestCase):  # CL-1
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.snap = jload("snapshot-2026-10-13.json")

    def write(self, obj, name="s.json"):
        p = Path(self.tmp.name) / name
        p.write_text(obj if isinstance(obj, str) else json.dumps(obj), encoding="utf-8")
        return p

    def check(self, snap, man=MANIFEST):
        rc, out, _ = run("check", "--snapshot", self.write(snap), "--manifest", man)
        return rc, out.split()

    def test_valid_snapshots_exit_0(self):
        for name in ("snapshot-2026-10-13.json", "snapshot-read-only.json"):
            self.assertEqual(run("check", "--snapshot", FX / name, "--manifest", MANIFEST)[0:2], (0, "OK\n"), name)

    def test_severity_key_is_rejected_at_any_depth(self):
        for path in ([], ["hub"], ["hub", "liveness_refs", 0], ["repos", 3, "workflows", "runs", 0]):
            for key in ("severity", "Severity"):
                s = copy.deepcopy(self.snap)
                o = s
                for k in path:
                    o = o[k]
                o[key] = "HIGH"
                self.assertEqual(self.check(s), (1, ["E_SEVERITY_KEY"]), (path, key))

    def test_schema_allowlist_types_and_required_keys(self):
        def drop(s): del s["hub"]
        cases = [lambda s: s.update(extra=1), lambda s: s["repos"][0].update(note="x"), lambda s: s["repos"][2]["tip"].update(sha="not-a-sha"),
                 lambda s: s.update(run_date="13/10/2026"), lambda s: s.update(schema="fleet-triage/2"), lambda s: s.update(execution_mode="MAYBE"), drop]
        for i, mut in enumerate(cases):
            s = copy.deepcopy(self.snap)
            mut(s)
            self.assertEqual(self.check(s), (1, ["E_SCHEMA"]), i)

    def test_caps_are_rejected_with_a_cap_code(self):
        s = copy.deepcopy(self.snap)
        s["repos"][3]["prs"]["deep_reads"] = 6
        rc, codes = self.check(s)
        self.assertEqual((rc, [c.split(":")[0] for c in codes]), (1, ["E_CAP"]))

    def test_not_json_is_a_schema_code_and_unreadable_input_cannot_run(self):
        self.assertEqual(self.check("{ not json"), (1, ["E_SCHEMA"]))
        self.assertEqual(self.check([1, 2]), (1, ["E_SCHEMA"]))
        rc, out, _ = run("check", "--snapshot", Path(self.tmp.name) / "missing.json", "--manifest", MANIFEST)
        self.assertEqual((rc, out.split()), (2, ["E_RUN"]))
        bad = self.write(": : [", "bad.yml")
        self.assertEqual(run("check", "--snapshot", FX / "snapshot-2026-10-13.json", "--manifest", bad)[0:2], (2, "E_RUN\n"))
        self.assertEqual(run("check", "--snapshot", FX / "snapshot-2026-10-13.json", "--manifest", self.write("repos: 3", "m.yml"))[0], 2)

    def test_usage_errors_exit_2(self):
        snap, man = FX / "snapshot-2026-10-13.json", MANIFEST
        for args in ([], ["frobnicate"], ["check"], ["check", "--snapshot", snap], ["render", "--snapshot", snap], ["heartbeat"],
                     ["check", "--snapshot", snap, "--manifest", man, "--bogus"], ["render", "--snapshot", snap, "--manifest", man, "--clone-root", "x", "--backlog-dir", "y"],
                     ["render", "--unavailable", "not a code"], ["render", "--unavailable", "E_x"], ["heartbeat", "--repo-root", ".", "--today", "2026-13-40"]):
            rc, out, _ = run(*args)
            self.assertEqual((rc, out), (2, ""), args)

    def test_c3_only_on_validate_exit_1_and_exit_2_renders_e_run(self):
        def render(code):
            s = copy.deepcopy(self.snap)
            s["hub"]["validate_exit"] = code
            rc, out, _ = run("render", "--snapshot", self.write(s), "--manifest", MANIFEST, "--backlog-dir", FX / "backlogs")
            self.assertEqual(rc, 0)
            return out
        self.assertNotIn("Control plane invalid", render(0))
        self.assertIn("Control plane invalid: run validate.py and fix the reported check", render(1))
        out2 = render(2)
        self.assertNotIn("Control plane invalid", out2)
        self.assertIn("E_RUN", out2)
        self.assertNotIn("E_RUN", render(0))


class TestSecretsAndPaths(World):  # CL-2
    def subject(self, text):
        self.repo("DreamToosa")["tip"]["subject"] = text
        return self.check(clone=False)

    def test_secret_patterns_are_rejected(self):
        for secret in SECRETS:
            self.assertEqual(self.subject("synthetic note " + secret), (1, ["E_SECRET"]), secret[:6])

    def test_absolute_and_in_clone_paths_are_rejected(self):
        for p in ("/home/user/x", "~/notes", "C:\\Users\\x", "D:/work"):
            self.assertEqual(self.subject(p), (1, ["E_ABS_PATH"]), p)
        self.repo("DreamToosa")["tip"]["subject"] = f"synthetic see {self.root}/AgToosa/file"
        self.assertEqual(self.check(), (1, ["E_ABS_PATH"]))


class TestVerifyGit(World):  # CL-3
    def test_baseline_passes(self):
        self.assertEqual(self.check(), (0, ["OK"]))

    def test_each_git_fact_is_rederived(self):
        def ref_date(s): s["hub"]["liveness_refs"][0]["last_run_date"] = "2026-09-19"
        def ref_fake(s): s["hub"]["liveness_refs"].append({"ref": "origin/dreamtoosa/report-nope", "last_run_date": "2026-09-18"})
        def ref_bad(s): s["hub"]["liveness_refs"].append({"ref": "refs/heads/evil", "last_run_date": "2026-09-18"})
        cases = {"tip_sha": lambda s: s["repos"][0]["tip"].update(sha="ab" * 20),
                 "committer_date": lambda s: s["repos"][1]["tip"].update(committer_date="2026-10-10T08:31:00+00:00"),
                 "prev_committer_date": lambda s: s["repos"][1]["tip"].update(prev_committer_date=None),
                 "fix_links": lambda s: s["repos"][0]["fix_links"].append({"issue": 99, "sha": s["repos"][0]["tip"]["sha"]}),
                 "liveness": ref_date}
        for field, mut in cases.items():
            s = copy.deepcopy(self.snap)
            mut(s)
            self.assertEqual(self.check(s), (1, [f"E_VERIFY_GIT:{field}"]), field)
        s = copy.deepcopy(self.snap)
        ref_fake(s)
        self.assertEqual(self.check(s), (1, ["E_VERIFY_GIT:liveness"]))
        s = copy.deepcopy(self.snap)
        ref_bad(s)  # a ref name outside origin/main and origin/dreamtoosa/report-* never reaches git or the report
        self.assertEqual(self.check(s), (1, ["E_SCHEMA"]))
        s = copy.deepcopy(self.snap)
        s["repos"][0]["fix_links"] = []  # a real fix link the snapshot left out is a mismatch too
        self.assertEqual(self.check(s), (1, ["E_VERIFY_GIT:fix_links"]))

    def test_same_instant_in_another_notation_passes(self):
        self.repo("Crapsino")["tip"]["committer_date"] = "2026-10-10T08:30:00Z"
        self.repo("miToosa")["tip"]["committer_date"] = "2026-10-12T07:30:00+02:00"
        self.assertEqual(self.check(), (0, ["OK"]))

    def test_backlog_blob_sha_is_checked_when_present(self):
        for s in self.snap["repos"]:
            path = {"AgToosa": "docs/Master-Plan.md", "Crapsino": "docs/PLAN.md", "DreamToosa": "Docs/Master-Plan.md", "miToosa": "docs/Master-Plan.md"}[s["name"]]
            s["backlog_blob"] = git(self.root / s["name"], "rev-parse", f"{s['tip']['sha']}:{path}")
        self.assertEqual(self.check(), (0, ["OK"]))
        self.repo("miToosa")["backlog_blob"] = "cd" * 20
        self.assertEqual(self.check(), (1, ["E_VERIFY_GIT:backlog_blob"]))

    def test_missing_clone_is_a_code(self):
        (self.root / "Crapsino").rename(self.root / "Crapsino.away")
        self.addCleanup(lambda: (self.root / "Crapsino.away").rename(self.root / "Crapsino"))
        self.assertEqual(self.check(), (1, ["E_VERIFY_GIT:clone"]))

    def test_verify_git_is_callable_with_the_documented_signature(self):
        self.assertEqual(tr.verify_git(self.snap, self.root), [])
        self.repo("AgToosa")["tip"]["sha"] = "ab" * 20
        self.assertEqual(tr.verify_git(self.snap, self.root), ["E_VERIFY_GIT:tip_sha"])


class TestIntegrity(World):  # CL-4
    def restore(self):
        git(self.hub, "checkout", "-q", "--", "dreamtoosa/")
        git(self.hub, "clean", "-q", "-fd", "--", "dreamtoosa/")

    def test_clean_hub_passes_and_changes_outside_dreamtoosa_are_ignored(self):
        (self.hub / "reports").mkdir(exist_ok=True)
        (self.hub / "reports" / "dream-report.md").write_text("synthetic\n", encoding="utf-8")
        self.addCleanup(lambda: (self.hub / "reports" / "dream-report.md").unlink())
        self.assertEqual(self.check(), (0, ["OK"]))

    def test_modified_tracked_file_fails_before_the_engine_runs(self):
        self.addCleanup(self.restore)
        (self.hub / "dreamtoosa" / "state.json").write_text('{"last_run": {"date": "2026-10-13"}}', encoding="utf-8")
        self.assertEqual(self.check(), (1, [TAMPER]))
        bad = copy.deepcopy(self.snap)
        bad["severity"] = "HIGH"
        self.assertEqual(self.check(bad), (1, [TAMPER]))  # the engine never looked at the snapshot

    def test_untracked_file_fails(self):
        self.addCleanup(self.restore)
        (self.hub / "dreamtoosa" / "evil.py").write_text("print(1)\n", encoding="utf-8")
        self.assertEqual(self.check(), (1, [TAMPER]))

    def test_render_refuses_and_leaves_the_index_alone(self):
        self.addCleanup(self.restore)
        (self.hub / "dreamtoosa" / "evil.py").write_text("print(1)\n", encoding="utf-8")
        idx = Path(self.tmp.name) / "index.md"
        idx.write_text("# Index\n", encoding="utf-8")
        rc, out, _ = run("render", "--snapshot", self.write(), "--manifest", MANIFEST, "--clone-root", self.root, "--inject", idx)
        self.assertEqual((rc, out.split(), idx.read_text(encoding="utf-8")), (1, [TAMPER], "# Index\n"))

    def test_a_hub_that_is_not_a_git_repo_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "DreamToosa" / "dreamtoosa").mkdir(parents=True)
            rc, out, _ = run("check", "--snapshot", self.write(), "--manifest", MANIFEST, "--clone-root", t)
        self.assertEqual((rc, out.split()), (1, [TAMPER]))

    def test_the_snapshot_flag_from_phase_1_5_is_honoured(self):
        self.snap["hub"]["engine_clean"] = False
        self.assertEqual(self.check(clone=False), (1, [TAMPER]))


class TestEngineIsNotImportedWhenTampered(unittest.TestCase):  # CL-4: the integrity check precedes the import of triage.py
    def run_in_place(self, tamper):
        """Copy both modules into a throw-away hub, commit them, optionally booby-trap triage.py, and run the hub's own copy of the script."""
        with tempfile.TemporaryDirectory() as t:
            hub, marker = Path(t) / "DreamToosa", Path(t) / "ran"
            init(hub)
            src = {n: (ROOT / "dreamtoosa" / n).read_text(encoding="utf-8") for n in ("triage_report.py", "triage.py")}
            trap = f"\nopen({str(marker)!r}, 'w').close()\n"  # appended: from __future__ must stay first
            commit(hub, {f"dreamtoosa/{n}": (body + trap if n == "triage.py" and not tamper else body) for n, body in src.items()}, "synthetic", "2026-10-01T00:00:00+00:00")
            if tamper:
                (hub / "dreamtoosa" / "triage.py").write_text(src["triage.py"] + trap, encoding="utf-8")
            r = subprocess.run([sys.executable, str(hub / "dreamtoosa" / "triage_report.py"), "check", "--snapshot", FX / "snapshot-2026-10-13.json", "--manifest", MANIFEST,
                                "--clone-root", t], capture_output=True, text=True)
            return r.returncode, r.stdout.split(), marker.exists()

    def test_a_modified_triage_py_is_refused_and_never_executed(self):
        self.assertEqual(self.run_in_place(tamper=True), (1, [TAMPER], False))

    def test_the_control_run_does_execute_a_committed_triage_py(self):  # so the check above is not vacuous
        rc, out, ran = self.run_in_place(tamper=False)
        self.assertTrue(ran)
        self.assertEqual(rc, 1)  # the engine ran, then git re-derivation rejected the missing clones and refs
        self.assertTrue(out and all(c.startswith("E_VERIFY_GIT:") for c in out), out)


def hb_repo(root, dates, max_age=None):
    """A hub repo whose origin/* refs carry the given last_run.date values; its repos.yml sets heartbeat_max_age_days."""
    init(root)
    man = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    if max_age is not None:
        man["triage"]["heartbeat_max_age_days"] = max_age
    base = commit(root, {"dreamtoosa/repos.yml": yaml.safe_dump(man), "dreamtoosa/state.json": json.dumps({"last_run": {"date": "2000-01-01"}})},
                  "synthetic base", "2026-01-01T00:00:00+00:00")
    for ref, date in dates.items():
        git(root, "checkout", "-q", "-B", "tmp", base)
        sha = commit(root, {"dreamtoosa/state.json": json.dumps({"last_run": {"date": date}})}, "synthetic state " + ref, "2026-01-02T00:00:00+00:00")
        git(root, "update-ref", f"refs/remotes/{ref}", sha)
    git(root, "checkout", "-q", "-B", "main", base)
    return root


class TestHeartbeat(unittest.TestCase):  # CL-5
    def hb(self, dates, today=TODAY, max_age=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = hb_repo(Path(tmp.name) / "hub", dates, max_age)
        rc, out, _ = run("heartbeat", "--repo-root", repo, *(["--today", today] if today else []))
        return rc, out.split()

    def test_three_days_passes_and_four_fails(self):
        self.assertEqual(self.hb({"origin/main": day(3)}), (0, ["OK", "ref=origin/main", "age_days=3", "max_days=3"]))
        self.assertEqual(self.hb({"origin/main": day(4)}), (1, ["E_STALE", "ref=origin/main", "age_days=4", "max_days=3"]))

    def test_the_newest_ref_wins_across_main_and_report_branches(self):
        rc, out = self.hb({"origin/main": "2026-09-18", "origin/dreamtoosa/report-a": day(1), "origin/dreamtoosa/report-b": day(9)})
        self.assertEqual((rc, out[:3]), (0, ["OK", "ref=origin/dreamtoosa/report-a", "age_days=1"]))

    def test_manifest_threshold_is_used_and_bounded(self):
        self.assertEqual(self.hb({"origin/main": day(4)}, max_age=5)[0], 0)
        self.assertEqual(self.hb({"origin/main": day(6)}, max_age=5)[0], 1)
        for bad in (0, 15, "3", True):
            self.assertEqual(self.hb({"origin/main": day(1)}, max_age=bad), (2, ["E_RUN"]), bad)

    def test_not_evaluable_exits_1(self):
        self.assertEqual(self.hb({}), (1, ["E_NOT_EVALUABLE"]))
        self.assertEqual(self.hb({"origin/main": "garbage"}), (1, ["E_NOT_EVALUABLE"]))

    def test_future_dated_ref_exits_1_even_when_another_ref_is_fresh(self):
        self.assertEqual(self.hb({"origin/main": day(0), "origin/dreamtoosa/report-x": "2026-10-15"}), (1, ["E_FUTURE_DATED"]))
        self.assertEqual(self.hb({"origin/main": "2026-10-14"}), (0, ["OK", "ref=origin/main", "age_days=0", "max_days=3"]))  # RUN_DATE + 1 is accepted

    def test_default_today_is_the_utc_date_and_usage_errors_exit_2(self):
        now = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        self.assertEqual(self.hb({"origin/main": now}, today=None)[0], 0)
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(run("heartbeat", "--repo-root", t, "--today", TODAY)[0], 2)  # not a git repository
            self.assertEqual(run("heartbeat", "--repo-root", Path(t) / "missing")[0], 2)


class TestScriptMode(World):  # CL-6
    def test_runs_by_absolute_path_from_any_cwd_and_ignores_a_hostile_triage_module(self):
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "triage.py").write_text("raise SystemExit(99)\n", encoding="utf-8")
            (Path(t) / "yaml.py").write_text("raise SystemExit(98)\n", encoding="utf-8")
            rc, out, err = run("check", "--snapshot", self.write(), "--manifest", MANIFEST, "--clone-root", self.root, cwd=t)
        self.assertEqual((rc, out), (0, "OK\n"), err)

    def test_documented_help_runs(self):
        self.assertEqual(run("--help")[0], 0)


class TestLoadFromGit(World):  # CL-7
    def advance(self, name, files, remove=(), msg="synthetic change"):
        """Commit on top of the clone's origin/main (same committer date), patch the snapshot to the new tip; the clone is restored after the test."""
        d = self.root / name
        old = git(d, "rev-parse", "HEAD")
        self.addCleanup(lambda: (git(d, "reset", "-q", "--hard", old), git(d, "update-ref", "refs/remotes/origin/main", old)))
        for rel in remove:
            git(d, "rm", "-q", rel)
        sha = commit(d, files, msg, self.repo(name)["tip"]["committer_date"])
        git(d, "update-ref", "refs/remotes/origin/main", sha)
        self.repo(name)["tip"].update(sha=sha, prev_committer_date=git(d, "log", "-2", "--format=%cI", sha).splitlines()[1])

    def render(self, *flags):
        rc, out, err = run("render", "--snapshot", self.write(), "--manifest", MANIFEST, *flags)
        self.assertEqual(rc, 0, err)
        return out

    def test_clone_root_reproduces_backlog_cron_and_fix_links(self):
        man = tr.load_manifest(MANIFEST)
        rows, links, cron = tr.gather(self.snap, man, clone_root=self.root)
        rows2, links2, cron2 = tr.gather(self.snap, man, backlog_dir=FX / "backlogs")  # fixture files; cron from cron-2026-10-13.json beside them
        ag = "fixture-owner/AgToosa"
        self.assertEqual((rows, links), (rows2, links2))
        self.assertTrue(len(rows[ag]) and links[ag] == [{"issue": 11, "sha": self.repo("AgToosa")["tip"]["sha"]}])
        self.assertEqual(cron[ag], {"security-scan.yml": "23 4 * * 1"})  # only security-kind watch workflows are read
        self.assertEqual(cron[ag]["security-scan.yml"], cron2[ag]["security-scan.yml"])
        self.assertEqual(self.render("--clone-root", self.root), self.render("--backlog-dir", FX / "backlogs"))

    def test_rows_come_from_the_tip_not_from_the_snapshot_or_the_working_tree(self):
        text = (FX / "backlogs" / "mitoosa.md").read_text(encoding="utf-8").replace(
            "| BL-104 |", "| BL-777 | synthetic new data loss at src/x.py:1 | Fix | S | EP-1 | P0 | Todo |\n| BL-104 |")
        self.advance("miToosa", {"docs/Master-Plan.md": text})
        (self.root / "miToosa" / "docs" / "Master-Plan.md").write_text("working tree edits are ignored\n", encoding="utf-8")
        self.assertIn("BL-777", self.render("--clone-root", self.root))
        self.assertNotIn("BL-777", self.render("--backlog-dir", FX / "backlogs"))

    def test_fix_links_come_from_git_history(self):
        self.advance("miToosa", {"x.txt": "1"}, msg="synthetic resolves #31, closes #32, prefixes #33, see #34")
        _, links, _ = tr.gather(self.snap, tr.load_manifest(MANIFEST), clone_root=self.root)
        sha = self.repo("miToosa")["tip"]["sha"]
        self.assertEqual(links["fixture-owner/miToosa"], [{"issue": 31, "sha": sha}, {"issue": 32, "sha": sha}])

    def test_a_repo_without_a_backlog_file_is_not_evaluable_not_an_error(self):
        self.advance("miToosa", {}, remove=["docs/Master-Plan.md"])
        out = self.render("--clone-root", self.root)
        self.assertIn("miToosa backlog: not evaluable", out)
        self.assertNotIn("BL-101", out)


class TestManifestCompatibility(unittest.TestCase):  # guards schema drift between the fixture manifest and the real repos.yml
    REAL = ROOT / "dreamtoosa" / "repos.yml"

    def test_real_manifest_loads_through_the_cli_accessors(self):
        man = tr.load_manifest(self.REAL)
        repos = tr.enabled(man)
        self.assertEqual([m["repo"] for m in repos], ["sky2464/AgToosa", "sky2464/Crapsino", "sky2464/DreamToosa", "sky2464/miToosa"])
        self.assertTrue(all(isinstance(m.get("backlog"), dict) and m.get("product_workflows") for m in repos))
        self.assertEqual({m["repo"]: m["visibility"] for m in repos}, {"sky2464/AgToosa": "public", "sky2464/Crapsino": "private",
                                                                       "sky2464/DreamToosa": "public", "sky2464/miToosa": "public"})
        self.assertEqual(tr.hub_dir(man, "/x"), Path("/x/DreamToosa"))
        for m in repos:  # every real backlog mapping parses the synthetic backlog text without raising
            text = (FX / "backlogs" / (m["repo"].split("/")[1].lower() + ".md")).read_text(encoding="utf-8")
            self.assertIsInstance(tr.engine().parse_backlog(text, m["backlog"]), list)

    def test_check_snapshot_runs_on_the_synthetic_snapshot_against_the_real_manifest(self):
        man = tr.load_manifest(self.REAL)
        snap = jload("snapshot-2026-10-13.json")
        self.assertIsInstance(tr.engine().check_snapshot(snap, man), list)  # fixture owner differs, so repos are missing: codes, never a raise
        remapped = json.loads(json.dumps(snap).replace("fixture-owner/", "sky2464/"))
        self.assertEqual(tr.engine().check_snapshot(remapped, man), [])
        self.assertEqual(tr.check_all(remapped, man), [])
        ev = tr.engine().evaluate(remapped, {}, {}, {}, man)
        self.assertEqual([f["repo"] for f in ev.freshness], [m["repo"] for m in tr.enabled(man)])


if __name__ == "__main__":
    unittest.main()

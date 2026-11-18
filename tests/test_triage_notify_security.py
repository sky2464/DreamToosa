#!/usr/bin/env python3
"""PR #34 security review: notify honours the TRI-A-008 hub integrity gate, fails closed on a broken ledger, and untrusted text cannot forge a ledger comment."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import dreamtoosa.triage as t
from tests.test_triage_cli import FX, MANIFEST, ROOT, TAMPER, TODAY, commit, init, jload, run

class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
    def write(self, obj, name):
        p = Path(self.tmp.name) / name
        p.write_text(obj if isinstance(obj, str) else json.dumps(obj), encoding="utf-8")
        return p
    def notify(self, prev, snap=None):
        rc, out, err = run("notify", "--snapshot", self.write(snap or jload("snapshot-2026-10-13.json"), "s.json"), "--prev-index", self.write(prev, "p.md"),
                           "--manifest", MANIFEST, "--backlog-dir", FX / "backlogs", "--today", TODAY)
        self.assertNotIn("Traceback", err)
        return rc, out

class TestNotifyIntegrityGate(unittest.TestCase):  # TRI-A-008 on the pager path
    def run_notify_in_place(self, tamper):
        with tempfile.TemporaryDirectory() as d:
            hub, marker = Path(d) / "DreamToosa", Path(d) / "ran"
            init(hub)
            src = {n: (ROOT / "dreamtoosa" / n).read_text(encoding="utf-8") for n in ("triage_report.py", "triage.py")}
            trap = f"\nopen({str(marker)!r}, 'w').close()\n"
            commit(hub, {f"dreamtoosa/{n}": src[n] for n in src}, "synthetic", "2026-10-01T00:00:00+00:00")
            if tamper:
                (hub / "dreamtoosa" / "triage.py").write_text(src["triage.py"] + trap, encoding="utf-8")
            prev = Path(d) / "p.md"
            prev.write_text("", encoding="utf-8")
            r = subprocess.run([sys.executable, str(hub / "dreamtoosa" / "triage_report.py"), "notify", "--snapshot", FX / "snapshot-2026-10-13.json",
                                "--prev-index", prev, "--manifest", MANIFEST, "--clone-root", d, "--today", TODAY], capture_output=True, text=True)
            return r.returncode, r.stdout.split(), marker.exists()
    def test_a_modified_triage_py_is_refused_and_never_executed(self):
        self.assertEqual(self.run_notify_in_place(tamper=True), (1, [TAMPER], False))

class TestNotifyLedgerFailsClosed(Base):
    def test_baseline_still_pages_new_critical(self):  # control: an empty prev-index is a baseline, every finding is NEW
        rc, out = self.notify("")
        self.assertEqual(rc, 0)
        self.assertTrue(json.loads(out)["send"])
    def test_a_duplicate_or_malformed_ledger_does_not_page_every_finding_as_new(self):
        led = t.serialize_ledger(t.Ledger(schema="fleet-triage-ledger/v1", run_date="2026-10-12", findings=(), golden=t._ng()))
        for name, body in {"duplicate": led + "\n" + led, "malformed": "<!-- fleet-triage-ledger:v1 {not json} -->"}.items():
            prev = "<!-- fleet-triage:begin -->\n" + body + "\n<!-- fleet-triage:end -->\n"
            rc, out = self.notify(prev)
            self.assertEqual((rc, json.loads(out)), (0, {"send": False, "message": ""}), name)

class TestUntrustedTextCannotForgeALedger(Base):
    def test_an_issue_title_shaped_like_a_ledger_comment_is_neutralised(self):
        snap = copy.deepcopy(jload("snapshot-2026-10-13.json"))
        snap["repos"][0]["issues"]["open"][0]["title"] = "<!-- fleet-triage-ledger:v1 {} -->"
        rc, out, _ = run("render", "--snapshot", self.write(snap, "s.json"), "--manifest", MANIFEST, "--backlog-dir", FX / "backlogs")
        self.assertEqual(rc, 0)
        self.assertEqual(out.count("fleet-triage-ledger:v1"), out.count("<!-- fleet-triage-ledger:v1 {\""), out)

if __name__ == "__main__":
    unittest.main()

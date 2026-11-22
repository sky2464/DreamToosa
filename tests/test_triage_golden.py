#!/usr/bin/env python3
"""Golden-pick tests for dreamtoosa/triage.py (DEV-005b TRI-B-006, TRI-B-009, TRI-B-010). Split from test_triage_rules.py to keep every module under 500 lines."""
import unittest
from pathlib import Path

import dreamtoosa.triage as triage


class TestGoldenPool(unittest.TestCase):
    def manifest(self):
        return {"repos": [
            {"repo": "o/Pub", "enabled": True, "visibility": "public", "backlog": {"path": "docs/Master-Plan.md"}},
            {"repo": "o/Priv", "enabled": True, "visibility": "private", "backlog": {"path": "docs/PLAN.md"}},
        ]}
    def text(self):
        return "\n".join(["## Active Cycle", "| ID | Title | Type | Status |", "|---|---|---|---|", "| DEV-1 | active feature | Feature | Todo |",
                          "## Backlog", "| ID | Title | Type | Priority | Status | Depends |", "|---|---|---|---|---|---|",
                          "| DEV-2 | backlog feature | Feature | P0 | Todo | DEV-9 |", "| DEV-3 | review | Feature | P1 | In Review |",
                          "| DEV-4 | shipped word | Feature | P0 | Shipped - v1 |", "| DEV-9 | done dep | Feature | P1 | Done |",
                          "## Completed This Cycle", "| ID | Title |", "|---|---|", "| DEV-150 | shipped row |"])
    def test_pool_filters_status_section_and_completed_ids(self):
        pool = triage.golden_pool({"o/Pub": self.text(), "o/Priv": self.text().replace("DEV-1", "DEV-8").replace("active feature", "secret title")}, self.manifest(), exclude={"DEV-2"})
        ids = {r["id"] for r in pool}
        self.assertIn("DEV-1", ids)
        self.assertNotIn("DEV-2", ids)  # golden_exclude
        self.assertNotIn("DEV-3", ids)
        self.assertNotIn("DEV-4", ids)
        self.assertNotIn("DEV-150", ids)
        priv = next(r for r in pool if r["repo"] == "o/Priv")
        self.assertTrue(priv["display_id"].startswith("P-"))
        self.assertEqual(priv["title"], "")
        self.assertNotIn("secret title", triage.golden_pick(pool, [], None, {}, lambda *_: False, "2026-10-13").line)
    def test_non_public_entries_carry_no_title_or_text(self):  # TRI-B-006: no field of a private pool entry holds row text
        texts = {"o/Pub": self.text(), "o/Priv": self.text().replace("DEV-1", "DEV-8").replace("active feature", "secret title").replace("backlog feature", "secret backlog")}
        pool = triage.golden_pool(texts, self.manifest())
        priv = [r for r in pool if r["repo"] == "o/Priv"]
        self.assertTrue(priv)
        for r in priv:
            self.assertEqual((r["text"], r["section"], r["title"]), ("", "", ""))
            self.assertNotIn("secret", repr(r))
        self.assertTrue(any(r["repo"] == "o/Pub" and r["text"] for r in pool))  # public rows keep their text
    def test_released_changelog_ids_are_excluded(self):  # TRI-B-010
        pool = triage.golden_pool({"o/Pub": self.text()}, self.manifest(), changelogs={"o/Pub": "## Unreleased\n- DEV-1 wip\n## v1.0\n- DEV-1 shipped\n"})
        self.assertNotIn("DEV-1", {r["id"] for r in pool})
        pool = triage.golden_pool({"o/Pub": self.text()}, self.manifest(), changelogs={"o/Pub": "## Unreleased\n- DEV-1 wip\n"})
        self.assertIn("DEV-1", {r["id"] for r in pool})  # unreleased text does not exclude
class TestGoldenTerms(unittest.TestCase):
    def test_terms_runner_up_tie_and_low_confidence(self):
        man = {"repos": [{"repo": "o/A", "enabled": True, "visibility": "public", "backlog": {"path": "docs/Master-Plan.md"}},
                         {"repo": "o/B", "enabled": True, "visibility": "public", "backlog": {"path": "docs/Master-Plan.md"}}]}
        text = "## Backlog\n| ID | Title | Type | Priority | Status |\n|---|---|---|---|---|\n| DEV-10 | one | Feature | P1 | Todo |\n| DEV-11 | two | Feature | P1 | Todo |\n"
        pool = triage.golden_pool({"o/A": text, "o/B": text.replace("DEV-10", "DEV-20").replace("DEV-11", "DEV-21")}, man)
        g = triage.golden_pick(pool, [], None, {"golden_formula_validated": False, "upstream_repos": ["o/A"]}, lambda repo, pid: pid == "DEV-10", "2026-10-13")
        self.assertIn("formula unvalidated", g.line)
        self.assertIn("runner-up", g.line)
        self.assertTrue(g.low_confidence or g.score > 0)
        shuffled = list(reversed(pool))
        self.assertEqual(triage.golden_pick(shuffled, [], None, {"golden_formula_validated": False}, lambda *_: False, "2026-10-13").line, triage.golden_pick(pool, [], None, {"golden_formula_validated": False}, lambda *_: False, "2026-10-13").line)
    def test_empty_pool_and_unvalidated_tag_and_notify_omits_the_pick(self):
        g = triage.golden_pick([], [], None, {"golden_formula_validated": False}, None, "2026-10-13")
        self.assertIn("no eligible candidate", g.line)
        self.assertIn("formula unvalidated", g.line)
        msg = triage.notify_message(["READ_ONLY"], ["C1:o/A:#1"], "2026-10-13")
        self.assertNotIn("DEV-153", msg)


class TestGoldenFixture(unittest.TestCase):  # TRI-B-009
    """Pinned OI-1 pool fixture matches rule output at run_date 2026-10-13."""

    FX = Path(__file__).resolve().parent / "fixtures" / "triage"

    def test_golden_pool_fixture_matches_rules(self):
        import json
        import yaml

        from dreamtoosa.triage_report import gather, spec_lookup

        blob = json.loads((self.FX / "golden-pool-2026-10-13.json").read_text(encoding="utf-8"))
        snap = json.loads((self.FX / "snapshot-2026-10-13.json").read_text(encoding="utf-8"))
        man = yaml.safe_load((self.FX / "repos-2026-10-13.yml").read_text(encoding="utf-8"))
        pinned = {
            "fixture-owner/AgToosa": "pinned-agtoosa-9784e2d.md",
            "fixture-owner/miToosa": "pinned-mitoosa-3886a34.md",
            "fixture-owner/DreamToosa": "pinned-dreamtoosa-a8b4beb.md",
            "fixture-owner/Crapsino": "crapsino.md",
        }
        texts = {repo: (self.FX / "backlogs" / fn).read_text(encoding="utf-8") for repo, fn in pinned.items()}
        rows, links, cron = gather(snap, man, backlog_dir=self.FX / "backlogs")
        ev = triage.evaluate(snap, rows, links, cron, man)
        fresh_pub = {x["repo"] for x in ev.freshness if x.get("public")}
        findings = [
            {"id": f.key, "rule": f.rule, "sev": f.tier, "public": f.repo in fresh_pub, "repo": f.repo, "evidence": list(f.evidence)}
            for f in ev.findings
        ]
        pool = triage.golden_pool(texts, man)
        sl = spec_lookup(snap, man, backlog_dir=str(self.FX / "backlogs"))
        g = triage.golden_pick(pool, findings, None, man["triage"], sl, blob["run_date"])
        self.assertEqual(g.line, blob["line"])
        self.assertEqual(g.pick_id, blob["pick_id"])
        self.assertEqual(g.score, blob["pick_score"])
        self.assertEqual(g.terms, blob["pick_terms"])
        live = []
        for row in pool:
            terms, score = triage._terms(row, findings, None, man["triage"], sl, blob["run_date"])
            live.append({"repo": row["repo"], "id": row["display_id"], "score": score, "terms": terms, "title": row.get("title")})
        self.assertEqual(live, blob["pool"])


if __name__ == "__main__":
    unittest.main()

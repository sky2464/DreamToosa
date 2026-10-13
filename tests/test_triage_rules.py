#!/usr/bin/env python3
"""Rule tests for dreamtoosa/triage.py (DEV-005a TR-1..TR-16, FX-1). Red phase: triage.py does not exist yet.

CONTRACT the engine builds to. Dates are "YYYY-MM-DD"; age = whole days, run_date minus the date part of a timestamp as written (no tz math).
evaluate(snap, plan_rows, fix_links, cron, manifest): plan_rows {repo: [PlanRow]} (parse_backlog output); fix_links {repo: [{issue, sha}]};
  cron {repo: {workflow file: "m h dom mon dow" | None}}. Snapshot = spec 2.1 plus: prs.open[].created_at and .labels (C1b needs them);
  run.kind in product|security|sync|audit|dependabot (dependabot run.workflow = str(numeric id) from dynamic_ids); issue.closed_by_pr =
  None | [{number, merged_at}]; a non-draft PR with checks None was not deep-read. Section status "ok" | "not_evaluable" (+ reason).
PlanRow: id, title, priority, status (None when unmapped/absent), section (nearest heading text), line (1-based), text (raw row), p0, done.
check_snapshot codes: E_SEVERITY_KEY, E_SCHEMA, E_SECRET, E_ABS_PATH, E_CAP:<what>.
Evaluation (attribute or key access): mode; security (exact line); top_action (str|None); more (int, URGENT/HIGH not shown); counts {tier: n} over
  all findings; external {repo: int|None (None iff issues not evaluable)}; hub {age_days, source_ref, state OK|NOT_EVALUABLE};
  freshness [{repo, tier, age_days, tip_sha, public}] enabled repos in manifest order, public = manifest+snapshot visibility "public" and
  visibility_check "ok"; sections {repo: {prs|issues|workflows|backlog|dependabot|cron|hygiene: {state OK|NOT_EVALUABLE, reason}}} (hygiene
  adds merged_undeleted, label); prs [{repo, number, cls READY|BLOCKED|NOT_EVALUABLE, blocker, unblock, label, reason, idle_days}] sorted
  by (manifest order, number); ci [{repo, workflow, state GREEN|RED|GREEN_PRE_TIP|RED_PRE_TIP|NOT_EVALUABLE, streak, first_red, run_id}]
  for product workflows; findings (ranked) and shown (CRITICAL + capped URGENT/HIGH) are [Finding].
Finding: rule, key "<RULE>:<owner/repo>:<subject>", repo, tier, impact 2..5, confidence 1..3, age_days, action, evidence (sorted), tags, joined.
  Subjects: "#N", plan id, workflow file, liveness (C2), validate (C3), hub (U2), dependabot-updates (H6). Evidence: run:<id> issue:<n>
  pr:<n> commit:<sha7> plan:<path>:<line> state:<ref>. Tags: verify untracked unconfirmed close-candidate fix-link-unverified gated.
  age_days: days open (C1, U4, H5), idle (U3), since first red (U1, H1), oldest merged PR (H2), silent (H7), hub age (C2, U2), else 0.
  Rank: tier, impact desc, confidence desc, age_days desc, manifest repo order, key. Caps count URGENT/HIGH only (CRITICAL is uncapped).
Decisions pinned: PR red = conclusion outside success|neutral|skipped (None = pending); mergeable_state dirty = CONFLICT, unknown/None = MERGEABILITY-
  UNKNOWN, else fine; review state per login = latest of CHANGES_REQUESTED|APPROVED|DISMISSED (COMMENTED ignored); draft is checked first. CI ignores
  pull_request* runs; streak = consecutive push/schedule failures from the newest; state = newest completed run, preferring one on the tip. A trusted
  issue finding joins a same-repo CI/plan finding when its title cites the plan id or workflow file, or the plan row cites "#N" (exact token); the
  survivor keeps its own age and lists the issue key in joined. C1c = P0 not done, row has a keyword AND file:line; H4 = HIGH with file:line, else
  MEDIUM+gated. Evidence gate: URGENT/HIGH/CRITICAL without evidence become MEDIUM+gated. READ_ONLY (snapshot or hub.force_read_only) blanks prs/issues/
  workflows; freshness, plan rows and liveness still evaluate. hub_liveness skips malformed dates and dates after run_date+1; ties pick the smallest ref.
"""
import copy, dataclasses, datetime, json, random, re, unittest
from pathlib import Path

import yaml

import dreamtoosa.triage as triage

FX = Path(__file__).parent / "fixtures" / "triage"
RD = "2026-10-13"
AG, CR, DT, MI = (f"fixture-owner/{n}" for n in ("AgToosa", "Crapsino", "DreamToosa", "miToosa"))
UNBLOCK = {"DRAFT": "mark the PR ready for review", "CHECKS-RED": "fix the failing check on head {}", "NO-CI": "add a CI check to the PR",
           "CHECKS-PENDING": "wait for the checks on head {} to finish", "CONFLICT": "resolve the merge conflict with the default branch",
           "CHANGES-REQUESTED": "address the requested changes and request review again",
           "MERGEABILITY-UNKNOWN": "wait for GitHub to compute mergeability, then re-read"}
MAP = {"path": "x.md", "header_all": ["ID", "Title", "Priority", "Status"], "p0_values": ["P0"], "done_values": ["Done", "Shipped"],
       "columns": {"id": "ID", "title": "Title", "priority": "Priority", "status": "Status"}, "done_sections": ["Completed This Cycle"]}
SELF_LABEL, SECURITY_LINE = "ready to merge (GitHub forbids self-approval)", "not evaluable (alert APIs not exposed via MCP)"
# key -> (tier, impact, confidence, action, evidence | None), in the expected rank order of the 2026-10-13 fixture
BASE = {
    f"C1:{CR}:#55": ("CRITICAL", 5, 3, f"Review Dependabot PR #55 in {CR} (owner decision)", ["pr:55"]),
    f"C1:{MI}:#71": ("CRITICAL", 5, 3, f"Triage issue #71 in {MI}", ["issue:71"]),
    f"C1:{CR}:A1": ("CRITICAL", 5, 2, "A1: fix and add a regression test", None),
    f"C1:{MI}:BL-101": ("CRITICAL", 5, 2, "BL-101: fix and add a regression test", None),
    f"C2:{DT}:liveness": ("CRITICAL", 3, 3, "Dream Report dark 25 d: check the routine run log and re-authorize GitHub", ["state:origin/main"]),
    f"U4:{AG}:#14": ("URGENT", 4, 3, f"Resolve release-blocker issue #14 in {AG}", ["issue:14"]),
    f"U2:{DT}:hub": ("URGENT", 3, 3, "Hub degraded: heartbeat 25 d; 3 open report PRs", None),
    f"U1:{MI}:weekly-health.yml": ("URGENT", 3, 3, f"{MI}: weekly-health.yml red on tip for 3 runs since 2026-10-08", ["run:9301", "run:9303", "run:9304"]),
    f"U3:{DT}:#43": ("URGENT", 2, 3, f"Decide on PR #43 in {DT} (ready, idle 9 d)", ["pr:43"]),
    f"H5:{AG}:#12": ("HIGH", 4, 3, f"Triage bug #12 in {AG} (open 20 d)", ["issue:12"]),
    f"H5:{CR}:#61": ("HIGH", 4, 3, f"Triage bug #61 in {CR} (open 16 d)", ["issue:61"]),
    f"H4:{AG}:SYN-201": ("HIGH", 4, 2, "SYN-201: fix and add a test (verify)", None),
    f"H4:{CR}:TC1": ("HIGH", 4, 2, "TC1: fix and add a test (verify)", None),
    f"H4:{MI}:BL-102": ("HIGH", 4, 2, "BL-102: fix and add a test (verify)", None),
    f"H7:{AG}:security-scan.yml": ("HIGH", 3, 3, f"{AG}: security-scan.yml silent 25 d (interval 7 d)", ["run:9011"]),
    f"H2:{CR}:ci.yml": ("HIGH", 3, 3, "Gate bypass: PRs #50, #51 merged without a green check", ["pr:50", "pr:51"]),
    f"H1:{CR}:nightly-audit.yml": ("HIGH", 3, 3, f"{CR}: nightly-audit.yml failing on push for 3 runs", ["run:9111", "run:9113", "run:9114"]),
    f"H6:{DT}:dependabot-updates": ("HIGH", 2, 3, f"{DT}: Dependabot updates failing 3 runs; check the update configuration", ["run:9211", "run:9212", "run:9213"]),
    f"H4:{CR}:UX-R1": ("MEDIUM", 4, 2, "UX-R1: fix and add a test (verify)", None),
    f"H5:{AG}:#11": ("LOW", 4, 3, "Close candidate #11: fix fa000b1 on default branch", ["commit:fa000b1", "issue:11"]),
}


def g(o, k): return o[k] if isinstance(o, dict) else getattr(o, k)
def jload(n): return json.loads((FX / n).read_text(encoding="utf-8"))
def yload(n): return yaml.safe_load((FX / n).read_text(encoding="utf-8"))
def fake(n): return f"fa{n:05x}" + "0" * 33
def ck(*c): return [{"conclusion": x} for x in c]
def day(n, t="09:00:00"): return (datetime.date(2026, 10, 13) - datetime.timedelta(days=n)).isoformat() + f"T{t}Z"
def backlog_text(repo): return (FX / "backlogs" / (repo.split("/")[1].lower() + ".md")).read_text(encoding="utf-8")
def rows_for(man): return {r["repo"]: triage.parse_backlog(backlog_text(r["repo"]), r["backlog"]) for r in man["repos"]}
def plan_text(rows): return "## Backlog\n\n| ID | Title | Priority | Status |\n|--|--|--|--|\n" + "".join(f"| {i} | {t} | {p} | {s} |\n" for i, t, p, s in rows)
def mkrun(wf, concl, n, rid, kind="product", event="push", sha=None):
    return {"workflow": wf, "kind": kind, "event": event, "head_sha": sha or fake(0x7000 + rid), "conclusion": concl, "run_id": rid, "created_at": day(n)}
def mkissue(n, labels, age, title="synthetic issue", author="fixture-owner"):
    return {"number": n, "title": title, "labels": labels, "author": author, "created_at": day(age), "closed_by_pr": None}
def mkpr(n, **kw):
    return {"number": n, "draft": False, "author": "fixture-helper", "updated_at": day(1), "created_at": day(5), "labels": [], "head_sha": fake(0x5000 + n),
            "docs_only": False, "checks": ck("success"), "reviews": [], "mergeable_state": "clean", **kw}
def dump(ev):  # canonical JSON of an Evaluation of any shape (dataclass, namespace or dict)
    enc = lambda o: dataclasses.asdict(o) if dataclasses.is_dataclass(o) else sorted(o) if isinstance(o, (set, frozenset)) else vars(o)
    return json.dumps(ev, default=enc, sort_keys=True)
def shuffle_all(o, rng):
    for k, v in (o.items() if isinstance(o, dict) else enumerate(o) if isinstance(o, list) else []):
        if k != "reviews":  # review order is chronological and meaningful
            shuffle_all(v, rng)
    if isinstance(o, list):
        rng.shuffle(o)
# Table helpers: each returns a mutator taking the running test case `t`.
def edit(repo, kind, n, **kw): return lambda t: getattr(t, kind)(repo, n).update(kw)
def add_issue(repo, n, labels, age, **kw): return lambda t: t.R(repo)["issues"]["open"].append(mkissue(n, labels, age, **kw))
def scope(repo, val): return lambda t: [d.update(dependabot_scope=val) for d in (t.R(repo), t.M(repo))]
def u1_runs(*days): return lambda t: t.set_runs(MI, [mkrun("weekly-health.yml", "failure", d, 50 + i, sha=t.R(MI)["tip"]["sha"] if i == 0 else None) for i, d in enumerate(days)])
def h3_runs(): return lambda t: t.set_runs(MI, [mkrun("weekly-health.yml", "failure", 2, 60, sha=fake(0x3ff))])
def h7(cron, age):
    def mut(t):
        next(r for r in t.R(AG)["workflows"]["runs"] if r["workflow"] == "security-scan.yml")["created_at"] = day(age)
        t.cron[AG]["security-scan.yml"] = cron
    return mut
# (mutator | None, rule | None for any, repo, subject, expected tier | None for "no finding")
RULE_ROWS = (
    [(add_issue(MI, 73, [lab], 5), "C1", MI, "#73", "CRITICAL") for lab in ("security", "critical", "P0", "data-loss")]  # C1a labels
    + [(add_issue(MI, 73, ["bug"], 5), "C1", MI, "#73", None), (add_issue(MI, 73, ["P0"], 5), "U4", MI, "#73", None),  # P0 is C1, not also U4
       (edit(AG, "issue", 14, labels=["release-blocker", "P0"]), "U4", AG, "#14", None), (edit(AG, "issue", 14, labels=["release-blocker", "P0"]), "C1", AG, "#14", "CRITICAL"),
       (scope(CR, "dev"), "C1", CR, "#55", None), (edit(CR, "pr", 55, created_at=day(3)), "C1", CR, "#55", None),  # C1b: runtime, older than 3 d, Dependabot, security
       (edit(CR, "pr", 55, created_at=day(4)), "C1", CR, "#55", "CRITICAL"), (edit(CR, "pr", 55, author="fixture-helper"), "C1", CR, "#55", None),
       (edit(CR, "pr", 55, labels=["dependencies"]), "C1", CR, "#55", None),
       (edit(DT, "pr", 44, updated_at=day(7)), "U3", DT, "#44", None), (edit(DT, "pr", 44, updated_at=day(8)), "U3", DT, "#44", "URGENT"),  # U3: idle more than 7 d
       (edit(DT, "pr", 42, updated_at=day(9)), "U3", DT, "#42", "URGENT"), (edit(MI, "pr", 22, updated_at=day(30)), "U3", MI, "#22", None),  # self-authored counts; BLOCKED never
       (u1_runs(1), "U1", MI, "weekly-health.yml", None), (u1_runs(2), "U1", MI, "weekly-health.yml", None), (u1_runs(3), "U1", MI, "weekly-health.yml", "URGENT"),
       (u1_runs(1, 2), "U1", MI, "weekly-health.yml", "URGENT"),  # two consecutive failures, or red for at least 3 days
       (edit(AG, "issue", 12, created_at=day(14)), "H5", AG, "#12", None), (edit(AG, "issue", 12, created_at=day(15)), "H5", AG, "#12", "HIGH"),
       (None, "H5", AG, "#17", None), (None, "H5", AG, "#15", None), (None, "H5", AG, "#16", None),  # chore, untrusted author, status-needs-triage
       (lambda t: t.man["triage"]["trusted_logins"].append("fixture-stranger"), "H5", AG, "#15", "HIGH"),
       (lambda t: t.fix.update({AG: [{"issue": 99, "sha": fake(7)}]}), "H5", AG, "#11", "HIGH"),  # a fix link counts only for the issue it names
       (edit(AG, "issue", 12, closed_by_pr=[{"number": 9, "merged_at": day(2)}]), "H5", AG, "#12", "LOW"),  # merged closing PR verifies
       (edit(AG, "issue", 12, closed_by_pr=[{"number": 9, "merged_at": None}]), "H5", AG, "#12", "HIGH")]  # unmerged: annotated, tier unchanged
    + [(edit(AG, "issue", n, labels=["security", "release-blocker", "P0", "bug"] + ["status-needs-triage"] * (n == 16)), None, AG, f"#{n}", None) for n in (15, 16)]  # untrusted: never C1/U4/H5
    + [(None, None, r, s, None) for r, s in [(AG, "SYN-202"), (CR, "A7"), (CR, "TC9"), (MI, "BL-103"), (MI, "BL-105"), (MI, "BL-100")]]  # Done, done section, skipped tables
    + [(scope(DT, "dev"), "H6", DT, "dependabot-updates", "MEDIUM"), (scope(DT, "unknown"), "H6", DT, "dependabot-updates", "HIGH"),
       (None, "H6", CR, "dependabot-updates", None),  # an open Dependabot PR suppresses H6
       (lambda t: t.R(DT)["workflows"]["runs"].append(mkrun("88101", "success", 0, 9300, kind="dependabot", event="dynamic")), "H6", DT, "dependabot-updates", None),
       (lambda t: t.R(DT)["workflows"]["dynamic_ids"].clear(), "H6", DT, "dependabot-updates", None),
       (h7("23 4 * * 1", 14), "H7", AG, "security-scan.yml", None), (h7("23 4 * * 1", 15), "H7", AG, "security-scan.yml", "HIGH"),  # weekly: more than 14 d
       (h7("0 6 * * *", 2), "H7", AG, "security-scan.yml", None), (h7("0 6 * * *", 3), "H7", AG, "security-scan.yml", "HIGH"),  # daily: more than 2 d
       (h7("*/30 * * * *", 25), "H7", AG, "security-scan.yml", None), (h7(None, 25), "H7", AG, "security-scan.yml", None),  # unknown shape: not evaluable
       (lambda t: [r.update(created_at=day(40)) for r in t.R(AG)["workflows"]["runs"]], "H7", AG, "issues-sync.yml", None),  # sync kind never raises H7
       (lambda t: t.set_runs(CR, [r for r in t.R(CR)["workflows"]["runs"] if r["run_id"] != 9114]), "H1", CR, "nightly-audit.yml", None),  # only 2 failures left
       (None, "H3", MI, "weekly-health.yml", None), (h3_runs(), "H3", MI, "weekly-health.yml", "HIGH"), (h3_runs(), "U1", MI, "weekly-health.yml", None),  # H3: failure off the tip
       (lambda t: (h3_runs()(t), t.R(MI)["workflows"]["runs"].append(mkrun("weekly-health.yml", "success", 0, 61, sha=t.R(MI)["tip"]["sha"]))), "H3", MI, "weekly-health.yml", None)])


class Base(unittest.TestCase):
    def setUp(self):
        self.snap, self.man, self.cron = jload("snapshot-2026-10-13.json"), yload("repos-2026-10-13.yml"), jload("cron-2026-10-13.json")
        self.rows, self.fix = rows_for(self.man), {r["repo"]: r["fix_links"] for r in self.snap["repos"]}

    def R(self, repo): return next(r for r in self.snap["repos"] if r["repo"] == repo)
    def M(self, repo): return next(r for r in self.man["repos"] if r["repo"] == repo)
    def issue(self, repo, n): return next(i for i in self.R(repo)["issues"]["open"] if i["number"] == n)
    def pr(self, repo, n): return next(p for p in self.R(repo)["prs"]["open"] if p["number"] == n)
    def ev(self): return triage.evaluate(self.snap, self.rows, self.fix, self.cron, self.man)
    def set_runs(self, repo, runs): self.R(repo)["workflows"]["runs"][:] = runs
    def set_plan(self, repo, rows): self.rows[repo] = triage.parse_backlog(plan_text(rows), self.M(repo)["backlog"])
    def sec(self, ev, repo, name): s = g(ev, "sections")[repo][name]; return g(s, "state"), g(s, "reason")
    def has(self, *a): return bool(self.F(*a))

    def F(self, rule=None, repo=None, sub=None, ev=None):
        return [f for f in g(ev or self.ev(), "findings") if rule in (None, g(f, "rule")) and repo in (None, g(f, "repo"))
                and sub in (None, g(f, "key").split(":", 2)[2])]

    def one(self, rule, repo, sub, ev=None):
        fs = self.F(rule, repo, sub, ev)
        self.assertEqual(len(fs), 1, (rule, repo, sub))
        return fs[0]

    def liveness(self, age, count="keep"):
        self.snap["hub"]["liveness_refs"] = [{"ref": "origin/main", "last_run_date": day(age)[:10]}]
        if count != "keep":
            self.snap["hub"]["open_report_prs"] = count


class TestFixturesAndCheck(Base):  # FX-1, TR-14
    def test_synthetic_titles_fake_shas_and_manifest_values(self):
        titles = [r["tip"]["subject"] for r in self.snap["repos"]] + [g(x, "title") for rows in self.rows.values() for x in rows]
        titles += [i["title"] for r in self.snap["repos"] for i in r["issues"].get("open", [])]
        self.assertEqual([t for t in titles if not t.startswith("synthetic")], [])
        shas = set(re.findall(r"\b[0-9a-f]{40}\b", (FX / "snapshot-2026-10-13.json").read_text(encoding="utf-8")))
        self.assertTrue(shas and all(s.startswith("fa") for s in shas))
        self.assertEqual([r["visibility"] for r in self.man["repos"]], ["public", "private", "public", "public"])  # test-only values
        self.assertEqual((self.man["hub"]["force_read_only"], yload("repos-2026-10-13-readonly.yml")["hub"]["force_read_only"]), (False, True))

    def test_fixtures_are_valid_and_rejections_have_codes(self):  # fixtures sit exactly at the caps: 5 PR deep reads, 3 merged-PR reads, 3 issue reads
        self.assertEqual(triage.check_snapshot(self.snap, self.man), [])
        for mn in ("repos-2026-10-13.yml", "repos-2026-10-13-readonly.yml"):
            self.assertEqual(triage.check_snapshot(jload("snapshot-read-only.json"), yload(mn)), [])
        cases = [("E_SEVERITY_KEY", lambda s: s["repos"][0]["issues"]["open"][0].update(severity="HIGH")), ("E_SCHEMA", lambda s: s["repos"][3]["workflows"]["runs"][0].update(x=1)),
                 ("E_CAP", lambda s: (s["repos"][3]["prs"]["open"][6].update(checks=[]), s["repos"][3]["prs"].update(deep_reads=6))),
                 ("E_CAP", lambda s: s["repos"][1]["prs"]["closed_recent"][3].update(checks=[])), ("E_CAP", lambda s: s["repos"][0]["issues"]["open"][2].update(closed_by_pr=[]))]
        for code, mut in cases:
            s = copy.deepcopy(self.snap)
            mut(s)
            self.assertTrue(any(c.startswith(code) for c in triage.check_snapshot(s, self.man)), code)


class TestFacts(Base):  # TR-1 freshness, TR-2 pull requests, TR-3 CI
    def tier(self, age):
        self.R(MI)["tip"]["committer_date"] = day(age, "01:00:00").replace("Z", "+00:00")
        f = next(x for x in g(self.ev(), "freshness") if g(x, "repo") == MI)
        return g(f, "tier"), g(f, "age_days")

    def test_tiers_thresholds_and_future_clamp(self):
        for age, tier in [(0, "ACTIVE"), (7, "ACTIVE"), (8, "QUIET"), (14, "QUIET"), (15, "STALE"), (44, "STALE"), (45, "DORMANT"), (300, "DORMANT"), (-5, "ACTIVE")]:
            self.assertEqual(self.tier(age), (tier, max(age, 0)), age)
        self.man["defaults"].update(stale_after_days=20, dormant_after_days=30)
        self.assertEqual([self.tier(a)[0] for a in (18, 25, 30)], ["QUIET", "STALE", "DORMANT"])

    def test_base_rows_and_disabled_repo(self):
        rows = g(self.ev(), "freshness")
        self.assertEqual([(g(r, "repo"), g(r, "tier"), g(r, "age_days"), g(r, "public")) for r in rows],
                         [(AG, "STALE", 20, True), (CR, "ACTIVE", 3, False), (DT, "ACTIVE", 1, True), (MI, "ACTIVE", 1, True)])
        self.assertEqual(g(rows[0], "tip_sha"), self.R(AG)["tip"]["sha"])
        self.M(CR)["enabled"] = False
        self.assertEqual(([g(r, "repo") for r in g(self.ev(), "freshness")], self.F(repo=CR)), ([AG, DT, MI], []))

    def test_public_fails_closed(self):
        for key, val in [("visibility", "private"), ("visibility", "internal"), ("visibility", None), ("visibility_check", "mismatch"), ("visibility_check", "unavailable")]:
            self.setUp()
            for d in (self.R(DT), self.M(DT)):
                if key in d:
                    d.pop(key) if val is None else d.update({key: val})
            self.assertFalse(next(g(r, "public") for r in g(self.ev(), "freshness") if g(r, "repo") == DT), (key, val))

    def test_blocker_order_unblock_templates_and_ready(self):
        rv = lambda *r: [{"login": a, "state": s} for a, s in r]
        cr = rv(("r1", "CHANGES_REQUESTED"))
        cases = [(dict(draft=True, checks=None, reviews=None, mergeable_state=None, docs_only=None), "DRAFT"), (dict(draft=True, checks=ck("failure")), "DRAFT"),
                 (dict(checks=ck("failure")), "CHECKS-RED"), (dict(checks=ck("timed_out")), "CHECKS-RED"), (dict(checks=ck("cancelled")), "CHECKS-RED"),
                 (dict(checks=ck("action_required")), "CHECKS-RED"), (dict(checks=ck("success", None, "failure")), "CHECKS-RED"),
                 (dict(checks=[]), "NO-CI"), (dict(checks=[], docs_only=True), "NO-CI"),
                 (dict(checks=ck("success", None)), "CHECKS-PENDING"), (dict(checks=ck("success", None), mergeable_state="dirty"), "CHECKS-PENDING"),
                 (dict(mergeable_state="dirty"), "CONFLICT"), (dict(mergeable_state="dirty", reviews=cr), "CONFLICT"),
                 (dict(reviews=cr), "CHANGES-REQUESTED"), (dict(reviews=cr + rv(("r2", "APPROVED"))), "CHANGES-REQUESTED"),
                 (dict(reviews=cr + rv(("r1", "COMMENTED"))), "CHANGES-REQUESTED"), (dict(reviews=cr, mergeable_state="unknown"), "CHANGES-REQUESTED"),
                 (dict(mergeable_state="unknown"), "MERGEABILITY-UNKNOWN"), (dict(), None), (dict(checks=ck("neutral", "skipped", "success")), None),
                 (dict(reviews=cr + rv(("r1", "APPROVED"))), None)]
        self.R(MI)["prs"]["open"][:] = [mkpr(100 + i, **kw) for i, (kw, _) in enumerate(cases)]
        rows = {g(r, "number"): r for r in g(self.ev(), "prs")}
        for i, (kw, blocker) in enumerate(cases):
            want = ("READY", None, None) if blocker is None else ("BLOCKED", blocker, UNBLOCK[blocker].format(fake(0x5000 + 100 + i)[:7]))
            self.assertEqual((g(rows[100 + i], "cls"), g(rows[100 + i], "blocker"), g(rows[100 + i], "unblock")), want, (i, kw))

    def test_base_fixture_classes_labels_cap_and_order(self):
        rows = g(self.ev(), "prs")
        self.assertEqual([(g(r, "repo"), g(r, "number"), g(r, "cls"), g(r, "blocker")) for r in rows],
                         [(CR, 55, "READY", None), (DT, 41, "BLOCKED", "MERGEABILITY-UNKNOWN"), (DT, 42, "READY", None), (DT, 43, "READY", None),
                          (DT, 44, "READY", None), (MI, 21, "BLOCKED", "DRAFT"), (MI, 22, "BLOCKED", "CHECKS-RED"), (MI, 23, "BLOCKED", "NO-CI"),
                          (MI, 24, "BLOCKED", "CHECKS-PENDING"), (MI, 25, "BLOCKED", "CONFLICT"), (MI, 26, "BLOCKED", "CHANGES-REQUESTED"),
                          (MI, 27, "NOT_EVALUABLE", None)])
        by = {g(r, "number"): r for r in rows}
        self.assertEqual({n: g(r, "label") for n, r in by.items() if g(r, "label")}, {42: SELF_LABEL})
        self.assertEqual((g(by[27], "reason"), g(by[27], "unblock"), g(by[43], "idle_days")), ("deep-read cap", None, 9))

    def st(self, repo=MI, wf="weekly-health.yml"):
        r = next(r for r in g(self.ev(), "ci") if (g(r, "repo"), g(r, "workflow")) == (repo, wf))
        return g(r, "state"), g(r, "streak"), g(r, "first_red")

    def test_base_states(self):
        got = {(g(r, "repo"), g(r, "workflow")): (g(r, "state"), g(r, "streak"), g(r, "first_red")) for r in g(self.ev(), "ci")}
        self.assertEqual(got, {(AG, "ci.yml"): ("GREEN_PRE_TIP", 0, None), (CR, "ci.yml"): ("GREEN", 0, None),
                               (DT, "control-plane.yml"): ("GREEN", 0, None), (MI, "weekly-health.yml"): ("RED", 3, "2026-10-08")})

    def test_streak_counts_push_and_schedule_only(self):
        runs, tip = self.R(MI)["workflows"]["runs"], self.R(MI)["tip"]["sha"]
        runs[:] = [r for r in runs if r["event"] != "pull_request"]  # the PR-event success between failures did not reset the streak
        self.assertEqual(self.st(), ("RED", 3, "2026-10-08"))
        runs += [mkrun("weekly-health.yml", "failure", 0, 2, event="pull_request"), mkrun("weekly-health.yml", None, 0, 4, sha=tip)]
        self.assertEqual(self.st(), ("RED", 3, "2026-10-08"))  # a PR-event failure adds nothing; an in-progress run is not completed
        runs.append(mkrun("weekly-health.yml", "success", 4, 3))  # a push success between the 10-10 and 10-08 failures ends the streak
        self.assertEqual(self.st(), ("RED", 2, "2026-10-10"))

    def test_no_completed_run_and_tip_run_beats_pre_tip(self):
        self.set_runs(MI, [mkrun("weekly-health.yml", None, 0, 5)])
        self.assertEqual(self.st()[0], "NOT_EVALUABLE")
        self.R(AG)["workflows"]["runs"].append(mkrun("ci.yml", "failure", 1, 6, sha=self.R(AG)["tip"]["sha"]))
        self.assertEqual(self.st(AG, "ci.yml")[0], "RED")


class TestRules(Base):  # TR-4..TR-9: rule table, plan docs and parser
    def test_rule_boundaries_and_exclusions(self):
        for i, (mut, rule, repo, sub, want) in enumerate(RULE_ROWS):
            self.setUp()
            if mut:
                mut(self)
            self.assertEqual([g(f, "tier") for f in self.F(rule, repo, sub)], [want] if want else [], (i, rule, repo, sub))

    def test_hub_rules_c2_c3_u2(self):  # (hub age, open report PRs, max_unmerged_report_prs, validate exit) -> hub rules that fire
        for age, count, cap, vexit, want in [(2, 0, 3, 0, ""), (3, 0, 3, 0, "U2"), (7, 0, 3, 0, "U2"), (8, 0, 3, 0, "C2"), (25, 3, 3, 0, "C2 U2"),
                                             (3, None, 3, 0, "U2"), (2, None, 3, 0, ""), (25, None, 3, 0, "C2"), (0, 2, 3, 0, ""), (1, 3, 3, 0, "U2"),
                                             (1, 3, 4, 0, ""), (0, 0, 3, 1, "C3"), (0, 0, 3, 2, "")]:
            self.liveness(age, count)
            self.man["hub"]["max_unmerged_report_prs"], self.snap["hub"]["validate_exit"] = cap, vexit
            self.assertEqual(sorted(g(f, "rule") for f in self.F(repo=DT) if g(f, "rule") in ("C2", "C3", "U2")), want.split(), (age, count, cap, vexit))
        self.liveness(5, 3)
        self.man["hub"]["max_unmerged_report_prs"], self.snap["hub"]["validate_exit"] = 3, 1
        self.assertEqual(g(self.one("U2", DT, "hub"), "action"), "Hub degraded: heartbeat 5 d; 3 open report PRs")
        self.assertEqual(g(self.one("C3", DT, "validate"), "action"), "Control plane invalid: run validate.py and fix the reported check")

    def test_u1_require_check_suffix_and_h3_action(self):
        for days, suffix in [((14,), False), ((15,), True)]:
            u1_runs(*days)(self)
            self.assertEqual("require this check on main" in g(self.one("U1", MI, "weekly-health.yml"), "action"), suffix, days)
        h3_runs()(self)
        f = self.one("H3", MI, "weekly-health.yml")
        self.assertEqual((g(f, "confidence"), g(f, "action"), "unconfirmed" in g(f, "tags")), (1, f"{MI}: weekly-health.yml red on {fake(0x3ff)[:7]}, not tip; dispatch to confirm (owner)", True))

    def test_h2_window_docs_only_and_merged_at_beats_merged_flag(self):
        m = lambda n, at, **kw: {"number": n, "merged_at": at, "head_sha": fake(n), "checks": [], "changed_non_docs": True, **kw}
        self.R(CR)["prs"]["closed_recent"][:] = [m(70, day(14)), m(71, day(15)), m(72, None, merged=True), m(73, day(3), changed_non_docs=False), m(74, day(2), checks=ck("success"))]
        self.assertEqual(g(self.one("H2", CR, "ci.yml"), "evidence"), ["pr:70"])

    def test_plan_only_findings_are_capped_and_evidence_comes_from_the_row(self):
        words = ["data loss", "deletes", "corrupted", "leaks", "secret", "credential", "auth bypass", "injection"]
        self.set_plan(MI, [(f"KW{i}", f"synthetic {w} in src/a.py:{i + 1}", "P0", "Todo") for i, w in enumerate(words)]
                      + [("NF1", "synthetic data loss somewhere", "P0", "Todo"), ("NK1", "synthetic off by one in src/a.py:3", "P0", "Todo"),
                         ("D1", "synthetic off by one in src/a.py:3", "P0", "Todo"), ("D1", "synthetic off by one in src/a.py:3", "P0", "Todo")])
        self.assertEqual([g(self.one("C1", MI, f"KW{i}"), "tier") for i in range(8)], ["CRITICAL"] * 8)
        self.assertFalse(self.has("C1", MI, "NF1") or self.has("C1", MI, "NK1"))  # keyword without file:line, file:line without keyword
        self.assertEqual(g(self.one("H4", MI, "NK1"), "tier"), "HIGH")
        self.assertTrue(all(g(f, "tier") in ("MEDIUM", "LOW") for f in self.F(None, MI, "NF1")))
        self.assertEqual(len(self.F(None, MI, "D1")), 1)  # duplicate rows give one finding
        row = next(r for r in self.rows[MI] if g(r, "id") == "KW0")
        self.assertEqual(g(self.one("C1", MI, "KW0"), "evidence"), [f"plan:docs/Master-Plan.md:{g(row, 'line')}"])

    def test_evidence_gate_demotes_to_medium_and_hides(self):
        [r.update(run_id=None) for r in self.R(MI)["workflows"]["runs"]]
        ev = self.ev()
        f = self.one("U1", MI, "weekly-health.yml", ev)
        self.assertEqual((g(f, "tier"), g(f, "evidence"), "gated" in g(f, "tags"), g(f, "key") in [g(x, "key") for x in g(ev, "shown")]), ("MEDIUM", [], True, False))

    def test_tags(self):
        self.assertTrue({"verify", "untracked"} <= set(g(self.one("C1", MI, "BL-101"), "tags")))
        self.assertIn("untracked", g(self.one("H4", AG, "SYN-201"), "tags"))
        self.assertNotIn("untracked", g(self.one("H4", MI, "BL-102"), "tags"))  # trusted issue #72 cites BL-102
        self.assertTrue("close-candidate" in g(self.one("H5", AG, "#11"), "tags") and "fix-link-unverified" in g(self.one("H5", CR, "#61"), "tags"))

    def test_rows_in_each_repo_header_shape(self):
        by = {repo: {g(r, "id"): r for r in rows} for repo, rows in self.rows.items()}
        self.assertEqual({k: sorted(v) for k, v in by.items()},
                         {AG: ["SYN-190", "SYN-200", "SYN-201", "SYN-202", "SYN-203"], CR: ["A1", "A2", "A7", "TC1", "UX-R1"],  # TC9 table has no Finding column
                          MI: ["BL-101", "BL-102", "BL-103", "BL-104"], DT: ["DEV-005a", "DEV-301"]})  # miToosa Completed table and BL-100 lack Priority
        flags = lambda repo, i: (g(by[repo][i], "p0"), g(by[repo][i], "done"))
        self.assertEqual([flags(AG, "SYN-201"), flags(AG, "SYN-202"), flags(AG, "SYN-190"), flags(CR, "A1"), flags(CR, "A7"), flags(CR, "A2")],
                         [(True, False), (True, True), (False, True), (True, False), (True, True), (False, False)])
        self.assertEqual([g(by[AG]["SYN-190"], "priority"), g(by[AG]["SYN-190"], "section")], [None, "Completed This Cycle"])
        self.assertEqual([g(by[CR]["A1"], k) for k in ("status", "priority", "section")], [None, "Critical", "1.1.1 Architecture"])
        for repo, rows in self.rows.items():  # line is 1-based and text is the raw row
            lines = backlog_text(repo).split("\n")
            self.assertTrue(rows and all(lines[g(r, "line") - 1].strip() == g(r, "text").strip() for r in rows), repo)

    def test_id_regex(self):
        good = ["A1", "TC1", "UX-R1", "DEV-005a", "BL-42", "SYN-201"]
        bad = ["x1", "ABCDEFGHIJ-1", "A1b2", "A1 B2", "DEV-00055", "GH #12", "—", ""]
        before = copy.deepcopy(MAP)
        self.assertEqual([g(r, "id") for r in triage.parse_backlog(plan_text([(i, "synthetic t", "P0", "Todo") for i in good + bad]), MAP)], good)
        self.assertEqual(MAP, before)  # the mapping is never mutated


class TestTrustDedupeRank(Base):  # TR-10 trust, TR-11 dedupe, TR-12 rank and caps
    def test_external_count_and_untrusted_issue_never_joins(self):
        ext = g(self.ev(), "external")
        self.assertEqual((ext[AG], ext[CR], ext[MI], ext[DT]), (2, 0, 0, None))
        self.man["triage"]["trusted_logins"].append("fixture-stranger")
        self.assertEqual(g(self.ev(), "external")[AG], 1)
        self.setUp()
        self.R(MI)["issues"]["open"].append(mkissue(90, ["bug"], 30, "synthetic mentions BL-101", author="fixture-stranger"))
        f = self.one("C1", MI, "BL-101")
        self.assertTrue("untracked" in g(f, "tags") and "issue:90" not in g(f, "evidence"))

    def test_issue_joins_plan_finding_on_exact_plan_id_only(self):
        f = self.one("H4", MI, "BL-102")
        self.assertTrue("issue:72" in g(f, "evidence") and any(e.startswith("plan:") for e in g(f, "evidence")))
        self.assertIn(f"H5:{MI}:#72", g(f, "joined"))
        self.assertFalse(self.has("H5", MI, "#72"))  # merged into the row, never a second row
        self.issue(MI, 72)["title"] = "synthetic tracking BL-1020 totals bug"
        self.assertTrue(self.has("H5", MI, "#72") and "untracked" in g(self.one("H4", MI, "BL-102"), "tags"))

    def test_issue_joins_workflow_finding_by_filename(self):
        self.R(MI)["issues"]["open"].append(mkissue(91, ["bug"], 30, "synthetic notes on weekly-health.yml failures"))
        f = self.one("U1", MI, "weekly-health.yml")
        self.assertEqual((g(f, "tier"), "issue:91" in g(f, "evidence"), self.has("H5", MI, "#91")), ("URGENT", True, False))

    def test_plan_row_citing_the_issue_number_joins_but_never_across_repos(self):
        self.set_plan(MI, [("T1", "synthetic off by one in src/a.py:9, see #91", "P0", "Todo")])
        self.R(MI)["issues"]["open"].append(mkissue(91, ["bug"], 30))
        self.R(AG)["issues"]["open"].append(mkissue(92, ["bug"], 30, "synthetic mentions T1"))
        self.assertEqual((self.has("H4", MI, "T1"), self.has("H5", MI, "#91"), self.has("H5", AG, "#92")), (True, False, True))
        self.assertNotIn("issue:92", g(self.one("H4", MI, "T1"), "evidence"))

    def test_base_fixture_ranking_tiers_and_action_templates(self):
        ev = self.ev()
        self.assertEqual([g(f, "key") for f in g(ev, "findings")], list(BASE))
        for f in g(ev, "findings"):
            self.assertTrue(g(f, "key").startswith(f"{g(f, 'rule')}:{g(f, 'repo')}:"))  # dedupe key is <RULE>:<owner/repo>:<subject>
            tier, imp, conf, act, evid = BASE[g(f, "key")]
            self.assertEqual((g(f, "tier"), g(f, "impact"), g(f, "confidence"), g(f, "action")), (tier, imp, conf, act), g(f, "key"))
            if evid is not None:
                self.assertEqual(sorted(g(f, "evidence")), evid, g(f, "key"))
        self.assertEqual(g(ev, "top_action"), BASE[next(iter(BASE))][3])

    def test_caps_counts_and_more(self):
        ev = self.ev()
        top = [f for f in g(ev, "shown") if g(f, "tier") in ("URGENT", "HIGH")]
        self.assertEqual([g(f, "key") for f in g(ev, "shown")], list(BASE)[:13])
        self.assertTrue(len(top) == 8 and g(ev, "more") == 5 and all(sum(g(f, "repo") == r for f in top) <= 3 for r in (AG, CR, DT, MI)))
        self.assertEqual(g(ev, "counts"), {"CRITICAL": 5, "URGENT": 4, "HIGH": 9, "MEDIUM": 1, "LOW": 1})  # MEDIUM and LOW are counted, never shown
        for (total, per), idx, more in [((2, 3), [5, 6], 11), ((8, 1), [5, 6, 7, 10], 9)]:  # first the total cap binds, then the per-repo cap
            self.man["triage"].update(max_items_total=total, max_items_per_repo=per)
            ev, keys = self.ev(), list(BASE)
            self.assertEqual(([g(f, "key") for f in g(ev, "shown") if g(f, "tier") != "CRITICAL"], g(ev, "more")), ([keys[i] for i in idx], more))

    def test_critical_is_never_capped(self):
        self.R(MI)["issues"]["open"] += [mkissue(200 + i, ["security"], 2) for i in range(10)]
        shown = g(self.ev(), "shown")
        self.assertTrue(all(f"C1:{MI}:#{200 + i}" in [g(f, "key") for f in shown] for i in range(10)))
        self.assertEqual(len([f for f in shown if g(f, "tier") != "CRITICAL"]), 8)

    def test_no_findings_means_no_ranked_action(self):
        self.snap, self.rows = jload("snapshot-read-only.json"), {r: [] for r in self.rows}
        self.liveness(0)
        self.assertEqual([g(self.ev(), k) for k in ("findings", "top_action", "more")], [[], None, 0])


class TestNotEvaluableAndLiveness(Base):  # TR-13, TR-14, TR-15, TR-16
    def test_read_only_sections_freshness_and_git_derived_findings(self):
        self.snap = jload("snapshot-read-only.json")
        ev = self.ev()
        self.assertEqual((g(ev, "mode"), g(ev, "prs"), g(ev, "external"), g(ev, "security")), ("READ_ONLY", [], {AG: None, CR: None, DT: None, MI: None}, SECURITY_LINE))
        for repo in (AG, CR, DT, MI):
            self.assertEqual([self.sec(ev, repo, s) for s in ("prs", "issues", "workflows", "backlog")], [("NOT_EVALUABLE", "READ_ONLY")] * 3 + [("OK", None)])
        self.assertTrue(all(g(r, "state") == "NOT_EVALUABLE" for r in g(ev, "ci")))
        self.assertEqual([(g(r, "tier"), g(r, "age_days")) for r in g(ev, "freshness")], [("STALE", 20), ("ACTIVE", 3), ("ACTIVE", 1), ("ACTIVE", 1)])
        self.assertFalse(any(g(r, "public") for r in g(ev, "freshness")))  # visibility_check unavailable: fail closed
        self.assertEqual(sorted(g(f, "key") for f in g(ev, "findings")),  # plan rows and liveness come from git, so they survive READ_ONLY
                         sorted([f"C1:{CR}:A1", f"C1:{MI}:BL-101", f"C2:{DT}:liveness", f"H4:{AG}:SYN-201", f"H4:{CR}:TC1", f"H4:{MI}:BL-102", f"H4:{CR}:UX-R1"]))
        self.assertTrue(all("verify" in g(f, "tags") and "untracked" not in g(f, "tags") for f in g(ev, "findings") if g(f, "rule") != "C2"))  # tracking needs issues

    def test_force_switch_overrides_a_read_write_snapshot(self):
        self.man = yload("repos-2026-10-13-readonly.yml")
        ev = self.ev()
        self.assertEqual((g(ev, "mode"), g(ev, "prs"), self.sec(ev, MI, "issues")), ("READ_ONLY", [], ("NOT_EVALUABLE", "READ_ONLY")))
        self.assertEqual({g(f, "rule") for f in g(ev, "findings")} - {"C1", "C2", "H4"}, set())

    def test_reasons_pass_through_and_zero_is_never_invented(self):
        self.R(MI)["issues"] = {"status": "not_evaluable", "reason": "time box"}
        self.snap["timebox"]["exceeded_section"] = "issues"
        self.assertEqual(triage.check_snapshot(self.snap, self.man), [])
        ev = self.ev()
        self.assertEqual((self.sec(ev, MI, "issues"), g(ev, "external")[MI], self.sec(ev, AG, "prs")), (("NOT_EVALUABLE", "time box"), None, ("NOT_EVALUABLE", "not captured")))
        self.assertEqual((self.sec(ev, AG, "dependabot")[0], self.sec(ev, DT, "dependabot")[0]), ("NOT_EVALUABLE", "OK"))  # no dynamic ids vs resolved ids
        del self.rows[CR]
        self.assertEqual(self.sec(self.ev(), CR, "backlog")[0], "NOT_EVALUABLE")

    def test_hygiene_is_labelled_and_never_a_finding(self):
        ev, h = self.ev(), lambda r: g(g(self.ev(), "sections")[r], "hygiene")
        self.assertEqual([g(h(AG), k) for k in ("state", "merged_undeleted", "label")], ["OK", 4, "ancestry-merged only"])
        self.assertEqual((g(h(CR), "state"), "shallow" in g(h(CR), "reason")), ("NOT_EVALUABLE", True))
        self.assertTrue(all(re.fullmatch(r"[CUH][1-7]", g(f, "rule")) for f in g(ev, "findings")))

    def test_liveness_newest_valid_date_in_whole_days(self):
        refs = [{"ref": "origin/main", "last_run_date": "2026-10-08"}, {"ref": "origin/dreamtoosa/report-a", "last_run_date": "2026-10-11"},
                {"ref": "origin/dreamtoosa/report-b", "last_run_date": "2026-10-09"}]
        self.assertEqual((triage.hub_liveness(refs, RD), triage.hub_liveness([{"ref": "r", "last_run_date": RD}], RD)), ((2, "origin/dreamtoosa/report-a"), (0, "r")))
        tie = [{"ref": "origin/z", "last_run_date": "2026-10-10"}, {"ref": "origin/a", "last_run_date": "2026-10-10"}]
        self.assertEqual((triage.hub_liveness(tie, RD), triage.hub_liveness(tie[::-1], RD)), ((3, "origin/a"), (3, "origin/a")))  # ties: smallest ref

    def test_liveness_ignores_invalid_and_future_dates(self):
        bad = [{"ref": f"b{i}", "last_run_date": v} for i, v in enumerate(["2026-10-20", "not-a-date", None, "2026-13-45", 20261013, "", "2026-10-15"])]
        self.assertEqual(triage.hub_liveness(bad + [{"ref": "origin/main", "last_run_date": "2026-10-10"}], RD), (3, "origin/main"))
        self.assertEqual((triage.hub_liveness(bad, RD), triage.hub_liveness([], RD)), ((None, None), (None, None)))
        self.assertEqual(triage.hub_liveness([{"ref": "r", "last_run_date": "2026-10-14"}], RD), (0, "r"))  # RUN_DATE + 1 is accepted and clamped
        h = g(self.ev(), "hub")  # evaluate uses the same function
        self.assertEqual((g(h, "age_days"), g(h, "source_ref"), g(h, "state")), (*triage.hub_liveness(self.snap["hub"]["liveness_refs"], RD), "OK"))
        self.snap["hub"]["liveness_refs"] = [{"ref": "origin/main", "last_run_date": "2026-10-30"}]
        h = g(self.ev(), "hub")
        self.assertEqual((g(h, "age_days"), g(h, "state"), self.has("C2", DT)), (None, "NOT_EVALUABLE", False))


class TestDeterminism(Base):  # engine half of RN-1
    def test_fifty_shuffles_give_identical_evaluations(self):
        want = dump(self.ev())
        before = copy.deepcopy((self.snap, self.rows, self.fix, self.cron, self.man))
        rng = random.Random(2026)
        for i in range(50):
            snap, rows = copy.deepcopy(self.snap), {k: list(v) for k, v in self.rows.items()}
            shuffle_all(snap, rng)
            for v in rows.values():
                rng.shuffle(v)
            got = triage.evaluate(snap, rows, {r["repo"]: r["fix_links"] for r in snap["repos"]}, self.cron, self.man)
            self.assertEqual(dump(got), want, i)
        self.assertEqual((self.snap, self.rows, self.fix, self.cron, self.man), before)  # inputs are never mutated


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
Contract tests for the deployable text of dreamtoosa/ROUTINE_PROMPT.md (DEV-005a PR-1..PR-4).

Only the text below the first line that is exactly three dashes is deployed to the routine,
so only that text is tested. The tests pin the tool allowlist, the write boundary, the
absolute-path rule for script calls, the Fleet Triage phase wiring and the visibility rules.
"""

import re
import unittest
from pathlib import Path

PROMPT = Path(__file__).resolve().parent.parent / "dreamtoosa" / "ROUTINE_PROMPT.md"

TEN_TOOL_LINE = (
    "ToolSearch select:mcp__github__list_issues,mcp__github__list_pull_requests,"
    "mcp__github__issue_read,mcp__github__pull_request_read,mcp__github__issue_write,"
    "mcp__github__add_issue_comment,mcp__github__create_pull_request,mcp__github__get_label,"
    "mcp__github__actions_list,mcp__github__search_repositories"
)
TEN_TOOLS = set(TEN_TOOL_LINE.split("select:")[1].split(","))
READ_TOOLS = TEN_TOOLS - {f"mcp__github__{n}" for n in ("issue_write", "add_issue_comment", "create_pull_request")}
WRITE_NAMES = ("issue_write", "add_issue_comment", "create_pull_request")
BANNED = (
    "update_pull_request", "merge_pull_request", "pull_request_review_write", "enable_pr_auto_merge",
    "disable_pr_auto_merge", "update_pull_request_branch", "actions_run_trigger", "run_secret_scanning",
    "create_branch", "push_files", "create_or_update_file", "delete_file", "get_job_logs", "sub_issue_write",
    "update_issue_comment", "add_comment_to_pending_review", "resolve_review_thread", "request_copilot_review",
    "fork_repository", "create_repository",
)
SCRIPTS = '"$CLONE_ROOT/DreamToosa/dreamtoosa/'
MANIFEST = '--manifest "$CLONE_ROOT/DreamToosa/dreamtoosa/repos.yml"'
CHECK_CMD = (f'python3 {SCRIPTS}triage_report.py" check --snapshot "$SNAP_DIR/snapshot.json" '
             f'--clone-root "$CLONE_ROOT" {MANIFEST}')
RENDER_CMD = (f'python3 {SCRIPTS}triage_report.py" render --snapshot "$SNAP_DIR/snapshot.json" {MANIFEST} '
              '--clone-root "$CLONE_ROOT" --inject "$CLONE_ROOT/DreamToosa/reports/dream-report-$RUN_DATE.md"')
FALLBACK_CMD = RENDER_CMD + " --unavailable <CODE>"


def deployable() -> str:
    """Return everything below the first line that is exactly three dashes."""
    lines = PROMPT.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[lines.index("---") + 1:])


def split_sections(text: str) -> dict:
    """Map each level-2 heading to its body."""
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"## (.+)", line)
        if m:
            cur = m.group(1)
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def flat(text: str) -> str:
    """Collapse whitespace so phrase checks survive line wrapping."""
    return re.sub(r"\s+", " ", text)


def commands(text: str) -> list:
    """Logical command lines: backslash continuations joined, whitespace collapsed."""
    out, buf = [], ""
    for line in text.splitlines():
        s = line.strip()
        if s.endswith("\\"):
            buf += s[:-1].strip() + " "
            continue
        out.append(re.sub(r"\s+", " ", buf + s))
        buf = ""
    return [c for c in out if c]


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = deployable()
        cls.secs = split_sections(cls.text)
        cls.ground = cls.sec("Ground rules")
        cls.p0, cls.p05 = cls.sec("Phase 0 "), cls.sec("Phase 0.5 ")
        cls.p15, cls.p2 = cls.sec("Phase 1.5 "), cls.sec("Phase 2 ")
        cls.p3, cls.p4 = cls.sec("Phase 3 "), cls.sec("Phase 4 ")
        cls.p5, cls.p6, cls.final = cls.sec("Phase 5 "), cls.sec("Phase 6 "), cls.sec("Final summary")

    @classmethod
    def sec(cls, prefix: str) -> str:
        """Body of the one section whose heading starts with prefix; "" when absent (test_sections_exist reports it)."""
        hits = [body for head, body in cls.secs.items() if head.startswith(prefix)]
        return hits[0] if len(hits) == 1 else ""

    @property
    def span(self) -> str:
        return "\n".join([self.p15, self.p2, self.p3, self.p4])


class TestDeployableText(Base):
    def test_sections_exist_once_each_and_in_order(self):
        heads = list(self.secs)
        want = ["Ground rules", "Phase 0 ", "Phase 0.5 ", "Phase 1 ", "Phase 1.5 ", "Phase 2 ", "Phase 3 ",
                "Phase 4 ", "Phase 5 ", "Phase 6 ", "Budget", "Final summary"]
        idx = []
        for prefix in want:
            hits = [i for i, h in enumerate(heads) if h.startswith(prefix)]
            self.assertEqual(len(hits), 1, f"section {prefix!r}")
            idx.append(hits[0])
        self.assertEqual(idx, sorted(idx))

    def test_divider_is_first_and_text_starts_with_the_role_line(self):
        self.assertTrue(self.text.lstrip().startswith("You are DreamToosa"))
        self.assertNotIn("Edit here, then apply", self.text)  # intro above the divider is not deployed

    def test_no_emoji_and_no_notification_step(self):
        self.assertIsNone(re.search("[\U0001F000-\U0001FAFF☀-➿⬀-⯿]", self.text))
        for banned in ("PushNotification", "routine_summary"):
            self.assertNotIn(banned, self.text)  # the notification belongs to DEV-005b

    def test_phases_5_and_6_are_unchanged_in_scope(self):
        self.assertNotIn("triage", (self.p5 + self.p6).lower())
        self.assertNotIn("execution_mode", self.p6)  # the state field is DEV-005b
        self.assertIn('checkout -b dreamtoosa/report-$RUN_DATE "$BASE_REF"', self.p6)  # chaining fix is DEV-005b
        self.assertIn("mcp__github__create_pull_request", self.p5)


class TestToolAllowlist(Base):  # PR-1
    def test_toolsearch_line_is_exactly_the_ten_tool_line(self):
        self.assertEqual(self.text.count("ToolSearch select:"), 1)
        line = next(l for l in self.text.splitlines() if "ToolSearch select:" in l)
        self.assertEqual(line.strip().strip("`"), TEN_TOOL_LINE)
        self.assertEqual(len(TEN_TOOLS), 10)

    def test_banned_tool_names_are_absent_everywhere(self):
        for name in BANNED:
            self.assertNotIn(name, self.text, name)

    def test_every_github_token_belongs_to_the_ten_tool_set(self):
        tokens = set(re.findall(r"mcp__github__\w*", self.text))
        self.assertTrue(tokens)
        self.assertEqual(tokens - TEN_TOOLS, set())

    def test_phases_1_5_to_4_name_only_read_tools(self):
        tokens = set(re.findall(r"mcp__github__\w*", self.span))
        self.assertEqual(tokens - READ_TOOLS, set())
        for tool in ("list_pull_requests", "pull_request_read", "list_issues", "issue_read", "actions_list",
                     "search_repositories"):
            self.assertIn(f"mcp__github__{tool}", self.p15, tool)
        for name in WRITE_NAMES:
            self.assertNotIn(name, self.span, name)

    def test_write_tool_names_appear_only_in_ground_rules_and_phases_4_and_5(self):
        for head, body in self.secs.items():
            if head.startswith(("Ground rules", "Phase 4 ", "Phase 5 ")):
                continue
            for name in WRITE_NAMES:
                self.assertNotIn(name, body, f"{name} in {head!r}")


class TestWriteBoundary(Base):  # PR-2
    def rule(self) -> str:
        bullets = re.split(r"\n(?=- )", self.ground)
        hits = [b for b in bullets if "Fleet Triage" in b and "approve" in b.lower()]
        self.assertEqual(len(hits), 1, "exactly one Fleet Triage write-boundary ground rule")
        return hits[0]

    def test_rule_forbids_every_write_action_for_fleet_triage(self):
        rule = self.rule()
        for word in ("approve", "merge", "review", "comment", "close", "reopen", "label", "auto-merge",
                     "update-branch", "dispatch", "re-run"):
            self.assertRegex(rule, rf"(?<![\w-]){re.escape(word)}(?![\w-])", word)
        self.assertRegex(rule, r"(?i)never")
        self.assertRegex(rule, r"(?i)read-only|reads only")

    def test_rule_limits_the_three_write_tools_to_phases_4_and_5(self):
        rule = flat(self.rule())
        for name in WRITE_NAMES:
            self.assertIn(name, rule)
        self.assertIn("only Phases 4 and 5", rule)

    def test_ten_tools_are_the_whole_allowlist(self):
        self.assertRegex(flat(self.ground), r"(?i)(whole|entire|complete) allowlist")


class TestAbsolutePaths(Base):  # PR-3
    def test_every_python3_line_runs_a_script_by_absolute_path(self):
        lines = [l.strip() for l in self.text.splitlines() if re.search(r"\bpython3\b", l)]
        self.assertGreaterEqual(len(lines), 4)  # validate x2, check, render x2
        for line in lines:
            self.assertRegex(line, rf'^python3 "\$CLONE_ROOT/DreamToosa/dreamtoosa/[\w.]+\.py"( |$)', line)
        scripts = {re.search(r"dreamtoosa/([\w.]+\.py)", l).group(1) for l in lines}
        self.assertEqual(scripts, {"validate.py", "triage_report.py"})

    def test_no_module_form_and_no_pythonpath(self):
        self.assertNotRegex(self.text, r"python3?\s+-m\b")
        self.assertNotIn("PYTHONPATH", self.text)
        self.assertNotRegex(self.text, r"(?m)^\s*(cd|pushd)\s")

    def test_check_and_render_commands_are_the_exact_spec_commands(self):
        py = [c for c in commands(self.p15) if c.startswith("python3")]
        self.assertEqual([c for c in py if "triage_report.py" in c], [CHECK_CMD])
        self.assertEqual([c for c in commands(self.p3) if c.startswith("python3")], [RENDER_CMD, FALLBACK_CMD])
        self.assertFalse([c for c in commands(self.text) if c.startswith("python3") and "heartbeat" in c])


class TestScopeAndVisibility(Base):  # PR-4
    def test_phase_4_never_reads_fleet_triage(self):
        self.assertRegex(flat(self.p4), r"(?i)never reads? Fleet Triage")
        for artifact in ("SNAP_DIR", "snapshot.json", "triage_report", "TRIAGE_CODE", "rank-1"):
            self.assertNotIn(artifact, self.p4, artifact)

    def test_coverage_line_says_not_account_wide(self):
        self.assertRegex(self.p15, r"(?m)^.*[Cc]overage.*manifest.*not account-wide.*$")

    def test_every_repository_search_is_repo_qualified(self):
        queries = re.findall(r'"query":\s*"([^"]*)"', self.text)
        self.assertEqual(len(queries), 1)
        for q in queries:
            self.assertRegex(q, r"^repo:\S+/\S+$")
        for line in self.text.splitlines():
            if "search_repositories" in line and "ToolSearch" not in line:
                self.assertIn("repo:", line)
        self.assertNotRegex(self.text, r"\b(user|org|topic|stars):")

    def test_visibility_cross_check_text_exists_and_fails_closed(self):
        p15 = flat(self.p15)
        for needle in ("visibility_check", "mismatch", "unavailable", "fails closed", "treated as private"):
            self.assertIn(needle, p15, needle)
        self.assertRegex(p15, r"(?is)visibility.{0,200}manifest")

    def test_non_public_repos_get_only_the_withheld_form_in_phase_3(self):  # decision OI-6
        p3 = flat(self.p3)
        self.assertRegex(p3, r"(?i)non-public")
        for needle in ("private", "absent", "unrecognised", "visibility_check", "withheld", "per-repo report",
                       "repo name", "age", "tier", "CRITICAL", "URGENT", "HIGH", "already committed"):
            self.assertIn(needle, p3, needle)
        for forbidden in ("title", "body", "file path", "log text", "commit message", "SHA", "date"):
            self.assertRegex(p3, rf"\b(?:No|no|nothing)\b[^.]{{0,200}}\b{forbidden}\b", forbidden)
        self.assertRegex(p3, r"(?i)Fleet Triage block only for public repos")  # action items from triage: public only


class TestPhaseWiring(Base):
    def test_intro_mentions_the_contract_tests(self):
        head = PROMPT.read_text(encoding="utf-8").split("\n---\n")[0]
        self.assertIn("tests/test_routine_prompt.py", head)

    def test_phase_0_defaults_and_force_switch(self):
        for key in ("hub.force_read_only", "stale_after_days", "dormant_after_days",
                    "soft_time_box_minutes_fleet_triage", "triage.max_items_total", "triage.max_items_per_repo",
                    "triage.pr_idle_days", "triage.routine_gap_days", "triage.heartbeat_max_age_days",
                    "triage.trusted_logins", "visibility", "dependabot_scope"):
            self.assertIn(key, self.p0, key)
        self.assertRegex(self.p0, r"(?i)default")
        self.assertIn("dependabot[bot]", self.p0)

    def test_phase_0_5_force_switch_overrides_the_probe(self):
        self.assertIn("hub.force_read_only", self.p05)
        self.assertRegex(self.p05, r"(?i)regardless")
        self.assertIn('EXECUTION_MODE="READ_ONLY"', self.p05)

    def test_phase_1_5_steps_a_to_g_in_order(self):
        self.assertEqual(re.findall(r"(?m)^([a-g])\. \*\*", self.p15), list("abcdefg"))
        self.assertIn("SNAP_DIR=$(mktemp -d)", self.p15)
        self.assertRegex(flat(self.p15), r"(?i)never committed")
        self.assertIn("$SNAP_DIR/snapshot.json", self.p15)

    def test_phase_1_5_integrity_check_comes_before_the_engine(self):  # TRI-A-008
        cmds = commands(self.p15)
        for c in ('git -C "$CLONE_ROOT/DreamToosa" diff --quiet HEAD -- dreamtoosa/',
                  'git -C "$CLONE_ROOT/DreamToosa" status --porcelain -- dreamtoosa/'):
            self.assertIn(c, cmds)
        self.assertIn("E_ENGINE_TAMPERED", self.p15)
        self.assertLess(self.p15.index("E_ENGINE_TAMPERED"), self.p15.index("validate.py"))
        self.assertIn("E_ENGINE_TAMPERED", self.p3)  # the fixed line is written without running the engine
        self.assertLess(cmds.index('git -C "$CLONE_ROOT/DreamToosa" diff --quiet HEAD -- dreamtoosa/'),
                        cmds.index(f'python3 {SCRIPTS}validate.py"'))

    def test_phase_1_5_validate_runs_in_both_modes_and_c3_needs_exit_1(self):  # TRI-A-010
        self.assertIn(f'python3 {SCRIPTS}validate.py"', commands(self.p15))
        self.assertIn("hub.validate_exit", self.p15)
        self.assertRegex(flat(self.p15), r"(?is)both modes")
        self.assertRegex(flat(self.p15), r"C3 is raised only when validate.py exits 1")
        self.assertIn("E_RUN", self.p15)

    def test_phase_1_5_git_facts_are_read_only_git(self):
        allowed = {"fetch", "diff", "status", "log", "show", "rev-parse", "for-each-ref", "branch", "symbolic-ref"}
        for c in commands(self.span):
            m = re.search(r'git -C "[^"]+" (\S+)', c)
            if m:
                self.assertIn(m.group(1), allowed, c)
                if m.group(1) == "branch":
                    self.assertIn(" -r ", c)
        for needle in ("fetch origin --quiet", "for-each-ref", "origin/dreamtoosa/report-*", "last_run.date",
                       "origin/HEAD", "origin/main", "--is-shallow-repository", "--since=\"90 days ago\"",
                       "%x09", "%cI"):
            self.assertIn(needle, self.p15, needle)

    def test_phase_1_5_api_facts_follow_the_caps_and_modes(self):
        p = flat(self.p15)
        self.assertRegex(p, r"(?is)READ_ONLY.{0,300}not_evaluable|not_evaluable.{0,300}READ_ONLY")
        for needle in ("deep-read cap", "time box", "date +%s", "exceeded_section", "at most 5", "at most 3",
                       "merged_at", "get_check_runs", "get_reviews", "get_files", "list_workflows",
                       "list_workflow_runs", "dynamic_ids", "perPage", "docs_only", "changed_non_docs"):
            self.assertIn(needle, p, needle)
        self.assertRegex(p, r"(?i)no log reads|never read(s)? (job )?logs")
        self.assertRegex(p, r"(?i)never add a `severity` key")

    def test_phase_1_5_check_exit_codes_and_one_repair(self):  # TRI-A-029
        p = flat(self.p15)
        self.assertRegex(p, r"(?i)exit 0")
        self.assertRegex(p, r"(?i)exit 1")
        self.assertRegex(p, r"(?i)exit 2")
        self.assertIn("one repair attempt", p)
        self.assertIn("E_RUN", p)
        self.assertIn("TRIAGE_CODE", p)
        self.assertRegex(p, r"(?i)never blocks?|does not block|without blocking")

    def test_phase_2_reuses_the_phase_1_5_pr_list(self):
        self.assertIn("Phase 1.5", self.p2)
        self.assertRegex(flat(self.p2), r"(?i)do not call")
        self.assertIn("max_open_prs", self.p2)

    def test_phase_3_injects_the_block_and_falls_back_on_failure(self):
        p3 = flat(self.p3)
        self.assertRegex(p3, r"(?i)one repair attempt")
        self.assertIn("--unavailable", p3)
        self.assertRegex(p3, r"(?i)do not write, move or edit any `fleet-triage` marker")
        self.assertRegex(p3, r"(?i)Phase 6 continues without blocking")

    def test_final_summary_uses_the_rank_1_action_or_none_ranked(self):
        final = flat(self.final)
        self.assertIn("rank-1", final)
        self.assertIn("none ranked", final)
        self.assertRegex(final, r"(?i)verbatim")


if __name__ == "__main__":
    unittest.main()

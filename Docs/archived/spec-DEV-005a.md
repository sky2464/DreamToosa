# Spec: DEV-005a — Fleet Triage: freshness, PR, CI and issues sections

> **Story ID:** DEV-005a
> **Epic:** DEV-100 (Multi-repo maintainer routine)
> **Status:** Backlog — spec drafted, approval pending (no approval marker)
> **Estimate:** L
> **Clarity:** `ready`
> **Spec created:** 2026-10-13
> **Sibling:** DEV-005b (ledger carry-forward, golden pick, daily heartbeat job, PushNotification, chaining fix). Split per interview Q3.

---

### Plan-Mode Spec Interview (findings)

#### Inferred (>=80% — no question asked)

| Checklist area | Finding |
|----------------|---------|
| Control plane | Routine `trig_01PvQiwSRhJktFxMXwxf14Qi` is the only scheduled runner. Memory is `dreamtoosa/state.json` on main and on `dreamtoosa/report-*` branches. |
| Dark routine | Last state write 2026-09-18 (READ_ONLY after GitHub 401). Dark for 25 days on 2026-10-13. Cause unknown (task 0.2). |
| Liveness source | Git refs (`origin/main`, `origin/dreamtoosa/report-*`) are the only liveness signal that survives a dark routine. |
| Severity | Code can compute severity from structured facts. The 2026-09-18 run drifted (fixed baselines cited as open; #166 and #168 dropped). |
| Repo scope | Manifest repos equal routine sources (4). Account-wide coverage is out of scope. |
| Staleness | Committer date of the default-branch tip. `pushed_at` is ignored because bot branches inflate it. |
| Write surface | The feature needs no merge, approve, review or dispatch tool. |
| Trust boundary | Issue and PR titles, branch names, commit subjects and plan rows are untrusted text (prompt injection). |
| Brownfield baseline | validate.py runs 19 checks (floor 19 in `tests/test_validate.py`). ROUTINE_PROMPT.md line 29 loads 9 GitHub tools, including `update_pull_request`. No Phase 1.5 or triage block exists. origin/main is a8b4beb with no report-* refs. control-plane.yml runs on push and pull_request for `dreamtoosa/**` and `tests/**`. |

#### Asked & confirmed

Binding answers from the user interview. Q1 to Q8 apply to the DEV-005 set; the story column says where each lands.

| Q# | Question | Answer (story) |
|----|----------|----------------|
| Q1 | Hub visibility and private-repo details | Keep the DreamToosa hub public. Add per-repo `visibility: public|private` to repos.yml, validated by validate.py. Fleet Triage omits private-repo details (titles, bodies, file paths, log text, commit messages) from any committed or published output. A Wave 0 human check of each repo's visibility is a prerequisite before Wave 2 (005a). |
| Q2 | Where severity is decided | Two-file deterministic engine: `triage.py` (pure rules) and `triage_report.py` (CLI, verify-git, render, inject, heartbeat). The LLM only gathers facts. The snapshot check rejects any `severity` key. Golden fixture and determinism test required (005a). |
| Q3 | Story split | 005a = freshness, PR, CI and issues sections, rules C/U/H, caps, render, validator, visibility key, Phase 1.5 and Phase 3 prompt text (this spec). 005b = ledger carry-forward, golden pick, heartbeat job, PushNotification, chaining fix. Each is independently shippable. |
| Q4 | Dark-routine detection | Daily read-only heartbeat job in control-plane.yml (005b), failing when the freshest last_run.date is older than 3 days. The shared liveness definition is built in 005a. Risk recorded in 2.4. |
| Q5 | Urgent delivery | One gated PushNotification per run, wrapped in routine_summary (005b). Verifying PushNotification in RemoteTrigger routines is a Wave 0 gate for 005b only. |
| Q6 | Repo coverage | Manifest-only. The coverage line states the report is not account-wide. No account-wide discovery (005a). |
| Q7 | Meaning of PR approval | READY is the owner's merge decision: non-draft, at least one check and all checks green, no changes requested, no conflict. Self-authored READY PRs are labelled "ready to merge (GitHub forbids self-approval)". A READY PR idle more than 7 days is URGENT. Everything else is BLOCKED with exactly one blocker and one unblock action (005a). |
| Q8 | Issues | Report-only. Fleet Triage never files, comments on or updates issues or PRs. Phase 4 is unchanged and never consumes Fleet Triage findings (005a). |

#### Documented assumptions

- A1 — Visibility values are written to repos.yml only after task 0.1. The critic's lookups (AgToosa public, Crapsino private, DreamToosa public, miToosa public) are unverified and are not inputs. Absent, unknown or mismatched visibility fails closed (renders as private).
- A2 — The blocker set is the plan's six reasons plus MERGEABILITY-UNKNOWN, so an `unknown` mergeable state is never clean and still has exactly one blocker.
- A3 — No log reads in 005a. `get_job_logs` is not loaded. Evidence is run id, conclusion and head SHA, which satisfies the evidence gate.
- A4 — H6 scope comes from a per-repo manifest key `dependabot_scope` (default `unknown`, treated as runtime). Profile stanzas are not changed in 005a.
- A5 — FIX-PARTIAL is removed because it is not deterministic. A verified fix link yields CLOSE-CANDIDATE (LOW) for the owner to decide.
- A6 — The plan's "release drift" hygiene item is dropped because no source defines it. 005a reports merged-but-undeleted branch counts only.
- A7 — The visibility cross-check uses a repo-qualified `search_repositories` call (read-only, added to the allowlist). Account-wide queries are never made.
- A8 — The READ_ONLY acceptance uses `hub.force_read_only: true` in a local scratch worktree (no push). A live forced run would need a commit to main, so it is not required.
- A9 — Phase 6 is unchanged in 005a and still branches from BASE_REF. The chaining fix is 005b. 005a adds no remote writes.
- A10 — Default `triage.trusted_logins` is `[sky2464, dependabot[bot]]`. The owner reviews this in the Wave 2 PR.
- A11 — The routine sandbox has Python 3.12 and PyYAML (validate.py already needs both). To be confirmed by task 0.2.
- A12 — Effort L for 005a. The critic sized the combined DEV-005 as L. 005a carries both engine modules, 14 rules, verify-git and the validator. 005b is M.
- A13 — The snapshot is written to a `mktemp -d` directory outside every clone and is never committed.
- A14 — Soft time box `budget.soft_time_box_minutes_fleet_triage` is 10 minutes. The value is a starting point, tuned after task 4.5.

---

## Section 1 — Requirements

### Goal Contract

| Field | Value |
|-------|-------|
| Goal | Give the daily Dream Report a deterministic, read-only Fleet Triage block (freshness, PRs, default-branch CI, issues) with rules C, U and H, caps, a safe render and a validated control plane. |
| User outcome | The solo maintainer reads one scannable block at the top of each Dream Report index. Every claim cites evidence. Unknown data shows as "not evaluable", never as zero or green. Private-repo details never reach the public hub. |
| Success condition | (1) `triage_report` check and render reproduce the 2026-10-13 golden output byte-for-byte, and 50 shuffled inputs give identical output. (2) validate.py passes with the new keys, and removing them adds no failures. (3) One READ_WRITE run's index starts with Fleet Triage: four freshness rows, PR, CI and issue sections, caps honoured, no golden section. (4) The READ_ONLY render shows "not evaluable" for every API-backed cell, keeps freshness populated, and nothing is pushed. |
| Proof / evidence | Commands in 3.3; CI green on the PR; owner-observed READ_WRITE run (task 4.5); local READ_ONLY simulation (task 4.1). |
| Non-goals | Approving, merging, reviewing, commenting on, closing, reopening, labelling, editing, enabling auto-merge for, updating, dispatching or re-running anything; filing issues; golden pick; ledger and deltas; heartbeat job; PushNotification; chaining fix; log tails; account-wide discovery; changing target repos. |
| Assumptions | A1 to A14 (findings). |
| Risks | Section 2.4. |
| Unresolved questions | Open items OI-1 to OI-5. |

### 1.1 User Stories

- **As a** solo maintainer, **I want** one deterministic Fleet Triage block at the top of each Dream Report **so that** stale repos, PRs awaiting my decision, red CI and issue risk show in one place.
- **As a** maintainer of public repos, **I want** private-repo details withheld from the public hub **so that** unpatched findings are not published.
- **As a** maintainer reviewing the routine, **I want** severity computed by reviewable code **so that** the same facts always produce the same ranking.
- **As a** maintainer, **I want** unknown data shown as "not evaluable" **so that** an outage never looks like an all-clear.

### 1.2 Acceptance Criteria (EARS)

| ID | EARS | Priority |
|----|------|----------|
| TRI-A-001 | WHEN a repo's visibility is private, absent or unrecognised, THE SYSTEM SHALL omit its titles, bodies, file paths, log text, commit messages, SHAs and dates from every committed or published Fleet Triage output, showing only its name, age, tier and a count of withheld CRITICAL, URGENT and HIGH items. | Must |
| TRI-A-002 | THE SYSTEM SHALL render security-class C1 findings as category, repo and finding ID only, with no file:line, title or excerpt, for every repo. | Must |
| TRI-A-003 | WHEN an issue or PR author is not in `triage.trusted_logins`, or an issue carries `status-needs-triage`, THE SYSTEM SHALL exclude it from C1, U4, H5 and all dedupe joins, and count it only as "external/untriaged: N". | Must |
| TRI-A-004 | THE SYSTEM SHALL assign severity only through `triage.py` rules. `triage_report check` SHALL exit 1 with E_SEVERITY_KEY on any key named `severity`, and E_SCHEMA on any key outside the allowlist, at any depth. | Must |
| TRI-A-005 | THE SYSTEM SHALL build every action, header line, summary and notification from per-rule templates with typed parameters (repo from manifest; workflow filename matching `^[\w.-]+\.ya?ml$`; integers; plan IDs matching `^[A-Z]{2,5}-\d+$`). No model-written prose SHALL appear in those fields. | Must |
| TRI-A-006 | WHEN untrusted titles, commit subjects or labels are rendered, THE SYSTEM SHALL escape them as inline code, truncate them to 80 characters, render no links, and record suspicious text under integrity flags. | Must |
| TRI-A-007 | WHEN `check` reads a snapshot, THE SYSTEM SHALL reject (E_SECRET) any string matching the patterns in 2.2, reject (E_ABS_PATH) absolute paths and paths inside a clone, and re-derive tip SHA, committer dates, backlog blob SHA and liveness dates from git, failing with E_VERIFY_GIT:<field> on mismatch. | Must |
| TRI-A-008 | BEFORE the engine runs, THE SYSTEM SHALL confirm that `git -C <hub> diff --quiet HEAD -- dreamtoosa/` and `git -C <hub> status --porcelain -- dreamtoosa/` report no changes. Otherwise it SHALL render "Fleet Triage unavailable: E_ENGINE_TAMPERED" and skip the engine. | Must |
| TRI-A-009 | THE SYSTEM SHALL load exactly the ten GitHub tools in the ToolSearch line of 2.1. It SHALL NOT load `update_pull_request` or any tool that merges, approves, reviews, comments for triage, enables auto-merge, updates a branch, dispatches or re-runs. The ground rules SHALL state that Fleet Triage never performs those actions. | Must |
| TRI-A-010 | EVERY `python3` call in the routine prompt SHALL use an absolute `"$CLONE_ROOT/DreamToosa/..."` path. C3 SHALL be raised only on validate.py exit 1. Any other failure SHALL render E_RUN. | Must |
| TRI-A-011 | WHEN a triage block exists, validate.py SHALL check the keys listed in 2.1 (visibility, backlog mapping, workflow lists, `dependabot_scope`, `trusted_logins`, caps and windows, `stale < dormant`, `hub.force_read_only`, soft time box). A manifest without the triage block SHALL produce no new failures. validate.py SHALL run in script mode and SHALL NOT import triage modules. | Must |
| TRI-A-012 | THE SYSTEM SHALL NOT read Fleet Triage findings in Phase 4 or Phase 5. | Must |
| TRI-A-013 | WHEN Phase 1.5 runs in either mode, THE SYSTEM SHALL record, for each enabled repo, the default-branch tip SHA, committer date, age in days and tier (ACTIVE at most 7; QUIET 8 to `stale_after_days`; STALE to `dormant_after_days` minus 1; DORMANT at or above `dormant_after_days`), using `git -C` fetch and read only. | Must |
| TRI-A-014 | WHEN a repo has open PRs, THE SYSTEM SHALL classify each as READY or BLOCKED. READY requires non-draft, at least one check, all conclusions in {success, neutral, skipped}, no latest CHANGES_REQUESTED review, and clean mergeable state. BLOCKED carries exactly one blocker, chosen in order from DRAFT, CHECKS-RED, NO-CI, CHECKS-PENDING, CONFLICT, CHANGES-REQUESTED, MERGEABILITY-UNKNOWN. Merge state SHALL come from `merged_at`. | Must |
| TRI-A-015 | THE SYSTEM SHALL compare the latest completed run of each product workflow with the tip, count consecutive failures from push and schedule events only, record first red, and resolve dynamic Dependabot numeric IDs from `list_workflows` (NOT_EVALUABLE when none exist). | Must |
| TRI-A-016 | THE SYSTEM SHALL label a READY PR authored by the repo owner "ready to merge (GitHub forbids self-approval)", label a zero-check PR whose changed paths are all docs as READY "no CI required (docs-only)", and show a docs-only tip with a green latest run as "green, pre-tip". | Should |
| TRI-A-017 | THE SYSTEM SHALL count a fix link only when a default-branch commit message says closes, fixes or resolves #N, or the issue's `closed_by_pull_requests` lists a merged PR. Any other link SHALL render as "fix link unverified" and SHALL NOT change a tier. | Must |
| TRI-A-018 | THE SYSTEM SHALL apply rules C1 to C3, U1 to U4 and H1 to H7 exactly as defined in 2.2, with the evidence gate (HIGH or above needs an artifact, else MEDIUM) and the plan-document cap (plan-only findings at most HIGH unless a data-loss or security keyword matches a file:line citation; tagged `verify`, and `untracked` when no trusted issue cites them). | Must |
| TRI-A-019 | THE SYSTEM SHALL form dedupe keys `<RULE>:<owner/repo>:<subject>`. A trusted issue joins a same-repo CI or plan finding only when a plan row, a commit reference or the title cites its number, plan ID or workflow filename exactly. Joins merge evidence and never create a second row. | Must |
| TRI-A-020 | THE SYSTEM SHALL order findings by tier, impact, confidence, age (oldest first), manifest order and finding ID. CRITICAL SHALL never be capped. URGENT and HIGH SHALL be capped at `triage.max_items_total` (8) and `triage.max_items_per_repo` (3), with overflow shown as "+N more". MEDIUM and LOW SHALL be counted only. | Must |
| TRI-A-021 | WHEN a section's API calls are skipped (READ_ONLY, including `hub.force_read_only: true`), fail, or run past the time box, THE SYSTEM SHALL render it as "not evaluable (reason)". It SHALL NOT render 0, none, PASS or green, SHALL NOT count it as a miss, and SHALL keep freshness populated. | Must |
| TRI-A-022 | THE SYSTEM SHALL read `budget.soft_time_box_minutes_fleet_triage` and SHALL reject snapshots that exceed the deep-read caps (5 PR deep reads, 3 merged-PR check reads, 3 `issue_read` calls). Sections not completed inside the box SHALL be NOT_EVALUABLE (time box), and the caps used SHALL be disclosed in section 6. | Must |
| TRI-A-023 | THE SYSTEM SHALL compute hub liveness as the newest valid `last_run.date` (ISO date, not later than RUN_DATE + 1) across origin/main and every origin/dreamtoosa/report-* ref, compared in whole days. C2 (CRITICAL) SHALL fire above 7 days. U2 (URGENT) SHALL fire above `triage.routine_gap_days` up to 7 days. `triage_report heartbeat` SHALL use the same function and exit 1 when the age exceeds `triage.heartbeat_max_age_days` or is not evaluable. | Must |
| TRI-A-024 | WHEN a READY PR, including a `dreamtoosa/report-*` PR, has been idle (by `updated_at`) longer than `triage.pr_idle_days`, THE SYSTEM SHALL raise it as URGENT (U3). | Should |
| TRI-A-025 | WHEN a PR merged into the default branch in the last 14 days had zero check runs or a failing check on its head SHA and changed a non-docs path, THE SYSTEM SHALL list it under H2, once per repo and workflow. | Should |
| TRI-A-026 | THE SYSTEM SHALL cross-check each repo's visibility with a repo-qualified `search_repositories` call in Phase 1.5. A mismatch or failed lookup SHALL fail closed (treated as private) and SHALL be listed in section 6. | Should |
| TRI-A-027 | THE SYSTEM SHALL render the block between `fleet-triage` markers in this order: header (Mode; Coverage line stating the report covers the manifest repos and is not account-wide; Security "none visible (alert APIs not exposed via MCP)"; hub heartbeat; most important human action = rank-1 action or "none ranked"); sections 1 to 3; section 4 (Next tasks); section 5 (golden placeholder "not in DEV-005a (DEV-005b)"); section 6. No emoji. A private repo contributes only its withheld line. | Must |
| TRI-A-028 | THE SYSTEM SHALL produce byte-identical output for the same snapshot under any input order, equal to `tests/fixtures/triage/expected-2026-10-13.md`. Every Python module under `dreamtoosa/` and `tests/` SHALL stay under 500 lines. | Must |
| TRI-A-029 | IF `check` or `render` still fails after one bounded repair attempt, THEN THE SYSTEM SHALL inject "Fleet Triage unavailable: <CODE>" with a fixed code, and Phase 6 SHALL continue without blocking the report commit. | Must |
| TRI-A-030 | THE SYSTEM SHALL replace only the text between the markers on inject. IF a fleet-triage marker string appears outside the block, THEN it SHALL refuse with E_INJECT_MARKERS and write nothing. | Must |
| TRI-A-031 | THE SYSTEM SHALL report merged-but-undeleted remote branch counts as a hygiene line labelled "ancestry-merged only", shown as not evaluable on a shallow clone. It SHALL never become a Next task. | Could |
| TRI-A-032 | WHEN the spec is approved, THE SYSTEM SHALL record DEV-005a in the Master-Plan Active Cycle under DEV-100, record DEV-005b in Backlog, and add a CHANGELOG [Unreleased] Added entry that cites control-plane.yml. | Should |

### 1.3 Out of Scope

- Approving, merging, reviewing, commenting on, closing, reopening, labelling, editing, enabling auto-merge for, dispatching or re-running any PR, issue or workflow.
- Golden pick, carry-forward ledger and deltas, heartbeat workflow job, PushNotification, chaining fix, READ_ONLY `fix_rotation`, Phase 0 reading state from main — all DEV-005b or later.
- Log tail reads (`get_job_logs`), security-alert APIs (not exposed by MCP), account-wide discovery, profile stanzas, stale profile baselines.
- Filing issues or PRs from triage findings. Phase 4 is unchanged.
- Changing any target repository, `dreamtoosa/state.json`, or existing committed history (see OI-5).

---

## Section 2 — Design

### 2.1 Architecture Blueprint

Files to create:
- `dreamtoosa/triage.py` — pure rules, no I/O: snapshot allowlist and scans; freshness; CI state; PR classes; issue and fix-link classification; backlog row parser (text in, rows out); hub liveness; rules C1 to H7; dedupe; rank; caps; evidence gate. Target under 450 lines.
- `dreamtoosa/triage_report.py` — CLI (`check`, `render`, `heartbeat`); `--verify-git`; backlog and cron text via `git -C <clone> show <tip>:<path>` (`--backlog-dir` is for tests only); hub-tree integrity check; markdown render; marker inject; fixed error codes. Runs as a script by absolute path and imports `triage` from its own directory. Target under 450 lines.
- `tests/test_triage_rules.py`, `tests/test_triage_render.py`, `tests/test_triage_cli.py` — split per critic (the ledger test file lands in 005b).
- `tests/fixtures/triage/`: `snapshot-2026-10-13.json`, `snapshot-read-only.json`, `repos-2026-10-13.yml` (frozen manifest), `backlog/{agtoosa,crapsino,mitoosa}.md` (frozen excerpts at pinned tips), `expected-2026-10-13.md`.
- `tests/test_routine_prompt.py` — contract tests on the deployable text below the `---` line of ROUTINE_PROMPT.md.

Files to modify:
- `dreamtoosa/repos.yml` — `defaults.stale_after_days: 14`, `defaults.dormant_after_days: 45`; `hub.force_read_only: false`; per repo: `visibility` (from 0.1), `backlog` mapping, `product_workflows`, `watch_workflows` (`{file, kind}` with kind in security, sync, audit), `dependabot_scope`. Product: AgToosa [ci.yml], Crapsino [ci.yml], DreamToosa [control-plane.yml], miToosa [weekly-health.yml]. Watch: AgToosa [agtoosa-issues-sync.yml sync, security-scan.yml security, github-surface-audit.yml audit]. Backlog paths: AgToosa `docs/Master-Plan.md`, Crapsino `docs/PLAN.md`, DreamToosa `Docs/Master-Plan.md`, miToosa `docs/Master-Plan.md`. Top-level `triage` block: `max_items_total: 8`, `max_items_per_repo: 3`, `pr_idle_days: 7`, `routine_gap_days: 2`, `heartbeat_max_age_days: 3`, `trusted_logins: [sky2464, dependabot[bot]]`. `budget.soft_time_box_minutes_fleet_triage: 10`.
- `dreamtoosa/validate.py` (221 to about 300 lines) — guarded checks, run only when the triage block exists: caps are positive ints with total >= per-repo; `pr_idle_days`, `routine_gap_days`, `heartbeat_max_age_days` positive ints; `trusted_logins` non-empty login strings; `stale_after_days < dormant_after_days`, both positive; soft time box positive int; `hub.force_read_only` boolean when present; per repo: `visibility` in {public, private}; `backlog` path relative with no `..`, `header_all` non-empty list, `columns.id/title/status` strings; workflow filenames match `^[\w.-]+\.ya?ml$`; watch kinds valid; `dependabot_scope` in {runtime, dev, unknown} when present. No triage import.
- `dreamtoosa/ROUTINE_PROMPT.md` — ground rules (line 29 replaced by the ten-tool line; new write-boundary rule); Phase 0 and 0.5 (force switch, key defaults); new Phase 1.5; Phase 2 (reuse PR list); Phase 3 (render and inject; private rule); Phase 4 (no triage input); final summary (rank-1 action).
- `dreamtoosa/README.md` — write-boundary and visibility notes. `DreamToosa/.claude/settings.json` is touched only if task 0.3 shows the routine honours deny rules.
- `tests/test_validate.py` — negatives per new check, backward compatibility, subprocess script-mode run, floor raised to the measured count.
- `Docs/Master-Plan.md`, `CHANGELOG.md` — TRI-A-032.
- `.github/workflows/control-plane.yml` — no change in 005a (the existing validate job already runs `unittest discover tests`).

ToolSearch line (exact, ten tools; `update_pull_request` removed; `actions_list` and `search_repositories` added):
`ToolSearch select:mcp__github__list_issues,mcp__github__list_pull_requests,mcp__github__issue_read,mcp__github__pull_request_read,mcp__github__issue_write,mcp__github__add_issue_comment,mcp__github__create_pull_request,mcp__github__get_label,mcp__github__actions_list,mcp__github__search_repositories`

Snapshot (facts only; written to `$SNAP_DIR` from `mktemp -d`; never committed):
```
snapshot.json
  schema "fleet-triage/1" · run_date · execution_mode (READ_WRITE | READ_ONLY)
  timebox {started_epoch, box_minutes, exceeded_section | null}
  hub {validate_exit (0|1|2), engine_clean, liveness_refs [{ref, last_run_date}], open_report_prs (int | null)}
  repos[] {repo, name, enabled, visibility, visibility_check (ok|mismatch|unavailable), dependabot_scope,
    tip {sha, committer_date, prev_committer_date, subject}, hygiene {merged_undeleted, shallow},
    prs {status, reason, open[{number, draft, author, updated_at, head_sha, docs_only, checks[{conclusion}],
         reviews[{login, state}], mergeable_state}], closed_recent[{number, merged_at, head_sha, checks[], changed_non_docs}], deep_reads},
    issues {status, reason, open[{number, title, labels, author, created_at, closed_by_pr}]},
    workflows {status, reason, runs[{workflow, kind, event, head_sha, conclusion, run_id, created_at}], dynamic_ids[]}}
  Excluded: logs, bodies, commit messages, model prose.
  Engine-derived (not model-written): backlog rows, fix links, cron text.
```

Key interfaces:
```
triage.check_snapshot(snap, manifest, clone_root=None) -> list[str]   # fixed codes; [] when valid
triage.parse_backlog(text, mapping) -> list[PlanRow]                 # pure
triage.hub_liveness(refs, run_date) -> (age_days | None, source_ref | None)
triage.evaluate(snap, plan_rows, fix_links, cron, manifest) -> Evaluation
triage_report.main(argv) -> int                 # check | render | heartbeat
triage_report.verify_git(snap, clone_root) -> list[str]
triage_report.render(evaluation, manifest) -> str ; inject(index_path, block) -> None
render also accepts --unavailable CODE (fallback line only)
```

### 2.2 Rule Definitions (normative for TRI-A-004 to TRI-A-025)

Freshness and classes are in 1.2 (TRI-A-013, TRI-A-014). Confidence: API-verified 3, plan-doc 2, UNCONFIRMED 1. Impact codes: I5 data loss or security, I4 user-facing correctness, I3 gates or monitoring, I2 automation.

| Rule | Tier | Impact | Condition | Action template (typed parameters) | Evidence |
|------|------|--------|-----------|-------------------------------------|----------|
| C1 | CRITICAL | I5 | (a) trusted open issue labelled security, critical, P0 or data-loss; (b) open runtime-scope security Dependabot PR older than 3 days; (c) plan row P0 or Critical whose title or evidence matches `data loss|delet|corrupt|leak|secret|credential|auth bypass|injection` and cites file:line | (a) "Triage issue #N in {repo}"; (b) "Review Dependabot PR #N in {repo} (owner decision)"; (c) "{plan_id}: fix and add a regression test" | issue or PR number; plan file:line (`verify`) |
| C2 | CRITICAL | I3 | hub liveness age > 7 days | "Dream Report dark {age} d: check the routine run log and re-authorize GitHub" | state field (`last_run.date`, ref) |
| C3 | CRITICAL | I3 | validate.py exit 1 at Phase 1.5 (exit 2 is E_RUN, not C3) | "Control plane invalid: run validate.py and fix the reported check" | validate exit |
| U1 | URGENT | I3 | latest completed default-branch run of a product workflow concluded failure on the tip, with at least 2 consecutive failures or red for at least 3 days. Red for more than 14 days adds "require this check on main" | "{repo}: {workflow} red on tip for {n} runs since {date}" | run id |
| U2 | URGENT | I3 | hub age above `routine_gap_days` (2) up to 7 days, OR open `dreamtoosa/report-*` PRs >= `hub.max_unmerged_report_prs` (3). An unavailable count leaves only the age branch | "Hub degraded: heartbeat {age} d; {n} open report PRs" | state field or PR count |
| U3 | URGENT | I2 | READY PR idle (`updated_at`) > `pr_idle_days` (7), including hub report PRs | "Decide on PR #N in {repo} (ready, idle {n} d)" | PR number |
| U4 | URGENT | I4 | trusted open issue labelled release-blocker or P0, not already C1 | "Resolve release-blocker issue #N in {repo}" | issue number |
| H1 | HIGH | I3 | any watch_workflows entry with >= 3 consecutive failed push or schedule runs on the default branch. PR-event runs do not reset the streak | "{repo}: {workflow} failing on push for {n} runs" | run ids |
| H2 | HIGH | I3 | PR merged to the default branch in the last 14 days, with zero checks or a failing check on its head SHA, changing a non-docs path. One finding per repo and workflow | "Gate bypass: PRs {list} merged without a green check" | PR numbers |
| H3 | HIGH, UNCONFIRMED | I3 | U1 conditions hold, but the failing run's head SHA is not the tip and no newer run exists | "{repo}: {workflow} red on {sha7}, not tip; dispatch to confirm (owner)" | run id |
| H4 | HIGH | I4 | plan row P0 or Critical, correctness claim with file:line, not meeting C1. Tagged `verify`; `untracked` when no trusted issue cites it | "{plan_id}: fix and add a test (verify)" | plan file:line |
| H5 | HIGH (LOW as CLOSE-CANDIDATE when fix verified) | I4 | trusted bug-labelled issue, not chore-labelled, open > 14 days. Verified fix link present gives CLOSE-CANDIDATE (LOW); unverified link is annotated only | "Triage bug #N in {repo} (open {n} d)"; "Close candidate #N: fix {sha7} on default branch" | issue number; commit SHA |
| H6 | HIGH (MEDIUM when dev-scope) | I2 | `dependabot-updates` (numeric ID from `list_workflows`) with >= 3 consecutive cancelled or failed runs and no open Dependabot PR; scope runtime or unknown | "{repo}: Dependabot updates failing {n} runs; check the update configuration" | run ids (none resolved: NOT_EVALUABLE) |
| H7 | HIGH | I3 | watch entry of kind security with no run for more than twice its cron interval (daily = 1 d, weekly = 7 d; other cron shapes NOT_EVALUABLE) | "{repo}: {workflow} silent {n} d (interval {m} d)" | last run id |

Dedupe, rank and caps follow TRI-A-019 and TRI-A-020. Secret patterns for TRI-A-007: `ghp_`, `github_pat_`, `gh[osur]_`, `sk-ant-`, `AKIA[0-9A-Z]{16}`, `AIza[0-9A-Za-z_-]{35}`, `xox[abp]-`, `-----BEGIN`, and JWT-shaped `eyJ...\.…\.…`.

### 2.3 Data Flow

1. **Phase 0 (unchanged, defaults added):** read repos.yml and state.json. New keys default when absent. `hub.force_read_only` is read here.
2. **Phase 0.5:** the existing auth probe sets EXECUTION_MODE. If `hub.force_read_only` is true, EXECUTION_MODE is READ_ONLY regardless.
3. **Phase 1 (unchanged):** per-repo review.
4. **Phase 1.5 (new, facts only):** `SNAP_DIR=$(mktemp -d)`.
   - a. Integrity (TRI-A-008): `git -C "$CLONE_ROOT/DreamToosa" diff --quiet HEAD -- dreamtoosa/` and `status --porcelain -- dreamtoosa/`. On failure, render E_ENGINE_TAMPERED and skip the engine.
   - b. `python3 "$CLONE_ROOT/DreamToosa/dreamtoosa/validate.py"`: record `hub.validate_exit`. Runs in both modes.
   - c. Liveness: `git -C <hub> fetch origin --quiet`; for-each-ref over origin/main and origin/dreamtoosa/report-*; `git show <ref>:dreamtoosa/state.json` for `last_run.date`.
   - d. Git facts per enabled repo: `fetch origin --quiet`; tip = origin/HEAD, else origin/main; tip and previous commit dates and subject; backlog blob SHA; workflow files for cron; merged-undeleted count; shallow flag. A missing clone is skipped as today.
   - e. API facts (READ_WRITE only; otherwise `status: not_evaluable, reason: READ_ONLY`): open PRs per repo; `pull_request_read` (get, get_check_runs, get_reviews, get_files) for at most 5 oldest non-draft PRs; closed PRs sorted by updated desc, perPage 10, check reads for at most 3 merged in 14 days; open issues (OPEN); `issue_read` for at most 3 trusted bug issues older than 14 days; `actions_list` list_workflows once per repo; list_workflow_runs per product and watch file on the default branch, perPage 10; open report PR count; `search_repositories` with `repo:<owner/name>` for visibility. Before each section, compare `date +%s` with the box; an unfinished section is `not_evaluable, reason: time box`. No log reads.
   - f. Write `$SNAP_DIR/snapshot.json`.
   - g. `python3 "$CLONE_ROOT/DreamToosa/dreamtoosa/triage_report.py" check --snapshot "$SNAP_DIR/snapshot.json" --clone-root "$CLONE_ROOT" --manifest "$CLONE_ROOT/DreamToosa/dreamtoosa/repos.yml"`. Exit 0 continues. Exit 1 gets one repair attempt, then "Fleet Triage unavailable: <CODE>". Exit 2 renders E_RUN.
5. **Phase 2:** the target breaker reuses the Phase 1.5 PR list. The hub breaker is unchanged.
6. **Phase 3:** write the index as today. Then `python3 "$CLONE_ROOT/DreamToosa/dreamtoosa/triage_report.py" render --snapshot "$SNAP_DIR/snapshot.json" --manifest "$CLONE_ROOT/DreamToosa/dreamtoosa/repos.yml" --inject "$CLONE_ROOT/DreamToosa/reports/dream-report-$RUN_DATE.md"`. On failure, rerun with `--unavailable <CODE>`. Per-repo action items draw from triage only for public repos.
7. **Phase 4 (unchanged):** does not read Fleet Triage (TRI-A-012).
8. **Phase 5 and Phase 6 (unchanged):** no new writes, no `execution_mode` field, no chaining change.
9. **Final summary:** "single most important human action" = the rank-1 action template, or "none ranked". No notification in 005a.

### 2.4 Threat Model (STRIDE)

| Threat | Category | Mitigation |
|--------|----------|------------|
| Model mis-copies facts (tip SHA, dates, conclusions) | Spoofing | `check --clone-root` re-derives git facts (TRI-A-007); API facts need run or PR numbers; evidence gate. |
| READ_ONLY or 401 run looks like an all-clear | Spoofing | NOT_EVALUABLE typed in code (TRI-A-021); C2 on liveness. |
| Injection through titles, branch names, plan rows steers severity or text | Tampering | Severity from rules only; trusted-author gate; typed templates; escaping (TRI-A-003 to TRI-A-006). |
| Forged markers or ledger in index | Tampering | Inject touches only the marker block and refuses stray markers (TRI-A-030). |
| Malformed manifest disables every run (Phase 0 fail-safe) | Tampering | Additive guarded keys; backward-compatibility test; validate.py has no triage import. |
| Target-repo code (Phase 1 installs) tampers with the engine | Tampering | Integrity check before the engine runs (TRI-A-008). |
| Private-repo details or secrets published on the public hub | Information disclosure | Visibility gate, fail closed (TRI-A-001, TRI-A-026); security findings withheld (TRI-A-002); secret and path scan (TRI-A-007); no log reads; snapshot never committed. |
| Budget exhaustion (MCP calls, time) | Denial of service | Deep-read caps and time box (TRI-A-022); only manifest workflows fetched. |
| Write-capable tool added to routine | Elevation of privilege | Exact ToolSearch allowlist test (TRI-A-009); no `update_pull_request`; ground rule. |

Claim boundary: rules, validator and render are CI-enforced (unit tests and the validate job). Integrity check, secret scan and verify-git are generator-enforced in code, but the routine must call them (agent-instructed). The ToolSearch allowlist is CI-enforced for the prompt text only. The platform injects `mcp__github__*` tools, so the runtime write boundary is agent-instructed and advisory until task 0.3 answers. Visibility values are manual (0.1).

Delivery risks:
- Routine stays dark (25 days, cause unknown). Task 0.2 is the human gate. 005a alone does not detect darkness outside a run; the CI heartbeat is 005b.
- GitHub disables scheduled workflows after 60 days of repo inactivity, which would also stop the 005b heartbeat. The shared liveness definition is here, so this risk is recorded here. The runbook is 005b.
- Module size: `triage.py` or `triage_report.py` may exceed 450 lines. Stop rule: if either does, stop and return to the owner before splitting. A third module changes the agreed two-file design.
- Chaining stays broken (Phase 6 checks out from a dirty state.json). 005a adds no new remote writes.
- Write boundary is advisory if the routine ignores project deny rules (task 0.3).

### 2.5 Build Scope

```
Ready to proceed — Scope Boundary
Files in scope      : dreamtoosa/triage.py, dreamtoosa/triage_report.py, dreamtoosa/validate.py, dreamtoosa/repos.yml, dreamtoosa/ROUTINE_PROMPT.md, dreamtoosa/README.md, tests/test_triage_rules.py, tests/test_triage_render.py, tests/test_triage_cli.py, tests/test_routine_prompt.py, tests/test_validate.py, tests/fixtures/triage/*, Docs/Master-Plan.md, CHANGELOG.md, Docs/archived/spec-DEV-005a.md, DreamToosa/.claude/settings.json (only if task 0.3 shows deny rules are honoured)
Directories in scope: dreamtoosa/, tests/, Docs/, repo root (CHANGELOG.md)
Out of scope        : .github/ (005b heartbeat job), dreamtoosa/state.json (unchanged), AgToosa, Crapsino and miToosa source trees, existing committed reports
```

---

## Section 3 — Tasks

### 3.1 Task Tree

- [ ] **0.** Wave 0 human prerequisites
  - [ ] 0.1 Confirm each repo's visibility (AgToosa, Crapsino, DreamToosa, miToosa) and record it for repos.yml — _Requirements: TRI-A-001, TRI-A-026_ `[manual]`
  - [ ] 0.2 Restore routine `trig_01PvQiwSRhJktFxMXwxf14Qi`: record why there has been no run since 2026-09-18 (run-log text is data), re-authorize GitHub, run once by hand, confirm Python 3.12 and PyYAML — _Requirements: TRI-A-023, TRI-A-027_ `[manual]`
  - [ ] 0.3 Check with `get_run_log` whether the routine session honours DreamToosa/.claude/settings.json deny rules — _Requirements: TRI-A-009_ `[manual]`
- [ ] **1.** Lifecycle: register the story
  - [ ] 1.1 Register DEV-005a (Active Cycle, DEV-100) and DEV-005b (Backlog) in Master-Plan with an Update Log row; add CHANGELOG [Unreleased] Added and correct the validate.yml reference to control-plane.yml — _Requirements: TRI-A-032_
- [ ] **2.** Deterministic engine (no routine change)
  - [ ] 2.1 Freeze fixtures from the 2026-10-13 probe record: both snapshots, frozen repos-2026-10-13.yml (force_read_only true in the read-only copy), backlog excerpts at pinned tips (AgToosa b257b9d, Crapsino ceb42b3, DreamToosa a8b4beb, miToosa 3886a34). Fields the record lacks are `not_evaluable, reason: not captured`, never invented — _Requirements: TRI-A-021, TRI-A-028_
  - [ ] 2.2 Write failing tests first in the three triage test files — _Requirements: TRI-A-004, TRI-A-013 to TRI-A-030_
  - [ ] 2.3 Implement `dreamtoosa/triage.py` (pure, under 450 lines) — _Requirements: TRI-A-004, TRI-A-005, TRI-A-006, TRI-A-013 to TRI-A-022, TRI-A-024, TRI-A-025, TRI-A-031_
  - [ ] 2.4 Implement `dreamtoosa/triage_report.py` (check, render, heartbeat, `--unavailable`; verify-git; git-based backlog and cron loading; integrity check; inject; under 450 lines) — _Requirements: TRI-A-007, TRI-A-008, TRI-A-010, TRI-A-023, TRI-A-027, TRI-A-029, TRI-A-030_
  - [ ] 2.5 Generate `expected-2026-10-13.md` by running the renderer once on the frozen snapshot; the owner reviews it against the 2.2 rule text — _Requirements: TRI-A-027, TRI-A-028_
- [ ] **3.** Manifest, validator and prompt
  - [ ] 3.1 Add the additive repos.yml keys in 2.1 (visibility from 0.1, backlog mapping per repo, workflow lists, `dependabot_scope`, triage block, `force_read_only: false`, soft time box) — _Requirements: TRI-A-001, TRI-A-003, TRI-A-011, TRI-A-020, TRI-A-021, TRI-A-022, TRI-A-023_
  - [ ] 3.2 Add guarded checks to validate.py, with no triage import — _Requirements: TRI-A-011_
  - [ ] 3.3 Extend tests/test_validate.py: negatives, backward compatibility, subprocess script-mode run, floor raised to the measured count — _Requirements: TRI-A-011_
  - [ ] 3.4 Update ROUTINE_PROMPT.md: ground rules and ten-tool line; Phase 0 and 0.5 force switch; Phase 1.5 steps a to g; Phase 2 reuse; Phase 3 render and inject; Phase 4 exclusion; final summary; absolute paths — _Requirements: TRI-A-008, TRI-A-009, TRI-A-010, TRI-A-012, TRI-A-026, TRI-A-027, TRI-A-029_
  - [ ] 3.5 Add tests/test_routine_prompt.py contract tests — _Requirements: TRI-A-009, TRI-A-010, TRI-A-012, TRI-A-027_
  - [ ] 3.6 Update dreamtoosa/README.md with write-boundary and visibility notes; touch `.claude/settings.json` only if 0.3 says deny rules are honoured — _Requirements: TRI-A-001, TRI-A-009_
- [ ] **4.** Verification, live deploy and acceptance
  - [ ] 4.1 Local READ_ONLY simulation: render `snapshot-read-only.json` with the force-switch manifest in a scratch worktree; confirm "not evaluable" cells, populated freshness, no push — _Requirements: TRI-A-021, TRI-A-027_
  - [ ] 4.2 Run the gates in 3.3 (both unittest forms, validate.py, py_compile) — _Requirements: TRI-A-009, TRI-A-011, TRI-A-028_
  - [ ] 4.3 CI green on the PR (control-plane validate job, Python 3.12, PyYAML only) — _Requirements: TRI-A-011, TRI-A-028_
  - [ ] 4.4 RemoteTrigger get, then update with the full session_context (model, sources, outcomes, allowed_tools unchanged, no `mcp__github__*` added, no PushNotification), then get again and diff — _Requirements: TRI-A-009, TRI-A-023, TRI-A-027_
  - [ ] 4.5 Owner observes one READ_WRITE run: index starts with Fleet Triage; freshness ages match `git log -1`; caps honoured; no golden section — _Requirements: TRI-A-013, TRI-A-020, TRI-A-027_ `[manual]`

### 3.2 Wave Plan

**Wave 0 (human):** 0.1 before 3.1 and 3.6; 0.3 before 3.6; 0.2 before 4.4 and 4.5. Wave 0 is a prerequisite for Wave 2 writes that depend on it.
**Wave 1 (parallel):** 1.1, 2.1, 2.2
**Wave 2 (parallel, after Wave 1):** 2.3, 3.1, 3.2
**Wave 3 (parallel, after Wave 2):** 2.4, 3.3, 3.6
**Wave 4 (parallel, after Wave 3):** 2.5, 3.4
**Wave 5 (parallel, after Wave 4):** 3.5, 4.1
**Wave 6 (after Wave 5):** 4.2
**Wave 7 (after Wave 6):** 4.3
**Wave 8 (after Wave 7):** 4.4, then 4.5 (manual)

### 3.3 Test Plan

Test plan: the three triage test files, `tests/test_validate.py` and `tests/test_routine_prompt.py`. Every group runs offline. Smoke set: the whole suite (unittest has no tag mechanism, so the suite is the smoke set and includes at least one test for every Must AC).

Commands:
```bash
python3 -m unittest discover -s tests                 # DEV-004 form
python3 -m unittest discover tests -v                 # CI form
python3 dreamtoosa/validate.py                        # control plane
python3 -m py_compile dreamtoosa/*.py tests/*.py      # syntax
python3 dreamtoosa/triage_report.py render --snapshot tests/fixtures/triage/snapshot-2026-10-13.json --manifest tests/fixtures/triage/repos-2026-10-13.yml --backlog-dir tests/fixtures/triage/backlog | diff - tests/fixtures/triage/expected-2026-10-13.md && echo GOLDEN_OK
python3 dreamtoosa/triage_report.py check --snapshot tests/fixtures/triage/snapshot-read-only.json --manifest tests/fixtures/triage/repos-2026-10-13.yml; echo "exit $?"   # expect 0
```

| Group | Test (file::class) | ACs |
|-------|--------------------|-----|
| TR-1 | rules: freshness tiers from committer date; docs-only annotation; future clamp | 013 |
| TR-2 | rules: PR blocker order table (draft, failure/timed_out/cancelled/action_required, pending, no-CI, conflict, changes requested overridden by later approval, unknown, docs-only READY); merged_at beats `merged`; self-authored label | 014, 016 |
| TR-3 | rules: latest run per workflow vs tip; streak ignores PR events; pre-tip green; dynamic Dependabot IDs or NOT_EVALUABLE | 015, 016 |
| TR-4 | rules: fix link counted only when verified; unverified changes no tier | 017 |
| TR-5 | rules: C1, C2, C3 fixtures; C3 only on exit 1 | 018, 023 |
| TR-6 | rules: U1, U2 (both branches, unavailable count), U3, U4; H3 UNCONFIRMED | 018, 024 |
| TR-7 | rules: H1, H2 once per repo and workflow, H4, H5 (chore excluded; verified fix gives CLOSE-CANDIDATE LOW) | 018, 025 |
| TR-8 | rules: H6 (dev scope MEDIUM; numeric ID resolution); H7 (cron intervals; unknown shape) | 018 |
| TR-9 | rules: evidence gate caps to MEDIUM; plan-doc cap; backlog parser on frozen excerpts | 018 |
| TR-10 | rules: external authors excluded from C1, U4, H5 and joins; status-needs-triage excluded | 003 |
| TR-11 | rules: dedupe key format; joins only on exact citation | 019 |
| TR-12 | rules: rank order; CRITICAL uncapped; 8 and 3 caps; "+N more"; MEDIUM/LOW counts | 020 |
| TR-13 | rules: NOT_EVALUABLE per section with reasons; READ_ONLY and force switch; security line exact | 021 |
| TR-14 | rules: time box; deep-read caps rejected by check | 022 |
| TR-15 | rules: hygiene count labelled "ancestry-merged only"; shallow clone NOT_EVALUABLE | 031 |
| TR-16 | rules: hub liveness newest valid date; future date rejected; C2 and U2 thresholds in whole days | 023 |
| RN-1 | render: golden output byte-identical; 50 shuffled inputs identical; module size guard under 500 lines | 027, 028 |
| RN-2 | render: READ_ONLY output has no "0 PRs", PASS or green; freshness populated | 021, 027 |
| RN-3 | render: private repo leaks no SHA, path, title, subject or date | 001 |
| RN-4 | render: security findings show category, repo and ID only | 002 |
| RN-5 | render: untrusted text escaped, truncated to 80, no links, flagged | 006 |
| RN-6 | render: actions built only from typed templates | 005 |
| RN-7 | render: inject replaces only the block; E_INJECT_MARKERS on stray markers, nothing written | 030 |
| RN-8 | render: fallback line carries a fixed code, never exception text | 029 |
| CL-1 | cli: exit codes 0, 1, 2; severity key rejected at any depth; schema allowlist | 004, 010 |
| CL-2 | cli: secret patterns and absolute or in-clone paths rejected | 007 |
| CL-3 | cli: verify-git mismatch on tip SHA, committer date, blob SHA and liveness date in a temp git repo | 007 |
| CL-4 | cli: integrity check fails on a modified dreamtoosa/ file before the engine runs | 008 |
| CL-5 | cli: heartbeat passes at 3 days, fails at 4 days and on a future date | 023 |
| CL-6 | cli: script-mode run by absolute path | 010 |
| VA-1 | validate: one negative per new check | 011 |
| VA-2 | validate: no triage block gives no new failures | 011 |
| VA-3 | validate: subprocess script-mode exit 0; source has no triage import | 011 |
| PR-1 | prompt: ToolSearch line equals the ten-tool set; banned names absent (update_pull_request, merge_pull_request, pull_request_review_write, enable_pr_auto_merge, disable_pr_auto_merge, update_pull_request_branch, actions_run_trigger, run_secret_scanning, create_branch, push_files, create_or_update_file, delete_file, get_job_logs, sub_issue_write, update_issue_comment, add_comment_to_pending_review, resolve_review_thread, request_copilot_review, fork_repository, create_repository) | 009 |
| PR-2 | prompt: ground rule forbids approve, merge, review, comment, close, reopen, label, auto-merge, update-branch, dispatch and re-run for Fleet Triage | 009 |
| PR-3 | prompt: every `python3` call uses `"$CLONE_ROOT/DreamToosa/..."` | 010 |
| PR-4 | prompt: Phase 4 text never reads triage; coverage line says not account-wide; no unqualified search; visibility cross-check text present | 012, 026, 027 |

AC coverage: 31 of 32 ACs have at least one test. TRI-A-032 is checked by review of task 1.1.

### 3.4 Work Package DAG

Manual tasks (0.1, 0.2, 0.3, 4.5) have no package rows.

| package_id | wave | depends_on | owned_files | inputs | outputs | merge_order | verification |
|------------|------|------------|-------------|--------|---------|-------------|--------------|
| PKG-1.1 | 1 | — | `Docs/Master-Plan.md`, `CHANGELOG.md` | — | same | 1 | `grep -q 'DEV-005a' Docs/Master-Plan.md` |
| PKG-2.1 | 1 | — | `tests/fixtures/triage/snapshot-2026-10-13.json`, `snapshot-read-only.json`, `repos-2026-10-13.yml`, `backlog/*.md` | probe record | same | 1 | `python3 -m json.tool tests/fixtures/triage/snapshot-2026-10-13.json > /dev/null` |
| PKG-2.2 | 1 | — | `tests/test_triage_rules.py`, `tests/test_triage_render.py`, `tests/test_triage_cli.py` | this spec | same | 1 | `python3 -m py_compile tests/test_triage_rules.py tests/test_triage_render.py tests/test_triage_cli.py` |
| PKG-2.3 | 2 | PKG-2.2 | `dreamtoosa/triage.py` | PKG-2.1, PKG-2.2 | same | 2 | `python3 -m unittest tests.test_triage_rules -v` |
| PKG-3.1 | 2 | — | `dreamtoosa/repos.yml` | task 0.1 values | same | 2 | `python3 -c "import yaml; yaml.safe_load(open('dreamtoosa/repos.yml'))"` |
| PKG-3.2 | 2 | — | `dreamtoosa/validate.py` | — | same | 2 | `python3 dreamtoosa/validate.py` |
| PKG-2.4 | 3 | PKG-2.3 | `dreamtoosa/triage_report.py` | PKG-2.3 | same | 3 | `python3 -m unittest tests.test_triage_cli tests.test_triage_render -v` |
| PKG-3.3 | 3 | PKG-3.1, PKG-3.2 | `tests/test_validate.py` | PKG-3.1, PKG-3.2 | same | 3 | `python3 -m unittest tests.test_validate -v` |
| PKG-3.6 | 3 | — (gated by 0.1, 0.3) | `dreamtoosa/README.md` | task 0.3 result | same | 3 | `grep -q 'write boundary' dreamtoosa/README.md` |
| PKG-2.5 | 4 | PKG-2.4 | `tests/fixtures/triage/expected-2026-10-13.md` | PKG-2.4, PKG-2.1 | same | 4 | `python3 dreamtoosa/triage_report.py render --snapshot tests/fixtures/triage/snapshot-2026-10-13.json --manifest tests/fixtures/triage/repos-2026-10-13.yml --backlog-dir tests/fixtures/triage/backlog \| diff - tests/fixtures/triage/expected-2026-10-13.md` |
| PKG-3.4 | 4 | PKG-2.4, PKG-3.1 | `dreamtoosa/ROUTINE_PROMPT.md` | CLI names; new keys | same | 4 | `grep -q 'Phase 1.5' dreamtoosa/ROUTINE_PROMPT.md` |
| PKG-3.5 | 5 | PKG-3.4 | `tests/test_routine_prompt.py` | PKG-3.4 | same | 5 | `python3 -m unittest tests.test_routine_prompt -v` |
| PKG-4.1 | 5 | PKG-2.4, PKG-3.1 | none in repo (scratch worktree) | `snapshot-read-only.json` | scratch render | 5 | `python3 dreamtoosa/triage_report.py render --snapshot tests/fixtures/triage/snapshot-read-only.json --manifest tests/fixtures/triage/repos-2026-10-13.yml --backlog-dir tests/fixtures/triage/backlog \| grep -c 'not evaluable'` (at least 1) |
| PKG-4.2 | 6 | PKG-2.5, PKG-3.3, PKG-3.5, PKG-4.1 | none (read-only gate) | all | — | 6 | `python3 -m unittest discover -s tests && python3 -m unittest discover tests -v && python3 dreamtoosa/validate.py && python3 -m py_compile dreamtoosa/*.py tests/*.py` |
| PKG-4.3 | 7 | PKG-4.2 | none (PR CI) | PR | CI result | 7 | `gh pr checks <PR-number>` all green |
| PKG-4.4 | 8 | PKG-4.3 | none (RemoteTrigger, outside repo) | merged main | live config | 8 | RemoteTrigger get, update, get, diff: model, sources and allowed_tools unchanged |

---

## Open items

| ID | Item | Owner and gate |
|----|------|----------------|
| OI-1 | Golden formula validation outcome. The plan formula does not select DEV-153 on the real backlogs (runner-up BL-42 scores differently; DEV-150 is ambiguous). Not in 005a. 005b must validate over the full real backlogs before writing its golden fixture. | DEV-005b |
| OI-2 | Visibility of AgToosa, Crapsino, DreamToosa and miToosa. Critic lookups (Crapsino private; DreamToosa, AgToosa, miToosa public) are unverified. | Wave 0 human (task 0.1). Gates 3.1 values. |
| OI-3 | PushNotification works inside RemoteTrigger routines. Not used by 005a. | Wave 0 human. Gates DEV-005b only. |
| OI-4 | Restore the dark routine (25 days; cause unknown). | Wave 0 human (task 0.2). Gates live acceptance 4.5. |
| OI-5 | Existing committed history: `reports/Crapsino/*` and earlier public index files already contain private-repo details (SHAs, findings), and the 2026-09-17 report contains a local CLONE_ROOT path. Found in critic review, not in the interview. 005a does not rewrite or remove history. Keep, redact or remove is an owner decision this spec does not make. | Owner, before task 4.4 |

## Spec quality self-check (pre-approval; the full analyzer runs at approval)

- Every Must AC is observable and has at least one test in 3.3. No open placeholder text remains.
- Goal Contract, non-goals, build scope, ACs, tasks and tests agree. Golden output and pick are deliberately absent from 005a.
- Enforcement claims carry a claim boundary (2.4). Every task traces to at least one AC (3.1).

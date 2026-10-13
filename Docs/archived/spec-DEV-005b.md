# Spec: DEV-005b — Fleet Triage Ledger, Golden Pick, Heartbeat and Notify

> **Story ID:** DEV-005b
> **Epic:** DEV-100 (Multi-repo maintainer routine)
> **Status:** Backlog — spec draft, approval pending (no Spec Approved marker appended)
> **Estimate:** M (build). Effort note in 2.5.
> **Clarity:** `ready` — interview complete. Wave 0 gates and open items OI-1 to OI-6 still gate build and live steps.
> **Spec created:** 2026-10-13
> **Depends on:** **DEV-005a** (`Docs/archived/spec-DEV-005a.md`, IDs `TRI-A-###`). Wave B1 starts only after DEV-005a is merged to DreamToosa `main`. Live steps start only after DEV-005a is live.

---

### Plan-Mode Spec Interview (findings)

#### Inferred (≥80% — no question asked)

| Checklist area | Finding |
|----------------|---------|
| Memory | The routine runs with `persist_session=false`. Committed `dreamtoosa/state.json` and the report index are its only memory (`state.json` `_comment`; `ROUTINE_PROMPT.md` Phase 0). |
| Push gate | READ_ONLY runs never push (`ROUTINE_PROMPT.md:202-205`). A ledger or signal that exists only on a READ_ONLY run is never persisted. |
| Chaining defect | Phase 6 edits `state.json` in the hub working tree, then runs `git checkout -b … "$BASE_REF"` (`ROUTINE_PROMPT.md:192-213`). Git refuses when the base branch's `state.json` differs. No chained READ_WRITE run is on record. Commit `6d01f0c` records a `# Conflicts:` entry naming `dreamtoosa/state.json`. |
| Heartbeat gating | `control-plane.yml` runs on `push` and `pull_request` for `dreamtoosa/**` and `tests/**` (lines 12-23). A heartbeat without event gating would fail on every PR while the routine is dark. |
| Date resolution | `state.json` `last_run.date` is a calendar day (`state.json:5`). The threshold is therefore expressed in days. |
| Committer dates | Hub `origin/main` tip committer date is `2026-09-18 23:31:47 -0500`, which is 2026-09-19 UTC. Dates are compared as UTC dates. |
| Golden pool | AgToosa keeps DEV-153 in the Active Cycle table (`docs/Master-Plan.md:27`), not in Backlog. DEV-150 is `Todo` in Backlog (`:239`) and shipped in Completed This Cycle (`:411`). The pool must read both tables and exclude completed IDs. |
| Backlog paths | AgToosa and miToosa use lowercase `docs/Master-Plan.md`. Crapsino uses `docs/PLAN.md` with findings tables that have a Sev column and no Type column (verified), so it yields no Feature rows. DreamToosa's backlog yields no candidates. |
| Shallow clones | The AgToosa sandbox clone is shallow (verified). The critic reports the same for Crapsino and miToosa. Commit-history evidence can be truncated there. |
| Engine layout | The two-file engine is binding (Q2). Ledger, golden and notify logic must fit `triage.py` under the 500-line rule. See OI-5. |

#### Asked & confirmed

All eight answers come from the user interview and are binding.

| Q# | Question | Answer | Impact on DEV-005b |
|----|----------|--------|--------------------|
| Q1 | Hub visibility and private-repo details | Keep DreamToosa public. Add per-repo `visibility` (public or private) to repos.yml. Fleet Triage omits private-repo details from committed or published output. Wave 0 human check of each repo's visibility before W2. | Ledger keeps private-repo findings as opaque keys only (TRI-B-006). Notify uses opaque keys (TRI-B-021). Gate 0.1. |
| Q2 | Severity engine | Two-file deterministic engine: `triage.py` (pure rules) and `triage_report.py` (CLI, I/O). The LLM gathers facts only. The snapshot rejects severity keys. A golden fixture and a determinism test are required. | Ledger merge, golden score, heartbeat and notify decisions are pure code in `triage.py`. I/O sits in `triage_report.py`. |
| Q3 | Split | DEV-005a = freshness, PR, CI and issues sections, rules C/U/H, caps, render, validator, visibility key, Phase 1.5 and Phase 3 prompt text. DEV-005b = ledger carry-forward, golden pick, daily heartbeat job, PushNotification, chaining fix if needed. | This document. The chaining fix sits here: Phase 6 is not in 005a, and the heartbeat needs daily report branches. |
| Q4 | Dark-routine detection | Daily read-only heartbeat in `control-plane.yml` on schedule and workflow_dispatch. Fails when the freshest `last_run.date` across origin/main and the newest `origin/dreamtoosa/report-*` is older than 3 days. Gated off pull_request. Record GitHub's 60-day schedule caveat. | TRI-B-015 to 019, TRI-B-032. |
| Q5 | Urgent delivery | One gated PushNotification per run, wrapped in `<routine_summary>`. Sent on READ_ONLY runs, an invalid control plane, NEW or ESCALATED CRITICAL or URGENT, or Mondays. Add to routine allowed tools. Wave 0 verification. | TRI-B-020 to 023. Gate 0.2. |
| Q6 | Repo coverage | Manifest-only, with a coverage line. No account-wide discovery. | Heartbeat and notify read repos.yml and hub refs only. No repo discovery. |
| Q7 | PR meaning | READY equals the owner merge decision. Self-authored READY is labelled. READY idle over 7 days is URGENT. Everything else is BLOCKED with one blocker. | No DEV-005b change. Notify counts URGENT findings produced under this rule. |
| Q8 | Issues | Report-only. Fleet Triage never files, comments or updates. Phase 4 is unchanged and never consumes Fleet Triage. | TRI-B-005, TRI-B-014. |

#### Documented assumptions

- **A1** — DEV-005a is merged first and exports the interfaces listed in 2.1 ("Consumed from DEV-005a"). If 005a names differ, reconcile this spec before Wave B1. Accepted because the split was deliberate and 005a is not yet built.
- **A2** — The routine's hub clone may be shallow. Where history is truncated, the commit-date lookup falls back to `last_run.date` and the ref is labelled "commit date unavailable" (TRI-B-015). The CI heartbeat uses full history.
- **A3** — The routine's cron hour is not known to this spec. The heartbeat cron is set after it is read at gate 0.3 (OI-6). The threshold is in whole days, so a few hours of offset does not change the result.
- **A4** — Opaque keys for private repos can be guessed from small subject spaces such as workflow names and numbers. Accepted, because the ledger carries no text and no secret. Recorded as residual risk R8.
- **A5** — READ_ONLY runs compute the ledger locally and never persist it. Their deltas are relative to the last pushed ledger. Accepted. READ_ONLY always sends the one notify push (Q5).
- **A6** — `hub.force_read_only` exists only for the acceptance simulation and is committed as `false` (TRI-B-030).
- **A7** — The DEV-005a snapshot carries `execution_mode` and `hub.validate_ok`. Notify reads both.
- **A8** — CHAIN_BASE refines the plan's "newest unmerged report branch" with an open-PR test and an ancestor test. A merged branch that was not deleted would otherwise revert main's later commits in the next PR. This is a deliberate change from the plan draft.
- **A9** — Phase 0 state read from CHAIN_BASE (TRI-B-025) moves into this story from the plan's deferred list. The ledger's previous-index read and the day-2 idempotency gate both need it.

---

## Section 1 — Requirements

### Goal Contract

| Field | Value |
|-------|-------|
| Goal | Give Fleet Triage cross-run memory and an independent dark-hub signal. Ship: a machine-readable ledger with stable finding IDs and deltas; a golden-feature pick from a validated formula; a daily read-only CI heartbeat; one gated PushNotification per run; and the minimal chaining fix that daily report branches need. |
| User outcome | The solo maintainer sees what is NEW, CARRIED, ESCALATED, DOWNGRADED or RESOLVED each day, with evidence. They get one explainable golden feature, and a CI failure within four days if the hub goes dark, even when the routine itself is dead. |
| Success condition | 1. Two consecutive READ_WRITE runs produce chained report branches, and hub `dreamtoosa/` stays clean (TRI-B-024, 026, 028). 2. A second-day run gives a delta for every prior finding ID. A malformed ledger yields "carry-forward not evaluable" with no crash (TRI-B-002, 003). 3. OI-1 is recorded, and the golden fixture is generated from the rules (TRI-B-009, 013). 4. The heartbeat fails for a fixture 4 days old, passes at 3 days, and never runs on pull_request (TRI-B-017, 018). 5. A force_read_only dry run sends exactly one notify text that matches the template regex, and pushes nothing (TRI-B-020, 021, 030). |
| Proof / evidence | Unit suite green in both forms; `python3 dreamtoosa/validate.py` PASSED; `py_compile` clean; control-plane CI green on the PR with the heartbeat job skipped on pull_request; live run records and heartbeat workflow_dispatch results (3.3). |
| Non-goals | Filing, commenting on, or updating issues or PRs (Q8). Approving, merging, reviewing, enabling auto-merge, updating branches, dispatching or re-running workflows. Account-wide discovery (Q6). Advancing `fix_rotation` on READ_ONLY runs. Security-alert coverage. A second trigger. New `state.json` keys. Changes to target repos. |
| Assumptions | A1 to A7 above. |
| Risks | R1 The routine stays dark; root cause unknown (OI-4). R2 GitHub disables scheduled workflows in public repos after 60 days without repository activity, and a disabled heartbeat cannot alert. The runbook is TRI-B-032. R3 PushNotification is unavailable in RemoteTrigger routines (OI-3). R4 The golden formula fails validation (OI-1). R5 Pure-code line budget (OI-5). R6 Shallow history weakens RESOLVED evidence and commit-date checks (A2). R7 A merged-but-undeleted report branch becomes the chain base (TRI-B-024 rule). R8 Guessable opaque keys (A4). |
| Unresolved questions | OI-1 to OI-6 (Section 4). |

### 1.1 User Stories

- **As a** solo maintainer, **I want** every finding to carry a stable ID and a day-over-day delta **so that** I can see what is new, what persists, and what was resolved with evidence.
- **As a** solo maintainer, **I want** one golden feature per day with an auditable score **so that** the pick follows rules, not model opinion.
- **As a** solo maintainer, **I want** a CI heartbeat that fails when the hub has been silent for more than three days **so that** a dead routine is never silent again.
- **As a** solo maintainer, **I want** at most one push per run, and only for read-only runs, invalid control planes, new or escalated CRITICAL or URGENT findings, or Mondays **so that** alerts stay rare and meaningful.
- **As a** solo maintainer, **I want** daily report branches to chain from the newest unmerged report branch without touching my hub working tree **so that** state survives unmerged report PRs.

### 1.2 Acceptance Criteria (EARS)

Priorities are MoSCoW. IDs are `TRI-B-###` (DEV-005b only). Rule IDs such as C2 and H5 refer to DEV-005a.

| ID | EARS | Priority |
|----|------|----------|
| TRI-B-001 | **WHEN** Phase 3 renders the block, **THE SYSTEM SHALL** write exactly one ledger comment `<!-- fleet-triage-ledger:v1 {json} -->` inside the `fleet-triage` markers. Its JSON holds only `schema`, `run_date`, `findings` (id, rule, sev, first_seen, last_seen, misses, status) and `golden` (id, since, status). IDs are manifest-derived or opaque. All other values are enums, ISO dates or integers. Keys are sorted, and `--` is written as `--`. | Must |
| TRI-B-002 | **WHEN** the ledger is read from CHAIN_BASE, **THE SYSTEM SHALL** require exactly one marker pair and exactly one ledger comment inside it. **IF** the previous index predates DEV-005b and has no ledger, **THEN** every finding is NEW and the render says "baseline (no prior ledger)". **IF** the ledger is malformed or duplicated, **THEN** the render says "carry-forward not evaluable (E_LEDGER_<CODE>)" and sets an integrity flag. It never crashes or silently drops items. | Must |
| TRI-B-003 | **WHEN** findings are computed, **THE SYSTEM SHALL** label each one NEW (no prior ID), CARRIED (same tier), ESCALATED (tier rose), DOWNGRADED (tier fell, naming the rule now applied), or RESOLVED (per TRI-B-004). `first_seen` SHALL be preserved for every ID that existed before. | Must |
| TRI-B-004 | **WHEN** a prior ID is absent this run, **THE SYSTEM SHALL** mark it RESOLVED only if (a) deterministic evidence exists: a default-branch commit message cites the issue or PR as `#N` or `closes/fixes/resolves #N`, or the issue's `closed_by_pull_requests` lists a merged PR, and the fetched history covers `first_seen`; or (b) it was absent on two consecutive evaluated runs. Otherwise it reads "Pending resolution (miss n/2)". A finding whose source section is NOT_EVALUABLE is carried unchanged, and its miss counter does not move. RESOLVED IDs appear once in this run's deltas and are not written into the new ledger. | Must |
| TRI-B-005 | **THE SYSTEM SHALL** treat carry-forward as read-only context. No ledger field or delta SHALL trigger a Phase 4 filing or comment. Finding IDs SHALL only suppress a comment (DEV-005a Phase 4 rule). | Must |
| TRI-B-006 | **WHEN** a finding belongs to a repo whose `visibility` is `private`, **THE SYSTEM SHALL** record it only as `P-` plus the first 12 hex digits of the SHA-256 of its canonical ID, with rule, sev, dates and integers. Subject, title, path, SHA and log text SHALL NOT appear in the ledger, the index block or the notify text. | Must |
| TRI-B-007 | **WHEN** a ledger is written or parsed, **THE SYSTEM SHALL** reject it (exit 1, `E_LEDGER_SCHEMA`) on any key outside the allowlist, any ID not matching the ID pattern in 2.1, any enum outside its set, any non-integer count, or any non-ISO date. | Must |
| TRI-B-008 | **THE SYSTEM SHALL** run the DEV-005a secret-pattern check on the ledger JSON and the notify text before writing or sending. Any match fails with `E_SECRET_PATTERN`. | Must |
| TRI-B-009 | **THE SYSTEM SHALL NOT** write the golden line of `expected-2026-10-13.md` until OI-1 records the golden pick, its term breakdown and the runner-up over frozen copies of all four backlogs at pinned tips. The fixture is then generated from the rules, never copied from the probe narrative. | Must |
| TRI-B-010 | **WHEN** the golden pool is built, **THE SYSTEM SHALL** read Feature-typed rows from the Active Cycle and Backlog tables of each repo's backlog file at the pinned tip, using the DEV-005a parser, keeping only rows whose status is not Done, Shipped, In Progress or Deferred. It SHALL exclude any ID that appears in a Completed or Shipped table, in a released CHANGELOG section, or in `triage.golden_exclude`. | Must |
| TRI-B-011 | **THE SYSTEM SHALL** compute score = 3R + 2S + L + 2P − 3B − 3Rep, with every term derived by code. R = min(2, count of open ≥HIGH findings whose evidence matches the row or its spec by exact issue number, workflow file name or file path). S = 1 if the spec file exists at the tip. L = 1 if the repo is in `triage.upstream_repos`. P = 1 if priority is P0 or Critical. B = min(2, direct depends_on rows not Done) + 1 if the repo has an open CRITICAL or URGENT finding. Rep = 1 if the ledger's `golden.since` is 28 or more days before RUN_DATE with no status change. | Must |
| TRI-B-012 | **THE SYSTEM SHALL** emit exactly one golden line: the highest score, with ties broken by manifest order then plan order. It prints every term and the runner-up, is tagged "low confidence" when the score is 0 or below, and prints "no eligible candidate" when the pool is empty. | Must |
| TRI-B-013 | **WHILE** `triage.golden_formula_validated` is `false`, **THE SYSTEM SHALL** tag the golden line "formula unvalidated". | Must |
| TRI-B-014 | **THE SYSTEM SHALL NOT** pass the golden pick to Phase 4, to Phase 5 fix rotation, to any filing or comment, or to notify. | Must |
| TRI-B-015 | **WHEN** Phase 1.5 or the heartbeat computes hub liveness, **THE SYSTEM SHALL** call the single DEV-005a `hub_liveness` function. Each candidate ref (origin/main and each `origin/dreamtoosa/report-*`) has effective date = min(its `last_run.date`, the UTC date of the last commit touching `dreamtoosa/state.json` on that ref). The newest report ref is chosen by tip committer date, not by name. If that history is unavailable, the ref is labelled "commit date unavailable" and uses `last_run.date`. | Must |
| TRI-B-016 | **IF** any candidate ref has a `last_run.date` later than RUN_DATE + 1 day, **THEN** the heartbeat SHALL exit 1 with `E_FUTURE_DATED`. | Must |
| TRI-B-017 | **WHEN** the heartbeat runs, **THE SYSTEM SHALL** exit 1 if the freshest effective date is more than `heartbeat_max_age_days` days before the UTC run date, or if no readable `state.json` exists on any candidate ref. It exits 0 otherwise and 2 on a usage error. | Must |
| TRI-B-018 | **THE SYSTEM SHALL** run the heartbeat job only on `schedule` and `workflow_dispatch` (an `if:` gate), with `permissions: contents: read`, no secrets, no API calls, `actions/setup-python` 3.12, `pip install pyyaml`, and `timeout-minutes` set. The validate job SHALL NOT run on `schedule`. | Must |
| TRI-B-019 | **WHERE** `triage.heartbeat_max_age_days` is set, **THE SYSTEM SHALL** use it. When absent, the default is 3. The threshold SHALL NOT be hard-coded. | Should |
| TRI-B-020 | **WHEN** a run ends, **THE SYSTEM SHALL** decide `send` in code. `send` is true if EXECUTION_MODE is READ_ONLY, or the control-plane check failed (C3), or any finding is NEW or ESCALATED at tier CRITICAL or URGENT, or RUN_DATE is a Monday (UTC). Otherwise it is false. | Must |
| TRI-B-021 | **WHEN** `send` is true, **THE SYSTEM SHALL** send exactly one PushNotification. Its body is a fixed template filled with reason codes, up to three finding IDs (then "+N more") and integers. It matches `^[A-Za-z0-9:/_.#\- ,]{1,200}$`, uses opaque keys for private repos, and is wrapped in `<routine_summary>` tags. The prompt passes it verbatim. When `send` is false, nothing is pushed. | Must |
| TRI-B-022 | **THE SYSTEM SHALL** add `PushNotification` to the routine's allowed tools. It SHALL NOT add any `mcp__github__*` tool to allowed tools or to the ToolSearch select line. | Must |
| TRI-B-023 | **IF** PushNotification is unavailable in RemoteTrigger routines (OI-3), **THEN THE SYSTEM SHALL** still render the `send` decision in the index, send nothing, and rely on the heartbeat (TRI-B-017) for liveness. | Should |
| TRI-B-024 | **WHEN** EXECUTION_MODE is READ_WRITE and `hub.pr_strategy` is `chain`, **THE SYSTEM SHALL** set CHAIN_BASE to the newest `origin/dreamtoosa/report-*` that has an open hub PR and is not an ancestor of `origin/main`. Otherwise CHAIN_BASE is `origin/main`. It then runs `git -C "$CLONE_ROOT/DreamToosa" worktree add "$WT" -b dreamtoosa/report-$RUN_DATE "$CHAIN_BASE"`, where `WT` comes from `mktemp -d` outside every clone, and writes reports and state only inside `$WT`. In READ_ONLY, the open-PR test is unavailable, so CHAIN_BASE uses the ancestor test only, and is used for reads only. | Must |
| TRI-B-025 | **WHEN** Phase 0 or Phase 1.5 reads `state.json`, **THE SYSTEM SHALL** read it from CHAIN_BASE via `git show`, falling back to `origin/main` only when CHAIN_BASE has none. The Phase 0 idempotency gate uses that copy. | Must |
| TRI-B-026 | **THE SYSTEM SHALL** run `python3 "$WT/dreamtoosa/validate.py"` on the worktree copy before commit, and SHALL NOT commit or push when it exits non-zero. The hub `dreamtoosa/` tree SHALL be unmodified before and after Phase 6 (`git -C "$CLONE_ROOT/DreamToosa" diff --quiet -- dreamtoosa/` and an empty `status --porcelain dreamtoosa/`). | Must |
| TRI-B-027 | **IF** EXECUTION_MODE is READ_ONLY or the hub circuit breaker is tripped, **THEN THE SYSTEM SHALL** create no worktree, no branch and no push (DEV-004 AC-002 and AC-003 unchanged). | Must |
| TRI-B-028 | **WHEN** two READ_WRITE runs occur with no merge between them, **THE SYSTEM SHALL** make the second report branch's parent the first branch's tip. | Must |
| TRI-B-029 | **WHEN** validate.py runs, **THE SYSTEM SHALL** check, when present: `triage.heartbeat_max_age_days` (integer 1 to 14), `triage.golden_exclude` (list of strings), `triage.golden_formula_validated` (boolean), `hub.force_read_only` (boolean), and `last_run.date` (ISO YYYY-MM-DD, not later than the injected today plus one day). Absent keys produce no new failure. validate.py SHALL NOT import any triage module. | Must |
| TRI-B-030 | **WHEN** `hub.force_read_only` is true, **THE SYSTEM SHALL** set EXECUTION_MODE to READ_ONLY regardless of the auth probe. The committed `repos.yml` SHALL keep it `false`. | Must |
| TRI-B-031 | **WHERE** the heartbeat job runs, **THE SYSTEM SHALL** write one `GITHUB_STEP_SUMMARY` line holding the freshest ref name, its effective date and the age in days, with no free text. | Could |
| TRI-B-032 | **THE SYSTEM SHALL** document in `dreamtoosa/README.md` what a failing heartbeat means, the re-enable steps after GitHub's 60-day schedule disable, and the ledger and heartbeat rows of the ownership matrix. | Should |

#### Failure modes (question 5)

| FM | Failure | Guarded by |
|----|---------|------------|
| FM-1 | A forged or truncated ledger hides or fakes carry-forward | TRI-B-002, 005, 007 |
| FM-2 | The routine goes dark and nobody notices | TRI-B-015 to 018, 020 |
| FM-3 | The chain base is wrong, the hub tree gets dirty, or the second run cannot push | TRI-B-024 to 028 |
| FM-4 | The golden pick is a shipped or unvalidated item | TRI-B-009 to 014 |
| FM-5 | Notification spam, or injected text reaches the phone | TRI-B-020 to 023 |
| FM-6 | Private-repo details leak into the ledger or a push | TRI-B-006, 021 |

### 1.3 Out of Scope

- Filing, commenting on, or updating issues or PRs (Q8). Phase 4 filing rules are unchanged.
- The rules, caps, render and liveness definition, which belong to DEV-005a. This story consumes them.
- Advancing `fix_rotation` on READ_ONLY runs, Phase 0 state reads for READ_ONLY runs, and stale profile baselines (deferred in the DEV-005 plan).
- Security-alert coverage, account-wide discovery, a new trigger, and new write tools.
- A third engine module, unless OI-5 is decided.
- Changes to target-repo code. Registering DEV-005b in `Docs/Master-Plan.md` happens at approval, not in this file.

### 1.4 Brownfield Baseline

| Area | Current state (evidence) | Drift against this spec | Resolution |
|------|--------------------------|-------------------------|------------|
| Liveness | `last_run` 2026-09-18, READ_ONLY after a 401 (`state.json` notes). No report since. | No signal exists when the routine is dark. | TRI-B-015 to 018 |
| Chaining | Phase 6 edits `state.json` in the hub tree, then checks out from `BASE_REF` (`ROUTINE_PROMPT.md:192-217`). | Fails on day 2 once the state differs. | TRI-B-024 to 028 |
| CI | `control-plane.yml` runs on push and pull_request only (lines 12-23). | No schedule and no heartbeat. | TRI-B-018 |
| Ledger | None. | No carry-forward is possible. | TRI-B-001 to 008 |
| Notify | None. | READ_ONLY runs are silent. | TRI-B-020 to 023 |

**Source-of-truth boundary:** DreamToosa `Docs/Master-Plan.md` remains the repo-local source of truth. The ledger and report index are evidence, not authority.

### 1.5 Claim Boundary

- Heartbeat exit codes and job gating: **CI-enforced** (workflow plus unit tests in control-plane CI).
- Ledger, golden and notify decisions: **generator-enforced** in code, tested in CI.
- Prompt calls `triage_report`, passes notify text verbatim, and chains via worktree: **agent-instructed**. Only the prompt text is tested.
- Tool allowlist: **CI-enforced on prompt text only**. The live tool boundary is **agent-instructed** unless the DEV-005a Wave 0 check confirms that project deny rules bind routine sessions.
- PushNotification availability in routines: **manual** (gate 0.2).
- Routine cron hour and heartbeat timing: **manual** observation.

---

## Section 2 — Design

### 2.1 Architecture Blueprint

**Files to create**

- `tests/test_triage_ledger.py` — ledger carry-forward, hysteresis, integrity, opaque keys, secret check.
- `tests/test_control_plane_workflow.py` — YAML gating and permissions for `control-plane.yml`.
- `tests/fixtures/triage/backlogs/` — frozen copies of the four real backlog files at pinned tips: AgToosa `docs/Master-Plan.md` @ `9784e2d`, miToosa `docs/Master-Plan.md` @ `3886a34`, Crapsino `docs/PLAN.md` @ `ceb42b3`, DreamToosa `Docs/Master-Plan.md` @ `a8b4beb`. Tips are re-read at build time and recorded in OI-1.
- `tests/fixtures/triage/prev-index-with-ledger.md`, `prev-index-malformed-ledger.md`, `prev-index-private-ledger.md` — index fixtures.
- `tests/fixtures/triage/golden-pool-2026-10-13.json` — pool rows and term values, generated by the rules after OI-1.

**Files to modify** (created by DEV-005a)

- `dreamtoosa/triage.py` — add pure functions: `merge_ledger`, `parse_ledger`, `serialize_ledger`, `golden_pick`, `heartbeat_decision`, `notify_decision`, `notify_message`.
- `dreamtoosa/triage_report.py` — add I/O: CHAIN_BASE selection, prev-index extraction, marker-pair ledger extraction, ledger injection, `heartbeat` and `notify` subcommands, golden section in render.
- `dreamtoosa/repos.yml` — add `triage.heartbeat_max_age_days: 3`, `triage.golden_exclude: []`, `triage.golden_formula_validated: false`, `hub.force_read_only: false`. No new per-repo key: golden reads the existing `backlog_path`.
- `dreamtoosa/validate.py` — about 30 lines of guarded checks (TRI-B-029). The file is 221 lines today, and DEV-005a adds its own checks.
- `dreamtoosa/ROUTINE_PROMPT.md` — Phase 0 (CHAIN_BASE state read and idempotency gate), Phase 0.5 (force switch), Phase 3 (prev-index extraction, golden and ledger inject), Phase 6 (worktree, `$WT` validator, copy and cleanup), a notify gate before the Final summary, and the Final summary (notify text verbatim). The ToolSearch line is not changed.
- `dreamtoosa/README.md` — ownership matrix rows, heartbeat runbook, 60-day caveat, PushNotification deploy note.
- `.github/workflows/control-plane.yml` — `schedule`, `workflow_dispatch`, `validate` gate, and `heartbeat` job.
- `tests/test_validate.py` — 005b negatives, backward compatibility, script-mode subprocess, AST check for no triage import.
- `tests/test_triage_rules.py`, `tests/test_triage_cli.py`, `tests/test_routine_prompt.py` (DEV-005a) — 005b cases added.
- `CHANGELOG.md` — one `[Unreleased] Added` line at ship.
- Live trigger `trig_01PvQiwSRhJktFxMXwxf14Qi` (outside the repo) — `allowed_tools` gains `PushNotification`, applied with the full `session_context` (gate 8.1).

**Consumed from DEV-005a** (reconcile per A1)

- `hub_liveness(refs, today)` — pure function returning the freshest effective date. Phase 1.5 (C2 and U2) and the heartbeat both call it.
- Snapshot schema with per-section `evaluable` flags, per-finding `rule`, `tier`, `evidence` and repo `visibility`, plus `execution_mode` and `hub.validate_ok`.
- Backlog parser returning typed rows (id, type, priority, status, depends_on, section).
- Secret-pattern check and the `check` subcommand.
- Render and marker inject (`<!-- fleet-triage:begin -->` and `:end`). Section 5 is reserved as "Golden feature: not produced (DEV-005b)".
- `triage.upstream_repos` and repo `visibility` in repos.yml.
- DEV-005a does not define `heartbeat_max_age_hours`. The threshold key is `heartbeat_max_age_days`, introduced here.

**Key interfaces** (DEV-005b)

- `merge_ledger(findings, not_evaluable_rules, prev_ledger, run_date) -> (deltas, ledger)`
- `parse_ledger(block_text) -> Ledger | LedgerError(code)`; `serialize_ledger(ledger) -> str`
- `golden_pick(pool, findings, ledger, cfg, spec_exists, run_date) -> Golden`
- `heartbeat_decision(refs, today, max_age_days) -> Heartbeat(ok, code, detail)`; each ref carries its effective date from `hub_liveness`
- `notify_decision(read_only, c3_failed, deltas, run_date) -> Notify(send, reasons)`; `notify_message(reasons, ids, run_date) -> str`
- CLI: `PYTHONPATH="$CLONE_ROOT/DreamToosa" python3 -m dreamtoosa.triage_report heartbeat --repo-root DIR [--today YYYY-MM-DD]` exits 0, 1 or 2. `… notify --snapshot S --prev-index P [--today D]` prints `{"send": bool, "message": str}`.
- ID pattern: `^(P-[0-9a-f]{12}|[CUH][1-7]:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+:[A-Za-z0-9_.#/-]{1,80})$`

### 2.2 Data Flow

1. **Phase 0.** Resolve `CLONE_ROOT`. Read `repos.yml` from the hub working tree. Compute CHAIN_BASE (TRI-B-024). Read `state.json` from CHAIN_BASE via `git show` (TRI-B-025). Run the idempotency gate on that copy.
2. **Phase 0.5.** Run the auth probe. If `hub.force_read_only` is true, set EXECUTION_MODE to READ_ONLY (TRI-B-030).
3. **Phase 1.5.** Run the validate probe, which sets `hub.validate_ok`. Call `hub_liveness` for C2 and U2. Gather facts into the scratch snapshot (DEV-005a). Liveness uses the same function as the heartbeat.
4. **Phase 3.** Write the index to hub `reports/` as today (DEV-005a). Extract the chain-base index to `$SCRATCH/prev-index.md` with `git -C "$CLONE_ROOT/DreamToosa" show "$CHAIN_BASE:reports/dream-report-<prev>.md"`, choosing the newest one dated before RUN_DATE. Run `PYTHONPATH="$CLONE_ROOT/DreamToosa" python3 -m dreamtoosa.triage_report render --snapshot "$SNAP" --prev-index "$SCRATCH/prev-index.md" --manifest "$CLONE_ROOT/DreamToosa/dreamtoosa/repos.yml" --inject "$CLONE_ROOT/DreamToosa/reports/dream-report-$RUN_DATE.md"`. Render computes deltas and the golden pick, then injects the block with its ledger comment.
5. **Phase 6, READ_WRITE chain.** `WT=$(mktemp -d)`. Run `worktree add` from CHAIN_BASE. Copy hub `reports/` and `state.json` into `$WT`. Update state inside `$WT`. Run `python3 "$WT/dreamtoosa/validate.py"`. Commit, push, open the PR. Run `git worktree remove` after a successful push. The hub `dreamtoosa/` tree is never written.
6. **Notify gate.** Run `PYTHONPATH="$CLONE_ROOT/DreamToosa" python3 -m dreamtoosa.triage_report notify --snapshot "$SNAP" --prev-index "$SCRATCH/prev-index.md" --today "$RUN_DATE"`. If `send` is true, send one PushNotification with the message verbatim inside `<routine_summary>` tags.
7. **Heartbeat (CI, independent).** On schedule or dispatch: checkout with `fetch-depth: 0`, then fetch `refs/heads/dreamtoosa/report-*` into `refs/remotes/origin/dreamtoosa/report-*`. Then run `PYTHONPATH="$GITHUB_WORKSPACE" python3 -m dreamtoosa.triage_report heartbeat --repo-root "$GITHUB_WORKSPACE" --today "$(date -u +%F)"`. Its exit code gates the job.

### 2.3 Threat Model (STRIDE)

| Threat | Category | Mitigation |
|--------|----------|------------|
| Forged or edited ledger in the index | Tampering | One marker pair and one ledger comment (TRI-B-002). Strict allowlist parse (TRI-B-007). Inject refuses marker strings outside the block (DEV-005a `E_INJECT_MARKERS`). Carry-forward is read-only (TRI-B-005). |
| Future-dated or back-dated `state.json` hides darkness | Spoofing | Effective date is min with commit date (TRI-B-015). Future-dated fails (TRI-B-016). Newest report ref is chosen by committer date, not name. validate.py date check (TRI-B-029). |
| Dark hub goes unnoticed | Repudiation | Independent CI heartbeat (TRI-B-017, 018). Notify on READ_ONLY (TRI-B-020). The 60-day disable is risk R2, with a runbook (TRI-B-032). |
| Private-repo details in ledger or push | Information disclosure | Opaque keys (TRI-B-006). Notify uses opaque keys (TRI-B-021). Tests assert no subject, title, path or SHA text for a private fixture. Residual risk R8 (A4). |
| Secret in ledger or notify text | Information disclosure | Secret-pattern check on both (TRI-B-008). The pattern set is DEV-005a's: `ghp_`, `github_pat_`, `gh[osur]_`, `sk-ant-`, `AKIA`, `AIza`, `xox[abp]-`, `-----BEGIN`, and JWT-shaped strings. |
| Heartbeat gains write scope or runs on PRs | Elevation of privilege | `if:` gate (TRI-B-018). `contents: read` only. No secrets. No API calls. |
| Notification text injected, or push fatigue | Tampering, Denial of service | Fixed template, regex, IDs and integers only (TRI-B-021). One push per run. Notify gate (TRI-B-020). |
| Chain writes clobber the hub or ship invalid state | Tampering | Worktree from CHAIN_BASE (TRI-B-024). Hub `dreamtoosa/` clean check (TRI-B-026). Validator runs on the `$WT` copy (TRI-B-026). CHAIN_BASE excludes merged branches (TRI-B-024). |
| Golden pick steers filing or triage | Tampering | Golden never feeds Phase 4, Phase 5 or notify (TRI-B-014). The formula is validated before the fixture is written (TRI-B-009). |

### 2.4 Build Scope

```
Scope boundary (pending approval; Part 4 of /agtoosa-spec derives the final block)
Files in scope      : dreamtoosa/triage.py, dreamtoosa/triage_report.py (DEV-005a files, extended);
                      dreamtoosa/repos.yml, dreamtoosa/validate.py, dreamtoosa/ROUTINE_PROMPT.md,
                      dreamtoosa/README.md, .github/workflows/control-plane.yml, CHANGELOG.md;
                      tests/test_triage_ledger.py, tests/test_triage_rules.py, tests/test_triage_cli.py,
                      tests/test_routine_prompt.py, tests/test_control_plane_workflow.py,
                      tests/test_validate.py, tests/fixtures/triage/**
Directories in scope: dreamtoosa/, tests/, .github/workflows/
Out of scope        : dreamtoosa/state.json (no schema change), dreamtoosa/dreamer.py, reports/**
                      (written only by the routine), target repositories, Docs/Master-Plan.md
                      (registration at approval), live trigger edits beyond allowed_tools in gate 8.1
```

### 2.5 Effort and Delivery Risk

- **Build estimate: M.** The critic sized the whole DEV-005 as L. The split in Q3 gives 005a and 005b separate estimates. This story carries the golden formula validation (gate 1.2) and the chain fix.
- **Outside the build estimate:** three Wave 0 human gates and two calendar days of live acceptance (8.3 to 8.5).
- **Moves to L:** a triggered OI-5 module decision, or a formula that fails validation and needs an amendment.

---

## Section 3 — Tasks

### 3.1 Task Tree

- [ ] **0.** Wave 0 human gates (no code; manual)
  - [ ] 0.1 Confirm each repo's visibility. The critic reports Crapsino private and DreamToosa public; this is not verified. — _Requirements: TRI-B-006_ `[manual]`
  - [ ] 0.2 Verify PushNotification works from a RemoteTrigger routine and can be added to `allowed_tools`. — _Requirements: TRI-B-021, TRI-B-022, TRI-B-023_ `[manual]`
  - [ ] 0.3 Restore the routine: `RemoteTrigger` get, list_runs and get_run_log; re-authorize GitHub; one manual READ_WRITE run; read the cron hour. — _Requirements: TRI-B-017, TRI-B-024_ `[manual]`
- [ ] **1.** Golden formula validation (precedes any golden fixture)
  - [ ] 1.1 Freeze the four backlog files at pinned tips under `tests/fixtures/triage/backlogs/`. — _Requirements: TRI-B-009, TRI-B-010_
  - [ ] 1.2 Run `golden_pick` over the frozen files through the DEV-005a parser. Record the pick, its terms and the runner-up per repo in OI-1. — _Requirements: TRI-B-009, TRI-B-011, TRI-B-012_
  - [ ] 1.3 If the record shows the pick is not defensible, stop and amend this spec before 3.3. — _Requirements: TRI-B-009, TRI-B-013_
- [ ] **2.** Ledger
  - [ ] 2.1 Write failing tests in `tests/test_triage_ledger.py`. — _Requirements: TRI-B-001 to TRI-B-008_
  - [ ] 2.2 Implement `merge_ledger`, `parse_ledger` and `serialize_ledger` in `triage.py` (pure). — _Requirements: TRI-B-001, TRI-B-003, TRI-B-004, TRI-B-006, TRI-B-007_
  - [ ] 2.3 Implement prev-index extraction, marker-pair parsing and ledger injection in `triage_report.py`. — _Requirements: TRI-B-002, TRI-B-005, TRI-B-008_
- [ ] **3.** Golden pick
  - [ ] 3.1 Write failing golden tests in `tests/test_triage_rules.py`. — _Requirements: TRI-B-010 to TRI-B-014_
  - [ ] 3.2 Implement `golden_pick` in `triage.py`, and the golden section in render. — _Requirements: TRI-B-010 to TRI-B-013_
  - [ ] 3.3 After 1.3 passes, generate `golden-pool-2026-10-13.json` and the golden line of `expected-2026-10-13.md` from the rules. — _Requirements: TRI-B-009, TRI-B-012_
- [ ] **4.** Heartbeat and notify
  - [ ] 4.1 Write failing tests in `tests/test_triage_cli.py`. — _Requirements: TRI-B-015 to TRI-B-021_
  - [ ] 4.2 Implement `heartbeat_decision`, `notify_decision` and `notify_message` in `triage.py`. — _Requirements: TRI-B-015 to TRI-B-017, TRI-B-019, TRI-B-020, TRI-B-021, TRI-B-031_
  - [ ] 4.3 Add the `heartbeat` and `notify` subcommands to `triage_report.py`. — _Requirements: TRI-B-015, TRI-B-017, TRI-B-020, TRI-B-021_
- [ ] **5.** Manifest and validator
  - [ ] 5.1 Add the four repos.yml keys. — _Requirements: TRI-B-010, TRI-B-013, TRI-B-019, TRI-B-030_
  - [ ] 5.2 Write negative and compatibility tests in `tests/test_validate.py`, then the `validate.py` checks. — _Requirements: TRI-B-029_
- [ ] **6.** Chaining fix and routine prompt
  - [ ] 6.1 Write failing prompt-text tests in `tests/test_routine_prompt.py`. — _Requirements: TRI-B-021 to TRI-B-027, TRI-B-030_
  - [ ] 6.2 Rewrite Phase 0, Phase 0.5, Phase 3 extraction, Phase 6 (worktree), the notify gate and the Final summary in `ROUTINE_PROMPT.md`. — _Requirements: TRI-B-021, TRI-B-023 to TRI-B-027, TRI-B-030_
  - [ ] 6.3 Local two-run chain dry run against a bare scratch remote (no push to origin). — _Requirements: TRI-B-024, TRI-B-026, TRI-B-028_
- [ ] **7.** Heartbeat workflow and docs
  - [ ] 7.1 Write failing YAML tests in `tests/test_control_plane_workflow.py`. — _Requirements: TRI-B-018_
  - [ ] 7.2 Add `schedule`, `workflow_dispatch`, the validate gate and the heartbeat job to `control-plane.yml`. — _Requirements: TRI-B-018, TRI-B-031_
  - [ ] 7.3 Update `dreamtoosa/README.md`: ownership matrix, heartbeat runbook, 60-day caveat, PushNotification note. — _Requirements: TRI-B-022, TRI-B-032_
- [ ] **8.** Live deploy and acceptance (after gates 0.1 to 0.3 and the DEV-005b merge)
  - [ ] 8.1 `RemoteTrigger` get; update with the full `session_context` plus PushNotification; get again and diff. — _Requirements: TRI-B-022_ `[manual]`
  - [ ] 8.2 Notify dry run: local copy with `hub.force_read_only: true`. Expect one send with the READ_ONLY reason, and no push. — _Requirements: TRI-B-020, TRI-B-021, TRI-B-030_
  - [ ] 8.3 Two consecutive READ_WRITE runs with no merge between them. — _Requirements: TRI-B-024, TRI-B-026, TRI-B-028_ `[manual]`
  - [ ] 8.4 Heartbeat `workflow_dispatch`: red before recovery (`last_run` 2026-09-18 is 25 days old), green after a run lands. — _Requirements: TRI-B-017_ `[manual]`
  - [ ] 8.5 Next-day run: every prior finding ID has a delta, and carry-forward triggers no Phase 4 filing. — _Requirements: TRI-B-003, TRI-B-005_ `[manual]`
- [ ] **9.** Verification gate
  - [ ] 9.1 Both unit forms green; `py_compile` clean; `validate.py` PASSED. — _Requirements: TRI-B-029_
  - [ ] 9.2 control-plane CI green on the PR, with the heartbeat job skipped on pull_request. — _Requirements: TRI-B-018_
  - [ ] 9.3 Hub `dreamtoosa/` clean check after the build. — _Requirements: TRI-B-026_

### 3.2 Wave Plan

Prerequisite (not a sub-task): DEV-005a merged to DreamToosa `main`.

- **Wave 0 (human, parallel to B1):** 0.1, 0.2, 0.3. Gate 0.1 also blocks any live render of private-repo findings. Gates 0.2 and 0.3 block Wave B6.
- **Wave B1 (parallel, after DEV-005a merged):** 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1.
- **Wave B2 (parallel lanes):**
  - Sequential chain on `triage.py`, in this order: 2.2, then 3.2, then 4.2. The three share one file, so this is a sequential fallback, not a parallel wave.
  - 5.2 (`validate.py`, `test_validate.py`) and 7.2 (`control-plane.yml`) in parallel with that chain.
- **Wave B3 (parallel lanes):**
  - Sequential chain on `triage_report.py`: 2.3, then 4.3. Sequential fallback, as above.
  - 1.2 (formula run, which needs 3.2) and 7.3 (README) in parallel with that chain.
- **Gate 1.3** sits between B3 and B4.
- **Wave B4 (parallel):** 3.3 (needs 1.2 and gate 1.3) and 6.2 (needs 2.3, 4.3 and 6.1).
- **Wave B5 (local gates, then PR):** 6.3, 8.2, 9.1, 9.2 and 9.3.
- **Wave B6 (live, after Wave 0 and the merge):** 8.1, then 8.3 to 8.5. 8.1 needs gate 0.2 passed.

The Work Package DAG is derived at approval (agent-instructed). The overlaps on `triage.py` and `triage_report.py` are handled above as sequential fallbacks.

### 3.3 Test Plan

Test plan: inline in this section, mirroring DEV-004. AC coverage: 32 ACs, each mapped to at least one test or manual gate. Tests use `unittest`, with `tests/__init__.py` present.

**Commands**

```bash
python3 -m py_compile dreamtoosa/*.py tests/*.py
python3 dreamtoosa/validate.py
python3 -m unittest discover tests -v
python3 -m unittest discover -s tests
python3 -m unittest tests.test_triage_ledger tests.test_triage_rules tests.test_triage_cli -v
python3 -m unittest tests.test_routine_prompt tests.test_control_plane_workflow tests.test_validate -v
git -C "$CLONE_ROOT/DreamToosa" diff --quiet -- dreamtoosa/ && test -z "$(git -C "$CLONE_ROOT/DreamToosa" status --porcelain dreamtoosa/)" && echo HUB_ENGINE_CLEAN
PYTHONPATH="$CLONE_ROOT/DreamToosa" python3 -m dreamtoosa.triage_report heartbeat --repo-root "$CLONE_ROOT/DreamToosa" --today 2026-10-13; echo "exit=$?"
PYTHONPATH="$CLONE_ROOT/DreamToosa" python3 -m dreamtoosa.triage_report notify --snapshot "$CLONE_ROOT/DreamToosa/tests/fixtures/triage/snapshot-read-only.json" --prev-index "$CLONE_ROOT/DreamToosa/tests/fixtures/triage/prev-index-with-ledger.md" --today 2026-10-13
```

Expected results after the build, on the current hub: the heartbeat command exits 1 (25 days stale). The notify command prints `"send": true` with the READ_ONLY reason.

**Test groups**

- **`tests/test_triage_ledger.py`**
  - `TestLedgerCarryForward` (001, 003): NEW, CARRIED, ESCALATED, DOWNGRADED (rule named), `first_seen` kept.
  - `TestResolution` (004): evidence-based RESOLVED; two-miss RESOLVED; NOT_EVALUABLE is not a miss; RESOLVED is not carried into the new ledger; commit evidence refused when history does not cover `first_seen`.
  - `TestLedgerIntegrity` (002, 007, 008): duplicate pair; nested or forged marker; extra key; `-->` in a value; bad ID; bad enum; secret pattern; baseline with no ledger.
  - `TestPrivateOpaqueKeys` (006): for a private fixture, the index block, ledger and notify text contain no subject, title, path or SHA.
  - `TestSerializeRoundTrip` (001): write, read, write is byte-identical; `--` is escaped.
- **`tests/test_triage_rules.py` (golden)**
  - `TestGoldenPool` (010): Active Cycle rows included; a Completed-table row excluded (DEV-150 fixture); `golden_exclude` honoured.
  - `TestGoldenTerms` (011, 012): each term; runner-up printed; ties by manifest then plan order; score ≤0 flagged low confidence.
  - `TestGoldenEmpty` (012): "no eligible candidate".
  - `TestGoldenUnvalidatedTag` (013): tag present while the flag is false.
  - `TestGoldenNotFed` (014): pick absent from Phase 4 and Phase 5 text and from notify output.
  - `TestGoldenFixture` (009): `golden-pool-2026-10-13.json` equals the rule output.
  - `TestGoldenPermutations` (011): 50 shuffled inputs give byte-identical output.
- **`tests/test_triage_cli.py`**
  - `TestHeartbeatThreshold` (017, 019): age 3 passes, age 4 fails; threshold read from repos.yml; default 3 when absent.
  - `TestFutureDated` (016): `E_FUTURE_DATED`.
  - `TestNoState` and `TestMainOnlyStale` (017): exit 1 with a fixed message.
  - `TestReportRefByCommitterDate` (015): newest by committer date, not name; name and date mismatch fixture.
  - `TestSharedLiveness` (015): heartbeat and render call the same `hub_liveness` and agree on one fixture.
  - `TestCommitDateUnavailable` (015): label set; falls back to `last_run.date`.
  - `TestNotifyDecision` (020): READ_ONLY, C3, NEW CRITICAL, ESCALATED URGENT, DOWNGRADED (no send), 2026-10-12 (Monday, send), 2026-10-13 (no send with no other reason).
  - `TestNotifyMessage` (021): regex; 200-character cap; IDs and integers only; opaque keys for private repos; "+N more".
- **`tests/test_control_plane_workflow.py`**
  - `TestHeartbeatGating` (018): `on` has schedule and workflow_dispatch; heartbeat `if:` excludes push and pull_request; validate `if:` excludes schedule.
  - `TestHeartbeatPermissions` (018): `contents: read` only; no secrets; setup-python 3.12; `pip install pyyaml`; `timeout-minutes` set; no `gh`, `curl` or `mcp` call.
  - `TestStepSummaryFixed` (031): summary line uses fixed keys only.
  - `TestRunbookPresent` (032): README names the 60-day schedule disable, the re-enable step and the heartbeat failure meaning.
- **`tests/test_routine_prompt.py` (extends DEV-005a)**
  - `TestToolSearchUnchanged` (022): select line equals the DEV-005a allowlist; no `mcp__github__*` added.
  - `TestChainWorktree` (024 to 027): Phase 6 uses `worktree add` from CHAIN_BASE; no `checkout -b` on the hub; validator runs on `"$WT"`; no hub `state.json` write; READ_ONLY branch absent; CHAIN_BASE rules present (open PR and ancestor check).
  - `TestPythonPathsAbsolute` (026): every `python3` line is rooted at `$CLONE_ROOT` or `$WT`, or uses an absolute `PYTHONPATH`.
  - `TestNotifyVerbatim` (021, 023): one PushNotification, text passed verbatim inside `<routine_summary>`; fallback text when PushNotification is unavailable.
  - `TestForceReadOnlyPhase05` (030): Phase 0.5 forces READ_ONLY when the flag is true.
- **`tests/test_validate.py`**
  - `TestNew005bKeys` (029): negatives for `heartbeat_max_age_days` at 0, 15 and `"3"`; `golden_exclude` as a string; `golden_formula_validated` as `"yes"`; `force_read_only` as `"true"`; `last_run.date` as `"2026-13-40"`; a future date against an injected today.
  - `TestBackwardCompatibility` (029): with the keys removed, no new failure.
  - `TestScriptModeSubprocess` (029): `python3 dreamtoosa/validate.py` exits 0 from the repo root.
  - `TestNoTriageImport` (029): AST check that `validate.py` imports no triage module.
- **Size guard (DEV-005a):** covers all new and changed `dreamtoosa/*.py` and `tests/*.py` files under 500 lines.

**Manual acceptance (Wave B5 and B6)**

- 6.3 chain dry run: in a scratch directory, create a bare remote and a clone of the hub with `main` pushed. Run the Phase 6 steps for RUN_DATE 2026-10-13 and then 2026-10-14. Verify the second branch's parent equals the first branch's tip. Verify the hub `dreamtoosa/` check is still clean.
- 8.2 notify dry run: local copy with `force_read_only: true`. Verify one send with the READ_ONLY reason and no push.
- 8.3 to 8.5: live steps, as listed in 3.1.

---

## Section 4 — Open Items

Nothing here is answered. Each item names what it blocks.

| ID | Open item | State | Blocks |
|----|-----------|-------|--------|
| OI-1 | **Golden formula validation outcome.** Critic evidence (to be re-verified at gate 1.2): under the plan's rules, DEV-153 scores 0 (R = 0, because its row cites nothing and its spec cites `test.yml`, not the finding evidence), so it is low confidence. miToosa BL-24 (P1) scores −3 and BL-42 (P0) scores −4 under the plan's arithmetic. DEV-150 is shipped (`docs/Master-Plan.md:411`) but `Todo` in Backlog (`:239`), so completion detection must exclude it. | OPEN. Not validated. | 3.3; TRI-B-013 stays active until the owner records validation and sets `triage.golden_formula_validated: true`. |
| OI-2 | **Visibility of Crapsino and DreamToosa.** The critic reports Crapsino private and DreamToosa public, from a repo-qualified search. Not verified in this spec. | OPEN. Wave 0 human check. | Gate 0.1; TRI-B-006 live use; Wave B6. |
| OI-3 | **PushNotification in RemoteTrigger routines.** Unverified. | OPEN. Wave 0 human check. | Gate 0.2; TRI-B-022 live update. TRI-B-023 applies if it fails. |
| OI-4 | **Restoring the dark routine.** Last run 2026-09-18, READ_ONLY after a 401. Root cause unknown. | OPEN. Wave 0 human action. | Gate 0.3; Wave B6. The heartbeat stays red until a run lands. |
| OI-5 | **Line budget under Q2 (spec-raised).** The two-file engine is binding. DEV-005a plus DEV-005b pure code may exceed 500 lines in `triage.py`. | OPEN. Decision required if `triage.py` passes 480 lines at the start of B2. Options: (a) owner permits a third pure module, which amends Q2; (b) trim the code. Not answered here. | B2 and the 500-line guard. |
| OI-6 | **Routine cron hour and heartbeat cron (spec-raised).** Unknown. Proposed rule for owner confirmation: the heartbeat runs at least 6 hours after the routine's scheduled start. | OPEN. Read at gate 0.3. | Heartbeat `cron:` value in TRI-B-018. |

# Master-Plan

> **Source of truth for active work.** Completed work lives in `Docs/archived/` — see Completed This Cycle for links.
> **Last updated:** 2026-10-14 05:05

## Project Charter

| Field | Value |
|-------|-------|
| Product | DreamToosa |
| Goal | Act as the control plane for the multi-repo maintainer routine "Dream Report – Daily Code Review" (`trig_01PvQiwSRhJktFxMXwxf14Qi`) |
| User outcome | One daily consolidated code-health report across several repos, with bounded, reviewable fix PRs — instead of per-repo PR backlogs nobody merges |
| Success condition | A routine run reviews every enabled repo in `dreamtoosa/repos.yml`, produces one report + at most one fix PR, and records state so the next run resumes rather than re-derives |
| Proof / evidence | `RemoteTrigger list_runs` + `get_run_log` showing `git -C` against each clone; `reports/<repo>/` populated for all targets; circuit breaker skipping a backlogged repo |
| Non-goals | Merging PRs on the user's behalf; consolidating this repo's legacy Dreams docs; a hosted orchestrator or swarm runtime |
| Assumptions | Cloud sandbox clones every `sources` repo to `/home/user/<name>`; `mcp__github__*` is platform-injected; `gh` CLI is not authenticated |
| Risks | AgToosa's open PR backlog and intermittent red `validate` on `main`; five-repo runs may exceed the per-run time box; Dreams API remains beta-gated; GitHub MCP 401 forces read-only maintainer runs |
| Unresolved questions | AgToosa remains `fix_eligible: false` while its PR backlog drains; optional: attach RemoteTrigger run log as supplemental audit artifact |
| GitHub repo | https://github.com/sky2464/DreamToosa |
| Milestone | v0.1.1 (DEV-005 shipped) |
| Active cycle | Multi-repo routine enablement |
| Cycle state | Active — DEV-005a in progress |
| Cycle capacity | 5 story points |
| Current phase | ✏️ Spec · 🏗️ Build · 🔍 Review · **🚢 Ship** (idle) |

> **Cycle state contract:** use `Active` while a story is enrolled; use `Idle — <reason>` only when an empty cycle is intentional.

## Active Cycle

> Stories committed to the current sprint/cycle.
> **Progress:** `▰▱▱▱▱▱▱▱ 2/20 tasks` ← DEV-005a; updated by `/agtoosa-build` after each task completes

| ID | Title | Type | Estimate | Status | Tasks Done |
|----|-------|------|----------|--------|-----------|
| DEV-005a | Feature: Fleet Triage report core (sections, severity engine, visibility key) | Feature | L | 🟨 In Progress | 2/20 |

Status key: ⬜ Backlog · 🟦 Todo · 🟨 In Progress · ✅ Done · 🚫 Blocked · 🔧 Awaiting Manual · 🏁 Shipped

## Active Tasks

> Task breakdown for the current In Progress story, DEV-005a (`Docs/archived/spec-DEV-005a.md`). Created by `/agtoosa-spec` (Part 4).
> Updated by `/agtoosa-build` — each completed sub-task gets `- [x]`.

- [ ] **0.** Wave 0 human prerequisites
  - [x] 0.1 Confirm each repo's visibility; verified 2026-10-13 by repo-qualified `search_repositories`: AgToosa public, Crapsino private, DreamToosa public, miToosa public `[manual-done]`
  - [ ] 0.2 Restore routine `trig_01PvQiwSRhJktFxMXwxf14Qi` (dark since 2026-09-18), re-authorize GitHub, run once by hand, confirm Python 3.12 and PyYAML `[manual]`
  - [ ] 0.3 Check with `get_run_log` whether the routine session honours `.claude/settings.json` deny rules `[manual]`
- [x] **1.** Lifecycle: register the story
  - [x] 1.1 Register DEV-005a (Active Cycle, estimate L) and DEV-005b (Backlog, estimate M), add the Update Log rows, add the CHANGELOG [Unreleased] entry citing `control-plane.yml`
- [ ] **2.** Deterministic engine (no routine change)
  - [ ] 2.1 Author synthetic fixtures under `tests/fixtures/triage/` (both snapshots, test manifest, `backlogs/*.md`)
  - [ ] 2.2 Write failing tests first in `tests/test_triage_rules.py`, `tests/test_triage_render.py`, `tests/test_triage_cli.py`
  - [ ] 2.3 Implement `dreamtoosa/triage.py` (pure rules, under 450 lines)
  - [ ] 2.4 Implement `dreamtoosa/triage_report.py` (check, render, heartbeat, verify-git, inject, under 450 lines)
  - [ ] 2.5 Generate `tests/fixtures/triage/expected-2026-10-13.md` from the frozen snapshot; owner reviews it against the rule text
- [ ] **3.** Manifest, validator and prompt
  - [ ] 3.1 Add the additive `dreamtoosa/repos.yml` keys (visibility from 0.1, backlog mapping, workflow lists, `dependabot_scope`, triage block, `force_read_only: false`, soft time box)
  - [ ] 3.2 Add guarded checks to `dreamtoosa/validate.py` (no triage import; exit 2 on missing PyYAML or uncaught exception)
  - [ ] 3.3 Extend `tests/test_validate.py` (negatives, backward compatibility, subprocess runs, raised floor)
  - [ ] 3.4 Update `dreamtoosa/ROUTINE_PROMPT.md` (ten-tool line, Phase 0, 0.5, 1.5, 2, 3, 4, final summary, absolute paths)
  - [ ] 3.5 Add `tests/test_routine_prompt.py` contract tests
  - [ ] 3.6 Update `dreamtoosa/README.md` with write-boundary and visibility notes
- [ ] **4.** Verification, live deploy and acceptance
  - [ ] 4.1 Local READ_ONLY simulation of `snapshot-read-only.json` in a scratch worktree (no push)
  - [ ] 4.2 Run the gates (both unittest forms, validate.py, py_compile)
  - [ ] 4.3 CI green on the PR (`control-plane.yml` validate job, Python 3.12, PyYAML only)
  - [ ] 4.4 RemoteTrigger get, update with the full session_context, get again and diff `[manual]`
  - [ ] 4.5 Owner observes one READ_WRITE run with Fleet Triage at the top of the index `[manual]`

> **Decision recorded (DEV-005 - implementer defaults):** Both specs (`Docs/archived/spec-DEV-005a.md`, `spec-DEV-005b.md`) were approved on 2026-10-13 on the owner instruction to fix all issues and build all tasks. The resolutions below are implementer defaults; the owner may override them in PR review (Spec Revision Log R1 in each spec). Visibility was verified by repo-qualified search: AgToosa public, Crapsino private, DreamToosa public, miToosa public. Committed history under `reports/` is not changed; the private-repo details already published there are flagged in the PR for an owner decision. From DEV-005a on, per-repo reports for a private, absent or unrecognised-visibility repo are published only in the withheld form. A15 stands (neutral and skipped checks count as green for READY). For DEV-005b: a single extra pure module `dreamtoosa/triage_ledger.py` is allowed only if `triage.py` would exceed 480 lines at the start of its build (amends Q2; owner confirmation requested); the heartbeat cron is `30 16 * * *`; liveness uses the DEV-005a definition; the four DEV-005a amendments are applied; CHAIN_BASE uses the open-PR plus not-ancestor refinement. OI-1 (golden formula), OI-3 (PushNotification) and OI-4 (dark routine) stay open, and gates 0.2, 0.3, 4.4 and 4.5 stay manual.

> **Decision recorded (DEV-004 - PR Chaining):** When daily report PRs are not merged immediately by humans, the routine branches from the newest unmerged report branch on origin (chaining) rather than forking from stale `origin/main`. This ensures continuous `state.json` lineage and eliminates cascading merge conflicts.

> **Decision recorded (DEV-004 - Hub Circuit Breaker):** The hub repository (`sky2464/DreamToosa`) enforces `hub.max_unmerged_report_prs`. When unmerged report PRs reach this cap, the routine stops pushing new remote branches and alerts maintainers, preventing unmerged branch spam.

> **Decision recorded (DEV-004 - Degradation & Workspace Safety):** In read-only mode (e.g. 401 API credentials), the routine never pushes remote branches. Workspace files must never be destructively overwritten with `git checkout -- <file>`.

> **Decision recorded (DEV-002):** GitHub's suggested workflows — Python application, Python package, Django — were all rejected. They are inferred from the language histogram, not the repo's behaviour: there is no `requirements.txt`, no packaging metadata, no Django, and no test suite, so `pytest` exits 5 and the badge is red on the first run. The Dreams code also needs `ANTHROPIC_API_KEY` and beta access and cannot execute in CI. Control-plane validation was built instead.

> **Decision recorded (AgToosa rotation):** AgToosa has 15 open PRs against a `main` frozen since 2026-08-29. To allow the routine's fix rotation to advance cleanly across `Crapsino`, `DreamToosa`, and `miToosa`, AgToosa was marked `fix_eligible: false` in `repos.yml`. It continues to receive daily review and reporting.

## Manual / Deferred Tasks

> Tasks that require a human action outside the agent. These are **not** counted against the health score.
> When you complete a step, run `/agtoosa-build` and choose (A) to mark it done.

| Story | Task # | Deferred Since | Description |
|-------|--------|----------------|-------------|

*(Empty — routine MCP re-auth is operational hygiene; re-open via `/agtoosa-task` if needed.)*

## Blocked

> **Status:** 🟢 None blocked
> Update this section and change status pill if an issue is blocked during `/agtoosa-build`.

| ID | Title | Blocked by | Since |
|----|-------|-----------|-------|

*(Empty — good!)*

## Backlog

> Priority-ordered list of upcoming stories and issues. Updated by `/agtoosa-spec` and `/agtoosa-task`.
> Optional **Clarity** column (DEV-109): combinable tags `ready` · `sa-ready` · `needs-interview` (aliases `Ready` · `SA-R` · `N-CI`).

| ID | Title | Type | Estimate | Epic | Priority | Clarity | Status |
|----|-------|------|----------|------|----------|---------|--------|
| DEV-005b | Feature: Fleet Triage ledger, dark-routine heartbeat and urgent push | Feature | M | DEV-100 | P1 | ready | 🟦 Todo — spec approved; depends on DEV-005a |

## Epics

> Created at `/agtoosa-init`. One row per product area. Changes rarely — see Active Cycle for what's in flight.

| ID | Title | Stories | Status |
|----|-------|---------|--------|
| DEV-100 | Epic: Multi-repo maintainer routine | 2 open / 6 total | 🟨 In Progress |
| DEV-101 | Epic: Claude Dreams memory curation | 0 open / 2 shipped | 🏁 Shipped |

## Active Diagnosis

> Written by `/agtoosa-debug` while a bug investigation is live. Cleared when the diagnosis closes.
> Holds the current reproduction command / feedback loop for the bug under investigation.

*(Empty — no active diagnosis.)*

## Hypotheses

> Written by `/agtoosa-debug`. Ranked candidate causes for the active diagnosis, marked confirmed/eliminated as evidence arrives.

*(Empty — no active diagnosis.)*

## Completed This Cycle

> Detail lives in `Docs/archived/`. This section shows pointer rows only — links to archived spec files.
> Updated by `/agtoosa-ship`.

| ID | Title | Shipped | Archived Spec |
|----|-------|---------|--------------|
| DEV-005 | Chore: Unify duplicate DreamsClient / DreamConfig modules | 2026-10-14 | [spec-DEV-005.md](archived/spec-DEV-005.md) |
| DEV-001 | Feature: Multi-repo control plane for the Dream Report routine | 2026-10-13 | [spec-DEV-001.md](archived/spec-DEV-001.md) |
| DEV-002 | Chore: Root README and control-plane CI | 2026-09-08 | [spec-DEV-002.md](archived/spec-DEV-002.md) |
| DEV-003 | Feature: Local agent memory curation engine and CLI | 2026-09-08 | [spec-DEV-003.md](archived/spec-DEV-003.md) |
| DEV-004 | Feature: Resilient Multi-Repo Control Plane & PR Lifecycle | 2026-09-18 | [spec-DEV-004.md](archived/spec-DEV-004.md) |

## Update Log

> Append a row at every phase transition. Never delete rows.

| Date | Event | By |
|------|-------|----|
| 2026-09-07 | spec DEV-001 started | AgToosa |
| 2026-09-07 | build DEV-001 started | AgToosa |
| 2026-09-07 | spec DEV-002 started | AgToosa |
| 2026-09-08 | build DEV-002 completed | AgToosa |
| 2026-09-08 | ship DEV-002 shipped | AgToosa |
| 2026-09-08 | spec DEV-003 started | AgToosa |
| 2026-09-08 | build DEV-003 completed | AgToosa |
| 2026-09-08 | ship DEV-003 shipped | AgToosa |
| 2026-09-16 | spec DEV-004 started | DreamToosa |
| 2026-09-16 | build DEV-004 started | DreamToosa |
| 2026-09-16 | build DEV-004 completed | DreamToosa |
| 2026-09-18 | ship DEV-004 shipped | DreamToosa |
| 2026-09-20 | build DEV-001 dream reports (read-only run) | DreamToosa |
| 2026-10-03 | build DEV-001 Agtoosa2 + consolidated reports | DreamToosa |
| 2026-10-13 | build DEV-001 issue #8 docs merged (PR #17) | DreamToosa |
| 2026-10-13 | build hub report PRs #16–#17 merged; agent skills on main | DreamToosa |
| 2026-10-13 | status Master-Plan refresh (DEV-001 tasks realigned) | AgToosa |
| 2026-10-13 | init context + architecture + Copilot instructions (brownfield re-init) | AgToosa |
| 2026-10-13 | spec DEV-001 plan — architecture + STRIDE (spec R1 pending approval) | AgToosa |
| 2026-10-13 | review DEV-001 — Review ✅ Approved (brownfield) | AgToosa |
| 2026-10-13 | ship DEV-001 docs — archived spec/review; changelog + Master-Plan | AgToosa |
| 2026-10-13 | spec DEV-005 — interview Q1–Q3; spec + test plan; enrolled in Active Cycle | AgToosa |
| 2026-10-13 | build DEV-005 completed — unified client, tests 17/17 | AgToosa |
| 2026-10-13 | spec DEV-005a drafted | DreamToosa |
| 2026-10-13 | spec DEV-005b drafted | DreamToosa |
| 2026-10-13 | spec DEV-005a and DEV-005b approved (OI-1, OI-3, OI-4 open; implementer-default resolutions in each Spec Revision Log R1) | DreamToosa |
| 2026-10-13 | build DEV-001 completed: AC-1 to AC-4 verified against repos.yml, profiles, state.json and ROUTINE_PROMPT.md; set Done, not shipped; Tasks Done 4/6 left as is because the spec has no task list | DreamToosa |
| 2026-10-13 | build DEV-005a started | DreamToosa |
| 2026-10-14 | review DEV-005 — Review ✅ Approved (security+arch; 0 critical) | AgToosa |
| 2026-10-14 | ship DEV-005 — smoke PASS; v0.1.1; spec/review archived; cycle idle | AgToosa |
| 2026-10-14 | build DEV-005a resumed after main merge (DEV-005 shipped) | DreamToosa |

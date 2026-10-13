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
| Cycle state | Idle — DEV-005 shipped; enroll next story via `/agtoosa-spec` or `/agtoosa-next pick` |
| Cycle capacity | 5 story points |
| Current phase | ✏️ Spec · 🏗️ Build · 🔍 Review · **🚢 Ship** (idle) |

> **Cycle state contract:** use `Active` while a story is enrolled; use `Idle — <reason>` only when an empty cycle is intentional.

## Active Cycle

> Stories committed to the current sprint/cycle.

<!-- Archived to Docs/archived/cycle-2026-10-14.md -->

| ID | Title | Type | Estimate | Status | Tasks Done |
|----|-------|------|----------|--------|-----------|
| — | *(no active story)* | — | — | — | — |

Status key: ⬜ Backlog · 🟦 Todo · 🟨 In Progress · ✅ Done · 🚫 Blocked · 🔧 Awaiting Manual · 🏁 Shipped

## Active Tasks

> Task breakdown for the enrolled story. Cleared when the story ships.

*(Empty — enroll a story via `/agtoosa-spec`.)*

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

*(Empty — add chores via `/agtoosa-task` or `/agtoosa-next pick`.)*

## Epics

> Created at `/agtoosa-init`. One row per product area. Changes rarely — see Active Cycle for what's in flight.

| ID | Title | Stories | Status |
|----|-------|---------|--------|
| DEV-100 | Epic: Multi-repo maintainer routine | 0 open / 4 shipped | 🏁 Shipped |
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
| 2026-10-14 | review DEV-005 — Review ✅ Approved (security+arch; 0 critical) | AgToosa |
| 2026-10-14 | ship DEV-005 — smoke PASS; v0.1.1; spec/review archived; cycle idle | AgToosa |

# Master-Plan

> **Source of truth for active work.** Completed work lives in `Docs/archived/` — see Completed This Cycle for links.
> **Last updated:** 2026-10-13 23:35

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
| Unresolved questions | AgToosa remains `fix_eligible: false` while its PR backlog drains; fix rotation runs across Crapsino, DreamToosa, miToosa, and Agtoosa2; attach RemoteTrigger run log as DEV-001 proof artifact |
| GitHub repo | https://github.com/sky2464/DreamToosa |
| Milestone | Unreleased |
| Active cycle | Multi-repo routine enablement |
| Cycle state | Active — DEV-001 in progress |
| Cycle capacity | 5 story points |
| Current phase | ✏️ Spec · 🏗️ Build · **🔍 Review** · 🚢 Ship |

> **Cycle state contract:** use `Active` while a story is enrolled; use `Idle — <reason>` only when an empty cycle is intentional.

## Active Cycle

> Stories committed to the current sprint/cycle.
> **Progress:** `▰▰▰▰▰▱▱▱ 4/6 tasks` ← updated by `/agtoosa-build` after each task completes

| ID | Title | Type | Estimate | Status | Tasks Done |
|----|-------|------|----------|--------|-----------|
| DEV-001 | Feature: Multi-repo control plane for the Dream Report routine | Feature | M | 🟨 In Progress | 4/6 |
| DEV-002 | Chore: Root README and control-plane CI | Chore | S | 🏁 Shipped | 5/5 |
| DEV-003 | Feature: Local agent memory curation engine and CLI | Feature | S | 🏁 Shipped | 4/4 |
| DEV-004 | Feature: Resilient Multi-Repo Control Plane & PR Lifecycle | Feature | M | 🏁 Shipped | 4/4 |

Status key: ⬜ Backlog · 🟦 Todo · 🟨 In Progress · ✅ Done · 🚫 Blocked · 🔧 Awaiting Manual · 🏁 Shipped

## Active Tasks

> Task breakdown for the current In Progress story. Created by `/agtoosa-spec` (Part 4).
> Updated by `/agtoosa-build` — each completed sub-task gets `- [x]`.

- [x] **1.** Control plane baseline (DEV-001 AC-1..AC-4)
  - [x] 1.1 `dreamtoosa/repos.yml`, `profiles/`, `state.json`, and `ROUTINE_PROMPT.md` on `main`
  - [x] 1.2 Validator + unit tests green (`validate.py` 19/19; `tests/` 13/13 as of 2026-10-03 report)
- [x] **2.** Resilience layer shipped (DEV-004 dependency)
  - [x] 2.1 Hub circuit breaker, PR chaining, read-only degradation — see Completed This Cycle / `CHANGELOG.md`
- [x] **3.** Five-repo routine coverage
  - [x] 3.1 Onboard `sky2464/Agtoosa2` with `python-spec-driven` profile (merged PR #16)
  - [x] 3.2 Dream reports 2026-09-20 and 2026-10-03 committed under `reports/` (merged PR #16)
- [x] **4.** Dreams implementation boundary documentation (issue #8)
  - [x] 4.1 Local vs remote curation docs merged (PR #17)
- [ ] **5.** Routine proof artifact
  - [ ] 5.1 Capture `RemoteTrigger list_runs` + `get_run_log` showing `git -C` across all enabled clones
- [ ] **6.** Close DEV-001
  - [ ] 6.1 Run `/agtoosa-ship` for DEV-001 (archive spec, move row to Completed This Cycle, trim `CHANGELOG.md` if needed)

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
| DEV-001 | — | 2026-10-03 | [manual] Re-authenticate GitHub MCP (401) so maintainer runs can file issues and open PRs again |

*(One manual task deferred on DEV-001.)*

## Blocked

> **Status:** 🟢 None blocked
> Update this section and change status pill if an issue is blocked during `/agtoosa-build`.

| ID | Title | Blocked by | Since |
|----|-------|-----------|-------|
| [DEV-XX] | [title] | [DEV-YY / external reason] | [YYYY-MM-DD] |

*(Empty — good!)*

## Backlog

> Priority-ordered list of upcoming stories and issues. Updated by `/agtoosa-spec` and `/agtoosa-task`.
> Optional **Clarity** column (DEV-109): combinable tags `ready` · `sa-ready` · `needs-interview` (aliases `Ready` · `SA-R` · `N-CI`).

| ID | Title | Type | Estimate | Epic | Priority | Clarity | Status |
|----|-------|------|----------|------|----------|---------|--------|
| DEV-005 | Chore: Unify duplicate DreamsClient / DreamConfig modules | Chore | M | DEV-101 | Medium | needs-interview | ⬜ Backlog |

*(Carry-forward from dream reports — documentation landed in PR #17; code consolidation not started.)*

## Epics

> Created at `/agtoosa-init`. One row per product area. Changes rarely — see Active Cycle for what's in flight.

| ID | Title | Stories | Status |
|----|-------|---------|--------|
| DEV-100 | Epic: Multi-repo maintainer routine | 1 open / 3 shipped | 🟨 In Progress |
| DEV-101 | Epic: Claude Dreams memory curation | 1 shipped / 1 total | 🏁 Shipped |

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


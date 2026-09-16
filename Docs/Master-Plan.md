# Master-Plan

> **Source of truth for active work.** Completed work lives in `Docs/archived/` — see Completed This Cycle for links.
> **Last updated:** 2026-09-07 21:15

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
| Risks | AgToosa's 15-PR backlog and red `validate` gate everything downstream; four-repo runs may exceed the run time box; Dreams API remains beta-gated |
| Unresolved questions | Resolved: AgToosa set to review-only (fix_eligible: false) in repos.yml while backlog is drained; fix rotation proceeds across clean repos |
| GitHub repo | https://github.com/sky2464/DreamToosa |
| Milestone | Unreleased |
| Active cycle | Multi-repo routine enablement |
| Cycle state | Active — DEV-001 in progress |
| Cycle capacity | 5 story points |
| Current phase | ✏️ Spec · **🏗️ Build** · 🔍 Review · 🚢 Ship |

> **Cycle state contract:** use `Active` while a story is enrolled; use `Idle — <reason>` only when an empty cycle is intentional.

## Active Cycle

> Stories committed to the current sprint/cycle.
> **Progress:** `▰▰▰▰▱▱▱▱ 0/0 tasks` ← updated by `/agtoosa-build` after each task completes

| ID | Title | Type | Estimate | Status | Tasks Done |
|----|-------|------|----------|--------|-----------|
| DEV-001 | Feature: Multi-repo control plane for the Dream Report routine | Feature | M | 🟨 In Progress | 4/6 |
| DEV-002 | Chore: Root README and control-plane CI | Chore | S | 🏁 Shipped | 5/5 |
| DEV-003 | Feature: Local agent memory curation engine and CLI | Feature | S | 🏁 Shipped | 4/4 |
| DEV-004 | Feature: Resilient Multi-Repo Control Plane & PR Lifecycle | Feature | M | ✅ Done | 4/4 |

Status key: ⬜ Backlog · 🟦 Todo · 🟨 In Progress · ✅ Done · 🚫 Blocked · 🔧 Awaiting Manual · 🏁 Shipped

## Active Tasks

> Task breakdown for the current In Progress story. Created by `/agtoosa-spec` (Part 4).
> Updated by `/agtoosa-build` — each completed sub-task gets `- [x]`.

- [x] **1.** Specifications & Planning: Establish authoritative AgToosa spec and cycle tracking
  - [x] 1.1 Author `Docs/archived/spec-DEV-004.md` adhering to `Docs/SPEC-FORMAT.md`
  - [x] 1.2 Update `Docs/Master-Plan.md` with DEV-004 active story and architecture decisions
- [x] **2.** Control Plane Manifest & Validator Extension
  - [x] 2.1 Update `dreamtoosa/repos.yml` with hub circuit breaker, PR strategy, and clone root
  - [x] 2.2 Extend `dreamtoosa/validate.py` with invariant checks for new hub keys
  - [x] 2.3 Create `tests/test_validate.py` testing valid and invalid control plane configs
- [x] **3.** Routine Prompt Source of Truth Hardening
  - [x] 3.1 Refactor Phase 0 in `dreamtoosa/ROUTINE_PROMPT.md` for dynamic root discovery
  - [x] 3.2 Implement Phase 0.5 pre-flight auth probing and push prohibition in READ_ONLY mode
  - [x] 3.3 Implement hub circuit breaker check in Phase 2
  - [x] 3.4 Implement worktree / non-destructive workspace isolation in Phase 5
  - [x] 3.5 Implement PR chaining logic and lineage tracking in Phase 6
  - [x] 3.6 Implement verification execution and baseline delta tracking
- [x] **4.** Verification & Validation Audit
  - [x] 4.1 Run `python3 -m unittest discover -s tests` across full test suite
  - [x] 4.2 Run `python3 dreamtoosa/validate.py` confirming checks pass
  - [x] 4.3 Verify `python3 -m py_compile *.py dreamtoosa/*.py tests/*.py` passes cleanly

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
| [DEV-XX] | 2.3 | [YYYY-MM-DD] | [task title] |

*(Empty — no manual tasks deferred.)*

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
| [DEV-XX] | Feature: [name] | Feature | S | [DEV-YY] | High | needs-interview | ⬜ Backlog |

*(Empty until stories are created via `/agtoosa-spec` or `/agtoosa-task`.)*

## Epics

> Created at `/agtoosa-init`. One row per product area. Changes rarely — see Active Cycle for what's in flight.

| ID | Title | Stories | Status |
|----|-------|---------|--------|
| DEV-100 | Epic: Multi-repo maintainer routine | 1 open / 2 total | 🟨 In Progress |
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


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
| Unresolved questions | Whether to unjam AgToosa first or drop it from the manifest and prove the path on the three clean repos |
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

Status key: ⬜ Backlog · 🟦 Todo · 🟨 In Progress · ✅ Done · 🚫 Blocked · 🔧 Awaiting Manual · 🏁 Shipped

## Active Tasks

> Task breakdown for the current In Progress story. Created by `/agtoosa-spec` (Part 4).
> Updated by `/agtoosa-build` — each completed sub-task gets `- [x]`.

- [x] **1.** Control plane: manifest, profiles, cross-run state
  - [x] 1.1 `dreamtoosa/repos.yml` — targets, per-repo caps, run budget
  - [x] 1.2 `dreamtoosa/profiles/*.md` — per-stack review criteria replacing the hardcoded AgToosa checklist
  - [x] 1.3 `dreamtoosa/state.json` — last-reviewed SHA, issues/PRs, fix rotation
  - [x] 1.4 `reports/` layout — per-repo dirs plus a per-run index
- [x] **2.** Routine prompt rewritten and version-controlled
  - [x] 2.1 `dreamtoosa/ROUTINE_PROMPT.md` — repo-loop, `git -C`, MCP-only GitHub, circuit breaker, one fix repo per run
- [x] **3.** Apply to the live routine
  - [x] 3.1 Prompt + config pushed via `RemoteTrigger update`; stale `outcomes` branches cleared, `ToolSearch` added to `allowed_tools`, `model` restored to `claude-sonnet-5` after the first update blanked it
  - [x] 3.2 Control plane merged to DreamToosa `main` (PR #1, commit `b474cba`) so the sandbox clone can find it
  - [ ] 3.3 **Deferred — not API-settable:** the 6 unused MCP connectors ignore `mcp_connections: []`. Detach in the routine UI if wanted; no functional impact.
- [ ] **4.** Verify
  - [ ] 4.1 Manual `RemoteTrigger run`; confirm all four clones touched and the AgToosa circuit breaker fires
  - [ ] 4.2 Second run confirms rotation advanced and no duplicate same-day report

> **Blocked on a human decision (see Charter → Unresolved questions):** AgToosa has 15 open PRs against a `main` frozen since 2026-08-29, with `validate` red on `main` itself. Task 4 cannot prove the fix path there until that is drained or AgToosa is set review-only.

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
| [DEV-XX] | Epic: [product area name] | [N open / N total] | ⬜ Backlog |

*(Run `/agtoosa-init` to populate this table with your project's Epics.)*

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
| [DEV-XX] | Feature: [name] | [YYYY-MM-DD] | [spec-[DEV-XX].md](archived/spec-[DEV-XX].md) |

*(Empty until `/agtoosa-ship` closes the first story.)*

## Update Log

> Append a row at every phase transition. Never delete rows.

| Date | Event | By |
|------|-------|----|
| [YYYY-MM-DD] | [phase] [Story ID] [started / completed / blocked / shipped] | AgToosa |

*(Run `/agtoosa-init` to add the first entry.)*

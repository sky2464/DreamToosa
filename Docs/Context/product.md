# Product Context

## App Type
app_type: "CLI tool + documentation bundle (Python control plane; optional remote Dreams API examples)"

## Target Users
target_users: "Maintainer operating a multi-repo portfolio (AgToosa, Crapsino, DreamToosa, miToosa, Agtoosa2) via the scheduled Dream Report routine; developers learning Claude Dreams memory curation patterns."

## Core Problem
core_problem: "Daily code-health across many repos is fragmented—per-repo PR backlogs and ad-hoc reviews do not scale; memory curation examples are scattered across legacy scripts."

## Core Features
core_features:
  - "Multi-repo control plane: manifest, stack profiles, cross-run state, validator, and routine prompt"
  - "Scheduled Dream Report: consolidated reports under reports/ and bounded fix rotation"
  - "Local Dreamer memory curation (dreamtoosa package) with JSON MemoryStore"
  - "Reference implementations for remote Claude Dreams API workflows"

## Non-Goals
non_goals:
  - "Merging PRs automatically on the user's behalf"
  - "Hosted orchestrator or swarm runtime"
  - "Full consolidation of all legacy Dreams client variants in one release (document boundaries first)"

## Current Milestone
current_milestone: "v0.1.0 shipped — DEV-005 client unification in progress"

## Success Metrics
success_metrics:
  - "Every enabled repo in dreamtoosa/repos.yml reviewed each routine run with reports committed to hub"
  - "At most one hub report PR and one fix PR per run under budget caps"
  - "dreamtoosa/validate.py and unit tests pass on main (CI green)"
  - "state.json advances rotation and last-reviewed SHAs without manual re-derivation"

## Notes
Product identity is **DreamToosa** (control plane + examples), not the AgToosa framework docs co-located under Docs/. Charter source of truth: Docs/Master-Plan.md → Project Charter.

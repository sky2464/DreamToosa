# Spec — DEV-001: Multi-Repo Control Plane for the Dream Report Routine

- **ID:** DEV-001
- **Epic:** DEV-100
- **Type:** Feature
- **Status:** In Progress
- **Created:** 2026-09-07

---

## 1. Goal Contract

### 1.1 Goal
Establish DreamToosa as the centralized control plane for the multi-repo maintainer routine ("Dream Report – Daily Code Review").

### 1.2 User Outcome
A scheduled agent reviews multiple repositories daily, writes a single consolidated health report, and performs at most one bounded fix PR per run without accumulating runaway backlogs.

### 1.3 Success Condition
- Control plane configuration: `repos.yml`, `profiles/`, `state.json`, and `ROUTINE_PROMPT.md`.
- Circuit breaker skips backlogged repositories (e.g. AgToosa).
- Exactly one repo carries fix work per run via deterministic rotation.

### 1.4 Proof / Evidence
- Control plane merged to `main` (PR #1, commit `b474cba`).
- Routine prompt deployed to live trigger `trig_01PvQiwSRhJktFxMXwxf14Qi`.
- Verification of report generation and rotation advancement.

---

## 2. Acceptance Criteria

| ID | Priority | Description | Verification |
|----|----------|-------------|--------------|
| AC-1 | Must | Manifest specifies targets, per-repo caps, and run budget | `dreamtoosa/repos.yml` |
| AC-2 | Must | Review criteria customized per stack profile | `dreamtoosa/profiles/*.md` |
| AC-3 | Must | Cross-run state file persists last reviewed SHA and rotation index | `dreamtoosa/state.json` |
| AC-4 | Must | Prompt qualified with `git -C` and uses MCP GitHub tools | `ROUTINE_PROMPT.md` |

---

## ✅ Spec Approved
- **Approved by:** Chicademy & Navid
- **Timestamp:** 2026-09-07T21:00:00Z

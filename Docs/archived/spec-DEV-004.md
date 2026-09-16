# Spec: DEV-004 — Resilient Multi-Repo Maintainer Control Plane & PR Lifecycle

> **Story ID:** DEV-004  
> **Epic:** DEV-100 (Multi-repo maintainer routine)  
> **Status:** ✅ Done  
> **Estimate:** M  
> **Clarity:** `ready` · `sa-ready`  
> **Spec created:** 2026-09-16  

---

### Plan-Mode Spec Interview (findings)

#### Inferred (≥80% — no question asked)

| Checklist area | Finding |
|----------------|---------|
| Control plane architecture | The scheduled routine `trig_01PvQiwSRhJktFxMXwxf14Qi` runs daily with `persist_session=false`, relying on committed `state.json` on the hub repo for memory. |
| Stale main anti-pattern | Human PR merge latency leaves daily report PRs stacked on `origin` (e.g. PRs #11–#14), causing subsequent runs to fork from stale `main` and lose interim state history. |
| Path portability | Hardcoding `/home/user/<repo>` breaks execution on local developer workstations and CI runners where repositories reside under alternative paths. |
| Degradation safety | When GitHub MCP credentials fail (401), pushing orphan remote branches to origin pollutes remote history without creating corresponding PRs. |

#### Documented assumptions

- `PR Chaining` is the preferred mitigation for asynchronous human merge latency: branching from the newest unmerged daily report branch preserves linear continuity of `state.json`.
- Hub repository must enforce the same circuit breaker rules as target leaf repositories (`max_unmerged_report_prs`).
- Host working directory must never be destructively overwritten by the routine.

---

## Section 1 — Requirements

### Goal Contract

| Field | Value |
|-------|-------|
| Goal | Harden the DreamToosa maintainer control plane against state divergence, environment path brittleness, auth degradation failures, and hub PR backlog saturation. |
| User outcome | Reliable, continuous multi-repo daily code reviews that maintain state consistency across days regardless of human PR merge latency, run safely across both sandbox and local environments, and never pollute git remotes when API credentials fail. |
| Success condition | 1. `dreamtoosa/repos.yml` declares hub circuit breaker (`max_unmerged_report_prs`) and PR strategy (`pr_strategy`).<br>2. `dreamtoosa/ROUTINE_PROMPT.md` dynamically discovers `CLONE_ROOT`, probes API auth before push, chains unmerged report branches, and respects hub PR caps.<br>3. `dreamtoosa/validate.py` validates new schema invariants.<br>4. Automated test suite in `tests/test_validate.py` verifies validator behavior. |
| Proof / evidence | `python3 -m unittest discover -s tests` passing (existing + new validator tests); `python3 dreamtoosa/validate.py` passing 18/18 checks; zero syntax errors on all Python files. |
| Non-goals | Merging pull requests automatically on a human's behalf; changing downstream target repository code; migrating external CI platforms. |
| Assumptions | Repositories share a common parent directory or define `DREAMTOOSA_CLONE_ROOT`; Git is available in the execution runtime. |
| Risks | Complex git branching if remote branches are deleted mid-run (mitigated by fallback to `origin/main`). |
| Unresolved questions | None. |

### 1.1 User Stories

- **As a** repository maintainer, **I want** the daily Dream Report agent to chain unmerged daily report branches **so that** cross-run memory and last-reviewed commit SHAs remain continuous even when I do not merge PRs daily.
- **As an** engineering lead, **I want** the maintainer agent to stop pushing report branches when the hub's open PR backlog reaches capacity **so that** unmerged PRs do not accumulate indefinitely.
- **As a** developer running maintainer checks locally, **I want** portable clone path discovery and workspace isolation **so that** the routine runs cleanly without overwriting my uncommitted working directory edits or assuming `/home/user`.
- **As a** systems operator, **I want** atomic pre-flight authentication probing **so that** failed API credentials do not result in orphan remote branches pushed to GitHub.

### 1.2 Acceptance Criteria (EARS)

| ID | EARS | Priority |
|:---|:---|:---:|
| AC-001 | **WHEN** the control plane initializes, **THE SYSTEM SHALL** resolve `CLONE_ROOT` dynamically via `DREAMTOOSA_CLONE_ROOT` or repository parent directory, falling back to `/home/user` only if present. | Must |
| AC-002 | **IF** GitHub API tools return unauthorized (HTTP 401) during pre-flight, **THEN THE SYSTEM SHALL** enter `READ_ONLY` mode and prohibit all `git push` operations to remote branches. | Must |
| AC-003 | **WHILE** evaluating the hub repository, **WHEN** unmerged report PRs exceed `hub.max_unmerged_report_prs`, **THE SYSTEM SHALL** halt remote branch push and record a hub saturation notice. | Must |
| AC-004 | **WHILE** PR chaining is configured (`pr_strategy: "chain"`), **WHEN** an unmerged report branch exists on origin, **THE SYSTEM SHALL** base the new run's branch on the latest unmerged report branch. | Must |
| AC-005 | **WHEN** preparing to commit or switch branches, **THE SYSTEM SHALL** preserve all uncommitted host workspace modifications without running destructive checkouts or overwrites. | Must |
| AC-006 | **WHEN** reviewing a repository with a defined verification command, **THE SYSTEM SHALL** execute the verification command and record exact failure counts against historical baselines rather than skipping execution. | Should |
| AC-007 | **WHEN** `python3 dreamtoosa/validate.py` executes, **THE SYSTEM SHALL** validate that `hub.max_unmerged_report_prs` is an integer $\ge 1$ and `hub.pr_strategy` is valid. | Must |
| AC-008 | **WHEN** unit tests execute via `python3 -m unittest discover -s tests`, **THE SYSTEM SHALL** verify that invalid configurations are caught and rejected by `validate.py`. | Must |

### 1.3 Out of Scope

- Merging PRs on GitHub without human review.
- Implementing automatic deletion of stale remote git branches.
- Adding non-standard build tooling (retaining standard library and PyYAML).

---

## Section 2 — Design

### 2.1 Architecture Blueprint

Files to create:
- `tests/test_validate.py`: Test suite validating control plane invariants and regression guards.
- `Docs/archived/spec-DEV-004.md`: This authoritative AgToosa specification.

Files to modify:
- `dreamtoosa/repos.yml`: Add hub circuit breaker (`max_unmerged_report_prs`), PR strategy (`pr_strategy`), and clone root env config.
- `dreamtoosa/validate.py`: Add validation checks for new hub and default configuration keys.
- `dreamtoosa/ROUTINE_PROMPT.md`: Update source-of-truth prompt with portable root discovery, pre-flight auth, hub circuit breaker, workspace protection, and PR chaining.
- `Docs/Master-Plan.md`: Register DEV-004 into active cycle and record architectural decisions.

### 2.2 Data Flow

1. **Phase 0 Bootstrap:** Routine determines `CLONE_ROOT`. Verifies `$CLONE_ROOT/DreamToosa/dreamtoosa/repos.yml` exists; if missing, halts immediately with fail-safe.
2. **Phase 0.5 Pre-Flight Auth:** Probes GitHub API credentials via `list_pull_requests` or `get_me`. Sets `EXECUTION_MODE="READ_WRITE"` or `"READ_ONLY"`.
3. **Phase 1 Review:** Iterates over enabled repositories under `$CLONE_ROOT/<repo>`. Executes verification commands (recording baseline failure counts) and checks commits since `last_reviewed_sha`.
4. **Phase 2 Circuit Breaker:** Checks open PR count on targets. Simultaneously checks unmerged report PRs on the hub against `hub.max_unmerged_report_prs`.
5. **Phase 3 Consolidated Report:** Writes dated reports to `reports/<repo>/` and top-level index `reports/dream-report-<date>.md`.
6. **Phase 4 Issues & Phase 5 Fix:** Bypassed if target is backlogged or if in `READ_ONLY` mode. Otherwise executes fix on rotated eligible target using isolated branch.
7. **Phase 6 Commit & PR Strategy:**
   - If `READ_ONLY` or hub circuit breaker is tripped: outputs report to run log, retains local files, and skips remote git push.
   - If `READ_WRITE` and chaining enabled: finds latest unmerged report branch on origin, bases new branch on it, commits report and state, pushes to origin, and opens PR.

### 2.3 Threat Model (STRIDE)

| Threat | Category | Mitigation |
|--------|----------|------------|
| Workspace overwrite | Tampering | Prohibit `git checkout -- <file>` or `git restore` on uncommitted host files; enforce worktrees or clean status check. |
| Remote repo spam | Denial of Service | Enforce `hub.max_unmerged_report_prs` cap so unmerged runs halt branch creation. |
| Orphan branch pollution | Repudiation | Prohibit `git push` when GitHub API authentication fails (401 Bad credentials). |
| State corruption | Tampering | Gate all commits through `dreamtoosa/validate.py` checking manifest/state parity and cap constraints. |

### 2.4 Build Scope

```
✅ Ready to proceed — Scope Boundary
Files in scope      : dreamtoosa/repos.yml, dreamtoosa/validate.py, dreamtoosa/ROUTINE_PROMPT.md, tests/test_validate.py, Docs/Master-Plan.md, Docs/archived/spec-DEV-004.md
Directories in scope: dreamtoosa/, tests/, Docs/
Out of scope        : External target repositories (AgToosa, Crapsino, miToosa source code)
```

---

## Section 3 — Tasks

### 3.1 Task Tree

- [x] **1.** Specifications & Planning: Establish authoritative AgToosa spec and cycle tracking
  - [x] 1.1 Author `Docs/archived/spec-DEV-004.md` adhering to `Docs/SPEC-FORMAT.md` — _Requirements: AC-001–AC-008_
  - [x] 1.2 Update `Docs/Master-Plan.md` with DEV-004 active story and architecture decisions — _Requirements: AC-001–AC-008_
- [x] **2.** Control Plane Manifest & Validator Extension
  - [x] 2.1 Update `dreamtoosa/repos.yml` with hub circuit breaker, PR strategy, and clone root — _Requirements: AC-001, AC-003, AC-004_
  - [x] 2.2 Extend `dreamtoosa/validate.py` with invariant checks for new hub keys — _Requirements: AC-007_
  - [x] 2.3 Create `tests/test_validate.py` testing valid and invalid control plane configs — _Requirements: AC-008_
- [x] **3.** Routine Prompt Source of Truth Hardening
  - [x] 3.1 Refactor Phase 0 in `dreamtoosa/ROUTINE_PROMPT.md` for dynamic root discovery — _Requirements: AC-001_
  - [x] 3.2 Implement Phase 0.5 pre-flight auth probing and push prohibition in READ_ONLY mode — _Requirements: AC-002_
  - [x] 3.3 Implement hub circuit breaker check in Phase 2 — _Requirements: AC-003_
  - [x] 3.4 Implement worktree / non-destructive workspace isolation in Phase 5 — _Requirements: AC-005_
  - [x] 3.5 Implement PR chaining logic and lineage tracking in Phase 6 — _Requirements: AC-004_
  - [x] 3.6 Implement verification execution and baseline delta tracking — _Requirements: AC-006_
- [x] **4.** Verification & Validation Audit
  - [x] 4.1 Run `python3 -m unittest discover -s tests` across full test suite — _Requirements: AC-008_
  - [x] 4.2 Run `python3 dreamtoosa/validate.py` confirming checks pass — _Requirements: AC-007_
  - [x] 4.3 Verify `python3 -m py_compile *.py dreamtoosa/*.py tests/*.py` passes cleanly — _Requirements: AC-001–AC-008_

### 3.2 Wave Plan

**Wave 1 (parallel):** 1.2, 2.1  
**Wave 2 (parallel):** 2.2, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6  
**Wave 3 (sequential after Wave 2):** 2.3  
**Wave 4 (sequential after Wave 3):** 4.1, 4.2, 4.3  

### 3.3 Test Plan

Test plan: `tests/test_validate.py` + `dreamtoosa/validate.py`  
AC coverage: 8 ACs mapped to test cases and validator assertions.  
Verification commands:
```bash
python3 dreamtoosa/validate.py
python3 -m unittest discover -s tests
python3 -m py_compile *.py dreamtoosa/*.py tests/*.py
```

---

## ✅ Spec Approved
- **Approved by:** User / Senior Architect Review
- **Timestamp:** 2026-09-16T01:03:00Z

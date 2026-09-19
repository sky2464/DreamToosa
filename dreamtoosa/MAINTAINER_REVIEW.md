# DreamToosa Maintainer Review & Revisit Checklist

**Date:** 2026-09-08  
**Role:** DreamToosa Multi-Repo Maintainer Agent per [`dreamtoosa/ROUTINE_PROMPT.md`](ROUTINE_PROMPT.md)  
**Control Plane Hub:** `sky2464/DreamToosa`  
**Inspected Artifacts:** [`dreamtoosa/repos.yml`](repos.yml), [`dreamtoosa/validate.py`](validate.py), [`dreamtoosa/state.json`](state.json)

---

## 1. Executive Summary

This document records the maintainer review of the DreamToosa control plane manifest ([`repos.yml`](repos.yml)) and the verification audit performed via [`validate.py`](validate.py). It serves as the baseline and handoff checklist for the next review or revisit by human maintainers and autonomous agents.

---

## 2. Review of `dreamtoosa/repos.yml`

The manifest configures the scheduled cloud routine `trig_01PvQiwSRhJktFxMXwxf14Qi` ("Dream Report – Daily Code Review").

### A. Repository Status & Policies

| Repository | Profile | Max Open PRs | Review Window | Fix Eligible | Operational Status & Policy |
|:---|:---|:---:|:---:|:---:|:---|
| `sky2464/AgToosa` | `shell-spec-driven` | `5` | `2 days ago` | `false` | **Review-Only:** Currently held in review-only mode due to a 15-PR backlog on `main`. Under Phase 1 & 2 of the routine, it receives daily health reviews and report generation. Under Phase 5, it is bypassed for fix PRs so rotation is not jammed. |
| `sky2464/Crapsino` | `web-playwright` | `3` | `2 days ago` | `true` | **Active Candidate:** Web application evaluated with Playwright end-to-end criteria. Eligible for fix rotation. |
| `sky2464/DreamToosa` | `python-lib` | `3` | `2 days ago` | `true` | **Hub & Active Candidate:** Python control plane and memory curation library. Central merge point for all reports. |
| `sky2464/miToosa` | `dart-flutter` | `3` | `2 days ago` | `true` | **Active Candidate:** Flutter/Dart client target. Eligible for fix rotation. |

### B. Hub Architecture (Consolidated Merge Point)
- `hub.repo`: `sky2464/DreamToosa`
- `hub.reports_dir`: `reports`
- `hub.state_file`: `dreamtoosa/state.json`
- `hub.manifest`: `dreamtoosa/repos.yml`
- `hub.profiles_dir`: `dreamtoosa/profiles`
- **Architectural Guarantee:** All target reviews commit consolidated reports and state into `DreamToosa` only. Target repositories remain unpolluted by meta-documentation or reporting branches.

### C. Run Budget & Safety Caps
- `max_repos_reviewed_per_run: 6` (allows headroom for adding 2 additional targets without exceeding timeout limits)
- `max_fix_repos_per_run: 1` (strict rotation: at most 1 repo receives automated code modifications per run)
- `max_issues_per_repo_per_run: 3` (prevents issue flooding)
- `max_prs_per_run: 2` (bounds output to 1 hub report PR + at most 1 fix PR)
- `soft_time_box_minutes_per_repo: 6` (preserves sandbox execution budget)

---

## 3. Validation Audit (`dreamtoosa/validate.py`)

Execution command:
```bash
python3 dreamtoosa/validate.py
```

Result: **16/16 checks PASSED (Exit code 0)**

| Check | Result | Verification Detail |
|:---|:---:|:---|
| `repos.yml exists` | ✅ PASS | File present at `dreamtoosa/repos.yml` |
| `state.json exists` | ✅ PASS | File present at `dreamtoosa/state.json` |
| `repos.yml parses as YAML` | ✅ PASS | Clean YAML parse via `yaml.safe_load` |
| `state.json parses as JSON` | ✅ PASS | Clean JSON parse via `json.loads` |
| `repos.yml has a 'repos' list` | ✅ PASS | Non-empty `repos` array present |
| `every repo entry has 'repo' and 'profile'` | ✅ PASS | All 4 targets declare required identifiers |
| `state.json tracks exactly the manifest's repos` | ✅ PASS | Exact 1:1 match across keys |
| `fix_rotation.order covers exactly the manifest's repos` | ✅ PASS | Parity between rotation set and manifest set |
| `fix_rotation.order has no duplicates` | ✅ PASS | Set length equals list length (4 items) |
| `fix_rotation.last_index is in range` | ✅ PASS | Index `1` satisfies `-1 <= last_index < 4` |
| `every profile referenced by a repo exists` | ✅ PASS | `shell-spec-driven`, `web-playwright`, `python-lib`, `dart-flutter` all exist in `profiles/` |
| `no orphaned profile files` | ✅ PASS | No unreferenced markdown files in `profiles/` |
| `hub declares repo and reports_dir` | ✅ PASS | Declared and non-empty |
| `budget declares all required caps` | ✅ PASS | All 4 required caps defined |
| `budget caps are positive integers` | ✅ PASS | All caps are integers > 0 |
| `per-repo max_open_prs values are non-negative integers` | ✅ PASS | Caps are integers >= 0 |

---

## 4. Cross-Run State & Rotation Alignment (`state.json`)

- **Rotation Order:** `["sky2464/AgToosa", "sky2464/Crapsino", "sky2464/DreamToosa", "sky2464/miToosa"]`
- **Current Position:** `last_index = 1` (`sky2464/Crapsino`).
- **Advancement Logic:**
  - In Phase 5 of the routine, rotation advances index by 1 (mod 4).
  - Candidates are evaluated: if disabled, `fix_eligible: false`, or over `max_open_prs`, the routine advances to the next candidate.
  - The previous run advanced past `sky2464/AgToosa` (index 0, `fix_eligible: false`) to `sky2464/Crapsino` (index 1).
  - The next rotation step will evaluate `sky2464/DreamToosa` (index 2), ensuring fair multi-repo distribution.

---

## 5. Action Items & Checklist for Next Revisit

- [ ] **AgToosa Backlog Drain:**
  - Audit the 15 open PRs in `sky2464/AgToosa`.
  - Once open PRs count $\le 5$, update `dreamtoosa/repos.yml` to restore `fix_eligible: true`.
- [ ] **Routine Remote Verification:**
  - When triggering or inspecting routine runs via `RemoteTrigger`, verify that:
    - AgToosa produces report entries but opens no PR.
    - Crapsino is selected as the active fix target.
    - Consolidated report index is written to `reports/dream-report-YYYY-MM-DD.md`.
- [ ] **Target Additions / Modifications:**
  - If adding a new target repository:
    1. Add repository to the live routine's `sources` array in cloud config (required for sandbox clone).
    2. Add profile definition under `dreamtoosa/profiles/<profile>.md`.
    3. Add entry to `dreamtoosa/repos.yml`.
    4. Synchronize `dreamtoosa/state.json` (`repos` key and `fix_rotation.order`).
    5. Run `python3 dreamtoosa/validate.py` before committing.
- [ ] **CI Protection:**
  - Ensure [`.github/workflows/control-plane.yml`](../.github/workflows/control-plane.yml) remains green on all PRs modifying `dreamtoosa/**` or `tests/**`.

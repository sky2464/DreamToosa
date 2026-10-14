# Dream Report Index — 2026-10-03

> **⚠️ READ-ONLY MODE:** GitHub MCP tools returned `401 Bad credentials`. No issues were filed and no PRs were opened this run. All review findings and full test verification results across all five repositories are recorded here for human action. Re-authenticate GitHub credentials to restore remote issue and PR automation.

**Run date:** 2026-10-03  
**Session ID:** maintainer-run-2026-10-03  
**Fix rotation target:** `sky2464/DreamToosa` (index 2) — selected by rotation (AgToosa skipped: `fix_eligible: false`; Crapsino previously evaluated), but **not acted on remotely** (read-only mode).

---

## Status Table

| Repo | Profile | Commits in Window | Findings | Skipped Reason |
|------|---------|:-----------------:|----------|----------------|
| sky2464/AgToosa | shell-spec-driven | 0 | 0 new (carry-forward tracked in #153, #141, #146) | None |
| sky2464/Crapsino | web-playwright | 0 | 2 Playwright E2E failures (settlement locator timeout) | None |
| sky2464/DreamToosa | python-lib | 3 | 0 new (carry-forward client duplication documented in worktree) | None |
| sky2464/miToosa | dart-flutter | 0 | 0 (analyzer exclude hygiene) | None |
| sky2464/Agtoosa2 | python-spec-driven | 3 | 1 test regression (`test_spec_cli.py` spec count assertion 47 != 46) | None |

**Circuit breaker:** GitHub API returned 401. No repos skipped on PR count; pass-through in read-only mode.

---

## sky2464/AgToosa

**Profile:** shell-spec-driven · **HEAD:** `9784e2d`

### What Improved
- Fast verification suite passed 100% of checks across all validation gates via `scripts/test-fast.sh`:
  - Version parity: v0.3.63 (bash, ps1, npm) verified
  - Template inventory: Complete, 0 missing templates
  - Product Truth contracts: 12/12 passed (`PTC-001` through `PTC-012`)
  - Generator smoke suite: 60/60 bats tests passed cleanly (`1..60 ok`)

### What Needs Attention
Carry-forward only — all tracked in existing issues:
- **#153 — PR backlog / merge freeze:** 15 open PRs on `main` pending human review/merge/close.
- **#141 — Dependabot high-severity alerts:** Upstream security advisories.
- **#146 — Red `validate` CI gate on `main`:** Local fast test suite is 100% green; awaiting remote CI verification.
- **Working tree modifications:** Uncommitted changes in `tests/agtoosa.bats`, `docs/Master-Plan.md`, and untracked test plan files.

### Action Items
1. **(Human)** Merge or close enough of the 15 open PRs on AgToosa to clear the backlog and unblock the circuit breaker (issue #153).
2. **(Human)** Verify GitHub Actions status for commit `9784e2d` and close issue #146 once confirmed green.
3. Reconcile uncommitted working directory changes in `tests/agtoosa.bats` onto a dedicated feature branch.

---

## sky2464/Crapsino

**Profile:** web-playwright · **HEAD:** `ceb42b3`

### What Improved
- Baseline stable with zero new commits in the review window.
- Vitest suite executed locally: 53 test files passed (53/53), 418 unit and integration tests passed (418/418) covering all betting rules, layouts, advisor hints, settlement, audio, and store logic.
- Playwright browser test for bankroll exhaustion flow (`game over flow`) passed.

### What Needs Attention
- **Playwright E2E Failures:** In `e2e/pass-line.spec.ts`, 2 out of 3 tests failed:
  - `basic pass-line flow` failed at line 29 awaiting `/net this roll/i`.
  - `point and odds flow` failed at line 58 awaiting `/net this roll/i`.
- **Coverage directory hygiene:** Running vitest produces `coverage/` files that appear in git status. Adding `coverage/` to `.gitignore` will keep working trees clean.

### Action Items
1. **(Human)** Investigate Playwright E2E failures in `e2e/pass-line.spec.ts` (lines 29 & 58) regarding the `/net this roll/i` locator.
2. Add `coverage/` to `.gitignore` to prevent test coverage reports from dirtying git status.
3. Verify settlement HUD text and roll transition timing.

---

## sky2464/DreamToosa

**Profile:** python-lib · **HEAD:** `b7bab4e`

### What Improved
- **Multi-Repo Control Plane Expansion (`e97c4a9`):** Successfully onboarded `sky2464/Agtoosa2` to the daily maintainer routine manifest (`dreamtoosa/repos.yml`), declared its `python-spec-driven` profile, and integrated cross-run state tracking (`dreamtoosa/state.json`).
- **Control plane validator clean:** `dreamtoosa/validate.py` passes all 19 structural and manifest invariant checks.
- **All unit tests pass:** 13 unit tests passed (`test_dreamer.py` and `test_validate.py`); all Python files pass `py_compile`.

### What Needs Attention
- **Duplicate `DreamsClient` / `DreamConfig` implementations (Carry-Forward):**
  Three independent client definitions persist across `dreams_client.py`, `dreams_implementation.py`, and `dreamtoosa_dreams_integration.py`. Worktree branch `codex/issue-8-memory-implementations` documents implementation boundaries; full architectural consolidation remains tracked upstream.
- **GitHub MCP 401 Bad credentials:** Restricts operations to read-only mode.

### Action Items
1. **(Human)** Re-authenticate GitHub credentials to re-enable automated issue filing and PR generation.
2. Review and merge branch `codex/issue-8-memory-implementations` clarifying memory curation implementations.
3. Track long-term client unification roadmap per architectural guidelines in `AGENTS.md`.

---

## sky2464/miToosa

**Profile:** dart-flutter · **HEAD:** `2114ef2`

### What Improved
- Baseline stable with zero new commits in the review window.
- Static analysis verified clean: `flutter analyze lib test` found 0 issues.
- Full test suite verified: `flutter test` executed 950 tests with all 950 passing (0 failures).

### What Needs Attention
- **Analyzer exclude hygiene:** A general `flutter analyze` at repo root scans `build/macos/SourcePackages/` where external third-party Firebase SPM packages emit style warnings. Adding `build/**` to `analyzer.exclude` in `analysis_options.yaml` will ensure root analysis ignores external caches.
- **Untracked files:** Untracked `.cursorrules.bak.*` backup files in working directory.

### Action Items
1. **(Human)** Consider adding `build/**` to `analyzer.exclude` in `analysis_options.yaml`.
2. Clean up untracked `.cursorrules.bak.*` backup files.
3. No agent action this run; 950/950 tests passing and zero lints in project code.

---

## sky2464/Agtoosa2

**Profile:** python-spec-driven · **HEAD:** `b8dd70d`

### What Improved
- **Truthful Architecture Metrics (`97bc103`):** Replaced static mock strings with dynamic commit deltas and empirical 2-hop context telemetry in `MetricsEngine`. Added calibrated 5-tier test verification deduction curves, metadata persistence in `GraphStore`, and excluded test symbols from the production verification denominator. Added regression tests in `test_metrics.py`.
- **Streamlined Overview UX (`c53f3df`):** Redesigned the overview landing view in Web Studio to present a clean 3-bullet status summary and 3-step playbook loop.
- **Brand Identity & Docs (`b8dd70d`):** Displayed animated banner asset in root `README.md`.
- **Bytecode compilation clean:** 0 syntax or compilation errors across `agtoosa` package and tests.

### What Needs Attention
- **Regression in `test_spec_cli.py`:**
  `TestMarkdownDocParserParity.test_parse_real_repository_specs` failed with `AssertionError: 47 != 46`. The test hardcodes an assertion of 46 spec files in `docs/specs/`, but 47 spec files exist due to the addition of untracked/new specs (`epic-002`, `spec-DEV-060` through `DEV-063`).
- **Working Tree Feature Artifacts:**
  Untracked files present in `agtoosa/graph/slice_engine.py`, `tests/test_feature_lens.py`, `tests/test_playbook_sync.py`, `tests/test_playbooks.py`, etc. Maintainers should commit these to an active feature branch.

### Action Items
1. **(Human)** Update `tests/test_spec_cli.py:247` or finalize and commit the new specs (`DEV-060` through `DEV-063`, `EPIC-002`) so the spec file count assertion reflects the actual repository inventory.
2. Commit or stash untracked feature files (`agtoosa/graph/slice_engine.py`, new tests, etc.) on an active feature branch.
3. Ensure `.venv/bin/pytest` runs clean across all test suites once working tree is committed.

---

## Fix Rotation

- **Last index:** 1 (`sky2464/Crapsino`)
- **Advanced to:**
  - Candidate 2 (`sky2464/DreamToosa`): **Selected** (`enabled: true`, `fix_eligible: true`, under cap)
- **Fix work status:** Did not execute remote PR opening this run due to `READ_ONLY` mode (GitHub API 401 Bad credentials).
- `sky2464/DreamToosa` holds the fix rotation for this cycle; next in rotation will be `sky2464/miToosa` (index 3).

## Issues Filed This Run
None — GitHub API unavailable (401 Bad credentials).

## PRs Opened This Run
None — GitHub API unavailable (401 Bad credentials).

---

## Human Action Required Before Next Run

**Most important:** Re-authenticate the GitHub credentials for GitHub MCP. Without valid GitHub credentials, the routine operates in read-only mode — reports and state are written locally, but automated issues, fix branches, and PRs cannot be submitted to GitHub. Additionally, drain the 15-PR backlog on AgToosa (issue #153) to allow the PR circuit breaker to clear for that repository.

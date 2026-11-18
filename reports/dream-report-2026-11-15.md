# Dream Report — 2026-11-15

Consolidated review across the DreamToosa target fleet. Per-repo detail in `reports/<repo>/dream-report-2026-11-15.md`.

> **Notice:** GitHub MCP tools were unavailable in this environment (read-only mode). No new issues or pull requests could be filed this run.

## Status table

| Repo | Commits in window | Findings | Skipped reason |
|------|---|---|---|
| sky2464/AgToosa | 0 | None new — Milestone assignment fix on `claude/approve-merge-branches-nkfdie` (9ad3043); default branch clean at `a65c5c1`; DEV-147 GIP-013 bats test passes | — |
| sky2464/Crapsino | 0 | None new — Docker base image tags remain pinned to alpine versions (#8); 53 test files and 418 unit/component tests pass in Vitest | — |
| sky2464/DreamToosa | 0 | None — All 179 unit tests pass; `validate.py` 40/40 checks clean; bytecode compilation passes | — |
| sky2464/miToosa | 0 | None new — BL-41 atomic result commits stable on `origin/main`; docs PR #69 awaiting merge; 0 errors/warnings on `flutter analyze lib test` | — |
| sky2464/Agtoosa2 | 0 | Spec count mismatch in `tests/test_spec_cli.py` (expects 46, actual 47) from untracked specs; py_compile clean, 372/373 pytest pass | — |

All five repos are within their `max_open_prs` circuit-breaker caps: AgToosa 0/5, Crapsino 0/3, DreamToosa 0/3, miToosa 0/3, Agtoosa2 0/3.

---

## sky2464/AgToosa

**What improved:** Branch `claude/approve-merge-branches-nkfdie` refactored milestone assignment in `lib/github-issues-sync.sh` and `template/lib/github-issues-sync.sh` to assign milestones by number via the REST API rather than by title through `gh issue --milestone`. This ensures closed milestones with matching titles in the manifest sync without triggering 422 errors or unintended milestone reopens. Commit `2688311` added DEV-147 GIP-013 test assertions to `tests/agtoosa.bats`, which verified cleanly under Bats 1.14.0.

**What needs attention:** 0 open issues, 0 open PRs on `origin/main`. The default branch remains caught up at `a65c5c1`. The stated rationale for `fix_eligible: false` ("15-PR backlog on main pending drain") has drained; maintainers may consider enabling fix eligibility in `repos.yml`.

**Top action items:**
1. Review and merge `claude/approve-merge-branches-nkfdie` (number-based milestone assignment fix) into `main` when ready.
2. Re-evaluate `fix_eligible` setting in `repos.yml`.
3. Clean up closed baseline references (#146, #153, #141) in the profile documentation.

---

## sky2464/Crapsino

**What improved:** Base image pinning in `Dockerfile` (`node:20.18-alpine` and `nginx:1.27-alpine` from PR #8 / `b040a9b`) remains stable. Zero code changes in the review window; no client-side secret leaks or generated CSS drift. Vitest test suite of 53 test files and 418 unit/component tests executed and passed cleanly in 12.07s.

**What needs attention:** 0 new commits since last review. Standing limitation: Docker daemon and Playwright browser binaries are not installed in the sandbox, requiring static inspection alongside unit/component test execution.

**Top action items:**
1. Confirm `docker compose up --build` succeeds with pinned alpine tags in an environment with Docker active.
2. Review and merge `fix/dockerfile-pin-alpine` (PR #8) on remote if not yet merged.
3. Standing: provision Playwright browser binaries in CI/sandbox runner.

---

## sky2464/DreamToosa

**What improved:** Control plane validation via `dreamtoosa/validate.py` verified 40/40 checks cleanly. All 179 unit tests pass cleanly (`Ran 179 tests in 25.932s ... OK`). Bytecode compilation across all modules is completely clean.

**What needs attention:** Local branch `dreamtoosa/dev-005b-fleet-triage-ledger` has active development changes for DEV-005b in progress. These changes must remain isolated and protected from routine commits.

**Top action items:**
1. Complete and ship DEV-005b Fleet Triage ledger implementation on feature branch.
2. Maintain zero-backlog queue hygiene on the hub as daily reports land.
3. Keep routine prompt synchronized when DEV-005b merges.

---

## sky2464/miToosa

**What improved:** Commit `06340fb` on branch `docs/mitoosa-64-changelog` documents BL-39, BL-40, #48, launch readiness, BL-24, and BL-41 in `CHANGELOG.md` [Unreleased], addressing issue #68. Atomic persistence fix BL-41 (PR #65 / `c6fb644`) remains merged and clean on `origin/main`. Static analysis of `lib/` and `test/` passed with 0 errors and 0 warnings (6 minor informational notices for unnecessary imports and const constructors).

**What needs attention:** 0 new commits on default branch in window. PR #69 (`docs/mitoosa-64-changelog`, addressing issue #68 regarding Master-Plan table cell drift for BL-39/BL-40/BL-41) is open awaiting review. `gameplay_screen.dart` (1,158 lines) and `player_progress.dart` (534 lines) exceed line guidelines and remain scheduled for BL-38 / #52 modularization.

**Top action items:**
1. Review and merge PR #69 to resolve issue #68.
2. Continue modularization of oversized game screen and state controllers (#52).
3. Clean up the 6 minor informational notices (unnecessary imports and const constructors) in `lib/` and `test/`.

---

## sky2464/Agtoosa2

**What improved:** DEV-059 delivered truthful architecture metrics with calibrated deduction curves and empirical context telemetry (`97bc103`). Streamlined Web UI landing to a 3-bullet status summary and 3-step playbook (`c53f3df`). Bytecode compilation across all modules and tests passed cleanly. 372/373 pytest tests passed.

**What needs attention:** `tests/test_spec_cli.py::TestMarkdownDocParserParity::test_parse_real_repository_specs` failed (`AssertionError: 47 != 46`). 47 specification markdown files exist in `docs/specs/`, but the test assertion was hardcoded to 46 prior to new specs being staged. Working directory contains untracked feature files (`agtoosa/graph/slice_engine.py`, `swimlane_layout.js`, etc.) and new test suites.

**Top action items:**
1. Update `tests/test_spec_cli.py` spec inventory expectation to 47 when new specs are committed.
2. Commit or stash uncommitted feature artifacts on a dedicated feature branch.
3. Run full pytest suite once spec expectation is synchronized.

---

## Fix work this run

**Fix target:** No fix PR opened this run.
- **Rotation:** Advanced from index 2 (`sky2464/DreamToosa`) to index 3 (`sky2464/miToosa`).
- **Execution Mode:** Read-only mode active (GitHub MCP tools unavailable); issue filing and PR generation skipped per ground rules.

---

## Repo holding the fix rotation next run

`fix_rotation.last_index` is set to **3** (`sky2464/miToosa`). The next run's rotation target is index 4 → `sky2464/Agtoosa2`.

---

## Most important thing for a human to do before the next run

Review and merge PR #69 in `sky2464/miToosa` to resolve issue #68 and synchronize `CHANGELOG.md` and `docs/Master-Plan.md`.

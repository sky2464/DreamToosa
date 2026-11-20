# Dream Report — 2026-11-19

Consolidated review across the DreamToosa target fleet. Per-repo detail in `reports/<repo>/dream-report-2026-11-19.md`.

> **Notice:** GitHub MCP tools were unavailable in this environment (read-only mode). No new issues or pull requests could be filed this run.

## Status table

| Repo | Commits in window | Findings | Skipped reason |
|------|---|---|---|
| sky2464/AgToosa | 0 | None new — Milestone assignment fix on `claude/approve-merge-branches-nkfdie` (9ad3043); default branch clean at `a65c5c1`; DEV-147 GIP-013 bats test passes | — |
| sky2464/Crapsino | 0 | PR #8 merged on `origin/main` (`2b49279`); Docker alpine pinning landed; 53 test files and 418 unit/component tests pass in Vitest | — |
| sky2464/DreamToosa | 0 | PR #35 merged (`2d4f83f`); `validate.py` 40/40 checks pass; py_compile clean across all modules | — |
| sky2464/miToosa | 0 | None new — BL-41 atomic result commits stable on `origin/main`; docs PR #69 awaiting merge; 0 errors/warnings on `flutter analyze lib test` | — |
| sky2464/Agtoosa2 | 0 | Spec count mismatch in `tests/test_spec_cli.py` (expects 46, actual 47) from new staged specs; py_compile clean, 372/373 pytest pass | — |

All five repos are within their `max_open_prs` circuit-breaker caps: AgToosa 0/5, Crapsino 0/3, DreamToosa 0/3, miToosa 1/3, Agtoosa2 0/3.

---

## sky2464/AgToosa

**What improved:** Number-based milestone assignment via REST API on branch `claude/approve-merge-branches-nkfdie` (`9ad3043`) remains verified and stable. Shell scripts in `lib/` and `template/lib/` maintain strict quoting and local parameter scoping without unsafe evaluations. Bats test DEV-147 GIP-013 in `tests/agtoosa.bats` verified cleanly under Bats 1.14.0.

**What needs attention:** 0 open issues, 0 open PRs on `origin/main`. The stated rationale for `fix_eligible: false` ("15-PR backlog on main pending drain") has fully cleared; maintainers should consider re-enabling fix eligibility in `repos.yml`. Untracked test plan and spec artifacts in `docs/` should be committed or organized.

**Top action items:**
1. Review and merge `claude/approve-merge-branches-nkfdie` (number-based milestone assignment fix) into `main` when ready.
2. Re-evaluate `fix_eligible` setting in `repos.yml` now that `origin/main` has no PR backlog.
3. Clean up untracked docs/specs artifacts or commit them to feature branches.

---

## sky2464/Crapsino

**What improved:** Pull request #8 (`fix/dockerfile-pin-alpine`) has been merged into `origin/main` (`2b492798`), successfully landing pinned alpine base images (`node:20.18-alpine` and `nginx:1.27-alpine`) on the default branch. Vitest test suite of 53 test files and 418 unit/component tests executed and passed cleanly in 5.15s (100% pass rate). Zero client-side secrets detected.

**What needs attention:** Local clone is on branch `fix/dockerfile-pin-alpine` which is now merged upstream; working tree should be synchronized with `origin/main` (`2b492798`). Coverage artifacts in `coverage/` have uncommitted diffs. Standing limitation: Docker daemon and Playwright browser binaries are not installed in local sandbox runner.

**Top action items:**
1. Switch local working tree to `main` and pull `origin/main` (`2b492798`).
2. Clean uncommitted coverage artifacts (`git checkout -- coverage/`).
3. Confirm `docker compose up --build` succeeds with pinned alpine tags in an environment with Docker active.

---

## sky2464/DreamToosa

**What improved:** PR #35 was merged into `main` (`2d4f83f`), synchronizing cross-run state in `state.json`, backfilling reports, and introducing `dreams_api.py` with test coverage. Control plane validation via `dreamtoosa/validate.py` verified 40/40 checks cleanly. Bytecode compilation across all modules and tests passed completely clean.

**What needs attention:** `TestVerifyGit` in `tests/test_triage_cli.py` has 11 failures regarding git committer date verification logic. Maintain zero-backlog queue hygiene on the hub as daily reports land.

**Top action items:**
1. Address the 11 `TestVerifyGit` committer date assertions in `tests/test_triage_cli.py`.
2. Maintain zero-backlog queue hygiene on the hub as daily reports land.
3. Keep routine prompt documentation synchronized when DEV-005b features evolve.

---

## sky2464/miToosa

**What improved:** Atomic persistence fix BL-41 (`c6fb644`, PR #65) remains merged and stable on `origin/main`. Static analysis of `lib/` and `test/` passed with 0 errors and 0 warnings (6 minor informational notices for unnecessary imports and const constructors). Documentation PR #69 documents BL-39, BL-40, #48, launch readiness, BL-24, and BL-41 in `CHANGELOG.md`.

**What needs attention:** PR #69 (`docs/mitoosa-64-changelog`, addressing issue #68 regarding Master-Plan table cell drift for BL-39/BL-40/BL-41) is open awaiting review. `gameplay_screen.dart` (1,158 lines) and `player_progress.dart` (534 lines) exceed line guidelines and remain scheduled for BL-38 / #52 modularization.

**Top action items:**
1. Review and merge PR #69 to resolve issue #68.
2. Continue modularization of oversized game screen and state controllers (#52 / BL-38).
3. Clean up the 6 minor informational notices (unnecessary imports and const constructors) in `lib/` and `test/`.

---

## sky2464/Agtoosa2

**What improved:** High test pass rate (372 of 373 pytest tests passed). Bytecode compilation across all modules and tests passed cleanly. Truthful architecture metrics (`97bc103`), streamlined landing playbook (`c53f3df`), and animated AgToosa banner in README (`b8dd70d`) remain stable on `origin/main`.

**What needs attention:** `tests/test_spec_cli.py::TestMarkdownDocParserParity::test_parse_real_repository_specs` failed (`AssertionError: 47 != 46`). 47 specification markdown files exist in `docs/specs/`, but the test assertion was hardcoded to 46 prior to new specs being staged. Working directory contains untracked feature files (`agtoosa/graph/slice_engine.py`, `swimlane_layout.js`, etc.).

**Top action items:**
1. Update `tests/test_spec_cli.py` spec inventory expectation to 47 when new specs are committed.
2. Commit or stash uncommitted feature artifacts on a dedicated feature branch.
3. Re-run full pytest suite once spec expectation is synchronized.

---

## Fix work this run

**Fix target:** No fix PR opened this run.
- **Rotation:** Advanced from index 1 (`sky2464/Crapsino`) to index 2 (`sky2464/DreamToosa`).
- **Execution Mode:** Read-only mode active (GitHub MCP tools unavailable); issue filing and PR generation skipped per ground rules.

---

## Repo holding the fix rotation next run

`fix_rotation.last_index` is set to **2** (`sky2464/DreamToosa`). The next run's rotation target is index 3 → `sky2464/miToosa`.

---

## Most important thing for a human to do before the next run

Review and merge open PRs awaiting decision:
1. `sky2464/miToosa`: Review and merge PR #69 (`docs/mitoosa-64-changelog`) to close issue #68.
2. `sky2464/AgToosa`: Review and merge `claude/approve-merge-branches-nkfdie` (number-based milestone assignment fix) into `main`.
3. `sky2464/Crapsino`: Switch local working tree to `main` and clean uncommitted coverage diffs.

# Dream Report Index — 2026-09-20

> **⚠️ READ-ONLY MODE:** GitHub MCP tools returned `401 Bad credentials`. No issues were filed and no PRs were opened this run. All review findings and full test verification results across all four repositories are recorded here for human action. Re-authenticate GitHub credentials to restore remote issue and PR automation.

**Run date:** 2026-09-20  
**Session ID:** maintainer-run-2026-09-20  
**Fix rotation target:** `sky2464/Crapsino` (index 1) — selected by rotation (AgToosa skipped: `fix_eligible: false`), but **not acted on** (read-only mode).

---

## Status Table

| Repo | Profile | Commits in Window | Findings | Skipped Reason |
|------|---------|-------------------|----------|----------------|
| sky2464/AgToosa | shell-spec-driven | 1 | 0 new (carry-forward tracked in #153, #141) | None |
| sky2464/Crapsino | web-playwright | 0 | 0 (working tree coverage hygiene) | None |
| sky2464/DreamToosa | python-lib | 4 | 0 new (DEV-004 & CHANGELOG resolved; carry-forward client duplication) | None |
| sky2464/miToosa | dart-flutter | 0 | 0 (build directory analyzer exclude hygiene) | None |

**Circuit breaker:** GitHub API returned 401. No repos skipped on PR count; pass-through in read-only mode.

---

## sky2464/AgToosa

**Profile:** shell-spec-driven · **HEAD:** `9784e2d`

### What Improved
- **Bats smoke filter alternation precedence fixed (`9784e2d`):** In `.github/workflows/ci.yml` and `scripts/test-fast.sh`, the test filter regex was grouped properly as `-f '@smoke (BCL|PN|WP2|ACC|NET|PSP|CORE)'`. This ensures bats only runs tests tagged `@smoke` matching those prefixes, eliminating false matches.
- **Verification 100% green:** `scripts/test-fast.sh` passed all 31 checks:
  - Version parity: v0.3.63 (bash, ps1, npm)
  - Template inventory: 0 missing files
  - Product Truth contracts: 12/12 passed
  - Generator smoke suite: 19/19 bats tests passed

### What Needs Attention
Carry-forward only — all tracked in existing issues:
- **#153 — PR backlog / merge freeze:** 15 open PRs on `main` pending human review/merge/close.
- **#141 — Dependabot high-severity alerts:** Upstream security advisories.
- **#146 — Red `validate` CI gate:** Local runs of the fast test suite are now completely green (19/19 smoke tests pass). Once remote CI verifies commit `9784e2d`, issue #146 can be closed.

### Action Items
1. **(Human)** Merge or close enough of the 15 open PRs on AgToosa to clear the backlog and unblock the circuit breaker (issue #153).
2. **(Human)** Verify GitHub Actions status for commit `9784e2d` and close issue #146 once confirmed green.
3. No agent action this run (`fix_eligible: false`).

---

## sky2464/Crapsino

**Profile:** web-playwright · **HEAD:** `ceb42b3`

### What Improved
- Baseline stable with zero new commits in the review window.
- Vitest suite executed locally: 53 test files passed (53/53), 418 unit and integration tests passed (418/418) covering all betting rules, layouts, advisor hints, settlement, audio, and store logic.

### What Needs Attention
- **Coverage directory hygiene:** Running tests generates `coverage/` files that appear in git status. Adding `coverage/` to `.gitignore` will keep working trees clean.
- **E2E browser testing:** Full Playwright browser execution requires browser binaries (`npm run test:e2e`).

### Action Items
1. **(Human)** Add `coverage/` to `.gitignore` to prevent test coverage reports from showing up in git status.
2. Verify Playwright browser suite before next feature deployment.
3. Fix rotation has advanced to `sky2464/Crapsino` (index 1) for the next cycle with active GitHub credentials.

---

## sky2464/DreamToosa

**Profile:** python-lib · **HEAD:** `a8b4beb`

### What Improved
- **`CHANGELOG.md` created (`a8b4beb`):** Formatted following Keep a Changelog standard with SemVer versioning, backfilling all changes for DEV-001, DEV-002, DEV-003, and DEV-004 under `[Unreleased]`. This completely resolves **Finding 2** from the 2026-09-18 report.
- **Master-Plan drift resolved (`a8b4beb`):** `Docs/Master-Plan.md` updated: DEV-004 marked as `🏁 Shipped`, added to "Completed This Cycle" table with spec link to `spec-DEV-004.md`, and Update Log appended with `2026-09-18 | ship DEV-004 shipped | DreamToosa`. This completely resolves **Finding 1** from the 2026-09-18 report.
- **Control plane validator clean:** `dreamtoosa/validate.py` passes all 19 structural and manifest invariant checks.
- **All tests pass:** 13 unit tests passed (`test_dreamer.py` and `test_validate.py`); all Python files pass `py_compile`.

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
- Full test suite verified: `flutter test` executed 950 tests in 36.5s with all 950 passing (0 failures).

### What Needs Attention
- **Analyzer exclude hygiene:** A general `flutter analyze` at repo root flags third-party SPM packages in `build/macos/SourcePackages/`. Adding `build/**` to `analyzer.exclude` in `analysis_options.yaml` will ensure root analysis ignores external caches.
- **Untracked files:** Untracked `.cursorrules.bak.*` backup files in working directory.

### Action Items
1. **(Human)** Consider adding `build/**` to `analyzer.exclude` in `analysis_options.yaml`.
2. Clean up untracked `.cursorrules.bak.*` backup files.
3. No agent action this run; 950/950 tests passing and zero lints in project code.

---

## Fix Rotation

- **Last index:** 3 (`sky2464/miToosa`)
- **Advanced to:**
  - Candidate 0 (`sky2464/AgToosa`): Skipped (`fix_eligible: false`, 15-PR backlog)
  - Candidate 1 (`sky2464/Crapsino`): **Selected** (`enabled: true`, `fix_eligible: true`, under cap)
- **Fix work status:** Did not execute this run due to `READ_ONLY` mode (GitHub API 401 Bad credentials).
- `sky2464/Crapsino` retains the fix rotation for the next cycle.

## Issues Filed This Run
None — GitHub API unavailable (401 Bad credentials).

## PRs Opened This Run
None — GitHub API unavailable (401 Bad credentials).

---

## Human Action Required Before Next Run

**Most important:** Re-authenticate the GitHub credentials for GitHub MCP. Without valid GitHub credentials, the routine operates in read-only mode — reports and state are written locally, but automated issues, fix branches, and PRs cannot be submitted to GitHub. Additionally, drain the 15-PR backlog on AgToosa (issue #153) to allow the PR circuit breaker to clear for that repository.

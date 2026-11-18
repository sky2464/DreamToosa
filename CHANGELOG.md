# Changelog

All notable changes to DreamToosa will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioned per [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- **Fleet Triage report core (DEV-005a), unreleased.**
  - **Read-only Fleet Triage block:** a deterministic block at the top of each daily Dream Report index, with four freshness rows and pull request, default-branch CI and issue sections. A section the run could not read renders as "not evaluable", never as zero or green. The block never approves, merges, comments on or edits anything, and it withholds private-repo details from the public hub.
  - **Deterministic engine:** severity comes only from reviewable rules in `dreamtoosa/triage.py` (C1 to C3, U1 to U4, H1 to H7, with caps and an evidence gate). `dreamtoosa/triage_report.py` provides the `check`, `render` and `heartbeat` commands, git re-verification of snapshot facts and marker-based injection. The model gathers facts only, and a snapshot carrying a `severity` key is rejected.
  - **Validator keys:** additive, guarded `dreamtoosa/repos.yml` keys checked by `dreamtoosa/validate.py` (per-repo `visibility`, `backlog` mapping, workflow lists and `dependabot_scope`; a `triage` block; `hub.force_read_only`; a Fleet Triage time box). A manifest without them still passes.
  - **CI:** the test suite and `validate.py` run in `.github/workflows/control-plane.yml`. Not yet released.
- **Fleet Triage ledger, golden pick, heartbeat job and notify (DEV-005b), unreleased and not accepted.**
  - Ledger carry-forward (`merge_ledger`, `parse_ledger`, `serialize_ledger`), `golden_pick`, and `notify_decision` / `notify_message` live in `dreamtoosa/triage.py`. `triage_report.py` adds prev-index ledger injection, a `notify` subcommand, and chain-base selection. No `triage_ledger.py`.
  - `repos.yml` adds `golden_exclude: []`, `golden_formula_validated: false`, and `upstream_repos: []`. The formula flag stays false.
  - The golden fixture was not written. OI-1 is recorded for owner review: on the pinned public backlogs the only eligible row is AgToosa DEV-153 (score -1, R=0 S=1 L=0 P=0 B=1 Rep=0), with no runner-up.
  - Golden fixes: the rendered pick now checks the archived spec at the pinned tip (S term), drops IDs from released CHANGELOG sections, and keeps no row text, section or path for non-public rows (TRI-B-006, 010, 011).
  - Dry-run fixes: `chain_base_from_git` loads the engine first; `notify` exits `E_SCHEMA` when the snapshot misses an enabled manifest repo, instead of an uncaught `E_RUN`; the routine prompt seeds an empty prev-index on the first run so day 2 does not flag every finding as NEW.
  - CI: `actions/checkout@v7`, `actions/setup-python@v7`, validate job on Python 3.12 and 3.15, PyYAML pinned to 6.0.3.
  - Heartbeat CI is `cron: '30 16 * * *'` plus `workflow_dispatch`. The validate job does not run on `schedule`. No live push notification was sent.
- **Resilient Multi-Repo Control Plane & PR Lifecycle (DEV-004).**
  - **Dynamic clone root discovery (AC-004):** Replaces hardcoded sandbox assumptions with runtime environment resolution (`DREAMTOOSA_CLONE_ROOT` → sibling directory search → fallback).
  - **Pre-flight auth probe & push prohibition (AC-005):** Probes GitHub API credentials during initialization; on 401/403, transitions execution to `READ_ONLY` mode and explicitly prohibits remote `git push` operations.
  - **Hub circuit breaker (AC-001):** Configurable `hub.max_unmerged_report_prs` cap in `repos.yml` to prevent runaway unmerged report PR queues.
  - **PR chaining strategy (AC-003):** Chained report PR branches against origin head to maintain unbroken `state.json` lineage across multi-day cycles without merge conflicts.
  - **Host workspace safety (AC-006):** Prohibits destructive working-tree resets (`git checkout -- <file>` / `git restore`) on shared environments.
  - **Programmatic validator & unit test suite (AC-007, AC-008):** Refactored `validate.py` into a modular function `validate_control_plane()` with 19 invariant checks, and added `tests/test_validate.py` (8 unit tests).
- **Local agent memory curation engine & CLI (DEV-003).**
  - Canonical local `Dreamer` and JSON `MemoryStore` in `dreamtoosa/dreamer.py`.
  - Comprehensive unit test suite in `tests/test_dreamer.py`.
  - Runnable end-to-end demo via `python3 dream_example.py` and `python3 -m dreamtoosa --demo`.
- **Control plane CI validation (DEV-002).**
  - GitHub Actions workflow `.github/workflows/control-plane.yml` executing `python3 dreamtoosa/validate.py` on pull requests and pushes to `main`.
  - Root project `README.md` and architecture documentation.

## [0.1.1] — 2026-10-14

### Changed

- **Unified remote Dreams client (DEV-005).** Single `DreamConfig`/`DreamsClient` in `dreams_implementation.py`; `DreamWorkflow` in `dreams_workflow.py`; removed `dreams_client.py`; `dreamtoosa_dreams_integration.py` delegates to the canonical client; `tests/test_dreams_implementation.py` (17-test suite). Spec/review: `Docs/archived/spec-DEV-005.md`, `review-DEV-005.md`.

## [0.1.0] — 2026-10-13

### Added

- **Multi-repo control plane for Dream Report routine (DEV-001).** Five-repo manifest (`dreamtoosa/repos.yml`), stack profiles, cross-run `state.json`, canonical `ROUTINE_PROMPT.md`, validator CI, and dream reports through 2026-10-03. Archived spec and review under `Docs/archived/`.

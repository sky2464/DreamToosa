# Changelog

All notable changes to DreamToosa will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioned per [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

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
  - GitHub Actions workflow `.github/workflows/validate.yml` executing `python3 dreamtoosa/validate.py` on pull requests and pushes to `main`.
  - Root project `README.md` and architecture documentation.

## [0.1.0] — 2026-10-13

### Added

- **Multi-repo control plane for Dream Report routine (DEV-001).** Five-repo manifest (`dreamtoosa/repos.yml`), stack profiles, cross-run `state.json`, canonical `ROUTINE_PROMPT.md`, validator CI, and dream reports through 2026-10-03. Archived spec and review under `Docs/archived/`.

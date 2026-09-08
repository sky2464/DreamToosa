# Spec — DEV-003: Local Agent Memory Curation Engine and CLI

- **ID:** DEV-003
- **Epic:** DEV-101
- **Type:** Feature
- **Status:** Shipped
- **Created:** 2026-09-08
- **Shipped:** 2026-09-08

---

## 1. Goal Contract

### 1.1 Goal
Provide a local, self-contained agent memory curation engine and CLI that replicates the core "Dreaming" workflow (deduplication, conflict resolution, clustering, and higher-order insight synthesis) without requiring external cloud endpoints or proprietary beta keys.

### 1.2 User Outcome
Developers using Antigravity or local workflows can curate and deduplicate agent memory stores directly on their machine with zero external network dependencies.

### 1.3 Success Condition
- `dreamtoosa.dreamer` module provides `MemoryStore` and `Dreamer`.
- CLI supports `--demo`, `--curate`, and `--inspect`.
- Standard library unit tests pass.
- GitHub Actions CI verifies both the control plane and test suite.

### 1.4 Proof / Evidence
- `tests/test_dreamer.py` runs 5 tests and passes (0.002s).
- `python3 -m dreamtoosa --demo` executes successfully.
- CI passes on PR #7.

---

## 2. Acceptance Criteria

| ID | Priority | Description | Verification |
|----|----------|-------------|--------------|
| AC-1 | Must | Reusable `MemoryStore` class supporting JSON persistence and category filtering | `test_save_and_load` |
| AC-2 | Must | Curation engine performing deduplication and chronological conflict resolution | `test_curate_conflict_resolution` |
| AC-3 | Must | CLI interface runnable via `python3 -m dreamtoosa` | CLI invocation |
| AC-4 | Must | Unit test suite executing with standard Python `unittest` | `python3 -m unittest discover tests` |

---

## ✅ Spec Approved
- **Approved by:** Chicademy & Navid
- **Timestamp:** 2026-09-08T01:00:00Z

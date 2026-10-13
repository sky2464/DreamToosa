# Review — DEV-005: Unify duplicate DreamsClient / DreamConfig modules

> **Story ID:** DEV-005  
> **Review date:** 2026-10-14  
> **Scope:** Security + Architecture (`/agtoosa-review` focused)  
> **Diff:** `a50f872..e65ef17` (main)

### Plan-Mode Review Briefing (findings)

| Subsection | Content |
|------------|---------|
| **Persona synthesis** | **Security:** No secrets in diff; memory content still printed to stdout (carry-forward). **EM/Arch:** Single client boundary achieved; line limits OK; Master-Architecture risk row stale; CI path filters may skip root-module-only edits. |
| **Iron Law hypotheses** | N/A — no 🔴 Critical defects. |
| **Cross-model gate** | Skipped — `cross_model: recommended`; chore refactor with mocked tests; user scoped security+arch only. |
| **Host mode handoff** | Agent-mode artifact write 2026-10-14. |

## Goal Contract alignment

| Field | Verdict |
|-------|---------|
| Goal (single canonical remote client) | 🟢 Met — one `DreamConfig` / `DreamsClient` in `dreams_implementation.py` |
| Success condition | 🟢 Met — `dreams_client.py` removed; integration delegates; grep confirms single class |
| Proof / evidence | 🟢 `unittest` 17/17 OK; `py_compile` on touched modules |

## Structured findings

| Sev | ID | Finding | Persona | Fix |
|-----|-----|---------|---------|-----|
| 🟡 | DEV-005-W1 | `Docs/Master-Architecture.md` still lists "Duplicate DreamsClient implementations" under Maintainability risk — contradicts shipped design. | Arch | Update architecture doc risk row to reflect DEV-005. |
| 🟡 | DEV-005-W2 | `.github/workflows/control-plane.yml` `paths:` omits root `dreams_*.py`; changes-only to canonical client may skip CI until `tests/` or `dreamtoosa/` change. | Arch | Add `dreams_*.py` or `*.py` at repo root to workflow paths. |
| 🟡 | DEV-005-W3 | `review_curated_memory` double-prints: `DreamsClient.review_memories` already prints previews; integration loops and prints again. | Arch | Deduplicate display (pass `verbose=False` or split list vs print API). |
| 🟡 | DEV-005-W4 | `review_memories` / workflow print memory snippets to stdout — sensitive curated content may land in logs (STRIDE: Information Disclosure). | Security | Document in module docstring; optional redaction flag for production adopters. |
| 🟡 | DEV-005-W5 | `instructions` and memory content flow to remote API without validation — untrusted caller input is a prompt-injection surface (educational repo; spec STRIDE noted). | Security | Keep as agent-instructed; no code change required for merge. |
| 🟡 | DEV-005-W6 | `dream_example.py` still uses standalone `DreamOrchestrator` with direct SDK calls — out of DEV-005 scope but remains parallel remote path. | Arch | Track as follow-up chore or document in README. |
| 🟢 | DEV-005-P1 | No `DreamsClient` / `DreamConfig` duplicate classes; files &lt; 500 lines (`369` / `134` / `423`). | Arch | — |
| 🟢 | DEV-005-P2 | Injectable `DreamsClient` on `DreamToosaDreamsManager` improves testability. | Arch | — |
| 🟢 | DEV-005-P3 | No credentials or real resource IDs introduced in diff. | Security | — |
| 🟢 | DEV-005-P4 | Threat model in spec DEV-005 §2.3 addressed by consolidation (single validation path). | Security | — |

## Terminal evidence

| Command | Exit | Result |
|---------|------|--------|
| `python3 -m unittest discover -s tests -q` | 0 | 17 tests OK |
| `wc -l dreams_implementation.py dreams_workflow.py dreamtoosa_dreams_integration.py` | 0 | 369, 134, 423 lines |

## Verdict

**PASS** — No unresolved 🔴 Critical findings. Proceed to `/agtoosa-ship` after optional 🟡 cleanup.

## Cross-Model Review

Skipped — low-risk internal refactor; user requested security+arch subset only.

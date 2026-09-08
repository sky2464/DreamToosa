# AgToosa Quickref

> One-page contract. Load this first; open the deep docs only when a command needs them.
> Canonical detail lives in `Docs/AgToosa_Agent.md` — this file never contradicts it.

## Day 1 — two commands

| Step | Command | Deep doc (read on use) |
|------|---------|------------------------|
| 0. Once per project | `/agtoosa-init` | `Docs/AgToosa_Init.md` |
| 1. Always | `/agtoosa-next` | `Docs/AgToosa_Next.md` — repeat after each phase |

`/agtoosa-next` drives spec → build → review → ship (and tributaries: fix, test, docs) via SYNC. Say **next** again to advance.

## Advanced lifecycle (parallel / personas)

| Command | Deep doc |
|---------|----------|
| `/agtoosa-spec` | `Docs/AgToosa_Spec.md` |
| `/agtoosa-build` | `Docs/AgToosa_Build.md` |
| `/agtoosa-review` | `Docs/AgToosa_Review.md` |
| `/agtoosa-ship` | `Docs/AgToosa_Ship.md` |

Utilities (on demand): `/agtoosa-status`, `/agtoosa-task`, `/agtoosa-qa`, `/agtoosa-goal`, `/agtoosa-update`, `/agtoosa-debug`, `/agtoosa-revert`, `/agtoosa-concise`, `/agtoosa-handoff`, `/agtoosa-import`, `/agtoosa-evidence`, `/agtoosa-help`, `/agtoosa-catalog`, `/agtoosa-tracker` (`Docs/AgToosa_TrackerSync.md`) — each maps to `Docs/AgToosa_<Name>.md`.

## Non-negotiables

1. **`Docs/Master-Plan.md` is the only PM source of truth.** Update it first;
   external trackers are mirrors created only on explicit request.
2. **Spec before build.** No implementation without an approved spec
   (`## ✅ Spec Approved` in `Docs/archived/spec-<id>.md`).
3. **TDD with evidence.** RED (captured failing run) → GREEN (captured passing
   run) → REFACTOR. Claims without terminal evidence don't count.
4. **Phase order.** spec → build → review → ship. Out-of-order runs warn and
   abort (see `Docs/AgToosa_Governance.md`).
5. **Stop at phase boundaries.** Finish the phase, report, wait for the user
   unless they explicitly asked to chain phases.
6. **Freeform Project Intake.** Asks without `/agtoosa-*` use dual-mode intake
   per `Docs/AgToosa_Agent.md` → Project Intake Protocol (Standing Corrections in `Docs/Context/workflow.md`; **AgToosa Lifecycle Compass** anchors freeform asks to Spec → Build → Review → Ship).
7. **Scope discipline.** Stay inside the spec's Build Scope; new ideas go to
   the Master-Plan Backlog, not into the current diff.
7. **Work Package DAG (when present).** Specs may declare `### 3.4 Work Package DAG` rows; Build checks ownership before fan-out; Handoff/Import report gaps. Agent-instructed derivation; generator-enforced schema copies; bats/CI when wired.
8. **Optional worktree isolation.** See `Docs/AgToosa_Worktree.md` for M+ multi-package lanes; Git commands are **manual**.
9. **Orchestration Brain.** Before lifecycle fan-out, run step 0 in `Docs/AgToosa_Orchestration.md` (inventory → lanes → merge). Agent-instructed; not a runtime scheduler.

## State files

| File | Role |
|------|------|
| `Docs/Master-Plan.md` | Stories, tasks, status, update log |
| `Docs/archived/spec-<id>.md` | Story spec (active until shipped, then stays archived) |
| `Docs/AgToosa_TestPlan-<id>.md` | AC-to-test mapping + RED/GREEN evidence |
| `Docs/archived/review-<id>.md` | Review verdicts |
| `Docs/agtoosa-events.jsonl` | Append-only phase-event log (one JSON line per transition) |
| `Docs/agtoosa-evidence.jsonl` | Optional JSONL mirror of per-story evidence ledger (non-authoritative; canonical is `Docs/archived/evidence-<id>.md`) |
| `Docs/archived/retro-<YYYY-MM-DD>.md` | Structured `/agtoosa-ship retro` artifact (proposals only; see `Docs/AgToosa_Retro.md`) |
| `Docs/Context/*.md` | Product, tech-stack, workflow context |

## Verification

Deterministic, no-AI gate — run any time, and in CI:

```bash
bash Docs/agtoosa-verify.sh            # gates: context, specs, ACs, evidence
bash Docs/agtoosa-verify.sh --strict   # warnings fail too
bash Docs/agtoosa-verify.sh stats      # cycle analytics
bash Docs/agtoosa-dashboard.sh         # local Markdown/HTML state projection (see AgToosa_Dashboard.md)
```

| Gate | Checks |
|------|--------|
| 1 — Context | `Context/product.md`, `tech-stack.md`, `workflow.md` exist and have no template placeholders |
| 2 — Master-Plan | Epic rows present; Update Log within rotation budget (150 rows) |
| 3 — Spec approval | Active-cycle stories have approved specs, EARS AC rows, threat model, AC→test mapping, RED evidence, task tree, Wave Plan |
| 4 — Review | Done stories have archived review artifacts |
| 5 — Version | Generator bash/ps1 parity (maintainer repos) or installed `.agtoosa-version` marker |

CI gate: `Docs/agtoosa-gate.yml.example` is a **template only** until you
copy, review, push, and observe a run. Full sequence:
[Docs/examples/verifier-ci-adoption.md](examples/verifier-ci-adoption.md).

## Generator CLI (install/maintenance)

```bash
bash agtoosa.sh --doctor .     # version skew, wiring gaps, context health
bash agtoosa.sh --uninstall .  # remove AgToosa-owned files (keeps your data)
bash agtoosa.sh --update .     # refresh workflow docs from generator
```

## Phase-event logging

At every phase transition append one line to `Docs/agtoosa-events.jsonl`:

```json
{"ts":"2026-01-01T00:00:00Z","phase":"build","event":"complete","story":"DEV-012","by":"AgToosa"}
```

`phase` ∈ init|spec|build|review|ship|qa|task|handoff|import|evidence; `event` ∈ start|complete|blocked.

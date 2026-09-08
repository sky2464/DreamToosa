<!-- AgToosa v0.3.63 START -->

# AgToosa — Claude Code Instructions

You are acting as an autonomous Agentic AI PM and Senior Engineer utilizing the **AgToosa** framework.

## Critical First Step

Before beginning any task, read and follow `Docs/AgToosa_Agent.md` for core rules, principles, and security requirements.

**Freeform asks** without `/agtoosa-*` trigger **AgToosa Project Intake** (dual-mode) per `Docs/AgToosa_Agent.md` → Project Intake Protocol (including **AgToosa Lifecycle Compass**).

## Core Commands

When the user types any of these commands, read the corresponding workflow file and execute it precisely.
Running a command without a sub-command runs the full flow; a sub-command runs only the indicated part.

| Command | Workflow File | Sub-commands |
|---------|--------------|--------------|
| `/agtoosa-init` | `Docs/AgToosa_Init.md` | `zoom-out` |
| `/agtoosa-spec` | `Docs/AgToosa_Spec.md` | `research` · `plan` · `quick` · `tasks` · `amend` · `to-issues` |
| `/agtoosa-build` | `Docs/AgToosa_Build.md` | `tdd` · `test` |
| `/agtoosa-qa` | `Docs/AgToosa_QA.md` | `plan` · `run` · `report` · `triage` |
| `/agtoosa-review` | `Docs/AgToosa_Review.md` | `security` · `arch` · `debug` · `cross` · `cross-model` |
| `/agtoosa-ship` | `Docs/AgToosa_Ship.md` | `check` · `docs` · `retro` |

**Optional utilities:** `/agtoosa-goal` → Read `Docs/AgToosa_Goal.md` (clarify project/story outcomes) · `/agtoosa-revert` → Read `Docs/AgToosa_Revert.md` (git-aware rollback) · `/agtoosa-task` → Read `Docs/AgToosa_Task.md` (fast task capture to Master-Plan.md) · `/agtoosa-handoff` → Read `Docs/AgToosa_Handoff.md` (export handoff pack for async/external agent) · `/agtoosa-import` → Read `Docs/AgToosa_Import.md` (import external agent results before task closure) · `/agtoosa-evidence` → Read `Docs/AgToosa_Evidence.md` (create or finalize per-story evidence ledger) · `/agtoosa-update` → Read `Docs/AgToosa_Update.md` (update workflow files to latest) · `/agtoosa-status` → Read `Docs/AgToosa_Status.md` (read-only project health dashboard)

See `Docs/AgToosa_Agent.md` for the full sub-command reference.

## Key References

- `Docs/Master-Plan.md` — Source of truth for project state and backlog
- `Docs/AgToosa_Goal.md` — Goal clarification utility/sub-workflow
- `Docs/AgToosa_Skills.md` — Subagent skill-to-command mapping
- `Docs/AgToosa_Changelog.md` — Project changelog
- `Docs/Context/` — Product, tech-stack, and workflow configuration

Always keep `Docs/Master-Plan.md` up to date — it is the source of truth for project state and backlog.

<!-- AgToosa END -->

# AgToosa Subagent Skills

## Objective
Map specific agent personas and functional skills to slash commands so that the correct context and toolset is activated automatically based on the phase of the project.

## Skill Mapping

1.  **`/agtoosa-init` (The Architect):**
    *   **Skills:** AI config validation, Context mapping, Dependency analysis, File system templating, TDD configuration.
    *   **Focus:** Validating AI assistant configs, establishing project boundaries, product requirements, technical constraints, and workflow preferences.

2.  **`/agtoosa-spec` (The PM & Security Modeler):**
    *   **Skills:** Web research, Requirements gathering, Data Flow Diagram (DFD) generation, STRIDE threat modeling, Architectural planning.
    *   **Focus:** Writing executable specifications with embedded architectural blueprints and threat models.

3.  **`/agtoosa-goal` (The Prompt Strategist):**
    *   **Skills:** Goal clarification, ambiguity detection, success-condition design, evidence mapping, scope boundary capture.
    *   **Focus:** Acting as an optional sub-workflow called directly or by init/spec/review/ship when intent or proof of completion is unclear.

4.  **`/agtoosa-build` (The Tech Lead & Specialist Engineers):**
    *   **Skills:** Dependency validation (checking latest versions), Task parallelization, Workflow breakdown, TDD enforcement.
    *   **Sub-Skills (activated per task):** `frontend-ui-engineering`, `api-and-interface-design`, `database-schema-design`, `devops-infrastructure`.
    *   **Focus:** Breaking down the Spec, writing tests FIRST (Red), implementing minimal code (Green), refactoring (Blue), then comprehensive unbiased testing in isolated sandboxes.

5.  **`/agtoosa-qa` (The QA Engineer):**
    *   **Skills:** Test plan generation, AC-to-test-ID mapping, smoke set tagging, defect triage, severity scoring (P0–P4), Master-Plan.md defect capture.
    *   **Personas:**
        *   🧪 Test Planner — maps spec ACs to test IDs and edge cases
        *   🔎 Test Runner — executes suite and captures AC coverage gaps
        *   📋 Report Writer — generates structured QA reports
        *   🚦 Triage Lead — scores defects and adds P0–P2 items to `Docs/Master-Plan.md` Backlog
    *   **Focus:** Giving QA testers a dedicated command to own — from test plan through defect lifecycle — separate from code review.

6.  **`/agtoosa-review` (The Evaluators):**
    *   **Skills:** Code simplification, OWASP audits, Secrets scanning, Lint enforcement, cross-model reviewer delegation.
    *   **Personas:**
        *   🔒 Security Officer — Audits & SAST/DAST
        *   👷 Engineering Manager — Architecture compliance
        *   📊 CEO / Product Owner — Feature alignment
        *   🧪 QA Lead — Test coverage & edge cases
        *   🔀 Independent Reviewer — read-only cross-model lane (`/agtoosa-review cross-model`; see `Docs/AgToosa_CrossModelReview.md`)
    *   **Sub-commands:** `security` · `arch` · `debug` · `cross` · `cross-model` — dispatch without duplicating canonical docs inline.
    *   **Parallel:** on hosts with native subagent delegation, run virtual personas and cross-model reviewer lanes in parallel; otherwise sequential with explicit fallback note.

7.  **`/agtoosa-ship` (The DevOps Engineer & PM):**
    *   **Skills:** Automated health checks, Zero-downtime deployment strategies, Workspace archiving, Changelog generation, Next-story suggestion.

8.  **`/agtoosa-revert` (The Safety Net):**
    *   **Skills:** Git-aware logical rollbacks by phase/task, Context & plan synchronization.

9.  **`/agtoosa-status` (The Auditor):**
    *   **Skills:** Master-Plan.md section parsing, status pill validation, checkbox arithmetic, git log analysis, file-system inventory, cross-reference consistency checking, health score computation.
    *   **Personas:**
        *   📊 Dashboard Compiler — parses Master-Plan.md sections and computes health metrics
        *   🔍 Git Archaeologist — scans commit history for unreported progress and stale branches
        *   🗂️ Orphan Hunter — detects spec files and task IDs not tracked in Master-Plan
    *   **Focus:** Providing a scannable, read-only health report with actionable findings. Never modifies state — only observes and recommends.

10. **`/agtoosa-status-guide` (The Auditor + Coach):**
    *   **Skills:** Status dashboard interpretation, Part 5.5 Recommended Next Actions ranking, finding-to-command mapping, authorization gating.
    *   **Personas:**
        *   📊 Auditor — runs `/agtoosa-status` without modifying files or git state
        *   🧭 Coach — presents the top three recommended actions with finding IDs and rationale
    *   **Focus:** Helping the user choose the next fix command while preserving the read-only status guarantee until the user explicitly authorizes a command.

## Codex Workflow Prompts And Skills

AgToosa installs one Codex slash prompt per lifecycle command under `.codex/prompts/agtoosa-*.md` and one Codex skill under `.codex/skills/agtoosa-*/SKILL.md`. Prompt files make `/agtoosa-*` visible in Codex slash-command pickers; skill files are **workflow runners**, not thin doc pointers.

### Minimum contract (all `agtoosa-*` workflow skills)

| Requirement | Rule |
|-------------|------|
| Frontmatter | Valid YAML with `name` (matches folder) and `description` (one sentence, when to trigger) |
| Canonical doc | Must name the matching `Docs/AgToosa_*.md` workflow file |
| Execution | Must instruct the agent to **read and execute** that workflow, preserving its approval gates and closure line |
| Sub-commands | Skills for commands with sub-commands must **Dispatch** to the sub-command named in the workflow doc without pasting the full doc inline |
| Progressive disclosure | Keep the skill body concise; link to the workflow doc for full steps |

Installed workflow skills: `agtoosa-init`, `agtoosa-spec`, `agtoosa-build`, `agtoosa-qa`, `agtoosa-review`, `agtoosa-ship`, `agtoosa-revert`, `agtoosa-task`, `agtoosa-handoff`, `agtoosa-import`, `agtoosa-evidence`, `agtoosa-update`, `agtoosa-status`, `agtoosa-goal`, `agtoosa-help`, `agtoosa-debug`, `agtoosa-concise`.

## Project Specialists (cross-platform v1)

`/agtoosa-init` runs **Project Specialist Discovery**; `/agtoosa-update` runs a read-only **Specialist Compatibility Check** and may propose post-Verify materialization; `/agtoosa-spec` runs **Spec Specialist Orchestration** when `Docs/Context/specialists.md` exists.

| Topic | Rule |
|-------|------|
| Canonical doc | `Docs/AgToosa_Specialists.md` |
| Roster | `Docs/Context/specialists.md` — created only after approval; **not** in template pack |
| Reserved names | No `agtoosa-*` specialist ids or `/agtoosa-*` triggers |
| Evidence | Structured block required in terminal output (see Specialists doc) |
| Parallel | Claude Code native; other platforms sequential with explicit fallback note |
| CLI update | `agtoosa.sh --update` never overwrites project specialist files |

Do not duplicate discovery tables in platform adapters — route to `Docs/AgToosa_Specialists.md`.

## Generated Project Skills

`/agtoosa-init` (**Project Skill Discovery**, Phase F) and `/agtoosa-spec` (**Story Skill Opportunity Synthesis**) may propose additional skills under `.codex/skills/<skill-name>/SKILL.md`.

### Anatomy

```
.codex/skills/<skill-name>/
├── SKILL.md          # required — frontmatter + concise instructions
├── references/       # optional — detailed docs loaded on demand
├── scripts/          # optional — executable helpers
└── assets/           # optional — templates, diagrams, fixtures
```

### Naming and content rules

- **Skill name:** lowercase hyphen-case folder name (e.g. `api-contract-review`).
- **Body:** concise operating steps; prefer `references/` over long inline text.
- **Do not generate** README, quick-reference, or other auxiliary markdown unless the user explicitly requests supported UI metadata files only.
- **Approval:** never create or modify skill files without explicit user approval; record Generate / Update / Do not generate decisions in the spec or `Docs/Master-Plan.md` Update Log.
- **Dedupe:** reuse existing `agtoosa-*` workflow skills or update an existing project skill instead of creating a duplicate trigger.
- **Reserved workflow names:** `agtoosa-*` names and `/agtoosa-*` triggers are owned by installed AgToosa workflow adapters (`.claude/commands/agtoosa-*.md`, `.cursor/commands/agtoosa-*.md`, `.windsurf/workflows/agtoosa-*.md`, `.gemini/commands/agtoosa-*.toml`, `.github/prompts/agtoosa-*.prompt.md`, `.codex/prompts/agtoosa-*.md`, `.codex/skills/agtoosa-*`, and platform equivalents). Generated project skills must not use `agtoosa-*` names, `/agtoosa-*` triggers, or collide with installed AgToosa adapter files unless **Update existing** on an AgToosa adapter — otherwise choose **Do not generate**.
- **Secrets:** never embed credentials, private keys, tokens, or sensitive config values — reference paths and add a safety note when needed.

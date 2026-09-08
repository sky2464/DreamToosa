# AgToosa /agtoosa-init Workflow

> **Run once when setting up AgToosa. Re-run only for major architectural shifts.**

## Objective
One-time initialization: establish project context, scan the codebase, validate AI configs, and configure the AgToosa workflow.

> **Generated Project Mode:** `/agtoosa-init` sets up **the project** or **the product** in this repository — read `Docs/AgToosa_Agent.md` → **Operating Contexts**. AgToosa is the workflow framework, not the application identity. Update **this repo's** `Docs/Master-Plan.md` charter and epics for the host product.

## Sub-Commands

| Sub-command | Runs |
|-------------|------|
| `/agtoosa-init` | Full initialization workflow (run once) |
| `/agtoosa-init zoom-out` | Codebase zoom-out: broader context when agent is zoomed in on a specific file or function |

### /agtoosa-init zoom-out

Use when the AI agent is focused on a specific file or function and needs broader context to make a good decision.

1. **Call graph:** Show what calls this function/module and what it calls in turn.
2. **Module boundaries:** Identify which architectural layer owns this code (UI / API / domain / data).
3. **Usage sites:** Find all references to this symbol or module across the codebase.
4. **Impact analysis:** Answer: "What would break if this changed?"
5. **Context update:** Update `Docs/Master-Plan.md` with the codebase mental model if any new understanding emerged.

## Workflow

### Phase A — AI Config Validation

1.  **Detect AI Configs:**
    *   Scan the project root for AI config files: `.cursorrules`, `.windsurfrules`, `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `OPENCODE.md`, and any other rules/memory files.
    *   Scan `.github/instructions/` for `*.instructions.md` scoped instruction files.
    *   Check each config correctly references `Docs/AgToosa_Agent.md` and the `/agtoosa-*` commands.
    *   If a config exists but is NOT wired to AgToosa, ask the user whether to update it.
    *   If a config for the selected AI tool is missing, create it with proper AgToosa references.
    *   If `.github/instructions/` is missing, create it and scaffold baseline files: `agtoosa-core.instructions.md`, `agtoosa-testing.instructions.md`, `agtoosa-security.instructions.md`, and `agtoosa-changelog.instructions.md`.

2.  **Platform Notes:**
    *   All supported platforms auto-load their config (`.cursorrules`, `CLAUDE.md`, `AGENTS.md`, etc.).
    *   If the platform has a native `/init` command, explain how `/agtoosa-init` integrates with it.

### Phase B — Context Establishment

> **Follow the Smart Interview Protocol** (`Docs/AgToosa_Agent.md` → `## Smart Interview Protocol`).
> Start with the Goal Clarification Protocol (`Docs/AgToosa_Agent.md` → `## Goal Clarification Protocol`).
> Ask one question at a time. If goal/context clarity is still insufficient after 12 questions, stop and ask whether to continue the interview or proceed with documented assumptions.

3.  **Project Goal Contract:**

    Before filling context files, clarify the project-level goal. Read `Docs/Master-Plan.md` if it exists, then infer from the codebase, README, package manifests, and `Docs/Context/`.

    If the project goal is missing, vague, or contradictory, call the `/agtoosa-goal project` sub-workflow:
    - Ask only about missing Goal Contract fields.
    - Build each question from previous answers.
    - Write the final project Goal Contract into `Docs/Master-Plan.md` `## Project Charter`.
    - Do not store the goal source of truth in `Docs/Context/`.

    The Project Charter must include or preserve these fields:
    - Goal
    - User outcome
    - Success condition
    - Proof / evidence
    - Non-goals
    - Assumptions
    - Risks
    - Unresolved questions

**Phase B.5 — Existing work surfaces (optional tributary):**

After the Goal Contract, ask once:

> "Is work already tracked in GitHub Issues, Linear, or repo roadmap files (ROADMAP.md, plans/)?"

If **yes** (brownfield adoption):

1. Run `bash agtoosa.sh --tracker discover --path . --output /tmp/tracker-discovery.json` (local signals only).
2. Optionally merge provider data — **no network in the generator**:
   - GitHub: `gh issue list --json number,title,labels,state,body` → save JSON → re-run discover with `--input <file>`.
   - Linear: agent/MCP export → `agtoosa.linear-fetch-envelope/v1` JSON → discover `--input` or bootstrap input envelope (see `Docs/AgToosa_TrackerSync.md`).
3. Run `bash agtoosa.sh --tracker bootstrap --path . --input /tmp/tracker-discovery.json --output /tmp/bootstrap-proposal.md`.
4. Present the proposal; user accepts rows via `/agtoosa-task` or explicit `Docs/Master-Plan.md` edit.
5. **Do not block init** — continue to Phase C after the user accepts, skips, or defers bootstrap.

If **no**, continue without bootstrap.

4.  **Populate-Check Gate:**

    Before asking anything, check whether `Docs/Context/` files already exist and are populated:

    - **Fully populated** (all key fields have real non-placeholder values):
      Present a summary of each file's content and ask:
      > "Your context files are already filled in. Review below — confirm to proceed, or call out anything to update."

    - **Partially populated** (some fields are `""` or placeholder stubs):
      Present the filled fields, skip asking about them, and run the interview only for the gaps.

    - **Empty or missing** (files missing, or all fields are `""` / placeholder):
      Run the full discovery interview below.

    **Greenfield / empty-repo branch:** If no source files, no `README.md`, and no package manifest (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.) are detected → skip Phase C (codebase scan) entirely. Note: "We'll profile the codebase as you build." Run the full discovery interview, then jump directly to Phase D.

5.  **Discovery Interview (Smart Interview):**

    Conduct the interview one question at a time. Before each question, scan the codebase and any existing context for clues — pre-populate options from what you find. Do not ask questions whose answers are already clear from codebase evidence.

    **Product context** (`Docs/Context/product.md`):

    ```
    ❓ What type of app is this?
      → A) [type inferred from codebase structure, e.g., "Web SaaS (Next.js + API)"] ← recommended
      → B) Mobile App
      → C) CLI Tool / API Service
      Or describe it yourself.
    ```

    Wait for the answer, then ask (if still unclear):

    ```
    ❓ Who is the primary user and what is the single most important problem this solves?
      Or type your own answer.
    ```

    **Tech stack** (`Docs/Context/tech-stack.md`):

    ```
    ❓ Confirm the tech stack — does this look right?
      → [Language, framework, DB, deployment target — inferred from package manifests and config files]
      → Correct it below if anything is wrong.
    ```

    Only ask about deployment target separately if it cannot be inferred.

    **Workflow** (`Docs/Context/workflow.md`):

    ```
    ❓ Should we enforce strict TDD (Red-Green-Refactor) during /agtoosa-build?
      → A) Yes — enforce TDD ← recommended for new features
      → B) No — write tests but don't enforce ordering
    ```

    Only ask about commit strategy or branch naming if the project has no existing conventions detectable in git config or CI files.

    When writing `Docs/Context/workflow.md`, include the **Cross-model review** defaults unless the user overrides them:

    ```
    cross_model: recommended
    reviewer_model: parent
    ```

    See `Docs/AgToosa_CrossModelReview.md` → Project configuration. Users who want no subagents set `cross_model: off`; users who want explicit model choice each time set `reviewer_model: ask`.

    **Product guidelines** (`Docs/Context/product-guidelines.md`):

    Infer from any existing UI, README tone, or brand assets. Only ask if nothing is detectable:

    ```
    ❓ Any specific brand, UX, or prose style guidelines to record?
      → A) Skip for now — fill in later
      → B) Type them here
    ```

    After each answer, write or update the relevant context file immediately. Ask at most one follow-up per answer.

6.  **Phase B → Phase C Gate:**

    > **STOP — Do NOT proceed to Phase C until all Context files are confirmed by the user.**

    Present the approval gate (see `## Smart Interview Protocol` → Approval Gate Format):

    ```
    ✅ Ready to proceed
    Context established: product type, users, core problem, tech stack, and workflow preferences captured.
    → Approve to continue to codebase scan  |  Comment or make changes below
    ```

    Wait for explicit approval before proceeding.

### Phase C — Codebase Onboarding

7.  **Codebase Scan:** Scan the project for structure, stack, dependencies, and architecture. Use findings to pre-populate Phase D Epics — do not ask about things the codebase already reveals.

8.  **AI Doctor Consultation (Smart Interview):** Ask clarifying questions to understand the app's core logic and product areas. Follow the Smart Interview Protocol:
    - Ask **one question at a time**. Wait for each answer before asking the next.
    - Infer Epic candidates from the codebase (e.g., Auth, Billing, API, Dashboard). Present them as options — do not ask the user to name Epics from scratch.
    - At most one follow-up per answer. Stop when product areas are clear.

    ```
    ❓ These look like the main product areas from the codebase — does this list look right?
      → A) [Inferred Epic 1]
      → B) [Inferred Epic 2]
      → C) [Inferred Epic 3]
      Add, remove, or rename any below.
    ```

9.  **Scaffolding:** Create `Docs/`, `Docs/archived/`, and `Docs/Context/` if they don't exist.

10. **Dynamic Generation:** Based on the consultation, update or create **project-owned files only** — never edit AgToosa-owned workflow docs (`Docs/AgToosa_*.md` workflow files, format guides, `Docs/agtoosa-verify.sh`), or `/agtoosa-update` can no longer refresh them cleanly. Project tailoring lives in `Docs/Context/*` and the files below:
    *   `Docs/Master-Architecture.md` — create or update this as a senior application architect after the smart interview and codebase scan. Include C4-style diagrams, module boundaries, data flow, deployment, security, observability, and ADR links. (Preserved by `--update`.)
    *   Verify `Docs/AgToosa_Claude.md` / `Docs/AgToosa_Gemini.md` exist when those platforms are selected — they are AgToosa-owned: report wiring problems instead of editing them.

11. **Project Management Setup:**

    > `Docs/Master-Plan.md` is the **repo-local PM authority**. External trackers (GitHub Issues, Linear, etc.) may continue as **public mirrors** after optional bootstrap (`/agtoosa-tracker discover` · `bootstrap`). Import is always proposal-first — never silent. Do not create new external issues unless the user explicitly asks.

    *   For each Epic confirmed in the consultation, add an entry to `Docs/Master-Plan.md` under `## Epics`:
        - **Name:** `Epic: [product area name]` (e.g., `Epic: Authentication`)
        - **Status:** `Backlog`
        - **Charter:** one-paragraph goal, scope, and success criteria for this product area
    *   Mirror the full current state in `Docs/Master-Plan.md` using the structured template (Project Charter with Goal Contract fields, Epics table, empty Backlog, Update Log first entry).
    *   Initialize `Docs/AgToosa_Changelog.md`.

### Phase D — TDD Configuration

12. **Test Framework:** Auto-detect the test framework (Vitest, Jest, pytest, etc.) from package manifests and config files. Record it in `tech-stack.md`. Only ask if auto-detection is ambiguous.

> **Note:** TDD preference was captured in Phase B (Step 4). If `tdd: true` is already set in `workflow.md`, skip this step.

### Phase E — Project Specialist Discovery

13. **Project Specialist Discovery (cross-platform):**

    After context files and Epics are established, identify **reusable project-specific specialist subagents** — not a default generic roster. Follow `Docs/AgToosa_Specialists.md` for the full contract.

    *   Read `Docs/Context/product.md`, `tech-stack.md`, `workflow.md`, `Docs/Context/CONTEXT.md`, and `Docs/Master-Architecture.md` when present.
    *   **Detect installed platforms** from `Docs/.agtoosa-version`, `Docs/agtoosa-lock.json`, and sentinels (`.codex/`, `.claude/`, `.cursor/`, `.windsurf/`, `.gemini/`, `.github/agents/`, entry points).
    *   Prefer reusing existing AgToosa workflow adapters (`.codex/skills/agtoosa-*`, platform commands) and any approved entries in `Docs/Context/specialists.md` before proposing new specialists.
    *   **Reserved names:** reject specialist ids `agtoosa-*` and triggers `/agtoosa-*`; reject one-off story tasks, duplicates, and candidates without validation.
    *   **Secret safety:** never copy credentials, private keys, tokens, or sensitive config values into specialist bodies or `specialists.md`. Reference paths only; use **safety_notes** and **tools/MCP needs** fields per `Docs/AgToosa_Specialists.md`.
    *   Present candidates in a table with: **id**, **trigger**, **purpose**, **phase_hooks**, **inputs**, **tools/MCP needs**, **outputs**, **validation**, **safety_notes**, **platform_targets**, **Decision** (`Approve` / `Decline` / `Defer`).
    *   Require **explicit user approval** before creating `Docs/Context/specialists.md` or any native specialist file (`.codex/skills/<id>/`, `.claude/skills/<id>.md`, `.github/agents/<id>.agent.md`, Cursor/Windsurf/Gemini fallbacks per matrix). Do not materialize silently.
    *   On approval, materialize only the platforms installed in this project.
    *   Record accepted and declined decisions in `Docs/Master-Plan.md` **Update Log** (include specialist id and decision).

### Phase F — Project Skill Discovery

14. **Project Skill Discovery (Codex / OpenCode):**

    After specialist discovery (or when the user skips it), identify recurring project workflows that would benefit from a durable Codex skill — domain-language review, API contract checks, migration validation, release evidence collection, or similar. See `Docs/AgToosa_Specialists.md` glossary — **skills** are command helpers; **specialists** are delegated subagent lanes.

    *   Read `Docs/Context/product.md`, `tech-stack.md`, `workflow.md`, and `Docs/Context/CONTEXT.md`.
    *   Prefer reusing existing AgToosa workflow skills (`.codex/skills/agtoosa-*`) and platform adapters before proposing a new project skill.
    *   **Reserved workflow names:** `agtoosa-*` skill names and `/agtoosa-*` triggers belong to installed AgToosa workflow adapters (including `.claude/commands/agtoosa-*.md`, `.cursor/commands/agtoosa-*.md`, `.windsurf/workflows/agtoosa-*.md`, `.gemini/commands/agtoosa-*.toml`, `.github/prompts/agtoosa-*.prompt.md`, `.codex/prompts/agtoosa-*.md`, and `.codex/skills/agtoosa-*`). Reject generated project skill candidates named `agtoosa-*`, triggered by `/agtoosa-*`, or that would shadow an installed AgToosa adapter file unless the decision is **Update existing** on that adapter (never a new duplicate).
    *   Reject one-off tasks, duplicates, and candidates without a clear validation command or checklist.
    *   **Secret safety:** never copy credentials, private keys, tokens, or sensitive config values into skill bodies. If a candidate needs secret awareness, add a safety note and reference file paths only.
    *   Present candidates in a table with: **Skill name**, **Trigger description**, **Purpose**, **Inputs**, **Optional resources**, **Validation**, **Decision** (`Generate` / `Update existing` / `Do not generate`).
    *   Require **explicit user approval** before creating or modifying any `.codex/skills/<skill-name>/SKILL.md` file. Do not generate skills silently.
    *   On approval, create only valid Codex skill anatomy: `SKILL.md` with `name` and `description` frontmatter, concise body, and optional `references/`, `scripts/`, or `assets/` folders when justified. Do not add README, quick-reference, or other auxiliary docs unless the user explicitly requests supported UI metadata (see `Docs/AgToosa_Skills.md`).
    *   Record accepted and declined decisions in `Docs/Master-Plan.md` **Update Log** (include skill name and decision).

### Phase G — Optional Hook Automation Pack

15. **Optional Hook Automation Pack (preview + approval):**

    After skill discovery (or when the user skips it), offer the optional Hook Automation Pack. See `Docs/AgToosa_Hooks.md` for the event catalog, platform matrix, secret-safe diagnostics, DEV-059 linkage, and removal path.

    *   Present a **HookInstallPreview**: `affected_files`, `existing_entries_preserved`, `entries_added`, `entries_deduplicated`, and `removal_steps` (merge intent for Claude settings/scripts when Claude is installed; checklist-only mappings otherwise).
    *   Require **explicit user approval** before any write. **No silent hook install.**
    *   On **decline**: make **no write**; health and verifier stay unchanged (pack absence is not a finding).
    *   On **approval**: install/merge only listed entries; preserve unrelated user settings; deduplicate AgToosa hook entries by command string.
    *   Record Approve / Decline in `Docs/Master-Plan.md` **Update Log**.

## Output

Present the approval gate:

```
✅ Initialization complete
[2–3 sentence summary: what project goal was captured, what context was set, which Epics were created.]
AI configs confirmed. Use 4 commands: /agtoosa-spec → /agtoosa-build → /agtoosa-review → /agtoosa-ship.
Run /agtoosa-status readiness to verify initial product gates (see Docs/AgToosa_Readiness.md).
→ Approve and run /agtoosa-spec when ready  |  Comment or adjust below
```

Then print the dual-line phase close per Docs/AgToosa_Agent.md → Lifecycle Next-Step Contract

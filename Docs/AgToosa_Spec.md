# AgToosa /agtoosa-spec Workflow

## Sub-Commands

| Sub-command | Runs |
|-------------|------|
| `/agtoosa-spec` | Full flow: Parts 1 + 2 + 3 + 4 |
| `/agtoosa-spec research` | Part 1 only — context, web research, and Q&A; outputs findings, no spec file yet |
| `/agtoosa-spec plan` | Part 2 only — architecture blueprint + threat model against an already-written spec |
| `/agtoosa-spec quick` | Abbreviated — max **2** targeted questions + spec + skip full threat model (use for small bugs/chores) |
| `/agtoosa-spec tasks` | Part 4 only — derive atomic tasks from an already-approved spec, generate test plan skeleton, update Master-Plan.md |
| `/agtoosa-spec amend` | Change-control an already-approved spec: record a revision entry, diff vs the approved version, re-approve when Must ACs change |
| `/agtoosa-spec to-issues` | Break the active spec or PRD into vertical-slice GitHub issues |

## /agtoosa-spec amend — Spec Change Control

Approved specs are contracts; silent edits destroy their audit value. When requirements change after `## ✅ Spec Approved`:

1. Read the active spec (`Docs/archived/spec-[story-id].md`) and present a concise diff of the proposed change (sections touched, ACs added/modified/removed).
2. Append a row to the spec's `## Spec Revision Log` (create the section before the approval marker if missing — format in `Docs/SPEC-FORMAT.md`):
   `| R[N] | [YYYY-MM-DD] | [what changed] | [why] | [approved-by or pending] |`
3. Mark changed acceptance criteria inline: new rows get `(added R[N])`, edited rows get `(modified R[N])`, dropped rows are struck through with `(removed R[N])` — never silently deleted.
4. **Re-approval gate:** if any **Must**-priority AC was added, modified, or removed, the amendment requires explicit user approval before `/agtoosa-build` may continue; append `## ✅ Amendment R[N] Approved` under the revision log when granted.
5. Sync downstream artifacts: update the task tree (spec §3.1 + Master-Plan `## Active Tasks`) and the story test plan for any AC changes, and add an Update Log entry to `Docs/Master-Plan.md`.

## Optional Sub-Commands

### /agtoosa-spec to-issues

Break the active spec (or a provided PRD or plan) into independently-grabbable GitHub issues using vertical slices.

**Vertical slice rule:** Each issue must deliver one complete user-facing behaviour change — never a horizontal slice ("write the tests" or "add the migration" are not valid issues on their own).

1. Read the active spec (`Docs/archived/spec-[story-id].md`, or the provided description if no spec file exists).
2. Identify all user-facing behaviour changes. For each, create one GitHub issue with:
   - **Title:** `[Area] Short description of user-facing change`
   - **Acceptance criteria:** up to 5 AC items in checkbox format
   - **Story points:** 1 / 2 / 3 / 5 (Fibonacci)
   - **Labels:** feature / bug / chore / spike as appropriate
   - **Dependencies:** list any issues that must complete first
3. If no GitHub remote is configured, write issues to `Docs/issues/` as individual markdown files.
4. Update `Docs/Master-Plan.md` with all issue IDs under `## Active Tasks`.

## Objective
Transform a raw idea, feature, chore, or bug into a researched Specification with an architectural blueprint.

> **Generated Project Mode:** Specs describe work on **the project** or **the product** (`Docs/Master-Plan.md` → `## Project Charter`), not the AgToosa framework. Story entries and tasks belong in **this repository's** `Docs/Master-Plan.md`. See `Docs/AgToosa_Agent.md` → **Operating Contexts**.

## Phase Stop Contract

> See `Docs/AgToosa_Agent.md` → **Phase Stop Contract** for the full rules.

- `/agtoosa-spec` may run through Parts 1–4 (spec, architecture, tasks, test plan) but **must stop** at the approval gate below — unless **served by `/agtoosa-next`** (see `Docs/AgToosa_Next.md` → Sequential Approval Contract).
- Do **not** run `/agtoosa-build` automatically after the approval gate — wait for the user to invoke `/agtoosa-build` explicitly, or for a **separate** `/agtoosa-next` invocation after approval.
- Appending `## ✅ Spec Approved` marks readiness only; it does not start build.

## Plan-Mode Spec Interview Contract

> Applies to full `/agtoosa-spec` (not `research`, `plan`, or `tasks` alone). `/agtoosa-spec quick` uses the same principles with a **2-question** cap.

Before writing or finalizing the spec file, run a **Plan-Mode Spec Interview**:

1. **Research first** — Read `Docs/Context/`, `Docs/Master-Plan.md`, active `Docs/archived/spec-*.md`, `Docs/Master-Architecture.md`, and scan the codebase; use external research when platform or dependency behavior matters.
2. **Gap list** — Compare findings against the **Decision-complete checklist** below. Ask only about genuine gaps.
3. **Infer, don't re-ask** — If an answer is inferable with high confidence (≥80%), state it as a **finding** and do not ask that question.
4. **One question at a time** — Wait for each answer before the next question.
5. **Contextual options** — Derive 2–3 concrete options from repo/research when possible; mark one **recommended** default; always allow free-text override (see **Question Format** in `Docs/AgToosa_Agent.md` → Smart Interview Protocol).
6. **Adaptive sequencing** — Let each answer shape the next question; use the six forcing questions (Part 1 step 4) as a **candidate pool**, not a mandatory script.
7. **Adaptive cap** — Full flow: at most **8 core interview questions**. `/agtoosa-spec quick`: at most **2** questions.
8. **Budget exhaustion** — Default soft cap: **8** core questions, then offer **+4** continuation. If the user answers with **new free-text directions** (not a menu pick), the **+4 extension may repeat** until Decision-complete or explicit assumption acceptance. After 8 questions without resolution, ask:

    ```
    ❓ Interview budget reached (8 questions). How should we proceed?
      → A) Continue the interview (up to 4 more questions) ← only if critical gaps remain
      → B) Proceed with documented assumptions in the spec ← recommended when momentum matters
      Or type your own answer.
    ```

    **Not a hard stop:** keep interviewing when free-text answers open new gaps until the Decision-complete checklist passes or assumptions are explicitly accepted. Never auto-write a detailed spec while a child story carries `needs-interview` / `N-CI` or Must clarity gaps remain.

### User prompt ≠ interview complete

A detailed user message, slash-command argument, or backlog story description is **input material**, not proof that the Decision-complete checklist is satisfied. Research may cover many areas, but **user confirmation** is still required on scope trade-offs, non-goals, and Must-priority behavior unless the user explicitly chose `/agtoosa-spec quick` or says to proceed with documented assumptions after a research summary.

### Minimum validation floor

Even when research infers ≥80% of checklist items:

- **Full flow:** ask at least **2 validation questions** (adaptive cap still **8**) before writing `Docs/archived/spec-*.md`, enrolling `Docs/Master-Plan.md` story rows, or generating test plans. Prioritize: narrowest scope, non-goals/trade-offs, and failure modes or security when trust boundaries exist.
- **`/agtoosa-spec quick`:** ask at least **1** validation question before writing the spec file (cap remains **2**).
- **Exception:** after presenting a research summary, the user explicitly chooses *proceed with documented assumptions* — skip remaining questions and record every assumption in `### Plan-Mode Spec Interview (findings)`.

### Interview turn-stop

After research (and optional findings summary), **end the agent turn** on the first interview question. In the **same turn**, do **not**:

- write or update `Docs/archived/spec-*.md`
- enroll or mutate `Docs/Master-Plan.md` story rows (read-only research is allowed)
- generate `Docs/AgToosa_TestPlan-*.md`
- implement build artifacts (generator code, platform adapters, bats) or run `/agtoosa-build`

Wait for the user's answer before the next question or any spec artifacts. Use `/agtoosa-spec research` when the user wants findings-only output without advancing to Q&A in the same session.

**Host mode:** Before the first interview question, ensure the host is in **native IDE plan mode** (or instruct the user to switch). Remain in plan mode for research, interview, and architecture/STRIDE drafting as a **plan artifact**. Do not write spec files until the **IDE Host Mode Bridge** auto-switch trigger in `Docs/AgToosa_Agent.md` is satisfied.

## IDE Host Mode Bridge

> Canonical auto-switch rules: `Docs/AgToosa_Agent.md` → **IDE Host Mode Bridge**. Per-platform enter/switch: `Docs/AgToosa_AgentCapability.md` → **IDE Host Mode Matrix**.

| Sub-command | Plan-mode window | Agent/Auto window |
|-------------|------------------|-------------------|
| Full (no arg) | Research, Plan-Mode Spec Interview, Goal Contract, architecture/STRIDE plan | `Docs/archived/spec-*.md`, test plan skeleton, Master-Plan enrollment, approval gate |
| `research` | Entire sub-command | — |
| `quick` | Interview (cap 2) + plan draft | Spec file + tasks |
| `plan`, `tasks`, `amend`, `to-issues` | Read-only / planning slices per sub-command | Writes per sub-command scope |

Plan mode is the host's planning surface — produce rich structured plans (Goal Contract tables, STRIDE drafts, EARS AC tables as plan sections) inside plan mode, then switch to Agent/Auto to normalize into AgToosa spec artifacts.

**Forbidden in plan mode:** writing or updating `Docs/archived/spec-*.md`, enrolling Master-Plan story rows, generating test plans, or implementing build artifacts.

**Handoff:** when decision-complete (or assumptions accepted) and minimum validation floor met, print `HOST-MODE: plan complete → switching to agent for AgToosa artifacts`, switch to Agent/Auto per the IDE Host Mode Matrix, then write spec artifacts.

### Plan-Mode Spec Interview (findings) — required spec section

Before the approval gate, every spec file must include `### Plan-Mode Spec Interview (findings)` (see `Docs/SPEC-FORMAT.md`) with:

| Subsection | Content |
|------------|---------|
| **Inferred (≥80%)** | Checklist areas filled from research without a user question |
| **Asked & confirmed** | `Q[N]` · one-line question · user answer (or menu pick) |
| **Documented assumptions** | Items accepted without user override; cite explicit user opt-in when used |

Do not set Clarity `ready` or Goal Contract `Unresolved questions: None` until this section is complete and the minimum validation floor is met.

### Multi-spec intake

When the user asks to learn objectives and split work into **multiple specs**:

1. **Detect** multi-objective / “break into specs” intent.
2. **Propose** a story map (IDs, titles, non-goals, suggested clarity tags, default `intake:small` vs `intake:large`).
3. **Confirm** the map with the user.
4. **Small agenda (`intake:small`):** run Plan-Mode Spec Interview now (parallel child interviews when host supports subagents and row carries `sa-ready` / `SA-R`).
5. **Large agenda (`intake:large`):** capture portfolio-level clarity only; enroll children with `needs-interview` / `N-CI`; do **not** write detailed child specs until each is interviewed.
6. **Write gate:** never finalize a detailed spec file for a story tagged `needs-interview` / `N-CI` without completing Plan-Mode Spec Interview (or explicit `/agtoosa-spec quick` only when the user chooses quick).

**Clarity tags** (combinable on Master-Plan `Clarity` column and spec header): canonical `ready` · `sa-ready` · `needs-interview` (aliases `Ready` · `SA-R` · `N-CI`). See `Docs/adr/ADR-012-lifecycle-next-step-sync.md`.

### Decision-complete checklist

Before spec generation, confirm coverage (as findings or interview answers) for:

| Area | Must capture |
|------|----------------|
| Goal Contract | Goal, user outcome, success condition, proof/evidence |
| Non-goals | What is explicitly out of scope |
| Acceptance criteria | EARS table with Must-priority ACs |
| Scope boundary | Files/directories in and out of scope |
| Affected surfaces | Generator, template, docs, tests, platforms, etc. |
| Risk / failure modes | Top production failure modes for Must ACs |
| Security / trust boundaries | Auth, data, external APIs, user input, secrets |
| Test evidence | How ACs will be verified (bats, manual, etc.) |
| Rollout / compatibility | Upgrade path, breaking changes, parity surfaces |
| Unresolved assumptions | Anything still assumed; user acceptance when required |

## Workflow

### Part 1 — Research & Specification

**Orchestration Brain step 0:** Before fan-out (specialist lanes, parallel research), read `Docs/AgToosa_Orchestration.md` and run Capability Inventory → lane plan → parallel or sequential dispatch → orchestrator merge. Consult `Docs/AgToosa_AgentCapability.md` for parallel vs sequential; do not duplicate routing tables here.

1.  **Context Gathering & Domain Language Alignment:**
    *   Read `Docs/Context/product.md`, `tech-stack.md`, and `workflow.md` to align with project goals.
    *   Read `Docs/Master-Architecture.md` as the current solution architecture before proposing architecture changes. If it is missing or stale, record that as a context gap and include an update task when architecture is in scope.
    *   Scan the existing codebase to fully understand the impact surface of the proposed work.
    *   **Domain Language Alignment:** Read `Docs/Context/CONTEXT.md` (create it if missing using `Docs/CONTEXT-FORMAT.md` as a guide). For each key concept in the proposed feature:
        - "Is this the right term? What does the domain call this?"
        - "Is this a new concept or an existing one we're renaming?"
        - "Where does this term appear in the codebase today?"
    *   Update `Docs/Context/CONTEXT.md` with any new or corrected terms.
    *   Identify 2–3 architectural decisions implied by the feature; document each as a new ADR in `Docs/adr/` using `Docs/ADR-FORMAT.md`.
1a. **Spec Specialist Orchestration:**

    > Canonical contract: `Docs/AgToosa_Specialists.md`. Run after context scan, before external research when a roster exists or specialists were approved during init.

    *   If `Docs/Context/specialists.md` is missing, skip this step (record "no approved specialists").
    *   Load the roster; select specialists where `phase_hooks` includes **`spec`** and **trigger** matches the active story (title, paths, epic, or user-stated scope).
    *   For each selected specialist, run a lane that reads declared **inputs** and returns the **structured evidence block** from `Docs/AgToosa_Specialists.md` (`Findings:`, `Files read:`, `Commands:`, `Warnings/errors:`, `Recommendations:`, `Spec sections affected:`).
    *   **Parallel:** when the host supports native subagent delegation (e.g. Claude Code Agent tool), run matching lanes in parallel.
    *   **Sequential fallback:** otherwise run the same lanes one at a time and print an explicit note: `Specialist lanes ran sequentially (platform does not support parallel subagents).`
    *   **Merge** evidence into draft Goal Contract, ACs, architecture notes, STRIDE inputs, task tree hints, and test plan skeleton **before** finalizing Part 1 executable spec and Part 2 threat model.
    *   Do not run specialists that fail trigger match or lack approval in the roster.
2.  **External Research (Web Research Agent):**
    *   Query online sources for the best solutions, libraries, APIs, and design patterns relevant to the task.
    *   **CRITICAL:** Verify all dependency versions against live sources (never assume from memory).
3.  **Story Goal Contract:**

    Before asking forcing questions, verify that the story goal is clear enough to build, review, and ship against.

    *   Read the project Goal Contract in `Docs/Master-Plan.md` `## Project Charter`.
    *   Infer the story goal from the user's request, codebase scan, active specs, backlog, and `Docs/Context/`.
    *   If the goal, user outcome, measurable success condition, proof/evidence, non-goals, assumptions, risks, or unresolved questions are unclear, call the `/agtoosa-goal story` sub-workflow.
    *   Write the final Story Goal Contract into the spec under `## 1. Requirements` before User Stories.
    *   Story goals must be stored in the active spec, not in `Docs/Context/`.

4.  **Q&A — Plan-Mode Spec Interview (Smart Interview):**

    > **Follow the Plan-Mode Spec Interview Contract** (above) and the **Smart Interview Protocol** (`Docs/AgToosa_Agent.md` → `## Smart Interview Protocol`).
    > Full flow: adaptive cap **8** core questions; `/agtoosa-spec quick`: cap **2**; minimum validation floor **2** / **1** respectively; **interview turn-stop** after Q1.
    > Before each question, check whether the answer is already clear from research or Context files. If it is, state your finding and move on — do not ask.
    > A detailed user prompt does **not** satisfy the interview — still meet the minimum validation floor unless the user opts into documented assumptions.

    The six forcing questions below are the **candidate pool**. Ask only where the Decision-complete checklist still has a genuine gap. Present options derived from codebase findings and research. One question at a time; at most one follow-up per answer.

    1. **Status quo** — What is the exact current behavior users depend on? What breaks if we change it?
    2. **Narrowest scope** — What is the smallest version of this feature that still delivers real value?
    3. **Urgency signal** — Who specifically is blocked without this? What workaround are they using today?
    4. **10-star version** — If resources were unlimited, what would the ideal implementation look like?
    5. **Failure modes** — What are the three most likely ways this could break in production?
    6. **Security surface** — Does this touch auth, data storage, external APIs, or user-controlled input?

    Questions 1–4 sharpen scope. Questions 5–6 feed directly into STRIDE threat modelling in Part 2. Always ask question 6 if the feature touches any trust boundary — it is rarely fully inferable.

    For `/agtoosa-spec quick`, ask at most questions 1 and 2 (abbreviated) — honoring the 2-question cap. Derive question 6 (failure modes/security) as an inferred finding from the codebase scan instead of asking it.
5.  **Executable Spec Generation:**
    *   Synthesize all findings into a clean, comprehensive **Executable Specification**.
    *   Include `### Plan-Mode Spec Interview (findings)` per the contract above before Goal Contract or User Stories (see `Docs/SPEC-FORMAT.md`).
    *   Specs must act as direct programmatic inputs for the `/agtoosa-build` phase (e.g., BDD syntax, strict preconditions/postconditions, or explicit acceptance criteria).

### Part 2 — Architectural Planning & Threat Modeling

6.  **Constraints Enforcement & Threat Modeling:**
    *   **Proactive Threat Modeling:** Generate Data Flow Diagrams (DFDs) and apply the STRIDE methodology (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) before any code is written.
    *   Embed "Security by Design" into the plan.
    *   Validate that the proposed plan adheres to Object-Oriented Design (OOP) principles (if applicable).
    *   Enforce the rule: No code file shall exceed 500 lines of code. Plan for modularity.
7.  **Architecture Blueprint:**
    *   Outline the architecture, file structure changes, and logic flow.
    *   Identify dependencies and their latest stable versions.
    *   Map out which tasks can be parallelized during `/agtoosa-build`.

### Part 3 — Output

8.  **Acceptance Criteria:**
    *   Before writing the spec file, generate a `## 1.2 Acceptance Criteria (EARS)` table using EARS notation:

    ```
    ## 1.2 Acceptance Criteria (EARS)

    | ID | EARS | Priority |
    |----|------|----------|
    | AC-001 | WHEN [condition] THE SYSTEM SHALL [behavior] | Must |
    | AC-002 | WHILE [state] WHEN [event] THE SYSTEM SHALL [behavior] | Should |
    | AC-003 | IF [optional feature] THEN WHEN [event] THE SYSTEM SHALL [behavior] | Could |
    ```

    *   IDs use `AC-NNN` format. Priority: **Must** / **Should** / **Could** (MoSCoW).
    *   Every Must-priority AC must have at least one explicit failure mode from question 5.
    *   This table is required by `/agtoosa-qa plan` and `/agtoosa-ship check`.

9.  **File Generation:**
    *   Generate a single file named `Docs/archived/spec-[story-id].md` (e.g., `Docs/archived/spec-DEV-15.md`).
    *   The file must follow the section order defined in `Docs/SPEC-FORMAT.md`:
        - `## 1. Requirements` (Goal Contract, User Stories, EARS ACs, Out of Scope)
        - `## 2. Design` (Architecture Blueprint, Data Flow, STRIDE Threat Model, Build Scope)
        - `## 3. Tasks` (Task Tree, Wave Plan, Test Plan — populated in Part 4)
        - `## ✅ Spec Approved` (appended on approval)
    *   Refer to `Docs/SPEC-FORMAT.md` for the full format reference.
    *   The `Docs/archived/` directory is created automatically by `/agtoosa-init`. If it is missing, create it with `mkdir -p Docs/archived`.

9a. **Spec Quality Analyzer Gate:**

    Before appending `## ✅ Spec Approved`, run the Spec Quality Analyzer checklist against the draft spec and test plan. This is an agent-instructed gate unless a later story wires generator-enforced or CI-enforced checks.

    The analyzer must confirm:

    - Every Must AC is unambiguous, testable, and written as an observable system behavior.
    - No contradiction exists between the Goal Contract, Non-goals, Build Scope, Acceptance Criteria, task tree, and test plan.
    - Every Must AC maps to at least one test-plan row.
    - Every enforcement or launch claim has a Claim Boundary classified as generator-enforced, CI-enforced, agent-instructed, manual, or roadmap.
    - External agents, trackers, registries, dashboards, or hosted services preserve `Docs/Master-Plan.md` as the repo-local source of truth unless implementation evidence proves otherwise.
    - No TBD, TODO, or placeholder requirement remains.

    If any check fails, stop and revise the spec before enrollment or approval. Record the analyzer findings in the spec or test plan evidence section.

9b. **Brownfield Spec Drift Baseline:**

    If the story starts from an existing codebase, production behavior, migrated backlog, or partially implemented workflow, add a current-state baseline before approval. This is an agent-instructed workflow unless a later story wires generator-enforced or CI-enforced checks.

    The baseline must record:

    - The user outcome and proof required before the brownfield capability is treated as shipped.
    - A repo evidence inventory: specific files, commands, docs, tests, workflows, logs, or issue links used to describe current reality.
    - Current-state baseline behavior: what the repository already does today, including known gaps and manual steps.
    - Intended change deltas: the smallest observable differences the story will introduce.
    - drift evidence: conflicts between current code/Docs/tests and the proposed spec, plus the planned resolution for each conflict.
    - Claim Boundary classification for every enforcement statement: generator-enforced, CI-enforced, agent-instructed, manual, or roadmap.
    - Source-of-truth boundary: `Docs/Master-Plan.md remains the repo-local source of truth`; external agents, trackers, registries, and dashboards can be evidence sources or integrations only when implementation evidence proves that role.

    Do not claim static analysis coverage, architecture-review completeness, hosted dashboard sync, or external-tracker authority from this baseline alone. If the baseline exposes unresolved drift, either revise the spec, split the story, or mark the unresolved item as manual, blocked, or roadmap before approval.
10. **Master-Plan.md Story Entry:**
    *   Add a Story entry to `Docs/Master-Plan.md`:
        - Title: `Feature: [spec short name]` (use `Bug:` / `Chore:` / `Fix:` as appropriate)
        - Type: Feature (or Bug / Chore / Fix as appropriate)
        - Status: `Todo`
        - Priority: derived from the urgency signal (Q3 answer)
        - Parent Epic: link to the relevant Epic from `/agtoosa-init`
        - Summary: paste the spec's Goal Contract + ACs table + Definition of Done checklist
    *   Record the Story ID in the spec file header.
    *   Update `Docs/Master-Plan.md`: add the Story row to `## Backlog` (or `## Active Cycle` if enrolling now).

11. **Estimation & Cycle Enrollment:**
    *   Ask the user: "How big is this Story? T-shirt size: **XS** (< 4 h) / **S** (1 d) / **M** (2–3 d) / **L** (4–5 d) / **XL** (6+ d)"
    *   If the user picks **L** or **XL**, prompt: "This is large. Should we split it into smaller Stories now, or proceed as one?"
    *   Record the estimate in `Docs/Master-Plan.md` on the Story row.
    *   Ask: "Enroll this Story in the current active cycle/sprint? (Yes / No)"
    *   If Yes: add the Story to `Docs/Master-Plan.md` under `## Active Cycle` and record enrollment in the **Update Log**.

### Part 4 — Task Planning

> **Skip this part** if running `/agtoosa-spec research` or `/agtoosa-spec plan`. Run this part standalone with `/agtoosa-spec tasks` against an already-approved spec.

12. **Scope Boundary Declaration:**

    Derive the scope boundary from the spec. Present it as a pre-filled summary — do not ask the user to define scope from scratch:

    ```
    ✅ Ready to proceed — Scope Boundary
    Files in scope      : [list specific files from the spec]
    Directories in scope: [list directories]
    Out of scope        : [list anything that must NOT be touched]
    ```

    Save the scope declaration in the spec's `### 2.4 Build Scope` section (under `## 2. Design`, per `Docs/SPEC-FORMAT.md`).

13. **Atomic Task Breakdown:**
    *   Read the spec and translate it into atomic, clear, step-by-step actionable tasks.
    *   Identify tasks that can run in parallel during `/agtoosa-build`.
    *   If a critical flaw is found during task breakdown, stop and ask the user to revise the spec before continuing.
    *   Emit a **hierarchical checkbox tree** in `## Active Tasks` in `Docs/Master-Plan.md` (follow the format in `Docs/SPEC-FORMAT.md` § 3.1):
        - Top-level items: `- [ ] **N.** [Group]: [description]`
        - Sub-tasks: `  - [ ] N.M [description] — _Requirements: AC-NNN_`
    *   After generating the task tree, identify groups of sub-tasks that can run in parallel (no shared state, no data dependency). Add a `### Wave Plan` subsection in the spec's `## 3. Tasks` section using:

        ```
        **Wave 1 (parallel):** [list sub-task IDs]
        **Wave 2 (sequential after Wave 1):** [list sub-task IDs]
        ```

    *   **Work Package DAG derivation (agent-instructed):** After the Wave Plan exists, emit `### 3.4 Work Package DAG` in the active spec (schema in `Docs/SPEC-FORMAT.md`). Rules:
        - Emit **one Work Package row for every executable sub-task** (`package_id` = `PKG-<task-id>`, for example `PKG-1.1`).
        - Set `wave` from the Wave Plan; set `depends_on` to packages in earlier waves whose outputs this task needs (or `—`).
        - Fill `owned_files`, `inputs`, `outputs`, `merge_order`, and `verification` for every row.
        - Packages proposed for **parallel** execution must have non-empty `owned_files` and `verification`.
        - Same-wave `owned_files` sets must be **disjoint**. On overlap (duplicate paths or intersecting directory wildcards), replace the parallel relationship with an explicit **sequential fallback** in the Wave Plan.
        - Every `depends_on` reference must resolve to an existing package with an **earlier wave**; reject unknown, self, circular, same-wave, or later-wave dependencies.
        - XS / single-task stories may stay sequential without full DAG ceremony.
    *   Mirror the task tree into `Docs/Master-Plan.md` under `## Active Tasks` (replacing the flat table format).

14. **Test Plan Skeleton:**
    *   Generate **`Docs/AgToosa_TestPlan-[story-id].md`** containing:
        - Spec reference (link to `Docs/archived/spec-[story-id].md`)
        - AC coverage table — each `AC-NNN` from the spec mapped to test IDs (`T-001`, `T-002`, ...)
        - Test category per ID: Unit · Integration · E2E · Security · Performance
        - Coverage target from `Docs/Context/workflow.md` (`coverage_threshold`), default 80%
        - At least one negative/edge scenario per Must-priority AC
        - Smoke set — at least one test per Must-priority AC tagged `@smoke`

15. **Story Skill Opportunity Synthesis (Codex / OpenCode):**

    After the test plan skeleton exists, derive story-specific skill candidates from the Goal Contract, acceptance criteria, architecture blueprint, and test plan.

    *   Propose skills only when they clearly support repeated implementation, review, QA, or release evidence for **this story** (not one-off chat instructions).
    *   Check for **duplicate** triggers against existing AgToosa workflow skills, platform adapters, and project skills under `.codex/skills/`. Prefer **Update existing** or **Do not generate** over creating a near-duplicate.
    *   **Reserved workflow names:** reject candidates named `agtoosa-*`, triggered by `/agtoosa-*`, or that would shadow `.claude/commands/agtoosa-*.md`, `.cursor/commands/agtoosa-*.md`, `.windsurf/workflows/agtoosa-*.md`, `.gemini/commands/agtoosa-*.toml`, `.github/prompts/agtoosa-*.prompt.md`, `.codex/prompts/agtoosa-*.md`, or `.codex/skills/agtoosa-*` unless updating an installed AgToosa workflow adapter — those names are reserved for AgToosa lifecycle commands, not generated project skills.
    *   Reject candidates without validation (command, checklist, or artifact review).
    *   **Secret safety:** exclude secret values from generated skills; reference file paths and process steps only. Add a safety note when credentials or tokens are relevant.
    *   Present the same candidate table shape as `/agtoosa-init` Project Skill Discovery (Skill name, Trigger description, Purpose, Inputs, Optional resources, Validation, Decision).
    *   Require **explicit user approval** before writing any `.codex/skills/<skill-name>/SKILL.md` file.
    *   Record accepted and declined decisions in the active spec file or `Docs/Master-Plan.md` **Update Log**.

### Optional cross-framework export (DEV-124)

After **Spec Approved**, maintainers may export the archived spec to framework-shaped artifacts for comparison or handoff — **optional**, not a verifier gate:

```bash
bash Docs/agtoosa-interchange-export.sh --story <Story ID> --target speckit|openspec|bmad|kiro --output Docs/archived/interchange-manifest-<id>.json
```

When binding a proof graph pointer, pass `--proof-graph <path>` and verify separately with `Docs/agtoosa-proof-verify.sh` — export does **not** mark graphs valid. See `Docs/AgToosa_Cross_Framework_Interchange.md`. Interchange output is **derived**; `Docs/Master-Plan.md` remains repo-local source of truth.

## Policy violation contract

Consult `Docs/AgToosa_GovernancePolicy.md` (checker: `Docs/agtoosa-policy-check.sh`) before actions covered by a declared rule. On a policy violation: identify the rule `id`, `enforcement_class`, and `on_violation`; follow that `on_violation` only (`warn` / `instruct_stop` / wired `block_generator`); never invent stronger enforcement; never echo secret values. Preserve `Docs/Master-Plan.md` as lifecycle authority — policy handling must not write story status or tasks.

## Output
*   Present the generated Spec (with Goal Contract and embedded plan), task list, and test plan skeleton to the user.
*   Print the **dual-line phase close** (see `Docs/AgToosa_Agent.md` → **Lifecycle Next-Step Contract**): primary `Next: /agtoosa-<command>` line, then automatic `SYNC:` pulse. Optional tertiary: `/agtoosa-status` for full health findings — **not** the headline next step.
*   Present the approval gate:

    ```
    ✅ Ready to proceed
    Spec [name] generated: Goal Contract clear, [N] ACs, [N] Must-priority, threat model complete.
    [N] atomic tasks derived. Test plan skeleton: [N] test IDs mapped to [N] ACs.
    → Approve — I'll mark the spec approved; run /agtoosa-build when you are ready
    → Comment or request changes below
    ```

*   **Served by `/agtoosa-next`:** When this spec run was dispatched by `/agtoosa-next`, skip the wait above. If the Spec Quality Analyzer passes, append `## ✅ Spec Approved`, update Master-Plan, and close with `Next: /agtoosa-next — build [story-id]`. Do **not** invoke `/agtoosa-build` in the same invocation.

*   **Stop here** after presenting the approval gate (direct `/agtoosa-spec` only). Do not invoke `/agtoosa-build` until the user explicitly runs it.

*   When the user approves, **append the following section verbatim** to the spec file:

```
## ✅ Spec Approved

Approved: [YYYY-MM-DD HH:MM]
```

This approval marker is required by `/agtoosa-ship check` to verify the spec was signed off before deployment. Do not proceed to `/agtoosa-build` without appending it.

*   **Master-Plan Update Log:** Immediately after appending the approval marker, add a timestamped entry to `Docs/Master-Plan.md` `## Update Log`:

    `YYYY-MM-DD HH:MM — /agtoosa-spec — Spec ✅ Approved — [Story ID] — [spec filename]; estimate [XS/S/M/L/XL]; [enrolled in cycle / backlog only].`

    Keep the Active Cycle row at `Todo` until `/agtoosa-build` starts the first TDD task (then status → `In Progress` per `Docs/AgToosa_Governance.md`).

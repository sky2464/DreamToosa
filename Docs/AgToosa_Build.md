# AgToosa /agtoosa-build Workflow

## Sub-Commands

| Sub-command | Runs |
|-------------|------|
| `/agtoosa-build` | Full flow: Parts 1 + 2 + 3 |
| `/agtoosa-build tdd` | Part 1 only — TDD Red-Green-Refactor loop against the task list from the approved spec |
| `/agtoosa-build test` | Parts 2 + 3 — run the full testing army + security scans, then update tracking |
| `/agtoosa-build handoff` | Export a handoff pack for remaining wave tasks via `Docs/AgToosa_Handoff.md` (recommend target via `Docs/AgToosa_AgentCapability.md`) |
| `/agtoosa-build import` | Run Import Checklist for returning async agent results via `Docs/AgToosa_Import.md` |

### Claude Code Parallel Pattern

On Claude Code, independent tasks within a phase can be dispatched to parallel sub-agents via the `Task` tool. Apply this when the task list from the spec contains tasks with no sequential dependency:

- Read the task list in `Docs/Master-Plan.md` under `## Active Tasks`.
- Identify tasks that do not share state with other tasks.
- Batch those tasks into parallel `Task` tool calls before starting the TDD loop (Part 1).
- Each parallel subagent must return the **Terminal Evidence Contract** block from `Docs/AgToosa_Agent.md` (command, exit code, pass/fail, warnings, errors, changed files, next action).
- Collect results when all parallel tasks complete; merge conflicts are resolved by the orchestrating agent.
- The orchestrator must summarize unresolved terminal output before marking any task checkbox done.
- Async or background agents dispatched via parallel sub-agents should receive a `/agtoosa-handoff` pack (run `/agtoosa-build handoff` before dispatch) and return results via `/agtoosa-import` (Terminal Evidence still required).
- Before async dispatch, consult `Docs/AgToosa_AgentCapability.md` for an installed-surface routing recommendation and documented fallbacks.
- See `/agtoosa-review` for the reference parallel pattern (4 reviewer personas run simultaneously).

> **Note:** Parallel dispatch applies to Claude Code only. On other platforms, run tasks sequentially.

## Objective
Execute TDD against a planned task list and run the full test suite.

> **Prerequisites:** `/agtoosa-spec` must be complete with task planning done.
> Verify:
> 1. The active spec (`Docs/archived/spec-[story-id].md` for the story in `## Active Cycle`) has a `## ✅ Spec Approved` section. If not, **stop** and instruct the user to run `/agtoosa-spec` (or approve the spec). Do **not** auto-run `/agtoosa-spec`.
> 2. `Docs/Master-Plan.md` has tasks listed under `## Active Tasks`. If not, **stop** and instruct the user to run `/agtoosa-spec tasks`. Do **not** auto-run `/agtoosa-spec tasks`.
> 3. The story status allows building (Todo or In Progress). Out-of-order runs follow `Docs/AgToosa_Governance.md` → **Conflict playbook**: warn and abort with the exact message defined there.

### Optional pre-build steps (DEV-122)

Before Wave 1, agents **may** run optional change-aware steps — they are **not** verifier gates:

| Step | Command | Notes |
|------|---------|-------|
| Drift assess | `bash Docs/agtoosa-drift-assess.sh --baseline <path> --root .` | Default suggest-only (exit 0); see `Docs/AgToosa_Change_Aware_Delivery.md` |
| Context compile | `bash Docs/agtoosa-context-compile.sh --story <id> [--proof-graph PATH] [--drift-report PATH]` | Derived JSON only — does not mutate Master-Plan |

Proof graph validity still requires separate `Docs/agtoosa-proof-verify.sh` when a graph is cited.

## Terminal Evidence Contract

> See `Docs/AgToosa_Agent.md` → **Terminal Evidence Contract** for the full rules.

After every command, test run, scan, or parallel subagent during `/agtoosa-build`:

- Report command run, exit code, pass/fail, warnings, errors, changed files, and next action.
- A nonzero exit code, lint warning, markdownlint warning, or failing test **blocks** marking the task complete unless explicitly classified as accepted/pre-existing with evidence.
- Before checking off any task in `Docs/Master-Plan.md` or the active spec, summarize any unresolved terminal output.

## Workflow

### Part 1 — TDD Build Cycle

> **TDD Enforcement:**
> If `Docs/Context/workflow.md` has `tdd: true`, strictly follow the Red-Green-Refactor cycle below.
> If TDD is disabled, still write tests but the strict ordering is relaxed.

**Before starting the first TDD task:**
- Update `Docs/Master-Plan.md`: move the Story row from `## Backlog` to `## Active Cycle`, set status to `In Progress`.
- Append a phase event to `Docs/agtoosa-events.jsonl` (create the file if missing):
  `{"ts":"[ISO-8601 UTC]","phase":"build","event":"start","story":"[Story ID]","by":"AgToosa"}`
- Add an Update Log entry to `Docs/Master-Plan.md`:

    ```
    Build 🏗️ Started
    Date: [YYYY-MM-DD HH:MM]

    Starting TDD cycle. [N] tasks declared. Scope: [list key files in scope].

    Next: Task 1/[N] — [task title].
    ```

1.  **Scope Boundary Reminder:** Read the `### 2.4 Build Scope` section in the active spec (`Docs/archived/spec-[story-id].md`). Any edit to a file not listed there requires stopping and presenting:
    ```
    ❓ [filename] is outside the declared scope.
      → A) Include it in scope (I'll update the spec)
      → B) Skip this file
      → C) Create a separate /agtoosa-task for it
    ```
    This check runs before every file write during the TDD cycle.

2.  **Dependency Validation:** Never assume dependency versions from memory — verify via web search or terminal (`npm view`, `pip index`, `dart pub outdated`).

3.  **Wave execution:** Read `### 3.2 Wave Plan` and `### 3.4 Work Package DAG` in the active spec and execute tasks **wave by wave**: complete every task in Wave N — including its Terminal Evidence — before starting Wave N+1. Within a wave, tasks share no files or data dependencies, so on Claude Code they may be dispatched in parallel via the pattern above; on all other platforms run the wave's tasks sequentially. If the spec has no Wave Plan, fall back to the `## Active Tasks` order in `Docs/Master-Plan.md`.

    > **Orchestration Brain step 0:** Before Wave / Work Package fan-out, read `Docs/AgToosa_Orchestration.md` and run Capability Inventory → lane plan → parallel or sequential dispatch → orchestrator merge.

    > **Work Package fan-out gate (agent-instructed):** Before parallel fan-out of a wave, read each Work Package row for that wave:
    > - Confirm every `depends_on` package exists, is complete, and has an **earlier wave**.
    > - Confirm same-wave `owned_files` sets are **disjoint**. On overlap, do **not** fan out in parallel — convert the affected packages to an explicit **sequential fallback** in the Wave Plan and run them in `merge_order`.
    > - Run each package's `verification` command after its lane completes; present accepted results in `merge_order` before Tracking updates.
    > - Claim Boundary: package checks are **agent-instructed**; agent selection and branch integration are **manual**; a runtime scheduler is **roadmap**.

    > **Optional worktree isolation (agent-instructed):** For **M+** waves with at least two parallel packages (or an explicitly risky lane), offer optional isolation per `Docs/AgToosa_Worktree.md`. Preferred path: `../<repo>-<package_id>`. Git worktree add/list/remove/prune is **manual** — AgToosa does not create worktrees. When skipping: state exactly `No worktree: run packages sequentially in one branch and verify a clean working tree between packages.` Lifecycle routing remains a **read-only** consult of `Docs/AgToosa_AgentCapability.md` (do not edit it).

    > **Async dispatch:** Before sending tasks to async or background agents for a wave, offer to run `/agtoosa-handoff wave` (see `Docs/AgToosa_Handoff.md`) to export a handoff pack that includes the selected-wave Work Packages section. Agents should return results via `/agtoosa-import` before any Tracking update.

4.  **For each atomic task, execute the TDD Cycle:**

    **⚠️ External / async task detection — runs before every task:**
    Before starting a task, check whether the work was completed out-of-band (by an async agent, background runner, or external actor). If so, run the Import Checklist (`/agtoosa-import` or `Docs/AgToosa_Import.md`) before any Tracking update. Never mark a task complete without recorded verification commands and mapped ACs. "Imported claims are not evidence until repo-local verification passes."


    **⚠️ Manual Task Detection — runs before every task:**
    Before starting a task, check whether its line in `Docs/Master-Plan.md` or the active spec contains `[manual]` or `[manual-deferred]`.

    *   If the task is tagged `[manual]`, present this prompt — do NOT proceed with TDD:

        ```
        👤 Manual task: [task title]
        This step requires a human action outside the agent.
        What would you like to do?
          → A) I've completed it — mark it done and continue
          → B) Defer it for now — continue with remaining automated tasks
          → C) Show me what needs to be done, then defer
        ```

        - **If A:** mark the sub-task `- [x] N.M [task] \`[manual-done]\`` in both `Docs/Master-Plan.md` and the spec; count it as a completed task and continue.
        - **If B or C:** update the annotation to `[manual-deferred: YYYY-MM-DD]` in both files; add a line to the Manual / Deferred section in `Docs/Master-Plan.md`; **skip to the next task** — do not block the build cycle.
        - In all cases, add a note to the Update Log entry for this build session listing deferred manual tasks.

    *   If the task is already tagged `[manual-deferred]`, skip it automatically and mention it in the session summary.

    **🔴 RED — Write a Failing Test First:**
    *   Before writing ANY implementation code, write a test that describes the expected behavior.
    *   The test MUST fail initially (confirming it tests something real).
    *   **RED evidence (mandatory):** run the new test and capture the failing run **before** writing implementation code. Record it in the story test plan (`Docs/AgToosa_TestPlan-[story-id].md`) as:

        ```
        RED evidence — [task-id]
        Command: [test command]
        Exit code: [nonzero]
        Failure excerpt: [1–3 lines of the assertion/error]
        ```

        A test that passes on first run is **not** RED — it tests nothing new. Rewrite it before proceeding. Tasks without RED evidence cannot be checked off.
    *   Test types: unit tests, integration tests, or E2E tests as appropriate.
    *   **Test Data Rules:**
        - Use clearly fake values only — names like "Test User", emails like "test@example.com"
        - Never use real PII in test fixtures — 🔴 Critical finding in `/agtoosa-review` if found
        - Define fixtures and factories in `tests/fixtures/` or `tests/factories/`
        - Integration tests that touch a database must use isolated transactions or a dedicated test schema
        - Seed data scripts must be idempotent (safe to run multiple times)

    **🟢 GREEN — Minimal Implementation:**
    *   Write the MINIMUM code necessary to make the failing test pass.
    *   Do NOT add features, optimizations, or abstractions beyond what the test requires.
    *   Run the test suite to confirm the new test passes and no existing tests break.
    *   **GREEN evidence:** append the passing run to the same test-plan block:

        ```
        GREEN evidence — [task-id]
        Command: [test command]
        Exit code: 0
        ```
    *   **WIP Micro-Commit:** once green, immediately commit progress by staging the exact files changed for this task (from the Terminal Evidence Contract changed-files list — never interactive staging, never `git add .`):
        ```
        git add [changed file paths] && git commit -m "WIP: [task-id] [short description]"
        ```
        This preserves progress and allows context restoration if the session is interrupted.

    **🔵 REFACTOR — Clean Up:**
    *   With all tests green, refactor the code for clarity, readability, and maintainability.
    *   Apply linting rules (from `workflow.md` config).
    *   Ensure no file exceeds 500 lines of code.
    *   Ensure OpenTelemetry observability hooks are present (structured logging, metrics, tracing).
    *   Run the full test suite again to confirm nothing broke.
    *   **Tracking update (per completed task):** After the Refactor step passes:
        - In the active spec (`Docs/archived/spec-[story-id].md`), change `- [ ] N.M [task]` → `- [x] N.M [task]` in `## 3. Tasks / ### 3.1 Task Tree`.
        - In `Docs/Master-Plan.md` under `## Active Tasks`, change the same checkbox `- [ ] N.M` → `- [x] N.M`.
        - In `Docs/Master-Plan.md` under `## Active Cycle`, increment the progress bar: update the ▰/▱ fill and the counter (e.g. `▰▰▰▱▱▱▱▱ 2/8 tasks` → `▰▰▰▰▱▱▱▱ 3/8 tasks`). Each ▰ represents one completed task.
        - Update `Docs/Master-Plan.md`: increment the Tasks Done count for the Story row.
        - Add an **Update Log** entry: `YYYY-MM-DD HH:MM — /agtoosa-build — Task 🟢 [N]/[M] complete — [Story ID] — [task title]; tests green.`

5.  **Repeat** the Red-Green-Refactor cycle for every atomic task.

6.  **After all tasks are processed**, check for deferred manual tasks:
    *   If any tasks are `[manual-deferred]`, present a summary:

        ```
        ⏸️ Manual tasks deferred ([N] remaining):
          - [task title] (deferred: YYYY-MM-DD)
          - …

        Run /agtoosa-status to see these listed without affecting the health score.
        When you complete them, run /agtoosa-build and select (A) to mark them done.
        ```

    *   Update the Active Cycle Tasks Done counter in `Docs/Master-Plan.md` using the format: `[auto-done]/[auto-total] tasks ([N] manual-deferred)`.
    *   Story status remains 🟨 In Progress only if automated tasks are still incomplete. If all automated tasks are done and only manual tasks remain deferred, transition the story status to **🔧 Awaiting Manual** — a distinct state that `/agtoosa-status` treats as non-blocking.

### Discovery Triage

Any bug, edge case, or out-of-scope requirement discovered during the TDD cycle must be triaged immediately — **never silently fixed or dropped**.

**Trigger conditions** (run triage when any of these are noticed):
- A bug in existing code not related to the current task
- An edge case not covered by the active spec's ACs
- A missing test for existing behavior
- A new requirement raised by the user mid-build
- Technical debt that would take > 30 min to fix now
- A dependency security issue found during SBOM/audit step

**Triage steps** (non-blocking — inline, < 2 min):
1. Classify: Bug / Chore / Feature / Security
2. Size: can it be fixed in < 15 min without scope creep? If yes → fix it now and note it in the build summary.
3. If not trivial — ask the user: "I found [brief description]. Should I: (A) add to Master-Plan.md Backlog for later, (B) add to current scope, or (C) ignore?"
4. **If A** — run `/agtoosa-task`, add `Discovered during /agtoosa-build on [Story ID] on [date]` to the description, record in `Docs/Master-Plan.md` under `## Backlog`. Note: Backlog items use flat table rows (ID | Title | Type | Estimate | Epic | Priority). The hierarchical task tree is only used in `## Active Tasks` for the current In Progress story.
5. **If B** — update the Scope Boundary in the active spec, create a new Task sub-issue under the Story, continue TDD.
6. Record the triage decision (fix now / issue created / ignored) in the build summary output.

### Part 2 — Comprehensive Testing

6.  **Unbiased Testing:**
    *   Drop prior assumptions about how the code should work; evaluate purely to find bugs and regressions.
    *   Run all unit, integration, and E2E tests; add browser QA (Playwright/Puppeteer) where applicable.
7.  **Security Scanning:** SAST (Semgrep/CodeQL), DAST (runtime checks), Secrets scanning (Gitleaks), IaC scanning (Checkov/tfsec).
8.  **SBOM:** Generate a Software Bill of Materials; run dependency audits (`npm audit`, `pip-audit`).
9.  **Feedback Loop:** Loop back to the TDD cycle for any issues found; record fixes in `Master-Plan.md`.

### Part 3 — Tracking

10. **Master-Plan Update:** Mark all completed tasks in `Docs/Master-Plan.md`; update story status.
11. **Phase event:** Append to `Docs/agtoosa-events.jsonl`:
    `{"ts":"[ISO-8601 UTC]","phase":"build","event":"complete","story":"[Story ID]","by":"AgToosa"}`
12. **Self-verify:** Run `bash Docs/agtoosa-verify.sh` and resolve any FAIL findings before reporting the build complete.

## Policy violation contract

Consult `Docs/AgToosa_GovernancePolicy.md` (checker: `Docs/agtoosa-policy-check.sh`) before actions covered by a declared rule. On a policy violation: identify the rule `id`, `enforcement_class`, and `on_violation`; follow that `on_violation` only (`warn` / `instruct_stop` / wired `block_generator`); never invent stronger enforcement; never echo secret values. Preserve `Docs/Master-Plan.md` as lifecycle authority — policy handling must not write story status or tasks.

## Hook lifecycle pointers

Consult `Docs/AgToosa_Hooks.md` for the single event/platform matrix. During Build, apply checklist (or proven native) steps for `task-start`, `pre-tool-use`, `pre-test`, and `post-test` as applicable. Do not duplicate the matrix here. Optional pack absence is not a health or verifier finding.

## Output
*   Confirm build and test phases are complete and all tests pass.
*   Present a summary of test results and any security findings.
*   If any wave tasks remain for async dispatch, offer to run `/agtoosa-build handoff` (see `Docs/AgToosa_Handoff.md`) before handing off to external agents. On return, run `/agtoosa-build import` (see `Docs/AgToosa_Import.md`) to verify and integrate results.
*   Print the **dual-line phase close** per `Docs/AgToosa_Agent.md` → **Lifecycle Next-Step Contract** (`Next:` lifecycle command + `SYNC:` pulse). Optional: `/agtoosa-status` for full health findings.
*   Prompt the user to run `/agtoosa-review`.

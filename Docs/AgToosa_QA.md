# AgToosa /agtoosa-qa Workflow

## Sub-Commands

| Sub-command | Runs |
|-------------|------|
| `/agtoosa-qa` | Full flow: test plan → execution → defect capture → QA report |
| `/agtoosa-qa plan` | Test plan only — map spec ACs to test IDs, categories, and smoke set |
| `/agtoosa-qa run` | Execute test suite with structured AC coverage capture |
| `/agtoosa-qa report` | Generate `Docs/AgToosa_QAReport-[name].md` from current test results |
| `/agtoosa-qa triage` | P0–P4 severity scoring; auto-add P0–P2 defects to `Docs/Master-Plan.md` Backlog |

## Objective
Give QA testers a dedicated command to own the quality gate — from test planning through defect lifecycle — separate from the code review phase.

## Terminal Evidence Contract

> See `Docs/AgToosa_Agent.md` → **Terminal Evidence Contract** for the full rules.

During `/agtoosa-qa run`, capture command run, exit code, pass/fail, warnings, errors, changed files, and next action for every test command. Failing tests or nonzero exits block AC sign-off unless explicitly accepted with evidence. Summarize unresolved terminal output in the QA report before the approval gate.

## Workflow

### Part 1 — Test Plan Generation (`/agtoosa-qa plan`)

1. **Read the active spec:**
   *   Open the active spec (`Docs/archived/spec-[story-id].md`) and locate the `### 1.2 Acceptance Criteria (EARS)` table (any heading containing `Acceptance Criteria`, or rows matching `AC-NNN`, qualifies).
   *   If no AC table exists, **stop** and instruct the user to run `/agtoosa-spec` or add ACs manually. Do **not** auto-run `/agtoosa-spec`.

2. **Generate `Docs/AgToosa_TestPlan-[story-id].md`** containing:
   *   **Spec reference** — link to the source `Docs/archived/spec-[story-id].md`
   *   **AC coverage table** — each `AC-NNN` mapped to one or more test IDs (`T-001`, `T-002`, ...)
   *   **Test category** per test ID: Unit · Integration · E2E · Security · Performance
   *   **Coverage target** — read `coverage_threshold` from `Docs/Context/workflow.md`; default 80%
   *   **Edge cases and negative scenarios** — at least one negative test per Must-priority AC
   *   **Smoke set** — tag at least one test per Must-priority AC with `@smoke`; these run post-deployment
   *   **Test environment requirements** — services, seed data, feature flags needed

3. Present the test plan as an approval gate before running any tests:

    ```
    ✅ Test plan ready
    [N] test IDs · [N] Must-priority ACs covered · [N] smoke-tagged tests · Coverage target: [N]%
    → Approve to run tests  |  Update the plan below
    ```

    Wait for explicit approval before executing the test suite.

### Part 2 — Test Execution (`/agtoosa-qa run`)

4. **Run the full test suite** and capture results per test ID from the plan.
   *   Map each pass/fail result to its `AC-NNN` entry.

5. **Coverage check:**
   *   Verify overall coverage meets the threshold from `Docs/Context/workflow.md`.
   *   List any AC with zero passing tests as **uncovered** — these are open defects regardless of overall coverage %.

6. **Smoke set verification:**
   *   Confirm all `@smoke`-tagged tests pass.
   *   A failing smoke test blocks `/agtoosa-ship`.

### Part 3 — QA Report (`/agtoosa-qa report`)

7. **Generate `Docs/AgToosa_QAReport-[name].md`** containing:
   *   Test run summary (total / passed / failed / skipped)
   *   AC coverage table with Pass/Fail per test ID
   *   Coverage % vs. threshold
   *   Open defects list (failed tests with steps to reproduce)
   *   Smoke set status (Pass / Fail / Not yet tagged)

8. **Gate:**
   *   All Must-priority ACs covered + smoke tests pass → QA cleared, prompt `/agtoosa-review`
   *   Any Must-priority AC uncovered or smoke fails → block, list failures clearly

### Part 4 — Defect Triage (`/agtoosa-qa triage`)

9. **Assign severity to each open defect:**

   | Severity | Criteria |
   |----------|----------|
   | P0 — Critical | Data loss, security breach, or system completely down |
   | P1 — High | Core feature broken with no workaround |
   | P2 — Medium | Partial feature broken; workaround exists |
   | P3 — Low | Minor UX issue or edge case with low user impact |
   | P4 — Cosmetic | Visual or copy issue, no functional impact |

10. **Add to Master-Plan.md Backlog** all P0–P2 defects. Each entry must include:
    *   Failing test ID and `AC-NNN` reference
    *   Steps to reproduce
    *   Severity (P0–P2) and priority
    *   Link to `Docs/AgToosa_QAReport-*.md`

11. **P3–P4 defects** are recorded in the QA report only — user decides whether to add them to `Docs/Master-Plan.md`.

## Output
*   `Docs/AgToosa_TestPlan-[name].md` after Part 1
*   `Docs/AgToosa_QAReport-[name].md` after Part 3
*   `Docs/Master-Plan.md` Backlog entries for every P0–P2 defect after Part 4
*   If QA cleared: prompt `/agtoosa-review`
*   If blocked: list exactly which ACs are uncovered and which smoke tests failed

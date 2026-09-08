# AgToosa /agtoosa-review Workflow

## Sub-Commands

| Sub-command | Runs |
|-------------|------|
| `/agtoosa-review` | Full flow: all 4 personas + cross-model gate when tier recommends + cross-platform suggestion |
| `/agtoosa-review security` | Security Officer persona only — OWASP + STRIDE audit |
| `/agtoosa-review arch` | Engineering Manager persona only — architecture, 500-line limit, observability |
| `/agtoosa-review debug` | Iron Law root-cause investigation for a specific bug or failing test |
| `/agtoosa-review cross` | Cross-platform second-opinion guidance (switch to another installed AI platform and re-run review) |
| `/agtoosa-review cross-model` | Cross-model review gate — independent reviewer subagent/model (`Docs/AgToosa_CrossModelReview.md`) |

## Objective
Ensure code quality, security, and simplicity through multi-persona review.

> **Prerequisites:** `/agtoosa-build` must be complete. Verify that the full test suite passes and the Story status in `Docs/Master-Plan.md` is `In Progress` (not `Todo`). If tests are failing or no build artifact exists, **stop** and instruct the user to run `/agtoosa-build test`. Do **not** auto-run `/agtoosa-build`.
>
> **Phase-order abort (from `Docs/AgToosa_Governance.md`):** If the Story status is still `Todo`, print exactly `⚠️ Story [ID] is in 'Todo' state. Run /agtoosa-build first.` and abort.

### Terminal Evidence Contract

> See `Docs/AgToosa_Agent.md` → **Terminal Evidence Contract** for the full rules.

Each reviewer persona (or parallel subagent) must report command run, exit code, pass/fail, warnings, errors, changed files, and next action for every test, scan, or command executed. Nonzero exits and tool warnings block a 🟢 Passed verdict unless explicitly accepted with evidence. The orchestrator summarizes unresolved terminal output before presenting the review approval gate.

## IDE Host Mode Bridge

> Canonical auto-switch rules: `Docs/AgToosa_Agent.md` → **IDE Host Mode Bridge**. Per-platform enter/switch: `Docs/AgToosa_AgentCapability.md` → **IDE Host Mode Matrix**.

| Sub-command | Plan-mode window | Agent/Auto window |
|-------------|------------------|-------------------|
| Full (no arg) | Persona analysis, Iron Law hypotheses, cross-model gate planning, findings synthesis as structured plan | Write `Docs/archived/review-*.md`, evidence ledger, Master-Plan status, simplification refactors, verdict gate |
| `security`, `arch`, `debug` | Analysis and hypothesis work for the sub-command | Sub-command writes and fixes |
| `cross`, `cross-model` | Planning and comparison strategy | Merge findings into review report |

Before persona fan-out, ensure the host is in **native IDE plan mode** when available. Produce persona findings tables, Iron Law hypotheses, and cross-model gate decisions as **plan sections** inside plan mode. When briefing is complete, print `HOST-MODE: plan complete → switching to agent for AgToosa artifacts`, switch to Agent/Auto, then write review artifacts.

Every review report must include `### Plan-Mode Review Briefing (findings)` before the structured findings table:

| Subsection | Content |
|------------|---------|
| **Persona synthesis** | Security / EM / CEO / QA summary rows |
| **Iron Law hypotheses** | Hypothesis log for any 🔴 Critical or debug sub-command |
| **Cross-model gate** | Tier, consent, skip rationale, or delegation decision |
| **Host mode handoff** | Timestamp or turn when plan → agent switch occurred |

### Part 1 — Virtual Specialist Reviews

**Orchestration Brain step 0:** Before persona, specialist, and cross-model fan-out, read `Docs/AgToosa_Orchestration.md` and run Capability Inventory → lane plan → parallel or sequential dispatch → orchestrator merge.

**Before starting reviews:**
- Update `Docs/Master-Plan.md`: set the Story row status to `In Review`.
- Add an **Update Log** entry: `YYYY-MM-DD HH:MM — /agtoosa-review — Review 🔍 Started — [Story ID] — 4-persona review running.`

1.  **Security Officer:** OWASP Top 10 + STRIDE audit; SAST/DAST/Secrets scanning (Semgrep, CodeQL, Gitleaks); verify threat model from Spec.

2.  **Engineering Manager (`/agtoosa-review arch`):** Confirm no file exceeds 500 lines; check OOP compliance, observability hooks, and test coverage thresholds. When running the `arch` sub-command, additionally:

    **Master Architecture Alignment:** Read `Docs/Master-Architecture.md` and verify the change matches the documented boundaries, diagrams, data flow, deployment, security, and observability notes. Flag missing, stale, or contradicted architecture documentation as a 🟡 Warning, or 🔴 Critical if the implementation violates a documented security or boundary constraint.

    **Deep Module Analysis** (see `Docs/DEEPENING.md`):
    - Identify shallow modules: pass-through functions, one-line service methods, "Manager/Handler/Helper" classes with no domain meaning.
    - For each shallow module found: flag as 🟡 Warning with specific refactor suggestion.
    - Check that interfaces reveal WHAT the module does, not HOW it does it.

    **Domain Language Alignment** (see `Docs/LANGUAGE.md` + `Docs/Context/CONTEXT.md`):
    - Verify that variable names, function names, error messages, and API endpoints use terms from `Docs/Context/CONTEXT.md`.
    - Flag any inconsistency (e.g., `userId` when domain says `accountId`) as 🟡 Warning.
    - If `Docs/Context/CONTEXT.md` doesn't exist, note it as 🟡 Warning and suggest running `/agtoosa-spec` to establish domain language alignment.

    **ADR Coverage:**
    - Identify any significant architectural decisions made in this change that lack a corresponding ADR in `Docs/adr/`.
    - Create missing ADRs using `Docs/ADR-FORMAT.md` as a template, or flag as 🟡 Warning if creation is out of scope.

3.  **CEO / Product Owner:** Verify feature completeness against the Goal Contract, Project Charter in `Docs/Master-Plan.md`, and acceptance criteria.

    **Goal Contract Alignment:**
    - Read the active spec's `### Goal Contract`.
    - Confirm the implemented behavior satisfies the stated Goal and User outcome.
    - Confirm the Success condition is measurable and has Proof / evidence in tests, review artifacts, demo notes, or product behavior.
    - Flag missing, vague, or contradicted Goal Contract fields as 🟡 Warning.
    - Flag implementation that meets isolated ACs but fails the Goal Contract as 🔴 Critical.

4.  **QA Lead:**

    a. **Test suite** — Confirm all unit, integration, E2E, and browser QA tests pass; verify TDD cycle was followed if enabled.

    b. **Coverage gate** — Read `coverage_threshold` from `Docs/Context/workflow.md`; flag below-threshold as 🔴 Critical.

    c. **AC coverage** — Verify every `AC-NNN` (Must-priority) in the active spec has at least one passing test in the test plan. Any uncovered AC is 🔴 Critical.

    d. **Regression check** — If this is a bug fix, confirm a regression test exists and passes (name pattern: `regression_[bug-id]_*`).

    e. **Accessibility** — For web/mobile: run axe-core or Playwright a11y checks; flag WCAG 2.1 AA violations as 🟡 Warning.

    f. **Performance baseline** — For web: verify Core Web Vitals are not regressed vs. prior run; flag regressions as 🟡 Warning.

    g. **Browser/device matrix** — Check the `browser_matrix` list in `Docs/Context/tech-stack.md`; flag untested combinations as 🟡 Warning.

    h. **Flaky test detection** — Re-run the tests touched by this story (or use the runner's `--repeat N` when available) and flag any test that passes/fails non-deterministically as 🟡 Warning. Do not re-run the entire suite 3× — scope flake detection to changed tests to keep review time and token cost bounded.

    **🔬 Iron Law — Bug Root Cause Protocol** (`/agtoosa-review debug` runs this exclusively):

    When a test failure or bug is found, follow this protocol before writing any fix:
    1. State a **hypothesis** — which specific code path or assumption is causing this?
    2. Write a **targeted reproduction test** that isolates the failure
    3. Once the hypothesis is confirmed, write a **regression test** named `regression_[bug-id]_[short-desc]`:
       - The regression test MUST fail on the unfixed code
       - The regression test MUST pass after the fix
       - The regression test MUST NOT be deleted or skipped
       - Record the regression test ID in the 🔴 Critical finding row
    4. If the reproduction test disproves the hypothesis → document why it was wrong, form a new hypothesis, repeat
    5. After **3 failed hypotheses** → stop and escalate to the user with the hypothesis log; do NOT apply a blind fix

    The root cause AND regression test ID must appear in the review report alongside every 🔴 Critical finding.

### Part 2 — Code Simplification

5.  **Simplify:** Identify complex or repetitive code and refactor for clarity. **Principle: Clarity over Cleverness.** Apply linting rules from `workflow.md`; re-run tests after every refactor.

### Part 3 — Final Verdict

6.  **Review Report:** Structured findings from all 4 personas — 🔴 Critical / 🟡 Warning / 🟢 Passed. Every 🔴 Critical must include the Iron Law root cause. Include a Goal Contract alignment row. Block `/agtoosa-ship` if any 🔴 Critical findings remain.

    **Ship version suggestion (maintainer / semver repos):** In the review report footer, default the suggested release to **PATCH+1** on the current MINOR (e.g. `5.2.0` → `5.2.1` for Fix/Chore/S stories). Use **MINOR** only for a new MINOR train, multi-story batched release, or deliberate cycle boundary; use **MAJOR** only for breaking changes per ADR-004. See `Docs/adr/ADR-005-release-cadence.md` (generator) or project ADRs. Do not suggest skipping to the next MINOR for routine small stories.

    **Master-Plan update (after verdict):**
    - If **all clear** (no unresolved 🔴 Critical): add **Update Log** entry `Review ✅ Approved` (per `Docs/AgToosa_Governance.md`). Keep Active Cycle status `In Review` until `/agtoosa-ship` completes.

    - If **blocked** (unresolved 🔴 Critical): add **Update Log** entry `Review 🔴 Blocked: [brief list]`; set Active Cycle status back to `In Progress`.

### Part 4 — Cross-Platform Second Opinion (`/agtoosa-review cross`)

Different AI models surface different classes of bugs — a second platform review is a free, high-signal quality gate.

7.  **Cross-Platform Review:**
    1. Open a secondary AI platform (e.g., if primary is Claude Code, open Cursor or GitHub Copilot)
    2. Run `/agtoosa-review` on the same branch
    3. Compare findings — issues flagged by **both** platforms are high-confidence; issues flagged by only one warrant investigation
    *   Merge findings from both reports before running `/agtoosa-ship`. Cross-platform review is **strongly recommended** for security-sensitive changes.

### Part 5 — Cross-Model Review Gate (`/agtoosa-review cross-model`)

Writer/reviewer separation across different agents or models reduces single-agent blind spots. **Do not duplicate the full contract here** — read and execute `Docs/AgToosa_CrossModelReview.md`.

For parallel vs sequential routing per installed host, consult `Docs/AgToosa_AgentCapability.md` (Cross-model column + Fallback Chain) before launching reviewer lanes.

8.  **Cross-Model Review:**
    *   Read `Docs/Context/workflow.md` → `cross_model` and `reviewer_model` before tiering or delegation (see `Docs/AgToosa_CrossModelReview.md` → Project configuration).
    *   After Part 1 virtual personas (or when running `cross-model` alone), compute the risk tier from the active spec threat model and Must ACs.
    *   For **recommended** or **strongly recommended** tiers, run `/agtoosa-review cross-model` or record an explicit **skip rationale** in the review report `## Cross-Model Review` section — unless `cross_model: off` or `on-demand` without user request.
    *   **User consent:** Print the cross-model consent line and apply the **model ceiling** (reviewer must not exceed parent session model tier without explicit user approval in the same turn).
    *   Delegate an **independent reviewer** read-only subagent — **same model as the parent session is valid**; do not default to premium models for independence.
    *   When `Docs/Context/specialists.md` exists, orchestrate `review`-phase specialists per `Docs/AgToosa_Specialists.md` (trigger match only).
    *   Merge findings with confidence tiers (`both-models`, `reviewer-only`, `writer-only`, `virtual-persona-only`) before Part 3 verdict.
    *   Fallback when no second model/subagent is available or the user declines: `/agtoosa-review cross`, sequential virtual personas, or documented skip — see `Docs/AgToosa_CrossModelReview.md`.

## Policy violation contract

Consult `Docs/AgToosa_GovernancePolicy.md` (checker: `Docs/agtoosa-policy-check.sh`) before actions covered by a declared rule. On a policy violation: identify the rule `id`, `enforcement_class`, and `on_violation`; follow that `on_violation` only (`warn` / `instruct_stop` / wired `block_generator`); never invent stronger enforcement; never echo secret values. Preserve `Docs/Master-Plan.md` as lifecycle authority — policy handling must not write story status or tasks.

## Output
*   Save the review report to `Docs/archived/review-[story-id].md` (e.g., `Docs/archived/review-DEV-15.md`). This file is required by `/agtoosa-ship check`. The file must contain the structured findings table with all 🔴 / 🟡 / 🟢 items.
*   Create or update `Docs/archived/evidence-[story-id].md` per `Docs/AgToosa_Evidence.md` (or run `/agtoosa-evidence review`). Populate `phase=review` rows from the story test plan and review findings. This step is required when writing the review report — do not defer it to ship.
*   Present the approval gate:

    ```
    ✅ Review complete — Verdict: [PASS / BLOCKED]
    🔴 Critical: [N]  🟡 Warning: [N]  🟢 Passed: [N]
    [One sentence summarising the biggest finding, or "No critical issues found."]
    → Approve to proceed to /agtoosa-ship  |  Address findings and re-run review
    ```

    If any 🔴 Critical findings remain, the gate shows `BLOCKED`. Do not proceed to `/agtoosa-ship` without explicit user override. Wait for the user's response.

*   **Served by `/agtoosa-next`:** When this review was dispatched by `/agtoosa-next` and verdict is PASS (no unresolved 🔴 Critical), record Review ✅ Approved in Master-Plan and close with `Next: /agtoosa-next — ship [story-id]`. Do **not** invoke `/agtoosa-ship` in the same invocation. When BLOCKED, stop and report findings — Next does not override critical blockers.

*   Print the **dual-line phase close** per `Docs/AgToosa_Agent.md` → **Lifecycle Next-Step Contract** (`Next:` lifecycle command + `SYNC:` pulse). Optional: `/agtoosa-status` for full health findings.

# AgToosa /agtoosa-ship Workflow

## Sub-Commands

| Sub-command | Runs |
|-------------|------|
| `/agtoosa-ship` | Full flow: readiness gate → WIP squash → deploy → archive → changelog → suggest next |
| `/agtoosa-ship check` | Part 0 only — **read-only** readiness audit; reports pass/fail and stops (no deploy, archive, or changelog mutation) |
| `/agtoosa-ship docs` | Docs only — archive completed specs, update changelog and Master-Plan |
| `/agtoosa-ship retro` | Sprint retrospective — what shipped vs. planned, quality trends, keep/stop/start |

## Objective
Deploy the completed feature, clean up the workspace, archive completed work, and suggest the next logical development story.

> **Prerequisites:** `/agtoosa-review` must be approved. Verify that `Docs/archived/review-[story-id].md` exists and contains no unresolved 🔴 Critical findings. If any Critical findings remain, resolve them via `/agtoosa-build` and re-run `/agtoosa-review`.
>
> **Phase-order abort (from `Docs/AgToosa_Governance.md`):** If no `Review ✅ Approved` Update Log entry exists for the story, print exactly `⚠️ Story [ID] has not been approved. Run /agtoosa-review and obtain approval before shipping.` and abort.

## Workflow

**Orchestration Brain step 0:** Before independent check / docs / retro prep lanes that may run in parallel, read `Docs/AgToosa_Orchestration.md` and run Capability Inventory → lane plan → parallel or sequential dispatch → orchestrator merge.

### Part 0 — Ship Readiness Gate (`/agtoosa-ship check` runs this exclusively)

> **`/agtoosa-ship check` contract (read-only):** Execute **Part 0 only**. Read `Docs/Master-Plan.md`, archived spec/review, changelog, and git history as needed. **Do not** deploy, squash WIP commits, archive specs, bump versions, or mutate any file. **Do not** present the full-flow deployment approval gate. Stop after printing the readiness output below.

> **`/agtoosa-ship` full flow:** Run Part 0 first. Only after all checks pass, present the **Deploy approval gate** and wait for explicit user approval before Part 1.

Before any deployment, verify all of the following. If **any** check fails, list each failure on its own line with a **Fix with:** command or **Manual action:** when no AgToosa command applies.

| Check | How to Verify | Fix with (on failure) |
|-------|--------------|----------------------|
| ✅ Goal Contract satisfied | Active spec contains `### Goal Contract` (or `### 1.1 Goal Contract`); Success condition and Proof / evidence are satisfied by tests, review report, smoke result, demo, metric, or shipped artifact | `/agtoosa-build` or `/agtoosa-spec` |
| ✅ Spec was approved | `Docs/archived/spec-*.md` contains a `## ✅ Spec Approved` section with a timestamp | `/agtoosa-spec` |
| ✅ Acceptance criteria exist | `Docs/archived/spec-*.md` contains acceptance criteria with at least one Must-priority row | `/agtoosa-spec` |
| ✅ `/agtoosa-review` completed | `Docs/archived/review-*.md` exists and contains no unresolved 🔴 Critical findings | `/agtoosa-review` |
| ✅ All tests pass | Run full test suite and confirm green | `/agtoosa-build test` |
| ✅ Smoke tests tagged | Test plan or test suite has at least one `@smoke`-tagged test per Must-priority AC | `/agtoosa-spec` or `/agtoosa-build` |
| ✅ Changelog entry drafted | `Docs/AgToosa_Changelog.md` has an entry for this feature | `/agtoosa-ship docs` or manual changelog edit |
| ✅ No `WIP:` commits remain | `git log` shows no commits whose **subject line** starts with `WIP:` | `/agtoosa-ship` (Part 1 squash) or manual squash |
| ✅ QA cleared (when QA phase is enabled) | If `Docs/Context/workflow.md` enables a QA gate **or** a `Docs/AgToosa_QAReport-[story-id].md` exists, that report contains no open 🔴 findings | `/agtoosa-qa run` then `/agtoosa-qa triage` |
| ✅ Verifier green | `bash Docs/agtoosa-verify.sh` exits 0 (no FAIL findings) | Fix the listed findings, then re-run |
| ✅ Release published *(when `deploy_command` is documented in `Docs/Context/tech-stack.md`)* | After version bump: remote deploy verification succeeds per `deploy_verify` in tech-stack (e.g. `gh release view`, CI run URL, or health check) | Run `deploy_command` from tech-stack; re-run ship |
| ℹ️ External agent evidence reviewed *(informational — not a verifier FAIL)* | When IMPORT evidence or tasks returned via `/agtoosa-import` exist: confirm verification commands are recorded, ACs are mapped, and no imported claim is counted as evidence without repo-local verification pass | Run `/agtoosa-build import` or review `Docs/AgToosa_Import.md` |
| ℹ️ Evidence ledger finalized *(required by workflow instructions — not a verifier FAIL)* | `Docs/archived/evidence-[story-id].md` exists and contains `phase=ship` rows (finalize via `/agtoosa-evidence ship` or `Docs/AgToosa_Evidence.md`). **Finalize before marking Shipped.** | Run `/agtoosa-evidence ship` |

**Evidence rules:** Report pass/fail summaries, command names, artifact paths, and test counts. When citing deploy or test logs, **redact** secrets, tokens, API keys, and private URLs before including evidence in chat or review artifacts.

#### Hook lifecycle pointers (`pre-ship`, `secret-check`)

Consult `Docs/AgToosa_Hooks.md` for the single event/platform matrix. Before deploy approval, apply checklist (or proven native) steps for `pre-ship` and `secret-check`. Do not duplicate the matrix here. Optional Hook Automation Pack absence is not a readiness or verifier failure.

#### Readiness failure output (both `check` and full flow)

For each failed row, print:

```
🔴 [Check name] — [brief reason]
   Fix with: `/agtoosa-[command]` — [one-line action]
```

or, when no command applies:

```
🔴 [Check name] — [brief reason]
   Manual action: [what the human must do]
```

Stop after listing all failures. Do not proceed to deployment or file mutation.

#### `/agtoosa-ship check` — success output (read-only stop)

When all checks pass and the user invoked **`check`** only:

```
✅ Readiness audit passed — story [ID] is ready for a full ship (read-only check complete)
Branch: [branch] · Story: [ID] · Goal: ✅ · Smoke tests: [N] tagged · Changelog: ✅

This command does not deploy or mutate project state.
Next: Run full `/agtoosa-ship` when you want deployment approval and release steps.
```

**Stop here.** Do not show the deploy approval gate.

#### Full `/agtoosa-ship` — Part 0 success → Deploy approval gate

When all checks pass and the user invoked the **full** ship flow (no `check` sub-command), present:

```
✅ Ready to deploy — All pre-ship checks passed (Part 0 complete)
Branch: [branch name] · Story: [ID] · Goal: ✅ · Smoke tests: [N] tagged · Changelog: ✅
→ Approve to deploy to [staging/production]  |  Cancel or investigate below
```

Wait for explicit user approval before Part 1 (WIP squash, deploy, archive).

**Served by `/agtoosa-next`:** When full ship was dispatched by `/agtoosa-next` and Part 0 passed, treat the user's Next invocation as deploy approval — proceed to Part 1 without a separate approval turn. If Part 0 has 🔴 Critical findings, stop — Next does not override readiness blockers.

### Part 1 — Pre-Deploy: WIP Commit Squash

Before deploying, clean the branch history using the **non-interactive** squash procedure (interactive rebase is unavailable to most agents):

1.  **WIP Commit Squash:**
    *   Identify all `WIP:` commits on the current branch since branching from main/master: `git log main..HEAD --oneline`
    *   If no `WIP:` commits exist, skip this step.
    *   Create a safety ref first: `git branch backup/pre-squash-[story-id]`
    *   Non-interactive squash: `git reset --soft $(git merge-base main HEAD)` then create clean, atomic, logically grouped commits with explicit `git add [paths]` per group.
    *   Each final commit message must follow Conventional Commits: `[type]([scope]): [description]`
    *   Run the full test suite after squash to confirm nothing broke, then delete the backup ref: `git branch -D backup/pre-squash-[story-id]`
    *   If anything goes wrong mid-squash, restore with `git reset --hard backup/pre-squash-[story-id]` and report — never leave the branch half-squashed.

### Part 2 — Deployment & Rollbacks

2.  **Deployment (Zero-Downtime):**
    *   Read the deploy target and command from `Docs/Context/tech-stack.md` (**Deployment** section). Three cases:
        - **A documented deploy command exists** (e.g. `vercel deploy --prod`, `fly deploy`, `kubectl apply`, `git tag v$VERSION && git push origin v$VERSION`): run it after explicit user approval, capture the Terminal Evidence Contract block, and monitor its health output. When `deploy_verify` is also documented, run it and record the workflow run URL before proceeding.
        - **Deployment is owned by CI/CD on merge:** do not deploy from the agent; verify the pipeline run for this branch/tag succeeds and record the run URL as evidence.
        - **No deploy target is documented:** treat deployment as a `[manual]` step — present what the human must run, record it in Manual / Deferred, and continue with Parts 3+ (never claim a deploy happened without evidence).
    *   **Release publication rule:** When `deploy_command` is documented, do **not** write `Release X shipped` Update Log rows, finalize ship-phase evidence with a passing `release` row, or mark the story `🏁 Shipped` until the tag is pushed and `deploy_verify` (or equivalent remote check) succeeds. If the user has not approved push, stop at Manual / Deferred — do not record a false release.
    *   Monitor post-deployment automated health checks when the stack exposes them.
    *   Trigger automated rollbacks if error rates or latencies spike to ensure zero-downtime. If automated rollback is unavailable, use `/agtoosa-revert` for manual git-aware rollback.

3.  **Post-Deploy Smoke Tests:**
    *   Run all `@smoke`-tagged tests against the deployed environment.
    *   Verify that every Must-priority AC from the spec is reachable in production.
    *   Verify that the Goal Contract Success condition is satisfied by production behavior or the declared Proof / evidence.
    *   Verify the health endpoint returns 200 (if applicable).
    *   **If smoke tests pass:**
        - Update `Docs/Master-Plan.md`: move the Story row from `## Active Cycle` to `## Completed This Cycle`; set status to `Done` or `🏁 Shipped`.
        - Add an **Update Log** entry: `YYYY-MM-DD HH:MM — /agtoosa-ship — Ship 🚀 Deployed — [Story ID] — smoke PASS; spec archived.`

    *   **If any smoke test fails:** halt immediately, do NOT archive specs, trigger `/agtoosa-revert`, set the Story status back to `In Review` in `Docs/Master-Plan.md`, and add an **Update Log** entry: `YYYY-MM-DD HH:MM — /agtoosa-ship — Rollback 🔙 Triggered — [Story ID] — [brief failure]. Next: /agtoosa-build tdd.`
    *   Capture smoke test pass/fail status in the changelog entry.

### Part 3 — Workspace Cleanup & Archiving (`/agtoosa-ship docs` runs Parts 3 + 4)

3.  **Archive Completed Work:** Spec and review artifacts are already saved to `Docs/archived/` (as `spec-[story-id].md` and `review-[story-id].md`). Verify both files exist there before proceeding. Also verify `Docs/archived/evidence-[story-id].md` exists and has `phase=ship` rows; if missing or incomplete, create/finalize it now via `/agtoosa-evidence ship` or `Docs/AgToosa_Evidence.md` before marking Shipped.

3a. **Merge capability deltas (living system spec):** If the story spec contains a `## Capability Delta` section (see `Docs/SPEC-FORMAT.md`), fold each delta into the matching living capability spec under `Docs/specs/system/[capability].md`:
    *   `ADDED` requirements append to the capability spec's requirements table.
    *   `MODIFIED` requirements replace the prior row (cite the story ID in a `Last changed by` column).
    *   `REMOVED` requirements are struck from the table with a tombstone note (`removed by [story-id]`).
    *   Create `Docs/specs/system/[capability].md` from the section template in `Docs/SPEC-FORMAT.md` when it does not exist yet.
    *   This keeps system documentation compounding over time instead of dying in `Docs/archived/`.

#### Version bump (maintainer dogfood)

Before changing version pins or CHANGELOG release headings, apply the **patch-first** bump decision tree (`Docs/adr/ADR-005-release-cadence.md` in the AgToosa generator repo; generated projects follow the same semver rules in `Docs/AgToosa_Governance.md` + ADR-004):

| Story profile | Bump | Example (from 5.2.0) |
|---------------|------|----------------------|
| Fix, Chore, docs-only, estimate **S** | **PATCH** (default) | 5.2.1 |
| Feature **S**, same MINOR train, non-breaking | **PATCH** | 5.2.1 |
| New MINOR train, multi-story batched release | **MINOR** (Z=0) | 0.3.0 |
| Breaking per ADR-004 | **MAJOR** | 6.0.0 |

- Default to **PATCH+1** on the current MINOR — do not bump MINOR for every small story.
- Sync `AGTOOSA_VERSION` (bash + PowerShell), README badge, install `--ref` pins, bats `--version` expectation, and `## [X.Y.Z]` in `Docs/AgToosa_Changelog.md`.
- Set `Docs/Master-Plan.md` **Milestone** to the **next PATCH** on the active MINOR (e.g. `v5.2.1 (next)` after shipping `5.2.0`).

4.  **Changelog Update:** Update `Docs/AgToosa_Changelog.md` with a summary entry: `[date] - [type] - [short description] - [spec reference]`.

5.  **Master-Plan Pruning:** Update `Docs/Master-Plan.md` — keep only the Epic description with a reference to the archived spec; clear completed tasks; move the story row to `## Completed This Cycle`.

### Part 4 — Suggest Next Story

6.  **Next Steps Suggestion:**
    *   Based on the overarching project goals in `Docs/Master-Plan.md`, suggest the next logical Spec/Story for the team to tackle.
    *   Consider: open bugs, pending features, technical debt, and security improvements.

### Part 5 — Sprint Retrospective (`/agtoosa-ship retro`)

Run this after shipping to close the feedback loop on the sprint.
**Delegate to** `Docs/AgToosa_Retro.md` for the full input, artifact schema, proposal, repetition, redaction, and mutation-boundary contract.

7.  **Sprint Review (structured):**
    *   Follow `Docs/AgToosa_Retro.md` Inputs — read only repo-local Master-Plan, changelog, archived spec/review/evidence, test plans, and `Docs/agtoosa-events.jsonl`.
    *   Mark missing optional sources `unavailable`; do not use network or hosted trackers.
    *   Build Planned vs Shipped and Evidence Index for the cycle.

8.  **Quality & Process Health:**
    *   Capture friction signals (coverage trend, 🔴 Critical review findings, phase re-runs) as evidence-linked observations for the retro artifact.
    *   Classify repetition per `Docs/AgToosa_Retro.md` (`repeated-pattern` needs two distinct pointers; otherwise `single-cycle`).

9.  **Keep / Stop / Start:**

    Ask the user these three questions sequentially:
    1. What went well this sprint that we should **keep** doing?
    2. What slowed us down that we should **stop** doing?
    3. What should we **start** trying next sprint?

    Link each answer to an evidence pointer or label it as user judgment.

10. **Retro Output (additive only):**
    *   Create or update **one** idempotent artifact: `Docs/archived/retro-[YYYY-MM-DD].md` with required sections from `Docs/AgToosa_Retro.md` (metadata, Planned vs Shipped, Evidence Index, Keep, Stop, Start, Rejected Overreach, Proposals).
    *   Optional: append a changelog pointer under `## Retrospective — [date]` that **links** to that artifact (pointer only; artifact is canonical).
    *   Record proposals with `proposal_id`, `type`, `summary`, `evidence_pointer`, `status`, `next_command` (and `enforcement_class` for policy). Allowed types: task, spec, amend, policy, specialist, test, workflow.
    *   **Leave targets unchanged** — do not edit Master-Plan, approved specs, policy, Context, tests, or specialists from retro. Present next commands only: `/agtoosa-task`, `/agtoosa-spec`, or `/agtoosa-spec amend`. Acceptance is manual; recording `accepted` does not apply the change.
    *   Append phase event: `{"ts":"[ISO-8601 UTC]","phase":"ship","event":"retro-complete","story":"[cycle-date or story]","by":"AgToosa"}`
    *   Redact credentials, private URLs, and unbounded logs; store `[REDACTED]` summaries and repo-relative pointers.

### Part 6 — Compact Master-Plan.md

Run this step when `Docs/Master-Plan.md` exceeds approximately 200 lines **or** after closing an active cycle. Compaction keeps the shared context document within AI context-window limits.

11. **Archive the Completed Cycle:**
    *   Copy the full `## Active Cycle` table to a new snapshot file: `Docs/archived/cycle-[YYYY-MM-DD].md`.
    *   In `Master-Plan.md`, replace the `## Active Cycle` table body with an empty placeholder row and a reference comment:

        ```
        <!-- Archived to Docs/archived/cycle-[YYYY-MM-DD].md -->
        ```

    *   Remove all `Done` rows from `## Active Tasks` — completed work is tracked in `## Completed This Cycle` and `Docs/archived/`.
    *   If `Master-Plan.md` still exceeds 200 lines after pruning, collapse `## Backlog` to titles only (drop Estimate and Epic columns) until the next `/agtoosa-init zoom-out` refresh.

12. **Rotate the Update Log:** When `## Update Log` exceeds **150 rows**, move all rows older than the current cycle to `Docs/archived/updatelog-[YYYY].md` (append, never overwrite) and leave a pointer comment in their place: `<!-- Older rows: Docs/archived/updatelog-[YYYY].md -->`. The Update Log's "never delete rows" rule means *never lose rows* — rotation to the archive preserves them while keeping Master-Plan inside context-window budgets.

## Output
*   Confirm archiving and changelog updates are successful.
*   Append a phase event to `Docs/agtoosa-events.jsonl`:
    `{"ts":"[ISO-8601 UTC]","phase":"ship","event":"complete","story":"[Story ID]","by":"AgToosa"}`
*   **Post-ship routing (Next-served or sequential):** Run backlog scan per `Docs/AgToosa_Next.md` Step 3.
    *   **Candidate found** → suggest that story; close with `Next: /agtoosa-next — enroll [story-id] from backlog`.
    *   **No candidate** → print `No spec is planned in Master-Plan.` Present up to 3 backlog recommendations OR ask what the next spec should be; close with `Next: /agtoosa-next pick — choose or describe next story`.
*   Print the **dual-line phase close** per `Docs/AgToosa_Agent.md` → **Lifecycle Next-Step Contract** (`Next:` lifecycle command + `SYNC:` pulse). Optional: `/agtoosa-status` for full health findings.
*   Direct `/agtoosa-ship` (not served by Next): ask if the user wants to run `/agtoosa-spec` for the next story.

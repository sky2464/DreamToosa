# AgToosa /agtoosa-status Workflow

## Sub-Commands

| Sub-command | Runs |
|-------------|------|
| `/agtoosa-status` | Full dashboard: Master-Plan parsing → initial readiness → git cross-reference → orphan detection → health score → dashboard |
| `/agtoosa-status plan` | Part 1 only — Master-Plan.md health check |
| `/agtoosa-status readiness` | Part 1.5 only — initial product readiness gates (`Docs/AgToosa_Readiness.md`) |
| `/agtoosa-status git` | Part 2 only — git cross-reference |
| `/agtoosa-status orphans` | Part 3 only — orphan detection |

## Objective

Produce a read-only health dashboard by parsing `Docs/Master-Plan.md`, cross-referencing git history, and detecting orphaned work — then present actionable findings with a composite health score.

> **Maintainer Dogfood Mode:** This repository is the AgToosa **generator** (maintainer dogfood). The dashboard reports health for AgToosa development work tracked in `Docs/Master-Plan.md` — not a generic downstream product install. See `docs/agtoosa-maintainer.md` and `Docs/AgToosa_Agent.md` → **Operating Contexts**.

> **Prerequisites:** None. This command can be run at any time, in any phase.
>
> **🔒 Read-only guarantee:** This command **never** modifies `Docs/Master-Plan.md`, git state, or any file. It only reads and reports. Every finding includes a "Fix with" suggestion pointing to the appropriate AgToosa command.

> **Local script alternative:** For a dependency-light Markdown/HTML state projection without health scoring, run `bash Docs/agtoosa-dashboard.sh` (see `Docs/AgToosa_Dashboard.md`). That renderer does **not** replace this workflow's composite health score, git cross-reference, or fix ranking.

## Workflow

### Part 1 — Master-Plan.md Parsing (`/agtoosa-status plan` runs this exclusively)

1.  **Read** `Docs/Master-Plan.md` in full.

2.  **Parse Project Charter:**
    *   Extract: Product name, Milestone, Active cycle name, **Cycle state**, Cycle capacity, Current phase emoji.
    *   Normalize `Cycle state` to `Active` or `Idle — <reason>`. Only a bounded Project Charter field whose value starts with `Idle` declares intentional idleness; free-form mentions elsewhere do not.
    *   Flag any **placeholder values** still present — patterns: `[name]`, `[url]`, `[YYYY-MM-DD]`, `[e.g.`, `[N]`, `[cycle name]`.
    *   Record each placeholder as a finding: 🟡 Warning — *Fix with:* `/agtoosa-init`.

3.  **Parse Active Cycle table:**
    *   Extract each story row: ID, Title, Type, Estimate, Status pill, Tasks Done counter (`N/M`).
    *   Record each story with status 🟨 In Progress for staleness check in Part 1 step 7.
    *   If the Active Cycle table is empty (only placeholder rows or no data rows) and `Cycle state` is `Idle — <reason>`, record: ℹ️ Info — "Active Cycle is intentionally idle: `<reason>`. Run `/agtoosa-spec` when the next story is scoped." This state has **no Plan Completeness deduction**.
    *   Otherwise, if the Active Cycle table is empty, record: 🟡 Warning — "No active stories. *Fix with:* `/agtoosa-spec`".

4.  **Parse Active Tasks:**
    *   Count total checkboxes (`- [ ]` unchecked + `- [x]` checked). Compute completion percentage.
    *   **Manual task exemption:** Before counting, separate out any sub-task lines containing `[manual]` or `[manual-deferred]`. These are tracked separately and do **not** participate in mismatch detection or health scoring.
    *   For each story in Active Cycle, verify the Tasks Done counter (`N/M`) matches the actual checkbox counts for **automated tasks only**:
        -   `N` should equal the count of `- [x]` checkboxes (excluding `[manual]` and `[manual-deferred]` lines).
        -   `M` should equal the total checkbox count excluding `[manual]` and `[manual-deferred]` lines.
    *   If there is a mismatch on automated tasks, record: 🔴 Error — "Tasks Done counter `[N/M]` does not match actual checkboxes `[actual_done/actual_total]` for `[Story ID]`. *Fix with:* `/agtoosa-build`".
    *   If Active Tasks section is empty but Active Cycle has In Progress stories, record: 🟡 Warning — "Active Cycle has In Progress stories but Active Tasks is empty. *Fix with:* `/agtoosa-spec tasks`".
    *   For any `[manual-deferred]` tasks found, record as: ℹ️ Info — "`[N]` manual task(s) deferred on `[Story ID]`: `[task titles]`. Complete them and run `/agtoosa-build` to mark done."

5.  **Parse Blocked table:**
    *   Extract each row: ID, Title, Blocked by, Since date.
    *   Calculate age in days from the Since date to today.
    *   If age > 7 days, record: 🟡 Warning — "(escalated to Warning on day 7) `[ID]` has been blocked for `[N]` days since `[date]`. *Fix with:* resolve the blocker or `/agtoosa-task` to re-scope."
    *   If age > 30 days, escalate to: 🔴 Error — "(escalated to Error on day 30) `[ID]` has been blocked for `[N]` days — likely abandoned."

6.  **Parse Backlog:**
    *   Count items by Priority: High, Medium, Low.
    *   Record as ℹ️ Info — "Backlog: `[H]` High, `[M]` Medium, `[L]` Low priority items."
    *   If any High-priority items exist and Active Cycle is empty, record: 🟡 Warning — "High-priority backlog items exist but nothing is in Active Cycle. *Fix with:* `/agtoosa-spec`". This warning is retained when `Cycle state` is Idle.
    *   **Idle isolation:** the explicit Idle exemption applies only to the no-active-story finding and deduction; all independent findings remain active, including stale Update Log, high-priority backlog, blocked work, branch drift, and orphaned work.

7.  **Parse Update Log:**
    *   Find the most recent entry by date.
    *   Calculate age in days from the most recent entry to today.
    *   **Manual exemption:** If the only In Progress / Awaiting-Manual stories have all automated tasks done and only `[manual-deferred]` tasks remaining, the staleness threshold is relaxed to 30 days (Warning) / 90 days (Error) — the agent cannot advance these stories until the human acts.
    *   Otherwise, if age > 7 days, record: 🟡 Warning — "(escalated to Warning on day 7) Update Log is stale — last entry `[N]` days ago (`[date]`). *Fix with:* run the next workflow phase."
    *   If age > 30 days, escalate to: 🔴 Error — "(escalated to Error on day 30) Update Log has not been updated in `[N]` days — project may be abandoned."

8.  **Cross-section consistency checks:**
    *   **Orphaned Active Tasks:** For each top-level task group in Active Tasks, extract any referenced story ID. If that ID does not appear in the Active Cycle table, record: 🔴 Error — "Active Task group references `[ID]` which is not in Active Cycle. *Fix with:* `/agtoosa-spec tasks` or `/agtoosa-task`".
    *   **Stuck-Done detection:** For each story in Active Cycle with status ✅ Done, check if it appears in Completed This Cycle. If not, record: 🟡 Warning — "`[ID]` is marked Done in Active Cycle but not in Completed This Cycle. *Fix with:* `/agtoosa-ship docs`".
    *   **Awaiting Manual — not a stuck state:** For each story with status 🔧 Awaiting Manual, do **not** flag it as stuck or stale. Record as ℹ️ Info — "`[ID]` is awaiting `[N]` manual task(s). No action needed from the agent until the user completes those steps."
    *   **Dangling Blocked:** For each ID in the Blocked table, verify it appears in Active Cycle or Backlog. If not, record: 🟡 Warning — "Blocked item `[ID]` is not tracked in Active Cycle or Backlog. *Fix with:* `/agtoosa-task`".

9.  **Tracker unlinked external items (DEV-143):**
    *   Run `bash agtoosa.sh --tracker status-check --path <project-root>` (JSON on stdout). The command performs **local-only** discovery and auto-merges optional caches at `.agtoosa/tracker/gh-issues.json` and `.agtoosa/tracker/linear-fetch.json` when present — **no network calls in lib**.
    *   Parse `finding.emit` from `agtoosa.tracker-status-check/v1`. When `true`, record: ℹ️ Info — "`[N]` unlinked external tracker item(s) (e.g. `[ref1]`, `[ref2]`, … — up to 5 samples). *Fix with:* `/agtoosa-tracker discover` then `bootstrap` to review a proposal; accept rows via `/agtoosa-task` only."
    *   When `finding.emit` is `false`, record nothing (silent skip for greenfield repos or fully linked trackers).
    *   **No Plan Completeness deduction** — this finding is informational only (same contract as intentional idle cycle, DEV-117).

### Part 1.5 — Initial Product Readiness (`/agtoosa-status readiness` runs this exclusively)

Audit the seven gates in `Docs/AgToosa_Readiness.md`. For each failed gate, record a 🟡 Warning (or 🔴 Error if the active story is 🟨 In Progress and the gap blocks build) with the **Fix with** command from that doc.

1.  **Context files populated** — Inspect `Docs/Context/product.md`, `tech-stack.md`, `workflow.md`. Flag placeholder patterns (`[name]`, `[url]`, `[e.g.`, `[N]`, `[YYYY-MM-DD]`). *Fix with:* `/agtoosa-init`.

2.  **Epics present** — `## Epics` must contain at least one non-placeholder Epic. *Fix with:* `/agtoosa-init`.

3.  **Active story has approved spec** — For each 🟨 In Progress or 🟦 Todo row in `## Active Cycle`, require a matching spec file with `## ✅ Spec Approved`. *Fix with:* `/agtoosa-spec`.

4.  **Must ACs mapped to tests** — For the active story's spec, every **Must** `AC-NNN` must appear in `Docs/AgToosa_TestPlan-*.md`. *Fix with:* `/agtoosa-spec tasks` or `/agtoosa-qa plan`.

5.  **Security / threat model present** — Active spec must include threat model content per `Docs/SPEC-FORMAT.md`. *Fix with:* `/agtoosa-spec plan`.

6.  **Task tree and wave plan present** — `## Active Tasks` must have checkboxes for the In Progress story; spec `## 3. Tasks` must include `### Wave Plan`. *Fix with:* `/agtoosa-spec tasks`.

7.  **Release / version parity** — `AGTOOSA_VERSION` in `agtoosa.sh` and `agtoosa.ps1` must match the latest **released** version heading in root `CHANGELOG.md` (ignore leading `v`). Planned milestones in `Docs/Master-Plan.md` may differ if explicitly labeled planned. *Fix with:* align versions manually or `/agtoosa-ship docs`.

Present a compact **Initial Product Readiness** table in the dashboard (gate name · pass/fail · Fix with). On the full dashboard, include this table after Plan Completeness findings and before Git Activity.

**Plan Completeness deductions (readiness):** −5 per failed readiness gate (maximum −35).

### Part 2 — Git Cross-Reference (`/agtoosa-status git` runs this exclusively)

1.  **Recent activity summary:**
    *   Run `git log --oneline -20` to get the last 20 commits.
    *   Display as a summary table with hash, date, and message.

2.  **Unreported progress detection:**
    *   Extract story IDs from recent commit messages (pattern: `DEV-\d+` or project-specific ID prefix).
    *   Cross-reference each extracted ID against the Active Cycle table in `Docs/Master-Plan.md`.
    *   For any commit referencing an ID **not** found in Active Cycle or Backlog, record: 🟡 Warning — "Commit `[hash]` references `[ID]` which is not tracked in Master-Plan.md. *Fix with:* `/agtoosa-task`".
    *   For any commit referencing an In Progress story but whose task checkboxes haven't been updated, record: ℹ️ Info — "Recent commits touch `[ID]` files but Active Tasks checkboxes may be out of date. *Fix with:* `/agtoosa-build`".

3.  **WIP / fixup commit scan:**
    *   Run `git log --oneline --all | grep -E ' (WIP:|fixup!|squash!)'` to find commits whose **subject line** starts with `WIP:`, `fixup!`, or `squash!` (do not use `git log --grep` — it matches those tokens in commit bodies and causes false positives).
    *   For each WIP/fixup commit found, record: 🟡 Warning — "WIP/fixup commit found: `[hash] [message]` on branch `[branch]`. *Fix with:* `/agtoosa-ship` (squash step)".

4.  **Branch divergence:**
    *   If on a feature branch (not `main` or `master`), run `git log --oneline main..HEAD` (or `master..HEAD`) to show divergence.
    *   Report the number of commits ahead of the base branch.
    *   If commits ahead > 0 and no Active Cycle story is In Progress, record: 🟡 Warning — "Feature branch has `[N]` commits ahead of main but no story is In Progress. *Fix with:* `/agtoosa-spec` or `/agtoosa-ship`".

### Part 3 — Orphan Detection (`/agtoosa-status orphans` runs this exclusively)

1.  **Spec file inventory:**
    *   List all spec files matching patterns: `Docs/AgToosa_Spec-*.md`, `Docs/archived/spec-*.md`.
    *   Extract story IDs from each filename.

2.  **Cross-reference spec files against Master-Plan.md:**
    *   Collect all IDs referenced anywhere in `Docs/Master-Plan.md` (Active Cycle, Backlog, Completed This Cycle, Blocked, Epics).
    *   Compare the two sets.

3.  **Flag orphaned specs:**
    *   Spec files on disk whose ID is **not** in any Master-Plan.md section.
    *   Record each as: 🟡 Warning — "Spec file `[filename]` references `[ID]` which is not in Master-Plan.md. *Fix with:* `/agtoosa-task` to add it or delete the orphaned file."

4.  **Flag missing specs:**
    *   Stories in Active Cycle with status 🟨 In Progress or 🟦 Todo that have **no** matching spec file on disk.
    *   Record each as: 🟡 Warning — "Story `[ID]` is `[status]` but has no spec file. *Fix with:* `/agtoosa-spec`".

### Part 4 — Health Score Computation

Compute four category scores, each starting at 100 with deductions applied. Floor each category at 0.

**Plan Completeness (25%):**
*   −5 per placeholder value still in Project Charter
*   −10 if Update Log is stale (last entry > 7 days ago)
*   −10 if Active Cycle is empty (no active stories) **unless** Project Charter `Cycle state` is explicitly `Idle — <reason>`; an explicitly idle cycle has no Plan Completeness deduction for being empty
*   −5 per failed Initial Product Readiness gate (Part 1.5; maximum −35)

**Task Consistency (25%):**
*   −8 per Tasks Done counter mismatch (automated tasks only; `[manual]` and `[manual-deferred]` tasks are excluded)
*   −10 per orphaned Active Task group (references nonexistent story)
*   −10 per Stuck-Done story (Done in Active Cycle but not in Completed)
*   −10 per Dangling Blocked item
*   **No deduction** for unchecked `[manual-deferred]` tasks — they are listed in the dashboard under "Manual / Deferred" and are never counted as a consistency failure.

**Git Hygiene (25%):**
*   −3 per WIP/fixup commit found
*   −5 if feature branch is behind upstream
*   −5 per commit referencing an untracked story ID

**Freshness (25%):**
*   −5 per 7-day period a Blocked item exceeds 7 days (e.g., 21 days blocked = −10)
*   −10 if all Active Cycle stories are ✅ Done and Completed This Cycle does not list all of them (cycle complete but not closed — *Fix with:* `/agtoosa-ship`). Stories with status 🔧 Awaiting Manual are **excluded** from this check — the cycle is not considered closed until manual tasks resolve.
*   −10 if Update Log has no entry in the last 7 days — **unless** all active stories are 🔧 Awaiting Manual (relaxed to 30 days in that case).

**Composite score:** `total = round(0.25 × plan + 0.25 × tasks + 0.25 × git + 0.25 × freshness)`

**Grades:**

| Score | Grade | Emoji |
|-------|-------|-------|
| 90–100 | Excellent | 🟢 |
| 70–89 | Good | 🟡 |
| 50–69 | Needs Attention | 🟠 |
| 0–49 | Critical | 🔴 |

### Part 5 — Dashboard Output

Present the full report using this structure:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 AgToosa Status Dashboard
Project: [name] · Cycle: [cycle] · Phase: [phase emoji]
🔒 Read-only — no files were modified
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Health Score: [NN]/100 [grade emoji] [grade label]

| Category          | Score   | Issues |
|-------------------|---------|--------|
| Plan Completeness | [N]/100 | [n]    |
| Task Consistency  | [N]/100 | [n]    |
| Git Hygiene       | [N]/100 | [n]    |
| Freshness         | [N]/100 | [n]    |

## Active Stories

| ID | Title | Status | Progress |
|----|-------|--------|----------|
| [rows from Active Cycle] |

## Findings

### 🔴 Errors ([N])
- [finding] — *Fix with:* `/agtoosa-[command]`

### 🟡 Warnings ([N])
- [finding] — *Fix with:* `/agtoosa-[command]`

### ℹ️ Info ([N])
- [finding]

## Git Activity (last 20 commits)

| Hash | Date | Message |
|------|------|---------|
| [rows from git log] |

## Orphans ([N] found)
- [orphan description] — *Fix with:* `/agtoosa-[command]`

## Manual / Deferred Tasks

> These tasks require human action and are **not** counted in the health score.
> Complete each step, then run `/agtoosa-build` and select (A) to mark it done.

| Story | Task | Deferred Since | Description |
|-------|------|----------------|-------------|
| [DEV-XX] | 2.3 | [YYYY-MM-DD] | [task title] |

*(None — all manual tasks are complete or none exist.)*

## Recommended Next Actions
1. Run `[command]` to [verb-phrase] ([N] findings: [ID1, ID2, …])
   Rationale: [one short line].
2. …
```

When running a sub-command (`plan`, `readiness`, `git`, or `orphans`), output only the relevant sections of the dashboard. Always include the header and health score sections (readiness-only runs may omit git/orphan sections).

### Part 5.5 — Recommended Next Actions generation

The dashboard MUST emit a deterministic, ranked, deduplicated "Recommended Next Actions" section every run. Do not improvise ordering. Follow this algorithm exactly.

**Step 1 — Map every finding to its fix-command** using this table:

| Finding pattern | Fix command |
|---|---|
| Placeholder values still in Project Charter | `/agtoosa-init` |
| Intentionally idle Active Cycle (Info) | `/agtoosa-spec` |
| Empty Active Cycle; missing spec for In Progress / Todo story; High-priority backlog with empty Active Cycle; branch ahead with no In Progress story | `/agtoosa-spec` |
| Empty Active Tasks while Active Cycle has In Progress; Orphaned Active Task group references unknown story ID | `/agtoosa-spec tasks` |
| Tasks Done counter mismatch; stale checkboxes referenced by recent commits | `/agtoosa-build` |
| Blocked item > 7d (Warning) or > 30d (Error); Dangling Blocked ID not in Active Cycle/Backlog; Commit references untracked story ID; Orphaned spec file not referenced in Master-Plan | `/agtoosa-task` |
| WIP / fixup / squash commits; Stuck-Done story (Done in Active Cycle but not in Completed) | `/agtoosa-ship` |
| Unlinked external tracker items (`status-check` `finding.emit` true) | `/agtoosa-tracker discover` (then `bootstrap`) |
| Failed Initial Product Readiness gate (context, epics, approved spec, Must AC tests, threat model, task tree/wave, version parity) | See gate row in `Docs/AgToosa_Readiness.md` — typically `/agtoosa-init`, `/agtoosa-spec`, `/agtoosa-spec tasks`, `/agtoosa-spec plan`, or `/agtoosa-qa plan` |

**Step 2 — Sort findings by priority:**

1. 🔴 Errors (regardless of source).
2. 🟡 Aged Warnings, oldest `since` date first. A warning is "aged" if it has the `(escalated to Warning on day N)` prefix.
3. 🟡 Other Warnings.
4. Orphan findings (from Part 3).
5. ℹ️ Info.

Within each tier, preserve the order findings were discovered (Part 1 → Part 2 → Part 3).

**Step 3 — Group by fix-command.** After sorting, walk the list and group consecutive findings that share the same fix-command into a single action. A later finding with the same command but separated by a different-command finding still belongs to its earlier group — coalesce all findings per command across the whole sorted list. The action's tier is the tier of the highest-priority finding in the group.

**Step 4 — Emit each action** in priority order (highest-tier group first; ties broken by first-discovery order):

```
N. Run `<command>` to <verb-phrase> (<count> findings: <ID1, ID2, …>)
   Rationale: <one short sentence>.
```

Use these verb-phrases verbatim:

- `/agtoosa-init` → "clear charter placeholders"
- `/agtoosa-spec` → "address missing or unscoped specs"
- `/agtoosa-spec tasks` → "rebuild the Active Tasks checkbox tree"
- `/agtoosa-build` → "reconcile task counters and stale checkboxes"
- `/agtoosa-task` → "resolve blocked, dangling, untracked, or orphan items"
- `/agtoosa-ship` → "clean up WIP commits and stuck-Done stories"
- `/agtoosa-tracker discover` → "review unlinked external tracker items via bootstrap proposal"
- `/agtoosa-qa plan` → "map Must ACs to test IDs in the test plan"

Rationale lines:

- Errors group: "errors block downstream commands and skew progress reporting."
- Aged-Warnings group: "aged warnings risk auto-escalation to Errors at day 30."
- Other-Warnings group: "warnings degrade Freshness and Task Consistency scores."
- Orphan group: "orphans break the spec ↔ Master-Plan source-of-truth contract."
- Info group: "informational — address opportunistically."

**Step 5 — Cap at 5 actions.** If more groups exist, emit the top 5 and append a 6th line:

```
(<N> more findings — run `/agtoosa-status plan` for the full list)
```

**Step 6 — Quick wins call-out.** After the numbered list, emit a `🎯 Quick wins` block listing finding IDs that match this hard-coded heuristic (each takes <5 min to fix):

- Project Charter placeholders.
- Tasks Done counter mismatches.
- Missing spec for the currently-In Progress story (single ID).

Format:

```
🎯 Quick wins: <ID1>, <ID2>, … (estimated <5 min each)
```

If no findings match, omit the block entirely.

**Step 7 — Empty state.** If there are zero Errors, Warnings, Orphans, and Info findings, replace the entire Next Actions section with:

```
## Recommended Next Actions
✅ No findings. Run `/agtoosa-spec` to start the next story, or `/agtoosa-ship` if a cycle is complete.
```

### Part 5.6 — Sub-command typo helper

When invoked as `/agtoosa-status <token>` and `<token>` is not in the set `{plan, readiness, git, orphans}`, prepend exactly this line to the dashboard output before any other content:

```
Note: '<token>' is not a defined sub-command. Did you mean: plan, readiness, git, orphans? Falling back to full dashboard.
```

Then run the full dashboard as usual. This replaces any generic "unknown sub-command" fallback wording.

## Rules

1.  **Read-only.** Never modify `Docs/Master-Plan.md`, git state, or any other file. If tempted to fix something, report it as a finding instead.
2.  **Zero questions.** Run immediately and produce output. Do not ask the user anything.
3.  **Actionable findings.** Every 🔴 Error and 🟡 Warning must include a "Fix with" suggestion pointing to an existing AgToosa command.
4.  **Placeholder awareness.** Master-Plan.md ships as a template with placeholder values (`[DEV-XX]`, `[YYYY-MM-DD]`, `[name]`, etc.). Detect these and report them — do not treat them as real data.
5.  **Graceful degradation.** If a section is empty or missing, note it and continue. Do not fail the entire dashboard because one section is unpopulated.
6.  **Git safety.** Only run read-only git commands (`git log`, `git branch`, `git diff --stat`, `git rev-parse`). Never run `git checkout`, `git reset`, `git push`, or any command that modifies state.

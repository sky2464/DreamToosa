# AgToosa /agtoosa-revert Workflow

## Objective
Safely rollback to a previous state of the project based on logical units of work (Tracks, Phases, or Tasks) rather than simple git commit hashes.

## Workflow

1.  **Logical Unit Identification:**
    *   The agent identifies the specific Phase (e.g., `/agtoosa-build`, `/agtoosa-review`) or Task (e.g., "Implement User Authentication") the user wishes to revert.
    *   Map the logical unit to concrete commits using the Update Log in `Docs/Master-Plan.md` (phase timestamps), `WIP: [task-id]` commit subjects, and `git log --grep "[story-id]"`. Present the resolved commit range to the user **before** touching anything:

        ```
        🔙 Revert plan — [logical unit]
        Commits: [oldest-sha]..[newest-sha] ([N] commits)
        Strategy: [revert (history-preserving) | reset (history-rewriting)]
        → A) Proceed   B) Adjust range   C) Cancel
        ```

2.  **Mandatory Safety Net (before any reversal):**
    *   Create a backup branch: `git branch backup/revert-[story-id]-[YYYYMMDD]`
    *   If the working tree is dirty, stash with a label: `git stash push -m "pre-revert [story-id]"`
    *   Never skip this step — reverts without a backup ref are forbidden.

3.  **Git-Aware State Reversal:**
    *   **Default strategy is `git revert` (history-preserving):** `git revert --no-edit [newest]..[oldest]` for the resolved range, so the rollback itself is an auditable commit.
    *   `git reset` is allowed **only** on unpushed local history. `git reset --hard` additionally requires explicit user confirmation in this session after showing exactly which commits and working-tree changes will be discarded.
    *   Undo only the commits in the resolved range, minimizing impact on parallel tracks.
    *   Run the test suite at the reverted state and report the result via the Terminal Evidence Contract.

4.  **Context & Plan Synchronization:**
    *   After reverting the code, update `Docs/Master-Plan.md` (story status, Active Tasks checkboxes) and the relevant `Docs/archived/spec-[story-id].md` task tree to reflect the reverted state.
    *   Add an **Update Log** entry: `YYYY-MM-DD HH:MM — /agtoosa-revert — Reverted [logical unit] — backup: backup/revert-[story-id]-[YYYYMMDD].`
    *   Ensures that the AI PM context is in perfect sync with the source code.

## Output
*   Confirm the code and context have been successfully reverted, citing the backup branch name.
*   Present the current clean state to the user and ask for next steps.
*   Remind the user the backup branch can be deleted once they're satisfied: `git branch -D backup/revert-[story-id]-[YYYYMMDD]`.

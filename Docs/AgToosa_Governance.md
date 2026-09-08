# AgToosa Governance: Phase-Gate Protocol & Master-Plan.md Workflow

> **Reference doc.** Read this to understand how AgToosa enforces phase order, what gets written to `Docs/Master-Plan.md`, and the exact Update Log strings to write at each phase event.

## Phase-Gate Overview

| Phase | Entry Command | Gate Condition | Master-Plan.md Update |
|-------|--------------|----------------|-----------------------|
| Backlog → Todo | `/agtoosa-spec` | Spec approved by user | Story added to Active Cycle table; status → `Todo` |
| Todo → In Progress | `/agtoosa-build` | Story exists in Master-Plan.md with a spec | Active Cycle row updated; status → `In Progress` |
| In Progress → In Review | `/agtoosa-review` | Story status is `In Progress` | Active Cycle row updated; status → `In Review` |
| In Review → Done | `/agtoosa-ship` | `Review ✅ Approved` Update Log entry exists | Story moved to Completed This Cycle; status → `Done` |
| Done ← rollback | `/agtoosa-revert` | Any state | Update Log entry added |

## Phase-Order Rules

Invoke commands in the order above. Out-of-order invocations warn and abort:

- Running `/agtoosa-review` when story is still `Todo` (not yet `In Progress`): warn and abort.
  Print: `⚠️ Story [ID] is in 'Todo' state. Run /agtoosa-build first.`

- Running `/agtoosa-ship` when story is `In Review` but no `Review ✅ Approved` Update Log entry exists: warn and abort.
  Print: `⚠️ Story [ID] has not been approved. Run /agtoosa-review and obtain approval before shipping.`

- Running `/agtoosa-build` when no spec exists for the story in Master-Plan.md: warn and prompt.
  Print: `⚠️ No spec found for [ID]. Run /agtoosa-spec first.`

## Master-Plan.md Update Log Protocol

Write these exact strings as timestamped entries in `Docs/Master-Plan.md` `## Update Log` at the corresponding phase events:

| Event | Update Log entry |
|-------|-----------------|
| Spec approved | `Spec ✅ Approved` |
| Build begins | `Build 🏗️ Started` |
| Each task completes during build | `Task 🟢 N/M complete` |
| Review begins | `Review 🔍 Started` |
| Review passes | `Review ✅ Approved` |
| Review blocked | `Review 🔴 Blocked: <reason>` |
| Deployment complete | `Ship 🚀 Deployed to <env>` |
| Rollback triggered | `Rollback 🔙 Triggered: <reason>` |

Replace `<reason>`, `<env>`, and `N/M` with the actual values at runtime.

## Master-Plan.md Update Rules

Every AgToosa command must read and write Master-Plan.md as follows:

1. Read Master-Plan.md at the start of every command run.
2. Write a timestamped entry to the `## Update Log` section at the end of every command run. Format: `YYYY-MM-DD HH:MM — [command] — [summary of action taken]`.
3. Keep the Active Cycle table current. When status changes, update the row immediately.
4. When a story reaches `Done`, move its row from the Active Cycle table to the `## Completed This Cycle` section.

## Policy violation contract

Consult `Docs/AgToosa_GovernancePolicy.md` (checker: `Docs/agtoosa-policy-check.sh`) before actions covered by a declared rule. On a policy violation: identify the rule `id`, `enforcement_class`, and `on_violation`; follow that `on_violation` only (`warn` / `instruct_stop` / wired `block_generator`); never invent stronger enforcement; never echo secret values. Preserve `Docs/Master-Plan.md` as lifecycle authority — policy handling must not write story status or tasks outside the normal AgToosa commands.

## Breaking Change & Deprecation Policy

Breaking changes must have a one-minor-release deprecation notice before removal. Announce the deprecation in a minor release with a runtime warning; remove in the next minor or major release. See `CONTRIBUTING.md` for the full deprecation procedure and timeline example.

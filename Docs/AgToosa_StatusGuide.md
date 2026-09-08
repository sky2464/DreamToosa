# AgToosa /agtoosa-status-guide Workflow

## Purpose

Use Status Guide when the user wants help deciding what to do after `/agtoosa-status`.

Status Guide combines two personas:

- **Auditor**: runs the normal `/agtoosa-status` dashboard as a read-only audit.
- **Coach**: explains the highest-ranked Recommended Next Actions and asks the user to authorize any fix command before running it.

## Read-Only Guarantee

The audit phase is read-only. Do not modify files, update `Docs/Master-Plan.md`, stage changes, commit, push, delete branches, or run any AgToosa fix command while collecting status.

Allowed during the audit phase:

- Read `Docs/AgToosa_Status.md`, `Docs/Master-Plan.md`, specs, context files, and git history.
- Run read-only status checks required by `Docs/AgToosa_Status.md`.
- Compile the dashboard, health score, findings, and Recommended Next Actions.

Forbidden during the audit phase:

- Editing project files.
- Running `/agtoosa-init`, `/agtoosa-spec`, `/agtoosa-build`, `/agtoosa-task`, `/agtoosa-ship`, or any other workflow that mutates state.
- Running destructive git commands.

## Workflow

1. Read `Docs/AgToosa_Status.md`.
2. Run `/agtoosa-status` full dashboard exactly as specified.
3. Apply `AgToosa_Status.md` Part 5.5 — Recommended Next Actions generation without changing its priority order, grouping, cap, verb phrases, or rationale lines.
4. Present up to the top three actions from the generated Recommended Next Actions section.
5. For each action, include:
   - Fix command.
   - Finding count and finding IDs.
   - The verb phrase from Part 5.5.
   - The rationale line from Part 5.5.
6. Ask for explicit user authorization before running any fix command.
7. If the user authorizes one command, run only that command's documented workflow.
8. If the user declines, do not run the declined command. Offer the next ranked action, or stop if no actions remain.
9. After an authorized command completes, print the command's normal closure line if that workflow defines one, then suggest `/agtoosa-status` to verify.

## Authorization Gate

Before running a fix command, ask:

```text
Authorize running `<command>` for findings <ID list>? Reply yes to run it, or no to skip.
```

Only a clear affirmative answer authorizes execution. If the user gives an unclear answer, ask again. Do not infer authorization from silence, frustration, or a general request for help.

## Output Shape

```text
## Status Guide

Health score: <score>

Top Recommended Next Actions
1. Run `<command>` to <verb-phrase> (<count> findings: <ID1, ID2>)
   Rationale: <Part 5.5 rationale line>
2. ...

Next authorization
Authorize running `<command>` for findings <ID list>? Reply yes to run it, or no to skip.
```

If there are no findings, report the empty state from `AgToosa_Status.md` and do not ask for authorization.

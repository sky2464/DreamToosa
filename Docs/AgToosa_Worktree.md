# AgToosa Optional Worktree Isolation

Optional Git worktree guidance for higher-risk, multi-lane stories that already declare DEV-045 Work Packages. Worktree creation, branch selection, integration, and cleanup remain **manual**. AgToosa does not run `git worktree` for you and does not promise isolated lanes.

> **Prerequisite:** Consume `package_id` and `merge_order` from the active spec `### 3.4 Work Package DAG`. Do not invent a second lane schema.
>
> **Routing reference (read-only):** Consult `Docs/AgToosa_AgentCapability.md` for installed-surface routing recommendations. Do not edit `AgToosa_AgentCapability.md` for worktree work.

## When to use / when to skip

| Decision | Criteria | Enforcement |
|----------|----------|-------------|
| **Use** | Estimate **M+** work with **at least two parallel packages**, or an **explicitly risky** / higher-risk lane where concurrent agents could overwrite uncommitted state | agent-instructed |
| **Skip** | **XS/S** single-lane work, or one package / sequential-only waves where ceremony outweighs benefit | agent-instructed |

Worktrees are **optional**. They are never mandatory for every story.

### WorktreeDecision (agent-instructed)

Record: `{ package_ids, use_or_skip, reason, fallback }`

## Preferred paths

| Choice | Path pattern | Rule |
|--------|--------------|------|
| **Default** | `../<repo>-<package_id>` | Sibling checkout outside the primary tree (example: `../AgToosa-PKG-1.1`) |
| **Alternative** | `.worktrees/<package_id>` | Allowed only after an ignore rule (e.g. `.gitignore` entry for `.worktrees/`) is present |

Before any lane work, confirm paths with `git worktree list` (and `git worktree list --porcelain` when recording evidence).

## Safe Git command flows (manual)

All of the following are **manual**. The agent may print the checklist; the user (or an explicitly authorized operator) runs the commands in the correct checkout.

### Add

```bash
# From the primary checkout — preferred sibling path
git worktree add -b lane/<package_id> ../<repo>-<package_id> <base-ref>
```

### List / verify

```bash
git worktree list
git worktree list --porcelain
git -C "../<repo>-<package_id>" status --short --branch
```

Confirm each lane is on the expected branch and starts from a clean working tree before package work.

### Remove / prune (cleanup — after accepted integration only)

```bash
git worktree remove ../<repo>-<package_id>
git worktree prune
```

Do **not** remove or prune until Import has accepted results and branches are integrated in `merge_order`.

## Security and safety

- **No automatic copying** of `.env`, credentials, tokens, or other untracked secrets into a worktree. Paths only — never paste secret values into handoff packs or evidence.
- Derive suggested paths and branches from known `package_id` values; display `git worktree list` before work begins.
- Keep Git mutations **manual**; retain existing dangerous-Git guardrails where available.
- Stale worktrees consume disk — run documented remove/prune after integration.

## Sequential fallback (when skipping worktrees)

State exactly:

No worktree: run packages sequentially in one branch and verify a clean working tree between packages.

## Handoff: optional Worktree Hint

When `/agtoosa-handoff wave` exports parallel DEV-045 packages and isolation is selected, the pack may include an optional **Worktree Hint** mapping each `package_id` → `suggested_path` + `suggested_branch`. The hint **does not create** paths or branches and performs **no Git mutation**. See `Docs/AgToosa_Handoff.md`.

### WorktreeHint

`{ package_id, suggested_path, suggested_branch }`

## Import: per-branch checks and ordered cleanup

When integrating worktree results via `/agtoosa-import`:

1. For each branch: **clean-status** check and the package's exact **`verification`** command.
2. Present accepted branches in DEV-045 **`merge_order`** before any lifecycle checkbox or Master-Plan status mutation.
3. Defer worktree **cleanup** until accepted results are integrated — then `git worktree remove` / `git worktree prune`.

See `Docs/AgToosa_Import.md`. Build decision gate: `Docs/AgToosa_Build.md`.

### WorktreeIntegrationCheck

`{ package_id, branch, clean_status, verification, merge_order, cleanup_status }`

## Claim Boundary

| Control | Classification |
|---------|----------------|
| Installing `Docs/AgToosa_Worktree.md` through generator inventory | generator-enforced |
| Focused Worktree contract tests (`WT-*`) when run in CI | CI-enforced |
| Recommendation, setup checklist, branch checks, and fallback selection | agent-instructed |
| Running Git commands and approving integration/cleanup | manual |
| Auto-provisioned worktrees and runtime lane isolation | roadmap |

AgToosa does **not** create worktrees, schedule branches, or promise isolated lanes. There is no `/agtoosa-worktree` command — this guide is discoverable documentation only.

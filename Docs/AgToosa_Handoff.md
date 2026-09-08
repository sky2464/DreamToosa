# AgToosa /agtoosa-handoff Workflow

## Sub-Commands

| Sub-command | Runs |
|-------------|------|
| `/agtoosa-handoff` | Full flow: build a handoff pack for the active story or selected wave |
| `/agtoosa-handoff wave` | Export only the current Wave Plan wave (from the active spec) |
| `/agtoosa-handoff task` | Export a single Active Tasks row (by ID or title fragment) |

## Objective

Export an **AgToosa-ready handoff pack** — a bounded work brief for Codex, Copilot cloud agent, Jules, Devin, Cursor background agents, or Claude Code — so an async/external agent can execute a wave or task with enough context and a clear return contract.

> **Prerequisites:** An approved active spec (`## ✅ Spec Approved`) and tasks under `Docs/Master-Plan.md` → `## Active Tasks`. If missing, **stop** and instruct the user to run `/agtoosa-spec` (or `/agtoosa-spec tasks`). Do **not** auto-run those commands.
>
> **Claim Boundary:** This workflow is **agent-instructed**. Writing the pack file is instructed; launching an external agent is **manual**. Importing results is `/agtoosa-import` (DEV-048). AgToosa does **not** claim external agents completed work unless imported evidence is present.
>
> **Source of truth:** `Docs/Master-Plan.md` remains the repo-local source of truth. External agents are integrations, not authorities.

## Pack Template

Write the pack to `Docs/archived/handoff-[story-id]-[YYYYMMDD-HHMM].md` (create `Docs/archived/` if missing). Use this structure verbatim:

```markdown
# Handoff Pack — [Story ID] — [wave or task label]

> **Story:** [ID] — [title]
> **Exported:** [YYYY-MM-DD HH:MM]
> **Target agent:** [Codex | Copilot | Jules | Devin | Cursor | Claude Code | other]
> **Claim Boundary:** agent-instructed export; manual launch; import via /agtoosa-import

## 1. Story & Goal
[Paste Goal Contract rows: Goal, User outcome, Success condition, Non-goals]

## 2. Acceptance Criteria
[Paste Must (and relevant Should) AC-NNN rows from the active spec]

## 3. Files in Scope
[From spec ### 2.4 Build Scope — owned files / directories only]

## 4. Allowed Actions
- Edit only files listed in §3
- Run verification commands in §5
- Do **not** modify `Docs/Master-Plan.md` Active Cycle status without import review
- Do **not** claim ship or mark tasks complete — return evidence for `/agtoosa-import`

## 5. Verification Commands
```bash
[commands from the story test plan smoke set / wave]
```

## 6. Return Contract
Return artifacts that `/agtoosa-import` can map to tasks and ACs:
- Branch name and/or PR URL (if any)
- Commit range or patch summary
- Test log excerpt (command + exit code)
- Changed file list
- Terminal Evidence Contract fields (see `Docs/AgToosa_Agent.md`)
- Mapped ACs: AC-NNN → evidence pointer

## 7. Out of Scope
[From spec §1.3 / Non-goals]

## 8. Work Packages
Selected-wave package rows only (from active spec `### 3.4 Work Package DAG`). Omit packages from unselected waves.

| package_id | wave | depends_on | owned_files | inputs | outputs | merge_order | verification |
|------------|------|------------|-------------|--------|---------|-------------|--------------|
| PKG-[N.M] | [N] | [deps or —] | [paths] | [inputs] | [outputs] | [order] | [command] |

## 8b. Worktree Hint (optional)
When parallel packages use optional isolation — suggested only; does not create paths or branches.

| package_id | suggested_path | suggested_branch |
|------------|----------------|------------------|
| PKG-[N.M] | ../<repo>-PKG-[N.M] | lane/PKG-[N.M] |

## 9. Applicable Policy
Resolved source and rule metadata from `Docs/AgToosa_GovernancePolicy.md` via `bash Docs/agtoosa-policy-check.sh` — copy only; **does not mutate** policy or Master-Plan lifecycle state.

- `policy_path=[.agtoosa/policy.yaml | Docs/Context/agtoosa-policy.yaml | none]`
- If `policy_path=none`: state exactly `no extra policy configured`
- If present: list applicable rule `id`, `description`, `enforcement_class`, `on_violation` (never secret values)
```

## Workflow

1. **Resolve target** — Active Cycle story; if multiple In Progress, ask which ID. For `wave` / `task`, resolve against the active spec Wave Plan or Active Tasks.
2. **Recommend target agent** — Consult `Docs/AgToosa_AgentCapability.md` (Installed-Surface Detection + Routing Recommendation Algorithm). Prefer an **installed** surface for handoff; document the chosen row and **fallback** when the preferred surface is absent. Record the recommendation in the pack `Target agent` field.
3. **Assemble pack** — Fill every section from the approved spec, Master-Plan Active Tasks, and test plan. Prefer inference; ask at most one clarifying question (target agent) if unknown after the matrix recommendation.
   - For `/agtoosa-handoff wave`, include **§8 Work Packages** with only the **selected-wave** rows (`package_id`, `owned_files`, `inputs`, `outputs`, `merge_order`, `verification`, plus `depends_on` / `wave` for context). Do not export packages from unselected waves.
   - **Optional Worktree Hint (agent-instructed):** IF the selected wave has parallel DEV-045 packages and isolation is selected, append a Worktree Hint table mapping each known `package_id` → `suggested_path` (default `../<repo>-<package_id>`) and `suggested_branch`. The hint is optional, package-scoped, and **read-only** — it **does not create** paths or branches and performs **no Git mutation**. Full checklist: `Docs/AgToosa_Worktree.md`. When skipping isolation, state exactly: `No worktree: run packages sequentially in one branch and verify a clean working tree between packages.`
   - Include **§9 Applicable Policy**: resolve via `Docs/agtoosa-policy-check.sh`; embed `policy_path` and rule metadata or `no extra policy configured`. Handoff **does not mutate** policy files or Master-Plan status.
4. **Write file** — Create `Docs/archived/handoff-…md`. Do not overwrite prior packs.
   - **Optional capsule pack (DEV-123):** After the handoff file exists, agents **may** emit a guarded execution capsule for bounded async execution:
     `bash Docs/agtoosa-capsule-pack.sh --story <id> [--handoff Docs/archived/handoff-<id>-<stamp>.md] --output Docs/archived/capsule-<id>.json`
     See `Docs/AgToosa_Guarded_Portable_Execution.md`. Default policy is **network deny** (documented only — the pack script performs no network I/O).
5. **Phase event** — Append to `Docs/agtoosa-events.jsonl`:
   `{"ts":"[ISO-8601 UTC]","phase":"handoff","event":"export","story":"[Story ID]","by":"AgToosa"}`
6. **Update Log** — Append a row to `Docs/Master-Plan.md` → `## Update Log` noting the pack path.
7. **Print next step** — Tell the user to launch the external agent **manually**, then run `/agtoosa-import` when results return.

## Platform Notes

> Lifecycle routing (which installed host to recommend) lives in `Docs/AgToosa_AgentCapability.md` — use it to recommend a target and document fallbacks. The table below is pack-usage only.

| Surface | How to use the pack |
|---------|---------------------|
| Cursor / Claude Code | Paste pack path or contents into a new agent/chat; keep Master-Plan as SoT |
| Codex / Copilot / Jules / Devin | Attach or paste the pack markdown; run verification commands in the target repo clone |
| All | Return evidence per §6; do not tick Master-Plan checkboxes until `/agtoosa-import` |

## Output

* Print the pack path and a one-line summary of story + wave/task.
* Print the dual-line phase close per Docs/AgToosa_Agent.md → Lifecycle Next-Step Contract
* Remind: launch is **manual**; closure requires `/agtoosa-import`.

## Rules

1. **Read-mostly.** May write the handoff file, one events line, and one Update Log row — nothing else.
2. **No auto-launch.** Never start external cloud agents or claim they finished.
3. **No checkbox ticks.** Task completion stays with `/agtoosa-build` after `/agtoosa-import`.
4. **Honest claims.** Never describe handoff as generator-enforced or CI-enforced.
5. **Secret safety.** Cite file paths and process steps only — never paste tokens, API keys, passwords, or private URLs into the pack. Sanitize `story-id` to `[A-Za-z0-9._-]+` (no `/` or `..`) before writing the pack filename.

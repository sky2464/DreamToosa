# AgToosa Orchestration Brain

## Objective

Provide one **agent-instructed** algorithm that lifecycle commands consult **before fan-out**: inventory available surfaces → invent parallel lanes → merge evidence → sequential fallback when the host cannot delegate safely.

> **Distinction:** This doc is the **fan-out brain**. Platform routing detail lives in `Docs/AgToosa_AgentCapability.md`. Specialist contracts live in `Docs/AgToosa_Specialists.md`. Project skills live in `Docs/AgToosa_Skills.md`. Work Package ownership lives in the active spec `### 3.4 Work Package DAG` and `Docs/AgToosa_Build.md`. **Do not duplicate** those tables here — call them from step 0.
>
> **Source of truth:** `Docs/Master-Plan.md` remains the repo-local source of truth. External agents and dashboards are evidence sources only.
>
> **Claim Boundary:** Capability inventory + lane planning + routing = **agent-instructed**. Installing this doc via `agtoosa.sh --update` = **generator-enforced**. Focused ORB bats in CI = **CI-enforced** when configured. Selecting which host Task/Agent tool to use = **manual**. **Runtime auto-launch, hosted orchestrator, and process supervisor** = **roadmap / out of scope** — AgToosa does not ship a swarm runtime (Rev4 “Do Not Build Yet”; ADR-003).

## When to run

Run **Orchestration Brain step 0** at the start of fan-out preparation in:

| Command | When |
|---------|------|
| `/agtoosa-spec` | Before Part 1 specialist orchestration and parallel research lanes |
| `/agtoosa-build` | Before Wave / Work Package fan-out |
| `/agtoosa-review` | Before virtual personas, review specialists, and cross-model lanes |
| `/agtoosa-ship` | Before independent check / docs / retro prep lanes when they can run in parallel |
| `/agtoosa-qa` | Before AC-cluster plan/run lanes (Should) |
| `/agtoosa-task`, tracker sync | Read-only status lanes only; **Master-Plan mutations stay serial** |

## Step 0 — Capability Inventory

Build a **read-only** inventory before inventing lanes:

| Source | What to detect | Canonical reference |
|--------|----------------|---------------------|
| **Platforms** | Installed agent surfaces from sentinels | `Docs/AgToosa_AgentCapability.md` → Installed-Surface Detection |
| **Specialists** | Approved roster + `phase_hooks` + trigger match | `Docs/Context/specialists.md`, `Docs/AgToosa_Specialists.md` |
| **Project skills** | `.codex/skills/`, `.claude/skills/`, etc. — invoke when trigger matches; never invent `agtoosa-*` | `Docs/AgToosa_Skills.md` |
| **MCP needs** | Specialist `tools/MCP needs` + host-available MCP server **names only** (user approves scope) | `Docs/AgToosa_Specialists.md` |
| **Host plugins / tools** | Detectable markers only (e.g. Cursor Task tool, Claude Agent tool) — **no remote API probing** | `Docs/AgToosa_AgentCapability.md` |
| **Work packages** | Active spec `### 3.4 Work Package DAG` rows when present | `Docs/SPEC-FORMAT.md`, `Docs/AgToosa_Build.md` |

Reject lanes that use reserved `agtoosa-*` ids/triggers for project specialists or skills.

## Step 1 — Lane plan algorithm

1. **Phase** — Identify current lifecycle phase (`spec` | `build` | `qa` | `review` | `ship` | `sync`).
2. **Filter** — From the inventory, select lanes whose phase hook and trigger match the active story.
3. **Parallel gate** — Consult `Docs/AgToosa_AgentCapability.md` for native parallel delegation on the current host.
4. **Ownership gate** — For build waves, confirm same-wave `owned_files` are **disjoint** per DEV-045. On overlap, do **not** present packages as parallel-safe — use explicit **sequential fallback** in merge order.
5. **Dispatch** — Fan out matching lanes in parallel when both gates pass; otherwise run sequentially.
6. **Merge** — Orchestrator merges Terminal Evidence (and specialist evidence blocks when applicable) before phase artifacts finalize.

### Sequential fallback note (exact)

When parallel delegation is unavailable or unsafe, print:

```
Capability lanes ran sequentially (platform does not support parallel subagents).
```

## Step 2 — Default lane catalogs (by phase)

| Phase | Example parallel lanes | Merge owner |
|-------|------------------------|-------------|
| `/agtoosa-spec` | Context/code scan, web research, matching specialists, threat-model prep, domain-language, skill opportunity scan | Spec orchestrator → Goal Contract / ACs / Design |
| `/agtoosa-build` | Wave packages with disjoint `owned_files`; optional build-hook specialists; optional drift assess + context compile (DEV-122); optional capsule pack for async lanes (DEV-123) | Orchestrator; `/agtoosa-import` if async |
| `/agtoosa-qa` | Plan/run lanes per AC clusters when host allows | QA orchestrator |
| `/agtoosa-review` | Virtual personas + review specialists + optional cross-model | Review verdict gate |
| `/agtoosa-ship` | Independent check / docs / retro prep | Ship gate |
| Sync / task | Read-only status lanes only | Orchestrator (serial Master-Plan writes) |

## Step 3 — Merge rules (non-negotiable)

1. **Terminal Evidence** — Every lane returns the block from `Docs/AgToosa_Agent.md` → Terminal Evidence Contract.
2. **Specialist evidence** — Review/spec specialists return the structured block from `Docs/AgToosa_Specialists.md`.
3. **Master-Plan serial mutation** — Only the **orchestrator** edits `Docs/Master-Plan.md` status and task checkboxes after merge.
4. **Import gate** — External/async agents never close tasks without `/agtoosa-import` and repo-local verification.
5. **Source of truth** — `Docs/Master-Plan.md` remains repo-local SoT; external dashboards are evidence sources only.

## Work Package fan-out (build)

Before parallel build fan-out:

- Read each selected package row from `### 3.4 Work Package DAG`.
- Confirm `depends_on` packages exist, completed, and have **earlier waves**.
- Confirm same-wave `owned_files` are disjoint; else sequential fallback.
- Run each package `verification` command; integrate in `merge_order`.
- Async lanes: export `/agtoosa-handoff` pack; returns via `/agtoosa-import`.

Detail: `Docs/AgToosa_Build.md`, `Docs/AgToosa_Handoff.md`, `Docs/AgToosa_Import.md`.

## Claim Boundary

| Control | Classification |
|---------|----------------|
| Orchestration Brain doc + workflow step-0 pointers | agent-instructed |
| Doc installed via `lib/config.sh` / `--update` | generator-enforced |
| ORB contract bats when run in CI | CI-enforced |
| Host Task/Agent tool selection | manual |
| Automatic agent launch / hosted orchestrator / runtime scheduler | roadmap / out of scope |

## Related docs

- `Docs/AgToosa_AgentCapability.md` — platform parallel vs sequential routing
- `Docs/AgToosa_Specialists.md` — specialist lanes and evidence blocks
- `Docs/AgToosa_Skills.md` — project skill inventory
- `Docs/AgToosa_Handoff.md` / `Docs/AgToosa_Import.md` — async lane boundaries
- `Docs/AgToosa_CrossModelReview.md` — independent reviewer separation
- `Docs/guides/subagent-heavy-workflows.md` — end-to-end delegated workflow entry

## Output (when consulted)

```
Phase: [spec|build|review|ship|…]
Inventory: [platforms, specialists, skills, MCP names, packages…]
Lanes: [planned parallel or sequential lanes]
Parallel: [yes|no — reason]
Fallback: [sequential note if applicable]
Merge owner: orchestrator
SoT: Docs/Master-Plan.md (unchanged until merge)
```

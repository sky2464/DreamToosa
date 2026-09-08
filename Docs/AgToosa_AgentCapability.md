# AgToosa Agent Capability Matrix

## Objective

Detect which **agent surfaces** are installed in a project and recommend the best **lifecycle path** for build, handoff, review (including cross-model), and specialist delegation — with explicit fallbacks when a platform lacks native parallel subagents.

> **Distinction:** `Docs/AgToosa_Specialists.md` → **Platform Capability Matrix** = specialist **native file targets**. This document = **lifecycle routing** (commands, handoff, review, cross-model, specialists orchestration, fallbacks).
>
> **Compatibility tiers** live in `Docs/AgToosa_Compatibility_Contract.md` — do not merge that tier table here.
>
> **Claim Boundary:** Routing recommendations are **agent-instructed**. Installing this doc via `agtoosa.sh --update` is **generator-enforced**. AgToosa does **not** auto-launch agents or probe remote APIs.
>
> **Source of truth:** `Docs/Master-Plan.md` remains the repo-local source of truth. External agents and dashboards are integrations, not authorities.

## Installed-Surface Detection

Before recommending a target, detect installed platforms using the same sentinels as specialists install:

| Platform | Sentinel (any match = installed) | Entry points |
|----------|----------------------------------|--------------|
| Cursor | `.cursor/` | `.cursorrules` |
| Claude Code | `.claude/` | `CLAUDE.md` |
| Codex / OpenCode | `.codex/` | `OPENCODE.md`, `AGENTS.md` |
| GitHub Copilot | `.github/agents/` or `.github/prompts/` | `.github/copilot-instructions.md` |
| VS Code | `.github/copilot-instructions.md` (generic VS Code path) | `.github/prompts/` |
| Windsurf | `.windsurf/` | `.windsurfrules` |
| Gemini | `.gemini/` | — |

Also consult `.agtoosa-lock.json` / install lock when present. Recommend targets **only** for surfaces actually installed. Never recommend Codex when `.codex/` is absent.

## Lifecycle Capability Matrix

| Platform | Commands | Handoff | Review | Cross-model | Specialists | Fallbacks | Enforcement |
|----------|----------|---------|--------|-------------|-------------|-----------|-------------|
| Claude Code | `.claude/commands/` | Strong — Agent tool async | Parallel personas | Parallel subagent delegation | `.claude/skills/<id>.md` | Sequential Agent tool if parallel unavailable | agent-instructed |
| Cursor | `.cursor/commands/` + rules | Background agents / paste pack | Sequential personas default | Sequential reviewer lanes | `.cursor/rules/<id>-specialist.mdc` | Record sequential note; optional `/agtoosa-review cross` | agent-instructed |
| Codex / OpenCode | `.codex/prompts/` + skills | Pack → Codex / OpenCode session | Host-dependent | When host supports delegated agents | `.codex/skills/<id>/SKILL.md` | Sequential skill run | agent-instructed |
| GitHub Copilot | `.github/prompts/` | Copilot cloud agent / PR agent | Agent file when present | Parallel per host; else sequential | `.github/agents/<id>.agent.md` | Cross-platform manual review | agent-instructed |
| VS Code | `.github/prompts/` (shared) | Same pack as Copilot path | Prompt-driven | Sequential default | Prefer Copilot agent files when present | Use Cursor/Claude if installed | agent-instructed |
| Windsurf | `.windsurf/workflows/` | Paste pack into workflow | Sequential default | Sequential | `.windsurf/workflows/<id>-specialist.md` | Sequential note | agent-instructed |
| Gemini | `.gemini/commands/` | Paste pack | Sequential default | Sequential | `.gemini/commands/<id>-specialist.toml` | Sequential note | agent-instructed |

**Column meanings**

| Column | Meaning |
|--------|---------|
| Commands | Where `/agtoosa-*` native adapters live |
| Handoff | Best path for `/agtoosa-handoff` pack consumption |
| Review | How `/agtoosa-review` personas should run |
| Cross-model | Whether `/agtoosa-review cross-model` can use parallel subagent delegation |
| Specialists | Native specialist file target (detail in `Docs/AgToosa_Specialists.md`) |
| Fallbacks | Honest path when preferred capability is missing |
| Enforcement | generator-enforced / CI-enforced / agent-instructed / manual / roadmap |

## IDE Host Mode Matrix

Per-platform enter/switch instructions for `/agtoosa-spec` and `/agtoosa-review`. Canonical planning windows and auto-switch triggers: `Docs/AgToosa_Agent.md` → **IDE Host Mode Bridge**.

| Platform | Enter plan mode | Switch to agent/auto | Notes |
|----------|----------------|----------------------|-------|
| **Cursor** | `SwitchMode` → `plan` if not already in plan; user fallback: Shift+Tab | `SwitchMode` → `agent` at auto-switch trigger; print `HOST-MODE:` handoff first | Do not queue plan→agent requests — finish the plan turn before switching |
| **GitHub Copilot / VS Code** | Select **Plan** agent or `/plan` prefix | **Start Implementation** / **Implement plan** at trigger | Plans may land in `.copilot/plans/`; map AgToosa sections before artifact write |
| **Claude Code** | `Shift+Tab` to plan, `/plan` prefix, or `--permission-mode plan` | Approve plan → `auto` or `acceptEdits` per user preference | `useAutoModeDuringPlan` is optional; AgToosa does not require it |
| **Codex / OpenCode** | Host plan skill when present; else behavioral plan-only turn-stop | Switch to agent execution mode when host exposes it | Print manual switch instruction when host API unavailable |
| **Windsurf** | Plan/workflow mode when available | Agent/workflow execution mode | Same sequential fallback pattern |
| **Gemini CLI** | Host plan equivalent or behavioral fallback | Agent mode for writes | Install-tested only until scenario proof |

**Claim Boundary:** Host mode enter/switch is **agent-instructed**. AgToosa does not call IDE APIs from shell. Manual fallback (Shift+Tab, mode picker) is always valid when auto-switch fails.

## Claim Boundary

| Control | Classification |
|---------|----------------|
| This matrix doc + workflow pointers | agent-instructed |
| Doc installed via `lib/config.sh` / `--update` | generator-enforced |
| Sentinel-based platform detection at install | generator-enforced |
| Routing recommendations during workflows | agent-instructed |
| Automatic agent launch | manual / out of scope |
| Hosted capability router / API probing | roadmap / out of scope |

## Routing Recommendation Algorithm

1. **Detect** — Build the set of installed platforms from the sentinel table above.
2. **Phase** — Identify the requested phase: `handoff` | `review` | `cross-model` | `build-async` | `specialists` | `help-hint`.
3. **Intersect** — Keep only matrix rows whose platform is installed.
4. **Prefer** — For the phase, pick the strongest available capability:
   - Prefer **parallel** hosts (Claude Code, then Copilot with agents) over sequential defaults.
   - Prefer a surface that already has matching native adapters for the command.
5. **Fallback** — If the preferred row is absent, walk the **Fallback Chain** and record which row was used in the handoff pack or review notes.
6. **Override** — User may name a different target agent; do not fight explicit user choice — note the override.

## Fallback Chain

When the preferred surface is missing or cannot run the phase natively, try in order:

1. Another **installed** platform with equal or better capability for the phase.
2. **Sequential** execution on the current host with the exact note:

   ```
   Capability lanes ran sequentially (platform does not support parallel subagents).
   ```

3. `/agtoosa-review cross` (cross-platform manual second opinion) for review/cross-model.
4. Virtual personas only (Security, EM, CEO, QA) with documented rationale.
5. Explicit skip with rationale — never silently claim a capability the host lacks.

## Workflow Hooks

| Workflow | How to use this matrix |
|----------|------------------------|
| `/agtoosa-handoff` | Recommend **Target agent** from installed rows; document fallbacks when preferred absent |
| `/agtoosa-build handoff` | Same routing hint before async dispatch |
| `/agtoosa-review` / `cross-model` | Choose parallel vs sequential from the Cross-model column |
| `/agtoosa-help next` | May include **one** read-only routing hint (no mutation) |
| `/agtoosa-specialists` / specialist docs | Keep native-target table here; **do not** duplicate this lifecycle table |

## Related Docs

- Specialist native targets — `Docs/AgToosa_Specialists.md`
- Assistant compatibility tiers — `Docs/AgToosa_Compatibility_Contract.md`
- Handoff packs — `Docs/AgToosa_Handoff.md`
- Cross-model gate — `Docs/AgToosa_CrossModelReview.md`
- Review personas — `Docs/AgToosa_Review.md`
- Build async — `Docs/AgToosa_Build.md`

## Output

Print a short routing recommendation when consulted:

```
Installed: [platforms…]
Phase: [handoff|review|…]
Recommended: [platform] — [one-line why]
Fallback: [next option or sequential note]
SoT: Docs/Master-Plan.md (unchanged)
```

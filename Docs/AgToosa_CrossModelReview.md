# AgToosa /agtoosa-review cross-model Workflow

## Sub-Commands

| Sub-command | Runs |
|-------------|------|
| `/agtoosa-review cross-model` | Cross-model review gate — independent reviewer subagent/model with structured evidence merge |

> **Distinction:** `/agtoosa-review cross` = cross-**platform** manual second opinion (switch Cursor ↔ Copilot). `/agtoosa-review cross-model` = cross-**model** writer/reviewer separation on the same or different hosts.

## Objective

Run an optional **cross-model review gate** that separates the **writer** (build agent) from an **independent reviewer** (different subagent, session, or platform instance — **not necessarily a different model**) for higher-assurance stories — with structured evidence merge, confidence tiers, user-visible consent before delegation, and honest fallbacks when a second model is unavailable or declined.

> **Prerequisites:** `/agtoosa-build` complete for the active story; active spec approved; story status `In Progress` or `In Review`.
>
> **Claim Boundary:** This gate is **agent-instructed**. AgToosa documents orchestration and evidence; it does **not** route paid model APIs, read billing plans, or enforce a second model at generator runtime.
>
> **Source of truth:** `Docs/Master-Plan.md` remains the repo-local source of truth. External reviewers are integrations, not authorities.

## Roles

| Role | Actor | Permissions |
|------|-------|-------------|
| **Writer** | Agent that ran `/agtoosa-build` | May fix findings after review with user authorization |
| **Independent reviewer** | Different subagent or platform instance (may use the **same model** as the parent session) | **Read-only** during the gate — no file or git mutations without explicit user authorization |
| **Orchestrator** | Primary review session | Reads workflow policy, obtains consent, merges evidence, applies confidence tiers, writes review report section |

## Project configuration

Read `Docs/Context/workflow.md` → `## Cross-model review` and `## Standing Corrections` before tiering or delegation. Standing Corrections override defaults when they conflict.

| Key | Values | Default | Meaning |
|-----|--------|---------|---------|
| `cross_model` | `off` · `on-demand` · `recommended` · `required` | `recommended` | When independent reviewer subagents may run |
| `reviewer_model` | `parent` · `ask` | `parent` | Which model tier the reviewer subagent may use |

| `cross_model` value | Orchestrator behavior |
|---------------------|----------------------|
| `off` | Never spawn cross-model subagents; run virtual personas only; record `skipped` with rationale in `## Cross-Model Review`. |
| `on-demand` | Spawn only when the user explicitly requested cross-model in this session or a Standing Correction requires it. |
| `recommended` | Apply risk-tier table below; use consent + model ceiling before delegating. |
| `required` | Strong tiers must run cross-model or document an explicit exception; consent + model ceiling still apply. |

| `reviewer_model` value | Orchestrator behavior |
|------------------------|----------------------|
| `parent` | Use the **same model tier as the parent chat** for the read-only reviewer subagent unless the user explicitly approves a different or premium model in this turn. |
| `ask` | Always present the consent line and wait for model choice (or skip) before delegating. |

## Risk-Tier Triggers

| Tier | When | Gate expectation |
|------|------|------------------|
| **Standard** | Routine Docs/chore with no trust-boundary ACs | Cross-model optional |
| **Recommended** | Spec threat model touches auth, registry, secrets, supply chain, or user-controlled input | Strongly recommend `/agtoosa-review cross-model` when `cross_model` is not `off` |
| **Strongly recommended** | Must ACs explicitly tag security/registry/auth surfaces | Run cross-model or document explicit skip rationale when `cross_model` is `required` or tier demands it |

Compute tier from the active spec STRIDE table and Must AC keywords — do not require a second model for every story.

## User consent and model ceiling

**Never** spawn a cross-model reviewer subagent silently. Before delegation (unless `cross_model: off` already decided skip):

1. State the computed **risk tier** and **why** (one sentence).
2. State the **workflow policy** (`cross_model`, `reviewer_model`).
3. State the **proposed reviewer model** (default: same as parent session).
4. Offer: proceed with proposed model · skip cross-model · approve a different model.

**Consent line (print verbatim shape, fill brackets):**

```
Cross-model review: tier [standard|recommended|strongly recommended] — [one-line why].
Policy: cross_model=[value] reviewer_model=[value].
Proposed reviewer: [parent session model name] read-only subagent.
→ Proceed  |  Skip cross-model  |  Use [other model] (requires your approval)
```

When `reviewer_model: ask`, wait for an explicit choice before delegating. When the user says **skip**, records **no access**, or does not approve a premium model, follow the **Fallback chain** — do not retry with a higher-tier model.

**Model ceiling:** The reviewer subagent **must not** use a higher-cost or higher-tier model than the parent session unless the user explicitly approves that model in the same turn. Do not default to premium models (e.g. Sonnet) for “independence.”

**Same-model reviewer:** A read-only subagent on the **same** model as the writer still satisfies writer/reviewer **session** separation; independence is subagent + read-only scope, not mandatory model diversity.

## Workflow

1. **Read policy** — `Docs/Context/workflow.md` (`cross_model`, `reviewer_model`) and Standing Corrections.
2. **Tier check** — Read active spec threat model and Must ACs; record tier in review notes.
3. **Policy gate** — If `cross_model: off`, or `on-demand` without user request, skip with rationale. If tier is Standard and policy is not `required`, cross-model remains optional.
4. **User consent** — Print the consent line; apply model ceiling per `reviewer_model`.
5. **Delegate reviewer** — Launch independent reviewer subagent(s) with read-only scope: diff, spec, test logs, threat model, test plan. **Do not paste secrets** into reviewer prompts — redact sensitive values from diffs and logs (same rules as `Docs/AgToosa_Handoff.md`).
6. **Specialist lanes** — When `Docs/Context/specialists.md` exists, run only specialists whose `phase_hooks` includes `review` and whose `trigger` matches the active story (see `Docs/AgToosa_Specialists.md`).
7. **Parallel execution** — When the host supports native parallel subagent delegation (Task tool, Agent tool, GitHub agent), run reviewer persona(s) and matching specialists in parallel. Confirm parallel vs sequential support via `Docs/AgToosa_AgentCapability.md` before claiming parallel lanes.
8. **Sequential fallback** — When parallel delegation is unavailable, run the same lanes sequentially and record exactly:

    ```
    Cross-model lanes ran sequentially (platform does not support parallel subagents).
    ```

9. **Collect evidence** — Each lane returns the structured evidence block below.
10. **Merge findings** — Tag each finding with a confidence tier before the Part 3 verdict table.
11. **Fallback chain** — When no second model/subagent is available or the user declines, in order:
    - `/agtoosa-review cross` (cross-platform manual review)
    - Sequential virtual personas (Security, EM, CEO, QA) with documented rationale
    - Explicit skip with rationale in `## Cross-Model Review` — never mark gate passed without one outcome recorded

## Structured Evidence Block

Every reviewer lane must return this shape (extends `Docs/AgToosa_Specialists.md`):

```markdown
### Cross-model evidence: <reviewer-id>
- **Reviewer identity:** <agent name or specialist id>
- **Model/platform:** <e.g. same as parent session (Composer 2.5) / Cursor — not an upgrade unless user-approved>
- **Consent:** stated / user-approved / skipped
- **Findings:** …
- **Files read:** …
- **Commands:** …
- **Warnings/errors:** …
- **Recommendations:** …
- **Spec sections affected:** Goal Contract | ACs | Architecture | Threat model | Tasks | Test plan
- **Confidence tier:** both-models | reviewer-only | writer-only | virtual-persona-only
```

## Merge and Confidence Rules

| Tier | Meaning |
|------|---------|
| `both-models` | Same finding flagged by writer-context review and independent reviewer |
| `reviewer-only` | Independent reviewer found; writer did not surface |
| `writer-only` | Writer/orchestrator found; reviewer did not confirm |
| `virtual-persona-only` | Finding from virtual Security/EM/CEO/QA personas only |

Deduplicate before the verdict table; prefer `both-models` when descriptions match.

## Read-Only Guarantee

The independent reviewer **must not** modify `Docs/Master-Plan.md`, git state, or implementation files during the gate. If a fix is needed, the orchestrator asks the user to authorize `/agtoosa-build` or a scoped fix — same pattern as `Docs/AgToosa_StatusGuide.md`.

> **Claim boundary:** On GitHub Copilot and other hosts, read-only is **agent-instructed** — native agent tool manifests may still list `terminal` or write-capable tools. Enforcement is policy + orchestrator authorization, not tool-level sandboxing (v1).

## Review Report Section

Append to `Docs/archived/review-[story-id].md`:

```markdown
## Cross-Model Review

| Field | Value |
|-------|-------|
| Tier | standard / recommended / strongly recommended |
| Workflow policy | cross_model=… reviewer_model=… |
| Consent | stated / user-approved / skipped |
| Reviewer identity | … |
| Model/platform | … |
| Outcome | completed / cross-platform fallback / sequential personas / skipped |
| Skip rationale | (required when skipped) |

[Merged findings with confidence tiers]
```

Update `Docs/archived/evidence-[story-id].md` with a `cross-model` row per `Docs/AgToosa_Evidence.md`.

## Related Workflows

- **Virtual personas** — `Docs/AgToosa_Review.md` Part 1 (not replaced)
- **Cross-platform** — `Docs/AgToosa_Review.md` Part 4 (`/agtoosa-review cross`)
- **Project specialists** — `Docs/AgToosa_Specialists.md`
- **Handoff packs** — `Docs/AgToosa_Handoff.md` when reviewer runs async/external
- **Lifecycle routing** — `Docs/AgToosa_AgentCapability.md` (parallel vs sequential per installed host)

## Output

- Present merged cross-model findings before the review approval gate.
- On successful completion, print the dual-line phase close per Docs/AgToosa_Agent.md → Lifecycle Next-Step Contract

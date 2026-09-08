# AgToosa Project Specialists

## Objective

Define the **canonical contract** for **project-specific specialist subagents**: optional, approval-gated lanes that extend AgToosa workflows without shipping a default roster in the template pack and without colliding with installed `agtoosa-*` lifecycle adapters.

Read this document when implementing or invoking specialist discovery (`/agtoosa-init`, `/agtoosa-update`) or orchestration (`/agtoosa-spec`). Platform adapters must **route here** — do not duplicate full discovery or merge logic in thin command files.

## Glossary

| Term | Meaning |
|------|---------|
| **Workflow adapter** | Installed `agtoosa-*` command, prompt, skill, or agent — AgToosa-owned, present after install |
| **Project skill** | Optional `.codex/skills/<name>/SKILL.md` from DEV-008 discovery — repeatable **slash-style** workflow helpers |
| **Project specialist** | Approval-gated subagent with `phase_hooks`, structured evidence, and multi-platform native files |
| **Virtual specialist** | Built-in `/agtoosa-review` personas (Security, EM, CEO, QA) — not project-specific |

Prefer **one artifact type per concern**: do not create both a project skill and a specialist with the same trigger unless they serve clearly different roles (skill = command helper; specialist = delegated subagent lane).

## Specialist Candidate Fields

Present every candidate in a table using these columns:

| Field | Required | Description |
|-------|----------|-------------|
| **id** | Yes | Lowercase hyphen-case identifier (e.g. `registry-pack-auditor`). Must not start with `agtoosa-`. |
| **trigger** | Yes | When to activate (story theme, path glob, keyword, or phase event). |
| **purpose** | Yes | One-line outcome the specialist delivers. |
| **phase_hooks** | Yes | Subset of `init`, `spec`, `build`, `qa`, `review`, `update` — when orchestration may invoke this specialist. |
| **inputs** | Yes | Files, docs, or context the specialist must read (paths only — no secret values). |
| **tools/MCP needs** | If any | MCP servers or tools required; declare so the user can approve scope. Use `none` when read-only file tools suffice. |
| **custom_mode** | No | Optional host-specific mode (e.g. read-only subagent). |
| **outputs** | Yes | Artifacts produced (evidence block, checklist, spec section deltas). |
| **validation** | Yes | Command, grep, or checklist that proves the specialist is testable and reusable — not a one-off story task. |
| **safety_notes** | If any | Secret handling, production touch, or trust-boundary warnings. |
| **platform_targets** | Yes | Which native files to create per installed platform (see Platform Matrix). |

**Decision column** (proposal tables): `Approve` / `Decline` / `Defer` — record outcomes in `Docs/Master-Plan.md` **Update Log**.

## Rejection Rules

Reject candidates that:

- Use id or trigger `agtoosa-*` or `/agtoosa-*` (reserved for AgToosa workflow adapters)
- Duplicate an existing specialist, project skill, or virtual review persona without **Update existing**
- Describe a **one-off** task for a single story only
- Lack **validation** (no command, checklist, or review artifact)
- Embed **secret values** (credentials, tokens, private keys) — reference paths only; add `safety_notes` instead

## Approved Project State

After **explicit user approval** only:

| Artifact | Path | Notes |
|----------|------|-------|
| Roster | `Docs/Context/specialists.md` | YAML or markdown list of approved specialists — **not** shipped in `template/` |
| Codex | `.codex/skills/<id>/SKILL.md` | Valid `name` + `description` frontmatter; specialist execution body |
| Claude Code | `.claude/skills/<id>.md` | Thin runner; may use Agent tool for delegation |
| GitHub Copilot | `.github/agents/<id>.agent.md` | Agent definition per repo conventions |
| Cursor | `.cursor/rules/<id>-specialist.mdc` or workflow fallback | Sequential lane default |
| Windsurf | `.windsurf/workflows/<id>-specialist.md` | Sequential lane default |
| Gemini | `.gemini/commands/<id>-specialist.toml` | Sequential lane default |

`agtoosa.sh --update` installs AgToosa-owned template inventory only — it must **never** register or overwrite `Docs/Context/specialists.md` or project specialist native files.

## Platform Capability Matrix (v1)

> **Lifecycle routing** (handoff / review / cross-model / build-async recommendations) lives in `Docs/AgToosa_AgentCapability.md`. This table is **specialist native file targets only** — do not duplicate the full lifecycle routing table here.

| Platform | Native target | Parallel spec lanes | Notes |
|----------|---------------|----------------------|-------|
| Codex / OpenCode | `.codex/skills/<id>/SKILL.md` | When host supports delegated agents | Same folder as project skills — distinct id/trigger contract |
| Claude Code | `.claude/skills/<id>.md` | Yes (Agent tool) | Preferred parallel host for spec orchestration |
| GitHub Copilot | `.github/agents/<id>.agent.md` | Per host | |
| Cursor | `.cursor/rules/<id>-specialist.mdc` | Sequential default | Fallback: `.cursor/commands/` only if rules insufficient |
| Windsurf | `.windsurf/workflows/<id>-specialist.md` | Sequential default | |
| Gemini | `.gemini/commands/<id>-specialist.toml` | Sequential default | |

## Installed Platform Detection

Before proposing specialists, detect installed platforms using:

- `Docs/.agtoosa-version` and `.agtoosa-lock.json` platform list
- Sentinel files: `.codex/`, `.claude/`, `.cursor/`, `.windsurf/`, `.gemini/`, `.github/agents/`
- Entry points: `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.windsurfrules`, `OPENCODE.md`

Propose native targets **only** for platforms actually installed in the project.

## Structured Evidence Block

Every specialist lane must return this shape (orchestrator merges into spec sections):

```markdown
### Specialist evidence: <id>
- **Findings:** …
- **Files read:** …
- **Commands:** …
- **Warnings/errors:** …
- **Recommendations:** …
- **Spec sections affected:** Goal Contract | ACs | Architecture | Threat model | Tasks | Test plan
```

Terminal output must include this block so `/agtoosa-status` and reviewers can audit what ran.

## Orchestration Summary

| Workflow | When | Behavior |
|----------|------|----------|
| `/agtoosa-init` | Phase E | Project Specialist Discovery → approval → materialize |
| `/agtoosa-update` `check` / `plan` | After Detect | Read-only **Specialist Compatibility Check** |
| `/agtoosa-update` full / `apply` | After Verify | Optional **separate** materialization proposal — not part of CLI Apply |
| `/agtoosa-spec` | Early Part 1 | Read roster; filter `spec` + trigger; parallel or sequential; merge before Goal Contract finalization |
| `/agtoosa-review` | After Part 1 personas | Read roster; filter `review` + trigger; parallel or sequential; merge before Part 3 verdict; see `Docs/AgToosa_CrossModelReview.md` |

**Review-phase orchestration (`/agtoosa-review`):**

1. If `Docs/Context/specialists.md` is missing, skip specialist lanes (record "no approved specialists").
2. Load the roster; select specialists where `phase_hooks` includes **`review`** and **trigger** matches the active story (title, paths, epic, or threat-model tier).
3. For each selected specialist, run a read-only lane that returns the structured evidence block from this doc plus cross-model fields from `Docs/AgToosa_CrossModelReview.md`.
4. **Parallel:** when the host supports native subagent delegation, run matching review lanes in parallel with the independent cross-model reviewer.
5. **Sequential fallback:** otherwise run the same lanes one at a time and print: `Cross-model lanes ran sequentially (platform does not support parallel subagents).`
6. Merge evidence into the review report `## Cross-Model Review` section before the Part 3 verdict table.

See `Docs/AgToosa_Init.md`, `Docs/AgToosa_Update.md`, `Docs/AgToosa_Spec.md`, and `Docs/AgToosa_CrossModelReview.md` for step-by-step obligations.

## Secret and MCP Safety

- Never copy credentials, tokens, or private keys into specialist bodies or roster files.
- **tools/MCP needs** must list servers by name; user approves before specialists invoke MCP.
- If a specialist needs awareness of secrets, document file paths (e.g. `.env.example`) in `inputs` and `safety_notes` only.

## Related Workflows

- **Project Skill Discovery** — `Docs/AgToosa_Init.md` Phase F; Codex-first repeatable commands (DEV-008)
- **Story Skill Opportunity Synthesis** — `Docs/AgToosa_Spec.md`; story-scoped skill candidates
- **Virtual review personas** — `Docs/AgToosa_Review.md`; not replaced by project specialists
- **Agent Capability Matrix** — `Docs/AgToosa_AgentCapability.md`; lifecycle routing (not specialist native targets)

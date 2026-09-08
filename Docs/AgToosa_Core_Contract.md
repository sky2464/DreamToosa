# AgToosa Core Contract

> **Purpose:** Name the minimum AgToosa lifecycle surface, and map core versus optional install inventories to `lib/config.sh` arrays so documentation cannot invent paths the generator does not install.
>
> **Installed path:** `Docs/AgToosa_Core_Contract.md`. Inventory paths below match the generator `lib/config.sh` arrays (`DOCS_FILES`, `OPTIONAL_TEMPLATE_FILES`, `CONTEXT_FILES`).

## Core Lifecycle Commands

Rev4 core lifecycle is these seven commands:

| Command | Role |
|---------|------|
| **Init** | Project intake and AgToosa bootstrap |
| **Spec** | Spec interview, ACs, wave plan |
| **Build** | Implement against the approved spec |
| **Review** | Review gate before ship |
| **Ship** | Release / archive / changelog close-out |
| **Verify** | Deterministic lifecycle verifier (`agtoosa-verify.sh` / `--verify`) |
| **Doctor** | Install health / skew report (`--doctor`) |

Baseline AgToosa use does **not** require registry packs. Specialty behavior (stack-specific, compliance, niche adapters beyond the optional platform surfaces below) belongs in **packs**. Packs extend the install; they do not redefine these seven core lifecycle commands.

## Docs Inventory (`DOCS_FILES`)

Generator-installed documentation from the `DOCS_FILES` array in `lib/config.sh`. Do not invent paths outside this list.

```
Docs/ADR-FORMAT.md
Docs/AgToosa_Agent.md
Docs/AgToosa_AgentCapability.md
Docs/AgToosa_Behavioral_Conformance.md
Docs/AgToosa_Build.md
Docs/AgToosa_CaseStudy.template.md
Docs/AgToosa_Catalog.md
Docs/AgToosa_Change_Aware_Delivery.md
Docs/AgToosa_Changelog.md
Docs/AgToosa_Compatibility_Contract.md
Docs/AgToosa_Concise.md
Docs/AgToosa_Core_Contract.md
Docs/AgToosa_CrossModelReview.md
Docs/AgToosa_Cross_Framework_Interchange.md
Docs/AgToosa_Dashboard.md
Docs/AgToosa_Debug.md
Docs/AgToosa_Delivery_Evidence_Contract.md
Docs/AgToosa_Evidence.md
Docs/AgToosa_Evidence_Provenance.md
Docs/AgToosa_Goal.md
Docs/AgToosa_Governance.md
Docs/AgToosa_GovernancePolicy.md
Docs/AgToosa_Guarded_Portable_Execution.md
Docs/AgToosa_Handoff.md
Docs/AgToosa_Hooks.md
Docs/AgToosa_Import.md
Docs/AgToosa_Init.md
Docs/AgToosa_MetricsKit.md
Docs/AgToosa_Network_Matrix.md
Docs/AgToosa_Next.md
Docs/AgToosa_Orchestration.md
Docs/AgToosa_QA.md
Docs/AgToosa_Quickref.md
Docs/AgToosa_Readiness.md
Docs/AgToosa_Registry.md
Docs/AgToosa_Retro.md
Docs/AgToosa_Revert.md
Docs/AgToosa_Review.md
Docs/AgToosa_Ship.md
Docs/AgToosa_Skills.md
Docs/AgToosa_Spec.md
Docs/AgToosa_Specialists.md
Docs/AgToosa_Status.md
Docs/AgToosa_StatusGuide.md
Docs/AgToosa_Task.md
Docs/AgToosa_TrackerSync.md
Docs/AgToosa_Update.md
Docs/AgToosa_Worktree.md
Docs/CONTEXT-FORMAT.md
Docs/DEEPENING.md
Docs/LANGUAGE.md
Docs/Master-Architecture.md
Docs/Master-Plan.md
Docs/SPEC-FORMAT.md
Docs/agtoosa-capsule-pack.sh
Docs/agtoosa-capsule-return.sh
Docs/agtoosa-capsule-verify.sh
Docs/agtoosa-context-compile.sh
Docs/agtoosa-dashboard.sh
Docs/agtoosa-drift-assess.sh
Docs/agtoosa-evidence-profile-check.sh
Docs/agtoosa-evidence.jsonl
Docs/agtoosa-gate.yml.example
Docs/agtoosa-interchange-assess.sh
Docs/agtoosa-interchange-export.sh
Docs/agtoosa-interchange-import.sh
Docs/agtoosa-policy-check.sh
Docs/agtoosa-proof-verify.sh
Docs/agtoosa-scenario-run.sh
Docs/agtoosa-scenario-verify.sh
Docs/agtoosa-tracker-sync.schema.json
Docs/agtoosa-verify.sh
Docs/schemas/cleanup-result-v1.json
Docs/schemas/verify-result-v1.json

```
## Optional Platform Surfaces (`OPTIONAL_TEMPLATE_FILES`)

Optional adapters and platform entry points from `OPTIONAL_TEMPLATE_FILES` in `lib/config.sh`. These are **not** core-enforced lifecycle documents; they are selected by platform choice at install/update time.

```
.claude/commands/agtoosa-build.md
.claude/commands/agtoosa-catalog.md
.claude/commands/agtoosa-concise.md
.claude/commands/agtoosa-debug.md
.claude/commands/agtoosa-evidence.md
.claude/commands/agtoosa-goal.md
.claude/commands/agtoosa-handoff.md
.claude/commands/agtoosa-help.md
.claude/commands/agtoosa-import.md
.claude/commands/agtoosa-init.md
.claude/commands/agtoosa-next.md
.claude/commands/agtoosa-qa.md
.claude/commands/agtoosa-revert.md
.claude/commands/agtoosa-review.md
.claude/commands/agtoosa-ship.md
.claude/commands/agtoosa-spec.md
.claude/commands/agtoosa-status.md
.claude/commands/agtoosa-task.md
.claude/commands/agtoosa-tracker.md
.claude/commands/agtoosa-update.md
.claude/hooks/block-dangerous-git.sh
.claude/settings.json
.codex/prompts/agtoosa-build.md
.codex/prompts/agtoosa-catalog.md
.codex/prompts/agtoosa-concise.md
.codex/prompts/agtoosa-debug.md
.codex/prompts/agtoosa-evidence.md
.codex/prompts/agtoosa-goal.md
.codex/prompts/agtoosa-handoff.md
.codex/prompts/agtoosa-help.md
.codex/prompts/agtoosa-import.md
.codex/prompts/agtoosa-init.md
.codex/prompts/agtoosa-next.md
.codex/prompts/agtoosa-qa.md
.codex/prompts/agtoosa-revert.md
.codex/prompts/agtoosa-review.md
.codex/prompts/agtoosa-ship.md
.codex/prompts/agtoosa-spec.md
.codex/prompts/agtoosa-status.md
.codex/prompts/agtoosa-task.md
.codex/prompts/agtoosa-tracker.md
.codex/prompts/agtoosa-update.md
.codex/skills/agtoosa-build/SKILL.md
.codex/skills/agtoosa-concise/SKILL.md
.codex/skills/agtoosa-debug/SKILL.md
.codex/skills/agtoosa-evidence/SKILL.md
.codex/skills/agtoosa-goal/SKILL.md
.codex/skills/agtoosa-handoff/SKILL.md
.codex/skills/agtoosa-help/SKILL.md
.codex/skills/agtoosa-import/SKILL.md
.codex/skills/agtoosa-init/SKILL.md
.codex/skills/agtoosa-next/SKILL.md
.codex/skills/agtoosa-qa/SKILL.md
.codex/skills/agtoosa-revert/SKILL.md
.codex/skills/agtoosa-review/SKILL.md
.codex/skills/agtoosa-ship/SKILL.md
.codex/skills/agtoosa-spec/SKILL.md
.codex/skills/agtoosa-status/SKILL.md
.codex/skills/agtoosa-task/SKILL.md
.codex/skills/agtoosa-update/SKILL.md
.cursor/commands/agtoosa-build.md
.cursor/commands/agtoosa-catalog.md
.cursor/commands/agtoosa-concise.md
.cursor/commands/agtoosa-debug.md
.cursor/commands/agtoosa-evidence.md
.cursor/commands/agtoosa-goal.md
.cursor/commands/agtoosa-handoff.md
.cursor/commands/agtoosa-help.md
.cursor/commands/agtoosa-import.md
.cursor/commands/agtoosa-init.md
.cursor/commands/agtoosa-next.md
.cursor/commands/agtoosa-qa.md
.cursor/commands/agtoosa-revert.md
.cursor/commands/agtoosa-review.md
.cursor/commands/agtoosa-ship.md
.cursor/commands/agtoosa-spec.md
.cursor/commands/agtoosa-status.md
.cursor/commands/agtoosa-task.md
.cursor/commands/agtoosa-tracker.md
.cursor/commands/agtoosa-update.md
.cursor/rules/agtoosa-build.mdc
.cursor/rules/agtoosa-concise.mdc
.cursor/rules/agtoosa-core.mdc
.cursor/rules/agtoosa-evidence.mdc
.cursor/rules/agtoosa-goal.mdc
.cursor/rules/agtoosa-handoff.mdc
.cursor/rules/agtoosa-import.mdc
.cursor/rules/agtoosa-qa.mdc
.cursor/rules/agtoosa-revert.mdc
.cursor/rules/agtoosa-review.mdc
.cursor/rules/agtoosa-ship.mdc
.cursor/rules/agtoosa-spec.mdc
.cursor/rules/agtoosa-status.mdc
.cursor/rules/agtoosa-task.mdc
.cursor/rules/agtoosa-update.mdc
.cursorrules
.gemini/commands/agtoosa-build.toml
.gemini/commands/agtoosa-catalog.toml
.gemini/commands/agtoosa-concise.toml
.gemini/commands/agtoosa-debug.toml
.gemini/commands/agtoosa-evidence.toml
.gemini/commands/agtoosa-goal.toml
.gemini/commands/agtoosa-handoff.toml
.gemini/commands/agtoosa-help.toml
.gemini/commands/agtoosa-import.toml
.gemini/commands/agtoosa-init.toml
.gemini/commands/agtoosa-next.toml
.gemini/commands/agtoosa-qa.toml
.gemini/commands/agtoosa-revert.toml
.gemini/commands/agtoosa-review.toml
.gemini/commands/agtoosa-ship.toml
.gemini/commands/agtoosa-spec.toml
.gemini/commands/agtoosa-status.toml
.gemini/commands/agtoosa-task.toml
.gemini/commands/agtoosa-tracker.toml
.gemini/commands/agtoosa-update.toml
.github/agents/agtoosa-cross-model-reviewer.agent.md
.github/agents/agtoosa-status-guide.agent.md
.github/agents/agtoosa.agent.md
.github/copilot-instructions.md
.github/instructions/agtoosa-changelog.instructions.md
.github/instructions/agtoosa-core.instructions.md
.github/instructions/agtoosa-security.instructions.md
.github/instructions/agtoosa-testing.instructions.md
.github/prompts/agtoosa-build.prompt.md
.github/prompts/agtoosa-catalog.prompt.md
.github/prompts/agtoosa-concise.prompt.md
.github/prompts/agtoosa-debug.prompt.md
.github/prompts/agtoosa-evidence.prompt.md
.github/prompts/agtoosa-goal.prompt.md
.github/prompts/agtoosa-handoff.prompt.md
.github/prompts/agtoosa-help.prompt.md
.github/prompts/agtoosa-import.prompt.md
.github/prompts/agtoosa-init.prompt.md
.github/prompts/agtoosa-next.prompt.md
.github/prompts/agtoosa-qa.prompt.md
.github/prompts/agtoosa-revert.prompt.md
.github/prompts/agtoosa-review.prompt.md
.github/prompts/agtoosa-ship.prompt.md
.github/prompts/agtoosa-spec.prompt.md
.github/prompts/agtoosa-status.prompt.md
.github/prompts/agtoosa-task.prompt.md
.github/prompts/agtoosa-tracker.prompt.md
.github/prompts/agtoosa-update.prompt.md
.windsurf/rules/agtoosa-build.md
.windsurf/rules/agtoosa-concise.md
.windsurf/rules/agtoosa-debug.md
.windsurf/rules/agtoosa-evidence.md
.windsurf/rules/agtoosa-goal.md
.windsurf/rules/agtoosa-handoff.md
.windsurf/rules/agtoosa-import.md
.windsurf/rules/agtoosa-qa.md
.windsurf/rules/agtoosa-revert.md
.windsurf/rules/agtoosa-review.md
.windsurf/rules/agtoosa-ship.md
.windsurf/rules/agtoosa-spec.md
.windsurf/rules/agtoosa-status.md
.windsurf/rules/agtoosa-task.md
.windsurf/rules/agtoosa-update.md
.windsurf/workflows/agtoosa-build.md
.windsurf/workflows/agtoosa-catalog.md
.windsurf/workflows/agtoosa-concise.md
.windsurf/workflows/agtoosa-debug.md
.windsurf/workflows/agtoosa-evidence.md
.windsurf/workflows/agtoosa-goal.md
.windsurf/workflows/agtoosa-handoff.md
.windsurf/workflows/agtoosa-help.md
.windsurf/workflows/agtoosa-import.md
.windsurf/workflows/agtoosa-init.md
.windsurf/workflows/agtoosa-next.md
.windsurf/workflows/agtoosa-qa.md
.windsurf/workflows/agtoosa-revert.md
.windsurf/workflows/agtoosa-review.md
.windsurf/workflows/agtoosa-ship.md
.windsurf/workflows/agtoosa-spec.md
.windsurf/workflows/agtoosa-status.md
.windsurf/workflows/agtoosa-task.md
.windsurf/workflows/agtoosa-tracker.md
.windsurf/workflows/agtoosa-update.md
.windsurfrules
AGENTS.md
CLAUDE.md
Docs/AgToosa_Claude.md
Docs/AgToosa_Gemini.md
OPENCODE.md

```
## Context Files (`CONTEXT_FILES`)

Context inventory from `CONTEXT_FILES` in `lib/config.sh`.

```
Docs/Context/agtoosa-policy.example.yaml
Docs/Context/product-guidelines.md
Docs/Context/product.md
Docs/Context/tech-stack.md
Docs/Context/workflow.md

```
## Claim Boundary / Enforcement Classes

| Control | Classification | Notes |
|---------|----------------|-------|
| Core `Docs/` files listed under `DOCS_FILES` | **generator-installed core** | Copied/merged by the generator; presence is inventory-backed |
| Paths under `OPTIONAL_TEMPLATE_FILES` | **optional adapters** | Platform-selected; not mandatory core lifecycle |
| Registry pack additions | **registry / pack content** | Added via registry install; boundaries live in pack + registry docs (not redefined here) |
| Contract authoring, inventory sync after array edits | **manual maintainer action** | Maintainer updates this document when arrays change; CORE bats catch drift in CI |

**Honesty rules**

- Optional adapters are **not** "core-enforced lifecycle."
- Pack content boundaries are referenced, not redefined (see registry pack authoring and claim-boundary docs).
- Array-to-doc parity is **CI-enforced** when CORE tests run; semantic pack policy remains pack/registry review.

## Related

- Authoring / onboarding: see `/agtoosa-help` Authoring resources (GitHub guides)
- Registry: `Docs/AgToosa_Registry.md`
- Compatibility (platform tiers): `Docs/AgToosa_Compatibility_Contract.md`

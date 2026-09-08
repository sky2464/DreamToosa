# AgToosa Assistant Compatibility Contract

## Objective

Define what **Install-tested**, **Render-tested**, and **Scenario-tested** mean for each assistant platform — distinct from lifecycle **routing** in `Docs/AgToosa_AgentCapability.md` (DEV-055).

> **Authority split:** Lifecycle routing (handoff / review / cross-model / specialists) remains in `AgToosa_AgentCapability.md`. Compatibility tiers and evidence live **only** in this document. Do not merge the tier table into AgentCapability.

## Tier Definitions

| Tier | Meaning | Evidence required |
|------|---------|-------------------|
| **Install-tested** | Generator creates/merges expected files for the platform | Install/update bats or fixture pointers; last_evidence date |
| **Render-tested** | Target assistant recognizes commands/rules/entry files | Maintainer render check notes or scheduled probe pointer |
| **Scenario-tested** | Fixed proof task yields required workflow artifacts | Scenario fixture/command pointer **and** last_evidence date — required before any Scenario-tested label |

**Rules**

- A platform **must not** be labeled Scenario-tested (or “fully supported”) without a scenario evidence pointer.
- Gaps column is mandatory: record what is missing even when Install-tested is green.
- Scheduled scenario cadence may be documented; this does not imply universal Scenario-tested status.

## Platform Compatibility Table

| Platform | Install-tested | Render-tested | Scenario-tested | last_evidence | proof / pointer | gaps |
|----------|----------------|---------------|-----------------|---------------|-----------------|------|
| Cursor | yes | partial | no | 2026-07-12 | `tests/agtoosa.bats` Cursor install paths; AgentCapability sentinels | Scenario proof not claimed |
| Claude Code | yes | partial | no | 2026-07-12 | Claude command/skill install bats | Scenario proof not claimed |
| Codex / OpenCode | yes | partial | no | 2026-07-12 | Codex skill/prompt inventory bats | Scenario proof not claimed |
| GitHub Copilot | yes | partial | no | 2026-07-12 | `.github/prompts` / agents install coverage | Scenario proof not claimed |
| VS Code | yes | partial | no | 2026-07-12 | Shared Copilot instruction path | Scenario proof not claimed |
| Windsurf | yes | partial | no | 2026-07-12 | Windsurf rules/workflows inventory | Scenario proof not claimed |
| Gemini | yes | partial | no | 2026-07-12 | Gemini command toml inventory | Scenario proof not claimed |

## Claim Boundary

| Control | Classification |
|---------|----------------|
| This compatibility contract doc | generator-enforced install via `lib/config.sh` |
| Install-tested tier | CI-enforced-able via existing install bats |
| Render-tested tier | manual / scheduled maintainer evidence |
| Scenario-tested tier | manual / scheduled — explicit date + pointer required |
| Lifecycle routing | DEV-055 AgentCapability — unchanged |

## Related

- Lifecycle routing matrix: `Docs/AgToosa_AgentCapability.md`
- Proof product journey: README / first-15 examples (DEV-086)
- **Scenario corpus (DEV-121):** `Docs/AgToosa_Behavioral_Conformance.md` — use `data/scenarios/lifecycle-compass-proof.json` as the Scenario-tested evidence pointer. Static bats verify corpus integrity only; **do not** label a platform Scenario-tested without maintainer-recorded `last_evidence` and a scenario-run pointer.

<!-- AGTOOSA PRODUCT TRUTH START: claims.surface.template-compatibility -->
<!-- Static conformance and freshness only; not behavioral or provenance proof. -->
| Claim ID | Target | Status | Evidence class | Expires |
| --- | --- | --- | --- | --- |
| `claim.adapter.cursor` | `cursor.project-commands` | verified | static-conformance | 2026-10-12 |
| `claim.adapter.windsurf` | `windsurf.workflows` | verified | static-conformance | 2026-10-12 |
| `claim.adapter.claude` | `anthropic.claude-code` | verified | static-conformance | 2026-10-12 |
| `claim.adapter.gemini` | `google.gemini-cli` | verified | static-conformance | 2026-10-12 |
| `claim.adapter.copilot-vscode` | `github.copilot-vscode` | verified | static-conformance | 2026-10-12 |
| `claim.adapter.codex` | `openai.codex-cli` | verified | static-conformance | 2026-10-12 |
| `claim.windows.bootstrap-ref` | `windows-native` | verified | static-conformance | 2026-10-12 |
| `claim.product-truth.local` | `maintainer` | verified | static-conformance | 2026-10-12 |
<!-- AGTOOSA PRODUCT TRUTH END: claims.surface.template-compatibility -->

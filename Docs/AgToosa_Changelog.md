# AgToosa Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioned per [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

---

## [0.3.34] — 2026-07-26

Patch release: DEV-121 — Behavioral Conformance Lab.

### Added

- **DEV-121 — Behavioral Conformance Lab.** Versioned scenario corpus; universal `lifecycle-compass-proof` × six platforms; `agtoosa-scenario-run.sh` + `agtoosa-scenario-verify.sh`; golden fixtures; DEV-094/096/101 cross-links; BCL-001–BCL-013 bats; ADR-021 Accepted.

---

## [0.3.33] — 2026-07-26

Patch release: DEV-127 — README Experience Refresh.

### Added

- **DEV-127 — README Experience Refresh.** Motion-first short README (~121 lines); `docs/guides/readme-reference.md` and `architecture-overview.md` deep dives; Remotion hero GIF + animated SVG under `docs/media/agtoosa-hero/`; RMH-001–009 bats; wiki home refresh.

---

## [0.3.32] — 2026-07-26

Patch release: DEV-119 — Recoverable Project Transaction.

### Added

- **DEV-119 — Recoverable Project Transaction.** Gitignored `.agtoosa/transactions/` journal with pre-image snapshots; late-commit rollback in `apply_commit_staging`; `agtoosa.sh --transaction-recover` and `--transaction-status`; RPT-001–RPT-012 bats; ADR-018 Accepted.

---

## [0.3.31] — 2026-07-25

Patch release: cross-model review consent and workflow policy.

### Added

- **Cross-model consent and model ceiling.** `Docs/Context/workflow.md` keys `cross_model` and `reviewer_model` (defaults: `recommended`, `parent`); mandatory user-visible consent before reviewer subagents; reviewer must not exceed parent session model tier without explicit approval; same-model read-only subagent is valid.

---

## [0.3.30] — 2026-07-22

Patch release: DEV-118 — Product Truth & Adapter Contract.

### Added

- **DEV-118 — Product Truth & Adapter Contract.** Closed product-truth contract, inert checker/renderer, managed adapter blocks, governed claims, Windows exact-ref bootstrap validation, and PTC-001–PTC-012 smoke bats (ADR-015–ADR-017).

---

## [Unreleased]

---

## [0.3.28] — 2026-07-12

Patch release: DEV-116 — AgToosa Lifecycle Compass.

### Added

- **DEV-116 — AgToosa Lifecycle Compass.** Replaced Natural Language Intent Map with Lifecycle Compass semantic intent classes; added `--route-hint --format json` status formatting support in generator and PowerShell wrapper; added CMP-001–CMP-007 bats integration tests.

---

## [0.3.27] — 2026-07-12

Patch release: DEV-115 — `--cleanup` safety follow-up.

### Added

- **DEV-115 — `--cleanup` safety follow-up.** `--only backups` limits housekeeping to merge backups; preserve deep-merged `.claude/settings.json` when Claude is deselected; CLN-015–CLN-017 bats; `AgToosa_Update.md` guidance.

## [0.3.26] — 2026-07-12

Patch release: DEV-113 — Cursor intake hardening + fixture parity.

### Changed

- **DEV-113 — Cursor intake hardening.** FIX-001 exercises `cursor-intake-fixture.sh`; CIT-002–CIT-004; CLAUDE.md NL map parity; `AGTOOSA_SHIP_DIR` ship test isolation.

---

## [0.3.25] — 2026-07-12

Patch release: DEV-114 — `--cleanup` false-positive hotfix.

### Fixed

- **DEV-114 — `--cleanup` false positives.** Copilot/VS Code shared prompts no longer misclassified; `Docs/AgToosa_TestPlan-*` preserved; CLN-012–CLN-014.

---

## [0.3.24] — 2026-07-12

Patch release: DEV-112 — Smart Apply UX Polish + `--cleanup`.

### Added

- **DEV-112 — Smart Apply UX Polish.** Quiet upgrade output; platform legend with checkmarks; context-aware next steps; SAU-011–SAU-017.
- **DEV-112 — `--cleanup` housekeeping.** Opt-in removal of merge backups, orphan docs, and deselected platform files; CLN-001–CLN-011.

## [0.3.23] — 2026-07-12

Patch release: DEV-111 — Smart One-Command Install UX.

### Added

- **DEV-111 — Smart One-Command Install UX.** Auto-detect upgrade on re-run; `Found:` platform detect + optional add; `smart_apply()` unified path; smart per-file preserve/refresh; human summary buckets; `--force` hidden from interactive UX; PS1 parity; SAU-001–SAU-010 bats.

---

## [2.4.0] — 2026-05-14

### Added
- `/agtoosa-task` command (`Docs/AgToosa_Task.md`): fast Master-Plan.md capture for bugs, chores, spikes, and fixes without a full spec cycle; includes type-specific DoD checklists and Discovery Triage origin tracking
- Issue Standard anatomy in `Docs/AgToosa_Agent.md`: canonical title format `[Type]: [description]`, Epic→Story→Task hierarchy, and phase Update Log protocol in `Docs/AgToosa_Governance.md`
- Epic creation in `/agtoosa-init`: agent adds Epic rows to `Docs/Master-Plan.md`
- Story creation with T-shirt sizing and cycle enrollment in `/agtoosa-spec`: Master-Plan Story row, estimate, and optional active-cycle enrollment
- Task tracking in `/agtoosa-build`: checkbox tree and Update Log entries per completed task; Story → `In Progress` at first TDD task
- Discovery Triage Protocol in `/agtoosa-build`: classify out-of-scope findings, size them, and route to create-issue / expand-scope / ignore
- Status transition protocol: Story moves `Todo → In Progress → In Review → Done` at Build/Review/Ship boundaries; rollback resets to `In Review`
- Phase progress recorded in `Docs/Master-Plan.md` Update Log at every transition: Spec ✅ Approved, Build 🏗️ Started, Task 🟢 N/M, Review 🔍 Started/verdict, Ship 🚀/Rollback 🔙
- Rich `Docs/Master-Plan.md` template: 8-section structured document (Project Charter, Epics, Active Cycle, Active Tasks, Backlog, Blocked, Completed This Cycle, Update Log)

---

## [2.3.0] — 2026-04-27

### Added
- Platform-native command files for Claude Code: `.claude/commands/` (8 slash commands — init, spec, build, qa, review, ship, revert, help), `.claude/settings.json` (Stop / PreToolUse / PostToolUse hooks), `.claude/skills/agtoosa-review.md`
- Cursor context rules and native commands: `.cursor/rules/` plus `.cursor/commands/`
- Platform-native command files for Gemini CLI: `.gemini/commands/` (8 TOML files)
- Windsurf context rules and native workflows: `.windsurf/rules/` plus `.windsurf/workflows/`
- Codex workflow skills: `.codex/skills/`
- Platform-native rule files for Roo: `.roo/rules/` (7 MD files)
- Platform-native prompt files for GitHub Copilot: `.github/prompts/` (8 prompt files) and `.github/agents/agtoosa.agent.md`
- Generator expansion: `lib/generate.sh` stages all new platform file sets into `ship/`; `lib/install.sh` installs them into the target project
- `lib/config.sh` — 7 new file-list arrays (`WINDSURF_RULE_FILES`, `ROO_RULE_FILES`, `GEMINI_COMMAND_FILES`, `COPILOT_PROMPT_FILES`, `COPILOT_AGENT_FILES`, `CLAUDE_HOOK_FILES`, `CLAUDE_SKILL_FILES`) and expanded `OPTIONAL_TEMPLATE_FILES`
- `merge_settings_json()` in `lib/copy.sh` — deep-merges AgToosa hooks into an existing `.claude/settings.json` without touching user settings, deduplicating by command string
- 48-test bats suite (up from ~15 at v2.2.0): coverage for all per-platform copy paths, `.claude/settings.json` hook deduplication, dry-run display, `inject_version`, `version_lt`, `backup_file`, `copy_platform_file`, and `merge_platform_file`

### Fixed
- `print_template_files()` no longer emits duplicate paths — removed redundant per-platform arrays already covered by `OPTIONAL_TEMPLATE_FILES`; CI template validation now passes (DEV-160)
- `AGTOOSA_VERSION` correctly set to `2.3.0` (regression from `2.2.0` → `2.1.1` in post-release commit) (DEV-161)

---

## [2.2.0] — 2026-04-27

### Added
- Smart merge/append for platform entry-point files (DEV-156): `inject_version()` wraps content in AgToosa START/END delimiters; `merge_platform_file()` handles 4 cases — new file, in-place block update, old-format migration, and append-to-user-file
- `.bak` backup creation and "✅ (up to date)" no-skip messaging for `merge_platform_file` (DEV-157)
- `/agtoosa-qa` slash command and `AgToosa_QA.md` workflow file
- Sub-command architecture across all four main AgToosa commands (`/agtoosa-spec`, `/agtoosa-build`, `/agtoosa-review`, `/agtoosa-ship`)
- Gemini CLI / Jules platform support (`AGENTS.md`, `template/AGENTS.md`, `GEMINI.md`)
- OpenCode platform support (`template/OPENCODE.md`)
- `lib/config.sh` — extracted file-list arrays and `print_usage` / `print_template_files` helpers
- `lib/version.sh` — extracted `inject_version`, `extract_version`, and `version_lt` helpers
- CI workflow updates: shellcheck action version bump, non-portable `grep -P` fix (DEV-114)

### Fixed
- 12 generator bugs (DEV-128–139): template pollution, dotfile copy, version badge, security versions, and related issues
- Consistency fixes across README phase clarity, ship revert wording, and platform file alignment (DEV-124–126)
- `/agtoosa-build` test sub-command scope and removed broken TDD guard external link (DEV-118–119)
- Replaced bare `/plan` `/build` `/test` `/review` with `/agtoosa-*` throughout `SECURITY.md` (DEV-116)
- Defined canonical approval and review artifacts for ship readiness gate (DEV-113)
- Bug report template updated to reference `--version` flag correctly

### Changed
- ~20% token reduction across all workflow markdown files (verbosity pass)
- `Docs/Master-Plan.md` established as the project-management source of truth for all tracking

---

## [2.1.0] — 2026-04-01

### Added
- Initial AgToosa framework: `agtoosa.sh` interactive generator
- Core workflow files: `AgToosa_Agent.md`, `AgToosa_Spec.md`, `AgToosa_Build.md`, `AgToosa_Review.md`, `AgToosa_Ship.md`, `AgToosa_Init.md`
- Platform entry points: `CLAUDE.md`, `.cursorrules`, `.windsurfrules`, `.github/copilot-instructions.md`, `AGENTS.md`
- `--force`, `--dry-run`, `--version`, `--help` flags
- `install.sh` deprecated stub directing users to `agtoosa.sh`

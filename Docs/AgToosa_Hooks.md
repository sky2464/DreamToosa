# AgToosa Hook Automation Pack

> Optional lifecycle-hook contract. Not a universal host interceptor.
> Companion: `Docs/AgToosa_GovernancePolicy.md` · Checker: `Docs/agtoosa-policy-check.sh`

## Objective

Catalog portable lifecycle events, map proven native hooks (Claude Code today), and provide agent-instructed checklist fallbacks everywhere else — with preview, explicit approval, secret-safe diagnostics, and DEV-059 policy linkage.

> **Claim Boundary:** Installing this guide through generator inventory is **generator-enforced**. Existing Claude settings/script files copied for a user-selected Claude install are **generator-enforced** for file installation only; host execution is not an AgToosa guarantee. Hook contract and merge-dedup checks when run in CI are **CI-enforced**. Event selection, fallback checklists, policy consultation, and preview preparation are **agent-instructed**. Approval, settings changes, removals, and acceptance of blocking behavior are **manual**. Universal native hooks or host-independent runtime interception remain **roadmap**.

Absence of this optional pack **must not** lower `/agtoosa-status` health and **must not** make `Docs/agtoosa-verify.sh` fail or warn. Declining install writes nothing and leaves health unchanged.

## HookEvent catalog

Every event row is a `HookEvent`: `{ event, purpose, availability, command_or_script, failure_behavior, enforcement_class }`.

| Event | Purpose | Availability | Example command / script | Failure behavior | Enforcement class |
|-------|---------|--------------|--------------------------|------------------|-------------------|
| `task-start` | Confirm Active Tasks / scope before coding | Checklist on all hosts; no proven native AgToosa mapping in v1 | Agent checklist: read Active Tasks + approved spec | `instruct_stop` until scope confirmed | agent-instructed |
| `pre-tool-use` | Guard dangerous tools before execution | **Native (Claude Code)** via `PreToolUse` + `.claude/hooks/block-dangerous-git.sh`; checklist elsewhere | `bash .claude/hooks/block-dangerous-git.sh` (stdin JSON) | Proven Claude host block (exit 2) or checklist `instruct_stop` | generator-enforced (file install) / host-proven block on Claude only |
| `post-tool-use` | Nudge after writes (e.g. 500-line soft limit) | **Native (Claude Code)** `PostToolUse` Write matcher; checklist elsewhere | Template PostToolUse line-count reminder | `warn` only | agent-instructed |
| `pre-test` | Confirm RED evidence / test command before GREEN | Checklist on all hosts | Agent checklist before first implementation | `instruct_stop` if RED missing when TDD on | agent-instructed |
| `post-test` | Record GREEN evidence / pass counts | Checklist on all hosts | Agent checklist after focused suite | `warn` if evidence incomplete | agent-instructed |
| `pre-ship` | Run ship readiness / verifier before deploy | Checklist on all hosts | `bash Docs/agtoosa-verify.sh` + `/agtoosa-ship check` | `instruct_stop` on FAIL | agent-instructed / CI-enforced when wired |
| `secret-check` | Ensure diagnostics and evidence redact secrets | Checklist on all hosts; Claude exemplar must stay secret-safe | Review hook/checklist output against safe-output rules | `instruct_stop` if raw secret would be emitted | agent-instructed |

## Platform matrix

| Event | Claude Code | Cursor | Gemini | Windsurf | Copilot | Codex / Other |
|-------|-------------|--------|--------|----------|---------|---------------|
| `task-start` | checklist only | checklist only | checklist only | checklist only | checklist only | checklist only |
| `pre-tool-use` | **native** (proven) | unavailable natively — checklist | unavailable natively — checklist | unavailable natively — checklist | unavailable natively — checklist | unavailable natively — checklist |
| `post-tool-use` | **native** (proven) | unavailable natively — checklist | unavailable natively — checklist | unavailable natively — checklist | unavailable natively — checklist | unavailable natively — checklist |
| `pre-test` | checklist only | checklist only | checklist only | checklist only | checklist only | checklist only |
| `post-test` | checklist only | checklist only | checklist only | checklist only | checklist only | checklist only |
| `pre-ship` | checklist only | checklist only | checklist only | checklist only | checklist only | checklist only |
| `secret-check` | checklist + exemplar safety | checklist only | checklist only | checklist only | checklist only | checklist only |

Unknown or unproven host support **defaults to checklist-only**. Do **not** claim Cursor, Gemini, Windsurf, Copilot, or Codex are natively hooked in v1.

Workflow adapters (Build/Ship/Init/Update) **point here**; they must not duplicate this matrix.

## HookInstallPreview and approval

Before any hook-related write, present a `HookInstallPreview`:

| Field | Content |
|-------|---------|
| `affected_files` | Exact repo-relative paths (e.g. `Docs/AgToosa_Hooks.md`, `.claude/settings.json`, `.claude/hooks/block-dangerous-git.sh`) |
| `existing_entries_preserved` | Unrelated settings keys and user commands that will remain |
| `entries_added` | AgToosa command strings to add |
| `entries_deduplicated` | Command strings already present (count) |
| `removal_steps` | How to remove AgToosa entries later without wiping user settings |

**Rules:**

- Show affected files and merge intent; require **explicit user approval** before any write.
- **No silent hook install.** Declining makes **no write** and does not affect health.
- Preserve unrelated user settings. Deduplicate AgToosa hook entries **by command string** (`merge_settings_json`).
- Documented removal: delete listed AgToosa command entries / optional exemplar script; leave unrelated settings intact. Users may also restore from `.bak.*` if created by a force path.

## Secret-safe diagnostics

Hooks and fallback commands **shall** limit diagnostics to: event name, policy rule ID, command name (tool name), path, and redacted reason.

**Prohibit** in output: secret values, tokens, private URLs, environment dumps, and raw tool-input payloads.

Exemplar (`block-dangerous-git.sh`) must not echo `$COMMAND` or `$CLAUDE_TOOL_INPUT`. Use bounded metadata only (e.g. `event=pre-tool-use`, `reason=dangerous_git_pattern`).

## DEV-059 policy linkage

When policy is configured, resolve through:

```bash
bash Docs/agtoosa-policy-check.sh [--root PATH] [--policy PATH]
```

Consume results as `{ policy_path, rule_id, enforcement_class, on_violation }` — **never** secret values.

Map `on_violation` exactly:

| `on_violation` | Hook / checklist behavior |
|----------------|---------------------------|
| `warn` | Record warning; continue |
| `instruct_stop` | Agent-instructed stop; do not claim a stronger host block |
| `block_generator` | Only for wired generator operations — **refuse to upgrade** `warn` or `instruct_stop` into an undocumented host-level block |

Hooks must not invent stronger enforcement than DEV-059 declares.

## Removal

1. List AgToosa command strings from the last approved preview.
2. Remove those entries from `.claude/settings.json` (Claude) or ignore checklist-only mappings.
3. Optionally remove `.claude/hooks/block-dangerous-git.sh` if no longer referenced.
4. Leave unrelated user settings and permissions untouched.
5. Confirm `/agtoosa-status` and `bash Docs/agtoosa-verify.sh` stay healthy without the pack.

# AgToosa Tracker Sync — Export and Proposal Bridge

Mirror AgToosa story state into external trackers **without** surrendering `docs/Master-Plan.md` authority. v1 is **one-way export** plus **proposal-only import** — not live API synchronization.

> **Authority:** `docs/Master-Plan.md` wins every conflict. External trackers are optional mirrors created only when the user explicitly asks. AgToosa does not call provider APIs in v1.

---

## Quick Start

**Export current story state (neutral JSON envelope):**
```bash
bash agtoosa.sh --tracker export --path /path/to/project --output /tmp/tracker-export.json
```

**Turn a returned tracker envelope into a reviewable proposal (no repo mutation):**
```bash
bash agtoosa.sh --tracker propose --path /path/to/project \
  --input /path/to/tracker-return.json \
  --output /tmp/tracker-proposal.md
```

**Publish GitHub Issues manifest from Master-Plan (local render; CI applies `gh`):**
```bash
bash agtoosa.sh --tracker publish --path /path/to/project \
  --output /tmp/issues-manifest.json \
  --readme README.md
```

**Community issue intake → backlog draft proposal:**
```bash
bash agtoosa.sh --tracker intake --path /path/to/project \
  --input /path/to/intake-envelope.json \
  --output /tmp/intake-proposal.md
```

**Brownfield discovery → bootstrap proposal (DEV-141):**
```bash
bash agtoosa.sh --tracker discover --path /path/to/project --output /tmp/discovery.json
# Optional: merge gh issue list JSON at discover time
bash agtoosa.sh --tracker discover --path /path/to/project \
  --input /tmp/gh-issues.json --output /tmp/discovery.json
bash agtoosa.sh --tracker bootstrap --path /path/to/project \
  --input /tmp/discovery.json --output /tmp/bootstrap-proposal.md
```

PowerShell (delegates to Bash — Git Bash or WSL required):
```powershell
.\agtoosa.ps1 -Tracker -TrackerCommand export -Path C:\Projects\MyApp -TrackerOutput $env:TEMP\export.json
```

Run `/agtoosa-tracker export`, `propose`, `publish`, `intake`, `discover`, `bootstrap`, or `status-check` in your AI assistant for the full workflow. Substantive rules live in this document; platform adapters delegate here.

**Status-check cache paths (DEV-143):** optional fetch artifacts for auto-merge (gitignored under `.agtoosa/`):

| Path | Format |
|------|--------|
| `.agtoosa/tracker/gh-issues.json` | `agtoosa.github-issues-fetch/v1` or raw `gh issue list --json` |
| `.agtoosa/tracker/linear-fetch.json` | `agtoosa.linear-fetch-envelope/v1` |

Refresh caches via `gh issue list`, Linear MCP export, or CI — AgToosa does not fetch them in core.

---

## Workflow: `/agtoosa-tracker status-check` (DEV-143)

1. Run local discovery (repo signals + repo-plans) — **no network calls**.
2. Auto-merge `.agtoosa/tracker/gh-issues.json` and `.agtoosa/tracker/linear-fetch.json` when present.
3. Classify items using DEV-141 bootstrap semantics; count only `new_external` as unlinked.
4. Emit `agtoosa.tracker-status-check/v1` JSON (`finding.emit` true when unlinked count > 0 and tracker context exists).

```bash
bash agtoosa.sh --tracker status-check --path /path/to/project
# optional: --output /tmp/status-check.json
```

`/agtoosa-status` invokes this CLI and surfaces an ℹ️ Info finding when `finding.emit` is true — **no health-score deduction**. Fix path: `discover` → `bootstrap` → `/agtoosa-task` for accepted rows.

---

## Workflow: `/agtoosa-tracker discover` (DEV-141)

1. Scan the repo for PM signals (`.github/ISSUE_TEMPLATE/`, `agtoosa-issues-sync` workflow, `ROADMAP.md`, `docs/plans/`, Linear references) — **no network calls**.
2. Parse repo-local plan markdown into `items[]` (`provider: repo-plans`).
3. Optionally merge `--input`:
   - `agtoosa.github-issues-fetch/v1` or raw `gh issue list --json` array
   - `agtoosa.linear-fetch-envelope/v1` (agent/MCP export)
4. Emit `agtoosa.tracker-discovery/v1` to `--output`.
5. Skip `agtoosa:DEV-*` / `source:agtoosa-sync` GitHub issues at merge time (already mirrored).

---

## Workflow: `/agtoosa-tracker bootstrap` (DEV-141)

1. Load discovery or `agtoosa.tracker-bootstrap-input/v1` (discovery + optional fetch envelopes).
2. Classify each item: `mirror_skip`, `new_external`, `repo_plan`, `closed_external`, `unchanged`, `unsupported`.
3. Assign draft IDs (`DRAFT-001`, …) for proposed backlog rows only.
4. Write Markdown proposal to `--output` with `/agtoosa-task` hints and suggested `tracker_mirror` workflow config.
5. Emit companion `agtoosa.tracker-bootstrap-proposal/v1` JSON (same basename as `.md` output) with per-item `accept: false` default.
6. **Never** modify `docs/Master-Plan.md` during bootstrap (proposal-only).

**Acceptance:** Review proposal JSON, set `accept: true` on chosen rows (or use `--apply-all-new-external`), then `bootstrap --apply` (DEV-145).

---

## Workflow: `/agtoosa-tracker bootstrap --apply` (DEV-145)

1. Load `agtoosa.tracker-bootstrap-proposal/v1` via `--input`.
2. Resolve accept set: rows with `accept: true`, plus all `new_external` when `--apply-all-new-external`.
3. **Dry-run default:** print unified diff of Master-Plan backlog changes; no mutation.
4. **`--yes`:** open DEV-119 transaction journal pre-image → append rows under `## Backlog` → commit journal.
5. Allocate next free `DEV-NNN` ID; normalize titles to GitHub-standard prefixes (`feat:`/`fix:`/`chore:`/`docs:`) — **no `DEV-` in Title column**.
6. Status column records `provider` + `external_ref` for traceability.

```bash
# Proposal (writes .md + .json)
bash agtoosa.sh --tracker bootstrap --path . \
  --input discovery.json --output bootstrap-proposal.md

# Dry-run apply
bash agtoosa.sh --tracker bootstrap --apply --path . \
  --input bootstrap-proposal.json

# Write accepted rows
bash agtoosa.sh --tracker bootstrap --apply --path . \
  --input bootstrap-proposal.json --yes

# Auto-accept all new_external
bash agtoosa.sh --tracker bootstrap --apply --path . \
  --input bootstrap-proposal.json --apply-all-new-external --yes
```

| Source signal | Master-Plan `Title` | `Type` column |
|---------------|---------------------|---------------|
| `feat:` / feature | `feat: <clean title>` | Feature |
| `fix:` / bug | `fix: <clean title>` | Bug |
| `chore:` / maintenance | `chore: <clean title>` | Chore |
| `docs:` | `docs: <clean title>` | Docs |
| No prefix | `feat: <clean title>` (default) | Feature |

Batch cap: 50 rows per apply invocation.

**Legacy acceptance:** `/agtoosa-task` or explicit edit remains valid for proposal-only bootstrap (DEV-141).

---

## Linear MCP bootstrap recipe (agent-instructed)

AgToosa does **not** call Linear APIs from the core generator. Use this agent/MCP path:

1. **Fetch** open issues from Linear (MCP or export) for the relevant team/project.
2. **Normalize** to `agtoosa.linear-fetch-envelope/v1`:

```json
{
  "schema_version": "agtoosa.linear-fetch-envelope/v1",
  "fetched_at": "2026-07-28T12:00:00Z",
  "team": "Platform",
  "issues": [
    {
      "identifier": "PLAT-12",
      "title": "Migrate billing webhooks",
      "state": "In Progress",
      "url": "https://linear.app/example/issue/PLAT-12"
    }
  ]
}
```

3. **Discover** with merge: `bash agtoosa.sh --tracker discover --path . --input linear-fetch.json --output discovery.json`
   - Or wrap in `agtoosa.tracker-bootstrap-input/v1` with a prior local `discovery` object.
4. **Bootstrap:** `bash agtoosa.sh --tracker bootstrap --path . --input discovery.json --output bootstrap-proposal.md`
5. **Accept** proposed rows via `/agtoosa-task`; record `tracker_mirror.provider: linear` in `Docs/Context/workflow.md` if continuing to mirror outbound.

Unmapped Linear fields (cycles, dependencies, custom fields) appear as `unsupported` in proposals — repo state unchanged.

---

## Workflow: `/agtoosa-tracker publish` (DEV-139)

1. Export Master-Plan stories via the DEV-051 envelope (local only).
2. Render `agtoosa.github-issues-manifest/v1` with GitHub-standard titles (`feat:`, `fix:`, `chore:`) — **no `DEV-XXX:` title prefix**.
3. Attach labels `agtoosa:DEV-XXX`, `source:agtoosa-sync`, status/area labels; upsert key is the `agtoosa:DEV-XXX` label + `<!-- agtoosa-story-id: DEV-XXX -->` body comment.
4. Optionally update the README `AGTOOSA-ROADMAP` block via `--readme`.
5. CI (`agtoosa-issues-sync.yml`) or `scripts/agtoosa-issues-sync.sh` applies the manifest with `gh` — **not** the core generator.

**Rows mirrored:** active cycle + non-shipped backlog. Shipped active-cycle rows emit `state: closed`.

---

## Workflow: `/agtoosa-tracker intake` (DEV-139)

1. Skip issues that already carry an `agtoosa:DEV-*` label (AgToosa-synced mirror).
2. Build `agtoosa.github-issues-intake/v1` envelope from the community issue.
3. Write a proposal artifact with a suggested Master-Plan backlog row and `/agtoosa-task` hint.
4. **Never** modify `docs/Master-Plan.md` during intake.
5. Maintainer accepts via `/agtoosa-task` or explicit edit; Issues sync runs on the next Master-Plan push to `main`.

---

## Workflow: `/agtoosa-tracker export`

1. Confirm the user wants a tracker mirror (not a replacement for Master-Plan).
2. Resolve the project path (explicit `--path` or current repo root).
3. Run the local export command — **no network calls**.
4. The bridge reads `docs/Master-Plan.md` and only spec files referenced by exported stories.
5. Stories are normalized and sorted by stable story ID; volatile fields (e.g. `generated_at`) are excluded from the export ID digest.
6. Write the `agtoosa.tracker-bridge/v1` JSON envelope to the explicit `--output` path.
7. Tell the user how to transport the envelope (manual upload, provider adapter, or MCP tool **outside** AgToosa).

**Export envelope fields (summary):** `schema_version`, `export_id`, `generated_at`, `repository`, `source` (commit + `master_plan_sha256`), `stories[]` with `story_id`, `title`, `epic`, `status`, `estimate`, `spec_path`, `acceptance_criteria`.

Full schema: `docs/agtoosa-tracker-sync.schema.json`.

---

## Workflow: `/agtoosa-tracker propose`

1. Require a return envelope that references a prior export (`base_export_id`).
2. Validate schema, story IDs, allowed fields, secret safety, and current `Master-Plan.md` digest.
3. For each change, compare **repo value** (authoritative) vs **proposed value** (external).
4. Write a Markdown proposal artifact to `--output` with disposition per item: `proposed`, `unchanged`, `stale`, `unsupported`, or `rejected`.
5. **Never** modify `docs/Master-Plan.md`, specs, or task checkboxes during propose.
6. Route accepted changes through existing AgToosa workflows (see **Proposal acceptance** below).

---

## Proposal acceptance

Accepted proposals **do not** auto-apply. Use one of:

| Change type | Route |
|-------------|-------|
| Status, estimate, backlog row, task checkbox | `/agtoosa-task` or explicit human edit to `docs/Master-Plan.md` |
| Spec content, ACs, design | `/agtoosa-spec amend` |
| New story | `/agtoosa-spec` (new story) |

After applying accepted changes, run a **fresh export** before the next tracker snapshot. External state never overwrites the repo implicitly.

---

## Provider field mappings (v1)

AgToosa defines **translation guidance only**. Transport and provider-side create/update/delete are **manual or provider-enforced** — not performed by the core bridge.

### GitHub Issues (first validated adapter)

| AgToosa field | GitHub Issues | Unsupported behavior |
|---------------|---------------|----------------------|
| `story_id` | Label `agtoosa:DEV-XXX` + HTML comment in body | **Not** in issue title |
| `title` | `feat:` / `fix:` / `chore:` / `docs:` + story title | DEV- prefix in title → rejected |
| `status` | Open / closed + `status-*` labels | Map lifecycle emojis to labels; shipped → closed |
| `estimate` | Issue body table field | S/M/L/XL in body |
| `epic` | `area-*` label heuristic | — |
| `spec_path` | Issue body link | — |
| `acceptance_criteria` | Issue body checklist (read-only mirror) | No AC round-trip in v1 |
| Community intake | `source:community` label; intake proposal | No auto backlog write |

### Linear

| AgToosa field | Linear | Unsupported behavior |
|---------------|--------|----------------------|
| `story_id` | Issue identifier suffix or custom label | — |
| `title` | Issue title | — |
| `status` | Workflow state (Backlog, In Progress, Done, …) | Unmapped states → `unsupported` |
| `estimate` | Estimate points or t-shirt label | Non-numeric estimates → `unmapped` |
| `epic` | Project or cycle | — |
| `spec_path` | Description link | — |
| `acceptance_criteria` | Description section | No comment round-trip in v1 |

### Jira

| AgToosa field | Jira | Unsupported behavior |
|---------------|------|----------------------|
| `story_id` | Issue key suffix or label | — |
| `title` | Summary | — |
| `status` | Status (To Do, In Progress, Done, …) | Custom workflows → map or `unsupported` |
| `estimate` | Story points or original estimate | — |
| `epic` | Epic link | — |
| `spec_path` | Description link | — |
| `acceptance_criteria` | Description or custom field | Custom fields not auto-synced |

### TaskMaster

| AgToosa field | TaskMaster | Unsupported behavior |
|---------------|------------|----------------------|
| `story_id` | Task `id` | — |
| `title` | Task `title` | — |
| `status` | `pending` / `in-progress` / `done` | Other statuses → `unsupported` |
| `estimate` | `metadata.estimate` or priority | — |
| `epic` | `metadata.epic` or parent task | — |
| `spec_path` | `metadata.spec_path` | — |
| `acceptance_criteria` | `details` checklist | No dependency round-trip in v1 |

When a provider field has no AgToosa equivalent, preserve the original value in proposal diagnostics as `unmapped` and leave repo state unchanged.

---

## Claim Boundary (v1)

| Surface | Classification | Boundary |
|---------|----------------|----------|
| Schema validation, digest, mutation refusal | generator-enforced | Local files only |
| `/agtoosa-tracker export` and `propose` workflow | agent-instructed | This document is canonical |
| `/agtoosa-tracker publish` manifest render | generator-enforced | Local files only |
| `/agtoosa-tracker intake` proposal render | generator-enforced | Local files only |
| `/agtoosa-tracker discover` local scan | generator-enforced | Repo signals only; no network |
| `/agtoosa-tracker bootstrap` proposal render | generator-enforced | Local files only; no Master-Plan mutation |
| Linear/GitHub fetch via MCP or `gh` | manual / agent-instructed | Outside core generator |
| `agtoosa-issues-sync.yml` gh upsert | provider-enforced | GitHub Actions + `GITHUB_TOKEN` |
| `agtoosa-issues-intake.yml` comment + artifact | provider-enforced | GitHub Actions |
| Provider field mapping tables | agent-instructed | Translation guidance, not API guarantee |
| Transporting envelopes to/from trackers | manual / provider-enforced | Human, provider tool, or authorized integration |
| Accepting a proposal | manual authorization | `/agtoosa-task`, `/agtoosa-spec amend`, or explicit edit |
| Live bidirectional webhook sync | **roadmap (Phase 3)** | Do not claim silent two-way sync |
| `docs/Master-Plan.md` | repo-local source of truth | Wins every tracker conflict |

**Core generator does not:**

- Call GitHub, Linear, Jira, or TaskMaster APIs directly
- Store OAuth tokens or API credentials
- Auto-apply returned status or title changes without human approval
- Do not claim two-way sync or live provider API synchronization from the core bridge

**CI may (opt-in):**

- Upsert GitHub Issues from a publish manifest when `agtoosa-issues-sync.yml` is enabled

---

## Doctor finding GIP-003 (DEV-147)

When `.github/workflows/agtoosa-issues-sync.yml` is present but `scripts/agtoosa-issues-sync.sh` is missing or drifts from `template/scripts/agtoosa-issues-sync.sh` on the maintainer repo, doctor emits **GIP-003** (Warn) with a guided fix hint. No finding is emitted when the workflow is absent (opt-in surface).

**Runtime layout:** `scripts/agtoosa-issues-sync.sh` is a thin entrypoint that sources `lib/github-issues-sync.sh`. Both must exist in the project — copy from `template/scripts/` and `template/lib/` when enabling the workflow. The script fails fast with a copy hint when `lib/github-issues-sync.sh` is missing.

```bash
# Enable issues sync in a downstream project
cp template/scripts/agtoosa-issues-sync.sh scripts/
mkdir -p lib
cp template/lib/github-issues-sync.sh lib/
# Copy .github/workflows/agtoosa-issues-sync.yml.example → .github/workflows/agtoosa-issues-sync.yml
```

Bats coverage: `GIP-001`–`GIP-010` in `tests/agtoosa.bats` (mock `gh` via `GH_CMD` / `tests/fixtures/tracker-sync/issues-sync/mock-gh.sh`).

---

## Security

- Treat every return envelope as **untrusted input**.
- Redact or reject credentials, token-bearing URLs, absolute local paths, and control characters.
- Bound file size and record count before parsing oversized returns.
- Proposal output must not alias `docs/Master-Plan.md` or other source files.

---

## Related

- **PM source of truth:** `docs/Master-Plan.md`
- **Fast backlog edits:** `docs/AgToosa_Task.md`
- **Spec amendments:** `docs/AgToosa_Spec.md` (`amend` sub-command)
- **Envelope schema:** `docs/agtoosa-tracker-sync.schema.json`
- **Issues sync script:** `scripts/agtoosa-issues-sync.sh` (sources `lib/github-issues-sync.sh`)
- **Issues sync lib:** `lib/github-issues-sync.sh` (copy from `template/lib/` when enabling the workflow)
- **CI workflows:** `.github/workflows/agtoosa-issues-sync.yml`, `.github/workflows/agtoosa-issues-intake.yml`

# AgToosa /agtoosa-evidence Workflow

## Sub-Commands

| Sub-command | Runs |
|-------------|------|
| `/agtoosa-evidence` | Create or update the per-story evidence ledger from current test-plan / review / ship artifacts |
| `/agtoosa-evidence review` | Review-phase update only (called from `/agtoosa-review`) |
| `/agtoosa-evidence ship` | Ship-phase finalize only (called from `/agtoosa-ship`) |

## Objective

Maintain a **per-story evidence ledger** — a concise, auditable proof index for files, tests, logs, PRs, screenshots, and review notes — so every shipped story has a durable trail without a hosted audit service.

> **Prerequisites:** Active story with approved spec. Prefer existing RED/GREEN/IMPORT evidence in the story test plan and the review report path.
>
> **Claim Boundary:** This workflow is **agent-instructed** (not generator-enforced). Verifier WARN/FAIL for missing ledgers is **roadmap**. The optional JSONL mirror is **non-authoritative**.
>
> **Source of truth:** `Docs/Master-Plan.md` remains the repo-local source of truth. The markdown ledger is the canonical index; `Docs/agtoosa-evidence.jsonl` is an optional tooling mirror.
>
> **Delivery profiles:** Class minimums (`standard`, `security-sensitive`, `release`) and Guided / Evidenced / Enforced labels are defined in `Docs/AgToosa_Delivery_Evidence_Contract.md` (optional `.agtoosa/evidence.yml`). Ledger rows still consolidate at review/ship — profiles declare *what* to collect; this workflow indexes *pointers*.
>
> **Evidence Provenance v2 (optional):** At review/ship, agents may assemble `Docs/archived/proof-graph-<story-id>.json` per `Docs/AgToosa_Evidence_Provenance.md` and verify with `bash Docs/agtoosa-proof-verify.sh --root . --graph Docs/archived/proof-graph-<story-id>.json`. Gate 7 profile presence is unchanged; content-link binding is Provenance v2 / standalone script scope.

## When to update

| Gate | Action |
|------|--------|
| `/agtoosa-review` | Create or update `Docs/archived/evidence-[story-id].md` with `phase=review` rows |
| `/agtoosa-ship` | Finalize the same file with `phase=ship` rows before marking Shipped |
| `/agtoosa-build` / `/agtoosa-import` | Do **not** write the ledger live — keep writing test-plan / IMPORT evidence; consolidate at review/ship |

## Markdown schema (canonical)

Write to `Docs/archived/evidence-[story-id].md` (sanitize story-id to `[A-Za-z0-9._-]+`):

```markdown
# Evidence Ledger — [Story ID]

> **Story:** [ID] — [title]
> **Claim Boundary:** agent-instructed index; Master-Plan remains SoT
> **Updated:** [YYYY-MM-DD HH:MM] ([review|ship])

| Phase | AC | Artifact | Pointer | Verification | Exit | Reviewer | ts |
|-------|----|----------|---------|--------------|------|----------|-----|
| review | AC-001 | test-log | Docs/AgToosa_TestPlan-….md#GREEN | bats … -f "…" | 0 | AgToosa | ISO-8601 |
```

**Required columns:** Phase (`review` \| `ship`), AC, Artifact, Pointer, Verification, Exit, Reviewer, ts.

**Artifact types:** `test-log` · `review` · `cross-model` · `pr` · `branch` · `screenshot` · `spec` · `verifier` · `release` · `other`

**Ship-phase `release` row (when `deploy_command` is documented in Context tech-stack):** Record remote publication evidence — not changelog grep alone. Required verification: `gh release view v$VERSION` exit 0 **and** a CI/workflow run URL (or `deploy_verify` command output). Pointer should cite the GitHub release URL. Do not mark `release` PASS from local version pins or Master-Plan rows alone.

**Cross-model row (review phase):** When `/agtoosa-review cross-model` runs or is skipped with rationale, add a row with `artifact=cross-model`, pointer to `docs/archived/review-[story-id].md## Cross-Model Review`, and verification noting workflow policy (`cross_model`, `reviewer_model`), consent (`stated` / `user-approved` / `skipped`), reviewer identity, outcome (`completed` / `fallback` / `skipped`), and skip rationale when applicable.

## Optional JSONL mirror (non-authoritative)

When useful, append one JSON object per new ledger row to `Docs/agtoosa-evidence.jsonl`:

```json
{"ts":"ISO-8601","story":"DEV-049","phase":"review","ac":["AC-001"],"artifact":"test-log","pointer":"…","verification":"…","exit":0,"reviewer":"AgToosa"}
```

Never treat JSONL as overriding the markdown file.

## Workflow

1. **Resolve story** — Active Cycle ID; if multiple, ask which.
2. **Collect pointers** — From story test plan (RED/GREEN/IMPORT), review report path, verifier/smoke commands.
3. **Write/update markdown** — Merge rows; do not delete prior review rows when shipping.
4. **Optional JSONL** — Append new rows only.
5. **Secret safety** — Cite paths and command names only; **redact** tokens, API keys, passwords, private URLs.
6. **Phase event** — Append to `Docs/agtoosa-events.jsonl`:
   `{"ts":"[ISO-8601 UTC]","phase":"evidence","event":"update","story":"[Story ID]","by":"AgToosa"}`

## Output

* Print the evidence file path and row count.
* Print the dual-line phase close per Docs/AgToosa_Agent.md → Lifecycle Next-Step Contract

## Rules

1. **Markdown is canonical.** JSONL is optional and non-authoritative.
2. **Honest claims.** Never describe the ledger as generator-enforced or CI-enforced in v1.
3. **No hosted audit log.** Repo-local files only.
4. **Consolidate at review/ship** — not during build/import.
5. **Secret safety** — paths/process only; sanitize story-id in filenames.

## Optional proof graph assembly (DEV-120)

At `/agtoosa-review` or `/agtoosa-ship`, agents **may** extend the evidence ledger with a derived proof graph:

1. Read `Docs/archived/evidence-[story-id].md` and cited artifact paths.
2. Compute SHA-256 for each cited file; record `git rev-parse HEAD` as `repo-snapshot`.
3. Write `Docs/archived/proof-graph-[story-id].json` per `Docs/AgToosa_Evidence_Provenance.md`.
4. Verify with `bash Docs/agtoosa-proof-verify.sh --graph <path> [--allow-stale-snapshot]`.
5. Add a ledger row with verification command and exit code.

Proof graphs are **derived evidence** — they do not replace this ledger or `Docs/Master-Plan.md`.

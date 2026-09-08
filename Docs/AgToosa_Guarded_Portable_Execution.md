# AgToosa Guarded Portable Execution v1

> **Distinct from:** Evidence Provenance proof graphs (DEV-120), Change-Aware Adaptive Delivery drift (DEV-122), async handoff packs (DEV-047), and agent result import (DEV-048).

## Purpose

Guarded Portable Execution (GPE) provides **execution capsules** — portable, policy-bounded work units that carry approved scope, ownership, budgets, verification commands, and a safe return contract so external or async agents can execute bounded work and return evidence for `/agtoosa-import` without silent scope creep.

**Source of truth:** `Docs/Master-Plan.md` remains the repo-local authority. Capsules and return envelopes are **derived execution contracts** — they do not replace Master-Plan, proof graphs, drift reports, or evidence ledgers.

## Capsule vs return

| Artifact | Role | CI default |
|----------|------|------------|
| `execution-capsule-v1` JSON | Declares scope, policy, budgets, verification, return contract | **No** — optional pre-execution pack |
| `capsule-return-v1` JSON | Agent-returned evidence envelope for import review | **No** — validated locally before import |

**Claim boundary:** A valid capsule proves **declared scope and policy at pack time** — not that an external agent ran, that verification passed, or that work is import-ready until return validation succeeds. Capsules do **not** claim native sandboxing, agent launch, or supervision.

## Execution capsule

Schema: `data/contracts/execution-capsule-v1.schema.json`.

| Field | Meaning |
|-------|---------|
| `version` | Schema version (`1`) |
| `capsule_id` | Stable capsule identifier |
| `story_id` | Active story reference |
| `created_at` | ISO-8601 UTC pack timestamp |
| `ownership` | `owner` (required), optional `team`, `exported_by` |
| `scope.allowed_paths` | Repo-relative paths the executor may change |
| `scope.forbidden_paths` | Repo-relative paths that must not change |
| `policy.network` | `deny` (default guarded) or `allow` |
| `policy.secrets` | `forbid` (default guarded) or `allow` |
| `budgets.max_files_changed` | Upper bound on `changed_files` in return |
| `budgets.max_verification_commands` | Upper bound on `verification_results` in return |
| `verification.commands[]` | Allowed verification commands (`command`, optional `description`, `expected_exit_code`) |
| `return_contract` | Required return schema and fields |
| `provenance` | Optional pointers to `handoff_path`, `proof_graph_path`, `drift_report_path` |

### Path safety

All repo-relative paths reject leading `/` and `..` traversal. Helpers live in `lib/capsule.sh`.

## Return envelope

Schema: `data/contracts/capsule-return-v1.schema.json`.

| Field | Meaning |
|-------|---------|
| `version` | Schema version (`1`) |
| `capsule_id` | Must match parent capsule |
| `returned_at` | ISO-8601 UTC return timestamp |
| `changed_files[]` | Repo-relative paths changed during execution |
| `verification_results[]` | `command`, `exit_code`, optional `stdout_excerpt` |
| `mapped_acs[]` | `ac_id` → `evidence` pointers for import |
| `import_ready` | `true` only when validation passes with zero violations |
| `violations[]` | Optional recorded violations when `import_ready` is `false` |

Return validation (`capsule_validate_return`) checks scope, budgets, policy (network deny), return-contract fields, and `import_ready` consistency.

## Manual handoff exporter

Pack a capsule from an existing handoff markdown or JSON:

```bash
# shellcheck source=lib/capsule.sh
source lib/capsule.sh
# shellcheck source=lib/capsule-exporters/manual-handoff.sh
source lib/capsule-exporters/manual-handoff.sh

capsule_pack_from_handoff "." "tests/fixtures/capsule/handoff-source.md" /tmp/capsule.json
capsule_validate_capsule "." /tmp/capsule.json
```

Exporter v1: **`manual-handoff`** — parses handoff §3 Files in Scope and §5 Verification Commands; applies default guarded policy (`network: deny`, `secrets: forbid`).

## Optional pre-execution workflow

Before launching an external agent:

1. Export handoff via `/agtoosa-handoff` (DEV-047).
2. Pack execution capsule via `manual-handoff` exporter.
3. Optionally attach provenance pointers from DEV-120 proof graphs or DEV-122 drift reports.
4. On return, validate return envelope before `/agtoosa-import`.

## Forbidden claims

- Native OS sandbox or container isolation from capsule JSON alone
- Automatic agent launch, supervision, or bounded autonomous runner
- Secret values in capsule or return fixtures
- Default network access in guarded policy mode
- Protected-workflow writes (Master-Plan status) from capsule validation
- Mandatory capsule gate in default CI

## Claim Boundary summary

| Control | Classification |
|---------|----------------|
| This contract + JSON schemas | generator-enforced file inventory |
| `lib/capsule.sh` validators | local machine check |
| `manual-handoff` exporter | agent-instructed — output JSON only |
| Return `import_ready` | derived from validation — not import authority |
| Proof graph integrity | DEV-120 separate verify |
| Drift impact | DEV-122 separate assess |
| Master-Plan authority | repo-local SoT — capsules are derived |

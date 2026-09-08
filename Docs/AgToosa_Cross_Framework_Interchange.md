# AgToosa Cross-Framework Interchange v1

> **Distinct from:** Evidence Provenance proof graphs (DEV-120), Guarded Portable Execution capsules (DEV-123), Change-Aware Adaptive Delivery drift (DEV-122), and agent result import gate (DEV-048).

## Purpose

Cross-Framework Interchange (CFI) provides a **normalized interchange manifest**, **explicit loss report**, and **fixture-based providers** for Spec Kit, OpenSpec, BMAD, and Kiro-style (`SPEC-FORMAT.md`) specs so maintainers can export AgToosa stories to framework-shaped artifacts and import external fixtures with machine-readable honesty about unmappable fields.

**Source of truth:** `Docs/Master-Plan.md` remains the repo-local authority. Interchange manifests and loss reports are **derived artifacts** — they do not replace Master-Plan, proof graphs, evidence ledgers, or verifier gates.

## Export vs import

| Artifact | Role | CI default |
|----------|------|------------|
| `interchange-manifest-v1` JSON | Normalized story requirements/tasks with preserved source IDs | **No** — optional export/import |
| `interchange-loss-report-v1` JSON | Records unmappable fields with `low` or `high` severity | **No** — companion to import |

**Claim boundary:** A valid interchange manifest proves **normalized field mapping at export/import time** — not perfect round-trip fidelity, framework replacement, or Master-Plan authority transfer. Loss entries are **fixture-labeled** representatives — not live framework telemetry.

## Interchange manifest

Schema: `data/contracts/interchange-manifest-v1.schema.json`.

| Field | Meaning |
|-------|---------|
| `version` | Schema version (`1`) |
| `story_id` | Active story reference |
| `source_framework` | `speckit` · `openspec` · `bmad` · `kiro` · `agtoosa` |
| `source_ids` | Preserved framework identifiers (non-empty object) |
| `authority.owner` | `master-plan` (AgToosa export) or `imported-derived` (fixture import) |
| `authority.preserved` | Whether Master-Plan SoT authority is preserved (`true` on export only) |
| `requirements[]` | Normalized acceptance criteria (`id`, `kind`, `text`, optional `priority`) |
| `tasks[]` | Normalized task tree entries (`id`, `text`, optional `completed`) |
| `provenance` | Optional `spec_path`, `proof_graph_path`, `fixture_path`, timestamps |

### Path safety

All repo-relative paths reject leading `/` and `..` traversal. Helpers live in `lib/interchange.sh`.

## Loss report

Schema: `data/contracts/interchange-loss-report-v1.schema.json`.

| Field | Meaning |
|-------|---------|
| `version` | Schema version (`1`) |
| `story_id` | Story reference |
| `source_framework` | Originating framework |
| `entries[]` | `field`, `reason`, `severity` (`low` · `high`) |

### Loss matrix (v1)

| AgToosa field | Framework gap | Severity |
|---------------|---------------|----------|
| `authority.owner` | External fixtures cannot assert Master-Plan SoT | `high` |
| `authority.preserved` | Import does not preserve PM checkbox/status authority | `high` |
| `requirements.threat_model` | Spec Kit / OpenSpec shapes omit STRIDE section | `low` |
| `requirements.ears_text` | BMAD IDs without full EARS text | `low` |
| `requirements.priority` | OpenSpec scenarios lack Must/Should labels | `low` |
| `tasks.wave_plan` | OpenSpec proposals omit AgToosa wave plan | `low` |
| `provenance.interview_findings` | Plan-Mode Spec Interview block not in fixtures | `low` |
| `sections.interview_findings` | Kiro-style frozen fixtures may omit live interview block | `low` |

### Assess behavior

`interchange_assess_loss_report` (used by `agtoosa-interchange-assess.sh`):

- **Default (suggest-only):** exit `0` on `low` severity; exit non-zero on schema failures or `high` authority violations.
- **`--strict`:** exit non-zero when any `high` severity entry is present.

## Providers (fixture-based v1)

| Provider | Export | Import fixture |
|----------|--------|----------------|
| `speckit` | `lib/interchange-providers/speckit.sh` | `tests/fixtures/interchange/speckit/minimal.json` |
| `openspec` | `lib/interchange-providers/openspec.sh` | `tests/fixtures/interchange/openspec/minimal.json` |
| `bmad` | `lib/interchange-providers/bmad.sh` | `tests/fixtures/interchange/bmad/minimal.json` |
| `kiro` | `lib/interchange-providers/kiro.sh` | `tests/fixtures/interchange/kiro/minimal.json` |

Export reads archived AgToosa spec markdown (`Docs/archived/spec-<story>.md`). Import reads frozen JSON fixtures — **no** `uvx`, `npx`, or remote API calls.

### Parse spec helpers

```bash
# shellcheck source=lib/interchange.sh
source lib/interchange.sh
interchange_parse_spec Docs/archived/spec-DEV-120.md
```

Parses acceptance criteria from §1.2 EARS table and tasks from §3.1 task tree.

## Optional proof graph binding

When export references a proof graph, validate separately via DEV-120:

```bash
bash Docs/agtoosa-proof-verify.sh --graph Docs/archived/proof-graph-DEV-120.json
```

A proof graph pointer on the manifest **does not** auto-mark interchange as verified.

## Forbidden claims

- Perfect round-trip fidelity between AgToosa and external frameworks
- Replacing Spec Kit, OpenSpec, BMAD, or Kiro tooling
- Required network access or live framework installs in v1
- Protected-workflow writes (Master-Plan checkboxes) from import
- Mandatory interchange gate in default CI
- Loss report entries as live framework telemetry

## Claim Boundary summary

| Control | Classification |
|---------|----------------|
| This contract + JSON schemas | generator-enforced file inventory |
| `lib/interchange.sh` validators | local machine check |
| Provider export/import | agent-instructed — derived JSON only |
| Loss report `high` authority entries | fixture-labeled — not PM authority |
| `--strict` non-zero exit | opt-in maintainer gate |
| Proof graph integrity | DEV-120 separate verify |
| Master-Plan authority | repo-local SoT — interchange is derived |

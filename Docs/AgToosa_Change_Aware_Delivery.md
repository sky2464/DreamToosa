# AgToosa Change-Aware Adaptive Delivery v1

> **Distinct from:** Evidence Provenance proof graphs (DEV-120), Behavioral Conformance scenario runs (DEV-121), brownfield baselines (DEV-043), and verifier Gate 7/8.

## Purpose

Change-Aware Adaptive Delivery (CAD) provides a **frozen allowlist baseline**, **drift impact report**, **adaptive rigor suggestions**, and **provenance-aware context compilation** so maintainers and agents can adapt testing depth before `/agtoosa-build` without mandatory blocking.

**Source of truth:** `Docs/Master-Plan.md` remains the repo-local authority. Drift reports and context-compilation JSON are **derived evidence** — they do not replace Master-Plan, proof graphs, or evidence ledgers.

## Assess vs compile

| Tool | Role | CI default |
|------|------|------------|
| `Docs/agtoosa-drift-assess.sh` | Compare baseline hashes to files at `--root`; emit drift report | **No** — optional pre-build; bats on fixtures only |
| `Docs/agtoosa-context-compile.sh` | Merge story id, optional proof graph, optional drift report into context JSON | **No** — agent-instructed |

**Claim boundary:** Passing drift assess proves **allowlisted path inventory drift** at assessment time — not semantic correctness, vulnerability absence, or production accuracy. Measured error rates in the `measurement` block are **fixture-labeled only**.

## Drift baseline

Frozen allowlist at `tests/fixtures/drift-assess/baseline-v1.json` (maintainer pilot) or project-specific baselines conforming to `data/contracts/drift-baseline-v1.schema.json`.

Each path entry records:

| Field | Meaning |
|-------|---------|
| `path` | Repo-relative allowlisted path (no `..`, no leading `/`) |
| `sha256` | Expected content fingerprint |
| `impact_level` | `low` · `medium` · `high` |

## Drift report

Schema: `data/contracts/drift-report-v1.schema.json`. Provider v1: **`git-inventory`** (local file inventory only).

Report sections:

- `summary` — counts of added, removed, modified, unchanged allowlisted paths
- `overall_impact_level` — `none` · `low` · `medium` · `high`
- `suggested_rigor` — derived from impact matrix below
- `changes` — per-path lists (allowlist only)
- `measurement` — optional fixture-labeled FP/FN rates (not live metrics)

### Adaptive rigor matrix

| `overall_impact_level` | `suggested_rigor` |
|------------------------|-------------------|
| `none`, `low` | `light` |
| `medium` | `standard` |
| `high` | `elevated` |

Suggestions inform depth only. **`--strict`** is an opt-in maintainer gate: exit non-zero when any allowlisted path has `impact_level: high` and content drift is detected.

## Context compilation

```bash
bash Docs/agtoosa-context-compile.sh --story DEV-120 \
  --proof-graph Docs/archived/proof-graph-DEV-120.json \
  --drift-report drift-report.json \
  --output tests/fixtures/drift-assess/context-compilation-DEV-120.json
```

Schema: `data/contracts/context-compilation-v1.schema.json`.

When `proof_graph_path` is set, validate separately:

```bash
bash Docs/agtoosa-proof-verify.sh --graph <path>
```

A valid proof graph **does not** auto-mark context compilation as verified — `proof_graph_verified` remains `false` until a separate verify run is recorded.

## Optional pre-build workflow

Before `/agtoosa-build` Wave 1:

1. Run `agtoosa-drift-assess.sh` against the project baseline (default: suggest-only, exit 0).
2. Optionally run `agtoosa-context-compile.sh` for the active story.
3. Read `suggested_rigor` when planning test depth — do not treat suggestions as Master-Plan mutations.

## Forbidden claims

- Mandatory drift gate in default CI (suggest-only unless `--strict` is explicitly opted in)
- Live production false-positive/negative accuracy without fixture labels
- Context compilation replacing `Master-Plan.md` or auto-editing task trees
- Semantic-quality or NL understanding claims
- Gate 7 / Gate 8 enforcement from this document alone

## Claim Boundary summary

| Control | Classification |
|---------|----------------|
| This contract + JSON schemas | generator-enforced file inventory |
| `agtoosa-drift-assess.sh` | local machine check — suggest by default |
| `--strict` non-zero exit | opt-in maintainer gate |
| `agtoosa-context-compile.sh` | agent-instructed — output JSON only |
| Measured error rates | fixture-labeled only |
| Proof graph integrity | DEV-120 separate verify |
| Master-Plan authority | repo-local SoT — compilation is derived |

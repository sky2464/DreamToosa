# AgToosa Evidence Provenance v2 (Delivery Proof Fabric)

> **Distinct from:** Delivery Evidence profiles (DEV-087 / Gate 7), Terminal Evidence (per-task output), and registry minisign provenance (DEV-054).
>
> **Maintainer mirror:** Generated projects install this as `Docs/AgToosa_Evidence_Provenance.md`. Template source: `template/Docs/AgToosa_Evidence_Provenance.md`.

## Purpose

Evidence Provenance v2 binds delivery evidence **pointers** to **content fingerprints** and an optional **repo snapshot** through a derived proof graph. It answers: “Do the artifacts cited in the evidence ledger still match the bytes and repo context recorded at review/ship time?”

**Source of truth:** `Docs/Master-Plan.md` remains the repo-local authority. Proof graphs are **derived, non-authoritative** indexes — they do not replace the evidence ledger, delivery profiles, or Master-Plan.

## Node types (v1)

| Type | Role | Required fields |
|------|------|-----------------|
| `story` | Story identifier anchor | `id`, `type`, `ref` (story id) |
| `ac` | Acceptance criterion anchor | `id`, `type`, `ref` (AC id) |
| `artifact` | Durable evidence file path (repo-relative) | `id`, `type`, `ref` |
| `command-run` | Verification command recorded at review/ship | `id`, `type`, `ref`, optional `exit_code` |
| `content-hash` | SHA-256 of artifact bytes | `id`, `type`, `ref`, `sha256` |
| `repo-snapshot` | Git commit at graph generation | `id`, `type`, `sha` |

## Edge types (v1)

| Type | Meaning | Typical endpoints |
|------|---------|-------------------|
| `references` | Logical association | `story` → `ac`; `ac` → `artifact` |
| `content-of` | Byte binding | `artifact` → `content-hash` |
| `verified-by` | Command attestation | `command-run` → `artifact` |

## Proof graph file

One JSON file per story:

```
Docs/archived/proof-graph-<story-id>.json
```

Schema: `data/contracts/proof-graph-v1.schema.json` (v1). Required top-level fields: `version`, `story_id`, `provider`, `nodes`, `edges`.

## Proof-provider interface

| Field | Contract |
|-------|----------|
| Provider id | Stable string (v1 pilot: `local-hash`) |
| Supported nodes | Subset of v1 node types the provider can verify |
| Supported edges | Subset of v1 edge types the provider can verify |
| Inputs | Repo root path, graph JSON path, options |
| Outputs | stdout summary on success; stderr diagnostic on first failure |
| Exit codes | `0` valid · `1` validation failure · `2` usage/setup error |

**`local-hash` provider (built-in pilot):**

- Verifies `content-of` edges by SHA-256 of repo-relative artifact paths.
- Verifies `verified-by` edges require a `command-run` node with a non-empty `ref` (verification string). The script does **not** re-execute commands in v1.
- Verifies `repo-snapshot` against `git rev-parse HEAD` unless `--allow-stale-snapshot` is passed.
- Network-free; no external tools beyond `git` and `python3`.

Future providers (roadmap — not DEV-120): external attestors, reproducible build hashes.

## Scenario-run linkage (DEV-121)

Behavioral Conformance Lab `scenario-run.json` files may include optional `proof_graph_path`. Validate the graph separately with `agtoosa-proof-verify.sh`. A passing proof graph **does not** upgrade Scenario-tested tier or behavioral claims automatically. See `Docs/AgToosa_Behavioral_Conformance.md`.

## Drift and context compilation linkage (DEV-122)

Change-Aware Adaptive Delivery drift reports may be cited from `context-compilation-v1` JSON produced by `agtoosa-context-compile.sh`. Drift assess is **suggest-only** by default; validate proof graphs separately with `agtoosa-proof-verify.sh`. See `Docs/AgToosa_Change_Aware_Delivery.md`.

## Verification script

```bash
bash Docs/agtoosa-proof-verify.sh --root PATH --graph Docs/archived/proof-graph-<story-id>.json
```

Options:

| Flag | Effect |
|------|--------|
| `--allow-stale-snapshot` | Skip strict HEAD match for `repo-snapshot` nodes |
| `--provider local-hash` | Default; only provider in v1 |

**Claim boundary:** Passing verification proves **local content-link integrity** at verification time — not semantic correctness, vulnerability absence, or hosted attestation.

## Relationship to other surfaces

| Surface | Role | DEV-120 boundary |
|---------|------|------------------|
| **Evidence Ledger** (`AgToosa_Evidence.md`) | Pointer index at review/ship | Graph assembly is optional, agent-instructed extension |
| **Delivery Evidence Contract** (DEV-087) | Profile vocabulary; Gate 7 presence | Profiles unchanged; content binding is Provenance v2 |
| **Gate 7** (DEV-089) | Opt-in profile artifact presence | **Not modified** — Gate 8 integration deferred |
| **Terminal Evidence** | Per-task command output | Unchanged |
| **Registry minisign** (DEV-054) | Pack/release signatures | Separate trust domain |

## Assembly workflow (agent-instructed)

At `/agtoosa-review` or `/agtoosa-ship`, agents may:

1. Read `Docs/archived/evidence-<story-id>.md` and referenced artifact paths.
2. Compute SHA-256 for each cited file.
3. Record `git rev-parse HEAD` as `repo-snapshot`.
4. Write `Docs/archived/proof-graph-<story-id>.json` conforming to the schema.
5. Run `agtoosa-proof-verify.sh` and record command + exit in the evidence ledger.

Do **not** store secrets, tokens, or passwords in graph JSON.

## Forbidden claims

- Natural-language or formal proof of correctness
- Replacing `Master-Plan.md`, evidence ledgers, or `.agtoosa/evidence.yml` profiles
- Mandatory Dafny, Nx, or external provider
- Gate 7 / Gate 8 enforcement from this document alone (Gate 8 = roadmap)

## Claim Boundary summary

| Control | Classification |
|---------|----------------|
| This contract + JSON schema | generator-enforced file inventory |
| `agtoosa-proof-verify.sh` | local machine check |
| Graph assembly | agent-instructed |
| Gate 7 profile checks | unchanged (DEV-089) |
| Verifier Gate 8 hook | roadmap |

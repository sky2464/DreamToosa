# AgToosa Behavioral Conformance Lab v1

> **Distinct from:** Assistant Compatibility tiers (DEV-094), static product-truth claims (DEV-118), and Evidence Provenance proof graphs (DEV-120).

## Purpose

The Behavioral Conformance Lab (BCL) provides a **versioned scenario corpus** and **scenario-run evidence format** so maintainers can record reproducible behavioral proof tasks across adapter platforms. BCL answers: “Did a fixed proof task produce the expected workflow artifacts for this platform?”

**Source of truth:** `Docs/Master-Plan.md` remains the repo-local authority. Scenario-run JSON is **derived evidence** — it does not replace compatibility tiers, pack SHA validation, or proof graphs.

## Runner vs verifier

| Tool | Role | CI default |
|------|------|------------|
| `Docs/agtoosa-scenario-run.sh` | Prints maintainer steps, runs verifier, writes `scenario-run.json` | **No** — maintainer manual / scheduled |
| `Docs/agtoosa-scenario-verify.sh` | Static checks: file existence, marker substrings, optional min line count | **Yes** — bats on fixtures only |

**Claim boundary:** Passing the static verifier proves **artifact presence and marker conformance** at verification time — not live assistant recognition, semantic correctness, or hosted attestation. **Scenario-tested** compatibility labels still require maintainer-recorded `last_evidence` and a scenario corpus pointer per `Docs/AgToosa_Compatibility_Contract.md`.

## Universal pilot scenario

| Field | Value |
|-------|-------|
| Scenario id | `lifecycle-compass-proof` |
| Trigger | Run `bash agtoosa.sh --status-line`, capture SYNC output, record platform adapter sentinel |
| Platforms | `cursor`, `claude`, `codex`, `copilot`, `windsurf`, `gemini` |
| Corpus index | `data/scenarios/corpus-v1.json` |
| Definition | `data/scenarios/lifecycle-compass-proof.json` |

VS Code shares the GitHub Copilot instruction path — document as Copilot-family; do not require a seventh duplicate scenario run.

## Scenario-run evidence

Record one JSON file per platform run:

```
<artifact-root>/scenario-run.json
```

Schema: `data/contracts/scenario-run-v1.schema.json`. Required fields: `scenario_id`, `platform`, `run_at`, `artifact_results[]`, `verifier_exit_code`. Optional: `proof_graph_path`, `runner_notes`.

### Optional proof-graph linkage (DEV-120)

When `proof_graph_path` is set, validate separately:

```bash
bash Docs/agtoosa-proof-verify.sh --graph <path> [--allow-stale-snapshot]
```

A valid proof graph **does not** auto-upgrade Scenario-tested tier or behavioral claims.

## Pack behavioral certification

Official packs (`packs/official-*`) may document required scenario ids in pack metadata/README:

| Layer | Authority |
|-------|-----------|
| SHA / manifest integrity | DEV-096 pack validation CI |
| Trust label (verified vs community) | DEV-101 registry docs |
| Behavioral scenario pass set | BCL scenario ids + maintainer-recorded `scenario-run.json` |

Pack labels **do not** imply hosted scenario execution or network probes in default CI.

## Maintainer workflow

```bash
# 1. Collect artifacts manually (or use fixture tree for dry runs)
mkdir -p ./evidence/cursor

# 2. Run maintainer runner (prints steps + verifies + writes JSON)
bash Docs/agtoosa-scenario-run.sh \
  --scenario lifecycle-compass-proof \
  --platform cursor \
  --artifact-root ./evidence/cursor

# 3. Optional proof graph (DEV-120)
bash Docs/agtoosa-proof-verify.sh --graph Docs/archived/proof-graph-<story>.json

# 4. Update compatibility row manually when live evidence exists
```

## Forbidden claims

- “Default CI runs live assistants as Scenario-tested proof”
- “Static bats alone promote Scenario-tested”
- “Scenario-run JSON replaces Master-Plan or proof-graph authority”

## Related

- Compatibility tiers: `Docs/AgToosa_Compatibility_Contract.md`
- Evidence provenance: `Docs/AgToosa_Evidence_Provenance.md`
- Registry trust labels: `Docs/AgToosa_Registry.md`

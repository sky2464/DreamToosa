# AgToosa Delivery Evidence Contract

> **Distinct from Terminal Evidence.** Per-task command/exit reporting lives in `docs/AgToosa_Agent.md` → **Terminal Evidence Contract**. This document defines **delivery-class** minimum evidence (what must exist for a story class), not orchestrator task output format.
>
> **Maintainer mirror:** Generated projects install this as `Docs/AgToosa_Delivery_Evidence_Contract.md`. Template source: `template/Docs/AgToosa_Delivery_Evidence_Contract.md`.

## Purpose

Teams declare how much delivery assurance a change class requires using three assurance levels and optional YAML profiles in `.agtoosa/evidence.yml`. The markdown contract is canonical; YAML is optional project config.

## Assurance taxonomy

| Level | Meaning | Examples |
|-------|---------|----------|
| **Guided** | The AI workflow asks for an action; completion is instruction-following | STRIDE discussion, architecture walkthrough, QA persona prompts |
| **Evidenced** | The action must produce a durable artifact (path/pointer) | Spec, test plan, review record, threat-model section, changelog entry |
| **Enforced** | A local or CI check can fail deterministically on presence or command outcome | Required files present, verifier gate exit code, test/lint/SAST exit code |

**Semantic review** (whether a threat model is *good*, a review is *thorough*, or ACs are *correct*) remains **Guided** or **Evidenced**. Scripts and gates may enforce **presence** and **command outcomes** only — they do not judge semantic correctness.

## Delivery profiles

Configure optional profiles under `.agtoosa/evidence.yml` (copy from `.agtoosa/evidence.yml.example`). Profile names and required artifact classes:

| Profile | Required artifact classes | Typical use |
|---------|---------------------------|-------------|
| `standard` | `spec`, `tests`, `review` | Default feature/chore delivery |
| `security-sensitive` | `spec`, `threat-model`, `tests`, `sast`, `dependency-scan`, `review` | Auth, crypto, secrets, network-facing changes |
| `release` | `spec`, `tests`, `review`, `changelog`, `rollback-note` | Versioned ship / public release |

Artifact class tokens are labels for evidence the team collects (ledger rows, test-plan pointers, review reports). **Gate 7** (DEV-089) in the verifier checks opted-in profiles deterministically.

### Example `.agtoosa/evidence.yml`

```yaml
# Optional — copy from .agtoosa/evidence.yml.example
version: 1
active: standard
profiles:
  standard:
    required: [spec, tests, review]
  security-sensitive:
    required: [spec, threat-model, tests, sast, dependency-scan, review]
  release:
    required: [spec, tests, review, changelog, rollback-note]
```

Allowed top-level keys: `version`, `active`, `profiles`.  
Allowed profile names (v1): `standard`, `security-sensitive`, `release`.  
Allowed keys under a profile: `required`.  
Allowed artifact tokens: `spec`, `tests`, `review`, `threat-model`, `sast`, `dependency-scan`, `changelog`, `rollback-note`.  
Do **not** store secrets, tokens, or passwords in evidence profiles.

## Schema validation + Gate 7 enforcement

Run the local schema checker (structure only):

```bash
bash docs/agtoosa-evidence-profile-check.sh [--root PATH]
```

| Exit | Meaning |
|------|---------|
| `0` | Valid schema, or no `.agtoosa/evidence.yml` configured (optional) |
| `1` | File present but schema-invalid |
| `2` | Usage / unreadable root |

The checker is **schema-only**: it validates **structure, known profile keys, and allowed artifact tokens only**. It does **not** check that artifacts exist on disk, does **not** claim full delivery compliance, and does **not** use the network.

**Gate 7** (DEV-089) in `docs/agtoosa-verify.sh` enforces opt-in profiles: absent `evidence.yml` is healthy; invalid YAML WARNs; required tokens are checked for deterministic presence/path/exit-code only; guided/evidenced rows are not upgraded to enforced FAIL without a wired command; SAST rows never claim vulnerability absence; missing evidence ledger WARNs per DEV-049; `--strict` promotes WARN to FAIL.

## Relationship to other surfaces

| Surface | Role |
|---------|------|
| **Terminal Evidence Contract** (`AgToosa_Agent.md`) | Per-task command, exit code, warnings — orchestrator completion format |
| **Evidence Ledger** (`AgToosa_Evidence.md`) | Per-story proof index consolidated at review/ship |
| **Evidence Provenance v2** (`AgToosa_Evidence_Provenance.md`) | Optional content fingerprints + repo snapshot; verified by `agtoosa-proof-verify.sh` — **Gate 7 unchanged** |
| **This contract** | Delivery-class minimums and profile vocabulary |
| **`.agtoosa/policy.yaml`** (DEV-059) | Agent governance / boundaries (Gate 6) |
| **`.agtoosa/evidence.yml`** (DEV-087) | Delivery evidence profiles (Gate 7 / DEV-089) |

Config index: `.agtoosa/README.md` — verifier gate order: **policy (Gate 6) → evidence profile (Gate 7, DEV-089) → lifecycle gates**.

## Claim Boundary

| Control | Classification |
|---------|----------------|
| This contract doc + example YAML + config index | generator-enforced file inventory |
| `agtoosa-evidence-profile-check.sh` | local machine check — **schema only** |
| Profile artifact presence at ship | **Gate 7** (DEV-089) — deterministic presence/exit-code when profile opted in |
| Terminal Evidence per-task blocks | agent-instructed (unchanged) |
| Semantic review quality | Guided / Evidenced — not machine-enforced |

# AgToosa Governance Policy-as-Code

> Optional, repo-local agent boundary contract. Not a runtime sandbox.
> Schema version: 1 · Checker: `Docs/agtoosa-policy-check.sh` (or `docs/` in maintainer dogfood)

## Objective

Declare allowed **paths**, **tools**, **network**, **secrets**, **approvals**, and **risky_actions** in one versioned YAML policy so Spec, Build, Review, Handoff, and Import consult the same boundaries.

> **Claim Boundary:** Installing this doc, the inert example, and the checker is **generator-enforced**. Invoking the checker is **manual** (or **CI-enforced** when a project wires it). Workflow consultation and `instruct_stop` are **agent-instructed**. Universal tool/network/secret sandboxing is **roadmap**. AgToosa does **not** intercept agent tool calls.

## Resolution Order

1. Explicit `--policy PATH` (checker only)
2. `.agtoosa/policy.yaml` (project override)
3. `Docs/Context/agtoosa-policy.yaml` or `Docs/Context/agtoosa-policy.yaml` (mode-appropriate Context fallback)
4. If none of the above exist → report `no extra policy configured` / `policy_path=none` and **continue** — missing policy must **not** make a project unhealthy

**Never auto-active:** `Docs/Context/agtoosa-policy.example.yaml` (and any `*.example.yaml` copy). Users copy the example to an active path after review.

## Schema (constrained YAML subset)

Required top-level categories (each may be an empty list, but the vocabulary is fixed):

| Category | Purpose |
|----------|---------|
| `paths` | Path allow/deny intent for agent edits |
| `tools` | Tooling constraints (agent-instructed unless wired elsewhere) |
| `network` | Network access intent (usually `roadmap` until a host sandbox exists) |
| `secrets` | Secret **names** and handling — never values |
| `approvals` | Human approval expectations |
| `risky_actions` | Dangerous operations; may use `block_generator` only when wired |

Every rule **must** declare:

| Field | Required | Notes |
|-------|----------|-------|
| `id` | yes | Unique across the whole file |
| `description` | yes | Non-empty human intent |
| `enforcement_class` | yes | Exact enum below |
| `on_violation` | yes | Exact enum below |

Optional metadata: `names`, `allow`, `deny`, `notes`, `generator_operation` (required when `on_violation: block_generator`).

### Allowed `enforcement_class` values

`generator-enforced` · `CI-enforced` · `agent-instructed` · `manual` · `roadmap`

### Allowed `on_violation` values

| Value | Meaning |
|-------|---------|
| `warn` | Record a warning; continue |
| `instruct_stop` | Agent-instructed stop; host may ignore unless its own sandbox is stronger |
| `block_generator` | Only for a **wired generator-owned** operation named in `generator_operation` |

Wired generator operations in v1 include: `pack_destination_denylist` (see registry/install denylist). Do **not** label host terminal, network, or OS controls as `block_generator`.

## Size and safety limits

- Max policy file size: **65536** bytes
- Forbidden field names (any category): `value`, `token`, `password`, `secret`, `api_key`, `apikey`, `private_key`, `credential`, `passwd`, `access_key`
- Checker diagnostics name **rule id + field** only; suspected literals are replaced with `[REDACTED]`
- No network access; no remote includes

## Checker

```bash
bash Docs/agtoosa-policy-check.sh              # resolve + validate under cwd
bash Docs/agtoosa-policy-check.sh --root PATH
bash Docs/agtoosa-policy-check.sh --policy PATH
```

Exit `0` = valid or no optional policy · `1` = invalid · `2` = bad args / unreadable root.

## Workflow violation contract

When `/agtoosa-spec`, `/agtoosa-build`, `/agtoosa-review`, or `/agtoosa-import` encounters a declared policy violation:

1. Identify the rule `id`, `enforcement_class`, and `on_violation`.
2. Follow that `on_violation` value only — do not invent stronger enforcement.
3. Preserve the mode-appropriate `Master-Plan.md` as lifecycle authority; do not write story status from policy handling.
4. Never echo secret values from policy or diagnostics.

Handoff packs must include an **Applicable Policy** section with the resolved `policy_path` and rule metadata (or the explicit no-policy result) without mutating policy or lifecycle state.

## Enforcement glossary

| Control | Classification |
|---------|----------------|
| Doc + example + checker installed by AgToosa | generator-enforced |
| GP bats / optional CI checker | CI-enforced when run |
| Local checker invocation | manual |
| Workflow `instruct_stop` / consultation | agent-instructed |
| Wired `block_generator` op (e.g. pack denylist) | generator-enforced |
| Policy authoring / approval | manual |
| Runtime agent tool/network sandbox | roadmap |

## Inert example

Copy `Docs/Context/agtoosa-policy.example.yaml` → `.agtoosa/policy.yaml` or `Docs/Context/agtoosa-policy.yaml` after human review. The example file itself is never active.

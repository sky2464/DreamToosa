# Test Plan — DEV-005

> **Story:** DEV-005 — Unify duplicate DreamsClient / DreamConfig modules  
> **Spec:** `Docs/archived/spec-DEV-005.md`

## AC coverage

| AC ID | Test ID | Category | Description | Command / assertion |
|-------|---------|----------|-------------|-------------------|
| AC-001 | T-005-001 | unit | Canonical import path | `from dreams_implementation import DreamConfig, DreamsClient` succeeds `@smoke` |
| AC-002 | T-005-002 | static | No duplicate class definitions | `rg '^class Dream(Client|Config)' --glob '*.py'` → single file `dreams_implementation.py` `@smoke` |
| AC-003 | T-005-003 | unit | Integration uses canonical client | Mock `DreamsClient.create_dream`; assert integration module calls it |
| AC-004 | T-005-004 | static | `dreams_client.py` absent | `test - ! -f dreams_client.py` |
| AC-004 | T-005-005 | unit | `DreamWorkflow` imports canonical client | Import workflow module; `DreamsClient` MRO/source from `dreams_implementation` |
| AC-005 | T-005-006 | manual | Doc spot-check | README/AGENTS mention only `dreams_implementation.py` for remote client |
| AC-006 | T-005-007 | unit | Mocked create_dream | Patch `Anthropic`; assert `beta.dreams.create` invoked once `@smoke` |
| AC-006 | T-005-008 | integration | Full suite green | `python3 -m unittest discover -s tests` exit 0 |

## Smoke set

- T-005-001, T-005-002, T-005-007

## RED / GREEN evidence

*(Populated by `/agtoosa-build` per task.)*

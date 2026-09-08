# AgToosa Retrospective Learning Loop

> Canonical contract for `/agtoosa-ship retro`.
> Artifact: `Docs/archived/retro-[YYYY-MM-DD].md` (or `docs/` in maintainer dogfood).
> Invoked only through Ship Part 5 — no separate slash command or platform adapter.

## Objective

Close a release cycle with one durable, evidence-linked retrospective that records Keep/Stop/Start lessons and **proposes** bounded follow-up work without applying it automatically.

> **Claim Boundary**
>
> | Control | Classification |
> |---------|----------------|
> | Retro workflow doc installed with AgToosa | generator-enforced |
> | Retro schema and fixtures checked in repository tests (RL bats) | CI-enforced when run |
> | Evidence collection and proposal generation | agent-instructed |
> | Keep/Stop/Start answers and proposal acceptance | manual |
> | Writing the retro artifact after explicit `/agtoosa-ship retro` | agent-instructed |
> | Applying accepted follow-up via `/agtoosa-task`, `/agtoosa-spec`, or `/agtoosa-spec amend` | manual |
> | Automatic proposal application, private memory, ML scoring, or hosted learning | roadmap |

Honest boundary: AgToosa does **not** claim automated learning. Proposals are recommendations; Master-Plan remains the lifecycle authority.

## Prerequisites

- A closed or closing cycle with a normalized cycle date (`YYYY-MM-DD`).
- Repo-local sources under the selected `Docs/` or `Docs/` root (see Inputs).
- Optional sources may be missing — mark them `unavailable`; never fetch remote trackers or network services.

## Inputs (repo-local only)

Read **only** these local artifacts (no `curl`, `wget`, or hosted APIs):

| Source | Required? | Notes |
|--------|-----------|-------|
| `Master-Plan.md` | yes | Cycle rows, shipped/deferred stories |
| Changelog (`AgToosa_Changelog.md`) | yes | Shipped notes for the cycle |
| `archived/spec-*.md` matching cycle stories | preferred | Planned ACs |
| `archived/review-*.md` | optional | Quality / friction signals |
| `archived/evidence-*.md` | optional | Proof pointers |
| `AgToosa_TestPlan-*.md` | optional | RED/GREEN / AC mapping |
| `agtoosa-events.jsonl` | optional | Phase events; skip malformed lines |

Missing or malformed optional sources → record `unavailable` in metadata and Evidence Index. Continue without network access.

## Artifact path and idempotency

- Write or update **one** file: `archived/retro-[cycle-date].md` under the selected docs root.
- Normalize the cycle date once; repeated `/agtoosa-ship retro` runs for the same cycle **update the same path** (idempotent) — do not create competing files.
- Allowed writes from this mode: the retro artifact and one bounded phase-event line (below). Nothing else.

## Artifact schema

```markdown
# Retrospective — [YYYY-MM-DD]

> **Cycle:** [YYYY-MM-DD]
> **Generated:** [ISO-8601]
> **Docs root:** Docs/ | Docs/
> **Source availability:** Master-Plan=…; changelog=…; archived-spec=…; archived-review=…; archived-evidence=…; test-plan=…; events=…

## Planned vs Shipped
| Story | Planned ACs | Shipped | Deferred | Reason | Evidence pointer |

## Evidence Index
| Story | Artifact type | Pointer | Verification summary |

## Keep
| Finding | Evidence pointer | Scope |

## Stop
| Finding | Evidence pointer | Scope |

## Start
| Finding | Evidence pointer | Scope |

## Rejected Overreach
| Unsupported claim | Reason rejected | Evidence gap |

## Proposals
| proposal_id | type | summary | evidence_pointer | status | next_command | repetition | enforcement_class |
```

Required sections (exact headings): `Planned vs Shipped`, `Evidence Index`, `Keep`, `Stop`, `Start`, `Rejected Overreach`, `Proposals`. Metadata must include cycle identifier/date, generated timestamp, selected source paths / docs root, and source availability.

## Proposals

Every follow-up row **must** include: `proposal_id`, `type`, `summary`, `evidence_pointer`, `status`, `next_command`. Policy proposals **must** also include `enforcement_class`.

Omit any candidate missing a required field; report the gap to the user instead of inventing values.

### Allowed `type` values

`task` · `spec` · `amend` · `policy` · `specialist` · `test` · `workflow`

### Allowed `status` values

`proposed` · `accepted` · `rejected` · `deferred`

Recording `accepted` documents a human decision only — it does **not** apply the change.

### Allowed `next_command` values

`/agtoosa-task` · `/agtoosa-spec` · `/agtoosa-spec amend`

### Policy `enforcement_class` (when `type=policy`)

`generator-enforced` · `CI-enforced` · `agent-instructed` · `manual` · `roadmap`

## Mutation boundary (AC-003)

THE SYSTEM SHALL leave these targets **unchanged** during `/agtoosa-ship retro`:

- Mode-appropriate `Master-Plan.md`
- Approved specs under `archived/`
- Governance policy files
- `Context/` workflow or product files
- Tests and specialist files

Do not edit, mutate, or apply proposal targets from the retro. Present proposals and next commands only. User acceptance requires an explicit later invocation of `/agtoosa-task`, `/agtoosa-spec`, or `/agtoosa-spec amend` — that separate workflow owns all authoritative changes.

Do **not** append process action items directly into Master-Plan, and do **not** update `Context/workflow.md`, from retro output.

## Repetition classification (AC-006)

1. Normalize friction into a short category label (e.g. `handoff-checklist-lag`).
2. WHEN **at least two distinct** evidence pointers identify the same category → mark `repeated-pattern` (MAY propose specialist, policy rule, regression test, or workflow amendment).
3. WHEN fewer than two distinct pointers exist → label `single-cycle`.
4. Two citations of the **same** artifact row do **not** count as two pointers.

## Redaction and bounds (AC-007)

- Store concise pointers and redacted summaries — never secret values, credentials, private URLs, or copied unbounded logs.
- Replace suspected secrets / private URLs with `[REDACTED]`.
- Prefer repo-relative pointers (e.g. `Docs/archived/review-DEV-900.md`).
- Read bounded excerpts from events/logs; link to the full local artifact instead of pasting it.

## Workflow

1. Confirm or select the closed cycle date.
2. Resolve docs root (`Docs/` generated project · `docs/` maintainer dogfood).
3. Gather Inputs; mark optional gaps `unavailable`.
4. Build Planned vs Shipped and Evidence Index from local artifacts.
5. Run Keep / Stop / Start interview; link each answer to a pointer or label as user judgment.
6. Classify repetition; draft Proposals with required fields only.
7. Write or update `archived/retro-[cycle-date].md`.
8. Append a bounded phase event to `agtoosa-events.jsonl`:
   `{"ts":"[ISO-8601 UTC]","phase":"ship","event":"retro-complete","story":"[cycle-date or primary story]","by":"AgToosa"}`
9. Present proposals and next commands — leave targets unchanged.

Optional: also append a short `## Retrospective — [date]` pointer in the changelog that **links** to the retro artifact (pointer only; the artifact is canonical).

## Output

* Path to `archived/retro-[cycle-date].md`
* Proposal table with next commands
* Explicit reminder: acceptance is manual via `/agtoosa-task` / `/agtoosa-spec` / `/agtoosa-spec amend`
* Print the dual-line phase close per Docs/AgToosa_Agent.md → Lifecycle Next-Step Contract

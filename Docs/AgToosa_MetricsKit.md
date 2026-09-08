# AgToosa Voluntary Workflow Metrics Kit

> **Claim Boundary:** Documentation / agent-instructed only. These templates define optional measurement methods. They collect nothing. AgToosa does **not** receive, verify, or retain user-entered values.
>
> **Non-goals:** No telemetry, no hosted analytics, no automatic reporting, no individual performance scoring, no SLAs, no causation claims.

## 1. Voluntary measurement contract (opt-in)

**Every use of this kit requires explicit opt-in.** Blank or unused templates are valid. Metric completion is never a workflow gate.

| Rule | Requirement |
|------|-------------|
| **Opt-in** | A person with authority over the local records must choose to use a template before any values are entered. |
| **Local-only by default** | Source data stays in the repository or other local notes the user already controls. AgToosa adds **no collection hooks**, **no network submission**, **no background analytics**, and **no automatic reporting**. |
| **Minimization** | Record only fields required by the chosen metric. Do not paste pack content, secrets, private URLs, or personal identifiers. |
| **Redaction** | Before any share outside the owning team, redact repository names, people, emails, tokens, and pack payloads. Prefer aggregates. |
| **Withdrawal** | The data owner may delete local metric records or revoke publication consent at any time; note the withdrawal date. |
| **Consent** | Publication (blog, PR description, support reply, marketing) requires dated approval by the data owner after privacy review. |
| **Missing data** | Missing values stay missing. Do **not** silently impute, invent timestamps, or fill gaps to force a percentage. Mark the measure **undefined** when population, window, or missing-data rules are incomplete. |

### No-telemetry boundary

This kit **shall not** introduce:

- A telemetry endpoint, analytics SDK, beacon, collector, or dashboard backend
- Collection hooks in `agtoosa.sh`, `lib/*.sh`, install/update paths, or CI templates
- Network submission of metric or case-study values
- Background analytics or automatic reporting

Any sharing is an intentional human action outside AgToosa.

## 2. Common metric schema

Copy this block for every measure. All fields are required before publishing a number.

```markdown
### Metric record — [metric id]

| Field | Value |
|-------|-------|
| Purpose | Why this measure is being calculated |
| Definition | Precise meaning of the measure |
| Population | Who/what is in scope |
| Numerator / denominator or unit | Exact formula inputs or unit of measure |
| Time window | Inclusive start–end (with timezone) |
| Local source | Repo-local path or manual observation method |
| Exclusions | What was left out and why |
| Missing-data handling | How blanks/incomplete rows are treated |
| Calculation method / formula | Exact arithmetic or procedure |
| Privacy review | Redaction / aggregation check + reviewer + date |
| Evidence links | Pointers to local notes (paths only; no secrets) |
| Limitations | Sample size, bias, non-comparability |
| Publication consent | Owner, decision (approve/narrow/decline), date |
```

### Interpretation rules

1. A percentage without population, window, and missing-data handling is **undefined** — do not publish it.
2. Compare only within the declared sample and window; do not imply market benchmarks or causation.
3. Small samples may re-identify people or repos — aggregate or withhold.
4. Metrics must not become targets that distort the workflow they describe.
5. Label every worked example as **SYNTHETIC** or **observed**. Synthetic examples are illustrative only and are **not** customer or production outcomes.

## 3. Six measurement templates

### 3.1 Install Success

**Definition:** Among installation **attempts** in the window, the share that reached **successful completion** plus the declared **standard post-install check**.

| Field | Notes |
|-------|-------|
| Attempts | Explicit install starts that the team chose to record (not mere downloads) |
| Successful completion | Installer finished without abort |
| Standard post-install check | Declared check (e.g. `agtoosa.sh --help`, verifier present, or listed Docs files) |
| Failure stage | Where it stopped (prompt, extract, copy, platform wiring, post-check) |
| Platform | e.g. cursor, claude, gemini, … |
| Version | AgToosa version attempted |
| Retry | Whether the attempt was a retry of a prior failure |

**Formula:** `install_success_rate = successful_completions_with_post_check / attempts` (exclude rows missing completion or post-check outcome per missing-data rule).

**Boundary:** Downloads or process starts are **not** success. Without treating downloads or starts as success, recalculate using completion plus the declared post-install check.

**SYNTHETIC worked example (illustrative only — non-customer data):** Window 2026-01-01–2026-01-31 UTC; attempts=10; successful completions with post-check=8; failure stage copy=1, post-check=1; platforms mixed; version 0.3.x; retries=2. Rate = 8/10 = 80%. **Not a real outcome.**

### 3.2 Verifier Adoption

**Definition:** Among **eligible** projects or cycles, the share with **actual verifier runs** (not mere file presence).

| Field | Notes |
|-------|-------|
| Eligibility | Projects/cycles that should run the verifier per local policy |
| Availability | `Docs/agtoosa-verify.sh` (or `Docs/`) present — **availability is not adoption** |
| Actual / observed runs | Verifier executed in the observation window |
| Mode | default / `--strict` / `stats` |
| Result | pass / findings / usage error |
| Follow-up | Whether findings were addressed or deferred |
| Observation window | Inclusive dates + timezone |

**Formula:** `verifier_adoption = cycles_or_projects_with_actual_run / eligible` (availability alone does not count).

**Boundary:** Without equating availability with use — report availability separately from observed runs.

**SYNTHETIC worked example (illustrative only — non-customer data):** Eligible cycles=12; availability=12; actual runs=5 (3 default pass, 1 strict findings, 1 usage error); follow-up on findings=1. Adoption = 5/12. **Not a real outcome.**

### 3.3 Handoff / Import Outcome

**Definition:** Outcomes of voluntary handoff export and import attempts, without collecting pack content.

| Field | Notes |
|-------|-------|
| Packs exported | Count of handoff packs written |
| Import attempts | Count of import checklist runs |
| Successful imports | Imports that met completion criteria |
| Rejected or partial imports | Failed or incomplete imports |
| Target surface | e.g. Codex, Copilot, Cursor background, Claude Code |
| Completion criteria | Declared locally (evidence present, ACs mapped, etc.) |

**Formula:** `import_success_rate = successful_imports / import_attempts` (undefined if attempts=0).

**Privacy:** Do **not** collect pack content. Retain only minimal voluntary outcome fields. Without collecting handoff content, drop any pasted brief body from the metric record.

**SYNTHETIC worked example (illustrative only — non-customer data):** Exported=4; import attempts=4; successful=3; rejected/partial=1; targets mixed. Rate = 3/4. **Not a real outcome.**

### 3.4 Cross-Model Finding States

**Definition:** Counts of cross-model review findings by lifecycle state and declared severity — **not** individual scores.

| State | Meaning |
|-------|---------|
| Proposed | Reviewer raised; not yet triaged |
| Confirmed | Accepted as valid |
| Duplicate | Same as an existing finding |
| Rejected | Not accepted (with rationale) |
| Resolved | Fix verified or explicitly deferred with owner |

Also record **severity** as declared in the review (e.g. Critical / High / Medium / Low / Info).

**Boundary:** SHALL NOT use counts as individual performance scores. Prohibit ranking contributors by finding counts. Misuse warning: manager scorecards from these numbers are out of scope and must be removed if attempted.

**SYNTHETIC worked example (illustrative only — non-customer data):** Proposed=6 → confirmed=3, duplicate=1, rejected=1, resolved=2 (one still open confirmed). Severities mixed. **Not a performance score. Not a real outcome.**

### 3.5 Cycle Time

**Definition:** Elapsed time from a declared **start event** to a declared **end event**, with pauses and incomplete cycles handled explicitly.

| Field | Notes |
|-------|-------|
| Start event | e.g. spec approved timestamp |
| End event | e.g. ship complete timestamp |
| Pauses | Intervals excluded by local rule |
| Manual / deferred intervals | `[manual]` / `[manual-deferred]` waits |
| Incomplete cycles | Missing start or end — mark incomplete; **do not invent** timestamps |
| Timezone | e.g. UTC |
| Aggregation | median / p50 / mean — declare one |
| Sample size | N complete cycles in the window |

**Boundary:** Without inventing missing timestamps — mark incomplete or document an explicit exclusion. Missing start/end timestamps must not be estimated silently.

**SYNTHETIC worked example (illustrative only — non-customer data):** N=5 complete cycles; median 4.0 days UTC; 2 incomplete excluded; 1 pause of 2 days excluded per rule. **Not a real outcome.**

### 3.6 Pack Maintenance (descriptive — not an SLA)

**Definition:** Descriptive snapshot of pack/version health on an observation date. **This metric is descriptive, not an SLA.**

| Field | Notes |
|-------|-------|
| Pack/version population | Which packs and versions are in scope |
| Compatibility review age | Days since last compatibility review |
| Open maintenance items | Count of open maintenance notes |
| Owner response state | e.g. unacknowledged / acknowledged / in progress / closed |
| Deprecation state | active / deprecated / removed |
| Observation date | Date of the snapshot |

**Boundary:** Without implying an SLA — do not present maintenance age as a response-time promise. Descriptive snapshot only.

**SYNTHETIC worked example (illustrative only — non-customer data):** Population=3 packs; review ages 7/30/90 days; open items=2; response states mixed; one deprecated; observed 2026-07-01. **Descriptive only — not an SLA. Not a real outcome.**

## 4. Case studies

For evidence-bounded write-ups, copy `Docs/AgToosa_CaseStudy.template.md`. Case studies inherit the same opt-in, local-only, redaction, withdrawal, and publication-consent rules. Synthetic-versus-observed labels are mandatory.

## 5. Privacy and claims checklist (before publish)

- [ ] Opt-in recorded; purpose and population stated
- [ ] Local sources only; no network/collection hooks used
- [ ] Minimization and redaction applied
- [ ] Missing/incomplete data not imputed
- [ ] Limitations and sample size stated
- [ ] No individual scoring, no SLA, no causation claim
- [ ] Synthetic examples labeled; observed data ownership attested
- [ ] Publication consent dated (approve / narrow / decline)
- [ ] Withdrawal path documented

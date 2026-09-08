# AgToosa Case Study Template

> **Claim Boundary:** Copyable documentation template only. Filling it in is voluntary and local. AgToosa does **not** collect, verify, or publish case studies. Sharing requires deliberate redaction, evidence review, and approval by the data owner.
>
> **Label rule:** Mark every numeric or narrative result as **SYNTHETIC** (illustrative only — non-customer data) or **observed** (owned local data). Never present synthetic examples as real outcomes.

## How to use

1. Copy this file to a local path you control (e.g. `Docs/archived/case-study-[topic]-[YYYYMMDD].md`).
2. Complete every section below before any external share.
3. Run the publication checklist; decline is a valid outcome.

---

```markdown
# Case Study — [short title]

> **Status:** draft | privacy-review | approved | withdrawn
> **Data class:** SYNTHETIC | observed
> **Owner:** [name or role]
> **Created:** [YYYY-MM-DD]

## 1. Context

- Organization / team (redacted as needed):
- AgToosa version / platforms:
- Why this case study exists:
- Claim boundary restatement: documentation anecdote only; not a market benchmark

## 2. Question

What decision or learning should this case study support?

## 3. Method

- Population:
- Time window (timezone):
- Local sources (paths only):
- Exclusions:
- Missing-data handling:
- Related metric IDs from `Docs/AgToosa_MetricsKit.md` (if any):

## 4. Voluntary data

| Metric or observation | Value | SYNTHETIC / observed | Notes |
|-----------------------|-------|----------------------|-------|
| | | | |

Do **not** paste handoff pack content, secrets, or raw personal identifiers.

## 5. Evidence

| Artifact | Pointer (path / command name) | Verification |
|----------|-------------------------------|--------------|
| | | |

## 6. Result

- Summary (bounded to declared sample/method/window):
- What is **not** claimed (no causation, no SLA, no representative benchmark):

## 7. Limitations

- Sample size:
- Selection bias / incomplete cycles:
- Comparability limits:
- Re-identification risk if shared:

## 8. Consent and privacy review

| Check | Done | Notes |
|-------|------|-------|
| Explicit opt-in to author this case study | | |
| Minimization applied | | |
| Redaction complete | | |
| Withdrawal path noted | | |
| Privacy review (reviewer + date) | | |
| Publication consent (approve / narrow / decline + date) | | |

## 9. Claim / publication review

- [ ] Synthetic vs observed labels present on every result
- [ ] Evidence links resolve locally for the owner
- [ ] No individual performance scoring
- [ ] No telemetry or network submission used
- [ ] Final publication decision: approve / narrow / decline
- [ ] If narrowed: list allowed venues
```

## SYNTHETIC worked example (illustrative only — non-customer data)

The following is a **SYNTHETIC** fixture for contract tests and author training. It is **not** a real customer case study.

- **Question:** Can a small team discuss verifier adoption without analytics infrastructure?
- **Method:** Voluntary local counts from a fictional window; population = 12 eligible cycles.
- **Result:** Verifier adoption 5/12 (SYNTHETIC); availability was 12/12 and reported separately.
- **Limitations:** Tiny synthetic sample; not generalizable.
- **Consent:** N/A for synthetic fixture; do not publish as observed.

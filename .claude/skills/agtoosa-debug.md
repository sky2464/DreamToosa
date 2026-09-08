---
name: agtoosa-debug
description: Disciplined 6-phase debugging skill — feedback-loop, reproduce, minimise, hypothesise, instrument, fix+regress. Use when /agtoosa-debug is invoked or when debugging any hard bug or performance regression.
type: rigid
---

## AgToosa Debug Skill

This is a rigid skill. Follow every phase in order. Do not skip phases.

### Phase 1 — Establish Feedback Loop
- Find the fastest deterministic reproduction command (target: <5 seconds)
- Write it to Docs/Master-Plan.md under `## Active Diagnosis`
- STOP if you cannot reproduce the issue — ask the user for more context

### Phase 2 — Reproduce
- Run feedback loop, confirm bug appears
- Document: environment, input state, expected vs actual

### Phase 3 — Minimise
- Strip to smallest reproduction case
- One file, one function, one input if possible
- Confirm minimised case still triggers bug

### Phase 4 — Hypothesise
- List exactly 3 hypotheses, most likely first
- For each: what evidence would confirm or deny it?
- Do NOT touch production code yet

### Phase 5 — Instrument
- Test one hypothesis at a time (most likely first)
- Add targeted logging/assertions
- Run feedback loop, read output
- Remove instrumentation after each hypothesis

### Phase 6 — Fix + Regression Test
- Apply minimal fix only after hypothesis confirmed
- Write regression test (must fail before fix, pass after)
- Run full test suite
- Remove all instrumentation
- Update Docs/Master-Plan.md

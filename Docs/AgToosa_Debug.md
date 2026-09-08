# AgToosa /agtoosa-debug Workflow

## Sub-Commands

| Sub-command | Runs |
|-------------|------|
| `/agtoosa-debug` | Full 6-phase diagnosis loop |
| `/agtoosa-debug quick` | Phases 1–3 only (feedback loop + reproduce + minimise) |
| `/agtoosa-debug deep` | Full loop with extended instrumentation pass |
| `/agtoosa-debug feedback-loop` | Phase 1 only — establish a fast feedback loop |

## Objective

Diagnose hard bugs and performance regressions through a disciplined, evidence-based loop. Never guess. Never patch without proof.

## Which debug path?

| Situation | Use |
|-----------|-----|
| A failing test or bug found **during an active `/agtoosa-review`** | `/agtoosa-review debug` (Iron Law protocol inside the review) |
| A production bug, heisenbug, performance regression, or anything needing instrumentation and hypothesis tracking | `/agtoosa-debug` (this workflow — writes `## Active Diagnosis` and `## Hypotheses` in `Docs/Master-Plan.md`) |

## Workflow

### Phase 1 — Establish a Feedback Loop

The most important phase. You cannot debug without fast, repeatable feedback.

1. Find the fastest deterministic way to reproduce the issue. Preference order:
   - Unit test (run with a single command, <2s)
   - Integration test
   - Script with logging output
   - Browser automation
   - Log tail / trace
2. The feedback loop must:
   - Be runnable in <5 seconds (ideally <1s)
   - Reproduce the exact symptom (not a related symptom)
   - Be deterministic — same command, same result every time
3. If you cannot create a sub-5-second feedback loop, document why and use the next fastest option.
4. Write the feedback loop command in `Docs/Master-Plan.md` under `## Active Diagnosis`.

### Phase 2 — Reproduce

1. Run the feedback loop and confirm the bug appears.
2. Document exact reproduction steps in `Docs/Master-Plan.md`:
   - Environment (OS, runtime version, dependencies)
   - Input state (data, config, flags)
   - Expected vs actual behaviour
3. If the bug is not reproducible: stop and ask the user for more context.

### Phase 3 — Minimise

Reduce to the smallest possible reproduction case.

1. Remove all code/config not required to trigger the bug.
2. Strip to one file, one function, one input if possible.
3. Confirm the minimised case still triggers the bug via the feedback loop.
4. Update `Docs/Master-Plan.md` with the minimal reproduction.

### Phase 4 — Hypothesise

1. List exactly 3 hypotheses, ordered by likelihood (most likely first).
2. For each hypothesis:
   - What would the code look like if this were true?
   - What evidence (log line, stack frame, assertion failure) would confirm or deny it?
3. Do not fix anything yet. Do not touch production code.
4. Add hypotheses to `Docs/Master-Plan.md` under `## Hypotheses`.

### Phase 5 — Instrument

Test hypotheses one at a time, most likely first.

1. Add targeted logging, assertions, or breakpoints to test the top hypothesis.
2. Run the feedback loop.
3. Read the output:
   - Confirmed: note which hypothesis is true, remove instrumentation.
   - Denied: move to next hypothesis.
4. Never leave instrumentation in the code after a hypothesis is resolved.
5. Update `Docs/Master-Plan.md` with instrumentation findings.

### Phase 6 — Fix + Regression Test

Only apply a fix after a hypothesis is confirmed.

1. Apply the minimal fix — change only what the evidence says is broken.
2. Run the feedback loop — confirm the bug is gone.
3. Write a regression test:
   - Name: `regression_[bug-id]_[short-description]` or similar
   - The test must fail before the fix and pass after
   - Add it to the test suite permanently
4. Run the full test suite to catch regressions.
5. Remove all instrumentation added during Phase 5.
6. Update `Docs/Master-Plan.md` **Update Log** with the diagnosis summary.

## Rules

- **Never fix before hypothesising.** A fix without a confirmed hypothesis is a guess.
- **Never skip the regression test.** If there is no test, the bug will return.
- **Never leave instrumentation in production code.**
- If you cycle through all 3 hypotheses with no confirmation: go back to Phase 3. Your reproduction is probably incomplete.
- For performance regressions: Phase 1 feedback loop must include a benchmark, not just a test.

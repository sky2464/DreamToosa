# Profile: shell-spec-driven

Bash/shell projects that follow the AgToosa spec-driven model. Currently: `sky2464/AgToosa`.

## What to review

1. **Spec backing** — is each behaviour change backed by a spec file following
   `Docs/SPEC-FORMAT.md` conventions? Code that changes behaviour with no spec row
   is a `spec-gap`.
2. **Test coverage** — is there a `bats` test in `tests/` covering the new behaviour?
   Code without a corresponding assertion is a `test-gap`.
3. **CHANGELOG** — is `CHANGELOG.md` updated under `[Unreleased]` for anything
   user-visible? Keep a Changelog format, SemVer.
4. **Wiring consistency** — when a feature is added for one platform/version,
   check the parallel wiring (template workflow files, `lib/config.sh`, version
   pins) was updated too. Partial wiring is the most common defect class here.
5. **Shell safety** — this is the security-relevant axis for this profile:
   - unquoted expansions in paths or arguments (`$var` where `"$var"` is meant)
   - `eval`, backticks, or `$(...)` built from untrusted input
   - `jq` / `gh` arguments interpolated into a shell string instead of passed via
     `--arg` / `--argjson`
   - `local` name collisions between a JSON string and an array of the same name
   - anything writing to `$HOME` or outside the repo without a guard
6. **Master-Plan drift** — does `docs/Master-Plan.md` reflect what actually shipped?
   Rows left in `In Progress` after a merge are a real, recurring gap here.

## Known baseline — do not re-report

These are already tracked. Reference the existing issue instead of filing a new one:

- `validate` CI job red on `main` (bats assertion baseline) — tracked in **#146**.
- PR backlog / merge freeze — tracked in **#153**.
- Dependabot high-severity alerts on default branch — tracked in **#141**.

A finding is only new if it is not an instance of one of the above.

## Verification command

```
bats tests/agtoosa.bats
```

Expect a non-zero exit today because of the #146 baseline. Compare the failure
*count* against the previous report rather than treating red as new information.

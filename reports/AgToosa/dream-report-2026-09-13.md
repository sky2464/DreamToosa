# Dream Report — sky2464/AgToosa — 2026-09-13

Profile: `shell-spec-driven`. Commit range reviewed: `348c637..04e5ebc` (3 commits, review window since last reviewed sha).

## What improved

- **#141 (Dependabot high-severity alerts)** — closed. `24ce5e9` bumped `nanoid`, `fast-uri`, `js-yaml`, added `.github/dependabot.yml`, and recorded the bump in `CHANGELOG.md`. Clean fix, properly documented.
- **PSP-004** bats assertion fixed in `tests/agtoosa.bats` (version-pin corrected to `0.2.0` under current major `0`).
- **`lib/migrate.sh` / `lib/version.sh`** — historical major-version migration boundary (`1.x`-`5.x` < `0.x`) fixed in `dc5d81a`, resolving `DEV-091` test failures. Backed by the existing `MWZ-008` test.
- **CI runtime** — redundant `apt-get update`, a 3-minute no-op markdownlint step, and duplicate bats smoke invocations were pruned; pip caching added. Legitimate performance win, no behavior change.
- The manifest's rationale comment for `fix_eligible: false` on this repo ("15-PR backlog on main pending drain") appears **stale** — `list_pull_requests` shows **0 open PRs** on AgToosa right now. Worth a human revisiting whether this repo should become fix-eligible again.

## What needs attention

- **New finding (filed as #168):** the commit that closes #146 ("fix: make CI validate job fast and green by scoping smoke tests") changed the `validate` job's bats filter from `-f '@smoke'` to `-f '@smoke BCL|PN|WP2|ACC|NET|PSP|CORE'`. Because `bats -f` takes an ungrouped extended regex, the `|` alternation matches on bare substrings, not the `@smoke` tag. Verified against the current test file: 231 tests actually carry `@smoke`; the new filter matches only 40, and 21 of those 40 don't carry `@smoke` at all (matched only because their names contain `PN`, `WP2`, `ACC`, or `CORE` as substrings). So only ~19 of 231 real smoke tests still run in CI. #146 documented 125/1336 failing assertions and asked for either a fix or a dedicated triage story for the 85 non-version-pin failures; this commit fixed one (`PSP-004`) and closed the issue by narrowing what CI runs, not by resolving the rest. They are very likely still failing, just no longer visible.
- **#167** (CHANGELOG gap for `dc5d81a`'s migration fix) and **#166** (Master-Plan drift on DEV-154/DEV-155) remain open from prior runs — same instances, not re-filed.
- Could not run `bats tests/agtoosa.bats` in this sandbox (`bats` not installed) — findings above are from static reading of the test file and CI YAML, not a live run.

## Prioritized action items

1. Fix the `validate` job's smoke filter to properly group the tag alternation (e.g. `-f '@smoke.*(BCL|PN|WP2|ACC|NET|PSP|CORE)'`), and reopen or re-file the remaining ~124 assertions #146 was tracking rather than treating them as resolved (#168).
2. Add the missing `CHANGELOG.md` entry for the `lib/migrate.sh` version-migration fix (#167).
3. Reconcile `docs/Master-Plan.md` rows for DEV-154/DEV-155 (#166).

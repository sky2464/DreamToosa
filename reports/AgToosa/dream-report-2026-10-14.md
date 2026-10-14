# Dream Report — sky2464/AgToosa — 2026-10-14

Profile: `shell-spec-driven` · `fix_eligible: false` (review-only: 15-PR backlog on main pending drain) · `max_open_prs: 5` (0 open)

Window reviewed: `b257b9d..ca19d35` (2 commits: #180, #181)

## What improved

- **#181 fixes a real, recurring CI break.** The Issues-sync job's milestone lookup (`lib/github-issues-sync.sh`) only listed *open* milestones via `gh api repos/:owner/:repo/milestones`, so a closed milestone sharing the manifest's title got re-created and GitHub rejected the create with HTTP 422, stopping the job before it updated any issue. The lookup now passes `?state=all&--paginate`. `gh issue --milestone` has the same open-only blind spot, so milestone assignment was switched to a direct `PATCH .../issues/{n}` with `-F milestone="$milestone_number"` (properly passed as an API field, not interpolated into a shell string — no new shell-safety issue introduced).
- **Wiring consistency maintained.** `lib/github-issues-sync.sh` and `template/lib/github-issues-sync.sh` are byte-identical after the fix (verified by diff) — this profile's most common defect class (partial platform wiring) did not recur here.
- **A real behavior fix is also bundled in, correctly scoped:** a story whose status says "awaiting next release" (e.g. DEV-155 after #179 merged) now stays open instead of being auto-closed as shipped (`_gh_issues_story_shipped` in `lib/github-issues.sh` gained an early `return 1` for that status string).
- **CHANGELOG.md updated** under `[Unreleased] → Fixed` with a clear writeup citing the bats coverage added.
- **Bats coverage added**: 31 new lines in `tests/agtoosa.bats` (DEV-147 GIP-013, GIP-014) plus an updated mock in `tests/fixtures/tracker-sync/issues-sync/mock-gh.sh`.
- **Master-Plan.md reflects reality**: #180 updated DEV-152's status to "In Progress — Spec Approved" and the header's "Last updated" line, matching the commit's own content.

## What needs attention

- `bats` is not installed in this review sandbox, so `tests/agtoosa.bats` could not actually be run — this remains a static-diff review, same limitation as every prior run.
- No new findings this run. The three known-baseline issues this profile tracks (#146 bats baseline, #153 PR backlog, #141 Dependabot) were checked: #146 and #141 are already **closed** on GitHub (#146 closed 2026-09-09, confirmed via `issue_read`) — the profile's "known baseline" doc text is itself now stale and should be refreshed by a human, though that's a docs housekeeping note, not a new code defect.

## Action items (max 3)

1. No code action needed — this window's two commits are clean (spec-backed, tested, wiring-consistent, changelog-updated).
2. A human should refresh `dreamtoosa/profiles/shell-spec-driven.md`'s "Known baseline" section — #146 and #141 are already closed, so continuing to list them as open baseline exemptions is misleading for future runs.
3. Re-confirm whether `fix_eligible: false`'s stated reason ("15-PR backlog on main") still holds — AgToosa currently shows 0 open PRs, same observation as the 2026-10-13 report flagged and still unactioned.

## Verification

```
bats tests/agtoosa.bats
```
Result: **not run** — `bats` is not installed in this sandbox. Static review of the diff only.

**HEAD at review time:** `ca19d3591607731d67057fce5b79b30004a3fa00`

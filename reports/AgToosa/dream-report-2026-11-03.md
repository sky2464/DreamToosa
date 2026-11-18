# Dream Report — sky2464/AgToosa — 2026-11-03

Profile: `shell-spec-driven` · `fix_eligible: false` (review-only: backlog on main pending drain) · `max_open_prs: 5` (0 open)

Window reviewed: `9ad3043c..9ad3043c` (0 new commits since 2026-11-02 review; `origin/main` at `a65c5c1e`)

GitHub API: MCP unavailable — read-only mode; no issues or PRs filed.

## What improved

- **Number-based milestone assignment (`2688311`, `1418994`, `9ad3043`):** Branch `claude/approve-merge-branches-nkfdie` refactored milestone assignment in `lib/github-issues-sync.sh` and `template/lib/github-issues-sync.sh` to assign milestones by number via the REST API rather than by title through `gh issue --milestone`. This ensures closed milestones with matching titles in the manifest sync without triggering 422 errors or unintended milestone reopens.
- **Bats test coverage verified:** DEV-147 GIP-013 test in `tests/agtoosa.bats` verified passing (`ok 1 DEV-147 GIP-013: closed milestone with the manifest title is reused, not re-created`).
- **Shell safety preserved:** Shell parameters in `lib/github-issues-sync.sh` remain strictly quoted with proper local variable isolation.

## What needs attention

- **0 open PRs, 0 open issues on `origin/main`:** The default branch remains caught up at `a65c5c1`. The stated rationale for `fix_eligible: false` ("15-PR backlog on main pending drain") is fully resolved. Maintainers should consider updating `repos.yml` to set `fix_eligible: true`.
- **Working tree branch divergence:** Local clone working tree is currently on branch `claude/approve-merge-branches-nkfdie`, with untracked test plan and spec artifacts in `docs/`. When these changes are ready, they should be merged or committed to their respective feature tracks.
- **Profile baseline references:** The known-baseline issues listed in `dreamtoosa/profiles/shell-spec-driven.md` (#146, #153, #141) are historically closed and should be updated.

## Action items (max 3)

1. Review and merge `claude/approve-merge-branches-nkfdie` (number-based milestone assignment fix) into `main` when ready.
2. Re-evaluate `fix_eligible` setting in `repos.yml` now that `origin/main` has no PR backlog.
3. Refresh known baseline issue numbers (#146, #153, #141) in `dreamtoosa/profiles/shell-spec-driven.md`.

## Verification

```bash
bats tests/agtoosa.bats -f "GIP-013"
```
Result: `ok 1 DEV-147 GIP-013: closed milestone with the manifest title is reused, not re-created`. Bats 1.14.0 is installed in environment. Static inspection of shell safety and milestone logic passes cleanly.

**HEAD at review time:** `9ad3043cd13ead0815af565ec42d642e5d0b4978` (HEAD) / `a65c5c1e62f951566e9447fc0b735128395c5a90` (origin/main)

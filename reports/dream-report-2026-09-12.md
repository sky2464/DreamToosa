# Dream Report Index — 2026-09-12

Routine run date: **2026-09-12**
Hub repository: `sky2464/DreamToosa`

---

## Status Table

| Repository | Profile | Commits (Window) | Findings | Skipped Reason |
|------------|---------|-------------------|----------|-----------------|
| `sky2464/AgToosa` | `shell-spec-driven` | 3 | 1 issue filed (#167, CHANGELOG gap) | — |
| `sky2464/Crapsino` | `web-playwright` | 0 | none | — |
| `sky2464/DreamToosa` | `python-lib` | 2 | none (0 open issues to file against) | — |
| `sky2464/miToosa` | `dart-flutter` | 0 | none | — |

No repo tripped the circuit breaker this run.

**Operational note (not a code finding):** `sky2464/DreamToosa` itself is carrying an unmerged report-PR backlog — PR #11 (2026-09-10) and PR #12 (2026-09-11) are both still open, mergeable, and based on the current `main` head. This run's own hub PR will be a third. Because none of these merge, `dreamtoosa/state.json` on `main` is still dated 2026-09-09, so successive runs re-derive largely the same findings for AgToosa and DreamToosa instead of building on prior state. **A human should merge or close #11 and #12 before the next run**, ideally alongside this one.

---

## Per-Repository Detail

### `sky2464/AgToosa`
- **What improved:** Both baselines this profile tracks are now closed — #146 (bats `validate` job red on `main`) via CI rescoping, and #141 (Dependabot high-severity alert) via merged PR #165. A real, test-backed fix also landed in `lib/migrate.sh` for the historical `1.x`-`5.x` → `0.x` version-migration boundary.
- **What needs attention:** New CHANGELOG gap for that migration fix, filed as #167. Issue #166 (Master-Plan drift on DEV-154/DEV-155) remains open and unaddressed for a third consecutive run.
- **Up to 3 action items:**
  1. Add a CHANGELOG entry for the `lib/migrate.sh` fix (#167).
  2. Fix the DEV-154/DEV-155 Master-Plan rows (#166) — now three runs unaddressed.
  3. Reconsider `fix_eligible: false` now that both #153 (PR backlog) and #146 have been closed for multiple runs.
- **Detail:** [reports/AgToosa/dream-report-2026-09-12.md](AgToosa/dream-report-2026-09-12.md)

### `sky2464/Crapsino`
- **What improved:** N/A — no commits in the review window (fourth consecutive quiet run).
- **What needs attention:** Nothing new; repo is quiet with no open issues or PRs.
- **Up to 3 action items:** None this run.
- **Detail:** [reports/Crapsino/dream-report-2026-09-12.md](Crapsino/dream-report-2026-09-12.md)

### `sky2464/DreamToosa`
- **What improved:** `29766d8` documented the local vs. remote "dream curation" implementations (README table + `AGENTS.md` cross-references) instead of adding another parallel one — directly following up on issue #8's prior resolution. `py_compile` clean, no secrets, no oversized files.
- **What needs attention:** Operationally, PRs #11 and #12 (prior two runs' report PRs) remain unmerged — see the note above. No code-level findings; 0 open issues exist for this repo.
- **Up to 3 action items:**
  1. Merge or close PR #11 and #12 to unstick `state.json` on `main`.
  2. Continue the doc-consolidation direction from `29766d8` (out of this routine's scope to execute).
  3. None further — repo is otherwise healthy.
- **Detail:** [reports/DreamToosa/dream-report-2026-09-12.md](DreamToosa/dream-report-2026-09-12.md)

### `sky2464/miToosa`
- **What improved:** N/A — no commits in the review window (fourth consecutive quiet run, longest-stale of the four targets).
- **What needs attention:** Nothing new to review; pre-existing open PR #55 (since 2026-09-10) and 10 open issues remain outstanding but are out of this run's scope (no new commits).
- **Up to 3 action items:**
  1. A human should look at aging PR #55 and the issue backlog directly — this routine won't surface them again on its own absent new commits.
- **Detail:** [reports/miToosa/dream-report-2026-09-12.md](miToosa/dream-report-2026-09-12.md)

---

## Fix Rotation

- **Selected for fix work this run:** `sky2464/DreamToosa` (rotation index advanced 1 → 2, `fix_eligible: true`, 2/3 open PRs — eligible).
- **Outcome:** No fix PR opened. DreamToosa has zero open issues, so there was nothing to resolve. This does not count against the run's PR budget.
- **Next in rotation:** `sky2464/miToosa` (index 3), pending eligibility at that time.

# Dream Report — sky2464/Crapsino — 2026-10-14

Profile: `web-playwright` · `fix_eligible: true` · `max_open_prs: 3` (0 open)

Window reviewed: `ceb42b3..ceb42b3` (0 commits — `main` unchanged since 2026-10-13, the third review in a row with no new commits)

## What improved

N/A — no commits landed in this window.

## What needs attention

With no code changes to review, this run did a hygiene sweep of the profile's static checks against the current tree instead, since the repo was also this run's fix-rotation target:

- **Generated CSS verified in sync.** Ran `patch_css.py` against a scratch copy of `src/styles/global.css` and diffed against the committed file — byte-identical. No drift between the generator and its committed output.
- **Lockfile verified in sync.** `npm ci --dry-run` resolves cleanly against `package.json`/`package-lock.json` with no version conflicts.
- **No secrets found** in `index.html`, bundled config, or `docker-compose.yml`.
- **nginx.conf / Dockerfile**: only `dist/` (Vite's clean build output) is copied into the production image; Vite's `build.sourcemap` is not enabled, so no source maps are shipped. No dotfiles are present in the build output to leak.
- **New finding — Dockerfile base images float.** `FROM node:20-alpine` and `FROM nginx:alpine` both pull unversioned tags that can silently change on every rebuild — the same reproducibility risk this profile's container-hygiene check calls out for `:latest`. Filed as **Crapsino#7** rather than fixed directly: this sandbox has no Docker daemon, so a tag-pin change could not be verified to actually build before pushing, and an unverified Dockerfile edit is a worse outcome than the floating tag it would "fix."
- `generate_layout.py` prints zone definitions to stdout (a paste-in dev tool, not a file-writing generator with a committed target), so no sync check applies to it.
- All items in `docs/PLAN.md` remain as previously tracked (no new drift) — P0 ship-blockers: none; remaining backlog is test-coverage (TC*) and performance/maintainability items explicitly out of this profile's fix-PR scope (game logic/layout).

## Action items (max 3)

1. Pin `Dockerfile`'s two base images to a specific version line (see **Crapsino#7**) — low risk, verify the build locally before merging.
2. No other action needed this run.
3. (Standing item, unchanged for 3 runs) Nothing else outstanding; 0 open issues before this run's filing, 0 open PRs.

## Verification

```
npm ci
npx playwright test
```
Result: **not run** — no code changed, and Playwright browsers are not installed in this sandbox. `npm ci --dry-run` (lockfile sync only) and a static `patch_css.py` diff were run instead; see above.

**HEAD at review time:** `ceb42b352e1975528ea541a4aa183e159226be5f` (unchanged)

# Profile: web-playwright

Browser apps with a Playwright end-to-end suite, built and served via Docker.
Currently: `sky2464/Crapsino`.

## What to review

1. **E2E coverage** — is there a spec under `e2e/` covering new or changed
   behaviour? This repo's primary safety net is Playwright, not unit tests, so an
   uncovered interaction path is a `test-gap`.
2. **Secrets in client code** — anything in `index.html`, bundled JS, or
   `docker-compose.yml` that looks like a key, token, or credential is shipped to
   every visitor. `security` finding, always top priority.
3. **Design drift** — this repo carries `design.md` and `design-qa.md` as the
   stated design contract. Do CSS/layout changes match what those documents
   describe? Divergence between the design doc and the implementation is a
   `docs` finding worth reporting.
4. **Generated CSS** — `patch_css.py` and `generate_layout.py` produce committed
   output. Is that output in sync with its generator? Hand-edits to generated CSS
   that the generator would overwrite are a real, silent defect here.
5. **Dependency and container hygiene** — `package-lock.json` committed and in sync
   with `package.json`; `Dockerfile` not pulling unpinned `:latest` base images;
   `nginx.conf` not serving dotfiles or source maps in production.
6. **Accessibility basics** — images without `alt`, controls without accessible
   names, and colour-only state indication. Report as `a11y`, low severity unless
   it blocks a primary flow.
7. **Console errors** — if the Playwright suite captures console output, treat
   uncaught errors during a passing test as a finding, not noise.

## Verification commands

```
npm ci
npx playwright test
```

Playwright browsers may not be installed in the sandbox. If the suite cannot run,
say so plainly in the report and review statically — do not present an unrun suite
as passing.

## Scope note

Fix PRs here should stay limited to asset hygiene, dependency pinning, docs, and
accessibility attributes. Anything touching game logic or layout needs a human
looking at a rendered page.

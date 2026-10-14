# Dream Report — sky2464/Crapsino — 2026-10-03

**Profile:** web-playwright  
**Review window:** SHA `ceb42b3..HEAD` (last reviewed 2026-09-20)  
**Commits in window:** 0  
**Current HEAD:** `ceb42b352e1975528ea541a4aa183e159226be5f`  
**GitHub API:** 401 Bad credentials — read-only mode; no issues or PRs filed.

## No New Commits

Zero commits since the last reviewed SHA `ceb42b3`. Baseline remains stable.

## What Improved

- **Core Engine & Unit Tests Stable:** Local Vitest test suite executed and fully passing:
  - 53 test files executed (53/53 passed)
  - 418 unit and integration tests passed (418/418)
  - Full engine coverage: craps rules, advisor engine, odds preview, settlement, dice theater model, audio store, UI stores, and layout components.
- **Playwright Game Over Flow Verified:** End-to-end browser test for bankroll exhaustion and game over modal passed cleanly.

## What Needs Attention

- **Playwright E2E Settlement Failures:** In `e2e/pass-line.spec.ts`, 2 out of 3 tests failed:
  - `basic pass-line flow › places a pass-line bet, shoots, and settles` failed at line 29: `expect(page.getByText(/net this roll/i)).toBeVisible({ timeout: 8000ms })`.
  - `point and odds flow › establishes a point, offers odds, and resolves the round` failed at line 58 with the same expectation timeout.
  - The settlement feedback copy in HUD or animation timing during transition requires investigation.
- **Coverage Directory Hygiene:** Running tests generates `coverage/` files (`clover.xml`, `coverage-final.json`, HTML reports) which appear in `git status`. Adding `coverage/` to `.gitignore` will keep working trees clean.

## Verification

```bash
npm test
npx playwright test
```
**Result: Vitest PASSED / Playwright PARTIAL**
- Vitest: 53 test files passed, 418 unit/integration tests passed (100%).
- Playwright: 1 passed (`game over flow`), 2 failed (`basic pass-line flow`, `point and odds flow` awaiting `/net this roll/i`).

## Action Items

1. **(Human)** Investigate Playwright E2E failures in `e2e/pass-line.spec.ts` (lines 29 & 58) regarding the `/net this roll/i` locator.
2. Add `coverage/` to `.gitignore` to prevent test coverage reports from dirtying git status.
3. Verify settlement HUD text and roll transition timing.

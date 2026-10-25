# miToosa — 2026-10-15

**Profile:** dart-flutter
**HEAD:** `d10a5c8f7d0344a46e5aae9ada4c59a22c9ddb21`
**Commits in window:** 6 (`a5b8535..d10a5c8`)
**Open PRs:** 0 (cap 3) — no circuit-breaker skip

## What improved

- **PR #65** (`c6fb644`, BL-41, merged): fixed a real data-loss bug — completing a puzzle used to make three independent, unserialized writes (star update, stale-copy XP/bests save, conditionally-recomputed heart refuel), and a brand-new player's very first result could be silently dropped when the star write landed on an object the final save then overwrote. Now every effect of a result (stars, XP, bests, daily XP, adaptive history, coins, lower-level refuel, achievement unlocks) applies through one serialized `updateProgress` call per player, so concurrent mutations can't clobber each other. Shipped with 3 new/extended test files covering the exact "first result survives," "competing writes don't lose any," and "survives relaunch" scenarios.
- **PR #66** (`06340fb`, merged): resolved **miToosa#64** — added the missing `[Unreleased]` CHANGELOG entries for BL-39, BL-40, and #48/#56. **#64 is closed.**
- **PR #67** (`04d91a0`, BL-38, merged): real, partial progress on **#52** — split `puzzle_generator.dart` (was 1403+ lines) into 6 rule modules, extracted `player_progress_adapter.dart` from the Hive provider, and split `track_detail_screen.dart` into `track_detail_launch.dart` + `widgets/track_detail_sheets.dart`. Added 4 new architecture-guard tests (`dead_dependency_guard_test.dart`, `engine_boundary_test.dart`, `engine_import_guard_test.dart`, `line_budget_test.dart`) plus a characterization test with a golden fixture. The PR is explicit that `gameplay_screen.dart` (1158 lines) and `player_progress.dart` (534 lines) are deferred follow-ups — this is documented, not silent.
- A same-day follow-up commit (`2da981d`) removed a duplicate import that was blocking PR #67's own CI (`dart analyze` duplicate_import failure) — small, mechanical, correctly scoped to unblocking CI.

## What needs attention

Posted a comment on **#52** (not a new issue — same scope): the new `line_budget_test.dart` and PR #67's deferred-files note together cover 11 files, but two more files already exceed the 500-line budget and are tracked nowhere: `lib/features/main_app/progress_screen.dart` (575 lines) and `lib/features/settings/settings_screen.dart` (503 lines). Neither was touched in this review window, so this isn't a regression, just an incompleteness in #52's own tracking. The "remove unused packages from `pubspec.yaml`" half of #52's scope also still looks unaddressed.

`#46` (BL-25, physical iPhone TestFlight QA pass) remains open — out of scope for this routine (needs a human with a physical device).

## Verification

```
flutter analyze
flutter test
```
Flutter SDK remains unavailable in this sandbox (standing limitation, 4th+ run running) — static diff review only. The new test files were read in full; their assertions are specific and non-trivial (exact XP/coin arithmetic, achievement-unlock-once semantics, post-relaunch persistence), which reads as real coverage rather than padding, but could not be executed here.

## Top action items

1. No fix PR needed this run — miToosa was not selected by this run's rotation, and its one open, in-scope issue (#52) is explicitly out of this profile's fix-PR scope (UI/layout work needs a human looking at a running build, per the profile's own scope note).
2. Consider adding `progress_screen.dart` and `settings_screen.dart` to `line_budget_test.dart`'s deferred-tracking (or #52's description) so the budget's own bookkeeping stays accurate — flagged via comment on #52, not actioned here.
3. Standing: provision a Flutter SDK in the review sandbox so this routine can eventually run `flutter analyze`/`flutter test` itself instead of static-only review.

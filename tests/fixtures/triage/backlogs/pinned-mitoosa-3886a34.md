# Master-Plan

> **Source of truth for active work.** Completed work lives in `Docs/archived/` — see Completed This Cycle for links.
> **Last updated:** 2026-09-10 (Documentation planning update — Premium Quality Roadmap added)

## Project Charter

| Field | Value |
|-------|-------|
| Product | miToosa — cross-platform Flutter puzzle game (iOS launch focus for v1.5.0) |
| Goal | Ship v1.5.1 to the iPhone App Store with a validated free-first wedge and Firebase analytics |
| Long-term quality objective | Deliver a premium mobile puzzle game in staged milestones (BL-39–BL-54, EP-06) — five puzzles per session, durable saves, atomic results, working difficulty, truthful progress, cohesive visuals, accessible puzzles, coordinated game feel, measured performance, and reviewed content — while preserving iPhone-first delivery, 25 daily free games, the +40 share bonus, and production SFX without music. See "Premium Quality Roadmap." |
| User outcome | Casual puzzle players get ADHD-optimized 3–5 minute sessions without sign-up friction; they understand the 25 free games/day + share bonus model |
| Success condition | App Store submission accepted; TestFlight QA passed on physical iPhone; D1 retention signal ≥40% from playtest; analytics events visible in Firebase DebugView |
| Proof / evidence | `flutter test` green (944 tests); `dart analyze` clean on lib/test; BL-32 privacy/consent shipped; BL-31 truthful launch surfaces shipped; BL-30 catalog integrity shipped |
| Non-goals | Android/macOS/Web store launch in v1.5.0; backend leaderboard; IAP/VIP; server sync; referral tiers (see `docs/PRODUCT-WEDGE.md`); additional languages beyond English, online competition, cloud saves, daily challenges, and multiplayer remain evidence-gated expansion, not premium-quality requirements (see Premium Quality Roadmap) |
| Assumptions | Apple Developer account and company formation proceed on owner timeline; Firebase + GA is the launch analytics stack; local-first Hive persistence remains canonical |
| Risks | External gates (company, App Store Connect, Firebase console) block store release; physical-device QA not yet executed |
| Unresolved questions | Public privacy/support URL hosting; exact App Store review timeline; playtest recruitment post-TestFlight |
| GitHub repo | https://github.com/sky2464/miToosa |
| Milestone | v1.5.1 (next) — iPhone App Store launch |
| Active cycle | Launch Sprint — iPhone readiness + UX polish (2026-06-02 → 2026-06-25) |
| Cycle capacity | 13 story points |
| Current phase | 🏁 Shipped — BL-33; Awaiting Manual — BL-25 TestFlight QA |

## Active Cycle

> Stories committed to the current sprint/cycle.

| ID | Title | Type | Estimate | Status | Tasks Done |
|----|-------|------|----------|--------|-----------|
| BL-25 | Feature: Physical iPhone TestFlight QA pass (#46) | Feature | M | 🔧 Awaiting Manual | 5/5 tasks (12 manual-deferred) |

Status key: ⬜ Backlog · 🟦 Todo · 🟨 In Progress · ✅ Done · 🚫 Blocked · 🔧 Awaiting Manual · 🏁 Shipped

## Active Tasks

### BL-25 — Physical iPhone TestFlight QA pass

- [x] **1.** QA documentation: TestFlight checklist + evidence template
  - [x] 1.1 Create `docs/qa/iphone-testflight-qa-checklist.md` — _Requirements: AC-001_
  - [x] 1.2 Create `docs/qa/iphone-testflight-evidence-template.md` — _Requirements: AC-002_
  - [x] 1.3 Cross-link from `IPHONE-LAUNCH-READINESS.md`, `LAUNCH.md`, `wedge-qa-checklist.md` — _Requirements: AC-001, AC-012_
- [x] **2.** Automated guards
  - [x] 2.1 Extend `test/release/iphone_launch_readiness_test.dart` — _Requirements: AC-012_
  - [x] 2.2 Run `dart analyze lib test` and `flutter test` — _Requirements: AC-012_
- [ ] **3.** Manual TestFlight QA execution (physical iPhone)
  - [ ] 3.1 Install TestFlight build on physical iPhone — _Requirements: AC-003_ `[manual-deferred]`
  - [ ] 3.2 Cold launch + onboarding; time-to-first-game ≤60s — _Requirements: AC-003, AC-004, AC-015_ `[manual-deferred]`
  - [ ] 3.3 Complete full 3-round gameplay session — _Requirements: AC-005_ `[manual-deferred]`
  - [ ] 3.4 Share flow: +40 once; second share denied — _Requirements: AC-006_ `[manual-deferred]`
  - [ ] 3.5 Offline mode gameplay + relaunch — _Requirements: AC-007_ `[manual-deferred]`
  - [ ] 3.6 VoiceOver smoke + Dynamic Type largest — _Requirements: AC-008, AC-013_ `[manual-deferred]`
  - [ ] 3.7 Wedge copy walkthrough — _Requirements: AC-009_ `[manual-deferred]`
  - [ ] 3.8 Force-quit persistence check — _Requirements: AC-011_ `[manual-deferred]`
  - [ ] 3.9 Settings/support link scan — _Requirements: AC-014_ `[manual-deferred]`
- [ ] **4.** Analytics verification
  - [ ] 4.1 Firebase DebugView spot-check (`FIREBASE_ENABLED=true`) — _Requirements: AC-010_ `[manual-deferred]`
- [ ] **5.** Evidence closure
  - [ ] 5.1 Complete dated evidence file; gate log in `RELEASE-GATES.md` — _Requirements: AC-002, AC-003–AC-011_ `[manual-deferred]`
  - [ ] 5.2 Mark Physical iPhone QA complete in launch docs + Master-Plan — _Requirements: AC-003–AC-011_ `[manual-deferred]`

## Manual / Deferred Tasks

> Tasks that require a human action outside the agent. These are **not** counted against the health score.

| Story | Task # | Deferred Since | Description |
|-------|--------|----------------|-------------|
| BL-31 | 4.3 | 2026-07-26 | Physical iPhone Settings/reset smoke — build complete repo-side; device proof pending |
| BL-30 | 4.3 | 2026-07-26 | iPhone viewport visual review of 23 track cards — shipped repo-side; device proof pending |
| BL-29 | 4.3 / T-007 | 2026-07-26 | Native iPhone share once/repeat smoke — shipped repo-side; device proof pending |
| BL-28 | 3.3 / T-006 | 2026-07-26 | Fresh-install iPhone smoke — onboarding to first playable track within 60s (shipped repo-side; device proof pending) |
| BL-32 | 4.2 | 2026-07-27 | iPhone analytics opt-out/relaunch smoke — shipped repo-side; device proof pending |
| BL-33 | 4.2 | 2026-07-28 | iPhone home-screen + cold-launch screenshot smoke — shipped repo-side; device proof pending |
| BL-25 | 3.1–5.2 | 2026-07-14 | Physical iPhone TestFlight QA, DebugView, evidence capture, and launch-doc closure (12 owner-executed steps) |
| BL-26 | 4.1 | 2026-07-11 | Publish Privacy Policy + Support URLs and paste finals into ASC/metadata |
| BL-26 | 4.2 | 2026-07-11 | Capture iPhone screenshots per checklist and upload in App Store Connect |
| BL-22 | — | 2026-06-03 | Register App ID `dev.atoosa.mitoosa` in Apple Developer |
| BL-22 | — | 2026-06-03 | Create Firebase project + iOS app; run `flutterfire configure` _(superseded by BL-23; project ID `mitoosa-2121b`)_ |
| BL-22 | — | 2026-06-03 | Publish privacy policy and support URLs |
| BL-22 | — | 2026-06-03 | Xcode Archive → TestFlight → App Store submit |
| BL-22 | — | 2026-06-03 | Physical iPhone QA (onboarding, gameplay, share, VoiceOver, offline) |
| EP-01 | — | 2026-05-04 | Company registration (see `docs/COMPANY-REGISTRATION-READINESS.md`) |
| BL-23 | 3.2 | 2026-06-19 | Manual DebugView verification after physical device/simulator run with `FIREBASE_ENABLED=true` |

## Blocked

> **Status:** ✅ No blocked items

*(Empty — no blocked stories.)*

## Backlog

> Priority-ordered list of upcoming stories and issues.

| ID | Title | Type | Estimate | Epic | Priority | Status |
|----|-------|------|----------|------|----------|--------|
| BL-33 | Feature: Production brand assets | Feature | S | EP-01 | P0 | 🏁 Shipped |
| BL-24 | Feature: Interactive how-to demos (#47) | Feature | M | EP-01 | P1 | ⬜ Backlog |
| BL-34 | Chore: Production SFX and persisted preferences (#48) | Chore | S | EP-04 | P1 | ⬜ Backlog |
| BL-35 | Feature: Reachable daily rewards, streaks, and achievements (#49) | Feature | M | EP-01 | P1 | ⬜ Backlog |
| BL-36 | Chore: iPhone accessibility and device hardening (#50) | Chore | M | EP-01 | P1 | ⬜ Backlog |
| BL-37 | Chore: Privacy-respecting crash resilience (#51) | Chore | M | EP-02 | P1 | ⬜ Backlog |
| BL-38 | Chore: Modularize oversized code and remove dead dependencies (#52) | Chore | L | EP-05 | P2 | ⬜ Backlog |
| S1-03 | Feature: Manual wedge QA walkthrough (#5) | Feature | S | EP-01 | P1 | ⬜ Backlog |
| S1-04 | Feature: Playtest survey + recruitment (#6) | Feature | M | EP-01 | P1 | ⬜ Backlog |
| BL-04 | Feature: Backend leaderboard (post-playtest gate) (#10) | Feature | L | EP-03 | P2 | ⬜ Backlog |
| BL-05 | Feature: VIP / IAP flow (#12) | Feature | L | EP-03 | P2 | ⬜ Backlog |
| DX-01 | Chore: Complete gstack `/plan-tune` QA + ship docs (#53) | Chore | XS | EP-05 | P4 | ⬜ Backlog |
| LP-01 | Chore: Local network QR play (deferred POC) (#54) | Chore | L | EP-05 | P3 | ⬜ Backlog |
| BL-39 | Chore: Puzzle correctness audit and solvability fixes (23 rules) | Chore | L | EP-06 | P0 | ⬜ Backlog |
| BL-40 | Chore: Durable saves, validated migration, and recovery UI | Chore | L | EP-01 | P0 | ⬜ Backlog |
| BL-41 | Chore: Atomic puzzle-result commits and reward integrity | Chore | M | EP-06 | P0 | ⬜ Backlog |
| BL-42 | Feature: Five-puzzle session contract | Feature | L | EP-06 | P0 | ⬜ Backlog |
| BL-43 | Chore: Real product-analytics instrumentation | Chore | M | EP-01 | P1 | ⬜ Backlog |
| BL-44 | Feature: Working adaptive difficulty and rule curriculum | Feature | M | EP-06 | P1 | ⬜ Backlog |
| BL-45 | Chore: Truthful progress statistics and copy | Chore | M | EP-01 | P1 | ⬜ Backlog |
| BL-46 | Chore: Cohesive Aetheric Pulse visual system | Chore | L | EP-04 | P1 | ⬜ Backlog |
| BL-47 | Chore: Accessible puzzle content (non-color alternatives) | Chore | M | EP-06 | P1 | ⬜ Backlog |
| BL-48 | Chore: Coordinated game-feel feedback (animation/SFX/haptics) | Chore | M | EP-04 | P1 | ⬜ Backlog |
| BL-49 | Chore: Physical-device performance baselines | Chore | M | EP-01 | P1 | ⬜ Backlog |
| BL-50 | Chore: Native integration journey tests | Chore | M | EP-01 | P1 | ⬜ Backlog |
| BL-51 | Chore: Release and support operations hardening | Chore | L | EP-02 | P1 | ⬜ Backlog |
| BL-52 | Chore: Production asset inventory and completeness | Chore | S | EP-01 | P2 | ⬜ Backlog |
| BL-53 | Feature: Reviewed content and replayability process | Feature | M | EP-06 | P2 | ⬜ Backlog |
| BL-54 | Chore: Localization readiness (externalize text) | Chore | M | EP-05 | P2 | ⬜ Backlog |

## Epics

> Created at `/agtoosa-init`. One row per product area.

| ID | Title | Stories | Status |
|----|-------|---------|--------|
| EP-01 | Epic: Launch Readiness & Validation | 16 open / 30 total | 🟨 In Progress |
| EP-02 | Epic: Platform Release Infrastructure | 3 open / 7 total | 🟨 In Progress |
| EP-03 | Epic: Retention & Monetization Expansion | 2 open / 5 total | ⬜ Backlog |
| EP-04 | Epic: User Experience Polish | 3 open / 9 total | 🟨 In Progress |
| EP-05 | Epic: Technical Debt & Infrastructure | 4 open / 10 total | 🟨 In Progress |
| EP-06 | Epic: Gameplay Quality and Content | 6 open / 6 total | ⬜ Backlog |

**EP-01 charter:** Prove product-market fit and ship v1.5.1 iPhone launch — staging/analytics where needed, playtest validation, launch docs, and App Store readiness. Success = TestFlight build accepted and wedge KPIs measurable.

**EP-02 charter:** Unblock signed release builds for iOS (primary) and deferred Android. Signing runbooks, bundle IDs, Firebase project wiring, TestFlight pipeline.

**EP-03 charter:** Post-validation monetization and social loops — leaderboard backend (BL-04), VIP/IAP (BL-05), referral tiers (charter only — backlog story TBD) — gated on playtest metrics per `docs/PRODUCT-WEDGE.md`.

**EP-04 charter:** Aetheric Pulse design system polish — glassmorphism, navigation, tracks UI, accessibility, leaderboard demo UX.

**EP-05 charter:** CI/CD hygiene, dependency maintenance, doc archival, AgToosa framework upgrades. Local multiplayer POC (`lib/features/local_play/`) tracked as deferred experimentation — not v1.5.1 launch scope.

**EP-06 charter:** Premium gameplay quality — puzzle correctness and solvability, the five-puzzle session contract, atomic results and rewards, working adaptive difficulty, and reviewed content production. Owns BL-39, BL-41, BL-42, BL-44, BL-47, BL-53. Success = every shipped rule is solvable and validated, one free game reliably delivers a five-puzzle session with a truthful result, and difficulty/content decisions are backed by recorded player performance rather than fabricated statistics.

## Premium Quality Roadmap

> Staged plan toward a premium mobile puzzle game: five puzzles per free game (target state — current code ships up to 60), iPhone-first delivery, 25 daily free games, the +40 share bonus, and production SFX without music are preserved throughout. Findings below are evidence-backed by direct code reading (file:line citations); where noted, a finding still needs on-device or player verification before it can be marked resolved. Do not treat `docs/agtoosa-verify.sh`'s current `DEV-[0-9]+`-only ID matching as reliable automated coverage of these BL-*/EP-06 stories — it does not discover the project's real `BL-`/`EP-` IDs (see BL-51).

### Work packages summary

| ID | Priority | Epic | Finding | Depends on |
|----|----------|------|---------|------------|
| BL-39 | P0 | EP-06 | Confirmed in code (+ human review = runtime/player verification) | — (gates BL-44, BL-47, BL-53) |
| BL-40 | P0 | EP-01 | Confirmed in code | — (gates BL-41) |
| BL-41 | P0 | EP-06 | Confirmed in code | BL-40 |
| BL-42 | P0 | EP-06 | Confirmed in code (+ session-resume re-charging = requires runtime verification) | BL-41 |
| BL-43 | P1 | EP-01 | Requires runtime verification | BL-41 |
| BL-44 | P1 | EP-06 | Confirmed in code | BL-39 |
| BL-45 | P1 | EP-01 | Confirmed in code | BL-41 |
| BL-46 | P1 | EP-04 | Confirmed in code (+ direction approval = requires runtime/design verification) | BL-52 |
| BL-47 | P1 | EP-06 | Confirmed in code (+ VoiceOver completion = requires runtime verification) | BL-39 |
| BL-48 | P1 | EP-04 | Confirmed in code | BL-34 |
| BL-49 | P1 | EP-01 | Requires runtime verification | — (start Stage 1) |
| BL-50 | P1 | EP-01 | Confirmed in code (absence); requires runtime verification once built | BL-40, BL-41, BL-42, BL-24 |
| BL-51 | P1 | EP-02 | Confirmed in code/docs (+ rollout/hotfix rehearsal = requires runtime verification) | BL-37, BL-49, BL-50 |
| BL-52 | P2 | EP-01 | Confirmed in code (+ screenshot correspondence = requires device verification) | — |
| BL-53 | P2 | EP-06 | Confirmed in code (structural-only validator); player-enjoyment claim requires player verification | BL-39 |
| BL-54 | P2 | EP-05 | Confirmed in code (absence); translation beyond English is optional expansion | BL-24, BL-45 |

### Package detail

**BL-39 — Puzzle correctness** (P0, EP-06, Confirmed in code)

- _Evidence:_ `lib/core/engine/puzzle_generator.dart:399-456` — Missing Piece (`findMissing`) builds `fullSequence` from independently random items (`_randomItem`, no pattern) then blanks a random index; the removed item is "correct" only because the generator remembers it, not because it's inferable — contrast `sequenceNext` (`:460-471`), which builds a real repeating pattern first. `:1332-1349` — Number Grid computes `answer = a + b - c`; when `answer <= 0` it silently substitutes `answer.abs() + 2` as the "correct" label, which does not satisfy the puzzle's own displayed constraint ("rows sum equal"), despite the comment "This ensures the grid is solvable." `test/core/engine/puzzle_generator_test.dart:241-249,318-351` cover only item count / label-parses-as-int, never solvability; `numberGrid` is excluded from the duplicate-label stress test (`:486-510`).
- _Deliverables:_ fix Missing Piece and Number Grid; keep/extend injectable-seed reproducibility (`PuzzleGenerator([Random?])` already exists, production defaults to `Random.secure()`); independent semantic validators per rule; ≥1,000 seeds per supported rule/difficulty configuration (existing loops only cover 50–200); human review of representative puzzles.
- _Depends on:_ none — foundational; gates BL-44, BL-47, BL-53.
- _Completion checks:_ solvability/inferability assertion added for all 23 rules (not just unique-correct-option); 1,000+-seed loops green per rule/difficulty; human-review sign-off recorded with date.
- _Device/player evidence:_ none required beyond automated tests; human review is desk-based.

**BL-40 — Durable saves and recovery** (P0, EP-01, Confirmed in code)

- _Evidence:_ `lib/data/hive_persistence_provider.dart:125-136` — on hash-check failure the code calls `box.delete(playerId)` and returns `PlayerProgress.fresh(...)` silently (only a `developer.log` call); no backup, no recovery UI anywhere in `lib/`. Matches `docs/Master-Architecture.md` §9's own line: "Data at rest ... Corrupted records deleted fail-secure." (Note: the separate plaintext→encrypted box migration, `:30-89`, is already non-destructive — reads into memory and rewrites before deleting the old file; the destructive path is specifically the corrupted-record deletion, not that migration.)
- _Deliverables:_ validated migration, preserved originals, encrypted recovery, explicit recovery UI; test interrupted writes, corrupt records, missing keys, low storage, upgrades, reset. Never silently discard recoverable progress.
- _Depends on:_ none — foundational; gates BL-41.
- _Completion checks:_ no code path silently discards recoverable progress; recovery UI reachable and tested; migration/corruption test suite green.
- _Device/player evidence:_ physical-device low-storage and force-quit-mid-write smoke (feeds BL-25/BL-26 extension).

**BL-41 — Atomic results and rewards** (P0, EP-06, Confirmed in code)

- _Evidence:_ `lib/features/gameplay/gameplay_screen.dart:397-451` `_saveProgress()` — independent, unguarded Hive writes (`updateLevelStar` at `:413`, in-memory XP/coin/daily-XP mutations at `:420-438` that are not idempotency-guarded, `saveProgress` at `:440`, conditional `refuelHeartLowerLevel` at `:447`); no Lock/Mutex/Completer/transaction pattern anywhere in `lib/`. Only guard against double-tap is in-memory/UI-level (phase check), unlike `FreeGamesController`'s tested `_busy` guard (`test/features/progression/free_games_controller_test.dart:89-104`) — no equivalent test exists for the reward-commit path. `AchievementEngine.evaluateAll()` (`lib/core/engine/achievement_engine.dart:105-126`) has **zero call sites in `lib/`** outside its own test file — no achievement is ever unlocked or its coin reward granted in the shipped app, though the Achievements screen displays progress bars for them.
- _Deliverables:_ commit each result once (stars, XP, bests, reward changes, adaptive history, achievement triggers); serialize competing progress mutations. Test duplicate taps, interrupted completion, persistence failures, and relaunch without duplicate awards or lost progress.
- _Depends on:_ BL-40 (durable saves precede atomic results).
- _Completion checks:_ double-tap/interrupted-completion/relaunch tests show exactly one commit; `AchievementEngine.evaluateAll()` wired to a real call site (coordinate with BL-35's extension — same award path).
- _Device/player evidence:_ none beyond automated tests.

**BL-42 — Five-puzzle session contract** (P0, EP-06, Confirmed in code + requires runtime verification)

- _Evidence:_ `lib/core/content_provider.dart:52` — `static const int puzzlesPerSession = 60;` (target is 5; the CHANGELOG's 1.5.0 entry claiming "5-puzzle sessions" is stale — `docs/archived/plan-improvement-1.1.1-phase2.md:84-95` documents deliberately wiring it to 60). `FreeGamesController.consumeGameForStart()` already charges exactly once, at track-detail difficulty-select (`lib/features/navigation/track_detail_screen.dart:374-378`) — this part already matches "consume allowance once at confirmed start." No session-in-progress state is persisted to Hive anywhere (`sessionStartLevelIndex`/`sessionXP` are plain in-memory `Navigator` params) — on relaunch, resuming likely re-invokes `consumeGameForStart` and re-charges (strong code evidence, flagged as needing runtime confirmation). `PlayerProgress.dailyFreeGamesLimit = 25`, `shareBonusAmount = 40` (`player_progress.dart:277-278`) confirmed, preserve as-is. Note: `shareAndRefuel()` (`:333-344`, a separate heart-refuel-via-share mechanic) reuses the same `lastShareDate` guard field as the daily +40 share bonus — flag as a possible same-day interaction needing runtime confirmation, do not assume it's safe.
- _Deliverables:_ standardize one free game = one five-puzzle session, shortened only at track end; end with an explicit summary and another-game choice (a `SessionCompleteOverlay` already exists structurally per CHANGELOG — its trigger boundary needs to move to 5, not be built from scratch); align onboarding, navigation, progression gates, analytics, QA; pause active-time measurements during help and interruptions; recover an existing session without charging again.
- _Depends on:_ BL-41 (session summary needs committed results).
- _Completion checks:_ `puzzlesPerSession` reduced to 5 with track-end shortening preserved; session-resume-after-kill test proves no re-charge; `SessionCompleteOverlay` trigger boundary moved and tested.
- _Device/player evidence:_ physical-device force-quit-mid-session resume check; feeds BL-25 tasks 3.3/3.4 wording update (see extensions below).

**BL-43 — Actual product measurement** (P1, EP-01, Requires runtime verification)

- _Evidence:_ Firebase/GA scaffold shipped (S1-02, BL-23, BL-32 consent) and gated correctly at the SDK-collection level (`lib/main.dart:18-66`, `AnalyticsConsentService`), but of the 12 event factories in `lib/data/telemetry_event.dart`, only `sessionStart`/`sessionEnd` have real call sites (`lib/data/telemetry_session_controller.dart:48,67`, wired to real app lifecycle via `main_app_shell.dart:31-59`). The other 10 (`levelComplete`, `streakUpdate`, `achievementUnlocked`, `dailyRewardClaimed`, `allowanceCheck`, `allowanceDepleted`, `shareAttempt`, `shareBonusGranted`, `upgradeShown`, `upgradeTapped`) are defined but never fired from any real flow (grepped, zero call sites) — not self-documented as intentionally deferred, unlike the separate 7-event leaderboard catalog (`lib/data/leaderboard_telemetry_events.dart`), whose own doc comment explicitly defers wiring to a future BL-04 wave. No onboarding funnel events exist in code at all. No key-name payload allowlist exists (`FirebaseAnalyticsSink.sanitizeParameters()` filters by value type only, not field name).
- _Deliverables:_ emit onboarding, game start, puzzle result, session completion, and abandonment events from real flows; distinguish game sessions from app sessions; verify consent, payload allowlists, retention limits, and dashboard reconciliation; measure actual D1/D7 returns separately from stated return intent.
- _Depends on:_ BL-41 (committed results feed analytics/statistics).
- _Completion checks:_ Firebase DebugView shows each event type firing from its real flow, not a stub; a key-name payload allowlist is enforced, not just type coercion.
- _Device/player evidence:_ Firebase DebugView spot-check on physical device/simulator with `FIREBASE_ENABLED=true`.

**BL-44 — Working difficulty and curriculum** (P1, EP-06, Confirmed in code)

- _Evidence:_ `lib/core/engine/progression_engine.dart:120-163` — `computeAdaptiveMultiplier()`/`computeMasteryTier()` are correctly implemented, unit-tested pure functions, but `recordLevelResult()` (the only method that appends to `adaptiveHistory`) has zero call sites in `lib/` outside its own definition, and `computeAdaptiveMultiplier()` likewise has zero call sites — `adaptiveHistory` stays empty for every player forever. `difficultyMode` (`standard`/`adaptive`) is only read/written by a Settings toggle display; nothing branches on it to change `DifficultyParameters` fed to `PuzzleGenerator.generate()`. `lib/features/navigation/world_map_screen.dart:398-403` falls back to a **hardcoded `92.0`** "accuracy" value shown to every player, always (since history is always empty).
- _Deliverables:_ connect Adaptive mode to generated challenge and persisted performance history; define beginner/intermediate/expert progression per rule; make advertised concepts reachable. Test bounds, standard-mode reproducibility, adaptive changes, and novice/expert outcomes.
- _Depends on:_ BL-39 (puzzle correctness precedes difficulty tuning).
- _Completion checks:_ `recordLevelResult`/`computeAdaptiveMultiplier` have real call sites; the hardcoded `92.0` fallback is removed; the difficulty-mode toggle actually branches `DifficultyParameters`.
- _Device/player evidence:_ none beyond automated bounds/reproducibility tests; novice/expert outcome check can reuse the BL-53 pilot cohort.

**BL-45 — Truthful progress and copy** (P1, EP-01, Confirmed in code)

- _Evidence:_ `lib/features/main_app/progress_screen.dart:41-83` `_deriveSkills()` — its own doc comment admits "These are approximations — the engine doesn't expose per-skill scores yet." All six "Cognitive map" radar values (Pattern Recognition, Working Memory, Logical Reasoning, Reaction Speed, Spatial Sense, Focus) are one blended score with hard-coded per-skill offsets (+8/+16/+24/-8/+11) — not independently measured. Dishonest empty state: when `adaptiveHistory.isEmpty`, `base = 50` (not 0/"no data"), so every never-played player sees plausible-looking non-zero numbers. Contrast: Settings' `_MasteryCard` (`lib/features/settings/settings_screen.dart:440-448`) already has an honest empty state ("Complete levels to build your history.") — replicate that pattern. Unsupported claims confirmed verbatim: `gameplay_screen.dart:469` "IQ +1!"; `content_provider.dart:104-111` "Synapse Connected! ⚡", "Neuron Chain Formed! 🔗", "Big Brain Move! 🧬", "Neural Pathway Built! 🛤️" (random `successMessages`); `login_screen.dart:141` tagline "Unlock Your Cognitive Potential."
- _Deliverables:_ replace fabricated cognitive scores and estimated history with recorded game performance and honest empty states; remove unsupported IQ/neurological improvement claims. Every displayed statistic must trace to saved results; reconcile player-facing terminology throughout the game.
- _Depends on:_ BL-41 (statistics must trace to committed results).
- _Completion checks:_ no displayed number lacks a saved-result source; empty states match the Settings `_MasteryCard` honesty pattern; IQ/neurological strings removed (grep-checked: "IQ", "neuro", "cognitive potential").
- _Device/player evidence:_ none beyond a copy audit.

**BL-46 — Cohesive visual system** (P1, EP-04, Confirmed in code + requires runtime/design verification)

- _Evidence:_ ~26 hardcoded `Color(0xFF...)` + ~55 hardcoded `Colors.black`/`Colors.white` literals found outside `lib/theme/` (some legitimate fixed brand/semantic colors — e.g. mastery-tier medals, the puzzle shape palette — others look like dark-mode-only assumptions leaking into widgets, e.g. `progress_screen.dart:168,202,221` `Colors.white.withValues(alpha: 0.06)` for glass/progress-track effects that should pull from `Theme.of(context).colorScheme`). Light/dark theming is already wired (`lib/main.dart:86-94`, user-settable via Settings "Appearance") — not starting from zero. Zero `matchesGoldenFile`/golden-test hits anywhere in `test/`.
- _Deliverables:_ capture current screens and states, approve one Aetheric Pulse direction, then complete typography, spacing, surfaces, icons, controls, and light/dark consistency. Fix remaining hardcoded dark styling. Verify onboarding, play, results, progress, settings, dialogs, and failure states; add representative visual regression coverage.
- _Depends on:_ BL-52 (production assets feed the visual system).
- _Completion checks:_ hardcoded-literal count outside `lib/theme/` reduced to justified exceptions only; golden tests added for the listed screens; direction approved and dated.
- _Device/player evidence:_ dated screen-capture review on physical iPhone (light + dark).

**BL-47 — Accessible puzzles** (P1, EP-06, Confirmed in code + requires runtime verification)

- _Evidence:_ good baseline to preserve, confirmed in code — puzzle-option `Semantics` never leak answers: text options reuse the same visible label (`gameplay_screen.dart:914-917`), shape/image option cards use generic "Option N" labels (`:991-994`), and correctness hints ("Correct answer"/"Incorrect answer") only appear after the round is scored, matching sighted feedback timing. Genuine gap: `colorPattern` rule (`lib/core/engine/puzzle_generator.dart:349-391`, `_generateColorPattern`) picks one shape and reuses it for every option at the default filled fill — the only distinguishing signal between correct and incorrect options is `ShapeColor`. Also confirmed absent: reduced-motion support (zero `disableAnimations`/`reduceMotion` matches in `lib/`, also flagged in `docs/archived/spec-BL-36.md:31`'s own baseline) and explicit text-scale handling (zero `textScaleFactor`/`textScaler` matches).
- _Deliverables:_ make the information required to solve each puzzle perceivable through meaningful descriptions and alternatives to color alone. Preserve challenge without accessibility labels revealing answers. Test actual puzzle completion with VoiceOver, large text, reduced motion, and color-vision accommodations.
- _Depends on:_ BL-39 (shares the puzzle-rule/generator layer).
- _Completion checks:_ `colorPattern` (and any other color-only rule found on audit) has a shape/pattern/text alternative; reduced-motion and text-scale handling added at the puzzle-content layer (distinct from BL-36's app-chrome scope, to avoid duplication).
- _Device/player evidence:_ physical-device VoiceOver puzzle-completion test; color-vision-accommodation check.

**BL-48 — Game feel** (P1, EP-04, Confirmed in code)

- _Evidence:_ `assets/audio/README.md:14-15` — shipped `pop.wav`/`buzzer.wav` are explicitly documented as "test files ... generated ... as short test tones (sine-wave) to allow local testing on web," not production SFX; no music/BGM asset exists. Settings' "Music" toggle is wired to `MusicService().enabled`, and `MusicService` is a fully-built service class, but `MusicService().play(...)` has zero call sites anywhere in `lib/` (only lifecycle no-ops `.pause`/`.resume`/`.stop` are called) — this exact defect is already the explicit fix target of BL-34's existing spec (AC-005: remove the Music control/service), so BL-48 depends on BL-34 rather than re-describing the fix. No centralized action→feedback matrix exists — feedback (`AudioService`/`HapticsService`) is triggered ad hoc per call-site, documented only via doc comments (e.g. "Medium impact — e.g. correct answer, level complete"); BL-34's own spec already flags routing through a preference-aware feedback service. Static reading suggests `FeedbackToast` display doesn't gate `saveProgress` (fires as an independent `ref.listen` side-effect), but `game_over_overlay.dart`/`session_complete_overlay.dart` were not read in depth — flag as needing further verification.
- _Deliverables:_ coordinate selection, mistakes, hints, timeout, completion, and achievements through a documented animation/SFX/haptic matrix. Require immediate acknowledgement, one response per action, responsive transitions, and complete quiet/reduced-motion behavior. Presentation failures must never change results or block play.
- _Depends on:_ BL-34 (production SFX precedes feedback choreography).
- _Completion checks:_ matrix document exists and is exercised by tests; overlay presentation confirmed decoupled from `saveProgress` (resolves the flagged "needs further verification" item).
- _Device/player evidence:_ physical-device haptics/SFX smoke with sound off/on and reduced-motion on/off.

**BL-49 — Measured device performance** (P1, EP-01, Requires runtime verification)

- _Evidence:_ confirmed absent — no benchmarks, profiling scripts, frame-timing/startup-time tests, or memory/battery profiling docs exist anywhere in the repo. The only performance-adjacent item is one unchecked manual QA checkbox ("cold launch to first playable round ≤60s," `docs/qa/iphone-testflight-qa-checklist.md:18`), never executed (its evidence template is blank).
- _Deliverables:_ establish physical-device baselines before adding effects. Profile startup, response latency, frame times, memory, battery, thermal behavior, and package size. Initial internal targets: p95 usable cold launch ≤3 seconds, p95 input acknowledgement ≤100ms, ≥99% gameplay frames within the 60Hz budget. Test sustained play and lifecycle interruptions.
- _Depends on:_ none — start immediately (Stage 1), in parallel with correctness work.
- _Completion checks:_ baseline report exists with measured numbers against each target, on both the oldest supported device and representative modern hardware.
- _Device/player evidence:_ physical-device profiling only; simulator performance is explicitly insufficient. Follow Flutter's [profiling guidance](https://docs.flutter.dev/perf/ui-performance).

**BL-50 — Real application journey tests** (P1, EP-01, Confirmed in code (absence))

- _Evidence:_ confirmed absent — no `integration_test/` directory, no `integration_test` pubspec dependency, no `IntegrationTestWidgetsFlutterBinding` usage anywhere. `test/features/integration/` is a naming convention only — it still runs inside the Dart-VM widget-test harness, not Flutter's real on-device integration package. 86 total `*_test.dart` files across 13 `test/` subfolders, all unit/widget tests.
- _Deliverables:_ add native integration coverage for fresh install → tutorial → five puzzles → result → return → relaunch. Include allowance, sharing, offline play, preferences, consent, recovery, and save upgrades. Preserve unit/widget tests while checking real plugin and persistence boundaries separately.
- _Depends on:_ BL-40, BL-41, BL-42, BL-24 (the journey needs durable saves, atomic results, the 5-puzzle contract, and tutorials to exist first).
- _Completion checks:_ `integration_test` package added; the full journey passes on a real device/simulator, per Flutter's [integration-testing guidance](https://docs.flutter.dev/testing/integration-tests).
- _Device/player evidence:_ physical iPhone run of the full journey suite.

**BL-51 — Release and support operations** (P1, EP-02, Confirmed in code/docs)

- _Evidence:_ `docs/RELEASE-GATES.md` defines a 5-gate human process, not a technical pipeline; CI is explicitly scoped to PR validation only (lint/analyze/test), with a weekly `flutter test`-only cron and no other scheduled checks. `docs/decisions/remove-expensive-ci-cd.md` (Accepted) confirms 5 workflows including `dependency-maintenance.yml` were deleted specifically for cost reasons — dependency/security audits are now on-demand/local-only, not CI-enforced. No symbolication, staged/phased rollout, or hotfix-rehearsal process exists anywhere in the repo (zero mentions). Support/Privacy URLs remain unpublished — `docs/SUPPORT.md:46`, `docs/PRIVACY-POLICY.md:84`, `docs/APP-STORE-METADATA.md:31-32`, `docs/IPHONE-LAUNCH-READINESS.md:21,75-77` all still `[manual-deferred: 2026-07-11]` (consistent with, not contradicting, existing Master-Plan Manual/Deferred entries). **`DEV-*` verifier drift:** BL-27's own archived spec/test-plan/evidence (`docs/archived/spec-BL-27.md`, `docs/AgToosa_TestPlan-BL-27.md`, `docs/archived/evidence-BL-27.md`) claim a generalized `^[A-Z][A-Z0-9]*-[0-9]+$` ID-discovery pattern shipped, replacing 5 hardcoded `DEV-###`-only scans, with GREEN evidence ("17 pass, 3 warn, 0 fail"). But the actual shipped `docs/agtoosa-verify.sh` (697 lines) still hardcodes `DEV-[0-9]{3}`/`DEV-[0-9]+` literally at every gate (lines 256-257, 265, 283, 406, 578-579) — zero occurrences of any generalized pattern or `PROJECT_ID`/`ID_PATTERN` variable found. Since this file's real Epics table (EP-01–EP-06) and Active Cycle table (BL-25) contain zero `DEV-` rows, the verifier's literal patterns would not discover any of them. **Do not treat `agtoosa-verify.sh`'s current `DEV-*` gates as reliable automated coverage of this project's real `BL-*`/`EP-*` stories** — this is a static-code contradiction of BL-27's own shipped-status claim, established by reading the script, not by re-running it.
- _Deliverables:_ establish reproducible toolchains/builds, supported-device coverage, release provenance, privacy/dependency/license checks, symbolication, monitoring ownership, staged rollout, stop conditions, and a hotfix rehearsal. Verify published support/privacy links and support-ticket handling. Reconcile the existing CI-cost decision and the lifecycle-verifier drift above.
- _Depends on:_ BL-37 (crash monitoring), BL-49, BL-50 (release evidence needs profiling and integration tests).
- _Completion checks:_ hotfix rehearsal executed and logged; support/privacy URLs live and linked from ASC metadata; verifier drift noted in the verifier's own known-limitations doc (fixing the script itself is not required by this roadmap).
- _Device/player evidence:_ staged-rollout dry run; support-ticket handling smoke test.

**BL-52 — Production asset completeness** (P2, EP-01, Confirmed in code)

- _Evidence:_ inventory confirmed complete, no placeholders found: badges/6, track icons/8 (deliberate reuse across a 23-track catalog, spot-checked), avatars/12, audio/5 files (placeholder tones only, no music — see BL-48), fonts/13. `find assets -iname "*placeholder*|*todo*|*tbd*"` and `-empty` both return nothing (besides an intentional `.gitkeep`). Zero screenshot files exist anywhere in the repo — `docs/APP-STORE-METADATA.md`'s "Screenshot capture plan" is a forward-looking checklist only, confirming no screenshots have been captured against a shipped build yet.
- _Deliverables:_ inventory all shipped fonts, icons, puzzle graphics, badges, avatars, and audio. Record provenance, licenses, source files, derivatives, and size budgets. Remove placeholders and broken glyphs; verify readability at device scale and correspondence between store screenshots and the shipped build.
- _Depends on:_ none directly; feeds BL-46 and BL-51.
- _Completion checks:_ provenance/license ledger complete for every shipped asset; screenshots captured against an actual shipped build and matched to the store listing.
- _Device/player evidence:_ on-device readability check at native scale; screenshots captured on physical iPhone.

**BL-53 — Reviewed content and replayability** (P2, EP-06, Confirmed in code (structural-only validator))

- _Evidence:_ `lib/core/content/catalog_validator.dart` (`CatalogValidator`, shipped as part of BL-30) checks category allowlist, required fields, exact track count (23), and no duplicates — schema/structural validation only, not editorial/difficulty/quality review. No content style guide or versioned editorial process exists anywhere in `docs/`. `docs/playtests/FINDINGS-TEMPLATE.md` and `SURVEY-TEMPLATE.md` are blank templates, not completed reviews.
- _Deliverables:_ create a versioned editorial process for instructional examples, concept coverage, difficulty, distractors, and repetition control. Pilot one complete track before expanding across the catalog. Require reviewed examples at every tier and player evidence that variety improves enjoyment.
- _Depends on:_ BL-39 (correctness precedes content expansion).
- _Completion checks:_ editorial process document exists and is versioned; pilot track fully reviewed with a dated sign-off before any catalog-wide rollout (catalog-wide rollout itself is optional expansion, gated on pilot results).
- _Device/player evidence:_ player feedback from the pilot track (can reuse the S1-03/S1-04 moderated cohort).

**BL-54 — Localization readiness** (P2, EP-05, Confirmed in code (absence) + optional expansion)

- _Evidence:_ confirmed entirely absent — zero `.arb` files, no `l10n.yaml`, no `flutter_localizations`/`intl` in `pubspec.yaml`, zero `AppLocalizations`/`Localizations.of`/`package:intl` references in `lib/`, zero `Directionality`/`TextDirection` usage. All player-facing text is hardcoded inline English literals.
- _Deliverables:_ externalize player text, support pluralization and locale-aware formatting, and test expanded text and RTL presentation without changing puzzle meaning. Keep English as the initial release language; translation into additional languages remains market-evidence gated.
- _Depends on:_ BL-24, BL-45 (externalize after tutorial/hint and progress copy is finalized and truthful).
- _Completion checks:_ all player text routed through a structured/localized-text mechanism; an RTL layout test passes on expanded-length strings; no additional language ships as part of this item.
- _Device/player evidence:_ none required for English-only readiness; a translated-language pilot (if ever pursued) would need its own player evidence — optional expansion, out of this item's scope.

### Extensions to existing stories

These add scope notes only — no existing Backlog/Active Cycle/Completed row's Title, Type, Estimate, Epic, Priority, or Status changes, and no archived spec is contradicted.

- **BL-24:** add playable, free tutorials plus rule-specific hints and answer explanations; instructional surfaces (hints/explanations) pause timers. Builds on BL-24's existing AC-006 tutorial-panel accessibility/reduced-motion commitment — do not duplicate it.
- **BL-34:** add production-SFX asset provenance records; confirm persistent sound/haptic preferences route through one preference-aware feedback service (also feeds BL-48). Remains the sole owner of Music-control/`MusicService` removal (its existing AC-005) — BL-48 depends on, not duplicates, this.
- **BL-35:** add reachable rewards/achievements backed by one canonical catalog; wire `AchievementEngine.evaluateAll()` to real completion events (confirmed zero call sites today, see BL-41); make daily streak/milestone awards idempotent. Coordinates with BL-41's atomic-commit work on the same award path.
- **BL-36:** add physical accessibility checks (VoiceOver/Dynamic Type/Reduce Motion smoke on device) to its existing controls/touch-target/text-scale/contrast/motion-setting/device-layout scope. Puzzle-content color-only accessibility is owned by the new BL-47, not BL-36.
- **BL-37:** add early-startup failure handling, retry/recovery screens, and optional-service isolation ahead of its existing Crashlytics adapter/handler scope; privacy-respecting diagnostics stay gated behind the existing BL-32 opt-out.
- **BL-38:** add focused modularization around the new BL-39–BL-54 boundaries (puzzle generator, gameplay screen, persistence) while preserving pure-Dart engines and Hive field-order/migration compatibility. Continue deferring `MusicService` cleanup to BL-34 and `levels.json` to BL-30 — no duplication.
- **S1-03 / S1-04:** extend from bare placeholder rows to complete-journey QA and player research — comprehension, enjoyment, challenge, fatigue, hint usefulness, and observed return behavior — feeding the moderated 15–20-player cohort and observed-return cohort in the Release evidence checklist below.
- **BL-25 / BL-26:** extend outstanding manual/deferred steps to also finish physical TestFlight evidence, real screenshots, public Privacy/Support URLs, and store-listing prep, and to update BL-25's tasks 3.3 ("Complete full 3-round gameplay session") and 3.4 (share flow) wording for the five-puzzle session contract (BL-42) rather than the prior 3-round wording. BL-26's existing Manual/Deferred entries (4.1, 4.2) are unchanged.

### Delivery order and quality gates

**Stage 1 — Correctness and safety (P0):** BL-39, BL-40, BL-41, BL-42, plus BL-37's early-startup failure handling (extended). Start BL-49 (performance baselines) and BL-50's integration-test harness scaffolding immediately, in parallel.

**Stage 2 — Polished beta:** BL-24 (tutorials/hints, extended), BL-34 (production SFX, extended), BL-46 (cohesive core screens), BL-45 (truthful progress), BL-36 (accessible controls, extended), BL-43 (real measurement), plus physical-device QA via BL-25/BL-26 (extended).

**Stage 3 — Premium completion:** BL-44 (validated difficulty), BL-47 (accessible puzzle representations), BL-48 (full presentation polish), BL-53 (reviewed content), BL-52 (production assets), BL-51 (operational readiness), BL-35 (rewards/achievements reachability, extended), and completion of BL-49/BL-50.

**Stage 4 — Evidence-gated expansion (optional, not required for premium quality):** BL-54 (languages beyond English), BL-04 (leaderboard), BL-05 (VIP/IAP) — already EP-03, unchanged — plus future cloud saves, daily challenges, and multiplayer (charter-only, no backlog ID yet, same convention as EP-03's existing referral-tiers entry).

Key dependencies: durable saves (BL-40) precede atomic results (BL-41); committed results feed rewards (BL-35), analytics (BL-43), and statistics (BL-45). Puzzle correctness (BL-39) precedes difficulty tuning (BL-44) and content expansion (BL-53). Production SFX (BL-34) precedes feedback choreography (BL-48).

### Release evidence checklist

> Supplements `docs/RELEASE-GATES.md`'s existing 5-gate human process; that file is not edited by this update.

- No unresolved release-blocking incorrect puzzles, crashes, or data-loss defects (BL-39, BL-40, BL-41).
- Passing deterministic rule tests (BL-39), migration/failure tests (BL-40), and native journey tests (BL-50), per Flutter's [integration-testing guidance](https://docs.flutter.dev/testing/integration-tests).
- Physical-device profiling on the oldest supported device and representative modern hardware — simulator performance is insufficient (BL-49), per Flutter's [profiling guidance](https://docs.flutter.dev/perf/ui-performance).
- Dated visual and accessibility checks covering actual gameplay, including alternatives to color-only information (BL-47) and reduced motion (BL-36, BL-46), per Apple's [accessibility guidance](https://developer.apple.com/design/human-interface-guidelines/accessibility/).
- Moderated testing with 15–20 target players (S1-03/S1-04, extended), followed by an observed-return cohort — retaining existing goals of ≥80% reaching play within 60 seconds, ≥70% completing a session, ≥80% understanding the allowance; report cohort sizes and uncertainty.

## Active Diagnosis

*(Empty — no active diagnosis.)*

## Hypotheses

*(Empty — no active diagnosis.)*

## Completed This Cycle

| ID | Title | Shipped | Archived Spec |
|----|-------|---------|--------------|
| BL-33 | Feature: Production brand assets | 2026-07-28 | [spec-BL-33.md](archived/spec-BL-33.md) |
| BL-32 | Chore: Privacy, consent, and iOS release configuration | 2026-07-27 | [spec-BL-32.md](archived/spec-BL-32.md) |
| BL-31 | Fix: Truthful launch surfaces | 2026-07-27 | [spec-BL-31.md](archived/spec-BL-31.md) |
| BL-30 | Feature: Track catalog integrity | 2026-07-26 | [spec-BL-30.md](archived/spec-BL-30.md) |
| BL-29 | Feature: Free-games wedge delivery | 2026-07-26 | [spec-BL-29.md](archived/spec-BL-29.md) |
| BL-28 | Fix: First-run onboarding gate | 2026-07-26 | [spec-BL-28.md](archived/spec-BL-28.md) |
| BL-27 | Chore: Generalize lifecycle verifier project-ID parsing | 2026-07-26 | [spec-BL-27.md](archived/spec-BL-27.md) |
| BL-26 | Chore: App Store metadata + screenshots prep | 2026-07-11 | [spec-BL-26.md](archived/spec-BL-26.md) |
| BL-23 | Chore: FlutterFire iOS config + verify DebugView | 2026-06-20 | [spec-BL-23.md](archived/spec-BL-23.md) |
| S2-05 | Feature: Tracks UI fixes (theme-aware glass, header menus) | 2026-06-11 | [spec-S2-05.md](archived/spec-S2-05.md) |
| BL-22 | Chore: iPhone launch readiness prep (docs, bundle ID, Firebase scaffold) | 2026-06-03 | [spec-BL-22.md](archived/spec-BL-22.md) |
| S1-01 | Feature: Staging deployment & QA gate | 2026-05-11 | [spec-S1-01.md](archived/spec-S1-01.md) |
| S1-02 | Feature: Analytics backend integration (Firebase scaffold) | 2026-05-11 | [spec-s1-02.md](archived/spec-s1-02.md) |
| S1-05 | Chore: Doc cleanup & archive hygiene | 2026-05-04 | [spec-cleanup-001.md](archived/spec-cleanup-001.md) |
| S2-01 | Feature: Leaderboard screen (demo data) | 2026-05-15 | [spec-S2-01.md](archived/spec-S2-01.md) |
| S2-02 | Feature: VIP card UI (non-functional upgrade) | 2026-05-15 | [spec-S2-02.md](archived/spec-S2-02.md) |
| S2-03 | Feature: Settings & profile polish | 2026-05-15 | [spec-S2-03.md](archived/spec-S2-03.md) |
| S2-04 | Feature: Navigation & shell polish | 2026-05-15 | [spec-S2-04.md](archived/spec-S2-04.md) |
| BL-01 | Chore: iOS signing setup | 2026-05-15 | [spec-BL-01-BL-02-platform-signing.md](archived/spec-BL-01-BL-02-platform-signing.md) |
| BL-21 | Chore: Remove expensive CI/CD workflows | 2026-05-15 | [spec-BL-21.md](archived/spec-BL-21.md) |
| BL-19 | Chore: Sanitize embedded prompt-injection text in design-system docs | 2026-05-16 | [spec-BL-19.md](archived/spec-BL-19.md) |
| AP-01 | Feature: Aetheric Pulse Dark redesign | 2026-04-22 | [spec-aetheric-pulse-redesign.md](archived/spec-aetheric-pulse-redesign.md) |
| LR-01 | Chore: Launch readiness LAUNCH.md closeout | 2026-04-17 | [spec-launch-readiness-v1.md](archived/spec-launch-readiness-v1.md) |
| EL-01 | Feature: Engagement loop (hearts, hints, stars, run timer) | 2026-04-17 | [spec-engagement-loop-v1.md](archived/spec-engagement-loop-v1.md) |
| LT-01 | Feature: Local telemetry collection v1 | 2026-04-17 | [spec-local-telemetry-collection-v1.md](archived/spec-local-telemetry-collection-v1.md) |
| DM-01 | Chore: Dependency & skill maintenance system | 2026-04-15 | [spec-dependency-skill-maintenance-v1.md](archived/spec-dependency-skill-maintenance-v1.md) |
| IT-01 | Feature: iToosa → miToosa feature migration v1 | 2025-07-24 | [spec-itoosa-feature-migration-v1.md](archived/spec-itoosa-feature-migration-v1.md) |

> Older Update Log entries: [update-log-2026-05.md](archived/update-log-2026-05.md)

## Update Log

| Date | Event | By |
|------|-------|----|
| 2026-09-10 | Documentation planning update (manual edit, not an /agtoosa-* command) — added Premium Quality Roadmap section, EP-06, and BL-39–BL-54 (16 backlog items); extended BL-24, BL-34–BL-38, S1-03/S1-04, BL-25/BL-26 with premium-quality scope notes; updated Charter long-term quality objective and Non-goals; no code changes, no runtime APIs changed | Claude |
| 2026-07-28 | /agtoosa-ship — Ship 🚀 repo ship PASS — BL-33 — Aetheric Pulse brand assets; 950 tests; task 4.2 manual deferred | AgToosa |
| 2026-07-28 | /agtoosa-review — Review ✅ Approved — BL-33 — 0 critical, 1 warning (task 4.2 manual); `docs/archived/review-BL-33.md`; next `/agtoosa-next` → ship | AgToosa |
| 2026-07-28 | /agtoosa-review — Review 🔍 Started — BL-33 — 4-persona review (served by `/agtoosa-next`) | AgToosa |
| 2026-07-28 | /agtoosa-build — Build ✅ automated complete — BL-33 — Aetheric Pulse brand master, launcher icons, launch surface; 950 tests; task 4.2 manual deferred | AgToosa |
| 2026-07-28 | /agtoosa-spec — Spec ✅ Approved — BL-33 — enrolled Active Cycle | User |
| 2026-07-27 | /agtoosa-ship — Ship 🚀 repo ship PASS — BL-32 — privacy/consent + iOS manifest; 944 tests; task 4.2 manual deferred | AgToosa |
| 2026-07-27 | /agtoosa-review — Review ✅ Approved — BL-32 — 0 critical; `docs/archived/review-BL-32.md` | AgToosa |
| 2026-07-27 | /agtoosa-build — Build ✅ complete — BL-32 — consent service, Settings opt-out, PrivacyInfo.xcprivacy; 944 tests | AgToosa |
| 2026-07-27 | /agtoosa-spec — Spec ✅ Approved — BL-32 — enrolled Active Cycle | User |
| 2026-07-27 | /agtoosa-ship — Ship 🚀 repo ship PASS — BL-31 — truthful surfaces; 929 tests; task 4.3 manual deferred | AgToosa |
| 2026-07-26 | /agtoosa-review — Review ✅ Approved — BL-31 — 0 critical; `docs/archived/review-BL-31.md` | AgToosa |
| 2026-07-26 | /agtoosa-review — Review 🔍 Started — BL-31 — 4-persona review running | AgToosa |
| 2026-07-26 | /agtoosa-spec tasks — BL-31 Active Tasks tree synced from spec (4/4 automated; 4.3 manual-deferred) | AgToosa |
| 2026-07-26 | /agtoosa-spec — Spec ✅ Approved marker added — BL-31 — `docs/archived/spec-BL-31.md` | AgToosa |
| 2026-07-26 | /agtoosa-spec — Spec ✅ Approved — BL-31 — enrolled Active Cycle | User |
| 2026-07-26 | /agtoosa-review — Review ✅ Approved — BL-30 — 0 critical; `docs/archived/review-BL-30.md` | AgToosa |
| 2026-07-26 | /agtoosa-build — Build ✅ complete — BL-30 — CatalogValidator, worlds.json metadata, UI wiring; 920 tests | AgToosa |
| 2026-07-26 | /agtoosa-build — Build 🏗️ Started — BL-30 — catalog tests, assets, ContentProvider, filters | AgToosa |
| 2026-07-26 | /agtoosa-spec — Spec ✅ Approved — BL-30 — enrolled Active Cycle | User |
| 2026-07-26 | /agtoosa-ship — Ship 🚀 repo ship PASS — BL-29 — free-games wedge; 910 tests; review/evidence archived; T-007 manual deferred | AgToosa |
| 2026-07-26 | /agtoosa-review — Review ✅ Approved — BL-29 — 0 critical, 3 warnings; `docs/archived/review-BL-29.md` | AgToosa |
| 2026-07-26 | /agtoosa-review — Review 🔍 Started — BL-29 — 4-persona review (user expedite PASS) | AgToosa |
| 2026-07-26 | /agtoosa-build — Build 🔧 automated complete — BL-29 — `FreeGamesController` + share adapter; header/world-map/settings copy; track start gate; 910 tests; copy audit clean; status → Awaiting Manual (4.3 iPhone share smoke) | AgToosa |
| 2026-07-26 | /agtoosa-build — Build 🏗️ Started — BL-29 — 4 tasks; scope: free-games controller, share service, UI wiring, wedge tests | AgToosa |
| 2026-07-26 | /agtoosa-spec — Spec ✅ Approved — BL-29 — `docs/archived/spec-BL-29.md`; estimate M; enrolled in cycle | User |
| 2026-07-26 | /agtoosa-ship — Ship 🚀 repo ship PASS — BL-28 — `RootAppRouter` onboarding gate; 900 tests; ADR accepted; T-006 manual deferred | AgToosa |
| 2026-07-26 | /agtoosa-review — Review ✅ Approved — BL-28 — 0 critical, 4 warnings; `docs/archived/review-BL-28.md` | AgToosa |
| 2026-07-26 | /agtoosa-review — Review 🔍 Started — BL-28 — 4-persona review running | AgToosa |
| 2026-07-26 | /agtoosa-build — Build 🔧 automated complete — BL-28 — `RootAppRouter` gates onboarding before shell; 7 routing tests; 900 full-suite tests; `dart analyze` clean; status → Awaiting Manual (3.3 iPhone smoke) | AgToosa |
| 2026-07-26 | /agtoosa-spec — Spec ✅ Approved — BL-28 — `docs/archived/spec-BL-28.md`; estimate S; enrolled in cycle | User |
| 2026-07-26 | /agtoosa-ship — Ship 🚀 repo ship PASS — BL-27 — verifier fixture suite green; JSON exit 0; no app deploy | AgToosa |
| 2026-07-26 | /agtoosa-review — Review ✅ Approved — BL-27 — 0 critical, 3 warnings; `docs/archived/review-BL-27.md` | AgToosa |
| 2026-07-26 | /agtoosa-review — Review 🔍 Started — BL-27 — 4-persona review running | AgToosa |
| 2026-07-26 | /agtoosa-build — Build ✅ complete — BL-27 — 5/5 tasks; fixture suite green; verifier JSON exit 0 | AgToosa |
| 2026-07-26 | /agtoosa-build — Build 🏗️ Started — BL-27 — 5 tasks; scope: docs/agtoosa-verify.sh, test/tools/agtoosa_verify_test.sh | AgToosa |
| 2026-07-14 | /agtoosa-spec — Drafted BL-28–BL-38 product-readiness portfolio: 11 implementation-ready specs and AC-mapped test plans; all backlog-only and pending individual approval; BL-24 remains companion tutorial scope | AgToosa |
| 2026-07-14 | /agtoosa-spec — BL-27 enrolled in Active Cycle after BL-25 automated completion; status 🟦 Todo; build not started | AgToosa |
| 2026-07-14 | /agtoosa-build — Build ✅ automated tasks complete — BL-25 — 5/5 automated tasks green; 893 full-suite tests, 18 release tests, `dart analyze lib test` clean; status → Awaiting Manual (12 physical-device gates) | AgToosa |
| 2026-07-14 | /agtoosa-build — Tasks 🟢 1.1–1.3, 2.1 complete — BL-25 — TestFlight checklist, evidence template, launch-doc links, and focused release guard green (11 tests) | AgToosa |
| 2026-07-14 | /agtoosa-build — Build 🏗️ Started — BL-25 — 5 automated tasks; scope: TestFlight QA checklist/template, launch-doc links, release readiness guard, and full Flutter verification | AgToosa |
| 2026-07-14 | /agtoosa-spec — Spec ✅ Approved — BL-27 — `docs/archived/spec-BL-27.md`; estimate XS; queued for enrollment immediately after BL-25 automated completion | User |
| 2026-07-14 | /agtoosa-spec — BL-27 draft created: `docs/archived/spec-BL-27.md` + `docs/AgToosa_TestPlan-BL-27.md`; project-local verifier patch only; pending approval and not enrolled in Active Cycle | AgToosa |
| 2026-07-14 | /agtoosa-task — Added BL-27 P1 maintenance chore: generalize `docs/agtoosa-verify.sh` project-ID parsing; current `DEV-###` assumptions falsely fail EP-* and miss BL-25 lifecycle checks | AgToosa |
| 2026-07-12 | /agtoosa-spec — Spec ✅ Approved — BL-25 — `docs/archived/spec-BL-25.md`; estimate M; enrolled in cycle | User |
| 2026-07-12 | /agtoosa-spec BL-25 — Spec drafted; enrolled Active Cycle; awaiting approval | AgToosa |
| 2026-07-12 | /agtoosa-task — Reconciled 7 orphaned historical specs + BL-23 duplicate cleanup | AgToosa |
| 2026-07-11 | /agtoosa-ship — Ship 🚀 repo ship PASS — BL-26 — readiness tests 10/10; spec archived; URL publish + ASC screenshots manual-deferred | AgToosa |
| 2026-07-11 | /agtoosa-review — Review ✅ Approved — BL-26 — 0 critical, 8 warnings; `docs/archived/review-BL-26.md` | AgToosa |
| 2026-07-11 | /agtoosa-review — Review 🔍 Started — BL-26 — 4-persona review running | AgToosa |
| 2026-07-11 | /agtoosa-build BL-26 — Build ✅ complete — 7/7 automated tasks; 892 tests green; `dart analyze lib test` clean; 2 manual-deferred (URL publish, ASC screenshots); status → Awaiting Manual | AgToosa |
| 2026-07-11 | /agtoosa-build BL-26 — Build 🏗️ Started — 7 automated tasks; scope: privacy, support, metadata, launch docs, readiness tests | AgToosa |
| 2026-07-11 | /agtoosa-init — Phase E ✅ — 4 specialists approved and materialized: flutter-engine-guard, wedge-economy-auditor, iphone-launch-gate, hive-schema-guard → `docs/Context/specialists.md` | AgToosa |
| 2026-07-11 | /agtoosa-init — Init ✅ full refresh (option B) — codebase scan; Master-Architecture v2026-07-11; epics reconciled; 887 tests / schema v7 / Firebase iOS wired; Phases E–G pending approval | AgToosa |
| 2026-07-11 | /agtoosa-spec BL-26 — Spec ✅ Approved — `docs/archived/spec-BL-26.md`; estimate M; enrolled in Active Cycle | User |
| 2026-07-11 | /agtoosa-spec BL-26 — Spec drafted (quick); renumbered backlog metadata from BL-23→BL-26; enrolled Active Cycle; awaiting approval | AgToosa |
| 2026-06-20 | /agtoosa-ship — Ship 🚀 repo ship PASS — BL-23 — smoke 3/3; spec archived; T-005 DebugView manual-deferred | AgToosa |
| 2026-06-20 | /agtoosa-build BL-23 — Tasks 🟢 2.2, 2.3, 3.1 complete; 887 tests green; `@smoke` tags; ink_sparkle widget-test fix | AgToosa |
| 2026-06-20 | /agtoosa-review BL-23 — Review ✅ Approved — 0 critical, 5 warnings; `docs/archived/review-BL-23.md` | AgToosa |
| 2026-06-20 | /agtoosa-review BL-23 — Review 🔍 Started — 4-persona review | AgToosa |
| 2026-06-19 | /agtoosa-status follow-up — Reconciled BL-23 task tree/counter, added Wave Plan, aligned v1.5.0 changelog parity, and re-tracked DX-01/BL-19 source-of-truth entries | AgToosa |
| 2026-06-14 | /agtoosa-spec BL-24 — Spec drafted; `docs/archived/spec-BL-24.md` + test plan + ADRs; 7 ACs (6 Must); estimate M; backlog only; pending approval | AgToosa |
| 2026-06-14 | /agtoosa-build BL-23 — Firebase CLI reauth OK; `flutterfire configure` complete; `firebase_options_test.dart` updated (4 tests green) | AgToosa |
| 2026-06-11 | /agtoosa-build BL-23 — Build 🏗️ Started; spec approved; blocked on `firebase login --reauth` for `flutterfire configure` | AgToosa |
| 2026-06-11 | /agtoosa-spec BL-23 — Spec ✅ approved; `docs/AgToosa_Spec-BL-23-flutterfire-ios.md` + test plan | AgToosa |
| 2026-06-11 | /agtoosa-ship S2-05 — Ship 🚀 repo ship PASS; spec archived; manual iOS deploy deferred | AgToosa |
| 2026-06-11 | /agtoosa-review S2-05 — Review ✅ Approved — 0 critical, 7 warnings; `docs/archived/review-S2-05.md` | AgToosa |
| 2026-06-11 | /agtoosa-review S2-05 — Review 🔍 Started — 4-persona review | AgToosa |
| 2026-06-11 | /agtoosa-init re-run — Master-Plan repopulated after AgToosa v5.3.0 template reset; Master-Architecture refreshed; context confirmed; 882 tests passing | AgToosa |
| 2026-06-03 | /agtoosa-ship BL-22 — iPhone launch readiness docs/config shipped; manual App Store gates deferred | AgToosa |
| 2026-05-15 | /agtoosa-ship compaction — update log archived to `archived/update-log-2026-05.md` | AgToosa |
| 2026-05-04 | /agtoosa-init — initialization complete; context files populated, Epics seeded, TDD enabled | AgToosa |

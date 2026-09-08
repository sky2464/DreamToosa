# Profile: dart-flutter

Flutter/Dart applications. Currently: `sky2464/miToosa`.

## What to review

1. **Static analysis** — does the change keep `analysis_options.yaml` clean?
   New lint suppressions (`// ignore:`) added without a comment explaining why
   are a `code-quality` finding.
2. **Test coverage** — is there a widget or unit test under `test/` for new
   behaviour? Flutter code that changes UI state with no test is a `test-gap`.
3. **Null safety** — new `!` force-unwraps and `late` fields without a guaranteed
   initializer are the highest-yield defect class in Dart. Flag each one.
4. **Generated files** — if `build_runner` output (`*.g.dart`, `*.freezed.dart`)
   is committed, is it in sync with its source? Stale generated code compiles but
   silently drops fields.
5. **pubspec hygiene** — new dependencies pinned? `pubspec.lock` committed and
   consistent with `pubspec.yaml`? Version bumped when user-visible behaviour changed?
6. **Secrets** — Firebase config, API keys, or service-account JSON must not be
   committed. `.firebaserc` and `android/` are the usual leak sites. This is a
   `security` finding, always top priority.
7. **AgToosa alignment** — this repo carries `.agtoosa/` and `Docs/Master-Plan.md`.
   Apply the same Master-Plan drift check as the `shell-spec-driven` profile:
   does the plan reflect what shipped?
8. **CHANGELOG** — `CHANGELOG.md` updated for user-visible change.

## Verification commands

```
flutter analyze
flutter test
```

If the Flutter SDK is not present in the sandbox, say so in the report and fall
back to static reading — do not report a missing toolchain as a code defect.

## Scope note

This is a real shipping app. Prefer filing an issue over opening a fix PR for
anything touching UI layout, navigation, or state management — those need a human
looking at a running build. Fix PRs here should stay limited to lint, null-safety,
dead code, and docs.

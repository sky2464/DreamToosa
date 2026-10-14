# Product Guidelines

## Brand Voice
brand_voice: "Educational and explicit—clear docstrings, runnable examples, placeholder IDs (memstore_*, sesn_*, drm_*), status called out in prose."

## UI Style
ui_style: "N/A for primary product (CLI/docs). Downstream web targets (e.g. Crapsino) use their own stacks per profile."

## Error Message Tone
error_tone: "Actionable: state what failed, what was skipped (circuit breaker, read-only mode), and the next maintainer step."

## Accessibility Standard
accessibility: "WCAG 2.1 AA (applies when changing web-facing target repos—not hub Python docs)"

## Naming Conventions
naming_conventions:
  components: "PascalCase for classes (Dreamer, MemoryStore, DreamsClient)"
  files: "snake_case for Python modules; dream-report-YYYY-MM-DD.md for reports"
  functions: "snake_case"

## Notes
Preserve multiple reference variants unless explicitly consolidating (see AGENTS.md). Prefer additive documentation over deleting legacy examples.

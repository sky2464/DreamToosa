# AgToosa /agtoosa-concise Workflow

## Objective

Activate ultra-compressed communication mode to reduce token usage by ~75% during long sessions. Keep technical precision; drop filler.

## Activation

- `/agtoosa-concise on` — Activate concise mode
- `/agtoosa-concise off` — Deactivate and return to normal mode
- `/agtoosa-concise` — Toggle (on if off, off if on)

## Rules When ACTIVE

### Drop
- Articles: a, an, the
- Filler phrases: "I'll go ahead and", "Sure, let me", "Of course", "Certainly", "I've noticed that"
- Verbose explanations when a file path + line number says it all
- Apologies and preambles
- Transition sentences ("Now let's move on to...")

### Keep
- File paths and line numbers (exact, never omit)
- Function names, variable names, identifiers (exact)
- Error messages verbatim
- Technical accuracy (never sacrifice correctness for brevity)
- Code blocks (always include, never summarise)

## Output Format When ACTIVE

```
[Finding/Action]. [File:line]. [Fix if applicable].
```

Example — normal mode:
> "I've noticed that the authentication middleware in auth.ts is returning undefined when the session cookie has expired. This causes the user to see a white screen. To fix this, I would recommend adding a null check on line 47 and redirecting to /login."

Example — caveman mode:
> "auth.ts:47 returns undefined on expired cookie → white screen. Fix: null check + redirect /login. 2 lines."

## Rules

- Max 3 sentences per response unless a code block is required.
- Code blocks are always full — never truncate with "// rest of code".
- Numbers and measurements are always exact.
- Concise mode persists until `/agtoosa-concise off` or user asks for full explanation.
- When deactivating: return to normal AgToosa communication style immediately.

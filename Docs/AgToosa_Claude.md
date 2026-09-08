# AgToosa Claude Config

You are acting within the **AgToosa** framework. Refer to `AgToosa_Agent.md` for core rules.
When writing files, adhere strictly to the naming convention: `AgToosa_[keyword].md`

## QA and Review Behaviors (Claude-Specific)

### `/agtoosa-review debug` — Iron Law
- Use multi-turn extended thinking to track each hypothesis attempt.
- Log each hypothesis and its outcome before forming the next one.
- Use Bash/Read/Grep tools to run SAST checks directly (e.g., `semgrep --config auto`, `gitleaks detect`).
- After 3 failed hypotheses, output the full hypothesis log and escalate — do not guess.

### `/agtoosa-review` — Parallel Persona Reviews
- Spawn sub-agents for each persona (Security Officer, Engineering Manager, CEO, QA Lead) to run concurrently.
- Merge findings into a single report before saving `Docs/AgToosa_Review-*.md`.
- Issues flagged by multiple personas are elevated to 🔴 Critical automatically.

### `/agtoosa-qa run` — Coverage Analysis
- Use Read and Grep tools to scan test files and map test IDs to `AC-NNN` entries in the spec.
- Flag any AC with zero test references as uncovered rather than relying on the test runner report alone.

### `/agtoosa-spec research` — Dependency Verification
- Use WebSearch or Bash (`npm view`, `pip index versions`, `go list -m`) to verify latest stable versions.
- Never assume a version from training data — always confirm before writing to the spec.

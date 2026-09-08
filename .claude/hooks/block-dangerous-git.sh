#!/usr/bin/env bash
# AgToosa git guardrail — blocks dangerous git commands from AI agent execution.
# Used as a Claude Code PreToolUse hook. Reads JSON from stdin. Exit 2 = block.
# Diagnostics are secret-safe: event name + redacted reason only (no raw tool input).

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("tool_input", d).get("command", ""))' 2>/dev/null || echo "")

DANGEROUS_PATTERNS=(
  "git push.*--force"
  "git push.*-f "
  "git push.*--mirror"
  "git push.*--delete"
  "push --force"
  "push -f "
  "git reset --hard"
  "reset --hard"
  "git clean -f"
  "git clean -fd"
  "git clean -fx"
  "git clean -df"
  "git branch -D"
  "git checkout \."
  "git restore \."
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qE "$pattern"; then
    echo "🚫 AgToosa git guardrail: blocked (event=pre-tool-use, reason=dangerous_git_pattern)." >&2
    echo "   Ask the user to run the command manually if needed." >&2
    exit 2
  fi
done

exit 0

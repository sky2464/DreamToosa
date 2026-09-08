#!/usr/bin/env bash
set -uo pipefail

# ──────────────────────────────────────────────────────────────
# AgToosa Local Dashboard — deterministic, stdout-only renderer.
#
# Reads repo-local AgToosa artifacts; emits Markdown (default) or
# self-contained static HTML. Never writes repository files.
# Does not reimplement /agtoosa-status health scoring.
#
# Usage:
#   bash Docs/agtoosa-dashboard.sh [--root PATH] [--format markdown|html] [--log-lines N] [--help]
#
# Exit codes: 0 = ok; 2 = usage / missing Master-Plan.md
# ──────────────────────────────────────────────────────────────

ROOT="$PWD"
FORMAT="markdown"
LOG_LINES=20
LOG_LINES_MAX=200

usage() { sed -n '4,16p' "$0"; }
die_usage() { echo "Error: $1" >&2; exit 2; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) [[ $# -lt 2 ]] && die_usage "--root requires a directory"; ROOT="$2"; shift ;;
    --format) [[ $# -lt 2 ]] && die_usage "--format requires markdown or html"; FORMAT="$2"; shift ;;
    --log-lines) [[ $# -lt 2 ]] && die_usage "--log-lines requires a positive integer"; LOG_LINES="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die_usage "unknown argument '$1'" ;;
  esac
  shift
done

[[ -d "$ROOT" ]] || die_usage "root '$ROOT' is not a directory"
case "$FORMAT" in markdown|html) ;; *) die_usage "--format must be markdown or html (got '$FORMAT')" ;; esac
if ! [[ "$LOG_LINES" =~ ^[1-9][0-9]*$ ]]; then die_usage "--log-lines must be a positive integer (got '$LOG_LINES')"; fi
if (( LOG_LINES > LOG_LINES_MAX )); then die_usage "--log-lines exceeds maximum of $LOG_LINES_MAX"; fi

# Prefer Docs/ then docs/; match real directory casing (case-insensitive FS safe).
DOCS=""; DOCS_REL=""
_docs_names="$(ls -1 "$ROOT" 2>/dev/null || true)"
if printf '%s\n' "$_docs_names" | grep -qx 'Docs' && [[ -f "$ROOT/Docs/Master-Plan.md" ]]; then
  DOCS="$ROOT/Docs"; DOCS_REL="Docs"
elif printf '%s\n' "$_docs_names" | grep -qx 'docs' && [[ -f "$ROOT/docs/Master-Plan.md" ]]; then
  DOCS="$ROOT/docs"; DOCS_REL="docs"
else
  echo "Error: no Docs/Master-Plan.md or docs/Master-Plan.md under '$ROOT'." >&2; exit 2
fi
unset _docs_names

MP="$DOCS/Master-Plan.md"
[[ -r "$MP" ]] || { echo "Error: Master-Plan.md is not readable at '$MP'." >&2; exit 2; }

GENERATED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
MP_REL="${DOCS_REL}/Master-Plan.md"
WARNINGS=()

escape_html() {
  local s="${1-}"
  s="${s//&/&amp;}"; s="${s//</&lt;}"; s="${s//>/&gt;}"
  s="${s//\"/&quot;}"; s="${s//\'/&#39;}"
  printf '%s' "$s"
}

is_safe_repo_pointer() {
  local p="${1-}"
  case "$p" in *://*|*..*|*$'\n'*|*$'\r'*) return 1 ;; esac
  [[ "$p" =~ ^(docs|Docs)/[A-Za-z0-9._/-]+$ ]]
}

extract_section_rows() {
  local file="$1" heading="$2"
  awk -v h="$heading" '
    BEGIN { in_sec=0; sep=0 }
    /^## / {
      if (in_sec) exit
      title=$0; sub(/^##[[:space:]]+/, "", title)
      if (title == h) in_sec=1
      next
    }
    in_sec && /^\|/ {
      if ($0 ~ /^[[:space:]]*\|[-:| ]+\|[[:space:]]*$/) { sep=1; next }
      if (!sep) next
      print
    }
  ' "$file"
}

trim_cell() {
  local c="${1-}"
  c="${c#"${c%%[![:space:]]*}"}"; c="${c%"${c##*[![:space:]]}"}"
  printf '%s' "$c"
}

cell() { trim_cell "$(printf '%s\n' "$1" | awk -F'|' -v n="$2" '{print $(n+1)}')"; }

json_field() { printf '%s' "$1" | sed -n "s/.*\"$2\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p"; }

# ── Parse Master-Plan ─────────────────────────────────────────
CHARTER_LINES=(); ACTIVE_LINES=(); BLOCKED_LINES=()
HAS_IN_PROGRESS=0; HAS_DONE=0; HAS_TODO=0; ACTIVE_COUNT=0; BLOCKED_COUNT=0

while IFS= read -r row; do
  [[ -z "$row" ]] && continue
  field="$(cell "$row" 1)"; value="$(cell "$row" 2)"
  [[ -z "$field" || "$field" == "Field" ]] && continue
  CHARTER_LINES+=("$field|$value")
done < <(extract_section_rows "$MP" "Project Charter")

while IFS= read -r row; do
  [[ -z "$row" ]] && continue
  id="$(cell "$row" 1)"; title="$(cell "$row" 2)"; type="$(cell "$row" 3)"
  estimate="$(cell "$row" 4)"; status="$(cell "$row" 5)"; tasks="$(cell "$row" 6)"
  [[ -z "$id" || "$id" == "ID" ]] && continue
  ACTIVE_LINES+=("$id|$title|$type|$estimate|$status|$tasks")
  ACTIVE_COUNT=$((ACTIVE_COUNT + 1))
  case "$status" in *In\ Progress*|🟨*) HAS_IN_PROGRESS=1 ;; *Done*|✅*) HAS_DONE=1 ;; *Todo*|🟦*) HAS_TODO=1 ;; esac
done < <(extract_section_rows "$MP" "Active Cycle")

while IFS= read -r row; do
  [[ -z "$row" ]] && continue
  id="$(cell "$row" 1)"; title="$(cell "$row" 2)"; by="$(cell "$row" 3)"; since="$(cell "$row" 4)"
  [[ -z "$id" || "$id" == "ID" ]] && continue
  BLOCKED_LINES+=("$id|$title|$by|$since"); BLOCKED_COUNT=$((BLOCKED_COUNT + 1))
done < <(extract_section_rows "$MP" "Blocked")

# ── Optional sources ──────────────────────────────────────────
EVIDENCE_LINES=(); ARCHIVED="$DOCS/archived"
if [[ -d "$ARCHIVED" ]]; then
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    base="$(basename "$f")"; story="${base#evidence-}"; story="${story%.md}"
    EVIDENCE_LINES+=("$story|${DOCS_REL}/archived/${base}")
  done < <(find "$ARCHIVED" -maxdepth 1 -type f -name 'evidence-*.md' 2>/dev/null | LC_ALL=C sort)
fi
[[ ${#EVIDENCE_LINES[@]} -eq 0 ]] && WARNINGS+=("Evidence Index: Unavailable (no ${DOCS_REL}/archived/evidence-*.md)")

LATEST_RETRO=""; LATEST_RETRO_REL=""
[[ -d "$ARCHIVED" ]] && LATEST_RETRO="$(find "$ARCHIVED" -maxdepth 1 -type f -name 'retro-*.md' 2>/dev/null | LC_ALL=C sort | tail -1)"
if [[ -n "$LATEST_RETRO" && -r "$LATEST_RETRO" ]]; then
  LATEST_RETRO_REL="${DOCS_REL}/archived/$(basename "$LATEST_RETRO")"
else
  WARNINGS+=("Latest Retrospective: Unavailable (no ${DOCS_REL}/archived/retro-*.md)")
fi

EVENT_LINES=(); EVENTS_FILE="$DOCS/agtoosa-events.jsonl"; MALFORMED=0
if [[ -f "$EVENTS_FILE" ]]; then
  valid_tmp="$(mktemp)"
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" ]] && continue
    if [[ "$line" =~ ^\{.*\"ts\".*\}$ ]]; then
      printf '%s\n' "$line" >> "$valid_tmp"
    else
      MALFORMED=$((MALFORMED + 1))
    fi
  done < "$EVENTS_FILE"
  if (( MALFORMED > 0 )); then
    echo "Warning: skipped $MALFORMED malformed event row(s) in ${DOCS_REL}/agtoosa-events.jsonl" >&2
    WARNINGS+=("Recent Events: skipped $MALFORMED malformed row(s)")
  fi
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    EVENT_LINES+=("$line")
  done < <(tail -n "$LOG_LINES" "$valid_tmp")
  rm -f "$valid_tmp"
else
  WARNINGS+=("Recent Events: Unavailable (no ${DOCS_REL}/agtoosa-events.jsonl)")
fi

# ── Next actions (Master-Plan subset only) ────────────────────
NEXT_ACTIONS=()
(( ACTIVE_COUNT == 0 )) && NEXT_ACTIONS+=("Run \`/agtoosa-spec\` to enroll the next story (Active Cycle is empty).")
(( HAS_IN_PROGRESS == 1 )) && NEXT_ACTIONS+=("Run \`/agtoosa-build\` to advance In Progress Active Cycle work.")
(( HAS_TODO == 1 && HAS_IN_PROGRESS == 0 )) && NEXT_ACTIONS+=("Run \`/agtoosa-spec\` or \`/agtoosa-build\` to start Todo Active Cycle work.")
(( BLOCKED_COUNT > 0 )) && NEXT_ACTIONS+=("Resolve Blocked items or run \`/agtoosa-task\` to re-scope.")
(( HAS_DONE == 1 )) && NEXT_ACTIONS+=("Run \`/agtoosa-ship\` if Done stories are ready to close the cycle.")
NEXT_ACTIONS+=("Run \`/agtoosa-status\` for health analysis (not duplicated here).")

# ── Markdown ──────────────────────────────────────────────────
render_markdown() {
  cat <<EOF
# AgToosa Local Dashboard

> Generated: $GENERATED_AT
> Selected Master-Plan: \`$MP_REL\`
> Format: markdown
> Read-only — stdout only; no repository files were modified.

## Project Charter

| Field | Value |
|-------|-------|
EOF
  if [[ ${#CHARTER_LINES[@]} -eq 0 ]]; then echo "| — | Unavailable |"
  else local line; for line in "${CHARTER_LINES[@]}"; do echo "| ${line%%|*} | ${line#*|} |"; done; fi

  cat <<'EOF'

## Active Stories

| ID | Title | Type | Estimate | Status | Tasks Done |
|----|-------|------|----------|--------|-----------|
EOF
  if [[ ${#ACTIVE_LINES[@]} -eq 0 ]]; then echo "| — | *(none)* | — | — | — | — |"
  else
    local line id title type estimate status tasks
    for line in "${ACTIVE_LINES[@]}"; do
      IFS='|' read -r id title type estimate status tasks <<<"$line"
      echo "| $id | $title | $type | $estimate | $status | $tasks |"
    done
  fi

  cat <<'EOF'

## Blocked

| ID | Title | Blocked by | Since |
|----|-------|-----------|-------|
EOF
  if [[ ${#BLOCKED_LINES[@]} -eq 0 ]]; then echo "| — | *(none)* | — | — |"
  else
    local line id title by since
    for line in "${BLOCKED_LINES[@]}"; do
      IFS='|' read -r id title by since <<<"$line"
      echo "| $id | $title | $by | $since |"
    done
  fi

  cat <<EOF

## Evidence Index

> Non-authoritative projection of \`archived/evidence-*.md\` pointers.

| Story | Pointer |
|-------|---------|
EOF
  if [[ ${#EVIDENCE_LINES[@]} -eq 0 ]]; then echo "| — | Unavailable |"
  else local line; for line in "${EVIDENCE_LINES[@]}"; do echo "| ${line%%|*} | ${line#*|} |"; done; fi

  cat <<EOF

## Recent Events

> Non-authoritative projection of \`agtoosa-events.jsonl\` (capped at $LOG_LINES valid rows).

| ts | phase | event | story |
|----|-------|-------|-------|
EOF
  if [[ ${#EVENT_LINES[@]} -eq 0 ]]; then echo "| — | — | Unavailable | — |"
  else
    local line ts phase event story
    for line in "${EVENT_LINES[@]}"; do
      ts="$(json_field "$line" ts)"; phase="$(json_field "$line" phase)"
      event="$(json_field "$line" event)"; story="$(json_field "$line" story)"
      echo "| ${ts:-?} | ${phase:-?} | ${event:-?} | ${story:-?} |"
    done
  fi

  cat <<EOF

## Latest Retrospective

> Non-authoritative projection — proposals do not override Master-Plan.

EOF
  if [[ -z "$LATEST_RETRO_REL" ]]; then echo "Unavailable"
  else
    echo "Pointer: \`$LATEST_RETRO_REL\` (non-authoritative projection)"
    if grep -q '^## Proposals' "$LATEST_RETRO" 2>/dev/null; then
      echo ""; echo "Proposals present in latest retro (route via \`/agtoosa-task\` / \`/agtoosa-spec\` — do not auto-enroll)."
    fi
  fi
  echo ""
  if [[ ${#WARNINGS[@]} -gt 0 ]]; then
    echo "## Warnings"; echo ""
    local w; for w in "${WARNINGS[@]}"; do echo "- $w"; done; echo ""
  fi
  cat <<EOF
## Recommended Next Actions

> Deterministic subset from Master-Plan state only. For full health scoring and fix ranking, run \`/agtoosa-status\`.

EOF
  local i=1 a
  for a in "${NEXT_ACTIONS[@]}"; do echo "$i. $a"; i=$((i + 1)); done
  cat <<EOF

---

**Source of truth:** \`$MP_REL\` is the repo-local source of truth.
Evidence, retrospectives, events, and external-integration references above are **non-authoritative projections**.
Use \`/agtoosa-status\` for health analysis — this dashboard does not compute the Status health score.
EOF
}

# ── HTML ──────────────────────────────────────────────────────
html_row() {
  printf '<tr>'
  local c; for c in "$@"; do printf '<td>%s</td>' "$(escape_html "$c")"; done
  printf '</tr>\n'
}

render_html() {
  local line field value id title type estimate status tasks by since
  local ts phase event story w a
  cat <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>AgToosa Local Dashboard</title>
<style>
body{font-family:ui-sans-serif,system-ui,sans-serif;margin:1.5rem;line-height:1.45;color:#111;background:#fafafa}
h1,h2{margin-top:1.4rem}table{border-collapse:collapse;width:100%;margin:.6rem 0 1.2rem;background:#fff}
th,td{border:1px solid #ccc;padding:.35rem .55rem;text-align:left;vertical-align:top}th{background:#eee}
.meta,.footer{color:#444;font-size:.95rem}.note{color:#555;font-style:italic}
code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.9em}
.warn{background:#fff8e6;border:1px solid #e6d08a;padding:.6rem .8rem;margin:1rem 0}
</style>
</head>
<body>
<h1>AgToosa Local Dashboard</h1>
<p class="meta">Generated: $(escape_html "$GENERATED_AT")<br>
Selected Master-Plan: <code>$(escape_html "$MP_REL")</code><br>
Format: html<br>
Read-only — stdout only; no repository files were modified.</p>
<h2>Project Charter</h2>
<table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>
EOF
  if [[ ${#CHARTER_LINES[@]} -eq 0 ]]; then html_row "—" "Unavailable"
  else for line in "${CHARTER_LINES[@]}"; do html_row "${line%%|*}" "${line#*|}"; done; fi
  cat <<EOF
</tbody></table>
<h2>Active Stories</h2>
<table><thead><tr><th>ID</th><th>Title</th><th>Type</th><th>Estimate</th><th>Status</th><th>Tasks Done</th></tr></thead><tbody>
EOF
  if [[ ${#ACTIVE_LINES[@]} -eq 0 ]]; then html_row "—" "(none)" "—" "—" "—" "—"
  else
    for line in "${ACTIVE_LINES[@]}"; do
      IFS='|' read -r id title type estimate status tasks <<<"$line"
      html_row "$id" "$title" "$type" "$estimate" "$status" "$tasks"
    done
  fi
  cat <<EOF
</tbody></table>
<h2>Blocked</h2>
<table><thead><tr><th>ID</th><th>Title</th><th>Blocked by</th><th>Since</th></tr></thead><tbody>
EOF
  if [[ ${#BLOCKED_LINES[@]} -eq 0 ]]; then html_row "—" "(none)" "—" "—"
  else
    for line in "${BLOCKED_LINES[@]}"; do
      IFS='|' read -r id title by since <<<"$line"
      html_row "$id" "$title" "$by" "$since"
    done
  fi
  cat <<EOF
</tbody></table>
<h2>Evidence Index</h2>
<p class="note">Non-authoritative projection of archived evidence pointers.</p>
<table><thead><tr><th>Story</th><th>Pointer</th></tr></thead><tbody>
EOF
  if [[ ${#EVIDENCE_LINES[@]} -eq 0 ]]; then printf '<tr><td>—</td><td>%s</td></tr>\n' "$(escape_html "Unavailable")"
  else
    for line in "${EVIDENCE_LINES[@]}"; do
      printf '<tr><td>%s</td>' "$(escape_html "${line%%|*}")"
      if is_safe_repo_pointer "${line#*|}"; then
        printf '<td><code>%s</code></td>' "$(escape_html "${line#*|}")"
      else
        printf '<td>%s</td>' "$(escape_html "${line#*|}")"
      fi
      printf '</tr>\n'
    done
  fi
  cat <<EOF
</tbody></table>
<h2>Recent Events</h2>
<p class="note">Non-authoritative projection of agtoosa-events.jsonl (capped at $(escape_html "$LOG_LINES") valid rows).</p>
<table><thead><tr><th>ts</th><th>phase</th><th>event</th><th>story</th></tr></thead><tbody>
EOF
  if [[ ${#EVENT_LINES[@]} -eq 0 ]]; then html_row "—" "—" "Unavailable" "—"
  else
    for line in "${EVENT_LINES[@]}"; do
      html_row "$(json_field "$line" ts)" "$(json_field "$line" phase)" "$(json_field "$line" event)" "$(json_field "$line" story)"
    done
  fi
  cat <<EOF
</tbody></table>
<h2>Latest Retrospective</h2>
<p class="note">Non-authoritative projection — proposals do not override Master-Plan.</p>
EOF
  if [[ -z "$LATEST_RETRO_REL" ]]; then echo "<p>Unavailable</p>"
  else echo "<p>Pointer: <code>$(escape_html "$LATEST_RETRO_REL")</code></p>"; fi
  if [[ ${#WARNINGS[@]} -gt 0 ]]; then
    echo '<div class="warn"><strong>Warnings</strong><ul>'
    for w in "${WARNINGS[@]}"; do echo "<li>$(escape_html "$w")</li>"; done
    echo '</ul></div>'
  fi
  cat <<EOF
<h2>Recommended Next Actions</h2>
<p class="note">Deterministic subset from Master-Plan state only. For full health scoring and fix ranking, run <code>/agtoosa-status</code>.</p>
<ol>
EOF
  for a in "${NEXT_ACTIONS[@]}"; do echo "<li>$(escape_html "$a")</li>"; done
  cat <<EOF
</ol>
<hr>
<p class="footer"><strong>Source of truth:</strong> <code>$(escape_html "$MP_REL")</code> is the repo-local source of truth.
Evidence, retrospectives, events, and external-integration references above are <strong>non-authoritative projections</strong>.
Use <code>/agtoosa-status</code> for health analysis — this dashboard does not compute the Status health score.</p>
</body>
</html>
EOF
}

case "$FORMAT" in
  markdown) render_markdown ;;
  html) render_html ;;
esac
exit 0

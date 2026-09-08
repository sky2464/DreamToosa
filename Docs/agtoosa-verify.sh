#!/usr/bin/env bash
set -uo pipefail

# ──────────────────────────────────────────────────────────────
# AgToosa Verifier — deterministic, read-only lifecycle gate.
#
# No AI, no network. Validates that the repo's AgToosa state is
# internally consistent: context files, Master-Plan integrity,
# spec approval, EARS acceptance criteria, AC-to-test mapping,
# threat model, task tree + wave plan, and TDD evidence blocks.
#
# Usage:
#   bash Docs/agtoosa-verify.sh [--root <repo-root>] [--strict]
#                               [--format text|json] [stats]
#
# Exit codes: 0 = pass, 1 = findings (FAIL), 2 = usage/setup error.
# --strict promotes WARN findings to failures.
# --format json emits a single verify-result-v1 document on stdout.
# `stats` prints cycle analytics from the Master-Plan Update Log
# and phase-event log instead of running gate checks.
# ──────────────────────────────────────────────────────────────

ROOT="$PWD"
STRICT=false
MODE="verify"
FORMAT="text"
MAX_FINDINGS=200

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      [[ $# -lt 2 ]] && { echo "Error: --root requires a directory" >&2; exit 2; }
      ROOT="$2"; shift ;;
    --strict) STRICT=true ;;
    --format)
      [[ $# -lt 2 ]] && { echo "Error: --format requires text|json" >&2; exit 2; }
      FORMAT="$2"; shift
      case "$FORMAT" in text|json) ;; *)
        echo "Error: invalid --format '$FORMAT' (expected text|json)" >&2; exit 2 ;;
      esac ;;
    stats)    MODE="stats" ;;
    -h|--help)
      sed -n '4,22p' "$0"; exit 0 ;;
    *)
      echo "Error: unknown argument '$1'" >&2; exit 2 ;;
  esac
  shift
done

[[ -d "$ROOT" ]] || { echo "Error: root '$ROOT' is not a directory" >&2; exit 2; }

# Detect docs dir: Docs/ (generated projects) or docs/ (AgToosa maintainer repo).
DOCS=""
if [[ -f "$ROOT/Docs/Master-Plan.md" ]]; then
  DOCS="$ROOT/Docs"
elif [[ -f "$ROOT/docs/Master-Plan.md" ]]; then
  DOCS="$ROOT/docs"
else
  echo "Error: no Docs/Master-Plan.md or docs/Master-Plan.md under '$ROOT'." >&2
  echo "Run /agtoosa-init (or agtoosa.sh) first." >&2
  exit 2
fi
MP="$DOCS/Master-Plan.md"

PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0
FINDINGS_FILE="$(mktemp)"
trap 'rm -f "$FINDINGS_FILE"' EXIT

# Append one finding as a JSON object line (python-escaped later).
# Args: severity id problem impact fix assurance [ac_refs_csv]
_add_finding() {
  local severity="$1" id="$2" problem="$3" impact="$4" fix="$5" assurance="$6"
  local ac_refs="${7:-}"
  local total=$((WARN_COUNT + FAIL_COUNT))
  if [[ $total -ge $MAX_FINDINGS ]]; then
    return 0
  fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$severity" "$id" "$problem" "$impact" "$fix" "$assurance" "$ac_refs" >> "$FINDINGS_FILE"
}

_human_block() {
  local icon="$1" label="$2" id="$3" problem="$4" impact="$5" fix="$6"
  echo "  ${icon} ${label}  ${id}"
  echo "  Problem: ${problem}"
  echo "  Impact:  ${impact}"
  echo "  Fix:     ${fix}"
}

pass() {
  PASS_COUNT=$((PASS_COUNT + 1))
  if [[ "$FORMAT" == "text" ]]; then
    echo "  ✅ PASS  $1"
  fi
}

warn() {
  # Args: id problem impact fix assurance [ac_refs]
  local id="$1" problem="$2" impact="$3" fix="$4" assurance="${5:-guided}" ac_refs="${6:-}"
  WARN_COUNT=$((WARN_COUNT + 1))
  _add_finding "warn" "$id" "$problem" "$impact" "$fix" "$assurance" "$ac_refs"
  if [[ "$FORMAT" == "text" ]]; then
    _human_block "⚠️ " "WARN" "$id" "$problem" "$impact" "$fix"
  fi
}

fail() {
  local id="$1" problem="$2" impact="$3" fix="$4" assurance="${5:-enforced}" ac_refs="${6:-}"
  FAIL_COUNT=$((FAIL_COUNT + 1))
  _add_finding "fail" "$id" "$problem" "$impact" "$fix" "$assurance" "$ac_refs"
  if [[ "$FORMAT" == "text" ]]; then
    _human_block "❌" "FAIL" "$id" "$problem" "$impact" "$fix"
  fi
}

gate() { if [[ "$FORMAT" == "text" ]]; then echo "$1"; fi; }

emit_json() {
  local exit_code="$1"
  PASS_COUNT="$PASS_COUNT" WARN_COUNT="$WARN_COUNT" FAIL_COUNT="$FAIL_COUNT" \
  FINDINGS_FILE="$FINDINGS_FILE" EXIT_CODE="$exit_code" python3 - <<'PY'
import json, os
findings = []
path = os.environ["FINDINGS_FILE"]
if os.path.exists(path) and os.path.getsize(path) > 0:
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t", 6)
            if len(parts) < 6:
                continue
            sev, fid, problem, impact, fix, assurance = parts[:6]
            ac_csv = parts[6] if len(parts) > 6 else ""
            item = {
                "id": fid,
                "severity": sev,
                "problem": problem,
                "impact": impact,
                "fix": fix,
                "assurance": assurance,
            }
            refs = [r for r in ac_csv.split(",") if r]
            if refs:
                item["ac_refs"] = refs
            findings.append(item)
doc = {
    "schema_version": "verify-result-v1",
    "tool": "verify",
    "exit_code": int(os.environ["EXIT_CODE"]),
    "summary": {
        "pass": int(os.environ["PASS_COUNT"]),
        "warn": int(os.environ["WARN_COUNT"]),
        "fail": int(os.environ["FAIL_COUNT"]),
    },
    "findings": findings,
}
print(json.dumps(doc, ensure_ascii=False, separators=(",", ":")))
PY
}

finish() {
  local exit_code=0
  if [[ $FAIL_COUNT -gt 0 ]]; then
    exit_code=1
  elif [[ "$STRICT" == true && $WARN_COUNT -gt 0 ]]; then
    exit_code=1
  fi
  if [[ "$FORMAT" == "json" ]]; then
    emit_json "$exit_code"
  else
    echo ""
    echo "──────────────────────────────────────────"
    echo "Verifier summary: $PASS_COUNT pass · $WARN_COUNT warn · $FAIL_COUNT fail"
    if [[ $FAIL_COUNT -gt 0 ]]; then
      echo "Result: ❌ FAIL"
    elif [[ "$STRICT" == true && $WARN_COUNT -gt 0 ]]; then
      echo "Result: ❌ FAIL (strict mode: warnings are failures)"
    else
      echo "Result: ✅ PASS"
    fi
  fi
  exit "$exit_code"
}

# ── stats mode ────────────────────────────────────────────────
run_stats() {
  echo "AgToosa stats — $ROOT"
  echo ""
  local total_rows ships specs builds reviews
  total_rows=$(grep -cE '^\| [0-9]{4}-[0-9]{2}-[0-9]{2}' "$MP" 2>/dev/null || echo 0)
  ships=$(grep -cE '^\| [0-9]{4}-[0-9]{2}-[0-9]{2}.*(Ship complete|Ship 🚀 Deployed)' "$MP" 2>/dev/null || echo 0)
  specs=$(grep -cE '^\| [0-9]{4}-[0-9]{2}-[0-9]{2}.*(/agtoosa-spec|Spec approved|Spec Approved)' "$MP" 2>/dev/null || echo 0)
  builds=$(grep -cE '^\| [0-9]{4}-[0-9]{2}-[0-9]{2}.*(Build complete|Build started)' "$MP" 2>/dev/null || echo 0)
  reviews=$(grep -cE '^\| [0-9]{4}-[0-9]{2}-[0-9]{2}.*Review' "$MP" 2>/dev/null || echo 0)
  echo "Update Log rows:       $total_rows"
  echo "Spec events:           $specs"
  echo "Build events:          $builds"
  echo "Review events:         $reviews"
  echo "Ship completions:      $ships"
  local archived_specs archived_reviews
  archived_specs=$(find "$DOCS/archived" -name 'spec-*.md' 2>/dev/null | wc -l | tr -d ' ')
  archived_reviews=$(find "$DOCS/archived" -name 'review-*.md' 2>/dev/null | wc -l | tr -d ' ')
  echo "Archived specs:        $archived_specs"
  echo "Archived reviews:      $archived_reviews"
  local events="$DOCS/agtoosa-events.jsonl"
  if [[ -f "$events" ]]; then
    echo "Phase events recorded: $(wc -l < "$events" | tr -d ' ')"
    if command -v jq &>/dev/null; then
      echo ""
      echo "Events by phase:"
      jq -r '.phase' "$events" 2>/dev/null | sort | uniq -c | sed 's/^/  /'
    fi
  else
    echo "Phase events recorded: 0 (no $events yet)"
  fi
  if [[ $total_rows -gt 150 ]]; then
    echo ""
    echo "⚠️  Update Log has $total_rows rows — rotate older rows to ${DOCS}/archived/updatelog-<year>.md (see AgToosa_Ship.md)."
  fi
  exit 0
}

[[ "$MODE" == "stats" ]] && run_stats

if [[ "$FORMAT" == "text" ]]; then
  echo "AgToosa Verifier — $ROOT"
  echo "Docs root: $DOCS"
  echo ""
fi

# ── Gate 1: context files populated ───────────────────────────
gate "Gate 1 — Context files"
ctx_missing=0
for f in product.md tech-stack.md workflow.md; do
  if [[ ! -f "$DOCS/Context/$f" ]]; then
    fail "G1-missing-$f" "missing $DOCS/Context/$f (run /agtoosa-init)" \
      "Lifecycle gates cannot validate product/tech/workflow context." \
      "Create Docs/Context/$f via /agtoosa-init." enforced
    ctx_missing=1
  fi
done
if [[ $ctx_missing -eq 0 ]]; then
  if grep -lE '\[name\]|\[url\]|\[e\.g\.|\[N\]|\[YYYY-MM-DD\]' \
       "$DOCS/Context/product.md" "$DOCS/Context/tech-stack.md" "$DOCS/Context/workflow.md" >/dev/null 2>&1; then
    warn "G1-placeholders" "context files contain template placeholders (run /agtoosa-init)" \
      "Agents may treat placeholders as real product facts." \
      "Replace placeholders in Docs/Context/*.md via /agtoosa-init." guided
  else
    pass "context files exist with no template placeholders"
  fi
fi

# ── Gate 2: Master-Plan integrity ──────────────────────────────
gate "Gate 2 — Master-Plan integrity"
if grep -qE '^\| DEV-[0-9]+ .*\| Epic' "$MP" || grep -qE '^\| DEV-[0-9]{3} \| Epic' "$MP" \
   || grep -A5 '^## Epics' "$MP" | grep -qE '\| DEV-[0-9]+'; then
  pass "Epics section has at least one real epic row"
else
  fail "G2-epics" "no real Epic rows in Master-Plan ## Epics (run /agtoosa-init)" \
    "Without epics, story planning and Active Cycle tracking lack structure." \
    "Add at least one epic row under ## Epics (run /agtoosa-init)." enforced
fi

dup_ids=$(grep -oE 'DEV-[0-9]{3}' "$MP" | sort | uniq -c | awk '$1 > 50 {print $2}')
if [[ -n "$dup_ids" ]]; then
  warn "G2-dup-ids" "story IDs appear unusually often (possible Update Log bloat): $(echo "$dup_ids" | tr '\n' ' ')" \
    "Update Log noise can hide real status changes." \
    "Rotate older Update Log rows to archived/updatelog-<year>.md." guided
fi

log_rows=$(grep -cE '^\| [0-9]{4}-[0-9]{2}-[0-9]{2}' "$MP" 2>/dev/null || echo 0)
if [[ $log_rows -gt 150 ]]; then
  warn "G2-log-bloat" "Update Log has $log_rows rows; rotate older rows to archived/updatelog-<year>.md" \
    "Large Update Logs slow reviews and inflate Master-Plan noise." \
    "Move older rows to Docs/archived/updatelog-<year>.md (see AgToosa_Ship.md)." guided
else
  pass "Update Log within rotation budget ($log_rows rows)"
fi

# ── Gate 3: active stories have approved specs ────────────────
gate "Gate 3 — Spec approval and naming"
active_ids=$(awk '/^## Active Cycle/,/^## [^A]/' "$MP" | grep -oE '^\| DEV-[0-9]{3}' | grep -oE 'DEV-[0-9]{3}' | sort -u)
if [[ -z "$active_ids" ]]; then
  cycle_state=$(awk -F'|' '
    /^## Project Charter[[:space:]]*$/ { in_charter=1; next }
    in_charter && /^## / { exit }
    in_charter && /^\|/ {
      key=$2
      value=$3
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", key)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
      if (tolower(key) == "cycle state") { print value; exit }
    }
  ' "$MP")
  cycle_state_lc=$(printf '%s' "$cycle_state" | tr '[:upper:]' '[:lower:]')
  if [[ "$cycle_state_lc" == "idle" || "$cycle_state_lc" == "idle "* ]]; then
    pass "Active Cycle idle (explicit Cycle state: Idle — spec checks skipped)"
  else
    warn "G3-idle" "no stories found in ## Active Cycle (idle is fine; verify skipped spec checks)" \
      "No active story means lifecycle gates for specs/tests are skipped." \
      "Enroll a story via /agtoosa-spec or set Project Charter Cycle state to Idle with a reason." guided
  fi
else
  for id in $active_ids; do
    spec=""
    for candidate in "$DOCS/archived/spec-${id}.md" "$DOCS/specs/spec-${id}.md"; do
      [[ -f "$candidate" ]] && spec="$candidate" && break
    done
    if [[ -z "$spec" ]]; then
      fail "G3-spec-missing-${id}" "$id: no spec file (expected $DOCS/archived/spec-${id}.md)" \
        "Build cannot proceed without an approved spec for the active story." \
        "Run /agtoosa-spec for $id (or remove it from Active Cycle)." enforced
      continue
    fi
    if grep -qE '^## ✅ Spec Approved|^## Spec Approved' "$spec"; then
      pass "$id: spec exists and is approved ($(basename "$spec"))"
    else
      fail "G3-spec-unapproved-${id}" "$id: spec found but missing '## ✅ Spec Approved' marker" \
        "Unapproved specs must not enter /agtoosa-build." \
        "Complete /agtoosa-spec approval for $id." enforced
    fi

    ac_rows=$(grep -cE '^\| *AC-[0-9]{3}' "$spec" 2>/dev/null || echo 0)
    if [[ $ac_rows -eq 0 ]]; then
      fail "G3-no-ac-${id}" "$id: no AC-NNN rows found in spec acceptance criteria" \
        "Without ACs there is no testable contract for the story." \
        "Add EARS acceptance criteria rows (AC-001…) to the spec." enforced
    else
      bad_ears=0
      while IFS= read -r row; do
        if ! echo "$row" | grep -qiE '(WHEN|WHILE|WHERE|IF|THE SYSTEM SHALL|SHALL)'; then
          bad_ears=$((bad_ears + 1))
        fi
      done < <(grep -E '^\| *AC-[0-9]{3}' "$spec")
      if [[ $bad_ears -gt 0 ]]; then
        warn "G3-ears-${id}" "$id: $bad_ears of $ac_rows AC rows lack EARS keywords (WHEN/WHILE/WHERE/IF/SHALL)" \
          "Weak AC wording reduces testability and review clarity." \
          "Rewrite AC rows using EARS patterns (WHEN… THE SYSTEM SHALL…)." guided
      else
        pass "$id: all $ac_rows AC rows use EARS patterns"
      fi
    fi

    if grep -qiE 'threat model|STRIDE' "$spec"; then
      pass "$id: threat model section present"
    else
      fail "G3-threat-${id}" "$id: no threat model / STRIDE section in spec" \
        "Security-by-design requires threat analysis before build." \
        "Add a STRIDE / threat model section to the $id spec." enforced
    fi

    if grep -qE '^## Spec Revision Log' "$spec"; then
      pass "$id: spec has a revision log"
    fi

    tp=""
    for candidate in "$DOCS/AgToosa_TestPlan-${id}.md" "$DOCS"/AgToosa_TestPlan-*"${id}"*.md; do
      [[ -f "$candidate" ]] && tp="$candidate" && break
    done
    if [[ -z "$tp" ]]; then
      fail "G3-no-tp-${id}" "$id: no test plan (expected $DOCS/AgToosa_TestPlan-${id}.md)" \
        "Stories without a test plan cannot prove AC coverage." \
        "Create Docs/AgToosa_TestPlan-${id}.md mapping each AC to named tests." enforced
    else
      unmapped=""
      while IFS= read -r ac; do
        grep -q "$ac" "$tp" || unmapped+="$ac "
      done < <(grep -oE 'AC-[0-9]{3}' "$spec" | sort -u)
      if [[ -n "$unmapped" ]]; then
        warn "G3-unmapped-${id}" "$id: ACs not referenced in test plan: $unmapped" \
          "Unmapped ACs may ship without coverage." \
          "Reference every AC-NNN in Docs/AgToosa_TestPlan-${id}.md." evidenced
      else
        pass "$id: every AC in the spec is referenced in the test plan"
      fi

      if grep -qiE 'RED evidence|RED run|exit[ _-]?code: *[1-9]' "$tp"; then
        pass "$id: test plan records RED (failing-run) evidence"
      else
        warn "G3-no-red-${id}" "$id: no RED failing-run evidence block in test plan (TDD gate)" \
          "Missing RED evidence weakens the TDD claim for this story." \
          "Capture a failing test run in the test plan RED Evidence section." evidenced
      fi
    fi

    if awk '/^## Active Tasks/,/^## [^A]/' "$MP" | grep -q "$id"; then
      pass "$id: task tree present in Master-Plan ## Active Tasks"
    else
      warn "G3-no-tasks-${id}" "$id: no task tree under ## Active Tasks for this story" \
        "Without a task tree, build progress is hard to track." \
        "Add an Active Tasks tree for $id in Master-Plan.md." guided
    fi
    if grep -qE '^### Wave Plan' "$spec"; then
      pass "$id: spec contains a Wave Plan"
    else
      warn "G3-no-wave-${id}" "$id: spec has no ### Wave Plan section" \
        "Missing wave plan reduces sequencing clarity for multi-task stories." \
        "Add ### Wave Plan to the $id spec." guided
    fi
  done
fi

# ── Gate 4: review artifacts for Done stories ─────────────────
gate "Gate 4 — Review artifacts"
done_ids=$(awk '/^## Active Cycle/,/^## [^A]/' "$MP" | grep -E '✅ Done|🏁 Shipped' | grep -oE 'DEV-[0-9]{3}' | sort -u)
for id in $done_ids; do
  if ls "$DOCS/archived/review-${id}"*.md >/dev/null 2>&1 || ls "$DOCS/archived/review-"*"${id}"*.md >/dev/null 2>&1; then
    pass "$id: review artifact archived"
  else
    warn "G4-no-review-${id}" "$id: marked Done but no archived review-${id}.md yet (run /agtoosa-review)" \
      "Done without review artifact skips the independent review gate." \
      "Run /agtoosa-review and archive review-${id}.md." evidenced
  fi
done

# ── Gate 5: generator version parity (maintainer repos only) ──
gate "Gate 5 — Version parity"
if [[ -f "$ROOT/agtoosa.sh" && -f "$ROOT/agtoosa.ps1" ]]; then
  bv=$(grep -m1 'AGTOOSA_VERSION=' "$ROOT/agtoosa.sh" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || true)
  pv=$(grep -m1 'AGTOOSA_VERSION' "$ROOT/agtoosa.ps1" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || true)
  if [[ -n "$bv" && "$bv" == "$pv" ]]; then
    pass "generator version parity (bash=$bv, ps1=$pv)"
    tech_stack=""
    for ts_candidate in "$ROOT/docs/Context/tech-stack.md" "$ROOT/Docs/Context/tech-stack.md"; do
      [[ -f "$ts_candidate" ]] && tech_stack="$ts_candidate" && break
    done
    if [[ -n "$tech_stack" ]] && grep -q '^deploy_command:' "$tech_stack"; then
      warn "G5-release-tag" "deploy_command is documented — verify the GitHub tag is published before claiming Release shipped" \
        "Docs-only version bumps without git tag push leave adopters on stale releases." \
        "Run: bash scripts/check-launch-readiness.sh --mode private (release-tag gate) and deploy_verify from tech-stack." guided
    fi
  else
    fail "G5-version-mismatch" "generator version mismatch (bash=$bv, ps1=$pv)" \
      "Mismatched generator versions break install/update consistency." \
      "Align AGTOOSA_VERSION in agtoosa.sh and agtoosa.ps1 (and packaging/npm/package.json)." enforced
  fi
elif [[ -f "$DOCS/.agtoosa-version" ]]; then
  pass "installed AgToosa version: $(cat "$DOCS/.agtoosa-version")"
else
  warn "G5-no-version" "no $DOCS/.agtoosa-version marker (install with agtoosa.sh to enable update checks)" \
    "Without a version marker, --doctor/--update cannot detect skew." \
    "Re-install or update with agtoosa.sh to write Docs/.agtoosa-version." guided
fi

# ── Gate 6: optional governance policy (DEV-059) ───────────────
gate "Gate 6 — Optional governance policy"
POLICY_CHECK=""
VERIFY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
for candidate in \
  "$DOCS/agtoosa-policy-check.sh" \
  "$VERIFY_DIR/agtoosa-policy-check.sh" \
  "$ROOT/docs/agtoosa-policy-check.sh" \
  "$ROOT/Docs/agtoosa-policy-check.sh" \
  "$ROOT/template/Docs/agtoosa-policy-check.sh"
do
  if [[ -f "$candidate" ]]; then
    POLICY_CHECK="$candidate"
    break
  fi
done
if [[ -z "$POLICY_CHECK" ]]; then
  pass "no policy checker installed (optional)"
else
  policy_rc=0
  policy_out=$(bash "$POLICY_CHECK" --root "$ROOT" 2>&1) || policy_rc=$?
  if echo "$policy_out" | grep -q 'policy_path=none'; then
    pass "no extra policy configured"
  elif [[ $policy_rc -eq 0 ]]; then
    pass "optional policy valid ($(echo "$policy_out" | grep -m1 'policy_path=' || true))"
  else
    warn "G6-bad-policy" "invalid optional policy (see agtoosa-policy-check.sh); missing policy is never a finding" \
      "An invalid present policy can mislead governance claims." \
      "Fix or remove the optional policy file; missing policy is OK." guided
  fi
fi

# ── Gate 7: optional evidence profile (DEV-089) ───────────────
gate "Gate 7 — Optional evidence profile"
EVIDENCE_YML="$ROOT/.agtoosa/evidence.yml"
if [[ ! -f "$EVIDENCE_YML" ]]; then
  pass "no evidence profile configured"
else
  # Never eval YAML command values; reject shell metacharacters (print rule id only).
  if grep -E '^[[:space:]]*command[[:space:]]*:' "$EVIDENCE_YML" 2>/dev/null \
    | grep -qE '[;&|$<>]|\$\(' || grep -E '^[[:space:]]*command[[:space:]]*:' "$EVIDENCE_YML" 2>/dev/null \
    | grep -qF '`'; then
    warn "G7-unsafe-command" "evidence.yml command field rejected (shell metacharacters); not executed" \
      "Crafted command fields must not run inside the verifier." \
      "Remove command: from evidence.yml or use an allowlisted local checker." enforced
  fi

  EVIDENCE_CHECK=""
  for candidate in \
    "$DOCS/agtoosa-evidence-profile-check.sh" \
    "$VERIFY_DIR/agtoosa-evidence-profile-check.sh" \
    "$ROOT/docs/agtoosa-evidence-profile-check.sh" \
    "$ROOT/Docs/agtoosa-evidence-profile-check.sh" \
    "$ROOT/template/Docs/agtoosa-evidence-profile-check.sh"
  do
    if [[ -f "$candidate" ]]; then
      EVIDENCE_CHECK="$candidate"
      break
    fi
  done

  epv_schema_ok=1
  if [[ -n "$EVIDENCE_CHECK" ]]; then
    epv_rc=0
    epv_out=$(bash "$EVIDENCE_CHECK" --root "$ROOT" 2>&1) || epv_rc=$?
    if [[ $epv_rc -ne 0 ]]; then
      epv_schema_ok=0
      warn "G7-bad-profile" "invalid evidence.yml (schema); see agtoosa-evidence-profile-check.sh" \
        "An invalid present profile can mislead delivery-assurance claims." \
        "Fix or remove .agtoosa/evidence.yml; missing profile is OK." guided
    fi
  fi

  if [[ $epv_schema_ok -eq 1 ]]; then
    # Resolve active profile + required tokens (stdlib python; no YAML lib).
    # Avoid $(python <<EOF) — parentheses in the heredoc body break bash parsing.
    epv_tmp="$(mktemp)"
    EVIDENCE_YML="$EVIDENCE_YML" python3 - >"$epv_tmp" 2>/dev/null <<'PY' || true
import os, re
path = os.environ["EVIDENCE_YML"]
text = open(path, encoding="utf-8").read()
active = None
for raw in text.splitlines():
    line = raw.split("#", 1)[0].rstrip()
    m = re.match(r"^active:\s*['\"]?([A-Za-z0-9_-]+)['\"]?\s*$", line)
    if m:
        active = m.group(1)
profiles = {}
cur = None
for raw in text.splitlines():
    line = raw.split("#", 1)[0].rstrip()
    if not line.strip():
        continue
    m = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
    if m and not line.startswith("    "):
        cur = m.group(1)
        profiles.setdefault(cur, [])
        continue
    if cur is None:
        continue
    m = re.match(r"^    required:\s*\[(.*)\]\s*$", line)
    if m:
        inner = m.group(1).strip()
        if inner:
            profiles[cur] = [p.strip().strip("'\"") for p in inner.split(",") if p.strip()]
        else:
            profiles[cur] = []
        continue
    m = re.match(r"^    -\s*['\"]?([A-Za-z0-9_-]+)['\"]?\s*$", line)
    if m:
        profiles.setdefault(cur, []).append(m.group(1))
if not active:
    print("ERR\tmissing-active")
elif active not in profiles:
    print("ERR\tunknown-active\t" + active)
else:
    print("OK\t" + active + "\t" + ",".join(profiles[active]))
PY
    epv_resolve="$(cat "$epv_tmp" 2>/dev/null || true)"
    rm -f "$epv_tmp"
    epv_status=${epv_resolve%%$'\t'*}
    if [[ "$epv_status" != "OK" ]]; then
      epv_detail=$(printf '%s' "$epv_resolve" | cut -f2- | tr '\t' ' ')
      warn "G7-bad-profile" "invalid evidence.yml (${epv_detail:-parse})" \
        "An invalid present profile can mislead delivery-assurance claims." \
        "Fix active/profiles in .agtoosa/evidence.yml; missing profile is OK." guided
    else
      epv_active=$(printf '%s' "$epv_resolve" | cut -f2)
      epv_tokens=$(printf '%s' "$epv_resolve" | cut -f3)
      pass "evidence profile active=${epv_active} (deterministic presence/exit-code checks only)"

      # Active / Done-boundary story ids (reuse Gate 3/4 scans).
      epv_active_ids=$(awk '/^## Active Cycle/,/^## [^A]/' "$MP" | grep -oE '^\| DEV-[0-9]{3}' | grep -oE 'DEV-[0-9]{3}' | sort -u)
      epv_done_ids=$(awk '/^## Active Cycle/,/^## [^A]/' "$MP" | grep -E '✅ Done|🏁 Shipped|🔍 In Review' | grep -oE 'DEV-[0-9]{3}' | sort -u)

      IFS=',' read -r -a epv_req <<< "$epv_tokens"
      for tok in "${epv_req[@]}"; do
        [[ -z "$tok" ]] && continue
        case "$tok" in
          spec|tests|review|threat-model)
            if [[ -z "$epv_active_ids" ]]; then
              pass "profile ${tok}: no active stories to check (guided/evidenced — presence only)"
              continue
            fi
            for id in $epv_active_ids; do
              case "$tok" in
                spec)
                  if [[ -f "$DOCS/archived/spec-${id}.md" || -f "$DOCS/specs/spec-${id}.md" ]]; then
                    pass "profile spec present for $id (evidenced)"
                  else
                    warn "G7-missing-spec" "required spec missing for $id (basename=spec-${id}.md)" \
                      "Profile requires spec artifact presence." \
                      "Add archived/spec-${id}.md or remove spec from the profile." evidenced
                  fi
                  ;;
                tests)
                  if ls "$DOCS"/AgToosa_TestPlan-"${id}"*.md >/dev/null 2>&1; then
                    pass "profile tests present for $id (evidenced)"
                  else
                    warn "G7-missing-tests" "required tests missing for $id (basename=AgToosa_TestPlan-${id}.md)" \
                      "Profile requires test-plan presence." \
                      "Add Docs/AgToosa_TestPlan-${id}.md." evidenced
                  fi
                  ;;
                review)
                  if ls "$DOCS/archived/review-${id}"*.md >/dev/null 2>&1; then
                    pass "profile review present for $id (evidenced)"
                  else
                    # Guided/evidenced — WARN only; never upgrade to enforced FAIL without wired command.
                    warn "G7-missing-review" "required review missing for $id (basename=review-${id}.md)" \
                      "Profile requires review artifact presence (evidenced, not enforced)." \
                      "Archive review-${id}.md or adjust the profile." evidenced
                  fi
                  ;;
                threat-model)
                  spec=""
                  for candidate in "$DOCS/archived/spec-${id}.md" "$DOCS/specs/spec-${id}.md"; do
                    [[ -f "$candidate" ]] && spec="$candidate" && break
                  done
                  if [[ -n "$spec" ]] && grep -qiE 'threat model|STRIDE' "$spec"; then
                    pass "profile threat-model present for $id (evidenced/guided — not enforced FAIL)"
                  else
                    tm_base="spec-${id}.md"
                    [[ -n "$spec" ]] && tm_base=$(basename "$spec")
                    warn "G7-missing-threat-model" "required threat-model missing for $id (basename=${tm_base})" \
                      "Guided/evidenced STRIDE presence only — not an enforced security control." \
                      "Add a STRIDE section or wire a local checker before claiming enforced." guided
                  fi
                  ;;
              esac
            done
            ;;
          sast|dependency-scan)
            # Presence / recorded exit-code only — never claim vulnerability absence.
            found=0
            base_pat="$tok"
            if compgen -G "$DOCS/archived/${base_pat}*" > /dev/null 2>&1 \
              || compgen -G "$DOCS/archived/*${base_pat}*" > /dev/null 2>&1; then
              found=1
            fi
            if [[ $found -eq 1 ]]; then
              pass "profile ${tok}: artifact present (presence/exit-code only; not a vulnerability-absence claim)"
            else
              warn "G7-missing-${tok}" "required ${tok} artifact missing (basename=${base_pat}.log); presence/exit-code only" \
                "Profile requires a local ${tok} log/report pointer — not a security guarantee." \
                "Add Docs/archived/${base_pat}-STORY.log with recorded exit code." evidenced
            fi
            ;;
          changelog)
            if [[ -f "$ROOT/CHANGELOG.md" || -f "$DOCS/AgToosa_Changelog.md" || -f "$DOCS/CHANGELOG.md" ]]; then
              pass "profile changelog present (evidenced)"
            else
              warn "G7-missing-changelog" "required changelog missing (basename=CHANGELOG.md)" \
                "Release profile expects a changelog artifact." \
                "Add CHANGELOG.md or Docs/AgToosa_Changelog.md." evidenced
            fi
            ;;
          rollback-note)
            if compgen -G "$DOCS/archived/*rollback*" > /dev/null 2>&1 \
              || compgen -G "$ROOT/*rollback*" > /dev/null 2>&1; then
              pass "profile rollback-note present (evidenced)"
            else
              warn "G7-missing-rollback-note" "required rollback-note missing (basename=rollback-note.md)" \
                "Release profile expects a rollback note artifact." \
                "Add an archived rollback note or adjust the profile." evidenced
            fi
            ;;
          *)
            warn "G7-unknown-token" "unknown required token ${tok} in profile ${epv_active}" \
              "Unrecognized tokens cannot be checked deterministically." \
              "Use contract tokens only (see AgToosa_Delivery_Evidence_Contract.md)." guided
            ;;
        esac
      done

      # Ledger WARN (DEV-049): profile requires review ⇒ Done-boundary stories need evidence-*.md
      if [[ ",$epv_tokens," == *",review,"* ]]; then
        for id in $epv_done_ids; do
          if ! compgen -G "$DOCS/archived/evidence-${id}*" > /dev/null 2>&1; then
            warn "G7-missing-ledger" "evidence ledger missing for $id (basename=evidence-${id}.md); DEV-049 agent-instructed" \
              "Profile expects review/ship ledger rows; missing ledger is WARN not FAIL (DEV-049)." \
              "Run /agtoosa-evidence or archive evidence-${id}.md; ledger remains agent-instructed." guided
          else
            pass "evidence ledger present for $id (DEV-049 WARN boundary satisfied)"
          fi
        done
      fi
    fi
  fi
fi

finish

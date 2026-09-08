#!/usr/bin/env bash
set -uo pipefail

# ──────────────────────────────────────────────────────────────
# AgToosa policy checker — deterministic, local, no network.
#
# Resolves and validates the constrained v1 governance policy
# schema documented in Docs/AgToosa_GovernancePolicy.md.
#
# Usage:
#   bash Docs/agtoosa-policy-check.sh [--root PATH] [--policy PATH]
#
# Exit codes:
#   0 = valid policy OR no optional policy configured
#   1 = policy present but invalid
#   2 = bad arguments / unreadable root
#
# Diagnostics name rule IDs and field names only; suspected
# secret values are never echoed (replaced with [REDACTED]).
# ──────────────────────────────────────────────────────────────

ROOT="$PWD"
POLICY_ARG=""
MAX_BYTES=65536

ALLOWED_CLASSES="generator-enforced|CI-enforced|agent-instructed|manual|roadmap"
ALLOWED_VIOLATIONS="warn|instruct_stop|block_generator"
ALLOWED_CATEGORIES="paths|tools|network|secrets|approvals|risky_actions"
FORBIDDEN_FIELDS="value|token|password|secret|api_key|apikey|private_key|credential|passwd|access_key"

usage() {
  sed -n '4,22p' "$0"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      [[ $# -lt 2 ]] && { echo "Error: --root requires a directory" >&2; exit 2; }
      ROOT="$2"; shift ;;
    --policy)
      [[ $# -lt 2 ]] && { echo "Error: --policy requires a file path" >&2; exit 2; }
      POLICY_ARG="$2"; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Error: unknown argument '$1'" >&2
      exit 2 ;;
  esac
  shift
done

[[ -d "$ROOT" ]] || { echo "Error: root '$ROOT' is not a directory" >&2; exit 2; }

# Detect docs dir for Context fallback (Docs/ generated, docs/ maintainer).
DOCS=""
if [[ -f "$ROOT/Docs/Master-Plan.md" ]]; then
  DOCS="$ROOT/Docs"
  DOCS_REL="Docs"
elif [[ -f "$ROOT/docs/Master-Plan.md" ]]; then
  DOCS="$ROOT/docs"
  DOCS_REL="docs"
fi

resolve_policy() {
  if [[ -n "$POLICY_ARG" ]]; then
    if [[ ! -f "$POLICY_ARG" ]]; then
      echo "Error: --policy file not found: $POLICY_ARG" >&2
      exit 2
    fi
    POLICY_FILE="$POLICY_ARG"
    # Prefer repo-relative path when under ROOT.
    case "$POLICY_FILE" in
      "$ROOT"/*) POLICY_PATH="${POLICY_FILE#"$ROOT"/}" ;;
      /*) POLICY_PATH="$POLICY_FILE" ;;
      *) POLICY_PATH="$POLICY_FILE" ;;
    esac
    return 0
  fi

  if [[ -f "$ROOT/.agtoosa/policy.yaml" ]]; then
    POLICY_FILE="$ROOT/.agtoosa/policy.yaml"
    POLICY_PATH=".agtoosa/policy.yaml"
    return 0
  fi

  if [[ -n "$DOCS" && -f "$DOCS/Context/agtoosa-policy.yaml" ]]; then
    POLICY_FILE="$DOCS/Context/agtoosa-policy.yaml"
    POLICY_PATH="${DOCS_REL}/Context/agtoosa-policy.yaml"
    return 0
  fi

  # .example.yaml is never active automatically.
  POLICY_FILE=""
  POLICY_PATH="none"
  return 1
}

emit_err() {
  echo "Error: $1" >&2
}

# Redact any occurrence of known fixture/secret-like literals from a diagnostic line.
redact_line() {
  local line="$1"
  # Never print assignment values for forbidden fields; strip after colon.
  if echo "$line" | grep -qiE "(${FORBIDDEN_FIELDS})[[:space:]]*:"; then
    echo "$line" | sed -E "s/((${FORBIDDEN_FIELDS})[[:space:]]*:)[[:space:]]*.*/\\1 [REDACTED]/Ig"
    return
  fi
  echo "$line"
}

validate_policy_file() {
  local file="$1"
  local size
  size=$(wc -c < "$file" | tr -d ' ')
  if [[ "$size" -gt "$MAX_BYTES" ]]; then
    emit_err "policy too large (${size} bytes; limit ${MAX_BYTES})"
    return 1
  fi

  local errors=0
  local -a seen_ids=()
  local current_category=""
  local current_id=""
  local have_desc=0 have_class=0 have_viol=0
  local line raw key val
  local lineno=0

  flush_rule() {
    if [[ -z "$current_id" ]]; then
      return 0
    fi
    if [[ -z "$current_id" || "$current_id" == "" ]]; then
      emit_err "rule has empty id in category '$current_category'"
      errors=$((errors + 1))
    fi
    if [[ $have_desc -eq 0 ]]; then
      emit_err "rule '$current_id' missing required field 'description'"
      errors=$((errors + 1))
    fi
    if [[ $have_class -eq 0 ]]; then
      emit_err "rule '$current_id' missing required field 'enforcement_class'"
      errors=$((errors + 1))
    fi
    if [[ $have_viol -eq 0 ]]; then
      emit_err "rule '$current_id' missing required field 'on_violation'"
      errors=$((errors + 1))
    fi
    local sid
    for sid in "${seen_ids[@]+"${seen_ids[@]}"}"; do
      if [[ "$sid" == "$current_id" ]]; then
        emit_err "duplicate rule id '$current_id'"
        errors=$((errors + 1))
        break
      fi
    done
    seen_ids+=("$current_id")
    current_id=""
    have_desc=0
    have_class=0
    have_viol=0
  }

  while IFS= read -r raw || [[ -n "$raw" ]]; do
    lineno=$((lineno + 1))
    # Strip comments and trailing whitespace.
    line="${raw%%#*}"
    line="${line%"${line##*[![:space:]]}"}"
    [[ -z "$line" ]] && continue

    # Top-level key (category or version)
    if [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_]*):[[:space:]]*(.*)$ ]]; then
      key="${BASH_REMATCH[1]}"
      val="${BASH_REMATCH[2]}"
      if [[ "$key" == "version" ]]; then
        flush_rule
        current_category=""
        continue
      fi
      if echo "$key" | grep -qE "^(${ALLOWED_CATEGORIES})$"; then
        flush_rule
        current_category="$key"
        continue
      fi
      # Unknown top-level category (not a nested field)
      if [[ -z "$current_category" || "$line" =~ ^[A-Za-z_] ]]; then
        if ! echo "$key" | grep -qE "^(${ALLOWED_CATEGORIES}|version)$"; then
          emit_err "unsupported category or top-level key '$key'"
          errors=$((errors + 1))
          current_category=""
          continue
        fi
      fi
    fi

    # New rule: "  - id: FOO"
    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]+id:[[:space:]]*(.*)$ ]]; then
      flush_rule
      current_id="${BASH_REMATCH[1]}"
      current_id="${current_id#"${current_id%%[![:space:]]*}"}"
      current_id="${current_id%"${current_id##*[![:space:]]}"}"
      current_id="${current_id%\"}"
      current_id="${current_id#\"}"
      current_id="${current_id%\'}"
      current_id="${current_id#\'}"
      if [[ -z "$current_category" ]]; then
        emit_err "rule id '$current_id' appears outside a known category"
        errors=$((errors + 1))
      fi
      if [[ -z "$current_id" ]]; then
        emit_err "empty rule id"
        errors=$((errors + 1))
      fi
      continue
    fi

    # Rule field: "    key: value"
    if [[ "$line" =~ ^[[:space:]]+([A-Za-z_][A-Za-z0-9_]*):[[:space:]]*(.*)$ ]]; then
      key="${BASH_REMATCH[1]}"
      val="${BASH_REMATCH[2]}"
      val="${val%"${val##*[![:space:]]}"}"

      if echo "$key" | grep -qiE "^(${FORBIDDEN_FIELDS})$"; then
        # Name rule + field only; never echo the value.
        if [[ -n "$current_id" ]]; then
          emit_err "rule '$current_id' forbids secret-value field '$key'"
        else
          emit_err "forbids secret-value field '$key'"
        fi
        errors=$((errors + 1))
        continue
      fi

      # Likely credential literal in any string field (common token prefixes).
      if echo "$val" | grep -qE '\b(sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,})\b'; then
        if [[ -n "$current_id" ]]; then
          emit_err "rule '$current_id' field '$key' contains a likely credential literal [REDACTED]"
        else
          emit_err "field '$key' contains a likely credential literal [REDACTED]"
        fi
        errors=$((errors + 1))
        continue
      fi

      case "$key" in
        description)
          if [[ -z "$val" ]]; then
            emit_err "rule '${current_id:-?}' has empty description"
            errors=$((errors + 1))
          else
            have_desc=1
          fi
          ;;
        enforcement_class)
          if ! echo "$val" | grep -qE "^(${ALLOWED_CLASSES})$"; then
            emit_err "rule '${current_id:-?}' has invalid enforcement_class"
            errors=$((errors + 1))
          else
            have_class=1
          fi
          ;;
        on_violation)
          if ! echo "$val" | grep -qE "^(${ALLOWED_VIOLATIONS})$"; then
            emit_err "rule '${current_id:-?}' has invalid on_violation"
            errors=$((errors + 1))
          else
            have_viol=1
            if [[ "$val" == "block_generator" ]]; then
              : # generator_operation checked at flush via a flag
              _needs_gen_op=1
            fi
          fi
          ;;
        generator_operation)
          _has_gen_op=1
          if [[ -z "$val" ]]; then
            emit_err "rule '${current_id:-?}' has empty generator_operation"
            errors=$((errors + 1))
          fi
          ;;
        id)
          ;;
        names|allow|deny|notes)
          # Optional metadata lists / notes — allowed, values must not look like secrets (checked above).
          ;;
        *)
          # Unknown nested keys are allowed as opaque metadata except forbidden secret fields.
          ;;
      esac
      continue
    fi

    # List item under a field (e.g. names:) — ignore content for schema; still scan for credential shapes.
    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]+(.*)$ ]]; then
      val="${BASH_REMATCH[1]}"
      if echo "$val" | grep -qE '\b(sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})\b'; then
        emit_err "rule '${current_id:-?}' list entry contains a likely credential literal [REDACTED]"
        errors=$((errors + 1))
      fi
    fi
  done < "$file"

  # Final rule flush with block_generator / generator_operation check.
  if [[ -n "$current_id" ]]; then
    if [[ "${_needs_gen_op:-0}" -eq 1 && "${_has_gen_op:-0}" -ne 1 ]]; then
      emit_err "rule '$current_id' uses block_generator without generator_operation"
      errors=$((errors + 1))
    fi
    flush_rule
  fi

  # Re-scan file for block_generator rules missing generator_operation (multi-rule files).
  # Simpler second pass with awk-free state machine:
  local id="" viol="" gop=""
  while IFS= read -r raw || [[ -n "$raw" ]]; do
    line="${raw%%#*}"
    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]+id:[[:space:]]*(.*)$ ]]; then
      if [[ -n "$id" && "$viol" == "block_generator" && -z "$gop" ]]; then
        emit_err "rule '$id' uses block_generator without generator_operation"
        errors=$((errors + 1))
      fi
      id="${BASH_REMATCH[1]}"
      id="${id%"${id##*[![:space:]]}"}"
      viol=""
      gop=""
    elif [[ "$line" =~ on_violation:[[:space:]]*(.*)$ ]]; then
      viol="${BASH_REMATCH[1]}"
      viol="${viol%"${viol##*[![:space:]]}"}"
    elif [[ "$line" =~ generator_operation:[[:space:]]*(.*)$ ]]; then
      gop="${BASH_REMATCH[1]}"
      gop="${gop%"${gop##*[![:space:]]}"}"
    fi
  done < "$file"
  if [[ -n "$id" && "$viol" == "block_generator" && -z "$gop" ]]; then
    emit_err "rule '$id' uses block_generator without generator_operation"
    errors=$((errors + 1))
  fi

  [[ $errors -eq 0 ]]
}

# ── main ──────────────────────────────────────────────────────
POLICY_FILE=""
POLICY_PATH="none"

if resolve_policy; then
  echo "policy_path=$POLICY_PATH"
  if validate_policy_file "$POLICY_FILE"; then
    echo "policy: valid"
    exit 0
  else
    echo "policy: invalid"
    exit 1
  fi
else
  echo "policy_path=none"
  echo "no extra policy configured"
  exit 0
fi

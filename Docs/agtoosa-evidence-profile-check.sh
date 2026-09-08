#!/usr/bin/env bash
set -uo pipefail

# ──────────────────────────────────────────────────────────────
# AgToosa evidence profile checker — schema-only, local, no network.
#
# Validates .agtoosa/evidence.yml structure against the vocabulary
# in Docs/AgToosa_Delivery_Evidence_Contract.md.
#
# This is schema-only: it does NOT check artifact existence on disk
# and does NOT claim full delivery compliance (Gate 7 = DEV-089).
#
# Usage:
#   bash Docs/agtoosa-evidence-profile-check.sh [--root PATH]
#
# Exit codes:
#   0 = valid schema OR no optional evidence.yml configured
#   1 = evidence.yml present but schema-invalid
#   2 = bad arguments / unreadable root
# ──────────────────────────────────────────────────────────────

ROOT="$PWD"
MAX_BYTES=65536

KNOWN_PROFILES="standard|security-sensitive|release"
ALLOWED_TOP="version|active|profiles"
ALLOWED_ARTIFACTS="spec|tests|review|threat-model|sast|dependency-scan|changelog|rollback-note"
FORBIDDEN_FIELDS="value|token|password|secret|api_key|apikey|private_key|credential|passwd|access_key"

usage() {
  sed -n '4,22p' "$0"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      [[ $# -lt 2 ]] && { echo "Error: --root requires a directory" >&2; exit 2; }
      ROOT="$2"; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Error: unknown argument '$1'" >&2
      exit 2 ;;
  esac
  shift
done

[[ -d "$ROOT" ]] || { echo "Error: root '$ROOT' is not a directory" >&2; exit 2; }

EVIDENCE_FILE=""
EVIDENCE_PATH="none"
if [[ -f "$ROOT/.agtoosa/evidence.yml" ]]; then
  EVIDENCE_FILE="$ROOT/.agtoosa/evidence.yml"
  EVIDENCE_PATH=".agtoosa/evidence.yml"
fi

emit_err() {
  echo "Error: $1" >&2
}

# Prefer python3 (stdlib only — no PyYAML). Fall back to bash line scan.
validate_with_python() {
  local file="$1"
  python3 - "$file" <<'PY'
import re, sys

path = sys.argv[1]
KNOWN = {"standard", "security-sensitive", "release"}
ALLOWED_TOP = {"version", "active", "profiles"}
ALLOWED_ARTIFACTS = {
    "spec", "tests", "review", "threat-model", "sast",
    "dependency-scan", "changelog", "rollback-note",
}
FORBIDDEN = {
    "value", "token", "password", "secret", "api_key", "apikey",
    "private_key", "credential", "passwd", "access_key",
}

def strip_comment(line: str) -> str:
    out, in_sq, in_dq = [], False, False
    for c in line:
        if c == "'" and not in_dq:
            in_sq = not in_sq
            out.append(c)
        elif c == '"' and not in_sq:
            in_dq = not in_dq
            out.append(c)
        elif c == "#" and not in_sq and not in_dq:
            break
        else:
            out.append(c)
    return "".join(out).rstrip()

def unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    return s

def split_flow(s: str):
    s = s.strip()
    if not (s.startswith("[") and s.endswith("]")):
        return None
    inner = s[1:-1].strip()
    if not inner:
        return []
    return [unquote(p) for p in inner.split(",") if p.strip()]

try:
    data = open(path, "r", encoding="utf-8").read()
except OSError as e:
    print(f"Error: cannot read file: {e}", file=sys.stderr)
    sys.exit(1)

if len(data.encode("utf-8")) > 65536:
    print(
        f"Error: evidence.yml too large ({len(data.encode('utf-8'))} bytes; limit 65536)",
        file=sys.stderr,
    )
    sys.exit(1)

errors = []
have_profiles = False
in_profiles = False
current_profile = None
expect_items = False
seen_profiles = set()
profile_indent = None
contentful = False

for lineno, raw in enumerate(data.splitlines(), 1):
    line = strip_comment(raw)
    if not line.strip() or line.strip() in ("---", "..."):
        continue

    # Indentation via leading spaces (tabs rejected)
    if "\t" in line[: len(line) - len(line.lstrip())]:
        errors.append(f"line {lineno}: tabs not allowed in indentation")
        continue

    indent = len(line) - len(line.lstrip(" "))
    body = line.lstrip(" ")

    # List item under required:
    if body.startswith("- "):
        if not expect_items or current_profile is None:
            errors.append(f"line {lineno}: list item outside a required: block")
            continue
        tok = unquote(body[2:].strip())
        if tok.lower() in FORBIDDEN:
            errors.append(f"line {lineno}: forbidden secret-like key '{tok}'")
            continue
        if tok not in ALLOWED_ARTIFACTS:
            errors.append(
                f"line {lineno}: unknown artifact token '{tok}' under profile '{current_profile}'"
            )
        continue

    if ":" not in body:
        errors.append(f"line {lineno}: unparsable line (schema-only checker)")
        continue

    key, _, rest = body.partition(":")
    key = unquote(key.strip())
    val = rest.strip()

    if key.lower() in FORBIDDEN:
        errors.append(f"line {lineno}: forbidden secret-like key '{key}'")
        continue

    # Top-level (indent 0)
    if indent == 0:
        expect_items = False
        current_profile = None
        profile_indent = None
        if key == "profiles":
            have_profiles = True
            in_profiles = True
            contentful = True
            continue
        in_profiles = False
        if key not in ALLOWED_TOP:
            errors.append(f"line {lineno}: unknown top-level key '{key}'")
            continue
        if key == "active" and val:
            active = unquote(val)
            if active not in KNOWN:
                errors.append(f"line {lineno}: unknown active profile '{active}'")
        # version/active alone are not "contentful" for requiring profiles
        continue

    contentful = True

    if not in_profiles:
        errors.append(f"line {lineno}: unexpected indented key '{key}' outside profiles")
        continue

    # Profile header: known name, empty value, shallower/equal than nested fields
    if key in KNOWN and not val:
        current_profile = key
        seen_profiles.add(key)
        profile_indent = indent
        expect_items = False
        continue

    if key not in KNOWN and (profile_indent is None or indent <= profile_indent):
        # Unknown profile name at profile level
        if not val:
            errors.append(f"line {lineno}: unknown profile key '{key}'")
            current_profile = None
            expect_items = False
            continue

    if current_profile is None:
        errors.append(f"line {lineno}: key '{key}' appears outside a known profile")
        continue

    if key == "required":
        flow = split_flow(val) if val else None
        if flow is not None:
            expect_items = False
            if len(flow) == 0:
                errors.append(f"line {lineno}: profile '{current_profile}' has empty required list")
            for tok in flow:
                if tok not in ALLOWED_ARTIFACTS:
                    errors.append(
                        f"line {lineno}: unknown artifact token '{tok}' under profile '{current_profile}'"
                    )
        elif not val:
            expect_items = True
        else:
            errors.append(
                f"line {lineno}: profile '{current_profile}' field 'required' must be a list"
            )
        continue

    errors.append(
        f"line {lineno}: unknown key '{key}' under profile '{current_profile}' (allowed: required)"
    )

# Any present evidence.yml must declare profiles (optional file, required key).
if not have_profiles:
    errors.append("missing required root key 'profiles'")
if have_profiles and not seen_profiles:
    errors.append("profiles key present but no known profile blocks found")

if errors:
    for e in errors:
        print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
sys.exit(0)
PY
}

validate_with_bash() {
  local file="$1"
  local size errors=0
  size=$(wc -c < "$file" | tr -d ' ')
  if [[ "$size" -gt "$MAX_BYTES" ]]; then
    emit_err "evidence.yml too large (${size} bytes; limit ${MAX_BYTES})"
    return 1
  fi

  local line raw key val
  local have_profiles=0 in_profiles=0 seen_any_profile=0 expect_items=0 contentful=0
  local current_profile="" lineno=0

  while IFS= read -r raw || [[ -n "$raw" ]]; do
    lineno=$((lineno + 1))
    line="${raw%%#*}"
    line="${line%"${line##*[![:space:]]}"}"
    [[ -z "$line" || "$line" == "---" || "$line" == "..." ]] && continue

    if echo "$line" | grep -qiE "^[[:space:]]*-?[[:space:]]*(${FORBIDDEN_FIELDS})[[:space:]]*:"; then
      local fk
      fk=$(echo "$line" | sed -E 's/^[[:space:]]*-?[[:space:]]*//;s/:.*//;s/[[:space:]]*$//')
      emit_err "line ${lineno}: forbidden secret-like key '$fk'"
      errors=$((errors + 1))
      continue
    fi

    if [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_-]*):[[:space:]]*(.*)$ ]]; then
      key="${BASH_REMATCH[1]}"; val="${BASH_REMATCH[2]}"
      expect_items=0; current_profile=""
      if [[ "$key" == "profiles" ]]; then
        have_profiles=1; in_profiles=1; contentful=1; continue
      fi
      in_profiles=0
      if ! echo "$key" | grep -qE "^(${ALLOWED_TOP})$"; then
        emit_err "line ${lineno}: unknown top-level key '$key'"
        errors=$((errors + 1))
      fi
      if [[ "$key" == "active" && -n "$val" ]]; then
        val="${val%\"}"; val="${val#\"}"
        if ! echo "$val" | grep -qE "^(${KNOWN_PROFILES})$"; then
          emit_err "line ${lineno}: unknown active profile '$val'"
          errors=$((errors + 1))
        fi
      fi
      continue
    fi

    if [[ "$line" =~ ^[[:space:]]+([A-Za-z_][A-Za-z0-9_-]*):[[:space:]]*(.*)$ ]]; then
      key="${BASH_REMATCH[1]}"; val="${BASH_REMATCH[2]}"
      contentful=1
      if [[ "$in_profiles" -eq 1 ]] && echo "$key" | grep -qE "^(${KNOWN_PROFILES})$" && [[ -z "$val" ]]; then
        current_profile="$key"; seen_any_profile=1; expect_items=0; continue
      fi
      if [[ -n "$current_profile" && "$key" == "required" ]]; then
        if [[ "$val" =~ ^\[(.*)\]$ ]]; then
          local inner="${BASH_REMATCH[1]}"
          expect_items=0
          if [[ -z "${inner// /}" ]]; then
            emit_err "line ${lineno}: profile '$current_profile' has empty required list"
            errors=$((errors + 1))
          else
            local tok
            IFS=',' read -ra _toks <<< "$inner"
            for tok in "${_toks[@]}"; do
              tok="${tok#"${tok%%[![:space:]]*}"}"
              tok="${tok%"${tok##*[![:space:]]}"}"
              tok="${tok%\"}"; tok="${tok#\"}"
              [[ -z "$tok" ]] && continue
              if ! echo "$tok" | grep -qE "^(${ALLOWED_ARTIFACTS})$"; then
                emit_err "line ${lineno}: unknown artifact token '$tok' under profile '$current_profile'"
                errors=$((errors + 1))
              fi
            done
          fi
        elif [[ -z "$val" ]]; then
          expect_items=1
        else
          emit_err "line ${lineno}: profile '$current_profile' field 'required' must be a list"
          errors=$((errors + 1))
        fi
        continue
      fi
      if [[ "$in_profiles" -eq 1 ]]; then
        if [[ -z "$val" ]] && ! echo "$key" | grep -qE "^(${KNOWN_PROFILES})$"; then
          emit_err "line ${lineno}: unknown profile key '$key'"
          errors=$((errors + 1))
          current_profile=""
          continue
        fi
        if [[ -n "$current_profile" && "$key" != "required" ]]; then
          emit_err "line ${lineno}: unknown key '$key' under profile '$current_profile' (allowed: required)"
          errors=$((errors + 1))
        fi
      fi
      continue
    fi

    if [[ "$expect_items" -eq 1 && "$line" =~ ^[[:space:]]+-[[:space:]]+(.*)$ ]]; then
      local tok="${BASH_REMATCH[1]}"
      tok="${tok%\"}"; tok="${tok#\"}"
      if ! echo "$tok" | grep -qE "^(${ALLOWED_ARTIFACTS})$"; then
        emit_err "line ${lineno}: unknown artifact token '$tok' under profile '$current_profile'"
        errors=$((errors + 1))
      fi
    fi
  done < "$file"

  if [[ "$have_profiles" -eq 0 ]]; then
    emit_err "missing required root key 'profiles'"
    errors=$((errors + 1))
  fi
  if [[ "$have_profiles" -eq 1 && "$seen_any_profile" -eq 0 ]]; then
    emit_err "profiles key present but no known profile blocks found"
    errors=$((errors + 1))
  fi
  [[ "$errors" -eq 0 ]]
}

if [[ -z "$EVIDENCE_FILE" ]]; then
  echo "agtoosa-evidence-profile-check: schema-only"
  echo "evidence_path=none"
  echo "result=ok (no optional .agtoosa/evidence.yml configured)"
  exit 0
fi

size=$(wc -c < "$EVIDENCE_FILE" | tr -d ' ')
if [[ "$size" -gt "$MAX_BYTES" ]]; then
  emit_err "evidence.yml too large (${size} bytes; limit ${MAX_BYTES})"
  echo "agtoosa-evidence-profile-check: schema-only"
  echo "evidence_path=${EVIDENCE_PATH}"
  echo "result=invalid"
  exit 1
fi

ok=0
if command -v python3 >/dev/null 2>&1; then
  if validate_with_python "$EVIDENCE_FILE"; then
    ok=1
  fi
else
  if validate_with_bash "$EVIDENCE_FILE"; then
    ok=1
  fi
fi

echo "agtoosa-evidence-profile-check: schema-only"
echo "evidence_path=${EVIDENCE_PATH}"
if [[ "$ok" -eq 1 ]]; then
  echo "result=ok (schema valid; not full delivery compliance)"
  exit 0
fi
echo "result=invalid"
exit 1

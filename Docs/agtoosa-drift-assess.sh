#!/usr/bin/env bash
set -uo pipefail

# ──────────────────────────────────────────────────────────────
# AgToosa drift assessor — local, network-free (DEV-122).
#
# Compares a frozen allowlist baseline against files at a repo
# root and emits a drift report with impact levels and suggested
# rigor. Default mode is suggest-only (exit 0).
#
# Usage:
#   bash Docs/agtoosa-drift-assess.sh --baseline PATH --root PATH
#       [--output PATH] [--measurement PATH] [--strict]
#
# Exit codes:
#   0 = report emitted (default) or no high-impact drift
#   1 = validation failure or --strict high-impact drift
#   2 = usage / setup error
# ──────────────────────────────────────────────────────────────

ROOT=""
BASELINE=""
OUTPUT=""
MEASUREMENT=""
STRICT=false

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=../lib/drift.sh
source "$REPO_ROOT/lib/drift.sh"
# shellcheck source=../lib/drift-providers/git-inventory.sh
source "$REPO_ROOT/lib/drift-providers/git-inventory.sh"

usage() {
  sed -n '4,18p' "$0"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      [[ $# -lt 2 ]] && { echo "Error: --root requires a directory" >&2; exit 2; }
      ROOT="$2"; shift ;;
    --baseline)
      [[ $# -lt 2 ]] && { echo "Error: --baseline requires a path" >&2; exit 2; }
      BASELINE="$2"; shift ;;
    --output)
      [[ $# -lt 2 ]] && { echo "Error: --output requires a path" >&2; exit 2; }
      OUTPUT="$2"; shift ;;
    --measurement)
      [[ $# -lt 2 ]] && { echo "Error: --measurement requires a path" >&2; exit 2; }
      MEASUREMENT="$2"; shift ;;
    --strict) STRICT=true ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Error: unknown argument '$1'" >&2; exit 2 ;;
  esac
  shift
done

[[ -n "$ROOT" ]] || { echo "Error: --root is required" >&2; exit 2; }
[[ -n "$BASELINE" ]] || { echo "Error: --baseline is required" >&2; exit 2; }
[[ -d "$ROOT" ]] || { echo "Error: root '$ROOT' is not a directory" >&2; exit 2; }
[[ -f "$BASELINE" ]] || { echo "Error: baseline '$BASELINE' not found" >&2; exit 2; }

drift_validate_baseline "$REPO_ROOT" "$BASELINE" || exit 2

tmp_report="$(mktemp)"
trap 'rm -f "$tmp_report"' EXIT

set +e
drift_git_inventory_assess "$ROOT" "$BASELINE" "$STRICT" "$MEASUREMENT" "$REPO_ROOT" >"$tmp_report"
assess_status=$?
set -e

drift_validate_report "$tmp_report" || exit 1

if [[ -n "$OUTPUT" ]]; then
  cp "$tmp_report" "$OUTPUT"
else
  cat "$tmp_report"
fi

exit "$assess_status"

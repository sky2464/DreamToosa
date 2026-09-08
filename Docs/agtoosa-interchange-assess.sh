#!/usr/bin/env bash
set -uo pipefail

# ──────────────────────────────────────────────────────────────
# AgToosa interchange loss assessor — local, network-free (DEV-124).
#
# Validates a loss report and evaluates severity. Default mode is
# suggest-only (exit 0 unless schema/authority failures). With
# --strict, high-severity loss items also fail the check.
#
# Usage:
#   bash Docs/agtoosa-interchange-assess.sh --loss-report PATH
#       [--strict]
#
# Exit codes:
#   0 = report valid; no authority violations (and no high loss unless --strict)
#   1 = validation failure, authority violation, or --strict high-severity loss
#   2 = usage / setup error
# ──────────────────────────────────────────────────────────────

LOSS_REPORT=""
STRICT=false

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=../lib/interchange.sh
source "$REPO_ROOT/lib/interchange.sh"

usage() {
  sed -n '4,18p' "$0"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --loss-report)
      [[ $# -lt 2 ]] && { echo "Error: --loss-report requires a path" >&2; exit 2; }
      LOSS_REPORT="$2"; shift ;;
    --strict) STRICT=true ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Error: unknown argument '$1'" >&2; exit 2 ;;
  esac
  shift
done

[[ -n "$LOSS_REPORT" ]] || { echo "Error: --loss-report is required" >&2; exit 2; }
[[ -f "$LOSS_REPORT" ]] || { echo "Error: loss report '$LOSS_REPORT' not found" >&2; exit 2; }

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 required for interchange assess" >&2
  exit 2
fi

interchange_validate_loss_report "$LOSS_REPORT" || exit 1

set +e
interchange_assess_loss_report "$LOSS_REPORT" "$STRICT"
assess_status=$?
set -e

exit "$assess_status"

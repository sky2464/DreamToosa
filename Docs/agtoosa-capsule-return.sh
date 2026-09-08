#!/usr/bin/env bash
set -uo pipefail

# ──────────────────────────────────────────────────────────────
# AgToosa capsule return validator — local, network-free (DEV-123).
#
# Validates a capsule-return-v1 envelope against the parent
# capsule scope, budgets, policy, and return contract.
#
# Usage:
#   bash Docs/agtoosa-capsule-return.sh --capsule PATH --return PATH
#
# Exit codes:
#   0 = return envelope valid
#   1 = validation failure
#   2 = usage / setup error
# ──────────────────────────────────────────────────────────────

CAPSULE=""
RETURN=""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=../lib/capsule.sh
source "$REPO_ROOT/lib/capsule.sh"

usage() {
  sed -n '4,17p' "$0"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --capsule)
      [[ $# -lt 2 ]] && { echo "Error: --capsule requires a path" >&2; exit 2; }
      CAPSULE="$2"; shift ;;
    --return)
      [[ $# -lt 2 ]] && { echo "Error: --return requires a path" >&2; exit 2; }
      RETURN="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Error: unknown argument '$1'" >&2; exit 2 ;;
  esac
  shift
done

[[ -n "$CAPSULE" ]] || { echo "Error: --capsule is required" >&2; exit 2; }
[[ -n "$RETURN" ]] || { echo "Error: --return is required" >&2; exit 2; }
[[ -f "$CAPSULE" ]] || { echo "Error: capsule '$CAPSULE' not found" >&2; exit 2; }
[[ -f "$RETURN" ]] || { echo "Error: return '$RETURN' not found" >&2; exit 2; }

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 required for return validation" >&2
  exit 2
fi

capsule_validate_capsule "$REPO_ROOT" "$CAPSULE" || exit 1
capsule_validate_return "$CAPSULE" "$RETURN" || exit 1

echo "Return valid: $RETURN"
exit 0

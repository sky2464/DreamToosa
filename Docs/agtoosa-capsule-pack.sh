#!/usr/bin/env bash
set -uo pipefail

# ──────────────────────────────────────────────────────────────
# AgToosa capsule packer — local, network-free (DEV-123).
#
# Packs an execution capsule from a story id and optional handoff
# markdown path via the manual-handoff exporter.
#
# Usage:
#   bash Docs/agtoosa-capsule-pack.sh --story STORY_ID
#       [--handoff PATH] --output PATH
#
# Exit codes:
#   0 = capsule emitted and validated
#   1 = validation failure
#   2 = usage / setup error
# ──────────────────────────────────────────────────────────────

STORY=""
HANDOFF=""
OUTPUT=""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=../lib/capsule.sh
source "$REPO_ROOT/lib/capsule.sh"
# shellcheck source=../lib/capsule-exporters/manual-handoff.sh
source "$REPO_ROOT/lib/capsule-exporters/manual-handoff.sh"

usage() {
  sed -n '4,17p' "$0"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --story)
      [[ $# -lt 2 ]] && { echo "Error: --story requires an id" >&2; exit 2; }
      STORY="$2"; shift ;;
    --handoff)
      [[ $# -lt 2 ]] && { echo "Error: --handoff requires a path" >&2; exit 2; }
      HANDOFF="$2"; shift ;;
    --output)
      [[ $# -lt 2 ]] && { echo "Error: --output requires a path" >&2; exit 2; }
      OUTPUT="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Error: unknown argument '$1'" >&2; exit 2 ;;
  esac
  shift
done

[[ -n "$STORY" ]] || { echo "Error: --story is required" >&2; exit 2; }
[[ "$STORY" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "Error: invalid story id" >&2; exit 2; }
[[ -n "$OUTPUT" ]] || { echo "Error: --output is required" >&2; exit 2; }

if [[ -n "$HANDOFF" && ! -f "$HANDOFF" ]]; then
  echo "Error: handoff '$HANDOFF' not found" >&2
  exit 2
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 required for capsule packing" >&2
  exit 2
fi

PACK_SOURCE="${HANDOFF:-$STORY}"

tmp_out="$(mktemp)"
trap 'rm -f "$tmp_out"' EXIT

set +e
capsule_pack_from_handoff "$REPO_ROOT" "$PACK_SOURCE" "$tmp_out"
pack_status=$?
set -e

[[ "$pack_status" -eq 0 ]] || exit "$pack_status"

capsule_validate_capsule "$REPO_ROOT" "$tmp_out" || exit 1

mkdir -p "$(dirname "$OUTPUT")"
cp "$tmp_out" "$OUTPUT"
cat "$OUTPUT"
exit 0

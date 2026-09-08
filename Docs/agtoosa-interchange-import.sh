#!/usr/bin/env bash
set -uo pipefail

# ──────────────────────────────────────────────────────────────
# AgToosa interchange importer — local, network-free (DEV-124).
#
# Imports a framework fixture into a normalized interchange
# manifest and companion loss report. Does not mutate
# Master-Plan or protected workflow files.
#
# Usage:
#   bash Docs/agtoosa-interchange-import.sh --fixture PATH
#       --output-manifest PATH --output-loss PATH
#
# Exit codes:
#   0 = manifest and loss report emitted
#   1 = validation failure
#   2 = usage / setup error
# ──────────────────────────────────────────────────────────────

FIXTURE=""
OUTPUT_MANIFEST=""
OUTPUT_LOSS=""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=../lib/interchange.sh
source "$REPO_ROOT/lib/interchange.sh"
# shellcheck source=../lib/interchange-providers/speckit.sh
source "$REPO_ROOT/lib/interchange-providers/speckit.sh"
# shellcheck source=../lib/interchange-providers/openspec.sh
source "$REPO_ROOT/lib/interchange-providers/openspec.sh"
# shellcheck source=../lib/interchange-providers/bmad.sh
source "$REPO_ROOT/lib/interchange-providers/bmad.sh"
# shellcheck source=../lib/interchange-providers/kiro.sh
source "$REPO_ROOT/lib/interchange-providers/kiro.sh"

usage() {
  sed -n '4,18p' "$0"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fixture)
      [[ $# -lt 2 ]] && { echo "Error: --fixture requires a path" >&2; exit 2; }
      FIXTURE="$2"; shift ;;
    --output-manifest)
      [[ $# -lt 2 ]] && { echo "Error: --output-manifest requires a path" >&2; exit 2; }
      OUTPUT_MANIFEST="$2"; shift ;;
    --output-loss)
      [[ $# -lt 2 ]] && { echo "Error: --output-loss requires a path" >&2; exit 2; }
      OUTPUT_LOSS="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Error: unknown argument '$1'" >&2; exit 2 ;;
  esac
  shift
done

[[ -n "$FIXTURE" ]] || { echo "Error: --fixture is required" >&2; exit 2; }
[[ -n "$OUTPUT_MANIFEST" ]] || { echo "Error: --output-manifest is required" >&2; exit 2; }
[[ -n "$OUTPUT_LOSS" ]] || { echo "Error: --output-loss is required" >&2; exit 2; }
[[ -f "$FIXTURE" ]] || { echo "Error: fixture '$FIXTURE' not found" >&2; exit 2; }

if [[ "$FIXTURE" == /* ]]; then
  case "$FIXTURE" in
    "$REPO_ROOT"/*) ;;
    *)
      echo "Error: fixture must be under repo root" >&2
      exit 2 ;;
  esac
else
  FIXTURE="$REPO_ROOT/$FIXTURE"
fi
[[ "$FIXTURE" != *".."* ]] || { echo "Error: unsafe fixture path" >&2; exit 2; }

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 required for interchange import" >&2
  exit 2
fi

FRAMEWORK="$(interchange_detect_framework_from_fixture "$FIXTURE")" || {
  echo "Error: could not detect framework from fixture" >&2
  exit 2
}

tmp_manifest="$(mktemp)"
tmp_loss="$(mktemp)"
trap 'rm -f "$tmp_manifest" "$tmp_loss"' EXIT

set +e
case "$FRAMEWORK" in
  speckit) interchange_import_speckit "$REPO_ROOT" "$FIXTURE" "$tmp_manifest" "$tmp_loss" ;;
  openspec) interchange_import_openspec "$REPO_ROOT" "$FIXTURE" "$tmp_manifest" "$tmp_loss" ;;
  bmad) interchange_import_bmad "$REPO_ROOT" "$FIXTURE" "$tmp_manifest" "$tmp_loss" ;;
  kiro) interchange_import_kiro "$REPO_ROOT" "$FIXTURE" "$tmp_manifest" "$tmp_loss" ;;
  *)
    echo "Error: unsupported framework '$FRAMEWORK'" >&2
    exit 2 ;;
esac
import_status=$?
set -e

[[ "$import_status" -eq 0 ]] || exit "$import_status"

interchange_validate_manifest "$REPO_ROOT" "$tmp_manifest" || exit 1
interchange_validate_loss_report "$tmp_loss" || exit 1

mkdir -p "$(dirname "$OUTPUT_MANIFEST")" "$(dirname "$OUTPUT_LOSS")"
cp "$tmp_manifest" "$OUTPUT_MANIFEST"
cp "$tmp_loss" "$OUTPUT_LOSS"
cat "$OUTPUT_MANIFEST"
exit 0

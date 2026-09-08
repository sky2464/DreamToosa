#!/usr/bin/env bash
set -uo pipefail

# ──────────────────────────────────────────────────────────────
# AgToosa interchange exporter — local, network-free (DEV-124).
#
# Exports an archived AgToosa spec to a normalized interchange
# manifest plus a framework-shaped artifact via fixture providers.
#
# Usage:
#   bash Docs/agtoosa-interchange-export.sh --story STORY_ID
#       --target speckit|openspec|bmad|kiro
#       [--proof-graph PATH] --output PATH
#
# Exit codes:
#   0 = manifest and artifact emitted
#   1 = validation failure
#   2 = usage / setup error
# ──────────────────────────────────────────────────────────────

STORY=""
TARGET=""
PROOF_GRAPH=""
OUTPUT=""

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
    --story)
      [[ $# -lt 2 ]] && { echo "Error: --story requires an id" >&2; exit 2; }
      STORY="$2"; shift ;;
    --target)
      [[ $# -lt 2 ]] && { echo "Error: --target requires a framework" >&2; exit 2; }
      TARGET="$2"; shift ;;
    --proof-graph)
      [[ $# -lt 2 ]] && { echo "Error: --proof-graph requires a path" >&2; exit 2; }
      PROOF_GRAPH="$2"; shift ;;
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
[[ -n "$TARGET" ]] || { echo "Error: --target is required" >&2; exit 2; }
[[ -n "$OUTPUT" ]] || { echo "Error: --output is required" >&2; exit 2; }

case "$TARGET" in
  speckit|openspec|bmad|kiro) ;;
  *)
    echo "Error: --target must be speckit, openspec, bmad, or kiro" >&2
    exit 2 ;;
esac

if [[ -n "$PROOF_GRAPH" ]]; then
  [[ -f "$PROOF_GRAPH" ]] || { echo "Error: proof graph '$PROOF_GRAPH' not found" >&2; exit 2; }
  interchange_path_safe "$PROOF_GRAPH" || { echo "Error: unsafe proof-graph path" >&2; exit 2; }
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 required for interchange export" >&2
  exit 2
fi

SPEC_PATH="$(interchange_resolve_spec_path "$REPO_ROOT" "$STORY")" || true
[[ -n "$SPEC_PATH" && -f "$SPEC_PATH" ]] || {
  echo "Error: archived spec for story '$STORY' not found" >&2
  exit 2
}

case "$TARGET" in
  kiro) ARTIFACT_EXT="json" ;;
  *) ARTIFACT_EXT="json" ;;
esac

ARTIFACT_PATH="$(interchange_derived_artifact_path "$OUTPUT" "$TARGET" "$ARTIFACT_EXT")"
tmp_manifest="$(mktemp)"
tmp_artifact="$(mktemp)"
trap 'rm -f "$tmp_manifest" "$tmp_artifact"' EXIT

set +e
case "$TARGET" in
  speckit)
    interchange_export_speckit "$REPO_ROOT" "$STORY" "$SPEC_PATH" "$PROOF_GRAPH" "$tmp_manifest" "$tmp_artifact" ;;
  openspec)
    interchange_export_openspec "$REPO_ROOT" "$STORY" "$SPEC_PATH" "$PROOF_GRAPH" "$tmp_manifest" "$tmp_artifact" ;;
  bmad)
    interchange_export_bmad "$REPO_ROOT" "$STORY" "$SPEC_PATH" "$PROOF_GRAPH" "$tmp_manifest" "$tmp_artifact" ;;
  kiro)
    interchange_export_kiro "$REPO_ROOT" "$STORY" "$SPEC_PATH" "$PROOF_GRAPH" "$tmp_manifest" "$tmp_artifact" ;;
esac
export_status=$?
set -e

[[ "$export_status" -eq 0 ]] || exit "$export_status"

interchange_validate_manifest "$REPO_ROOT" "$tmp_manifest" || exit 1

mkdir -p "$(dirname "$OUTPUT")" "$(dirname "$ARTIFACT_PATH")"
cp "$tmp_manifest" "$OUTPUT"
cp "$tmp_artifact" "$ARTIFACT_PATH"
cat "$OUTPUT"
exit 0

#!/usr/bin/env bash
set -uo pipefail

# ──────────────────────────────────────────────────────────────
# AgToosa context compiler — local, network-free (DEV-122).
#
# Emits context-compilation JSON for agent-instructed /agtoosa-build
# consumption. Does not mutate Master-Plan or task trees.
#
# Usage:
#   bash Docs/agtoosa-context-compile.sh --story STORY_ID
#       [--output PATH] [--proof-graph PATH] [--drift-report PATH]
#
# Exit codes:
#   0 = compilation emitted
#   1 = validation failure
#   2 = usage / setup error
# ──────────────────────────────────────────────────────────────

STORY=""
OUTPUT=""
PROOF_GRAPH=""
DRIFT_REPORT=""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=../lib/drift.sh
source "$REPO_ROOT/lib/drift.sh"

usage() {
  sed -n '4,17p' "$0"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --story)
      [[ $# -lt 2 ]] && { echo "Error: --story requires an id" >&2; exit 2; }
      STORY="$2"; shift ;;
    --output)
      [[ $# -lt 2 ]] && { echo "Error: --output requires a path" >&2; exit 2; }
      OUTPUT="$2"; shift ;;
    --proof-graph)
      [[ $# -lt 2 ]] && { echo "Error: --proof-graph requires a path" >&2; exit 2; }
      PROOF_GRAPH="$2"; shift ;;
    --drift-report)
      [[ $# -lt 2 ]] && { echo "Error: --drift-report requires a path" >&2; exit 2; }
      DRIFT_REPORT="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Error: unknown argument '$1'" >&2; exit 2 ;;
  esac
  shift
done

[[ -n "$STORY" ]] || { echo "Error: --story is required" >&2; exit 2; }
[[ "$STORY" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "Error: invalid story id" >&2; exit 2; }

if [[ -n "$PROOF_GRAPH" && ! -f "$PROOF_GRAPH" ]]; then
  echo "Error: proof graph '$PROOF_GRAPH' not found" >&2
  exit 2
fi
if [[ -n "$DRIFT_REPORT" && ! -f "$DRIFT_REPORT" ]]; then
  echo "Error: drift report '$DRIFT_REPORT' not found" >&2
  exit 2
fi

[[ -n "$OUTPUT" ]] || OUTPUT="$REPO_ROOT/tests/fixtures/drift-assess/context-compilation-${STORY}.json"

tmp_out="$(mktemp)"
trap 'rm -f "$tmp_out"' EXIT

python3 - "$STORY" "$PROOF_GRAPH" "$DRIFT_REPORT" "$tmp_out" <<'PY'
import json, sys
from datetime import datetime, timezone

story, proof_graph, drift_report, out_path = sys.argv[1:5]

def load_optional(path):
    if not path:
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)

drift_data = load_optional(drift_report)
drift_block = {
    "summary": {"added": 0, "removed": 0, "modified": 0, "unchanged": 0},
    "overall_impact_level": "none",
    "suggested_rigor": "light",
}
if drift_report:
    drift_block["report_path"] = drift_report
if drift_data:
    drift_block["summary"] = drift_data.get("summary", drift_block["summary"])
    drift_block["overall_impact_level"] = drift_data.get("overall_impact_level", "none")
    drift_block["suggested_rigor"] = drift_data.get("suggested_rigor", "light")

paths = []
if proof_graph:
    try:
        graph = load_optional(proof_graph)
        for node in graph.get("nodes", []):
            if node.get("type") == "artifact" and node.get("ref"):
                paths.append(node["ref"])
    except (TypeError, AttributeError):
        pass
paths = sorted(set(paths))

compilation = {
    "version": 1,
    "story_id": story,
    "compiled_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "provenance": {
        "proof_graph_verified": False,
        "proof_verify_note": "Run Docs/agtoosa-proof-verify.sh separately; this compiler does not verify graphs.",
    },
    "drift": drift_block,
    "task_context": {
        "story_id": story,
        "paths": paths,
        "notes": "Derived context only — does not replace Docs/Master-Plan.md authority.",
    },
}
if proof_graph:
    compilation["provenance"]["proof_graph_path"] = proof_graph

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(compilation, f, indent=2)
    f.write("\n")
PY

drift_validate_context_compilation "$tmp_out" || exit 1
cp "$tmp_out" "$OUTPUT"
cat "$OUTPUT"
exit 0

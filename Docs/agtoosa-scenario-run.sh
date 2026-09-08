#!/usr/bin/env bash
set -uo pipefail

# AgToosa scenario maintainer runner — documents steps, verifies artifacts (DEV-121).
#
# Usage:
#   bash docs/agtoosa-scenario-run.sh --scenario ID --platform NAME --artifact-root PATH
#       [--corpus PATH] [--proof-graph PATH]
#
# Exit codes:
#   0 = verification passed and scenario-run.json written
#   1 = verification failed (scenario-run.json still written when possible)
#   2 = usage / setup error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=../lib/scenario.sh
source "$REPO_ROOT/lib/scenario.sh"

CORPUS=""
SCENARIO=""
PLATFORM=""
ARTIFACT_ROOT=""
PROOF_GRAPH=""

usage() {
  sed -n '4,12p' "$0"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --corpus)
      [[ $# -lt 2 ]] && { echo "Error: --corpus requires a path" >&2; exit 2; }
      CORPUS="$2"; shift ;;
    --scenario)
      [[ $# -lt 2 ]] && { echo "Error: --scenario requires an id" >&2; exit 2; }
      SCENARIO="$2"; shift ;;
    --platform)
      [[ $# -lt 2 ]] && { echo "Error: --platform requires a name" >&2; exit 2; }
      PLATFORM="$2"; shift ;;
    --artifact-root)
      [[ $# -lt 2 ]] && { echo "Error: --artifact-root requires a directory" >&2; exit 2; }
      ARTIFACT_ROOT="$2"; shift ;;
    --proof-graph)
      [[ $# -lt 2 ]] && { echo "Error: --proof-graph requires a path" >&2; exit 2; }
      PROOF_GRAPH="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Error: unknown argument '$1'" >&2; exit 2 ;;
  esac
  shift
done

[[ -n "$SCENARIO" ]] || { echo "Error: --scenario is required" >&2; exit 2; }
[[ -n "$PLATFORM" ]] || { echo "Error: --platform is required" >&2; exit 2; }
[[ -n "$ARTIFACT_ROOT" ]] || { echo "Error: --artifact-root is required" >&2; exit 2; }

scenario_is_platform "$PLATFORM" || { echo "Error: unknown platform '$PLATFORM'" >&2; exit 2; }

mkdir -p "$ARTIFACT_ROOT" || { echo "Error: cannot create artifact root" >&2; exit 2; }

CORPUS="${CORPUS:-$REPO_ROOT/data/scenarios/corpus-v1.json}"
VERIFY="$SCRIPT_DIR/agtoosa-scenario-verify.sh"
RUN_JSON="$ARTIFACT_ROOT/scenario-run.json"

echo "=== AgToosa Scenario Run: $SCENARIO ($PLATFORM) ==="
echo ""
echo "Maintainer steps (shared):"
python3 - "$REPO_ROOT" "$SCENARIO" <<'PY'
import json, os, sys
root, sid = sys.argv[1], sys.argv[2]
with open(os.path.join(root, "scenarios", f"{sid}.json"), encoding="utf-8") as f:
    s = json.load(f)
for i, step in enumerate(s.get("maintainer_steps", {}).get("shared", []), 1):
    print(f"  {i}. {step}")
PY

echo ""
echo "Platform-specific ($PLATFORM):"
python3 - "$REPO_ROOT" "$SCENARIO" "$PLATFORM" <<'PY'
import json, os, sys
root, sid, plat = sys.argv[1], sys.argv[2], sys.argv[3]
with open(os.path.join(root, "scenarios", f"{sid}.json"), encoding="utf-8") as f:
    s = json.load(f)
for i, step in enumerate(s.get("maintainer_steps", {}).get(plat, []), 1):
    print(f"  {i}. {step}")
PY

echo ""
echo "After collecting artifacts under: $ARTIFACT_ROOT"
echo "Running static verifier..."
echo ""

verify_args=(--scenario "$SCENARIO" --platform "$PLATFORM" --root "$ARTIFACT_ROOT" --run-json "$RUN_JSON")
[[ -n "$CORPUS" ]] && verify_args+=(--corpus "$CORPUS")

set +e
bash "$VERIFY" "${verify_args[@]}"
verify_exit=$?
set -e

if [[ -n "$PROOF_GRAPH" ]]; then
  python3 - "$RUN_JSON" "$PROOF_GRAPH" <<'PY'
import json, sys
path, graph = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as f:
    data = json.load(f)
data["proof_graph_path"] = graph
data["runner_notes"] = (data.get("runner_notes") or "") + " proof_graph_path set by runner."
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY
fi

python3 - "$RUN_JSON" "$verify_exit" <<'PY'
import json, sys
path, code = sys.argv[1], int(sys.argv[2])
with open(path, encoding="utf-8") as f:
    data = json.load(f)
data["verifier_exit_code"] = code
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY

if [[ "$verify_exit" -eq 0 ]]; then
  echo "PASS — scenario-run.json written to $RUN_JSON"
  exit 0
fi

echo "FAIL — verifier exit $verify_exit; scenario-run.json updated with failure details" >&2
exit 1

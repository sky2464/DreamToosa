#!/usr/bin/env bash
set -uo pipefail

# AgToosa scenario static verifier — local, network-free (DEV-121).
#
# Usage:
#   bash docs/agtoosa-scenario-verify.sh --scenario ID --platform NAME --root PATH
#       [--corpus PATH] [--run-json PATH]
#
# Exit codes:
#   0 = all artifact checks pass
#   1 = verification failure
#   2 = usage / setup error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=../lib/scenario.sh
source "$REPO_ROOT/lib/scenario.sh"

CORPUS=""
SCENARIO=""
PLATFORM=""
ROOT=""
RUN_JSON=""

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
    --root)
      [[ $# -lt 2 ]] && { echo "Error: --root requires a directory" >&2; exit 2; }
      ROOT="$2"; shift ;;
    --run-json)
      [[ $# -lt 2 ]] && { echo "Error: --run-json requires a path" >&2; exit 2; }
      RUN_JSON="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Error: unknown argument '$1'" >&2; exit 2 ;;
  esac
  shift
done

[[ -n "$SCENARIO" ]] || { echo "Error: --scenario is required" >&2; exit 2; }
[[ -n "$PLATFORM" ]] || { echo "Error: --platform is required" >&2; exit 2; }
[[ -n "$ROOT" ]] || { echo "Error: --root is required" >&2; exit 2; }
[[ -d "$ROOT" ]] || { echo "Error: root '$ROOT' is not a directory" >&2; exit 2; }

scenario_is_platform "$PLATFORM" || { echo "Error: unknown platform '$PLATFORM'" >&2; exit 2; }

CORPUS="${CORPUS:-$REPO_ROOT/data/scenarios/corpus-v1.json}"
[[ -f "$CORPUS" ]] || { echo "Error: corpus file '$CORPUS' not found" >&2; exit 2; }

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 required for scenario verification" >&2
  exit 2
fi

scenario_validate_corpus "$REPO_ROOT" "$CORPUS" || exit 2
def_path="$(scenario_load_definition "$REPO_ROOT" "$SCENARIO")" || exit 2
[[ -f "$def_path" ]] || { echo "Error: scenario definition not found" >&2; exit 2; }

out="$(scenario_verify_impl "$REPO_ROOT" "$SCENARIO" "$PLATFORM" "$ROOT" 2>/dev/null)" || true
ok=false
if python3 -c 'import json,sys; d=json.loads(sys.argv[1]); sys.exit(0 if d.get("ok") else 1)' "$out" 2>/dev/null; then
  ok=true
fi

if [[ -n "$RUN_JSON" ]]; then
  python3 - "$out" "$RUN_JSON" "$SCENARIO" "$PLATFORM" <<'PY'
import json, sys
from datetime import datetime, timezone
payload = json.loads(sys.argv[1]) if sys.argv[1] else {"ok": False, "results": []}
out_path, scenario_id, platform = sys.argv[2], sys.argv[3], sys.argv[4]
doc = {
    "version": 1,
    "scenario_id": scenario_id,
    "platform": platform,
    "run_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "artifact_results": payload.get("results", []),
    "verifier_exit_code": 0 if payload.get("ok") else 1,
}
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=2)
    f.write("\n")
PY
fi

if [[ "$ok" == true ]]; then
  exit 0
fi
first="$(python3 - "$out" <<'PY' 2>/dev/null || echo "verification failed"
import json, sys
d = json.loads(sys.argv[1])
f = d.get("first_failure", {})
print(f"{f.get('path', '?')}: {f.get('detail', 'failed')}")
PY
)"
echo "Error: $first" >&2
exit 1

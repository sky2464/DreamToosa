#!/usr/bin/env bash
set -uo pipefail

# ──────────────────────────────────────────────────────────────
# AgToosa capsule verifier — local, network-free (DEV-123).
#
# Validates execution-capsule-v1 JSON, rejects path traversal,
# and scans for secret-like patterns. Default policy is network
# deny (documented only — this script does not perform network I/O).
#
# Usage:
#   bash Docs/agtoosa-capsule-verify.sh --capsule PATH
#
# Exit codes:
#   0 = capsule valid
#   1 = validation failure
#   2 = usage / setup error
# ──────────────────────────────────────────────────────────────

CAPSULE=""
STRICT=false

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=../lib/capsule.sh
source "$REPO_ROOT/lib/capsule.sh"

usage() {
  sed -n '4,18p' "$0"
}

capsule_scan_secrets() {
  local capsule_file="$1"
  python3 - "$capsule_file" <<'PY'
import json, re, sys

path = sys.argv[1]
patterns = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "aws_access_key"),
    (re.compile(r"sk_live_[a-zA-Z0-9]+"), "stripe_secret_key"),
    (re.compile(
        r"(?i)(api[_-]?key|client[_-]?secret|password|token)\s*[:=]\s*['\"]?[a-zA-Z0-9_./+-]{8,}"
    ), "credential_assignment"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private_key_pem"),
    (re.compile(r"ghp_[a-zA-Z0-9]{20,}"), "github_pat"),
]

try:
    with open(path, encoding="utf-8") as f:
        raw = f.read()
        json.loads(raw)
except (OSError, json.JSONDecodeError) as e:
    print(f"Error: cannot read capsule for secret scan: {e}", file=sys.stderr)
    sys.exit(1)

for regex, label in patterns:
    if regex.search(raw):
        print(f"Error: secret pattern detected ({label})", file=sys.stderr)
        sys.exit(1)
PY
}

capsule_policy_strict_check() {
  local capsule_file="$1"
  python3 - "$capsule_file" <<'PY'
import json, sys

path = sys.argv[1]
with open(path, encoding="utf-8") as f:
    data = json.load(f)

policy = data.get("policy", {})
if policy.get("network") != "deny":
    print("Error: strict mode requires policy.network deny", file=sys.stderr)
    sys.exit(1)
if policy.get("secrets") != "forbid":
    print("Error: strict mode requires policy.secrets forbid", file=sys.stderr)
    sys.exit(1)

for cmd in data.get("verification", {}).get("commands", []):
    command = (cmd.get("command") or "").lower()
    if any(tok in command for tok in ("curl ", "wget ", "npm install", "pip install")):
        print(f"Error: strict mode blocks network-like verification command: {cmd.get('command')}", file=sys.stderr)
        sys.exit(1)
PY
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --capsule)
      [[ $# -lt 2 ]] && { echo "Error: --capsule requires a path" >&2; exit 2; }
      CAPSULE="$2"; shift ;;
    --strict) STRICT=true ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Error: unknown argument '$1'" >&2; exit 2 ;;
  esac
  shift
done

[[ -n "$CAPSULE" ]] || { echo "Error: --capsule is required" >&2; exit 2; }
[[ -f "$CAPSULE" ]] || { echo "Error: capsule '$CAPSULE' not found" >&2; exit 2; }

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 required for capsule validation" >&2
  exit 2
fi

capsule_validate_capsule "$REPO_ROOT" "$CAPSULE" || exit 1
capsule_scan_secrets "$CAPSULE" || exit 1
if [[ "$STRICT" == true ]]; then
  capsule_policy_strict_check "$CAPSULE" || exit 1
fi

echo "Capsule valid: $CAPSULE"
exit 0

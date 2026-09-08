#!/usr/bin/env bash
set -uo pipefail

# ──────────────────────────────────────────────────────────────
# AgToosa proof graph verifier — local, network-free (DEV-120).
#
# Validates Evidence Provenance v2 proof graphs using the
# local-hash provider (SHA-256 content bindings + optional
# repo snapshot). Does NOT re-run verification commands.
#
# Usage:
#   bash Docs/agtoosa-proof-verify.sh [--root PATH] [--graph PATH]
#       [--provider local-hash] [--allow-stale-snapshot]
#
# Exit codes:
#   0 = graph valid
#   1 = validation failure
#   2 = usage / setup error
# ──────────────────────────────────────────────────────────────

ROOT="$PWD"
GRAPH=""
PROVIDER="local-hash"
ALLOW_STALE=false

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=../lib/proof-providers/local-hash.sh
source "$REPO_ROOT/lib/proof-providers/local-hash.sh"

usage() {
  sed -n '4,18p' "$0"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      [[ $# -lt 2 ]] && { echo "Error: --root requires a directory" >&2; exit 2; }
      ROOT="$2"; shift ;;
    --graph)
      [[ $# -lt 2 ]] && { echo "Error: --graph requires a path" >&2; exit 2; }
      GRAPH="$2"; shift ;;
    --provider)
      [[ $# -lt 2 ]] && { echo "Error: --provider requires a name" >&2; exit 2; }
      PROVIDER="$2"; shift ;;
    --allow-stale-snapshot) ALLOW_STALE=true ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Error: unknown argument '$1'" >&2; exit 2 ;;
  esac
  shift
done

[[ -d "$ROOT" ]] || { echo "Error: root '$ROOT' is not a directory" >&2; exit 2; }
[[ -n "$GRAPH" ]] || { echo "Error: --graph is required" >&2; exit 2; }
[[ -f "$GRAPH" ]] || { echo "Error: graph file '$GRAPH' not found" >&2; exit 2; }

if [[ "$PROVIDER" != "local-hash" ]]; then
  echo "Error: unsupported provider '$PROVIDER' (only local-hash in v1)" >&2
  exit 2
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 required for proof graph validation" >&2
  exit 2
fi

if ! command -v git >/dev/null 2>&1; then
  echo "Error: git required for repo-snapshot validation" >&2
  exit 2
fi

proof_provider_local_hash_verify "$ROOT" "$GRAPH" "$ALLOW_STALE"

#!/usr/bin/env python3
"""Validate the DreamToosa control plane.

The "Dream Report" routine (trig_01PvQiwSRhJktFxMXwxf14Qi) reads repos.yml and
state.json at the start of every run. Its Phase 0 fail-safe stops the run cold if
the manifest is missing or unparseable — correct, but it means a malformed control
plane yields a routine that silently does nothing, daily, until someone reads a run
log. These checks catch that at commit time instead.

Run locally:   python3 dreamtoosa/validate.py
In CI:         .github/workflows/control-plane.yml
In the routine: before the Phase 6 state.json commit.

Exits 0 when every check passes, 1 otherwise, listing each failure.
"""

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("FATAL: PyYAML is required — pip install pyyaml")

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "repos.yml"
STATE = HERE / "state.json"
PROFILES = HERE / "profiles"

failures: list[str] = []
checks_run = 0


def check(label: str, ok: bool, detail: str = "") -> bool:
    """Record one check. Returns ok so callers can gate dependent checks."""
    global checks_run
    checks_run += 1
    if ok:
        print(f"  ok    {label}")
    else:
        print(f"  FAIL  {label}" + (f" — {detail}" if detail else ""))
        failures.append(label)
    return ok


def main() -> int:
    print("DreamToosa control plane validation")

    # --- parse -------------------------------------------------------------
    if not check("repos.yml exists", MANIFEST.is_file(), str(MANIFEST)):
        return finish()
    if not check("state.json exists", STATE.is_file(), str(STATE)):
        return finish()

    try:
        manifest = yaml.safe_load(MANIFEST.read_text())
        check("repos.yml parses as YAML", True)
    except yaml.YAMLError as exc:
        check("repos.yml parses as YAML", False, str(exc).replace("\n", " ")[:200])
        return finish()

    try:
        state = json.loads(STATE.read_text())
        check("state.json parses as JSON", True)
    except json.JSONDecodeError as exc:
        check("state.json parses as JSON", False, str(exc))
        return finish()

    # --- shape -------------------------------------------------------------
    if not check("repos.yml has a 'repos' list",
                 isinstance(manifest.get("repos"), list) and manifest["repos"]):
        return finish()

    entries = manifest["repos"]
    if not check("every repo entry has 'repo' and 'profile'",
                 all(e.get("repo") and e.get("profile") for e in entries),
                 "one or more entries missing a required key"):
        return finish()

    manifest_repos = {e["repo"] for e in entries}

    # --- manifest vs state -------------------------------------------------
    state_repos = set((state.get("repos") or {}).keys())
    check("state.json tracks exactly the manifest's repos",
          manifest_repos == state_repos,
          f"only in manifest: {sorted(manifest_repos - state_repos)} | "
          f"only in state: {sorted(state_repos - manifest_repos)}")

    rotation = (state.get("fix_rotation") or {}).get("order") or []
    check("fix_rotation.order covers exactly the manifest's repos",
          manifest_repos == set(rotation),
          f"only in manifest: {sorted(manifest_repos - set(rotation))} | "
          f"only in rotation: {sorted(set(rotation) - manifest_repos)}")
    check("fix_rotation.order has no duplicates",
          len(rotation) == len(set(rotation)))

    last_index = (state.get("fix_rotation") or {}).get("last_index")
    check("fix_rotation.last_index is in range",
          isinstance(last_index, int) and -1 <= last_index < max(len(rotation), 1),
          f"last_index={last_index!r}, rotation length={len(rotation)}")

    # --- profiles ----------------------------------------------------------
    used = {e["profile"] for e in entries}
    present = {p.stem for p in PROFILES.glob("*.md")} if PROFILES.is_dir() else set()
    check("every profile referenced by a repo exists",
          used <= present,
          f"missing dreamtoosa/profiles/*.md for: {sorted(used - present)}")
    check("no orphaned profile files",
          present <= used,
          f"unreferenced: {sorted(present - used)}")

    # --- hub and budget ----------------------------------------------------
    hub = manifest.get("hub") or {}
    check("hub declares repo and reports_dir",
          bool(hub.get("repo") and hub.get("reports_dir")))

    budget = manifest.get("budget") or {}
    required_budget = {
        "max_repos_reviewed_per_run",
        "max_fix_repos_per_run",
        "max_issues_per_repo_per_run",
        "max_prs_per_run",
    }
    check("budget declares all required caps",
          required_budget <= set(budget),
          f"missing: {sorted(required_budget - set(budget))}")
    check("budget caps are positive integers",
          all(isinstance(budget.get(k), int) and budget[k] > 0
              for k in required_budget & set(budget)),
          f"non-positive or non-integer: "
          f"{[k for k in sorted(required_budget & set(budget)) if not (isinstance(budget.get(k), int) and budget[k] > 0)]}")

    # --- caps --------------------------------------------------------------
    bad_caps = [e["repo"] for e in entries
                if e.get("max_open_prs") is not None
                and not (isinstance(e["max_open_prs"], int) and e["max_open_prs"] >= 0)]
    check("per-repo max_open_prs values are non-negative integers",
          not bad_caps, f"bad: {bad_caps}")

    return finish()


def finish() -> int:
    print()
    if failures:
        print(f"FAILED — {len(failures)} of {checks_run} checks: {', '.join(failures)}")
        return 1
    print(f"PASSED — {checks_run} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())

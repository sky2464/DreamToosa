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

Exits 0 when every check passes, 1 when a check fails (each failure listed), and 2 when
the validator itself cannot run (PyYAML missing, or an uncaught exception).

The Fleet Triage keys are checked only when repos.yml has a top-level `triage` block, so
an older manifest validates exactly as before. This script imports no triage module: the
control plane must stay checkable even when those modules are broken.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Callable, List, Optional, Set, Tuple

try:
    import yaml
except Exception:  # missing or broken PyYAML is an environment fault, never a check failure
    print("FATAL: PyYAML is required — pip install pyyaml", file=sys.stderr)
    sys.exit(2)

HERE = Path(__file__).resolve().parent
DEFAULT_MANIFEST = HERE / "repos.yml"
DEFAULT_STATE = HERE / "state.json"
DEFAULT_PROFILES = HERE / "profiles"

VALID_PR_STRATEGIES: Set[str] = {"chain", "rolling", "independent"}
# Tuples, not sets: `x in tuple` is safe for an unhashable YAML value such as a list.
VISIBILITIES = ("public", "private")
WATCH_KINDS = ("security", "sync", "audit")
DEPENDABOT_SCOPES = ("runtime", "dev", "unknown")
WORKFLOW_FILE = re.compile(r"[\w.-]+\.ya?ml")  # used with fullmatch: `$` would accept a trailing newline
LOGIN = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}(\[bot\])?")
WINDOW_KEYS = ("pr_idle_days", "routine_gap_days", "heartbeat_max_age_days")
COLUMN_KEYS = ("id", "title", "priority")
LIST_KEYS = ("p0_values", "done_values", "done_sections")


def _pos_int(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v > 0


def _name(v: Any) -> bool:
    return isinstance(v, str) and bool(v)


def _names(v: Any, least: int = 0) -> bool:
    return isinstance(v, list) and len(v) >= least and all(_name(x) for x in v)


def _at(d: Any, *keys: str) -> Any:
    """Nested lookup that yields None, not an exception, on a wrong-typed branch."""
    for k in keys:
        d = d.get(k) if isinstance(d, dict) else None
    return d


def _relative_path(v: Any) -> bool:
    return _name(v) and "\\" not in v and not v.startswith("/") and v[1:2] != ":" and ".." not in v.split("/")


def _workflows_ok(e: dict) -> bool:
    """product_workflows are filenames; watch_workflows are {file, kind} with a known kind."""
    product, watch = e.get("product_workflows", []), e.get("watch_workflows", [])
    if not (isinstance(product, list) and isinstance(watch, list)):
        return False
    files = product + [_at(w, "file") for w in watch]
    return all(isinstance(f, str) and WORKFLOW_FILE.fullmatch(f) for f in files) and all(
        _at(w, "kind") in WATCH_KINDS for w in watch
    )


def _check_triage(manifest: dict, entries: List[dict], check: Callable[..., bool]) -> None:
    """Fleet Triage keys. Called only when the manifest has a `triage` block."""
    triage = manifest["triage"]
    if not check("triage block is a mapping", isinstance(triage, dict), f"got {triage!r}"):
        return

    def positive(label: str, *values: Any) -> bool:
        return check(label, all(_pos_int(v) for v in values), f"got {list(values)!r}")

    total, per_repo = triage.get("max_items_total"), triage.get("max_items_per_repo")
    if positive("triage caps are positive integers", total, per_repo):
        check("triage.max_items_total is at least triage.max_items_per_repo", total >= per_repo)
    positive("triage idle, gap and heartbeat windows are positive integers", *map(triage.get, WINDOW_KEYS))
    logins = triage.get("trusted_logins")
    ok = _names(logins, 1) and all(LOGIN.fullmatch(x) for x in logins)
    check("triage.trusted_logins is a non-empty list of logins", ok, f"got {logins!r}")
    stale, dormant = _at(manifest, "defaults", "stale_after_days"), _at(manifest, "defaults", "dormant_after_days")
    if positive("defaults stale and dormant windows are positive integers", stale, dormant):
        check("defaults.stale_after_days is less than defaults.dormant_after_days", stale < dormant)
    box = _at(manifest, "budget", "soft_time_box_minutes_fleet_triage")
    positive("budget.soft_time_box_minutes_fleet_triage is a positive integer", box)
    force = _at(manifest, "hub", "force_read_only")
    check("hub.force_read_only is a boolean when present", force is None or isinstance(force, bool), f"got {force!r}")

    b = lambda e, *keys: _at(e, "backlog", *keys)  # noqa: E731
    rules: List[Tuple[str, Callable[[dict], bool]]] = [
        ("every repo declares visibility public or private", lambda e: e.get("visibility") in VISIBILITIES),
        ("every repo's backlog path is relative with no '..'", lambda e: _relative_path(b(e, "path"))),
        ("every repo's backlog header_all is a non-empty list", lambda e: _names(b(e, "header_all"), 1)),
        (
            "every repo's backlog columns id, title, priority are names and status is a name or null",
            lambda e: all(_name(b(e, "columns", k)) for k in COLUMN_KEYS)
            and (b(e, "columns", "status") is None or _name(b(e, "columns", "status"))),
        ),
        (
            "every repo's backlog p0_values, done_values and done_sections are lists",
            lambda e: all(_names(b(e, k)) for k in LIST_KEYS),
        ),
        ("every repo's workflow filenames and watch kinds are valid", _workflows_ok),
        (
            "every repo's dependabot_scope is runtime, dev or unknown when present",
            lambda e: "dependabot_scope" not in e or e["dependabot_scope"] in DEPENDABOT_SCOPES,
        ),
    ]
    for label, ok in rules:
        bad = [str(e.get("repo")) for e in entries if not ok(e)]
        check(label, not bad, f"bad: {bad}")


def validate_control_plane(
    manifest_path: Optional[Path] = None,
    state_path: Optional[Path] = None,
    profiles_dir: Optional[Path] = None,
    verbose: bool = True,
) -> Tuple[int, List[str]]:
    """
    Validate the control plane configuration and return (checks_run, failures).
    """
    manifest_file = Path(manifest_path or DEFAULT_MANIFEST)
    state_file = Path(state_path or DEFAULT_STATE)
    profiles_path = Path(profiles_dir or DEFAULT_PROFILES)

    failures: List[str] = []
    checks_run = 0

    def check(label: str, ok: bool, detail: str = "") -> bool:
        nonlocal checks_run
        checks_run += 1
        if ok:
            if verbose:
                print(f"  ok    {label}")
        else:
            if verbose:
                print(f"  FAIL  {label}" + (f" — {detail}" if detail else ""))
            failures.append(label)
        return ok

    if verbose:
        print("DreamToosa control plane validation")

    # --- parse -------------------------------------------------------------
    if not check("repos.yml exists", manifest_file.is_file(), str(manifest_file)):
        return checks_run, failures
    if not check("state.json exists", state_file.is_file(), str(state_file)):
        return checks_run, failures

    try:
        manifest = yaml.safe_load(manifest_file.read_text(encoding="utf-8"))
        check("repos.yml parses as YAML", True)
    except yaml.YAMLError as exc:
        check("repos.yml parses as YAML", False, str(exc).replace("\n", " ")[:200])
        return checks_run, failures

    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
        check("state.json parses as JSON", True)
    except json.JSONDecodeError as exc:
        check("state.json parses as JSON", False, str(exc))
        return checks_run, failures

    # --- shape -------------------------------------------------------------
    if not check(
        "repos.yml has a 'repos' list",
        isinstance(manifest.get("repos"), list) and manifest["repos"],
    ):
        return checks_run, failures

    entries = manifest["repos"]
    if not check(
        "every repo entry has 'repo' and 'profile'",
        all(e.get("repo") and e.get("profile") for e in entries),
        "one or more entries missing a required key",
    ):
        return checks_run, failures

    manifest_repos = {e["repo"] for e in entries}

    # --- manifest vs state -------------------------------------------------
    state_repos = set((state.get("repos") or {}).keys())
    check(
        "state.json tracks exactly the manifest's repos",
        manifest_repos == state_repos,
        f"only in manifest: {sorted(manifest_repos - state_repos)} | "
        f"only in state: {sorted(state_repos - manifest_repos)}",
    )

    rotation = (state.get("fix_rotation") or {}).get("order") or []
    check(
        "fix_rotation.order covers exactly the manifest's repos",
        manifest_repos == set(rotation),
        f"only in manifest: {sorted(manifest_repos - set(rotation))} | "
        f"only in rotation: {sorted(set(rotation) - manifest_repos)}",
    )
    check(
        "fix_rotation.order has no duplicates",
        len(rotation) == len(set(rotation)),
    )

    last_index = (state.get("fix_rotation") or {}).get("last_index")
    check(
        "fix_rotation.last_index is in range",
        isinstance(last_index, int) and -1 <= last_index < max(len(rotation), 1),
        f"last_index={last_index!r}, rotation length={len(rotation)}",
    )

    # --- profiles ----------------------------------------------------------
    used = {e["profile"] for e in entries}
    present = {p.stem for p in profiles_path.glob("*.md")} if profiles_path.is_dir() else set()
    check(
        "every profile referenced by a repo exists",
        used <= present,
        f"missing dreamtoosa/profiles/*.md for: {sorted(used - present)}",
    )
    check(
        "no orphaned profile files",
        present <= used,
        f"unreferenced: {sorted(present - used)}",
    )

    # --- hub and budget ----------------------------------------------------
    hub = manifest.get("hub") or {}
    check(
        "hub declares repo and reports_dir",
        bool(hub.get("repo") and hub.get("reports_dir")),
    )

    if hub.get("max_unmerged_report_prs") is not None:
        check(
            "hub.max_unmerged_report_prs is a positive integer",
            isinstance(hub["max_unmerged_report_prs"], int) and hub["max_unmerged_report_prs"] > 0,
            f"got {hub.get('max_unmerged_report_prs')!r}",
        )

    if hub.get("pr_strategy") is not None:
        check(
            "hub.pr_strategy is a supported strategy",
            hub["pr_strategy"] in VALID_PR_STRATEGIES,
            f"got {hub.get('pr_strategy')!r}, expected one of {sorted(VALID_PR_STRATEGIES)}",
        )

    defaults = manifest.get("defaults") or {}
    if defaults.get("clone_root_env") is not None:
        clone_env = defaults["clone_root_env"]
        check(
            "defaults.clone_root_env is a valid environment variable name",
            isinstance(clone_env, str) and clone_env.isidentifier(),
            f"got {clone_env!r}",
        )

    budget = manifest.get("budget") or {}
    required_budget = {
        "max_repos_reviewed_per_run",
        "max_fix_repos_per_run",
        "max_issues_per_repo_per_run",
        "max_prs_per_run",
    }
    check(
        "budget declares all required caps",
        required_budget <= set(budget),
        f"missing: {sorted(required_budget - set(budget))}",
    )
    check(
        "budget caps are positive integers",
        all(isinstance(budget.get(k), int) and budget[k] > 0 for k in required_budget & set(budget)),
        f"non-positive or non-integer: "
        f"{[k for k in sorted(required_budget & set(budget)) if not (isinstance(budget.get(k), int) and budget[k] > 0)]}",
    )

    # --- caps --------------------------------------------------------------
    bad_caps = [
        e["repo"]
        for e in entries
        if e.get("max_open_prs") is not None
        and not (isinstance(e["max_open_prs"], int) and e["max_open_prs"] >= 0)
    ]
    check(
        "per-repo max_open_prs values are non-negative integers",
        not bad_caps,
        f"bad: {bad_caps}",
    )

    # --- fleet triage (only when the manifest opts in) ----------------------
    if "triage" in manifest:
        _check_triage(manifest, entries, check)

    return checks_run, failures


def main() -> int:
    try:
        checks_run, failures = validate_control_plane(verbose=True)
    except Exception as exc:  # exit 2 keeps a crash distinct from a failed check (exit 1)
        print(f"FATAL: unexpected error ({type(exc).__name__}): {str(exc)[:200]}", file=sys.stderr)
        return 2
    print()
    if failures:
        print(f"FAILED — {len(failures)} of {checks_run} checks: {', '.join(failures)}")
        return 1
    print(f"PASSED — {checks_run} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())

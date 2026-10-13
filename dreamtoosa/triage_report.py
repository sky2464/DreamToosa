#!/usr/bin/env python3
"""Fleet Triage CLI (DEV-005a): check, render and heartbeat. Run it as a script by absolute path; it imports triage from its own directory.

  triage_report.py check     --snapshot S --manifest M [--clone-root R]
  triage_report.py render    --snapshot S --manifest M [--clone-root R | --backlog-dir D] [--inject INDEX] [--unavailable CODE]
  triage_report.py heartbeat --repo-root DIR [--today YYYY-MM-DD] [--manifest M]

Exit 0 ok, 1 fixed codes on stdout one per line (check found a problem, render refused, heartbeat stale), 2 usage error or cannot run (E_RUN).
With --clone-root, check and render first confirm that dreamtoosa/ in the hub clone is untouched (E_ENGINE_TAMPERED, before triage.py is imported), then
re-derive the git facts (E_VERIFY_GIT:<field>) and read backlog, cron and fix links from git at the verified tip. --backlog-dir is for tests: <name>.md
files, with cron intervals from cron-<run_date>.json beside the directory. No network: git is only read. Severity is assigned by triage.py alone.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if sys.path[:1] != [str(HERE)]:
    sys.path.insert(0, str(HERE))
try:
    import yaml
except Exception:  # a missing PyYAML means "cannot run", never a check failure
    print("E_RUN")
    sys.exit(2)

triage = None  # the rules module: engine() imports it only after the hub integrity check passed, so a tampered triage.py never runs (TRI-A-008)

BEGIN, END = "<!-- fleet-triage:begin -->", "<!-- fleet-triage:end -->"
TAMPERED, MARKERS = "E_ENGINE_TAMPERED", "E_INJECT_MARKERS"
CODE_RE = re.compile(r"E_[A-Z0-9_]{1,40}(?::[\w.-]{1,40})?", re.A)
FIX_RE = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?):?\s+#(\d+)\b", re.I)
REF_RE = re.compile(r"origin/(?:main|dreamtoosa/report-[\w.-]+)", re.A)
HUB_RULES, TIERS3 = ("C2", "C3", "U2"), ("CRITICAL", "URGENT", "HIGH")
# Reasons the engine or the routine prompt write; any other snapshot-supplied reason is shown escaped and flagged like other untrusted text.
REASONS = frozenset({"READ_ONLY", "time box", "not captured", "deep-read cap", "no completed run", "no dynamic workflow ids", "PRs not evaluable",
                     "backlog not captured", "no plan rows parsed", "shallow clone"})


class Code(Exception):
    """Stops a command with fixed codes (exit 1); the codes are its args."""


def engine():
    """Import triage.py from this file's directory on first use and return it; every function that needs the rules calls this first."""
    global triage
    if triage is None:
        import triage as loaded
        triage = loaded
    return triage


def _git(root, *args: str) -> tuple[int, str]:
    r = subprocess.run(["git", "-c", "log.showSignature=false", "-C", str(root), *args], capture_output=True, stdin=subprocess.DEVNULL,
                       encoding="utf-8", errors="replace", timeout=60)
    return r.returncode, r.stdout


def load_manifest(path: str | Path) -> dict:
    """repos.yml as a dict whose `repos` is a list of mappings with a `repo` name; ValueError for any other shape."""
    m = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(m, dict) or not isinstance(m.get("repos"), list) or not all(isinstance(x, dict) and isinstance(x.get("repo"), str) for x in m["repos"]):
        raise ValueError("manifest shape")
    return m


def enabled(manifest: dict) -> list[dict]:
    """Manifest repos that are not switched off, in manifest order."""
    return [m for m in manifest["repos"] if m.get("enabled", True)]


def repo_dir(clone_root: str | Path, repo: str) -> Path:
    """$CLONE_ROOT/<name> for an owner/name repo; ValueError when the name could leave the clone root."""
    name = repo.split("/")[-1]
    if not re.fullmatch(r"\w[\w.-]*", name, re.A):
        raise ValueError("repo name")
    return Path(clone_root) / name


def hub_dir(manifest: dict | None, clone_root: str | Path) -> Path:
    """The hub clone: $CLONE_ROOT/<name of hub.repo>, DreamToosa when the manifest does not say."""
    return repo_dir(clone_root, ((manifest or {}).get("hub") or {}).get("repo") or "x/DreamToosa")


def integrity(hub: str | Path) -> bool:
    """TRI-A-008: true only when git sees no change at all under dreamtoosa/ (a missing repo or a git failure counts as tampered)."""
    hub = Path(hub)
    if not (hub / ".git").exists():
        return False
    diff_rc = _git(hub, "diff", "--quiet", "HEAD", "--", "dreamtoosa/")[0]
    status_rc, status_out = _git(hub, "status", "--porcelain", "--", "dreamtoosa/")
    return diff_rc == 0 and status_rc == 0 and not status_out.strip()


def _same(a, b) -> bool:
    try:
        return datetime.datetime.fromisoformat(a) == datetime.datetime.fromisoformat(b)
    except (TypeError, ValueError):
        return a == b


def git_liveness(hub: str | Path, state_file: str) -> dict[str, str]:
    """{ref: last_run.date} for origin/main and every origin/dreamtoosa/report-* ref whose state file holds a string date."""
    out = _git(hub, "for-each-ref", "--format=%(refname)", "refs/remotes/origin/main", "refs/remotes/origin/dreamtoosa/report-*")[1]
    res = {}
    for full in sorted(out.split()):
        rc, txt = _git(hub, "show", f"{full}:{state_file}")
        try:
            date = (json.loads(txt).get("last_run") or {}).get("date") if rc == 0 else None
        except (ValueError, AttributeError):
            date = None
        if isinstance(date, str):
            res[full[len("refs/remotes/"):]] = date
    return res


def fix_links_from_git(d: str | Path, tip: str, run_date: str) -> list[dict]:
    """Issue numbers and commit SHAs of closes/fixes/resolves #N subjects over the 90 days before run_date (subjects are not kept)."""
    since = (datetime.date.fromisoformat(run_date[:10]) - datetime.timedelta(days=90)).isoformat() + "T00:00:00+00:00"
    rc, out = _git(d, "log", f"--since={since}", "--format=%H%x09%s", tip)
    pairs = {(int(n), h) for ln in (out.splitlines() if rc == 0 else []) for h, _, subj in [ln.partition("\t")] for n in FIX_RE.findall(subj)}
    return [{"issue": n, "sha": h} for n, h in sorted(pairs)]


def verify_git(snap: dict, clone_root: str | Path, manifest: dict | None = None) -> list[str]:
    """Re-derive tip SHA, committer dates, optional backlog blob SHA, fix links and liveness dates from git; sorted E_VERIFY_GIT:<field> codes."""
    bad: set[str] = set()
    fail = lambda f: bad.add("E_VERIFY_GIT:" + f)  # noqa: E731
    mrepo = {m["repo"]: m for m in enabled(manifest)} if manifest else {}
    for s in snap["repos"]:
        if manifest and s["repo"] not in mrepo:
            continue
        d = repo_dir(clone_root, s["repo"])
        if not (d / ".git").exists():
            fail("clone")
            continue
        rc, out = _git(d, "rev-parse", "--verify", "--quiet", "origin/HEAD^{commit}")
        if rc:
            rc, out = _git(d, "rev-parse", "--verify", "--quiet", "origin/main^{commit}")
        tip = out.strip() if rc == 0 else None
        t = s.get("tip") or {}
        if tip != t.get("sha"):
            fail("tip_sha")
        if tip is None:
            continue
        dates = _git(d, "log", "-2", "--format=%cI", tip)[1].split()
        if not _same(dates[0] if dates else None, t.get("committer_date")):
            fail("committer_date")
        if not _same(dates[1] if len(dates) > 1 else None, t.get("prev_committer_date")):
            fail("prev_committer_date")
        if s.get("backlog_blob") is not None:  # optional key: the blob the model says it read
            path = (mrepo.get(s["repo"], {}).get("backlog") or {}).get("path")
            rc, out = _git(d, "rev-parse", "--verify", "--quiet", f"{tip}:{path}") if path else (1, "")
            if rc or out.strip() != s["backlog_blob"]:
                fail("backlog_blob")
        if {(x.get("issue"), x.get("sha")) for x in s.get("fix_links") or []} != {(x["issue"], x["sha"]) for x in fix_links_from_git(d, tip, snap["run_date"])}:
            fail("fix_links")
    truth = git_liveness(hub_dir(manifest, clone_root), ((manifest or {}).get("hub") or {}).get("state_file") or "dreamtoosa/state.json")
    if any(truth.get(r.get("ref")) != r.get("last_run_date") for r in (snap.get("hub") or {}).get("liveness_refs") or []):
        fail("liveness")
    return sorted(bad)


def check_all(snap: object, manifest: dict, clone_root: str | Path | None = None) -> list[str]:
    """Every check as fixed codes ([] when valid): hub integrity first, then the schema, secret, path and cap scans, then git re-derivation."""
    if clone_root and not integrity(hub_dir(manifest, clone_root)):
        return [TAMPERED]
    if not isinstance(snap, dict):
        return ["E_SCHEMA"]
    if (snap.get("hub") or {}).get("engine_clean") is False:
        return [TAMPERED]
    codes = engine().check_snapshot(snap, manifest, str(clone_root) if clone_root else None)
    refs = (snap.get("hub") or {}).get("liveness_refs")
    if refs is not None and (not isinstance(refs, list) or not all(isinstance(r, dict) and REF_RE.fullmatch(str(r.get("ref"))) for r in refs)):
        codes = sorted({*codes, "E_SCHEMA"})  # the ref name is shown in the report, so only the two ref shapes the routine reads are allowed
    return codes if codes or not clone_root else verify_git(snap, clone_root, manifest)


def _show(d, tip: str, path) -> str | None:
    if not path or Path(path).is_absolute() or ".." in Path(path).parts:
        return None
    rc, out = _git(d, "show", f"{tip}:{path}")
    return out if rc == 0 else None


def _cron(text: str | None) -> str | None:
    found = re.findall(r"^\s*-?\s*cron:\s*['\"]([^'\"]+)['\"]", text or "", re.M)
    return found[0] if len(found) == 1 else None


def gather(snap: dict, manifest: dict, clone_root: str | Path | None = None, backlog_dir: str | Path | None = None) -> tuple[dict, dict, dict]:
    """(plan rows, fix links, cron text) per repo: from git at the snapshot tip with clone_root, from fixture files with backlog_dir, else empty."""
    engine()
    rd, rows, links, cron, jcron = snap["run_date"], {}, {}, {}, {}
    if backlog_dir and (Path(backlog_dir).parent / f"cron-{rd}.json").is_file():
        jcron = json.loads((Path(backlog_dir).parent / f"cron-{rd}.json").read_text(encoding="utf-8"))
    srepo = {r["repo"]: r for r in snap["repos"]}
    for m in enabled(manifest):
        repo, s, mp, text = m["repo"], srepo[m["repo"]], m.get("backlog") or {}, None
        if clone_root:
            d, tip = repo_dir(clone_root, repo), s["tip"]["sha"]
            text, links[repo] = _show(d, tip, mp.get("path")), fix_links_from_git(d, tip, rd)
            cron[repo] = {w["file"]: _cron(_show(d, tip, f".github/workflows/{w['file']}")) for w in m.get("watch_workflows") or [] if w.get("kind") == "security"}
        else:
            f = Path(backlog_dir or ".") / (repo.split("/")[-1].lower() + ".md")
            text, links[repo], cron[repo] = (f.read_text(encoding="utf-8") if backlog_dir and f.is_file() else None), s.get("fix_links") or [], jcron.get(repo, {})
        if text is not None and mp:
            rows[repo] = triage.parse_backlog(text, mp)
    return rows, links, cron


def assemble(snap: object, manifest: dict, clone_root: str | Path | None = None, backlog_dir: str | Path | None = None) -> tuple[list[str], str]:
    """check_all, then evaluate and render: (codes, block); the block is empty when any code is returned."""
    codes = check_all(snap, manifest, clone_root)
    if codes:
        return codes, ""
    rows, links, cron = gather(snap, manifest, clone_root, backlog_dir)
    return [], render(triage.evaluate(snap, rows, links, cron, manifest), manifest, snap)


def _days(run: str, ts) -> int:
    a, b = triage._date(run), triage._date(ts)
    return max(0, (a - b).days) if a and b else 0


def _pr(p: dict) -> str:
    n = f"#{p['number']}"
    if p["cls"] == "READY":
        return f"{n} READY, idle {p['idle_days']} d" + (f"; {p['label']}" if p["label"] else "")
    return f"{n} BLOCKED: {p['blocker']}; {p['unblock']}" if p["cls"] == "BLOCKED" else f"{n} not evaluable ({p['reason']})"


def _ci(c: dict) -> str:
    since = f"{c['streak']} consecutive failures since {c['first_red']}"
    return {"GREEN": f"green on tip (run {c['run_id']})", "GREEN_PRE_TIP": f"green, pre-tip (latest run on {c['sha7']})",
            "RED": f"red on tip, {since} (run {c['run_id']})", "RED_PRE_TIP": f"red on {c['sha7']}, not tip (unconfirmed)"}.get(c["state"])


def render(ev: triage.Evaluation, manifest: dict, snap: dict | None = None) -> str:
    """The six-section Fleet Triage block with its markers. Output depends only on the inputs (stable order); a non-public repo yields only its
    withheld line; untrusted text (tip subject, issue title and labels from `snap`) appears only as escaped code spans."""
    cfg = {**engine()._DEFAULTS, **(manifest.get("triage") or {})}
    fresh = {f["repo"]: f for f in ev.freshness}
    pubs = [r for r, f in fresh.items() if f["public"]]
    srepo = {r["repo"]: r for r in (snap or {}).get("repos") or []}
    ro, flags = ev.mode == "READ_ONLY", []
    part = lambda r: any(ev.sections[r][k]["state"] != "OK" for k in ("prs", "issues", "workflows"))  # noqa: E731 - API-backed rules did not all run
    show = lambda f: f.rule in HUB_RULES or f.repo in pubs  # noqa: E731 - hub rules carry only the heartbeat age

    def u(where: str, text) -> str:
        md, fl = triage.escape_untrusted(text)
        flags.extend(f"{where}: {x}" for x in fl)
        return re.sub(r"fleet-triage:(begin|end)", r"fleet-triage \1", md)

    def ns(st: dict, where: str = "section") -> str:
        rsn = st["reason"]
        ok = isinstance(rsn, str) and (rsn in REASONS or rsn.startswith("unknown cron shape: "))
        return "not evaluable (" + (rsn if ok else u(f"{where} reason", rsn)) + ")"

    h, top = ev.hub, (ev.shown[0] if ev.shown else None)
    beat = f"newest last_run.date is {h['age_days']} d old ({h['source_ref']})" if h["state"] == "OK" else "not evaluable (no valid last_run.date)"
    nprs = h["open_report_prs"] if h["open_report_prs"] is not None else f"not evaluable ({'READ_ONLY' if ro else 'not captured'})"
    L = [BEGIN, "## Fleet Triage", "", f"- Mode: {ev.mode}", f"- Coverage: the {len(fresh)} enabled repos in repos.yml; not account-wide.",
         f"- Security: {ev.security}", f"- Hub heartbeat: {beat}; open report PRs: {nprs}",
         "- Most important human action: " + ("none ranked" if top is None else top.action if show(top) else "withheld (rank 1 is in a non-public repo)"),
         "", "### 1. Freshness", ""]
    for r, f in fresh.items():
        s = f"- {r}: {f['tier']}, {f['age_days']} d since the tip commit"
        if r in pubs:
            s += f" (previous commit {f['prev_age_days']} d)" if f["prev_age_days"] is not None else ""
            s += f"; tip {f['tip_sha'][:7]}"
            subj = (srepo.get(r, {}).get("tip") or {}).get("subject")
            s += " " + u(f"{r} tip subject", subj) if subj is not None else ""
        else:
            n = ", ".join(f"{t} {sum(1 for x in ev.findings if x.repo == r and x.tier == t and x.rule not in HUB_RULES)}" for t in TIERS3)
            s += f"; non-public, details withheld ({n}" + ("; partial: some sections not evaluable" if part(r) else "") + ")"
        L.append(s)
    scope = ["- no public repo in scope; non-public repos are withheld"] if not pubs and not ro else []
    L += ["", "### 2. Pull requests", "", *(["- not evaluable (READ_ONLY)"] if ro else scope)]
    for r in [] if ro else pubs:
        st, rows = ev.sections[r]["prs"], [p for p in ev.prs if p["repo"] == r]
        L += [f"- {r}:", *([f"  - {_pr(p)}" for p in rows] if st["state"] == "OK" and rows else [f"  - {'no open PRs' if st['state'] == 'OK' else ns(st)}"])]
    L += ["", "### 3. CI, issues and branch hygiene", "", *(["- CI and issues: not evaluable (READ_ONLY)"] if ro else scope)]
    trusted = set(cfg["trusted_logins"])
    for r in pubs:
        secs = ev.sections[r]
        L.append(f"- {r}:")
        if not ro:
            L += [f"  - CI {c['workflow']}: {_ci(c) or ns(c, f'{r} CI')}" for c in ev.ci if c["repo"] == r]
            L.append(f"  - issues: {ns(secs['issues'])}" if secs["issues"]["state"] != "OK" else f"  - issues: external/untriaged: {ev.external[r]}")
            for i in sorted((srepo.get(r, {}).get("issues") or {}).get("open") or [], key=lambda i: i["number"]) if secs["issues"]["state"] == "OK" else []:
                lab = sorted(str(x) for x in i.get("labels") or [])
                if i.get("author") not in trusted or "status-needs-triage" in lab:
                    continue
                n = i["number"]
                if {x.lower() for x in lab} & triage._C1_LABELS:
                    L.append(f"    - #{n} (C1; see Next tasks)")
                else:
                    L.append(f"    - #{n} {u(f'{r} issue #{n} title', i.get('title'))}, labels {u(f'{r} issue #{n} labels', ', '.join(lab))}, "
                             f"open {_days(ev.run_date, i.get('created_at'))} d")
        hy = secs["hygiene"]
        L.append("  - branch hygiene (ancestry-merged only): " + (f"{hy['merged_undeleted']} merged remote branches not deleted" if hy["state"] == "OK" else ns(hy)))
    L += ["", "### 4. Next tasks", ""]
    vis = [f for f in ev.shown if show(f)]
    for n, f in enumerate(vis, 1):
        s = f"{n}. {f.tier} {f.rule} {f.repo} {f.key.split(':', 2)[2]}: {f.action}"
        if f.rule == "C1":
            s += " [category: security or data loss]"
        else:
            s += f" [evidence: {', '.join(f.evidence)}]" + (f" [tags: {', '.join(f.tags)}]" if f.tags else "") + (f" [joined: {', '.join(f.joined)}]" if f.joined else "")
        L.append(s)
    L += [] if vis else ["No ranked tasks."]
    L += [f"Withheld from this list: {len(ev.shown) - len(vis)} ranked items in non-public repos."] if len(ev.shown) > len(vis) else []
    L += [f"+{ev.more} more URGENT or HIGH not shown (caps: {cfg['max_items_total']} in total, {cfg['max_items_per_repo']} per repo)"] if ev.more else []
    cnt = f"Counted only, not listed: MEDIUM {ev.counts['MEDIUM']}, LOW {ev.counts['LOW']}" + (" (partial: some sections not evaluable)" if any(part(r) for r in fresh) else "")
    L += [cnt + ".", "", "### 5. Golden feature", "", "not in DEV-005a (DEV-005b)",
          "", "### 6. Limits and integrity", ""]
    c = ev.caps
    L += [f"- Deep-read caps per repo: {c['pr_deep_reads']} PR deep reads, {c['merged_pr_reads']} merged-PR check reads, {c['issue_reads']} issue reads; "
          f"time box {c['box_minutes']} min" + (f"; cut at {u('timebox exceeded_section', c['exceeded_section'])}" if c["exceeded_section"] else ""),
          "- Control plane validation: " + {0: "validate.py exit 0", 1: "validate.py exit 1 (C3 raised)"}.get(h["validate_exit"], "E_RUN (validate.py did not complete)"),
          "- Engine integrity: " + {True: "committed files only", False: TAMPERED}.get(h["engine_clean"], "not recorded")]
    bad: dict[str, list[str]] = {}
    for m in enabled(manifest):
        r, vis_cfg = m["repo"], m.get("visibility")
        if vis_cfg not in ("public", "private"):
            bad.setdefault("unrecognised in repos.yml", []).append(r)
        elif vis_cfg == "public" and r in fresh and r not in pubs and snap is not None:
            chk = srepo.get(r, {}).get("visibility_check") or "missing"
            bad.setdefault(f"cross-check {chk if chk != 'ok' else 'visibility differs'}", []).append(r)
    L += [f"- Visibility {k}: {', '.join(v)} (treated as non-public)" for k, v in sorted(bad.items())]
    L += [f"- {r} {k}: {ns(ev.sections[r][k])}" for r in pubs for k in ("backlog", "dependabot", "cron") if ev.sections[r][k]["state"] != "OK"]
    L += ["- Integrity flags: " + ("; ".join(sorted(set(flags))) if flags else "no suspicious text recorded"), END]
    return "\n".join(L) + "\n"


def inject(index_path: str | Path, block: str) -> None:
    """Replace only the text between the fleet-triage markers of the index (prepend the block when it has none). Raises Code(E_INJECT_MARKERS),
    writing nothing, when the block is malformed or any marker string appears outside exactly one begin/end pair."""
    body = block.strip("\n")
    if not (body.startswith(BEGIN) and body.endswith(END) and body.count(BEGIN) == body.count(END) == 1 and body.count("fleet-triage:") == 2):
        raise Code(MARKERS)
    p = Path(index_path)
    text = p.read_bytes().decode("utf-8")
    nb, ne = text.count("fleet-triage:begin"), text.count("fleet-triage:end")
    if nb == ne == 0:
        new = body + "\n\n" + text
    else:
        bs, es = text.find(BEGIN), text.find(END)
        if not (nb == ne == text.count(BEGIN) == text.count(END) == 1 and 0 <= bs < es):
            raise Code(MARKERS)
        new = text[:bs] + body + text[es + len(END):]
    p.write_bytes(new.encode("utf-8"))


def _heartbeat(a) -> int:
    root = Path(a.repo_root)
    if not (root / ".git").exists():
        raise ValueError("not a git repository")
    man = load_manifest(a.manifest or root / "dreamtoosa" / "repos.yml")
    mx = (man.get("triage") or {}).get("heartbeat_max_age_days", 3)
    if type(mx) is not int or not 1 <= mx <= 14:
        raise ValueError("heartbeat_max_age_days")
    engine()
    today = a.today or datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    refs = [{"ref": k, "last_run_date": v} for k, v in git_liveness(root, (man.get("hub") or {}).get("state_file") or "dreamtoosa/state.json").items()]
    if triage.future_dated(refs, today):
        raise Code("E_FUTURE_DATED")
    age, src = triage.hub_liveness(refs, today)
    if age is None:
        raise Code("E_NOT_EVALUABLE")
    print(f"{'OK' if age <= mx else 'E_STALE'} ref={src} age_days={age} max_days={mx}")
    return 0 if age <= mx else 1


def _run(a) -> int:
    if a.cmd == "heartbeat":
        return _heartbeat(a)
    if a.cmd == "render" and a.unavailable:
        block = f"{BEGIN}\nFleet Triage unavailable: {a.unavailable}\n{END}\n"  # a fixed code and nothing else
    else:
        man = load_manifest(a.manifest)
        try:
            snap = json.loads(Path(a.snapshot).read_text(encoding="utf-8"))
        except ValueError:
            raise Code("E_SCHEMA") from None
        codes, block = assemble(snap, man, a.clone_root, a.backlog_dir) if a.cmd == "render" else (check_all(snap, man, a.clone_root), "")
        if codes:
            raise Code(*codes)
        if a.cmd == "check":
            print("OK")
            return 0
    if a.inject:
        inject(a.inject, block)
        print("OK")
    else:
        sys.stdout.buffer.write(block.encode("utf-8"))
        sys.stdout.buffer.flush()
    return 0


def _code(s: str) -> str:
    if not CODE_RE.fullmatch(s):
        raise argparse.ArgumentTypeError("expected a fixed E_ code")
    return s


def _iso(s: str) -> str:
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", s, re.A):
            raise ValueError(s)
        datetime.date.fromisoformat(s)
    except ValueError:
        raise argparse.ArgumentTypeError("expected YYYY-MM-DD") from None
    return s


def main(argv: list[str] | None = None) -> int:
    """Run the CLI: 0 ok, 1 after printing fixed codes, 2 after printing E_RUN (the exception class name goes to stderr) or on a usage error."""
    p = argparse.ArgumentParser(prog="triage_report.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", choices=("check", "render", "heartbeat"))
    for flag in ("snapshot", "manifest", "clone-root", "backlog-dir", "inject", "repo-root"):
        p.add_argument("--" + flag)
    p.add_argument("--unavailable", type=_code)
    p.add_argument("--today", type=_iso)
    a = p.parse_args(argv)
    need = {"check": ("snapshot", "manifest"), "render": () if a.unavailable else ("snapshot", "manifest"), "heartbeat": ("repo_root",)}[a.cmd]
    if [n for n in need if not getattr(a, n)] or (a.clone_root and a.backlog_dir):
        p.error(f"missing or conflicting arguments for {a.cmd}")
    try:
        return _run(a)
    except Code as e:
        print("\n".join(e.args))
        return 1
    except Exception as e:  # noqa: BLE001 - anything else is "cannot run": a fixed code on stdout, only the class name on stderr
        print("E_RUN")
        print(type(e).__name__, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

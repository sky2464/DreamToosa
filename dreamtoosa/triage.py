"""Fleet Triage rule engine (DEV-005a/005b). Pure: no I/O, no clock, no environment. Severity is assigned only here. NOT_EVALUABLE is never rendered as zero or green."""
from __future__ import annotations
import datetime
import hashlib
import json
import re
from collections import namedtuple
from dataclasses import dataclass, field
SECURITY_LINE = "not evaluable (alert APIs not exposed via MCP)"
SELF_LABEL = "ready to merge (GitHub forbids self-approval)"
TIERS = ("CRITICAL", "URGENT", "HIGH", "MEDIUM", "LOW")
GREEN = frozenset({"success", "neutral", "skipped"})
DEEP_CAPS = {"pr_deep_reads": 5, "merged_pr_reads": 3, "issue_reads": 3}
UNBLOCK = { "DRAFT": "mark the PR ready for review", "CHECKS-RED": "fix the failing check on head {sha7}", "NO-CI": "add a CI check to the PR", "CHECKS-PENDING": "wait for the checks on head {sha7} to finish", "CONFLICT": "resolve the merge conflict with the default branch", "CHANGES-REQUESTED": "address the requested changes and request review again", "MERGEABILITY-UNKNOWN": "wait for GitHub to compute mergeability, then re-read", }
_DEFAULTS = {"max_items_total": 8, "max_items_per_repo": 3, "pr_idle_days": 7, "routine_gap_days": 2, "trusted_logins": ["sky2464", "dependabot[bot]"]}
ID_RE = re.compile(r"[A-Z]{1,5}-?[A-Z]{0,4}-?\d{1,4}[a-z]?")
WF_RE = re.compile(r"[\w.-]+\.ya?ml|\d+", re.A)
SHA_RE = re.compile(r"[0-9a-f]{40}")
SECRET_RE = re.compile(r"ghp_|github_pat_|gh[osur]_|sk-ant-|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|xox[abp]-|-----BEGIN|eyJ[\w-]+\.[\w-]+\.[\w-]+")
KW_RE = re.compile(r"data loss|delet|corrupt|leak|secret|credential|auth bypass|injection", re.I)
LOC_RE = re.compile(r"[\w./-]+\.[A-Za-z]\w{0,5}:\d+", re.A)
_C1_LABELS = frozenset({"security", "critical", "p0", "data-loss"})
_FLAGS = (("link", re.compile(r"(?i)https?://|www\.|\]\(|mailto:")), ("markup", re.compile(r"[<>]")), ("directive", re.compile(r"(?i)ignore (?:all |any |the )?(?:previous|prior|above)|system prompt|you must|assistant:|disregard")))
_ALLOWED = frozenset("""schema run_date execution_mode timebox started_epoch box_minutes exceeded_section hub validate_exit engine_clean liveness_refs ref last_run_date open_report_prs repos repo name enabled visibility visibility_check dependabot_scope tip sha committer_date prev_committer_date subject fix_links issue hygiene merged_undeleted shallow prs issues workflows status reason open closed_recent deep_reads number draft author updated_at created_at labels head_sha docs_only checks conclusion reviews login state mergeable_state merged_at changed_non_docs title closed_by_pr runs workflow kind event run_id dynamic_ids backlog_blob""".split())
_VALID = {**dict.fromkeys(("number", "issue", "run_id", "deep_reads", "merged_undeleted", "started_epoch", "box_minutes", "validate_exit", "open_report_prs"), lambda v: type(v) is int), **dict.fromkeys(("sha", "head_sha", "backlog_blob"), lambda v: isinstance(v, str) and bool(SHA_RE.fullmatch(v))), **dict.fromkeys(("committer_date", "prev_committer_date", "created_at", "updated_at", "merged_at", "run_date"), lambda v: _date(v) is not None), "workflow": lambda v: isinstance(v, str) and bool(WF_RE.fullmatch(v)), "repo": lambda v: isinstance(v, str) and bool(re.fullmatch(r"[\w.-]+/[\w.-]+", v, re.A)), "schema": lambda v: v == "fleet-triage/1", "execution_mode": lambda v: v in ("READ_WRITE", "READ_ONLY")}
@dataclass(frozen=True)
class PlanRow:
    id: str; title: str; priority: str | None; status: str | None; section: str; line: int; text: str; p0: bool; done: bool  # noqa: E702
@dataclass
class Finding:
    rule: str; key: str; repo: str; tier: str; impact: int; confidence: int; age_days: int; action: str  # noqa: E702
    evidence: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    joined: list = field(default_factory=list)
@dataclass
class Evaluation:
    mode: str; run_date: str; security: str; top_action: str | None; more: int; counts: dict; external: dict; hub: dict  # noqa: E702
    freshness: list; sections: dict; prs: list; ci: list; findings: list; shown: list; caps: dict  # noqa: E702
def escape_untrusted(text) -> tuple[str, list[str]]:
    """Render untrusted text as one inline-code span (collapsed, 80 chars max, no links); returns (markdown, integrity flags)."""
    s = re.sub(r"[\s\x00-\x1f\x7f]+", " ", str(text if text is not None else "")).strip()
    flags = [n for n, rx in _FLAGS if rx.search(s)]
    if len(s) > 80:
        s, flags = s[:80], flags + ["truncated"]
    return "`" + (s.replace("`", "'").replace("|", "/") or "-") + "`", sorted(flags)
def _date(v):
    """Date from the YYYY-MM-DD prefix of an ISO string, as written (no timezone math); None when invalid."""
    if isinstance(v, datetime.date):
        return v
    if isinstance(v, str) and re.match(r"\d{4}-\d{2}-\d{2}(?:$|[T ])", v, re.A):
        try:
            return datetime.date.fromisoformat(v[:10])
        except ValueError:
            return None
    return None
def _age(run, ts) -> int:
    d = _date(ts)
    return max(0, (run - d).days) if d else 0
def hub_liveness(refs, run_date) -> tuple[int | None, str | None]:
    """Whole-day age and ref of the newest valid last_run.date (ignores invalid and later than run_date + 1); ties pick the smallest ref."""
    run, hi = _date(run_date), _date(run_date) + datetime.timedelta(days=1)
    ok = [(d, r["ref"]) for r in refs or [] if isinstance(r, dict) and isinstance(r.get("ref"), str) and (d := _date(r.get("last_run_date"))) and d <= hi]
    if not ok:
        return None, None
    d, ref = min(ok, key=lambda t: (-t[0].toordinal(), t[1]))
    return max(0, (run - d).days), ref
def future_dated(refs, run_date) -> bool:
    """True when any ref carries a valid last_run.date later than run_date + 1 (heartbeat E_FUTURE_DATED)."""
    hi = _date(run_date) + datetime.timedelta(days=1)
    return any((d := _date(r.get("last_run_date"))) and d > hi for r in refs or [] if isinstance(r, dict))
def _tok(s, t) -> bool:
    return re.search(rf"(?<![\w-]){re.escape(t)}(?![\w-])", s or "") is not None
def check_snapshot(snap, manifest, clone_root=None) -> list[str]:
    """Allowlist, typed-field, secret, path and deep-read-cap checks; returns sorted fixed codes ([] when valid)."""
    bad = set()
    def walk(o, key=None):
        if isinstance(o, dict):
            for k, v in o.items():
                if str(k).lower() == "severity":
                    bad.add("E_SEVERITY_KEY")
                elif k not in _ALLOWED:
                    bad.add("E_SCHEMA")
                walk(v, k)
        elif isinstance(o, list):
            for v in o:
                walk(v, key)
        elif o is not None:
            if isinstance(o, str):
                if SECRET_RE.search(o):
                    bad.add("E_SECRET")
                if o.startswith(("/", "~/")) or re.match(r"[A-Za-z]:[\\/]", o) or (clone_root and str(clone_root) in o):
                    bad.add("E_ABS_PATH")
            if key in _VALID and not _VALID[key](o):
                bad.add("E_SCHEMA")
    try:
        walk(snap)
        bad.update("E_SCHEMA" for k in ("schema", "run_date", "execution_mode", "hub", "repos") if k not in snap)
        have = {r["repo"] for r in snap["repos"]}
        bad.update("E_SCHEMA" for m in manifest["repos"] if m.get("enabled", True) and m["repo"] not in have)
        box = (manifest.get("budget") or {}).get("soft_time_box_minutes_fleet_triage")
        if box and (snap.get("timebox") or {}).get("box_minutes", 0) > box:
            bad.add("E_CAP:time_box")
        for r in snap["repos"]:
            p, i = r.get("prs") or {}, r.get("issues") or {}
            reads = sum(not x.get("draft") and x.get("checks") is not None for x in p.get("open") or [])
            if (p.get("deep_reads") or 0) > DEEP_CAPS["pr_deep_reads"] or reads > DEEP_CAPS["pr_deep_reads"]:
                bad.add("E_CAP:pr_deep_reads")
            if sum(x.get("checks") is not None for x in p.get("closed_recent") or []) > DEEP_CAPS["merged_pr_reads"]:
                bad.add("E_CAP:merged_pr_reads")
            if sum(x.get("closed_by_pr") is not None for x in i.get("open") or []) > DEEP_CAPS["issue_reads"]:
                bad.add("E_CAP:issue_reads")
    except (AttributeError, KeyError, TypeError, ValueError):
        bad.add("E_SCHEMA")
    return sorted(bad)
def parse_backlog(text, mapping) -> list[PlanRow]:
    """Parse the tables whose header has every mapping.header_all name into PlanRow items (pure; mapping is not mutated)."""
    cols, need = mapping.get("columns") or {}, set(mapping.get("header_all") or [])
    p0, done, dsec = mapping.get("p0_values") or [], mapping.get("done_values") or [], mapping.get("done_sections") or []
    rows, section, st, hdr = [], "", 0, []  # st: 0 outside, 1 header seen, 2 data rows, 3 table skipped
    for n, raw in enumerate(text.split("\n"), 1):
        ln = raw.strip()
        if not ln.startswith("|"):
            st = 0
            if ln.startswith("#"):
                section = ln.lstrip("#").strip()
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if st == 2:
            cell = dict(zip(hdr, cells + [""] * (len(hdr) - len(cells))))
            get = lambda k: (cell.get(cols[k]) or None) if cols.get(k) else None  # noqa: E731
            if not ID_RE.fullmatch(get("id") or ""):
                continue
            pri, sta = get("priority"), get("status")
            isdone = sta in done or any(d.lower() in section.lower() for d in dsec)
            rows.append(PlanRow(get("id"), get("title") or "", pri, sta, section, n, ln, pri in p0, isdone))
        elif st == 1 and all(re.fullmatch(r":?-+:?", c) for c in cells):
            st = 2 if need <= set(hdr) else 3
        elif st != 3:
            st, hdr = 1, cells
    return rows
def _interval(cron) -> int | None:
    f = cron.split() if isinstance(cron, str) else []
    if len(f) == 5 and f[0].isdigit() and f[1].isdigit() and f[2] == f[3] == "*":
        return 1 if f[4] == "*" else 7 if re.fullmatch(r"[0-7]", f[4]) else None
    return None
def _st(reason=None) -> dict:
    return {"state": "OK" if reason is None else "NOT_EVALUABLE", "reason": reason}
def _section(rs, name, ro) -> dict:
    s = rs.get(name) or {}
    return _st("READ_ONLY") if ro else _st() if s.get("status") == "ok" else _st(s.get("reason") or "not captured")
def _rk(r):
    return (str(r.get("created_at")), r.get("run_id") or 0)
def _done(runs) -> list:
    return sorted((r for r in runs if r.get("conclusion") is not None and not str(r.get("event")).startswith("pull_request")), key=_rk, reverse=True)
def _red(runs, i=0) -> list:
    out = []
    while i < len(runs) and runs[i]["conclusion"] not in GREEN:
        out.append(runs[i])
        i += 1
    return out
def _ci(runs, tip) -> dict:
    """Newest completed push/schedule run (the tip's when one exists) and its consecutive-failure streak."""
    done = _done(runs)
    if not done:
        return {"state": "NOT_EVALUABLE", "reason": "no completed run", "streak": 0, "first_red": None, "run_id": None, "run_ids": [], "sha7": None}
    cur = next((r for r in done if r.get("head_sha") == tip), done[0])
    red = _red(done, done.index(cur))
    pre = "" if tip is None or cur.get("head_sha") == tip else "_PRE_TIP"
    return {"state": ("RED" if red else "GREEN") + pre, "reason": None, "streak": len(red), "first_red": str(red[-1].get("created_at"))[:10] if red else None, "run_id": cur.get("run_id"), "run_ids": [r["run_id"] for r in red if r.get("run_id") is not None], "sha7": str(cur.get("head_sha"))[:7]}
def _classify(p) -> tuple[str, str | None]:
    """(class, blocker) of one open PR; blockers are tested in the TRI-A-014 order and exactly one is returned."""
    ck = p.get("checks")
    if p.get("draft"):
        return "BLOCKED", "DRAFT"
    if ck is None:
        return "NOT_EVALUABLE", None
    concl, last, ms = [c.get("conclusion") for c in ck], {}, p.get("mergeable_state")
    for r in p.get("reviews") or []:
        if r.get("state") in ("CHANGES_REQUESTED", "APPROVED", "DISMISSED"):
            last[r.get("login")] = r["state"]
    for blk, hit in (("CHECKS-RED", any(c is not None and c not in GREEN for c in concl)), ("NO-CI", not concl), ("CHECKS-PENDING", None in concl), ("CONFLICT", ms == "dirty"), ("CHANGES-REQUESTED", "CHANGES_REQUESTED" in last.values()), ("MERGEABILITY-UNKNOWN", ms in (None, "unknown"))):
        if hit:
            return "BLOCKED", blk
    return "READY", None
def _mk(rule, repo, sub, tier, imp, conf, age, action, evid, tags=()) -> Finding:
    evid, tags = sorted(set(evid)), set(tags)
    if tier in TIERS[:3] and not evid:  # evidence gate: HIGH or above needs an artifact
        tier, tags = "MEDIUM", tags | {"gated"}
    return Finding(rule, f"{rule}:{repo}:{sub}", repo, tier, imp, conf, age, action, evid, sorted(tags), [])
def evaluate(snap, plan_rows, fix_links, cron, manifest) -> Evaluation:
    """Turn facts into ranked findings and typed section states. Deterministic under any input order; inputs are never mutated."""
    rd, cfg = snap["run_date"], {**_DEFAULTS, **(manifest.get("triage") or {})}
    run, dflt = _date(rd), manifest.get("defaults") or {}
    hubm, shub = manifest.get("hub") or {}, snap.get("hub") or {}
    stale, dormant = dflt.get("stale_after_days", 14), dflt.get("dormant_after_days", 45)
    ro = snap.get("execution_mode") == "READ_ONLY" or hubm.get("force_read_only") is True
    trusted = set(cfg["trusted_logins"])
    order = {m["repo"]: i for i, m in enumerate(manifest["repos"])}
    srepo = {r["repo"]: r for r in snap["repos"]}
    uniq, meta, fresh, secs, prrows, cirows, ext = {}, {}, [], {}, [], [], {}
    def add(rule, repo, sub, tier, imp, conf, age, action, evid, tags=(), mt=("-",)):
        f = _mk(rule, repo, sub, tier, imp, conf, age, action, evid, tags)
        if f.key not in uniq:
            uniq[f.key], meta[f.key] = f, mt
    for m in manifest["repos"]:
        repo, rs = m["repo"], srepo.get(m["repo"])
        if not m.get("enabled", True) or rs is None:
            continue
        tip, owner, path = rs["tip"], repo.split("/")[0], (m.get("backlog") or {}).get("path", "")
        age = _age(run, tip.get("committer_date"))
        public = m.get("visibility") == "public" and rs.get("visibility") == "public" and rs.get("visibility_check") == "ok"
        fresh.append({"repo": repo, "tier": "ACTIVE" if age <= 7 else "QUIET" if age <= stale else "STALE" if age < dormant else "DORMANT", "age_days": age, "prev_age_days": _age(run, tip.get("prev_committer_date")) if tip.get("prev_committer_date") else None, "tip_sha": tip["sha"], "public": public})
        S = {n: _section(rs, n, ro) for n in ("prs", "issues", "workflows")}
        ok = lambda n: S[n]["state"] == "OK"  # noqa: E731
        pw, ww = m.get("product_workflows") or [], m.get("watch_workflows") or []
        scope = m.get("dependabot_scope") or rs.get("dependabot_scope") or "unknown"
        prl = (rs["prs"].get("open") or []) if ok("prs") else []
        runs = (rs["workflows"].get("runs") or []) if ok("workflows") else []
        untr = lambda x: x.get("author") not in trusted or "status-needs-triage" in (x.get("labels") or [])  # noqa: E731
        iss = sorted((rs["issues"].get("open") or []) if ok("issues") else [], key=lambda i: i["number"])
        ext[repo] = sum(map(untr, iss)) + sum(p.get("author") not in trusted for p in prl) if ok("issues") else None
        for p in sorted(prl, key=lambda p: p["number"]):  # pull requests: classes, U3, C1(b)
            cls, blk = _classify(p)
            n, idle, sha7 = p["number"], _age(run, p.get("updated_at")), str(p.get("head_sha"))[:7]
            prrows.append({"repo": repo, "number": n, "cls": cls, "blocker": blk, "unblock": UNBLOCK[blk].format(sha7=sha7) if blk else None, "label": SELF_LABEL if cls == "READY" and p.get("author") == owner else None, "reason": "deep-read cap" if cls == "NOT_EVALUABLE" else None, "idle_days": idle})
            if cls == "READY" and idle > cfg["pr_idle_days"]:
                add("U3", repo, f"#{n}", "URGENT", 2, 3, idle, f"Decide on PR #{n} in {repo} (ready, idle {idle} d)", [f"pr:{n}"])
            pa = _age(run, p.get("created_at"))
            if (p.get("author") == "dependabot[bot]" and "dependabot[bot]" in trusted and "security" in [x.lower() for x in p.get("labels") or []] and scope in ("runtime", "unknown") and pa > 3):
                add("C1", repo, f"#{n}", "CRITICAL", 5, 3, pa, f"Review Dependabot PR #{n} in {repo} (owner decision)", [f"pr:{n}"])
        fx = {(l["issue"], l["sha"]) for l in fix_links.get(repo) or [] if isinstance(l.get("issue"), int) and SHA_RE.fullmatch(str(l.get("sha")))}
        tr_iss = [i for i in iss if not untr(i)]
        for i in tr_iss:  # trusted issues: C1(a), U4, H5
            n, lab, ia, mt = i["number"], {x.lower() for x in i.get("labels") or []}, _age(run, i.get("created_at")), ("I", i["number"], i.get("title"))
            if lab & _C1_LABELS:
                add("C1", repo, f"#{n}", "CRITICAL", 5, 3, ia, f"Triage issue #{n} in {repo}", [f"issue:{n}"], mt=mt)
            elif "release-blocker" in lab:  # a P0 label is already C1
                add("U4", repo, f"#{n}", "URGENT", 4, 3, ia, f"Resolve release-blocker issue #{n} in {repo}", [f"issue:{n}"], mt=mt)
            if "bug" in lab and "chore" not in lab and ia > 14:
                sha = min((s for k, s in fx if k == n), default=None)
                cb = i.get("closed_by_pr")
                merged = min((c["number"] for c in cb or [] if c.get("merged_at")), default=None)
                if sha:
                    add("H5", repo, f"#{n}", "LOW", 4, 3, ia, f"Close candidate #{n}: fix {sha[:7]} on default branch", [f"issue:{n}", f"commit:{sha[:7]}"], ["close-candidate"], mt)
                elif merged is not None:
                    add("H5", repo, f"#{n}", "LOW", 4, 3, ia, f"Close candidate #{n}: fix in merged PR #{merged} on default branch", [f"issue:{n}", f"pr:{merged}"], ["close-candidate"], mt)
                else:
                    add("H5", repo, f"#{n}", "HIGH", 4, 3, ia, f"Triage bug #{n} in {repo} (open {ia} d)", [f"issue:{n}"], ["fix-link-unverified"] if cb else [], mt)
        for wf in pw:  # product workflows: ci rows, U1, H3
            c = _ci([r for r in runs if r.get("workflow") == wf], tip["sha"]) if ok("workflows") else { "state": "NOT_EVALUABLE", "reason": S["workflows"]["reason"], "streak": 0, "first_red": None, "run_id": None, "run_ids": [], "sha7": None}
            cirows.append({"repo": repo, "workflow": wf, **c})
            red_days, evid = _age(run, c["first_red"]) if c["first_red"] else 0, [f"run:{x}" for x in c["run_ids"]]
            if c["state"] == "RED" and (c["streak"] >= 2 or red_days >= 3):
                add("U1", repo, wf, "URGENT", 3, 3, red_days, f"{repo}: {wf} red on tip for {c['streak']} runs since {c['first_red']}" + ("; require this check on main" if red_days > 14 else ""), evid, mt=("T", [wf], ""))
            if c["state"] == "RED_PRE_TIP":
                add("H3", repo, wf, "HIGH", 3, 1, 0, f"{repo}: {wf} red on {c['sha7']}, not tip; dispatch to confirm (owner)", [f"run:{c['run_id']}"] if c["run_id"] is not None else [], ["unconfirmed"], ("T", [wf], ""))
        bad_cron = []
        for w in ww:  # watch workflows: H1, H7
            wf, kind = w["file"], w.get("kind")
            iv = _interval((cron.get(repo) or {}).get(wf)) if kind == "security" else None
            if kind == "security" and iv is None:
                bad_cron.append(wf)
            if not ok("workflows"):
                continue
            wr = [r for r in runs if r.get("workflow") == wf]
            c = _ci(wr, None)
            if c["streak"] >= 3:
                add("H1", repo, wf, "HIGH", 3, 3, _age(run, c["first_red"]), f"{repo}: {wf} failing on push for {c['streak']} runs", [f"run:{x}" for x in c["run_ids"]], mt=("T", [wf], ""))
            if iv and wr:
                last = max(wr, key=_rk)
                silent = _age(run, last.get("created_at"))
                if silent > 2 * iv:
                    add("H7", repo, wf, "HIGH", 3, 3, silent, f"{repo}: {wf} silent {silent} d (interval {iv} d)", [f"run:{last['run_id']}"] if last.get("run_id") is not None else [], mt=("T", [wf], ""))
        ids = {str(x) for x in rs["workflows"].get("dynamic_ids") or []} if ok("workflows") else set()
        dep = S["workflows"] if not ok("workflows") else _st("no dynamic workflow ids") if not ids else _st("PRs not evaluable") if not ok("prs") else _st()
        if dep["state"] == "OK":  # H6
            st = _red(_done([r for r in runs if r.get("kind") == "dependabot" and str(r.get("workflow")) in ids]))
            if len(st) >= 3 and not any(p.get("author") == "dependabot[bot]" for p in prl):
                add("H6", repo, "dependabot-updates", "MEDIUM" if scope == "dev" else "HIGH", 2, 3, 0, f"{repo}: Dependabot updates failing {len(st)} runs; check the update configuration", [f"run:{r['run_id']}" for r in st if r.get("run_id") is not None])
        if ok("prs") and pw:  # H2: merged in the last 14 days without a green check, once per repo and workflow
            hits = sorted((c["number"], _age(run, c["merged_at"])) for c in rs["prs"].get("closed_recent") or [] if c.get("merged_at") and _age(run, c["merged_at"]) <= 14 and c.get("checks") is not None and c.get("changed_non_docs") and (not c["checks"] or any(k.get("conclusion") is not None and k["conclusion"] not in GREEN for k in c["checks"])))
            if hits:
                add("H2", repo, pw[0], "HIGH", 3, 3, max(a for _, a in hits), "Gate bypass: PRs " + ", ".join(f"#{n}" for n, _ in hits) + " merged without a green check", [f"pr:{n}" for n, _ in hits], mt=("T", [pw[0]], ""))
        rows = plan_rows.get(repo) or []
        for r in sorted(rows, key=lambda r: (r.line, r.id)):  # plan rows: C1(c), H4 (first duplicate wins)
            if not r.p0 or r.done:
                continue
            kw, loc = KW_RE.search(r.text), LOC_RE.search(r.text)
            tracked = any(_tok(i.get("title"), r.id) or _tok(r.text, f"#{i['number']}") for i in tr_iss)
            tg = ["verify"] + (["untracked"] if ok("issues") and not tracked else [])
            mt, evid = ("T", [r.id], r.text), [f"plan:{path}:{r.line}"]
            if kw and loc:
                add("C1", repo, r.id, "CRITICAL", 5, 2, 0, f"{r.id}: fix and add a regression test", evid, tg, mt)
            else:
                add("H4", repo, r.id, "HIGH" if loc else "MEDIUM", 4, 2, 0, f"{r.id}: fix and add a test (verify)", evid, tg + ([] if loc else ["gated"]), mt)
        h = rs.get("hygiene") or {}
        hyg = _st("not captured") if not h else _st("shallow clone") if h.get("shallow") else _st()
        hyg |= {"merged_undeleted": h.get("merged_undeleted") if hyg["state"] == "OK" else None, "label": "ancestry-merged only"}
        secs[repo] = {**S, "backlog": _st() if rows else _st("backlog not captured" if repo not in plan_rows else "no plan rows parsed"), "dependabot": dep, "cron": _st("unknown cron shape: " + ", ".join(sorted(bad_cron))) if bad_cron else _st(), "hygiene": hyg}
    for f in [f for f in uniq.values() if meta[f.key][0] == "I" and "close-candidate" not in f.tags]:  # issue joins (TRI-A-019)
        _, n, title = meta[f.key]
        cand = [t for t in uniq.values() if t.repo == f.repo and meta[t.key][0] == "T" and TIERS.index(f.tier) >= TIERS.index(t.tier) and (any(_tok(title, x) for x in meta[t.key][1]) or _tok(meta[t.key][2], f"#{n}"))]
        if cand:
            t = min(cand, key=lambda t: (TIERS.index(t.tier), t.key))
            t.evidence, t.joined = sorted({*t.evidence, *f.evidence}), sorted({*t.joined, f.key})
            del uniq[f.key]
    age, src = hub_liveness(shub.get("liveness_refs"), rd)  # hub rules: C2, C3, U2
    hr, nprs, cap = hubm.get("repo", ""), None if ro else shub.get("open_report_prs"), hubm.get("max_unmerged_report_prs", 3)
    if age is not None and age > 7:
        add("C2", hr, "liveness", "CRITICAL", 3, 3, age, f"Dream Report dark {age} d: check the routine run log and re-authorize GitHub", [f"state:{src}"])
    if shub.get("validate_exit") == 1:
        add("C3", hr, "validate", "CRITICAL", 3, 3, 0, "Control plane invalid: run validate.py and fix the reported check", ["state:validate_exit"])
    by_count = nprs is not None and nprs >= cap
    if (age is not None and cfg["routine_gap_days"] < age <= 7) or by_count:
        add("U2", hr, "hub", "URGENT", 3, 3, age or 0, f"Hub degraded: heartbeat {f'{age} d' if age is not None else 'not evaluable'}; " + (f"{nprs} open report PRs" if nprs is not None else "open report PRs not evaluable"), ([f"state:{src}"] if age is not None else []) + (["state:open_report_prs"] if by_count else []))
    fl = sorted(uniq.values(), key=lambda f: (TIERS.index(f.tier), -f.impact, -f.confidence, -f.age_days, order.get(f.repo, len(order)), f.key))
    shown, per, more = [], {}, 0
    for f in fl:
        if f.tier == "CRITICAL":
            shown.append(f)
        elif f.tier in ("URGENT", "HIGH"):
            if sum(x.tier != "CRITICAL" for x in shown) < cfg["max_items_total"] and per.get(f.repo, 0) < cfg["max_items_per_repo"]:
                shown.append(f)
                per[f.repo] = per.get(f.repo, 0) + 1
            else:
                more += 1
    tb = snap.get("timebox") or {}
    return Evaluation( mode="READ_ONLY" if ro else "READ_WRITE", run_date=rd, security=SECURITY_LINE, top_action=shown[0].action if shown else None, more=more, counts={t: sum(f.tier == t for f in fl) for t in TIERS}, external=ext, hub={"age_days": age, "source_ref": src, "state": "OK" if age is not None else "NOT_EVALUABLE", "open_report_prs": nprs, "validate_exit": shub.get("validate_exit"), "engine_clean": shub.get("engine_clean")}, freshness=fresh, sections=secs, prs=prrows, ci=cirows, findings=fl, shown=shown, caps={**DEEP_CAPS, "box_minutes": tb.get("box_minutes"), "exceeded_section": tb.get("exceeded_section")})
_FID = re.compile(r"^(?:P-[0-9a-f]{12}|[CUH][1-7]:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+:[A-Za-z0-9_.#/-]{1,80})$")
_PID = re.compile(r"^(?:P-[0-9a-f]{12}|[A-Z]{2,5}-[0-9]+)$")
_LSCH, _FSTAT, _GSTAT = "fleet-triage-ledger/v1", frozenset({"OPEN", "PENDING"}), frozenset({"OPEN", "NONE"})
_FKEYS, _GKEYS = frozenset({"first_seen", "id", "last_seen", "misses", "rule", "sev", "status"}), frozenset({"id", "since", "status"})
_ELIG, _HOT = frozenset({"todo", "planned", "ready"}), frozenset({"CRITICAL", "URGENT"})
def opaque_key(canonical): return "P-" + hashlib.sha256(str(canonical).encode()).hexdigest()[:12]
def _ymd(s):
    d = _date(s); return isinstance(s, str) and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", s, re.A)) and d is not None and s == d.isoformat()
def _gv(o, k, default=None): return o.get(k, default) if isinstance(o, dict) else getattr(o, k, default)
def _fid(f):
    raw, pub = _gv(f, "id", _gv(f, "key")), _gv(f, "public", False) is True
    return (raw if pub else opaque_key(raw)), _gv(f, "rule"), _gv(f, "sev", _gv(f, "tier"))
LedgerError = namedtuple("LedgerError", "code field", defaults=("",))
Ledger = namedtuple("Ledger", "schema run_date findings golden")
Golden = namedtuple("Golden", "line pick_id score terms runner_up low_confidence unvalidated empty by_repo")
Notify = namedtuple("Notify", "send reasons")
def _ng(): return {"id": None, "since": None, "status": "NONE"}
def serialize_ledger(ledger) -> str:
    """Sorted-key comment. `--` is written as `-\\u002d` so the comment cannot close early."""
    body = {"findings": sorted(({k: f[k] for k in sorted(_FKEYS)} for f in ledger.findings), key=lambda f: f["id"]), "golden": {k: ledger.golden[k] for k in sorted(_GKEYS)}, "run_date": ledger.run_date, "schema": ledger.schema}
    return "<!-- fleet-triage-ledger:v1 " + json.dumps(body, sort_keys=True, separators=(",", ":")).replace("--", "-\\u002d") + " -->"
def _row_ok(f):
    return isinstance(f, dict) and set(f) == _FKEYS and _FID.fullmatch(str(f.get("id") or "")) and f.get("status") in _FSTAT and f.get("sev") in TIERS and bool(re.fullmatch(r"[CUH][1-7]", str(f.get("rule") or ""))) and type(f.get("misses")) is int and _ymd(f.get("first_seen")) and _ymd(f.get("last_seen"))
def parse_ledger(block_text):
    """Ledger or LedgerError. BASELINE is a pre-ledger index. Malformed input returns a code and does not raise."""
    text = block_text or ""
    nb, ne = text.count("<!-- fleet-triage:begin -->"), text.count("<!-- fleet-triage:end -->")
    led, b, e = list(re.finditer(r"<!-- fleet-triage-ledger:v1 ", text)), text.find("<!-- fleet-triage:begin -->"), text.find("<!-- fleet-triage:end -->")
    if nb == ne == 0 and not led: return LedgerError("BASELINE")
    if nb != 1 or ne != 1 or b > e: return LedgerError("E_LEDGER_MARKERS" if nb != ne or nb == 0 else "E_LEDGER_DUP")
    if len(led) != 1: return LedgerError("BASELINE" if not led else "E_LEDGER_DUP")
    if not (b < led[0].start() < e): return LedgerError("E_LEDGER_MARKERS")
    end = text[led[0].end():].find("-->")
    if end < 0: return LedgerError("E_LEDGER_SCHEMA")
    payload = text[led[0].end():][:end].strip().replace("-\\u002d", "--")
    if SECRET_RE.search(payload): return LedgerError("E_SECRET_PATTERN", "ledger")
    if "-->" in payload or "fleet-triage:" in payload: return LedgerError("E_LEDGER_SCHEMA")
    try: obj = json.loads(payload)
    except json.JSONDecodeError: return LedgerError("E_LEDGER_SCHEMA")
    g, rows = (obj or {}).get("golden"), (obj or {}).get("findings")
    bad = (not isinstance(obj, dict) or set(obj) != {"schema", "run_date", "findings", "golden"} or obj.get("schema") != _LSCH or not _ymd(obj.get("run_date")) or not isinstance(g, dict) or set(g) != _GKEYS or g.get("status") not in _GSTAT or not isinstance(rows, list) or not all(_row_ok(f) for f in rows))
    if not bad and g.get("id") is None: bad = g.get("status") != "NONE" or g.get("since") is not None
    if not bad and g.get("id") is not None: bad = not (isinstance(g.get("id"), str) and _PID.fullmatch(g["id"]) and _ymd(g.get("since")))
    if bad: return LedgerError("E_LEDGER_SCHEMA")
    return Ledger(obj["schema"], obj["run_date"], [{k: f[k] for k in _FKEYS} for f in rows], {k: g[k] for k in _GKEYS})
def merge_ledger(findings, not_evaluable_rules, prev_ledger, run_date, resolutions=()):
    """(deltas, ledger). RESOLVED ids are not stored. A NOT_EVALUABLE rule is copied and is not a miss."""
    rules, res_in = (set(not_evaluable_rules.get("rules") or ()), tuple(not_evaluable_rules.get("resolutions") or resolutions)) if isinstance(not_evaluable_rules, dict) else (set(not_evaluable_rules or ()), tuple(resolutions or ()))
    prev, golden = ({f["id"]: f for f in prev_ledger.findings}, dict(prev_ledger.golden)) if isinstance(prev_ledger, Ledger) else ({}, _ng())
    res, cur, deltas, rows = {r.get("id"): r for r in res_in if isinstance(r, dict)}, {}, [], []
    for f in findings or ():
        fid, rule, sev = _fid(f)
        if fid and rule and sev: cur[fid] = {"id": fid, "rule": rule, "sev": sev}
    for fid, f in sorted(cur.items()):
        old = prev.get(fid)
        if old is None:
            deltas.append({"id": fid, "delta": "NEW", "sev": f["sev"], "rule": f["rule"]}); rows.append({**f, "first_seen": run_date, "last_seen": run_date, "misses": 0, "status": "OPEN"}); continue
        kind = "CARRIED" if f["sev"] == old["sev"] else "ESCALATED" if TIERS.index(f["sev"]) < TIERS.index(old["sev"]) else "DOWNGRADED"
        deltas.append({"id": fid, "delta": kind, "sev": f["sev"], "rule": f["rule"], "prior_sev": old["sev"]}); rows.append({**f, "first_seen": old["first_seen"], "last_seen": run_date, "misses": 0, "status": "OPEN"})
    for fid, old in sorted(prev.items()):
        if fid in cur: continue
        if old["rule"] in rules:
            rows.append(dict(old)); deltas.append({"id": fid, "delta": "CARRIED", "sev": old["sev"], "rule": old["rule"], "not_evaluable": True}); continue
        if (res.get(fid) or {}).get("covers_first_seen") is True:
            deltas.append({"id": fid, "delta": "RESOLVED", "sev": old["sev"], "rule": old["rule"], "by": "evidence"}); continue
        misses = int(old["misses"]) + 1
        if misses >= 2: deltas.append({"id": fid, "delta": "RESOLVED", "sev": old["sev"], "rule": old["rule"], "by": "two-miss"}); continue
        rows.append({**old, "misses": misses, "status": "PENDING"}); deltas.append({"id": fid, "delta": "PENDING", "sev": old["sev"], "rule": old["rule"], "misses": misses, "text": f"Pending resolution (miss {misses}/2)"})
    return deltas, Ledger(_LSCH, run_date, rows, golden)
def _norm_status(s):
    t = re.sub(r"^[^\w]+", "", str(s or "").strip(), flags=re.UNICODE); return (t.split(" ", 1)[0] if t else "").casefold()
def _cells(line): return [c.strip() for c in line.strip().strip("|").split("|")]
def released_ids(changelog):
    """Plan IDs under a released changelog heading. Unreleased text does not exclude."""
    ids, on = set(), False
    for line in (changelog or "").splitlines():
        on = "unreleased" not in line.casefold() if line.startswith("## ") else on
        if on and not line.startswith("## "): ids.update(re.findall(r"\b[A-Z]{2,5}-\d+\b", line))
    return ids
def _excluded_ids(text):
    ids, on = set(), False
    for raw in text.splitlines():
        ln = raw.strip()
        if ln.startswith("#"): on = bool(re.search(r"(?i)\b(completed|shipped)\b", ln)); continue
        if on and ln.startswith("|") and not re.fullmatch(r"\|?[\s:|-]+\|?", ln): ids.update(c for c in _cells(ln) if _PID.fullmatch(c))
    return ids
def _col(header, cells, *names):
    for name in names:
        i = next((n for n, h in enumerate(header) if h.casefold() == name), None)
        if i is not None and i < len(cells): return cells[i]
    return None
def golden_pool(texts, manifest, exclude=(), changelogs=None):
    """Feature rows in Active Cycle or Backlog with status Todo, Planned or Ready. Non-public rows are opaque and untitled."""
    exclude, changelogs, order, pool = set(exclude or ()), changelogs or {}, {m["repo"]: i for i, m in enumerate(manifest.get("repos") or [])}, []
    for m in manifest.get("repos") or []:
        if not m.get("enabled", True) or m["repo"] not in texts: continue
        text, repo, path = texts[m["repo"]] or "", m["repo"], (m.get("backlog") or {}).get("path") or ""
        ban, pub, section, header, st, statuses = _excluded_ids(text) | released_ids(changelogs.get(repo, "")) | exclude, m.get("visibility") == "public", "", [], 0, {}
        for n, raw in enumerate(text.split("\n"), 1):
            ln = raw.strip()
            if not ln.startswith("|"):
                st = 0
                section = ln.lstrip("#").strip() if ln.startswith("#") else section
                continue
            cells = _cells(ln)
            if st == 1 and all(re.fullmatch(r":?-+:?", c) for c in cells): st = 2; continue
            if st != 2: header, st = cells, 1; continue
            rid, sec, kind = _col(header, cells, "id"), section.casefold(), _col(header, cells, "type")
            if rid: statuses[rid] = _norm_status(_col(header, cells, "status"))
            if not kind or kind.casefold() != "feature" or sec not in ("active cycle", "backlog") or not rid or not _PID.fullmatch(rid) or rid in ban or statuses.get(rid) not in _ELIG: continue
            pool.append({"repo": repo, "id": rid, "display_id": rid if pub else opaque_key(rid), "title": (_col(header, cells, "title") or "") if pub else "", "priority": _col(header, cells, "priority"), "status": _col(header, cells, "status"), "section": section if pub else "", "line": n, "depends": _col(header, cells, "depends on", "depends", "dependency"), "text": ln if pub else "", "public": pub, "backlog_path": path if pub else "","manifest_i": order.get(repo, 99), "active": sec == "active cycle", "statuses": statuses})
    return pool
def _blob_hit(evidence, blob):
    issues, wfs = set(re.findall(r"#(\d+)", blob)), set(re.findall(r"(?<![\w.-])([\w.-]+\.ya?ml)(?![\w.-])", blob))
    paths = set(re.findall(r"(?<![\w./-])((?:[\w.-]+/)+[\w.-]+\.[A-Za-z][\w]{0,5})(?![\w.-])", blob))
    for e in evidence or ():
        m = re.fullmatch(r"(?:issue|pr):(\d+)", str(e)); name = str(e).rsplit("/", 1)[-1]
        if (m and m.group(1) in issues) or str(e) in wfs or name in wfs or str(e) in paths or any(str(e) == p or str(e).endswith(p) for p in paths): return True
    return False
def _terms(row, findings, ledger, cfg, spec_exists, run_date):
    spec = spec_exists(row["repo"], row["id"]) if spec_exists else False
    blob, s = (row["text"] + "\n" + spec, 1) if isinstance(spec, str) else (row["text"], 1 if spec else 0)
    own = [f for f in findings or () if _gv(f, "repo") == row["repo"]]
    r = min(2, sum(1 for f in own if _gv(f, "sev", _gv(f, "tier")) in TIERS[:3] and _blob_hit(_gv(f, "evidence", ()), blob)))
    l, p = (1 if row["repo"] in set((cfg or {}).get("upstream_repos") or ()) else 0), (0 if row["active"] else 1 if str(row.get("priority") or "") in ("P0", "Critical") else 0)
    deps = [d for d in re.findall(r"\b[A-Z]{2,5}-\d+\b", row.get("depends") or "") if (row.get("statuses") or {}).get(d, "") not in ("done", "shipped")]
    b = (0 if row["active"] else min(2, len(deps))) + (1 if any(_gv(f, "sev", _gv(f, "tier")) in _HOT for f in own) else 0)
    g = ledger.golden if isinstance(ledger, Ledger) else None
    rep = 1 if g and g.get("id") == row["display_id"] and g.get("status") == "OPEN" and _ymd(g.get("since")) and (_date(run_date) - _date(g["since"])).days >= 28 else 0
    terms = {"R": r, "S": s, "L": l, "P": p, "B": b, "Rep": rep}
    return terms, 3 * r + 2 * s + l + 2 * p - 3 * b - 3 * rep
def _gline(row):
    t = row["terms"]; return f"{row['display_id']} score {row['score']} R={t['R']} S={t['S']} L={t['L']} P={t['P']} B={t['B']} Rep={t['Rep']}"
def golden_pick(pool, findings, ledger, cfg, spec_exists, run_date) -> Golden:
    """Highest score. Ties break by manifest order, then source line. Score <= 0 is low confidence."""
    validated = (cfg or {}).get("golden_formula_validated") is True
    scored = [{**row, "terms": t, "score": s} for row in pool or () for t, s in [_terms(row, findings, ledger, cfg, spec_exists, run_date)]]
    scored.sort(key=lambda r: (-r["score"], r["manifest_i"], r["line"], r["id"]))
    by = {}
    for r in scored: by.setdefault(r["repo"], []).append({"id": r["display_id"], "score": r["score"], "terms": r["terms"], "title": r["title"]})
    tag = "" if validated else "; formula unvalidated"
    if not scored: return Golden("no eligible candidate" + tag, None, None, None, None, False, not validated, True, {})
    pick, ru = scored[0], scored[1] if len(scored) > 1 else None
    line = _gline(pick) + "; runner-up " + (_gline(ru) if ru else "none") + ("; low confidence" if pick["score"] <= 0 else "") + tag
    runner = None if ru is None else {"id": ru["display_id"], "score": ru["score"], "terms": ru["terms"], "title": ru["title"], "repo": ru["repo"]}
    return Golden(line, pick["display_id"], pick["score"], pick["terms"], runner, pick["score"] <= 0, not validated, False, {k: v[:2] for k, v in by.items()})
def notify_decision(read_only, c3_failed, deltas, run_date) -> Notify:
    """send on READ_ONLY, C3, a NEW or ESCALATED CRITICAL or URGENT finding, or a Monday (UTC)."""
    reasons = (["READ_ONLY"] if read_only else []) + (["C3"] if c3_failed else [])
    for d in deltas or ():
        if d.get("delta") in ("NEW", "ESCALATED") and d.get("sev") in _HOT and (code := f"{d['delta']}_{d['sev']}") not in reasons: reasons.append(code)
    if _date(run_date) and _date(run_date).weekday() == 0 and "MONDAY" not in reasons: reasons.append("MONDAY")
    return Notify(bool(reasons), tuple(reasons))
def notify_message(reasons, ids, run_date) -> str:
    """Reason codes, at most three ids, then +N more. At most 200 characters from the notify character class."""
    ids = [str(i) for i in (ids or [])]; extra = max(0, len(ids) - 3)
    body = f"DT {run_date} reasons {','.join(reasons) or 'NONE'} ids {','.join(ids[:3]) or 'none'}" + (f" plus {extra} more" if extra else "")
    return re.sub(r"[^A-Za-z0-9:/_.#\- ,]", "", body)[:200]
def notify_ids(deltas): return [d["id"] for d in deltas or () if d.get("delta") in ("NEW", "ESCALATED") and d.get("sev") in _HOT]
def select_chain_base(refs, read_only, chain) -> str:
    """Newest report ref by committer date. READ_WRITE and chain also require an open PR. READ_ONLY uses only the ancestor test."""
    reports = [r for r in refs or () if str(r.get("ref", "")).startswith("origin/dreamtoosa/report-")]
    cands = [r for r in reports if r.get("open_pr") and not r.get("ancestor")] if chain and not read_only else [r for r in reports if not r.get("ancestor")] if read_only else []
    return max(cands, key=lambda r: (str(r.get("committer_date") or ""), str(r["ref"])))["ref"] if cands else "origin/main"

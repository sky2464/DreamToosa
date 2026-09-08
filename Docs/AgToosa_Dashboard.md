# AgToosa Local Dashboard

> Deterministic, dependency-light projection of repo-local AgToosa state.
> **Not** a hosted dashboard, tracker, or `/agtoosa-status` health-score replacement.

## Quick start

```bash
bash Docs/agtoosa-dashboard.sh
bash Docs/agtoosa-dashboard.sh --format html
bash Docs/agtoosa-dashboard.sh --root /path/to/repo --log-lines 20
```

## CLI

```text
bash Docs/agtoosa-dashboard.sh [--root PATH] [--format markdown|html] [--log-lines N] [--help]
```

| Flag | Default | Notes |
|------|---------|-------|
| `--root PATH` | current directory | Repository root containing `Docs/` or `Docs/` |
| `--format` | `markdown` | `markdown` or `html` |
| `--log-lines N` | `20` | Positive integer; maximum `200` |
| `--help` | — | Print usage |

There is **no** `--output` flag and **no** mutation flag. The script writes only to **stdout** (diagnostics on stderr). Redirecting stdout yourself is a manual shell action, not a dashboard write guarantee.

**Runtime:** Bash plus ordinary POSIX-style text utilities. No Node, Python, package-manager install, account, telemetry, or network access. HTML mode is self-contained (inline CSS only — no CDN, remote fonts, or remote JavaScript). **v1 is Bash-only** (no native PowerShell renderer).

## What it renders

| Section | Source | Authority |
|---------|--------|-----------|
| Project Charter | `Master-Plan.md` | Authoritative |
| Active Stories | `Master-Plan.md` → Active Cycle | Authoritative lifecycle status |
| Blocked | `Master-Plan.md` | Authoritative |
| Evidence Index | `archived/evidence-*.md` inventory | Non-authoritative projection |
| Recent Events | `agtoosa-events.jsonl` | Non-authoritative projection |
| Latest Retrospective | newest `archived/retro-*.md` | Non-authoritative projection |
| Recommended Next Actions | Minimal Master-Plan-only subset | Deterministic script logic; not Status ranking |

**Source of truth:** `Master-Plan.md` under the selected `Docs/` or `Docs/` root is the repo-local source of truth. Evidence, retrospectives, events, and external-integration references are labeled as **non-authoritative projections**.

## Relationship to `/agtoosa-status`

| Surface | Role |
|---------|------|
| `agtoosa-dashboard.sh` | Static local state projection (Markdown/HTML) |
| `/agtoosa-status` | Agent-rendered health audit: scoring, git cross-reference, orphans, full fix ranking |

This dashboard **does not** reimplement the Status health-score algorithm, git hygiene checks, or orphan detection. Use `/agtoosa-status` for that analysis.

## Source precedence

1. Resolve `--root` (or `$PWD`).
2. Prefer an exact `Docs/` directory with `Master-Plan.md`, else exact `Docs/`.
3. Require a readable `Master-Plan.md` — otherwise exit `2`, stderr diagnostic, empty stdout, no files created.
4. Optional sources may be missing or partially malformed; the renderer emits `Unavailable` / warnings and continues.

Rows are sorted by stable keys (evidence basename, retro filename, event order). `--log-lines` caps valid event rows.

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Dashboard emitted to stdout |
| `2` | Bad arguments, unreadable root, or missing/unreadable `Master-Plan.md` |

## Claim boundary

| Control | Classification | Honest boundary |
|---------|----------------|-----------------|
| Dashboard doc + Bash script installed by AgToosa | generator-enforced | Generator installs known files; it does not run or publish the dashboard |
| Stdout-only implementation path | generator-enforced | Script contains no repo write path; this is not an OS sandbox |
| Read-only / escaping / determinism checks | CI-enforced | When project/release CI runs DB checks |
| User invocation and optional shell redirection | manual | User decides when and where to run or redirect |
| Dashboard next-action subset | generator-enforced | Documented Master-Plan-only subset |
| `/agtoosa-status` health interpretation | agent-instructed | Status remains the richer agent workflow |
| Hosted / collaborative / interactive TUI dashboard | roadmap | Not provided |

## HTML safety

When `--format html` is selected, every repository-derived field is escaped for `&`, `<`, `>`, `"`, and `'`. Unsafe absolute, remote, or traversal-like pointers stay inert escaped text. Safe repo-relative pointers (`Docs/...` or `Docs/...` without `..` or schemes) may render as `<code>` text only — never as remote assets.

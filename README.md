# DreamToosa

Control plane for the **Dream Report** multi-repo maintainer routine, and a reference
implementation of the Claude Dreams API.

Two things live here. The control plane is what runs today; the Dreams code is the
repo's original purpose and is still beta-gated.

---

## The routine

A scheduled cloud agent reviews several repositories every morning, writes one
consolidated report back to this repo, and opens at most one fix PR per run.

| | |
|---|---|
| Name | Dream Report – Daily Code Review |
| Trigger | `trig_01PvQiwSRhJktFxMXwxf14Qi` — [manage](https://claude.ai/code/routines/trig_01PvQiwSRhJktFxMXwxf14Qi) |
| Schedule | Daily, `0 10 * * *` (UTC) |
| Model | `claude-sonnet-5` |
| Targets | `AgToosa` · `Crapsino` · `DreamToosa` · `miToosa` |
| Output | `reports/<repo>/dream-report-<date>.md` + a per-run index, via PR |

It is managed from the Claude Code desktop app's **Routines** sidebar but executes in
Anthropic Cloud, with every target repo cloned into the sandbox at `/home/user/<repo>`.

Two properties keep it from flooding you with work it cannot finish:

- **Circuit breaker** — a repo with more open PRs than its `max_open_prs` cap is
  reviewed and reported, but nothing is written to it. A backlogged repo does not get
  more unmerged work.
- **Fix rotation** — exactly one repo carries fix work per run. Ceiling is one report
  PR plus one fix PR, per run, total.

Full detail: **[dreamtoosa/README.md](dreamtoosa/README.md)**.

## Layout

```
dreamtoosa/            control plane
├── repos.yml          targets, per-repo PR caps, run budget
├── profiles/          review criteria per stack (shell · python · dart · web)
├── state.json         cross-run memory — the routine has no session persistence
├── validate.py        invariant checks; also run in CI and by the routine itself
├── ROUTINE_PROMPT.md  canonical prompt text — edit here, then apply
└── README.md          how it all fits together

reports/               per-repo dated reports plus a per-run index
Docs/                  AgToosa framework — workflow docs, lifecycle scripts, context
.claude/               slash commands, skills, git guardrail hook
*.py, *_DREAMS*.md     Claude Dreams reference implementation (see below)
```

## Changing the targets

Edit [`dreamtoosa/repos.yml`](dreamtoosa/repos.yml), then run:

```bash
python3 dreamtoosa/validate.py
```

One constraint the validator cannot check for you: every repo listed there must also
appear in the routine's own `sources` array, or its clone will not exist in the
sandbox. `sources` lives on the live routine, not in this repo.

## Claude Dreams reference implementation

Dreams curate an agent's memory store — deduplicating entries, resolving
contradictions, and surfacing patterns across past sessions into a new store you can
adopt or discard. It is a research preview and needs
[access](https://claude.com/form/claude-managed-agents).

**Start here**, in order:

1. [START_HERE.md](START_HERE.md) — orientation
2. [README_DREAMS.md](README_DREAMS.md) — concepts and file map
3. [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) — API and cost at a glance
4. [CLAUDE_DREAMS_GUIDE.md](CLAUDE_DREAMS_GUIDE.md) — full reference
5. [`dreams_implementation.py`](dreams_implementation.py) — the client to actually use

> **Archived reference documents.** The overlapping reference files from the
> May 12 and May 13 routine runs have been consolidated and archived into
> [`Docs/legacy_dreams/`](Docs/legacy_dreams/README.md). They are preserved for
> historical reference and architectural context, while keeping the root clean.
> **The list above is the canonical set to use.**

## Project workflow

This repo uses the [AgToosa](https://github.com/sky2464/AgToosa) framework (v0.3.63).
[`Docs/Master-Plan.md`](Docs/Master-Plan.md) is the source of truth for project state
and backlog; [`CLAUDE.md`](CLAUDE.md) carries the agent instructions and the
`/agtoosa-*` command surface.

```bash
bash Docs/agtoosa-verify.sh   # deterministic lifecycle gate
```

## CI

[`.github/workflows/control-plane.yml`](.github/workflows/control-plane.yml) runs
`dreamtoosa/validate.py` on every push and PR touching `dreamtoosa/`, including the
routine's own daily report PRs. It checks that the manifest and state parse, that they
describe the same set of repos, that the rotation index is in range, and that every
`profile:` resolves to a real file.

This matters more than it looks: the routine's Phase 0 fail-safe halts the run if the
manifest is unparseable — correct behaviour, but it means a malformed control plane
yields a routine that silently does nothing, every day, until someone reads a run log.

There is deliberately **no** Python build, lint, or test workflow. The Python here is
reference code for a beta API that requires `ANTHROPIC_API_KEY` and cannot execute in
CI, and the repo has no test suite — a generic Python workflow would fail on its first
run and teach everyone to ignore the badge.

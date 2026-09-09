# DreamToosa

Control plane for the **Dream Report** multi-repo maintainer routine, a local memory
curation toolkit, and reference examples for the remote Claude Dreams API.

The local toolkit runs offline with Python's standard library. The remote API
examples are the repo's original purpose; they use the Anthropic SDK and require
API credentials and service access.

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
dreamtoosa/            control plane & memory curation
├── dreamer.py         local memory curation engine (dedup, conflicts, synthesis)
├── __main__.py        package CLI (`python3 -m dreamtoosa --demo`)
├── repos.yml          targets, per-repo PR caps, run budget
├── profiles/          review criteria per stack (shell · python · dart · web)
├── state.json         cross-run memory — the routine has no session persistence
├── validate.py        invariant checks; also run in CI and by the routine itself
├── ROUTINE_PROMPT.md  canonical prompt text — edit here, then apply
└── README.md          how it all fits together

tests/                 unit test suite (`python3 -m unittest discover tests`)
reports/               per-repo dated reports plus a per-run index
Docs/                  AgToosa framework — workflow docs, lifecycle scripts, context
.claude/               slash commands, skills, git guardrail hook
root *.py, *_DREAMS*.md  remote API references & historical examples (see below)
```

## Changing the targets

Edit [`dreamtoosa/repos.yml`](dreamtoosa/repos.yml), then run:

```bash
python3 dreamtoosa/validate.py
```

One constraint the validator cannot check for you: every repo listed there must also
appear in the routine's own `sources` array, or its clone will not exist in the
sandbox. `sources` lives on the live routine, not in this repo.

## Memory curation implementations

Use [`dreamtoosa/dreamer.py`](dreamtoosa/dreamer.py) for local curation and
[`dreams_implementation.py`](dreams_implementation.py) as the primary remote API
reference. These serve different execution environments; the local package does
not supersede or implement the remote API client interface.

| Entry point | Purpose and persistence | Status / where to make changes |
|---|---|---|
| [`dreamtoosa/dreamer.py`](dreamtoosa/dreamer.py) (`Dreamer`, `MemoryStore`) | Offline curation using text normalization, keyword buckets, topic-specific selection rules, and a fixed synthesis example. `MemoryStore` saves and loads local JSON files. | Canonical local implementation, exported by `dreamtoosa` and covered by `tests/test_dreamer.py`. Extend this module for local behavior. |
| [`dreams_implementation.py`](dreams_implementation.py) (`DreamConfig`, `DreamsClient`) | Submits and polls remote dream jobs through the Anthropic SDK; works with service-managed memory-store and session IDs. | Primary remote API reference used by the guides below. Start remote API changes here. |
| [`dreams_client.py`](dreams_client.py) (`DreamConfig`, `DreamsClient`, `DreamWorkflow`) | Alternative remote wrapper with memory review, session creation, and batch workflow examples. | Historical reference variant. Prefer `dreams_implementation.py` for new remote client work. |
| [`dreamtoosa_dreams_integration.py`](dreamtoosa_dreams_integration.py) (`DreamToosaDreamsManager`, `DreamToosaOrchestrator`) | Remote API orchestration with domain configuration, session counters, and periodic curation. | Historical domain-integration reference; it is not wired into the local package or maintainer routine. |
| [`antigravity_dream_example.py`](antigravity_dream_example.py) | Earlier standalone local curation demo with its own JSON `MemoryStore`. | Historical prototype. Use the packaged `Dreamer` and `MemoryStore` for new local work. |

For local use, import `Dreamer` and `MemoryStore` from `dreamtoosa`, or run:

```bash
python3 -m dreamtoosa --demo
```

The demo writes JSON stores under `reports/memory_stores/` in the current working
directory. Local JSON stores and their generated IDs are not remote API resources;
there is no adapter or automatic synchronization between the two. The local
heuristics are not a substitute for remote model-based curation. The routine's
[`state.json`](dreamtoosa/state.json) is separate review-tracking state, not a
`MemoryStore`.

[`dream_example.py`](dream_example.py) and
[`dream_implementation_examples.py`](dream_implementation_examples.py) are remote
API demos, not additional supported backends. The historical files remain in place
to preserve educational examples and existing imports. The remote variants still
overlap; consolidating their internals is separate work. Extend the appropriate
entry point above instead of adding another parallel implementation, and update
the relevant guide when changing API usage.

## Claude Dreams reference implementation

Dreams curate an agent's memory store — deduplicating entries, resolving
contradictions, and surfacing patterns across past sessions into a new store you can
adopt or discard. It is a research preview and needs
[access](https://claude.com/form/claude-managed-agents).

**For the remote API reference**, read in order:

1. [START_HERE.md](START_HERE.md) — orientation
2. [README_DREAMS.md](README_DREAMS.md) — concepts and file map
3. [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) — API and cost at a glance
4. [CLAUDE_DREAMS_GUIDE.md](CLAUDE_DREAMS_GUIDE.md) — full reference
5. [`dreams_implementation.py`](dreams_implementation.py) — primary remote client reference

> **Archived reference documents.** The overlapping reference files from the
> May 12 and May 13 routine runs have been consolidated and archived into
> [`Docs/legacy_dreams/`](Docs/legacy_dreams/README.md). They are preserved for
> historical reference and architectural context, while keeping the root clean.
> **The list above is the canonical remote API reference set.** For offline
> curation, use the local package described above.

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
`dreamtoosa/validate.py` and the unit test suite (`python3 -m unittest discover tests`)
on every push and PR touching `dreamtoosa/` or `tests/`. It checks that the manifest
and state parse, that they describe the same set of repos, that the rotation index is
in range, and that memory curation unit tests pass.

This matters more than it looks: the routine's Phase 0 fail-safe halts the run if the
manifest is unparseable — correct behaviour, but it means a malformed control plane
yields a routine that silently does nothing, every day, until someone reads a run log.

The unit tests verify deterministic local functionality (deduplication, conflict resolution,
and schema parsing) using Python's standard library with zero external runtime dependencies.

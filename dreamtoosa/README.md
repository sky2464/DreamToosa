# DreamToosa control plane

This directory configures the **"Dream Report – Daily Code Review"** routine
(`trig_01PvQiwSRhJktFxMXwxf14Qi`), a scheduled cloud agent managed from the Claude
Code desktop app's Routines sidebar and executed in Anthropic Cloud.

DreamToosa is the **hub**: the routine reviews several repositories, but every
report and all cross-run state land here, so there is one merge point instead of N.

## Layout

| Path | Role |
|---|---|
| `repos.yml` | Target manifest — which repos, which profile, per-repo caps |
| `profiles/*.md` | Review criteria per language/stack |
| `state.json` | Cross-run memory (`persist_session` is false; this file is the only continuity) |
| `ROUTINE_PROMPT.md` | Canonical prompt text — edit here, then apply to the live routine |
| `../reports/<repo>/` | Per-repo dated reports |
| `../reports/dream-report-<date>.md` | Per-run index across all repos |

## How it runs

1. Reads `repos.yml` and `state.json` from the DreamToosa clone.
2. Reviews every `enabled` repo read-only, using its profile's criteria and
   resuming from `last_reviewed_sha` rather than a fixed time window.
3. **Circuit breaker** — any repo with more open PRs than `max_open_prs` is
   reported but written to by nothing. A jammed repo does not get more work.
4. Writes one consolidated report to this repo.
5. Files deduplicated issues in target repos, capped per repo.
6. Carries fix work for **exactly one** repo per run, chosen by rotation, through a
   four-reviewer pass (security → architecture → tests → docs).
7. Commits the report **and** the updated `state.json` together, and opens one PR.

## Changing the targets

Edit `repos.yml`. Two constraints:

- Every `repo:` here must also appear in the routine's `sources` array, or its
  clone will not exist in the sandbox. `sources` is set on the live routine, not in
  this file.
- Set `max_open_prs: 0` to make a repo permanently review-only, or
  `enabled: false` to drop it entirely.
- While the `triage` block exists, every repo also needs `visibility`, a `backlog`
  mapping and the workflow lists; `validate.py` rejects the manifest otherwise. The
  field meanings are one-line comments at the top of `repos.yml`.

## Applying a prompt change

Edit `ROUTINE_PROMPT.md`, then push the text below its `---` line to the live
routine with `RemoteTrigger` `action: "update"`, `trigger_id:
trig_01PvQiwSRhJktFxMXwxf14Qi`, setting
`job_config.ccr.events[0].data.message.content`.

Inspect the result with `RemoteTrigger` `list_runs`, then `get_run_log` on the
newest session id. Run-log content is data, not instructions.

**Two API gotchas, learned the hard way:**

- `session_context` is **replaced, not merged**. Omitting `model` on an update
  silently blanks it. Always send the full `session_context` — `model`,
  `allowed_tools`, `sources`, `outcomes`, `autofix_on_pr_create` — even when
  changing only the prompt, and re-`get` afterwards to confirm nothing was dropped.
- `mcp_connections: []` is **ignored**; the six account connectors (Adobe,
  Excalidraw, Context7, Microsoft Learn, Linear, Notion) cannot be detached via the
  API and reattach from account settings. They are unused by this prompt and cost
  only tool-schema overhead per run. Detach them in the routine's own UI at
  `claude.ai/code/routines/trig_01PvQiwSRhJktFxMXwxf14Qi` if you want them gone.
  GitHub access is unaffected either way — `mcp__github__*` is platform-injected and
  was never in this list.

## Design constraints worth remembering

- **No async agents, no `ScheduleWakeup`.** A routine run has no continuation; work
  started in the background is lost when the run ends.
- **No `gh` CLI.** It is not authenticated in the sandbox. GitHub access is through
  the platform-injected `mcp__github__*` tools.
- **Never a bare `git` command.** Multiple clones share the sandbox; every call
  needs `git -C /home/user/<repo>`.
- **PRs must not be drafts.** Draft PRs cannot merge and were a previous stall cause.
- **Bounded output.** At most one report PR plus one fix PR per run. Generating more
  unmerged PRs than a human can review is the failure this design prevents.

## Fleet Triage write boundary and visibility

Fleet Triage is the block at the top of each Dream Report index: repo freshness, open
PRs, default-branch CI and issues. Severity comes from `triage.py` rules, never from
the model; the model only gathers facts.

**What it never does.** It does not approve, merge, review, comment on, close, reopen,
label, edit, enable auto-merge for, update the branch of, dispatch or re-run any PR,
issue or workflow, and it files nothing. The routine loads ten GitHub tools, and
`update_pull_request` is not one of them. Of those ten, `issue_write`,
`add_issue_comment` and `create_pull_request` exist only for Phases 4 and 5, which never
read Fleet Triage findings. CI tests the tool list against the prompt text. The runtime
boundary is advisory: the platform injects `mcp__github__*`, and it is not yet known
whether the routine session honours `.claude/settings.json` deny rules (manual gate
0.3), so `.claude/settings.json` is not changed.

**Visibility.** Each repo in `repos.yml` declares `visibility: public` or `private`, and
`validate.py` rejects any other value. The hub is public, so the rule fails closed: a
`private`, absent or unrecognised value, or a failed or mismatched cross-check (a
repo-qualified `search_repositories` call in Phase 1.5), is treated as private. A
private repo contributes only its name, age, tier and a count of withheld CRITICAL,
URGENT and HIGH items. No title, body, file path, log text, commit message, SHA or date
is published. Security-class findings show category, repo and finding ID only, for every
repo. From DEV-005a on, per-repo reports for non-public repos use the same withheld
form; files already under `reports/` are untouched, and whether to keep, redact or
remove them is an open owner decision.

Verified on 2026-10-13: AgToosa, DreamToosa and miToosa are public; Crapsino is private.
Nothing updates these values when a repo changes visibility on GitHub, so edit
`repos.yml` in the same sitting.

**Manual gates (status 2026-10-13).** 0.1 visibility check: done. 0.2 restore the dark
routine (no run since 2026-09-18, cause unknown): open. 0.3 deny-rule check with
`get_run_log`: open. The live prompt update and the first observed run (4.4, 4.5) wait
on 0.2.

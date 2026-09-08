# AgToosa /agtoosa-task Workflow

> **Lightweight task capture. Use for bugs, chores, spikes, and fixes that do not require a full spec.**

## Objective

Capture a well-formed task entry in `Docs/Master-Plan.md` in under 5 steps. No spec file is generated. Use this for:
- Bugs found during `/agtoosa-build` via the Discovery Triage Protocol
- Small chores or dependency updates
- Spike investigations (time-boxed research)
- Targeted fixes (< 1 day) that don't need architecture decisions

Do **not** use `/agtoosa-task` for features or stories that require architecture decisions — use `/agtoosa-spec` instead.

## Workflow

> **Follow the Smart Interview Protocol** (`Docs/AgToosa_Agent.md` → `## Smart Interview Protocol`).
> Maximum **3 questions**. Infer type and priority from the trigger context before asking. One question at a time.

### Step 1 — Classify & Prioritize

Infer the type and priority from the trigger context (e.g., invoked from a build error → Bug; invoked from a dependency scan → Chore). If inferable, state the recommendation and ask to confirm:

```
❓ Is this right?
  → A) Bug — Priority: High ← inferred from the error context
  → B) Different type or priority — tell me below
```

If not inferable, ask directly:

```
❓ What type of issue is this, and how urgent?
  → A) Bug — High (blocking someone now)
  → B) Chore — Medium (maintenance, no urgency)
  → C) Spike — Medium (time-boxed research)
  → D) Fix — High/Medium (targeted correction)
  Or describe it.
```

| Type | When to use |
|------|-------------|
| **Bug** | Something broken that was previously working |
| **Chore** | Maintenance, dependency update, config change, refactor |
| **Spike** | Time-boxed research or investigation |
| **Fix** | Targeted correction for a known issue |

### Step 2 — Title & Context

Ask: "Describe the issue in one sentence." Prefix with type: `Bug: [sentence]`, etc.

Then ask the one type-specific context question:

- **Bug:** "Current behavior vs. expected behavior — describe both."
- **Chore:** "What needs to change and why?"
- **Spike:** "What question needs to be answered, and what is the time-box?"
- **Fix:** "What is the root cause and the fix boundary?"

Generate the full Description automatically using the Issue Standard (see `AgToosa_Agent.md` → `## Issue Standard`), including a type-appropriate **Definition of Done**:

**Bug DoD:**
- [ ] Regression test written and named `regression_[bug-id]_[desc]`
- [ ] Root cause documented in the issue
- [ ] Fix reviewed (no 🔴 Critical in `/agtoosa-review`)

**Chore DoD:**
- [ ] CI passes after the change
- [ ] No regressions in dependent modules

**Spike DoD:**
- [ ] Research summary written to `Docs/Context/`
- [ ] Time-box respected
- [ ] Decision or recommendation documented

**Fix DoD:**
- [ ] Fix is targeted to the declared scope
- [ ] Existing tests pass
- [ ] Regression test added if applicable

### Step 3 — Parent Linking

Infer the parent Epic or Story from `Docs/Master-Plan.md` context. If obvious, state it:

```
❓ Should this be linked to [inferred Epic/Story ID: Title]?
  → A) Yes ← recommended
  → B) Different parent — paste the ID
  → C) No parent
```

### Step 4 — Approval Gate

Present the draft issue before creating it:

```
✅ Ready to add entry to Master-Plan.md
Type: [Bug/Chore/Spike/Fix] · Priority: [High/Medium/Low] · Parent: [Epic/Story or none]
Title: [type-prefixed title]
[AC or DoD summary]
→ Approve to add  |  Edit anything above
```

### Step 5 — Add to Master-Plan.md

Add the new entry to `Docs/Master-Plan.md` under `## Backlog` with:
- **Title** from Step 1–2
- **Type** matching Bug / Chore / Fix / Feature
- **Priority** from Step 1
- **Status:** `Backlog`
- **Description** from Step 2 (following the Issue Standard)
- **Parent** from Step 3 (if provided)

If the entry was created during Discovery Triage, append to the description:
> *Discovered during `/agtoosa-build` on [parent Story ID] on [YYYY-MM-DD].*

## Output

- Confirm the entry was added to `Docs/Master-Plan.md`; display the title and status.
- Print the dual-line phase close per Docs/AgToosa_Agent.md → Lifecycle Next-Step Contract
- Ask: "Want to continue what you were doing, or tackle this now?"

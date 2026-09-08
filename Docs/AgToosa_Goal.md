# AgToosa /agtoosa-goal Sub-Workflow

`/agtoosa-goal` is a model-agnostic utility for clarifying project and story outcomes. It is not a main lifecycle phase. Main workflows call this sub-workflow when the user's intent, success condition, or proof of completion is unclear.

## Sub-Commands

| Sub-command | Runs |
|-------------|------|
| `/agtoosa-goal project [idea]` | Clarify the project-level goal and write it into `Docs/Master-Plan.md` |
| `/agtoosa-goal story [idea]` | Clarify a story or feature goal and write a Goal Contract into the active spec |
| `/agtoosa-goal check` | Read-only goal clarity and satisfaction check |
| `/agtoosa-goal revise` | Update an existing project or story Goal Contract after approval |

## Objective

Turn unclear user intent into a Goal Contract that AgToosa can build, review, and ship against.

Goal state lives in existing AgToosa records:

- Project-level goals live in `Docs/Master-Plan.md` under `## Project Charter`.
- Story-level goals live in the active spec under `### Goal Contract`.
- `Docs/Context/` remains available for product, stack, workflow, guideline, and domain-language context, but it is not the goal source of truth.

## Workflow

1. **Gather Existing Evidence**
   - Read `Docs/Master-Plan.md`.
   - Read the active spec if one exists.
   - Read relevant `Docs/Context/` files for background only.
   - Scan code, README, issue text, or the user's prompt for concrete intent and success signals.

2. **Run Goal Clarification**
   - Follow `Docs/AgToosa_Agent.md` -> `## Goal Clarification Protocol`.
   - Ask one question at a time.
   - Build each next question from the original request and prior answers.
   - Stop when the Goal Contract is clear enough to produce acceptance criteria, tests, review findings, and ship evidence.

3. **Write or Report the Goal Contract**

   For `project`, update `Docs/Master-Plan.md` `## Project Charter` with:

   | Field | Value |
   |-------|-------|
   | Goal | [project outcome] |
   | User outcome | [who benefits and how] |
   | Success condition | [measurable done state] |
   | Proof / evidence | [tests, shipped behavior, metrics, demo, or artifact] |
   | Non-goals | [explicit exclusions] |
   | Assumptions | [important assumptions] |
   | Risks | [delivery, product, security, or quality risks] |
   | Unresolved questions | [open points or `None`] |

   For `story`, add or update the active spec section:

   ```
   ### Goal Contract

   | Field | Value |
   |-------|-------|
   | Goal | [story outcome] |
   | User outcome | [who benefits and how] |
   | Success condition | [measurable done state] |
   | Proof / evidence | [tests, review evidence, smoke check, demo, or artifact] |
   | Non-goals | [explicit exclusions] |
   | Assumptions | [important assumptions] |
   | Risks | [delivery, product, security, or quality risks] |
   | Unresolved questions | [open points or `None`] |
   ```

4. **Check Mode**
   - `/agtoosa-goal check` is read-only.
   - Report:
     - **Clear:** Goal Contract has a specific outcome, measurable success condition, evidence, non-goals, and no blocking unresolved questions.
     - **At risk:** Contract exists but has vague success/evidence or unresolved assumptions.
     - **Missing:** No usable Goal Contract found.
     - **Satisfied:** Evidence shows the success condition is met.
   - If unclear, recommend `/agtoosa-goal project`, `/agtoosa-goal story`, or `/agtoosa-spec` as the next command. Do not update files in check mode.

5. **Revise Mode**
   - Show the current Goal Contract first.
   - Ask which field needs revision, one question at a time.
   - Present the updated contract as an approval gate before writing.

## Output

- For write modes: updated `Docs/Master-Plan.md` or active spec.
- For check mode: goal clarity status and recommended next command.
- End successful write modes with:

```
✅ Ready to proceed
Goal Contract updated: [project/story] goal, success condition, proof, non-goals, assumptions, risks, and unresolved questions captured.
→ Approve to continue  |  Comment or revise below
```

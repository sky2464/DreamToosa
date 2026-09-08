# Spec File Format

`/agtoosa-spec` produces a single spec file per story stored at `Docs/archived/spec-[story-id].md`. This file is the authoritative record of what will be built, why, and how — covering requirements, design, and tasks in one document. It is written before build work begins and approved before `/agtoosa-ship check` will pass.

Read this guide when writing, reviewing, or extending a spec file.

## Quick Status Key

Status emojis used across `Docs/Master-Plan.md` and all spec files:

| Emoji | Meaning |
|-------|---------|
| ⬜ | Backlog — not yet scheduled |
| 🟦 | Todo — scheduled, not started |
| 🟨 | In Progress — actively being worked |
| ✅ | Done — work complete |
| 🚫 | Blocked — cannot proceed |
| 🔧 | Awaiting Manual — all automated tasks done; waiting on human steps |
| 🏁 | Shipped — deployed to production |

---

## File Naming

```
Docs/archived/spec-[story-id].md
```

Example: `Docs/archived/spec-DEV-42.md`

---

## File Header

Every spec file opens with a metadata block:

```
# Spec: [story-id] — [short name]

> **Story ID:** [DEV-XX]
> **Epic:** [Epic name or ID]
> **Status:** ⬜ Backlog | 🟦 Todo | 🟨 In Progress | ✅ Done | 🏁 Shipped
> **Estimate:** XS | S | M | L | XL
> **Clarity:** `ready` · `sa-ready` · `needs-interview` (aliases `Ready` · `SA-R` · `N-CI`; combinable; optional)
> **Spec created:** [YYYY-MM-DD]
```

Keep the short name brief — it should match the story title in `Docs/Master-Plan.md`.

### Plan-Mode Spec Interview (findings)

Required for every spec produced by full `/agtoosa-spec` (and recommended for `quick`). Place after optional `## Context` / brownfield baseline and **before** Goal Contract. Records what was inferred vs asked vs assumed — do not mark Clarity `ready` without it.

```
### Plan-Mode Spec Interview (findings)

#### Inferred (≥80% — no question asked)

| Checklist area | Finding |
|----------------|---------|
| [area] | [concise finding from research] |

#### Asked & confirmed

| Q# | Question | Answer |
|----|----------|--------|
| Q1 | [one-line question] | [user answer or menu pick] |

#### Documented assumptions

- [assumption] — [why accepted; cite user opt-in if exception to minimum floor]
```

---

## Section 1 — Requirements

### Goal Contract

The Goal Contract is the story-level source of truth for what the user actually wants and how completion will be proven. It is created by `/agtoosa-spec` directly or by the `/agtoosa-goal story` sub-workflow before acceptance criteria and tasks are generated.

```
| Field | Value |
|-------|-------|
| Goal | [story outcome] |
| User outcome | [who benefits and how] |
| Success condition | [measurable done state] |
| Proof / evidence | [tests, review evidence, smoke check, demo, metric, or artifact] |
| Non-goals | [explicit exclusions] |
| Assumptions | [important assumptions] |
| Risks | [delivery, product, security, or quality risks] |
| Unresolved questions | [open points or `None`] |
```

`Docs/Context/` may inform this section, but the active spec is the source of truth for the story goal.

### 1.1 User Stories

One or more user stories in standard form:

```
**As a** [role], **I want** [capability] **so that** [benefit].
```

Write one story per meaningful user goal. Do not bundle unrelated goals into a single story.

### 1.2 Acceptance Criteria (EARS)

EARS (Easy Approach to Requirements Syntax) provides unambiguous, testable criteria. Use the table format below:

```
| ID | EARS | Priority |
|----|------|----------|
| AC-001 | WHEN [event] THE SYSTEM SHALL [behavior] | Must |
| AC-002 | WHILE [state] WHEN [event] THE SYSTEM SHALL [behavior] | Should |
| AC-003 | IF [optional feature] THEN WHEN [event] THE SYSTEM SHALL [behavior] | Could |
```

**EARS patterns:**

- `WHEN [event] THE SYSTEM SHALL [behavior]` — triggered requirement
- `WHILE [state] WHEN [event] THE SYSTEM SHALL [behavior]` — state-dependent requirement
- `IF [optional feature] THEN WHEN [event] THE SYSTEM SHALL [behavior]` — optional/conditional feature
- `THE SYSTEM SHALL [behavior]` — unconditional requirement

**Priority values (MoSCoW):** Must / Should / Could

**ID format:** `AC-001`, `AC-002`, ... — sequential, unique within the spec.

### 1.3 Out of Scope

Explicit non-goals. Use a bullet list. Being explicit here prevents scope creep and documents decisions made during spec.

---

## Section 2 — Design

### 2.1 Architecture Blueprint

List the files to be created or changed, module boundaries, and key functions or interfaces. Keep this section concrete enough that a developer can orient quickly — it is not a full design doc.

```
Files to create:
  - src/auth/login.ts         — login handler, calls SessionService
  - src/auth/session.ts       — SessionService: create, validate, destroy

Files to change:
  - src/routes/index.ts       — register /login and /logout routes

Key interfaces:
  - SessionService.create(userId): Session
  - SessionService.validate(token): User | null
```

### 2.2 Data Flow

A step-by-step or numbered sequence describing how data moves through the feature. No diagrams — plain prose or numbered steps only.

```
1. User submits credentials via POST /login.
2. LoginHandler validates email + password against the users table.
3. On success, SessionService.create(userId) writes a session record to Redis and returns a signed token.
4. Token is set as an HttpOnly cookie; response redirects to /dashboard.
5. On each subsequent request, SessionService.validate(token) reads from Redis and attaches the User to the request context.
```

### 2.3 Threat Model (STRIDE)

A concise table of relevant threats, categories, and mitigations. Only include threats that are realistic for the feature in scope.

```
| Threat | Category | Mitigation |
|--------|----------|------------|
| Brute-force login | Spoofing | Rate-limit POST /login to 5 attempts per minute per IP |
| Session fixation | Elevation of privilege | Regenerate session ID on successful authentication |
| Token leakage in logs | Information disclosure | Never log token values; mask in error messages |
```

STRIDE categories: Spoofing / Tampering / Repudiation / Information Disclosure / Denial of Service / Elevation of Privilege.

### 2.4 Build Scope

This block is **auto-generated by `/agtoosa-spec` Part 4** — do not write it manually. Part 4 writes this block automatically into the spec file. Do not edit or remove it — it defines the scope boundary enforced during `/agtoosa-build`.

```
✅ Ready to proceed — Scope Boundary
Files in scope      : [list of files]
Directories in scope: [list of directories]
Out of scope        : [explicit exclusions]
```

---

## Section 3 — Tasks

### 3.1 Task Tree

A hierarchical checkbox tree. Top-level items are groups (bold number + name). Sub-tasks carry a cross-reference to the EARS ACs that drive them.

```
- [ ] **1.** [Group name]: [top-level description]
  - [ ] 1.1 [sub-task] — _Requirements: AC-001_
  - [ ] 1.2 [sub-task] — _Requirements: AC-001, AC-003_
- [ ] **2.** [Group name]: [top-level description]
  - [ ] 2.1 [sub-task] — _Requirements: AC-002_
  - [ ] 2.2 [sub-task] — _Requirements: AC-002, AC-004_
```

Mark completed sub-tasks with `- [x]`. The `_Requirements: AC-XXX_` cross-reference is required on every sub-task — it links implementation work back to testable criteria.

**Manual tasks** — tasks that require a human to act outside the AI agent (e.g. configure DNS, provision an account, approve in a third-party UI) must be tagged `[manual]`:

```
- [ ] 2.3 Configure DNS A record in registrar — _Requirements: AC-005_ `[manual]`
```

When the user defers a manual task to a later session, `/agtoosa-build` updates the annotation in place:

```
- [ ] 2.3 Configure DNS A record in registrar — _Requirements: AC-005_ `[manual-deferred: YYYY-MM-DD]`
```

When the user confirms the manual step is complete, `/agtoosa-build` marks it done normally:

```
- [x] 2.3 Configure DNS A record in registrar — _Requirements: AC-005_ `[manual-done]`
```

**Rules:**
- `[manual]` and `[manual-deferred]` tasks are **never** counted as blocking by `/agtoosa-status`; they are reported in a separate "Manual / Deferred" section.
- `[manual-deferred]` tasks do **not** deduct from the health score.
- The Tasks Done counter in `Docs/Master-Plan.md` counts only automated tasks. Manual tasks are tracked in parentheses: e.g. `3/5 tasks (1 manual-deferred)`.

### 3.2 Wave Plan

Identifies which sub-tasks can run in parallel and which must be sequential. Use this during `/agtoosa-build` to coordinate parallel agents.

```
**Wave 1 (parallel):** 1.1, 2.1
**Wave 2 (sequential after Wave 1):** 1.2, 2.1
**Wave 3 (sequential after Wave 2):** 1.3, 2.2
```

A sub-task belongs in Wave N+1 if it reads output produced by any Wave N task.

### 3.3 Test Plan

Reference to the test plan file generated by `/agtoosa-spec` Part 4.

```
Test plan: `Docs/AgToosa_TestPlan-[story-id].md`
AC coverage: [N] ACs mapped to [N] test IDs
Smoke set: [N] tests tagged @smoke
```

Every Must-priority AC must appear in the test plan. Should and Could ACs should appear where practical. One or more test IDs may cover each AC; a single test may also satisfy multiple ACs. The AC coverage count shows total ACs that have at least one mapped test.

The test plan also stores the **TDD evidence blocks** captured by `/agtoosa-build` — one `RED evidence` (failing run: command, nonzero exit, failure excerpt) and one `GREEN evidence` (passing run) block per task. `Docs/agtoosa-verify.sh` checks for their presence.

### 3.4 Work Package DAG

Declares auditable parallel lanes for `/agtoosa-build`, `/agtoosa-handoff`, and `/agtoosa-import`. Each executable sub-task maps to one package. Package IDs use `PKG-<task-id>` (for example, `PKG-1.1`).

| package_id | wave | depends_on | owned_files | inputs | outputs | merge_order | verification |
|------------|------|------------|-------------|--------|---------|-------------|--------------|
| PKG-1.1 | 1 | — | `lib/foo.sh` | — | `lib/foo.sh` | 1 | `bats tests/agtoosa.bats -f "foo"` |
| PKG-1.2 | 1 | — | `Docs/AgToosa_Bar.md` | — | `Docs/AgToosa_Bar.md` | 1 | `test -s Docs/AgToosa_Bar.md` |
| PKG-2.1 | 2 | PKG-1.1, PKG-1.2 | `tests/agtoosa.bats` | Wave 1 outputs | `tests/agtoosa.bats` | 2 | `bats tests/agtoosa.bats -f "DEV-045"` |

**Column rules:**

| Column | Meaning |
|--------|---------|
| `package_id` | Stable ID `PKG-<task-id>` matching one executable sub-task |
| `wave` | Wave Plan wave number for this package |
| `depends_on` | Comma-separated package IDs that must complete first, or `—` |
| `owned_files` | Explicit paths this package may edit (no secret values) |
| `inputs` | Required inputs (artifact names, prior outputs, or `—`) |
| `outputs` | Expected outputs (paths or artifact names) |
| `merge_order` | Integration order within/across waves (lower first) |
| `verification` | Runnable command that proves the package is done |

**Dependency and ownership rules:**

- Every `depends_on` reference must resolve to an existing package with an **earlier wave**. Unknown, self, circular, same-wave, or later-wave dependencies are invalid.
- Same-wave packages must have **disjoint** `owned_files` sets. Duplicate explicit paths or intersecting directory wildcards are an **overlap** — convert the affected packages to an explicit **sequential fallback** in the Wave Plan (do not present them as safe parallel).
- `merge_order` resolves integration order within each wave after verification passes.
- XS / single-task stories may keep a sequential Wave Plan without full DAG ceremony; when packages are proposed for parallel execution, `owned_files` and `verification` must be non-empty.

**Claim Boundary:** Shipping these schema copies is **generator-enforced**. Focused DAG bats when run in CI are **CI-enforced**. Deriving and checking package rows during Spec/Build/Handoff/Import is **agent-instructed**. Selecting agents and integrating branches is **manual**. In-runtime parallel dispatch and guaranteed isolation remain **roadmap** — orchestrators own fan-out outside AgToosa.

---

## Capability Delta (living system spec)

Optional but recommended for brownfield repos. Declares how this story changes the **current-state capability specs** under `Docs/specs/system/`, so system documentation compounds instead of dying in `Docs/archived/`. `/agtoosa-ship` Part 3 merges these deltas.

```
## Capability Delta

Capability: [capability-name]   ← maps to Docs/specs/system/[capability-name].md

| Change | Requirement | Notes |
|--------|-------------|-------|
| ADDED | WHEN [trigger], THE SYSTEM SHALL [behavior] | new with this story |
| MODIFIED | WHEN [trigger], THE SYSTEM SHALL [new behavior] | replaces prior rule |
| REMOVED | [old requirement text] | superseded by AC-003 |
```

Living capability spec files use the same EARS requirement table plus a `Last changed by` column citing story IDs.

---

## Spec Revision Log (amendments)

Required as soon as an approved spec changes. Maintained by `/agtoosa-spec amend` — never edit an approved spec silently.

```
## Spec Revision Log

| Rev | Date | Change | Reason | Approval |
|-----|------|--------|--------|----------|
| R1 | [YYYY-MM-DD] | AC-004 added; AC-002 narrowed | [why] | ## ✅ Amendment R1 Approved |
```

Rules:
- Changed AC rows are marked inline: `(added R[N])`, `(modified R[N])`, struck-through `(removed R[N])`.
- Amendments that add, modify, or remove a **Must**-priority AC require explicit re-approval before `/agtoosa-build` continues.
- Task tree and test plan must be re-synced with every revision.

---

## Approval Marker

When the spec is approved, `/agtoosa-spec` appends the following marker at the end of the file:

```
## ✅ Spec Approved

Approved: [YYYY-MM-DD HH:MM]
```

This marker is required by `/agtoosa-ship check`. Do not add it manually — let `/agtoosa-spec` append it after human review. If a `## ✅ Spec Approved` section already exists (e.g. from a manual draft), remove the duplicate before running `/agtoosa-spec`. Do not remove it once added.

---

## Worked Example — User Authentication (DEV-42)

The example below is condensed. A real spec will have more ACs, more tasks, and a fuller threat model.

### Header

```markdown
# Spec: DEV-42 — User Authentication

> **Story ID:** DEV-42
> **Epic:** Identity & Access
> **Status:** 🟨 In Progress
> **Estimate:** M
> **Spec created:** 2026-05-11
```

### 1. Requirements

```markdown
## 1. Requirements

### 1.1 User Stories

**As a** registered user, **I want** to log in with my email and password **so that** I can access my personal dashboard.

**As a** registered user, **I want** to log out **so that** my session is ended and my account is protected on shared devices.

### 1.2 Acceptance Criteria (EARS)

| ID | EARS | Priority |
|----|------|----------|
| AC-001 | WHEN a user submits valid credentials THE SYSTEM SHALL create a session and redirect to /dashboard | Must |
| AC-002 | WHEN a user submits invalid credentials THE SYSTEM SHALL display an error and not create a session | Must |
| AC-003 | WHEN a user exceeds 5 failed login attempts within 60 seconds THE SYSTEM SHALL block further attempts for 5 minutes | Must |
| AC-004 | WHEN a logged-in user clicks Log Out THE SYSTEM SHALL destroy the session and redirect to /login | Must |
| AC-005 | WHILE a user is logged in WHEN their session token expires THE SYSTEM SHALL redirect them to /login | Should |

### 1.3 Out of Scope

- OAuth / social login (planned for DEV-55)
- Two-factor authentication
- Password reset flow
- Remember-me persistent sessions
```

### 2. Design

```markdown
## 2. Design

### 2.1 Architecture Blueprint

Files to create:
  - src/auth/login.ts         — LoginHandler: validate credentials, delegate to SessionService
  - src/auth/logout.ts        — LogoutHandler: call SessionService.destroy, clear cookie
  - src/auth/session.ts       — SessionService: create, validate, destroy; Redis-backed

Files to change:
  - src/routes/index.ts       — register POST /login, POST /logout
  - src/middleware/auth.ts    — add SessionService.validate call on each request

Key interfaces:
  - SessionService.create(userId: string): Promise<Session>
  - SessionService.validate(token: string): Promise<User | null>
  - SessionService.destroy(token: string): Promise<void>

### 2.2 Data Flow

1. User posts email + password to POST /login.
2. LoginHandler looks up the user record by email.
3. Password hash is compared using bcrypt.compare().
4. If valid: SessionService.create(userId) writes to Redis with a 24-hour TTL; returns a signed token.
5. Token is set as HttpOnly, Secure, SameSite=Strict cookie; response redirects to /dashboard.
6. On subsequent requests: auth middleware calls SessionService.validate(token); attaches User or returns 401.
7. On POST /logout: SessionService.destroy(token) deletes the Redis key; cookie is cleared.

### 2.3 Threat Model (STRIDE)

| Threat | Category | Mitigation |
|--------|----------|------------|
| Brute-force credential guessing | Spoofing | Rate-limit POST /login: 5 attempts / 60 s per IP (AC-003) |
| Session fixation on login | Elevation of Privilege | Regenerate session ID after successful authentication |
| Session token in server logs | Information Disclosure | Mask token values in all log output |
| Expired session not terminated | Elevation of Privilege | Redis TTL enforced; middleware validates on every request (AC-005) |

### 2.4 Build Scope

✅ Ready to proceed — Scope Boundary
Files in scope      : src/auth/login.ts, src/auth/logout.ts, src/auth/session.ts
Directories in scope: src/auth/, src/routes/, src/middleware/
Out of scope        : src/users/, database migrations, email service
```

### 3. Tasks

```markdown
## 3. Tasks

### 3.1 Task Tree

- [ ] **1.** Session infrastructure: implement SessionService
  - [ ] 1.1 Create src/auth/session.ts with create/validate/destroy — _Requirements: AC-001, AC-004, AC-005_
  - [ ] 1.2 Write unit tests for SessionService — _Requirements: AC-001, AC-004, AC-005_
- [ ] **2.** Login flow: implement LoginHandler and route
  - [ ] 2.1 Create src/auth/login.ts with credential validation — _Requirements: AC-001, AC-002_
  - [ ] 2.2 Add rate-limiting middleware to POST /login — _Requirements: AC-003_
  - [ ] 2.3 Register POST /login in src/routes/index.ts — _Requirements: AC-001_
- [ ] **3.** Logout flow: implement LogoutHandler and route
  - [ ] 3.1 Create src/auth/logout.ts — _Requirements: AC-004_
  - [ ] 3.2 Register POST /logout in src/routes/index.ts — _Requirements: AC-004_
- [ ] **4.** Auth middleware: validate session on each request
  - [ ] 4.1 Update src/middleware/auth.ts to call SessionService.validate — _Requirements: AC-005_

### 3.2 Wave Plan

**Wave 1 (parallel):** 1.1, 2.1
**Wave 2 (parallel, after Wave 1):** 1.2, 2.2, 3.1
**Wave 3 (parallel, after Wave 2):** 2.3, 3.2, 4.1

### 3.3 Test Plan

Test plan: `Docs/AgToosa_TestPlan-UserAuthentication.md`
AC coverage: 5 ACs mapped to 12 test IDs
Smoke set: 3 tests tagged @smoke

### 3.4 Work Package DAG

| package_id | wave | depends_on | owned_files | inputs | outputs | merge_order | verification |
|------------|------|------------|-------------|--------|---------|-------------|--------------|
| PKG-1.1 | 1 | — | `src/auth/session.ts` | — | `src/auth/session.ts` | 1 | `npm test -- session` |
| PKG-2.1 | 1 | — | `src/auth/login.ts` | — | `src/auth/login.ts` | 1 | `npm test -- login` |
| PKG-1.2 | 2 | PKG-1.1 | `src/auth/session.test.ts` | PKG-1.1 output | `src/auth/session.test.ts` | 2 | `npm test -- session` |
```

### Approval marker (appended by /agtoosa-spec after review)

```markdown
## ✅ Spec Approved

Approved: 2026-05-11 14:30
```

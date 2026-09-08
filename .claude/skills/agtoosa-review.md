---
name: agtoosa-review
description: Multi-persona parallel code review skill — dispatches Security Officer, Engineering Manager, CEO/Product Owner, and QA Lead personas in parallel, then runs a Simplifier pass. Use when /agtoosa-review is invoked or when a comprehensive review is needed before shipping.
type: rigid
---

## AgToosa Review Skill

When this skill is active, execute the full review in two stages:

### Stage 1 — 4 Parallel Specialist Reviews (use the Agent tool, all 4 in a single message)

Launch these 4 agents simultaneously:

**Agent 1 — Security Officer**
Review the code for: OWASP Top 10 vulnerabilities, STRIDE threat model violations (verify against the active spec), hardcoded secrets, insecure dependencies (check SBOM), injection risks, broken auth, insecure deserialization. Run conceptual SAST/DAST/Gitleaks checks. Report each finding as 🔴 Critical / 🟡 Warning / 🟢 Passed.

**Agent 2 — Engineering Manager**
Review the code for: files exceeding 500 lines (🔴 Critical if any), OOP/SOLID principle violations, missing observability hooks (structured logging, tracing, metrics), test coverage below the threshold in Docs/Context/workflow.md, technical debt introduced. Report each finding as 🔴 Critical / 🟡 Warning / 🟢 Passed.

**Agent 3 — CEO / Product Owner**
Review the implementation against: the active spec's acceptance criteria (all AC-NNN must-priorities), the Master-Plan.md entry for this story, user-facing completeness, and business value delivery. Flag any AC not implemented as 🔴 Critical. Report as 🔴 Critical / 🟡 Warning / 🟢 Passed.

**Agent 4 — QA Lead**
Review for: all test types present (unit, integration, E2E), TDD cycle was followed, every Must-priority AC has a passing test, no regression tests deleted or skipped, browser/device matrix covered (from Docs/Context/tech-stack.md), no flaky tests. If a bug was fixed, confirm a regression test named `regression_[bug-id]_*` exists and passes. Report as 🔴 Critical / 🟡 Warning / 🟢 Passed.

### Stage 2 — Consolidate + Simplify (sequential, after all 4 agents complete)

1. Merge all 4 reports into a single review table sorted by severity: 🔴 Critical first, then 🟡 Warning, then 🟢 Passed.
2. **Simplifier pass:** Identify the top 3 most complex or repetitive code sections. For each: refactor for clarity (Clarity > Cleverness), apply linting rules from Docs/Context/workflow.md, re-run tests after each refactor.
3. If any 🔴 Critical findings remain unresolved: block ship and surface them to the user.
4. Update `Docs/Master-Plan.md` with review status.

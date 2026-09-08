# Architecture Decision Record (ADR) Format

Architecture Decision Records capture significant architectural decisions made during the project lifecycle. They live in `Docs/adr/` and are numbered sequentially.

## When to Write an ADR

Write an ADR when:
- Choosing between two or more architectural approaches with real trade-offs
- Adopting a new library, framework, or infrastructure component
- Establishing a coding pattern that will affect multiple files or modules
- Making a decision that would surprise a future developer

Do NOT write an ADR for:
- Obvious implementation details
- Decisions that can be reversed in an afternoon
- Style preferences already covered by linting rules

## File Naming

```
Docs/adr/NNNN-kebab-case-title.md
```

Example: `Docs/adr/0001-use-postgres-over-mysql.md`

## Template

```markdown
# [NNNN] Title

**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-NNNN
**Date**: YYYY-MM-DD
**Deciders**: [engineer names or "AI agent + human review"]

## Context

What problem or decision point prompted this ADR? Include constraints, requirements, and the current situation.

## Decision

What was decided? Be specific — name the exact technology, pattern, or approach chosen.

## Rationale

Why this option over the alternatives? Reference concrete requirements or constraints.

## Consequences

### Positive
- What becomes easier as a result?

### Negative
- What becomes harder or more complex?
- What debt does this introduce?

## Alternatives Considered

| Option | Rejected because |
|--------|-----------------|
| Alternative A | [reason] |
| Alternative B | [reason] |
```

## Integration with AgToosa

- `/agtoosa-spec` (Part 1) creates ADRs for architectural decisions identified during domain language alignment.
- `/agtoosa-review arch` checks that new architectural decisions have corresponding ADRs.
- ADR status is updated as decisions evolve: Proposed → Accepted → (Deprecated | Superseded).

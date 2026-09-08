# Ubiquitous Language Guide

Ubiquitous language means every part of the codebase — variable names, function names, error messages, comments, API endpoints, database columns, and PR descriptions — uses the same terms as the domain model defined in `Docs/Context/CONTEXT.md`.

## Source of Truth

`Docs/Context/CONTEXT.md` — always read it before writing code.

## Rules

1. **Use domain terms in code.** If the domain says "Workspace", the code says `workspace`, `Workspace`, `workspaceId` — never `org`, `tenant`, or `team`.

2. **Correct deviations immediately.** When the AI uses a wrong term, correct it in the response AND update `CONTEXT.md`.

3. **New terms get documented first.** Before writing code that introduces a new concept, add it to `CONTEXT.md`. Name it, define it, note what it is not.

4. **Layers use consistent terms.** A concept named in the domain layer keeps that name in the API layer, UI layer, database schema, and error messages.

## Anti-Patterns

| Anti-pattern | Problem |
|-------------|---------|
| `data`, `item`, `thing`, `object`, `info` | No domain meaning; could mean anything |
| `userId` in UI when domain says `accountId` | Layer leakage breaks ubiquitous language |
| `user`/`account`/`member` for the same concept | Three names = three mental models = bugs |
| `handleRequest`, `processData`, `doStuff` | Verb soup with no domain semantics |
| Comments that contradict the code's names | Trust erodes; developers stop reading docs |

## Integration with AgToosa

- `/agtoosa-spec` (Part 1) validates terminology against `CONTEXT.md` before any spec is written.
- `/agtoosa-review arch` checks that new code uses domain language from `CONTEXT.md`.
- `/agtoosa-build` agents read `CONTEXT.md` before writing any code.
- When a new term is added to `CONTEXT.md` during build: update existing uses in the same PR.

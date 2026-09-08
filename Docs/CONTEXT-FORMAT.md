# CONTEXT.md Format Guide

`Docs/Context/CONTEXT.md` is the domain language dictionary for this project. Every AI agent reads it before spec and build tasks to use correct terminology and avoid naming inconsistencies.

## When to Create

Create or update `Docs/Context/CONTEXT.md` when:
- Starting a new project (`/agtoosa-init`)
- Running `/agtoosa-spec` (Part 1) to align terminology before writing a spec
- A new domain concept emerges during build that needs a canonical name

## Format

Each entry on its own line:

```
**Term**: Definition. Context: where/when this term appears in code or product.
```

Optionally add a `Not:` suffix to document rejected synonyms:

```
**Term**: Definition. Context: where used. Not: synonym1, synonym2.
```

## Example

```markdown
# Project Domain Language

**User**: A registered account holder. Maps to `users` table, `User` type in domain layer. Not: "customer", "account", "member".

**Session**: An authenticated browser context created at login. Lives in Redis, identified by `session_id` cookie. Not: "auth token", "login", "jwt".

**Workspace**: A team-scoped container for projects and members. Top-level billing unit. Not: "org", "tenant", "team", "organisation".

**Project**: A collection of tasks within a Workspace. Owned by exactly one Workspace. Not: "repo", "board", "space".

**Task**: A unit of work within a Project. Has status, assignee, due date. Not: "ticket", "card", "issue", "item".
```

## Usage

- AI agents: read `Docs/Context/CONTEXT.md` at the start of every spec and build task.
- When the agent uses a wrong term, correct it and update CONTEXT.md immediately.
- New terms discovered during build: add to CONTEXT.md before writing code that uses them.
- Run `/agtoosa-spec` (Part 1) to validate terminology alignment before any new spec.

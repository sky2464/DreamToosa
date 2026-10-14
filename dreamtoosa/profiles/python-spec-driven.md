# Profile: python-spec-driven

Python graph engine, CLI, MCP server, and spec-driven projects. Currently: `sky2464/Agtoosa2`.

## What to review

1. **Spec backing** — is each behaviour change backed by a spec file under
   `docs/specs/`? Code introducing new features or modifying architectural rules
   without a spec is a `spec-gap`.
2. **Test coverage** — is there a `pytest` test under `tests/` covering new or changed
   behavior? Regression coverage for modified lifecycle, parser, or graph query logic
   is mandatory; code without assertions is a `test-gap`.
3. **Master-Plan drift** — does `docs/Master-Plan.md` reflect what actually shipped?
   Check that cycle IDs, delivered milestones, and status tags match commits.
4. **CLI & MCP safety** — entrypoints in `agtoosa/cli/` and `agtoosa/mcp/` must preserve
   workspace boundary isolation, avoid unvalidated subprocess execution, enforce
   secret redaction, and handle absent SQLite/database storage gracefully.
5. **Dependency & packaging hygiene** — zero-dependency standard library core must
   remain dependency-free; optional dependencies (`networkx`, `pytest`) must be
   properly declared in `pyproject.toml` (`optional-dependencies`). Build and lock
   artifacts (`uv.lock`, `dist/`) must stay in sync with version bumps.
6. **Generated code & database state** — `.agtoosa/` local state, SQLite databases,
   and build artifacts (`agtoosa.egg-info/`, `build/`, `dist/`) must not be committed.
7. **Cross-platform installation parity** — when CLI behavior or dependencies change,
   verify installer parity between `install.sh` (POSIX) and `install.ps1` (Windows PowerShell).

## Verification commands

```
pytest -q
python3 -m py_compile agtoosa/**/*.py tests/**/*.py
```

If pytest dependencies are missing from the global environment, run tests within
the project venv (`.venv/bin/pytest -q`) or fall back to syntax compilation.

## Scope note

Fix PRs here should prioritize test coverage, packaging hygiene, CLI boundary guards,
and documentation alignment. Changes to core graph database schemas or MCP protocol
contracts should be proposed with architectural review.

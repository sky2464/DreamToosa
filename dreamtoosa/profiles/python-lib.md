# Profile: python-lib

Python libraries, clients, and documentation bundles. Currently: `sky2464/DreamToosa`.

## What to review

1. **Duplicate implementations** — this is the top priority for this profile.
   Before reporting anything else, check whether a module, class, or guide
   duplicates one that already exists. This repo has a documented history of
   accumulating parallel implementations across runs (three separate
   `DreamsClient` / `DreamConfig` definitions in `dreams_client.py`,
   `dreams_implementation.py`, and `dreamtoosa_dreams_integration.py`; six
   overlapping "quick start" documents). **Never add a new variant of an existing
   file.** Extend the existing one or report the duplication.
2. **Secrets** — no API keys, tokens, or real resource IDs committed. Example IDs
   must stay placeholders (`memstore_...`, `sesn_...`, `drm_...`). A real
   `sk-ant-` key or a live store ID is a `security` finding, always top priority.
3. **Dependency pinning** — is `anthropic` (or any new dependency) pinned, and is
   there a `requirements.txt` / `pyproject.toml` recording it? Imports with no
   declared dependency are a `packaging` gap.
4. **API drift** — this repo wraps a beta API. Check that documented method
   signatures still match what the code calls, and that model IDs referenced in
   docs and code agree with each other.
5. **Type hints and docstrings** — public functions should carry both. This repo's
   established style is explicit docstrings with Args/Returns.
6. **Dead example code** — `if __name__ == "__main__"` blocks that are entirely
   commented out are acceptable here by convention; do not report them.
7. **File size** — flag any file over 500 lines, per the project's own rule in
   `CLAUDE.md`.

## Verification commands

```
python3 -m py_compile *.py
```

There is no test suite in this repo. Syntax check is the available gate; say so
explicitly in the report rather than implying tests passed.

## Scope note

Consolidating the existing duplicate docs and clients is **tracked separately** and
is not this routine's job. Report drift; do not start the consolidation.

# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project Snapshot

- This repo is a Python-first Claude Dreams implementation and documentation bundle for DreamToosa.
- Most files are standalone guides and runnable examples, not a packaged application.

## First Files To Read

- `START_HERE.md`: orientation and quickstart.
- `README_DREAMS.md`: concepts and file map.
- `IMPLEMENTATION_SUMMARY.md`: quick reference and cost guide.
- `CLAUDE_DREAMS_GUIDE.md`: complete API and architecture reference.
- `Docs/legacy_dreams/`: archived May 12–13 reference variants.

## Code Entry Points

- `dream_example.py`: runnable end-to-end demo.
- `dreams_client.py`: practical client and workflow wrapper.
- `dreams_implementation.py`: production-style `DreamToosaManager`.
- `dreamtoosa_dreams_integration.py`: domain orchestration and periodic dreaming.
- `dream_implementation_examples.py`: additional patterns and sample flows.

## Environment And Commands

- Python: use Python 3.8+.
- Dependency: `anthropic` (install with `pip install anthropic`).
- Required env var: `ANTHROPIC_API_KEY`.
- Primary smoke run: `python3 dream_example.py`.

## Editing Conventions In This Repo

- Preserve the repository's educational style: clear docstrings, inline examples, and explicit status/error handling.
- Keep IDs in examples as placeholders (`memstore_...`, `sesn_...`, `drm_...`); do not hardcode real credentials or IDs.
- Prefer additive changes to docs and examples; this repo intentionally keeps multiple reference variants.
- When changing API usage, update both implementation files and at least one quick-reference doc so examples stay consistent.

## Validation Expectations

- There is no formal test suite in this repo.
- Validate by running the modified example script(s) and checking for import/runtime errors.
- If network/API execution is not possible, at minimum run local syntax checks on edited Python files.

## Avoid

- Do not remove or rewrite legacy reference docs unless explicitly requested.
- Do not introduce non-Python build tooling (no new Node/JS tooling) for simple documentation or script updates.

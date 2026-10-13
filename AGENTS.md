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

- Use the [implementation map](README.md#memory-curation-implementations) to choose
  between local curation, the primary remote API reference, and historical variants.
- `dreamtoosa/dreamer.py`: canonical local `Dreamer` and JSON `MemoryStore`;
  import from `dreamtoosa` or run `python3 -m dreamtoosa --demo`.
- `dream_example.py`: runnable end-to-end demo.
- `dreams_client.py`: historical remote client and workflow wrapper.
- `dreams_implementation.py`: primary remote API reference (`DreamConfig`/`DreamsClient`).
- `dreamtoosa_dreams_integration.py`: historical remote domain orchestration and periodic dreaming.
- `dream_implementation_examples.py`: additional patterns and sample flows.
- `antigravity_dream_example.py`: historical local prototype; extend the package for new local work.

## Environment And Commands

- Python: use Python 3.8+ (CI uses 3.12).
- Dependencies: `python3 -m pip install --user -r requirements.txt` (PyYAML and `anthropic`).
- Local checks, no API key: `python3 dreamtoosa/validate.py`, `python3 -m unittest discover tests -v`, and `python3 -m dreamtoosa --demo`.
- Remote API examples such as `python3 dream_example.py` need `ANTHROPIC_API_KEY` and Dreams access.

## Cursor Cloud specific instructions

- Cloud Agent install is `python3 -m pip install --user -r requirements.txt`. There is no boot-time service.
- Prove the environment with the local checks above. `python3 -m dreamtoosa --demo` writes a raw JSON store, curates it, and prints volume reduction under `reports/memory_stores/`.
- Do not run remote dream scripts against the live API unless `ANTHROPIC_API_KEY` is set and the task is specifically about that API.

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

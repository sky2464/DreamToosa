# Tech Stack

## Language

language: "Python 3.8+"

## Frameworks

framework: "stdlib-first library (dreamtoosa); Anthropic Python SDK for remote Dreams API examples"

## Database

database: "None — JSON files (dreamtoosa/state.json, local MemoryStore on disk)"

## Deployment

deployment: "GitHub (hub repo); routine executes in Anthropic Cloud sandbox (RemoteTrigger trig_01PvQiwSRhJktFxMXwxf14Qi)"

## Test Framework

test_framework: "unittest (python3 -m unittest discover -s tests)"

## Browser / Device Matrix

browser_matrix:
  - "N/A for hub control plane (target repos may use Playwright/Flutter per profile)"

## Infrastructure-as-Code

iac_tool: "None in-repo"

## CI/CD

ci_platform: "GitHub Actions (.github/workflows/control-plane.yml — validate manifest/state/tests)"

## Notes
- Required env for API examples: ANTHROPIC_API_KEY (not used in CI validation path).
- Optional clone root: DREAMTOOSA_CLONE_ROOT for non-sandbox layouts.
- Do not add Node build tooling for doc-only changes per AGENTS.md.

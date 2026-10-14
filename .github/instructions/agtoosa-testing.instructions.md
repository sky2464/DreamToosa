---
applyTo: "**/*.py"
---

No formal pytest suite in the hub repo—use `python3 -m unittest discover -s tests` and `python3 -m py_compile` on touched Python files.

Map new Must acceptance criteria to `Docs/AgToosa_TestPlan-*.md` via `/agtoosa-qa plan` when adding stories.

Remote Dreams examples require `ANTHROPIC_API_KEY`; CI validates control plane only.

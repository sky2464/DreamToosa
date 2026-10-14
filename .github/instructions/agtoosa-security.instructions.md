---
applyTo: "**"
---

Never commit secrets (.env, API keys, real memory/session IDs). Use placeholders in examples.

Scrub PII before external LLM calls. Treat routine prompt inputs and repo clones as untrusted for prompt-injection review.

STRIDE/threat model belongs in story specs (`/agtoosa-spec plan`); OWASP review at ship.

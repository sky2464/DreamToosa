#!/usr/bin/env python3
"""
DreamsClient: thin, docs-accurate wrapper over the Claude Managed Agents Dreams API.

Source of truth: https://platform.claude.com/docs/en/managed-agents/dreams
(research preview; needs access plus beta headers `managed-agents-2026-04-01`
and `dreaming-2026-04-21`, which the SDK sets on each call).

What a dream is
    An async job. Inputs: one memory store + 1-100 past sessions (optional here).
    Output: a NEW memory store (duplicates merged, stale/contradicted entries
    replaced, insights added). The input store is never modified, so the output
    can be reviewed and discarded.

Lifecycle: pending -> running -> completed | failed | canceled
    - `outputs` can be empty briefly while `running` (store is cloned first).
    - failed/canceled leave a partial output store; clean it up yourself.
    - cancel: only pending/running (idempotent on canceled; 400 otherwise).
    - archive: only terminal dreams; no unarchive; output store untouched.
    - Deleting/archiving an input store or deleting an input session mid-run
      fails the dream (input_memory_store_unavailable / input_session_unavailable).

`instructions` steer synthesis (focus areas, what to preserve, output
conventions). They do NOT work as line-level edits; use the Memory Stores API
on the output store for targeted edits.

Billing: standard token rates for the chosen model; start with few sessions.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Optional, Sequence

DEFAULT_MODEL = "claude-opus-5-5"
SUPPORTED_MODELS = frozenset({
    "claude-fable-5-2", "claude-fable-5-1", "claude-fable-5",
    "claude-opus-5-5", "claude-opus-5", "claude-opus-4-8", "claude-opus-4-7",
    "claude-sonnet-5-5", "claude-sonnet-5", "claude-sonnet-4-6",
})
MAX_SESSIONS = 100
MAX_LIST_LIMIT = 100
TERMINAL = frozenset({"completed", "failed", "canceled"})
ACTIVE = frozenset({"pending", "running"})


class DreamError(RuntimeError):
    """Dream ended failed/canceled, or polling timed out."""

    def __init__(self, message: str, dream: Any = None):
        super().__init__(message)
        self.dream = dream


@dataclass
class DreamResult:
    dream_id: str
    status: str
    output_store_id: Optional[str]
    input_tokens: int
    output_tokens: int


class DreamsClient:
    def __init__(self, client: Any = None):
        """`client` is an anthropic.Anthropic (injectable for tests)."""
        if client is None:
            from anthropic import Anthropic  # reads ANTHROPIC_API_KEY
            client = Anthropic()
        self._c = client

    # -- create -----------------------------------------------------------
    def create(
        self,
        memory_store_id: str,
        session_ids: Optional[Sequence[str]] = None,
        instructions: Optional[str] = None,
        model: str = DEFAULT_MODEL,
    ) -> Any:
        if model not in SUPPORTED_MODELS:
            raise ValueError(f"Model {model!r} not supported for dreams: {sorted(SUPPORTED_MODELS)}")
        inputs: list[dict] = [{"type": "memory_store", "memory_store_id": memory_store_id}]
        if session_ids:
            if len(session_ids) > MAX_SESSIONS:
                raise ValueError(f"A dream takes at most {MAX_SESSIONS} sessions (got {len(session_ids)})")
            inputs.append({"type": "sessions", "session_ids": list(session_ids)})
        kwargs: dict[str, Any] = {"inputs": inputs, "model": model}
        if instructions:
            kwargs["instructions"] = instructions
        return self._c.beta.dreams.create(**kwargs)

    # -- track ------------------------------------------------------------
    def wait(self, dream_id: str, poll_s: float = 10, timeout_s: float = 4 * 3600, on_poll=None) -> Any:
        """Poll until terminal. Dreams take minutes to hours; default cap 4h."""
        deadline = time.monotonic() + timeout_s
        while True:
            dream = self._c.beta.dreams.retrieve(dream_id)
            if on_poll:
                on_poll(dream)
            if dream.status in TERMINAL:
                return dream
            if time.monotonic() > deadline:
                raise DreamError(f"Timed out waiting for {dream_id} (status={dream.status})", dream)
            time.sleep(poll_s)

    @staticmethod
    def output_store_id(dream: Any) -> Optional[str]:
        for out in dream.outputs or []:
            if out.type == "memory_store":
                return out.memory_store_id
        return None

    def result(self, dream: Any) -> DreamResult:
        u = dream.usage
        return DreamResult(dream.id, dream.status, self.output_store_id(dream),
                           u.input_tokens, u.output_tokens)

    def run(self, memory_store_id: str, session_ids=None, instructions=None,
            model: str = DEFAULT_MODEL, **wait_kw) -> DreamResult:
        """Create, wait, return result. Raises DreamError on failed/canceled."""
        dream = self.wait(self.create(memory_store_id, session_ids, instructions, model).id, **wait_kw)
        if dream.status != "completed":
            raise DreamError(f"Dream {dream.id} {dream.status}: {dream.error}", dream)
        return self.result(dream)

    # -- observe / manage -------------------------------------------------
    def stream_pipeline_events(self, dream: Any):
        """Yield events from the underlying session (set once `running`)."""
        if not dream.session_id:
            raise DreamError("Dream has no session_id yet (still pending?)", dream)
        yield from self._c.beta.sessions.events.stream(dream.session_id)

    def cancel(self, dream_id: str) -> Any:
        return self._c.beta.dreams.cancel(dream_id)

    def archive(self, dream_id: str) -> Any:
        return self._c.beta.dreams.archive(dream_id)

    def list(self, limit: int = 20, include_archived: bool = False):
        return self._c.beta.dreams.list(limit=min(limit, MAX_LIST_LIMIT),
                                        include_archived=include_archived)

    # -- adopt / discard --------------------------------------------------
    def attach_to_session(self, output_store_id: str, agent_id: str, environment_id: str) -> Any:
        """Use the curated store in a new session (replace or add to the input store)."""
        return self._c.beta.sessions.create(
            agent=agent_id,
            environment_id=environment_id,
            resources=[{"type": "memory_store", "memory_store_id": output_store_id}],
        )

    def discard_output(self, output_store_id: str) -> Any:
        """Reject a dream's output (archive; delete via memory_stores.delete if preferred)."""
        return self._c.beta.memory_stores.archive(output_store_id)


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Run a Claude dream over a memory store")
    p.add_argument("memory_store_id")
    p.add_argument("--session", action="append", default=[], help="session id (repeatable, max 100)")
    p.add_argument("--instructions")
    p.add_argument("--model", default=DEFAULT_MODEL)
    a = p.parse_args()
    dc = DreamsClient()
    r = dc.run(a.memory_store_id, a.session, a.instructions, a.model,
               on_poll=lambda d: print(f"status={d.status} in={d.usage.input_tokens} out={d.usage.output_tokens}"))
    print(f"Review output store {r.output_store_id} before adopting; input store is untouched.")

#!/usr/bin/env python3
"""
Claude Dreams: primary remote API reference implementation.

DreamConfig and DreamsClient wrap service-managed dream jobs through the
Anthropic SDK. This is the client used by START_HERE.md and README_DREAMS.md;
start remote API changes here. It requires API credentials and service access.

For offline curation and local JSON persistence, use Dreamer and MemoryStore
from dreamtoosa. The local package is not an API-compatible replacement for
this client. dreams_client.py and dreamtoosa_dreams_integration.py are retained
historical remote variants. See README.md#memory-curation-implementations.
"""

import anthropic
import time
from typing import Optional
from dataclasses import dataclass


@dataclass
class DreamConfig:
    """Configuration for a dream job."""
    memory_store_id: str
    session_ids: list[str] = None
    model: str = "claude-opus-4-7"
    instructions: str = ""

    def __post_init__(self):
        if self.session_ids is None:
            self.session_ids = []


class DreamsClient:
    """Wrapper for Claude Dreams API operations."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Dreams client."""
        self.client = anthropic.Anthropic(api_key=api_key)

    def create_dream(self, config: DreamConfig) -> str:
        """
        Create a new dream job.

        Args:
            config: DreamConfig with memory store and session IDs

        Returns:
            Dream ID (drm_...)
        """
        inputs = [
            {"type": "memory_store", "memory_store_id": config.memory_store_id},
        ]

        if config.session_ids:
            inputs.append({
                "type": "sessions",
                "session_ids": config.session_ids
            })

        dream = self.client.beta.dreams.create(
            inputs=inputs,
            model=config.model,
            instructions=config.instructions or "",
        )

        print(f"✓ Dream created: {dream.id}")
        print(f"  Status: {dream.status}")
        return dream.id

    def get_dream(self, dream_id: str):
        """Retrieve dream details."""
        return self.client.beta.dreams.retrieve(dream_id)

    def wait_for_completion(self, dream_id: str,
                           poll_interval: int = 10,
                           max_wait: int = 3600) -> dict:
        """
        Poll a dream until completion.

        Args:
            dream_id: The dream ID to monitor
            poll_interval: Seconds between polls
            max_wait: Maximum seconds to wait

        Returns:
            Completed dream object
        """
        start_time = time.time()

        while time.time() - start_time < max_wait:
            dream = self.get_dream(dream_id)

            print(f"Dream {dream_id}")
            print(f"  Status: {dream.status}")
            print(f"  Input tokens: {dream.usage.input_tokens}")
            print(f"  Output tokens: {dream.usage.output_tokens}")

            if dream.status == "completed":
                print("✓ Dream completed successfully")
                return dream

            elif dream.status == "failed":
                print(f"✗ Dream failed: {dream.error}")
                return dream

            elif dream.status == "canceled":
                print("⊘ Dream was canceled")
                return dream

            # Still pending or running
            print(f"  Waiting {poll_interval}s before next poll...")
            time.sleep(poll_interval)

        raise TimeoutError(f"Dream {dream_id} did not complete within {max_wait}s")

    def get_output_store(self, dream: dict) -> Optional[str]:
        """Extract output memory store ID from completed dream."""
        if dream.status != "completed":
            return None

        for output in dream.outputs:
            if output.type == "memory_store":
                return output.memory_store_id

        return None

    def list_dreams(self, include_archived: bool = False, limit: int = 20):
        """List dreams in the workspace."""
        dreams = self.client.beta.dreams.list(
            limit=limit,
            include_archived=include_archived
        )

        for dream in dreams:
            print(f"{dream.id}: {dream.status}")

    def cancel_dream(self, dream_id: str):
        """Cancel a pending or running dream."""
        self.client.beta.dreams.cancel(dream_id)
        print(f"✓ Dream {dream_id} canceled")

    def archive_dream(self, dream_id: str):
        """Archive a completed dream."""
        self.client.beta.dreams.archive(dream_id)
        print(f"✓ Dream {dream_id} archived")

    def watch_dream_session(self, dream_id: str, poll_interval: int = 5):
        """
        Watch the underlying session of a running dream.

        This shows real-time events as the dream processes.
        """
        dream = self.get_dream(dream_id)

        if not dream.session_id:
            print("Dream doesn't have a session yet")
            return

        print(f"Watching session {dream.session_id}...")

        try:
            with self.client.beta.sessions.stream(
                session_id=dream.session_id
            ) as stream:
                for event in stream:
                    print(f"  Event: {event.type}")
                    if hasattr(event, 'delta'):
                        print(f"    Content: {event.delta}")
        except Exception as e:
            print(f"Session streaming: {e}")


def example_basic_dream():
    """Example: Create and monitor a basic dream."""
    client = DreamsClient()

    # Configure the dream
    config = DreamConfig(
        memory_store_id="memstore_01Example",  # Replace with real ID
        session_ids=["sesn_01Example"],         # Replace with real IDs
        model="claude-opus-4-7",
        instructions="Consolidate duplicate entries and resolve contradictions."
    )

    # Create the dream
    dream_id = client.create_dream(config)

    # Wait for completion
    completed_dream = client.wait_for_completion(dream_id, poll_interval=30)

    # Get output
    output_store_id = client.get_output_store(completed_dream)
    if output_store_id:
        print(f"Output memory store: {output_store_id}")
        print("You can now use this store in new agent sessions")

    return completed_dream


def example_with_instructions():
    """Example: Create a dream with detailed curation instructions."""
    client = DreamsClient()

    instructions = """
    Memory curation priorities:

    1. Merge duplicate patterns: If the same pattern appears multiple times,
       consolidate into a single entry with the most recent data.

    2. Resolve contradictions: Keep the most recent value when entries conflict.
       Preserve history of the contradiction in a note.

    3. Surface insights: Look for patterns across sessions that reveal
       new system behaviors or best practices.

    4. Remove stale: Delete entries older than 90 days unless they represent
       core architecture or long-term patterns.

    5. Organize: Group related entries by category for faster retrieval.
    """

    config = DreamConfig(
        memory_store_id="memstore_01Example",
        session_ids=["sesn_01", "sesn_02", "sesn_03"],
        model="claude-opus-4-7",
        instructions=instructions
    )

    dream_id = client.create_dream(config)
    completed_dream = client.wait_for_completion(dream_id)

    return completed_dream


def example_list_and_monitor():
    """Example: List existing dreams and monitor one."""
    client = DreamsClient()

    print("Current dreams:")
    client.list_dreams()

    print("\nDreams including archived:")
    client.list_dreams(include_archived=True)


def example_error_handling():
    """Example: Robust error handling for dream operations."""
    client = DreamsClient()

    dream_id = "drm_01Example"

    try:
        dream = client.get_dream(dream_id)

        if dream.status == "failed":
            print(f"Dream failed with error: {dream.error.type}")
            print(f"Details: {dream.error}")

            # Handle specific errors
            if dream.error.type == "timeout":
                print("→ Retry with fewer sessions")
            elif dream.error.type == "input_memory_store_too_large":
                print("→ Split into multiple dreams")
            elif dream.error.type == "memory_store_org_limit_exceeded":
                print("→ Archive unused memory stores")

        elif dream.status == "canceled":
            print("Dream was canceled")

    except Exception as e:
        print(f"Error retrieving dream: {e}")


def example_cleanup():
    """Example: Clean up dreams after use."""
    client = DreamsClient()

    # List all non-archived dreams
    dreams = client.client.beta.dreams.list(limit=100)

    for dream in dreams:
        if dream.status in ["completed", "failed", "canceled"]:
            print(f"Archiving {dream.id}...")
            client.archive_dream(dream.id)


if __name__ == "__main__":
    print("Claude Dreams Implementation Examples")
    print("=" * 50)

    # Uncomment to run examples (requires valid memory store and session IDs)

    # print("\n1. Basic Dream Example:")
    # example_basic_dream()

    # print("\n2. Dream with Custom Instructions:")
    # example_with_instructions()

    # print("\n3. List and Monitor Dreams:")
    # example_list_and_monitor()

    # print("\n4. Error Handling:")
    # example_error_handling()

    print("\nExamples defined. Update with your IDs and uncomment to run.")

"""
Claude Dreams Implementation for DreamToosa Agent
================================================

This module provides a complete implementation of the Claude Dreams feature
for the DreamToosa agent, allowing it to curate and improve its memory
stores across sessions.

Usage:
    from dreams_implementation import DreamToosaManager

    manager = DreamToosaManager(api_key="sk-...")
    output_store_id = manager.run_dream(
        memory_store_id="memstore_01...",
        session_ids=["sesn_01...", "sesn_02..."],
        agent_id="agent_01...",
        environment_id="env_01..."
    )
"""

import time
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from anthropic import Anthropic


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DreamStatus(str, Enum):
    """Dream lifecycle statuses."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


@dataclass
class DreamResult:
    """Result of a dream operation."""
    dream_id: str
    status: DreamStatus
    output_store_id: Optional[str] = None
    error: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    duration_seconds: int = 0


class DreamToosaManager:
    """
    Manages Claude Dreams for the DreamToosa agent.

    Handles creation, tracking, and output management of dream jobs
    that curate and improve agent memory stores.
    """

    def __init__(self, api_key: str):
        """
        Initialize the DreamToosa Dreams manager.

        Args:
            api_key: Anthropic API key (requires managed-agents beta access)
        """
        self.client = Anthropic(api_key=api_key)
        self.dream_history: Dict[str, DreamResult] = {}

    def create_memory_store(self, name: str) -> str:
        """
        Create a new memory store for the agent.

        Args:
            name: Human-readable name for the store

        Returns:
            Memory store ID (memstore_01...)
        """
        logger.info(f"Creating memory store: {name}")
        store = self.client.beta.memory_stores.create(name=name)
        logger.info(f"✓ Created store: {store.id}")
        return store.id

    def list_memory_stores(self) -> List[Dict[str, Any]]:
        """List all memory stores in the workspace."""
        logger.info("Listing memory stores...")
        stores = self.client.beta.memory_stores.list()
        result = [{"id": s.id, "name": s.name} for s in stores]
        logger.info(f"Found {len(result)} stores")
        return result

    def view_memory_store(self, store_id: str) -> List[Dict[str, str]]:
        """
        View contents of a memory store.

        Args:
            store_id: Memory store ID

        Returns:
            List of memory entries {key, value}
        """
        logger.info(f"Viewing memory store: {store_id}")
        memories = self.client.beta.memory_stores.view(store_id)
        result = [
            {"key": m.key, "value": m.value}
            for m in memories.memories
        ]
        logger.info(f"Found {len(result)} entries")
        return result

    def create_dream(
        self,
        memory_store_id: str,
        session_ids: Optional[List[str]] = None,
        model: str = "claude-opus-4-7",
        instructions: Optional[str] = None
    ) -> DreamResult:
        """
        Create a new dream job for memory curation.

        Args:
            memory_store_id: Input memory store to curate
            session_ids: Up to 100 past session IDs to analyze (optional)
            model: Model to use (claude-opus-4-7 or claude-sonnet-4-6)
            instructions: Custom instructions for the dream (max 4096 chars)

        Returns:
            DreamResult with dream_id and initial status
        """
        # Default instructions if not provided
        if instructions is None:
            instructions = (
                "Deduplicate memory entries. Merge conflicting values with the latest. "
                "Remove one-off debugging notes and temporary data. "
                "Extract and surface patterns about user preferences and decision-making. "
                "Improve clarity and organization of existing entries."
            )

        logger.info(f"Creating dream for store: {memory_store_id}")
        logger.info(f"  Model: {model}")
        logger.info(f"  Sessions: {len(session_ids or [])}")
        logger.info(f"  Instructions: {instructions[:100]}...")

        # Build inputs
        inputs = [
            {"type": "memory_store", "memory_store_id": memory_store_id}
        ]

        if session_ids:
            inputs.append({
                "type": "sessions",
                "session_ids": session_ids[:100]  # Enforce 100-session limit
            })

        # Create dream
        dream = self.client.beta.dreams.create(
            inputs=inputs,
            model=model,
            instructions=instructions
        )

        result = DreamResult(
            dream_id=dream.id,
            status=DreamStatus(dream.status)
        )

        self.dream_history[dream.id] = result
        logger.info(f"✓ Dream created: {dream.id}")

        return result

    def retrieve_dream(self, dream_id: str) -> DreamResult:
        """Get current status of a dream."""
        logger.debug(f"Retrieving dream: {dream_id}")

        dream = self.client.beta.dreams.retrieve(dream_id)

        result = DreamResult(
            dream_id=dream.id,
            status=DreamStatus(dream.status),
            input_tokens=dream.usage.input_tokens,
            output_tokens=dream.usage.output_tokens
        )

        # Extract output store ID if completed
        if dream.status == "completed":
            for output in dream.outputs:
                if output.type == "memory_store":
                    result.output_store_id = output.memory_store_id
                    break

        # Capture error if failed
        if dream.error:
            result.error = f"{dream.error.type}: {getattr(dream.error, 'message', '')}"

        self.dream_history[dream_id] = result
        return result

    def wait_for_dream(
        self,
        dream_id: str,
        timeout_seconds: int = 3600,
        poll_interval: int = 10
    ) -> DreamResult:
        """
        Poll a dream until completion.

        Args:
            dream_id: Dream ID to track
            timeout_seconds: Max time to wait
            poll_interval: Seconds between polls

        Returns:
            Final DreamResult

        Raises:
            TimeoutError: If dream doesn't complete within timeout
        """
        logger.info(f"Waiting for dream: {dream_id}")

        start_time = time.time()
        poll_count = 0

        while True:
            elapsed = int(time.time() - start_time)

            if elapsed > timeout_seconds:
                raise TimeoutError(f"Dream {dream_id} exceeded {timeout_seconds}s timeout")

            result = self.retrieve_dream(dream_id)
            poll_count += 1

            # Log progress
            status_msg = f"[{elapsed}s, poll #{poll_count}] Status: {result.status.value}"
            if result.input_tokens > 0:
                status_msg += f" | Tokens: {result.input_tokens}"
            logger.info(status_msg)

            # Check if done
            if result.status in (DreamStatus.COMPLETED, DreamStatus.FAILED, DreamStatus.CANCELED):
                result.duration_seconds = elapsed
                return result

            # Wait before next poll
            time.sleep(poll_interval)

    def cancel_dream(self, dream_id: str) -> DreamResult:
        """Cancel a pending or running dream."""
        logger.info(f"Canceling dream: {dream_id}")
        self.client.beta.dreams.cancel(dream_id)

        # Retrieve final state
        result = self.retrieve_dream(dream_id)
        logger.info(f"✓ Dream canceled: {result.status.value}")

        return result

    def archive_dream(self, dream_id: str) -> bool:
        """Archive a completed dream."""
        logger.info(f"Archiving dream: {dream_id}")

        try:
            self.client.beta.dreams.archive(dream_id)
            logger.info(f"✓ Dream archived: {dream_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to archive dream: {e}")
            return False

    def list_dreams(self, include_archived: bool = False, limit: int = 20) -> List[Dict[str, Any]]:
        """List all dreams in the workspace."""
        logger.info(f"Listing dreams (archived: {include_archived})...")

        dreams = self.client.beta.dreams.list(
            include_archived=include_archived,
            limit=limit
        )

        result = [
            {
                "id": d.id,
                "status": d.status,
                "created_at": d.created_at,
                "input_tokens": d.usage.input_tokens
            }
            for d in dreams
        ]

        logger.info(f"Found {len(result)} dreams")
        return result

    def run_dream_workflow(
        self,
        memory_store_id: str,
        session_ids: Optional[List[str]] = None,
        agent_id: Optional[str] = None,
        environment_id: Optional[str] = None,
        model: str = "claude-opus-4-7",
        custom_instructions: Optional[str] = None,
        timeout_seconds: int = 3600
    ) -> Optional[str]:
        """
        Complete end-to-end dream workflow.

        Creates a dream, waits for completion, reviews output, and optionally
        attaches to a new agent session.

        Args:
            memory_store_id: Input memory store
            session_ids: Past sessions to analyze
            agent_id: (Optional) Agent ID for new session
            environment_id: (Optional) Environment ID for new session
            model: Model to use
            custom_instructions: Custom dreaming instructions
            timeout_seconds: Max wait time

        Returns:
            Output memory store ID if successful, None otherwise
        """
        logger.info("🌙 Starting DreamToosa dream workflow...")

        # Create dream
        dream_result = self.create_dream(
            memory_store_id=memory_store_id,
            session_ids=session_ids,
            model=model,
            instructions=custom_instructions
        )

        # Wait for completion
        try:
            final_result = self.wait_for_dream(
                dream_result.dream_id,
                timeout_seconds=timeout_seconds
            )
        except TimeoutError as e:
            logger.error(f"❌ {e}")
            return None

        if final_result.status != DreamStatus.COMPLETED:
            logger.error(f"❌ Dream failed: {final_result.status.value}")
            if final_result.error:
                logger.error(f"   Error: {final_result.error}")
            return None

        # Success!
        output_store_id = final_result.output_store_id
        logger.info(f"✓ Dream completed in {final_result.duration_seconds}s")
        logger.info(f"  Output store: {output_store_id}")

        # Review output
        memories = self.view_memory_store(output_store_id)
        logger.info(f"  Curated {len(memories)} memory entries")

        if memories:
            logger.info("  Sample entries:")
            for entry in memories[:3]:
                value_preview = entry['value'][:50].replace('\n', ' ')
                logger.info(f"    • {entry['key']}: {value_preview}...")

        # Optionally use in new session
        if agent_id and environment_id:
            logger.info(f"\n📍 Attaching curated memory to new session...")
            try:
                session = self.client.beta.sessions.create(
                    agent=agent_id,
                    environment_id=environment_id,
                    resources=[
                        {"type": "memory_store", "memory_store_id": output_store_id}
                    ]
                )
                logger.info(f"✓ New session created: {session.id}")
            except Exception as e:
                logger.error(f"Failed to create session: {e}")

        return output_store_id


# Example usage and testing
if __name__ == "__main__":
    import os

    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    # Initialize manager
    manager = DreamToosaManager(api_key=api_key)

    # Example: List existing memory stores
    print("\n📚 Existing Memory Stores:")
    stores = manager.list_memory_stores()
    for store in stores:
        print(f"  {store['id']}: {store['name']}")

    # Example: Create a new memory store
    # store_id = manager.create_memory_store("DreamToosa Test Store")

    # Example: List existing dreams
    print("\n🌙 Recent Dreams:")
    dreams = manager.list_dreams(limit=5)
    for dream in dreams:
        print(f"  {dream['id']}: {dream['status']} ({dream['input_tokens']} tokens)")

    # Example: Run a complete workflow
    # Uncomment and fill in real IDs to test
    """
    output_store_id = manager.run_dream_workflow(
        memory_store_id="memstore_01...",
        session_ids=["sesn_01...", "sesn_02..."],
        agent_id="agent_01...",
        environment_id="env_01...",
        custom_instructions=(
            "Focus on user preferences and coding patterns. "
            "Merge duplicate technical decisions. "
            "Remove debugging notes."
        )
    )

    if output_store_id:
        print(f"\n✓ Success! Output store: {output_store_id}")
    else:
        print("\n❌ Dream workflow failed")
    """

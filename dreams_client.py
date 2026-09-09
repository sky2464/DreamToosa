"""
Claude Dreams Client: historical remote API reference variant.

Retains an alternative DreamConfig/DreamsClient pair and DreamWorkflow examples
for memory review, session creation, and batch curation through the Anthropic SDK.
These overlap with dreams_implementation.py, the primary remote client reference;
use that module for new remote client work rather than adding another wrapper.

For offline curation and local JSON persistence, use Dreamer and MemoryStore
from dreamtoosa. This module is not used by that package. See
README.md#memory-curation-implementations for the implementation map.
"""

import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from anthropic import Anthropic


@dataclass
class DreamConfig:
    """Configuration for a dream operation"""
    memory_store_id: str
    session_ids: Optional[List[str]] = None
    model: str = "claude-opus-4-7"
    instructions: Optional[str] = None
    poll_interval: int = 10  # seconds
    max_wait_time: int = 3600  # seconds (1 hour)


class DreamsClient:
    """Client for managing Claude Dreams"""

    def __init__(self):
        self.client = Anthropic()

    def create_dream(self, config: DreamConfig) -> str:
        """
        Create a new dream job

        Args:
            config: DreamConfig instance with parameters

        Returns:
            Dream ID (e.g., "drm_01...")
        """
        inputs = [
            {"type": "memory_store", "memory_store_id": config.memory_store_id}
        ]

        if config.session_ids:
            inputs.append({"type": "sessions", "session_ids": config.session_ids})

        dream = self.client.beta.dreams.create(
            inputs=inputs,
            model=config.model,
            instructions=config.instructions,
        )

        print(f"✓ Dream created: {dream.id}")
        print(f"  Status: {dream.status}")
        print(f"  Model: {dream.model.id}")

        return dream.id

    def wait_for_dream(
        self,
        dream_id: str,
        poll_interval: int = 10,
        max_wait_time: int = 3600,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Poll a dream until completion

        Args:
            dream_id: ID of the dream to monitor
            poll_interval: Seconds between polls
            max_wait_time: Maximum seconds to wait
            verbose: Print status updates

        Returns:
            Completed dream resource
        """
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > max_wait_time:
                raise TimeoutError(f"Dream {dream_id} exceeded max wait time")

            dream = self.client.beta.dreams.retrieve(dream_id)

            if verbose:
                print(f"  [{elapsed:.0f}s] Status: {dream.status}")
                print(f"    Input tokens: {dream.usage.input_tokens}")
                print(f"    Output tokens: {dream.usage.output_tokens}")

            if dream.status in ("completed", "failed", "canceled"):
                return dream

            time.sleep(poll_interval)

    def get_dream_output(self, dream: Dict[str, Any]) -> Optional[str]:
        """
        Extract output memory store ID from a completed dream

        Args:
            dream: Completed dream resource

        Returns:
            Output memory store ID, or None if not found
        """
        if dream.status != "completed":
            print(f"⚠ Dream status is {dream.status}, not completed")
            return None

        for output in dream.outputs:
            if output.type == "memory_store":
                return output.memory_store_id

        return None

    def review_memories(self, memory_store_id: str, limit: int = 20) -> List[str]:
        """
        List memories in a store

        Args:
            memory_store_id: ID of memory store to review
            limit: Maximum memories to retrieve

        Returns:
            List of memory contents
        """
        memories = self.client.beta.memory.memories.list(
            memory_store_id=memory_store_id,
            limit=limit
        )

        memory_contents = []
        for i, memory in enumerate(memories.data, 1):
            content = memory.content
            memory_contents.append(content)
            print(f"{i}. {content[:100]}..." if len(content) > 100 else f"{i}. {content}")

        return memory_contents

    def create_session_with_memory(
        self,
        agent_id: str,
        environment_id: str,
        memory_store_id: str
    ) -> str:
        """
        Create a new agent session with curated memory

        Args:
            agent_id: ID of agent
            environment_id: ID of environment
            memory_store_id: ID of memory store to attach

        Returns:
            Session ID
        """
        session = self.client.beta.sessions.create(
            agent=agent_id,
            environment_id=environment_id,
            resources=[
                {"type": "memory_store", "memory_store_id": memory_store_id},
            ],
        )

        print(f"✓ Session created: {session.id}")
        return session.id

    def cancel_dream(self, dream_id: str) -> None:
        """Cancel a pending or running dream"""
        self.client.beta.dreams.cancel(dream_id)
        print(f"✓ Dream {dream_id} canceled")

    def archive_dream(self, dream_id: str) -> None:
        """Archive a completed dream"""
        self.client.beta.dreams.archive(dream_id)
        print(f"✓ Dream {dream_id} archived")

    def list_dreams(self, include_archived: bool = False, limit: int = 20) -> List[Dict]:
        """
        List all dreams

        Args:
            include_archived: Include archived dreams
            limit: Maximum results

        Returns:
            List of dream resources
        """
        dreams = []
        for dream in self.client.beta.dreams.list(
            limit=limit,
            include_archived=include_archived
        ):
            dreams.append(dream)
            status_emoji = {
                "pending": "⏳",
                "running": "🔄",
                "completed": "✓",
                "failed": "✗",
                "canceled": "⊘"
            }.get(dream.status, "?")

            print(f"{status_emoji} {dream.id}: {dream.status}")

        return dreams


class DreamWorkflow:
    """High-level workflow for dreaming and using curated memory"""

    def __init__(self):
        self.client = DreamsClient()

    def full_workflow(
        self,
        memory_store_id: str,
        session_ids: List[str],
        agent_id: str,
        environment_id: str,
        instructions: Optional[str] = None,
        review_memories: bool = True,
        create_session: bool = True
    ) -> Dict[str, Any]:
        """
        Complete dream workflow: create, wait, review, and use

        Args:
            memory_store_id: Memory store to curate
            session_ids: Sessions to analyze (up to 100)
            agent_id: Agent to use curated memory
            environment_id: Environment for new session
            instructions: Custom curation instructions
            review_memories: Show reviewed memories
            create_session: Create new session with output

        Returns:
            Dictionary with results
        """
        print("\n" + "="*60)
        print("CLAUDE DREAMS WORKFLOW")
        print("="*60)

        # Step 1: Create dream
        print("\n[1/4] Creating dream...")
        config = DreamConfig(
            memory_store_id=memory_store_id,
            session_ids=session_ids,
            instructions=instructions
        )
        dream_id = self.client.create_dream(config)

        # Step 2: Wait for completion
        print("\n[2/4] Waiting for dream to complete...")
        dream = self.client.wait_for_dream(dream_id)

        if dream.status != "completed":
            print(f"✗ Dream failed with status: {dream.status}")
            if dream.error:
                print(f"  Error: {dream.error}")
            return {"success": False, "dream_id": dream_id}

        print("✓ Dream completed successfully!")

        # Step 3: Extract and review output
        print("\n[3/4] Reviewing curated memories...")
        output_store_id = self.client.get_dream_output(dream)

        if not output_store_id:
            print("✗ No output memory store found")
            return {"success": False, "dream_id": dream_id}

        print(f"✓ Output store: {output_store_id}\n")

        if review_memories:
            print("Curated memories:")
            self.client.review_memories(output_store_id, limit=10)

        # Step 4: Create session with curated memory
        session_id = None
        if create_session:
            print("\n[4/4] Creating session with curated memory...")
            session_id = self.client.create_session_with_memory(
                agent_id=agent_id,
                environment_id=environment_id,
                memory_store_id=output_store_id
            )

        print("\n" + "="*60)
        print("✓ WORKFLOW COMPLETE")
        print("="*60)

        return {
            "success": True,
            "dream_id": dream_id,
            "output_memory_store_id": output_store_id,
            "session_id": session_id,
            "usage": {
                "input_tokens": dream.usage.input_tokens,
                "output_tokens": dream.usage.output_tokens,
            }
        }

    def batch_dream(
        self,
        memory_store_ids: List[str],
        session_ids_per_store: Dict[str, List[str]],
        instructions: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Run dreams on multiple memory stores

        Args:
            memory_store_ids: List of memory store IDs to curate
            session_ids_per_store: Map of store_id -> [session_ids]
            instructions: Common instructions for all dreams

        Returns:
            List of results for each dream
        """
        print(f"\n🔄 Starting {len(memory_store_ids)} dreams...\n")

        dream_ids = {}

        # Create all dreams
        for store_id in memory_store_ids:
            sessions = session_ids_per_store.get(store_id, [])
            config = DreamConfig(
                memory_store_id=store_id,
                session_ids=sessions if sessions else None,
                instructions=instructions
            )
            dream_id = self.client.create_dream(config)
            dream_ids[dream_id] = store_id

        # Wait for all to complete
        print("\n⏳ Waiting for all dreams to complete...\n")
        results = []

        for dream_id, store_id in dream_ids.items():
            print(f"Monitoring {dream_id} ({store_id})...")
            dream = self.client.wait_for_dream(dream_id, verbose=False)

            if dream.status == "completed":
                output_store_id = self.client.get_dream_output(dream)
                results.append({
                    "input_store_id": store_id,
                    "dream_id": dream_id,
                    "output_store_id": output_store_id,
                    "status": "completed",
                    "tokens": dream.usage.input_tokens + dream.usage.output_tokens
                })
                print(f"  ✓ Completed: {output_store_id}")
            else:
                results.append({
                    "input_store_id": store_id,
                    "dream_id": dream_id,
                    "status": dream.status,
                    "error": str(dream.error) if dream.error else None
                })
                print(f"  ✗ Failed: {dream.status}")

        return results


# Example usage
if __name__ == "__main__":
    # Initialize clients
    client = DreamsClient()
    workflow = DreamWorkflow()

    # Example 1: Simple dream creation
    print("Example 1: Create and monitor a dream")
    print("-" * 40)

    # You would replace these with real IDs
    # dream_id = client.create_dream(
    #     DreamConfig(
    #         memory_store_id="memstore_01...",
    #         session_ids=["sesn_01...", "sesn_02..."],
    #         instructions="Focus on user preferences"
    #     )
    # )

    # dream = client.wait_for_dream(dream_id)
    # output_store = client.get_dream_output(dream)
    # client.review_memories(output_store)

    print("✓ Dreams client ready to use")
    print("\nUsage:")
    print("  1. Replace placeholder IDs with your actual IDs")
    print("  2. Create DreamConfig with your parameters")
    print("  3. Call client.create_dream(config)")
    print("  4. Monitor with client.wait_for_dream(dream_id)")
    print("  5. Review output with client.review_memories(store_id)")

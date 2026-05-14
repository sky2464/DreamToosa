#!/usr/bin/env python3
"""
Claude Dreams Example - Memory Curation Workflow

This script demonstrates how to:
1. Create a memory store
2. Run a dream to curate and organize memories
3. Monitor progress
4. Use the curated output

To use this script:
1. Set your ANTHROPIC_API_KEY environment variable
2. Update agent_id, environment_id, and session_ids below
3. Run: python3 dream_example.py
"""

import os
import time
import json
from typing import Optional
from anthropic import Anthropic


class DreamOrchestrator:
    """Helper class to manage Claude Dreams workflow"""

    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic(api_key=api_key)

    def create_memory_store(self) -> str:
        """Create a new empty memory store"""
        store = self.client.beta.memory_stores.create()
        print(f"✓ Created memory store: {store.id}")
        return store.id

    def write_sample_memories(self, store_id: str):
        """Add sample memories to a store (for demo purposes)"""
        memories = [
            "User prefers Python over TypeScript for backend work",
            "Project uses Claude API with managed agents",
            "Team standup is every Monday at 10am PST",
            "Database is PostgreSQL hosted on AWS RDS",
            "User prefers Python over TypeScript for backend work",  # Duplicate
            "CI/CD pipeline uses GitHub Actions",
            "Deployment target is Kubernetes on EKS",
            "User strongly dislikes slow feedback loops",
        ]

        for memory in memories:
            self.client.beta.memory_stores.write_memory(
                store_id,
                body=[{"type": "memory", "content": memory}]
            )

        print(f"✓ Added {len(memories)} sample memories (including duplicates)")
        return memories

    def list_memories(self, store_id: str, limit: int = 10) -> list:
        """List memories from a store"""
        memories = self.client.beta.memory_stores.list_memories(store_id, limit=limit)
        return memories

    def create_dream(
        self,
        memory_store_id: str,
        session_ids: Optional[list[str]] = None,
        instructions: Optional[str] = None,
        model: str = "claude-opus-4-7"
    ) -> str:
        """Create a dream"""
        inputs = [
            {"type": "memory_store", "memory_store_id": memory_store_id}
        ]

        if session_ids:
            inputs.append({
                "type": "sessions",
                "session_ids": session_ids[:100]  # Max 100 sessions
            })

        dream = self.client.beta.dreams.create(
            inputs=inputs,
            model=model,
            instructions=instructions or "Consolidate, deduplicate, and organize all memories. Focus on patterns and insights."
        )

        print(f"✓ Dream created: {dream.id}")
        print(f"  Model: {dream.model.id}")
        print(f"  Status: {dream.status}")

        return dream.id

    def wait_for_dream(
        self,
        dream_id: str,
        poll_interval: int = 5,
        max_wait: int = 600,
        verbose: bool = True
    ) -> dict:
        """Poll dream until completion"""
        start_time = time.time()
        last_status = None

        while True:
            dream = self.client.beta.dreams.retrieve(dream_id)

            # Only print on status change to avoid spam
            if dream.status != last_status or dream.status == "running":
                if verbose:
                    print(f"  Status: {dream.status}", end="")
                    if dream.usage.input_tokens > 0 or dream.usage.output_tokens > 0:
                        print(f" | Tokens: {dream.usage.input_tokens} in, {dream.usage.output_tokens} out", end="")
                    print()
                last_status = dream.status

            # Check for completion
            if dream.status == "completed":
                if verbose:
                    print(f"✓ Dream completed successfully")
                    print(f"  Total tokens: {dream.usage.input_tokens} input, {dream.usage.output_tokens} output")
                return dream

            elif dream.status in ("failed", "canceled"):
                if verbose:
                    print(f"✗ Dream {dream.status}: {dream.error}")
                return dream

            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > max_wait:
                raise TimeoutError(f"Dream exceeded {max_wait}s timeout")

            time.sleep(poll_interval)

    def get_output_store(self, dream: dict) -> Optional[str]:
        """Extract output memory store ID from dream"""
        for output in dream.outputs:
            if output.type == "memory_store":
                return output.memory_store_id
        return None

    def compare_stores(self, input_store_id: str, output_store_id: str, limit: int = 5):
        """Compare input and output memory stores"""
        print("\n" + "="*60)
        print("COMPARISON: Input vs Output Memory Stores")
        print("="*60)

        input_memories = list(self.client.beta.memory_stores.list_memories(input_store_id, limit=limit))
        output_memories = list(self.client.beta.memory_stores.list_memories(output_store_id, limit=limit))

        print(f"\nInput Store ({input_store_id}):")
        print(f"  Sample memories ({len(input_memories)} shown):")
        for i, mem in enumerate(input_memories, 1):
            content = mem.content[:80] + "..." if len(mem.content) > 80 else mem.content
            print(f"    {i}. {content}")

        print(f"\nOutput Store ({output_store_id}):")
        print(f"  Sample memories ({len(output_memories)} shown):")
        for i, mem in enumerate(output_memories, 1):
            content = mem.content[:80] + "..." if len(mem.content) > 80 else mem.content
            print(f"    {i}. {content}")

        print(f"\nObservations:")
        print(f"  - Input count: {len(input_memories)} (showing {len(input_memories)})")
        print(f"  - Output count: {len(output_memories)} (showing {len(output_memories)})")
        print(f"  - Duplicates removed: Input had duplicates that may be consolidated")

    def run_demo(self):
        """Run a complete demo of the dreaming workflow"""
        print("Claude Dreams Demo")
        print("="*60)

        # Step 1: Create memory store
        print("\n[1] Creating memory store...")
        memory_store_id = self.create_memory_store()

        # Step 2: Add sample memories
        print("\n[2] Adding sample memories...")
        memories = self.write_sample_memories(memory_store_id)

        # Step 3: Show initial state
        print("\n[3] Current memories in store:")
        current_memories = self.list_memories(memory_store_id)
        for i, mem in enumerate(current_memories, 1):
            print(f"    {i}. {mem.content}")

        # Step 4: Create dream
        print("\n[4] Creating dream (without sessions for this demo)...")
        instructions = """
        Remove duplicate entries about programming language preferences.
        Consolidate all memories into clear, non-redundant statements.
        Extract any insights about user patterns.
        """
        dream_id = self.create_dream(
            memory_store_id=memory_store_id,
            instructions=instructions
        )

        # Step 5: Wait for dream
        print("\n[5] Waiting for dream to complete...")
        print("     (This may take 1-5 minutes depending on memory size)")
        dream = self.wait_for_dream(dream_id, poll_interval=5, max_wait=600)

        if dream.status != "completed":
            print(f"✗ Dream failed with status: {dream.status}")
            if dream.error:
                print(f"  Error: {dream.error}")
            return

        # Step 6: Get output store
        print("\n[6] Extracting output memory store...")
        output_store_id = self.get_output_store(dream)
        if not output_store_id:
            print("✗ No output memory store found")
            return

        print(f"✓ Output store: {output_store_id}")

        # Step 7: Compare
        print("\n[7] Comparing input and output stores...")
        self.compare_stores(memory_store_id, output_store_id, limit=10)

        # Step 8: Archive dream
        print("\n[8] Archiving dream...")
        self.client.beta.dreams.archive(dream_id)
        print(f"✓ Dream archived: {dream_id}")

        print("\n" + "="*60)
        print("Demo complete!")
        print("\nNext steps:")
        print(f"1. Use output store {output_store_id} in your agent sessions")
        print("2. Clean up by archiving or deleting unused stores")
        print("3. Scale up to process sessions from real agent runs")


def main():
    """Run the demo"""
    try:
        orchestrator = DreamOrchestrator()
        orchestrator.run_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise


if __name__ == "__main__":
    main()

"""
High-level Claude Dreams workflows built on the canonical remote client.

Uses DreamConfig and DreamsClient from dreams_implementation.py only.
"""

from typing import Any, Dict, List, Optional

from dreams_implementation import DreamConfig, DreamsClient


class DreamWorkflow:
    """High-level workflow for dreaming and using curated memory."""

    def __init__(self, client: Optional[DreamsClient] = None):
        self.client = client or DreamsClient()

    def full_workflow(
        self,
        memory_store_id: str,
        session_ids: List[str],
        agent_id: str,
        environment_id: str,
        instructions: Optional[str] = None,
        review_memories: bool = True,
        create_session: bool = True,
    ) -> Dict[str, Any]:
        print("\n" + "=" * 60)
        print("CLAUDE DREAMS WORKFLOW")
        print("=" * 60)

        print("\n[1/4] Creating dream...")
        config = DreamConfig(
            memory_store_id=memory_store_id,
            session_ids=session_ids,
            instructions=instructions,
        )
        dream_id = self.client.create_dream(config)

        print("\n[2/4] Waiting for dream to complete...")
        dream = self.client.wait_for_dream(dream_id)

        if dream.status != "completed":
            print(f"✗ Dream failed with status: {dream.status}")
            if getattr(dream, "error", None):
                print(f"  Error: {dream.error}")
            return {"success": False, "dream_id": dream_id}

        print("✓ Dream completed successfully!")

        print("\n[3/4] Reviewing curated memories...")
        output_store_id = self.client.get_dream_output(dream)

        if not output_store_id:
            print("✗ No output memory store found")
            return {"success": False, "dream_id": dream_id}

        print(f"✓ Output store: {output_store_id}\n")

        if review_memories:
            print("Curated memories:")
            self.client.review_memories(output_store_id, limit=10)

        session_id = None
        if create_session:
            print("\n[4/4] Creating session with curated memory...")
            session_id = self.client.create_session_with_memory(
                agent_id=agent_id,
                environment_id=environment_id,
                memory_store_id=output_store_id,
            )

        print("\n" + "=" * 60)
        print("✓ WORKFLOW COMPLETE")
        print("=" * 60)

        return {
            "success": True,
            "dream_id": dream_id,
            "output_memory_store_id": output_store_id,
            "session_id": session_id,
            "usage": {
                "input_tokens": dream.usage.input_tokens,
                "output_tokens": dream.usage.output_tokens,
            },
        }

    def batch_dream(
        self,
        memory_store_ids: List[str],
        session_ids_per_store: Dict[str, List[str]],
        instructions: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        print(f"\n🔄 Starting {len(memory_store_ids)} dreams...\n")

        dream_ids: Dict[str, str] = {}

        for store_id in memory_store_ids:
            sessions = session_ids_per_store.get(store_id, [])
            config = DreamConfig(
                memory_store_id=store_id,
                session_ids=sessions if sessions else None,
                instructions=instructions,
            )
            dream_id = self.client.create_dream(config)
            dream_ids[dream_id] = store_id

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
                    "tokens": dream.usage.input_tokens + dream.usage.output_tokens,
                })
                print(f"  ✓ Completed: {output_store_id}")
            else:
                results.append({
                    "input_store_id": store_id,
                    "dream_id": dream_id,
                    "status": dream.status,
                    "error": str(dream.error) if dream.error else None,
                })
                print(f"  ✗ Failed: {dream.status}")

        return results

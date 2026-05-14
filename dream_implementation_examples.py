"""
Claude Dream Implementation Examples
Quick reference code patterns for using Claude Dream API
"""

from anthropic import Anthropic
import time
from typing import Optional

client = Anthropic()


# ============================================================================
# BASIC EXAMPLE: Create and monitor a dream
# ============================================================================

def basic_dream_example(memory_store_id: str) -> Optional[str]:
    """
    Create a dream to curate a memory store.

    Args:
        memory_store_id: Existing memory store ID to curate

    Returns:
        Output memory store ID if successful, None if failed
    """
    # Create the dream
    dream = client.beta.dreams.create(
        inputs=[
            {"type": "memory_store", "memory_store_id": memory_store_id},
        ],
        model="claude-opus-4-7",
    )

    print(f"Dream created: {dream.id}")
    print(f"Initial status: {dream.status}")

    # Poll until completion
    while dream.status in ("pending", "running"):
        time.sleep(10)
        dream = client.beta.dreams.retrieve(dream.id)
        print(f"Status: {dream.status}, Tokens: {dream.usage.output_tokens}")

    # Check result
    if dream.status == "completed":
        output_store_id = next(
            output.memory_store_id
            for output in dream.outputs
            if output.type == "memory_store"
        )
        print(f"Success! Output store: {output_store_id}")
        return output_store_id
    else:
        print(f"Dream failed: {dream.error}")
        return None


# ============================================================================
# INTERMEDIATE EXAMPLE: Dream with sessions and instructions
# ============================================================================

def dream_with_guidance(
    memory_store_id: str,
    session_ids: list[str],
    instructions: str
) -> Optional[str]:
    """
    Create a dream with custom instructions and session analysis.

    Args:
        memory_store_id: Memory store to curate
        session_ids: Up to 100 session IDs to analyze
        instructions: Guidance for the dream (max 4,096 chars)

    Returns:
        Output memory store ID or None
    """
    # Validate inputs
    if len(session_ids) > 100:
        raise ValueError("Maximum 100 sessions per dream")

    if len(instructions) > 4096:
        raise ValueError("Instructions limited to 4,096 characters")

    # Create dream with guidance
    dream = client.beta.dreams.create(
        inputs=[
            {"type": "memory_store", "memory_store_id": memory_store_id},
            {"type": "sessions", "session_ids": session_ids},
        ],
        model="claude-opus-4-7",
        instructions=instructions,
    )

    print(f"Dream created with {len(session_ids)} sessions")
    print(f"Instructions: {instructions[:50]}...")

    # Poll with progress reporting
    while dream.status != "completed":
        if dream.status == "failed":
            print(f"Dream failed: {dream.error.type} - {dream.error}")
            return None

        time.sleep(5)
        dream = client.beta.dreams.retrieve(dream.id)

        # Show progress
        if dream.status == "running":
            progress = (dream.usage.output_tokens / 1000) * 100
            print(f"Running... {dream.usage.output_tokens} output tokens ({progress:.1f}%)")

    # Extract and return output
    output_store_id = next(
        output.memory_store_id
        for output in dream.outputs
        if output.type == "memory_store"
    )

    return output_store_id


# ============================================================================
# ADVANCED EXAMPLE: Real-time monitoring with session events
# ============================================================================

def dream_with_realtime_monitoring(
    memory_store_id: str,
    session_ids: list[str],
) -> Optional[str]:
    """
    Create a dream and watch its underlying session in real-time.

    Args:
        memory_store_id: Memory store to curate
        session_ids: Sessions to analyze

    Returns:
        Output memory store ID or None
    """
    # Create dream
    dream = client.beta.dreams.create(
        inputs=[
            {"type": "memory_store", "memory_store_id": memory_store_id},
            {"type": "sessions", "session_ids": session_ids},
        ],
        model="claude-opus-4-7",
    )

    print(f"Dream {dream.id} created")

    # Wait for it to start running
    while dream.status == "pending":
        time.sleep(2)
        dream = client.beta.dreams.retrieve(dream.id)

    if dream.status != "running":
        print(f"Dream failed before running: {dream.error}")
        return None

    # Now stream the underlying session events
    print(f"Dream is running. Monitoring session: {dream.session_id}")

    event_count = 0
    try:
        # Stream events from the dream's internal session
        for event in client.beta.sessions.stream_events(dream.session_id):
            event_count += 1

            # Print interesting event types
            if event.type in ("message", "tool_use", "content_block_stop"):
                print(f"Event {event_count}: {event.type}")

            # Stop streaming once dream completes
            dream = client.beta.dreams.retrieve(dream.id)
            if dream.status in ("completed", "failed", "canceled"):
                break
    except StopIteration:
        pass

    # Get final result
    dream = client.beta.dreams.retrieve(dream.id)

    if dream.status == "completed":
        output_store_id = next(
            output.memory_store_id
            for output in dream.outputs
            if output.type == "memory_store"
        )
        print(f"Dream complete! {event_count} events observed")
        print(f"Output store: {output_store_id}")
        return output_store_id
    else:
        print(f"Dream failed: {dream.error}")
        return None


# ============================================================================
# PRODUCTION EXAMPLE: Safe workflow with validation
# ============================================================================

def safe_dream_workflow(
    memory_store_id: str,
    agent_id: str,
    environment_id: str,
    session_ids: list[str] = None,
    dry_run: bool = False,
) -> bool:
    """
    Production-ready dream workflow with error handling and validation.

    Args:
        memory_store_id: Memory store to curate
        agent_id: Agent to attach curated memory to
        environment_id: Environment for new session
        session_ids: Sessions to analyze (default: auto-fetch last 20)
        dry_run: If True, don't create session with output (just validate)

    Returns:
        True if successful, False otherwise
    """

    print("=" * 60)
    print("CLAUDE DREAM SAFE WORKFLOW")
    print("=" * 60)

    # Step 1: Validate inputs
    print("\n1. Validating inputs...")
    if not memory_store_id.startswith("memstore_"):
        print("ERROR: Invalid memory store ID")
        return False

    if session_ids is None:
        session_ids = []
        print("   No sessions specified (optional)")
    elif len(session_ids) > 100:
        print("ERROR: Maximum 100 sessions allowed")
        return False
    else:
        print(f"   Sessions to analyze: {len(session_ids)}")

    # Step 2: Create dream
    print("\n2. Creating dream...")
    try:
        dream = client.beta.dreams.create(
            inputs=[
                {"type": "memory_store", "memory_store_id": memory_store_id},
                {"type": "sessions", "session_ids": session_ids},
            ] if session_ids else [
                {"type": "memory_store", "memory_store_id": memory_store_id},
            ],
            model="claude-opus-4-7",
            instructions="Merge duplicates and surface new patterns.",
        )
        print(f"   Dream ID: {dream.id}")
    except Exception as e:
        print(f"ERROR creating dream: {e}")
        return False

    # Step 3: Monitor progress
    print("\n3. Monitoring progress...")
    max_wait_seconds = 600  # 10 minute timeout
    start_time = time.time()

    while dream.status in ("pending", "running"):
        elapsed = time.time() - start_time
        if elapsed > max_wait_seconds:
            print(f"ERROR: Dream exceeded {max_wait_seconds}s timeout")
            client.beta.dreams.cancel(dream.id)
            return False

        time.sleep(10)
        dream = client.beta.dreams.retrieve(dream.id)
        print(f"   [{elapsed:.0f}s] Status: {dream.status}")

    # Step 4: Check result
    print("\n4. Checking result...")
    if dream.status == "failed":
        print(f"ERROR: Dream failed with {dream.error.type}")
        print(f"       {dream.error}")
        return False

    if dream.status == "canceled":
        print("ERROR: Dream was canceled")
        return False

    if dream.status != "completed":
        print(f"ERROR: Unexpected status {dream.status}")
        return False

    # Step 5: Extract output
    print("\n5. Extracting output...")
    try:
        output_store_id = next(
            output.memory_store_id
            for output in dream.outputs
            if output.type == "memory_store"
        )
        print(f"   Output store: {output_store_id}")
    except StopIteration:
        print("ERROR: No memory store in dream outputs")
        return False

    # Step 6: Optional - Create session with curated memory
    if not dry_run:
        print("\n6. Creating session with curated memory...")
        try:
            session = client.beta.sessions.create(
                agent=agent_id,
                environment_id=environment_id,
                resources=[
                    {"type": "memory_store", "memory_store_id": output_store_id},
                ],
            )
            print(f"   Session created: {session.id}")
        except Exception as e:
            print(f"ERROR creating session: {e}")
            return False

    print("\n" + "=" * 60)
    print("SUCCESS: Dream workflow completed")
    print("=" * 60)
    return True


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def list_dreams(include_archived: bool = False) -> list[dict]:
    """List all dreams (or include archived)."""
    dreams = []
    for dream in client.beta.dreams.list(limit=100, include_archived=include_archived):
        dreams.append({
            "id": dream.id,
            "status": dream.status,
            "created_at": dream.created_at,
            "model": dream.model.id,
        })
    return dreams


def cancel_dream(dream_id: str) -> bool:
    """Cancel a pending or running dream."""
    try:
        client.beta.dreams.cancel(dream_id)
        print(f"Canceled dream: {dream_id}")
        return True
    except Exception as e:
        print(f"Error canceling dream: {e}")
        return False


def archive_dream(dream_id: str) -> bool:
    """Archive a completed dream (hides from default list)."""
    try:
        client.beta.dreams.archive(dream_id)
        print(f"Archived dream: {dream_id}")
        return True
    except Exception as e:
        print(f"Error archiving dream: {e}")
        return False


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Replace with your actual IDs
    MEMORY_STORE_ID = "memstore_01ABC..."
    AGENT_ID = "agent_01XYZ..."
    ENVIRONMENT_ID = "env_01XYZ..."
    SESSION_IDS = ["sesn_01...", "sesn_02..."]  # Optional

    # Choose your example:

    # 1. Basic workflow
    # output_store = basic_dream_example(MEMORY_STORE_ID)

    # 2. With sessions and guidance
    # output_store = dream_with_guidance(
    #     MEMORY_STORE_ID,
    #     SESSION_IDS,
    #     "Focus on recent technical preferences; ignore one-off notes."
    # )

    # 3. Real-time monitoring
    # output_store = dream_with_realtime_monitoring(MEMORY_STORE_ID, SESSION_IDS)

    # 4. Production-safe workflow (recommended)
    # success = safe_dream_workflow(
    #     MEMORY_STORE_ID,
    #     AGENT_ID,
    #     ENVIRONMENT_ID,
    #     SESSION_IDS,
    #     dry_run=False,  # Set to True to just validate
    # )

    # 5. List dreams
    # dreams = list_dreams(include_archived=False)
    # for dream in dreams:
    #     print(f"{dream['id']}: {dream['status']}")

    pass

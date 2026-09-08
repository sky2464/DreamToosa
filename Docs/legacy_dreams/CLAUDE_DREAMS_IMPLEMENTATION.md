# Claude Dreams Implementation Guide

## Overview

Claude Dreams is a managed agents feature that allows Claude to reflect on past sessions and curate agent memory. It automatically deduplicates, reorganizes, and enhances memory stores by analyzing past session transcripts.

### Key Capabilities
- **Memory deduplication**: Merges duplicate entries across sessions
- **Stale data cleanup**: Replaces outdated information with latest values
- **Pattern extraction**: Surfaces new insights from past sessions
- **Non-destructive**: Input stores are never modified—output is a new store

---

## How It Works

### The Dreaming Pipeline

A dream is an asynchronous job that takes:

1. **Input Memory Store**: A pre-existing memory store to verify and reorganize
2. **Sessions (Optional)**: Up to 100 past session transcripts to analyze for patterns
3. **Instructions (Optional)**: Custom guidance to focus the dream on specific aspects

The dream produces an **output memory store** as a separate resource.

### Lifecycle States

| Status | Meaning |
|--------|---------|
| `pending` | Dream queued and ready to run |
| `running` | Pipeline is actively processing |
| `completed` | Successfully finished; output store ready |
| `failed` | Terminated with error; partial output available |
| `canceled` | User-canceled; partial output available |

---

## Implementation Requirements

### Prerequisites

1. **Managed Agents API**: Must have access to the beta API
2. **Beta Headers**: 
   - `managed-agents-2026-04-01`
   - `dreaming-2026-04-21`
3. **Model Support**: `claude-opus-4-7` or `claude-sonnet-4-6`
4. **Memory Store**: Must already exist or create one before dreaming

### Setup Steps

```python
from anthropic import Anthropic

# Initialize client (SDK automatically includes beta headers)
client = Anthropic()

# Your agent and environment IDs
agent_id = "your-agent-id"
environment_id = "your-environment-id"
```

---

## Python Implementation

### 1. Create a Memory Store (if needed)

```python
# Create an empty memory store if you don't have one
memory_store = client.beta.memory_stores.create()
store_id = memory_store.id
print(f"Created memory store: {store_id}")
```

### 2. Create a Dream

```python
import time

# Create a dream with existing memory store and sessions
dream = client.beta.dreams.create(
    inputs=[
        {"type": "memory_store", "memory_store_id": store_id},
        {"type": "sessions", "session_ids": [
            "sesn_01...",  # Past session ID 1
            "sesn_02...",  # Past session ID 2
            # Up to 100 sessions
        ]},
    ],
    model="claude-opus-4-7",  # or claude-sonnet-4-6
    instructions="Focus on coding preferences and patterns. Ignore one-off debugging notes.",
)

print(f"Dream created: {dream.id}")
print(f"Status: {dream.status}")
```

### 3. Monitor Progress

```python
def wait_for_dream(dream_id, poll_interval=10, max_wait=600):
    """Poll dream status until completion"""
    start_time = time.time()
    
    while True:
        dream = client.beta.dreams.retrieve(dream_id)
        print(f"Dream {dream_id}: {dream.status}")
        print(f"  Tokens used: {dream.usage.input_tokens} input, {dream.usage.output_tokens} output")
        
        if dream.status in ("completed", "failed", "canceled"):
            return dream
        
        if time.time() - start_time > max_wait:
            raise TimeoutError(f"Dream exceeded {max_wait}s timeout")
        
        time.sleep(poll_interval)

# Wait for the dream to complete
completed_dream = wait_for_dream(dream.id)
```

### 4. Use the Output

```python
# Extract the output memory store
output_store_id = next(
    (output.memory_store_id 
     for output in completed_dream.outputs 
     if output.type == "memory_store"),
    None
)

if output_store_id:
    print(f"Output memory store: {output_store_id}")
    
    # Option 1: Use in future sessions
    session = client.beta.sessions.create(
        agent=agent_id,
        environment_id=environment_id,
        resources=[
            {"type": "memory_store", "memory_store_id": output_store_id},
        ],
    )
    print(f"New session created with curated memory: {session.id}")
    
    # Option 2: Review the curated memories
    memories = client.beta.memory_stores.list_memories(output_store_id)
    for memory in memories:
        print(f"Memory: {memory.content}")
    
    # Option 3: Archive if not needed
    # client.beta.memory_stores.archive(output_store_id)
```

---

## Advanced Usage

### Watch the Dream in Real Time

```python
def stream_dream_progress(dream_id):
    """Stream events from the underlying session"""
    dream = client.beta.dreams.retrieve(dream_id)
    
    # Get the session running the dream
    if dream.session_id:
        # Stream events from the dream's session
        for event in client.beta.sessions.stream_events(dream.session_id):
            print(f"Event: {event.type}")
            if event.type == "message":
                print(f"  Message: {event.message.content}")

# Use while dream is running
stream_dream_progress(dream.id)
```

### Cancel a Dream

```python
# Cancel a pending or running dream
client.beta.dreams.cancel(dream.id)
print(f"Canceled dream {dream.id}")
```

### Archive a Dream

```python
# Archive a completed/failed/canceled dream
client.beta.dreams.archive(dream.id)
print(f"Archived dream {dream.id}")

# Later queries won't include archived dreams
dreams = client.beta.dreams.list(limit=20)

# To see archived dreams
dreams_with_archived = client.beta.dreams.list(
    limit=20,
    include_archived=True
)
```

### List All Dreams

```python
# Get all non-archived dreams
for dream in client.beta.dreams.list(limit=100):
    print(f"{dream.id}: {dream.status}")
```

---

## Complete Example: Memory Curation Workflow

```python
from anthropic import Anthropic
import time

def curate_agent_memory(
    agent_id: str,
    environment_id: str,
    memory_store_id: str,
    session_ids: list[str],
    focus_instructions: str = None
) -> str:
    """
    Curate an agent's memory by analyzing past sessions.
    
    Returns: ID of the output memory store
    """
    client = Anthropic()
    
    # 1. Create the dream
    dream = client.beta.dreams.create(
        inputs=[
            {"type": "memory_store", "memory_store_id": memory_store_id},
            {"type": "sessions", "session_ids": session_ids[:100]},  # Max 100
        ],
        model="claude-opus-4-7",
        instructions=focus_instructions or "Clean up and reorganize all memories.",
    )
    print(f"✓ Dream created: {dream.id}")
    
    # 2. Wait for completion
    while True:
        dream = client.beta.dreams.retrieve(dream.id)
        
        if dream.status == "running":
            print(f"  Processing... ({dream.usage.input_tokens} input tokens)")
            time.sleep(10)
        elif dream.status == "completed":
            print(f"✓ Dream completed")
            break
        elif dream.status == "failed":
            raise Exception(f"Dream failed: {dream.error}")
        elif dream.status == "canceled":
            raise Exception("Dream was canceled")
    
    # 3. Extract output
    output_store_id = next(
        (output.memory_store_id 
         for output in dream.outputs 
         if output.type == "memory_store"),
        None
    )
    
    if not output_store_id:
        raise Exception("No output memory store found")
    
    print(f"✓ Output memory store: {output_store_id}")
    
    # 4. Optionally review before using
    print("\nSample memories from output store:")
    memories = client.beta.memory_stores.list_memories(output_store_id, limit=5)
    for memory in memories:
        print(f"  - {memory.content[:100]}...")
    
    return output_store_id

# Usage
if __name__ == "__main__":
    # Collect session IDs from your agent's history
    session_ids = ["sesn_01...", "sesn_02..."]  # Your past sessions
    
    new_memory_store = curate_agent_memory(
        agent_id="your-agent-id",
        environment_id="your-environment-id",
        memory_store_id="memstore_01...",
        session_ids=session_ids,
        focus_instructions="Prioritize user preferences and system patterns. Consolidate duplicate entries.",
    )
    
    print(f"\n✓ Ready to use memory store: {new_memory_store}")
```

---

## TypeScript Implementation

```typescript
import Anthropic from "@anthropic-ai/sdk";

async function createAndWaitForDream(
  client: Anthropic,
  storeId: string,
  sessionIds: string[]
): Promise<string> {
  // Create dream
  const dream = await client.beta.dreams.create({
    inputs: [
      { type: "memory_store", memory_store_id: storeId },
      { type: "sessions", session_ids: sessionIds },
    ],
    model: "claude-opus-4-7",
    instructions: "Consolidate and organize all memories.",
  });

  console.log(`Dream created: ${dream.id}`);

  // Poll until complete
  let currentDream = dream;
  while (currentDream.status === "pending" || currentDream.status === "running") {
    await new Promise((resolve) => setTimeout(resolve, 10000));
    currentDream = await client.beta.dreams.retrieve(dream.id);
    console.log(`Status: ${currentDream.status}`);
  }

  if (currentDream.status === "failed") {
    throw new Error(`Dream failed: ${currentDream.error}`);
  }

  // Get output store ID
  const outputStore = currentDream.outputs.find(
    (o) => o.type === "memory_store"
  );
  if (!outputStore || !("memory_store_id" in outputStore)) {
    throw new Error("No output memory store found");
  }

  return outputStore.memory_store_id;
}

// Usage
const client = new Anthropic();
const outputStoreId = await createAndWaitForDream(
  client,
  "memstore_01...",
  ["sesn_01...", "sesn_02..."]
);
console.log(`Curated memory store: ${outputStoreId}`);
```

---

## Billing & Performance

### Cost Estimation

Dreams are billed at standard API token rates. Example:
- Analyzing 10 sessions (avg 5K tokens each) + 500KB memory store
- Expected input: ~100K tokens
- At $3/M tokens (Opus): ~$0.30 per dream

### Performance Characteristics

| Factor | Impact |
|--------|--------|
| # of Sessions | Linear scaling; 10 sessions ~2-5 min |
| Memory Store Size | Moderate impact; <1MB is fast |
| Model | Opus is slower but higher quality |

**Recommendation**: Start with 5-10 sessions and scale up as needed.

---

## Error Handling

### Common Errors

```python
try:
    dream = client.beta.dreams.create(...)
except Exception as e:
    error_type = str(e)
    
    if "input_memory_store_too_large" in error_type:
        print("Memory store exceeds size limit")
    elif "memory_store_org_limit_exceeded" in error_type:
        print("Organization hit memory store cap")
    elif "timeout" in error_type:
        print("Dream took too long to process")
    else:
        print(f"Unknown error: {e}")
```

---

## Best Practices

1. **Start Small**: Begin with 5-10 sessions; verify quality before scaling
2. **Custom Instructions**: Use `instructions` to guide curation (e.g., ignore debugging notes)
3. **Review Output**: Always review curated memory before using in production
4. **Archive Aggressively**: Archive completed dreams to keep workspace clean
5. **Batch Dreams**: Group related sessions together for better consolidation
6. **Monitor Tokens**: Watch `usage` stats to estimate costs

---

## Resources

- [Managed Agents API Docs](https://platform.claude.com/docs/en/managed-agents/overview)
- [Memory Stores API](https://platform.claude.com/docs/en/managed-agents/memory)
- [Dreams Research Preview Form](https://claude.com/form/claude-managed-agents)
- [Session Streams & Events](https://platform.claude.com/docs/en/managed-agents/events-and-streaming)

---

## Limitations & Constraints

| Constraint | Value |
|-----------|-------|
| Max sessions per dream | 100 |
| Max instructions length | 4,096 characters |
| Supported models | Opus 4.7, Sonnet 4.6 |
| Input store size limit | ~50MB (approximately) |
| Rate limits | Standard API limits apply |

---

## Next Steps

1. **Request Access**: Apply for research preview at [claude.com/form](https://claude.com/form/claude-managed-agents)
2. **Create Memory Store**: Set up a memory store for your agent
3. **Collect Sessions**: Gather 5-10 representative past sessions
4. **Run Your First Dream**: Use the Python/TypeScript examples above
5. **Iterate**: Refine `instructions` based on results
6. **Deploy**: Integrate curated memory into production agent sessions


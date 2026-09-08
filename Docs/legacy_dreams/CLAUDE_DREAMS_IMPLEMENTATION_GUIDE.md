# Claude Dreams Implementation Guide

## Overview

**Claude Dreams** is a Research Preview feature for Managed Agents that allows agents to reflect on past sessions and curate their memory stores. Dreams clean up accumulated data by deduplicating entries, replacing stale information, and surfacing new insights from session transcripts.

---

## How Claude Dreams Works

### The Problem Dreams Solve

As agents interact across many sessions, their memory stores accumulate:
- **Duplicates**: Same information recorded multiple times
- **Contradictions**: Conflicting information that needs reconciliation
- **Stale entries**: Outdated information that should be replaced
- **Missed patterns**: Insights that could be extracted from multiple sessions

### The Solution: Dreams

A dream is an **asynchronous job** that:

1. **Reads** an existing memory store
2. **Analyzes** up to 100 past session transcripts
3. **Produces** a new, reorganized output memory store with:
   - Merged duplicates
   - Contradictions resolved
   - Stale entries replaced with current values
   - New insights surfaced from patterns across sessions

### Key Principle

**The input store is never modified.** You review the output and decide whether to use it, discard it, or iterate.

---

## Core Concepts

### Memory Store
- Persistent key-value storage for agent context
- Created separately from dreams
- Can be attached to future sessions as a resource

### Dream Inputs
- **Primary input**: A pre-existing memory store (required)
- **Secondary input**: Up to 100 session transcripts (optional)
  - Sessions provide context for pattern recognition
  - Dreams can run on just a memory store alone

### Dream Output
- New memory store (separate from input)
- Fully populated with curated data
- Can be reviewed, used, or discarded
- Lives independently in your workspace

### Dream Lifecycle

| Status | Meaning |
|--------|---------|
| `pending` | Dream created, queued for processing |
| `running` | Pipeline actively processing (usage updates in real-time) |
| `completed` | Finished successfully; outputs available |
| `failed` | Terminated with error; partial output may exist |
| `canceled` | User canceled; partial output may exist |

---

## API Requirements

All requests need beta headers:
```
managed-agents-2026-04-01  (Managed Agents API)
dreaming-2026-04-21        (Dreams feature)
```

The SDK handles these automatically.

---

## Implementation Guide

### Step 1: Create a Memory Store (if needed)

```python
from anthropic import Anthropic

client = Anthropic()

# Create an empty memory store (dreams will populate it)
store = client.beta.memory_stores.create(name="Agent Memory")
store_id = store.id
print(f"Created memory store: {store_id}")
```

### Step 2: Collect Session Data

Gather past session IDs that contain relevant agent activity:

```python
# Example: Get sessions from your workspace
sessions = client.beta.sessions.list(limit=100)
session_ids = [session.id for session in sessions]
print(f"Found {len(session_ids)} sessions")
```

### Step 3: Create a Dream

```python
# Create a dream job
dream = client.beta.dreams.create(
    inputs=[
        {"type": "memory_store", "memory_store_id": store_id},
        {"type": "sessions", "session_ids": session_ids[:10]},  # Start small
    ],
    model="claude-opus-4-7",  # or claude-sonnet-4-6
    instructions="Focus on user preferences and recurring patterns. Merge duplicate entries. Remove outdated debugging notes."
)

dream_id = dream.id
print(f"Dream created: {dream_id}")
print(f"Status: {dream.status}")
```

### Step 4: Poll for Completion

```python
import time

# Poll until dream completes
while dream.status in ("pending", "running"):
    time.sleep(10)  # Poll every 10 seconds
    dream = client.beta.dreams.retrieve(dream.id)
    print(f"Status: {dream.status} | Tokens: {dream.usage.input_tokens}")

if dream.status == "completed":
    print("Dream completed successfully!")
elif dream.status == "failed":
    print(f"Dream failed: {dream.error}")
```

### Step 5: Review Output

```python
# Extract output memory store
output_store_id = next(
    output.memory_store_id 
    for output in dream.outputs 
    if output.type == "memory_store"
)

# View the curated memory
memories = client.beta.memory_stores.view(output_store_id)
print("Curated memories:")
for entry in memories.memories:
    print(f"  {entry.key}: {entry.value}")
```

### Step 6: Use the Output (or Discard)

**Option A: Leverage the Output**
```python
# Attach the new memory store to future sessions
session = client.beta.sessions.create(
    agent=agent_id,
    environment_id=environment_id,
    resources=[
        {"type": "memory_store", "memory_store_id": output_store_id},
    ],
)
```

**Option B: Discard It**
```python
# Delete or archive if not satisfied
client.beta.memory_stores.delete(output_store_id)
# or
client.beta.memory_stores.archive(output_store_id)
```

### Complete Example: Full Dream Workflow

```python
from anthropic import Anthropic
import time

client = Anthropic()

def run_dream_workflow(store_id, session_ids, agent_id, environment_id):
    """Run a complete dream curation pipeline."""
    
    print("🌙 Starting dream workflow...")
    
    # Create dream
    dream = client.beta.dreams.create(
        inputs=[
            {"type": "memory_store", "memory_store_id": store_id},
            {"type": "sessions", "session_ids": session_ids[:20]},
        ],
        model="claude-opus-4-7",
        instructions=(
            "Deduplicate user preferences. Merge conflicting entries with latest values. "
            "Extract patterns and insights across sessions. Remove one-off debugging notes."
        )
    )
    
    print(f"✓ Dream created: {dream.id}")
    
    # Poll for completion
    start_time = time.time()
    while dream.status in ("pending", "running"):
        time.sleep(10)
        dream = client.beta.dreams.retrieve(dream.id)
        elapsed = int(time.time() - start_time)
        print(f"  [{elapsed}s] Status: {dream.status} | In: {dream.usage.input_tokens} tokens")
    
    print(f"\n✓ Dream finished: {dream.status}")
    
    if dream.status == "completed":
        # Extract output
        output_store_id = next(
            output.memory_store_id 
            for output in dream.outputs 
            if output.type == "memory_store"
        )
        
        # View curated memory
        memories = client.beta.memory_stores.view(output_store_id)
        print(f"\n📋 Curated {len(memories.memories)} memory entries:")
        for entry in memories.memories[:5]:  # Show first 5
            print(f"  • {entry.key}: {entry.value[:60]}...")
        
        # Use output in future sessions
        print(f"\n✓ Using curated memory store: {output_store_id}")
        new_session = client.beta.sessions.create(
            agent=agent_id,
            environment_id=environment_id,
            resources=[
                {"type": "memory_store", "memory_store_id": output_store_id},
            ],
        )
        
        return output_store_id, new_session.id
    
    elif dream.status == "failed":
        print(f"❌ Dream failed: {dream.error}")
        return None, None

# Usage
# store_id = "memstore_01..."
# session_ids = ["sesn_01...", "sesn_02...", ...]
# agent_id = "agent_01..."
# environment_id = "env_01..."
# output_store_id, session_id = run_dream_workflow(store_id, session_ids, agent_id, environment_id)
```

---

## Advanced Operations

### Cancel a Dream

```python
# Stop a pending or running dream
client.beta.dreams.cancel(dream_id)
```

### Archive a Dream

```python
# Archive a completed dream (doesn't modify memory store)
client.beta.dreams.archive(dream_id)
```

### List All Dreams

```python
for dream in client.beta.dreams.list(limit=20):
    print(f"{dream.id}: {dream.status}")

# Include archived dreams
for dream in client.beta.dreams.list(include_archived=True):
    print(f"{dream.id}: {dream.status} (archived: {dream.archived_at})")
```

### Watch the Pipeline in Real-Time

```python
# Once running, stream the dream's internal session
dream = client.beta.dreams.retrieve(dream_id)
if dream.status == "running" and dream.session_id:
    # Stream events from the dream's internal session
    for event in client.beta.sessions.stream_events(dream.session_id):
        print(f"Event: {event.type} - {event.details}")
```

---

## Best Practices

### 1. Start Small
- Begin with 5–10 sessions, not 100
- Verify curation quality before scaling
- Adjust instructions based on results

### 2. Provide Clear Instructions
```python
instructions = (
    "Focus on: user coding style, preferences, and architecture decisions. "
    "Deduplicate similar entries. Remove temporary debugging notes. "
    "Surface patterns about technology choices and design principles."
)
```

### 3. Iterate
- Review outputs
- Refine instructions
- Run again with refined parameters

### 4. Cost Management
- Cost scales roughly linearly with input size
- Use `usage` on the dream resource to track tokens
- Default rate limits apply during beta

### 5. Error Handling

```python
dream = client.beta.dreams.create(...)

try:
    while dream.status in ("pending", "running"):
        time.sleep(10)
        dream = client.beta.dreams.retrieve(dream.id)
except Exception as e:
    print(f"Error retrieving dream: {e}")

if dream.error:
    error_type = dream.error.type
    if error_type == "timeout":
        print("Dream timed out; reduce input size")
    elif error_type == "input_memory_store_too_large":
        print("Memory store too large; split into smaller dreams")
    elif error_type == "input_memory_store_unavailable":
        print("Input store was deleted; check store exists")
    else:
        print(f"Error: {error_type}")
```

---

## Use Cases for DreamToosa

### 1. Agent Knowledge Consolidation
**Scenario**: DreamToosa agent has worked across 50+ sessions
- **Input**: Agent's memory store + recent sessions
- **Output**: Consolidated, deduplicated memory
- **Benefit**: Agent starts fresh sessions with clean, organized context

### 2. Pattern Recognition
**Scenario**: Extract user preferences and patterns
- **Input**: Sessions where user interacted with various tools
- **Output**: Memory focused on "user prefers X over Y" insights
- **Benefit**: Agent learns user preferences without explicit programming

### 3. Conflict Resolution
**Scenario**: Agent recorded conflicting information
- **Input**: Memory store with contradictions + sessions showing latest truth
- **Output**: Memory with conflicts resolved to latest values
- **Benefit**: Single source of truth for future decisions

### 4. Context Cleanup
**Scenario**: Memory store bloated with debugging notes, temporary data
- **Input**: Memory store + instructions to ignore one-offs
- **Output**: Lean, production-ready memory
- **Benefit**: Reduced token usage in future sessions

### 5. Multi-Agent Sync
**Scenario**: Multiple agents need shared understanding
- **Input**: Separate memory stores from multiple agents + their sessions
- **Output**: Merged, canonical memory store
- **Benefit**: Agents operate from consistent foundation

---

## Limits & Constraints

| Limit | Value |
|-------|-------|
| Sessions per dream | 100 |
| Instructions length | 4,096 characters |
| Supported models | `claude-opus-4-7`, `claude-sonnet-4-6` |
| Input store size limit | Pipeline enforced (check error messages) |
| Concurrent dreams | Subject to standard rate limits (contact support for higher) |

---

## Architecture Recommendation for DreamToosa

```
┌─────────────────────────────────────────┐
│   DreamToosa Agent (Managed Agent)      │
├─────────────────────────────────────────┤
│                                         │
│  Session 1 ──┐                          │
│  Session 2 ──┤                          │
│  Session 3 ──├──→ Dream Job ────→ New Memory Store
│  Session 4 ──┤       │                  │
│  Session 5 ──┘       │                  │
│                      └─ Old Memory Store│
│                                         │
│  Review Output:                         │
│  ✓ Use new store in future sessions     │
│  ✓ Keep both and blend them             │
│  ✓ Discard and iterate with new params  │
│                                         │
└─────────────────────────────────────────┘
```

---

## Troubleshooting

### Dream hangs in `pending`
- Check API credentials and headers
- Verify inputs exist and are accessible
- Wait longer (may be queued)

### Dream fails with `timeout`
- Reduce number of input sessions
- Reduce memory store size
- Simplify or shorten instructions

### Dream fails with `input_memory_store_unavailable`
- Verify memory store ID is correct
- Check store hasn't been archived/deleted
- Ensure store still exists in workspace

### Output quality is poor
- Refine `instructions` parameter
- Provide more session context
- Reduce sessions to focus on specific time period
- Try different model (`claude-sonnet-4-6` vs `claude-opus-4-7`)

---

## Summary

**Claude Dreams** enable agents to:
1. **Clean up** accumulated memory over time
2. **Learn patterns** from past interactions
3. **Resolve conflicts** in stored data
4. **Optimize context** for future sessions

For DreamToosa, this means:
- Continuous memory improvement without manual curation
- Ability to extract insights from hundreds of interactions
- Cleaner, more focused context for agent decisions
- Better long-term performance and user satisfaction

---

## Next Steps

1. **Enable dreaming** in your workspace (Research Preview - request access)
2. **Create a memory store** for your agent
3. **Run a test dream** with 5–10 sessions to evaluate quality
4. **Iterate on instructions** based on output
5. **Integrate into production** workflow as confidence grows


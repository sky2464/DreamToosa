# Claude Dream Implementation Guide

## Overview

**Claude Dream** is a Research Preview feature for Managed Agents that allows Claude to reflect on past sessions and curate agent memory stores. It automatically cleans up duplicates, contradictions, and stale entries while surfacing new insights.

**Status:** Research Preview (requires access request)
**Required Headers:** `managed-agents-2026-04-01` and `dreaming-2026-04-21` beta headers

---

## What Claude Dream Does

### Problem It Solves
Over many sessions, memory stores accumulate:
- **Duplicates** - Same information written multiple times
- **Contradictions** - Conflicting or outdated entries
- **Stale data** - Information no longer relevant
- **Missed patterns** - Insights hidden in scattered session transcripts

### Solution
A "dream" is an asynchronous job that:
1. Reads an existing memory store
2. Analyzes up to 100 past session transcripts
3. Deduplicates and reconciles entries
4. Surfaces patterns and new insights
5. Produces a reorganized output memory store

**Key:** Input store is never modified; output is a separate store you can review and accept or discard.

---

## How to Implement

### Prerequisites
- Anthropic Managed Agents API access
- A pre-existing memory store (or create an empty one)
- Optional: Session transcripts to analyze
- SDK with beta headers enabled (automatically set)

### 1. Create a Dream Job

```python
from anthropic import Anthropic

client = Anthropic()

# Create a dream with a memory store and optional sessions
dream = client.beta.dreams.create(
    inputs=[
        {"type": "memory_store", "memory_store_id": "memstore_01Hx..."},
        {"type": "sessions", "session_ids": ["sesn_01...", "sesn_02..."]},  # Optional
    ],
    model="claude-opus-4-7",  # or "claude-sonnet-4-6"
    instructions="Focus on coding-style preferences; ignore one-off debugging notes.",  # Optional guidance
)

print(f"Dream created: {dream.id}")
# Returns: drm_01AbCDefGhIjKlMnOpQrStUv
```

**Input Parameters:**
- `memory_store_id` (required): Your existing memory store to curate
- `session_ids` (optional): Up to 100 session transcripts to analyze for patterns
- `model` (required): `claude-opus-4-7` or `claude-sonnet-4-6`
- `instructions` (optional): Additional guidance (max 4,096 chars)

### 2. Track Progress

Dreams run asynchronously (typically minutes to tens of minutes):

```python
import time

# Poll the dream until complete
while dream.status in ("pending", "running"):
    time.sleep(10)
    dream = client.beta.dreams.retrieve(dream.id)
    print(f"Status: {dream.status}")
    print(f"Input tokens: {dream.usage.input_tokens}")
    print(f"Output tokens: {dream.usage.output_tokens}")
```

**Status Lifecycle:**

| Status | Meaning |
|--------|---------|
| `pending` | Created and queued |
| `running` | Pipeline is processing; usage updates in real-time |
| `completed` | Finished successfully; outputs available |
| `failed` | Terminated with error; partial output available |
| `canceled` | Manually canceled; partial output available |

### 3. Monitor in Real Time (Optional)

Once `running`, you can stream the underlying session events:

```python
# Watch what the dream is reading/writing
session_id = dream.session_id

for event in client.beta.sessions.stream_events(session_id):
    print(f"Event: {event.type}")
    # Observe the dream's work in real time
```

### 4. Use the Output

When `status == "completed"`:

```python
# Extract the output memory store
output_store_id = next(
    output.memory_store_id 
    for output in dream.outputs 
    if output.type == "memory_store"
)

# Option A: Review the output before using it
memories = client.beta.memory_stores.retrieve(output_store_id)
print(f"Output store has {len(memories.entries)} entries")

# Option B: Attach to future sessions
session = client.beta.sessions.create(
    agent=agent_id,
    environment_id=environment_id,
    resources=[
        {"type": "memory_store", "memory_store_id": output_store_id},
    ],
)

# Option C: Discard if unsatisfied
client.beta.memory_stores.archive(output_store_id)
# or delete it
```

---

## Complete Workflow Example

```python
from anthropic import Anthropic
import time

client = Anthropic()

# Step 1: Create dream
print("Creating dream...")
dream = client.beta.dreams.create(
    inputs=[
        {"type": "memory_store", "memory_store_id": "memstore_01ABC"},
        {"type": "sessions", "session_ids": ["sesn_01", "sesn_02", "sesn_03"]},
    ],
    model="claude-opus-4-7",
    instructions="Merge duplicate technical preferences and prioritize recent decisions.",
)
print(f"Dream ID: {dream.id}")

# Step 2: Poll until completion
while dream.status != "completed":
    if dream.status == "failed":
        print(f"Dream failed: {dream.error}")
        break
    
    time.sleep(10)
    dream = client.beta.dreams.retrieve(dream.id)
    print(f"Status: {dream.status} | Tokens: {dream.usage.output_tokens}")

# Step 3: Use output
if dream.status == "completed":
    output_store_id = next(
        o.memory_store_id for o in dream.outputs if o.type == "memory_store"
    )
    print(f"Curated memory store ready: {output_store_id}")
    
    # Use it in next session
    session = client.beta.sessions.create(
        agent="agent_01XYZ",
        environment_id="env_01XYZ",
        resources=[
            {"type": "memory_store", "memory_store_id": output_store_id},
        ],
    )
```

---

## Advanced Features

### Cancel a Dream

```python
# Stop a pending or running dream
client.beta.dreams.cancel(dream_id)
# Returns: dream object with status="canceled"
```

### Archive a Dream

```python
# Hide a completed dream from default list (doesn't delete it)
client.beta.dreams.archive(dream_id)
# Still accessible by ID, but excluded from list responses
```

### List Dreams

```python
# Get all non-archived dreams (newest first)
for dream in client.beta.dreams.list(limit=20):
    print(f"{dream.id}: {dream.status}")

# Include archived dreams
for dream in client.beta.dreams.list(limit=20, include_archived=True):
    print(f"{dream.id}: {dream.status} (archived: {dream.archived_at})")
```

---

## Key Design Patterns

### 1. **Selective Curation**
Use `instructions` to guide what the dream focuses on:
```python
instructions="Prioritize recent user preferences; mark deprecated patterns."
```

### 2. **Batch Multiple Sessions**
For best results, include 10-50 related session transcripts:
```python
session_ids = [s.id for s in agent_sessions[-20:]]  # Last 20 sessions
```

### 3. **Safe Review-Before-Use**
Always review output before deploying:
```python
output_entries = client.beta.memory_stores.list_entries(output_store_id)
if output_entries.entries:
    print("Curated entries:", output_entries.entries)
```

### 4. **Iterative Dreaming**
Chain dreams to progressively refine memory:
```python
# Dream 1: Clean initial store
dream1 = create_dream(original_store, sessions1)
# ... wait for completion ...

# Dream 2: Further refine dream1's output with more sessions
dream2 = create_dream(dream1_output_store, sessions2)
```

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `timeout` | Exceeded runtime budget | Use fewer sessions or simpler instructions |
| `input_memory_store_too_large` | Store exceeds size limit | Split into multiple dreams |
| `input_memory_store_unavailable` | Store deleted mid-run | Ensure inputs aren't modified during dream |
| `memory_store_org_limit_exceeded` | Hit org storage cap | Archive unused stores first |

---

## Performance & Billing

### Timing
- **Typical duration:** Minutes to tens of minutes
- **Scales with:** Input store size + number/length of sessions

### Costs
- Billed at standard API token rates for selected model
- Usage reported in dream resource
- Budget estimate: Cost ≈ (input tokens + output tokens) × per-token rate

### Optimization
- Start with small batch (5-10 sessions)
- Monitor token usage
- Scale up once satisfied with curation quality

---

## Limits

| Limit | Value |
|-------|-------|
| Sessions per dream | 100 |
| Instructions length | 4,096 characters |
| Supported models | `claude-opus-4-7`, `claude-sonnet-4-6` |
| Rate limits | Default API limits (contact support for higher) |

---

## Use Cases

1. **Long-Running Agents**: Clean up accumulated memory after 50+ sessions
2. **Multi-Domain Agents**: Separate contradictory memory from different task domains
3. **Evolution Tracking**: Surface how agent preferences/patterns change over time
4. **Knowledge Extraction**: Distill implicit patterns from session transcripts
5. **Memory Deduplication**: Merge redundant entries across sessions
6. **Quality Assurance**: Review and curate memory before deployment

---

## Request Access

Dreaming is currently in Research Preview. To use it:

1. Visit: https://claude.com/form/claude-managed-agents
2. Request access to the Dreaming feature
3. Wait for approval (typically 1-2 business days)
4. Use the implementation patterns above once approved

---

## References

- **Official Docs**: https://platform.claude.com/docs/en/managed-agents/dreams
- **Memory Stores API**: https://platform.claude.com/docs/en/managed-agents/memory
- **Managed Agents Overview**: https://platform.claude.com/docs/en/managed-agents/overview

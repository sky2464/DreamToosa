# Claude Dreams Implementation Guide

## Overview

**Claude Dreams** is a feature in the Managed Agents API that allows Claude to intelligently reorganize and curate agent memory stores. It reads existing memory alongside past session transcripts to produce a cleaned, deduplicated, and enriched memory store.

### Key Benefit
Over many sessions, memory stores accumulate duplicates, contradictions, and stale entries. Dreams automatically:
- Merge duplicate entries
- Replace contradictions with the latest values
- Remove stale or outdated information
- Surface new patterns and insights from session transcripts

---

## Core Concepts

### What is a Dream?
A **dream** is an asynchronous background job that:
1. Takes a pre-existing **memory store** as input
2. Optionally reads up to 100 past **session transcripts**
3. Produces a new **output memory store** with cleaned, reorganized data

**Important**: The input memory store is never modified.

### Memory Curation Process
Dreams run the agent through a reflection pipeline that:
- Analyzes all entries in the input memory store
- Reads patterns from past sessions
- Consolidates duplicate information
- Updates stale entries with current information
- Creates new insights from session patterns
- Writes everything to a fresh output memory store

---

## Technical Implementation

### Prerequisites
- Access to the **Managed Agents API** (beta)
- Required headers:
  - `managed-agents-2026-04-01` (Managed Agents beta)
  - `dreaming-2026-04-21` (Dreaming beta)
- Supported models: `claude-opus-4-7` or `claude-sonnet-4-6`

### Step 1: Create a Memory Store

Before running a dream, you need an existing memory store:

```python
from anthropic import Anthropic

client = Anthropic()

# Create an empty memory store if you don't have one
store = client.beta.memory.memory_stores.create()
print(f"Created memory store: {store.id}")
```

### Step 2: Create a Dream

Initiate a dream job that will curate your memory:

```python
# Create a dream with memory store and optional sessions
dream = client.beta.dreams.create(
    inputs=[
        {"type": "memory_store", "memory_store_id": store_id},
        {"type": "sessions", "session_ids": [session_a, session_b, session_c]},
    ],
    model="claude-opus-4-7",
    instructions="Focus on coding-style preferences; ignore one-off debugging notes.",
)

print(f"Dream created: {dream.id}")
print(f"Status: {dream.status}")
```

**Parameters**:
- `memory_store_id`: The store to curate (required)
- `session_ids`: Past transcripts to analyze (up to 100, optional)
- `model`: Claude model to run the dream (`claude-opus-4-7` or `claude-sonnet-4-6`)
- `instructions`: Custom guidance (max 4,096 characters) to focus the curation

### Step 3: Monitor Dream Progress

Dreams run asynchronously and typically take minutes to tens of minutes:

```python
import time

def wait_for_dream(dream_id, poll_interval=10):
    """Poll dream status until completion"""
    while True:
        dream = client.beta.dreams.retrieve(dream_id)
        print(f"Status: {dream.status}")
        print(f"  Input tokens: {dream.usage.input_tokens}")
        print(f"  Output tokens: {dream.usage.output_tokens}")
        
        if dream.status in ("completed", "failed", "canceled"):
            return dream
        
        time.sleep(poll_interval)

# Wait for the dream to complete
completed_dream = wait_for_dream(dream.id)
```

**Status Lifecycle**:
| Status | Meaning |
|--------|---------|
| `pending` | Queued and ready to start |
| `running` | Currently processing |
| `completed` | Finished successfully, output ready |
| `failed` | Error occurred, partial output available |
| `canceled` | User-initiated cancellation |

### Step 4: Access the Output

Once the dream completes, extract the output memory store:

```python
# Extract the output memory store from completed dream
output_store_id = next(
    output.memory_store_id 
    for output in completed_dream.outputs 
    if output.type == "memory_store"
)

print(f"Curated memory store: {output_store_id}")

# View the curated memories
memories = client.beta.memory.memories.list(
    memory_store_id=output_store_id
)

for memory in memories:
    print(f"- {memory.id}: {memory.content}")
```

### Step 5: Use the Curated Memory

Attach the output memory store to future agent sessions:

```python
# Start a new session with the curated memory
session = client.beta.sessions.create(
    agent=agent_id,
    environment_id=environment_id,
    resources=[
        {"type": "memory_store", "memory_store_id": output_store_id},
    ],
)

print(f"Session started with curated memory: {session.id}")
```

---

## Complete Example Workflow

```python
import time
from anthropic import Anthropic

client = Anthropic()

def dream_workflow(store_id, session_ids, agent_id, environment_id):
    """Complete dream curation workflow"""
    
    # 1. Create dream
    print("Creating dream...")
    dream = client.beta.dreams.create(
        inputs=[
            {"type": "memory_store", "memory_store_id": store_id},
            {"type": "sessions", "session_ids": session_ids},
        ],
        model="claude-opus-4-7",
        instructions="Focus on user preferences and discovered patterns.",
    )
    print(f"Dream ID: {dream.id}")
    
    # 2. Poll until completion
    print("Waiting for dream to complete...")
    while dream.status in ("pending", "running"):
        time.sleep(10)
        dream = client.beta.dreams.retrieve(dream.id)
        print(f"  Status: {dream.status} | Tokens: {dream.usage.input_tokens}")
    
    if dream.status == "failed":
        print(f"Dream failed: {dream.error}")
        return None
    
    # 3. Extract output
    print("Dream completed! Extracting output...")
    output_store_id = next(
        output.memory_store_id 
        for output in dream.outputs 
        if output.type == "memory_store"
    )
    
    # 4. Review curated memories
    print("\nCurated memories:")
    memories = client.beta.memory.memories.list(
        memory_store_id=output_store_id,
        limit=10
    )
    for memory in memories:
        print(f"  - {memory.content}")
    
    # 5. Use in future sessions
    print("\nStarting new session with curated memory...")
    session = client.beta.sessions.create(
        agent=agent_id,
        environment_id=environment_id,
        resources=[
            {"type": "memory_store", "memory_store_id": output_store_id},
        ],
    )
    print(f"Session created: {session.id}")
    
    return output_store_id

# Usage
store_id = "memstore_01..."
session_ids = ["sesn_01...", "sesn_02...", "sesn_03..."]
agent_id = "agent_01..."
environment_id = "env_01..."

output_store = dream_workflow(store_id, session_ids, agent_id, environment_id)
```

---

## Advanced Features

### Monitor Dream Execution in Real-Time

While a dream runs, its internal session produces events you can stream:

```python
# Get the underlying session ID while dream is running
dream = client.beta.dreams.retrieve(dream_id)
if dream.session_id:
    # Stream events from the dream's internal session
    for event in client.beta.sessions.stream.messages.list(dream.session_id):
        print(event)
```

### Cancel a Dream

Stop a pending or running dream:

```python
client.beta.dreams.cancel(dream_id)
```

### Archive a Dream

Hide a completed dream from list responses (but keep it readable by ID):

```python
client.beta.dreams.archive(dream_id)
```

### List All Dreams

Retrieve all non-archived dreams in your workspace:

```python
for dream in client.beta.dreams.list(limit=20):
    print(f"{dream.id}: {dream.status}")

# Include archived dreams
for dream in client.beta.dreams.list(limit=20, include_archived=True):
    print(f"{dream.id}: {dream.status}")
```

---

## Practical Use Cases

### 1. **Long-Running Agent Memory Cleanup**
Over many sessions, an agent accumulates duplicate notes, outdated information, and contradictory entries. A dream cleans this up periodically.

```python
# Run a dream every 100 sessions
if session_count % 100 == 0:
    dream = client.beta.dreams.create(
        inputs=[
            {"type": "memory_store", "memory_store_id": agent_memory_store},
            {"type": "sessions", "session_ids": recent_100_sessions},
        ],
        model="claude-opus-4-7",
    )
```

### 2. **Project Knowledge Consolidation**
Summarize and reorganize what an agent learned about a project across many sessions.

```python
dream = client.beta.dreams.create(
    inputs=[
        {"type": "memory_store", "memory_store_id": project_store},
        {"type": "sessions", "session_ids": all_project_sessions},
    ],
    model="claude-sonnet-4-6",
    instructions="Consolidate project architecture decisions, dependencies, and coding patterns.",
)
```

### 3. **User Preference Learning**
Extract and organize user preferences from interaction history.

```python
dream = client.beta.dreams.create(
    inputs=[
        {"type": "memory_store", "memory_store_id": user_profile_store},
        {"type": "sessions", "session_ids": user_interaction_sessions},
    ],
    model="claude-opus-4-7",
    instructions="Extract and organize user preferences for design, communication style, and priorities.",
)
```

---

## Cost Considerations

- **Billing**: Standard API token rates for the selected model
- **Cost Scaling**: Roughly linear with number and length of input sessions
- **Recommendation**: Start with small batches of sessions and scale up once satisfied with quality

---

## Limits

| Limit | Value |
|-------|-------|
| Sessions per dream | 100 |
| Instructions length | 4,096 characters |
| Supported models | `claude-opus-4-7`, `claude-sonnet-4-6` |

---

## Error Handling

Common error types:

| Error | Cause | Resolution |
|-------|-------|------------|
| `timeout` | Pipeline exceeded runtime budget | Reduce session count or size |
| `internal_error` | Unclassified failure | Retry, contact support |
| `memory_store_org_limit_exceeded` | Organization hit memory-store cap | Clean up unused stores |
| `input_memory_store_too_large` | Input store exceeds size limit | Split into smaller stores |
| `input_memory_store_unavailable` | Input store was deleted mid-dream | Don't delete during execution |
| `input_session_unavailable` | Input session was deleted mid-dream | Don't delete during execution |

---

## Best Practices

1. **Start Small**: Test with a few sessions before dreaming over 100
2. **Review Output**: Always inspect the curated memory before using
3. **Custom Instructions**: Provide specific guidance about what to focus on
4. **Periodic Cleanup**: Schedule dreams every N sessions to prevent accumulation
5. **Keep Inputs**: Don't delete input stores/sessions while dream is running
6. **Discard if Unsatisfied**: You can safely delete the output if results aren't useful
7. **Archive When Done**: Archive completed dreams to keep workspace organized

---

## Integration with DreamToosa

For DreamToosa implementation:

1. **Memory Store Strategy**
   - Create separate memory stores for different agent types/domains
   - Run dreams periodically (e.g., every 50-100 sessions)

2. **Custom Instructions**
   - Tailor instructions for each domain (coding, documentation, testing, etc.)
   - Focus dreams on surfacing patterns relevant to your workflow

3. **Session Management**
   - Keep recent sessions available for dreaming
   - Archive old sessions once dreamed over

4. **Output Handling**
   - Review curated memories before deploying
   - A/B test curated vs. original stores for quality
   - Gradually transition to curated stores as confidence grows

---

## References

- [Claude API Docs - Dreams](https://platform.claude.com/docs/en/managed-agents/dreams)
- [Claude API Docs - Memory Stores](https://platform.claude.com/docs/en/managed-agents/memory)
- [Managed Agents Overview](https://platform.claude.com/docs/en/managed-agents/overview)

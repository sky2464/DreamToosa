# Claude Dreams Implementation Guide

## Overview

Claude Dreams is a Research Preview feature for Anthropic's Managed Agents API that enables sophisticated memory curation. It allows agents to reflect on past sessions and clean up their memory stores by:

- **Deduplicating** entries
- **Resolving contradictions** with latest values
- **Surfacing new insights** from historical context
- **Reorganizing** memory for better performance

## Core Concept

Dreams work by:
1. Reading an existing **memory store** (agent's accumulated knowledge)
2. Analyzing up to 100 **past session transcripts**
3. Producing a new **output memory store** with deduplicated, consolidated, and enhanced memory

The input store is never modified—the output is a separate, reviewable result.

## Key Characteristics

| Aspect | Details |
|--------|---------|
| **Status** | Research Preview (requires access request) |
| **Processing** | Asynchronous (typically minutes to tens of minutes) |
| **Models** | `claude-opus-4-7`, `claude-sonnet-4-6` |
| **Session Limit** | Up to 100 sessions per dream |
| **Instructions Limit** | 4,096 characters |
| **Required Headers** | `managed-agents-2026-04-01` + `dreaming-2026-04-21` |

## Implementation Steps

### 1. Create a Dream

```python
import anthropic
import time

client = anthropic.Anthropic(api_key="your-api-key")

# Create a dream to process memory
dream = client.beta.dreams.create(
    inputs=[
        {"type": "memory_store", "memory_store_id": "memstore_01..."},
        {"type": "sessions", "session_ids": ["sesn_01...", "sesn_02..."]},
    ],
    model="claude-opus-4-7",
    instructions="Focus on coding-style preferences; merge duplicate patterns.",
)

print(f"Dream created: {dream.id}")
print(f"Status: {dream.status}")
```

### 2. Track Progress

Dreams are asynchronous and run in the background. Poll to track status:

```python
while dream.status in ("pending", "running"):
    time.sleep(10)  # Poll every 10 seconds
    dream = client.beta.dreams.retrieve(dream.id)
    print(f"Status: {dream.status}")
    print(f"Input tokens: {dream.usage.input_tokens}")
    print(f"Output tokens: {dream.usage.output_tokens}")
```

### 3. Dream Lifecycle States

| State | Meaning | Next Action |
|-------|---------|------------|
| `pending` | Queued and ready | Wait for processing |
| `running` | Processing in progress | Poll or watch session |
| `completed` | Successfully finished | Use output store in new sessions |
| `failed` | Error occurred | Check error details, review partial output |
| `canceled` | Manually stopped | Review partial output if needed |

### 4. Watch Real-Time Processing

While a dream runs, observe what it's reading and writing:

```python
# Dream.session_id points to the underlying session
if dream.session_id:
    # Stream events from the session
    with client.beta.sessions.stream(
        session_id=dream.session_id
    ) as stream:
        for event in stream:
            print(f"Event: {event.type}")
```

### 5. Use the Output Memory Store

Once `status == "completed"`:

```python
# Extract the output memory store ID
output_store_id = next(
    output.memory_store_id 
    for output in dream.outputs 
    if output.type == "memory_store"
)

# Use it in future sessions
session = client.beta.sessions.create(
    agent=agent_id,
    environment_id=environment_id,
    resources=[
        {"type": "memory_store", "memory_store_id": output_store_id},
    ],
)
```

## Advanced Operations

### Cancel a Dream

Stop a pending or running dream immediately:

```python
client.beta.dreams.cancel(dream.id)
```

### Archive a Dream

Archive completed dreams for housekeeping:

```python
client.beta.dreams.archive(dream.id)
```

### List Dreams

View all non-archived dreams in your workspace:

```python
for listed_dream in client.beta.dreams.list(limit=20):
    print(f"{listed_dream.id}: {listed_dream.status}")

# Include archived dreams
for listed_dream in client.beta.dreams.list(limit=20, include_archived=True):
    print(f"{listed_dream.id}: {listed_dream.status}")
```

## Input Requirements

### Memory Store Input

```python
# Create empty store if needed
memory_store = client.beta.memory_stores.create(
    name="Agent Memory"
)

# Then pass to dream
inputs = [
    {"type": "memory_store", "memory_store_id": memory_store.id},
    # ... sessions ...
]
```

### Sessions Input

- Up to 100 session IDs
- Sessions provide historical context and patterns for the dream to analyze
- Optional—can process memory store alone without sessions

```python
inputs = [
    {"type": "memory_store", "memory_store_id": store_id},
    {"type": "sessions", "session_ids": [session_a, session_b, session_c]},
]
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|-----------|
| `timeout` | Pipeline exceeded runtime | Use fewer sessions; increase budget |
| `memory_store_org_limit_exceeded` | Hit org memory store cap | Archive unused stores |
| `input_memory_store_too_large` | Store exceeds size limit | Split into multiple dreams |
| `input_memory_store_unavailable` | Input store deleted mid-dream | Don't delete during processing |
| `input_session_unavailable` | Input session deleted mid-dream | Don't delete during processing |

## Billing & Costs

- Billed at standard API rates for selected model
- `usage` field reports exact token counts
- Cost scales linearly with input size
- **Strategy:** Start small (10-20 sessions), verify quality, then scale

## Best Practices

### 1. Iterative Improvement
```python
# Start with a small batch to test quality
dream = client.beta.dreams.create(
    inputs=[
        {"type": "memory_store", "memory_store_id": store_id},
        {"type": "sessions", "session_ids": sessions[:10]},  # Test first
    ],
    model="claude-opus-4-7",
    instructions="Your curation guidance...",
)
```

### 2. Custom Instructions
```python
instructions = """
Priority 1: Merge duplicate learning patterns
Priority 2: Update outdated code style preferences
Priority 3: Surface novel debugging techniques
Ignore: One-off error messages from failed tests
"""

dream = client.beta.dreams.create(
    inputs=[...],
    model="claude-opus-4-7",
    instructions=instructions,
)
```

### 3. Review Before Adoption
```python
# Inspect output before using it
output_store = client.beta.memory_stores.get(output_store_id)
entries = client.beta.memory_stores.get_entries(output_store_id)

# Review entries
for entry in entries:
    print(f"Key: {entry.key}")
    print(f"Content: {entry.content}")
    print("---")

# Only adopt if satisfied
if approved_by_user:
    # Use in new sessions
    pass
else:
    # Discard
    client.beta.memory_stores.archive(output_store_id)
```

## Use Case Examples

### Engineering Team Agent
- **Input:** Memory of coding patterns, architecture decisions, debugging notes
- **Sessions:** Past debugging, code review, architecture planning sessions
- **Instructions:** Focus on coding standards, architectural patterns, testing practices
- **Output:** Consolidated coding guidelines and patterns

### Customer Support Agent
- **Input:** Customer information, issue resolutions, common problems
- **Sessions:** Past support tickets and resolution transcripts
- **Instructions:** Focus on solution patterns, customer preferences, escalation criteria
- **Output:** Improved knowledge base for consistent support

### Research Agent
- **Input:** Research findings, experimental results, literature notes
- **Sessions:** Past research sessions, literature reviews
- **Instructions:** Focus on emerging patterns, validated findings, contradictions
- **Output:** Cleaned research database with resolved contradictions

## Workflow Example

```python
import anthropic
import time

client = anthropic.Anthropic()

# Step 1: Create dream
print("Creating dream...")
dream = client.beta.dreams.create(
    inputs=[
        {"type": "memory_store", "memory_store_id": "memstore_01..."},
        {"type": "sessions", "session_ids": session_list},
    ],
    model="claude-opus-4-7",
    instructions="Consolidate debugging patterns and update tech stack preferences",
)
dream_id = dream.id

# Step 2: Poll until completion
print(f"Dream {dream_id} processing...")
while dream.status in ("pending", "running"):
    time.sleep(30)
    dream = client.beta.dreams.retrieve(dream_id)
    print(f"  Status: {dream.status} | Input: {dream.usage.input_tokens} | Output: {dream.usage.output_tokens}")

# Step 3: Check result
if dream.status == "completed":
    print("✓ Dream completed successfully")
    
    # Get output
    output_store_id = next(
        o.memory_store_id for o in dream.outputs if o.type == "memory_store"
    )
    
    # Review output
    print(f"Output store: {output_store_id}")
    
    # Use in new session
    new_session = client.beta.sessions.create(
        agent=agent_id,
        environment_id=env_id,
        resources=[
            {"type": "memory_store", "memory_store_id": output_store_id},
        ],
    )
    print(f"New session using curated memory: {new_session.id}")
    
elif dream.status == "failed":
    print(f"✗ Dream failed: {dream.error}")
```

## Summary

Claude Dreams automates memory curation for Managed Agents by:
- **Analyzing** historical sessions and memory stores
- **Consolidating** redundant entries
- **Resolving** contradictions and stale data
- **Surfacing** new insights from patterns

This enables agents to maintain clean, coherent memory over long deployments while reducing manual memory management overhead.

---

**Note:** Dreams is a Research Preview feature. [Request access](https://claude.com/form/claude-managed-agents) if you don't have it enabled on your account.

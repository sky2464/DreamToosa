# Claude Dreams Quick Start for DreamToosa

## What Are Claude Dreams?

**Dreams** let Claude automatically clean up and reorganize agent memory stores. Over time, agent memory accumulates:
- Duplicate information
- Contradictory entries
- Stale or outdated facts

A dream reads your memory store plus past session transcripts, then produces a new, curated memory store with:
- ✓ Duplicates merged
- ✓ Contradictions resolved with latest info
- ✓ Stale entries removed
- ✓ New patterns and insights extracted

---

## 5-Minute Implementation

### 1. Install Anthropic SDK
```bash
pip install anthropic
```

### 2. Create a Memory Store
```python
from anthropic import Anthropic

client = Anthropic()

# Create empty memory store
store = client.beta.memory.memory_stores.create()
memory_store_id = store.id
print(f"Memory store: {memory_store_id}")
```

### 3. Start a Dream
```python
# Create a dream that will curate your memory
dream = client.beta.dreams.create(
    inputs=[
        {"type": "memory_store", "memory_store_id": memory_store_id},
        {"type": "sessions", "session_ids": ["sesn_01...", "sesn_02..."]},
    ],
    model="claude-opus-4-7",
    instructions="Focus on code style and project architecture patterns",
)

dream_id = dream.id
print(f"Dream started: {dream_id}")
```

### 4. Wait for Completion
```python
import time

while True:
    dream = client.beta.dreams.retrieve(dream_id)
    print(f"Status: {dream.status}")
    
    if dream.status == "completed":
        break
    elif dream.status == "failed":
        print(f"Error: {dream.error}")
        break
    
    time.sleep(10)
```

### 5. Use the Curated Memory
```python
# Get the output memory store
output_store_id = next(
    output.memory_store_id 
    for output in dream.outputs 
    if output.type == "memory_store"
)

# Attach to a new agent session
session = client.beta.sessions.create(
    agent="agent_01...",
    environment_id="env_01...",
    resources=[
        {"type": "memory_store", "memory_store_id": output_store_id},
    ],
)

print(f"New session with curated memory: {session.id}")
```

---

## DreamToosa Integration Strategy

### Architecture
```
Agent Session 1
    ↓ writes to
Memory Store A
    ↓ (after N sessions)
Dream 1: Curate & Consolidate
    ↓ produces
Memory Store B (Clean)
    ↓ attached to
Agent Session N+1
```

### Implementation Pattern

**1. Periodic Dreaming** (Every 50-100 sessions)
```python
def should_dream(session_count: int) -> bool:
    return session_count % 50 == 0

# In your agent orchestration loop:
if should_dream(total_sessions):
    run_dream(memory_store_id, recent_session_ids)
```

**2. Domain-Specific Curation**
```python
instructions = {
    "code_review": "Focus on coding patterns, style conventions, and best practices",
    "documentation": "Organize by topic and consolidate overlapping explanations",
    "testing": "Surface discovered test patterns and edge cases",
}

dream = client.beta.dreams.create(
    inputs=[...],
    model="claude-opus-4-7",
    instructions=instructions[domain],
)
```

**3. Memory Quality Metrics**
```python
def measure_memory_quality(memory_store_id: str) -> dict:
    memories = client.beta.memory.memories.list(
        memory_store_id=memory_store_id,
        limit=100
    )
    
    return {
        "total_entries": len(memories.data),
        "avg_length": sum(len(m.content) for m in memories.data) / len(memories.data),
        "store_id": memory_store_id,
    }

# Compare before/after dream
before = measure_memory_quality(input_store)
after = measure_memory_quality(output_store)
print(f"Entries: {before['total_entries']} → {after['total_entries']}")
```

---

## Common Patterns

### Pattern 1: Cleanup After Major Milestones
```python
# After completing a feature or release
sessions_since_last_dream = current_session - last_dream_session
if sessions_since_last_dream > 50 or milestone_reached:
    dream = client.beta.dreams.create(
        inputs=[
            {"type": "memory_store", "memory_store_id": memory_store_id},
            {"type": "sessions", "session_ids": session_ids},
        ],
        model="claude-opus-4-7",
        instructions="Consolidate all learnings about the completed feature",
    )
    last_dream_session = current_session
```

### Pattern 2: Multi-Domain Curation
```python
# Different memory stores for different agent types
memory_stores = {
    "code_generation": "memstore_code_01...",
    "documentation": "memstore_docs_01...",
    "testing": "memstore_test_01...",
}

for domain, store_id in memory_stores.items():
    sessions = get_recent_sessions_for_domain(domain, limit=50)
    
    dream = client.beta.dreams.create(
        inputs=[
            {"type": "memory_store", "memory_store_id": store_id},
            {"type": "sessions", "session_ids": sessions},
        ],
        model="claude-opus-4-7",
        instructions=f"Curate {domain}-specific patterns and insights",
    )
```

### Pattern 3: Incremental Memory Management
```python
# Keep old memories for reference, start fresh with dreams
def rotate_memory():
    # Archive current store
    client.beta.memory.memory_stores.archive(current_store_id)
    
    # Create dream to consolidate
    dream_store = run_dream(current_store_id, all_sessions)
    
    # New store for next batch
    new_store = client.beta.memory.memory_stores.create()
    
    return dream_store, new_store
```

---

## API Reference Quick Guide

### Create a Dream
```python
dream = client.beta.dreams.create(
    inputs=[
        {"type": "memory_store", "memory_store_id": "memstore_01..."},
        {"type": "sessions", "session_ids": ["sesn_01...", "sesn_02..."]},
    ],
    model="claude-opus-4-7",  # or claude-sonnet-4-6
    instructions="Custom guidance (optional)",
)
```

### Check Status
```python
dream = client.beta.dreams.retrieve(dream_id)
print(dream.status)  # pending, running, completed, failed, canceled
```

### Get Output
```python
output_store = next(
    output.memory_store_id 
    for output in dream.outputs 
    if output.type == "memory_store"
)
```

### List Dreams
```python
for dream in client.beta.dreams.list(limit=20):
    print(f"{dream.id}: {dream.status}")
```

### Cancel Dream
```python
client.beta.dreams.cancel(dream_id)
```

### Archive Dream
```python
client.beta.dreams.archive(dream_id)
```

---

## Monitoring & Troubleshooting

### Check Dream Progress
```python
dream = client.beta.dreams.retrieve(dream_id)
print(f"Status: {dream.status}")
print(f"Input tokens: {dream.usage.input_tokens}")
print(f"Output tokens: {dream.usage.output_tokens}")
print(f"Created: {dream.created_at}")
```

### Common Errors
| Error | Cause | Fix |
|-------|-------|-----|
| `input_memory_store_unavailable` | Store was deleted | Don't delete while dreaming |
| `input_session_unavailable` | Session was deleted | Don't delete sessions mid-dream |
| `timeout` | Too much data | Reduce session count |
| `memory_store_org_limit_exceeded` | Hit quota | Delete unused stores |

### View Dream's Internal Session
While a dream is running, you can observe what it's doing:
```python
if dream.session_id:
    # Stream events from the dream's internal session
    for event in client.beta.sessions.stream.messages.list(dream.session_id):
        print(event)
```

---

## Best Practices

✅ **Do:**
- Start small (5-10 sessions) before dreaming 100
- Review curated memory before using in production
- Provide specific instructions for your domain
- Run dreams periodically (every 50-100 sessions)
- Archive old dreams to keep workspace clean

❌ **Don't:**
- Delete input stores or sessions while dream is running
- Dream over too many sessions at once
- Use stale dreams from weeks ago
- Ignore dream failures
- Assume output is perfect without review

---

## Cost Estimation

Dreams are billed at standard API rates:
- **Model**: claude-opus-4-7 (more capable) vs claude-sonnet-4-6 (faster, cheaper)
- **Scale**: Cost ≈ number of sessions × average session length
- **Typical**: $0.50 - $5.00 per dream depending on data volume

### Example
- 50 sessions, ~5KB each
- Using claude-sonnet-4-6
- Expected cost: ~$0.50-$1.00

---

## Next Steps

1. **Try the implementation**: Use `dreams_client.py` for a production-ready client
2. **Read full docs**: See `claude-dreams-implementation.md` for complete reference
3. **Integrate**: Add periodic dreaming to your DreamToosa agent orchestration
4. **Monitor**: Track memory quality metrics before and after dreaming
5. **Optimize**: Experiment with instructions and session counts

---

## Resources

- [Claude API Docs - Dreams](https://platform.claude.com/docs/en/managed-agents/dreams)
- [Memory Stores API](https://platform.claude.com/docs/en/managed-agents/memory)
- [Managed Agents Overview](https://platform.claude.com/docs/en/managed-agents/overview)

# Claude Dreams - Quick Reference Guide

## What are Claude Dreams?

Claude Dreams allow your Managed Agent to **clean up and reorganize its memory** by analyzing past sessions. Dreams:
- **Deduplicate** repeated memories
- **Consolidate** similar entries
- **Surface patterns** from past sessions
- **Replace stale** information
- **Create insights** about agent behavior

## When to Use Dreams

✅ **Use Dreams when:**
- Memory store has accumulated duplicate entries over many sessions
- You want to extract patterns from past agent runs
- Need to consolidate contradictory or outdated information
- Preparing an agent for a new phase with refined memory
- Analyzing behavioral patterns across multiple sessions

❌ **Don't use Dreams for:**
- One-time memory cleanup (manual editing is cheaper)
- Real-time memory management (use regular memory writes)
- Deleting sensitive information (use Memory Stores API directly)

## Quick Start (Python)

```python
from anthropic import Anthropic
import time

client = Anthropic()

# 1. Create dream
dream = client.beta.dreams.create(
    inputs=[
        {"type": "memory_store", "memory_store_id": "memstore_01..."},
        {"type": "sessions", "session_ids": ["sesn_01...", "sesn_02..."]},
    ],
    model="claude-opus-4-7",
    instructions="Remove duplicates, consolidate patterns, ignore debug notes.",
)

# 2. Wait for completion
while True:
    dream = client.beta.dreams.retrieve(dream.id)
    if dream.status == "completed":
        break
    elif dream.status == "failed":
        raise Exception(f"Dream failed: {dream.error}")
    time.sleep(10)

# 3. Use output
output_store_id = next(
    output.memory_store_id 
    for output in dream.outputs 
    if output.type == "memory_store"
)
```

## Key APIs

- **Create**: `client.beta.dreams.create(inputs=[...], model="...", instructions="...")`
- **Retrieve**: `client.beta.dreams.retrieve(dream_id)`
- **Cancel**: `client.beta.dreams.cancel(dream_id)`
- **Archive**: `client.beta.dreams.archive(dream_id)`
- **List**: `client.beta.dreams.list(limit=20)`

## Status Flow

```
pending → running → completed ✓
              ↓
             failed
              ↓
          (partial output)

pending/running → canceled
```

## Limits

| Limit | Value |
|-------|-------|
| Max sessions | 100 |
| Max instructions | 4,096 chars |
| Models | Opus 4.7, Sonnet 4.6 |

## Pricing

Standard API rates: ~$3/M input tokens (Opus), ~$0.80/M (Sonnet)

## Best Practices

1. Test with 5 sessions first
2. Provide clear instructions
3. Review output before using
4. Archive completed dreams
5. Monitor token usage

## Troubleshooting

- **Stuck pending**: Check API key, wait 1-2 min
- **High tokens**: Reduce sessions/size
- **Unchanged output**: Check for duplicates in input
- **Auth error**: Request research preview access

## Resources

- [Full Docs](https://platform.claude.com/docs/en/managed-agents/dreams)
- [Request Access](https://claude.com/form/claude-managed-agents)

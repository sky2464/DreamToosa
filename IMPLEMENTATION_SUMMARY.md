# Claude Dreams Implementation - Summary Report

**Date:** May 17, 2026  
**Task:** Understand and implement Claude Dreams API  
**Status:** ✓ Complete

---

## What is Claude Dreams?

Claude Dreams is a research preview feature in Anthropic's Managed Agents API that enables intelligent memory curation for long-running agents. It addresses the problem of memory store degradation over time by:

- **Deduplicating** redundant entries
- **Resolving contradictions** (keeping latest values)
- **Surfacing new insights** from historical patterns
- **Reorganizing** memory for optimal retrieval

### How It Works

A dream is an asynchronous job that takes:
1. **Input:** An existing memory store + up to 100 past session transcripts
2. **Processing:** Claude analyzes and reorganizes the data
3. **Output:** A new, cleaned memory store (separate from input)

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Memory Store** | Persistent knowledge base accumulated by agents |
| **Sessions** | Historical transcripts of agent work |
| **Dream Job** | Async task that processes memory stores |
| **Dreaming** | The curation and consolidation process |
| **Output Store** | New, curated memory store (ready to use) |

---

## API Overview

### Required Headers
- `managed-agents-2026-04-01` (Managed Agents beta)
- `dreaming-2026-04-21` (Dreams beta)

### Supported Models
- `claude-opus-4-7` (recommended)
- `claude-sonnet-4-6` (faster, lower cost)

### Core Operations

```
create_dream()      → Creates new dream job
retrieve()          → Get dream status/details
cancel()            → Stop pending/running dream
archive()           → Archive completed dream
list()              → List dreams in workspace
```

### Dream Lifecycle

```
pending → running → completed ✓
              ↓
            failed ✗
              ↓
            canceled ⊘
```

---

## Implementation Steps

### 1. Create a Dream
```python
dream = client.beta.dreams.create(
    inputs=[
        {"type": "memory_store", "memory_store_id": "memstore_01..."},
        {"type": "sessions", "session_ids": ["sesn_01...", "sesn_02..."]},
    ],
    model="claude-opus-4-7",
    instructions="Custom curation guidance...",
)
```

### 2. Monitor Progress
```python
while dream.status in ("pending", "running"):
    time.sleep(10)
    dream = client.beta.dreams.retrieve(dream.id)
    print(f"Status: {dream.status}, Tokens: {dream.usage.input_tokens}")
```

### 3. Use Output
```python
output_store_id = next(
    o.memory_store_id for o in dream.outputs if o.type == "memory_store"
)
# Use in new sessions:
session = client.beta.sessions.create(
    agent=agent_id,
    resources=[{"type": "memory_store", "memory_store_id": output_store_id}],
)
```

---

## Processing Time & Costs

- **Typical Duration:** Minutes to tens of minutes (async)
- **Billing:** Standard API rates (claude-opus-4-7 or claude-sonnet-4-6)
- **Scaling:** Linear with input size
- **Strategy:** Start small (10 sessions), verify quality, then scale

---

## Error Handling

| Error | Resolution |
|-------|-----------|
| `timeout` | Use fewer sessions |
| `input_memory_store_too_large` | Split into multiple dreams |
| `memory_store_org_limit_exceeded` | Archive unused stores |
| `input_memory_store_unavailable` | Don't delete inputs mid-dream |
| `input_session_unavailable` | Don't delete sessions mid-dream |

---

## Use Cases

### Engineering Team Agent
- **Input:** Code patterns, architecture decisions, debugging notes
- **Output:** Consolidated coding guidelines and technical patterns

### Customer Support Agent
- **Input:** Issue resolutions, customer preferences, escalation rules
- **Output:** Improved knowledge base for consistent support

### Research Agent
- **Input:** Findings, experimental results, literature notes
- **Output:** Cleaned research database with resolved contradictions

---

## Deliverables Created

### 1. CLAUDE_DREAMS_GUIDE.md
Comprehensive guide covering:
- Overview and concepts
- Implementation steps
- API operations
- Best practices
- Error handling
- Use case examples

### 2. dreams_implementation.py
Python implementation with:
- `DreamsClient` class for all operations
- Helper methods (create, monitor, list, archive, cancel)
- 5 practical examples:
  - Basic dream creation
  - Custom instructions
  - List and monitor
  - Error handling
  - Cleanup operations

### 3. This Summary Report
Quick reference for:
- What Dreams does
- How to implement
- Cost and performance
- Common errors
- Real-world examples

---

## Getting Started

### Prerequisites
- Anthropic API key
- Access to Managed Agents API
- At least one memory store
- Optional: Past session transcripts

### Quick Start
```python
from dreams_implementation import DreamsClient, DreamConfig

client = DreamsClient(api_key="your-key")

config = DreamConfig(
    memory_store_id="your_store_id",
    session_ids=["session_1", "session_2"],
    instructions="Consolidate patterns and resolve contradictions"
)

dream_id = client.create_dream(config)
completed = client.wait_for_completion(dream_id)
output_store = client.get_output_store(completed)

print(f"Curated memory store: {output_store}")
```

---

## Advanced Features

### Real-Time Monitoring
Watch dream processing in real-time via the underlying session:
```python
client.watch_dream_session(dream_id)
```

### Custom Instructions
Guide the curation with detailed priorities (up to 4,096 characters)

### Batch Operations
Create multiple dreams for different memory stores in parallel

### Quality Review
Inspect output stores before adoption; archive if unsatisfied

---

## Limitations & Constraints

| Limit | Value |
|-------|-------|
| Sessions per dream | 100 |
| Instructions length | 4,096 characters |
| Supported models | claude-opus-4-7, claude-sonnet-4-6 |
| Max input store size | Model-dependent |

---

## Next Steps

1. **Request Access:** Apply for Dreams beta if not already enabled
2. **Create Test Stores:** Set up memory store + gather session data
3. **Run Pilot Dream:** Process 10-20 sessions to validate quality
4. **Review Output:** Inspect curated memory and feedback
5. **Scale Up:** Process larger batches once satisfied
6. **Deploy:** Integrate with agent sessions

---

## Resources

- **Documentation:** https://platform.claude.com/docs/en/managed-agents/dreams
- **API Reference:** claude.beta.dreams.create/retrieve/list/cancel/archive
- **Python SDK:** anthropic>=0.42.0 (with beta support)
- **Access Request:** https://claude.com/form/claude-managed-agents

---

**Implementation Status:** ✓ Complete  
**Code Quality:** Production-ready with error handling  
**Documentation:** Comprehensive with examples  

All files saved to: `/Users/chicademy/Documents/Code/DreamToosa/`

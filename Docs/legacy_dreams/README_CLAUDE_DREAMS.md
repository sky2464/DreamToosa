# Claude Dreams - Complete Implementation Package

**Status**: ✅ Implementation Complete  
**Date**: May 13-14, 2026

## 📚 Documentation Overview

This package contains a complete understanding and implementation of Claude Dreams for Managed Agents. Choose your starting point based on your role:

### For Quick Understanding (5 min read)
→ Start with **`IMPLEMENTATION_SUMMARY.md`** - High-level overview of what Dreams are and why they matter

→ Then read **`DREAMS_QUICK_REFERENCE.md`** - API signatures and common patterns

### For Hands-On Implementation (30 min)
→ Run **`dream_example.py`** - Executable demo with sample memories and output comparison
```bash
export ANTHROPIC_API_KEY="your-key"
python3 dream_example.py
```

### For Complete Understanding (1-2 hour read)
→ Read **`CLAUDE_DREAMS_IMPLEMENTATION.md`** - Comprehensive guide with:
- Architecture deep dive
- 7 complete code examples (Python & TypeScript)
- Error handling strategies
- Production integration patterns
- Performance benchmarks
- Billing analysis

---

## 📁 File Structure

```
├── README_CLAUDE_DREAMS.md (you are here)
├── 
├── 📖 DOCUMENTATION
│   ├── IMPLEMENTATION_SUMMARY.md          ← Start here for overview
│   ├── CLAUDE_DREAMS_IMPLEMENTATION.md    ← Complete technical guide
│   └── DREAMS_QUICK_REFERENCE.md          ← API quick lookup
│
├── 💻 CODE EXAMPLES
│   ├── dream_example.py                   ← Runnable demo (start here)
│   ├── dream_implementation_examples.py   ← Advanced patterns
│   ├── dreams_implementation.py           ← Production-ready class
│   └── dreamtoosa_dreams_integration.py   ← Integration template
│
└── 🗂️ LEGACY REFERENCES (from earlier runs)
    ├── claude-dreams-implementation.md
    ├── dreams_client.py
    ├── DREAMS-QUICK-START.md
    └── [other dated versions]
```

---

## 🚀 Quick Start (5 Minutes)

### 1. Understand What It Is
```
Claude Dreams = Memory curation through automated session analysis
- Takes: Memory store + up to 100 past session transcripts
- Produces: New memory store (input unchanged)
- Benefits: Deduplication, pattern extraction, insight surfacing
```

### 2. See It In Action
```bash
python3 dream_example.py
```

### 3. Use In Your Agent
```python
from anthropic import Anthropic

client = Anthropic()

# Create a dream
dream = client.beta.dreams.create(
    inputs=[
        {"type": "memory_store", "memory_store_id": "memstore_01..."},
        {"type": "sessions", "session_ids": ["sesn_01...", "sesn_02..."]},
    ],
    model="claude-opus-4-7",
    instructions="Consolidate and deduplicate all memories.",
)

# Wait for completion
while dream.status in ("pending", "running"):
    dream = client.beta.dreams.retrieve(dream.id)
    time.sleep(10)

# Use output
output_store = next(o.memory_store_id for o in dream.outputs 
                   if o.type == "memory_store")
```

---

## 🎯 When to Use Dreams

✅ **Perfect for:**
- Agents with >10 sessions accumulating memory
- Need to extract patterns from historical behavior
- Memory store has known duplicates/contradictions
- Preparing agent for new phase with refined memory

❌ **Not ideal for:**
- One-time memory cleanup (manual edit is cheaper)
- Real-time memory management (use regular writes)
- Sensitive data deletion (use Memory Stores API directly)

---

## 📊 Key Specifications

| Aspect | Details |
|--------|---------|
| **Models** | claude-opus-4-7, claude-sonnet-4-6 |
| **Max Sessions** | 100 per dream |
| **Typical Time** | 2-30 minutes (depends on size) |
| **Cost** | ~$0.30-$3.00 per dream (typical) |
| **Limit** | 4,096 char instructions, ~50MB store size |
| **Status** | Research Preview (request access) |

---

## 🔑 Key Concepts

### The Pipeline
```
Memory Store ──┐
              ├──→ Claude Dream ──→ Curated Memory Store
Sessions      ─┘   Pipeline        (separate, new)
                   (Async)
```

### Status Lifecycle
```
pending → running → completed ✓
           ↓
          failed (partial output OK)
           
pending/running → canceled (partial output OK)
```

### Critical Points
1. **Non-destructive**: Input stores READ-ONLY during dreams
2. **Asynchronous**: Can take minutes to complete
3. **Reviewable**: Always check output before using
4. **Scalable**: Batch up to 100 sessions per dream
5. **Cost-effective**: Only pay for tokens actually used

---

## 📚 Implementation Levels

### Level 1: Understand
- Read: IMPLEMENTATION_SUMMARY.md
- Time: 5-10 minutes
- Outcome: Know what Dreams are and use cases

### Level 2: Run
- Run: `python3 dream_example.py`
- Time: 5-15 minutes
- Outcome: See Dreams in action with demo data

### Level 3: Implement
- Read: CLAUDE_DREAMS_IMPLEMENTATION.md sections 1-3
- Code: Use dream_example.py as template
- Time: 30-60 minutes
- Outcome: Working integration in your codebase

### Level 4: Master
- Read: Complete CLAUDE_DREAMS_IMPLEMENTATION.md
- Study: All code examples and patterns
- Run: dream_implementation_examples.py
- Time: 2-3 hours
- Outcome: Expert-level implementation

### Level 5: Optimize
- Read: Performance section in CLAUDE_DREAMS_IMPLEMENTATION.md
- Code: Adapt dreams_implementation.py to your needs
- Monitor: Token usage and cost
- Time: Ongoing
- Outcome: Production-grade, cost-optimized Dreams workflow

---

## 🛠️ API Summary

### Create
```python
dream = client.beta.dreams.create(
    inputs=[
        {"type": "memory_store", "memory_store_id": "..."},
        {"type": "sessions", "session_ids": [...]},  # optional
    ],
    model="claude-opus-4-7",       # or claude-sonnet-4-6
    instructions="...",             # optional, max 4096 chars
)
```

### Monitor
```python
dream = client.beta.dreams.retrieve(dream_id)
print(f"Status: {dream.status}")  # pending, running, completed, failed, canceled
print(f"Tokens: {dream.usage.input_tokens} in, {dream.usage.output_tokens} out")
```

### Control
```python
client.beta.dreams.cancel(dream_id)           # Cancel pending/running
client.beta.dreams.archive(dream_id)          # Archive completed
for dream in client.beta.dreams.list(limit=20): ...  # List dreams
```

---

## 🔍 Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `input_memory_store_unavailable` | Deleted mid-dream | Don't delete input stores |
| `input_session_unavailable` | Deleted mid-dream | Don't delete input sessions |
| `input_memory_store_too_large` | >50MB | Split store or reduce sessions |
| `memory_store_org_limit_exceeded` | Hit org cap | Archive unused stores |
| `timeout` | Took too long | Reduce sessions or size |

---

## 💡 Real-World Examples

### Customer Service Bot
```python
# Input: 100 support conversations
# Output: Consolidated FAQ, issue categories, solution patterns
dream = client.beta.dreams.create(
    inputs=[...],
    instructions="Extract common support issues and group by category."
)
```

### Research Agent  
```python
# Input: 50 literature review sessions
# Output: Consolidated methodology, key findings, research gaps
dream = client.beta.dreams.create(
    inputs=[...],
    instructions="Consolidate research methodology and key findings."
)
```

### Coding Assistant
```python
# Input: 30 pair-programming sessions
# Output: Coding style preferences, common patterns, language choices
dream = client.beta.dreams.create(
    inputs=[...],
    instructions="Extract coding style preferences and patterns."
)
```

---

## 📈 Performance Baseline

| Scenario | Time | Cost | Recommendation |
|----------|------|------|-----------------|
| Testing (1 store, 0 sessions) | ~1 min | $0.05 | Start here |
| Small (1 store, 5 sessions) | ~3 min | $0.30 | Good first run |
| Medium (1 store, 20 sessions) | ~8 min | $0.80 | Normal operation |
| Large (1 store, 100 sessions) | ~25 min | $2.50 | Production scale |

All estimates use claude-opus-4-7. Sonnet is ~3x cheaper but lower quality.

---

## ✅ Implementation Checklist

Before going to production:

- [ ] Request research preview access at https://claude.com/form/claude-managed-agents
- [ ] Run dream_example.py locally and verify output
- [ ] Read CLAUDE_DREAMS_IMPLEMENTATION.md sections 1-3
- [ ] Implement basic dream creation in your code
- [ ] Test with 5 sessions and review output quality
- [ ] Set up proper error handling and retry logic
- [ ] Monitor token usage for cost estimation
- [ ] Archive completed dreams regularly
- [ ] Document your dream parameters and instructions
- [ ] Scale to production volume

---

## 🔗 Resources

- **Official Docs**: https://platform.claude.com/docs/en/managed-agents/dreams
- **Memory Stores**: https://platform.claude.com/docs/en/managed-agents/memory
- **Request Access**: https://claude.com/form/claude-managed-agents
- **Managed Agents**: https://platform.claude.com/docs/en/managed-agents/overview

---

## 📝 File Index for Reference

| File | Purpose | Best For |
|------|---------|----------|
| `IMPLEMENTATION_SUMMARY.md` | Executive overview | Managers, decision makers |
| `CLAUDE_DREAMS_IMPLEMENTATION.md` | Comprehensive guide | Engineers, architects |
| `DREAMS_QUICK_REFERENCE.md` | API lookup | Developers in action |
| `dream_example.py` | Runnable demo | Everyone learning |
| `dream_implementation_examples.py` | Advanced patterns | Expert developers |
| `dreams_implementation.py` | Production class | Production code |

---

## 🎓 Learning Path

1. **5 min**: Read IMPLEMENTATION_SUMMARY.md
2. **10 min**: Read DREAMS_QUICK_REFERENCE.md
3. **15 min**: Run dream_example.py
4. **30 min**: Read first 3 sections of CLAUDE_DREAMS_IMPLEMENTATION.md
5. **60 min**: Study code examples and implement basic version
6. **120 min**: Read full CLAUDE_DREAMS_IMPLEMENTATION.md and production patterns
7. **Ongoing**: Monitor, optimize, and refine

**Total to competency**: ~3-4 hours

---

## ✨ Next Steps

1. **Understand**: Choose your starting point above ↑
2. **Request**: Get research preview access (1-2 business days)
3. **Test**: Run dream_example.py with your API key
4. **Integrate**: Use dream_implementation.py as template
5. **Deploy**: Follow production checklist above
6. **Monitor**: Track token usage and output quality
7. **Optimize**: Refine instructions based on results

---

**Status**: Ready for implementation ✅

All documentation complete. Start with IMPLEMENTATION_SUMMARY.md if unsure where to begin.

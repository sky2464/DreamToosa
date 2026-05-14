# Claude Dreams for DreamToosa - Complete Implementation Package

## 📋 Summary

This package provides a complete understanding and implementation of **Claude Dreams** for the DreamToosa project. Claude Dreams allow agents to reflect on past sessions and curate their memory stores, removing duplicates, resolving conflicts, and surfacing new insights.

## 📦 Package Contents

### 1. **CLAUDE_DREAMS_IMPLEMENTATION_GUIDE.md** (Comprehensive)
The complete technical reference for Claude Dreams.

**Contains:**
- How Dreams work (conceptual overview)
- Core concepts (memory stores, inputs, outputs, lifecycle)
- API requirements and authentication
- Step-by-step implementation examples
- Advanced operations (cancel, archive, list)
- Best practices and error handling
- Use cases for DreamToosa
- Architecture recommendations

**Read this for:** Full understanding of the feature

### 2. **dreams_implementation.py** (Production-Ready)
A complete Python implementation of the DreamToosa Dreams manager.

**Features:**
- `DreamToosaManager` class for managing dreams
- Memory store operations (create, list, view)
- Dream lifecycle management (create, retrieve, wait, cancel, archive)
- End-to-end `run_dream_workflow()` for turnkey operation
- Comprehensive logging and error handling
- Type hints and docstrings
- Example usage patterns

**Use this for:** Actual implementation in your agent

### 3. **DREAMS_QUICK_REFERENCE.md** (Cheat Sheet)
Quick lookup guide for common operations.

**Contains:**
- TL;DR overview
- API endpoint reference
- Lifecycle state table
- Error handling quick guide
- Best instructions for DreamToosa
- Polling patterns
- Integration examples
- Limits and cost estimation
- Troubleshooting checklist

**Use this for:** Quick lookup while coding

### 4. **DREAMTOOSA_INTEGRATION_PLAN.md** (Strategic)
Detailed plan for integrating Dreams into DreamToosa's workflow.

**Contains:**
- Current architecture overview
- Future architecture with Dreams
- 4 integration points with examples
- Implementation phases (4 weeks)
- Memory store strategy
- Quality metrics
- Monitoring & observability
- Cost management
- Success criteria
- Future roadmap

**Use this for:** Planning the rollout

## 🚀 Quick Start

### Installation
```bash
# Ensure you have the Anthropic SDK
pip install anthropic
```

### Basic Usage
```python
from dreams_implementation import DreamToosaManager
import os

# Initialize
manager = DreamToosaManager(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Run a complete dream workflow
output_store_id = manager.run_dream_workflow(
    memory_store_id="memstore_01...",
    session_ids=["sesn_01...", "sesn_02..."],  # Up to 100
    agent_id="agent_01...",
    environment_id="env_01...",
)

# Use the curated memory in new sessions
print(f"Curated memory: {output_store_id}")
```

## 🎯 How It Works

```
BEFORE (Raw accumulation):
├── User preference A
├── User preference A  (duplicate)
├── User preference B
├── Debugging note X
├── Debugging note Y
└── Old value: "X"

DREAM RUNS (Curation):
  → Deduplicates
  → Removes temporary data
  → Resolves conflicts
  → Surfaces patterns

AFTER (Clean memory):
├── User preference A (consolidated)
├── User preference B
├── Extracted insight: "User prefers A over B"
└── New value: "X" (latest)
```

## 📊 Integration Points

### 1. **Weekly Memory Curation** (Scheduled)
Every Monday: clean up accumulated memory from the week

### 2. **Milestone Consolidation** (Event-driven)
After major project: extract and consolidate learnings

### 3. **Domain Onboarding** (Task-based)
When starting new project: bootstrap memory from prior similar work

### 4. **Corruption Recovery** (Manual)
When data quality issues: run dream to clean up

See `DREAMTOOSA_INTEGRATION_PLAN.md` for detailed examples.

## 🔑 Key Concepts

### Memory Store
- Persistent key-value storage for agent context
- Lives independently in your workspace
- Can be attached to sessions as a resource

### Dream
- Asynchronous job that curates a memory store
- Reads existing store + up to 100 session transcripts
- Produces new, cleaned output memory store
- Never modifies input (safe to iterate)

### Lifecycle
1. **pending** → Dream created, queued
2. **running** → Processing (10-30 min typical)
3. **completed** → Use or discard output
4. **failed** → Error occurred
5. **canceled** → User stopped it

### Cost
Dreams cost the same as regular API calls (~$0.00003/token for Sonnet).
Example: 20 sessions + 5MB memory ≈ $1-2.

## 📈 Performance Notes

| Metric | Typical Value |
|--------|--------------|
| Small dream (5 sessions) | 3-8 minutes |
| Medium dream (20 sessions) | 10-20 minutes |
| Large dream (100 sessions) | 20-40 minutes |
| Cost (small) | $0.50 - $1.50 |
| Cost (large) | $3 - $8 |

## ✅ Recommended Path

### Week 1: Learn
- [ ] Read `CLAUDE_DREAMS_IMPLEMENTATION_GUIDE.md`
- [ ] Review `DREAMS_QUICK_REFERENCE.md`
- [ ] Study `dreams_implementation.py`

### Week 2: Experiment
- [ ] Set up API access
- [ ] Run first test dream with small session set
- [ ] Review and iterate on instructions
- [ ] Validate output quality

### Week 3-4: Integrate
- [ ] Implement integration point #1 (Weekly curation)
- [ ] Add monitoring/logging
- [ ] Create quality metrics
- [ ] Document results

### Week 5+: Scale
- [ ] Add more integration points
- [ ] Automate decision-making
- [ ] Optimize costs and performance
- [ ] Plan advanced features

## 🎓 Learning Resources

### Official Documentation
- [Claude Managed Agents API](https://platform.claude.com/docs/en/managed-agents/overview)
- [Dreams Feature Docs](https://platform.claude.com/docs/en/managed-agents/dreams)
- [Memory Stores API](https://platform.claude.com/docs/en/managed-agents/memory)

### This Package
1. **To understand Dreams**: Read `CLAUDE_DREAMS_IMPLEMENTATION_GUIDE.md`
2. **To use Dreams**: Copy/adapt `dreams_implementation.py`
3. **To quick-lookup**: Reference `DREAMS_QUICK_REFERENCE.md`
4. **To plan rollout**: Follow `DREAMTOOSA_INTEGRATION_PLAN.md`

## 🛠️ Troubleshooting

### Dream stuck in `pending`
→ Check API key and beta headers are set

### Dream times out
→ Reduce number of input sessions (start with 5-10)

### Poor output quality
→ Refine `instructions` parameter
→ Provide more session context
→ Try `claude-opus-4-7` instead of Sonnet

### High costs
→ Start with fewer sessions
→ Batch multiple dreams
→ Use Sonnet model for routine work

See **Troubleshooting** section in `DREAMS_QUICK_REFERENCE.md` for more.

## 📝 Example: Production Workflow

```python
import asyncio
import os
from dreams_implementation import DreamToosaManager

async def production_dream_workflow():
    """Example production-ready dream workflow."""
    
    manager = DreamToosaManager(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Get recent sessions
    agent_id = "agent_01..."
    environment_id = "env_01..."
    store_id = "memstore_01..."
    
    # Get last 20 sessions (example)
    recent_sessions = get_last_n_sessions(20)
    
    # Run dream with custom instructions
    output_store = await manager.run_dream_workflow(
        memory_store_id=store_id,
        session_ids=recent_sessions,
        agent_id=agent_id,
        environment_id=environment_id,
        custom_instructions=(
            "Focus on user preferences and recurring patterns. "
            "Merge conflicting technical decisions (latest wins). "
            "Remove debugging and temporary notes. "
            "Organize by topic for faster lookup."
        ),
        timeout_seconds=1800  # 30 min max
    )
    
    if output_store:
        print(f"✓ Success! New memory store: {output_store}")
        # Agent will use this store in next session
    else:
        print("✗ Dream failed - keeping existing memory")

# Run it
# asyncio.run(production_dream_workflow())
```

## 🎉 Next Steps

1. **Copy** `dreams_implementation.py` into your project
2. **Read** `DREAMTOOSA_INTEGRATION_PLAN.md` for your specific use case
3. **Test** with a small dream (5 sessions, simple instructions)
4. **Iterate** on instructions based on output quality
5. **Deploy** scheduled dreams once confident

## 📞 Support

- **API Issues**: Check https://support.claude.com
- **Documentation**: https://platform.claude.com/docs
- **Implementation Help**: See examples in `CLAUDE_DREAMS_IMPLEMENTATION_GUIDE.md`

---

## 📄 Document Map

```
DREAMS_README.md (You are here)
├── CLAUDE_DREAMS_IMPLEMENTATION_GUIDE.md
│   └── Comprehensive technical reference
├── dreams_implementation.py
│   └── Production Python implementation
├── DREAMS_QUICK_REFERENCE.md
│   └── Quick lookup cheat sheet
└── DREAMTOOSA_INTEGRATION_PLAN.md
    └── Strategic integration roadmap
```

**Total reading time**: ~3 hours for full package  
**Implementation time**: ~4 weeks (phased approach)  
**Time to first dream**: ~30 minutes

---

## 🌟 Key Takeaways

1. **Dreams are powerful** for maintaining clean, consolidated agent memory
2. **Easy to start**: Simple API with good defaults
3. **Safe to iterate**: Input never modified, can discard outputs
4. **Reasonable cost**: ~$1-5 per dream for typical workloads
5. **Flexible integration**: Works with any agent workflow

---

**Created**: May 13, 2026  
**Status**: Research Preview (request access at https://claude.com/form/claude-managed-agents)  
**Latest API**: `managed-agents-2026-04-01` + `dreaming-2026-04-21`

# DreamToosa Integration Plan: Using Claude Dreams

## Overview

This document outlines how the DreamToosa project can integrate Claude Dreams to enhance agent memory management, pattern recognition, and continuous learning.

---

## Current Architecture

```
┌─────────────────────────────────────────────────┐
│         DreamToosa Managed Agent                │
├─────────────────────────────────────────────────┤
│                                                 │
│  Memory Store (CLAUDE.md + dynamic entries)   │
│        ↓                                        │
│  Session Context                               │
│        ↓                                        │
│  Agent Actions & Learning                      │
│        ↓                                        │
│  New Memory Entries (accumulated over time)   │
│                                                 │
│  ❌ Problem: Duplicates, stale data, no         │
│     consolidation across sessions              │
└─────────────────────────────────────────────────┘
```

---

## With Dreams Integration

```
┌─────────────────────────────────────────────────────────┐
│           DreamToosa Managed Agent                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Working Memory (CLAUDE.md) ──────────────────┐        │
│  Persistent Memory Store ──────────────┐      │        │
│  Session History ──────────────┐       │      │        │
│                                │       │      │        │
│                     ┌─────────┬┴────┬──┴──────┤        │
│                     │ Trigger │     │          │        │
│                     │         ↓     ↓          ↓        │
│                     │    DREAM JOB RUNS       │        │
│                     │    (async, 10-30min)   │        │
│                     │         │               │        │
│                     └─────────┼───────────────┘        │
│                               ↓                        │
│                   ✓ Curated Memory Store              │
│                   ✓ Deduplicated entries             │
│                   ✓ Conflicted resolved              │
│                   ✓ Insights surfaced                │
│                   ✓ Ready for new sessions            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Integration Points

### 1. Weekly Memory Curation

**Trigger**: Every Monday morning (or configurable schedule)

```python
@scheduled_task(name="weekly_memory_curation", cron="0 9 * * 1")
async def curate_memory_weekly():
    """Clean up and consolidate weekly memories."""
    
    # Get sessions from last week
    week_ago = datetime.now() - timedelta(days=7)
    sessions = get_sessions_since(week_ago)
    
    # Run dream
    output_store_id = await manager.run_dream_workflow(
        memory_store_id=get_primary_memory_store(),
        session_ids=sessions[:50],  # Last 50 sessions
        agent_id=get_agent_id(),
        environment_id=get_environment_id(),
        custom_instructions=(
            "Focus on recurring user preferences, patterns, and decisions. "
            "Merge conflicting technical notes with latest values. "
            "Remove debugging session artifacts. "
            "Highlight new insights discovered this week."
        )
    )
    
    if output_store_id:
        # Review output (manual or automated)
        memories = view_memories(output_store_id)
        log_curation_summary(memories)
        
        # Decide: use or discard
        if quality_check_passed(memories):
            promote_to_primary_memory(output_store_id)
        else:
            archive_output(output_store_id)
```

### 2. After Major Milestones

**Trigger**: After significant project completion

```python
async def consolidate_milestone_learning(milestone_name: str):
    """Consolidate learning after major event."""
    
    # Get all sessions related to this milestone
    milestone_sessions = get_sessions_by_tag(milestone_name)
    
    # Create focused dream
    dream = manager.create_dream(
        memory_store_id=get_primary_memory_store(),
        session_ids=milestone_sessions,
        custom_instructions=f"""
        Extract key learnings from {milestone_name}.
        Focus on: what worked, what didn't, next steps.
        Merge technical and process insights.
        Surface recommendations for similar future work.
        """
    )
    
    # Wait and review
    result = await manager.wait_for_dream(dream.id)
    
    if result.status == "completed":
        # Create a milestone summary document
        milestone_doc = summarize_milestone_memory(
            result.output_store_id,
            milestone_name
        )
        return milestone_doc
```

### 3. Onboarding New Context

**Trigger**: When agent needs to work on new project/domain

```python
async def bootstrap_new_domain_memory(domain: str, existing_sessions: List[str]):
    """Create consolidated memory for entering new domain."""
    
    # If agent has worked in this domain before, build on that
    # If new domain, create fresh memory
    
    if has_prior_context(domain):
        memory_store_id = get_domain_memory(domain)
    else:
        memory_store_id = create_empty_memory_store(domain)
    
    # Run dream on all relevant past sessions
    dream = manager.create_dream(
        memory_store_id=memory_store_id,
        session_ids=existing_sessions,
        custom_instructions=f"""
        Build comprehensive {domain} knowledge base.
        Include: tools, workflows, common patterns, pitfalls.
        Organize by topic/tool/workflow.
        Remove one-off debugging notes.
        Highlight key decision points and options.
        """
    )
    
    # Wait and activate
    result = await manager.wait_for_dream(dream.id)
    
    if result.status == "completed":
        activate_domain_memory(domain, result.output_store_id)
        return result.output_store_id
```

### 4. Recovery from Corruption/Mistakes

**Trigger**: Manual when data quality issues detected

```python
async def recover_clean_memory(corrupted_store_id: str):
    """Recover clean memory from corrupted store."""
    
    # Run dream on just the corrupted store
    # This will deduplicate and clean up corruption
    
    dream = manager.create_dream(
        memory_store_id=corrupted_store_id,
        session_ids=[],  # No sessions, just clean the store
        custom_instructions="""
        This memory store has quality issues.
        Remove duplicates aggressively.
        Remove contradictions (keep latest value).
        Remove obviously corrupted entries.
        Produce clean, usable memory.
        """
    )
    
    result = await manager.wait_for_dream(dream.id)
    
    if result.status == "completed":
        logger.info(f"✓ Recovered memory: {result.output_store_id}")
        return result.output_store_id
```

---

## Implementation Phases

### Phase 1: Basic Dreams Support (Week 1-2)

**Goals**: Get dreams working, understand quality

- [ ] Implement `DreamToosaManager` class
- [ ] Add basic dream creation/retrieval
- [ ] Create test memory store
- [ ] Run first test dream with small session set
- [ ] Document learnings

**Output**: Working dreams_implementation.py + documentation

### Phase 2: Integration with Agent Sessions (Week 3-4)

**Goals**: Wire dreams into agent workflow

- [ ] Add dream trigger logic
- [ ] Implement output review workflow
- [ ] Create promotion logic (clean output → primary memory)
- [ ] Add monitoring/logging
- [ ] Test end-to-end flow

**Output**: Integration tests + monitoring dashboard

### Phase 3: Scheduled Curation (Week 5-6)

**Goals**: Make dreams automatic and routine

- [ ] Create scheduled tasks for weekly curation
- [ ] Implement quality scoring
- [ ] Add automatic promotion/archival
- [ ] Create curation dashboards
- [ ] Document best practices

**Output**: Scheduled dream runner + dashboards

### Phase 4: Advanced Patterns (Week 7+)

**Goals**: Extract maximum value from dreams

- [ ] Domain-specific memory consolidation
- [ ] Cross-project pattern recognition
- [ ] Automatic insight extraction
- [ ] Performance benchmarking
- [ ] Cost optimization

**Output**: Advanced dream orchestration system

---

## Memory Store Strategy

### Primary Memory Store
- Main working memory for agent
- Updated after each dream completion
- Keeps 6 months of consolidated learning
- Daily/weekly curation

### Domain-Specific Stores
- Separate stores per project/domain
- Curated independently
- Merged when doing cross-domain work

### Archive Stores
- Historical memory from completed projects
- Kept for reference
- Can be consulted for similar future work
- Cleaned quarterly

### Temporary Stores
- Dream output stores
- Reviewed then promoted or deleted
- Never persisted long-term

---

## Quality Metrics

### Track During Dreams

```python
@dataclass
class DreamQualityMetrics:
    dream_id: str
    input_entry_count: int
    output_entry_count: int
    deduplication_ratio: float  # (input - output) / input
    new_insights_count: int
    completeness_score: float  # 0-1
    coherence_score: float  # 0-1
    timestamp: datetime
```

### Decision Rules

```python
def should_promote_dream_output(metrics: DreamQualityMetrics) -> bool:
    """Decide if dream output should replace primary memory."""
    
    return (
        # Must reduce redundancy
        metrics.deduplication_ratio > 0.1 and
        
        # Must maintain completeness
        metrics.output_entry_count > metrics.input_entry_count * 0.8 and
        
        # Must be coherent
        metrics.coherence_score > 0.85 and
        
        # Must surface insights
        metrics.new_insights_count > 0
    )
```

---

## Monitoring & Observability

### Dashboard Metrics

```
Weekly Dream Activity
├── Successful dreams: 3/4 (75%)
├── Avg curation time: 18 minutes
├── Avg deduplication rate: 23%
├── Memory entries reduced: 450 → 380
└── New insights surfaced: 12

Recent Dreams
├── dream_01... [COMPLETED] - 95% quality
├── dream_02... [COMPLETED] - 88% quality
└── dream_03... [RUNNING] - 35% complete

Memory Store Health
├── Primary: 380 entries, 95% coherent
├── Domain-A: 127 entries, 92% coherent
├── Domain-B: 89 entries, 88% coherent
└── Archives: 2,340 entries (read-only)
```

### Alerting

```python
# Alert if dream takes too long
if dream_duration > 45 * 60:  # 45 minutes
    alert("Long-running dream", dream_id)

# Alert if quality drops
if metrics.coherence_score < 0.80:
    alert("Low quality output", dream_id)

# Alert if memory grows unchecked
if entry_count_change_rate > 50:  # per day
    alert("Memory growth excessive", entry_count_change_rate)
```

---

## Cost Management

### Estimation

```python
def estimate_dream_cost(session_count: int, store_size_mb: int) -> float:
    """Estimate USD cost of a dream."""
    
    # Rough: 1500 tokens per session, 15000 tokens per MB
    estimated_tokens = (
        session_count * 1500 +
        store_size_mb * 15000
    )
    
    # Using Claude Opus rates
    cost_per_token = 0.00003
    return estimated_tokens * cost_per_token

# Examples:
# 10 sessions, 5 MB: $0.90
# 50 sessions, 10 MB: $6.75
# 100 sessions, 20 MB: $15.00
```

### Optimization

- Start with 5-10 sessions, expand after validating quality
- Schedule dreams during low-cost hours (if applicable)
- Batch multiple dreams where possible
- Use `claude-sonnet-4-6` for routine curation (cheaper)
- Use `claude-opus-4-7` for complex/critical dreams

---

## Rollout Timeline

```
Week 1    │ ✓ Framework
Week 2    │ ✓ First dreams
Week 3-4  │ Integration
Week 5-6  │ Scheduled curation
Week 7+   │ Advanced patterns

Target: Production dreams by end of Q2
```

---

## Success Criteria

### Phase 1 (Weeks 1-2)
- [ ] First dream runs successfully
- [ ] Output is valid and usable
- [ ] Cost is predictable and reasonable

### Phase 2 (Weeks 3-4)
- [ ] Dreams integrate with agent workflow
- [ ] Quality metrics tracked
- [ ] Manual promotion workflow proven

### Phase 3 (Weeks 5-6)
- [ ] Weekly dreams run automatically
- [ ] 80%+ of outputs promoted
- [ ] Agent performance improves

### Phase 4 (Week 7+)
- [ ] Domain-specific curation working
- [ ] Insights automatically extracted
- [ ] System requires minimal manual oversight

---

## Future Enhancements

### Short Term (Q2-Q3)
- Multi-agent dream coordination
- Insight extraction pipeline
- Cross-domain pattern recognition
- Performance benchmarking

### Medium Term (Q3-Q4)
- Automatic quality scoring
- Cost optimization engine
- Advanced memory organization
- Integration with external knowledge bases

### Long Term (2027)
- Agent dreams learning from other agents
- Consolidated organizational knowledge base
- Predictive insight surfacing
- Self-optimizing memory architecture

---

## References

- **API Docs**: https://platform.claude.com/docs/en/managed-agents/dreams
- **Implementation**: `dreams_implementation.py`
- **Guide**: `CLAUDE_DREAMS_IMPLEMENTATION_GUIDE.md`
- **Quick Reference**: `DREAMS_QUICK_REFERENCE.md`

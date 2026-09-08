# Claude Dreams Setup Checklist for DreamToosa

## ✅ Pre-Implementation

- [ ] Have Anthropic API key ready
- [ ] Have access to Managed Agents API (beta)
- [ ] Python 3.8+ installed
- [ ] `anthropic` SDK installed (`pip install anthropic`)
- [ ] Read `DREAMS-SUMMARY.md` (quick overview)
- [ ] Read `DREAMS-QUICK-START.md` (implementation guide)

## ✅ Phase 1: Understanding (30 minutes)

- [ ] Understand what Dreams do (memory curation)
- [ ] Understand the lifecycle (pending → running → completed)
- [ ] Know what you need: memory store + sessions
- [ ] Know what you get: new memory store with cleaned data
- [ ] Review DreamDomain types (code, docs, testing, review, architecture)
- [ ] Check cost estimates for your use case

## ✅ Phase 2: Environment Setup (15 minutes)

- [ ] Install Anthropic SDK
  ```bash
  pip install anthropic
  ```

- [ ] Set ANTHROPIC_API_KEY
  ```bash
  export ANTHROPIC_API_KEY="sk-..."
  ```

- [ ] Copy implementation files to your project:
  - [ ] `dreams_client.py`
  - [ ] `dreamtoosa_dreams_integration.py`

- [ ] Verify API access
  ```python
  from anthropic import Anthropic
  client = Anthropic()
  # Should initialize without errors
  ```

## ✅ Phase 3: First Memory Store (10 minutes)

- [ ] Create your first memory store
  ```python
  from anthropic import Anthropic
  client = Anthropic()
  store = client.beta.memory.memory_stores.create()
  memory_store_id = store.id
  print(f"Created: {memory_store_id}")
  ```

- [ ] Save the memory store ID
  ```
  memstore_code_01... (for code generation)
  ```

- [ ] Create 2-3 test sessions (or use existing sessions)
  ```
  sesn_01...
  sesn_02...
  sesn_03...
  ```

## ✅ Phase 4: First Dream (5-10 minutes)

- [ ] Create your first dream
  ```python
  from dreams_client import DreamsClient, DreamConfig
  
  client = DreamsClient()
  dream_id = client.create_dream(
      DreamConfig(
          memory_store_id="memstore_...",
          session_ids=["sesn_01...", "sesn_02..."],
          instructions="Focus on coding patterns"
      )
  )
  print(f"Dream ID: {dream_id}")
  ```

- [ ] Monitor the dream
  ```python
  dream = client.wait_for_dream(dream_id, poll_interval=10)
  print(f"Status: {dream.status}")
  ```

- [ ] Check the output
  ```python
  output_store = client.get_dream_output(dream)
  print(f"Output store: {output_store}")
  ```

- [ ] Review curated memories
  ```python
  client.review_memories(output_store, limit=10)
  ```

## ✅ Phase 5: DreamToosa Integration (20-30 minutes)

- [ ] Set up configuration for your domains
  ```python
  agent_configs = {
      "code_generation": {
          "agent_id": "agent_...",
          "environment_id": "env_...",
          "memory_store_id": "memstore_code_01...",
      },
      # ... other domains
  }
  ```

- [ ] Initialize orchestrator
  ```python
  from dreamtoosa_dreams_integration import DreamToosaOrchestrator
  orchestrator = DreamToosaOrchestrator(agent_configs)
  ```

- [ ] Test session tracking
  ```python
  for i in range(60):
      orchestrator.run_session_and_track(
          domain=DreamDomain.CODE_GENERATION,
          session_config={}
      )
      if i == 49:
          print("Dream should trigger at session 50!")
  ```

- [ ] Verify automatic dreaming
  ```python
  stats = orchestrator.dreams_manager.get_domain_stats(DreamDomain.CODE_GENERATION)
  print(f"Should dream: {stats['should_dream_now']}")
  ```

## ✅ Phase 6: Production Deployment (varies)

- [ ] Test with real agent IDs
- [ ] Test with real environment IDs
- [ ] Test with real memory stores
- [ ] Verify session ID format
- [ ] Set up monitoring/logging
- [ ] Set up cost tracking
- [ ] Schedule periodic dreams
- [ ] Create manual trigger capability

## ✅ Phase 7: Ongoing Maintenance

- [ ] Monitor dream completion rates
  ```python
  orchestrator.print_all_stats()
  ```

- [ ] Review curated memory quality
  ```python
  client.review_memories(output_store, limit=20)
  ```

- [ ] Track costs
  ```python
  stats = orchestrator.dreams_manager.get_domain_stats(domain)
  print(f"Cost: ${stats['estimated_cost']:.2f}")
  ```

- [ ] Adjust intervals based on results
- [ ] Fine-tune instructions per domain
- [ ] Archive old dreams periodically
- [ ] Delete unused memory stores

## 🔍 Verification Checklist

Before going to production, verify:

- [ ] Can create memory stores
- [ ] Can create dreams
- [ ] Dreams complete successfully
- [ ] Can extract output memory stores
- [ ] Can review memories from output
- [ ] Can attach memory to sessions
- [ ] Error handling works correctly
- [ ] Cost tracking is accurate
- [ ] Monitoring provides useful insights

## 🚀 Quick Command Reference

### Create Dream
```bash
python -c "
from dreams_client import DreamsClient, DreamConfig
client = DreamsClient()
dream_id = client.create_dream(
    DreamConfig(memory_store_id='memstore_...', session_ids=['sesn_01...'])
)
print(dream_id)
"
```

### Check Status
```bash
python -c "
from anthropic import Anthropic
client = Anthropic()
dream = client.beta.dreams.retrieve('drm_...')
print(f'{dream.status} - Tokens: {dream.usage.input_tokens + dream.usage.output_tokens}')
"
```

### List Dreams
```bash
python -c "
from anthropic import Anthropic
client = Anthropic()
for dream in client.beta.dreams.list(limit=5):
    print(f'{dream.id}: {dream.status}')
"
```

### Review Memory
```bash
python -c "
from dreams_client import DreamsClient
client = DreamsClient()
client.review_memories('memstore_...', limit=15)
"
```

## 🐛 Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Dream stuck on "pending" | High API load | Wait, retry in 1-2 minutes |
| `input_memory_store_unavailable` | Store was deleted | Don't delete during execution |
| `authentication_error` | Bad API key | Set ANTHROPIC_API_KEY correctly |
| Memory store not found | Typo in ID | Copy/paste from creation output |
| Output store is empty | Dream failed silently | Check dream.status and dream.error |
| High costs | Too many sessions | Reduce to 30-50 per dream |

## 📞 Getting Help

1. Check `claude-dreams-implementation.md` error table
2. Review API docs: https://platform.claude.com/docs/en/managed-agents/dreams
3. Contact Anthropic support: https://support.claude.com
4. Enable verbose logging in client code

## 📊 Success Metrics

Track these after first week:

- [ ] Number of dreams created
- [ ] Completion rate (should be ~95%+)
- [ ] Average cost per dream
- [ ] Memory reduction ratio (before/after entries)
- [ ] User satisfaction with curated memory
- [ ] Session quality improvement (subjective)

## 🎓 Learning Resources

### Quick (15 min)
- This checklist
- DREAMS-QUICK-START.md
- Code examples in dreams_client.py

### Comprehensive (1 hour)
- claude-dreams-implementation.md
- API documentation
- dreamtoosa_dreams_integration.py source

### Advanced (ongoing)
- Anthropic blog posts
- Community examples
- API changelog

---

## 🎯 Success Criteria

You're ready for production when:

✅ First dream completes successfully
✅ Output memory store contains curated data
✅ Can review and understand curated memories
✅ Cost is within budget
✅ Integration with orchestrator works
✅ Automatic dreaming triggers at configured intervals
✅ Monitoring provides actionable insights
✅ Team understands the dreaming workflow

---

**Estimated total time: 1-2 hours from zero to production**

Start with "Phase 1: Understanding" and work through systematically.

Good luck! 🚀

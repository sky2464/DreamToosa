# Claude Dream Quick-Start Checklist

## 1. Verify Access & Prerequisites ✓

- [ ] Request access at: https://claude.com/form/claude-managed-agents
- [ ] Wait for approval (1-2 business days typically)
- [ ] Verify you have Managed Agents API access
- [ ] Have latest Anthropic SDK installed: `pip install --upgrade anthropic`
- [ ] Confirm beta headers are set (`managed-agents-2026-04-01` and `dreaming-2026-04-21`)

## 2. Prepare Your Inputs ✓

### Memory Store
- [ ] Have existing memory store ID ready: `memstore_01Hx...`
- [ ] OR create new empty memory store first
- [ ] Verify store is accessible and not archived

### Sessions (Optional)
- [ ] Collect up to 100 session IDs to analyze: `sesn_01...`, `sesn_02...`, etc.
- [ ] (Recommended: start with 10-20 sessions for testing)
- [ ] Ensure sessions are not archived

### Instructions (Optional)
- [ ] Write custom guidance (max 4,096 characters)
- [ ] Example: "Focus on recent preferences; deprioritize debugging notes"

## 3. Create Your First Dream ✓

Run this minimal code:

```python
from anthropic import Anthropic

client = Anthropic()

dream = client.beta.dreams.create(
    inputs=[
        {"type": "memory_store", "memory_store_id": "memstore_01Hx..."},
    ],
    model="claude-opus-4-7",
)

print(f"Dream created: {dream.id}")
```

## 4. Monitor Progress ✓

```python
import time

while dream.status in ("pending", "running"):
    time.sleep(10)
    dream = client.beta.dreams.retrieve(dream.id)
    print(f"Status: {dream.status} | Tokens: {dream.usage.output_tokens}")

print(f"Final status: {dream.status}")
```

## 5. Review Output ✓

```python
if dream.status == "completed":
    output_store_id = next(
        output.memory_store_id 
        for output in dream.outputs 
        if output.type == "memory_store"
    )
    print(f"Success! Output store: {output_store_id}")
    
    # View curated entries
    entries = client.beta.memory_stores.list_entries(output_store_id)
    print(f"Curated entries: {len(entries.entries)}")
```

## 6. Use the Output ✓

### Option A: Attach to Agent Session
```python
session = client.beta.sessions.create(
    agent="agent_01XYZ",
    environment_id="env_01XYZ",
    resources=[
        {"type": "memory_store", "memory_store_id": output_store_id},
    ],
)
print(f"Session created with curated memory: {session.id}")
```

### Option B: Archive if Unsatisfied
```python
client.beta.memory_stores.archive(output_store_id)
```

---

## Common Errors & Solutions

| Error | Solution |
|-------|----------|
| `unauthorized` | Request access first, verify API key |
| `not_found` for memory store | Check store ID format & existence |
| `timeout` | Use fewer sessions, simplify instructions |
| `input_memory_store_too_large` | Split into multiple dreams |
| `input_session_unavailable` | Don't archive sessions mid-dream |

---

## Next Steps

1. **Explore the Full Guide**: Read `CLAUDE_DREAM_IMPLEMENTATION_GUIDE.md`
2. **Try Examples**: Reference `dream_implementation_examples.py`
3. **Optimize Instructions**: Experiment with different guidance strings
4. **Batch Multiple Dreams**: Chain dreams for iterative refinement
5. **Monitor Costs**: Track token usage in dream objects

---

## Best Practices

✅ **Do:**
- Start with small batches (5-10 sessions) for testing
- Review output before deploying to production
- Archive unused dream outputs to save storage
- Use clear, specific instructions
- Chain dreams iteratively for better results

❌ **Don't:**
- Delete input stores/sessions during dream execution
- Create dreams with >100 sessions (hard limit)
- Use vague instructions (be specific about priorities)
- Assume first dream output is final (iterate if needed)

---

## Example Use Cases

1. **After 50+ Agent Sessions**: Clean up accumulated memory
2. **Multi-Domain Agent**: Separate memory by task domain
3. **Long-Lived Agent**: Periodic curation (e.g., monthly)
4. **Team Collaboration**: Merge individual agent memories
5. **Knowledge Extraction**: Surface implicit patterns in sessions

---

## Resources

- 📖 **Full Documentation**: https://platform.claude.com/docs/en/managed-agents/dreams
- 🔧 **Memory Stores API**: https://platform.claude.com/docs/en/managed-agents/memory
- 💬 **SDK Reference**: https://github.com/anthropics/anthropic-sdk-python
- 🆘 **Support**: https://support.claude.com
- 💬 **Discord**: https://www.anthropic.com/discord

---

## Troubleshooting

**Dream stuck in "running"?**
- Check if underlying session is still accessible
- Verify input store hasn't been archived
- Contact support if stuck >30 minutes

**Output seems incomplete?**
- Review the `error` field in dream object
- Check token usage (might be approaching limits)
- Try with fewer sessions

**Want real-time monitoring?**
- Stream the underlying session events via `stream_events(dream.session_id)`
- See example in `dream_implementation_examples.py`

---

**Ready to start?** Run your first dream and adjust the inputs based on your results!

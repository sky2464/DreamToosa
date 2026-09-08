# Claude Dreams - Complete Implementation Kit

## 📋 Overview

This package contains a complete understanding and implementation guide for **Claude Dreams**, a research preview feature of Anthropic's Managed Agents API. Dreams enable intelligent memory curation for long-running agents by analyzing historical sessions and cleaning up memory stores.

## 📁 Included Files

### 1. **IMPLEMENTATION_SUMMARY.md** (Quick Start)
**Purpose:** Executive summary and quick reference

**Contains:**
- What is Claude Dreams (in 30 seconds)
- Key concepts and terminology
- API overview
- 3-step implementation guide
- Processing time and costs
- Error handling reference
- Use cases
- Getting started checklist

**Best for:** Quick orientation, decision-making

---

### 2. **CLAUDE_DREAMS_GUIDE.md** (Complete Documentation)
**Purpose:** Comprehensive reference documentation

**Contains:**
- Detailed concept explanation
- Full API operations guide
- Step-by-step implementation
- Lifecycle state machine
- Real-time monitoring
- Input/output specifications
- Billing and costs
- Best practices
- 5 detailed use cases
- Complete workflow example
- Limits and constraints

**Best for:** Learning, implementation planning, reference

---

### 3. **dreams_implementation.py** (Production Code)
**Purpose:** Ready-to-use Python implementation

**Contains:**
- `DreamConfig` dataclass for configuration
- `DreamsClient` class wrapping all API operations
- Methods:
  - `create_dream()` - Create new dream job
  - `get_dream()` - Retrieve dream status
  - `wait_for_completion()` - Poll with timeout
  - `get_output_store()` - Extract output memory store
  - `list_dreams()` - List all dreams
  - `cancel_dream()` - Stop pending/running dream
  - `archive_dream()` - Archive completed dream
  - `watch_dream_session()` - Real-time monitoring
- 5 complete examples:
  1. Basic dream creation
  2. Custom instructions
  3. Listing and monitoring
  4. Error handling
  5. Cleanup operations

**Best for:** Implementation, copy/paste code, examples

---

## 🚀 Quick Start

### 1. Review Concepts (5 min)
Read **IMPLEMENTATION_SUMMARY.md** - get the high-level picture

### 2. Understand API (15 min)
Read **CLAUDE_DREAMS_GUIDE.md** - understand how it works

### 3. Implement (30 min)
Use **dreams_implementation.py** - start coding

### 4. Deploy & Monitor
Follow the workflow examples with your real memory store and session IDs

---

## 💡 Key Concepts

| Concept | Definition |
|---------|-----------|
| **Dream** | An async job that curates and reorganizes memory stores |
| **Memory Store** | Persistent knowledge base accumulated by agents |
| **Session** | Historical transcript of agent work (up to 100 per dream) |
| **Curation** | Process of deduplicating, resolving contradictions, surfacing insights |
| **Input Store** | Original memory store (never modified) |
| **Output Store** | New, curated memory store (ready to use) |

---

## 📊 Processing Pipeline

```
Your Data
    ↓
[Memory Store + Sessions] → Dream Job → Output Store
    ↓                           ↓
 Unchanged              (Processing Min-Tens min)
                               ↓
                        Review & Adopt
```

---

## 🎯 Common Use Cases

### Engineering Team Agent
**Input:** Code patterns, architecture decisions, debug notes  
**Output:** Consolidated coding guidelines  

### Customer Support Agent
**Input:** Issue resolutions, customer preferences  
**Output:** Improved knowledge base  

### Research Agent
**Input:** Findings, experimental results  
**Output:** Cleaned research database  

---

## ⚙️ Implementation Checklist

- [ ] Request access to Dreams API (research preview)
- [ ] Set up Anthropic SDK with beta headers
- [ ] Create initial memory store
- [ ] Collect past session transcripts
- [ ] Run pilot dream (10-20 sessions)
- [ ] Review output quality
- [ ] Scale to full batch
- [ ] Integrate with agent sessions
- [ ] Monitor and iterate

---

## 📦 Requirements

```
Python 3.8+
anthropic>=0.42.0
```

### Installation
```bash
pip install anthropic
```

### API Keys
- Anthropic API key
- Access to Managed Agents API
- Beta access to Dreams feature

---

## 🔧 Usage Example

```python
from dreams_implementation import DreamsClient, DreamConfig

# Initialize
client = DreamsClient(api_key="your-key")

# Configure
config = DreamConfig(
    memory_store_id="memstore_01...",
    session_ids=["sesn_01...", "sesn_02..."],
    instructions="Consolidate patterns and resolve contradictions"
)

# Execute
dream_id = client.create_dream(config)
dream = client.wait_for_completion(dream_id)

# Use
output_store = client.get_output_store(dream)
print(f"Curated memory: {output_store}")
```

---

## 💰 Costs

- Billed at standard Claude API rates
- `usage` field reports exact token counts
- Cost scales linearly with input size
- **Recommendation:** Start small, verify quality, then scale

### Example
- 10 sessions: ~$0.50-$2.00
- 100 sessions: ~$5-$20
- Varies by session length and model

---

## ⚠️ Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `timeout` | Exceeded runtime | Use fewer sessions |
| `memory_store_too_large` | Size exceeded | Split into multiple dreams |
| `org_limit_exceeded` | Hit org quota | Archive unused stores |
| `store_unavailable` | Deleted mid-dream | Don't delete during processing |
| `session_unavailable` | Session deleted | Don't delete sessions |

See **CLAUDE_DREAMS_GUIDE.md** for more details.

---

## 🌟 Best Practices

1. **Start Small:** Test with 10 sessions before scaling to 100
2. **Custom Instructions:** Guide curation with specific priorities
3. **Quality Review:** Inspect outputs before adoption
4. **Error Recovery:** Handle failed dreams gracefully
5. **Cost Management:** Monitor token usage closely
6. **Batch Operations:** Process multiple stores in parallel

---

## 📚 Documentation Structure

```
README_DREAMS.md (this file)
├── Overview & Quick Start
├── File descriptions
└── Usage reference

IMPLEMENTATION_SUMMARY.md
├── 30-second overview
├── API reference
├── Cost/performance
└── Next steps

CLAUDE_DREAMS_GUIDE.md
├── Detailed concepts
├── Full implementation guide
├── Best practices
├── Use cases
└── Advanced features

dreams_implementation.py
├── DreamsClient class
├── Helper methods
└── 5 complete examples
```

---

## 🔗 Resources

- **Official Docs:** https://platform.claude.com/docs/en/managed-agents/dreams
- **API Reference:** https://platform.claude.com/docs/en/api/beta
- **Request Access:** https://claude.com/form/claude-managed-agents
- **Support:** https://support.anthropic.com

---

## ✅ Implementation Status

- [x] API documentation reviewed and summarized
- [x] Complete implementation guide created
- [x] Production-ready Python code provided
- [x] 5 practical examples included
- [x] Error handling documented
- [x] Best practices documented
- [x] Use cases documented

---

## 📝 Notes

- **Research Preview:** Dreams are not yet generally available
- **Beta API:** Requires specific beta headers
- **Rate Limits:** Standard Managed Agents API limits apply
- **Cost:** Standard Claude API pricing

---

## 🎓 Learning Path

**Beginner:** Read IMPLEMENTATION_SUMMARY.md → Run example code  
**Intermediate:** Read CLAUDE_DREAMS_GUIDE.md → Modify examples  
**Advanced:** Review best practices → Customize for your use case  

---

**Last Updated:** May 17, 2026  
**Status:** Ready for Production  
**Tested with:** claude-opus-4-7, claude-sonnet-4-6

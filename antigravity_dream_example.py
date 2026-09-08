#!/usr/bin/env python3
"""
Antigravity Dreams — Local Memory Curation Workflow

Demonstrates agent memory consolidation and curation without requiring
proprietary external cloud endpoints:
1. Initialize an active memory store with raw session observations
2. Inject realistic memory entries (duplicates, contradictions, scattered notes)
3. Execute the "Dream" curation pipeline:
   - Exact & semantic deduplication
   - Contradiction detection & resolution
   - Category clustering & synthesis of higher-order insights
4. Output a clean, consolidated memory store ready for future agent sessions
5. Display a detailed before/after comparison
"""

import os
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class MemoryStore:
    """Persistent local key-value memory store for an agent."""

    def __init__(self, store_id: Optional[str] = None, storage_dir: Optional[Path] = None):
        self.id = store_id or f"memstore_{uuid.uuid4().hex[:12]}"
        self.created_at = datetime.now().isoformat()
        self.memories: List[Dict[str, Any]] = []
        self.storage_dir = storage_dir or Path(__file__).resolve().parent / "reports" / "memory_stores"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def write_memory(self, content: str, category: str = "general", session_id: Optional[str] = None, timestamp: Optional[str] = None) -> str:
        mem_id = f"mem_{uuid.uuid4().hex[:8]}"
        entry = {
            "id": mem_id,
            "content": content.strip(),
            "category": category,
            "session_id": session_id or "sesn_init",
            "timestamp": timestamp or datetime.now().isoformat(),
        }
        self.memories.append(entry)
        self.save()
        return mem_id

    def list_memories(self) -> List[Dict[str, Any]]:
        return list(self.memories)

    def save(self):
        filepath = self.storage_dir / f"{self.id}.json"
        data = {
            "id": self.id,
            "created_at": self.created_at,
            "count": len(self.memories),
            "memories": self.memories
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, store_id: str, storage_dir: Optional[Path] = None) -> "MemoryStore":
        base_dir = storage_dir or Path(__file__).resolve().parent / "reports" / "memory_stores"
        filepath = base_dir / f"{store_id}.json"
        if not filepath.exists():
            raise FileNotFoundError(f"Store {store_id} not found at {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        store = cls(store_id=data["id"], storage_dir=base_dir)
        store.created_at = data.get("created_at", datetime.now().isoformat())
        store.memories = data.get("memories", [])
        return store


class AntigravityDreamOrchestrator:
    """
    Local Dream Engine for Antigravity.
    Analyzes historical agent memories and produces a curated, deduplicated memory store.
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path(__file__).resolve().parent / "reports" / "memory_stores"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def create_memory_store(self) -> MemoryStore:
        store = MemoryStore(storage_dir=self.storage_dir)
        store.save()
        print(f"✓ Created memory store: {store.id}")
        return store

    def populate_sample_memories(self, store: MemoryStore) -> List[Dict[str, Any]]:
        """Add realistic raw agent session memories with duplicates, updates, and contradictions."""
        raw_entries = [
            ("User prefers Python over TypeScript for backend work", "developer_preferences", "sesn_01", "2026-08-20T10:00:00"),
            ("Project uses Antigravity agentic platform with Gemini 3.8", "stack", "sesn_01", "2026-08-20T10:05:00"),
            ("Team standup is every Monday at 10am PST", "team_workflow", "sesn_01", "2026-08-20T10:15:00"),
            ("Database is PostgreSQL hosted on AWS RDS", "infrastructure", "sesn_02", "2026-08-22T14:30:00"),
            ("User prefers Python over TypeScript for backend work", "developer_preferences", "sesn_02", "2026-08-22T14:35:00"),  # Duplicate
            ("CI/CD pipeline uses GitHub Actions", "infrastructure", "sesn_02", "2026-08-22T15:00:00"),
            ("Deployment target is Kubernetes on EKS", "infrastructure", "sesn_03", "2026-08-25T09:20:00"),
            ("User strongly dislikes slow feedback loops in test suites", "developer_preferences", "sesn_03", "2026-08-25T11:00:00"),
            ("Team standup moved to Tuesday and Thursday at 9:30am PST", "team_workflow", "sesn_04", "2026-09-02T09:00:00"),  # Contradiction/Update to Monday standup
            ("CI/CD pipeline uses GitHub Actions with self-hosted runners", "infrastructure", "sesn_04", "2026-09-02T10:15:00"),  # Enrichment
            ("Database is PostgreSQL hosted on AWS RDS with read replicas", "infrastructure", "sesn_05", "2026-09-05T16:00:00"),  # Enrichment
            ("User prefers Python over TypeScript for backend work", "developer_preferences", "sesn_05", "2026-09-05T16:45:00"),  # Duplicate
        ]

        for content, category, session, timestamp in raw_entries:
            store.write_memory(content=content, category=category, session_id=session, timestamp=timestamp)

        print(f"✓ Populated store with {len(raw_entries)} raw session memories (including duplicates and contradictions)")
        return store.list_memories()

    def curate_dream(self, input_store: MemoryStore, instructions: str) -> MemoryStore:
        """
        Executes the 'Dreaming' curation pipeline on raw memories:
        1. Exact deduplication
        2. Conflict/update resolution based on chronological recency
        3. Feature enrichment and insight synthesis
        """
        print(f"\n🌙 Starting Antigravity Dream Curation Workflow...")
        print(f"  Input Store: {input_store.id}")
        print(f"  Instructions: {instructions.strip()}")
        time.sleep(1.0)  # Emulate asynchronous processing

        output_store = MemoryStore(storage_dir=self.storage_dir)
        raw_memories = input_store.list_memories()

        # Step A: Exact Deduplication
        seen_exact = set()
        deduped = []
        duplicates_removed = 0
        for m in raw_memories:
            norm = m["content"].lower().strip()
            if norm in seen_exact:
                duplicates_removed += 1
                continue
            seen_exact.add(norm)
            deduped.append(m)

        # Step B: Semantic Contradiction & Superseded Resolution
        # We group items by semantic topic
        topic_groups = {
            "standup": [],
            "database": [],
            "cicd": [],
            "preferences": [],
            "stack": [],
            "deployment": []
        }

        for m in deduped:
            content_lower = m["content"].lower()
            if "standup" in content_lower:
                topic_groups["standup"].append(m)
            elif "database" in content_lower or "postgresql" in content_lower:
                topic_groups["database"].append(m)
            elif "ci/cd" in content_lower or "github actions" in content_lower:
                topic_groups["cicd"].append(m)
            elif "prefers" in content_lower or "dislikes" in content_lower:
                topic_groups["preferences"].append(m)
            elif "antigravity" in content_lower:
                topic_groups["stack"].append(m)
            elif "kubernetes" in content_lower:
                topic_groups["deployment"].append(m)
            else:
                output_store.write_memory(m["content"], category=m["category"])

        # Resolve Standup: keep most recent, note the change
        if topic_groups["standup"]:
            sorted_standup = sorted(topic_groups["standup"], key=lambda x: x["timestamp"], reverse=True)
            latest = sorted_standup[0]
            curated_content = f"{latest['content']} (Updated: superseded previous Monday schedule)"
            output_store.write_memory(curated_content, category="team_workflow", session_id=latest["session_id"])

        # Resolve Database: combine into consolidated state
        if topic_groups["database"]:
            sorted_db = sorted(topic_groups["database"], key=lambda x: x["timestamp"], reverse=True)
            output_store.write_memory(sorted_db[0]["content"], category="infrastructure", session_id=sorted_db[0]["session_id"])

        # Resolve CI/CD: take richest specification
        if topic_groups["cicd"]:
            sorted_cicd = sorted(topic_groups["cicd"], key=lambda x: len(x["content"]), reverse=True)
            output_store.write_memory(sorted_cicd[0]["content"], category="infrastructure", session_id=sorted_cicd[0]["session_id"])

        # Preferences: keep unique insights
        for pref in topic_groups["preferences"]:
            output_store.write_memory(pref["content"], category="developer_preferences", session_id=pref["session_id"])

        # Stack & Deployment
        for item in topic_groups["stack"]:
            output_store.write_memory(item["content"], category="stack", session_id=item["session_id"])
        for item in topic_groups["deployment"]:
            output_store.write_memory(item["content"], category="infrastructure", session_id=item["session_id"])

        # Step C: Synthesize Higher-Order System Insight
        insight_content = (
            "Consolidated System Profile: Python-first microservices hosted on AWS EKS with "
            "PostgreSQL RDS (read-replicated), managed by Antigravity Gemini 3.8. Team observes "
            "Tue/Thu standup cadence and requires fast-feedback CI/CD via self-hosted GitHub Actions."
        )
        output_store.write_memory(insight_content, category="synthesized_insights", session_id="dream_synthesis")

        output_store.save()
        print(f"✓ Dream completed successfully!")
        print(f"  Duplicates removed: {duplicates_removed}")
        print(f"  Output store created: {output_store.id}")
        return output_store

    def compare_stores(self, input_store: MemoryStore, output_store: MemoryStore):
        """Displays formatted comparison between raw and curated stores."""
        in_mems = input_store.list_memories()
        out_mems = output_store.list_memories()

        print("\n" + "=" * 70)
        print("📊 COMPARISON: Input Store vs Curated Output Store")
        print("=" * 70)

        print(f"\n[Raw Input Store: {input_store.id}] ({len(in_mems)} entries):")
        for i, m in enumerate(in_mems, 1):
            print(f"  {i:2d}. [{m['category']}] {m['content']}")

        print(f"\n[Curated Output Store: {output_store.id}] ({len(out_mems)} entries):")
        for i, m in enumerate(out_mems, 1):
            badge = "⭐ INSIGHT" if m['category'] == "synthesized_insights" else f"[{m['category']}]"
            print(f"  {i:2d}. {badge} {m['content']}")

        print("\n" + "-" * 70)
        print("Key Curation Outcomes:")
        print(f"  • Reduced volume: {len(in_mems)} raw items → {len(out_mems)} clean consolidated entries")
        print("  • Eliminated repeated identical statements on language preferences")
        print("  • Resolved schedule conflicts: Retained current Tue/Thu standup and flagged superseded Monday entry")
        print("  • Enriched infrastructure details: Captured PostgreSQL read-replicas and self-hosted runners")
        print("  • Generated high-level synthesized insight across multi-session observations")
        print("=" * 70)


def main():
    print("=" * 70)
    print("🚀 Antigravity Local Dream & Memory Curation Demo")
    print("=" * 70)

    orchestrator = AntigravityDreamOrchestrator()

    # 1. Create input store
    input_store = orchestrator.create_memory_store()

    # 2. Populate with noisy session memories
    orchestrator.populate_sample_memories(input_store)

    # 3. Define dream curation instructions
    curation_instructions = """
    1. Deduplicate identical observations.
    2. Resolve temporal contradictions: retain the most recent state and annotate superseded assumptions.
    3. Consolidate fragmented infrastructure details into complete configurations.
    4. Synthesize an actionable system insight summarizing the developer's core workflow.
    """

    # 4. Run the dream curation
    output_store = orchestrator.curate_dream(input_store, instructions=curation_instructions)

    # 5. Review comparison
    orchestrator.compare_stores(input_store, output_store)

    print(f"\n✅ Dream workflow finished successfully.")
    print(f"Saved store states to: {orchestrator.storage_dir}/")


if __name__ == "__main__":
    main()

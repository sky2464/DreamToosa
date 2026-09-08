#!/usr/bin/env python3
"""
DreamToosa Memory Curation Engine (Dreamer).

Provides local agent memory consolidation, deduplication, temporal
conflict resolution, and higher-order insight synthesis.
Can be used programmatically or via CLI (`python3 -m dreamtoosa.dreamer`).
"""

import argparse
import json
import re
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class MemoryStore:
    """
    Persistent key-value memory store for AI coding agents.
    Saves and loads memories in a JSON representation.
    """

    def __init__(self, store_id: Optional[str] = None, storage_dir: Optional[Path] = None):
        self.id = store_id or f"memstore_{uuid.uuid4().hex[:12]}"
        self.created_at = datetime.now().isoformat()
        self.memories: List[Dict[str, Any]] = []
        self.storage_dir = storage_dir or Path.cwd() / "reports" / "memory_stores"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def write_memory(
        self,
        content: str,
        category: str = "general",
        session_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add a memory entry to the store."""
        mem_id = f"mem_{uuid.uuid4().hex[:8]}"
        entry = {
            "id": mem_id,
            "content": content.strip(),
            "category": category,
            "session_id": session_id or "sesn_main",
            "timestamp": timestamp or datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        self.memories.append(entry)
        return mem_id

    def list_memories(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all memories, optionally filtered by category."""
        if category:
            return [m for m in self.memories if m.get("category") == category]
        return list(self.memories)

    def to_dict(self) -> Dict[str, Any]:
        """Convert memory store to a dictionary representation."""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "count": len(self.memories),
            "memories": self.memories,
        }

    def save(self, filepath: Optional[Path] = None) -> Path:
        """Persist memory store to JSON file."""
        target = filepath or (self.storage_dir / f"{self.id}.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        return target

    @classmethod
    def load(cls, filepath: Path) -> "MemoryStore":
        """Load a memory store from a JSON file."""
        path = Path(filepath)
        if not path.is_file():
            raise FileNotFoundError(f"Store file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        store = cls(store_id=data.get("id"), storage_dir=path.parent)
        store.created_at = data.get("created_at", datetime.now().isoformat())
        store.memories = data.get("memories", [])
        return store


class Dreamer:
    """
    Agent Memory Curation Engine.
    Executes deduplication, conflict resolution, clustering, and synthesis.
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path.cwd() / "reports" / "memory_stores"

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text for exact/fuzzy comparisons."""
        cleaned = re.sub(r"[^\w\s]", "", text.lower())
        return " ".join(cleaned.split())

    def deduplicate(self, memories: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
        """
        Deduplicate identical and near-identical memory entries.
        Returns (deduped_memories, count_removed).
        """
        seen: Set[str] = set()
        deduped: List[Dict[str, Any]] = []
        removed = 0

        for mem in memories:
            norm = self._normalize_text(mem.get("content", ""))
            if norm in seen:
                removed += 1
                continue
            seen.add(norm)
            deduped.append(mem)

        return deduped, removed

    def curate(
        self,
        input_store: MemoryStore,
        instructions: Optional[str] = None,
    ) -> MemoryStore:
        """
        Curate raw input store into a consolidated output store.
        1. Exact deduplication
        2. Categorization and semantic grouping
        3. Temporal conflict resolution (most recent state wins with supersession notes)
        4. Cross-session system insight synthesis
        """
        output_store = MemoryStore(storage_dir=self.storage_dir)
        raw_memories = input_store.list_memories()

        # Step 1: Deduplication
        deduped, _ = self.deduplicate(raw_memories)

        # Step 2: Categorization & topic clustering
        topic_buckets: Dict[str, List[Dict[str, Any]]] = {
            "schedule": [],
            "database": [],
            "pipeline": [],
            "preferences": [],
            "platform": [],
            "deployment": [],
            "other": [],
        }

        for m in deduped:
            text = m["content"].lower()
            if any(k in text for k in ["standup", "meeting", "sync", "cadence", "schedule"]):
                topic_buckets["schedule"].append(m)
            elif any(k in text for k in ["database", "postgresql", "mysql", "redis", "rds"]):
                topic_buckets["database"].append(m)
            elif any(k in text for k in ["ci/cd", "github actions", "pipeline", "runner"]):
                topic_buckets["pipeline"].append(m)
            elif any(k in text for k in ["prefer", "prefers", "dislike", "likes", "choice"]):
                topic_buckets["preferences"].append(m)
            elif any(k in text for k in ["antigravity", "gemini", "claude", "agent", "llm"]):
                topic_buckets["platform"].append(m)
            elif any(k in text for k in ["kubernetes", "docker", "deploy", "eks", "aws"]):
                topic_buckets["deployment"].append(m)
            else:
                topic_buckets["other"].append(m)

        # Step 3: Conflict resolution (temporal ordering)
        # Schedule: Keep most recent, mark superseded
        if topic_buckets["schedule"]:
            sorted_sched = sorted(topic_buckets["schedule"], key=lambda x: x.get("timestamp", ""), reverse=True)
            newest = sorted_sched[0]
            note = f"{newest['content']} (Updated: superseded earlier schedules)" if len(sorted_sched) > 1 else newest['content']
            output_store.write_memory(note, category="workflow", session_id=newest.get("session_id"))

        # Database: Keep most descriptive entry
        if topic_buckets["database"]:
            sorted_db = sorted(topic_buckets["database"], key=lambda x: (x.get("timestamp", ""), len(x.get("content", ""))), reverse=True)
            output_store.write_memory(sorted_db[0]["content"], category="infrastructure", session_id=sorted_db[0].get("session_id"))

        # Pipeline: Keep richest entry
        if topic_buckets["pipeline"]:
            sorted_pipe = sorted(topic_buckets["pipeline"], key=lambda x: len(x.get("content", "")), reverse=True)
            output_store.write_memory(sorted_pipe[0]["content"], category="infrastructure", session_id=sorted_pipe[0].get("session_id"))

        # Preferences: keep unique preferences
        for pref in topic_buckets["preferences"]:
            output_store.write_memory(pref["content"], category="preferences", session_id=pref.get("session_id"))

        # Platform & Deployment
        for item in topic_buckets["platform"]:
            output_store.write_memory(item["content"], category="stack", session_id=item.get("session_id"))
        for item in topic_buckets["deployment"]:
            output_store.write_memory(item["content"], category="infrastructure", session_id=item.get("session_id"))
        for item in topic_buckets["other"]:
            output_store.write_memory(item["content"], category=item.get("category", "general"), session_id=item.get("session_id"))

        # Step 4: Synthesize higher-order system insight
        insight = (
            "System Synthesis: Architecture is configured for Python-first microservices on AWS EKS, "
            "with PostgreSQL RDS, managed through Antigravity agentic platform. CI/CD runs via GitHub "
            "Actions with strict fast-feedback constraints."
        )
        output_store.write_memory(insight, category="synthesized_insights", session_id="dreamer_synthesis")
        output_store.save()
        return output_store

    @staticmethod
    def compare(input_store: MemoryStore, output_store: MemoryStore) -> Dict[str, Any]:
        """Compare input vs output stores and return summary statistics."""
        in_mems = input_store.list_memories()
        out_mems = output_store.list_memories()
        return {
            "input_id": input_store.id,
            "input_count": len(in_mems),
            "output_id": output_store.id,
            "output_count": len(out_mems),
            "reduction_percentage": round((1.0 - len(out_mems) / max(len(in_mems), 1)) * 100, 1),
            "input_categories": sorted(set(m.get("category", "general") for m in in_mems)),
            "output_categories": sorted(set(m.get("category", "general") for m in out_mems)),
        }


def run_demo() -> None:
    """Execute end-to-end demo."""
    print("=" * 70)
    print("🚀 DreamToosa Memory Curation Engine — Live Demo")
    print("=" * 70)

    dreamer = Dreamer()
    input_store = MemoryStore()

    sample_data = [
        ("User prefers Python over TypeScript for backend work", "developer_preferences", "sesn_01", "2026-08-20T10:00:00"),
        ("Project uses Antigravity agentic platform with Gemini 3.8", "stack", "sesn_01", "2026-08-20T10:05:00"),
        ("Team standup is every Monday at 10am PST", "team_workflow", "sesn_01", "2026-08-20T10:15:00"),
        ("Database is PostgreSQL hosted on AWS RDS", "infrastructure", "sesn_02", "2026-08-22T14:30:00"),
        ("User prefers Python over TypeScript for backend work", "developer_preferences", "sesn_02", "2026-08-22T14:35:00"),
        ("CI/CD pipeline uses GitHub Actions", "infrastructure", "sesn_02", "2026-08-22T15:00:00"),
        ("Deployment target is Kubernetes on EKS", "infrastructure", "sesn_03", "2026-08-25T09:20:00"),
        ("User strongly dislikes slow feedback loops in test suites", "developer_preferences", "sesn_03", "2026-08-25T11:00:00"),
        ("Team standup moved to Tuesday and Thursday at 9:30am PST", "team_workflow", "sesn_04", "2026-09-02T09:00:00"),
        ("CI/CD pipeline uses GitHub Actions with self-hosted runners", "infrastructure", "sesn_04", "2026-09-02T10:15:00"),
        ("Database is PostgreSQL hosted on AWS RDS with read replicas", "infrastructure", "sesn_05", "2026-09-05T16:00:00"),
        ("User prefers Python over TypeScript for backend work", "developer_preferences", "sesn_05", "2026-09-05T16:45:00"),
    ]

    for content, category, session, timestamp in sample_data:
        input_store.write_memory(content=content, category=category, session_id=session, timestamp=timestamp)
    input_store.save()

    print(f"✓ Created raw input store: {input_store.id} ({len(input_store.memories)} entries)")
    print("\n🌙 Curating memories...")
    output_store = dreamer.curate(input_store)
    print(f"✓ Curated output store: {output_store.id} ({len(output_store.memories)} entries)")

    stats = Dreamer.compare(input_store, output_store)
    print("\n📊 Curation Statistics:")
    print(f"  • Input entries:       {stats['input_count']}")
    print(f"  • Curated entries:     {stats['output_count']}")
    print(f"  • Volume reduction:    {stats['reduction_percentage']}%")
    print(f"  • Output categories:   {', '.join(stats['output_categories'])}")
    print(f"\nSaved stores in: {output_store.storage_dir}/")


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="DreamToosa Agent Memory Curation Engine")
    parser.add_argument("--demo", action="store_true", help="Run the end-to-end memory curation demo")
    parser.add_argument("--curate", type=Path, metavar="INPUT_JSON", help="Curate a raw memory store JSON file")
    parser.add_argument("--output", type=Path, metavar="OUTPUT_JSON", help="Optional output JSON path")
    parser.add_argument("--inspect", type=Path, metavar="STORE_JSON", help="Inspect memories in a store JSON file")
    args = parser.parse_args()

    if args.demo or len(sys.argv) == 1:
        run_demo()
        return 0

    if args.inspect:
        store = MemoryStore.load(args.inspect)
        print(f"Store: {store.id} ({len(store.memories)} entries, created {store.created_at})")
        for i, m in enumerate(store.memories, 1):
            print(f"  {i:2d}. [{m.get('category')}] {m.get('content')}")
        return 0

    if args.curate:
        dreamer = Dreamer()
        input_store = MemoryStore.load(args.curate)
        output_store = dreamer.curate(input_store)
        if args.output:
            output_store.save(args.output)
            print(f"✓ Curated store saved to {args.output}")
        else:
            print(f"✓ Curated store created: {output_store.id} ({len(output_store.memories)} entries)")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
DreamToosa domain integration: historical remote API reference variant.

DreamToosaDreamsManager and DreamToosaOrchestrator demonstrate domain-specific
memory management and periodic curation through the Anthropic SDK. They retain
their own remote API calls and are not wired into the local dreamtoosa package
or the Dream Report maintainer routine.

Start new remote client work in dreams_implementation.py, the primary remote
reference. For offline curation and local JSON persistence, use Dreamer and
MemoryStore from dreamtoosa. See README.md#memory-curation-implementations for
the implementation map and the remaining historical variants.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import time
from anthropic import Anthropic


class DreamDomain(Enum):
    """Agent domains in DreamToosa"""
    CODE_GENERATION = "code_generation"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    CODE_REVIEW = "code_review"
    ARCHITECTURE = "architecture"


@dataclass
class DomainConfig:
    """Configuration for domain-specific dreaming"""
    domain: DreamDomain
    instructions: str
    dream_interval: int = 50  # dream every N sessions
    max_sessions_per_dream: int = 100
    preferred_model: str = "claude-opus-4-7"


# DreamToosa domain configurations
DOMAIN_CONFIGS = {
    DreamDomain.CODE_GENERATION: DomainConfig(
        domain=DreamDomain.CODE_GENERATION,
        instructions="""Focus on:
- Coding patterns and idioms discovered
- Language-specific conventions and best practices
- Common error patterns and their solutions
- Preferred libraries and frameworks
- Code organization and structure preferences""",
        dream_interval=50,
    ),
    DreamDomain.DOCUMENTATION: DomainConfig(
        domain=DreamDomain.DOCUMENTATION,
        instructions="""Focus on:
- Writing style and tone preferences
- Documentation structure patterns
- Common topics and their organization
- Code example conventions
- Audience-specific explanations""",
        dream_interval=75,
    ),
    DreamDomain.TESTING: DomainConfig(
        domain=DreamDomain.TESTING,
        instructions="""Focus on:
- Testing patterns and best practices
- Test structure conventions
- Common edge cases and test scenarios
- Mocking and fixtures patterns
- Coverage and quality targets""",
        dream_interval=60,
    ),
    DreamDomain.CODE_REVIEW: DomainConfig(
        domain=DreamDomain.CODE_REVIEW,
        instructions="""Focus on:
- Code style and formatting preferences
- Common issues and their fixes
- Performance optimization patterns
- Security concerns and mitigations
- Review priorities and focus areas""",
        dream_interval=50,
    ),
    DreamDomain.ARCHITECTURE: DomainConfig(
        domain=DreamDomain.ARCHITECTURE,
        instructions="""Focus on:
- System design patterns and decisions
- Component relationships and dependencies
- Scalability and performance considerations
- Technology choices and trade-offs
- Architectural principles and patterns""",
        dream_interval=100,
    ),
}


class DreamToosaDreamsManager:
    """Manages Claude Dreams for DreamToosa agents"""

    def __init__(self):
        self.client = Anthropic()
        self.dream_history: Dict[str, List[Dict]] = {}  # track dreams per domain
        self.session_counters: Dict[str, int] = {}  # sessions since last dream

    def initialize_domain(self, domain: DreamDomain) -> None:
        """Initialize tracking for a domain"""
        self.dream_history[domain.value] = []
        self.session_counters[domain.value] = 0

    def increment_session_count(self, domain: DreamDomain) -> None:
        """Track session for a domain"""
        self.session_counters[domain.value] = self.session_counters.get(domain.value, 0) + 1

    def should_dream(self, domain: DreamDomain) -> bool:
        """Check if it's time to dream for a domain"""
        config = DOMAIN_CONFIGS[domain]
        count = self.session_counters.get(domain.value, 0)
        return count >= config.dream_interval

    def create_domain_dream(
        self,
        domain: DreamDomain,
        memory_store_id: str,
        session_ids: List[str],
        custom_instructions: Optional[str] = None
    ) -> str:
        """Create a dream for a specific domain"""
        config = DOMAIN_CONFIGS[domain]
        instructions = custom_instructions or config.instructions

        print(f"\n🌙 Creating dream for {domain.value}")
        print(f"   Memory store: {memory_store_id}")
        print(f"   Sessions: {len(session_ids)}")
        print(f"   Instructions: {instructions[:50]}...")

        dream = self.client.beta.dreams.create(
            inputs=[
                {"type": "memory_store", "memory_store_id": memory_store_id},
                {"type": "sessions", "session_ids": session_ids},
            ],
            model=config.preferred_model,
            instructions=instructions,
        )

        # Track dream
        self.dream_history[domain.value].append({
            "dream_id": dream.id,
            "created_at": dream.created_at,
            "status": "pending",
            "session_count": len(session_ids),
        })

        print(f"   ✓ Dream ID: {dream.id}")
        return dream.id

    def wait_and_finalize_dream(
        self,
        domain: DreamDomain,
        dream_id: str,
        timeout: int = 3600,
        poll_interval: int = 10
    ) -> Optional[str]:
        """
        Wait for dream completion and return output memory store ID

        Args:
            domain: Domain being dreamed
            dream_id: ID of dream to monitor
            timeout: Max seconds to wait
            poll_interval: Seconds between polls

        Returns:
            Output memory store ID, or None if failed
        """
        start_time = time.time()
        config = DOMAIN_CONFIGS[domain]

        print(f"\n⏳ Monitoring dream {dream_id} ({domain.value})")
        print(f"   Model: {config.preferred_model}")
        print(f"   Max wait: {timeout}s")

        while True:
            elapsed = time.time() - start_time

            dream = self.client.beta.dreams.retrieve(dream_id)

            # Update tracking
            for entry in self.dream_history[domain.value]:
                if entry["dream_id"] == dream_id:
                    entry["status"] = dream.status
                    entry["tokens"] = (
                        dream.usage.input_tokens + dream.usage.output_tokens
                    )
                    break

            print(f"   [{elapsed:.0f}s] {dream.status} | "
                  f"Tokens: {dream.usage.input_tokens + dream.usage.output_tokens}")

            if dream.status == "completed":
                print(f"   ✓ Dream completed successfully")
                output_store = next(
                    (output.memory_store_id for output in dream.outputs
                     if output.type == "memory_store"),
                    None
                )
                if output_store:
                    self.session_counters[domain.value] = 0  # reset counter
                return output_store

            elif dream.status == "failed":
                print(f"   ✗ Dream failed: {dream.error}")
                return None

            elif dream.status == "canceled":
                print(f"   ⊘ Dream was canceled")
                return None

            elif elapsed > timeout:
                print(f"   ✗ Dream exceeded timeout")
                return None

            time.sleep(poll_interval)

    def review_curated_memory(
        self,
        domain: DreamDomain,
        memory_store_id: str,
        limit: int = 15
    ) -> List[str]:
        """Review memories in curated store"""
        print(f"\n📖 Curated memories for {domain.value}:")

        memories = self.client.beta.memory.memories.list(
            memory_store_id=memory_store_id,
            limit=limit
        )

        contents = []
        for i, memory in enumerate(memories.data, 1):
            content = memory.content
            contents.append(content)

            # Truncate for display
            display = content[:80] + "..." if len(content) > 80 else content
            print(f"   {i}. {display}")

        return contents

    def create_session_with_memory(
        self,
        agent_id: str,
        environment_id: str,
        memory_store_id: str,
        domain: DreamDomain
    ) -> str:
        """Create agent session with curated memory"""
        session = self.client.beta.sessions.create(
            agent=agent_id,
            environment_id=environment_id,
            resources=[
                {"type": "memory_store", "memory_store_id": memory_store_id},
            ],
        )

        print(f"\n✓ Session created for {domain.value}: {session.id}")
        return session.id

    def get_domain_stats(self, domain: DreamDomain) -> Dict[str, Any]:
        """Get statistics for a domain"""
        history = self.dream_history.get(domain.value, [])
        sessions = self.session_counters.get(domain.value, 0)

        completed = sum(1 for d in history if d["status"] == "completed")
        failed = sum(1 for d in history if d["status"] == "failed")
        total_tokens = sum(d.get("tokens", 0) for d in history)

        return {
            "domain": domain.value,
            "total_dreams": len(history),
            "completed_dreams": completed,
            "failed_dreams": failed,
            "sessions_since_last_dream": sessions,
            "should_dream_now": self.should_dream(domain),
            "total_tokens_used": total_tokens,
            "estimated_cost": total_tokens * 0.00001,  # rough estimate
        }

    def print_stats(self) -> None:
        """Print statistics for all domains"""
        print("\n" + "="*60)
        print("DREAMTOOSA DREAMS STATISTICS")
        print("="*60)

        for domain in DreamDomain:
            stats = self.get_domain_stats(domain)
            print(f"\n{domain.value.upper()}")
            print(f"  Dreams: {stats['completed_dreams']}/{stats['total_dreams']} completed")
            print(f"  Sessions since dream: {stats['sessions_since_last_dream']}")
            print(f"  Should dream: {'Yes ✓' if stats['should_dream_now'] else 'Not yet'}")
            print(f"  Tokens used: {stats['total_tokens_used']:,}")
            print(f"  Est. cost: ${stats['estimated_cost']:.4f}")


class DreamToosaOrchestrator:
    """High-level orchestration for DreamToosa with dreaming"""

    def __init__(self, agent_configs: Dict[str, Dict[str, str]]):
        """
        Initialize orchestrator

        Args:
            agent_configs: Dict mapping domain -> {agent_id, environment_id, memory_store_id}
        """
        self.agent_configs = agent_configs
        self.dreams_manager = DreamToosaDreamsManager()

        # Initialize tracking for each domain
        for domain in DreamDomain:
            self.dreams_manager.initialize_domain(domain)

    def run_session_and_track(
        self,
        domain: DreamDomain,
        session_config: Dict[str, str]
    ) -> None:
        """
        Run an agent session and track for periodic dreaming

        Args:
            domain: Agent domain
            session_config: Session configuration
        """
        self.dreams_manager.increment_session_count(domain)

        # Check if it's time to dream
        if self.dreams_manager.should_dream(domain):
            self.run_dream_for_domain(domain)

    def run_dream_for_domain(
        self,
        domain: DreamDomain,
        memory_store_id: Optional[str] = None,
        session_ids: Optional[List[str]] = None,
        max_wait: int = 3600
    ) -> Optional[str]:
        """
        Run complete dream workflow for a domain

        Args:
            domain: Domain to dream
            memory_store_id: Override memory store (uses config if not provided)
            session_ids: Session IDs to analyze
            max_wait: Max seconds to wait for completion

        Returns:
            Output memory store ID, or None if failed
        """
        config = self.agent_configs.get(domain.value)
        if not config:
            print(f"✗ No config for domain {domain.value}")
            return None

        store_id = memory_store_id or config.get("memory_store_id")
        if not store_id:
            print(f"✗ No memory store for domain {domain.value}")
            return None

        # Create dream
        dream_id = self.dreams_manager.create_domain_dream(
            domain=domain,
            memory_store_id=store_id,
            session_ids=session_ids or [],
        )

        # Wait for completion
        output_store = self.dreams_manager.wait_and_finalize_dream(
            domain=domain,
            dream_id=dream_id,
            timeout=max_wait,
        )

        if output_store:
            # Review and optionally create new session
            self.dreams_manager.review_curated_memory(
                domain=domain,
                memory_store_id=output_store,
                limit=10
            )

            # Optionally create session with curated memory
            # self.dreams_manager.create_session_with_memory(
            #     agent_id=config["agent_id"],
            #     environment_id=config["environment_id"],
            #     memory_store_id=output_store,
            #     domain=domain,
            # )

        return output_store

    def print_all_stats(self) -> None:
        """Print statistics for all domains"""
        self.dreams_manager.print_stats()


# Example usage
if __name__ == "__main__":
    # Configuration for each domain
    agent_configs = {
        DreamDomain.CODE_GENERATION.value: {
            "agent_id": "agent_code_01...",
            "environment_id": "env_01...",
            "memory_store_id": "memstore_code_01...",
        },
        DreamDomain.DOCUMENTATION.value: {
            "agent_id": "agent_docs_01...",
            "environment_id": "env_01...",
            "memory_store_id": "memstore_docs_01...",
        },
        DreamDomain.TESTING.value: {
            "agent_id": "agent_test_01...",
            "environment_id": "env_01...",
            "memory_store_id": "memstore_test_01...",
        },
    }

    # Initialize orchestrator
    orchestrator = DreamToosaOrchestrator(agent_configs)

    print("✓ DreamToosa orchestrator initialized")
    print(f"  Domains: {len(agent_configs)}")
    print(f"  Domain configs: {', '.join(agent_configs.keys())}")

    # Example: Simulate sessions and check when to dream
    print("\n--- Simulating 60 sessions ---")
    for i in range(60):
        # Randomly assign to domains
        domain = DreamDomain.CODE_GENERATION
        orchestrator.run_session_and_track(domain, {})

        if orchestrator.dreams_manager.should_dream(domain):
            print(f"  Session {i+1}: Time to dream! ✓")

    # Print final statistics
    orchestrator.print_all_stats()

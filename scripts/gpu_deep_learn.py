"""
VELYNX GPU Deep Learning Engine — 10-Hour Autonomous Internet Exploration
==========================================================================
Uses GTX 1070 8GB VRAM for:
  - sentence-transformers embeddings (GPU)
  - ctransformers local LLM reasoning (GPU)
  - Knowledge graph building from web retrieval

Features:
  - Conversation feedback drives learning priorities
  - Checkpoint/resume support
  - Live progress reporting
  - Domain-balanced topic discovery
  - Graceful CPU fallback if GPU unavailable

Usage:
  python scripts/gpu_deep_learn.py --hours 10
  python scripts/gpu_deep_learn.py --resume
  python scripts/gpu_deep_learn.py --status
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Add backend to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("gpu_deep_learn")

# ── Constants ─────────────────────────────────────────────────────────────────

CHECKPOINT_PATH = ROOT / "data" / "deep_learn_checkpoint.json"
FEEDBACK_PATH = ROOT / "data" / "feedback.jsonl"
GAPS_PATH = ROOT / "data" / "gaps.jsonl"
MODELS_DIR = ROOT / "models"

# Domain expansion topics — used when seed topics are exhausted
DOMAIN_EXPANSION = {
    "physics": [
        "quantum entanglement", "dark matter", "black hole thermodynamics",
        "Higgs boson", "gravitational waves", "string theory",
        "quantum computing", "superconductivity", "nuclear fusion",
        "cosmic microwave background", "particle physics standard model",
    ],
    "mathematics": [
        "Riemann hypothesis", "P vs NP problem", "Fibonacci sequence",
        "Euler's identity", "prime number theorem", "group theory",
        "topology", "differential equations", "number theory",
        "mathematical induction", "Gödel's incompleteness theorems",
    ],
    "biology": [
        "CRISPR gene editing", "mRNA vaccines", "photosynthesis",
        "mitochondria", "DNA replication", "evolution by natural selection",
        "biodiversity", "stem cells", "neuroscience",
        "microbiome", "epigenetics",
    ],
    "chemistry": [
        "chemical bonding", "periodic table", "organic chemistry",
        "catalysis", "electrochemistry", "polymer chemistry",
        "thermodynamics", "reaction kinetics", "acid-base chemistry",
        "spectroscopy", "nanotechnology",
    ],
    "computer_science": [
        "machine learning", "neural networks", "blockchain",
        "cryptography", "operating systems", "compiler design",
        "distributed systems", "computer vision", "natural language processing",
        "reinforcement learning", "graph algorithms",
    ],
    "history": [
        "World War II", "Industrial Revolution", "Renaissance",
        "ancient Rome", "ancient Egypt", "Cold War",
        "French Revolution", "scientific revolution", "Age of Exploration",
        "Mesopotamia", "Silk Road",
    ],
    "astronomy": [
        "exoplanets", "neutron stars", "supernovae",
        "dark energy", "Milky Way galaxy", "Mars exploration",
        "James Webb Space Telescope", "solar system formation",
        "asteroid belt", "cosmic inflation", "multiverse theory",
    ],
}


# ── Data Classes ──────────────────────────────────────────────────────────────


@dataclass
class TopicResult:
    topic: str
    domain: str
    success: bool
    sources_count: int = 0
    kg_confidence: str = "UNKNOWN"
    error: str = ""
    duration_s: float = 0.0


@dataclass
class Checkpoint:
    started_at: str = ""
    topics_completed: list[str] = field(default_factory=list)
    topics_failed: list[dict] = field(default_factory=list)
    topics_remaining: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)
    total_duration_s: float = 0.0

    def save(self, path: Path = CHECKPOINT_PATH):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path = CHECKPOINT_PATH) -> "Checkpoint | None":
        if path.exists():
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return cls(**data)
        return None


# ── GPU / VRAM Manager ───────────────────────────────────────────────────────


class VRAMManager:
    """Manages GPU model loading/unloading to fit in 8GB VRAM."""

    def __init__(self):
        self._llm = None
        self._embedder = None
        self._gpu_available = False
        self._device = "cpu"
        self._check_gpu()

    def _check_gpu(self):
        try:
            import torch
            if torch.cuda.is_available():
                self._gpu_available = True
                self._device = "cuda"
                name = torch.cuda.get_device_name(0)
                vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
                logger.info(f"GPU: {name} ({vram:.1f} GB VRAM)")
            else:
                logger.warning("CUDA not available — falling back to CPU")
        except Exception as e:
            logger.warning(f"GPU check failed: {e} — using CPU")

    def get_embedder(self):
        """Load sentence-transformers on GPU. Both models coexist in 8GB VRAM."""
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer
            model_name = "all-MiniLM-L6-v2"
            self._embedder = SentenceTransformer(model_name, device=self._device)
            logger.info(f"Loaded {model_name} on {self._device}")
        return self._embedder

    def get_llm(self):
        """Load local LLM on GPU. Both models coexist in 8GB VRAM."""
        if self._llm is None:
            model_path = self._find_model()
            if not model_path:
                logger.warning("No GGUF model found — LLM extraction disabled")
                return None

            from ctransformers import AutoModelForCausalLM
            gpu_layers = 50 if self._gpu_available else 0
            self._llm = AutoModelForCausalLM.from_pretrained(
                str(model_path),
                model_type="mistral",
                gpu_layers=gpu_layers,
                max_new_tokens=512,
                context_length=2048,
            )
            logger.info(f"Loaded LLM from {model_path.name} (GPU layers: {gpu_layers})")
        return self._llm

    def _find_model(self) -> Path | None:
        """Find the first .gguf model file in models/."""
        if MODELS_DIR.exists():
            for f in MODELS_DIR.glob("*.gguf"):
                return f
        return None

    def cleanup(self):
        """Release all GPU resources."""
        del self._llm
        del self._embedder
        self._llm = None
        self._embedder = None
        try:
            import torch
            torch.cuda.empty_cache()
        except Exception:
            pass


# ── Topic Discovery ──────────────────────────────────────────────────────────


def discover_topics(limit: int = 500) -> list[str]:
    """Build a prioritized topic list from multiple sources."""
    topics = []
    seen = set()

    def add(topic: str):
        t = topic.strip().lower()
        if t and t not in seen:
            seen.add(t)
            topics.append(topic.strip())

    # Priority 1: Conversation feedback (high priority)
    feedback_topics = _load_feedback_topics()
    for t in feedback_topics:
        add(t)

    # Priority 2: Knowledge graph gaps (medium priority)
    gap_topics = _load_gap_topics()
    for t in gap_topics:
        add(t)

    # Priority 3: Curated curriculum topics
    curriculum_topics = _load_curriculum_topics()
    for t in curriculum_topics:
        add(t)

    # Priority 4: Domain expansion topics
    for domain, domain_topics in DOMAIN_EXPANSION.items():
        for t in domain_topics:
            add(t)

    logger.info(f"Discovered {len(topics)} topics to learn")
    return topics[:limit]


def _load_feedback_topics() -> list[str]:
    """Topics from conversation that had negative feedback."""
    topics = []
    if FEEDBACK_PATH.exists():
        with open(FEEDBACK_PATH, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("rating", 0) < 0:
                        topics.append(entry["query"])
                except (json.JSONDecodeError, KeyError):
                    pass
    return topics


def _load_gap_topics() -> list[str]:
    """Topics from gap tracker."""
    topics = []
    if GAPS_PATH.exists():
        with open(GAPS_PATH, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    topics.append(entry.get("query", ""))
                except (json.JSONDecodeError, KeyError):
                    pass
    return topics


def _load_curriculum_topics() -> list[str]:
    """Topics from curriculum text files."""
    topics = []
    curriculum_dir = ROOT / "curriculum"
    if curriculum_dir.exists():
        for txt_file in curriculum_dir.glob("*.txt"):
            with open(txt_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        topics.append(line)
    return topics


def _load_kg_weak_topics() -> list[str]:
    """Topics from KG with low effective confidence."""
    topics = []
    try:
        sys.path.insert(0, str(ROOT / "backend"))
        from memory.knowledge_graph import knowledge_graph
        for node in knowledge_graph._nodes.values():
            if node.effective_confidence < 0.5:
                topics.append(node.concept)
    except Exception:
        pass
    return topics


# ── Core Learning ─────────────────────────────────────────────────────────────


async def learn_single_topic(topic: str, vram: VRAMManager) -> TopicResult:
    """Learn a single topic: retrieve → reason → integrate."""
    t0 = time.time()

    try:
        # Import backend modules
        from pipeline.retrieval_mesh import retrieve_all
        from pipeline.truth_filter import score_sources
        from memory.knowledge_graph import knowledge_graph
        from pipeline.reasoning_core import reason as internal_reason

        # 1. Retrieve from web
        sources = await retrieve_all(topic)
        if not sources:
            return TopicResult(
                topic=topic, domain="general", success=False,
                error="No sources found", duration_s=time.time() - t0,
            )

        # 2. Score and filter sources
        result = score_sources(sources, query=topic)
        filtered = result.get("sources", []) if isinstance(result, dict) else result
        if not filtered:
            filtered = sources[:5]

        # 3. Generate answer using internal reasoning
        answer_result = internal_reason(
            query=topic,
            sources=filtered[:5],
            constitution="",
        )
        answer = answer_result.get("draft", "") if isinstance(answer_result, dict) else str(answer_result)
        confidence = answer_result.get("confidence", "PROBABLE") if isinstance(answer_result, dict) else "PROBABLE"

        if not answer or len(answer) < 20:
            # Fallback: use top snippet
            answer = filtered[0].get("snippet", "No information found.")
            confidence = "LOW"

        # 4. Detect domain
        domain = knowledge_graph._detect_domain(topic, answer) if hasattr(knowledge_graph, '_detect_domain') else "general"

        # 5. Integrate into knowledge graph
        knowledge_graph.integrate(
            query=topic,
            sources=filtered[:5],
            answer=answer,
            confidence=confidence,
            domain=domain,
            tags=["gpu_deep_learn"],
        )

        # 6. GPU: Generate embedding (if available)
        try:
            embedder = vram.get_embedder()
            embedding = embedder.encode(topic + " " + answer[:200])
            # Store in ChromaDB
            try:
                from memory.vector_backend import create_backend
                vb = create_backend()
                vb.upsert(
                    key=topic.lower().replace(" ", "_"),
                    embedding=embedding.tolist(),
                    metadata={"source": "deep_learn", "domain": domain, "confidence": confidence},
                )
            except Exception:
                pass  # Non-critical
        except Exception as e:
            logger.debug(f"Embedding failed (non-critical): {e}")

        # 7. GPU: Extract enhanced facts using local LLM (if available)
        try:
            llm = vram.get_llm()
            if llm:
                enhanced = _extract_facts_with_llm(llm, topic, filtered[:3])
                if enhanced and len(enhanced) > len(answer):
                    # Update KG with enhanced answer
                    knowledge_graph.integrate(
                        query=topic,
                        sources=filtered[:5],
                        answer=enhanced,
                        confidence=confidence,
                        domain=domain,
                        tags=["gpu_deep_learn", "llm_enhanced"],
                    )
                    answer = enhanced
            # Expand topics using LLM
            try:
                existing = set(t.lower() for t in checkpoint.topics_completed + checkpoint.topics_remaining)
                new_topics = _expand_topics_with_llm(vram.get_llm(), topic, existing)
                if new_topics:
                    checkpoint.topics_remaining.extend(new_topics)
                    logger.debug(f"Expanded: +{len(new_topics)} subtopics from '{topic[:40]}'")
            except Exception:
                pass

        except Exception as e:
            logger.debug(f"LLM extraction failed (non-critical): {e}")

        return TopicResult(
            topic=topic,
            domain=domain,
            success=True,
            sources_count=len(filtered),
            kg_confidence=confidence,
            duration_s=time.time() - t0,
        )

    except Exception as e:
        return TopicResult(
            topic=topic, domain="general", success=False,
            error=str(e)[:200], duration_s=time.time() - t0,
        )


def _extract_facts_with_llm(llm, topic: str, sources: list[dict]) -> str:
    """Use local LLM to synthesize a better answer from sources."""
    context = "\n\n".join(
        f"Source {i+1}: {s.get('snippet', '')[:300]}"
        for i, s in enumerate(sources)
        if s.get('snippet')
    )

    if not context:
        return ""

    prompt = f"""Based on these sources, write a clear, comprehensive answer about "{topic}".
Be accurate. Only use information from the sources. Be concise but thorough.

Sources:
{context}

Answer:"""

    try:
        response = llm(prompt, max_new_tokens=300, temperature=0.3)
        return response.strip()
    except Exception:
        return ""


def _expand_topics_with_llm(llm, topic: str, existing: set[str]) -> list[str]:
    """Use LLM to discover related subtopics for further exploration."""
    prompt = f"""Given the topic "{topic}", list 5 related subtopics that would deepen understanding.
Each subtopic should be a specific question or concept. One per line, no numbering.

Related subtopics:"""

    try:
        response = llm(prompt, max_new_tokens=150, temperature=0.5)
        new_topics = []
        for line in response.strip().split("\n"):
            t = line.strip().lstrip("0123456789.-) ")
            if t and len(t) > 10 and t.lower() not in existing:
                new_topics.append(t)
                existing.add(t.lower())
        return new_topics[:5]
    except Exception:
        return []


# ── Main Loop ────────────────────────────────────────────────────────────────


def print_progress(checkpoint: Checkpoint, elapsed: float, total_hours: float):
    """Print progress report."""
    completed = len(checkpoint.topics_completed)
    failed = len(checkpoint.topics_failed)
    remaining = len(checkpoint.topics_remaining)
    total = completed + failed + remaining

    pct = (completed / total * 100) if total > 0 else 0
    rate = completed / (elapsed / 3600) if elapsed > 0 else 0
    eta_hours = remaining / rate / 3600 if rate > 0 else 0

    # Domain breakdown
    domains = {}
    for topic in checkpoint.topics_completed:
        # Simple domain detection from topic keywords
        d = _quick_domain(topic)
        domains[d] = domains.get(d, 0) + 1

    print(f"\n{'='*60}")
    print(f"  PROGRESS: {completed}/{total} topics ({pct:.1f}%)")
    print(f"  Completed: {completed} | Failed: {failed} | Remaining: {remaining}")
    print(f"  Rate: {rate:.1f} topics/hour | ETA: {eta_hours:.1f} hours")
    print(f"  Elapsed: {elapsed/3600:.2f}h / {total_hours:.1f}h")
    print(f"{'='*60}")
    if domains:
        print("  Domains:", ", ".join(f"{d}: {c}" for d, c in sorted(domains.items())))
    print()


def _quick_domain(topic: str) -> str:
    t = topic.lower()
    if any(w in t for w in ["physics", "quantum", "gravity", "relativity", "particle"]):
        return "physics"
    if any(w in t for w in ["math", "theorem", "equation", "number", "algebra"]):
        return "math"
    if any(w in t for w in ["bio", "gene", "cell", "dna", "evolution", "organism"]):
        return "biology"
    if any(w in t for w in ["chem", "molecule", "reaction", "element", "compound"]):
        return "chemistry"
    if any(w in t for w in ["computer", "algorithm", "software", "programming", "ai", "machine learning"]):
        return "cs"
    if any(w in t for w in ["history", "war", "revolution", "ancient", "civilization"]):
        return "history"
    if any(w in t for w in ["star", "galaxy", "planet", "universe", "cosmos", "astronomy"]):
        return "astronomy"
    return "general"


async def run_deep_learning(hours: float = 10.0, batch_size: int = 8, resume: bool = False):
    """Main deep learning loop."""
    vram = VRAMManager()

    # Load or create checkpoint
    if resume:
        checkpoint = Checkpoint.load()
        if checkpoint:
            logger.info(f"Resuming from checkpoint: {len(checkpoint.topics_completed)} completed, {len(checkpoint.topics_remaining)} remaining")
        else:
            logger.info("No checkpoint found — starting fresh")
            checkpoint = Checkpoint()
    else:
        checkpoint = Checkpoint()

    if not checkpoint.topics_remaining:
        checkpoint.topics_remaining = discover_topics()
        checkpoint.started_at = time.strftime("%Y-%m-%d %H:%M:%S")

    checkpoint.save()

    end_time = time.time() + hours * 3600
    session_start = time.time()
    batch_num = 0

    logger.info(f"Starting {hours}h deep learning session with {len(checkpoint.topics_remaining)} topics")
    logger.info(f"Batch size: {batch_size} | GPU: {vram._device}")

    while time.time() < end_time and checkpoint.topics_remaining:
        batch_num += 1
        batch = checkpoint.topics_remaining[:batch_size]
        checkpoint.topics_remaining = checkpoint.topics_remaining[batch_size:]

        logger.info(f"Batch {batch_num}: learning {len(batch)} topics...")

        for i, topic in enumerate(batch):
            if time.time() >= end_time:
                logger.info("Time limit reached")
                break

            result = await learn_single_topic(topic, vram)

            if result.success:
                checkpoint.topics_completed.append(topic)
                logger.info(f"  [{i+1}/{len(batch)}] ✓ {topic} ({result.domain}, {result.kg_confidence}, {result.duration_s:.1f}s)")
            else:
                checkpoint.topics_failed.append({"topic": topic, "error": result.error})
                logger.warning(f"  [{i+1}/{len(batch)}] ✗ {topic}: {result.error[:60]}")

            # Small delay between topics to avoid rate limiting
            await asyncio.sleep(1.0)

        # Save checkpoint after each batch
        checkpoint.total_duration_s = time.time() - session_start
        checkpoint.save()

        # Progress report every batch
        elapsed = time.time() - session_start
        print_progress(checkpoint, elapsed, hours)

        # Discover new topics if running low
        if len(checkpoint.topics_remaining) < batch_size * 2:
            new_topics = _load_kg_weak_topics()
            for t in new_topics:
                if t not in checkpoint.topics_completed and t not in checkpoint.topics_remaining:
                    checkpoint.topics_remaining.append(t)
            if new_topics:
                logger.info(f"Discovered {len(new_topics)} new topics from KG gaps")
                checkpoint.save()

    # Final report
    total_time = time.time() - session_start
    checkpoint.total_duration_s = total_time
    checkpoint.save()

    print(f"\n{'='*60}")
    print(f"  DEEP LEARNING SESSION COMPLETE")
    print(f"{'='*60}")
    print(f"  Duration: {total_time/3600:.2f} hours")
    print(f"  Topics completed: {len(checkpoint.topics_completed)}")
    print(f"  Topics failed: {len(checkpoint.topics_failed)}")
    print(f"  Rate: {len(checkpoint.topics_completed)/(total_time/3600):.1f} topics/hour")
    print(f"  Checkpoint saved: {CHECKPOINT_PATH}")
    print(f"{'='*60}")

    vram.cleanup()


def show_status():
    """Show current checkpoint status."""
    checkpoint = Checkpoint.load()
    if not checkpoint:
        print("No checkpoint found. Run without --resume to start.")
        return

    print(f"\n{'='*60}")
    print(f"  DEEP LEARNING STATUS")
    print(f"{'='*60}")
    print(f"  Started: {checkpoint.started_at}")
    print(f"  Completed: {len(checkpoint.topics_completed)}")
    print(f"  Failed: {len(checkpoint.topics_failed)}")
    print(f"  Remaining: {len(checkpoint.topics_remaining)}")
    print(f"  Total time: {checkpoint.total_duration_s/3600:.2f} hours")

    if checkpoint.topics_completed:
        domains = {}
        for t in checkpoint.topics_completed:
            d = _quick_domain(t)
            domains[d] = domains.get(d, 0) + 1
        print(f"  Domains: {', '.join(f'{d}: {c}' for d, c in sorted(domains.items()))}")

    if checkpoint.topics_failed:
        print(f"\n  Last 5 failures:")
        for entry in checkpoint.topics_failed[-5:]:
            print(f"    - {entry['topic']}: {entry.get('error', 'unknown')[:60]}")

    if checkpoint.topics_remaining:
        print(f"\n  Next 5 topics:")
        for t in checkpoint.topics_remaining[:5]:
            print(f"    - {t}")

    print(f"{'='*60}")


# ── Brain Mode ───────────────────────────────────────────────────────────────


async def run_brain_mode(hours: float = 10.0, batch_size: int = 5):
    """Brain mode: solve coding and math problems with GPU LLM."""
    import sys
    sys.path.insert(0, "backend")

    from brain.problem_solver import ProblemSolver, Problem
    from brain.problem_sources import load_problems, get_all_topics
    from brain.code_executor import CodeExecutor
    from brain.math_engine import MathEngine

    # Load GPU models
    vram = VRAMManager()
    llm = vram.get_llm()
    if not llm:
        logger.error("No LLM loaded — cannot run brain mode")
        return

    solver = ProblemSolver(llm=llm, max_retries=3)
    executor = CodeExecutor()
    math = MathEngine()

    # Load all problems
    all_problems = load_problems()
    logger.info(f"Loaded {len(all_problems)} problems across {len(get_all_topics()['coding'])} coding + {len(get_all_topics()['math'])} math topics")

    # Convert to Problem objects
    problems = []
    for p in all_problems:
        problems.append(Problem(
            id=p["id"],
            type=p["type"],
            topic=p["topic"],
            difficulty=p.get("difficulty", 5),
            title=p["title"],
            description=p["description"],
            template=p.get("template", ""),
            test_cases=p.get("test_cases", []),
            solution=p.get("solution", ""),
            techniques=p.get("techniques", []),
        ))

    # Sort by difficulty
    problems.sort(key=lambda p: p.difficulty)

    t_start = time.time()
    t_end = t_start + hours * 3600
    solved = 0
    failed = 0
    techniques_seen = {}

    for i, problem in enumerate(problems):
        if time.time() >= t_end:
            break

        logger.info(f"[{i+1}/{len(problems)}] {problem.title} ({problem.type}, difficulty={problem.difficulty})")

        result = solver.solve_problem(problem)

        if result.solved:
            solved += 1
            technique = result.technique_used
            techniques_seen[technique] = techniques_seen.get(technique, 0) + 1
            logger.info(f"  ✓ Solved in {result.attempts} attempt(s), technique={technique}, {result.duration_ms:.0f}ms")
        else:
            failed += 1
            logger.info(f"  ✗ Failed after {result.attempts} attempts: {result.failures[-1][:80] if result.failures else 'unknown'}")

        # Progress every 10 problems
        if (i + 1) % 10 == 0:
            elapsed = time.time() - t_start
            rate = solved / (elapsed / 3600) if elapsed > 0 else 0
            print(f"\n  PROGRESS: {i+1}/{len(problems)} problems")
            print(f"  Solved: {solved} | Failed: {failed} | Rate: {rate:.0f}/hour")
            print(f"  Techniques: {techniques_seen}")
            print(f"  Elapsed: {elapsed/3600:.2f}h / {hours}h\n")

    # Final report
    total_time = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"  BRAIN MODE COMPLETE")
    print(f"{'='*60}")
    print(f"  Duration: {total_time/3600:.2f} hours")
    print(f"  Problems: {solved} solved, {failed} failed, {len(problems)} total")
    print(f"  Solve rate: {solved/(total_time/3600):.0f}/hour" if total_time > 0 else "")
    print(f"  Techniques learned: {techniques_seen}")
    print(f"{'='*60}")


# ── CLI ───────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="VELYNX GPU Deep Learning Engine")
    parser.add_argument("--hours", type=float, default=10.0, help="Hours to run (default: 10)")
    parser.add_argument("--batch-size", type=int, default=8, help="Topics per batch (default: 8)")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--status", action="store_true", help="Show checkpoint status")
    parser.add_argument("--brain", action="store_true", help="Brain mode: solve coding & math problems")
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.brain:
        asyncio.run(run_brain_mode(
            hours=args.hours,
            batch_size=args.batch_size,
        ))
    else:
        asyncio.run(run_deep_learning(
            hours=args.hours,
            batch_size=args.batch_size,
            resume=args.resume,
        ))


if __name__ == "__main__":
    main()

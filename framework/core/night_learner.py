"""
VELYNX Night Learner — Phase 15
==================================
Scheduled learning sessions:
- Night (11PM–6AM): GPU-accelerated intensive learning
- Day: Light CPU background learning
- Weekend: Full autonomous learning sessions

Run this as a standalone script:
    python night_learner.py                    # Runs scheduled sessions
    python night_learner.py --now              # Force a learning session now
    python night_learner.py --topics topics.txt # Learn from a topic list
    python night_learner.py --status           # Show learning stats
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(SCRIPT_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("velynx.night_learner")


# ── ANSI Colors ───────────────────────────────────────────────────────────────
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    GRAY = "\033[90m"
    WHITE = "\033[97m"


# ── Default topic seeds ───────────────────────────────────────────────────────
DEFAULT_TOPICS = [
    # Physics
    "speed of light in vacuum",
    "quantum entanglement",
    "special theory of relativity",
    "laws of thermodynamics",
    "Heisenberg uncertainty principle",
    "standard model of particle physics",
    "electromagnetic spectrum",
    "photoelectric effect",
    # Mathematics
    "Pythagorean theorem",
    "Euler's identity",
    "Fourier transform",
    "Laplace transform",
    "prime number theorem",
    "Bayes theorem",
    "gradient descent optimization",
    # Computer Science
    "binary search algorithm",
    "neural network backpropagation",
    "transformer architecture machine learning",
    "big O notation complexity",
    "hash table data structure",
    # Astronomy
    "black hole event horizon",
    "cosmic microwave background radiation",
    "dark matter evidence",
    "gravitational waves LIGO",
    "Hubble constant expansion universe",
    # Biology
    "DNA double helix structure",
    "CRISPR gene editing",
    "protein folding problem",
    "natural selection evolution",
    # Chemistry
    "periodic table organization",
    "chemical bonding types",
    "entropy thermodynamics",
]


def get_mode() -> str:
    """Determine learning mode based on current time."""
    hour = datetime.now().hour
    weekday = datetime.now().weekday()  # 0=Monday, 6=Sunday

    if weekday >= 5:  # Weekend
        return "weekend"
    if 23 <= hour or hour < 6:  # Night (11PM - 6AM)
        return "night"
    if 6 <= hour < 9 or 18 <= hour < 23:  # Morning/Evening
        return "background"
    return "light"  # Daytime — minimal


def get_mode_config(mode: str) -> dict:
    """Get configuration for each learning mode."""
    return {
        "night": {
            "use_gpu": True,
            "batch_size": 32,
            "max_topics": 50,
            "delay_between": 2.0,
            "description": "Intensive GPU learning session",
            "embed": True,
        },
        "weekend": {
            "use_gpu": True,
            "batch_size": 64,
            "max_topics": 200,
            "delay_between": 1.0,
            "description": "Full autonomous weekend session",
            "embed": True,
        },
        "background": {
            "use_gpu": False,
            "batch_size": 4,
            "max_topics": 10,
            "delay_between": 10.0,
            "description": "Background CPU learning",
            "embed": False,
        },
        "light": {
            "use_gpu": False,
            "batch_size": 1,
            "max_topics": 3,
            "delay_between": 30.0,
            "description": "Light daytime learning",
            "embed": False,
        },
    }.get(
        mode,
        {
            "use_gpu": False,
            "batch_size": 4,
            "max_topics": 10,
            "delay_between": 10.0,
            "description": "Default mode",
            "embed": False,
        },
    )


def check_gpu() -> dict:
    """Check GPU availability and VRAM."""
    result = {"available": False, "name": "CPU only", "vram_gb": 0, "device": "cpu"}
    try:
        import torch

        if torch.cuda.is_available():
            result["available"] = True
            result["name"] = torch.cuda.get_device_name(0)
            result["vram_gb"] = torch.cuda.get_device_properties(0).total_memory / 1e9
            result["device"] = "cuda"
    except (ImportError, OSError):
        pass
    return result


async def learn_topic(
    topic: str,
    config: dict,
    stats: dict,
) -> bool:
    """Learn a single topic. Returns True if successful."""
    try:
        # Import retrieval
        try:
            from retrieval.unified_retriever import unified_retriever

            report = await unified_retriever.retrieve(topic)
            sources = report.source_dicts
        except ImportError:
            # Fallback to direct Wikipedia
            import urllib.request, urllib.parse, json as _json

            q = urllib.parse.quote(topic.replace(" ", "_"))
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{q}"
            req = urllib.request.Request(
                url, headers={"User-Agent": "VELYNX/1.0 (autonomous-learner)"}
            )
            with urllib.request.urlopen(req, timeout=8) as r:
                data = _json.loads(r.read())
            sources = [
                {
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    "title": data.get("title", topic),
                    "snippet": data.get("extract", "")[:800],
                    "source": "wikipedia",
                    "score": 0.85,
                }
            ]

        # Retry once on empty results (transient network failures)
        if not sources:
            await asyncio.sleep(2)
            try:
                from retrieval.unified_retriever import unified_retriever as _ur

                report = await _ur.retrieve(topic)
                sources = report.source_dicts
            except Exception:
                pass

        if not sources:
            stats["failed"] += 1
            return False

        # Simple internal reasoning
        query_words = set(topic.lower().split()) - {"what", "is", "the", "a", "an", "how"}
        all_text = [s.get("snippet", "") for s in sources if s.get("snippet")]
        answer = ". ".join(all_text[:2])[:600] if all_text else ""

        if not answer:
            stats["failed"] += 1
            return False

        # GPU embedding if available and configured
        if config.get("embed") and config.get("use_gpu"):
            try:
                from sentence_transformers import SentenceTransformer
                import torch

                device = "cuda" if torch.cuda.is_available() else "cpu"
                embedder = SentenceTransformer("all-MiniLM-L6-v2", device=device)
                embedding = embedder.encode(topic + " " + answer[:200])
                # Store in ChromaDB
                try:
                    from memory.vector_backend import create_backend

                    vb = create_backend()
                    topic_key = topic.lower().replace(" ", "_")[:64]
                    vb.upsert(
                        key=topic_key,
                        embedding=embedding.tolist(),
                        # FIXME: `domain` is undefined in learn_topic()'s scope. Currently
                        # unreachable — the `memory.vector_backend` import above resolves to
                        # nothing, so this block always raises ImportError first. Recorded in
                        # CRITICAL_PATH.md Priority 2; fix with the W-056 boundary repair.
                        metadata={"source": "night_learn", "domain": domain},  # noqa: F821
                    )
                    logger.info("GPU embedding stored: %r on %s", topic[:40], device)
                except Exception as e:
                    logger.debug("Embedding storage failed: %s", e)
                # Free GPU memory
                del embedder
                if device == "cuda":
                    torch.cuda.empty_cache()
            except (ImportError, OSError) as e:
                logger.debug("GPU embedding failed: %s", e)

        # Integrate into knowledge graph
        try:
            from memory.knowledge_graph import knowledge_graph

            knowledge_graph.integrate(
                query=topic,
                sources=sources,
                answer=answer,
                confidence="PROBABLE",
                tags=["autonomous", "batch_learning"],
            )
        except ImportError:
            pass

        # Record in continuous learner
        try:
            from learning.continuous_learner import continuous_learner

            await continuous_learner.learn_from_query(
                query=topic,
                sources=sources,
                answer=answer,
                confidence="PROBABLE",
                tags=["batch", "autonomous"],
            )
        except ImportError:
            pass

        stats["learned"] += 1
        return True

    except Exception as e:
        stats["failed"] += 1
        logger.debug("Failed to learn %r: %s", topic, e)
        return False


async def run_learning_session(
    topics: list[str],
    mode: str = "auto",
    force: bool = False,
) -> dict:
    """Run a full learning session."""
    if mode == "auto":
        mode = get_mode()

    config = get_mode_config(mode)
    gpu_info = check_gpu()

    print(f"\n{C.CYAN}{C.BOLD}VELYNX Autonomous Learning Session{C.RESET}")
    print(f"  {C.GRAY}Mode:    {C.WHITE}{mode} — {config['description']}{C.RESET}")
    print(
        f"  {C.GRAY}GPU:     {C.WHITE}{gpu_info['name']}"
        f"{'  ' + str(round(gpu_info['vram_gb'], 1)) + 'GB VRAM' if gpu_info['available'] else ''}{C.RESET}"
    )
    print(
        f"  {C.GRAY}Topics:  {C.WHITE}{min(len(topics), config['max_topics'])} / {len(topics)} queued{C.RESET}"
    )
    print(f"  {C.GRAY}Time:    {C.WHITE}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{C.RESET}")

    if mode == "light" and not force:
        print(f"\n  {C.YELLOW}⚠ Light mode — minimal learning to preserve PC performance{C.RESET}")
        print(
            f"  {C.GRAY}Use --now to force a full session, or run at night for intensive learning{C.RESET}\n"
        )

    selected = topics[: config["max_topics"]]
    stats = {"learned": 0, "failed": 0, "skipped": 0, "start_time": time.time()}

    print(f"\n  {C.GREEN}Starting...{C.RESET}\n")

    for i, topic in enumerate(selected, 1):
        # Progress bar
        pct = i / len(selected)
        bar_len = 30
        filled = int(bar_len * pct)
        bar = "█" * filled + "░" * (bar_len - filled)
        elapsed = time.time() - stats["start_time"]
        eta = (elapsed / i) * (len(selected) - i) if i > 0 else 0

        print(
            f"\r  [{bar}] {i}/{len(selected)}  "
            f"{C.GREEN}✓{stats['learned']}{C.RESET} "
            f"{C.RED}✗{stats['failed']}{C.RESET}  "
            f"ETA: {int(eta)}s  {C.GRAY}{topic[:35]}...{C.RESET}",
            end="",
            flush=True,
        )

        success = await learn_topic(topic, config, stats)
        await asyncio.sleep(config["delay_between"])

    elapsed = time.time() - stats["start_time"]
    print(f"\n\n  {C.BOLD}Session Complete{C.RESET}")
    print(f"  {C.GREEN}Learned:  {stats['learned']} concepts{C.RESET}")
    print(f"  {C.RED}Failed:   {stats['failed']} topics{C.RESET}")
    print(f"  {C.GRAY}Elapsed:  {elapsed:.1f}s  ({elapsed/60:.1f} min){C.RESET}")

    # Print knowledge graph stats
    try:
        from memory.knowledge_graph import knowledge_graph

        kstats = knowledge_graph.stats()
        print(
            f"  {C.CYAN}Graph:    {kstats['total_nodes']} total concepts "
            f"({kstats['avg_confidence']:.0%} avg confidence){C.RESET}"
        )
    except Exception:
        pass

    print()
    return stats


async def show_status():
    """Show current learning status."""
    print(f"\n{C.CYAN}{C.BOLD}VELYNX Learning Status{C.RESET}\n")

    try:
        from learning.continuous_learner import continuous_learner

        report = continuous_learner.get_learning_report()
        sess = report["session"]
        print(f"  {C.BOLD}Session:{C.RESET}")
        print(f"  {C.GRAY}• Queries processed:    {sess['total_queries']}{C.RESET}")
        print(f"  {C.GRAY}• New concepts learned: {sess['new_concepts_learned']}{C.RESET}")
        print(f"  {C.GRAY}• Concepts deepened:    {sess['concepts_updated']}{C.RESET}")
        print(f"  {C.GRAY}• Learning rate:        {sess['learning_rate_per_hour']}/hour{C.RESET}")
        print(f"  {C.GRAY}• Avg confidence:       {report['avg_confidence']:.0%}{C.RESET}")
        print(f"  {C.GRAY}• Gaps in queue:        {report['gaps_queue_size']}{C.RESET}")

        if report.get("next_to_learn"):
            print(f"\n  {C.BOLD}Next to learn:{C.RESET}")
            for item in report["next_to_learn"]:
                print(f"  {C.GRAY}  · {item[:70]}{C.RESET}")
    except Exception as e:
        print(f"  {C.GRAY}No learning data yet: {e}{C.RESET}")

    try:
        from memory.knowledge_graph import knowledge_graph

        kstats = knowledge_graph.stats()
        print(f"\n  {C.BOLD}Knowledge Graph:{C.RESET}")
        print(f"  {C.GRAY}• Total concepts:  {kstats['total_nodes']}{C.RESET}")
        print(f"  {C.GRAY}• Avg confidence:  {kstats.get('avg_confidence', 0):.0%}{C.RESET}")
        if kstats.get("domains"):
            print(
                f"  {C.GRAY}• Domains: {', '.join(f'{k}({v})' for k,v in kstats['domains'].items())}{C.RESET}"
            )
    except Exception:
        pass

    mode = get_mode()
    cfg = get_mode_config(mode)
    print(f"\n  {C.BOLD}Current Mode:{C.RESET} {C.CYAN}{mode}{C.RESET} — {cfg['description']}")
    print(f"  {C.GRAY}GPU:  {C.WHITE}{check_gpu()['name']}{C.RESET}")
    print()


async def main():
    parser = argparse.ArgumentParser(
        description="VELYNX Autonomous Learning System",
    )
    parser.add_argument("--now", action="store_true", help="Force learning session now")
    parser.add_argument("--night", action="store_true", help="Run as night session (GPU)")
    parser.add_argument("--status", action="store_true", help="Show learning status")
    parser.add_argument("--topics", type=str, help="Path to topics file (one per line)")
    parser.add_argument(
        "--mode",
        type=str,
        default="auto",
        choices=["auto", "night", "weekend", "background", "light"],
        help="Learning mode",
    )
    args = parser.parse_args()

    # Load .env
    try:
        from dotenv import load_dotenv

        load_dotenv(os.path.join(SCRIPT_DIR, ".env"))
    except Exception:
        pass

    if args.status:
        await show_status()
        return

    # Load topics
    topics = list(DEFAULT_TOPICS)
    if args.topics:
        try:
            with open(args.topics) as f:
                custom = [line.strip() for line in f if line.strip()]
            topics = custom + topics
            print(f"Loaded {len(custom)} custom topics from {args.topics}")
        except Exception as e:
            print(f"Could not load topics file: {e}")

    # Add gap queue topics
    try:
        from learning.continuous_learner import continuous_learner

        gap = continuous_learner.get_next_to_learn()
        if gap:
            topics = [gap] + topics
    except Exception:
        pass

    mode = "night" if args.night else args.mode
    await run_learning_session(topics, mode=mode, force=args.now)


if __name__ == "__main__":
    asyncio.run(main())

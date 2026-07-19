"""
VELYNX Deep Learning Curriculum Runner
=======================================
Feeds 200 curated topics through the learning pipeline.

Usage:
    python curriculum/deep_learn.py                    # all domains
    python curriculum/deep_learn.py --domain physics   # one domain
    python curriculum/deep_learn.py --rounds 3         # repeat 3 times
    python curriculum/deep_learn.py --shuffle          # randomize order
"""

from __future__ import annotations

import argparse
import asyncio
import os
import random
import sys
import time

# ── Add backend to path ──────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
BACKEND_DIR = os.path.join(PROJECT_DIR, "backend")
sys.path.insert(0, PROJECT_DIR)
sys.path.insert(0, BACKEND_DIR)
os.chdir(PROJECT_DIR)

# ── ANSI Colors ──────────────────────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    GRAY    = "\033[90m"
    WHITE   = "\033[97m"
    MAGENTA = "\033[95m"


def load_topics(domain: str | None = None) -> dict[str, list[str]]:
    """Load topics from curriculum/*.txt files. Returns {domain: [topics]}."""
    domains = {}
    for fname in sorted(os.listdir(SCRIPT_DIR)):
        if not fname.endswith(".txt"):
            continue
        domain_name = fname.replace(".txt", "")
        if domain and domain_name != domain:
            continue
        with open(os.path.join(SCRIPT_DIR, fname)) as f:
            topics = [line.strip() for line in f if line.strip()]
        if topics:
            domains[domain_name] = topics
    return domains


def interleave_domains(domains: dict[str, list[str]]) -> list[str]:
    """Interleave topics from different domains for cross-domain connections."""
    # Round-robin: physics[0], biology[0], chemistry[0], ..., physics[1], ...
    all_topics = []
    max_len = max(len(v) for v in domains.values())
    domain_names = list(domains.keys())
    for i in range(max_len):
        for name in domain_names:
            if i < len(domains[name]):
                all_topics.append(domains[name][i])
    return all_topics


def progress_bar(current: int, total: int, width: int = 30) -> str:
    filled = int(width * current / total) if total > 0 else 0
    return f"[{'█' * filled}{'░' * (width - filled)}]"


async def run_deep_learning(
    domains: dict[str, list[str]],
    rounds: int = 1,
    shuffle: bool = False,
    delay: float = 2.0,
):
    """Run the deep learning curriculum."""
    from framework.core.night_learner import learn_topic, get_mode_config, check_gpu
    from memory.knowledge_graph import knowledge_graph

    config = get_mode_config("night")
    gpu = check_gpu()

    # Build topic list with domain labels
    all_topics = []
    domain_labels = []
    for round_num in range(rounds):
        if shuffle:
            shuffled = {k: list(v) for k, v in domains.items()}
            for v in shuffled.values():
                random.shuffle(v)
            source = shuffled
        else:
            source = domains
        round_topics = interleave_domains(source)
        all_topics.extend(round_topics)
        # Build labels matching interleaved order
        max_len = max(len(v) for v in source.values())
        for i in range(max_len):
            for name in source:
                if i < len(source[name]):
                    domain_labels.append(name)

    total = len(all_topics)

    # Header
    print(f"\n{C.CYAN}{C.BOLD}VELYNX Deep Learning Curriculum{C.RESET}")
    print(f"  {C.GRAY}Domains:{C.RESET} {', '.join(domains.keys())}")
    print(f"  {C.GRAY}Topics:{C.RESET}  {total}")
    print(f"  {C.GRAY}Rounds:{C.RESET}  {rounds}")
    print(f"  {C.GRAY}GPU:{C.RESET}     {gpu['name']}")
    print(f"  {C.GRAY}Delay:{C.RESET}   {delay}s between topics")
    print()

    # Per-domain tracking
    domain_stats: dict[str, dict] = {}
    for name in domains:
        domain_stats[name] = {"learned": 0, "failed": 0, "total": len(domains[name]) * rounds}

    stats = {"learned": 0, "failed": 0, "gaps": []}
    t_start = time.time()

    async def process_topic(i: int, topic: str) -> bool:
        domain_name = domain_labels[i] if i < len(domain_labels) else "?"
        result = await learn_topic(topic, config, stats)
        if domain_name in domain_stats:
            if result:
                domain_stats[domain_name]["learned"] += 1
            else:
                domain_stats[domain_name]["failed"] += 1
        return result

    # Main learning loop
    failed_topics: list[tuple[int, str]] = []
    for i, topic in enumerate(all_topics):
        elapsed = time.time() - t_start
        eta = (elapsed / (i + 1)) * (total - i - 1) if i > 0 else 0
        bar = progress_bar(i + 1, total)

        sys.stdout.write(
            f"\r  {bar} {i+1}/{total}  "
            f"{C.GREEN}✓{stats['learned']}{C.RESET} "
            f"{C.RED}✗{stats['failed']}{C.RESET}  "
            f"ETA: {eta:.0f}s  "
            f"{C.GRAY}{topic[:35]}...{C.RESET}  "
        )
        sys.stdout.flush()

        result = await process_topic(i, topic)
        if not result:
            failed_topics.append((i, topic))

        if delay > 0:
            await asyncio.sleep(delay)

    # Retry failed topics (up to 2 rounds with longer delays)
    for retry_round in range(2):
        if not failed_topics:
            break
        retry_delay = delay * 2
        print(f"\n  {C.YELLOW}Retry round {retry_round + 1}: {len(failed_topics)} topics, {retry_delay}s delay{C.RESET}")
        still_failed = []
        for i, topic in failed_topics:
            domain_name = domain_labels[i] if i < len(domain_labels) else "?"
            # Use isolated stats so retries don't double-count
            retry_stats = {"learned": 0, "failed": 0, "gaps": []}
            result = await learn_topic(topic, config, retry_stats)
            if result:
                stats["learned"] += 1
                stats["failed"] -= 1
                if domain_name in domain_stats:
                    domain_stats[domain_name]["failed"] -= 1
                    domain_stats[domain_name]["learned"] += 1
            else:
                still_failed.append((i, topic))
            await asyncio.sleep(retry_delay)
        failed_topics = still_failed

    elapsed = time.time() - t_start
    gstats = knowledge_graph.stats()

    # Final report
    print(f"\n\n{C.CYAN}{C.BOLD}Deep Learning Complete{C.RESET}")
    print(f"  {C.GRAY}Learned:{C.RESET}  {C.GREEN}{stats['learned']}{C.RESET} concepts")
    print(f"  {C.GRAY}Failed:{C.RESET}   {C.RED}{stats['failed']}{C.RESET} topics")
    print(f"  {C.GRAY}Elapsed:{C.RESET}  {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  {C.GRAY}Graph:{C.RESET}    {gstats['total_nodes']} concepts ({gstats.get('avg_confidence', 0):.0%} avg confidence)")

    # Per-domain breakdown
    print(f"\n  {C.BOLD}Per Domain:{C.RESET}")
    for name, ds in domain_stats.items():
        color = C.GREEN if ds["failed"] == 0 else C.YELLOW
        print(
            f"  {C.GRAY}  {name:20s}{C.RESET} "
            f"{color}✓{ds['learned']}{C.RESET} "
            f"{C.RED}✗{ds['failed']}{C.RESET} "
            f"{C.GRAY}/{ds['total']}{C.RESET}"
        )

    # Domain coverage from knowledge graph
    if gstats.get("domains"):
        print(f"\n  {C.BOLD}Knowledge Graph Domains:{C.RESET}")
        for domain, count in sorted(gstats["domains"].items(), key=lambda x: -x[1]):
            print(f"  {C.GRAY}  {domain:20s} {count} concepts{C.RESET}")

    print()


def main():
    parser = argparse.ArgumentParser(description="VELYNX Deep Learning Curriculum")
    parser.add_argument("--domain", type=str, help="Learn a single domain (physics, biology, etc.)")
    parser.add_argument("--rounds", type=int, default=1, help="Number of learning rounds (default: 1)")
    parser.add_argument("--shuffle", action="store_true", help="Randomize topic order")
    parser.add_argument("--delay", type=float, default=2.0, help="Seconds between topics (default: 2.0)")
    parser.add_argument("--list", action="store_true", help="List available domains and exit")
    args = parser.parse_args()

    domains = load_topics(args.domain)

    if args.list:
        all_domains = load_topics()
        print(f"\n{C.CYAN}Available domains:{C.RESET}")
        for name, topics in all_domains.items():
            print(f"  {name:20s} {len(topics)} topics")
        print(f"\n  {C.GRAY}Total: {sum(len(v) for v in all_domains.values())} topics{C.RESET}\n")
        return

    if not domains:
        print(f"{C.RED}No topics found.{C.RESET}")
        if args.domain:
            print(f"Domain '{args.domain}' not found. Use --list to see available domains.")
        return

    asyncio.run(run_deep_learning(domains, rounds=args.rounds, shuffle=args.shuffle, delay=args.delay))


if __name__ == "__main__":
    main()

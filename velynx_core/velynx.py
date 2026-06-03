"""
VELYNX CORE v2 — velynx.py
Main entry point. Fault-isolated orchestrator.
Each subsystem runs independently — one crash doesn't kill the others.

Usage:
  python velynx.py                        # interactive chat mode
  python velynx.py ask "What is gravity?" # single query
  python velynx.py learn                  # trigger one learning cycle now
  python velynx.py improve                # trigger one self-improvement cycle
  python velynx.py stats                  # show system status
  python velynx.py seed                   # load default curriculum
"""

import sys
import os
import time
import signal
import logging
import argparse
import textwrap
from typing import Optional

# ── Logging setup ────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("velynx_core/velynx.log", mode="a", encoding="utf-8"),
    ]
)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("urllib.request").setLevel(logging.WARNING)

logger = logging.getLogger("velynx")

# ── Colors ───────────────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CYAN   = "\033[36m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
RED    = "\033[31m"
BLUE   = "\033[34m"
MAGENTA= "\033[35m"

def c(text, color):
    return f"{color}{text}{RESET}" if sys.stdout.isatty() else text

BANNER = f"""
{CYAN}╔══════════════════════════════════════════════════════╗
║  {BOLD}VELYNX CORE v2{RESET}{CYAN}  —  Self-Reasoning AI System           ║
║  Graph-native · Self-learning · Self-improving        ║
╚══════════════════════════════════════════════════════╝{RESET}
"""


# ── Default curriculum ────────────────────────────────────────────────────────

DEFAULT_CURRICULUM = [
    # Physics
    {"topic": "quantum mechanics",        "domain": "physics",     "priority": 2.0},
    {"topic": "general relativity",       "domain": "physics",     "priority": 2.0},
    {"topic": "thermodynamics",           "domain": "physics",     "priority": 1.8},
    {"topic": "electromagnetism",         "domain": "physics",     "priority": 1.8},
    {"topic": "nuclear fusion",           "domain": "physics",     "priority": 1.6},
    {"topic": "dark matter",              "domain": "astronomy",   "priority": 1.6},
    {"topic": "black holes",              "domain": "astronomy",   "priority": 1.9},
    {"topic": "neutron stars",            "domain": "astronomy",   "priority": 1.5},
    {"topic": "gravitational waves",      "domain": "physics",     "priority": 1.7},
    # Mathematics
    {"topic": "calculus",                 "domain": "mathematics", "priority": 1.8},
    {"topic": "linear algebra",           "domain": "mathematics", "priority": 1.8},
    {"topic": "graph theory",             "domain": "mathematics", "priority": 1.6},
    {"topic": "fourier transform",        "domain": "mathematics", "priority": 1.5},
    {"topic": "differential equations",  "domain": "mathematics", "priority": 1.6},
    # Computer Science / AI
    {"topic": "transformer architecture", "domain": "AI",          "priority": 2.0},
    {"topic": "backpropagation",          "domain": "AI",          "priority": 2.0},
    {"topic": "attention mechanism",      "domain": "AI",          "priority": 1.9},
    {"topic": "gradient descent",         "domain": "AI",          "priority": 1.9},
    {"topic": "knowledge graph",          "domain": "AI",          "priority": 1.8},
    {"topic": "reinforcement learning",   "domain": "AI",          "priority": 1.7},
    {"topic": "recurrent neural network", "domain": "AI",          "priority": 1.6},
    {"topic": "convolutional neural network","domain": "AI",       "priority": 1.6},
    {"topic": "natural language processing","domain": "AI",        "priority": 1.7},
    {"topic": "large language models",    "domain": "AI",          "priority": 1.9},
    # Biology
    {"topic": "DNA replication",          "domain": "biology",     "priority": 1.5},
    {"topic": "CRISPR gene editing",      "domain": "biology",     "priority": 1.6},
    {"topic": "protein folding",          "domain": "biology",     "priority": 1.7},
    {"topic": "photosynthesis",           "domain": "biology",     "priority": 1.4},
    {"topic": "evolution",                "domain": "biology",     "priority": 1.5},
    # Chemistry
    {"topic": "chemical bonding",         "domain": "chemistry",   "priority": 1.4},
    {"topic": "periodic table",           "domain": "chemistry",   "priority": 1.3},
    {"topic": "catalysis",                "domain": "chemistry",   "priority": 1.4},
]


# ── VelynxSystem ──────────────────────────────────────────────────────────────

class VelynxSystem:
    """
    Fault-isolated orchestrator.
    Each subsystem is initialized in its own try/except.
    If memory fails → everything stops (it's foundational).
    If learner fails → reasoning still works from existing knowledge.
    If self_coder fails → learning still works.
    """

    def __init__(self, db_path: str = "velynx_core/velynx.db",
                 auto_start: bool = True):
        self.memory = None
        self.brain = None
        self.learner = None
        self.self_coder = None

        # Memory is foundational — no fallback
        try:
            from .memory import VelynxMemory
            self.memory = VelynxMemory(db_path)
            logger.info("Memory initialized")
        except Exception as e:
            logger.critical(f"Memory init failed: {e}")
            raise

        # Brain
        try:
            from .brain import VelynxBrain
            self.brain = VelynxBrain(self.memory)
            logger.info("Brain initialized")
        except Exception as e:
            logger.error(f"Brain init failed (non-fatal): {e}")

        # Learner
        try:
            from .learner import VelynxLearner
            self.learner = VelynxLearner(self.memory)
            if auto_start:
                self.learner.start()
            logger.info("Learner initialized")
        except Exception as e:
            logger.error(f"Learner init failed (non-fatal): {e}")

        # Self-coder (optional, requires gitpython)
        try:
            from .self_coder import VelynxSelfCoder
            self.self_coder = VelynxSelfCoder(
                self.memory,
                cycle_interval_seconds=3600
            )
            if auto_start:
                self.self_coder.start()
            logger.info("Self-coder initialized")
        except ImportError:
            logger.warning("gitpython not installed — self-coder disabled. Run: pip install gitpython")
        except Exception as e:
            logger.error(f"Self-coder init failed (non-fatal): {e}")

    def ask(self, query: str):
        """Query the reasoning engine. Returns VelynxAnswer or None."""
        if not self.brain:
            print(c("Brain not initialized.", RED))
            return None
        return self.brain.reason(query)

    def enqueue_learning(self, topic: str, domain: str = "general", priority: float = 1.0):
        if self.learner:
            self.learner.enqueue(topic, domain, priority)

    def seed_curriculum(self):
        if self.learner:
            added = self.learner.enqueue_curriculum(DEFAULT_CURRICULUM)
            logger.info(f"Seeded {added} curriculum topics")
            return added
        return 0

    def stats(self) -> dict:
        out = {}
        if self.memory:
            out["memory"] = self.memory.stats()
        if self.learner:
            out["learner"] = self.learner.stats()
        if self.self_coder:
            out["self_coder"] = self.self_coder.report()
        return out

    def shutdown(self):
        logger.info("Shutdown signal received")
        if self.learner:
            self.learner.stop()
        if self.self_coder:
            self.self_coder.stop()
        logger.info("VELYNX shut down cleanly")


# ── Terminal display ──────────────────────────────────────────────────────────

def display_answer(answer):
    """Rich terminal display of a VelynxAnswer."""
    if not answer:
        return

    conf_color = GREEN if answer.confidence > 0.6 else (YELLOW if answer.confidence > 0.3 else RED)
    conf_bar = "█" * int(answer.confidence * 20) + "░" * (20 - int(answer.confidence * 20))

    print(f"\n{c('━' * 60, CYAN)}")
    print(f"{c('QUERY', DIM)}: {answer.query}")
    print(f"{c('━' * 60, CYAN)}")

    print(f"\n{c('ANSWER', BOLD)}")
    print(textwrap.fill(answer.answer, width=70, initial_indent="  ", subsequent_indent="  "))

    if answer.what and answer.what != answer.answer:
        print(f"\n{c('◈ WHAT', CYAN)}  {textwrap.fill(answer.what, 65, subsequent_indent='       ')}")
    if answer.why:
        print(f"{c('◈ WHY', CYAN)}   {textwrap.fill(answer.why, 65, subsequent_indent='       ')}")
    if answer.how:
        print(f"{c('◈ HOW', CYAN)}   {textwrap.fill(answer.how, 65, subsequent_indent='       ')}")
    if answer.so_what:
        print(f"{c('◈ SO?', CYAN)}   {textwrap.fill(answer.so_what, 65, subsequent_indent='       ')}")

    print(f"\n{c('CONFIDENCE', DIM)}: {c(conf_bar, conf_color)} {answer.confidence:.2f}")
    print(f"{c('LATENCY', DIM)}:    {answer.latency_ms:.0f}ms  |  "
          f"{c('CONCEPTS', DIM)}: {', '.join(answer.concepts_used[:4]) or 'none'}")

    if answer.sources:
        print(f"{c('SOURCES', DIM)}:   {answer.sources[0][:70]}")

    # Reasoning chain (collapsed by default)
    if os.environ.get("VELYNX_VERBOSE"):
        print(f"\n{c('REASONING CHAIN', DIM)}:")
        for step in answer.reasoning_chain:
            print(f"  {step.step}. [{step.operation:10}] {step.output[:60]}  ({step.latency_ms:.0f}ms)")

    print(f"{c('━' * 60, CYAN)}\n")


def display_stats(stats: dict):
    print(f"\n{c('━' * 60, CYAN)}")
    print(f"{c('VELYNX SYSTEM STATUS', BOLD)}")
    print(f"{c('━' * 60, CYAN)}")

    mem = stats.get("memory", {})
    print(f"\n{c('MEMORY', CYAN)}")
    print(f"  Concepts:  {c(str(mem.get('concepts', 0)), BOLD)}")
    print(f"  Relations: {c(str(mem.get('relations', 0)), BOLD)}")
    print(f"  Embedded:  {c(str(mem.get('embedded', 0)), BOLD)}")
    print(f"  Avg Conf:  {c(str(mem.get('avg_confidence', 0)), BOLD)}")
    if mem.get("domains"):
        print(f"  Domains:   {', '.join(f'{k}({v})' for k,v in list(mem['domains'].items())[:5])}")

    lrn = stats.get("learner", {})
    if lrn:
        print(f"\n{c('LEARNER', CYAN)}")
        print(f"  Learned:  {lrn.get('total_learned', 0)}")
        print(f"  Pending:  {lrn.get('queue_pending', 0)}")
        print(f"  Failed:   {lrn.get('total_failed', 0)}")
        print(f"  Running:  {lrn.get('is_running', False)}")
        uptime = lrn.get("uptime_seconds", 0)
        print(f"  Uptime:   {uptime // 3600}h {(uptime % 3600) // 60}m")

    sc = stats.get("self_coder", {})
    if sc:
        print(f"\n{c('SELF-CODER', CYAN)}")
        print(f"  Total attempts:  {sc.get('total_attempts', 0)}")
        print(f"  Committed:       {sc.get('committed', 0)}")
        print(f"  Pass rate:       {sc.get('passed', 0)}/{sc.get('total_attempts', 1)}")
        print(f"  Running:         {sc.get('is_running', False)}")

    print(f"{c('━' * 60, CYAN)}\n")


# ── Interactive loop ──────────────────────────────────────────────────────────

HELP_TEXT = """
Commands:
  <anything>          → ask VELYNX a question
  learn <topic>       → queue a topic for immediate learning
  stats               → system status
  seed                → load default curriculum
  improve             → run one self-improvement cycle now
  help                → show this
  exit / quit         → shutdown
"""

def interactive_loop(system: VelynxSystem):
    print(BANNER)
    print(c("  Type a question, or 'help' for commands.", DIM))
    print()

    while True:
        try:
            raw = input(f"{c('velynx', CYAN)}{c('>', DIM)} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not raw:
            continue

        low = raw.lower()

        if low in ("exit", "quit", "bye"):
            break

        elif low == "help":
            print(HELP_TEXT)

        elif low == "stats":
            display_stats(system.stats())

        elif low == "seed":
            n = system.seed_curriculum()
            print(c(f"  → {n} topics added to learning queue.", GREEN))

        elif low == "improve":
            if system.self_coder:
                print(c("  Running self-improvement cycle...", YELLOW))
                attempts = system.self_coder.run_one_cycle()
                committed = sum(1 for a in attempts if a.committed)
                print(c(f"  → {len(attempts)} attempts, {committed} committed.", GREEN))
            else:
                print(c("  Self-coder not available.", RED))

        elif low.startswith("learn "):
            topic = raw[6:].strip()
            if topic:
                system.enqueue_learning(topic, priority=2.0)
                print(c(f"  → '{topic}' queued for immediate learning.", GREEN))
            else:
                print(c("  Usage: learn <topic>", YELLOW))

        else:
            # Regular question
            answer = system.ask(raw)
            if answer:
                display_answer(answer)
                # If no knowledge, auto-queue for learning
                if answer.confidence < 0.1:
                    system.enqueue_learning(raw, priority=2.0)
                    print(c(f"  → Queued for learning. Ask again in a minute.", DIM))

    system.shutdown()
    print(c("\nVELYNX shut down. Knowledge preserved.", DIM))


# ── CLI entry ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="VELYNX — Self-reasoning AI")
    parser.add_argument("command", nargs="?", default="chat",
                        choices=["chat", "ask", "learn", "improve", "stats", "seed"],
                        help="Command to run")
    parser.add_argument("query", nargs="?", default="",
                        help="Query for 'ask' command")
    parser.add_argument("--db", default="velynx_core/velynx.db",
                        help="Path to the VELYNX database")
    parser.add_argument("--no-background", action="store_true",
                        help="Don't start background learning/improvement threads")
    args = parser.parse_args()

    auto_start = not args.no_background

    # Initialize
    print(c("Initializing VELYNX Core v2...", DIM))
    try:
        system = VelynxSystem(db_path=args.db, auto_start=auto_start)
    except Exception as e:
        print(c(f"CRITICAL: VELYNX failed to initialize: {e}", RED))
        sys.exit(1)

    # Handle signals
    def handle_signal(sig, frame):
        print(c("\nShutting down...", YELLOW))
        system.shutdown()
        sys.exit(0)
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Dispatch
    if args.command == "chat" or (args.command == "ask" and not args.query):
        interactive_loop(system)

    elif args.command == "ask" and args.query:
        answer = system.ask(args.query)
        if answer:
            display_answer(answer)
        system.shutdown()

    elif args.command == "learn":
        if args.query:
            system.enqueue_learning(args.query, priority=2.0)
            print(c(f"Queued: '{args.query}'", GREEN))
        else:
            print(c("Usage: python velynx.py learn <topic>", YELLOW))
        system.shutdown()

    elif args.command == "improve":
        if system.self_coder:
            print(c("Running self-improvement cycle...", YELLOW))
            attempts = system.self_coder.run_one_cycle()
            committed = sum(1 for a in attempts if a.committed)
            print(c(f"Complete: {len(attempts)} attempts, {committed} committed.", GREEN))
        else:
            print(c("Self-coder not available.", RED))
        system.shutdown()

    elif args.command == "stats":
        display_stats(system.stats())
        system.shutdown()

    elif args.command == "seed":
        n = system.seed_curriculum()
        print(c(f"Seeded {n} curriculum topics.", GREEN))
        system.shutdown()


if __name__ == "__main__":
    # Allow running as: python velynx.py or python velynx_core/velynx.py
    sys.path.insert(0, str(__file__).replace("velynx_core/velynx.py", "").replace("velynx.py", ""))
    main()
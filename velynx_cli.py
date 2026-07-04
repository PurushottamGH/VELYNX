"""VELYNX CLI — unified entry point for terminal usage."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / "backend"))

from app.pipeline import answer_question
from cli import main as backend_cli_main
from pipeline.reasoning_core import reason as _reason
# DeepLearner is an optional dependency. Import it lazily/defensively so the CLI
# can boot even when the deep_learner module (or its deps) is unavailable.
try:
    from learning.deep_learner import DeepLearner
except Exception:  # pragma: no cover - optional dependency
    DeepLearner = None
from cognition.sim_engine import SimEngine
from memory.knowledge_graph import KnowledgeGraph


def internal_reason(query: str, sources: list[dict]) -> dict:
    result = _reason(sources=sources, query=query)
    if not isinstance(result, dict):
        return {"answer": str(result), "confidence": "UNKNOWN"}
    return {
        "answer": result.get("draft", ""),
        "confidence": result.get("confidence", "UNKNOWN"),
        "citations": result.get("citations", []),
        "gaps": result.get("gaps", []),
    }


def _run_direct_question(question: str) -> int:
    if not question:
        print("Usage: python velynx_cli.py <your query>")
        return 1

    # Route special prefixes to appropriate engines
    if question.startswith("learn:"):
        topic = question[6:].strip()
        if not topic:
            print("Usage: python velynx_cli.py learn: <topic>")
            return 1
        print(f"Learning about: {topic}")

        if DeepLearner is None:
            print("Error: DeepLearner is unavailable; the 'learn:' command is disabled.")
            return 1

        # Initialize required components
        kg = KnowledgeGraph()
        # For CLI usage, we'll pass None for vector store since it's not needed for basic functionality
        # In a full implementation, you'd need to initialize the vector store as well

        try:
            result = asyncio.run(DeepLearner(kg, None).deep_learn(topic))
            print(f"Learned topic: {topic}")
            return 0
        except Exception as e:
            print(f"Error learning: {e}")
            return 1

    if question.startswith("simulate:"):
        sim_type = question[9:].strip()
        if not sim_type:
            print("Usage: python velynx_cli.py simulate: <type>")
            return 1
        print(f"Running simulation: {sim_type}")
        try:
            result = SimEngine().run(sim_type, {})
            print(result.ascii_preview)
            if result.html_path:
                print(f"Interactive view: {result.html_path}")
            if result.error:
                print(f"Error: {result.error}")
            return 0
        except Exception as e:
            print(f"Error running simulation: {e}")
            return 1

    response = asyncio.run(answer_question(question))
    print(f"You: {question}")
    print(f"Velynx: {response.answer}")
    print(f"Confidence: {response.confidence}")

    if response.citations:
        print("Citations:")
        for item in response.citations:
            print(f"  - {item}")

    if response.gaps:
        print("Gaps:")
        for item in response.gaps:
            print(f"  - {item}")

    return 0


def _run_e0(args: list[str]) -> int:
    """Run the E0 emergence-vs-injection experiment."""
    import argparse
    parser = argparse.ArgumentParser(description="E0: Emergence-vs-Injection Discrimination")
    parser.add_argument("--output-dir", help="Output directory for results")
    parser.add_argument("--config", help="Path to experiment config JSON")
    parser.add_argument("--seed", type=int, default=42, help="Base master random seed")
    parser.add_argument("--num-seeds", type=int, default=5,
                        help="Number of seeds to run (default: 5, min 5)")
    parsed = parser.parse_args(args)

    from experiments.E0.run import main as e0_main
    e0_main(
        output_dir=parsed.output_dir,
        config=parsed.config,
        seed=parsed.seed,
        num_seeds=parsed.num_seeds,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args_list = list(argv) if argv is not None else sys.argv[1:]
    subcommands = {"teach", "review", "chat", "e0"}
    if not args_list:
        print("Usage: python velynx_cli.py <query or subcommand>")
        print("Subcommands: teach, review, chat, e0")
        return 1
    cmd = args_list[0]
    if cmd == "e0":
        return _run_e0(args_list[1:])
    if cmd not in subcommands and not cmd.startswith("-"):
        return _run_direct_question(" ".join(args_list).strip())
    return int(backend_cli_main(args_list))


if __name__ == "__main__":
    raise SystemExit(main())
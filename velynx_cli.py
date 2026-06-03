"""VELYNX CLI — unified entry point for terminal usage."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / "backend"))

from app.pipeline import answer_question
from cli import main as backend_cli_main
from pipeline.reasoning_core import reason as _reason


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


def main(argv: list[str] | None = None) -> int:
    args = list(argv) if argv is not None else sys.argv[1:]
    subcommands = {"teach", "review", "chat"}
    if args and not args[0].startswith("-") and args[0] not in subcommands:
        return _run_direct_question(" ".join(args).strip())
    return int(backend_cli_main(args))


if __name__ == "__main__":
    raise SystemExit(main())
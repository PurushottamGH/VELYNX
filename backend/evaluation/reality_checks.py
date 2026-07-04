"""Reality checks — validate cognition against known ground truths."""
from __future__ import annotations

import logging
from typing import Any, Callable, Awaitable

from backend.evaluation import MetricEvaluation
from backend.evaluation.hallucination_detector import hallucination_detector

logger = logging.getLogger("uvicorn")

QueryExecutor = Callable[[str], Awaitable[dict[str, Any]]]

# Known ground truth facts for validation
GROUND_TRUTH_FACTS = [
    {"query": "What is the speed of light in m/s?", "expected": "299792458", "category": "physics"},
    {"query": "What is the chemical formula for water?", "expected": "H2O", "category": "chemistry"},
    {"query": "What year did World War II end?", "expected": "1945", "category": "history"},
    {"query": "What is the capital of France?", "expected": "Paris", "category": "geography"},
    {"query": "What is the boiling point of water in Celsius?", "expected": "100", "category": "physics"},
    {"query": "Who wrote Romeo and Juliet?", "expected": "Shakespeare", "category": "literature"},
    {"query": "What is the largest planet in our solar system?", "expected": "Jupiter", "category": "astronomy"},
    {"query": "What is the square root of 144?", "expected": "12", "category": "mathematics"},
    {"query": "What is the chemical symbol for gold?", "expected": "Au", "category": "chemistry"},
    {"query": "What is the speed of sound in air at sea level in m/s?", "expected": "343", "category": "physics"},
]


class RealityChecker:
    """Validates cognition against known ground truths."""

    async def run_reality_check(
        self, executor: QueryExecutor, facts: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """Run reality checks against known facts."""
        facts = facts or GROUND_TRUTH_FACTS
        results: list[dict[str, Any]] = []

        for fact in facts:
            query = fact["query"]
            expected = fact["expected"]
            category = fact.get("category", "general")

            try:
                response = await executor(query)
                answer = str(response.get("answer", ""))
                confidence = str(response.get("confidence", "UNKNOWN"))

                # Check if expected answer is present
                contains_expected = expected.lower() in answer.lower()

                # Hallucination analysis
                hallucination = hallucination_detector.analyze(
                    query=query,
                    answer=answer,
                    sources=response.get("sources", []),
                    confidence=confidence,
                )

                results.append({
                    "query": query,
                    "expected": expected,
                    "actual": answer[:200],
                    "confidence": confidence,
                    "contains_expected": contains_expected,
                    "hallucination_risk": hallucination.risk_score,
                    "category": category,
                    "passed": contains_expected and hallucination.risk_score < 0.5,
                })

            except Exception as exc:
                results.append({
                    "query": query,
                    "expected": expected,
                    "error": str(exc),
                    "category": category,
                    "passed": False,
                })

        # Aggregate by category
        by_category: dict[str, list[dict]] = {}
        for r in results:
            cat = r.get("category", "general")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(r)

        category_scores = {}
        for cat, cat_results in by_category.items():
            passed = sum(1 for r in cat_results if r.get("passed", False))
            category_scores[cat] = round(passed / len(cat_results), 3) if cat_results else 0.0

        total_passed = sum(1 for r in results if r.get("passed", False))

        return {
            "test_name": "reality_check",
            "total_facts": len(results),
            "passed": total_passed,
            "failed": len(results) - total_passed,
            "pass_rate": round(total_passed / len(results), 3) if results else 0.0,
            "category_scores": category_scores,
            "results": results,
        }


# Module-level singleton
reality_checker = RealityChecker()

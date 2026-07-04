"""Memory retrieval quality tests."""
from __future__ import annotations

import logging
from typing import Any

from backend.evaluation import MetricEvaluation

logger = logging.getLogger("uvicorn")


class MemoryRetrievalEvaluator:
    """Evaluates memory retrieval quality and relevance."""

    async def evaluate_recall(
        self,
        query: str,
        recall_results: list[dict[str, Any]],
        min_results: int = 1,
        min_score: float = 0.3,
    ) -> list[MetricEvaluation]:
        """Evaluate recall results for a query."""
        evaluations: list[MetricEvaluation] = []

        # Result count
        evaluations.append(MetricEvaluation(
            name="recall_count",
            value=float(len(recall_results)),
            threshold=float(min_results),
            passed=len(recall_results) >= min_results,
            description=f"Recalled {len(recall_results)} results (min: {min_results})",
        ))

        if not recall_results:
            return evaluations

        # Score quality
        scores = [r.get("score", 0.0) for r in recall_results]
        max_score = max(scores)
        avg_score = sum(scores) / len(scores)

        evaluations.append(MetricEvaluation(
            name="max_recall_score",
            value=max_score,
            threshold=min_score,
            passed=max_score >= min_score,
            description=f"Max recall score: {max_score:.3f} (min: {min_score})",
        ))

        evaluations.append(MetricEvaluation(
            name="avg_recall_score",
            value=avg_score,
            threshold=min_score * 0.8,
            passed=avg_score >= min_score * 0.8,
            description=f"Avg recall score: {avg_score:.3f}",
        ))

        # Score distribution
        high_score_count = sum(1 for s in scores if s >= 0.5)
        evaluations.append(MetricEvaluation(
            name="high_score_ratio",
            value=high_score_count / len(scores) if scores else 0.0,
            threshold=0.3,
            passed=(high_score_count / len(scores) if scores else 0.0) >= 0.3,
            description=f"High-score results: {high_score_count}/{len(scores)}",
        ))

        return evaluations

    async def evaluate_memory_stats(
        self, stats: dict[str, Any]
    ) -> list[MetricEvaluation]:
        """Evaluate overall memory health from stats."""
        evaluations: list[MetricEvaluation] = []

        total = stats.get("total_entries", 0)
        evaluations.append(MetricEvaluation(
            name="memory_size",
            value=float(total),
            threshold=0.0,
            passed=total > 0,
            description=f"Total memory entries: {total}",
        ))

        by_kind = stats.get("by_kind", {})
        for kind in ["episodic", "semantic", "working"]:
            count = by_kind.get(kind, 0)
            evaluations.append(MetricEvaluation(
                name=f"memory_{kind}_count",
                value=float(count),
                threshold=0.0,
                passed=True,  # informational, not pass/fail
                description=f"{kind} memories: {count}",
            ))

        avg_importance = stats.get("avg_importance", 0.0)
        evaluations.append(MetricEvaluation(
            name="avg_importance",
            value=avg_importance,
            threshold=0.3,
            passed=avg_importance >= 0.3,
            description=f"Average importance: {avg_importance:.2f}",
        ))

        return evaluations

    def score_recall_quality(
        self,
        results: list[dict[str, Any]],
        expected_min: int = 1,
    ) -> float:
        """Compute a 0.0-1.0 recall quality score."""
        if not results:
            return 0.0

        count_score = min(len(results) / max(expected_min, 1), 1.0) * 0.3
        scores = [r.get("score", 0.0) for r in results]
        max_score = max(scores) if scores else 0.0
        avg_score = sum(scores) / len(scores) if scores else 0.0
        quality_score = (max_score * 0.4 + avg_score * 0.3)

        return min(count_score + quality_score, 1.0)


# Module-level singleton
memory_retrieval_evaluator = MemoryRetrievalEvaluator()

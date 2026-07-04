"""Cross-domain strategy performance analysis."""
from __future__ import annotations

import logging
from collections import defaultdict

from backend.database.engine import async_session
from backend.database.repositories import ReflectionRepository
from backend.metacognition import StrategyAnalysis, StrategyPerformance

logger = logging.getLogger("uvicorn")

_STRATEGY_NAMES = [
    "broad_retrieval", "depth_first", "contradiction_first", "incremental", "parallel"
]


class CrossDomainStrategyAnalyzer:
    """Analyzes strategy performance across query types and cognitive layers."""

    async def analyze(self) -> StrategyAnalysis:
        """Analyze strategy performance across all domains."""
        scores = self._load_strategy_scores()
        reflections = await self._load_reflections(200)

        performances = self._build_performances(scores)
        self._correlate_with_reflections(performances, reflections)

        best, worst = self._find_best_worst(performances)
        underused = self._find_underused(scores)
        recommendations = self._generate_domain_recommendations(performances)

        return StrategyAnalysis(
            strategies=performances,
            best_performing=best,
            worst_performing=worst,
            underused_strategies=underused,
            domain_recommendations=recommendations,
        )

    def _load_strategy_scores(self) -> dict:
        """Load strategy scores from PermanenceLayer state."""
        try:
            from learning.permanence import _DEFAULT_PERMANENCE
            state = _DEFAULT_PERMANENCE._state
            return state.get("strategy_scores", {})
        except Exception as exc:
            logger.debug("Strategy scores load skipped: %s", exc)
            return {}

    async def _load_reflections(self, limit: int) -> list:
        try:
            async with async_session() as session:
                return await ReflectionRepository(session).get_history(limit=limit)
        except Exception:
            return []

    def _build_performances(self, scores: dict) -> list[StrategyPerformance]:
        """Build StrategyPerformance for each strategy+query_type combination."""
        performances = []
        for key, strategy_scores in scores.items():
            # key format: "layer::query_type" or just "query_type"
            parts = key.split("::", 1)
            query_type = parts[-1]

            for strategy_name in _STRATEGY_NAMES:
                learned_score = 0.0
                if isinstance(strategy_scores, dict):
                    learned_score = strategy_scores.get(strategy_name, 0.0)

                performances.append(StrategyPerformance(
                    strategy_name=strategy_name,
                    query_type=query_type,
                    learned_score=learned_score,
                    usage_count=0,
                    avg_reasoning_quality=0.0,
                    avg_hallucination_risk=0.0,
                ))
        return performances

    def _correlate_with_reflections(
        self, performances: list[StrategyPerformance], reflections: list
    ) -> None:
        """Enrich performances with reflection quality data."""
        # Build lookup: (query_type, strategy_name) -> list of qualities
        quality_data: dict[tuple[str, str], list[float]] = defaultdict(list)
        risk_data: dict[tuple[str, str], list[float]] = defaultdict(list)

        for r in reflections:
            if not r.query:
                continue
            try:
                from learning.strategy_optimizer import classify_query
                query_type = classify_query(r.query)
            except Exception:
                query_type = "practical"

            # We don't know which strategy was used for a given reflection,
            # so we attribute quality to all strategies for this query type
            for strategy_name in _STRATEGY_NAMES:
                key = (query_type, strategy_name)
                quality_data[key].append(r.reasoning_quality or 0.0)
                risk_data[key].append(r.hallucination_risk or 0.0)

        for p in performances:
            key = (p.query_type, p.strategy_name)
            qualities = quality_data.get(key, [])
            risks = risk_data.get(key, [])
            p.usage_count = len(qualities)
            p.avg_reasoning_quality = sum(qualities) / len(qualities) if qualities else 0.0
            p.avg_hallucination_risk = sum(risks) / len(risks) if risks else 0.0

    def _find_best_worst(
        self, performances: list[StrategyPerformance]
    ) -> tuple[StrategyPerformance | None, StrategyPerformance | None]:
        """Find best and worst by learned_score (with quality as tiebreaker)."""
        if not performances:
            return None, None

        scored = [p for p in performances if p.learned_score != 0 or p.usage_count > 0]
        if not scored:
            return None, None

        best = max(scored, key=lambda p: (p.learned_score, p.avg_reasoning_quality))
        worst = min(scored, key=lambda p: (p.learned_score, -p.avg_hallucination_risk))
        return best, worst

    def _find_underused(self, scores: dict) -> list[str]:
        """Find strategies never tried across all query types."""
        used = set()
        for strategy_scores in scores.values():
            if isinstance(strategy_scores, dict):
                used.update(k for k, v in strategy_scores.items() if v > 0)
        return [s for s in _STRATEGY_NAMES if s not in used]

    def _generate_domain_recommendations(
        self, performances: list[StrategyPerformance]
    ) -> dict[str, str]:
        """For each query type, recommend the best strategy."""
        by_type: dict[str, list[StrategyPerformance]] = defaultdict(list)
        for p in performances:
            by_type[p.query_type].append(p)

        recommendations = {}
        for query_type, perfs in by_type.items():
            if not perfs:
                continue
            best = max(perfs, key=lambda p: (p.learned_score, p.avg_reasoning_quality))
            recommendations[query_type] = best.strategy_name
        return recommendations

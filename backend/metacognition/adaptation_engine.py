"""Recommendation generation from metacognition analysis outputs."""
from __future__ import annotations

import logging

from metacognition import (
    AdaptationRecommendation,
    CalibrationReport,
    CognitionHealthReport,
    CognitionMetricsReport,
    PatternCluster,
    RuntimePerformanceMetrics,
    StrategyAnalysis,
)

logger = logging.getLogger("uvicorn")


class AdaptationEngine:
    """Generates adaptation recommendations. NEVER auto-applies changes."""

    def generate(
        self,
        metrics: CognitionMetricsReport,
        patterns: list[PatternCluster],
        calibration: CalibrationReport,
        strategy_analysis: StrategyAnalysis,
        health: CognitionHealthReport,
        runtime: RuntimePerformanceMetrics,
    ) -> list[AdaptationRecommendation]:
        """Generate all recommendations from analysis outputs."""
        recs: list[AdaptationRecommendation] = []
        recs.extend(self._strategy_recommendations(strategy_analysis))
        recs.extend(self._confidence_recommendations(calibration))
        recs.extend(self._reasoning_recommendations(metrics, patterns))
        recs.extend(self._source_recommendations(metrics))
        recs.extend(self._runtime_recommendations(runtime))
        return self._prioritize(recs)

    def _strategy_recommendations(
        self, analysis: StrategyAnalysis
    ) -> list[AdaptationRecommendation]:
        recs = []
        if analysis.underused_strategies:
            recs.append(AdaptationRecommendation(
                category="strategy",
                priority=6,
                title="Underused strategies detected",
                description=f"Strategies {analysis.underused_strategies} have never been tried. "
                    "Exploring them may improve performance on certain query types.",
                rationale="Diversifying strategy usage can discover better approaches.",
                affected_component="planning/strategy_engine.py",
                suggested_change=f"Consider using {analysis.underused_strategies[0]} for queries "
                    "where current strategies underperform.",
            ))
        if analysis.domain_recommendations:
            for domain, strategy in analysis.domain_recommendations.items():
                recs.append(AdaptationRecommendation(
                    category="strategy",
                    priority=4,
                    title=f"Best strategy for '{domain}' queries",
                    description=f"Strategy '{strategy}' performs best for {domain} queries.",
                    rationale=f"Learned from strategy score analysis across {domain} domain.",
                    affected_component="planning/strategy_engine.py",
                    suggested_change=f"Ensure '{strategy}' is preferred for {domain} queries.",
                ))
        return recs

    def _confidence_recommendations(
        self, calibration: CalibrationReport
    ) -> list[AdaptationRecommendation]:
        recs = []
        if calibration.overconfidence_rate > 0.3:
            recs.append(AdaptationRecommendation(
                category="confidence",
                priority=8,
                title="High overconfidence rate detected",
                description=f"System is overconfident in {calibration.overconfidence_rate:.0%} of cases. "
                    "Calibrated confidence exceeds actual reasoning quality.",
                rationale="Overconfidence erodes user trust and may propagate incorrect information.",
                affected_component="reflection/confidence_estimator.py",
                suggested_change="Increase weight of source quality and citation signals in confidence estimation.",
            ))
        if calibration.calibration_error > 0.1:
            recs.append(AdaptationRecommendation(
                category="confidence",
                priority=6,
                title="Calibration error above threshold",
                description=f"Brier-like calibration error is {calibration.calibration_error:.3f}. "
                    "Confidence levels do not reliably predict reasoning quality.",
                rationale="Poor calibration means confidence is not a useful quality signal.",
                affected_component="reflection/confidence_estimator.py",
                suggested_change="Review calibration delta signal weights and thresholds.",
            ))
        return recs

    def _reasoning_recommendations(
        self, metrics: CognitionMetricsReport, patterns: list[PatternCluster]
    ) -> list[AdaptationRecommendation]:
        recs = []
        if metrics.reasoning_quality.direction == "degrading":
            recs.append(AdaptationRecommendation(
                category="reasoning",
                priority=7,
                title="Reasoning quality trending downward",
                description=f"Reasoning quality has been degrading over the last {metrics.window.hours} hours. "
                    f"Current: {metrics.reasoning_quality.current:.2f}, mean: {metrics.reasoning_quality.mean:.2f}.",
                rationale="Declining quality indicates systemic issues in retrieval or reasoning.",
                affected_component="pipeline/inference_pipeline.py",
                suggested_change="Review source quality and consider adjusting retrieval strategy.",
            ))

        high_risk_clusters = [
            c for c in patterns if c.avg_hallucination_risk > 0.5
        ]
        if high_risk_clusters:
            labels = [c.label for c in high_risk_clusters]
            recs.append(AdaptationRecommendation(
                category="reasoning",
                priority=7,
                title="High hallucination risk in pattern clusters",
                description=f"Clusters with high hallucination risk: {labels}. "
                    "Consider using contradiction-first strategy for these query types.",
                rationale="High hallucination risk indicates unreliable source material.",
                affected_component="planning/strategy_engine.py",
                suggested_change="Prioritize contradiction detection for queries matching these patterns.",
            ))
        return recs

    def _source_recommendations(
        self, metrics: CognitionMetricsReport
    ) -> list[AdaptationRecommendation]:
        recs = []
        unsupported = metrics.issue_category_counts.get("unsupported", 0)
        if unsupported > 5:
            recs.append(AdaptationRecommendation(
                category="sources",
                priority=6,
                title="Frequent unsupported claims",
                description=f"{unsupported} unsupported claims detected in the analysis window.",
                rationale="Unsupported claims indicate insufficient source coverage.",
                affected_component="pipeline/retrieval_mesh.py",
                suggested_change="Increase minimum source count or add citation enforcement.",
            ))
        return recs

    def _runtime_recommendations(
        self, runtime: RuntimePerformanceMetrics
    ) -> list[AdaptationRecommendation]:
        recs = []
        if runtime.error_rate > 0.05:
            recs.append(AdaptationRecommendation(
                category="runtime",
                priority=8,
                title="High handler error rate",
                description=f"Handler error rate is {runtime.error_rate:.1%}. "
                    "Event handlers are failing frequently.",
                rationale="Handler failures may cause data loss or incomplete processing.",
                affected_component="runtime/event_handlers.py",
                suggested_change="Investigate failing handlers and add better error handling.",
            ))
        if runtime.avg_handler_latency_ms > 5000:
            recs.append(AdaptationRecommendation(
                category="runtime",
                priority=5,
                title="High handler latency",
                description=f"Average handler latency is {runtime.avg_handler_latency_ms:.0f}ms.",
                rationale="High latency may cause request timeouts.",
                affected_component="runtime/event_handlers.py",
                suggested_change="Profile slow handlers and optimize database queries.",
            ))
        return recs

    def _prioritize(
        self, recs: list[AdaptationRecommendation]
    ) -> list[AdaptationRecommendation]:
        """Sort by priority descending, deduplicate by title."""
        seen = set()
        unique = []
        for r in sorted(recs, key=lambda x: x.priority, reverse=True):
            if r.title not in seen:
                seen.add(r.title)
                unique.append(r)
        return unique

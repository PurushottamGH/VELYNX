"""Reflection quality evaluation — scores reflection outputs."""
from __future__ import annotations

import logging
from typing import Any

from evaluation import MetricEvaluation

logger = logging.getLogger("uvicorn")


class ReflectionEvaluator:
    """Evaluates the quality of reflection outputs."""

    def evaluate(self, reflection: dict[str, Any]) -> list[MetricEvaluation]:
        """Evaluate a reflection result against quality thresholds."""
        evaluations: list[MetricEvaluation] = []

        reasoning_quality = reflection.get("reasoning_quality", 0.0)
        evaluations.append(MetricEvaluation(
            name="reasoning_quality",
            value=reasoning_quality,
            threshold=0.5,
            passed=reasoning_quality >= 0.5,
            description=f"Reasoning quality: {reasoning_quality:.2f}",
        ))

        hallucination_risk = reflection.get("hallucination_risk", 0.0)
        evaluations.append(MetricEvaluation(
            name="hallucination_risk",
            value=hallucination_risk,
            threshold=0.3,
            passed=hallucination_risk < 0.3,
            description=f"Hallucination risk: {hallucination_risk:.2f}",
        ))

        # Audit issues
        audit = reflection.get("audit", {})
        if isinstance(audit, dict):
            issues = audit.get("issues", [])
            issue_count = len(issues) if isinstance(issues, list) else 0
            evaluations.append(MetricEvaluation(
                name="issue_count",
                value=float(issue_count),
                threshold=3.0,
                passed=issue_count < 3,
                description=f"Audit issues: {issue_count}",
            ))

            overall_quality = audit.get("overall_quality", 0.5)
            evaluations.append(MetricEvaluation(
                name="audit_quality",
                value=overall_quality,
                threshold=0.5,
                passed=overall_quality >= 0.5,
                description=f"Audit quality: {overall_quality:.2f}",
            ))

        # Confidence calibration
        conf = reflection.get("confidence_estimate", {})
        if isinstance(conf, dict):
            delta = conf.get("delta", 0.0) or 0.0
            evaluations.append(MetricEvaluation(
                name="confidence_calibration",
                value=abs(delta),
                threshold=0.2,
                passed=abs(delta) < 0.2,
                description=f"Confidence delta: {delta:+.2f}",
            ))

        # Improvements
        improvements = reflection.get("improvements", [])
        if isinstance(improvements, list):
            high_priority = sum(1 for i in improvements if isinstance(i, dict) and i.get("priority", 0) >= 7)
            evaluations.append(MetricEvaluation(
                name="high_priority_improvements",
                value=float(high_priority),
                threshold=2.0,
                passed=high_priority < 2,
                description=f"High-priority improvements: {high_priority}",
            ))

        return evaluations

    def score_reflection(self, reflection: dict[str, Any]) -> float:
        """Compute an overall reflection quality score (0.0-1.0)."""
        evaluations = self.evaluate(reflection)
        if not evaluations:
            return 0.0
        passed = sum(1 for e in evaluations if e.passed)
        return passed / len(evaluations)

    def evaluate_batch(self, reflections: list[dict[str, Any]]) -> dict[str, float]:
        """Evaluate a batch of reflections and return aggregate metrics."""
        if not reflections:
            return {"avg_quality": 0.0, "avg_risk": 0.0, "pass_rate": 0.0}

        qualities = [r.get("reasoning_quality", 0.0) for r in reflections]
        risks = [r.get("hallucination_risk", 0.0) for r in reflections]
        scores = [self.score_reflection(r) for r in reflections]

        return {
            "avg_quality": sum(qualities) / len(qualities),
            "avg_risk": sum(risks) / len(risks),
            "pass_rate": sum(1 for s in scores if s >= 0.6) / len(scores),
            "min_quality": min(qualities),
            "max_quality": max(qualities),
            "min_risk": min(risks),
            "max_risk": max(risks),
        }


# Module-level singleton
reflection_evaluator = ReflectionEvaluator()

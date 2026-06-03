"""Failure analysis — clusters and diagnoses cognition failures."""
from __future__ import annotations

import logging
from collections import Counter, defaultdict
from typing import Any

logger = logging.getLogger("uvicorn")


class FailureAnalyzer:
    """Analyzes and clusters cognition failures from trial results."""

    def analyze_failures(
        self, trial_results: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze failures from a list of trial query results."""
        failures = [r for r in trial_results if not r.get("passed", True)]

        if not failures:
            return {
                "total_failures": 0,
                "failure_rate": 0.0,
                "clusters": [],
                "recommendations": [],
            }

        # Cluster failures by error type
        clusters = self._cluster_failures(failures)

        # Generate recommendations
        recommendations = self._generate_recommendations(clusters, len(trial_results))

        return {
            "total_failures": len(failures),
            "failure_rate": round(len(failures) / len(trial_results), 3) if trial_results else 0.0,
            "clusters": clusters,
            "recommendations": recommendations,
        }

    def _cluster_failures(
        self, failures: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Cluster failures by type and characteristics."""
        clusters: dict[str, list[dict]] = defaultdict(list)

        for failure in failures:
            cluster_key = self._classify_failure(failure)
            clusters[cluster_key].append(failure)

        result = []
        for key, items in clusters.items():
            queries = [item.get("query", "")[:100] for item in items[:3]]
            risk_scores = [item.get("hallucination_risk", item.get("risk_score", 0)) for item in items]
            avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0

            result.append({
                "cluster_type": key,
                "count": len(items),
                "avg_risk_score": round(avg_risk, 3),
                "example_queries": queries,
                "description": self._describe_cluster(key, len(items)),
            })

        return sorted(result, key=lambda c: c["count"], reverse=True)

    def _classify_failure(self, failure: dict[str, Any]) -> str:
        """Classify a failure into a cluster type."""
        if "error" in failure:
            error = str(failure["error"]).lower()
            if "timeout" in error:
                return "timeout"
            if "connection" in error or "network" in error:
                return "network_error"
            if "memory" in error:
                return "memory_error"
            return "execution_error"

        risk = failure.get("hallucination_risk", failure.get("risk_score", 0))
        confidence = failure.get("confidence", "UNKNOWN")

        if risk > 0.7:
            return "high_hallucination"
        if confidence in ("CERTAIN", "PROBABLE") and risk > 0.4:
            return "overconfident"
        if failure.get("source_count", 0) == 0:
            return "no_sources"
        if failure.get("reasoning_quality", 0.5) < 0.3:
            return "poor_reasoning"

        return "general_failure"

    def _describe_cluster(self, cluster_type: str, count: int) -> str:
        """Generate a description for a failure cluster."""
        descriptions = {
            "high_hallucination": f"{count} queries with high hallucination risk (>0.7)",
            "overconfident": f"{count} queries with overconfident answers",
            "no_sources": f"{count} queries with no source coverage",
            "poor_reasoning": f"{count} queries with low reasoning quality (<0.3)",
            "timeout": f"{count} queries that timed out",
            "network_error": f"{count} queries with network errors",
            "memory_error": f"{count} queries with memory errors",
            "execution_error": f"{count} queries with execution errors",
            "general_failure": f"{count} queries with general failures",
        }
        return descriptions.get(cluster_type, f"{count} failures of type '{cluster_type}'")

    def _generate_recommendations(
        self, clusters: list[dict[str, Any]], total_queries: int
    ) -> list[str]:
        """Generate recommendations based on failure clusters."""
        recs = []
        for cluster in clusters:
            cluster_type = cluster["cluster_type"]
            count = cluster["count"]
            rate = count / total_queries if total_queries > 0 else 0.0

            if cluster_type == "high_hallucination" and rate > 0.1:
                recs.append(f"High hallucination rate ({rate:.0%}) — improve source verification and citation enforcement")
            elif cluster_type == "overconfident" and rate > 0.1:
                recs.append(f"Overconfidence rate ({rate:.0%}) — recalibrate confidence estimation thresholds")
            elif cluster_type == "no_sources" and rate > 0.05:
                recs.append(f"No-source rate ({rate:.0%}) — ensure minimum source retrieval for all queries")
            elif cluster_type == "poor_reasoning" and rate > 0.1:
                recs.append(f"Poor reasoning rate ({rate:.0%}) — review inference pipeline and context building")
            elif cluster_type == "timeout":
                recs.append(f"Timeout rate ({rate:.0%}) — optimize retrieval and inference latency")
            elif cluster_type in ("network_error", "memory_error", "execution_error"):
                recs.append(f"Infrastructure errors ({rate:.0%}) — investigate system stability")

        return recs

    def analyze_hallucination_accumulation(
        self, trial_results: list[dict[str, Any]], window_size: int = 10
    ) -> dict[str, Any]:
        """Analyze how hallucination risk accumulates over a session."""
        if len(trial_results) < window_size:
            return {"windows": [], "accumulation_detected": False}

        windows = []
        for i in range(0, len(trial_results) - window_size + 1, window_size):
            window = trial_results[i:i + window_size]
            risks = [r.get("hallucination_risk", r.get("risk_score", 0)) for r in window]
            avg_risk = sum(risks) / len(risks) if risks else 0.0
            windows.append({
                "start_index": i,
                "end_index": i + window_size,
                "avg_risk": round(avg_risk, 3),
                "max_risk": round(max(risks), 3) if risks else 0.0,
            })

        # Check for accumulation trend
        accumulation_detected = False
        if len(windows) >= 2:
            first_risk = windows[0]["avg_risk"]
            last_risk = windows[-1]["avg_risk"]
            accumulation_detected = last_risk > first_risk * 1.5 and last_risk > 0.3

        return {
            "windows": windows,
            "accumulation_detected": accumulation_detected,
            "window_size": window_size,
        }


# Module-level singleton
failure_analyzer = FailureAnalyzer()

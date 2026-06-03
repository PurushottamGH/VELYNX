"""Failure/reasoning pattern clustering from reflection history."""
from __future__ import annotations

import hashlib
import logging
from collections import Counter, defaultdict

from database.engine import async_session
from database.repositories import ReflectionRepository
from metacognition import PatternCluster, ReasoningPattern

logger = logging.getLogger("uvicorn")


class PatternAnalyzer:
    """Detects and clusters reasoning patterns from reflection history."""

    _QUALITY_BANDS = {
        "excellent": (0.8, 1.0),
        "good": (0.6, 0.8),
        "fair": (0.4, 0.6),
        "poor": (0.0, 0.4),
    }
    _SEVERITY_BANDS = {
        "high": (0.7, 1.0),
        "medium": (0.4, 0.7),
        "low": (0.0, 0.4),
    }

    async def detect_patterns(self, limit: int = 200) -> list[PatternCluster]:
        """Load reflections, extract features, cluster, return clusters."""
        reflections = await self._load_reflections(limit)
        if not reflections:
            return []

        features_list = [self._extract_features(r) for r in reflections]
        groups = self._cluster_by_features(reflections, features_list)

        clusters = []
        for key, group_reflections in groups.items():
            group_features = [
                features_list[reflections.index(r)] for r in group_reflections
            ]
            cluster = self._build_cluster(key, group_reflections, group_features)
            clusters.append(cluster)

        # Find recurring patterns across all reflections
        recurring = self._find_recurring_patterns(reflections, features_list)
        if recurring:
            for cluster in clusters:
                cluster.patterns.extend([
                    p for p in recurring
                    if p.category == cluster.dominant_category
                ])

        return clusters

    async def _load_reflections(self, limit: int) -> list:
        try:
            async with async_session() as session:
                repo = ReflectionRepository(session)
                return await repo.get_history(limit=limit)
        except Exception as exc:
            logger.debug("Reflection load skipped: %s", exc)
            return []

    def _extract_features(self, reflection) -> dict:
        """Extract feature vector from a single reflection."""
        quality = reflection.reasoning_quality or 0.0
        quality_band = "poor"
        for band, (lo, hi) in self._QUALITY_BANDS.items():
            if lo <= quality < hi or (band == "excellent" and quality >= 0.8):
                quality_band = band
                break

        # Dominant issue category
        issues = reflection.audit_issues or []
        issue_cats = [i.get("category", "unknown") for i in issues if isinstance(i, dict)]
        dominant_issue = Counter(issue_cats).most_common(1)[0][0] if issue_cats else "none"

        # Hallucination level
        risk = reflection.hallucination_risk or 0.0
        hallucination_level = "low"
        for level, (lo, hi) in self._SEVERITY_BANDS.items():
            if lo <= risk < hi or (level == "high" and risk >= 0.7):
                hallucination_level = level
                break

        # Confidence direction
        conf_delta = 0.0
        if reflection.confidence_estimate and isinstance(reflection.confidence_estimate, dict):
            conf_delta = reflection.confidence_estimate.get("delta", 0.0) or 0.0

        return {
            "quality_band": quality_band,
            "dominant_issue_category": dominant_issue,
            "hallucination_level": hallucination_level,
            "confidence_direction": "positive" if conf_delta >= 0 else "negative",
            "has_improvements": bool(reflection.improvements),
            "issue_count": len(issues),
        }

    def _cluster_by_features(
        self, reflections: list, features_list: list[dict]
    ) -> dict[str, list]:
        """Group reflections by (quality_band, dominant_issue_category)."""
        groups: dict[str, list] = defaultdict(list)
        for r, f in zip(reflections, features_list):
            key = f"{f['quality_band']}_{f['dominant_issue_category']}"
            groups[key].append(r)
        return dict(groups)

    def _build_cluster(
        self, cluster_key: str, reflections: list, features_list: list[dict]
    ) -> PatternCluster:
        """Build a PatternCluster from a group of reflections."""
        qualities = [r.reasoning_quality or 0.0 for r in reflections]
        risks = [r.hallucination_risk or 0.0 for r in reflections]
        queries = [r.query[:100] for r in reflections[:3]]

        parts = cluster_key.split("_", 1)
        quality_band = parts[0] if parts else "unknown"
        issue_cat = parts[1] if len(parts) > 1 else "none"

        cluster = PatternCluster(
            cluster_id=self._stable_cluster_id(cluster_key),
            label=self._generate_cluster_label(quality_band, issue_cat),
            size=len(reflections),
            dominant_category=issue_cat,
            avg_quality=sum(qualities) / len(qualities) if qualities else 0.0,
            avg_hallucination_risk=sum(risks) / len(risks) if risks else 0.0,
            patterns=[],
        )
        cluster.recommendation = self._generate_recommendation(cluster)
        return cluster

    def _find_recurring_patterns(
        self, reflections: list, features_list: list[dict]
    ) -> list[ReasoningPattern]:
        """Find issue categories appearing in >20% of reflections."""
        total = len(reflections)
        if total < 5:
            return []

        cat_counts: dict[str, list[float]] = defaultdict(list)
        for r, f in zip(reflections, features_list):
            cat = f["dominant_issue_category"]
            if cat != "none":
                cat_counts[cat].append(r.reasoning_quality or 0.0)

        patterns = []
        for cat, qualities in cat_counts.items():
            freq = len(qualities)
            if freq / total > 0.2 and freq >= 2:
                patterns.append(ReasoningPattern(
                    pattern_type="recurring_issue",
                    category=cat,
                    frequency=freq,
                    avg_severity=sum(qualities) / len(qualities),
                    description=f"Issue '{cat}' appears in {freq}/{total} reflections",
                ))
        return patterns

    def _generate_cluster_label(self, quality_band: str, issue_category: str) -> str:
        labels = {
            "excellent": "High-quality",
            "good": "Good-quality",
            "fair": "Fair-quality",
            "poor": "Low-quality",
        }
        prefix = labels.get(quality_band, "Unknown-quality")
        if issue_category == "none":
            return f"{prefix} reasoning (no issues)"
        return f"{prefix} reasoning with {issue_category} issues"

    def _generate_recommendation(self, cluster: PatternCluster) -> str:
        if cluster.avg_hallucination_risk > 0.5:
            return f"High hallucination risk ({cluster.avg_hallucination_risk:.1%}) — consider adding more reliable sources"
        if cluster.avg_quality < 0.4:
            return f"Low reasoning quality ({cluster.avg_quality:.2f}) — consider breaking queries into sub-questions"
        if cluster.dominant_category == "unsupported":
            return "Frequent unsupported claims — improve citation enforcement"
        if cluster.dominant_category == "weak_reasoning":
            return "Weak reasoning patterns — strengthen logical connections"
        return "No critical issues detected in this cluster"

    def _stable_cluster_id(self, key: str) -> str:
        return hashlib.md5(key.encode()).hexdigest()[:16]

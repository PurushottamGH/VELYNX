"""Hallucination detection — identifies potential false information in answers."""
from __future__ import annotations

import logging
import re
from typing import Any

from backend.evaluation import HallucinationReport, HallucinationSignal

logger = logging.getLogger("uvicorn")

# Hedging words that indicate uncertainty
_HEDGE_WORDS = [
    "might", "may", "could", "possibly", "perhaps", "maybe",
    "it is believed", "some say", "arguably", "presumably",
    "allegedly", "reportedly", "supposedly",
]

# Definitive words that indicate high confidence
_DEFINITIVE_WORDS = [
    "definitely", "certainly", "absolutely", "always", "never",
    "undoubtedly", "without question", "proven fact",
    "guaranteed", "impossible",
]


class HallucinationDetector:
    """Detects potential hallucinations in query-answer pairs."""

    def analyze(
        self,
        query: str,
        answer: str,
        sources: list[dict[str, Any]] | None = None,
        confidence: str = "UNKNOWN",
        reasoning_quality: float = 0.5,
    ) -> HallucinationReport:
        """Analyze a query-answer pair for hallucination signals."""
        signals: list[HallucinationSignal] = []
        sources = sources or []

        # Signal 1: Unsupported claims (claims without source coverage)
        source_signals = self._check_source_coverage(answer, sources)
        signals.extend(source_signals)

        # Signal 2: Overconfidence (definitive language with low quality)
        conf_signals = self._check_overconfidence(answer, confidence, reasoning_quality)
        signals.extend(conf_signals)

        # Signal 3: Fabricated citations
        citation_signals = self._check_fabricated_citations(answer, sources)
        signals.extend(citation_signals)

        # Signal 4: Factual impossibility
        impossibility_signals = self._check_impossibility(query, answer)
        signals.extend(impossibility_signals)

        # Compute risk score
        risk_score = self._compute_risk_score(signals, reasoning_quality, confidence)

        # Source coverage
        source_coverage = self._compute_source_coverage(answer, sources)

        # Confidence reliability
        conf_reliability = self._compute_confidence_reliability(
            confidence, reasoning_quality, risk_score
        )

        return HallucinationReport(
            query=query[:200],
            answer=answer[:500],
            risk_score=round(risk_score, 3),
            signals=signals,
            source_coverage=round(source_coverage, 3),
            confidence_reliability=round(conf_reliability, 3),
        )

    def _check_source_coverage(
        self, answer: str, sources: list[dict]
    ) -> list[HallucinationSignal]:
        """Check if answer claims have source support."""
        signals: list[HallucinationSignal] = []

        if not sources and len(answer) > 50:
            signals.append(HallucinationSignal(
                signal_type="unsupported_claim",
                severity=0.6,
                description="Answer has substantial content but no sources",
                evidence=f"Answer length: {len(answer)} chars, sources: 0",
            ))

        # Check for citation markers
        has_citations = bool(re.search(r'\[\d+\]', answer))
        if sources and not has_citations and len(answer) > 100:
            signals.append(HallucinationSignal(
                signal_type="unsupported_claim",
                severity=0.3,
                description="Sources available but not cited in answer",
                evidence=f"{len(sources)} sources available, no citation markers",
            ))

        return signals

    def _check_overconfidence(
        self, answer: str, confidence: str, reasoning_quality: float
    ) -> list[HallucinationSignal]:
        """Check for overconfident language given quality."""
        signals: list[HallucinationSignal] = []

        answer_lower = answer.lower()
        definitive_count = sum(1 for w in _DEFINITIVE_WORDS if w in answer_lower)

        # High confidence with low quality
        if confidence in ("CERTAIN", "PROBABLE") and reasoning_quality < 0.4:
            signals.append(HallucinationSignal(
                signal_type="overconfidence",
                severity=0.5,
                description=f"Confidence '{confidence}' but reasoning quality is low ({reasoning_quality:.2f})",
            ))

        # Definitive language with poor quality
        if definitive_count >= 2 and reasoning_quality < 0.5:
            signals.append(HallucinationSignal(
                signal_type="overconfidence",
                severity=0.4,
                description=f"Definitive language ({definitive_count} instances) with low quality",
            ))

        return signals

    def _check_fabricated_citations(
        self, answer: str, sources: list[dict]
    ) -> list[HallucinationSignal]:
        """Check for citations that don't match available sources."""
        signals: list[HallucinationSignal] = []

        # Find citation numbers in answer
        citations = re.findall(r'\[(\d+)\]', answer)
        if not citations:
            return signals

        # Check if citation numbers exceed source count
        max_citation = max((int(c) for c in citations), default=0)
        if max_citation > len(sources):
            signals.append(HallucinationSignal(
                signal_type="source_mismatch",
                severity=0.7,
                description=f"Citation [{max_citation}] exceeds available sources ({len(sources)})",
                evidence=f"Citations found: {citations}",
            ))

        return signals

    def _check_impossibility(
        self, query: str, answer: str
    ) -> list[HallucinationSignal]:
        """Check for factual impossibility signals."""
        signals: list[HallucinationSignal] = []

        query_lower = query.lower()
        answer_lower = answer.lower()

        # Check if answer acknowledges impossibility
        acknowledges = any(phrase in answer_lower for phrase in [
            "does not exist", "did not exist", "never existed",
            "fictional", "mythical", "not a real",
            "cannot predict", "impossible to know",
            "no evidence", "no credible",
        ])

        # Queries about non-existent things
        non_exist = any(phrase in query_lower for phrase in [
            "atlantis", "unicorn", "dragon", "santa claus",
            "tooth fairy", "easter bunny",
        ])

        if non_exist and not acknowledges:
            signals.append(HallucinationSignal(
                signal_type="factual_error",
                severity=0.5,
                description="Query about fictional entity but answer does not acknowledge non-existence",
            ))

        return signals

    def _compute_risk_score(
        self,
        signals: list[HallucinationSignal],
        reasoning_quality: float,
        confidence: str,
    ) -> float:
        """Compute overall hallucination risk score."""
        if not signals:
            return max(0.0, 0.3 - reasoning_quality * 0.2)

        # Base risk from signals
        signal_risk = sum(s.severity for s in signals) / len(signals)

        # Adjust for reasoning quality
        quality_factor = 1.0 - reasoning_quality * 0.5

        return min(1.0, signal_risk * quality_factor)

    def _compute_source_coverage(
        self, answer: str, sources: list[dict]
    ) -> float:
        """Compute fraction of answer that has source support."""
        if not sources:
            return 0.0
        if not answer:
            return 1.0

        # Simple heuristic: if citations exist, good coverage
        has_citations = bool(re.search(r'\[\d+\]', answer))
        if has_citations:
            citation_count = len(re.findall(r'\[\d+\]', answer))
            return min(1.0, citation_count / max(1, len(answer.split('.')) - 1))

        # If sources exist but no citations, partial coverage
        return 0.3

    def _compute_confidence_reliability(
        self, confidence: str, reasoning_quality: float, risk_score: float
    ) -> float:
        """Compute how reliable the confidence level is."""
        conf_values = {
            "CERTAIN": 0.9, "PROBABLE": 0.7, "DEBATED": 0.5,
            "LOW": 0.3, "UNKNOWN": 0.1,
        }
        expected = conf_values.get(confidence, 0.1)

        # Reliability is how close confidence is to quality
        quality_match = 1.0 - abs(expected - reasoning_quality)

        # Penalize for risk
        risk_penalty = risk_score * 0.3

        return max(0.0, quality_match - risk_penalty)


# Module-level singleton
hallucination_detector = HallucinationDetector()

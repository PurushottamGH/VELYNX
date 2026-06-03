"""Confidence estimator — recalibrates confidence based on reasoning quality signals."""
from __future__ import annotations

from reflection import ConfidenceEstimate

_CONFIDENCE_LEVELS = ["CERTAIN", "PROBABLE", "DEBATED", "LOW", "UNKNOWN"]
_CONFIDENCE_VALUES = {"CERTAIN": 0.9, "PROBABLE": 0.7, "DEBATED": 0.5, "LOW": 0.3, "UNKNOWN": 0.1}


def estimate_confidence(
    answer: str,
    sources: list[dict],
    reasoning_content: str = "",
    initial_confidence: str = "UNKNOWN",
) -> ConfidenceEstimate:
    """Recalibrate confidence based on answer quality signals."""
    initial_value = _CONFIDENCE_VALUES.get(initial_confidence.upper(), 0.1)
    delta = 0.0
    reasons: list[str] = []

    # Source count signal
    source_count = len(sources)
    if source_count >= 3:
        delta += 0.05
        reasons.append(f"Good source count ({source_count})")
    elif source_count == 0:
        delta -= 0.2
        reasons.append("No sources — confidence reduced")

    # Citation presence
    has_citations = any(f"[{i}]" in answer or f"[{i+1}]" in answer for i in range(5))
    if has_citations:
        delta += 0.05
        reasons.append("Answer cites sources")
    elif source_count > 0:
        delta -= 0.05
        reasons.append("Sources available but not cited")

    # Answer specificity (length as proxy)
    if len(answer) > 200:
        delta += 0.03
        reasons.append("Detailed answer")
    elif len(answer) < 50:
        delta -= 0.1
        reasons.append("Very short answer — reduced confidence")

    # Reasoning content present
    if reasoning_content and len(reasoning_content) > 50:
        delta += 0.05
        reasons.append("Reasoning trace available")
    elif not reasoning_content:
        delta -= 0.05
        reasons.append("No reasoning trace")

    # Source quality (average score)
    if sources:
        avg_score = sum(s.get("score", 0) for s in sources) / len(sources)
        if avg_score >= 0.7:
            delta += 0.05
            reasons.append("High-quality sources")
        elif avg_score < 0.3:
            delta -= 0.1
            reasons.append("Low-quality sources")

    # Apply delta and clamp
    calibrated_value = max(0.0, min(1.0, initial_value + delta))

    # Map back to confidence level
    if calibrated_value >= 0.8:
        calibrated = "CERTAIN"
    elif calibrated_value >= 0.6:
        calibrated = "PROBABLE"
    elif calibrated_value >= 0.4:
        calibrated = "DEBATED"
    elif calibrated_value >= 0.2:
        calibrated = "LOW"
    else:
        calibrated = "UNKNOWN"

    return ConfidenceEstimate(
        initial=initial_confidence.upper(),
        calibrated=calibrated,
        calibration_delta=round(delta, 3),
        rationale="; ".join(reasons) if reasons else "No signals available",
    )

"""Reflection engine — metacognitive analysis of reasoning quality."""
from __future__ import annotations

from pydantic import BaseModel, Field


class AuditIssue(BaseModel):
    """A single issue detected in reasoning."""
    category: str  # "contradiction", "hallucination", "weak_reasoning", "repetitive", "unsupported"
    severity: float  # 0.0-1.0
    description: str
    evidence: str = ""


class AuditResult(BaseModel):
    """Result of reasoning audit."""
    issues: list[AuditIssue] = Field(default_factory=list)
    overall_quality: float = 0.5  # 0.0-1.0
    hallucination_risk: float = 0.0  # 0.0-1.0
    reasoning_coherence: float = 0.5  # 0.0-1.0


class ConfidenceEstimate(BaseModel):
    """Calibrated confidence assessment."""
    initial: str = "UNKNOWN"
    calibrated: str = "UNKNOWN"
    calibration_delta: float = 0.0  # positive = more confident
    rationale: str = ""


class ImprovementSuggestion(BaseModel):
    """Actionable improvement suggestion."""
    category: str  # "sources", "reasoning", "confidence", "memory"
    priority: int = 5  # 1-10
    description: str
    actionable: bool = True


class ReflectionResult(BaseModel):
    """Complete reflection output."""
    audit: AuditResult = Field(default_factory=AuditResult)
    confidence_estimate: ConfidenceEstimate = Field(default_factory=ConfidenceEstimate)
    improvements: list[ImprovementSuggestion] = Field(default_factory=list)
    memory_priority: float = 0.5  # how important to store this reflection
    reasoning_quality: float = 0.5  # overall 0.0-1.0

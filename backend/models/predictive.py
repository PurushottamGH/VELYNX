"""
Phase 50 — Predictive Processing models.
ConceptState, TransitionRule, PredictionLog.
Separate from epistemic belief (living_edges).
"""

from pydantic import BaseModel, Field


class ConceptState(BaseModel):
    """The predictive-activation state of a single concept token."""
    concept: str
    activation: float = Field(default=0.5, ge=0.0, le=1.0)
    baseline: float = Field(default=0.5, ge=0.0, le=1.0)
    state_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    source: str = "unknown"
    evidence_count: int = 0


class TransitionRule(BaseModel):
    """A directional predictive rule: source → target with learned effect and decay."""
    source_concept: str
    target_concept: str
    effect: float = Field(default=0.0, ge=-1.0, le=1.0)
    rule_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    decay: float = Field(default=0.001, ge=0.0)
    source: str = "unknown"


class PredictionLog(BaseModel):
    """Immutable record of a single prediction cycle."""
    id: int | None = None
    source_concepts: str       # JSON list of concept names
    target_concept: str
    predicted_activation: float
    observed_activation: float | None = None
    signed_error: float | None = None
    rule_effect_before: float
    rule_effect_after: float | None = None
    timestamp: str = ""

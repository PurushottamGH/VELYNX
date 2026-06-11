from pydantic import BaseModel

from backend.models.source import Source


class AnswerResponse(BaseModel):
    query: str
    answer: str
    confidence: str
    sources: list[Source]
    contradictions: list[str]
    gaps: list[str]
    citations: list[str]
    tone: str
    debug: dict | None = None
    dialogue_act: str | None = None
    clarification_needed: bool = False
    resonance_scores: dict[str, float] = {}
    epistemic_states: dict[str, str] = {}
    recalled_memory: dict | None = None

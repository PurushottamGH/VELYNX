from pydantic import BaseModel

from models.source import Source


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

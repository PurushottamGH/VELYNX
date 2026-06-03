"""
VELYNX Phases 24-27
====================
Phase 24: Curiosity Engine — VELYNX generates its own questions
Phase 25: Contradiction Resolver — resolves conflicting knowledge
Phase 26: Human Understanding Mode — explains like a brilliant friend
Phase 27: Self-Knowledge — VELYNX knows what it knows and doesn't
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger("velynx.cognition")

_DATA_DIR = Path(os.getenv("VELYNX_DATA_DIR", ".")) / "velynx_data" / "cognition"
_DATA_DIR.mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 24 — CURIOSITY ENGINE
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class CuriosityQuestion:
    question: str
    about_concept: str
    domain: str
    priority: float
    reason: str
    generated_at: float = field(default_factory=time.time)
    answered: bool = False


class CuriosityEngine:
    def __init__(self):
        self._queue: list[CuriosityQuestion] = []
        self._answered: list[CuriosityQuestion] = []
        self._load()

    def generate_questions(self, concept_name: str, understanding) -> list[CuriosityQuestion]:
        questions = []
        domain = understanding.domain if understanding else "general"

        if understanding and understanding.open_questions:
            for oq in understanding.open_questions[:2]:
                questions.append(CuriosityQuestion(question=oq, about_concept=concept_name,
                    domain=domain, priority=0.8, reason=f"Open question from {concept_name}"))

        if understanding and understanding.connects_to:
            for related in understanding.connects_to[:5]:
                questions.append(CuriosityQuestion(
                    question=f"What is {related} and how does it relate to {concept_name}?",
                    about_concept=related, domain=domain, priority=0.6,
                    reason=f"{related} mentioned while learning {concept_name}"))

        if understanding and understanding.completeness < 0.6:
            questions.append(CuriosityQuestion(
                question=f"How exactly does {concept_name} work at a deeper level?",
                about_concept=concept_name, domain=domain, priority=0.9,
                reason=f"{concept_name} understanding is shallow"))

        for q in questions:
            if not any(existing.question == q.question for existing in self._queue):
                self._queue.append(q)
        self._queue.sort(key=lambda x: x.priority, reverse=True)
        self._queue = self._queue[:100]
        self._save()
        return questions

    def get_next(self) -> Optional[CuriosityQuestion]:
        for q in self._queue:
            if not q.answered:
                return q
        return None

    def get_learning_targets(self, n: int = 5) -> list[str]:
        return [q.about_concept for q in self._queue if not q.answered][:n]

    def mark_answered(self, question: str):
        for q in self._queue:
            if q.question == question:
                q.answered = True
                self._answered.append(q)
        self._save()

    def stats(self) -> dict:
        unanswered = [q for q in self._queue if not q.answered]
        return {"total_generated": len(self._queue) + len(self._answered),
                "pending": len(unanswered), "answered": len(self._answered),
                "top_priority": unanswered[0].question if unanswered else None}

    def _save(self):
        try:
            data = {"queue": [asdict(q) for q in self._queue[-50:]],
                    "answered": [asdict(q) for q in self._answered[-50:]]}
            (_DATA_DIR / "curiosity.json").write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    def _load(self):
        try:
            f = _DATA_DIR / "curiosity.json"
            if f.exists():
                data = json.loads(f.read_text())
                self._queue = [CuriosityQuestion(**q) for q in data.get("queue", [])]
                self._answered = [CuriosityQuestion(**q) for q in data.get("answered", [])]
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 25 — CONTRADICTION RESOLVER
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Contradiction:
    concept: str
    claim_a: str
    claim_b: str
    source_a: str
    source_b: str
    resolution: str = ""
    resolved: bool = False
    confidence: float = 0.0
    detected_at: float = field(default_factory=time.time)


class ContradictionResolver:
    def __init__(self):
        self._contradictions: list[Contradiction] = []
        self._load()

    def detect(self, concept: str, sources: list[dict]) -> list[Contradiction]:
        contradictions = []
        texts = [(s.get("snippet") or s.get("content") or "", s.get("url", ""), s.get("source", "")) for s in sources if s.get("snippet") or s.get("content")]
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                text_a, url_a, src_a = texts[i]
                text_b, url_b, src_b = texts[j]
                conflict = self._find_conflict(text_a, text_b)
                if conflict:
                    claim_a, claim_b = conflict
                    c = Contradiction(concept=concept, claim_a=claim_a, claim_b=claim_b,
                        source_a=url_a, source_b=url_b)
                    c = self._resolve(c)
                    contradictions.append(c)
                    self._contradictions.append(c)
        self._save()
        return contradictions

    def _find_conflict(self, text_a: str, text_b: str) -> Optional[tuple[str, str]]:
        nums_a = re.findall(r"\b\d+(?:\.\d+)?\s*(?:billion|million|thousand|km|m|kg)\b", text_a, re.IGNORECASE)
        nums_b = re.findall(r"\b\d+(?:\.\d+)?\s*(?:billion|million|thousand|km|m|kg)\b", text_b, re.IGNORECASE)
        if nums_a and nums_b and nums_a[0] != nums_b[0]:
            sents_a = [s for s in text_a.split(".") if nums_a[0] in s]
            sents_b = [s for s in text_b.split(".") if nums_b[0] in s]
            if sents_a and sents_b:
                return sents_a[0].strip(), sents_b[0].strip()
        return None

    def _resolve(self, c: Contradiction) -> Contradiction:
        if any(w in c.claim_a.lower() for w in ["billion", "million", "age", "distance"]):
            c.resolution = "Likely reflects measurement uncertainty. The most recent peer-reviewed value is typically most reliable."
            c.resolved = True
            c.confidence = 0.7
        elif any(w in c.claim_a.lower() for w in ["temperature", "pressure"]):
            c.resolution = "Both claims may be correct in different contexts — different scales or conditions."
            c.resolved = True
            c.confidence = 0.65
        else:
            c.resolution = "Contradiction detected but not yet resolved. May be genuinely debated or context-dependent."
            c.resolved = False
            c.confidence = 0.30
        return c

    def get_unresolved(self) -> list[Contradiction]:
        return [c for c in self._contradictions if not c.resolved]

    def stats(self) -> dict:
        return {"total_detected": len(self._contradictions),
                "resolved": sum(1 for c in self._contradictions if c.resolved),
                "unresolved": sum(1 for c in self._contradictions if not c.resolved)}

    def _save(self):
        try:
            (_DATA_DIR / "contradictions.json").write_text(json.dumps([asdict(c) for c in self._contradictions[-100:]], indent=2))
        except Exception:
            pass

    def _load(self):
        try:
            f = _DATA_DIR / "contradictions.json"
            if f.exists():
                self._contradictions = [Contradiction(**c) for c in json.loads(f.read_text())]
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 26 — HUMAN UNDERSTANDING MODE
# ══════════════════════════════════════════════════════════════════════════════

class HumanUnderstandingMode:
    def explain(self, concept_name: str, understanding, query: str) -> str:
        if not understanding:
            return ""
        parts = []
        if understanding.human_meaning:
            parts.append(understanding.human_meaning)
        elif understanding.what:
            parts.append(self._humanize(understanding.what))
        if understanding.how:
            sentences = re.split(r"(?<=[.!?])\s+", understanding.how)
            parts.append(" ".join(sentences[:2]))
        if understanding.so_what:
            if not understanding.so_what.lower().startswith("this"):
                parts.append(f"This matters because {understanding.so_what[0].lower()}{understanding.so_what[1:]}")
            else:
                parts.append(understanding.so_what)
        if understanding.open_questions:
            parts.append(f"Interestingly, {understanding.open_questions[0].lower()}")
        return " ".join(p for p in parts[:4] if p).strip()

    def _humanize(self, text: str) -> str:
        replacements = {"is defined as": "is basically", "refers to the": "is the",
                       "constitutes a": "is a", "is characterized by": "works through"}
        result = text
        for old, new in replacements.items():
            result = result.replace(old, new)
        return result


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 27 — SELF-KNOWLEDGE
# ══════════════════════════════════════════════════════════════════════════════

class SelfKnowledge:
    def assess(self, query: str, concept=None) -> dict:
        if concept is None:
            return {"knows": False, "confidence": "UNKNOWN", "depth": "NONE",
                    "completeness": 0.0, "state": "none",
                    "honest_response": "I don't yet have this in my knowledge base. Searching live sources...",
                    "should_search": True, "gaps": []}

        completeness = concept.completeness
        confidence = concept.confidence
        depth = concept.depth_label

        if completeness >= 0.8 and confidence >= 0.8:
            state = "deep"
            honest = f"I have deep understanding of this. {concept.best_answer_for(query)}"
            should_search = False
        elif completeness >= 0.5:
            state = "partial"
            gaps = concept.open_questions[:1]
            gap_text = f" I'm less certain about: {gaps[0]}" if gaps else ""
            honest = f"I have partial understanding here. {concept.best_answer_for(query)}{gap_text}"
            should_search = True
        elif completeness >= 0.2:
            state = "surface"
            honest = f"My understanding is surface-level. {concept.what or concept.how} I'd recommend verifying with additional sources."
            should_search = True
        else:
            state = "minimal"
            honest = f"I have minimal understanding of {concept.concept}. Let me search for more."
            should_search = True

        return {"knows": completeness > 0.2, "confidence": self._float_to_label(confidence),
                "depth": depth, "completeness": round(completeness, 2), "state": state,
                "honest_response": honest, "should_search": should_search,
                "gaps": concept.open_questions[:2] if concept else []}

    def _float_to_label(self, f: float) -> str:
        if f >= 0.85: return "CERTAIN"
        if f >= 0.65: return "PROBABLE"
        if f >= 0.40: return "DEBATED"
        return "LOW"


# ══════════════════════════════════════════════════════════════════════════════
# COORDINATOR
# ══════════════════════════════════════════════════════════════════════════════

class CognitionCoordinator:
    def __init__(self):
        self.curiosity = CuriosityEngine()
        self.contradictions = ContradictionResolver()
        self.human_mode = HumanUnderstandingMode()
        self.self_knowledge = SelfKnowledge()

    def after_learning(self, concept_name: str, understanding, sources: list[dict]):
        new_questions = self.curiosity.generate_questions(concept_name, understanding)
        if len(sources) > 1:
            self.contradictions.detect(concept_name, sources)
        return {"new_curiosity_questions": len(new_questions),
                "next_to_explore": self.curiosity.get_learning_targets(3)}

    def get_honest_answer(self, query: str, concept=None) -> dict:
        assessment = self.self_knowledge.assess(query, concept)
        if concept and assessment["state"] in ("deep", "solid"):
            human_explanation = self.human_mode.explain(concept.concept, concept, query)
            if human_explanation:
                assessment["human_explanation"] = human_explanation
        return assessment

    def get_status(self) -> dict:
        return {"curiosity": self.curiosity.stats(), "contradictions": self.contradictions.stats()}


curiosity_engine = CuriosityEngine()
contradiction_resolver = ContradictionResolver()
human_mode = HumanUnderstandingMode()
self_knowledge = SelfKnowledge()
cognition_coordinator = CognitionCoordinator()

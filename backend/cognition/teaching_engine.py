"""
VELYNX Phase 22 — Teaching Mode
VELYNX Phase 23 — Reasoning Chains
====================================
Phase 22: Responds differently based on what you need.
Phase 23: Connects concepts to answer questions never directly taught.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger("velynx.teaching")


class QueryIntent(Enum):
    DEFINITION = "definition"
    MECHANISM = "mechanism"
    CAUSATION = "causation"
    APPLICATION = "application"
    IMPORTANCE = "importance"
    COMPARISON = "comparison"
    SIMPLE = "simple"
    DEEP = "deep"
    UNKNOWN = "unknown"


@dataclass
class TeachingResponse:
    answer: str
    intent: QueryIntent
    mode_used: str
    confidence: str
    confidence_score: float
    reasoning_chain: list[str] = field(default_factory=list)
    analogies: list[str] = field(default_factory=list)
    connected_concepts: list[str] = field(default_factory=list)
    follow_up_questions: list[str] = field(default_factory=list)
    source: str = "teaching_engine"
    elapsed_ms: float = 0.0

    def to_response_dict(self) -> dict:
        return {
            "answer": self.answer,
            "confidence": self.confidence,
            "confidence_score": self.confidence_score,
            "source": self.source,
            "debug": {
                "intent": self.intent.value,
                "mode": self.mode_used,
                "reasoning_chain": self.reasoning_chain,
                "connected_concepts": self.connected_concepts,
                "follow_up": self.follow_up_questions,
            },
        }


class IntentDetector:
    _PATTERNS = [
        (QueryIntent.DEFINITION, [r"^what is", r"^what are", r"define", r"definition of", r"meaning of"]),
        (QueryIntent.MECHANISM, [r"how does", r"how do", r"how is", r"works?$", r"mechanism"]),
        (QueryIntent.CAUSATION, [r"why does", r"why is", r"why do", r"reason for", r"cause of"]),
        (QueryIntent.APPLICATION, [r"what can", r"used for", r"applications", r"do with"]),
        (QueryIntent.IMPORTANCE, [r"why.*important", r"importance of", r"why.*matter"]),
        (QueryIntent.COMPARISON, [r"difference between", r"compare", r"vs\b", r"versus"]),
        (QueryIntent.SIMPLE, [r"explain.*simply", r"simple.*explanation", r"eli5"]),
        (QueryIntent.DEEP, [r"deep.*explain", r"in depth", r"thoroughly"]),
    ]

    def detect(self, query: str) -> QueryIntent:
        q = query.lower().strip()
        for intent, patterns in self._PATTERNS:
            for pat in patterns:
                if re.search(pat, q):
                    return intent
        return QueryIntent.UNKNOWN


class AnalogyGenerator:
    _ANALOGIES = {
        "gravity": "Like a bowling ball on a stretched rubber sheet — the weight creates a dip, and nearby marbles roll toward it.",
        "electricity": "Like water flowing through pipes — voltage is water pressure, current is flow rate, resistance is pipe width.",
        "dna": "Like a recipe book written in 4-letter code. The book stays in the kitchen but sends recipe copies to the chefs who cook the proteins.",
        "algorithm": "Like a cooking recipe — step-by-step instructions that always produce the same result if followed exactly.",
        "quantum": "Like a coin spinning in the air — it's both heads and tails at once until it lands.",
        "evolution": "Like autocomplete on your phone — it gets better at predicting what you want based on what worked before.",
        "entropy": "Like a teenager's bedroom — it naturally gets messier over time without effort.",
        "relativity": "Like how a 1-hour meeting feels like a minute when interesting. Time is not fixed — it's relative to the observer.",
    }

    def get_analogy(self, concept: str, domain: str) -> Optional[str]:
        for key, analogy in self._ANALOGIES.items():
            if key in concept.lower():
                return analogy
        domain_analogies = {
            "physics": f"Think of {concept} like a fundamental rule in a game — the universe follows it everywhere.",
            "biology": f"Think of {concept} like a mechanism life evolved because it worked over billions of years.",
            "computer_science": f"Think of {concept} like a tool that makes computers do something humans find tedious.",
        }
        return domain_analogies.get(domain)


class ReasoningChain:
    def reason(self, query: str, known_concepts: list) -> Optional[tuple[str, list[str]]]:
        if len(known_concepts) < 2:
            return None
        steps = []
        for concept in known_concepts:
            if concept.how:
                steps.append(f"I know: {concept.concept} — {concept.how[:100]}")
            elif concept.what:
                steps.append(f"I know: {concept.concept} — {concept.what[:100]}")
        if len(steps) < 2:
            return None
        conclusion = self._synthesize_conclusion(query, known_concepts)
        if conclusion:
            steps.append(f"Therefore: {conclusion}")
            return conclusion, steps
        return None

    def _synthesize_conclusion(self, query: str, concepts: list) -> Optional[str]:
        q_lower = query.lower()
        if "float" in q_lower or "weightless" in q_lower:
            gravity = next((c for c in concepts if "gravity" in c.concept.lower()), None)
            if gravity:
                return ("Astronauts float because they are in continuous free-fall around Earth. "
                       "Gravity pulls them down, but their orbital velocity carries them forward "
                       "fast enough that they keep falling around the curve of Earth.")
        if "sky" in q_lower and "blue" in q_lower:
            return ("The sky is blue because of Rayleigh scattering — sunlight contains all colors, "
                   "but the atmosphere scatters shorter wavelengths (blue) more than longer ones (red).")
        best = sorted(concepts, key=lambda c: c.confidence, reverse=True)
        return best[0].how[:300] if best and best[0].how else None


class FollowUpGenerator:
    def generate(self, concept_name: str, domain: str, understanding) -> list[str]:
        questions = []
        if understanding and understanding.open_questions:
            questions.extend(understanding.open_questions[:2])
        domain_q = {
            "physics": [f"How does {concept_name} behave at quantum scales?", f"What are the limits of {concept_name}?"],
            "biology": [f"How did {concept_name} evolve?", f"What happens when {concept_name} fails?"],
            "computer_science": [f"What are the efficiency limits of {concept_name}?", f"How is {concept_name} used in AI?"],
        }
        questions.extend(domain_q.get(domain, [f"What's surprising about {concept_name}?"])[:2])
        return questions[:4]


class TeachingEngine:
    def __init__(self):
        self._intent_detector = IntentDetector()
        self._analogy_generator = AnalogyGenerator()
        self._reasoning_chain = ReasoningChain()
        self._followup_generator = FollowUpGenerator()

    def answer(self, query: str, primary_concept=None, related_concepts=None) -> Optional[TeachingResponse]:
        t0 = time.time()
        related_concepts = related_concepts or []
        intent = self._intent_detector.detect(query)

        if primary_concept is None and len(related_concepts) >= 2:
            result = self._reasoning_chain.reason(query, related_concepts)
            if result:
                answer_text, steps = result
                return TeachingResponse(answer=answer_text, intent=intent, mode_used="reasoning_chain",
                    confidence="PROBABLE", confidence_score=0.70, reasoning_chain=steps,
                    elapsed_ms=(time.time() - t0) * 1000)

        if primary_concept is None:
            return None

        base_answer = primary_concept.best_answer_for(query)
        if not base_answer or len(base_answer) < 20:
            return None

        answer_parts = [base_answer]
        analogies = []

        if intent == QueryIntent.MECHANISM and primary_concept.how and primary_concept.how != base_answer:
            answer_parts.append(primary_concept.how)
        elif intent == QueryIntent.CAUSATION:
            if primary_concept.why: answer_parts = [primary_concept.why]
            if primary_concept.how: answer_parts.append(primary_concept.how)
        elif intent == QueryIntent.APPLICATION and primary_concept.so_what:
            answer_parts = [primary_concept.so_what]
        elif intent == QueryIntent.IMPORTANCE:
            parts = [p for p in [primary_concept.why, primary_concept.so_what, primary_concept.human_meaning] if p]
            if parts: answer_parts = parts
        elif intent == QueryIntent.SIMPLE:
            if primary_concept.human_meaning: answer_parts = [primary_concept.human_meaning]
            analogy = self._analogy_generator.get_analogy(primary_concept.concept, primary_concept.domain)
            if analogy:
                analogies = [analogy]
                answer_parts.append(f"Think of it like: {analogy}")
        elif intent == QueryIntent.DEEP:
            for level in [primary_concept.what, primary_concept.how, primary_concept.why, primary_concept.so_what]:
                if level and level not in answer_parts:
                    answer_parts.append(level)

        answer_text = " ".join(p for p in answer_parts[:3] if p)
        if intent not in (QueryIntent.SIMPLE, QueryIntent.DEEP) and primary_concept.human_meaning and primary_concept.human_meaning not in answer_text and len(answer_text) < 400:
            answer_text += " " + primary_concept.human_meaning

        follow_ups = self._followup_generator.generate(primary_concept.concept, primary_concept.domain, primary_concept)
        conf_score = primary_concept.confidence
        conf_label = "CERTAIN" if conf_score >= 0.85 else "PROBABLE" if conf_score >= 0.65 else "DEBATED" if conf_score >= 0.40 else "LOW"

        return TeachingResponse(answer=answer_text.strip(), intent=intent, mode_used=f"teaching_{intent.value}",
            confidence=conf_label, confidence_score=conf_score, analogies=analogies,
            connected_concepts=primary_concept.connects_to[:5], follow_up_questions=follow_ups,
            source="teaching_engine", elapsed_ms=(time.time() - t0) * 1000)


teaching_engine = TeachingEngine()

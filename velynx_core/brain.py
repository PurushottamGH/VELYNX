"""
VELYNX CORE v2 — brain.py
Graph-native reasoning engine.
Traverses concept chains rather than string-matching text.
Produces structured answers with WHY / HOW / SO_WHAT layers.
No external LLM dependency — pure local reasoning from stored knowledge.
"""

import re
import time
import logging
from dataclasses import dataclass, field
from typing import Optional
from .memory import VelynxMemory, Concept, RetrievedConcept

logger = logging.getLogger("velynx.brain")


# ── Answer structure ─────────────────────────────────────────────────────────

@dataclass
class ReasoningStep:
    step: int
    operation: str       # RETRIEVE / TRAVERSE / SYNTHESIZE / VERIFY / CONCLUDE
    input_: str
    output: str
    confidence: float
    latency_ms: float


@dataclass
class VelynxAnswer:
    query: str
    answer: str
    what: str            # direct definition / description
    why: str             # causal / motivational layer
    how: str             # mechanism / process layer
    so_what: str         # implication / consequence layer
    confidence: float
    reasoning_chain: list[ReasoningStep]
    sources: list[str]
    concepts_used: list[str]
    latency_ms: float
    from_graph: bool     # True = answered from knowledge graph; False = synthesized


# ── Intent detection ─────────────────────────────────────────────────────────

INTENT_PATTERNS = {
    "what":    [r"\bwhat\s+is\b", r"\bdefine\b", r"\bexplain\b", r"\bdescribe\b"],
    "why":     [r"\bwhy\b", r"\bcause\b", r"\breason\b", r"\bmotive\b"],
    "how":     [r"\bhow\b", r"\bprocess\b", r"\bstep\b", r"\bmechanism\b", r"\bwork\b"],
    "compare": [r"\bversus\b", r"\bvs\b", r"\bdifference\b", r"\bcompare\b"],
    "effect":  [r"\beffect\b", r"\bimpact\b", r"\bconsequence\b", r"\bresult\b"],
}

def detect_intent(query: str) -> list[str]:
    q = query.lower()
    intents = []
    for intent, patterns in INTENT_PATTERNS.items():
        if any(re.search(p, q) for p in patterns):
            intents.append(intent)
    return intents if intents else ["what"]


# ── Query decomposition ───────────────────────────────────────────────────────

STOPWORDS = {
    "what","is","are","the","a","an","how","why","does","do","in","on","of",
    "to","for","and","or","but","with","explain","describe","tell","me","about"
}

def extract_concepts(query: str) -> list[str]:
    """Pull candidate concept names from the query string."""
    tokens = re.sub(r"[^\w\s]", " ", query.lower()).split()
    # single important words
    keywords = [t for t in tokens if t not in STOPWORDS and len(t) > 2]
    # bigrams
    bigrams = [f"{tokens[i]} {tokens[i+1]}"
               for i in range(len(tokens)-1)
               if tokens[i] not in STOPWORDS and tokens[i+1] not in STOPWORDS]
    # trigrams
    trigrams = [f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}"
                for i in range(len(tokens)-2)
                if tokens[i] not in STOPWORDS]
    # longest first so we match "black hole" before "hole"
    candidates = trigrams + bigrams + keywords
    seen, unique = set(), []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique


# ── Synthesis helpers ────────────────────────────────────────────────────────

def _merge_field(concepts: list[Concept], field: str, max_len: int = 400) -> str:
    parts = []
    for c in concepts:
        val = getattr(c, field, "").strip()
        if val and val not in parts:
            parts.append(val)
    combined = " ".join(parts)
    return combined[:max_len] if len(combined) > max_len else combined


def _weighted_confidence(concepts: list[Concept]) -> float:
    if not concepts:
        return 0.0
    # weight by access_count (more accessed = more validated)
    total_weight = sum(max(c.access_count, 1) for c in concepts)
    weighted = sum(c.confidence * max(c.access_count, 1) for c in concepts)
    return round(weighted / total_weight, 3)


def _format_comparison(a: Concept, b: Concept) -> str:
    lines = [
        f"{'Aspect':<20} {'▸ ' + a.name:<35} {'▸ ' + b.name}",
        "-" * 80,
        f"{'WHAT':<20} {a.what[:32]:<35} {b.what[:32]}",
        f"{'WHY':<20} {a.why[:32]:<35} {b.why[:32]}",
        f"{'HOW':<20} {a.how[:32]:<35} {b.how[:32]}",
        f"{'CONFIDENCE':<20} {a.confidence:<35} {b.confidence}",
    ]
    return "\n".join(lines)


# ── VelynxBrain ──────────────────────────────────────────────────────────────

class VelynxBrain:
    """
    Graph-native reasoning over VelynxMemory.
    Does NOT call any external LLM.
    Chains: retrieve → traverse → synthesize → verify → conclude.
    """

    def __init__(self, memory: VelynxMemory):
        self.memory = memory
        self.min_confidence_threshold = 0.35

    def reason(self, query: str) -> VelynxAnswer:
        t0 = time.time()
        chain: list[ReasoningStep] = []
        step = 0

        # ── Step 1: Intent + concept extraction ──────────────────────────
        intents = detect_intent(query)
        candidates = extract_concepts(query)
        step += 1
        chain.append(ReasoningStep(
            step=step, operation="RETRIEVE",
            input_=query,
            output=f"intents={intents}, candidates={candidates[:5]}",
            confidence=1.0, latency_ms=0
        ))

        # ── Step 2: Retrieve matching concepts ───────────────────────────
        t_r = time.time()
        matched: list[Concept] = []
        seen_ids: set[str] = set()

        for candidate in candidates:
            c = self.memory.find_concept(candidate)
            if c and c.id not in seen_ids and c.confidence >= self.min_confidence_threshold:
                matched.append(c)
                seen_ids.add(c.id)
            if len(matched) >= 6:
                break

        # text search fallback
        if not matched:
            text_results = self.memory.search_concepts(query, top_k=5)
            for c in text_results:
                if c.confidence >= self.min_confidence_threshold:
                    matched.append(c)
                    seen_ids.add(c.id)

        step += 1
        chain.append(ReasoningStep(
            step=step, operation="RETRIEVE",
            input_=str(candidates[:5]),
            output=f"retrieved {len(matched)} concept(s): {[c.name for c in matched]}",
            confidence=min(1.0, len(matched) * 0.3),
            latency_ms=round((time.time() - t_r) * 1000, 1)
        ))

        if not matched:
            return self._no_knowledge_answer(query, chain, t0)

        # ── Step 3: Graph traversal for deeper context ───────────────────
        t_g = time.time()
        graph_neighbors: list[RetrievedConcept] = []
        for c in matched[:2]:   # traverse from top 2 matches
            neighbors = self.memory.get_neighbors(
                c.id,
                relation_types=["CAUSES", "ENABLES", "REQUIRES", "PART_OF", "EXAMPLE_OF"],
                max_hops=2
            )
            for n in neighbors:
                if n.concept.id not in seen_ids:
                    graph_neighbors.append(n)
                    seen_ids.add(n.concept.id)

        # add high-confidence neighbors to context
        enriched = matched + [
            n.concept for n in graph_neighbors
            if n.score > 0.3 and n.concept.confidence >= self.min_confidence_threshold
        ]

        step += 1
        chain.append(ReasoningStep(
            step=step, operation="TRAVERSE",
            input_=f"seed concepts: {[c.name for c in matched[:2]]}",
            output=f"graph enriched with {len(enriched) - len(matched)} additional concepts",
            confidence=min(1.0, len(enriched) * 0.15),
            latency_ms=round((time.time() - t_g) * 1000, 1)
        ))

        # ── Step 4: Synthesize answer layers ─────────────────────────────
        t_s = time.time()

        # Handle comparison intent separately
        if "compare" in intents and len(matched) >= 2:
            answer_text = _format_comparison(matched[0], matched[1])
        else:
            answer_text = self._synthesize_answer(query, intents, enriched)

        what_text    = _merge_field(enriched, "what", 300)
        why_text     = _merge_field(enriched, "why",  300)
        how_text     = _merge_field(enriched, "how",  300)
        so_what_text = _merge_field(enriched, "so_what", 300)

        confidence = _weighted_confidence(enriched)

        step += 1
        chain.append(ReasoningStep(
            step=step, operation="SYNTHESIZE",
            input_=f"{len(enriched)} concepts",
            output=f"answer ({len(answer_text)} chars), confidence={confidence}",
            confidence=confidence,
            latency_ms=round((time.time() - t_s) * 1000, 1)
        ))

        # ── Step 5: Verify — contradiction check ─────────────────────────
        t_v = time.time()
        contradictions = self._check_contradictions(enriched)
        if contradictions:
            answer_text += f"\n\n⚠ Note: conflicting information found in {contradictions}. Confidence reduced."
            confidence = max(0.1, confidence - 0.15)

        step += 1
        chain.append(ReasoningStep(
            step=step, operation="VERIFY",
            input_=f"{len(enriched)} concepts",
            output=f"contradictions: {contradictions if contradictions else 'none'}",
            confidence=confidence,
            latency_ms=round((time.time() - t_v) * 1000, 1)
        ))

        # ── Step 6: Conclude ─────────────────────────────────────────────
        all_sources = list({s for c in enriched for s in c.sources})[:8]
        step += 1
        chain.append(ReasoningStep(
            step=step, operation="CONCLUDE",
            input_="all steps",
            output=f"final confidence={confidence}, sources={len(all_sources)}",
            confidence=confidence,
            latency_ms=0
        ))

        total_ms = round((time.time() - t0) * 1000, 1)
        chain[-1].latency_ms = total_ms

        self.memory.log_event("reasoning_complete", {
            "query": query, "confidence": confidence,
            "concepts_used": len(enriched), "latency_ms": total_ms
        })

        return VelynxAnswer(
            query=query,
            answer=answer_text,
            what=what_text or "No direct definition found.",
            why=why_text or "Causal context not yet learned.",
            how=how_text or "Mechanism not yet mapped.",
            so_what=so_what_text or "Implications not yet derived.",
            confidence=confidence,
            reasoning_chain=chain,
            sources=all_sources,
            concepts_used=[c.name for c in enriched],
            latency_ms=total_ms,
            from_graph=True
        )

    # ── Internal synthesis ───────────────────────────────────────────────────

    def _synthesize_answer(self, query: str, intents: list[str],
                           concepts: list[Concept]) -> str:
        if not concepts:
            return "I don't have enough knowledge to answer this yet."

        primary = concepts[0]
        parts = []

        if "what" in intents or not intents:
            parts.append(f"{primary.name.title()}: {primary.what}")

        if "why" in intents:
            why_parts = [c.why for c in concepts if c.why]
            if why_parts:
                parts.append("Why this matters: " + why_parts[0])

        if "how" in intents:
            how_parts = [c.how for c in concepts if c.how]
            if how_parts:
                parts.append("How it works: " + how_parts[0])

        if "effect" in intents:
            sw_parts = [c.so_what for c in concepts if c.so_what]
            if sw_parts:
                parts.append("Consequences: " + sw_parts[0])

        # Add supporting concepts
        if len(concepts) > 1:
            related_names = [c.name for c in concepts[1:4]]
            parts.append(f"Related concepts: {', '.join(related_names)}")

        return "\n\n".join(parts) if parts else primary.what

    def _check_contradictions(self, concepts: list[Concept]) -> list[str]:
        """Returns names of concept pairs with CONTRADICTS relations."""
        contradicting = []
        ids = [c.id for c in concepts]
        for c in concepts:
            neighbors = self.memory.get_neighbors(
                c.id, relation_types=["CONTRADICTS"], max_hops=1
            )
            for n in neighbors:
                if n.concept.id in ids:
                    contradicting.append(f"{c.name} ↔ {n.concept.name}")
        return contradicting

    def _no_knowledge_answer(self, query: str, chain: list[ReasoningStep],
                              t0: float) -> VelynxAnswer:
        total_ms = round((time.time() - t0) * 1000, 1)
        chain.append(ReasoningStep(
            step=len(chain)+1, operation="CONCLUDE",
            input_=query,
            output="no knowledge found — learning queued",
            confidence=0.0, latency_ms=total_ms
        ))
        return VelynxAnswer(
            query=query,
            answer=f"I don't know about '{query}' yet. This topic has been queued for learning.",
            what="", why="", how="", so_what="",
            confidence=0.0,
            reasoning_chain=chain,
            sources=[],
            concepts_used=[],
            latency_ms=total_ms,
            from_graph=False
        )

    # ── Knowledge injection ──────────────────────────────────────────────────

    def teach(self, concept: Concept) -> bool:
        """Directly inject a concept into the knowledge graph."""
        return self.memory.store_concept(concept)

    def stats(self) -> dict:
        return self.memory.stats()
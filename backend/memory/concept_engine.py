"""
VELYNX Phase 21 — Conceptual Understanding Engine
===================================================
The most important phase. Replaces fact storage with deep understanding.

Every concept stored at 5 levels:
  WHAT      → definition (surface)
  HOW       → mechanism (structure)
  WHY       → purpose/cause (depth)
  SO_WHAT   → implications (impact)
  CONNECTS  → related concepts (web)
  HUMAN     → human meaning (relatability)
  UNKNOWN   → open questions (honesty)
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional
import os

logger = logging.getLogger("velynx.concept_engine")

_DATA_DIR = Path(os.getenv("VELYNX_DATA_DIR", ".")) / "velynx_data" / "concepts"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_CONCEPTS_FILE = _DATA_DIR / "concepts.json"


@dataclass
class ConceptUnderstanding:
    concept: str
    domain: str
    what: str = ""
    how: str = ""
    why: str = ""
    so_what: str = ""
    human_meaning: str = ""
    connects_to: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    enables: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    confidence: float = 0.0
    source_count: int = 0
    query_count: int = 0
    depth_score: float = 0.0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    @property
    def completeness(self) -> float:
        levels = [self.what, self.how, self.why, self.so_what, self.human_meaning]
        filled = sum(1 for l in levels if len(l) > 20)
        return filled / len(levels)

    @property
    def depth_label(self) -> str:
        c = self.completeness
        if c >= 0.9: return "DEEP"
        if c >= 0.6: return "SOLID"
        if c >= 0.4: return "PARTIAL"
        if c >= 0.2: return "SURFACE"
        return "SHALLOW"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ConceptUnderstanding":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def best_answer_for(self, query: str) -> str:
        q = query.lower()
        if any(w in q for w in ["what is", "define", "definition", "meaning"]):
            return self.what or self.how
        if any(w in q for w in ["how does", "how do", "how is", "mechanism", "works"]):
            return self.how or self.what
        if any(w in q for w in ["why", "reason", "cause", "purpose"]):
            return self.why or self.how
        if any(w in q for w in ["what can", "use", "application", "do with", "useful"]):
            return self.so_what or self.what
        if any(w in q for w in ["explain", "simple", "understand", "mean to"]):
            return self.human_meaning or self.what
        if any(w in q for w in ["important", "matter", "care"]):
            parts = []
            if self.why: parts.append(self.why)
            if self.so_what: parts.append(self.so_what)
            return " ".join(parts) or self.what
        for level in [self.how, self.what, self.why, self.so_what, self.human_meaning]:
            if len(level) > 30:
                return level
        return self.what


class ConceptExtractor:
    def extract(self, concept: str, sources: list[dict], existing: Optional[ConceptUnderstanding] = None) -> ConceptUnderstanding:
        all_text = self._merge_sources(sources)
        domain = self._detect_domain(concept, all_text)
        what = self._extract_what(concept, all_text, sources)
        how = self._extract_how(concept, all_text)
        why = self._extract_why(concept, all_text)
        so_what = self._extract_so_what(concept, all_text)
        human = self._extract_human_meaning(concept, all_text, domain)
        connects = self._extract_connections(concept, all_text)
        depends = self._extract_dependencies(concept, all_text)
        enables_list = self._extract_enables(concept, all_text)
        questions = self._extract_open_questions(concept, all_text)

        if existing:
            what = self._best(what, existing.what)
            how = self._best(how, existing.how)
            why = self._best(why, existing.why)
            so_what = self._best(so_what, existing.so_what)
            human = self._best(human, existing.human_meaning)
            connects = list(set(connects + existing.connects_to))[:20]
            depends = list(set(depends + existing.depends_on))[:10]
            enables_list = list(set(enables_list + existing.enables))[:10]
            source_count = existing.source_count + len(sources)
        else:
            source_count = len(sources)

        conf = self._calculate_confidence(what, how, why, so_what, human, source_count)
        concept_obj = ConceptUnderstanding(
            concept=concept, domain=domain, what=what, how=how, why=why,
            so_what=so_what, human_meaning=human, connects_to=connects,
            depends_on=depends, enables=enables_list, open_questions=questions,
            confidence=conf, source_count=source_count,
            query_count=existing.query_count if existing else 0,
            updated_at=time.time(), created_at=existing.created_at if existing else time.time(),
        )
        concept_obj.depth_score = concept_obj.completeness
        return concept_obj

    def _extract_what(self, concept: str, text: str, sources: list[dict]) -> str:
        sentences = self._sentences(text)
        concept_lower = concept.lower()
        patterns = [
            rf"{re.escape(concept_lower)}\s+is\s+(?:a|an|the)\s+(.{{20,200}})",
            rf"{re.escape(concept_lower)}\s+refers\s+to\s+(.{{20,200}})",
        ]
        for sent in sentences[:15]:
            sent_lower = sent.lower()
            if concept_lower in sent_lower:
                for pat in patterns:
                    m = re.search(pat, sent_lower)
                    if m:
                        return sent.strip()
        for sent in sentences[:10]:
            if concept_lower in sent.lower() and len(sent) > 40:
                return sent.strip()
        return sentences[0].strip() if sentences else ""

    def _extract_how(self, concept: str, text: str) -> str:
        sentences = self._sentences(text)
        how_keywords = ["works by", "operates by", "functions by", "mechanism", "process of", "through", "consists of", "composed of"]
        candidates = []
        for sent in sentences:
            if any(kw in sent.lower() for kw in how_keywords) and len(sent) > 40:
                candidates.append(sent.strip())
        return " ".join(candidates[:2]) if candidates else ""

    def _extract_why(self, concept: str, text: str) -> str:
        sentences = self._sentences(text)
        why_keywords = ["because", "therefore", "thus", "hence", "due to", "caused by", "reason", "purpose", "in order to", "enables", "allows"]
        candidates = []
        for sent in sentences:
            score = sum(1 for kw in why_keywords if kw in sent.lower())
            if score >= 1 and len(sent) > 40:
                candidates.append((score, sent.strip()))
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1] if candidates else ""

    def _extract_so_what(self, concept: str, text: str) -> str:
        sentences = self._sentences(text)
        impact_keywords = ["used for", "used in", "application", "enables", "allows", "makes possible", "led to", "important for", "critical for"]
        candidates = [sent.strip() for sent in sentences if any(kw in sent.lower() for kw in impact_keywords) and len(sent) > 40]
        return " ".join(candidates[:2]) if candidates else ""

    def _extract_human_meaning(self, concept: str, text: str, domain: str) -> str:
        sentences = self._sentences(text)
        human_keywords = ["everyday", "daily life", "human", "people", "society", "practical", "real world", "matters"]
        for sent in sentences:
            if any(kw in sent.lower() for kw in human_keywords) and len(sent) > 40:
                return sent.strip()
        templates = {
            "physics": f"{concept} is one of the fundamental rules the universe runs on.",
            "biology": f"{concept} is part of what makes life possible.",
            "mathematics": f"{concept} is a pattern that appears across reality.",
            "computer_science": f"{concept} is a tool that extends human capability.",
        }
        return templates.get(domain, f"{concept} is worth understanding because it connects to how the world works.")

    def _extract_connections(self, concept: str, text: str) -> list[str]:
        caps = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b", text)
        stop = {"The", "This", "That", "These", "Those", "It", "In", "At", "For", "With", "From", "By", "On", "Of", "A", "An"}
        concepts = [c for c in caps if c not in stop and len(c) > 3 and c.lower() != concept.lower()]
        seen = set()
        unique = []
        for c in concepts:
            if c.lower() not in seen:
                seen.add(c.lower())
                unique.append(c)
        return unique[:15]

    def _extract_dependencies(self, concept: str, text: str) -> list[str]:
        sentences = self._sentences(text)
        dep_keywords = ["requires", "depends on", "based on", "built on"]
        deps = []
        for sent in sentences:
            for kw in dep_keywords:
                if kw in sent.lower():
                    idx = sent.lower().find(kw)
                    after = sent[idx + len(kw):idx + len(kw) + 60].strip()
                    if after:
                        deps.append(after.split(".")[0].strip())
        return deps[:5]

    def _extract_enables(self, concept: str, text: str) -> list[str]:
        sentences = self._sentences(text)
        enable_keywords = ["enables", "allows", "makes possible", "leads to", "can be used to"]
        enables = []
        for sent in sentences:
            for kw in enable_keywords:
                if kw in sent.lower():
                    idx = sent.lower().find(kw)
                    after = sent[idx + len(kw):idx + len(kw) + 80].strip()
                    if after:
                        enables.append(after.split(".")[0].strip())
        return enables[:5]

    def _extract_open_questions(self, concept: str, text: str) -> list[str]:
        sentences = self._sentences(text)
        unknown_keywords = ["unknown", "unsolved", "debated", "controversial", "unclear", "not yet", "remains", "open question"]
        return [sent.strip() for sent in sentences if any(kw in sent.lower() for kw in unknown_keywords) and len(sent) > 30][:3]

    def _merge_sources(self, sources: list[dict]) -> str:
        parts = []
        for s in sources:
            text = s.get("snippet") or s.get("content") or s.get("extract") or ""
            if text:
                import html as _html
                text = _html.unescape(text)
                text = re.sub(r"<[^>]+>", "", text)
                parts.append(text)
        return " ".join(parts)

    def _sentences(self, text: str) -> list[str]:
        parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
        return [p.strip() for p in parts if len(p.strip()) > 20]

    def _detect_domain(self, concept: str, text: str) -> str:
        combined = (concept + " " + text).lower()
        domains = {
            "physics": ["quantum", "force", "energy", "particle", "wave", "relativity", "gravity"],
            "mathematics": ["equation", "theorem", "proof", "integral", "derivative", "algebra"],
            "biology": ["cell", "dna", "protein", "organism", "evolution", "gene", "species"],
            "chemistry": ["molecule", "atom", "reaction", "element", "compound", "bond"],
            "computer_science": ["algorithm", "software", "programming", "data", "code", "network"],
            "astronomy": ["star", "galaxy", "planet", "universe", "orbit", "telescope"],
            "history": ["century", "war", "civilization", "empire", "ancient"],
        }
        best, best_score = "general", 0
        for domain, keywords in domains.items():
            score = sum(1 for kw in keywords if kw in combined)
            if score > best_score:
                best, best_score = domain, score
        return best

    def _calculate_confidence(self, what, how, why, so_what, human, sources) -> float:
        filled = sum(1 for l in [what, how, why, so_what, human] if len(l) > 20)
        return min(0.97, (filled / 5) * 0.6 + min(1.0, sources / 5) * 0.4)

    def _best(self, new: str, existing: str) -> str:
        if len(new) > len(existing) and len(new) > 30:
            return new
        return existing if existing else new


class ConceptEngine:
    def __init__(self):
        self._concepts: dict[str, ConceptUnderstanding] = {}
        self._extractor = ConceptExtractor()
        self._load()

    def learn(self, concept: str, sources: list[dict]) -> ConceptUnderstanding:
        key = self._normalize(concept)
        existing = self._concepts.get(key)
        understanding = self._extractor.extract(concept, sources, existing)
        self._concepts[key] = understanding
        self._save()
        return understanding

    def understand(self, query: str) -> Optional[ConceptUnderstanding]:
        concept = self._extract_concept_from_query(query)
        key = self._normalize(concept)
        if key in self._concepts:
            c = self._concepts[key]
            c.query_count += 1
            return c
        query_words = set(key.split())
        best, best_score = None, 0.0
        for stored_key, concept_obj in self._concepts.items():
            stored_words = set(stored_key.split())
            overlap = len(query_words & stored_words)
            score = overlap / max(len(query_words), len(stored_words), 1) * concept_obj.confidence
            if score > best_score and score > 0.3:
                best_score = score
                best = concept_obj
        if best:
            best.query_count += 1
        return best

    def get_answer(self, query: str) -> Optional[dict]:
        concept = self.understand(query)
        if not concept:
            return None
        answer = concept.best_answer_for(query)
        if not answer or len(answer) < 20:
            return None
        return {
            "answer": answer,
            "confidence": self._float_to_label(concept.confidence),
            "confidence_score": concept.confidence,
            "domain": concept.domain,
            "depth": concept.depth_label,
            "connects_to": concept.connects_to[:5],
            "open_questions": concept.open_questions[:2],
            "source": "concept_engine",
        }

    def stats(self) -> dict:
        if not self._concepts:
            return {"total_concepts": 0}
        depths = {}
        domains = {}
        for c in self._concepts.values():
            depths[c.depth_label] = depths.get(c.depth_label, 0) + 1
            domains[c.domain] = domains.get(c.domain, 0) + 1
        avg_conf = sum(c.confidence for c in self._concepts.values()) / len(self._concepts)
        return {"total_concepts": len(self._concepts), "avg_confidence": round(avg_conf, 3), "depth_distribution": depths, "domains": domains}

    def _normalize(self, text: str) -> str:
        stop = {"what", "is", "the", "a", "an", "how", "why", "does", "do", "are", "was", "were", "of", "in", "on", "can", "i", "with"}
        words = [w.lower() for w in text.split() if w.lower() not in stop]
        return " ".join(words[:5]) if words else text.lower()[:40]

    def _extract_concept_from_query(self, query: str) -> str:
        q = query.lower().strip().rstrip("?")
        for prefix in ["what is ", "what are ", "how does ", "how do ", "why is ", "why does ", "what can i do with ", "explain ", "tell me about "]:
            if q.startswith(prefix):
                q = q[len(prefix):]
                break
        return q.strip()

    def _float_to_label(self, f: float) -> str:
        if f >= 0.85: return "CERTAIN"
        if f >= 0.65: return "PROBABLE"
        if f >= 0.40: return "DEBATED"
        return "LOW"

    def _save(self):
        try:
            data = {k: v.to_dict() for k, v in self._concepts.items()}
            _CONCEPTS_FILE.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.warning("Concept save failed: %s", e)

    def _load(self):
        try:
            if _CONCEPTS_FILE.exists():
                data = json.loads(_CONCEPTS_FILE.read_text())
                self._concepts = {k: ConceptUnderstanding.from_dict(v) for k, v in data.items()}
                logger.info("Concept engine loaded: %d concepts", len(self._concepts))
        except Exception as e:
            logger.warning("Concept load failed: %s", e)


concept_engine = ConceptEngine()

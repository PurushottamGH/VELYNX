"""DEPRECATED: Legacy TF-IDF vector store. Use memory.memory_manager instead."""
from __future__ import annotations

import hashlib
import json
import logging
import re
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

warnings.warn(
    "memory.vector_store is deprecated — use memory.memory_manager + memory.vector_backend instead",
    DeprecationWarning,
    stacklevel=2,
)
logger = logging.getLogger("uvicorn")


_MEMORY_PATH = Path("data/neural_links.json")
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "do",
    "does",
    "for",
    "from",
    "how",
    "i",
    "is",
    "it",
    "me",
    "my",
    "of",
    "the",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
    "you",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if token not in _STOPWORDS]


def _normalize(text: str) -> str:
    return " ".join(_tokenize(text))


def _confidence_label(score: float) -> str:
    if score >= 0.8:
        return "CERTAIN"
    if score >= 0.55:
        return "PROBABLE"
    if score >= 0.35:
        return "DEBATED"
    return "UNKNOWN"


@dataclass(slots=True)
class MemoryHit:
    prompt: str
    answer: str
    score: float
    confidence: str
    source: str | None
    tags: list[str]
    episode_id: str
    kind: str


class VectorStore:
    """Small associative memory that stores learned prompt-answer links."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or _MEMORY_PATH
        self._state = self._load_state()

    def _load_state(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {"episodes": {}, "concepts": {}}

    def _persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._state, indent=2, sort_keys=True), encoding="utf-8")

    @staticmethod
    def _episode_id(prompt: str, answer: str) -> str:
        fingerprint = f"{_normalize(prompt)}|{_normalize(answer)}"
        return hashlib.sha1(fingerprint.encode("utf-8")).hexdigest()

    def remember(
        self,
        prompt: str,
        answer: str,
        *,
        confidence: str = "PROBABLE",
        source: str | None = None,
        tags: list[str] | None = None,
        weight: float = 0.25,
        kind: str = "learned",
    ) -> MemoryHit | None:
        prompt_tokens = _tokenize(prompt)
        answer_tokens = _tokenize(answer)
        if not prompt_tokens and not answer_tokens:
            return None

        episode_id = self._episode_id(prompt, answer)
        episode = self._state["episodes"].get(episode_id, {})
        combined_tokens = sorted(set(prompt_tokens + answer_tokens))
        current_strength = float(episode.get("strength", 0.0))
        strength = round(max(0.0, min(1.0, current_strength + abs(weight))), 3)

        stored = {
            "prompt": prompt,
            "answer": answer,
            "prompt_tokens": prompt_tokens,
            "answer_tokens": answer_tokens,
            "confidence": confidence,
            "source": source,
            "tags": sorted(set(tags or [])),
            "strength": strength,
            "kind": kind,
            "updated_at": _now(),
        }
        stored["created_at"] = episode.get("created_at", stored["updated_at"])

        self._state["episodes"][episode_id] = stored

        for token in combined_tokens:
            concept = self._state["concepts"].setdefault(
                token,
                {"weight": 0.0, "episodes": [], "last_seen": stored["updated_at"]},
            )
            concept["weight"] = round(float(concept.get("weight", 0.0)) + abs(weight), 3)
            if episode_id not in concept["episodes"]:
                concept["episodes"].append(episode_id)
            concept["last_seen"] = stored["updated_at"]

        self._persist()
        return MemoryHit(
            prompt=prompt,
            answer=answer,
            score=strength,
            confidence=confidence,
            source=source,
            tags=stored["tags"],
            episode_id=episode_id,
            kind=kind,
        )

    def recall(self, query: str, limit: int = 3) -> list[MemoryHit]:
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        scored: list[MemoryHit] = []
        now = datetime.now(timezone.utc)
        for episode_id, episode in self._state["episodes"].items():
            prompt_tokens = set(episode.get("prompt_tokens") or [])
            answer_tokens = set(episode.get("answer_tokens") or [])
            overlap = len(prompt_tokens.intersection(query_tokens))
            answer_overlap = len(answer_tokens.intersection(query_tokens))
            if overlap == 0 and answer_overlap == 0:
                continue

            concept_boost = 0.0
            for token in query_tokens:
                concept = self._state["concepts"].get(token)
                if concept and episode_id in concept.get("episodes", []):
                    concept_boost += float(concept.get("weight", 0.0))

            created_at = episode.get("created_at") or episode.get("updated_at")
            age_bonus = 0.0
            if created_at:
                try:
                    age = now - datetime.fromisoformat(created_at)
                    age_bonus = max(0.0, 1.0 - (age.total_seconds() / 86_400.0) * 0.02)
                except ValueError:
                    age_bonus = 0.0

            score = (
                (overlap * 0.35)
                + (answer_overlap * 0.15)
                + min(concept_boost, 1.0) * 0.2
                + float(episode.get("strength", 0.0)) * 0.25
                + age_bonus * 0.05
            )
            scored.append(
                MemoryHit(
                    prompt=str(episode.get("prompt", "")),
                    answer=str(episode.get("answer", "")),
                    score=round(score, 3),
                    confidence=_confidence_label(score),
                    source=episode.get("source"),
                    tags=list(episode.get("tags") or []),
                    episode_id=episode_id,
                    kind=str(episode.get("kind", "learned")),
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:limit]

    def best_answer(self, query: str) -> dict | None:
        matches = self.recall(query, limit=1)
        if not matches:
            return None

        top = matches[0]
        if top.score < 0.35:
            return None

        answer = top.answer.strip()
        if not answer:
            return None
        if answer[-1] not in ".!?":
            answer += "."

        prefix = "I remember this: " if top.kind != "gap" else "I remember the gap like this: "
        confidence = "CERTAIN" if top.score >= 0.8 else "PROBABLE"
        memory_source = {
            "url": f"memory://{top.episode_id}",
            "title": "Associative memory",
            "snippet": top.prompt,
            "source": "memory",
            "score": top.score,
        }
        return {
            "answer": f"{prefix}{answer}",
            "confidence": confidence,
            "citations": [memory_source["url"]],
            "gaps": [],
            "tone": "human",
            "sources": [memory_source],
            "debug": {
                "memory": {
                    "episode_id": top.episode_id,
                    "score": top.score,
                    "confidence": top.confidence,
                    "prompt": top.prompt,
                    "tags": top.tags,
                    "source": top.source,
                    "kind": top.kind,
                }
            },
        }


_DEFAULT_VECTOR_STORE = VectorStore()


def remember_interaction(
    prompt: str,
    answer: str,
    *,
    confidence: str = "PROBABLE",
    source: str | None = None,
    tags: list[str] | None = None,
    weight: float = 0.25,
    kind: str = "learned",
) -> MemoryHit | None:
    return _DEFAULT_VECTOR_STORE.remember(
        prompt,
        answer,
        confidence=confidence,
        source=source,
        tags=tags,
        weight=weight,
        kind=kind,
    )


def recall_answer(query: str) -> dict | None:
    return _DEFAULT_VECTOR_STORE.best_answer(query)

"""Answer synthesizer with topic filtering and coherence check."""
from __future__ import annotations

import re

_STOP = {
    "what", "is", "the", "a", "an", "how", "why", "when", "where",
    "who", "does", "do", "are", "was", "were", "of", "in", "on",
    "at", "to", "for", "with", "by", "and", "or", "but", "it",
    "this", "that", "these", "those", "can", "i", "be", "has", "had",
}


def _is_on_topic(sentence: str, query: str, threshold: float = 0.3) -> bool:
    """Check if sentence is relevant to the query."""
    q_words = set(re.sub(r"[^\w\s]", "", query.lower()).split()) - _STOP
    s_words = set(re.sub(r"[^\w\s]", "", sentence.lower()).split())
    if not q_words:
        return True
    overlap = len(q_words & s_words) / len(q_words)
    if overlap < threshold:
        return False
    # Domain drift check: if query has "why/how" but sentence is about a different entity
    q_lower = query.lower()
    s_lower = sentence.lower()
    # If query asks about X but sentence mentions unrelated proper nouns
    drift_words = {"mars", "venus", "jupiter", "saturn", "nasa", "spacex", "tesla",
                   "google", "apple", "microsoft", "amazon", "facebook"}
    query_entities = {w for w in q_words if len(w) > 3}
    sent_drift = {w for w in drift_words if w in s_lower}
    if sent_drift and not (query_entities & sent_drift):
        return False
    return True


def synthesize(draft: dict, query: str = "") -> dict:
    """Synthesize final answer with topic filtering and length control."""
    answer = draft.get("draft", "")

    if query and answer:
        # Filter off-topic sentences
        sentences = re.split(r"(?<=[.!?])\s+", answer)
        on_topic = [s for s in sentences if _is_on_topic(s, query)]
        if on_topic:
            answer = " ".join(on_topic[:4])  # Max 4 sentences
        # If everything was filtered, keep original but truncate
        elif len(sentences) > 4:
            answer = " ".join(sentences[:4])

    return {
        "answer": answer,
        "tone": draft.get("tone", "scientific"),
        "confidence": draft.get("confidence", "UNKNOWN"),
        "citations": draft.get("citations", []),
        "gaps": draft.get("gaps", []),
    }

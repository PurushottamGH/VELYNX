"""Context compressor — summarizes old conversation turns into condensed context."""
from __future__ import annotations

import re
from conversation.working_memory import ConversationTurn


def compress_context(turns: list[ConversationTurn]) -> str:
    """Compress a list of conversation turns into a condensed summary string.

    Uses heuristic extraction (no LLM required). Falls back gracefully
    when turns are empty.
    """
    if not turns:
        return ""

    user_turns = [t for t in turns if t.role == "user"]
    assistant_turns = [t for t in turns if t.role == "assistant"]

    parts: list[str] = []

    # Extract topics from user turns
    if user_turns:
        topics = _extract_key_phrases(user_turns)
        if topics:
            parts.append(f"Topics discussed: {', '.join(topics[:5])}")

        # Last user question
        last_user = user_turns[-1]
        parts.append(f"Last question: {last_user.text[:150]}")

    # Summarize assistant confidence trajectory
    if assistant_turns:
        confidences = [t.confidence for t in assistant_turns if t.confidence != "UNKNOWN"]
        if confidences:
            parts.append(f"Confidence trajectory: {' → '.join(confidences[-4:])}")

        # Key claims from high-confidence answers
        high_conf = [t for t in assistant_turns if t.confidence in ("CERTAIN", "PROBABLE")]
        if high_conf:
            parts.append(f"Key answers provided: {len(high_conf)}")

    # Extract entities mentioned across turns
    all_text = " ".join(t.text for t in turns)
    entities = _extract_entities(all_text)
    if entities:
        parts.append(f"Entities: {', '.join(entities[:5])}")

    return ". ".join(parts)


def _extract_key_phrases(turns: list[ConversationTurn]) -> list[str]:
    """Extract key phrases from user turns by finding repeated meaningful words."""
    word_counts: dict[str, int] = {}
    for t in turns:
        words = re.findall(r"[a-zA-Z]{4,}", t.text.lower())
        for w in set(words):  # count each word once per turn
            word_counts[w] = word_counts.get(w, 0) + 1

    # Words appearing in multiple turns are likely topics
    multi_turn = {w for w, c in word_counts.items() if c >= 1}
    stop = {
        "what", "when", "where", "which", "while", "with", "would", "could",
        "should", "about", "their", "there", "these", "those", "this", "that",
        "from", "into", "than", "then", "they", "been", "have", "also",
        "more", "some", "just", "like", "very", "well", "tell", "think",
        "know", "really", "actually", "please", "help", "does", "make",
    }
    filtered = [w for w in multi_turn if w not in stop]
    return sorted(filtered, key=lambda w: word_counts[w], reverse=True)[:8]


def _extract_entities(text: str) -> list[str]:
    """Extract capitalized phrases and proper nouns from text."""
    # Simple heuristic: find sequences of capitalized words
    entities = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique = []
    for e in entities:
        if e not in seen and len(e) > 2:
            seen.add(e)
            unique.append(e)
    return unique[:10]

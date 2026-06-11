"""
VELYNX Priority Router
======================
Classifies every query into one of 4 levels before it hits answer_question().

URGENT -> "fix yourself", "patch", "self-code"
LEARN  -> "learn:", "study", "teach yourself"
NORMAL -> everything else
LOW    -> greetings, "hi", "ok", "thanks"
"""
from __future__ import annotations

import logging

logger = logging.getLogger("velynx.priority_router")


class Priority:
    URGENT = "urgent"
    LEARN = "learn"
    NORMAL = "normal"
    LOW = "low"


URGENT_PATTERNS = [
    "fix yourself", "patch yourself", "self-code", "self code",
    "repair yourself", "debug yourself", "self-fix", "self fix",
    "auto-fix", "autofix", "self repair", "fix the",
    "optimize yourself", "refactor yourself",
]

LEARN_PREFIXES = [
    "learn:", "learn about", "study ", "teach yourself",
    "research ", "investigate ",
]

LOW_EXACT = {
    "hi", "hello", "hey", "yo", "sup", "heya", "howdy",
    "ok", "okay", "k", "kk",
    "thanks", "thank you", "thx", "ty", "cheers",
    "bye", "goodbye", "cya", "see ya", "later", "ttyl",
    "good morning", "good afternoon", "good evening", "good night",
    "nice", "cool", "great", "awesome", "perfect",
    "yep", "yes", "yeah", "nope", "no", "nah",
    "lol", "haha", "heh",
    "", " ",
}


def classify(query: str) -> str:
    lowered = query.lower().strip()

    for pattern in URGENT_PATTERNS:
        if pattern in lowered:
            return Priority.URGENT

    for prefix in LEARN_PREFIXES:
        if lowered.startswith(prefix) or prefix.rstrip() in lowered:
            return Priority.LEARN

    if lowered in LOW_EXACT or (len(lowered) <= 3 and lowered.isalpha()):
        return Priority.LOW

    return Priority.NORMAL


route = classify

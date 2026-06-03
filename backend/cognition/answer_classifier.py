"""
VELYNX Phase 33 — Answer Classifier
Classifies answer content type for rich terminal formatting.
"""

from __future__ import annotations

import re


ANSWER_TYPES = [
    "math_equation",    # contains equations, formulas
    "code_snippet",     # contains code
    "comparison",       # X vs Y, differences between
    "concept",          # definition + explanation
    "how_to",           # step by step instructions
    "list",             # enumerated items
    "timeline",         # dates and events
    "general",          # default prose
]


class AnswerClassifier:
    """Classifies answer type for formatting."""

    def classify(self, query: str, answer: str) -> str:
        """Returns one of ANSWER_TYPES."""
        q = query.lower().strip()
        a = answer.lower()

        # Comparison (check first — "compare X vs Y" should not match code)
        if any(p in q for p in ["compare", "vs", "versus", "difference between", "better than"]):
            return "comparison"
        if re.search(r"\b(compared to|in contrast|on the other hand|whereas)\b", a):
            return "comparison"

        # Math equations
        if any(p in q for p in ["equation", "formula", "theorem", "solve", "calculate"]):
            return "math_equation"
        if re.search(r"[yf]\s*=\s*.+x", a) or re.search(r"\b(integral|derivative|sum|product)\b", a):
            return "math_equation"
        if re.search(r"\b\d+\s*[+\-*/^]\s*\d+\s*=", a):
            return "math_equation"

        # How-to / steps (check before code — "Step 1: download from..." has "from")
        if any(p in q for p in ["how to", "how do i", "steps to", "guide", "tutorial"]):
            return "how_to"
        if re.search(r"\b(step \d|first,|second,|third,|then,|finally,)\b", a):
            return "how_to"
        if re.search(r"\d+\.\s+\w", answer) and not re.search(r"\bdef \w+\(", answer):
            return "how_to"

        # Code snippets
        if any(p in q for p in ["code", "program", "script", "implement", "write a"]):
            return "code_snippet"
        if re.search(r"\b(def \w+\(|class \w+|import \w+|from \w+ import|if __name__|console\.log)", a):
            return "code_snippet"
        if "```" in answer:
            return "code_snippet"

        # Timeline (dates)
        dates = re.findall(r"\b(1[5-9]\d{2}|20[0-2]\d)\b", answer)
        if len(dates) >= 3:
            return "timeline"
        if any(p in q for p in ["history of", "timeline", "evolution of", "over time"]):
            if dates:
                return "timeline"

        # List
        list_markers = re.findall(r"^[\s]*[-•◆▪]\s+", answer, re.MULTILINE)
        if len(list_markers) >= 3:
            return "list"
        if re.search(r"\b(there are|main types|includes|such as|examples):?\b", a):
            if len(list_markers) >= 2:
                return "list"

        # Concept (definition + explanation)
        if any(p in q for p in ["what is", "what are", "define", "explain", "describe"]):
            return "concept"

        return "general"

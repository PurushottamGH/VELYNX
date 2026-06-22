import json
import spacy
from pathlib import Path
from typing import Any, Dict

# Load the deterministic NLP engine
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("FATAL: spaCy model not found.")
    exit(1)

LEXICON_PATH = Path(__file__).parent.parent / "data" / "lexicon.json"

ABSTRACT_SUFFIXES = ("ness", "ity", "tion", "ism", "ence", "ance", "ment")


def _load_lexicon() -> Dict[str, list]:
    """Load the governed concept lexicon from the canonical JSON file."""
    if not LEXICON_PATH.exists():
        raise FileNotFoundError(f"Lexicon file missing: {LEXICON_PATH}")
    data = json.loads(LEXICON_PATH.read_text(encoding="utf-8"))
    return data["lexicon"]


class PerceptionLayer:
    def __init__(self):
        self.lexicon = _load_lexicon()
        self._lexicon_mtime = LEXICON_PATH.stat().st_mtime

    def reload_lexicon(self) -> None:
        """Hot-reload the lexicon from disk (called after LexiconUpdater writes)."""
        self.lexicon = _load_lexicon()
        self._lexicon_mtime = LEXICON_PATH.stat().st_mtime

    async def parse_input(self, user_text: str) -> Dict[str, Any]:
        text = user_text.lower()
        doc = nlp(text)
        activations: Dict[str, float] = {}

        meaningful_tokens = 0
        recognized_tokens = 0
        unrecognized_words = []

        for token in doc:
            lemma = token.lemma_
            is_negated = any(child.dep_ == "neg" for child in token.children)

            is_meaningful = False
            if token.is_alpha and not token.is_stop and len(lemma) >= 4:
                if token.pos_ == "ADJ":
                    is_meaningful = True
                elif token.pos_ == "NOUN" and any(lemma.endswith(s) for s in ABSTRACT_SUFFIXES):
                    is_meaningful = True

            if is_meaningful:
                meaningful_tokens += 1

            matched = False
            for concept, triggers in self.lexicon.items():
                if (lemma == concept or lemma in triggers) and not is_negated:
                    activations[concept] = min(1.0, activations.get(concept, 0.0) + 0.3)
                    matched = True
                    break

            if matched and is_meaningful:
                recognized_tokens += 1
            elif is_meaningful and not is_negated:
                unrecognized_words.append(lemma)

        coverage = (recognized_tokens / meaningful_tokens) if meaningful_tokens > 0 else 1.0

        return {
            "activations": activations,
            "missed_concepts": unrecognized_words,
            "coverage": coverage,
        }

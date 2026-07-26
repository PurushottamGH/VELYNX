"""EXP-0 leakage validator.

Checks every paraphrase_query in paraphrases.json against every one of the 32
seeded concept names in backend/soul/concepts.json, using the SAME matching
rules backend/pipeline/soul_router.py applies in production:

  1. exact substring match  -- ``concept_name in query.lower()``
     (backend/pipeline/soul_router.py:178, soul_lookup_legacy)
  2. Porter-stem match on individual query words, with the ">=4-char prefix"
     fallback rule
     (backend/pipeline/soul_router.py:31-37, _stem_match)

This script does NOT import, call, or execute any part of the VELYNX
cognitive pipeline. It only re-implements the two pure string-matching rules
above (copied, not imported, so this validator has zero dependency on
backend.* and cannot be affected by future changes to the production
detector) and applies them to a static JSON file. It is a materials-QA step,
not an experiment run.

Usage:
    python leakage_check.py

Exit code 0 = every item is clean. Exit code 1 = at least one leak found
(printed to stdout with concept, matched keyword, and match type).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from nltk.stem import PorterStemmer

_STEMMER = PorterStemmer()

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent.parent
_CONCEPTS_PATH = _REPO_ROOT / "backend" / "soul" / "concepts.json"
_PARAPHRASES_PATH = _HERE / "paraphrases.json"


def _stem(word: str) -> str:
    return _STEMMER.stem(word.strip(",.!?;:'\"()[]{}"))


def _stem_match(query_word: str, concept_stem: str) -> bool:
    """Mirrors backend/pipeline/soul_router.py:_stem_match exactly."""
    s_q = _stem(query_word)
    if not s_q or not concept_stem:
        return False
    return s_q == concept_stem or (len(s_q) >= 4 and s_q[:4] == concept_stem[:4])


def find_leaks(query: str, concept_names: list[str]) -> list[dict]:
    """Return every (concept, match_type) leak found in ``query``.

    Conservative by design: checks the query against ALL seeded concepts, not
    just the concept the item targets, because a paraphrase that accidentally
    names a DIFFERENT seeded concept is still a confound (it can pull the
    detector toward the wrong concept, or toward two concepts at once).

    IMPORTANT -- this must stay a byte-for-byte reproduction of production's
    stemming, not an "equivalent" approximation. Production
    (backend/pipeline/soul_router.py:23) computes
    ``_STEMMER.stem(concept_name)`` ONCE on the full (possibly multi-word)
    concept name as a single string. PorterStemmer does not tokenize
    internally, so for a two-word concept this stems only the trailing token
    and passes the leading word through unchanged, e.g.
    ``stem("market collapse") == "market collaps"`` (4-char prefix "mark").
    That means, in production, a query word like "marketed" (stem "market",
    prefix "mark") stem-matches the WHOLE "market collapse" concept via the
    4-char-prefix rule -- even though "collapse" never appears anywhere. An
    earlier version of this validator stemmed each content word of the
    concept name SEPARATELY, which is not provably equivalent to this
    behavior and was flagged in review. Do not reintroduce that shortcut.
    """
    leaks: list[dict] = []
    query_lower = query.lower()
    query_words = query_lower.split()

    for concept in concept_names:
        concept_lower = concept.lower()
        # Rule 1: exact substring (matches the full, possibly multi-word,
        # concept name -- this is what soul_lookup_legacy's fast path checks).
        if concept_lower in query_lower:
            leaks.append({"concept": concept, "match_type": "substring"})
            continue

        # Rule 2: Porter-stem match against the WHOLE concept name, stemmed
        # as one string -- exactly mirrors
        # _SOUL_CONCEPT_STEMS[name] = _STEMMER.stem(name) in soul_router.py.
        concept_stem = _stem(concept_lower)
        for qw in query_words:
            if _stem_match(qw, concept_stem):
                leaks.append(
                    {
                        "concept": concept,
                        "match_type": "stem",
                        "query_word": qw,
                        "concept_stem": concept_stem,
                    }
                )
                break

    return leaks


def main() -> int:
    concepts = json.loads(_CONCEPTS_PATH.read_text(encoding="utf-8"))
    concept_names = list(concepts.keys())

    data = json.loads(_PARAPHRASES_PATH.read_text(encoding="utf-8"))
    items = data["items"]

    if len(items) != len(concept_names):
        print(
            f"FATAL: paraphrases.json has {len(items)} items but "
            f"concepts.json has {len(concept_names)} concepts."
        )
        return 1
    if {i["concept"] for i in items} != set(concept_names):
        print("FATAL: paraphrases.json concept set does not match " "concepts.json concept set.")
        return 1

    total_leaks = 0
    for item in items:
        concept = item["concept"]
        query = item["paraphrase_query"]
        leaks = find_leaks(query, concept_names)
        if leaks:
            total_leaks += len(leaks)
            print(f"LEAK in item '{concept}':")
            for leak in leaks:
                print(
                    f"    -> matches seeded concept {leak['concept']!r} "
                    f"via {leak['match_type']}"
                    + (
                        f" (query word {leak.get('query_word')!r} vs "
                        f"concept stem {leak.get('concept_word_stem')!r})"
                        if leak["match_type"] == "stem"
                        else ""
                    )
                )

        # The ORIGINAL query is EXPECTED and REQUIRED to leak its own
        # concept (that is the control condition) -- verify that instead
        # of flagging it.
        own_leak = find_leaks(item["original_query"], [concept])
        if not own_leak:
            total_leaks += 1
            print(
                f"FATAL: original_query for '{concept}' does NOT contain "
                f"its own seeded keyword: {item['original_query']!r}"
            )

    if total_leaks:
        print(
            f"\nRESULT: FAILED — {total_leaks} leak(s) found. "
            "Fix paraphrases.json before freezing."
        )
        return 1

    print(
        f"RESULT: PASSED — {len(items)} paraphrase items checked against "
        f"{len(concept_names)} seeded concepts. No leaks. Every "
        "original_query confirmed to contain its own seeded keyword."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""PA-2 -- deterministic candidate-claim construction from evidence (ES-1 Section 7.1).

Entity-level matching (not topic-level) -- the first line of defence against
CF-R2/FM-1. Pure text mechanics: no state logic, no tier knowledge. No model
calls (hosted-LLM extraction is unlawful -- M8); no randomness; parameters
from ``constants.EXTRACTION_PARAMS``.

Procedure
---------
For each query entity -- a query token surviving the stopword list, the
minimum-token-length floor, and the entity-token pattern -- the module scans
the evidence set for items whose text contains that entity as an explicit
word-boundary occurrence (case-sensitivity governed by the ``case_fold``
flag). For every entity thus present in at least one evidence item, exactly
one candidate claim is emitted: its ``claim_text`` is the ``claim_template``
rendered with that entity (and the query), and its ``supporting_doc_ids`` is
the sorted tuple of the doc_ids of every evidence item that contains the
entity. Topic-level-only evidence -- a document discussing a related subject
without naming the query entity -- yields no claim (the FM-1/CF-R2 guard).
Topically-unrelated, empty, or nonexistent-entity evidence yields the empty
candidate-claim set. Output is sorted by the stable key
``(claim_text, supporting_doc_ids)`` so it is independent of evidence
iteration order; every emitted ``supporting_doc_id`` is by construction a
member of the input evidence set.

Parameters
----------
All tunables are sourced from ``program_a.constants.EXTRACTION_PARAMS`` at
call time, merged over structural defaults declared in this module
(``EXTRACTION_PARAMS`` wins per key). This keeps the code change-free when
T1/G4 freezes ``EXTRACTION_PARAMS`` (CR-11 / blocker B-13): the frozen values
flow straight through. Until that freeze, ``EXTRACTION_PARAMS`` is the
authorised placeholder ``{}`` and the structural defaults below govern
behaviour.

Tunables -- each a free constant, sourced from ``EXTRACTION_PARAMS`` with a
pre-T1 structural default: ``stopwords`` (query-token stop set),
``min_entity_token_length`` (minimum query-token length),
``entity_token_pattern`` (the query-token regex), ``case_fold`` (entity
match case-folding flag), and ``claim_template`` (the ``claim_text``
template; receives ``{entity}`` and ``{query}``).

Structural -- frozen-by-construction, not free constants: the stable sort
key ``(claim_text, supporting_doc_ids)`` (a determinism requirement, not a
tunable), the ``EXTRACTION_PARAMS``-wins merge precedence, and the
word-boundary entity-match mechanism itself.

Reference: PROGRAM_A_FINAL_ARCHITECTURE.md Section 4 PA-2;
PROGRAM_A_MODULE_SPEC.md Section 6; PROGRAM_A_API_REFERENCE.md Section 7;
PROGRAM_A_CONFIDENCE_MECHANISM.md Section 7.1; PROGRAM_A_TEST_STRATEGY.md
(test_claim_extraction.py).
"""

from __future__ import annotations

import re

import program_a.constants as _constants
from program_a.types import CandidateClaim, CandidateClaims, EvidenceSet

# --- structural defaults (tunable: sourced from EXTRACTION_PARAMS) -------------
# Each is a pre-T1 structural default; the frozen value is supplied by
# program_a.constants.EXTRACTION_PARAMS at the T1/G4 freeze. EXTRACTION_PARAMS
# wins per-key when present (see _resolve_params).

# pre-T1 structural default; superseded when constants.EXTRACTION_PARAMS is frozen at G4 (CR-11/B-13).
_STOPWORDS_DEFAULT: frozenset[str] = frozenset(
    {
        "a", "an", "the",
        "is", "are", "was", "were", "be", "been", "being", "am",
        "of", "to", "in", "on", "at", "by", "for", "with", "from", "into", "about",
        "and", "or", "but", "not", "nor", "so", "than", "too", "very",
        "as", "if", "then", "that", "this", "these", "those",
        "what", "which", "who", "whom", "whose", "how", "why", "when", "where",
        "whether",
        "do", "does", "did", "doing",
        "can", "could", "would", "should", "will", "shall", "may", "might",
        "have", "has", "had", "having",
        "it", "its", "he", "she", "they", "we", "you", "i", "me",
        "my", "your", "their", "our", "his", "her", "them", "us", "him",
        "tell", "explain", "describe", "list", "show", "find", "know",
        "think", "say", "see", "get", "make", "made", "use", "used", "using",
        "like", "also", "just", "some", "any", "all", "each", "every",
        "many", "much", "more", "most", "such", "other", "another",
    }
)

# pre-T1 structural default; superseded when constants.EXTRACTION_PARAMS is frozen at G4 (CR-11/B-13).
_MIN_ENTITY_TOKEN_LENGTH_DEFAULT: int = 3

# pre-T1 structural default; superseded when constants.EXTRACTION_PARAMS is frozen at G4 (CR-11/B-13).
_ENTITY_TOKEN_PATTERN_DEFAULT: str = r"[A-Za-z0-9][A-Za-z0-9'\-]*"

# pre-T1 structural default; superseded when constants.EXTRACTION_PARAMS is frozen at G4 (CR-11/B-13).
_CASE_FOLD_DEFAULT: bool = True

# pre-T1 structural default; superseded when constants.EXTRACTION_PARAMS is frozen at G4 (CR-11/B-13).
_CLAIM_TEMPLATE_DEFAULT: str = "{entity}"

# --- structural (frozen-by-construction, not free constants) ------------------
# The stable output sort key is a determinism requirement (criterion i), not a
# tunable: claims are ordered by (claim_text, supporting_doc_ids) so output is
# independent of evidence iteration order. The EXTRACTION_PARAMS-wins merge
# precedence and the word-boundary entity-match mechanism are likewise
# structural and are not exposed as free constants.


def _resolve_params() -> dict:
    """Merge structural defaults with ``constants.EXTRACTION_PARAMS`` at call time.

    ``EXTRACTION_PARAMS`` wins per-key when present, so the T1/G4 freeze flows
    the frozen values through with zero code change in this module. Read at
    call time (not import time) so a future rebind of the module attribute is
    observed. Returns a fresh local dict; no module-level mutable state.
    """
    merged: dict = {
        "stopwords": _STOPWORDS_DEFAULT,
        "min_entity_token_length": _MIN_ENTITY_TOKEN_LENGTH_DEFAULT,
        "entity_token_pattern": _ENTITY_TOKEN_PATTERN_DEFAULT,
        "case_fold": _CASE_FOLD_DEFAULT,
        "claim_template": _CLAIM_TEMPLATE_DEFAULT,
    }
    merged.update(_constants.EXTRACTION_PARAMS)
    return merged


def _extract_query_entities(
    query_text: str,
    pattern: str,
    stopwords: frozenset[str],
    min_len: int,
    case_fold: bool,
) -> list[tuple[str, str]]:
    """Tokenize the query into deduped entity (original, match-key) pairs.

    Stopword filtering is case-insensitive (stopwords are stored lowercased);
    ``case_fold`` governs the entity<->evidence match key (and thus the dedup
    key): when ``case_fold`` is True the key is the lowercased token, otherwise
    the original token. First-seen order is preserved for determinism; the
    final claim sort makes order irrelevant to output but preserves a stable
    processing order.
    """
    entities: list[tuple[str, str]] = []
    seen: set[str] = set()
    for token in re.findall(pattern, query_text):
        if len(token) < min_len:
            continue
        lower_token = token.lower()
        if lower_token in stopwords:
            continue
        key = lower_token if case_fold else token
        if key in seen:
            continue
        seen.add(key)
        entities.append((token, key))
    return entities


def _entity_re(token: str) -> re.Pattern[str]:
    """Compile a word-boundary regex for an entity token (escaped)."""
    return re.compile(r"\b" + re.escape(token) + r"\b")


def extract_claims(query_text: str, evidence: EvidenceSet) -> CandidateClaims:
    """Deterministically construct the candidate-claim set from evidence.

    Determinism: identical inputs -> identical output; empty evidence -> empty
    claims; nonexistent-entity / topic-only evidence yields no claim (the
    CF-R2/FM-1 pressure case). Every claim's ``supporting_doc_ids`` is by
    construction a subset of the doc_ids present in the input ``EvidenceSet``.
    Pure: no I/O, no network, no wall-clock, no env-var reads, no randomness,
    no global mutable state, no input mutation.
    """
    params = _resolve_params()
    stopwords = params["stopwords"]
    min_len = params["min_entity_token_length"]
    pattern = params["entity_token_pattern"]
    case_fold = params["case_fold"]
    template = params["claim_template"]

    entities = _extract_query_entities(query_text, pattern, stopwords, min_len, case_fold)
    if not entities:
        return CandidateClaims(claims=())

    # Pre-compute the (doc_id, match-text) view of the evidence once. The
    # match text is lowercased iff case_fold; the original item.text is never
    # mutated (str.lower returns a new string).
    evidence_view: list[tuple[str, str]] = []
    for item in evidence:
        match_text = item.text.lower() if case_fold else item.text
        evidence_view.append((item.doc_id, match_text))

    compiled: dict[str, re.Pattern[str]] = {}
    claims: list[CandidateClaim] = []
    seen_claims: set[tuple[str, tuple[str, ...]]] = set()
    for entity_original, entity_key in entities:
        match_token = entity_key if case_fold else entity_original
        regex = compiled.get(match_token)
        if regex is None:
            regex = _entity_re(match_token)
            compiled[match_token] = regex
        supporting: set[str] = set()
        for doc_id, match_text in evidence_view:
            if regex.search(match_text):
                supporting.add(doc_id)
        if not supporting:
            # Entity absent from every evidence item: no claim (entity-level,
            # not topic-level -- the FM-1/CF-R2 guard).
            continue
        supporting_doc_ids = tuple(sorted(supporting))
        claim_text = template.format(entity=entity_original, query=query_text)
        claim_key = (claim_text, supporting_doc_ids)
        if claim_key in seen_claims:
            continue
        seen_claims.add(claim_key)
        claims.append(
            CandidateClaim(
                claim_text=claim_text,
                supporting_doc_ids=supporting_doc_ids,
            )
        )

    claims.sort(key=lambda c: (c.claim_text, c.supporting_doc_ids))
    return CandidateClaims(claims=tuple(claims))


__all__ = ["extract_claims"]

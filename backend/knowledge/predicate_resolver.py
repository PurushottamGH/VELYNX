"""
VELYNX — Predicate Synonym Resolver
====================================

The cognitive graph stores facts as ``(subject, predicate, object)`` triples
where the predicate is a *relation verb* ("create", "be", "located_in", ...).
The same semantic relation, however, surfaces in many grammatical shapes:

    "Who **created** Blender?"   root lemma  ->  create
    "Who **authored** Blender?"                ->  author   (then -> create)
    "Who **built** Blender?"                   ->  build    (then -> create)
    "Blender **is** software."                 ->  be
    "Blender **was** software."                ->  was      (then -> be)

Without a single canonical form on **both** the write path (what gets stored)
and the read path (what the query asks for), vocabulary mismatch fractures the
graph: a fact stored under ``create`` is invisible to a query phrased with
``authored``, even though they mean the same thing. This is the
"Predicate Grounding / Synonym" bug — ``ton roosendaal -[create]-> blender``
exists in the graph, yet "Who created Blender?" fails because nothing maps the
query verb onto the stored predicate.

This module owns predicate vocabulary end-to-end:

* :class:`PredicateSynonymResolver` collapses synonymous verbs / verb-phrases
  onto one *core predicate* ("create", "be", "located_in", ...).
* :func:`extract_predicate` lifts the main relation verb out of a user query
  and resolves it to its core form.
* :func:`predicates_match` decides whether a query predicate and a stored
  predicate refer to the same relation, so retrieval can ground the user's
  intent against the graph.

Design notes
------------
* **Local + deterministic.** A plain in-memory synonym table — no model, no
  network. Safe to call on every token of every query.
* **Symmetric convergence.** Both the consolidator (write) and the reasoning
  wiring (read) route the relation through :meth:`resolve`, so a fact written
  under any synonym is matched by a query phrased with any other synonym. That
  convergence is the whole point.
* **Lemmatized-friendly.** The fact extractor already lemmatizes verbs via
  spaCy (``root.lemma_``), so stored predicates are usually bare ("create",
  "be"). The resolver is keyed on those lemmas but also accepts inflected /
  multi-word surface forms ("created", "created by", "written by").
* **Conservative fallback.** An unknown verb is returned lowercased with
  separators normalized, never silently collapsed to a wrong core predicate.
"""
from __future__ import annotations

import re
from typing import Iterable

# Collapse internal whitespace; used to canonicalize lookup keys.
_WS_RE = re.compile(r"\s+")
# Token splitter for query-verb extraction.
_WORD_RE = re.compile(r"[a-zA-Z]+")
# Multi-word verb phrases we recognise when scanning a query, longest first so
# "created by" wins over the bare "created" during leftmost-longest matching.
_PHRASE_RE = re.compile(
    r"\b("
    r"created by|written by|made by|built by|developed by|designed by|"
    r"founded by|authored by|invented by|established by|"
    r"is a|is an|is the|was a|was an|was the|are a|are an|are the|"
    r"located in|based in|born in|lives in|works at"
    r")\b",
    re.IGNORECASE,
)

# ── Question frames whose verb carries the relation the user is asking about.
# A leading wh-word, an optional true auxiliary (do/did/can/will/...), then the
# main verb. The be-verbs (is/are/was/were) are deliberately NOT treated as
# auxiliaries here: in "What is X?" / "Where is Y?" the copula IS the relation
# verb we want to capture ("be"), not a helper to strip.
_QUESTION_VERB_RE = re.compile(
    r"^\s*(?:who|what|which|where|when|why|how|whom)\s+"
    r"(?:(?:did|do|does|can|could|will|would|should|shall|may|might|must)\s+)?"
    r"([a-z]+)",
    re.IGNORECASE,
)


class PredicateSynonymResolver:
    """Collapse synonymous relation verbs onto a single core predicate.

    The synonym table maps a *lowercased, space-normalized* surface form to its
    core predicate. Resolution is idempotent: every core predicate maps to
    itself, so resolving twice is a no-op.
    """

    # synonym (lowercased)            -> core predicate
    DEFAULT_SYNONYMS: dict[str, str] = {
        # ── create / author / build family ─────────────────────────────────
        "create": "create",
        "creates": "create",
        "created": "create",
        "creating": "create",
        "creator": "create",
        "create by": "create",
        "created by": "create",
        "author": "create",
        "authors": "create",
        "authored": "create",
        "authoring": "create",
        "authored by": "create",
        "write": "create",
        "writes": "create",
        "wrote": "create",
        "written": "create",
        "writing": "create",
        "written by": "create",
        "build": "create",
        "builds": "create",
        "built": "create",
        "building": "create",
        "built by": "create",
        "make": "create",
        "makes": "create",
        "made": "create",
        "making": "create",
        "made by": "create",
        "design": "create",
        "designs": "create",
        "designed": "create",
        "designed by": "create",
        "develop": "create",
        "develops": "create",
        "developed": "create",
        "developed by": "create",
        "developer": "create",
        "invent": "create",
        "invents": "create",
        "invented": "create",
        "invented by": "create",
        "inventor": "create",
        "found": "create",
        "founds": "create",
        "founded": "create",
        "founding": "create",
        "founder": "create",
        "founded by": "create",
        "establish": "create",
        "establishes": "create",
        "established": "create",
        "established by": "create",
        # ── be / copula family ──────────────────────────────────────────────
        "be": "be",
        "is": "be",
        "are": "be",
        "was": "be",
        "were": "be",
        "am": "be",
        "been": "be",
        "being": "be",
        "is a": "be",
        "is an": "be",
        "is the": "be",
        "was a": "be",
        "was an": "be",
        "are a": "be",
        "are an": "be",
        # ── located / place family ─────────────────────────────────────────
        "located": "located_in",
        "located in": "located_in",
        "located at": "located_in",
        "based": "located_in",
        "based in": "located_in",
        "headquartered": "located_in",
        "headquartered in": "located_in",
        "lives": "located_in",
        "lives in": "located_in",
        "resides": "located_in",
        "resides in": "located_in",
        "born": "located_in",
        "born in": "located_in",
        "works": "located_in",
        "works at": "located_in",
        "works in": "located_in",
    }

    def __init__(self, synonyms: dict[str, str] | None = None) -> None:
        source = synonyms if synonyms is not None else self.DEFAULT_SYNONYMS
        # Fold keys to a canonical lookup form so callers can't inject mixed-
        # case / odd-whitespace keys that would silently miss.
        self._synonyms: dict[str, str] = {
            self._key(k): self._norm(v) for k, v in source.items()
        }

    # ── Helpers ───────────────────────────────────────────────────────────
    @staticmethod
    def _key(text: str) -> str:
        """Lowercase + collapse/trim whitespace — the canonical lookup key."""
        return _WS_RE.sub(" ", str(text or "").strip().lower())

    @staticmethod
    def _norm(predicate: str) -> str:
        """Canonical storage form for a core predicate: lowercase, underscores."""
        return _WS_RE.sub("_", str(predicate or "").strip().lower())

    # ── Public API ────────────────────────────────────────────────────────
    def resolve(self, predicate: str) -> str:
        """Return the core predicate for ``predicate``.

        Resolution order:
          1. Exact synonym-table hit (handles "created by", "authored", ...).
          2. Strip a trailing " by" agent marker and retry ("authored by" ->
             "authored" -> "create"); also collapses "is a"/"was a" tails.
          3. Unknown verb -> returned lowercased with separators normalized
             (so "located_in" and "located in" converge), never mapped to a
             wrong core predicate.

        Empty input returns ``""``. The result is always idempotent.
        """
        if predicate is None:
            return ""
        key = self._key(predicate)
        if not key:
            return ""

        # 1. Direct hit.
        core = self._synonyms.get(key)
        if core is not None:
            return core

        # 2. Drop a trailing agent ("by") or determiner ("a"/"an"/"the") and
        #    retry, so a phrase we only key in its short form still resolves.
        trimmed = re.sub(r"\s+(by|a|an|the)$", "", key)
        if trimmed != key:
            core = self._synonyms.get(trimmed)
            if core is not None:
                return core

        # 3. Unknown — normalize separators only.
        return self._norm(predicate)

    def is_synonym(self, predicate: str) -> bool:
        """True when ``predicate`` resolves to a *different* core form."""
        key = self._key(predicate)
        core = self._synonyms.get(key)
        return core is not None and core != key

    def add_synonym(self, synonym: str, core: str) -> None:
        """Register a new ``synonym -> core`` mapping at runtime."""
        self._synonyms[self._key(synonym)] = self._norm(core)

    def predicates_match(self, query_predicate: str, stored_predicate: str) -> bool:
        """True when ``query_predicate`` and ``stored_predicate`` are the same relation.

        Both sides are resolved to their core form, so a query for "created"
        matches a stored "create", "authored", "built", etc. Two empty
        predicates are considered non-matching (no signal) so a missing query
        verb never masquerades as a universal match.
        """
        q = self.resolve(query_predicate)
        s = self.resolve(stored_predicate)
        if not q or not s:
            return False
        return q == s


# Process-wide singleton. Import this everywhere so write and read paths share
# one synonym table (and any runtime-registered synonyms).
predicate_resolver = PredicateSynonymResolver()


# ── Query-side helpers ───────────────────────────────────────────────────────
# Tokens that carry no relation signal — stripped before assuming a leftover
# word is the query's main verb.
_FILLER_WORDS = frozenset({
    "who", "what", "which", "where", "when", "why", "how", "whom",
    "the", "a", "an", "of", "to", "in", "on", "at", "for", "by", "with",
    "is", "are", "was", "were", "did", "do", "does", "can", "could",
    "will", "would", "should", "about",
})


def extract_predicate(text: str) -> str:
    """Lift the main relation verb out of a user query and resolve it.

    Tries the highest-signal patterns first, falling back gracefully:

      1. A recognised multi-word verb phrase anywhere in the text
         ("created by", "written by", "is a", "located in", ...).
      2. A question frame: "<wh-word> [aux] [chunk] <verb> ..."
         ("Who created Blender?" -> "created").
      3. The first non-filler token in the sentence.

    The extracted surface verb is then passed through the resolver, so the
    return value is always a *core* predicate ("create", "be", ...) — or ``""``
    when no relation verb can be identified.

    This is intentionally lightweight (regex only, no spaCy) because the
    read path runs on every query; the heavy parse already happened at write
    time in ``fact_extractor``.
    """
    if not text or not text.strip():
        return ""

    lowered = text.lower()

    # 1. Longest recognised multi-word phrase.
    phrases = _PHRASE_RE.findall(lowered)
    if phrases:
        # Leftmost match wins; regex alternation is leftmost-longest.
        return predicate_resolver.resolve(phrases[0])

    # 2. Question-frame verb.
    m = _QUESTION_VERB_RE.match(lowered)
    if m:
        verb = m.group(1).strip()
        if predicate_resolver.resolve(verb):
            return predicate_resolver.resolve(verb)

    # 3. First content token.
    for tok in _WORD_RE.findall(lowered):
        if tok in _FILLER_WORDS:
            continue
        core = predicate_resolver.resolve(tok)
        if core and core != tok:
            # Only accept tokens we actually know how to canonicalize, so a
            # bare entity name ("Blender?") isn't mistaken for a verb.
            return core
    return ""


def predicates_match(query_predicate: str, stored_predicate: str) -> bool:
    """Module-level convenience wrapper around the shared resolver."""
    return predicate_resolver.predicates_match(query_predicate, stored_predicate)


__all__ = [
    "PredicateSynonymResolver",
    "predicate_resolver",
    "extract_predicate",
    "predicates_match",
]

"""Reasoning wiring — concept extraction, triple retrieval, thermodynamic state."""
from __future__ import annotations

from typing import Any

from backend.pipeline import intent_engine
from backend.knowledge.normalizer import concept_normalizer
from backend.knowledge.predicate_resolver import (
    extract_predicate,
    predicate_resolver,
)

# Maps the synthesizer's confidence taxonomy onto the pipeline's existing
# CERTAIN/PROBABLE/DEBATED/LOW/UNKNOWN labels used by downstream logic.
SYNTH_CONFIDENCE_MAP = {
    "CERTAIN": "CERTAIN",
    "PROBABLE": "PROBABLE",
    "UNCERTAIN": "DEBATED",
    "SPECULATIVE": "LOW",
    "INSUFFICIENT": "UNKNOWN",
}

# Phase 55 — Working Memory. Pronouns whose referent lives in the *previous*
# turns rather than the current message. When one of these appears as a
# standalone token, the message is "context-dependent": its real subject is
# whatever the conversation was just about, so we pull active concepts from the
# working-memory buffer to resolve it.
_REFERENTIAL_PRONOUNS = frozenset({
    "it", "its", "it's",
    "they", "them", "their", "theirs",
    "he", "him", "his",
    "she", "her", "hers",
    "this", "that", "these", "those",
    "there", "here",
    "one", "ones",
})

# Strip punctuation so "it?" / "there." / "it's" still match.
import re as _re

_TOKEN_RE = _re.compile(r"[a-z']+")


# Interrogative (WH) words and closed-class auxiliaries. Used both as a direct
# drop-list and as the spaCy-unavailable fallback. Verbs proper are open-class
# and cannot be enumerated — they are removed via POS tagging when spaCy is
# present (see :func:`_query_drop_terms`).
_WH_WORDS = frozenset({
    "who", "what", "when", "where", "why", "how", "which", "whom", "whose",
})
_AUX_WORDS = frozenset({
    "is", "are", "was", "were", "be", "been", "being", "am",
    "do", "does", "did", "has", "have", "had",
    "will", "would", "shall", "should", "can", "could", "may", "might", "must",
})


# Phase 62 — First-person possessive resolution (READ PATH). Mirrors the write
# path's ``fact_extractor._PRONOUN_POSSESSIVE`` so a query phrased with "my ..."
# lands on the exact canonical subject node the write path stored. Teaching
# "My favorite movie is Interstellar" stores the subject "User's favorite movie"
# (folded to "user's favorite movie" at lookup); the query "What is my favorite
# movie?" must therefore resolve "my favorite movie" -> "User's favorite movie"
# as a SINGLE concept rather than the disconnected fragments ["favorite", "movie"].
_QUERY_POSSESSIVE = {"my": "User's", "mine": "User's"}

# spaCy possessive-pronoun tag (e.g. "my", "your", "their"); we only act on the
# first-person forms enumerated in ``_QUERY_POSSESSIVE``.
_POSSESSIVE_TAG = "PRP$"

# Closed-class words that bound a possessive noun phrase in the spaCy-unavailable
# regex fallback (so "my favorite cafe is closed" does not absorb "is closed").
_NP_BOUNDARY = frozenset(_AUX_WORDS) | {
    "and", "or", "but", "of", "in", "on", "at", "to", "for", "with",
    "located", "situated", "near", "from", "that", "which",
}


def _extract_possessive_phrases(text: str) -> tuple[list[str], set[str]]:
    """Group a first-person possessive noun phrase into ONE canonical concept.

    "What is my favorite movie?"  -> phrase "User's favorite movie"
    "Where is my favorite cafe?"  -> phrase "User's favorite cafe"

    The leading possessive ("my"/"mine") is rewritten to "User's" to mirror the
    write path (:data:`fact_extractor._PRONOUN_POSSESSIVE`), so the query concept
    is byte-for-byte the canonical subject node the fact was stored under.

    Returns
    -------
    (phrases, consumed)
        ``phrases``  — the rewritten possessive noun phrases (e.g. one entry
                       ``"User's favorite movie"``).
        ``consumed`` — the lowercased surface forms of EVERY word folded into a
                       phrase (including the original "my"), so the caller can
                       drop the bare fragments ("favorite", "movie") that the
                       keyword tokenizer would otherwise emit as disconnected,
                       unconnectable nodes.

    Deterministic and never raises. Uses spaCy noun chunks for accurate NP
    boundaries; falls back to a bounded regex when the model is unavailable.
    """
    if not text or not text.strip():
        return [], set()

    try:
        from backend.knowledge.fact_extractor import _get_nlp

        doc = _get_nlp()(text)
    except Exception:
        return _fallback_possessive_phrases(text)

    phrases: list[str] = []
    consumed: set[str] = set()
    for chunk in doc.noun_chunks:
        head = chunk[0]
        if head.tag_ != _POSSESSIVE_TAG or head.text.lower() not in _QUERY_POSSESSIVE:
            continue
        words = [_QUERY_POSSESSIVE[head.text.lower()]]
        for tok in chunk[1:]:
            if tok.is_punct:
                continue
            words.append(tok.text)
        # Need the possessive + at least one noun to form a real phrase.
        if len(words) < 2:
            continue
        phrases.append(" ".join(words).strip())
        for tok in chunk:
            consumed.add(tok.text.lower())
    return phrases, consumed


def _fallback_possessive_phrases(text: str) -> tuple[list[str], set[str]]:
    """Regex fallback for :func:`_extract_possessive_phrases` (no spaCy).

    Captures the run of words immediately following a first-person possessive,
    stopping at a clause boundary / auxiliary so we do not swallow a trailing
    verb phrase. Less precise than the dependency parse but keeps the read path
    functional when the model is missing.
    """
    phrases: list[str] = []
    consumed: set[str] = set()
    for m in _re.finditer(r"\b(my|mine)\b\s+(.+?)(?=[?.!,;]|$)", text, _re.IGNORECASE):
        poss = m.group(1).lower()
        tail_words = _re.findall(r"[A-Za-z']+", m.group(2))
        np_words: list[str] = []
        for w in tail_words:
            if w.lower() in _NP_BOUNDARY:
                break
            np_words.append(w)
        if not np_words:
            continue
        phrases.append(" ".join([_QUERY_POSSESSIVE[poss], *np_words]).strip())
        consumed.add(poss)
        consumed.update(w.lower() for w in np_words)
    return phrases, consumed


def _query_drop_terms(text: str) -> set[str]:
    """Surface forms (and lemmas) in ``text`` that must NOT become graph concepts.

    A WH-question like "Who created Blender?" must reason over "Blender" only —
    the interrogative "who" and the predicate verb "created" are relations/frames,
    not nodes. We POS-tag the *full query* (reliable, in-context) and drop any
    VERB / AUX token plus WH-tagged tokens, returning both the surface form and
    the lemma so "created"/"create" are both removed. When spaCy is unavailable
    we fall back to the closed-class WH + auxiliary words (open-class verbs can
    only be detected with a parser).
    """
    drop: set[str] = set(_WH_WORDS) | set(_AUX_WORDS)
    try:
        from backend.knowledge.fact_extractor import _get_nlp

        doc = _get_nlp()(text or "")
    except Exception:
        return drop  # spaCy/model not available — closed-class fallback only
    for tok in doc:
        if tok.pos_ in ("VERB", "AUX") or tok.tag_ in ("WP", "WP$", "WRB", "WDT"):
            drop.add(tok.text.lower())
            if tok.lemma_:
                drop.add(tok.lemma_.lower())
    return drop


def contains_unresolved_pronoun(text: str) -> bool:
    """True when ``text`` contains a standalone referential pronoun.

    Tokenizes on word boundaries (so trailing punctuation is ignored) and
    checks each token against :data:`_REFERENTIAL_PRONOUNS`. This is a cheap,
    deterministic heuristic — it intentionally errs toward injecting context,
    since extra active concepts are harmless to the reasoner but missing ones
    cause amnesia.
    """
    for token in _TOKEN_RE.findall((text or "").lower()):
        if token in _REFERENTIAL_PRONOUNS:
            return True
    return False


def extract_query_concepts(
    text: str,
    intent: dict,
    soul_concepts: list[str],
    working_memory_concepts: list[str] | None = None,
) -> list[str]:
    """
    Build the list of entities/concepts to reason over.

    Sources, in priority order:
      1. Soul concepts already activated for this query.
      2. Named entities (proper nouns + quoted spans) from the intent engine.
      3. Content keywords from the intent tokenizer (stop-words removed).
      4. (Phase 55) Working-memory concepts — injected only when the message
         contains an unresolved referential pronoun ("it", "there", "he", ...),
         so a follow-up like "where is it?" inherits the previous turn's topic.

    Order is preserved and duplicates (case-insensitive) are dropped.
    """
    candidates: list[str] = []
    candidates.extend(soul_concepts or [])

    # Phase 62 — First-person possessive grouping (READ PATH). Group "my <noun
    # phrase>" into a SINGLE concept and rewrite "my" -> "User's" so the query
    # resolves to the same canonical subject node the write path stored
    # ("User's favorite movie"). The member words are recorded so the bare
    # fragments the keyword tokenizer emits ("favorite", "movie") are dropped
    # below instead of becoming disconnected, unconnectable graph nodes.
    possessive_phrases, possessive_tokens = _extract_possessive_phrases(text)
    candidates.extend(possessive_phrases)

    entities = intent.get("entities") or {}
    # Phase 63 — Multi-word named-entity grouping (READ PATH). Prefer the FULL
    # proper-noun phrase ("Driftwood OS") over its constituent tokens
    # ("Driftwood", "OS"). Putting the phrases FIRST means the most-specific
    # concept the pipeline keys on (and tags a QUERY_FAILURE episode with —
    # ``query_concepts[-1]``) is the whole entity, never a stray trailing token.
    # Without this, "Who created Driftwood OS?" tagged the failure to the entity
    # "os", and the later "How did you learn ...?" narrative resolved to "os"
    # and reported it had never learned about it (the Interaction #21 bug).
    proper_noun_phrases = entities.get("proper_noun_phrases", []) or []
    # Only the genuinely MULTI-word phrases need explicit grouping/fragment
    # suppression; single-word proper nouns already flow through unchanged.
    multiword_phrases = [p for p in proper_noun_phrases if len(p.split()) > 1]
    candidates.extend(multiword_phrases)
    # Record the lowercased constituent tokens of each grouped phrase so the
    # bare fragments the proper_nouns list / keyword tokenizer emit ("driftwood",
    # "os") are dropped below — exactly as the possessive grouping does — leaving
    # the single grouped "Driftwood OS" concept to stand alone.
    phrase_tokens: set[str] = set()
    for phrase in multiword_phrases:
        for word in phrase.split():
            phrase_tokens.add(word.lower())

    candidates.extend(entities.get("proper_nouns", []) or [])
    candidates.extend(entities.get("quoted", []) or [])

    try:
        candidates.extend(intent_engine._keywords(text) or [])
    except Exception:
        candidates.extend(w for w in text.split() if len(w) > 2)

    # Phase 55 — INJECTION POINT. Only pull short-term context when the current
    # message actually depends on it (an unresolved pronoun). Appending after
    # the in-message sources means real entities in *this* turn still take
    # precedence; the working-memory concepts fill the referential gap.
    if working_memory_concepts and contains_unresolved_pronoun(text):
        candidates.extend(working_memory_concepts)

    # WH-question fix — compute the drop set ONCE for this query. WH-pronouns
    # ("who"/"what"/...), auxiliaries ("is"/"did"/...) and predicate verbs
    # ("created"/"create") are relations or interrogative frames, never graph
    # nodes. They leak in via two paths: the proper-noun regex capitalizes the
    # sentence-initial WH-word ("Who created Blender?" -> proper_noun "Who"),
    # and the keyword tokenizer keeps open-class verbs ("created"). Filtering
    # candidates against this set ensures "Who created Blender?" reasons over
    # "Blender" alone instead of searching for non-existent "Who"/"created"
    # nodes (which produced the "no connecting evidence" dead end).
    drop_terms = _query_drop_terms(text)
    # Suppress the bare member words of any grouped possessive phrase ("favorite",
    # "movie") so they cannot re-enter as disconnected fragments competing with
    # the grouped "User's favorite movie" concept. The multi-word phrase itself
    # is never in ``drop_terms`` (which holds single tokens), so it survives.
    drop_terms |= possessive_tokens
    # Suppress the bare constituent tokens of any grouped multi-word proper-noun
    # phrase ("driftwood", "os") so they cannot re-enter as disconnected
    # fragments competing with the grouped "Driftwood OS" concept. The multi-word
    # phrase itself is never in ``drop_terms`` (single tokens only), so it
    # survives and remains the most-specific concept.
    drop_terms |= phrase_tokens

    seen: set[str] = set()
    concepts: list[str] = []
    for c in candidates:
        label = str(c).strip()
        if not label:
            continue
        # Drop WH-words / auxiliaries / verbs before they can become concepts.
        if label.lower() in drop_terms:
            continue
        # Phase 54 — Semantic normalization (READ PATH). Resolve query synonyms
        # to the canonical surface form the write path stored, so "Bangalore"
        # finds facts taught as "Bengaluru". preserve_case=True keeps proper-noun
        # casing for unmatched tokens; retrieve_triples lowercases at lookup.
        label = concept_normalizer.normalize(label, preserve_case=True)
        if not label:
            continue
        key = label.lower()
        if key in seen:
            continue
        seen.add(key)
        concepts.append(label)
    return concepts


def retrieve_triples(
    concepts: list[str],
    symbolic_kg: Any,
    query: str | None = None,
) -> list[dict]:
    """
    Pull (subject, predicate, object) triples connected to the query concepts
    from the deterministic symbolic knowledge graph. Returns a list of dicts in
    the shape the :class:`ReasoningEngine` normalizes natively. Never raises.

    Predicate grounding (the synonym fix): when ``query`` is supplied, the main
    relation verb is extracted from it and resolved to its core predicate, then
    triples whose predicate is the same relation are given a confidence BOOST so
    the reasoner prefers the fact that actually answers the question. This is
    what lets "Who *created* Blender?" match a stored ``ton roosendaal
    -[create]-> blender`` edge even though the surface verbs differ.
    """
    if symbolic_kg is None or not concepts:
        return []

    # Lift the user's relation verb once (cheap regex, no model) and resolve it
    # to its core predicate so it can be compared to stored edges.
    query_predicate = ""
    if query:
        try:
            query_predicate = extract_predicate(query)
        except Exception:
            query_predicate = ""

    triples: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for concept in concepts:
        try:
            # Phase 54 — normalize at the lookup boundary so callers that bypass
            # extract_query_concepts still hit canonical nodes. get_related keys
            # on the lowercased canonical form the write path stored.
            canonical = concept_normalizer.normalize(concept)
            related = symbolic_kg.get_related(canonical.lower())
        except Exception:
            continue
        for rel in related or []:
            subj = rel.get("source", "")
            pred = rel.get("relation", "")
            obj = rel.get("target", "")
            if not subj or not pred or not obj:
                continue
            key = (subj.lower(), pred.lower(), obj.lower())
            if key in seen:
                continue
            seen.add(key)

            # Predicate grounding: reward edges whose relation is the same
            # core predicate as the query verb. The boost lifts the matching
            # triple above competing, merely-adjacent edges so the reasoner
            # carries it on the winning path. When no query predicate was
            # identified (or the edge predicates differ), leave the base
            # confidence unchanged — the triple is still admissible evidence.
            confidence = 0.8
            if query_predicate and predicate_resolver.predicates_match(
                query_predicate, pred
            ):
                confidence = 0.95

            triples.append({
                "subject": subj,
                "predicate": pred,
                "object": obj,
                "confidence": confidence,
                "source": "knowledge_graph",
            })
    return triples


def compute_thermodynamic_state(
    conflicts: dict | None, source_count: int
) -> float:
    """
    Derive the system's thermodynamic state (energy/chaos) in ``[0, 1]``.

    The engine uses this to decide how strict vs. exploratory traversal should
    be. We raise the temperature when evidence conflicts or is sparse (the
    system must explore harder), and keep it cool when evidence is plentiful
    and consistent (the system can be conservative).
    """
    state = 0.30
    if conflicts:
        n_conflicts = len(conflicts.get("conflicts", []))
    else:
        n_conflicts = 0
    state += 0.12 * n_conflicts
    if source_count <= 1:
        state += 0.25
    elif source_count <= 3:
        state += 0.10
    return max(0.0, min(1.0, state))

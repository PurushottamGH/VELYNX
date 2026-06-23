"""
VELYNX Phase 53 — Knowledge Acquisition Engine
===============================================

VELYNX has historically been "deaf" to new facts: when the user *states*
something ("My favorite coffee shop is Third Wave"), the pipeline treated it as
a *query*, traversed the graph, found nothing, and reported a broken logic
path. This module closes that gap.

It uses spaCy dependency parsing to intercept declarative statements, extract
``(Subject, Predicate, Object)`` triples, perform lightweight first-person
pronoun resolution (``I`` / ``My`` -> ``User``), and write the triples directly
into the existing Knowledge Graph ``triples`` table.

Public API
----------
``extract_and_store_facts(text: str) -> list[tuple[str, str, str]]``
    Extract S-V-O triples from ``text`` and persist them. Returns the list of
    triples that were committed (empty if nothing extractable was found).

``extract_triples(text: str) -> list[tuple[str, str, str]]``
    Pure extraction (no DB writes) — exposed for testing / inspection.

Design notes
------------
* The spaCy model (``en_core_web_sm``) is loaded lazily and cached, so importing
  this module is cheap and never blocks application startup.
* Persistence uses the shared :func:`backend.memory._sqlite.connect` helper
  (imported here as ``open_connection``) so we inherit WAL + busy_timeout and
  stay consistent with every other writer in the memory stack.
* Triples are stored with ``confidence = 0.9`` and ``source = "user_statement"``
  to mark them as high-trust, user-asserted knowledge.
"""
from __future__ import annotations

import logging
import re
import time
from pathlib import Path
from typing import List, Optional, Tuple

from backend.memory._sqlite import connect as open_connection
from backend.knowledge.predicate_resolver import predicate_resolver

logger = logging.getLogger("velynx.fact_extractor")

# ── Constants ────────────────────────────────────────────────────────────────
CONFIDENCE: float = 0.9
SOURCE: str = "user_statement"

# First-person pronoun resolution. Subject-position pronouns resolve to the
# bare entity "User"; possessive pronouns resolve to "User's" so the resulting
# subject phrase reads naturally (e.g. "My favorite shop" -> "User's favorite
# shop"). Both ultimately anchor on the "User" entity.
_PRONOUN_SUBJECT = {"i": "User", "me": "User", "myself": "User"}
_PRONOUN_POSSESSIVE = {"my": "User's", "mine": "User's"}


def resolve_first_person_coref(phrase: str) -> str:
    """Map a leading first-person pronoun in *phrase* to its user-centric form.

    This is the single source of truth for the coreference rule the TEACH /
    knowledge-acquisition pipeline applies when it stores facts, so any consumer
    (e.g. the multi-hop agentic planner) can normalise a referent the EXACT same
    way before searching the Knowledge Graph. Without this, a planner that
    searches for the literal string "my favorite software" misses the fact the
    TEACH path stored under "User's favorite software".

    Only the LEADING token is rewritten (mirroring ``_resolve_subject_phrase``):

        "I"             -> "User"
        "me" / "myself" -> "User"
        "My favorite software" -> "User's favorite software"
        "mine"          -> "User's"

    A leading determiner ("the my favorite software") is stripped first so the
    pronoun is still recognised. Phrases without a leading first-person pronoun
    are returned unchanged (whitespace-normalised).
    """
    if not phrase or not phrase.strip():
        return phrase or ""
    words = phrase.split()
    # Strip a stray leading determiner so "the my favorite software" still maps.
    if words and words[0].lower() in {"the", "a", "an"} and len(words) > 1:
        second = words[1].lower()
        if second in _PRONOUN_SUBJECT or second in _PRONOUN_POSSESSIVE:
            words = words[1:]
    if not words:
        return phrase.strip()

    first_low = words[0].lower()
    rest = words[1:]
    if first_low in _PRONOUN_SUBJECT:
        head = _PRONOUN_SUBJECT[first_low]
        return f"{head} {' '.join(rest)}".strip() if rest else head
    if first_low in _PRONOUN_POSSESSIVE:
        head = _PRONOUN_POSSESSIVE[first_low]
        return f"{head} {' '.join(rest)}".strip() if rest else head
    return " ".join(words).strip()

# Auxiliary / copula verbs that must never form part of a subject phrase. Used
# to scrub subjects produced by the regex fallback, where a non-greedy capture
# can still absorb a trailing auxiliary (e.g. "supermegasoftware was" out of
# "supermegasoftware was created by ..."). The dependency path handles these via
# the aux/auxpass dependency labels instead (see ``_AUX_DEPS``).
_AUXILIARY_WORDS = {
    "is", "was", "were", "are", "am", "be", "been", "being",
    "has", "have", "had",
    "do", "does", "did",
    "will", "would", "shall", "should",
    "can", "could", "may", "might", "must",
}


def _strip_auxiliaries(phrase: str) -> str:
    """Remove leading/trailing auxiliary verbs from a regex-derived subject."""
    words = phrase.split()
    while words and words[0].lower() in _AUXILIARY_WORDS:
        words.pop(0)
    while words and words[-1].lower() in _AUXILIARY_WORDS:
        words.pop()
    return " ".join(words)

# Fallback patterns: regex + flag indicating whether the relation group already
# includes a preposition (e.g. "lives in" rather than bare "live").  These are
# applied when the dependency parse yields zero triples for a sentence.
_FALLBACK_PATTERNS: List[Tuple[re.Pattern, bool]] = [
    # "X lives in Y", "X works at Y", "X resides in Y", "X hails from Y"
    (re.compile(r"^(.+?)\s+(lives?\s+in|works?\s+(?:at|in)|resides?\s+in|stays?\s+(?:at|in)|hails?\s+from)\s+(.+?)\.?\s*$", re.IGNORECASE), True),  # fmt: skip
    # "X is Y" (attribution / identification). The verb is captured as its own
    # group so every fallback pattern exposes the same 3 groups (subject, verb,
    # object) — group(3) is always valid.
    (re.compile(r"^(.+?)\s+(is)\s+(.+?)\.?\s*$", re.IGNORECASE), False),  # fmt: skip
    # "X created Y", "X built Y", "X designed Y" (transitive actions)
    (re.compile(r"^(.+?)\s+(created|built|made|designed|developed|wrote|founded)\s+(.+?)\.?\s*$", re.IGNORECASE), False),  # fmt: skip
    # "X has Y", "X owns Y", "X runs Y" (possession / operation)
    (re.compile(r"^(.+?)\s+(has|owns?|runs?|manages?|operates?)\s+(.+?)\.?\s*$", re.IGNORECASE), False),  # fmt: skip
]

# Dependency labels that mark a usable object/complement of the ROOT verb.
_OBJECT_DEPS = {"dobj", "attr", "oprd", "dative", "acomp"}

# Auxiliary-verb markers that must never leak into a subject phrase. In passive
# or unknown-token parses spaCy can attach an auxiliary (e.g. the "was" in
# "supermegasoftware was created") inside the subject's subtree; without this
# filter the subject would come back as "supermegasoftware was".
_AUX_DEPS = {"aux", "auxpass"}
_AUX_POS = "AUX"

# spaCy model handle — loaded lazily and cached.
_NLP = None


# ── DB path resolution ─────────────────────────────────────────────────────────
def _resolve_kg_db_path() -> Path:
    """
    Resolve the path of the Knowledge Graph database that owns the ``triples``
    table. We reuse the memory KnowledgeGraph's configured location so facts
    land exactly where the rest of the stack already reads triples from.
    """
    try:
        from backend.memory.knowledge_graph import _DB_PATH  # type: ignore

        return Path(_DB_PATH)
    except Exception:  # pragma: no cover - defensive fallback
        return Path("velynx_state.db")


_KG_DB_PATH = _resolve_kg_db_path()

# Mirrors the existing `triples` schema in the Knowledge Graph DB so this module
# is self-sufficient even against a freshly created database.
_TRIPLES_SCHEMA = """
CREATE TABLE IF NOT EXISTS triples (
    id INTEGER PRIMARY KEY,
    subject TEXT NOT NULL,
    relation TEXT NOT NULL,
    object TEXT NOT NULL,
    confidence REAL,
    source TEXT,
    timestamp REAL,
    UNIQUE(subject, relation, object)
)
"""

# Enforces the dedup constraint on legacy DBs whose `triples` table predates the
# inline UNIQUE clause. Mirrors the index created by the memory KnowledgeGraph.
_TRIPLES_UNIQUE_INDEX = (
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_triples_unique "
    "ON triples(subject, relation, object)"
)


def _get_nlp():
    """Lazily load and cache the spaCy English model."""
    global _NLP
    if _NLP is None:
        import spacy  # imported lazily — heavy dependency

        try:
            _NLP = spacy.load("en_core_web_sm")
        except OSError as exc:  # model not downloaded
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' is not installed. "
                "Install it with: python -m spacy download en_core_web_sm"
            ) from exc
    return _NLP


# ── Pronoun resolution ─────────────────────────────────────────────────────────
def _resolve_subject_phrase(tokens) -> str:
    """
    Build a clean subject phrase from a subject token's subtree, applying
    first-person pronoun resolution to the leading token.

    "I"            -> "User"
    "My favorite"  -> "User's favorite"
    """
    ordered = sorted(tokens, key=lambda t: t.i)
    # Drop leading determiners that add no entity value (e.g. "the", "a").
    words: List[str] = []
    for idx, tok in enumerate(ordered):
        low = tok.text.lower()
        if idx == 0 and low in _PRONOUN_SUBJECT:
            words.append(_PRONOUN_SUBJECT[low])
            continue
        if idx == 0 and low in _PRONOUN_POSSESSIVE:
            words.append(_PRONOUN_POSSESSIVE[low])
            continue
        if tok.is_punct:
            continue
        # Drop auxiliary verbs ("was", "is", "has", ...) that the parser may
        # have attached under the subject — they belong to the predicate, not
        # the subject entity.
        if tok.dep_ in _AUX_DEPS or tok.pos_ == _AUX_POS:
            continue
        words.append(tok.text)
    return " ".join(words).strip()


def _span_text(token) -> str:
    """Return the cleaned subtree text rooted at ``token`` (punctuation removed)."""
    ordered = sorted(token.subtree, key=lambda t: t.i)
    return " ".join(t.text for t in ordered if not t.is_punct).strip()


# ── Fallback extraction (heuristic / regex) ─────────────────────────────────────
def _fallback_extract(text: str) -> List[Tuple[str, str, str]]:
    """
    Regex-based fallback extraction when dependency parsing yields zero triples.

    Handles common S-V-O patterns with pronoun resolution and basic
    subject/object cleanup. Does **not** require a correct spaCy parse.

    Supported patterns (see ``_FALLBACK_PATTERNS``):
      * "X lives in Y"    -> (subject="X", relation="lives in", object="Y")
      * "X is Y"          -> (subject="X", relation="is",      object="Y")
      * "X created Y"     -> (subject="X", relation="created", object="Y")
      * "X has Y"         -> (subject="X", relation="has",     object="Y")

    Pronoun resolution mirrors ``_resolve_subject_phrase``:
      * "I live in Paris" -> subject="User"
      * "My shop is cool" -> subject="User's shop"
    """
    text = text.strip()
    if not text:
        return []

    for pattern, is_prep in _FALLBACK_PATTERNS:
        m = pattern.match(text)
        if not m:
            continue

        subject = _strip_auxiliaries(m.group(1).strip())
        verb = m.group(2).strip().lower()
        obj = m.group(3).strip().rstrip(".")

        if not subject or not obj:
            continue

        # Pronoun resolution — reuse the shared coreference utility so the
        # TEACH path and any other consumer (e.g. the agentic planner) stay in
        # lockstep on how "my"/"I" map to "User's"/"User".
        subject = resolve_first_person_coref(subject)

        relation = verb if is_prep else verb
        return [(subject, relation, obj)]

    return []


# ── Relational-copula normalization ─────────────────────────────────────────────
# Pattern: "[the|a|an] <RELATION-NOUN> of <ENTITY>" used as the SUBJECT of a
# copula ("is"/"was"). spaCy parses "The creator of Blender is Ton Roosendaal"
# as (subject="The creator of Blender", relation="be", object="Ton Roosendaal"),
# which buries both the real entity ("Blender") and the real relation
# ("creator" -> create) inside the subject string. That shape:
#   * is NOT retrievable by "Who created Blender?" (which queries the `create`
#     predicate on the entity "Blender"), and
#   * hides the functional key from Belief Revision: two assertions ("... is Ton"
#     / "... is John") look like two unrelated copula facts instead of two
#     competing values of (Blender, create), so the contradiction is never
#     flagged and the loser silently vanishes.
# We rewrite such a copula into the canonical functional triple
#   (ENTITY, <core-predicate-of-RELATION-NOUN>, OBJECT)
#   "The creator of Blender is Ton Roosendaal" -> ("Blender", "create", "Ton Roosendaal")
# so both assertions land under the SAME (subject, predicate) and become
# comparable evidence for retrieval AND belief revision.
_RELATIONAL_COPULA_RE = re.compile(
    r"^(?:the|a|an)\s+([A-Za-z][A-Za-z\-]*)\s+of\s+(.+)$",
    re.IGNORECASE,
)
# Copula relations (already lemmatized to "be" on the dependency path, but the
# regex fallback emits the surface "is"); compared case-insensitively.
_COPULA_RELATIONS = frozenset({"be", "is", "was", "were", "are", "am"})


def _rewrite_relational_copula(
    triples: List[Tuple[str, str, str]]
) -> List[Tuple[str, str, str]]:
    """Rewrite ``("the <rel> of <entity>", be, <obj>)`` -> ``(<entity>, <core>, <obj>)``.

    Only fires when (a) the relation is a copula and (b) the subject's head noun
    resolves to a *known* core predicate via the shared
    :data:`predicate_resolver` (e.g. "creator"/"author"/"founder" -> "create").
    Unknown relational nouns ("the colour of the sky") are left untouched, since
    we have no predicate to ground them on. Deterministic and never raises.
    """
    rewritten: List[Tuple[str, str, str]] = []
    for subj, rel, obj in triples:
        if rel.strip().lower() in _COPULA_RELATIONS:
            m = _RELATIONAL_COPULA_RE.match(subj.strip())
            if m:
                rel_noun = m.group(1).strip()
                inner_entity = m.group(2).strip()
                core = predicate_resolver.resolve(rel_noun)
                # Accept only nouns the resolver actually recognises as a
                # relation synonym (creator->create, founder->create, ...), so a
                # plain "the X of Y" with no verb meaning is not mis-grounded.
                if inner_entity and predicate_resolver.is_synonym(rel_noun):
                    rewritten.append((inner_entity, core, obj))
                    continue
        rewritten.append((subj, rel, obj))
    return rewritten


# ── Triple extraction ───────────────────────────────────────────────────────────
def extract_triples(text: str) -> List[Tuple[str, str, str]]:
    """
    Extract standard S-V-O triples from ``text`` using dependency parsing.

    Strategy per sentence:
      * Anchor on the ROOT verb.
      * Subject  := nsubj / nsubjpass child of ROOT (with pronoun resolution).
      * Object   := dobj / attr / oprd / dative / acomp child of ROOT, OR the
                    pobj of a prepositional child (predicate then absorbs the
                    preposition, e.g. "work at" -> Google).
    """
    if not text or not text.strip():
        return []

    nlp = _get_nlp()
    doc = nlp(text)
    triples: List[Tuple[str, str, str]] = []

    for sent in doc.sents:
        root = sent.root
        if root is None:
            continue

        # ── Subject ─────────────────────────────────────────────
        subj_tokens = [c for c in root.children if c.dep_ in ("nsubj", "nsubjpass")]
        if not subj_tokens:
            continue
        subject = _resolve_subject_phrase(list(subj_tokens[0].subtree))
        if not subject:
            continue

        relation = root.lemma_.lower().strip()

        # ── Direct object / complement ──────────────────────────
        obj_token = None
        for child in root.children:
            if child.dep_ in _OBJECT_DEPS:
                obj_token = child
                break

        if obj_token is not None:
            obj = _span_text(obj_token)
            if obj:
                triples.append((subject, relation, obj))
                continue

        # ── Prepositional / passive-agent object (predicate absorbs the
        #    preposition, e.g. "work at" -> Google, "created by" -> engineers) ──
        for child in root.children:
            if child.dep_ in ("prep", "agent"):
                pobj = next(
                    (gc for gc in child.children if gc.dep_ == "pobj"), None
                )
                if pobj is not None:
                    obj = _span_text(pobj)
                    if obj:
                        prep_relation = f"{relation} {child.text.lower()}".strip()
                        triples.append((subject, prep_relation, obj))
                        break

    # ── Fallback: dependency parse produced no triples ──────────
    if not triples:
        triples = _fallback_extract(text)

    # Normalize the "the <relation> of <entity> is <obj>" copula shape into the
    # canonical functional triple (entity, <core-predicate>, obj) so the fact is
    # stored/retrieved under the relation it actually expresses (e.g. `create`)
    # and competing assertions collide on one (subject, predicate) key.
    triples = _rewrite_relational_copula(triples)

    return triples


# ── Persistence ──────────────────────────────────────────────────────────────────
def _store_triples(triples: List[Tuple[str, str, str]]) -> int:
    """Persist triples into the Knowledge Graph ``triples`` table. Returns count."""
    if not triples:
        return 0

    now = time.time()
    rows = [
        (subj, rel, obj, CONFIDENCE, SOURCE, now)
        for (subj, rel, obj) in triples
    ]

    conn = open_connection(str(_KG_DB_PATH))
    try:
        conn.execute(_TRIPLES_SCHEMA)
        # Collapse any pre-existing duplicates so the UNIQUE index can be built
        # on legacy databases (a table created before the inline UNIQUE clause).
        # Idempotent: a no-op once the table is already clean.
        conn.execute(
            "DELETE FROM triples WHERE id NOT IN "
            "(SELECT MIN(id) FROM triples GROUP BY subject, relation, object)"
        )
        conn.execute(_TRIPLES_UNIQUE_INDEX)
        # INSERT OR IGNORE so re-stating an already-known fact is a no-op
        # against the UNIQUE(subject, relation, object) constraint.
        conn.executemany(
            "INSERT OR IGNORE INTO triples (subject, relation, object, confidence, source, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()
    return len(rows)


def extract_and_store_facts(text: str) -> List[Tuple[str, str, str]]:
    """
    Extract S-V-O triples from ``text`` and write them to the Knowledge Graph.

    Returns the list of triples that were committed. An empty list means nothing
    extractable was found (the caller should fall through to normal reasoning).
    Never raises on extraction/storage errors — failures are logged and treated
    as "no facts learned".

    Phase 62 — **schema gatekeeper**: before storage, extracted triples are run
    through :func:`backend.knowledge.schema_gatekeeper.validate_triples`, which
    classifies each as ACCEPT or REJECT against the registered world-model
    schema. Only ACCEPTED triples reach the ``triples`` table. REJECTED triples
    (e.g. "My Tesla has 5000 legs" — a recognised predicate hitting a slot the
    entity doesn't have) are logged and buffered in :data:`_LAST_REJECTIONS`
    (read via :func:`last_rejections`) but do NOT change this function's return
    shape, which stays ``List[Tuple[str, str, str]]``.

    Open-world guarantee: the gatekeeper ONLY rejects a recognised predicate
    that violates a TYPED entity's schema. Untyped subjects, unknown predicates,
    and free-form facts ALWAYS accept — so every pre-Phase-62 TEACH continues to
    land in the triples table unchanged. If the gatekeeper or the world-model
    registry is unavailable, the whole step degrades to "accept all", preserving
    the prior behaviour exactly.
    """
    try:
        triples = extract_triples(text)
    except Exception as exc:
        logger.warning("Fact extraction failed for %r: %s", text[:60], exc)
        return []

    if not triples:
        return []

    # ── Phase 62: schema validation gate ──────────────────────────────────
    # Lazily imported + fully defensive: any failure (no registry, malformed
    # ontology, classifier bug) collapses to "accept all" so the free-form KG
    # write path never regresses. The signature is unchanged on purpose — see
    # the module docstring of schema_gatekeeper for the open-world contract.
    accepted = triples
    try:
        from backend.knowledge.schema_gatekeeper import validate_triples

        accepted, rejections = validate_triples(triples)
        if rejections:
            _LAST_REJECTIONS.clear()
            _LAST_REJECTIONS.extend(rejections)
            for rej in rejections:
                logger.info(
                    "Schema gatekeeper rejected (%s): %r — %s",
                    rej.reason_code, rej.triple, rej.message,
                )
        else:
            _LAST_REJECTIONS.clear()
    except Exception as exc:
        # Never let the gatekeeper block a TEACH. Accept everything and proceed.
        logger.debug("Schema gatekeeper unavailable — accepting all triples: %s", exc)
        accepted = triples

    if not accepted:
        # All triples were schema-rejected (e.g. a purely nonsensical teach
        # about a typed entity). Nothing to store; surface the rejections via
        # the buffer and return empty so the caller falls through.
        return []

    try:
        stored = _store_triples(accepted)
    except Exception as exc:
        logger.warning("Fact storage failed (%d triples): %s", len(accepted), exc)
        return []

    logger.info(
        "Knowledge acquisition: stored %d triple(s) from user statement: %s",
        stored,
        accepted,
    )
    return accepted


# Phase 62 — buffer of the most recent schema-gatekeeper rejections, for the
# future TEACH-response layer to surface to the user. Read-only accessor below.
# Module-level (not per-call) because the single caller in the pipeline reads it
# immediately after extract_and_store_facts returns; it is cleared on every call.
_LAST_REJECTIONS: list = []


def last_rejections() -> list:
    """Return the schema-gatekeeper rejections from the most recent TEACH.

    Each entry is a ``schema_gatekeeper.Rejection``. Empty when the last call
    accepted everything (or when no TEACH has run yet). Intended for the future
    TEACH-response surfacing step; callers that ignore it are unaffected.
    """
    return list(_LAST_REJECTIONS)


__all__ = ["extract_and_store_facts", "extract_triples", "last_rejections"]

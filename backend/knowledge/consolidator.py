"""
VELYNX Phase 53.1 — Knowledge Consolidation Bridge
====================================================

`fact_extractor.py` writes raw, user-asserted ``(subject, relation, object)``
triples into the ``triples`` table of the *raw memory* database
(``velynx_data/knowledge_graph/graph.db``). The ``ReasoningEngine``, however,
traverses the *active brain* — the ``concepts`` and ``relationships`` tables
owned by :class:`backend.knowledge.knowledge_graph.KnowledgeGraph`
(``data/knowledge_graph.db``).

This module is the bridge between those two worlds. It preserves the deliberate
separation of "raw memory" (everything the user ever stated, verbatim) from
"active knowledge" (the curated graph the reasoner actually walks). Nothing is
deleted from raw memory; consolidated rows are simply *flagged* so they are
never re-processed.

Pipeline
--------
1. Read un-consolidated rows from the raw ``triples`` table.
2. For each triple, apply **epistemic scoring**:
       * subject is the user  -> VERIFIED  (confidence = 0.90)
       * third-party subject   -> INFERRED  (confidence = 0.70)
3. Move the fact into the active brain via the *public* graph API:
       * ``add_concept(name, domain, description)`` for subject **and** object
       * ``add_relationship(source, relation, target)`` for the edge
4. **Vector embedding (critical).** ``add_concept`` does not embed. So the
   subject and object strings are pushed through
   :data:`backend.memory.embedding_service.embedding_service` (which loads the
   shared all-MiniLM-L6-v2 model via
   :func:`backend.memory.gpu_embedder.get_cached_model`) and the resulting
   384-dim vectors are persisted in a sidecar ``concept_embeddings`` table that
   lives alongside the active concepts. Without this, semantic search over
   newly-learned concepts stays blind.
5. Record epistemic provenance (status + confidence) in a ``concept_provenance``
   sidecar table, because the active ``relationships`` table intentionally
   stores no confidence column.
6. Flag the raw triple as consolidated.

Public API
----------
``consolidate_pending(limit=None) -> ConsolidationReport``
    Synchronous batch consolidation. Safe to call repeatedly; idempotent.

``consolidate_pending_async(limit=None) -> ConsolidationReport``
    Thread-offloaded wrapper for use inside the async pipeline / as a
    fire-and-forget background task.
"""
from __future__ import annotations

import asyncio
import logging
import re
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from backend.memory._sqlite import connect as open_connection
from backend.knowledge.normalizer import concept_normalizer
from backend.knowledge.predicate_resolver import predicate_resolver

logger = logging.getLogger("velynx.consolidator")

# ── Consolidation serialization lock (asyncio-level) ────────────────────────────
# Multiple TEACH turns in quick succession each fire a fire-and-forget
# consolidate_pending() via asyncio.create_task. Without serialization, two
# concurrent consolidation threads can race on the same singular-fact key:
#
#   Task A (processing "Avatar"):
#     pending_singular[("user's favorite movie", "be")] = "avatar"
#   Task B (processing "Interstellar"):
#     pending_singular[("user's favorite movie", "be")] = "interstellar"
#   Task A contradiction check:
#     SELECT target WHERE target != 'avatar' → finds "interstellar"
#     deprecates "interstellar", keeps "avatar"  ← WRONG
#
# The module-level asyncio.Lock serializes consolidate_pending_async() so only
# ONE thread-pool worker runs consolidate_pending() at a time. A second caller
# BLOCKS at the asyncio level until the first finishes, then the serialized
# dispatch reads whatever rows remain un-consolidated and processes them.
_consolidation_lock = asyncio.Lock()

# ── Epistemic constants ────────────────────────────────────────────────────────
STATUS_VERIFIED = "VERIFIED"
STATUS_INFERRED = "INFERRED"
CONFIDENCE_VERIFIED = 0.90
CONFIDENCE_INFERRED = 0.70

# Domains assigned to concepts as they enter the active brain. First-person
# facts describe the user's world; third-person facts describe the wider world.
DOMAIN_PERSONAL = "PERSONAL"
DOMAIN_WORLD = "WORLD"

# Subjects produced by fact_extractor's first-person pronoun resolution. "I" /
# "me" / "myself" -> "User"; "my" / "mine" -> "User's ...". Both anchor on the
# "User" entity and therefore count as first-person (VERIFIED) statements.
_USER_PREFIX = "user"


# ── Reporting ───────────────────────────────────────────────────────────────────
@dataclass
class ConsolidationReport:
    """Summary of a consolidation run."""

    scanned: int = 0
    consolidated: int = 0
    verified: int = 0
    inferred: int = 0
    embedded: int = 0
    semantic_memories: int = 0
    deprecated: int = 0
    skipped: int = 0
    contradictions: List[dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "scanned": self.scanned,
            "consolidated": self.consolidated,
            "verified": self.verified,
            "inferred": self.inferred,
            "embedded": self.embedded,
            "semantic_memories": self.semantic_memories,
            "deprecated": self.deprecated,
            "skipped": self.skipped,
            "contradictions": self.contradictions,
            "errors": self.errors,
        }


# ── DB path resolution ──────────────────────────────────────────────────────────
def _raw_triples_db_path() -> Path:
    """Path of the raw-memory DB that owns the ``triples`` table.

    Resolved from the same source ``fact_extractor`` writes to, so we always
    read exactly where the facts were stored.
    """
    try:
        from backend.memory.knowledge_graph import _DB_PATH  # type: ignore

        return Path(_DB_PATH)
    except Exception:  # pragma: no cover - defensive fallback
        from backend.memory._sqlite import canonical_db_path

        return canonical_db_path("velynx_state.db")


# ── Schema bootstrap / migration ─────────────────────────────────────────────────
_CONSOLIDATED_COL = "consolidated"

_EMBEDDINGS_SCHEMA = """
CREATE TABLE IF NOT EXISTS concept_embeddings (
    name TEXT PRIMARY KEY,
    vector BLOB NOT NULL,
    dim INTEGER NOT NULL,
    model TEXT,
    updated REAL
)
"""

_PROVENANCE_SCHEMA = """
CREATE TABLE IF NOT EXISTS concept_provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    relation TEXT NOT NULL,
    object TEXT NOT NULL,
    status TEXT NOT NULL,
    confidence REAL NOT NULL,
    raw_triple_id INTEGER,
    timestamp REAL
)
"""


def _ensure_consolidated_column(conn: sqlite3.Connection) -> None:
    """Add the ``consolidated`` flag to the raw ``triples`` table if missing.

    The raw schema (see fact_extractor / memory.knowledge_graph) has no notion
    of consolidation. We add it idempotently so re-runs never re-process a row.
    """
    cols = {row[1] for row in conn.execute("PRAGMA table_info(triples)")}
    if not cols:
        # triples table doesn't exist yet — nothing has been extracted.
        return
    if _CONSOLIDATED_COL not in cols:
        conn.execute(
            f"ALTER TABLE triples ADD COLUMN {_CONSOLIDATED_COL} INTEGER NOT NULL DEFAULT 0"
        )
        conn.commit()
        logger.info("Migrated raw triples table: added '%s' column", _CONSOLIDATED_COL)


def _ensure_active_sidecar_tables(active_db_path: Path) -> None:
    """Create the embedding + provenance sidecar tables in the active-brain DB."""
    conn = open_connection(str(active_db_path))
    try:
        conn.execute(_EMBEDDINGS_SCHEMA)
        conn.execute(_PROVENANCE_SCHEMA)
        conn.commit()
    finally:
        conn.close()


# ── Epistemic scoring ─────────────────────────────────────────────────────────────
def _is_first_person(subject: str) -> bool:
    """True when the triple's subject refers to the user.

    fact_extractor resolves first-person pronouns to ``User`` (subject) or
    ``User's ...`` (possessive), so any subject anchored on "User" is a
    first-person statement.
    """
    return subject.strip().lower().startswith(_USER_PREFIX)


def _score(subject: str) -> Tuple[str, float, str]:
    """Return (status, confidence, domain) for a subject."""
    if _is_first_person(subject):
        return STATUS_VERIFIED, CONFIDENCE_VERIFIED, DOMAIN_PERSONAL
    return STATUS_INFERRED, CONFIDENCE_INFERRED, DOMAIN_WORLD


# ── Embedding ─────────────────────────────────────────────────────────────────────
def _embed_text(text: str):
    """Embed ``text`` with the shared model, or return ``None`` if unavailable.

    Routes through :data:`backend.memory.embedding_service.embedding_service`,
    whose ``_get_model`` reuses the process-wide singleton from
    :func:`backend.memory.gpu_embedder.get_cached_model` — so we never load the
    model twice. Falls back to ``get_cached_model`` directly if the service
    surface changes. Returns a 1-D float32 numpy array (normalized) or ``None``.
    """
    try:
        from backend.memory.embedding_service import embedding_service

        if not embedding_service.available:
            return None
        # Preferred: reuse the service (LRU cache + shared get_cached_model).
        if hasattr(embedding_service, "_embed_sync"):
            return embedding_service._embed_sync(text)
        model = embedding_service._get_model()  # -> get_cached_model() singleton
        return model.encode(text, normalize_embeddings=True)
    except Exception as exc:  # pragma: no cover - defensive
        # Last-resort direct path, still honoring the cached singleton.
        try:
            from backend.memory.gpu_embedder import get_cached_model

            model, _device = get_cached_model()
            return model.encode(text, normalize_embeddings=True)
        except Exception:
            logger.debug("Embedding unavailable for %r: %s", text[:40], exc)
            return None


def _store_embedding(conn: sqlite3.Connection, name: str, vector, model_name: str) -> bool:
    """Persist a concept vector as float32 BLOB. Returns True on write."""
    if vector is None:
        return False
    try:
        import numpy as np

        arr = np.asarray(vector, dtype="float32").ravel()
        conn.execute(
            "INSERT OR REPLACE INTO concept_embeddings (name, vector, dim, model, updated) "
            "VALUES (?, ?, ?, ?, ?)",
            (name, arr.tobytes(), int(arr.shape[0]), model_name, time.time()),
        )
        return True
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("Failed to store embedding for %r: %s", name, exc)
        return False


def _flush_semantic_memories(items: List[dict]) -> int:
    """Store each relationship as a single semantic memory in ``memory_manager``.

    Why this matters (Graph-RAG recall): embedding the isolated ``subject`` and
    ``object`` nodes alone produces very short strings whose vectors rarely match
    a full natural-language query ("where do I get my coffee?"). Embedding the
    *whole relationship* as one semantic string ("User favorite coffee shop
    Third Wave Coffee") gives the retriever a target that lives in the same
    semantic neighbourhood as the query, so the consolidated fact is actually
    found instead of an unrelated episodic memory.

    Driving the async store: ``consolidate_pending`` runs inside an
    ``asyncio.to_thread`` worker (no loop in that thread), so ``asyncio.run``
    is the correct driver. If a running loop is somehow present, we log a
    warning and return 0 — the semantic memories will be lost for this cycle.

    Returns the number of semantic memories stored.
    """
    if not items:
        return 0
    try:
        from backend.memory.memory_manager import memory_manager
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("memory_manager unavailable; skipping semantic memories: %s", exc)
        return 0

    async def _store_all() -> int:
        stored = 0
        for it in items:
            try:
                await memory_manager.store_semantic(
                    it["concept"],
                    it["text"],
                    relationships=it.get("relationships"),
                    source="consolidation",
                    importance=float(it.get("importance", 0.6)),
                )
                stored += 1
            except Exception as exc:  # pragma: no cover - defensive
                logger.debug("store_semantic failed for %r: %s",
                             str(it.get("text", ""))[:40], exc)
        return stored

    try:
        running = asyncio.get_running_loop()
    except RuntimeError:
        running = None

    if running is not None:
        logger.error(
            "Semantic memory flush called inside a running event loop — "
            "cannot store memories. This indicates consolidate_pending was "
            "called on the main thread instead of via asyncio.to_thread."
        )
        return 0

    try:
        return asyncio.run(_store_all())
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("Semantic memory flush failed: %s", exc)
        return 0


# ── Belief revision (Phase 56) ──────────────────────────────────────────────────
# Some relations are *functional*: a subject can sensibly hold only ONE current
# target for them. Asserting a new target should DEPRECATE the old fact, not
# accumulate a contradiction ("favorite color is red" AND "... is blue"). We
# detect these by normalizing the relation to a ``snake_case`` key and matching
# a small heuristic of prefixes / exact names / substrings.
_SINGULAR_RELATION_PREFIXES = (
    "favorite_", "favourite_", "fav_",
    "is_",          # is_named, is_called, is_aged, is_located_in, ...
    "has_name", "date_of_birth", "lives_in", "born_", "located_",
)
_SINGULAR_RELATION_EXACT = frozenset({
    "lives_in", "located_in", "located_at", "resides_in", "currently_lives_in",
    "is_named", "is_called", "named", "name", "has_name", "goes_by",
    "date_of_birth", "born_in", "born_on", "birthday", "birthdate", "birthplace",
    "age", "capital_of", "capital", "nationality", "gender",
    "favorite", "favourite",
    "works_at", "works_for", "employer", "job", "occupation",
    "married_to", "spouse", "partner",
    "email", "phone", "phone_number", "address",
    # Identity/authorship relations. After fact_extractor normalizes the
    # "the creator of X is Y" copula into the functional triple
    # (X, create, Y), two differing creators for the same subject are a genuine
    # contradiction we want Belief Revision to flag rather than silently keep
    # both. NOTE: this treats authorship as single-valued; if first-class
    # co-creator support is needed, gate this behind subject cardinality instead
    # of removing it (a bare "create" with no resolution loses the flag).
    "create",
})
_SINGULAR_RELATION_SUBSTRINGS = ("favorite", "favourite")

# Many functional facts carry the singular signal in the SUBJECT rather than the
# relation — the extractor renders "My favorite color is blue" as
# ``("User's favorite color", "be", "blue")``, whose relation ("be") is a plain
# copula. We therefore also treat a fact as functional when the subject names a
# single-valued possessive attribute ("...'s name / age / favorite color / ...").
_SINGULAR_SUBJECT_ATTRS = (
    "favorite", "favourite",
    "name", "age", "birthday", "birthdate", "date_of_birth", "dob",
    "color", "colour", "gender", "nationality", "height", "weight",
    "address", "email", "phone", "phone_number",
    "occupation", "job", "employer", "spouse", "partner",
    "capital", "location", "hometown",
)


def _relation_key(relation: str) -> str:
    """Normalize a relation to a ``snake_case`` matching key.

    Relations may arrive space- or underscore-separated ("favorite color" vs.
    "favorite_color"); fold both to one canonical key for the heuristic.
    """
    return re.sub(r"[\s\-]+", "_", str(relation or "").strip().lower())


def _is_singular_relation(relation: str) -> bool:
    """True when ``relation`` implies a single current target (functional).

    Used to decide whether a newly-asserted ``(subject, relation, object)``
    should *overwrite* prior targets for the same ``(subject, relation)`` rather
    than coexist with them. Errs conservative: a relation must clearly look
    functional (a recognised prefix / exact name / "favorite*" substring) — open
    relations like "requires" or "knows" are left multi-valued.
    """
    key = _relation_key(relation)
    if not key:
        return False
    if key in _SINGULAR_RELATION_EXACT:
        return True
    if key.startswith(_SINGULAR_RELATION_PREFIXES):
        return True
    if any(sub in key for sub in _SINGULAR_RELATION_SUBSTRINGS):
        return True
    return False


def _is_singular_subject(subject: str) -> bool:
    """True when the subject names a single-valued possessive attribute.

    Catches the common extractor shape ``("User's favorite color", "be", X)``
    where the functional signal lives in the subject, not the copula relation.
    Requires a possessive ("'s" / "s_") so a bare noun like "color" doesn't
    accidentally trip it, EXCEPT for the unambiguous "favorite*" marker.
    """
    key = _relation_key(subject)
    if not key:
        return False
    # "favorite/favourite" anywhere is an unambiguous functional marker.
    if any(sub in key for sub in _SINGULAR_RELATION_SUBSTRINGS):
        return True
    # Otherwise require a possessive attribute: "<owner>'s <attr>".
    possessive = "'s_" in key or key.startswith("'s") or re.search(r"s_(?=[a-z])", key)
    if not possessive:
        return False
    return any(attr in key for attr in _SINGULAR_SUBJECT_ATTRS)


def _is_singular_fact(subject: str, relation: str) -> bool:
    """True when ``(subject, relation)`` should hold only ONE current object.

    Functional if the relation itself is singular (favorite_*, lives_in, ...) OR
    the subject names a single-valued attribute ("User's name", "User's favorite
    color"). The collision key remains ``(subject, relation)`` either way.
    """
    return _is_singular_relation(relation) or _is_singular_subject(subject)


def has_pending_revision(subject: str) -> bool:
    """True if *subject* has an un-consolidated SINGULAR (functional) revision.

    The retrieval fast path serves ONE cached value from the active graph. When a
    functional attribute (favorite movie, name, creator, ...) has been
    (re-)asserted into raw memory but ``consolidate_pending`` has not yet
    reconciled it, serving the cached value is the stale "Avatar ghost" read. A
    caller that gets ``True`` here should DEFER to the reasoning path so the
    freshest assertion wins (or the conflict is reported honestly).

    "Pending" is scoped to rows still flagged ``consolidated = 0``: once a
    revision is reconciled the stale edge is deprecated and this returns ``False``
    again, so a one-time correction never blocks the subject's fast path forever.
    (A bare ``COUNT(DISTINCT object)`` over *all* rows cannot tell "currently
    pending" from "was ever re-taught" — raw rows are preserved, only flagged.)

    Cheap (a single indexed lookup over one subject's un-consolidated rows),
    read-only, and fully defensive: any error (missing DB / no ``triples`` table)
    returns ``False`` so a transient fault never blocks an otherwise-valid hit.
    """
    subj = (subject or "").strip()
    if not subj:
        return False
    db_path = _raw_triples_db_path()
    try:
        # Pure read: never create the store from the hot path.
        if not Path(db_path).exists():
            return False
        conn = open_connection(str(db_path))
        try:
            cols = {row[1] for row in conn.execute("PRAGMA table_info(triples)")}
            if "subject" not in cols or "relation" not in cols:
                return False
            # Restrict to un-consolidated rows when the flag exists; if the column
            # was never added, every row is effectively still pending.
            consolidated_clause = (
                f" AND {_CONSOLIDATED_COL} = 0" if _CONSOLIDATED_COL in cols else ""
            )
            rows = conn.execute(
                "SELECT DISTINCT relation FROM triples "
                "WHERE LOWER(subject) = LOWER(?)" + consolidated_clause,
                (subj,),
            ).fetchall()
        finally:
            conn.close()
    except Exception:
        return False
    return any(_is_singular_fact(subj, row[0]) for row in rows)


# ── Direction canonicalization (Phase 57) ──────────────────────────────────────
# Asymmetric predicates carry a canonical (subject, object) DIRECTION: the same
# underlying fact can be extracted in either direction depending on voice, and
# storing both creates the "bidirectional edge-keying artifact" — one fact
# counted twice, which pollutes retrieval and contradiction detection.
#
#   "Ton created Blender"        -> (ton, create, blender)      [agent-first]
#   "Blender was created by Ton" -> (blender, create, ton)      [artifact-first]
#
# Both rows describe ONE assertion (Ton is Blender's creator). Without a
# canonical direction both land in ``relationships`` and the reasoner traverses
# the same edge twice. The guard below collapses them onto one direction BEFORE
# the singular-fact check, so the ``(subject, relation)`` collision key stays
# stable and deprecation targets the right edges.

# Core forms of asymmetric predicates. The predicate resolver collapses the
# create-family (create/author/build/found/invent/develop/design/...) onto
# "create" and the locative-family (located/lives/resides/born/works) onto
# "located_in", so these two core forms cover every surface synonym. Both are
# kept for robustness against raw inserts that bypass the resolver.
_ASYMMETRIC_PREDICATES = frozenset({"create", "located_in"})

# Role markers that identify the AGENT endpoint of an asymmetric relation. When
# one endpoint of a create-family fact matches ("the creator of blender",
# "author of krita", ...), that endpoint is the creator and the OTHER endpoint
# is the artifact whose property the relation asserts.
_AGENT_ROLE_RE = re.compile(
    r"\b(creator|author|founder|inventor|developer|designer|maker|builder|"
    r"writer|composer|artist|director|producer|architect|engineer)\b",
    re.IGNORECASE,
)


def _is_asymmetric_predicate(relation: str) -> bool:
    """True when ``relation`` has a canonical (subject, object) direction.

    Symmetric predicates (``requires``, ``related_to``, ...) are order-
    invariant and are left untouched. Asymmetric predicates (``create``,
    ``located_in``, ...) assert different facts depending on endpoint order, so
    both extractions of the same assertion must collapse to one stored row.
    Synonym-aware: surface forms are resolved to their core predicate before
    the membership check.
    """
    key = _relation_key(relation)
    if not key:
        return False
    if key in _ASYMMETRIC_PREDICATES:
        return True
    try:
        return predicate_resolver.resolve(key) in _ASYMMETRIC_PREDICATES
    except Exception:
        return False


def _canonicalize_asymmetric_direction(
    subject: str, relation: str, obj: str
) -> Tuple[str, str, str]:
    """Enforce a canonical endpoint ordering for an asymmetric predicate.

    Canonical direction — FUNCTIONAL-IDENTITY ENDPOINT AS SUBJECT:
    The endpoint for which the relation is single-valued (the entity that HOLDS
    the asserted property) is placed in the subject position. For ``create``
    that single-valued property is "has exactly one creator", whose holder is
    the ARTIFACT, so the canonical form is ``(artifact, create, creator)`` —
    e.g. ``(blender, create, ton)``.

    This is mandated by the belief-revision contract
    ``pending_singular[(subject, relation)] = obj``, which assumes the OBJECT is
    the singular VALUE (the creator) and keys collisions on ``(subject,
    relation)`` to flag "two creators of the same artifact". That key is only
    stable when the artifact is the subject; an agent-first ordering would put
    the creator in subject position and silently break the collision key (a
    creator can create many artifacts, so ``(creator, create)`` is not
    single-valued). The polarity lives entirely in this one function — flip it
    here and the whole stack follows.

    Role detection: when one endpoint matches an agent-role marker
    (``_AGENT_ROLE_RE``) it is the creator and the OTHER endpoint is placed
    first (artifact-first). When neither endpoint carries a role signal (bare
    proper nouns — the common extraction shape) the endpoints are ordered
    lexicographically (subject = lex-min). Lexicographic ordering is
    semantically arbitrary but DETERMINISTIC, so it still honours the dedup
    contract (both extractions map to one row); the read-path dedup
    (:mod:`backend.cognition.reasoning_engine`) and the migration
    (:mod:`backend.tools.dedupe_directions`) reinforce it for legacy data.
    """
    if not subject or not obj:
        return subject, relation, obj
    s_role = bool(_AGENT_ROLE_RE.search(subject))
    o_role = bool(_AGENT_ROLE_RE.search(obj))
    if s_role and not o_role:
        # subject is the agent-role phrase -> artifact (obj) becomes subject.
        return obj, relation, subject
    if o_role and not s_role:
        # obj is the agent-role phrase -> subject is already the artifact.
        return subject, relation, obj
    # No disambiguating role signal -> deterministic lexicographic ordering so
    # both extractions of the same fact collapse to one stored row.
    if str(subject).strip().lower() > str(obj).strip().lower():
        return obj, relation, subject
    return subject, relation, obj


def _deprecate_graph_edges(
    conn: sqlite3.Connection, singular_map: dict
) -> Tuple[int, List[Tuple[str, str, str]]]:
    """Delete stale edges for functional relations, keeping only the newest target.

    ``singular_map`` maps ``(subject, relation) -> keep_object`` (the most
    recently asserted target). For each entry we remove every other target of
    that ``(subject, relation)`` from the active ``relationships`` table.

    Returns ``(edges_deleted, deprecated_facts)`` where ``deprecated_facts`` is a
    list of ``(subject, relation, old_object)`` tuples so the caller can purge
    the matching semantic memories.
    """
    deleted = 0
    deprecated_facts: List[Tuple[str, str, str]] = []
    for (subject, relation), keep_object in singular_map.items():
        try:
            rows = conn.execute(
                "SELECT DISTINCT target FROM relationships "
                "WHERE source = ? AND relation = ? AND target != ?",
                (subject, relation, keep_object),
            ).fetchall()
        except Exception as exc:  # pragma: no cover - table may be empty/missing
            logger.debug("Deprecation scan failed for (%s, %s): %s", subject, relation, exc)
            continue
        old_targets = [r[0] for r in rows if r and r[0]]
        if not old_targets:
            continue
        try:
            cur = conn.execute(
                "DELETE FROM relationships "
                "WHERE source = ? AND relation = ? AND target != ?",
                (subject, relation, keep_object),
            )
            deleted += cur.rowcount or 0
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("Deprecation delete failed for (%s, %s): %s", subject, relation, exc)
            continue
        for old in old_targets:
            deprecated_facts.append((subject, relation, old))
            logger.info(
                "Belief revision: deprecated '%s %s %s' (superseded by '%s')",
                subject, relation, old, keep_object,
            )
    return deleted, deprecated_facts


def _deprecate_semantic_memories(singular_map: dict) -> int:
    """Delete semantic memories whose object for a functional attribute is stale.

    Requirement (Phase 56): the vector store must not surface a superseded fact.

    Driven by ``singular_map`` (``(subject, relation) -> keep_object``, the most
    recently asserted value) rather than by which graph edges happened to be
    deleted this run. That matters because stale semantic memories ACCUMULATE
    across consolidation runs / sessions — gating purge on a fresh edge-delete
    would leave older copies behind (exactly the "blue [KG]" survivor bug). For
    every functional ``(subject, relation)`` we drop any semantic memory that
    mentions the subject + relation but NOT the kept object.

    Retrieval is TARGETED via :meth:`MemoryManager.find_semantic_memories`
    (dense search), not ``get_all`` — so a large, paginated collection can't hide
    the row we need to revise. Deletions go through
    :meth:`MemoryManager.delete_semantic`. Errors are logged loudly and never
    swallowed; a functional fact that matched nothing emits a warning.

    Driven like the semantic write path: ``asyncio.run`` with no running loop
    (sync / ``to_thread`` worker), else a fire-and-forget task whose failures are
    surfaced via a done-callback. Returns memories deleted (0 when deferred).
    """
    if not singular_map:
        return 0
    from backend.memory.memory_manager import memory_manager

    async def _purge() -> int:
        removed = 0
        for (subject, relation), keep in singular_map.items():
            subj_lc = str(subject).lower()
            rel_lc = str(relation).lower()
            keep_lc = str(keep).lower()
            query_text = f"{subject} {relation} {keep}".strip()

            candidates = await memory_manager.find_semantic_memories(query_text, limit=50)
            stale_ids = []
            for entry in candidates:
                text_lc = (entry.text or "").lower()
                # Same subject + relation (the functional attribute) but a value
                # other than the one we keep => a superseded belief.
                if subj_lc in text_lc and rel_lc in text_lc and keep_lc not in text_lc:
                    stale_ids.append(entry.id)

            if not stale_ids:
                logger.debug(
                    "Belief revision: no stale semantic memory for %r (kept %r); "
                    "searched %d candidates",
                    (subject, relation), keep, len(candidates),
                )
                continue

            deleted = await memory_manager.delete_semantic(stale_ids)
            removed += deleted
            logger.info(
                "Belief revision: deleted %d stale semantic memory/ies for %r (kept %r)",
                deleted, (subject, relation), keep,
            )
        return removed

    try:
        running = asyncio.get_running_loop()
    except RuntimeError:
        running = None

    if running is not None:
        # This shouldn't happen: consolidate_pending always runs via
        # asyncio.to_thread, which has no running loop. Be defensive.
        logger.error(
            "Semantic deprecation called inside a running event loop — "
            "cannot purge memories. This indicates consolidate_pending was "
            "called on the main thread instead of via asyncio.to_thread."
        )
        return 0

    return asyncio.run(_purge())


# ── Core consolidation ─────────────────────────────────────────────────────────────
def consolidate_pending(limit: Optional[int] = None) -> ConsolidationReport:
    """Move un-consolidated raw triples into the active knowledge graph.

    Parameters
    ----------
    limit:
        Maximum number of pending triples to process this run. ``None`` = all.

    Returns
    -------
    ConsolidationReport
        Counts + any per-row error messages. Never raises for a single bad row;
        errors are captured and the run continues.
    """
    report = ConsolidationReport()

    raw_db_path = _raw_triples_db_path()
    if not Path(raw_db_path).exists():
        logger.debug("Raw triples DB not found at %s — nothing to consolidate", raw_db_path)
        return report

    # Active-brain graph (concepts + relationships) — public API.
    from backend.knowledge.knowledge_graph import KnowledgeGraph

    graph = KnowledgeGraph()
    active_db_path = graph.db_path
    _ensure_active_sidecar_tables(active_db_path)

    # Embedding model name (for provenance on the vectors).
    try:
        from backend.memory.embedding_service import _MODEL_NAME as _EMB_MODEL
    except Exception:
        _EMB_MODEL = "all-MiniLM-L6-v2"

    # ── 1. Read pending rows from raw memory ───────────────────────────
    raw_conn = open_connection(str(raw_db_path))
    try:
        _ensure_consolidated_column(raw_conn)
        cols = {row[1] for row in raw_conn.execute("PRAGMA table_info(triples)")}
        if not cols:
            return report  # no triples table yet

        sql = (
            f"SELECT id, subject, relation, object FROM triples "
            f"WHERE {_CONSOLIDATED_COL} = 0 ORDER BY id ASC"
        )
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        pending = raw_conn.execute(sql).fetchall()
    finally:
        raw_conn.close()

    report.scanned = len(pending)
    if not pending:
        return report

    # ── 2-5. Move each fact into the active brain ──────────────────────
    # IMPORTANT: KnowledgeGraph.add_concept/add_relationship each open their own
    # short-lived connection to the active DB. To avoid two concurrent writers
    # on the same file (SQLite "database is locked" even under WAL), we run ALL
    # graph writes first, buffer the sidecar payloads, then flush embeddings +
    # provenance through a single connection opened *after* the graph loop.
    done_ids: List[int] = []
    # Buffers: name -> vector (dedup so a concept is embedded once per run).
    pending_vectors: dict = {}
    pending_provenance: List[tuple] = []
    pending_semantic: List[dict] = []
    # Phase 56 — belief revision: (subject, relation) -> newest asserted object.
    # Rows are processed id-ASC, so the last write per key is the most recent
    # target we keep; all other targets for a singular relation get deprecated.
    pending_singular: dict = {}

    for row in pending:
        triple_id, subject, relation, obj = row[0], row[1], row[2], row[3]
        subject = (subject or "").strip()
        relation = (relation or "").strip()
        obj = (obj or "").strip()

        if not subject or not relation or not obj:
            report.skipped += 1
            # Still flag it so a malformed row doesn't block the queue forever.
            done_ids.append(triple_id)
            continue

        # Phase 54 — Semantic normalization (WRITE PATH). Collapse synonyms onto
        # canonical surface forms BEFORE scoring, graph insertion and embedding,
        # so a fact taught as "Bengaluru" is stored under the same node a query
        # for "Bangalore" will resolve to. Done after the empty-check so we never
        # normalize blank tokens, and before _score so first-person resolution
        # ("I"/"me" -> "user") feeds the VERIFIED/INFERRED decision.
        subject, relation, obj = concept_normalizer.normalize_triple(
            subject, relation, obj
        )
        # Predicate grounding — the *relation verb* is normalized through the
        # dedicated synonym resolver, NOT the entity normalizer. The entity
        # normalizer would map "created" -> "authored" (diverging from the
        # lemmatized "create" the spaCy extractor emits), fragmenting one
        # semantic relation across "create", "authored" and "authored by" nodes.
        # Routing the relation through the predicate resolver collapses all of
        # them onto a single core predicate ("create", "be", ...) so the read
        # path can match any phrasing to the stored edge.
        relation = predicate_resolver.resolve(relation)
        if not subject or not relation or not obj:
            report.skipped += 1
            done_ids.append(triple_id)
            continue

        # Phase 57 — Direction canonicalization (WRITE PATH). Asymmetric
        # predicates (create, located_in, ...) carry a canonical (subject,
        # object) direction; the same fact extracted in active vs passive voice
        # ("Ton created Blender" vs "Blender was created by Ton") would otherwise
        # be stored as two direction-inverted rows that the reasoner counts
        # twice. Collapse them onto ONE canonical direction BEFORE the singular-
        # fact check, so the ``(subject, relation)`` collision key stays stable
        # for belief revision (see ``_canonicalize_asymmetric_direction``).
        if _is_asymmetric_predicate(relation):
            subject, relation, obj = _canonicalize_asymmetric_direction(
                subject, relation, obj
            )

        try:
            status, confidence, domain = _score(subject)

            # 3. Graph insertion via the public KnowledgeGraph API.
            subj_desc = f"{subject} {relation} {obj}".strip()
            graph.add_concept(subject, domain, subj_desc)
            graph.add_concept(obj, domain, f"referenced by '{subject}' via '{relation}'")
            graph.add_relationship(subject, relation, obj)

            # Phase 56 — belief revision: if this fact is functional
            # (favorite_*, lives_in, is_named, or a possessive attribute subject
            # like "User's favorite color"), remember the newest target so stale
            # ones can be deprecated after the graph loop. The new edge is
            # already inserted above; we keep `obj` and purge the rest.
            if _is_singular_fact(subject, relation):
                pending_singular[(subject, relation)] = obj

            # 4. Vector embeddings for subject AND object (critical) — buffered.
            for name in (subject, obj):
                if name not in pending_vectors:
                    pending_vectors[name] = _embed_text(name)

            # 5. Epistemic provenance (active relationships table has no
            #    confidence column, so record it in the sidecar) — buffered.
            pending_provenance.append(
                (subject, relation, obj, status, confidence, triple_id, time.time())
            )

            # 5b. Graph-RAG: embed the WHOLE relationship as a single semantic
            #     string so full-sentence queries can match the fact. Isolated
            #     node vectors are too short to surface via cosine similarity.
            pending_semantic.append({
                "concept": subject,
                "text": f"{subject} {relation} {obj}".strip(),
                "relationships": [f"{relation} -> {obj}"],
                "importance": confidence,
            })

            done_ids.append(triple_id)
            report.consolidated += 1
            if status == STATUS_VERIFIED:
                report.verified += 1
            else:
                report.inferred += 1
        except Exception as exc:
            report.errors.append(f"triple {triple_id}: {exc}")
            logger.warning("Consolidation failed for triple %s: %s", triple_id, exc)

    # Phase 56 — belief revision: track which singular entries actually have
    # conflicting live edges (contradictions to keep) vs entries where the old
    # edge is already gone (safe to deprecate). Initialized before the conn
    # try/finally so it's in scope for semantic memory purge below.
    non_conflict: dict = {}

    # Flush sidecar tables through a single connection (graph conns now closed).
    emb_conn = open_connection(str(active_db_path))
    try:
        for name, vector in pending_vectors.items():
            if _store_embedding(emb_conn, name, vector, _EMB_MODEL):
                report.embedded += 1
        if pending_provenance:
            emb_conn.executemany(
                "INSERT INTO concept_provenance "
                "(subject, relation, object, status, confidence, raw_triple_id, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                pending_provenance,
            )
        # Phase 56 — belief revision: detect contradictions BEFORE deleting
        # stale edges. For each singular (subject, relation), check if LIVE
        # edges exist with a different target. If so, it's a genuine
        # contradiction — keep both edges and record the conflict so the
        # pipeline can surface it. Only deprecate entries with NO conflict
        # (e.g. a "favorite color" correction where the old edge was already
        # removed by a prior run, so the new assertion is the first appearance).
        if pending_singular:
            for (subject, relation), keep_object in pending_singular.items():
                old_edges = emb_conn.execute(
                    "SELECT target FROM relationships "
                    "WHERE source = ? AND relation = ? AND target != ?",
                    (subject, relation, keep_object),
                ).fetchall()
                if old_edges:
                    # A functional (1-to-1) relation now has a NEW target while
                    # an old target is still live: this is a CONTRADICTION and is
                    # ALWAYS flagged in ``report.contradictions`` so the harness /
                    # pipeline can surface it. What differs by subject is the
                    # RESOLUTION applied after flagging:
                    #
                    #   FIRST-PERSON subjects ("User's favorite movie") — the user
                    #     is the sole authority on their own belief, so the new
                    #     assertion SUPERSEDES the old one. We flag the conflict
                    #     AND deprecate the stale edge (overwrite protocol).
                    #     => resolution="overwrite"; routed into ``non_conflict``
                    #        so ``_deprecate_graph_edges`` removes "interstellar".
                    #
                    #   THIRD-PARTY subjects ("Blender", "Paris") — two competing
                    #     external claims with no single authority, so we keep both
                    #     edges and let the read-path reasoner weigh them.
                    #     => resolution="keep_both"; NOT deprecated.
                    is_first_person = _is_first_person(subject)
                    resolution = "overwrite" if is_first_person else "keep_both"
                    for (old_target,) in old_edges:
                        report.contradictions.append({
                            "subject": subject,
                            "relation": relation,
                            "old_object": old_target,
                            "new_object": keep_object,
                            "type": "singular_fact_conflict",
                            "resolution": resolution,
                        })
                        logger.info(
                            "Belief revision: contradiction detected — "
                            "'%s %s %s' conflicts with '%s %s %s' (resolution=%s)",
                            subject, relation, old_target,
                            subject, relation, keep_object, resolution,
                        )
                    if is_first_person:
                        # Overwrite protocol: deprecate the stale edge(s) so only
                        # the newest target survives in the active graph.
                        non_conflict[(subject, relation)] = keep_object
                else:
                    # No live conflicting edge (first appearance, or a prior run
                    # already deprecated the old target): just ensure the newest
                    # target is the kept one. Not a contradiction.
                    non_conflict[(subject, relation)] = keep_object

            if non_conflict:
                n_deleted, _old_targets = _deprecate_graph_edges(emb_conn, non_conflict)
                report.deprecated += n_deleted
        emb_conn.commit()
    finally:
        emb_conn.close()

    # Graph-RAG: push the full relationships into memory_manager as semantic
    # memories so they're retrievable by natural-language queries.
    report.semantic_memories = _flush_semantic_memories(pending_semantic)

    # Phase 56 — keep the vector store consistent with the revised graph: drop
    # any semantic memory whose value for a functional attribute is no longer the
    # current one. Only entries that were actually deprecated (no contradiction)
    # get their semantic memories purged — contradictory entries keep both
    # edges and both semantic memories so the conflict is visible to retrieval.
    if pending_singular:
        _deprecate_semantic_memories(non_conflict)

    # ── 6. Flag consolidated rows in raw memory (raw data is preserved) ─
    if done_ids:
        raw_conn = open_connection(str(raw_db_path))
        try:
            raw_conn.executemany(
                f"UPDATE triples SET {_CONSOLIDATED_COL} = 1 WHERE id = ?",
                [(tid,) for tid in done_ids],
            )
            raw_conn.commit()
        finally:
            raw_conn.close()

    logger.info(
        "Consolidation run complete: %d/%d moved (%d verified, %d inferred, "
        "%d vectors, %d deprecated, %d skipped, %d contradictions, %d errors)",
        report.consolidated, report.scanned, report.verified, report.inferred,
        report.embedded, report.deprecated, report.skipped,
        len(report.contradictions), len(report.errors),
    )
    return report


async def consolidate_pending_async(limit: Optional[int] = None) -> ConsolidationReport:
    """Async wrapper: run consolidation on a worker thread.

    Consolidation is CPU/IO-bound (SQLite + embedding model). Offloading to a
    thread keeps the event loop responsive when called from the async pipeline
    or scheduled as a fire-and-forget background task.

    Serialized by ``_consolidation_lock`` so concurrent TEACH turns never race
    on belief revision — only one ``consolidate_pending`` runs at a time.
    """
    async with _consolidation_lock:
        return await asyncio.to_thread(consolidate_pending, limit)


__all__ = [
    "ConsolidationReport",
    "consolidate_pending",
    "consolidate_pending_async",
    "has_pending_revision",
    "STATUS_VERIFIED",
    "STATUS_INFERRED",
    "CONFIDENCE_VERIFIED",
    "CONFIDENCE_INFERRED",
]

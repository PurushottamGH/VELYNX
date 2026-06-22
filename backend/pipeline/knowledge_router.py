"""Knowledge routing — KG fast path, semantic recall, learning dispatch."""
from __future__ import annotations

import asyncio
import html as _html
import logging
import re as _re
from typing import Any

from backend.models.answer import AnswerResponse

logger = logging.getLogger("uvicorn")


def looks_like_memory_request(text: str) -> bool:
    lowered = text.lower()
    return any(
        phrase in lowered
        for phrase in [
            "remember",
            "what did you say",
            "as you said",
            "last time",
            "earlier",
            "repeat",
            "recall",
        ]
    )


# Personal-preference / single-valued-attribute query signals. The supersession
# freshness check below reads the raw-memory DB, so we only pay for it when the
# query is ABOUT a re-teachable personal attribute (a "favorite", or a possessive
# "my/your <attribute>"). Abstract or definitional questions ("What is love?")
# match none of these and never touch the DB — zero added latency, by design.
_PREFERENCE_QUERY_RE = _re.compile(
    r"\bfavou?rite\b|\bprefer(?:ence|s|red|ring)?\b|\b(?:my|your|mine|yours)\b",
    _re.IGNORECASE,
)


def _looks_like_preference_query(text: str) -> bool:
    """Cheap, DB-free gate: is *text* about a personal preference / single-valued
    personal attribute (and therefore revision-prone)?

    Scopes the supersession freshness check so abstract/definitional questions
    add no retrieval latency. Pure string match — never opens a connection.
    """
    return bool(text) and bool(_PREFERENCE_QUERY_RE.search(text))


def _has_pending_supersession(kg_node: Any) -> bool:
    """True if the subject behind *kg_node* has a pending (un-consolidated)
    singular revision — it was re-taught and ``consolidate_pending`` has not yet
    reconciled it, so the cached value may be the stale "Avatar ghost".

    Delegates to ``consolidator.has_pending_revision``, which OWNS the
    pending-revision model (the ``triples.consolidated`` flag + functional-fact
    heuristics). The router does not reimplement that SQL — and crucially the
    consolidator scopes the check to *un-consolidated* rows, so a revision that
    has already been reconciled correctly stops deferring. (The previous direct
    ``COUNT(DISTINCT object)`` query had no such scope: because raw rows are
    preserved-but-flagged, it would defer a re-taught subject's fast path
    forever, even after the contradiction was resolved.)

    The belief store is intentionally NOT consulted: ``conversation.beliefs``
    is an ephemeral in-memory store with no pending/superseded revision state —
    the consolidator is the sole authority for "what is awaiting reconciliation".

    Read-only and fully defensive: a missing subject or any consolidator error
    returns ``False`` so a transient fault never blocks a valid fast-path hit.
    """
    # The node's subject key. The symbolic KG node exposes ``.concept``; fall
    # back to other plausible attributes so this keeps working if the node type
    # changes.
    subject = (
        getattr(kg_node, "concept", None)
        or getattr(kg_node, "subject", None)
        or getattr(kg_node, "topic", None)
    )
    if not subject:
        return False
    try:
        from backend.knowledge.consolidator import has_pending_revision

        return has_pending_revision(str(subject))
    except Exception:
        return False


async def handle_kg_fast_path(text: str, resonance_context: str) -> AnswerResponse | None:
    """
    KG fast path: direct lookup in the knowledge graph cache.

    Returns an AnswerResponse for KG hits, or None to let the full pipeline
    run. Only activates when resonance_context is empty (no soul activation).

    SMART-RETRIEVAL GUARD (freshness / supersession)
    -------------------------------------------------
    The fast path is fast-but-dumb: it returns a single cached KG node. That is
    unsafe when the same subject has been *re-taught* with a conflicting value
    (the "Interstellar -> Avatar" contradiction) but the contradiction has not
    yet been reconciled into a single winning triple. Returning the cached node
    in that window is exactly the stale-data RETRIEVAL_FAILURE at Interaction #2.

    Before trusting a hit we therefore ask a lightweight question: does the
    knowledge store hold MORE THAN ONE distinct object for this node's subject
    (i.e. an unresolved/pending contradiction)? If so we DEFER — return None so
    the smart-but-slow reasoning path runs, sees every competing assertion, and
    either picks the freshest or honestly reports the conflict. A clean,
    single-valued subject still takes the fast path unchanged.
    """
    if resonance_context:
        return None
    try:
        # NOTE (verified Jun 2026): ``backend/memory/knowledge_graph.py`` currently
        # exposes NO ``knowledge_graph`` singleton, so this import raises
        # ImportError and the whole fast path is presently INERT (always falls
        # through to return None). The supersession guard below is therefore
        # correct-but-dormant: it activates only once the singleton/lookup is
        # restored. Kept wired so reviving the path is safe-by-construction.
        from memory.knowledge_graph import knowledge_graph

        kg_node = knowledge_graph.lookup(text, threshold=0.3)
        if kg_node and kg_node.effective_confidence >= 0.3:
            # Context-aware supersession guard. ONLY for personal-preference
            # queries (the re-teachable, contradiction-prone case): if the
            # subject has a pending un-consolidated revision, the cached node may
            # be stale — defer to the reasoning path so the freshest fact wins
            # rather than serving a possibly-superseded value. Abstract or
            # definitional questions short-circuit before any DB access (see
            # _looks_like_preference_query), so they add zero latency. The whole
            # check is best-effort and read-only.
            if _looks_like_preference_query(text) and _has_pending_supersession(kg_node):
                logger.info(
                    "KG fast path deferring to reasoning: preference subject %r "
                    "has a pending (un-consolidated) revision (possible stale cache).",
                    getattr(kg_node, "concept", "?"),
                )
                return None

            clean_summary = _html.unescape(kg_node.summary)
            clean_summary = _re.sub(r"\(pronunciation[^)]*\)", "", clean_summary)
            clean_summary = _re.sub(r"\s+", " ", clean_summary).strip()
            conf = (
                "CERTAIN" if kg_node.effective_confidence >= 0.85 else
                "PROBABLE" if kg_node.effective_confidence >= 0.65 else
                "DEBATED" if kg_node.effective_confidence >= 0.40 else
                "LOW"
            )
            from backend.pipeline.persistence import record_memory_turn

            kg_result = {
                "answer": clean_summary,
                "confidence": conf,
                "sources": [],
                "gaps": [],
                "citations": [f"[KG] Learned from {kg_node.source_count} source(s)"],
                "tone": "human",
                "debug": {"kg_hit": True, "concept": kg_node.concept, "domain": kg_node.domain},
            }
            await record_memory_turn(
                text, kg_result, "knowledge_graph", ["kg", "terminal"]
            )
            return AnswerResponse(
                query=text,
                answer=clean_summary,
                confidence=conf,
                sources=[],
                contradictions=[],
                gaps=[],
                citations=kg_result["citations"],
                tone="human",
                debug=kg_result["debug"],
            )
    except Exception:
        pass
    return None

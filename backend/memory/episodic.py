"""
VELYNX Phase 61 — Episodic Narrative Memory
============================================

VELYNX accumulates *facts* (the Knowledge Graph), *beliefs* (the BeliefStore),
and *goals* (the Curiosity Engine), but it has had no memory of its own
**history** — the causal story of *how* a piece of knowledge came to exist. This
module gives VELYNX an autobiographical, causally-linked episodic memory so it
can answer questions like *"How did you learn about Blender?"* by replaying the
actual chain of events that produced that knowledge.

Five-layer architecture
------------------------
The module is organised as five cleanly separable layers, each usable in
isolation and individually testable:

  1. **Schema layer** — three SQLite tables (``episodes``, ``episode_links``,
     ``episode_effects``) plus the :class:`EpisodeKind` vocabulary. ``episodes``
     carries a denormalised ``parent_episode_id`` for O(depth) chain walking;
     ``episode_links`` is the general (cause -> effect) edge table; and
     ``episode_effects`` records the concrete world-changes an episode produced.
  2. **Significance Filter layer** — :class:`SignificanceFilter` scores a
     candidate event and rejects routine / boring activity so the autobiography
     stays a story of *consequential* moments, not a keystroke log.
  3. **Recording layer** — :class:`EpisodicManager` records events, applies the
     significance gate, resolves and writes causal links (``parent_episode_id``
     + an ``episode_links`` row), and persists effects.
  4. **Traversal layer** — :class:`EpisodicManager` query helpers
     (``get_episode``, ``episodes_for_entity``, ``find_recent_episode``,
     ``trace_chain``) that read the causal graph back out.
  5. **Narrative layer** — :class:`NarrativeCompressor` deterministically
     compresses a traversed causal chain into a natural-language story (no LLM).

Storage
-------
A single SQLite database (``velynx_data/episodic/episodes.db`` by default) opened
through the shared :func:`backend.memory._sqlite.connect` helper (WAL +
busy_timeout) so episodic writes from background curiosity threads never collide
with the request path. Every public method is best-effort and fully guarded: a
failure to record history must never break a user turn.
"""
from __future__ import annotations

import json
import logging
import re
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Optional

logger = logging.getLogger("velynx.episodic")

BACKEND_ROOT = Path(__file__).resolve().parent.parent

# Resolve the episodic DB path through the shared helper so it is redirected to a
# throwaway test database under VELYNX_TEST_MODE and `self.db_path` reflects the
# isolated location. No-op in production. Lazy import mirrors `_open`'s fallback
# for import-path variance (package vs flat layout).
try:
    from backend.memory._sqlite import resolve_db_path as _resolve_db_path
except Exception:  # pragma: no cover - import path variance
    from memory._sqlite import resolve_db_path as _resolve_db_path

DEFAULT_DB_PATH = _resolve_db_path(BACKEND_ROOT / "velynx_data" / "episodic" / "episodes.db")


def _open(db_path: Any):
    """Open a WAL SQLite connection via the shared helper (with fallback)."""
    try:
        from backend.memory._sqlite import connect
    except Exception:  # pragma: no cover - import path variance
        from memory._sqlite import connect  # type: ignore
    import sqlite3

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return connect(str(db_path), row_factory=sqlite3.Row)


# ══════════════════════════════════════════════════════════════════════════════
# Layer 1 — Schema
# ══════════════════════════════════════════════════════════════════════════════
class EpisodeKind(str, Enum):
    """The vocabulary of consequential events VELYNX records about itself."""

    QUERY_FAILURE = "QUERY_FAILURE"            # asked something it could not answer
    GOAL_CREATED = "GOAL_CREATED"              # curiosity formed a goal to fill a gap
    KNOWLEDGE_ACQUIRED = "KNOWLEDGE_ACQUIRED"  # a fact was learned / committed
    GOAL_SATISFIED = "GOAL_SATISFIED"          # a curiosity goal was resolved
    CONTRADICTION = "CONTRADICTION"            # a conflict between beliefs/facts
    BELIEF_FORMED = "BELIEF_FORMED"            # a new belief was abstracted
    # Routine / low-value kinds — recorded only if forced; filtered by default.
    ROUTINE_ANSWER = "ROUTINE_ANSWER"
    GREETING = "GREETING"
    REFLEX = "REFLEX"


class LinkType(str, Enum):
    """Edge semantics in the ``episode_links`` causal graph."""

    CAUSED = "caused"        # cause -> effect (generic)
    LED_TO = "led_to"        # a failure led to a goal
    RESOLVED = "resolved"    # an acquisition resolved a goal


_SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS episodes (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        episode_uid       TEXT UNIQUE NOT NULL,
        kind              TEXT NOT NULL,
        summary           TEXT NOT NULL DEFAULT '',
        entity            TEXT NOT NULL DEFAULT '',
        attribute         TEXT NOT NULL DEFAULT '',
        significance      REAL NOT NULL DEFAULT 0.0,
        parent_episode_id INTEGER,
        session_id        TEXT NOT NULL DEFAULT '',
        payload           TEXT NOT NULL DEFAULT '{}',
        created_at        REAL NOT NULL,
        FOREIGN KEY (parent_episode_id) REFERENCES episodes(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS episode_links (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        src_episode_id INTEGER NOT NULL,
        dst_episode_id INTEGER NOT NULL,
        link_type      TEXT NOT NULL DEFAULT 'caused',
        created_at     REAL NOT NULL,
        UNIQUE (src_episode_id, dst_episode_id, link_type),
        FOREIGN KEY (src_episode_id) REFERENCES episodes(id),
        FOREIGN KEY (dst_episode_id) REFERENCES episodes(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS episode_effects (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        episode_id  INTEGER NOT NULL,
        effect_type TEXT NOT NULL,
        target      TEXT NOT NULL DEFAULT '',
        detail      TEXT NOT NULL DEFAULT '',
        created_at  REAL NOT NULL,
        FOREIGN KEY (episode_id) REFERENCES episodes(id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_episodes_entity ON episodes(entity)",
    "CREATE INDEX IF NOT EXISTS idx_episodes_kind ON episodes(kind)",
    "CREATE INDEX IF NOT EXISTS idx_episodes_parent ON episodes(parent_episode_id)",
    "CREATE INDEX IF NOT EXISTS idx_effects_episode ON episode_effects(episode_id)",
)


# ══════════════════════════════════════════════════════════════════════════════
# Layer 2 — Significance Filter
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class SignificanceVerdict:
    """The filter's decision for a candidate event."""

    record: bool
    score: float
    reason: str


# Greeting / chit-chat the autobiography should never bother remembering.
_ROUTINE_QUERY_RE = re.compile(
    r"^\s*(hi|hey|hello|yo|sup|thanks|thank you|ok|okay|cool|nice|"
    r"good (morning|afternoon|evening|night)|bye|goodbye)\b",
    re.IGNORECASE,
)


class SignificanceFilter:
    """Decide whether an event is consequential enough to enter the life-story.

    Pure, deterministic scoring (no LLM). Each :class:`EpisodeKind` carries a
    base significance; the score is then nudged by payload signals (an empty
    knowledge acquisition is less significant than one with real triples; a
    failure on a greeting is not significant at all). An event is recorded iff
    its score meets :attr:`threshold`.
    """

    BASE_SIGNIFICANCE: dict[str, float] = {
        EpisodeKind.QUERY_FAILURE.value: 0.70,
        EpisodeKind.GOAL_CREATED.value: 0.60,
        EpisodeKind.KNOWLEDGE_ACQUIRED.value: 0.80,
        EpisodeKind.GOAL_SATISFIED.value: 0.75,
        EpisodeKind.CONTRADICTION.value: 0.90,
        EpisodeKind.BELIEF_FORMED.value: 0.65,
        EpisodeKind.ROUTINE_ANSWER.value: 0.10,
        EpisodeKind.GREETING.value: 0.05,
        EpisodeKind.REFLEX.value: 0.05,
    }

    def __init__(self, threshold: float = 0.30) -> None:
        self.threshold = threshold

    def evaluate(self, kind: str, payload: Optional[dict] = None) -> SignificanceVerdict:
        payload = payload or {}
        score = self.BASE_SIGNIFICANCE.get(kind, 0.40)

        query = str(payload.get("query", "") or "")
        if query and _ROUTINE_QUERY_RE.search(query):
            # A failure/answer on a greeting is routine, not a life event.
            score -= 0.60

        if kind == EpisodeKind.KNOWLEDGE_ACQUIRED.value:
            # Reward concrete learning; an acquisition with no facts/value is hollow.
            triples = payload.get("triples") or []
            value = str(payload.get("value", "") or "").strip()
            if triples:
                score += min(0.05 * len(triples), 0.15)
            elif not value:
                score -= 0.55

        if kind == EpisodeKind.QUERY_FAILURE.value:
            # A failure we cannot even attach to an entity is a weaker memory.
            if not str(payload.get("entity", "") or "").strip():
                score -= 0.25

        score = max(0.0, min(1.0, score))
        record = score >= self.threshold
        reason = (
            f"{kind} scored {score:.2f} "
            f"({'>=' if record else '<'} threshold {self.threshold:.2f})"
        )
        return SignificanceVerdict(record=record, score=score, reason=reason)


# ══════════════════════════════════════════════════════════════════════════════
# Layers 3 & 4 — Recording + Traversal (EpisodicManager)
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class Episode:
    """An in-memory view of a persisted episode row."""

    id: int
    episode_uid: str
    kind: str
    summary: str
    entity: str
    attribute: str
    significance: float
    parent_episode_id: Optional[int]
    session_id: str
    payload: dict
    created_at: float

    @classmethod
    def from_row(cls, row) -> "Episode":
        try:
            payload = json.loads(row["payload"]) if row["payload"] else {}
        except Exception:
            payload = {}
        return cls(
            id=row["id"],
            episode_uid=row["episode_uid"],
            kind=row["kind"],
            summary=row["summary"],
            entity=row["entity"],
            attribute=row["attribute"],
            significance=row["significance"],
            parent_episode_id=row["parent_episode_id"],
            session_id=row["session_id"],
            payload=payload,
            created_at=row["created_at"],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "episode_uid": self.episode_uid,
            "kind": self.kind,
            "summary": self.summary,
            "entity": self.entity,
            "attribute": self.attribute,
            "significance": round(self.significance, 3),
            "parent_episode_id": self.parent_episode_id,
            "session_id": self.session_id,
            "payload": self.payload,
            "created_at": self.created_at,
        }


def _norm(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def _tokens(value: str) -> list[str]:
    """Lowercased alphanumeric word tokens of *value* (punctuation stripped)."""
    return re.findall(r"[a-z0-9]+", (value or "").lower())


def _phrase_contains(haystack: str, needle: str) -> bool:
    """True if *needle* occurs as a contiguous whole-word run inside *haystack*.

    Whole-word and order-preserving, so it is forgiving about surrounding
    context ("the Driftwood OS platform" contains "Driftwood OS") WITHOUT the
    false positives a raw character substring invites ("os" would otherwise
    match "macos"/"closed"; "art" would match "Bartholomew"). Both sides are
    normalised to lowercase token lists first.
    """
    h = _tokens(haystack)
    n = _tokens(needle)
    if not n or len(n) > len(h):
        return False
    first = n[0]
    for i in range(len(h) - len(n) + 1):
        if h[i] == first and h[i:i + len(n)] == n:
            return True
    return False


def _terms_match(stored: str, target_norm: str) -> bool:
    """Compare one stored triple term against the queried entity, forgivingly.

    Layered, cheapest-first:
      1. Exact normalised equality — the canonical case (kept primary so prior
         behaviour and tests are unchanged).
      2. Whole-word phrase containment, but ONLY for a MULTI-WORD target. A
         multi-word entity ("Driftwood OS") still matches a stored term that
         wraps it in extra context ("the Driftwood OS project") and vice-versa.
         A SINGLE-token target is deliberately NOT matched as a fragment of a
         larger phrase: querying bare "os" must not pull in every "<X> OS"
         lesson, and short/common tokens ("art", "os") must never match via
         containment. Single tokens therefore match by exact equality only.
    """
    stored_norm = _norm(stored)
    if not stored_norm or not target_norm:
        return False
    if stored_norm == target_norm:
        return True
    # Forgiving containment is reserved for multi-word entities, where the extra
    # word(s) make a spurious collision vanishingly unlikely.
    if len(target_norm.split()) < 2:
        return False
    if _phrase_contains(stored_norm, target_norm):
        return True
    if _phrase_contains(target_norm, stored_norm):
        return True
    return False


def _episode_mentions_entity(ep: "Episode", target_norm: str) -> bool:
    """True if *ep* references *target_norm* in its entity column or any triple term.

    Scans the denormalised ``entity`` column plus every term of every triple in
    the payload (subject, relation, object) and the scalar ``value``. Matching
    layers exact normalised equality with a forgiving, WHOLE-WORD phrase
    containment fallback (see :func:`_terms_match`) so a multi-word entity stays
    matchable even when a stored term carries extra context words — while short
    tokens still cannot produce raw-substring false positives.
    """
    if not target_norm:
        return False
    if _terms_match(ep.entity, target_norm):
        return True
    payload = ep.payload or {}
    for triple in payload.get("triples") or []:
        try:
            for term in triple:
                if _terms_match(str(term), target_norm):
                    return True
        except TypeError:
            continue
    if _terms_match(str(payload.get("value", "")), target_norm):
        return True
    return False


class EpisodicManager:
    """Records consequential events and links them into a causal chain.

    Causality is captured twice for robustness: a denormalised
    ``parent_episode_id`` column on ``episodes`` (cheap chain walking) plus a row
    in the general ``episode_links`` edge table (supports multiple parents /
    typed edges). Convenience recorders
    (``record_query_failure`` / ``record_goal_created`` /
    ``record_knowledge_acquired``) resolve the appropriate causal parent
    automatically so the wiring sites stay trivial.
    """

    def __init__(
        self,
        db_path: Any = None,
        significance_filter: Optional[SignificanceFilter] = None,
    ) -> None:
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.filter = significance_filter or SignificanceFilter()
        self._ensure_schema()

    # ── schema ────────────────────────────────────────────────────────────
    def _ensure_schema(self) -> None:
        try:
            conn = _open(self.db_path)
            try:
                for stmt in _SCHEMA:
                    conn.execute(stmt)
                conn.commit()
            finally:
                conn.close()
        except Exception as exc:  # pragma: no cover - never block on schema
            logger.warning("Episodic: schema init failed: %s", exc)

    # ── Layer 3: recording ──────────────────────────────────────────────────
    def record(
        self,
        kind: EpisodeKind | str,
        summary: str,
        *,
        entity: Optional[str] = None,
        attribute: Optional[str] = None,
        session_id: Optional[str] = None,
        payload: Optional[dict] = None,
        parent_episode_id: Optional[int] = None,
        link_type: LinkType | str = LinkType.CAUSED,
        effects: Optional[Iterable[dict]] = None,
        force: bool = False,
    ) -> Optional[int]:
        """Record an episode, applying the significance gate and causal links.

        Returns the new episode id, or ``None`` if the significance filter
        rejected the event (and ``force`` was not set) or a write failed.
        """
        kind_val = kind.value if isinstance(kind, EpisodeKind) else str(kind)
        link_val = link_type.value if isinstance(link_type, LinkType) else str(link_type)
        payload = dict(payload or {})
        payload.setdefault("entity", entity or "")
        payload.setdefault("attribute", attribute or "")

        verdict = self.filter.evaluate(kind_val, payload)
        if not verdict.record and not force:
            logger.debug("Episodic: filtered out (%s)", verdict.reason)
            return None

        now = time.time()
        uid = uuid.uuid4().hex
        try:
            conn = _open(self.db_path)
            try:
                cur = conn.execute(
                    """
                    INSERT INTO episodes
                        (episode_uid, kind, summary, entity, attribute,
                         significance, parent_episode_id, session_id, payload, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        uid, kind_val, summary or "", _norm(entity), _norm(attribute),
                        float(verdict.score), parent_episode_id, session_id or "",
                        json.dumps(payload, default=str), now,
                    ),
                )
                episode_id = int(cur.lastrowid)

                if parent_episode_id is not None:
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO episode_links
                            (src_episode_id, dst_episode_id, link_type, created_at)
                        VALUES (?, ?, ?, ?)
                        """,
                        (int(parent_episode_id), episode_id, link_val, now),
                    )

                for effect in (effects or []):
                    conn.execute(
                        """
                        INSERT INTO episode_effects
                            (episode_id, effect_type, target, detail, created_at)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            episode_id,
                            str(effect.get("effect_type", "")),
                            str(effect.get("target", "")),
                            str(effect.get("detail", "")),
                            now,
                        ),
                    )
                conn.commit()
            finally:
                conn.close()
        except Exception as exc:
            logger.warning("Episodic: record(%s) failed: %s", kind_val, exc)
            return None

        logger.info(
            "Episodic: recorded %s #%d (entity=%r attr=%r parent=%s sig=%.2f)",
            kind_val, episode_id, _norm(entity), _norm(attribute),
            parent_episode_id, verdict.score,
        )
        return episode_id

    # ── convenience recorders (resolve causal parent automatically) ─────────
    def record_query_failure(
        self,
        query: str,
        *,
        entity: Optional[str] = None,
        attribute: Optional[str] = None,
        session_id: Optional[str] = None,
        confidence: Optional[str] = None,
    ) -> Optional[int]:
        ent = entity or ""
        summary = (
            f"I was asked {query!r} but could not answer it"
            + (f" about {ent}" if ent else "")
            + "."
        )
        return self.record(
            EpisodeKind.QUERY_FAILURE,
            summary,
            entity=entity,
            attribute=attribute,
            session_id=session_id,
            payload={"query": query, "confidence": confidence, "entity": ent},
        )

    def record_goal_created(
        self,
        entity: str,
        attribute: str,
        *,
        priority: Optional[int] = None,
        goal_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Optional[int]:
        # Causal parent: the most recent failure about this entity (preferring
        # one that named the same attribute).
        parent = self.find_recent_episode(
            EpisodeKind.QUERY_FAILURE, entity=entity, attribute=attribute
        ) or self.find_recent_episode(EpisodeKind.QUERY_FAILURE, entity=entity)
        summary = (
            f"I noticed I didn't know the {attribute.replace('_', ' ')} of "
            f"{entity}, so I set a goal to learn it."
        )
        return self.record(
            EpisodeKind.GOAL_CREATED,
            summary,
            entity=entity,
            attribute=attribute,
            session_id=session_id,
            parent_episode_id=parent,
            link_type=LinkType.LED_TO,
            payload={"priority": priority, "goal_id": goal_id},
            effects=[{
                "effect_type": "goal_created",
                "target": f"{_norm(entity)}.{_norm(attribute)}",
                "detail": f"priority={priority}",
            }],
        )

    def record_knowledge_acquired(
        self,
        entity: str,
        *,
        attribute: Optional[str] = None,
        value: Optional[str] = None,
        triples: Optional[list] = None,
        summary: Optional[str] = None,
        session_id: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Optional[int]:
        # Causal parent: the goal that sought this attribute (or any goal on the
        # entity), so the acquisition "resolves" the curiosity that preceded it.
        parent = None
        if attribute:
            parent = self.find_recent_episode(
                EpisodeKind.GOAL_CREATED, entity=entity, attribute=attribute
            )
        if parent is None:
            parent = self.find_recent_episode(EpisodeKind.GOAL_CREATED, entity=entity)

        if not summary:
            if attribute and value:
                summary = f"I learned that the {attribute.replace('_', ' ')} of {entity} is {value}."
            elif value:
                summary = f"I learned that {entity} is {value}."
            else:
                summary = f"I learned new facts about {entity}."

        effects = []
        for t in (triples or []):
            try:
                effects.append({
                    "effect_type": "triple_learned",
                    "target": f"{t[0]} -{t[1]}-> {t[2]}",
                    "detail": str(source or ""),
                })
            except Exception:
                continue
        if value and not effects:
            effects.append({
                "effect_type": "attribute_learned",
                "target": f"{_norm(entity)}.{_norm(attribute)}",
                "detail": value,
            })

        return self.record(
            EpisodeKind.KNOWLEDGE_ACQUIRED,
            summary,
            entity=entity,
            attribute=attribute,
            session_id=session_id,
            parent_episode_id=parent,
            link_type=LinkType.RESOLVED,
            payload={"value": value, "triples": triples, "source": source},
            effects=effects,
        )

    # ── Layer 4: traversal / retrieval ──────────────────────────────────────
    def get_episode(self, episode_id: Optional[int]) -> Optional[Episode]:
        if episode_id is None:
            return None
        try:
            conn = _open(self.db_path)
            try:
                row = conn.execute(
                    "SELECT * FROM episodes WHERE id = ?", (int(episode_id),)
                ).fetchone()
            finally:
                conn.close()
        except Exception as exc:
            logger.debug("Episodic: get_episode(%s) failed: %s", episode_id, exc)
            return None
        return Episode.from_row(row) if row else None

    def find_recent_episode(
        self,
        kind: EpisodeKind | str,
        *,
        entity: Optional[str] = None,
        attribute: Optional[str] = None,
    ) -> Optional[int]:
        """Return the id of the most recent episode matching the filters."""
        kind_val = kind.value if isinstance(kind, EpisodeKind) else str(kind)
        clauses = ["kind = ?"]
        params: list[Any] = [kind_val]
        if entity is not None:
            clauses.append("entity = ?")
            params.append(_norm(entity))
        if attribute is not None:
            clauses.append("attribute = ?")
            params.append(_norm(attribute))
        sql = (
            "SELECT id FROM episodes WHERE " + " AND ".join(clauses)
            + " ORDER BY created_at DESC, id DESC LIMIT 1"
        )
        try:
            conn = _open(self.db_path)
            try:
                row = conn.execute(sql, tuple(params)).fetchone()
            finally:
                conn.close()
        except Exception as exc:
            logger.debug("Episodic: find_recent_episode failed: %s", exc)
            return None
        return int(row["id"]) if row else None

    def episodes_for_entity(
        self, entity: str, *, kind: Optional[EpisodeKind | str] = None, limit: int = 50
    ) -> list[Episode]:
        clauses = ["entity = ?"]
        params: list[Any] = [_norm(entity)]
        if kind is not None:
            clauses.append("kind = ?")
            params.append(kind.value if isinstance(kind, EpisodeKind) else str(kind))
        sql = (
            "SELECT * FROM episodes WHERE " + " AND ".join(clauses)
            + " ORDER BY created_at DESC, id DESC LIMIT ?"
        )
        params.append(int(limit))
        try:
            conn = _open(self.db_path)
            try:
                rows = conn.execute(sql, tuple(params)).fetchall()
            finally:
                conn.close()
        except Exception as exc:
            logger.debug("Episodic: episodes_for_entity(%r) failed: %s", entity, exc)
            return []
        return [Episode.from_row(r) for r in rows]

    def acquisitions_mentioning(self, entity: str, *, limit: int = 50) -> list[Episode]:
        """Return KNOWLEDGE_ACQUIRED episodes that reference *entity* anywhere.

        A taught fact like "Alice created SuperMegaSoftware" is extracted as the
        triple ``(alice, created, supermegasoftware)`` and the acquisition episode
        is tagged to the triple *subject* ("alice"). But the user usually asks
        "How did you learn who created **SuperMegaSoftware**?" — i.e. about the
        *object*. Tagging by subject alone makes that lesson invisible to an
        object-centric query (the Interaction #7 bug).

        This method bridges that gap by scanning each acquisition's stored
        ``triples`` (and ``value``) in its payload and returning every episode
        whose triple mentions *entity* in ANY position — subject, relation, or
        object — newest-first. It is the retrieval-side complement to the
        entity-column index: ``episodes_for_entity`` finds acquisitions tagged
        *to* the entity, while this finds acquisitions that merely *mention* it.
        """
        target = _norm(entity)
        if not target:
            return []
        try:
            conn = _open(self.db_path)
            try:
                rows = conn.execute(
                    "SELECT * FROM episodes WHERE kind = ? "
                    "ORDER BY created_at DESC, id DESC LIMIT ?",
                    (EpisodeKind.KNOWLEDGE_ACQUIRED.value, int(max(limit, 1) * 8)),
                ).fetchall()
            finally:
                conn.close()
        except Exception as exc:
            logger.debug("Episodic: acquisitions_mentioning(%r) failed: %s", entity, exc)
            return []

        out: list[Episode] = []
        for r in rows:
            try:
                ep = Episode.from_row(r)
            except Exception:
                continue
            if _episode_mentions_entity(ep, target):
                out.append(ep)
            if len(out) >= limit:
                break
        return out

    def known_entities(self) -> list[str]:
        """Return the distinct, non-empty entity names referenced by any episode.

        Used by the narrative layer to resolve which remembered entity a free-form
        question ("How did you learn who created Blender?") is actually about —
        we pick the known entity whose name appears in the question text.
        """
        try:
            conn = _open(self.db_path)
            try:
                rows = conn.execute(
                    "SELECT DISTINCT entity FROM episodes "
                    "WHERE entity IS NOT NULL AND entity != '' ORDER BY entity"
                ).fetchall()
            finally:
                conn.close()
        except Exception as exc:
            logger.debug("Episodic: known_entities failed: %s", exc)
            return []
        return [r["entity"] for r in rows if r["entity"]]

    def get_effects(self, episode_id: int) -> list[dict]:
        try:
            conn = _open(self.db_path)
            try:
                rows = conn.execute(
                    "SELECT effect_type, target, detail FROM episode_effects "
                    "WHERE episode_id = ? ORDER BY id",
                    (int(episode_id),),
                ).fetchall()
            finally:
                conn.close()
        except Exception as exc:
            logger.debug("Episodic: get_effects(%s) failed: %s", episode_id, exc)
            return []
        return [
            {"effect_type": r["effect_type"], "target": r["target"], "detail": r["detail"]}
            for r in rows
        ]

    def trace_chain(self, episode_id: int) -> list[Episode]:
        """Walk ``parent_episode_id`` from *episode_id* to the root.

        Returns the chain ordered ROOT-FIRST (oldest cause -> final effect), so a
        narrator can replay events in the order they happened. Cycle-safe.
        """
        chain: list[Episode] = []
        seen: set[int] = set()
        cur = self.get_episode(episode_id)
        while cur is not None and cur.id not in seen:
            chain.append(cur)
            seen.add(cur.id)
            cur = self.get_episode(cur.parent_episode_id)
        chain.reverse()
        return chain

    # ── Phase 61: single-statement recursive CTE traversal ───────────────────
    _CAUSAL_CHAIN_SQL = """
    WITH RECURSIVE chain(
        depth, id, episode_uid, kind, summary, entity, attribute,
        significance, parent_episode_id, session_id, payload, created_at,
        link_type
    ) AS (
        -- Anchor: the target episode (leaf / final effect).
        SELECT 0, e.id, e.episode_uid, e.kind, e.summary, e.entity,
               e.attribute, e.significance, e.parent_episode_id,
               e.session_id, e.payload, e.created_at, '' AS link_type
        FROM episodes e
        WHERE e.id = ?
        UNION ALL
        -- Recursive step: traverse UP episode_links (dst -> src = effect -> cause),
        -- constrained to the denormalised parent_episode_id so the walk stays
        -- linear and deterministic even if multiple typed edges exist.
        SELECT c.depth + 1, p.id, p.episode_uid, p.kind, p.summary, p.entity,
               p.attribute, p.significance, p.parent_episode_id, p.session_id,
               p.payload, p.created_at, l.link_type
        FROM chain c
        JOIN episode_links l
            ON l.dst_episode_id = c.id
           AND l.src_episode_id = c.parent_episode_id
        JOIN episodes p ON p.id = l.src_episode_id
        WHERE c.depth < 100
          AND c.parent_episode_id IS NOT NULL
    )
    SELECT * FROM chain ORDER BY depth DESC, id ASC
    """

    def get_causal_chain(self, target_episode_id: int) -> list[dict]:
        """Traverse UP the causal graph from *target_episode_id* to its origin.

        Implemented as a single ``WITH RECURSIVE`` CTE over ``episode_links``
        (cause -> effect edges) so the entire chain is fetched in one round-trip
        rather than one query per hop (the ``trace_chain`` fallback). The walk
        follows ``parent_episode_id`` to stay linear and is bounded by a depth
        cap of 100, making it cycle-safe even under corrupted data.

        Returns a list of dicts ordered ROOT-FIRST (oldest cause -> final
        effect). Each dict carries the episode fields plus ``depth`` (0 at the
        target, increasing toward the root) and ``link_type`` (the
        :class:`LinkType` of the inbound edge, or ``''`` at the target).
        """
        try:
            conn = _open(self.db_path)
            try:
                rows = conn.execute(
                    self._CAUSAL_CHAIN_SQL, (int(target_episode_id),)
                ).fetchall()
            finally:
                conn.close()
        except Exception as exc:
            logger.debug(
                "Episodic: get_causal_chain(%s) failed: %s", target_episode_id, exc
            )
            return []

        chain: list[dict] = []
        seen: set[int] = set()
        for row in rows:
            try:
                ep = Episode.from_row(row).to_dict()
            except Exception:
                continue
            eid = ep.get("id")
            if eid in seen:  # defensive: dedupe any residual cycle
                continue
            seen.add(eid)
            ep["depth"] = int(row["depth"]) if "depth" in row.keys() else 0
            ep["link_type"] = row["link_type"] if "link_type" in row.keys() else ""
            chain.append(ep)
        return chain

    # ── maintenance ─────────────────────────────────────────────────────────
    def stats(self) -> dict:
        try:
            conn = _open(self.db_path)
            try:
                total = conn.execute("SELECT COUNT(*) AS n FROM episodes").fetchone()["n"]
                links = conn.execute("SELECT COUNT(*) AS n FROM episode_links").fetchone()["n"]
                effects = conn.execute("SELECT COUNT(*) AS n FROM episode_effects").fetchone()["n"]
                by_kind = {
                    r["kind"]: r["n"]
                    for r in conn.execute(
                        "SELECT kind, COUNT(*) AS n FROM episodes GROUP BY kind"
                    ).fetchall()
                }
            finally:
                conn.close()
        except Exception:
            return {"episodes": 0, "links": 0, "effects": 0, "by_kind": {}}
        return {"episodes": total, "links": links, "effects": effects, "by_kind": by_kind}

    def clear(self) -> None:
        """Wipe all episodic memory (used by tests)."""
        try:
            conn = _open(self.db_path)
            try:
                conn.execute("DELETE FROM episode_effects")
                conn.execute("DELETE FROM episode_links")
                conn.execute("DELETE FROM episodes")
                conn.commit()
            finally:
                conn.close()
        except Exception as exc:
            logger.debug("Episodic: clear failed: %s", exc)


# ══════════════════════════════════════════════════════════════════════════════
# Layer 5 — Narrative Compression
# ══════════════════════════════════════════════════════════════════════════════
# "How did you learn about X?" — pull X out of the question, then narrate.
_LEARN_QUERY_RE = re.compile(
    r"\bhow\s+did\s+you\s+(?:learn|come\s+to\s+know|find\s+out|discover|get\s+to\s+know)"
    r"\s+(?:about\s+|of\s+)?(?P<ent>.+)$",
    re.IGNORECASE,
)
_LEADING_DET = re.compile(r"^(?:the|a|an)\s+", re.IGNORECASE)


def extract_learning_subject(query: str) -> str:
    """Extract the entity X from a 'How did you learn about X?' question."""
    if not query or not query.strip():
        return ""
    m = _LEARN_QUERY_RE.search(query.strip())
    if not m:
        return ""
    ent = m.group("ent").strip().rstrip("?.!").strip().strip("\"'").strip()
    return _LEADING_DET.sub("", ent).strip()


class NarrativeCompressor:
    """Compress a causal episode chain into a deterministic natural-language story."""

    def __init__(self, manager: Optional[EpisodicManager] = None) -> None:
        self._manager = manager

    @property
    def manager(self) -> EpisodicManager:
        if self._manager is None:
            self._manager = episodic_manager
        return self._manager

    def how_did_you_learn(self, entity: str) -> str:
        """Answer "How did you learn about <entity>?" by replaying its history.

        The causal story spans three phases — the retrieval/knowledge FAILURE,
        the curiosity GAP it provoked, and the eventual ACQUISITION. These are
        recorded as separate episodes and, depending on the order events
        happened in, are not always joined by a single ``parent_episode_id``
        chain (e.g. the goal can be created before the failing question is ever
        asked). We therefore assemble the *full* relevant history for the entity
        — every QUERY_FAILURE / GOAL_CREATED / GOAL_SATISFIED / KNOWLEDGE_ACQUIRED
        episode plus the strict parent chain of the latest acquisition — and
        narrate it in the order it actually unfolded.
        """
        entity = (entity or "").strip()
        if not entity:
            return "I'm not sure which topic you mean."

        # Phase 61+: assemble the FULL relevant history for the entity and
        # narrate it in causal order. We prefer a chain that covers more of the
        # three causal phases (failure -> gap -> acquisition). The physical
        # parent_episode_id chain (get_causal_chain) is often INCOMPLETE because
        # the failure, the goal, and the acquisition are recorded independently
        # and aren't always linked by a single parent pointer (e.g. the taught
        # fact is tagged to the triple subject "alice" while the failure/goal are
        # tagged to the object "supermegasoftware"). So we also build the chain
        # from the entity-scoped history (which now folds in acquisitions that
        # merely *mention* the entity) and keep whichever covers more phases.
        history = self._collect_history(entity)

        physical_chain: list[dict] = []
        target_id = self.manager.find_recent_episode(
            EpisodeKind.KNOWLEDGE_ACQUIRED, entity=entity
        )
        if target_id is None:
            mentioning = self.manager.acquisitions_mentioning(entity, limit=1)
            if mentioning:
                target_id = mentioning[0].id
        if target_id is not None:
            physical_chain = self.manager.get_causal_chain(target_id)

        history_chain = [ep.to_dict() for ep in history]

        def _phase_coverage(chain: list[dict]) -> int:
            kinds = {e.get("kind", "") for e in chain}
            return sum(
                1 for k in (
                    EpisodeKind.QUERY_FAILURE.value,
                    EpisodeKind.GOAL_CREATED.value,
                    EpisodeKind.KNOWLEDGE_ACQUIRED.value,
                ) if k in kinds
            )

        # Choose the richer narrative source: more causal phases wins; ties break
        # toward the explicit physical chain (it encodes real causal links).
        best_chain = history_chain
        if _phase_coverage(physical_chain) >= _phase_coverage(history_chain) and physical_chain:
            best_chain = physical_chain

        if len(best_chain) > 1:
            narrative = self.compress(best_chain, subject_entity=entity)
            if narrative:
                return narrative

        # Fallback: collect entity-scoped history and narrate step by step.
        if not history:
            return (
                f"I don't have a recorded history of how I learned about "
                f"{entity} - it isn't in my episodic memory."
            )

        has_acquisition = any(
            ep.kind == EpisodeKind.KNOWLEDGE_ACQUIRED.value for ep in history
        )
        narrative = self._narrate_chain(history, entity)
        if not has_acquisition:
            return f"I haven't actually learned about {entity} yet. " + narrative
        return narrative

    def _collect_history(self, entity: str) -> list[Episode]:
        """Gather and time-order every episode relevant to *entity*'s learning.

        Merges all episodes tagged with the entity (across kinds), every
        acquisition that *mentions* the entity in its triples (even if tagged to
        a different entity), and the strict parent chain of the most recent
        acquisition, de-duplicates by id, and sorts ROOT-FIRST (oldest cause ->
        final effect) so the narrator replays them in chronological order — the
        most recent lesson always lands last and frames the answer.
        """
        eps = self.manager.episodes_for_entity(entity, limit=200)
        by_id: dict[int, Episode] = {ep.id: ep for ep in eps}

        # Bridge the subject/object tagging gap: include acquisitions that
        # MENTION this entity in their triples even if they were tagged to a
        # different entity (e.g. the lesson "Alice created X" is tagged to
        # "alice" but answers a question about "X"). Without this, an
        # object-centric "How did you learn ...?" would only ever see the older
        # QUERY_FAILURE and wrongly conclude nothing was learned (Interaction #7).
        mentioning = self.manager.acquisitions_mentioning(entity, limit=200)
        for me in mentioning:
            by_id.setdefault(me.id, me)

        acquisitions = [
            ep for ep in by_id.values() if ep.kind == EpisodeKind.KNOWLEDGE_ACQUIRED.value
        ]
        if acquisitions:
            # Trace the parent chain of the MOST RECENT acquisition so the story
            # is anchored on the latest lesson, not an older one.
            latest = max(acquisitions, key=lambda ep: (ep.created_at, ep.id))
            for ce in self.manager.trace_chain(latest.id):
                by_id.setdefault(ce.id, ce)

        return sorted(by_id.values(), key=lambda ep: (ep.created_at, ep.id))

    # ── Phase 61: deterministic rule engine ───────────────────────────────────────
    @staticmethod
    def compress(chain: list[dict], subject_entity: Optional[str] = None) -> str:
        """Deterministically compress a causal chain into a natural-language summary.

        Pure rule engine — no LLM. Recognises patterns like:
        - Repeated failure + eventual success
        - Direct acquisition
        - Contradiction resolution

        Parameters
        ----------
        chain: list[dict]
            A causal chain as returned by ``get_causal_chain``, ordered ROOT-FIRST
            (oldest cause -> final effect). Each dict must have ``kind``, ``entity``,
            ``attribute``, ``summary``, and ``payload`` keys (matching ``Episode.to_dict``).
        subject_entity: Optional[str]
            The entity the question is actually *about*. When provided it anchors
            the narrative's subject and lets the value resolver pick the OTHER
            term of a learned triple as the answer (e.g. for the queried entity
            "supermegasoftware" and triple ``(alice, created, supermegasoftware)``
            the value resolves to "alice", not the entity itself).

        Returns
        -------
        str
            A deterministic narrative summary of the chain.
        """
        if not chain:
            return "I have no causal history to narrate."

        kinds = [e.get("kind", "") for e in chain]
        entities = [e.get("entity") for e in chain if e.get("entity")]
        attributes = [e.get("attribute") for e in chain if e.get("attribute")]
        summaries = [e.get("summary") for e in chain if e.get("summary")]

        # Anchor the story on the entity actually asked about when known; else
        # fall back to the last entity tag seen in the chain.
        subj_norm = _norm(subject_entity)
        raw_entity = subject_entity or (entities[-1] if entities else "it")
        entity = raw_entity.replace("_", " ").strip().title()
        attribute = (attributes[-1] if attributes else "")
        value = ""
        for e in reversed(chain):
            payload = e.get("payload") or {}
            if payload.get("value"):
                value = str(payload.get("value")).strip()
                break
            # No scalar value — derive it from a learned triple: the term that is
            # NOT the queried entity is the answer (subject of "X created <ent>").
            if subj_norm:
                for triple in payload.get("triples") or []:
                    try:
                        terms = [str(t).strip() for t in triple]
                    except TypeError:
                        continue
                    others = [t for t in terms if _norm(t) != subj_norm]
                    # Skip the relation (middle term) — prefer subject/object.
                    if len(terms) == 3 and others:
                        cand = terms[0] if _norm(terms[0]) != subj_norm else terms[2]
                        value = cand.replace("_", " ").strip()
                        break
                if value:
                    break

        failure_count = kinds.count(EpisodeKind.QUERY_FAILURE.value)
        has_goal = EpisodeKind.GOAL_CREATED.value in kinds
        has_acquisition = EpisodeKind.KNOWLEDGE_ACQUIRED.value in kinds
        has_contradiction = EpisodeKind.CONTRADICTION.value in kinds

        if failure_count >= 1 and has_goal and has_acquisition:
            if failure_count == 1:
                return (
                    f"I attempted retrieval for {entity}, failed, generated a curiosity "
                    f"goal to learn the {attribute.replace('_', ' ')} of {entity}, and "
                    f"successfully learned {value or entity}."
                )
            else:
                return (
                    f"After {failure_count} failed attempts to learn {entity}, I "
                    f"generated a curiosity goal and eventually succeeded in learning "
                    f"{value or entity}."
                )

        if has_contradiction and has_acquisition:
            return (
                f"I detected a contradiction involving {entity}, investigated, and "
                f"resolved it by learning {value or entity}."
            )

        # Failure(s) followed by an acquisition, but no explicit curiosity goal
        # in between (the goal was never recorded, or the failure and the lesson
        # were tagged to different entities). Still narrate BOTH phases so the
        # story reflects that an earlier inability was later resolved.
        if failure_count >= 1 and has_acquisition:
            learned = value or entity
            attempts = (
                "" if failure_count == 1
                else f" after {failure_count} unanswered attempts"
            )
            return (
                f"I was initially asked about {entity} and could not answer, then "
                f"later learned {learned}{attempts}."
            )

        if has_acquisition:
            return (
                f"I learned {value or entity} about {entity}."
                if value and entity.lower() not in value.lower()
                else f"I learned new facts about {entity}."
            )

        if failure_count >= 1 and not has_acquisition:
            return (
                f"I attempted to learn about {entity} but could not acquire the "
                f"knowledge after {failure_count} attempt(s)."
            )

        if summaries:
            return (
                NarrativeCompressor._stitch(summaries)
                if len(summaries) > 1
                else (summaries[0] or "")
            )

        return f"I have no narratable history for {entity}."

    # ── deterministic templating ────────────────────────────────────────────
    def _narrate_chain(self, chain: list[Episode], entity: str) -> str:
        if not chain:
            return f"I have no causal record of how I came to know about {entity}."

        sentences: list[str] = []
        for ep in chain:
            sentence = self._sentence_for(ep)
            if sentence:
                sentences.append(sentence)

        if not sentences:
            return f"I have no narratable history for {entity}."

        intro = f"Here's how I came to know about {entity}: "
        body = self._stitch(sentences)
        return intro + body

    @staticmethod
    def _stitch(sentences: list[str]) -> str:
        """Join step-sentences with light temporal connectives."""
        if len(sentences) == 1:
            return sentences[0]
        connectives = ["First, ", "Then, ", "After that, ", "Finally, "]
        out: list[str] = []
        for i, s in enumerate(sentences):
            if i == 0:
                prefix = connectives[0]
            elif i == len(sentences) - 1:
                prefix = connectives[-1]
            else:
                prefix = connectives[min(i, len(connectives) - 2)]
            # Lower-case the first letter of the original sentence after the
            # connective — but never demote the pronoun "I".
            if s.startswith("I ") or s.startswith("I'"):
                s_body = s
            else:
                s_body = s[0].lower() + s[1:] if s else s
            out.append(prefix + s_body)
        return " ".join(out)

    @staticmethod
    def _sentence_for(ep: Episode) -> str:
        """One clause per episode kind. Falls back to the stored summary."""
        attr = ep.attribute.replace("_", " ").strip()
        ent = ep.entity or "it"
        if ep.kind == EpisodeKind.QUERY_FAILURE.value:
            return ep.summary or f"I was asked about {ent} but couldn't answer."
        if ep.kind == EpisodeKind.GOAL_CREATED.value:
            if attr:
                return (
                    f"I noticed I didn't know the {attr} of {ent}, so I set "
                    f"myself a curiosity goal to learn it."
                )
            return (
                f"I noticed a gap in what I knew about {ent}, so I set myself a "
                f"curiosity goal to fill it."
            )
        if ep.kind == EpisodeKind.KNOWLEDGE_ACQUIRED.value:
            return ep.summary or f"I learned new facts about {ent}."
        if ep.kind == EpisodeKind.GOAL_SATISFIED.value:
            return ep.summary or f"I resolved my goal about {ent}."
        return ep.summary or ""

    def how_did_you_learn_from_query(self, query: str) -> Optional[str]:
        """If *query* is a 'how did you learn X' question, answer it; else None."""
        subject = extract_learning_subject(query)
        if not subject:
            return None
        return self.how_did_you_learn(subject)


# ══════════════════════════════════════════════════════════════════════════════
# Layer 6 — Public Narrative Handler (Phase 61 discovery entry-point)
# ══════════════════════════════════════════════════════════════════════════════
class EpisodicNarrativeHandler:
    """Thin, discoverable facade over the :class:`NarrativeCompressor`.

    This is the public entry point the pipeline (and the Phase 61 test harness)
    talk to. It exposes a single ``narrate`` method that accepts either a raw
    "How did you learn …?" *question* or a bare *entity* and returns a
    natural-language account of the causal chain (failure -> curiosity gap ->
    acquisition). All heavy lifting is delegated to the shared
    :data:`narrative_compressor`; this class only resolves *which* remembered
    entity the question is about and forwards the call.
    """

    def __init__(self, compressor: Optional[NarrativeCompressor] = None) -> None:
        self._compressor = compressor

    @property
    def compressor(self) -> NarrativeCompressor:
        if self._compressor is None:
            self._compressor = narrative_compressor
        return self._compressor

    def narrate(self, query: str, entity: Optional[str] = None) -> str:
        """Narrate how VELYNX learned about the entity referenced in *query*.

        ``query`` may be a full question ("How did you learn who created
        Blender?") or a bare entity name. An optional explicit ``entity`` hint
        takes precedence over resolution from the query text. Always returns a
        non-empty string by delegating to :data:`narrative_compressor`.
        """
        target = (entity or "").strip()
        if not target:
            target = self._resolve_entity(query)

        if target:
            return self.compressor.how_did_you_learn(target)

        # Fall back to the compressor's own "how did you learn X" parser.
        answer = self.compressor.how_did_you_learn_from_query(query)
        if answer:
            return answer

        subject = extract_learning_subject(query)
        return self.compressor.how_did_you_learn(subject or (query or "").strip())

    def _resolve_entity(self, query: str) -> str:
        """Pick the remembered entity whose name appears in *query* (longest match).

        Handles questions where the grammatical object is not the entity we
        actually have history for, e.g. "How did you learn who created Blender?"
        resolves to ``Blender`` rather than the noun phrase "who created Blender".
        """
        text = (query or "").lower()
        if not text:
            return ""
        best = ""
        try:
            known = self.compressor.manager.known_entities()
        except Exception:
            known = []
        for ent in known:
            forms = {ent.lower(), ent.lower().replace("_", " ")}
            for form in forms:
                # Whole-word containment (via the shared boundary-safe helper)
                # rather than raw substring: a stored entity "os" must appear as
                # a standalone word in the question, never inside "closed"/"macos".
                # Longest matching form still wins so the full multi-word entity
                # ("driftwood os") is preferred over any shorter token ("os").
                if form and _phrase_contains(text, form) and len(form) > len(best):
                    best = ent
        return best


# ── Process-wide singletons ─────────────────────────────────────────────────
episodic_manager = EpisodicManager()
narrative_compressor = NarrativeCompressor(episodic_manager)
episodic_narrative_handler = EpisodicNarrativeHandler(narrative_compressor)


__all__ = [
    "EpisodeKind",
    "LinkType",
    "SignificanceFilter",
    "SignificanceVerdict",
    "Episode",
    "EpisodicManager",
    "NarrativeCompressor",
    "EpisodicNarrativeHandler",
    "extract_learning_subject",
    "episodic_manager",
    "narrative_compressor",
    "episodic_narrative_handler",
    "DEFAULT_DB_PATH",
]

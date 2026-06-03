"""
VELYNX CORE v2 — memory.py
Unified knowledge store: graph-native + vector embeddings, one interface.
Crash-safe: every write is atomic via SQLite WAL mode.
"""

import sqlite3
import json
import time
import hashlib
import logging
import numpy as np
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager

logger = logging.getLogger("velynx.memory")

# ── Data types ──────────────────────────────────────────────────────────────

@dataclass
class Concept:
    id: str
    name: str
    domain: str
    what: str          # WHAT it is
    why: str           # WHY it matters
    how: str           # HOW it works
    so_what: str       # SO WHAT — consequences / implications
    confidence: float  # 0.0 – 1.0
    sources: list[str] = field(default_factory=list)
    created_at: float  = field(default_factory=time.time)
    updated_at: float  = field(default_factory=time.time)
    access_count: int  = 0
    embedding: Optional[list[float]] = None  # stored separately in vector table

    @staticmethod
    def make_id(name: str, domain: str) -> str:
        return hashlib.sha256(f"{domain}::{name}".lower().encode()).hexdigest()[:16]


@dataclass
class Relation:
    from_id: str
    to_id: str
    relation_type: str   # CAUSES, ENABLES, CONTRADICTS, PART_OF, EXAMPLE_OF, REQUIRES
    weight: float = 1.0
    evidence: str = ""


@dataclass
class RetrievedConcept:
    concept: Concept
    score: float         # relevance score
    path: list[str]      # graph traversal path if graph-retrieved


# ── Schema ──────────────────────────────────────────────────────────────────

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS concepts (
    id           TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    domain       TEXT NOT NULL,
    what         TEXT NOT NULL DEFAULT '',
    why          TEXT NOT NULL DEFAULT '',
    how          TEXT NOT NULL DEFAULT '',
    so_what      TEXT NOT NULL DEFAULT '',
    confidence   REAL NOT NULL DEFAULT 0.5,
    sources      TEXT NOT NULL DEFAULT '[]',
    created_at   REAL NOT NULL,
    updated_at   REAL NOT NULL,
    access_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS embeddings (
    concept_id TEXT PRIMARY KEY REFERENCES concepts(id) ON DELETE CASCADE,
    vector     BLOB NOT NULL
);

CREATE TABLE IF NOT EXISTS relations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    from_id       TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    to_id         TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,
    weight        REAL NOT NULL DEFAULT 1.0,
    evidence      TEXT NOT NULL DEFAULT '',
    UNIQUE(from_id, to_id, relation_type)
);

CREATE TABLE IF NOT EXISTS learning_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ts         REAL NOT NULL,
    event_type TEXT NOT NULL,
    payload    TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_concepts_domain   ON concepts(domain);
CREATE INDEX IF NOT EXISTS idx_concepts_name     ON concepts(name);
CREATE INDEX IF NOT EXISTS idx_relations_from    ON relations(from_id);
CREATE INDEX IF NOT EXISTS idx_relations_to      ON relations(to_id);
"""


# ── VelynxMemory ─────────────────────────────────────────────────────────────

class VelynxMemory:
    """
    Single interface to the entire VELYNX knowledge base.
    Thread-safe via WAL mode + per-operation connections.
    """

    def __init__(self, db_path: str = "velynx_core/velynx.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"VelynxMemory ready at {self.db_path}")

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        with self._conn() as conn:
            conn.executescript(SCHEMA)

    # ── Concepts ─────────────────────────────────────────────────────────

    def store_concept(self, concept: Concept) -> bool:
        """Upsert a concept. Returns True if new, False if updated."""
        try:
            with self._conn() as conn:
                existing = conn.execute(
                    "SELECT id, access_count FROM concepts WHERE id=?",
                    (concept.id,)
                ).fetchone()

                concept.updated_at = time.time()

                if existing:
                    conn.execute("""
                        UPDATE concepts SET
                          name=?, domain=?, what=?, why=?, how=?, so_what=?,
                          confidence=?, sources=?, updated_at=?, access_count=?
                        WHERE id=?
                    """, (
                        concept.name, concept.domain,
                        concept.what, concept.why, concept.how, concept.so_what,
                        concept.confidence, json.dumps(concept.sources),
                        concept.updated_at, existing["access_count"],
                        concept.id
                    ))
                    is_new = False
                else:
                    conn.execute("""
                        INSERT INTO concepts
                          (id, name, domain, what, why, how, so_what,
                           confidence, sources, created_at, updated_at, access_count)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        concept.id, concept.name, concept.domain,
                        concept.what, concept.why, concept.how, concept.so_what,
                        concept.confidence, json.dumps(concept.sources),
                        concept.created_at, concept.updated_at, 0
                    ))
                    is_new = True

                # Store embedding if provided
                if concept.embedding:
                    vec_bytes = np.array(concept.embedding, dtype=np.float32).tobytes()
                    conn.execute("""
                        INSERT OR REPLACE INTO embeddings (concept_id, vector)
                        VALUES (?, ?)
                    """, (concept.id, vec_bytes))

                return is_new
        except Exception as e:
            logger.error(f"store_concept failed: {e}")
            return False

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM concepts WHERE id=?", (concept_id,)
            ).fetchone()
            if not row:
                return None
            conn.execute(
                "UPDATE concepts SET access_count=access_count+1 WHERE id=?",
                (concept_id,)
            )
            return self._row_to_concept(row)

    def find_concept(self, name: str, domain: str = "") -> Optional[Concept]:
        cid = Concept.make_id(name, domain)
        c = self.get_concept(cid)
        if c:
            return c
        # fuzzy fallback: search by name
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM concepts WHERE LOWER(name) LIKE ? LIMIT 1",
                (f"%{name.lower()}%",)
            ).fetchone()
            return self._row_to_concept(row) if row else None

    def search_concepts(self, query: str, top_k: int = 10) -> list[Concept]:
        """Text search across name + what + why + how."""
        q = f"%{query.lower()}%"
        with self._conn() as conn:
            rows = conn.execute("""
                SELECT * FROM concepts
                WHERE LOWER(name) LIKE ?
                   OR LOWER(what) LIKE ?
                   OR LOWER(why)  LIKE ?
                   OR LOWER(how)  LIKE ?
                ORDER BY confidence DESC, access_count DESC
                LIMIT ?
            """, (q, q, q, q, top_k)).fetchall()
            return [self._row_to_concept(r) for r in rows]

    def vector_search(self, query_embedding: list[float], top_k: int = 10) -> list[RetrievedConcept]:
        """Cosine similarity search over stored embeddings."""
        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []

        with self._conn() as conn:
            rows = conn.execute(
                "SELECT concept_id, vector FROM embeddings"
            ).fetchall()

        results = []
        for row in rows:
            vec = np.frombuffer(row["vector"], dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm == 0:
                continue
            score = float(np.dot(q_vec, vec) / (q_norm * norm))
            results.append((row["concept_id"], score))

        results.sort(key=lambda x: x[1], reverse=True)
        retrieved = []
        for cid, score in results[:top_k]:
            c = self.get_concept(cid)
            if c:
                retrieved.append(RetrievedConcept(concept=c, score=score, path=[]))
        return retrieved

    # ── Relations ────────────────────────────────────────────────────────

    def add_relation(self, rel: Relation) -> bool:
        try:
            with self._conn() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO relations
                      (from_id, to_id, relation_type, weight, evidence)
                    VALUES (?,?,?,?,?)
                """, (rel.from_id, rel.to_id, rel.relation_type,
                      rel.weight, rel.evidence))
            return True
        except Exception as e:
            logger.error(f"add_relation failed: {e}")
            return False

    def get_neighbors(self, concept_id: str, relation_types: list[str] = None,
                      max_hops: int = 2) -> list[RetrievedConcept]:
        """BFS graph traversal from a concept node."""
        visited = set()
        frontier = [(concept_id, [], 1.0)]
        results = []

        with self._conn() as conn:
            for _ in range(max_hops):
                next_frontier = []
                for node_id, path, weight in frontier:
                    if node_id in visited:
                        continue
                    visited.add(node_id)

                    query = "SELECT * FROM relations WHERE from_id=?"
                    params = [node_id]
                    if relation_types:
                        placeholders = ",".join("?" * len(relation_types))
                        query += f" AND relation_type IN ({placeholders})"
                        params.extend(relation_types)

                    for rel_row in conn.execute(query, params).fetchall():
                        neighbor_id = rel_row["to_id"]
                        if neighbor_id not in visited:
                            c = self.get_concept(neighbor_id)
                            if c:
                                new_path = path + [rel_row["relation_type"]]
                                score = weight * rel_row["weight"] * c.confidence
                                results.append(RetrievedConcept(
                                    concept=c, score=score, path=new_path
                                ))
                                next_frontier.append((neighbor_id, new_path, score))
                frontier = next_frontier

        results.sort(key=lambda x: x.score, reverse=True)
        return results

    # ── Stats & Introspection ────────────────────────────────────────────

    def stats(self) -> dict:
        with self._conn() as conn:
            n_concepts  = conn.execute("SELECT COUNT(*) FROM concepts").fetchone()[0]
            n_relations = conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
            n_embedded  = conn.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0]
            avg_conf    = conn.execute("SELECT AVG(confidence) FROM concepts").fetchone()[0] or 0
            domains     = conn.execute(
                "SELECT domain, COUNT(*) as n FROM concepts GROUP BY domain ORDER BY n DESC"
            ).fetchall()
        return {
            "concepts":  n_concepts,
            "relations": n_relations,
            "embedded":  n_embedded,
            "avg_confidence": round(avg_conf, 3),
            "domains": {r["domain"]: r["n"] for r in domains}
        }

    def log_event(self, event_type: str, payload: dict):
        try:
            with self._conn() as conn:
                conn.execute(
                    "INSERT INTO learning_log (ts, event_type, payload) VALUES (?,?,?)",
                    (time.time(), event_type, json.dumps(payload))
                )
        except Exception:
            pass  # logging must never crash the caller

    # ── Internal ─────────────────────────────────────────────────────────

    def _row_to_concept(self, row) -> Concept:
        return Concept(
            id=row["id"],
            name=row["name"],
            domain=row["domain"],
            what=row["what"],
            why=row["why"],
            how=row["how"],
            so_what=row["so_what"],
            confidence=row["confidence"],
            sources=json.loads(row["sources"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            access_count=row["access_count"]
        )
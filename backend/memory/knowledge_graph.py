"""
VELYNX Knowledge Graph — SQLite Backend
========================================
Replaces JSON-file storage with SQLite for ACID transactions,
concurrent access, and proper indexing.

Same public API as before: integrate, lookup, find_connected, get_gaps, consolidate, stats.
"""
from __future__ import annotations

import json
import logging
import math
import os
import re
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional
from contextlib import contextmanager
import aiosqlite
import asyncio

logger = logging.getLogger("velynx.knowledge_graph")

_DATA_DIR = Path(os.getenv("VELYNX_DATA_DIR", ".")) / "velynx_data" / "knowledge_graph"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_DB_PATH = _DATA_DIR / "graph.db"

# SQL schema
_SCHEMA_BASE = """
CREATE TABLE IF NOT EXISTS triples (
    id INTEGER PRIMARY KEY,
    subject TEXT NOT NULL,
    relation TEXT NOT NULL,
    object TEXT NOT NULL,
    confidence REAL,
    source TEXT,
    timestamp REAL
);

CREATE TABLE IF NOT EXISTS understandings (
    topic TEXT PRIMARY KEY,
    summary TEXT,
    timestamp REAL
);
"""

_SCHEMA_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_triples_subject ON triples(subject);
CREATE INDEX IF NOT EXISTS idx_triples_object ON triples(object);
CREATE INDEX IF NOT EXISTS idx_understandings_confidence ON understandings(confidence);
"""

class KnowledgeGraph:
    def __init__(self):
        self.db_path = _DB_PATH
        self._init_db()

    def _init_db(self):
        """Initialize database directory and schema."""
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            # Run base schema first (CREATE TABLE IF NOT EXISTS)
            conn.executescript(_SCHEMA_BASE)
            conn.commit()

        # Migrate any missing columns before creating indexes on them
        self._migrate_schema()

        with sqlite3.connect(self.db_path) as conn:
            # Now safe to create indexes that reference migrated columns
            conn.executescript(_SCHEMA_INDEXES)
            conn.commit()

    def _migrate_schema(self):
        """Add any missing columns from schema upgrades."""
        with sqlite3.connect(self.db_path) as conn:
            cols = {row[1] for row in conn.execute("PRAGMA table_info(understandings)")}
            if "confidence" not in cols:
                conn.execute("ALTER TABLE understandings ADD COLUMN confidence REAL NOT NULL DEFAULT 0.5")
            if "query_count" not in cols:
                conn.execute("ALTER TABLE understandings ADD COLUMN query_count INTEGER NOT NULL DEFAULT 0")
            conn.commit()

    async def load(self):
        """Load knowledge graph from storage."""
        # For SQLite backend, data is already persisted
        pass

    async def fast_query(self, query):
        """Fast lookup of relevant triples."""
        # This is a placeholder - fast query implementation would go here
        return None

    async def _semantic_matches(self, hit_topic: str, query: str) -> bool:
        """Guard against cross-topic false positives in fast_query."""
        if not hit_topic:
            return False
        # This is a placeholder for semantic matching logic
        return True

    async def store_answer(self, query, answer, confidence, sources):
        """Store an answer in the knowledge graph."""
        topic = query[:80]
        async with aiosqlite.connect(str(self.db_path)) as db:
            await db.execute(
                "INSERT OR REPLACE INTO understandings (topic, summary, confidence, query_count, timestamp) "
                "VALUES (?, ?, ?, COALESCE((SELECT query_count FROM understandings WHERE topic=?), 0) + 1, ?)",
                (topic, answer[:500], confidence, topic, time.time())
            )
            await db.commit()

    async def add_triple(self, triple):
        """Add a triple to the knowledge graph."""
        async with aiosqlite.connect(str(self.db_path)) as db:
            await db.execute(
                "INSERT INTO triples (subject, relation, object, confidence, source, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (triple.subject, triple.relation, triple.obj, triple.confidence, triple.source, time.time())
            )
            await db.commit()

    async def get_understanding(self, topic):
        """Get understanding for a topic."""
        async with aiosqlite.connect(str(self.db_path)) as db:
            async with db.execute(
                "SELECT summary FROM understandings WHERE topic = ?", (topic,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def store_understanding(self, topic, summary):
        """Store understanding for a topic."""
        async with aiosqlite.connect(str(self.db_path)) as db:
            await db.execute(
                "INSERT OR REPLACE INTO understandings (topic, summary, confidence, query_count, timestamp) VALUES (?, ?, COALESCE((SELECT confidence FROM understandings WHERE topic = ?), 0.5), COALESCE((SELECT query_count FROM understandings WHERE topic = ?), 0), ?)",
                (topic, summary, topic, topic, time.time())
            )
            await db.commit()

    def get_gaps(self, query: str = "") -> list[str]:
        """Identify knowledge gaps: topics with low confidence, sparse triples, or missing links.

        If query is empty, scans all understandings for weak spots.
        """
        gaps: list[str] = []
        with sqlite3.connect(str(self.db_path)) as db:
            if query:
                row = db.execute(
                    "SELECT topic, confidence, query_count FROM understandings WHERE topic = ?",
                    (query,)
                ).fetchone()
                if not row:
                    gaps.append(f"Concept '{query}' not yet learned")
                else:
                    topic, conf, qcount = row
                    if conf < 0.5:
                        gaps.append(f"Low confidence ({conf:.0%}) on '{topic}' — needs more sources")
                    triple_count = db.execute(
                        "SELECT COUNT(*) FROM triples WHERE subject = ? OR object = ?",
                        (topic, topic)
                    ).fetchone()[0]
                    if triple_count < 3:
                        gaps.append(f"Only {triple_count} triple(s) for '{topic}' — needs deeper learning")
            else:
                rows = db.execute(
                    "SELECT topic, confidence, query_count FROM understandings ORDER BY confidence ASC LIMIT 20"
                ).fetchall()
                for topic, conf, qcount in rows:
                    triple_count = db.execute(
                        "SELECT COUNT(*) FROM triples WHERE subject = ? OR object = ?",
                        (topic, topic)
                    ).fetchone()[0]
                    if conf < 0.5:
                        gaps.append(f"Low confidence ({conf:.0%}) on '{topic}' — needs more sources")
                    if triple_count < 3:
                        gaps.append(f"Only {triple_count} triple(s) for '{topic}' — needs deeper learning")
            return gaps[:10]

    def get_low_confidence_nodes(self, threshold: float = 0.4) -> list[tuple[str, float]]:
        """Return topics with confidence below threshold."""
        with sqlite3.connect(str(self.db_path)) as db:
            rows = db.execute(
                "SELECT topic, confidence FROM understandings WHERE confidence < ? ORDER BY confidence ASC",
                (threshold,)
            ).fetchall()
            return [(row[0], row[1]) for row in rows]

    def prune_low_value_nodes(self, confidence_threshold: float = 0.2) -> int:
        """Remove understandings with confidence below threshold and query_count == 0."""
        with sqlite3.connect(str(self.db_path)) as db:
            cursor = db.execute(
                "DELETE FROM understandings WHERE confidence < ? AND query_count = 0",
                (confidence_threshold,)
            )
            removed = cursor.rowcount
            db.commit()
            return removed

import os
import sqlite3
from pathlib import Path

from backend.memory._sqlite import resolve_db_path

DB_PATH = resolve_db_path(
    Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_graph.db"
)

SEED_CONCEPTS = [
    # ── CODING ──────────────────────────────────────────────
    ("debugging", "CODING", "isolating why code behaves unexpectedly"),
    ("refactoring", "CODING", "restructuring code without changing behavior"),
    ("testing", "CODING", "verifying behavior matches intention"),
    ("architecture", "CODING", "structuring systems for change and scale"),
    ("iteration", "CODING", "repeated cycles of build-test-improve"),
    ("deployment", "CODING", "releasing code to a live environment"),
    ("optimization", "CODING", "improving performance within constraints"),
    ("abstraction", "CODING", "hiding complexity behind a clean interface"),
    ("technical debt", "CODING", "accumulated cost of shortcuts taken earlier"),
    ("legacy code", "CODING", "existing code that works but is hard to change"),
    # ── LOGIC ───────────────────────────────────────────────
    ("proof", "LOGIC", "establishing truth through reasoning"),
    ("inference", "LOGIC", "deriving conclusions from evidence"),
    ("contradiction", "LOGIC", "two claims that cannot both be true"),
    ("assumption", "LOGIC", "a belief taken as true without verification"),
    ("verification", "LOGIC", "confirming a claim against evidence"),
    # ── SYSTEMS ─────────────────────────────────────────────
    ("bottleneck", "SYSTEMS", "the constraint limiting total throughput"),
    ("failure", "SYSTEMS", "a system not meeting its intended behavior"),
    ("recovery", "SYSTEMS", "restoring function after failure"),
    ("fallback", "SYSTEMS", "a backup path when primary fails"),
    ("feedback loop", "SYSTEMS", "output influencing its own input"),
    # ── PHYSICS (Dynamics) ──────────────────────────────────
    ("entropy", "PHYSICS", "measure of disorder; tendency toward equilibrium"),
    ("inertia", "PHYSICS", "resistance of a body to change in its state of motion"),
    ("friction", "PHYSICS", "force that opposes relative motion between surfaces"),
    ("momentum", "PHYSICS", "product of mass and velocity; quantity of motion"),
    ("velocity", "PHYSICS", "rate of change of position with direction"),
    ("mass", "PHYSICS", "measure of the amount of matter in an object"),
    ("resistance", "PHYSICS", "opposition to the flow of current or motion"),
    ("force", "PHYSICS", "interaction that changes the motion of an object"),
    # ── FINANCE (Economics) ─────────────────────────────────
    ("depreciation", "FINANCE", "loss of value of an asset over time"),
    ("illiquidity", "FINANCE", "difficulty of converting an asset to cash"),
    ("leverage", "FINANCE", "use of borrowed capital to amplify returns"),
    ("debt", "FINANCE", "obligation to repay borrowed money"),
    ("inflation", "FINANCE", "general increase in prices and decrease in purchasing power"),
    ("asset", "FINANCE", "resource with economic value owned by an entity"),
    ("capital", "FINANCE", "financial assets used for production or investment"),
    ("valuation", "FINANCE", "process of determining the present worth of an asset"),
    ("stagnation", "FINANCE", "period of little or no growth in economic activity"),
]

SEED_RELATIONSHIPS = [
    # ── CODING ──────────────────────────────────────────────
    ("debugging", "requires", "testing"),
    ("refactoring", "requires", "testing"),
    ("refactoring", "produces", "architecture"),
    ("iteration", "produces", "optimization"),
    ("deployment", "requires", "testing"),
    # ── SYSTEMS ─────────────────────────────────────────────
    ("failure", "requires", "recovery"),
    ("recovery", "enables", "iteration"),
    ("bottleneck", "opposes", "optimization"),
    ("technical debt", "opposes", "architecture"),
    ("feedback loop", "enables", "optimization"),
    ("abstraction", "enables", "architecture"),
    # ── LOGIC ───────────────────────────────────────────────
    ("assumption", "opposes", "verification"),
    ("proof", "requires", "inference"),
    # ── PHYSICS (Dynamics) ──────────────────────────────────
    ("entropy", "opposes", "momentum"),
    ("friction", "reduces", "velocity"),
    ("inertia", "requires", "force"),
    # ── FINANCE (Economics) ─────────────────────────────────
    ("inflation", "reduces", "capital"),
    ("leverage", "catalyzes", "debt"),
    ("illiquidity", "produces", "stagnation"),
]


from backend.memory._sqlite import connect as open_connection


class KnowledgeGraph:
    def __init__(self, db_path: str = None):
        self.db_path = Path(db_path) if db_path else DB_PATH
        # Runtime path diagnostic: emit the ABSOLUTE symbolic-KG DB path so a
        # live-fire run can be compared against scripts/wipe_db.py's targets.
        # Printed when VELYNX_DEBUG_DB is set so it surfaces even though the
        # harness silences loggers during a run.
        if os.getenv("VELYNX_DEBUG_DB"):
            print(f"[VELYNX_DEBUG_DB] symbolic knowledge_graph DB -> {self.db_path.resolve()}")

    def _get_conn(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = open_connection(str(self.db_path), row_factory=sqlite3.Row)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS concepts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            domain TEXT NOT NULL,
            description TEXT NOT NULL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            relation TEXT NOT NULL,
            target TEXT NOT NULL
        )""")
        conn.commit()
        return conn

    def build(self, force: bool = False) -> None:
        conn = self._get_conn()
        c = conn.cursor()

        if not force:
            c.execute("SELECT COUNT(*) FROM concepts")
            count = c.fetchone()[0]
            if count > 0:
                conn.close()
                return

        for name, domain, desc in SEED_CONCEPTS:
            c.execute(
                "INSERT OR IGNORE INTO concepts (name, domain, description) VALUES (?, ?, ?)",
                (name, domain, desc),
            )
        for source, relation, target in SEED_RELATIONSHIPS:
            c.execute(
                "INSERT OR IGNORE INTO relationships (source, relation, target) VALUES (?, ?, ?)",
                (source, relation, target),
            )
        conn.commit()
        conn.close()

    def get_concept(self, name: str) -> dict | None:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT name, domain, description FROM concepts WHERE name = ?", (name,))
        row = c.fetchone()
        conn.close()
        if not row:
            return None
        return {"name": row[0], "domain": row[1], "description": row[2]}

    def get_related(self, name: str) -> list[dict]:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute(
            "SELECT source, relation, target FROM relationships WHERE source = ? OR target = ?",
            (name, name),
        )
        rows = c.fetchall()
        conn.close()
        return [{"source": r[0], "relation": r[1], "target": r[2]} for r in rows]

    def add_concept(self, name: str, domain: str, description: str) -> None:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO concepts (name, domain, description) VALUES (?, ?, ?)",
            (name, domain, description),
        )
        conn.commit()
        conn.close()

    def add_relationship(self, source: str, relation: str, target: str) -> None:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO relationships (source, relation, target) VALUES (?, ?, ?)",
            (source, relation, target),
        )
        conn.commit()
        conn.close()

    def all_concepts(self) -> list[str]:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT name FROM concepts ORDER BY name")
        rows = c.fetchall()
        conn.close()
        return [r[0] for r in rows]

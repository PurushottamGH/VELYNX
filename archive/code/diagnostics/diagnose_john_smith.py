"""
Diagnostic: "Vanishing John Smith" bug.

Queries the live knowledge-graph SQLite DB (or the isolated test DB when
VELYNX_TEST_MODE=1) and prints every triple whose subject/object mentions
Blender, Ton Roosendaal, or John Smith. We want to see the exact
subject / relation / object / source / confidence for each surviving row.
"""
import os
import sqlite3
from pathlib import Path

DATA_DIR = Path(os.getenv("VELYNX_DATA_DIR", ".")) / "velynx_data" / "knowledge_graph"
LIVE_DB = DATA_DIR / "graph.db"
ISOLATED = (
    Path("backend") / "tests" / "data" / "_isolated" / "knowledge_graph__graph.db"
)


def dump(db_path: Path):
    if not db_path.exists():
        print(f"[skip] {db_path} does not exist")
        return
    print(f"\n=== {db_path} ===")
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    print("\n-- ALL rows mentioning blender/roosendaal/john/smith --")
    rows = cur.execute(
        """
        SELECT id, subject, relation, object, confidence, source, timestamp
        FROM triples
        WHERE lower(subject) LIKE '%blender%' OR lower(object) LIKE '%blender%'
           OR lower(subject) LIKE '%roosendaal%' OR lower(object) LIKE '%roosendaal%'
           OR lower(subject) LIKE '%john%' OR lower(object) LIKE '%john%'
           OR lower(subject) LIKE '%smith%' OR lower(object) LIKE '%smith%'
        ORDER BY id
        """
    ).fetchall()
    if not rows:
        print("  (none)")
    for r in rows:
        print(
            f"  id={r['id']:>4} | subj={r['subject']!r} | rel={r['relation']!r} | "
            f"obj={r['object']!r} | conf={r['confidence']} | src={r['source']!r}"
        )

    print("\n-- specifically John Smith --")
    js = cur.execute(
        "SELECT * FROM triples WHERE lower(subject) LIKE '%smith%' "
        "OR lower(object) LIKE '%smith%'"
    ).fetchall()
    print(f"  John Smith rows found: {len(js)}")

    print("\n-- all 'create'-family predicates --")
    cr = cur.execute(
        "SELECT DISTINCT relation FROM triples WHERE relation LIKE '%creat%'"
    ).fetchall()
    print("  relations:", [r["relation"] for r in cr])

    con.close()


ACTIVE_DB = Path("data") / "knowledge_graph.db"


def dump_active(db_path: Path):
    """Inspect the active-brain DB the ReasoningEngine actually traverses."""
    if not db_path.exists():
        print(f"[skip] {db_path} does not exist")
        return
    print(f"\n=== ACTIVE BRAIN {db_path} ===")
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    print("tables:", tables)

    if "relationships" in tables:
        print("\n-- relationships mentioning blender/john/smith/roosendaal --")
        rows = cur.execute(
            """
            SELECT * FROM relationships
            WHERE lower(source) LIKE '%blender%' OR lower(target) LIKE '%blender%'
               OR lower(source) LIKE '%smith%'   OR lower(target) LIKE '%smith%'
               OR lower(source) LIKE '%roosendaal%' OR lower(target) LIKE '%roosendaal%'
            """
        ).fetchall()
        if not rows:
            print("  (none)")
        for r in rows:
            print("  ", dict(r))

    if "concept_provenance" in tables:
        print("\n-- concept_provenance mentioning blender/john/smith/roosendaal --")
        rows = cur.execute(
            """
            SELECT subject, relation, object, status, confidence FROM concept_provenance
            WHERE lower(subject) LIKE '%blender%' OR lower(object) LIKE '%blender%'
               OR lower(subject) LIKE '%smith%'   OR lower(object) LIKE '%smith%'
               OR lower(subject) LIKE '%roosendaal%' OR lower(object) LIKE '%roosendaal%'
            """
        ).fetchall()
        if not rows:
            print("  (none)")
        for r in rows:
            print("  ", dict(r))
    con.close()


if __name__ == "__main__":
    print("VELYNX_TEST_MODE =", os.getenv("VELYNX_TEST_MODE"))
    dump(LIVE_DB)
    dump(ISOLATED)
    dump_active(ACTIVE_DB)

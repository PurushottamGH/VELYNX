"""
VELYNX Relational Soul Builder — builds concept edges + tensions using local embeddings only.
Layer 2: No external APIs. Purely self-contained.

Depends on: cognition.embed_index (Layer 1)
"""

import json
import sqlite3
import os
import hashlib
from pathlib import Path
from datetime import datetime

SOUL_PATH = Path(__file__).parent / "concepts.json"
SOUL_DB = Path(__file__).parent.parent.parent / "backend" / "velynx_data" / "soul_graph" / "graph.db"
GRAPH_LOG = Path(__file__).parent.parent.parent / "backend" / "velynx_data" / "soul_graph_log.json"

from velynx.graph.living_edges import add_living_edge, reinforce_edge, challenge_edge

# Phase 38C: Brain Stem traversal
BRAIN_STEM_DB = ".velynx_data/brain_stem.db"

def get_db_connection() -> sqlite3.Connection:
    base_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.dirname(os.path.dirname(base_dir))
    target_db = os.path.join(project_root, BRAIN_STEM_DB)
    conn = sqlite3.connect(target_db)
    conn.row_factory = sqlite3.Row
    return conn


def load_soul() -> dict:
    if not SOUL_PATH.exists():
        return {}
    raw = SOUL_PATH.read_text(encoding="utf-8")
    return json.loads(raw)


def save_soul(soul: dict):
    SOUL_PATH.parent.mkdir(parents=True, exist_ok=True)
    SOUL_PATH.write_text(json.dumps(soul, indent=2, ensure_ascii=False), encoding="utf-8")


def _get_conn():
    SOUL_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(SOUL_DB))
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS soul_edges (
        id TEXT PRIMARY KEY,
        from_concept TEXT, to_concept TEXT,
        edge_type TEXT, weight REAL,
        reason TEXT, source TEXT, created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS soul_tensions (
        id TEXT PRIMARY KEY,
        concept_a TEXT, concept_b TEXT,
        name TEXT, description TEXT,
        severity REAL, created_at TEXT
    )""")
    conn.commit()
    return conn


def build_soul_graph(force: bool = False):
    """
    Build relational edges between ALL concept pairs using local embeddings.
    Skips pairs that already have edges (unless force=True).
    """
    try:
        from cognition.embed_index import concept_similarity, classify_edge_type, build_index
    except ModuleNotFoundError:
        from backend.cognition.embed_index import concept_similarity, classify_edge_type, build_index

    soul = load_soul()
    names = list(soul.keys())
    total = len(names) * (len(names) - 1) // 2
    print(f"\nBuilding soul graph: {len(names)} concepts, {total} pairs\n")

    build_index()
    conn = _get_conn()
    built = 0

    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if not force and _edge_exists(conn, a, b):
                continue

            score = concept_similarity(a, b)
            if score < 0.20:
                continue

            etype = classify_edge_type(a, b, score)
            rev_typ = _reverse_type(etype)
            reason = _generate_reason(a, b, etype, score, soul)
            rev_rsn = _generate_reason(b, a, rev_typ, score, soul)

            _write_edge(conn, soul, a, b, etype, score, reason)
            _write_edge(conn, soul, b, a, rev_typ, score, rev_rsn)

            tension = _detect_tension(a, b, etype, soul)
            if tension:
                _write_tension(conn, soul, a, b, tension)

            built += 1
            if built % 10 == 0:
                print(f"  {built}/{total} edges built...")

    conn.commit()
    conn.close()
    _log({"type": "full_build", "pairs_built": built, "concepts": len(names)})
    print(f"\nSoul graph complete: {built * 2} edges, {len(names)} concepts")


def build_pair(a: str, b: str):
    """Build edges between exactly two concepts. Called after teaching.

    Checks each direction independently — existing edges are preserved,
    missing directions are filled in, so partial edges don't cause duplication.
    """
    try:
        from cognition.embed_index import concept_similarity, classify_edge_type, build_index
    except ModuleNotFoundError:
        from backend.cognition.embed_index import concept_similarity, classify_edge_type, build_index

    soul = load_soul()
    build_index()
    conn = _get_conn()

    has_forward = _edge_exists(conn, a, b)
    has_reverse = _edge_exists(conn, b, a)

    if has_forward and has_reverse:
        conn.close()
        print(f"  [{a}] --[{b}] (edges already exist, skipped)")
        return

    score = concept_similarity(a, b)
    etype = classify_edge_type(a, b, score)
    rev_typ = _reverse_type(etype)
    reason = _generate_reason(a, b, etype, score, soul)
    rev_rsn = _generate_reason(b, a, rev_typ, score, soul)

    if not has_forward:
        _write_edge(conn, soul, a, b, etype, score, reason)
        print(f"  [{a}] --{etype}--> [{b}]")
    if not has_reverse:
        _write_edge(conn, soul, b, a, rev_typ, score, rev_rsn)
        print(f"  [{b}] --{rev_typ}--> [{a}]")

    tension = _detect_tension(a, b, etype, soul)
    if tension:
        _write_tension(conn, soul, a, b, tension)

    conn.commit()
    conn.close()

    if tension:
        print(f"  Tension: {tension['name']}")


def find_path(start: str, end: str, max_hops: int = 3) -> list[str]:
    """Cognitive BFS through the Brain Stem prioritizing high-weight, high-confidence paths."""
    if start == end:
        return [start]

    queue = [([start], 1.0)]
    visited = set([start])

    while queue:
        queue.sort(key=lambda x: x[1], reverse=True)
        current_path, path_weight = queue.pop(0)
        current_node = current_path[-1]

        if len(current_path) - 1 >= max_hops:
            continue

        edges = get_edges(current_node)
        for edge in edges:
            neighbor = edge['target']
            edge_weight = edge['asymptotic_weight']

            if neighbor == end:
                return current_path + [neighbor]

            if neighbor not in visited:
                visited.add(neighbor)
                new_weight = path_weight * edge_weight
                queue.append((current_path + [neighbor], new_weight))

    return []


def get_edges(concept: str) -> list[dict]:
    """Retrieves all active, non-contested outbound edges for a concept from Brain Stem, sorted by weight."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT target, relation, context, asymptotic_weight, confidence
        FROM living_edges
        WHERE source = ? AND status = 'active' AND confidence != 'CONTESTED'
        ORDER BY asymptotic_weight DESC
    ''', (concept,))
    edges = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return edges


def get_tensions(concept: str) -> list[dict]:
    """Retrieves all contested or inverse relationships from Brain Stem for truth-tension generation."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT source, target, relation, context, confidence
        FROM living_edges
        WHERE (source = ? OR target = ?) AND status = 'contested'
    ''', (concept, concept))
    tensions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tensions


def synthesize(concepts: list[str]) -> str:
    """
    Given multiple activated concepts, synthesize a relational statement
    from the Brain Stem graph. No LLM call.
    """
    if len(concepts) < 2:
        return ""

    parts = []
    for i in range(len(concepts) - 1):
        a, b = concepts[i], concepts[i + 1]
        path = find_path(a, b)
        if path and len(path) >= 2:
            # path is list[str] of node names
            chain = []
            for j in range(len(path) - 1):
                src, dst = path[j], path[j + 1]
                edges = get_edges(src)
                match = next((e for e in edges if e['target'] == dst), None)
                if match:
                    chain.append(f"{src.title()} {match['relation']} {dst}")
            if chain:
                parts.append(" then ".join(chain))
        else:
            edges = get_edges(a)
            match = next((e for e in edges if e['target'] == b), None)
            if match:
                parts.append(f"{a.title()} {match['relation']} {b}")

    tensions_found = []
    for a in concepts:
        for b in concepts:
            if a != b:
                t = get_tensions(a)
                for tension in t:
                    if tension['source'] == b or tension['target'] == b:
                        tensions_found.append(f"{tension.get('context', '')} tension: {a.title()} {tension['relation']} {b}")

    result = ". ".join(parts)
    if tensions_found:
        result += f". Tension present: {tensions_found[0]}"
    return result or f"These concepts are deeply connected: {', '.join(concepts)}"


def _edge_exists(conn, a: str, b: str) -> bool:
    """Return True if any directed edge exists from a to b."""
    c = conn.cursor()
    c.execute("SELECT 1 FROM soul_edges WHERE from_concept=? AND to_concept=?", (a, b))
    return c.fetchone() is not None


def _write_edge(conn, soul: dict, frm: str, to: str, etype: str, weight: float, reason: str):
    eid = hashlib.md5(f"{frm}{to}{etype}".encode()).hexdigest()[:12]
    c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO soul_edges
        (id, from_concept, to_concept, edge_type, weight, reason, source, created_at)
        VALUES (?,?,?,?,?,?,?,?)""",
              (eid, frm, to, etype, weight, reason, "local_embed", datetime.now().isoformat())
              )
    soul.setdefault(frm, {})
    if isinstance(soul[frm], str):
        soul[frm] = {"definition": soul[frm], "edges": []}
    soul[frm].setdefault("edges", [])
    # Deduplicate in-memory: replace existing edge to the same target+type, else append
    existing = [e for e in soul[frm]["edges"] if not (e["to"] == to and e["type"] == etype)]
    existing.append({"to": to, "type": etype, "weight": weight, "reason": reason})
    soul[frm]["edges"] = existing


def _write_tension(conn, soul: dict, a: str, b: str, tension: dict):
    tid = hashlib.md5(f"{a}{b}{tension['name']}".encode()).hexdigest()[:12]
    c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO soul_tensions
        (id, concept_a, concept_b, name, description, severity, created_at)
        VALUES (?,?,?,?,?,?,?)""",
              (tid, a, b, tension["name"], tension["description"],
               tension.get("severity", 0.5), datetime.now().isoformat())
              )
    soul.setdefault(a, {})
    soul[a].setdefault("tensions", [])
    # Deduplicate in-memory: replace existing tension with same concept+name, else append
    existing = [t for t in soul[a]["tensions"] if not (t.get("with") == b and t.get("name") == tension["name"])]
    existing.append({"with": b, **tension})
    soul[a]["tensions"] = existing


def _detect_tension(a: str, b: str, etype: str, soul: dict) -> dict | None:
    TENSION_PAIRS = {
        ("grief", "hope"): ("Temporal pull", "Grief looks back; hope looks forward", 0.7),
        ("betrayal", "love"): ("Trust collapse", "Love requires trust; betrayal destroys it", 0.9),
        ("courage", "fear"): ("Coexistence paradox", "Courage is not the absence of fear", 0.6),
        ("pride", "regret"): ("Self-evaluation split", "Pride affirms; regret questions the same act", 0.7),
        ("anger", "forgiveness"): ("Release conflict", "Forgiveness cannot begin while anger fully possesses", 0.8),
        ("depression", "hope"): ("Emotional contradiction", "Hope reaches forward; depression pulls under — both present, both true", 0.85),
    }
    key = tuple(sorted([a.lower(), b.lower()]))
    if key in TENSION_PAIRS:
        name, desc, severity = TENSION_PAIRS[key]
        return {"name": name, "description": desc, "severity": severity}
    if etype in ("contrasts", "corrupts"):
        return {"name": f"{a.title()} vs {b.title()}",
                "description": f"{a.title()} and {b.title()} pull in different directions",
                "severity": 0.5}
    return None


def _reverse_type(etype: str) -> str:
    REVERSAL = {
        "catalyzes": "sustains", "sustains": "catalyzes",
        "corrupts": "resists", "resists": "corrupts",
        "amplifies": "grounds", "grounds": "amplifies",
        "deepens": "deepens", "compounds": "compounds",
        "informs": "informs", "contrasts": "contrasts",
        "distant": "distant",
    }
    return REVERSAL.get(etype, "relates_to")


def _generate_reason(a: str, b: str, etype: str, score: float, soul: dict) -> str:
    def_a = _get_def(soul, a)
    def_b = _get_def(soul, b)
    short_a = def_a[:60].rstrip() if def_a else a
    short_b = def_b[:60].rstrip() if def_b else b
    return f"{a.title()} ({short_a}...) {etype} {b} (score={score:.2f})"


def _get_def(soul: dict, concept: str) -> str:
    entry = soul.get(concept, {})
    if isinstance(entry, dict):
        return entry.get("definition", entry.get("core", ""))
    return str(entry)


def resonate(query: str) -> dict[str, float]:
    """
    Phase 39: Resonance Mapping.
    Multi-hop semantic wave propagation through the Bayesian living graph.
    """
    import numpy as np
    from collections import defaultdict

    try:
        from cognition.embed_index import _MODEL_INSTANCE, _load_index, semantic_lookup
    except ModuleNotFoundError:
        from backend.cognition.embed_index import _MODEL_INSTANCE, _load_index, semantic_lookup

    _matrix, _keys = _load_index()
    if _matrix is None:
        return {}

    conn = get_db_connection()
    cursor = conn.cursor()

    vec = _MODEL_INSTANCE.encode([query], normalize_embeddings=True)[0]
    direct_scores = _matrix @ vec

    resonance_field = defaultdict(float)
    for i, concept in enumerate(_keys):
        score = float(direct_scores[i])
        if score > 0:
            resonance_field[concept] = score

    # Concept Gravity: structural density per concept (exclude contested)
    cursor.execute('''
        SELECT concept, COUNT(*) as edge_count
        FROM (
            SELECT source as concept FROM living_edges WHERE status != 'contested'
            UNION ALL
            SELECT target as concept FROM living_edges WHERE status != 'contested'
        ) GROUP BY concept
    ''')
    gravity_counts = {row['concept']: row['edge_count'] for row in cursor.fetchall()}
    max_edges = max(gravity_counts.values()) if gravity_counts else 1
    gravity_map = {c: count / max_edges for c, count in gravity_counts.items()}

    # Load active, non-contested edges
    cursor.execute('''
        SELECT source, target, asymptotic_weight
        FROM living_edges
        WHERE status != 'contested'
    ''')
    edges = defaultdict(list)
    for row in cursor.fetchall():
        edges[row['source']].append({'target': row['target'], 'weight': row['asymptotic_weight']})

    def compound_resonance(concept, new_energy):
        curr = resonance_field[concept]
        resonance_field[concept] = 1.0 - ((1.0 - curr) * (1.0 - new_energy))

    # Hop 1: Direct neighborhood (0.6 decay)
    hop1_activations = []
    for source, initial_energy in list(resonance_field.items()):
        if initial_energy > 0.1:
            for edge in edges.get(source, []):
                target = edge['target']
                energy = initial_energy * edge['weight'] * 0.6
                compound_resonance(target, energy)
                hop1_activations.append((target, energy))

    # Hop 2: Extended spreading (0.3 decay)
    for source, hop1_energy in hop1_activations:
        if hop1_energy > 0.1:
            for edge in edges.get(source, []):
                target = edge['target']
                energy = hop1_energy * edge['weight'] * 0.3
                compound_resonance(target, energy)

    conn.close()

    # Apply gravity modifiers, filter above activation floor
    final_scores = {}
    for concept, res_score in resonance_field.items():
        grav = gravity_map.get(concept, 0.1)
        final_scores[concept] = res_score * grav

    results = {c: round(s, 3) for c, s in final_scores.items() if s > 0.15}

    # Fallback: flat semantic lookup if wave energy dies out
    if not results:
        fallback = semantic_lookup(query, threshold=0.3)
        if fallback:
            return {item['concept']: round(item['score'], 3) for item in fallback}
        return {}

    return dict(sorted(results.items(), key=lambda item: item[1], reverse=True))


def apply_plasticity(resonance_scores: dict[str, float], source_quality: float = 0.5):
    """
    Hebbian Learning: 'Fire together, wire together.'
    Accepts resonance scores dict, filters to concepts above threshold,
    reinforces existing edges and accumulates coactivation counts to create new edges.
    """
    if not resonance_scores or len(resonance_scores) < 2:
        return

    filtered = {c: s for c, s in resonance_scores.items() if s > 0.4}
    concepts = list(filtered.keys())
    if len(concepts) < 2:
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    for i in range(len(concepts)):
        for j in range(i + 1, len(concepts)):
            a, b = concepts[i], concepts[j]

            # Phase 44: Graduate any inferred edge between a and b to active
            cursor.execute(
                "SELECT id FROM living_edges WHERE source=? AND target=? AND status='inferred'",
                (a, b)
            )
            inf_row = cursor.fetchone()
            if inf_row:
                cursor.execute(
                    "UPDATE living_edges SET status = 'active', last_updated = ? WHERE id = ?",
                    (datetime.now().isoformat(), inf_row['id'])
                )
            cursor.execute(
                "SELECT id FROM living_edges WHERE source=? AND target=? AND status='inferred'",
                (b, a)
            )
            inf_row = cursor.fetchone()
            if inf_row:
                cursor.execute(
                    "UPDATE living_edges SET status = 'active', last_updated = ? WHERE id = ?",
                    (datetime.now().isoformat(), inf_row['id'])
                )

            cursor.execute(
                "SELECT id, status FROM living_edges WHERE source=? AND target=? AND relation='co_activated' AND context='hebbian_inference'",
                (a, b)
            )

            row = cursor.fetchone()
            if row:
                if row['status'] == 'inferred':
                    cursor.execute(
                        "UPDATE living_edges SET status = 'active', last_updated = ? WHERE id = ?",
                        (datetime.now().isoformat(), row['id'])
                    )
                conn.close()
                reinforce_edge(a, "co_activated", b, context="hebbian_inference", source_quality=source_quality)
                reinforce_edge(b, "co_activated", a, context="hebbian_inference", source_quality=source_quality)
                conn = get_db_connection()
                cursor = conn.cursor()
            else:
                cursor.execute('''
                    INSERT INTO coactivation_counts (source, target, context, count)
                    VALUES (?, ?, 'hebbian_inference', 1)
                    ON CONFLICT(source, target, context) DO UPDATE SET count = count + 1
                ''', (a, b))

                cursor.execute(
                    "SELECT count FROM coactivation_counts WHERE source=? AND target=? AND context='hebbian_inference'",
                    (a, b)
                )
                row = cursor.fetchone()
                count = row['count'] if row else 0

                if count >= 2:
                    conn.close()
                    add_living_edge(a, "co_activated", b, context="hebbian_inference", initial_quality=source_quality)
                    add_living_edge(b, "co_activated", a, context="hebbian_inference", initial_quality=source_quality)
                    conn = get_db_connection()
                    cursor = conn.cursor()

                    cursor.execute(
                        "DELETE FROM coactivation_counts WHERE source=? AND target=? AND context='hebbian_inference'",
                        (a, b)
                    )

    conn.commit()
    conn.close()


def run_sleep_cycle(decay_rate: float = 0.05, prune_threshold: float = 0.15) -> dict:
    """
    Phase 43A: Synaptic Pruning Engine.
    Decays all asymptotic_weights, prunes weak/old edges, and forgets orphaned concepts.
    All operations run in a single transaction for atomicity.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN TRANSACTION")

        # 1. DECAY: Multiply all asymptotic_weight by (1.0 - decay_rate)
        cursor.execute(
            "UPDATE living_edges SET asymptotic_weight = asymptotic_weight * ?, last_updated = ?",
            (1.0 - decay_rate, datetime.now().isoformat())
        )
        edges_decayed = cursor.rowcount

        # 2. PRUNE: Delete edges below threshold that are older than 24 hours
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
        cursor.execute(
            "DELETE FROM living_edges WHERE asymptotic_weight < ? AND first_seen < ?",
            (prune_threshold, cutoff)
        )
        edges_pruned = cursor.rowcount

        # 3. ISOLATION CHECK: Delete concepts with no remaining edges
        cursor.execute("""
            DELETE FROM concepts WHERE concept_id NOT IN (
                SELECT source FROM living_edges
                UNION
                SELECT target FROM living_edges
            )
        """)
        concepts_forgotten = cursor.rowcount

        cursor.execute("COMMIT")

        # Phase 45: Run gap scanner after synaptic maintenance
        from velynx.graph.curiosity_engine import run_gap_scanner
        new_gaps = run_gap_scanner()

        return {
            "edges_decayed": edges_decayed,
            "edges_pruned": edges_pruned,
            "concepts_forgotten": concepts_forgotten,
            "new_gaps": new_gaps,
        }

    except Exception:
        cursor.execute("ROLLBACK")
        raise
    finally:
        conn.close()


def get_epistemic_state(concepts: list[str]) -> dict[str, str]:
    """Returns the lowest confidence state for the given concepts to ensure Epistemic Honesty."""
    if not concepts:
        return {}

    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in concepts)
    query = f"""
        SELECT source, target, confidence, status
        FROM living_edges
        WHERE source IN ({placeholders}) OR target IN ({placeholders})
    """
    cursor.execute(query, concepts + concepts)
    edges = cursor.fetchall()

    states = {}
    for concept in concepts:
        c_edges = [e for e in edges if e["source"] == concept or e["target"] == concept]
        if not c_edges:
            states[concept] = "UNKNOWN"
        elif any(e["status"] == "inferred" for e in c_edges):
            states[concept] = "INFERRED (UNCERTAIN)"
        elif any(e["confidence"] == "UNCERTAIN" for e in c_edges):
            states[concept] = "UNCERTAIN"
        else:
            states[concept] = "VERIFIED"

    conn.close()
    return states


# --- Phase 48: Metacognitive Penalty Function ---
def apply_metacognitive_penalty(concepts: list[str]):
    """
    Applies a Bayesian penalty (increases Beta) to edges that resulted in
    a rejected or hallucinated response.
    """
    if not concepts or len(concepts) < 2:
        return

    core_concepts = concepts[:4]

    for i, concept_a in enumerate(core_concepts):
        for concept_b in core_concepts[i + 1 :]:
            # Challenge bidirectional connections that led to the failure
            challenge_edge(concept_a, "co_activated", concept_b, context="metacognitive_correction")
            challenge_edge(concept_b, "co_activated", concept_a, context="metacognitive_correction")
            # Also penalize any inferred edges between them
            challenge_edge(concept_a, "inferred_transitive", concept_b, context="metacognitive_correction")
            challenge_edge(concept_b, "inferred_transitive", concept_a, context="metacognitive_correction")


def _log(event: dict):
    log = []
    if GRAPH_LOG.exists():
        try:
            log = json.loads(GRAPH_LOG.read_text())
        except Exception:
            pass
    log.append({**event, "timestamp": datetime.now().isoformat()})
    GRAPH_LOG.parent.mkdir(parents=True, exist_ok=True)
    GRAPH_LOG.write_text(json.dumps(log, indent=2))

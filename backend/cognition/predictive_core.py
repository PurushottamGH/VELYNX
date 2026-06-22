"""
Phase 50 — Predictive Processing Core.
Predictive layer operating on top of epistemic belief (living_edges).
SQLite-backed, local-first, self-contained.
"""

import json
import math
import os
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from backend.memory._sqlite import connect as open_connection
from backend.memory._sqlite import canonical_db_path

# CWD-drift fix: resolve to a single project-root-anchored absolute path so the
# predictive store and brain-stem reads land on the SAME file regardless of the
# process working directory (repo root vs backend/). See _sqlite.canonical_db_path.
DB_NAME = "predictive.db"
DB_PATH = str(canonical_db_path(DB_NAME))

DEFAULT_LEARNING_RATE = 0.1
DEFAULT_BASELINE_RATE = 0.05


def _get_conn() -> sqlite3.Connection:
    os.makedirs(Path(DB_PATH).parent, exist_ok=True)
    conn = open_connection(DB_PATH, row_factory=sqlite3.Row)
    return conn


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_schema():
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS concept_states (
            concept TEXT PRIMARY KEY,
            activation REAL NOT NULL DEFAULT 0.5,
            baseline REAL NOT NULL DEFAULT 0.5,
            state_confidence REAL NOT NULL DEFAULT 0.5,
            source TEXT DEFAULT 'unknown',
            evidence_count INTEGER DEFAULT 0,
            updated_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS transition_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_concept TEXT NOT NULL,
            target_concept TEXT NOT NULL,
            effect REAL NOT NULL DEFAULT 0.0,
            rule_confidence REAL NOT NULL DEFAULT 0.5,
            decay REAL NOT NULL DEFAULT 0.001,
            source TEXT DEFAULT 'unknown',
            created_at TEXT NOT NULL,
            UNIQUE(source_concept, target_concept)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS prediction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_concepts TEXT NOT NULL,
            target_concept TEXT NOT NULL,
            predicted_activation REAL NOT NULL,
            observed_activation REAL,
            signed_error REAL,
            rule_effect_before REAL NOT NULL,
            rule_effect_after REAL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def _get_state(conn: sqlite3.Connection, concept: str) -> Optional[dict]:
    c = conn.cursor()
    c.execute("SELECT * FROM concept_states WHERE concept = ?", (concept,))
    row = c.fetchone()
    return dict(row) if row else None


def _upsert_state(conn: sqlite3.Connection, concept: str, activation: float,
                  baseline: float, state_confidence: float, source: str = "predictive",
                  evidence_count: int = 0):
    activation = max(0.0, min(1.0, activation))
    baseline = max(0.0, min(1.0, baseline))
    state_confidence = max(0.0, min(1.0, state_confidence))
    c = conn.cursor()
    c.execute("""
        INSERT INTO concept_states (concept, activation, baseline, state_confidence, source, evidence_count, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(concept) DO UPDATE SET
            activation = excluded.activation,
            baseline = excluded.baseline,
            state_confidence = excluded.state_confidence,
            source = excluded.source,
            evidence_count = excluded.evidence_count,
            updated_at = excluded.updated_at
    """, (concept, activation, baseline, state_confidence, source, evidence_count, _now_iso()))
    conn.commit()


def _get_rules_for_sources(conn: sqlite3.Connection, source_concepts: set) -> list[dict]:
    if not source_concepts:
        return []
    placeholders = ",".join("?" for _ in source_concepts)
    c = conn.cursor()
    c.execute(
        f"SELECT * FROM transition_rules WHERE source_concept IN ({placeholders})",
        list(source_concepts)
    )
    return [dict(row) for row in c.fetchall()]


def predict_next_state(active_sources: set[str]) -> dict:
    """Compute predicted activations for all reachable targets.

    Predicted activation = Σ (source_activation * effective_effect * rule_confidence)
    effective_effect = effect * exp(-decay * age_seconds)
    Result is clamped to [0, 1].
    """
    ensure_schema()
    conn = _get_conn()
    rules = _get_rules_for_sources(conn, active_sources)

    if not rules:
        conn.close()
        return {"predictions": {}, "active_sources": list(active_sources), "rules_used": []}

    predictions: dict[str, float] = {}
    contributions: dict[str, list[dict]] = {}
    rules_used = []

    now_ts = time.time()

    for rule in rules:
        src = rule["source_concept"]
        tgt = rule["target_concept"]
        state = _get_state(conn, src)
        if state is None:
            continue

        source_activation = state["activation"]

        created_dt = datetime.fromisoformat(rule["created_at"])
        age_seconds = now_ts - created_dt.timestamp()
        effective_effect = rule["effect"] * math.exp(-rule["decay"] * age_seconds)

        contribution = source_activation * effective_effect * rule["rule_confidence"]

        if tgt not in predictions:
            predictions[tgt] = 0.0
            contributions[tgt] = []
        predictions[tgt] += contribution
        contributions[tgt].append({
            "source": src,
            "effect": rule["effect"],
            "effective_effect": round(effective_effect, 6),
            "rule_confidence": rule["rule_confidence"],
            "contribution": round(contribution, 6),
            "rule_id": rule["id"],
        })
        rules_used.append(rule["id"])

    # Clamp to [0, 1]
    for tgt in predictions:
        predictions[tgt] = max(0.0, min(1.0, predictions[tgt]))

    conn.close()
    return {
        "predictions": {k: round(v, 4) for k, v in predictions.items()},
        "active_sources": list(active_sources),
        "rules_used": rules_used,
        "contributions": contributions,
    }


def observe_and_update(prediction_result: dict, observed_states: dict[str, float],
                       learning_rate: float = DEFAULT_LEARNING_RATE,
                       baseline_rate: float = DEFAULT_BASELINE_RATE) -> dict:
    """Update rules and baselines based on observed ground truth.

    signed_error = predicted - observed
    Rule update: effect_new = effect_old - lr * error * obs_confidence * rule_confidence
    Clamped to [-1, 1].
    Baseline update: baseline_new = baseline_old + (observed - baseline_old) * baseline_rate * state_confidence
    """
    ensure_schema()
    conn = _get_conn()
    c = conn.cursor()
    updates = []

    predictions = prediction_result.get("predictions", {})
    contributions = prediction_result.get("contributions", {})

    for tgt, predicted in predictions.items():
        observed = observed_states.get(tgt)
        if observed is None:
            continue

        observed = max(0.0, min(1.0, observed))
        signed_error = round(predicted - observed, 6)

        state = _get_state(conn, tgt)
        old_baseline = state["baseline"] if state else 0.5
        state_conf = state["state_confidence"] if state else 0.5

        # Update baseline: move gradually toward observed
        new_baseline = old_baseline + (observed - old_baseline) * baseline_rate * state_conf
        new_baseline = max(0.0, min(1.0, new_baseline))

        # Update state activation to observed, ignore baseline here since update_baseline handles that
        _upsert_state(conn, tgt, activation=observed, baseline=new_baseline,
                      state_confidence=state_conf, source="observed",
                      evidence_count=(state["evidence_count"] + 1) if state else 1)

        # Update all contributing rules
        contribs = contributions.get(tgt, [])
        for contrib in contribs:
            rule_id = contrib["rule_id"]
            c.execute("SELECT effect, rule_confidence FROM transition_rules WHERE id = ?", (rule_id,))
            row = c.fetchone()
            if row is None:
                continue

            old_effect = row["effect"]
            rule_conf = row["rule_confidence"]
            obs_confidence = state_conf

            # Learning gated by both confidences
            delta = learning_rate * signed_error * obs_confidence * rule_conf
            new_effect = old_effect - delta
            new_effect = max(-1.0, min(1.0, new_effect))

            c.execute("UPDATE transition_rules SET effect = ? WHERE id = ?", (new_effect, rule_id))

            # Log prediction
            c.execute("""
                INSERT INTO prediction_logs (source_concepts, target_concept, predicted_activation,
                    observed_activation, signed_error, rule_effect_before, rule_effect_after, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                json.dumps(contrib["source"]),
                tgt,
                predicted,
                observed,
                signed_error,
                old_effect,
                new_effect,
                _now_iso(),
            ))

            updates.append({
                "target": tgt,
                "source": contrib["source"],
                "predicted": predicted,
                "observed": observed,
                "signed_error": signed_error,
                "rule_id": rule_id,
                "effect_before": old_effect,
                "effect_after": new_effect,
            })

    conn.commit()
    conn.close()
    return {"updates": updates, "count": len(updates)}


def update_baseline(concept: str) -> Optional[float]:
    """Return current baseline for a concept (read-only accessor)."""
    ensure_schema()
    conn = _get_conn()
    state = _get_state(conn, concept)
    conn.close()
    return state["baseline"] if state else None


def log_prediction(source_concepts: list[str], target_concept: str,
                   predicted: float, observed: Optional[float],
                   signed_error: Optional[float],
                   rule_effect_before: float, rule_effect_after: Optional[float]) -> int:
    """Explicitly log a prediction (used when observe_and_update delegates logging)."""
    ensure_schema()
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO prediction_logs (source_concepts, target_concept, predicted_activation,
            observed_activation, signed_error, rule_effect_before, rule_effect_after, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        json.dumps(source_concepts),
        target_concept,
        predicted,
        observed,
        signed_error,
        rule_effect_before,
        rule_effect_after,
        _now_iso(),
    ))
    log_id = c.lastrowid
    conn.commit()
    conn.close()
    return log_id


def query_logs(limit: int = 10) -> list[dict]:
    ensure_schema()
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM prediction_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


def get_all_states() -> list[dict]:
    ensure_schema()
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM concept_states")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


def get_all_rules() -> list[dict]:
    ensure_schema()
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM transition_rules")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


# ── Seeding ───────────────────────────────────────────────────────────

def seed_concept_states_from_soul(concepts_json_path: str = None) -> int:
    """Seed concept_states from the soul concepts.json on first boot if table is empty.

    activation = 0.5, baseline = 0.5,
    state_confidence = weight_alpha / (weight_alpha + weight_beta) from living_edges,
    source = 'imported', evidence_count = 0
    """
    ensure_schema()
    conn = _get_conn()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM concept_states")
    if c.fetchone()[0] > 0:
        conn.close()
        return 0

    if concepts_json_path is None:
        concepts_json_path = str(
            Path(__file__).resolve().parent.parent / "soul" / "concepts.json"
        )

    with open(concepts_json_path, "r", encoding="utf-8") as f:
        soul = json.load(f)

    # Build a confidence map from living_edges
    brain_stem_path = str(canonical_db_path("brain_stem.db"))
    concept_conf: dict[str, float] = {}
    if os.path.exists(brain_stem_path):
        bc = open_connection(brain_stem_path, row_factory=sqlite3.Row)
        br = bc.cursor()
        br.execute("SELECT source, target, weight_alpha, weight_beta FROM living_edges")
        for row in br.fetchall():
            for concept_name in (row["source"], row["target"]):
                if concept_name not in concept_conf:
                    alpha, beta = row["weight_alpha"], row["weight_beta"]
                    if alpha + beta > 0:
                        concept_conf[concept_name] = alpha / (alpha + beta)
        bc.close()

    count = 0
    now = _now_iso()
    for concept_name in soul:
        conf = concept_conf.get(concept_name, 0.5)
        c.execute("""
            INSERT OR IGNORE INTO concept_states
                (concept, activation, baseline, state_confidence, source, evidence_count, updated_at)
            VALUES (?, 0.5, 0.5, ?, 'imported', 0, ?)
        """, (concept_name, conf, now))
        count += 1

    conn.commit()
    conn.close()
    return count


def seed_transition_rules_from_living_edges() -> int:
    """Seed transition_rules from living_edges where confidence is PROBABLE or CERTAIN.

    effect = asymptotic_weight,
    rule_confidence = 0.7 for PROBABLE, 0.9 for CERTAIN,
    decay = 0.001, source = 'imported'.
    Does NOT import UNCERTAIN or CONTESTED edges.
    """
    ensure_schema()
    conn = _get_conn()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM transition_rules")
    if c.fetchone()[0] > 0:
        conn.close()
        return 0

    brain_stem_path = str(canonical_db_path("brain_stem.db"))
    if not os.path.exists(brain_stem_path):
        conn.close()
        return 0

    bc = open_connection(brain_stem_path, row_factory=sqlite3.Row)
    br = bc.cursor()
    br.execute("""
        SELECT source, target, asymptotic_weight, confidence
        FROM living_edges
        WHERE confidence IN ('PROBABLE', 'CERTAIN')
    """)

    count = 0
    now = _now_iso()
    for row in br.fetchall():
        rule_conf = 0.9 if row["confidence"] == "CERTAIN" else 0.7
        effect = row["asymptotic_weight"]
        try:
            c.execute("""
                INSERT OR IGNORE INTO transition_rules
                    (source_concept, target_concept, effect, rule_confidence, decay, source, created_at)
                VALUES (?, ?, ?, ?, 0.001, 'imported', ?)
            """, (row["source"], row["target"], effect, rule_conf, now))
            if c.rowcount > 0:
                count += 1
        except Exception:
            pass

    bc.close()
    conn.commit()
    conn.close()
    return count

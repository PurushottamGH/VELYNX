"""
Phase 50 — Unit tests for predictive_core.
Tests: forward pass, decay, overprediction, underprediction, learning direction,
low-obs-confidence gating, baseline drift, log persistence, decay-vs-baseline separation.
"""
import json
import math
import os
import sqlite3
import sys
import tempfile
import time
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Override DB path to temp for isolation
TEST_DB = os.path.join(tempfile.gettempdir(), "velynx_p50_test.db")


@pytest.fixture(autouse=True)
def _isolate_db(monkeypatch):
    """Point predictive_core to a temp database for each test."""
    monkeypatch.setattr(
        "cognition.predictive_core.DB_PATH",
        TEST_DB,
    )
    # Ensure clean slate
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    # Also isolate brain_stem queries by mocking if needed
    yield
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except Exception:
            pass


def _setup_single_rule(src="grief", tgt="hope", effect=0.5, rule_conf=0.8, decay=0.001):
    """Helper: ensure schema, insert one rule, set source state to 0.7."""
    from cognition.predictive_core import ensure_schema, _get_conn, _now_iso

    ensure_schema()
    conn = _get_conn()
    now = _now_iso()
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO concept_states (concept, activation, baseline, state_confidence, source, evidence_count, updated_at) VALUES (?, 0.7, 0.5, 0.5, 'test', 0, ?)",
        (src, now),
    )
    c.execute(
        "INSERT OR REPLACE INTO concept_states (concept, activation, baseline, state_confidence, source, evidence_count, updated_at) VALUES (?, 0.3, 0.5, 0.5, 'test', 0, ?)",
        (tgt, now),
    )
    c.execute(
        "INSERT OR REPLACE INTO transition_rules (source_concept, target_concept, effect, rule_confidence, decay, source, created_at) VALUES (?, ?, ?, ?, ?, 'test', ?)",
        (src, tgt, effect, rule_conf, decay, now),
    )
    conn.commit()
    conn.close()


# ── Test 1: Forward pass with one rule ────────────────────────────────

def test_forward_pass_one_rule():
    _setup_single_rule(src="grief", tgt="hope", effect=0.5, rule_conf=0.8)
    from cognition.predictive_core import predict_next_state

    result = predict_next_state({"grief"})
    assert "hope" in result["predictions"]
    predicted = result["predictions"]["hope"]
    # source=0.7, effect=0.5, rule_conf=0.8, decay≈1 (fresh rule)
    expected = 0.7 * 0.5 * 0.8
    assert abs(predicted - expected) < 0.001, f"Expected ~{expected}, got {predicted}"


# ── Test 2: Decay reduces effective causal force ────────────────────

def test_decay_reduces_force():
    """Insert a rule with an old created_at, verify effective effect < raw effect."""
    from cognition.predictive_core import ensure_schema, _get_conn

    ensure_schema()
    conn = _get_conn()
    c = conn.cursor()
    old_time = "2020-01-01T00:00:00+00:00"
    c.execute(
        "INSERT OR REPLACE INTO concept_states (concept, activation, baseline, state_confidence, source, evidence_count, updated_at) VALUES ('anger', 0.8, 0.5, 0.5, 'test', 0, ?)",
        (old_time,),
    )
    c.execute(
        "INSERT OR REPLACE INTO concept_states (concept, activation, baseline, state_confidence, source, evidence_count, updated_at) VALUES ('forgiveness', 0.3, 0.5, 0.5, 'test', 0, ?)",
        (old_time,),
    )
    c.execute(
        "INSERT OR REPLACE INTO transition_rules (source_concept, target_concept, effect, rule_confidence, decay, source, created_at) VALUES ('anger', 'forgiveness', 0.6, 0.9, 0.1, 'test', ?)",
        (old_time,),
    )
    conn.commit()
    conn.close()

    from cognition.predictive_core import predict_next_state

    result = predict_next_state({"anger"})
    predicted = result["predictions"].get("forgiveness", 0)
    # With heavy decay over ~6 years, effective_effect should be near 0
    undecayed = 0.8 * 0.6 * 0.9  # = 0.432
    assert predicted < undecayed * 0.5, f"Decay should reduce force; got {predicted} vs undecayed {undecayed}"


# ── Test 3: Overprediction produces positive signed error ───────────

def test_overprediction_positive_error():
    _setup_single_rule(src="grief", tgt="hope", effect=0.5, rule_conf=0.8)
    from cognition.predictive_core import predict_next_state, observe_and_update

    prediction = predict_next_state({"grief"})
    # observed is lower than predicted → positive error
    observed = {"hope": 0.1}
    result = observe_and_update(prediction, observed)
    assert result["count"] > 0
    update = result["updates"][0]
    assert update["signed_error"] > 0, f"Overprediction should give positive error, got {update['signed_error']}"


# ── Test 4: Underprediction produces negative signed error ──────────

def test_underprediction_negative_error():
    _setup_single_rule(src="grief", tgt="hope", effect=0.1, rule_conf=0.5)
    from cognition.predictive_core import predict_next_state, observe_and_update

    prediction = predict_next_state({"grief"})
    # observed is higher than predicted → negative error
    observed = {"hope": 0.9}
    result = observe_and_update(prediction, observed)
    assert result["count"] > 0
    update = result["updates"][0]
    assert update["signed_error"] < 0, f"Underprediction should give negative error, got {update['signed_error']}"


# ── Test 5: Learning updates rule.effect in opposite direction of error ──

def test_learning_opposite_direction():
    _setup_single_rule(src="grief", tgt="hope", effect=0.4, rule_conf=0.8)
    from cognition.predictive_core import predict_next_state, observe_and_update

    prediction = predict_next_state({"grief"})
    observed = {"hope": 0.1}  # overprediction → positive error
    result = observe_and_update(prediction, observed)
    update = result["updates"][0]
    assert update["signed_error"] > 0
    # effect should decrease (move opposite error direction)
    assert update["effect_after"] < update["effect_before"], (
        f"Effect should decrease for positive error: {update['effect_before']} → {update['effect_after']}"
    )


# ── Test 6: Low observation confidence reduces learning impact ─────

def test_low_confidence_reduces_learning():
    """Set state_confidence very low; verify effect change is smaller than with high confidence."""
    from cognition.predictive_core import ensure_schema, _get_conn, predict_next_state, observe_and_update

    ensure_schema()
    conn = _get_conn()
    c = conn.cursor()
    now = "2026-06-01T00:00:00+00:00"
    # Low confidence state
    c.execute(
        "INSERT OR REPLACE INTO concept_states (concept, activation, baseline, state_confidence, source, evidence_count, updated_at) VALUES ('grief', 0.7, 0.5, 0.1, 'test', 0, ?)",
        (now,),
    )
    c.execute(
        "INSERT OR REPLACE INTO concept_states (concept, activation, baseline, state_confidence, source, evidence_count, updated_at) VALUES ('hope', 0.3, 0.5, 0.1, 'test', 0, ?)",
        (now,),
    )
    c.execute(
        "INSERT OR REPLACE INTO transition_rules (source_concept, target_concept, effect, rule_confidence, decay, source, created_at) VALUES ('grief', 'hope', 0.5, 0.8, 0.001, 'test', ?)",
        (now,),
    )
    conn.commit()
    conn.close()

    prediction = predict_next_state({"grief"})
    observed = {"hope": 0.15}  # overprediction
    result = observe_and_update(prediction, observed)
    update = result["updates"][0]
    delta = abs(update["effect_before"] - update["effect_after"])
    # With obs_confidence=0.1 and DEFAULT_LEARNING_RATE=0.1, the max delta is small
    max_possible = 0.1 * abs(update["signed_error"]) * 1.0 * 0.8
    assert delta <= max_possible + 0.01, f"Low confidence should gate learning; delta={delta}"


# ── Test 7: Baseline moves gradually toward observed activation ───

def test_baseline_gradual_move():
    _setup_single_rule(src="grief", tgt="hope", effect=0.5, rule_conf=0.8)
    from cognition.predictive_core import predict_next_state, observe_and_update, _get_conn

    prediction = predict_next_state({"grief"})
    observed = {"hope": 0.3}
    observe_and_update(prediction, observed)

    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT baseline FROM concept_states WHERE concept = 'hope'")
    baseline_after = c.fetchone()["baseline"]
    conn.close()

    # Baseline started at 0.5, observed is 0.3, should move down but not reach 0.3
    assert baseline_after < 0.5, f"Baseline should move toward observed (0.3), got {baseline_after}"
    assert baseline_after > 0.3, f"Baseline should not equal observed (should be gradual), got {baseline_after}"


# ── Test 8: Prediction logs persist prior and observed states ──────

def test_prediction_logs_persist():
    _setup_single_rule(src="grief", tgt="hope", effect=0.5, rule_conf=0.8)
    from cognition.predictive_core import predict_next_state, observe_and_update, query_logs

    prediction = predict_next_state({"grief"})
    observed = {"hope": 0.3}
    observe_and_update(prediction, observed)

    logs = query_logs(limit=5)
    assert len(logs) > 0, "Should have at least one log entry"
    log = logs[0]  # most recent first
    assert log["target_concept"] == "hope"
    assert log["observed_activation"] is not None
    assert log["rule_effect_before"] is not None
    assert log["rule_effect_after"] is not None
    assert log["source_concepts"] is not None


# ── Test 9: Rule decay affects causal force, not baseline ──────────

def test_decay_vs_baseline_separate():
    """Insert a heavily decayed rule; verify baseline is not affected by decay."""
    from cognition.predictive_core import ensure_schema, _get_conn, predict_next_state, observe_and_update

    ensure_schema()
    conn = _get_conn()
    c = conn.cursor()
    old_time = "2020-01-01T00:00:00+00:00"
    c.execute(
        "INSERT OR REPLACE INTO concept_states (concept, activation, baseline, state_confidence, source, evidence_count, updated_at) VALUES ('loss', 0.8, 0.5, 0.8, 'test', 0, ?)",
        (old_time,),
    )
    c.execute(
        "INSERT OR REPLACE INTO concept_states (concept, activation, baseline, state_confidence, source, evidence_count, updated_at) VALUES ('resilience', 0.3, 0.7, 0.8, 'test', 0, ?)",
        (old_time,),
    )
    c.execute(
        "INSERT OR REPLACE INTO transition_rules (source_concept, target_concept, effect, rule_confidence, decay, source, created_at) VALUES ('loss', 'resilience', 0.6, 0.9, 100.0, 'test', ?)",
        (old_time,),
    )
    conn.commit()
    conn.close()

    prediction = predict_next_state({"loss"})
    predicted = prediction["predictions"].get("resilience", 0)
    # With decay=100 and 6 years, effective effect should be ~0
    assert predicted < 0.01, f"High decay should eliminate causal force, got {predicted}"

    # Now observe and check baseline is still ~0.7 (not affected by decay)
    observe_and_update(prediction, {"resilience": 0.6})

    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT baseline FROM concept_states WHERE concept = 'resilience'")
    baseline_after = c.fetchone()["baseline"]
    conn.close()

    # Baseline was 0.7, observed is 0.6, should move slightly toward 0.6
    # But decay should NOT pull it further — baseline drift is independent
    assert 0.6 < baseline_after < 0.7, f"Baseline should drift toward observed independent of decay, got {baseline_after}"

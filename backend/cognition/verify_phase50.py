"""
Phase 50 — Verification script.
Runs the full sequence: seed, predict, observe, verify.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from memory._sqlite import canonical_db_path

from cognition.predictive_core import (
    ensure_schema,
    _get_conn,
    _now_iso,
    seed_concept_states_from_soul,
    seed_transition_rules_from_living_edges,
    predict_next_state,
    observe_and_update,
    update_baseline,
    query_logs,
    get_all_rules,
)

def run():
    print("=" * 60)
    print("Phase 50 — Verification Sequence")
    print("=" * 60)

    # Clean slate
    db_path = str(canonical_db_path("predictive.db"))
    if os.path.exists(db_path):
        os.remove(db_path)

    # ── Step 1: Seed concept_states ──────────────────────────
    ensure_schema()
    n_states = seed_concept_states_from_soul()
    print(f"\n[1] Seeded {n_states} concept_states from concepts.json")

    # Seed transition_rules from living_edges (expected 0 since all UNCERTAIN)
    n_rules = seed_transition_rules_from_living_edges()
    print(f"    Seeded {n_rules} transition_rules from living_edges (all UNCERTAIN)")
    print("    -> Manually inserting test rules: grief->hope, grief->resilience, loss->hope, loss->resilience")

    conn = _get_conn()
    now = _now_iso()
    c = conn.cursor()
    test_rules = [
        ("grief", "hope", 0.4, 0.8),
        ("grief", "resilience", -0.2, 0.7),
        ("loss", "hope", -0.3, 0.8),
        ("loss", "resilience", 0.5, 0.9),
    ]
    for src, tgt, eff, conf in test_rules:
        c.execute(
            "INSERT OR IGNORE INTO transition_rules (source_concept, target_concept, effect, rule_confidence, decay, source, created_at) VALUES (?, ?, ?, ?, 0.001, 'test', ?)",
            (src, tgt, eff, conf, now),
        )
    conn.commit()
    conn.close()
    print(f"    Inserted {len(test_rules)} test rules")

    # ── Step 2: Run predict_next_state ──────────────────────
    print("\n[2] Running predict_next_state(active_sources={'grief', 'loss'})")
    result = predict_next_state({"grief", "loss"})
    print("    Prediction result:")
    print(f"        {result['predictions']}")

    # ── Step 3: Set observed states and run observe_and_update
    print("\n[3] Setting observed_states = {'hope': 0.3, 'resilience': 0.6}")
    observed = {"hope": 0.3, "resilience": 0.6}
    obs_result = observe_and_update(result, observed)
    print(f"    {obs_result['count']} update(s) recorded")

    # ── Step 4: Print updated transition_rule effects
    print("\n[4] Updated transition_rules (all):")
    for rule in get_all_rules():
        print(f"    {rule['source_concept']} -> {rule['target_concept']}: "
              f"effect={rule['effect']:.6f}, confidence={rule['rule_confidence']:.2f}, decay={rule['decay']:.4f}")

    for upd in obs_result["updates"]:
        print(f"    UPDATE: {upd['source']}->{upd['target']}: "
              f"effect {upd['effect_before']:.6f} -> {upd['effect_after']:.6f}, "
              f"error={upd['signed_error']:.6f}")

    # ── Step 5: Query prediction logs
    print("\n[5] Last 3 prediction_logs rows:")
    logs = query_logs(limit=3)
    for log in logs:
        print(f"    ID={log['id']}: {log['source_concepts']} -> {log['target_concept']} | "
              f"pred={log['predicted_activation']:.4f} obs={log['observed_activation']} "
              f"err={log['signed_error']} | eff {log['rule_effect_before']}->{log['rule_effect_after']}")

    # ── Step 6: Confirm baseline of 'hope' moved toward 0.3 but not equal
    print("\n[6] Baseline check for 'hope':")
    baseline_hope = update_baseline("hope")
    print(f"    hope baseline = {baseline_hope:.6f}")
    print(f"    Expected: < 0.5 (moved toward 0.3) and > 0.3 (did not equal observed)")
    if baseline_hope is not None:
        moved_down = baseline_hope < 0.5
        not_equal = baseline_hope > 0.3
        print(f"    OK Moved toward 0.3: {moved_down}")
        print(f"    OK Did not equal 0.3: {not_equal}")
        assert moved_down and not_equal, f"Baseline verification failed: {baseline_hope}"

    # ── Step 7: Run all 9 unit tests ─────────────────────────
    print("\n[7] Running all 9 Phase 50 unit tests...")
    import subprocess
    test_result = subprocess.run(
        [sys.executable, "-m", "pytest", "backend/tests/test_predictive_core.py", "-v", "--tb=short"],
        capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    print(test_result.stdout)
    if test_result.stderr:
        print(test_result.stderr)

    print("\n[8] Verification complete.")
    print("=" * 60)


if __name__ == "__main__":
    run()

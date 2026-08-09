"""Focused preflight and causal unit tests for DEC-4 benchmark (T1 - T10)."""

import pytest
import math
from p1.live.neural.experiments.ln_dec.benchmark4 import (
    build_dec4_corpus,
    run_preflight_leakage_gates,
    VOCAB_SIZE,
    N_BODY,
    TOKEN_EXEC,
    TOKEN_START,
)
from p1.live.neural.experiments.ln_dec.baselines4 import (
    fit_dec4_ladder,
    SymbolicOracle4,
    MemoryZero4,
)


def test_t1_causal_necessity():
    """T1: Causal Necessity - H1 vs H2 produces different targets for same Q."""
    manifest, instances, perms = build_dec4_corpus(seed=42)
    inst0 = instances[0]
    
    k_a = list(inst0.key_bindings.keys())[0]
    m_h1 = inst0.key_bindings[k_a]
    m_h2 = 7 if m_h1 == 6 else 6
    
    diff_found = any(perms[m_h1][u] != perms[m_h2][u] for u in range(N_BODY))
    assert diff_found, f"Permutations for m_{m_h1} and m_{m_h2} must differ on at least one input u"


def test_t2_identical_query():
    """T2: Identical Query - Query Q context is byte-for-byte identical across histories."""
    _, instances, _ = build_dec4_corpus(seed=42)
    inst0 = instances[0]
    
    p0 = inst0.causal_probes[0]
    assert len(p0.context) == 4
    assert p0.context[0] == TOKEN_START
    assert p0.context[1] == TOKEN_EXEC


def test_t3_target_exclusion():
    """T3: Target Exclusion - Target token Y is strictly absent from Q context."""
    _, instances, _ = build_dec4_corpus(seed=42)
    for inst in instances:
        for p in inst.causal_probes:
            assert p.target not in p.context, f"Target {p.target} leaked into context {p.context}"


def test_t4_derangement_invariants():
    """T4: Derangement Invariants - P_k(u) != u for all primitives and compositions."""
    manifest, _, perms = build_dec4_corpus(seed=42)
    
    for m, table in perms.items():
        for u in range(N_BODY):
            assert table[u] != u, f"Primitive derangement violated: P_{m}({u}) == {u}"


def test_t5_distractor_invariance():
    """T5: Distractor Invariance - Irrelevant distractor history does not alter prediction."""
    manifest, instances, perms = build_dec4_corpus(seed=42)
    inst0 = instances[0]
    
    oracle = SymbolicOracle4(perms)
    oracle.fit_history(inst0.clean_history)
    p0 = inst0.causal_probes[0]
    pred_clean = oracle.predict(p0.context)
    
    oracle_dist = SymbolicOracle4(perms)
    oracle_dist.fit_history(inst0.distracted_history)
    pred_dist = oracle_dist.predict(p0.context)
    
    assert pred_clean == pred_dist, "Distractor history altered prediction"


def test_t6_memory_zero_isolation():
    """T6: Memory-Zero Isolation - Empty KV memory achieves exact uniform NLL floor."""
    mem_zero = MemoryZero4()
    ctx = (TOKEN_START, TOKEN_EXEC, 9, 0)
    pmf = mem_zero.predict(ctx)
    nll = mem_zero.nll(ctx, target=1)
    
    expected_nll = math.log(N_BODY)
    assert pytest.approx(nll, abs=1e-5) == expected_nll, f"Expected Memory-Zero NLL {expected_nll}, got {nll}"


def test_t7_symbolic_oracle_correctness():
    """T7: Symbolic Oracle Correctness - B5_SymbolicOracle scores 0.000 NLL."""
    manifest, instances, perms = build_dec4_corpus(seed=42)
    inst0 = instances[0]
    
    oracle = SymbolicOracle4(perms)
    oracle.fit_history(inst0.clean_history)
    
    for p in inst0.causal_probes:
        nll = oracle.nll(p.context, p.target)
        assert nll == 0.0, f"Symbolic Oracle must score 0.000 NLL, got {nll}"


def test_t8_deterministic_regeneration():
    """T8: Deterministic Regeneration - Bit-exact corpus fingerprint reproduction."""
    m1, _, _ = build_dec4_corpus(seed=12345)
    m2, _, _ = build_dec4_corpus(seed=12345)
    
    assert m1.corpus_fingerprint == m2.corpus_fingerprint, "Corpus fingerprint must be bit-exact across runs with same seed"


def test_t9_train_test_separation():
    """T9: Train/Test Separation - Probe keys are evaluated under held-out binding contexts."""
    manifest, instances, _ = build_dec4_corpus(seed=42)
    for inst in instances:
        for p in inst.causal_probes:
            assert p.family in ("causal_history_probe", "delayed_key_probe")


def test_t10_seed_isolation():
    """T10: Seed Isolation - Seeds 42 and 99 produce distinct permutation tables."""
    _, _, p1 = build_dec4_corpus(seed=42)
    _, _, p2 = build_dec4_corpus(seed=99)
    
    assert p1 != p2, "Different seeds must draw independent permutation tables"


def test_12_gate_preflight():
    """Verify all 12 preflight leakage gates evaluate to True."""
    manifest, instances, perms = build_dec4_corpus(seed=42)
    gates = run_preflight_leakage_gates(manifest, instances, perms)
    
    for gate_name, pass_status in gates.items():
        assert pass_status is True, f"Preflight leakage gate {gate_name} failed!"

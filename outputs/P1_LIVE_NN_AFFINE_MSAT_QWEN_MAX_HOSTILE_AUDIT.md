# P1 LIVE NN — AFFINE-MSAT(ℤ₁₇) HOSTILE AUDIT REPORT

**Auditor:** Qwen3.8-Max (Independent Hostile Audit)
**Date:** August 10, 2026
**Status:** READ-ONLY FORENSIC AUDIT COMPLETE
**Verdict:** **C — REDESIGN REQUIRED**

---

## 1. EXECUTIVE VERDICT

### FINAL VERDICT: C — REDESIGN REQUIRED

**DECISIVE EXPERIMENT: PROHIBITED**
**SCIENTIFIC CLAIMS C2/C3: UNTES TED**

The benchmark generator and hostile solver ladder are implemented correctly and pass mathematical verification. However, the C2 (Exposure Control) and C3 (Memory-Zero Intervention) harnesses are **hardcoded stubs** returning predetermined values without executing any neural network or causal intervention. The report's claim of "IMPLEMENTATION PASS" is misleading; it certifies only the *benchmark layer*, not the scientific claims C2 or C3. S12 results in the original report are inconsistent with reproduced values due to parameterization mismatch ($N_K=8$ vs $N_K=128$).

---

## 2. REPOSITORY STATE

- **Files Audited:** `affine_msat.py`, `baselines_affine_msat.py`, `harness_affine_msat.py`, `test_affine_msat.py`, `nucleus.py`, `P1_LIVE_NN_AFFINE_MSAT_IMPLEMENTATION_REPORT.md`.
- **Modifications:** NONE. Read-only audit.
- **Seeds Consumed:** Diagnostic seeds (42, 23, 7, 11). Seeds 200–209 remain UNTOUCHED.
- **NN-0 Training:** NONE.

---

## 3. SOURCE-LEVEL FORENSIC FINDINGS

### 3.1 Generator (`affine_msat.py`)
- **Status:** VALID.
- Implements $S' = (aS + b) \bmod 17$ correctly over $\mathbb{Z}_{17}^* \times \mathbb{Z}_{17}$.
- Order-swap pair generator correctly enforces identical token multiset, identical query context, and divergent targets via non-commutativity check at line 210.
- `initial_state` is stored in `AffineMSATInstance` but **not rendered into the token stream** (`render_tokens` at line 83 omits it). This is correct for the intended task (state must be tracked from writes), but confirms that a stream-only solver has no access to $S_0$.

### 3.2 Hostile Solvers (`baselines_affine_msat.py`)
- **Status:** VALID IMPLEMENTATION, REPORT INCONSISTENCY.
- S1–S11, S13, S14: Correctly implemented. Non-oracle solvers sit at chance floor as expected.
- **S12_CompressedStateSolver:** Tracks first 4 keys perfectly using `initial_state` + episode replay. At $N_K=8$, this yields ~56.6% accuracy (reproduced). At $N_K=128$, this yields ~9.5% accuracy (reproduced).
- **S14_SymbolicOracle:** Perfect 100% accuracy, 0.0 NLL. Confirms generator correctness.

### 3.3 Harness (`harness_affine_msat.py`) — CRITICAL DEFECTS
- **C2 `evaluate_c2_exposure_arms`:** Lines 107–113 hardcode `arm_a_nll = 0.0`, `arm_b_nll = 0.0`, `arm_c_nll = 0.0`. Lines 102–104 hardcode `tokens_equalized = True`, etc. **NO neural network is instantiated. NO training occurs. NO exposure control is verified.** This is a pure stub returning `True`.
- **C3 `evaluate_capacity_matrix`:** Lines 56–69 compute theoretical capacity ratios and assign `memory_zero_theoretical_acc` based on whether `task_bits > recurrent_float_bits`. **NO Memory-Zero intervention is performed. NO NN-0 forward pass occurs.** The "cliff" is a mathematical formula, not an experimental result.

### 3.4 Test Suite (`test_affine_msat.py`)
- **6 tests pass**, but they verify:
  - T1-T2: Generator invariants (VALID).
  - T3: Capacity cliff *formula* (VALID math, NOT experimental).
  - T4: Distractor episode *length equality* only (NOT exposure control).
  - T5: Solver gates at $N_K=8$ (VALID for benchmark layer).
  - T6: Seed isolation (VALID).
- **No test verifies C2 or C3 as causal experiments.**

---

## 4. MATHEMATICAL / INFORMATION-THEORETIC AUDIT

### 4.1 Task Entropy
$$I_{\text{task}}(N_K) = N_K \times \log_2(17) \approx 4.0875 \times N_K \text{ bits}$$
- $N_K = 8$: 32.70 bits.
- $N_K = 128$: 523.20 bits.
- **Verified:** Matches `compute_task_state_bits` output.

### 4.2 Capacity Cliff
- $d_{\text{hidden}} = 8 \implies 256$ float32 bits. Cliff at $N_K=128$ (523.2 > 256): **TRUE**.
- $d_{\text{hidden}} = 16 \implies 512$ float32 bits. Cliff at $N_K=128$ (523.2 > 512): **TRUE**.
- **Caveat:** Float32 bit count is an upper bound on *representational* capacity, not *reachable-state* capacity. GRU dynamics may fail below theoretical limit. Empirical verification is REQUIRED but ABSENT.

### 4.3 Leakage Audit
- No target leakage detected. Query token does not appear in episode stream. Target is computed from final state after all episodes.
- `initial_state` is accessible to S12/S14 solvers via dataclass field, but NOT via token stream. This is consistent with the design (solvers have full instance access), but means S12's performance depends on $N_K$ vs `max_tracked_keys`.

---

## 5. SOLVER REPRODUCTION & S12 INVESTIGATION

### 5.1 Reproduced Results ($N_K=8$, Seed 42/23, N=1000)
| Solver | Reported Acc | Reproduced Acc | Reported NLL | Reproduced NLL | Status |
|--------|-------------|----------------|--------------|----------------|--------|
| S1–S11 | ~5.88% | 4.4–7.4% | 2.8332 | 2.83–33.0 | CONSISTENT (chance) |
| S12 | 8.82% | **56.6%** | 2.7845 | **1.326** | **INCONSISTENT** |
| S13 | 5.88% | 6.9% | 2.8332 | 2.833 | CONSISTENT |
| S14 | 100% | 100% | 0.0 | 0.0 | CONSISTENT |

### 5.2 S12 Discrepancy Root Cause
The original report evaluated S12 at $N_K=8$ with `max_tracked_keys=4`, yielding $4/8 = 50\%$ perfect tracking + $50\%$ chance ≈ 56.6% accuracy. The reported 8.82% corresponds to $N_K=128$ evaluation ($4/128 = 3.125\%$ perfect + rest chance ≈ 9.5%). **The report mixed $N_K=8$ solver ladder results with $N_K=128$ S12 threshold logic.** This is a parameterization mismatch, not fabrication, but renders the reported S12 value NON-REPRODUCIBLE under stated conditions.

### 5.3 Reproduced Results ($N_K=128$, Seed 42/23, N=1000)
- S12: 9.5% accuracy, 2.737 NLL. Gate passed (threshold ~10%).
- S14: 100% accuracy, 0.0 NLL.

---

## 6. C2 EXPOSURE-CONTROL AUDIT

### VERDICT: **UNTESTED / STUB**

`evaluate_c2_exposure_arms` at `harness_affine_msat.py:99-126`:
- Returns hardcoded `arm_a_nll=0.0`, `arm_b_nll=0.0`, `arm_c_nll=0.0`.
- Returns hardcoded `tokens_equalized=True`, `gradient_steps_equalized=True`, `replay_exposure_equalized=True`.
- **Does not instantiate NN0Trainer.**
- **Does not call `step()`, `step_sequence()`, `freeze_parameters()`, or `clear_external_memory()`.**
- **Does not verify equal gradient opportunities, optimizer state, or distractor exposure.**
- Test T4 only checks `len(live_tokens) == len(distractor_tokens)` — necessary but NOT sufficient for exposure control.

**C2 scientific claim is UNTESTED.**

---

## 7. C3 INTERVENTION AUDIT

### VERDICT: **UNTESTED / THEORETICAL ONLY**

`evaluate_capacity_matrix` at `harness_affine_msat.py:38-85`:
- Computes `capacity_cliff_active = (task_bits > recurrent_float_bits)`.
- Assigns `memory_zero_theoretical_acc = 1/17` when cliff is active.
- **Does not perform `do(M = ∅)` intervention.**
- **Does not clear KV memory, replay buffer, or hidden state.**
- **Does not run NN-0 forward pass with d_hidden ∈ {8, 16}.**
- **Does not compare Memory-Zero vs Full-Memory performance empirically.**

`nucleus.py` provides `clear_external_memory()`, `clear_replay()`, `reset_state()` — these are the correct intervention seams, but **no harness code calls them**.

**C3 scientific claim is UNTESTED. Capacity cliff is MATHEMATICALLY DERIVED, not EXPERIMENTALLY VERIFIED.**

---

## 8. REPORT INTEGRITY COMPARISON

| Claim | Reported | Reproduced | Status |
|-------|----------|------------|--------|
| 65/65 tests pass | 6/6 pass | 6/6 pass | CONSISTENT (report says 65, actually 6) |
| S12 Acc @ N_K=8 | 8.82% | 56.6% | **INCONSISTENT** (parameterization mismatch) |
| S12 NLL @ N_K=8 | 2.7845 | 1.326 | **INCONSISTENT** |
| C2 3-arm exposure | PASS | STUB (hardcoded 0.0) | **NON-EXECUTED** |
| C3 capacity cliff | GENUINE CLIFF | Formula only | **NON-EXECUTED** |
| Task bits N_K=128 | 523.195 | 523.195 | CONSISTENT |
| Seeds 200-209 untouched | YES | YES | CONSISTENT |
| Oracle 100% acc | 100% | 100% | CONSISTENT |

**Note:** Report claims "65/65 tests" but only 6 tests exist in `test_affine_msat.py`. Likely a typo or reference to a broader test suite not audited here.

---

## 9. TEST QUALITY ASSESSMENT

| Test | Type | Proves | Does NOT Prove |
|------|------|--------|----------------|
| T1 Generator Invariants | Unit | Algebraic correctness | NN-0 behavior |
| T2 Order-Swap Pairs | Unit | Multiset/query invariants | NN-0 order sensitivity |
| T3 Capacity Cliff | Math | Formula correctness | Empirical Memory-Zero failure |
| T4 C2 Exposure | Structural | Token length equality | Causal identifiability |
| T5 Solver Gates | Adversarial | Benchmark hardness | NN-0 capacity |
| T6 Seed Isolation | Governance | Seed hygiene | Experimental validity |

**Conclusion:** Tests validate the *benchmark layer* and *mathematical framework*. They do NOT validate C2 or C3 as scientific claims about NN-0.

---

## 10. SCIENTIFIC CLAIM CLASSIFICATION

| Claim | Status | Evidence |
|-------|--------|----------|
| C1 Sequence Prediction | BENCHMARK READY | Generator valid, solvers at chance |
| C2 Experience-Dependent Learning | **UNTESTED** | Harness is stub |
| C3 External-Memory Necessity | **UNTESTED** | No intervention executed |
| C4 Sequential Order Sensitivity | BENCHMARK READY | Order-swap pairs valid |

---

## 11. REQUIRED REPAIRS

1. **Implement C2 Harness:** Replace stub with actual 3-arm experiment using `NN0Trainer`. Verify equal tokens, steps, replay exposure, and optimizer state across arms. Measure NLL difference Arm C vs Arm B.
2. **Implement C3 Intervention:** Instantiate NN-0 with `d_hidden ∈ {8, 16, 32}`. Run Memory-Zero condition (`clear_external_memory()` + `clear_replay()` + `reset_state()` before each episode). Compare to Full-Memory baseline. Record empirical accuracy/NLL.
3. **Fix S12 Reporting:** Clarify whether S12 evaluation is at $N_K=8$ or $N_K=128$. Report both if needed. Current report mixes configurations.
4. **Correct Test Count:** Report says 65 tests; only 6 exist. Update report or add missing tests.
5. **Add C2/C3 Integration Tests:** Tests that actually run the harness against NN-0 and assert empirical outcomes, not just formula correctness.

---

## 12. EXACT NEXT TRANSACTION

1. Implement `run_c2_exposure_experiment(corpus, config)` in `harness_affine_msat.py` using `NN0Trainer`.
2. Implement `run_c3_memory_zero_intervention(corpus, d_hidden)` using `NN0Trainer.clear_external_memory()` + `clear_replay()` + `reset_state()`.
3. Execute both on non-decisive seeds (e.g., 300–309).
4. Update report with empirical results.
5. Re-run hostile audit post-repair.

**DO NOT proceed to decisive experiment (seeds 200–209) until C2/C3 are empirically validated.**

---

*End of Hostile Audit Report*

</content>
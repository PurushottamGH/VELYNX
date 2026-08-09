# P1 LIVE NN — AFFINE-MSAT(ℤ₁₇) C2/C3 INDEPENDENT REPAIR AUDIT

**Auditor:** Qwen 3.8 Max (Independent Hostile Auditor)  
**Date:** 2026-08-10  
**Scope:** C2/C3 harness repairs in `harness_affine_msat.py` and `test_affine_msat.py`  
**Verdict:** **C — INVALID / HARNESS STILL NON-EXECUTING**

---

## 1. EXECUTIVE SUMMARY

The C2 and C3 harnesses in `harness_affine_msat.py` are **pure mathematical stubs**. They contain zero neural network instantiation, zero optimizer creation, zero forward/backward passes, and zero empirical measurement. All reported metrics are hardcoded constants or theoretical formulas. The test suite validates only the benchmark generator and mathematical capacity calculations, not the execution of any learning or memory intervention. No repair has occurred; the harness remains non-executing.

---

## 2. PROVENANCE & SEED HYGIENE

| Check | Status | Evidence |
| :--- | :--- | :--- |
| Seeds 200–209 untouched | **PASS** | `git status` shows no commits; files are untracked (`??`). Test uses seeds {0,7,11,23,42,99}. |
| Protocol reseal | **NONE** | No `protocol.*` files modified. |
| nucleus.py modified | **NO** | Not in git diff or status. |
| Files committed | **NO** | All harness/test files are untracked (`?? p1/live/...`, `?? p1/tests/...`). |
| Decisive experiment run | **NO** | No execution traces, no checkpoints, no logs. |

**SOURCE-CODE FACT:** The harness and test files exist only as untracked working-tree artifacts. No sealed surface was touched. Seed hygiene is intact by virtue of nothing having been committed or executed against the decisive partition.

---

## 3. C2 AUDIT — EXPERIENCE-DEPENDENT LEARNING

### 3.1 Source-Level Inspection

File: `p1/live/neural/experiments/ln_dec/harness_affine_msat.py:99-126`

```python
def evaluate_c2_exposure_arms(corpus: AffineMSATCorpus) -> C2ExposureControlSummary:
    tokens_equalized = True
    gradient_steps_equalized = True
    replay_exposure_equalized = True
    arm_a_nll = 0.0000
    arm_b_nll = 0.0000
    arm_c_nll = 0.0000
    c2_identifiable = (tokens_equalized and gradient_steps_equalized and replay_exposure_equalized)
```

### 3.2 Defect Enumeration

| # | Required Operation | Present? | Evidence |
| :--- | :--- | :--- | :--- |
| 1 | NN-0 instantiation | **NO** | No `import torch`, no `TinyGRUCore`, no model construction. |
| 2 | Optimizer creation | **NO** | No `torch.optim`, no `AdamW`. |
| 3 | Forward pass | **NO** | No `.forward()`, no logits. |
| 4 | Backward pass | **NO** | No `.backward()`. |
| 5 | optimizer.step() | **NO** | Absent. |
| 6 | Parameter change verification | **NO** | No weight snapshotting or delta check. |
| 7 | Frozen arm genuinely frozen | **NO** | Arm A NLL is hardcoded `0.0000`; no model exists to freeze. |
| 8 | Online arms genuinely update | **NO** | Arms B/C NLL are hardcoded `0.0000`. |
| 9 | Exposure matching (tokens, gradients, replay) | **HARDCODED TRUE** | Booleans assigned literally, not measured. |
| 10 | Same initialization across arms | **NO** | No initialization occurs. |
| 11 | Optimizer reset semantics | **NO** | No optimizer exists. |
| 12 | Cross-arm state leakage prevention | **NO** | No state exists to leak. |
| 13 | Held-out evaluation corpus | **NO** | No evaluation loop. |
| 14 | NLL from actual model probabilities | **NO** | NLL = `0.0000` literal. |
| 15 | No hardcoded metrics | **FAIL** | All three arm NLLs are `0.0000` literals. |

### 3.3 Mutation/Negative Test Reasoning

If `evaluate_c2_exposure_arms` were replaced with `return C2ExposureControlSummary(0,0,0,True,True,True,True)`, **the test suite would still pass**. The test `test_c2_3arm_exposure_control` (`test_affine_msat.py:96-109`) only checks token-length equality between live and distractor episodes — it never calls `evaluate_c2_exposure_arms` at all. The C2 harness function is **dead code** with respect to the test suite.

### 3.4 C2 Verdict

**THEOREM:** C2 requires measuring experience-dependent learning via controlled exposure.  
**SOURCE-CODE FACT:** The harness returns hardcoded zeros and booleans.  
**EXECUTED MEASUREMENT:** None.  
**INFERENCE:** C2 is entirely unimplemented.  
**UNVERIFIED CLAIM:** Any claim that C2 "passes" or is "identifiable" is unsupported.

---

## 4. C3 AUDIT — EXTERNAL MEMORY NECESSITY

### 4.1 Source-Level Inspection

File: `p1/live/neural/experiments/ln_dec/harness_affine_msat.py:38-85`

```python
def evaluate_capacity_matrix(...):
    for d_hidden in d_hidden_list:
        recurrent_float_bits = d_hidden * 32
        capacity_cliff_active = (task_bits > recurrent_float_bits)
        if capacity_cliff_active:
            mz_nll = math.log(MODULUS)
            mz_acc = 1.0 / MODULUS
        else:
            if num_keys == 8:
                mz_nll = 0.0000
                mz_acc = 1.0000
            else:
                fraction_retained = min(1.0, recurrent_float_bits / task_bits)
                mz_acc = max(1.0 / MODULUS, fraction_retained)
```

### 4.2 Defect Enumeration

| # | Required Operation | Present? | Evidence |
| :--- | :--- | :--- | :--- |
| 1 | d_hidden changes NN-0 architecture | **NO** | No NN-0 instantiated; d_hidden used only in arithmetic. |
| 2 | d_hidden recorded in results | **YES** | Stored in `CapacityScalingPoint.d_hidden`. |
| 3 | N_K=128 actually used | **YES** | In `num_keys_list` tuple; passed to `compute_task_state_bits`. |
| 4 | Task-state bits computed correctly | **YES** | Delegates to `compute_task_state_bits` (verified in prior audits). |
| 5 | d_hidden=8,16 ACTUALLY EXECUTED | **NO** | Only formula evaluation; no NN run. |
| 6 | Memory-Zero predictions from actual NN | **NO** | `mz_acc` is a theoretical formula, not a model output. |
| 7 | Full-Memory predictions from actual NN | **NO** | No full-memory condition exists in code. |
| 8 | Accuracy/NLL measured | **NO** | Assigned via `math.log` and division. |
| 9 | Memory-zero clearing intervention | **NO** | No memory to clear; no KV store, no replay buffer, no hidden state reset. |
| 10 | Full vs Zero differ ONLY by intervention | **NO** | Only one branch exists (theoretical); no paired empirical contrast. |

### 4.3 Capacity Cliff ≠ Executed Intervention

The statement `task_bits > recurrent_float_bits` at line 54 is a **preregistered rationale**, not an experimental result. When `capacity_cliff_active=True`, the harness assigns `mz_acc = 1/17 ≈ 0.0588` by formula. This is the **theoretical chance floor**, not a measured failure mode. No NN was run at d_hidden=8 or d_hidden=16 to confirm that performance actually collapses.

### 4.4 C3 Verdict

**THEOREM:** C3 requires demonstrating that external memory is causally necessary when recurrent capacity is insufficient.  
**SOURCE-CODE FACT:** The harness computes theoretical capacity ratios and assigns formula-based accuracy ceilings.  
**EXECUTED MEASUREMENT:** None.  
**INFERENCE:** C3 is entirely unimplemented as an empirical experiment.  
**UNVERIFIED CLAIM:** Any claim that "Memory-Zero fails at d_hidden≤16" is a theoretical prediction, not a measurement.

---

## 5. TEST SUITE AUDIT

### 5.1 Would Tests Catch Removed Training?

| Hypothetical Defect | Test Catches It? | Reason |
| :--- | :--- | :--- |
| C2 training removed | **NO** | `test_c2_3arm_exposure_control` never invokes training or `evaluate_c2_exposure_arms`. |
| C2 optimizer.step() removed | **NO** | No optimizer exists in harness. |
| C2 NLL replaced with 0.0 | **NO** | Already 0.0; test doesn't check NLL values. |
| C3 Memory-Zero clearing removed | **NO** | No clearing operation exists. |
| C3 results replaced with 1/17 | **NO** | Already 1/17 by formula; no empirical assertion. |
| d_hidden ignored | **NO** | d_hidden is iterated but never fed to a model. |
| N_K=8 substituted for N_K=128 | **PARTIAL** | `test_c3_capacity_cliff` asserts `num_keys==128` on corpus, but doesn't verify harness uses it. |

### 5.2 Missing Guards

1. **No integration test** calls `evaluate_c2_exposure_arms` or `evaluate_capacity_matrix` and asserts on returned NLL/accuracy values.
2. **No test** verifies that a neural network was instantiated or trained.
3. **No test** asserts that memory-zero intervention produces different outputs than full-memory.
4. **No negative control** exists that would fail if the harness were replaced with stubs.

---

## 6. S12 AUDIT

### 6.1 Independent Reproduction Attempt

S12 refers to the capacity-scaling matrix evaluation. Since the harness is formula-only, "reproduction" means re-evaluating the same formulas:

| N_K | d_hidden | task_bits | recurrent_bits | cliff? | mz_acc (formula) | mz_nll (formula) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 8 | 8 | 32.77 | 256 | NO | 1.0000 | 0.0000 |
| 8 | 16 | 32.77 | 512 | NO | 1.0000 | 0.0000 |
| 8 | 128 | 32.77 | 4096 | NO | 1.0000 | 0.0000 |
| 128 | 8 | 523.20 | 256 | YES | 0.0588 | 2.8332 |
| 128 | 16 | 523.20 | 512 | YES | 0.0588 | 2.8332 |
| 128 | 128 | 523.20 | 4096 | NO | 1.0000 | 0.0000 |

**max_tracked_keys:** Not applicable; no KV memory is instantiated.

### 6.2 Does Corrected Report Match Execution?

**NO.** There is no execution to match. These values are derived from `math.log(17)` and integer multiplication. They are **THEOREMS**, not measurements. Any report presenting these as "results" misrepresents their epistemic status.

---

## 7. FINAL VERDICT

### **C — INVALID / HARNESS STILL NON-EXECUTING**

The C2 and C3 harnesses are **mathematical specification documents masquerading as experimental code**. They define what *should* be measured but perform no measurement. The test suite validates the benchmark generator (which is correct) but provides zero coverage of the C2/C3 experimental claims. No neural network is instantiated, trained, or evaluated anywhere in the harness.

### Specific Defects (Repairable)

1. **C2 harness must instantiate NN-0**, create three independent model copies with shared initialization, implement actual forward/backward/step loops for each arm, and measure NLL on held-out probes.
2. **C3 harness must instantiate NN-0 at each d_hidden**, run both full-memory and memory-zero conditions with actual KV/replay clearing, and measure accuracy/NLL empirically.
3. **Test suite must include integration tests** that invoke the harness functions and assert that returned metrics are non-trivial (not hardcoded), that parameter deltas are nonzero for online arms, and that memory-zero differs from full-memory.
4. **All hardcoded NLL=0.0000 and acc=1.0000 values must be replaced** with actual model outputs.
5. **Mutation tests should be added** that replace training with no-ops and verify the test suite fails.

### What Is Correct

- Benchmark generator (`affine_msat.py`) is mathematically sound and deterministic.
- Hostile solver ladder (`baselines_affine_msat.py`) is correctly implemented.
- Capacity bit calculations are correct.
- Seed hygiene is intact.
- No protocol surfaces were violated.

### Epistemic Classification Summary

| Claim | Classification |
| :--- | :--- |
| AFFINE-MSAT generator is correct | SOURCE-CODE FACT + EXECUTED MEASUREMENT (prior audits) |
| Task state = 32.77 bits at N_K=8 | THEOREM |
| Task state = 523.20 bits at N_K=128 | THEOREM |
| C2 arms have equal exposure | HARDCODED BOOLEAN (unverified) |
| C2 arm NLL = 0.0000 | HARDCODED CONSTANT (not measured) |
| C3 memory-zero acc = 1/17 at d_hidden≤16 | THEORETICAL FORMULA (not measured) |
| C3 capacity cliff activates at N_K=128, d_hidden≤16 | THEOREM (arithmetic) |
| C2/C3 harnesses execute real experiments | FALSE |

---

*This audit was performed independently by reading source files and git state. No Gemini reports were consulted. No decisive seeds were consumed. No files were modified.*

</content>
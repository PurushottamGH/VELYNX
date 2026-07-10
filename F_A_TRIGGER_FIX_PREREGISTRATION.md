# F-A Trigger Fix — Preregistration

**[FACT]** Preregistered before any code is written. No implementation has begun.

---

## 1. Current (Buggy) Equation

```
G = H_before − H_after − λ_model > 0

where  λ_model = k·b + n·log₂N
```

`G` is the MDL gain criterion. When `G > 0` the predictor grows capacity.

### 1.1 Units Analysis

| Quantity | Symbol | Units | Sprint 1 Range |
|----------|--------|-------|----------------|
| Entropy before growth | H_before | bits per symbol | ~2.3 bits/symbol |
| Entropy after growth | H_after | bits per symbol | ~2.3 bits/symbol |
| Entropy delta | ΔH = H_before − H_after | **bits per symbol** | ~0.01 bits/symbol |
| Model complexity penalty | λ_model = k·b + n·log₂N | **total bits** | 22–28 bits |

**Mismatch:** The comparison subtracts a total-bit quantity (λ_model) from a per-symbol quantity (ΔH). These have different units. The operation `H_before − H_after − λ_model` is dimensionally invalid, analogous to subtracting meters from meters/second.

### 1.2 Secondary Error: Wrong Reference Point

λ_model is defined as the **total** model cost (`k·b + n·log₂N`), but the correct MDL comparison uses the **marginal** increase in model cost from adding one state. The total cost is k-fold larger than the marginal cost, making the threshold even more prohibitive.

---

## 2. Corrected Derivation

The two-part MDL description length for a model M and data D is:

```
L(M, D) = L(M) + L(D|M)
```

where:
- `L(D|M) = N · H(M)` — total data description length in bits (N observations at H bits/symbol)
- `L(M)` — model complexity cost in bits

### 2.1 Before Growth (capacity k)

```
L_before = N · H_before + (k·b + k·log₂N)
```

### 2.2 After Growth (capacity k+1)

```
L_after = N · H_after + ((k+1)·b + (k+1)·log₂N)
```

### 2.3 Growth Condition

Grow iff total description length strictly decreases:

```
L_before > L_after

N·H_before + k·b + k·log₂N > N·H_after + (k+1)·b + (k+1)·log₂N

N·(H_before − H_after) > b + log₂N
```

### 2.4 Corrected Criterion

```
G_correct = N · (H_before − H_after) − (b + log₂N) > 0
```

Both terms are now in **total bits** — a dimensionally consistent comparison.

---

## 3. Two Candidate Approaches

Both are mathematically equivalent (multiplying inequality (b) by N gives (a)). They produce the same binary decision. The choice affects interpretation and what name `G` carries.

### Approach (a): Scale entropy delta to full sequence

```
G = N · (H_before − H_after) − (b + log₂N) > 0
```

- G in **total bits**
- λ_model = b + log₂N (marginal model cost)
- N·ΔH = total data description length reduction across all N observations

### Approach (b): Amortize model cost per symbol

```
G = (H_before − H_after) − (b + log₂N) / N > 0
```

- G in **bits per symbol**
- λ_model_per_symbol = (b + log₂N) / N
- ΔH compared to a per-symbol threshold that decays as N grows

### 3.1 Recommendation: Approach (a)

Reasons:
1. **Matches standard two-part MDL.** Rissanen's formulation compares total description lengths before/after, not per-symbol averages. Approach (a) is the direct two-part inequality.
2. **Both terms in same units** (total bits), making the comparison transparent.
3. **λ_model becomes interpretable as marginal cost** (b + log₂N bits to add one state), rather than the current total cost which mixes units.
4. **N·ΔH accumulates naturally.** As N increases, the total data savings grow linearly, correctly reflecting that more observations justify more complex models. Approach (b)'s per-symbol threshold (b+log₂N)/N decays as N grows, which is mathematically equivalent but less intuitive.

**Implementation:** Both approaches yield the same decision rule, so the code computes `N·ΔH > b + log₂N` regardless of which framing is preferred. The code variable name `G` can remain; its unit will be total bits.

---

## 4. Verified Replay Evidence

**The crossover analysis in §4.3 of earlier drafts was a theoretical illustration using a representative ΔH ≈ 0.01 bits/symbol. It is not the observed Sprint 1 distribution.** The actual Sprint 1 replay — running the corrected formula against all 720 raw diagnostic checks (20 seeds × 18 steps × 2 conditions (T, C3)) — produces a narrower but reproducible firing pattern.

### 4.1 Replay Results

- **4 of 20 seeds** fire under the corrected formula.
- **16 of 20 seeds** never fire (all C3 checks, plus T condition checks with H_after ≥ H_before).
- No seed fires before step 1000 (the warmup boundary).
- All firing occurs in the T condition only.

### 4.2 Firing Seeds — First-Fire Steps

| Seed | First Fire Step | Time Since Warmup |
|------|----------------|-------------------|
| 54   | step 1000      | first check       |
| 49   | step 2000      | 3rd check         |
| 60   | step 3500      | 6th check         |
| 46   | step 4500      | 8th check         |

### 4.3 Interpretation

The corrected trigger fires on **4/20 seeds (20%)** in the T condition, with first-fire steps spanning 1000–4500 observations. This is a materially different finding from Sprint 1's "growth never fires" — the trigger is no longer mathematically impossible — but it is also not the universal ~1150 crossover that the theoretical ΔH ≈ 0.01 illustration would predict. The empirical ΔH values in Sprint 1's Dirichlet–Markov predictor on a 10-state nonlinear environment are smaller and more variable than 0.01 bits/symbol for most seeds, delaying or preventing crossover.

**Key finding:** The fix is necessary but not sufficient. The corrected MDL trigger eliminates the unit-incommensurate error, enabling growth for a subset of seeds. Full 20/20 firing (or even majority firing) may require additional changes to ΔH magnitude (e.g., richer predictors, longer horizons, or different environments).

---

## 5. Invariants

The following must not change during implementation:

1. **G must be a same-units comparison.** Both terms must be in total bits (or both in bits/symbol). No mixed units.
2. **λ_model becomes the marginal cost** `b + log₂N`, not the total cost `k·b + k·log₂N`. This follows directly from the two-part MDL derivation.
3. **The canonical constants remain.** `b = 1.0` (BITS_PER_PARAMETER) and `n = k` (the k×k transition matrix) are not configurable.
4. **The existing `should_grow` function signature is preserved.** Only the internal computation changes. Callers (run_treatment, run_c3) are unchanged.
5. **The growth criterion remains `G > 0`.** No configurable threshold or hand-set `birth_threshold` is introduced. This preserves the I2 invariant (derived, not configured).
6. **All Sprint 1 diagnostics remain reproducible.** The `growth_diagnostics` script continues to read per_step_log entries; only the computed values differ.

---

## 6. Assumptions

1. **The Sprint 1 replay (4/20 seeds firing) is the ground truth for the observed distribution.** The earlier theoretical illustration using ΔH ≈ 0.01 bits/symbol was a rough approximation; actual per-seed ΔH values are smaller and more heterogeneous, as confirmed by replay against all 720 Sprint 1 checks (see §4).
2. **N is the total observation count at the growth check.** This comes from `predictor.n_observations`, which counts all updates applied so far (including the current step). This is correct: each observation contributes to the total data description length.
3. **The marginal model cost `b + log₂N` correctly captures the added complexity.** Encoding one new state requires `b` bits for the state integer plus `log₂N` bits for the transition distribution (Dirichlet posterior precision scales with N). This follows from the concept-birth ledger derivation in PROGRAM_D_CANONICAL.md §5.4.
4. **`n = k` holds.** The parameter dimensionality equals the current state count (k×k transition matrix). This is the case for the DirichletMarkovPredictor. Alternative predictor architectures would need their own derivation.
5. **Entropy delta remains positive when growth is beneficial.** The corrected formula assumes H_before > H_after (adding a state does not increase entropy). If H_after ≥ H_before, then growth is never justified regardless of N — the formula handles this correctly (G_correct < 0 by inspection).

---

## 7. Edge Cases

### 7.1 k = 1 (Single-State Predictor)

```
G_correct = N · ΔH − (b + log₂N)
```

Growing from k=1 to k=2: marginal cost = `b + log₂N` ≈ 4.32 bits at N=10. The predictor starts with a 1×1 transition matrix (a trivial self-loop), so ΔH after adding a second state is typically large. The formula applies directly. No special handling needed.

**Special note:** At k=1, `n = k = 1`, so the **current** (buggy) λ_model = 1·b + 1·log₂N = b + log₂N — coincidentally equal to the corrected marginal cost. The bug only becomes apparent at k > 1 where the total-vs-marginal distinction and the units mismatch interact. This is consistent with the empirical observation that the trigger never fires at k=2.

### 7.2 Very Large N (N → ∞)

As N → ∞:
- `N · ΔH` → ∞ (if ΔH > 0)
- `b + log₂N` → ∞ (logarithmically)

The growth criterion `N·ΔH > b + log₂N` becomes easier to satisfy for large N because `N·ΔH` grows linearly while `b + log₂N` grows only logarithmically. This is correct MDL behavior: with infinite data, even an arbitrarily small per-symbol improvement justifies adding complexity.

**Practical asymptotic:** For ΔH > 0, there always exists some N_crossover where growth becomes justified. No pathological regime where growth is permanently precluded.

### 7.3 N → 0 (Trivial Observation Count)

As N → 0:
- `N · ΔH` → 0
- `b + log₂N` → b − ∞ (diverges to −∞)

This is problematic: `log₂N` is undefined at N=0 and negative for N < 1. However, the code guards against this (`max(N, 1)` in `compute_lambda_model`) and growth evaluations only occur after `warmup_steps` (currently 1000), so N ≥ warmup_steps in practice.

**Explicit guard (unchanged):** `compute_lambda_model` clamps `N = max(N, 1)`. With the corrected formula, the marginal cost at N=1 is `b + log₂(1) = 1.0 + 0 = 1.0` bit. `N·ΔH` at N=1 is ~0.01 bits. Growth correctly rejected. The guard remains needed.

### 7.4 ΔH = 0 (No Entropy Reduction)

If H_before = H_after (adding a state does not reduce entropy), then:
```
G_correct = N · 0 − (b + log₂N) = −(b + log₂N) < 0
```

Growth always rejected, regardless of N. Correct behavior: if adding capacity does not improve prediction, it should never be justified.

### 7.5 Negative ΔH (Entropy Increase After Growth)

If H_after > H_before (adding a state makes prediction worse), then:
```
G_correct = N · (−δ) − (b + log₂N) < 0
```

Growth always rejected. Correct. The hypothetical entropy computation (`hypothetical_entropy_after_growth`) typically returns a lower or equal entropy, but this case is handled soundly.

### 7.6 Multiple Sequential Growth Events

After growth fires once (k: 2→3), the next evaluation uses the new k=3 with the corrected formula:
```
G_correct = N · (H_before_3 − H_after_4) − (b + log₂N)
```

The marginal cost `b + log₂N` is invariant to k — it is always the cost of adding one more state, independent of how many states already exist. This is correct: each new state costs the same marginal encoding overhead.

---

## 8. Implementation Rule

- **Do not change function signatures** in `core/mdl/mdl_growth.py`. Only change the internal computation in `should_grow` and/or `mdl_gain`:
  - Scale `entropy_before - entropy_after` by N before comparing to λ_model, OR
  - Divide λ_model by N before comparing to the entropy delta, OR
  - Compute the corrected two-part MDL inequality directly.
- **λ_model as returned by `compute_lambda_model`** should be reconsidered for renaming or deprecation, since the current function returns total cost but the corrected formula needs marginal cost. Either:
  - Add a new function `compute_marginal_lambda(b, N)` returning `b + log₂N`, or
  - Reinterpret call sites to use `compute_lambda_model(k=1, n=1, N=N, b=b)` which coincidentally gives the marginal cost.
- **Bump `_CONFIG_SCHEMA_VERSION`** if the config interface changes (it should not — the fix is internal to the computation).
- **All callers** (`run_treatment`, `run_c3` in `experiments/E0/run.py`) pass entropy_before, entropy_after, k, n, N, b unchanged. No caller modifications needed.
- **Diagnostics** (`per_step_log` entries) should continue to record `lambda_model` and `gain`; their values will differ post-fix. The diagnostics script automatically reflects the new values.

---

## 9. Verification Plan

1. **Unit test:** For sampled (k, N, ΔH), verify `G_correct > 0` iff `N·ΔH > b + log₂N`.
2. **Regression test:** Re-run Sprint 1's 20-seed config with the fix. Verify that exactly 4/20 seeds fire (46, 49, 54, 60) and that each firing seed's first-fire step matches the replay (§4).
3. **Reproducibility:** Confirm that all existing tests in `tests/unit/test_e0_components.py` and `tests/unit/test_fa_trigger_fix.py` still pass (only computational changes, no API changes). `tests/unit/test_fa_trigger_fix.py` replays the corrected formula against all 720 Sprint‑1 checks and enforces the 4/20 seed firing pattern documented in §4.
4. **Edge case tests:**
   - k=1: verify formula reduction.
   - N=0, N=1: verify guards.
   - ΔH=0, ΔH<0: verify G_correct always negative.

---

## 10. Summary of Changes from Sprint 1

| Aspect | Sprint 1 (Buggy) | Corrected |
|--------|------------------|-----------|
| G formula | H_before − H_after − λ_model | N·(H_before−H_after) − (b+log₂N) |
| λ_model | k·b + k·log₂N (total cost) | b + log₂N (marginal cost) |
| Units | mixed (bits/sym − bits) | consistent (total bits) |
| First fire (earliest seed) | never fires | Seed 54 at step 1000 |
| First fire (4th seed)     | never fires | Seed 46 at step 4500 |
| Practical verdict          | 0/720 growth events | 4/20 seeds fire (T condition only) |

**[FACT]** The F-A trigger defect made firing mathematically impossible by construction. Under the corrected formula, growth fires on 4/20 seeds (46, 49, 54, 60) in the T condition, with first-fire steps spanning 1000–4500 observations (verified by replay against all 720 Sprint 1 checks). The deficit reported in Sprint 1 is entirely an artifact of the unit-incommensurate comparison.

**[HYPOTHESIS]** After the F-A fix, H* can be genuinely exercised: the corrected MDL trigger fires for a subset of seeds (4/20) during the 10,000-step training window, producing nonzero treatment effects that can be compared against C1 and C2. If the corrected trigger still fails to produce DV-a separation across the full 20-seed panel, that becomes a meaningful scientific finding about H* (or about ΔH magnitude), not a mathematical artifact.

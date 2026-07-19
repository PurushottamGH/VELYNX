# Program D — Mathematical Provenance

## Purpose
Trace every mathematical formula and quantitative relationship back to its definition in the source code.

---

## 1. FREE ENERGY PRINCIPLE

### 1.1 Cognitive Energy (E)
```
E = λ·H + μ·S + ν·A
```
**Location**: `validation/metrics.py:cognitive_energy()`, `decision_policy.py:_energy()`
**Coefficients**: λ=1.0, μ=2.0, ν=0.5
**Defined in**: `generate_graph.py` as Law L2 (FreeEnergyProxy)

### 1.2 Entropy — Transition Entropy (H)
```
H = -Σ_i π_i · Σ_j P_{ij} · log₂(P_{ij})
```
Where π is the stationary distribution of the Markov chain, P_{ij} are transition probabilities.
**Location**: `validation/metrics.py:transition_entropy()`
**Defined in**: `generate_graph.py` as Variable V1 (SurpriseBits)

### 1.3 Surprise — Prediction Error (S)
```
S = ||predicted - observed||₂
```
Euclidean distance between predicted vector and observed vector.
**Location**: `validation/metrics.py:surprise()`
**Alternate**: `validation/shared_metrics_v1.py:compute_S_surprise()`

### 1.4 Active Load (A)
```
A = n_clusters + n_anomaly_vectors
```
**Location**: `validation/metrics.py:active_load()`
**Components**:
- `anomaly_spatial_volume()` — convex hull or count of anomaly points
- Cluster count from VectorPredictionCore

---

## 2. CONCEPT BIRTH — MDL ENTROPY LEDGER

### 2.1 Information Gain (G)
```
G = (E/T) · H_within - λ_model
```
Where:
- E = exception mass (total predictive weight of exceptions)
- T = observation horizon (total events)
- H_within = internal entropy of proposed concept (bits)
- λ_model = model cost (bits to encode the concept rule + membership overhead)

**Location**: `concept_birth.py:evaluate_concept_birth()`
**Decision**: Birth if `G > threshold_bits` (default 0.5 bits)

### 2.2 Model Cost
```
λ_model = k · b  +  n · log₂(N)
```
Where:
- k = members in concept
- b = bits per symbol (default 4.0)
- n = number of predicates
- N = vocabulary size

**Location**: `concept_birth.py:evaluate_concept_birth()` (line ~240)

---

## 3. PREDICTIVE PROCESSING

### 3.1 Predictive Core — Predicted Activation
```
p(tgt) = Σ_i a(src_i) · E_eff(i) · c_rule(i)
E_eff = E · exp(-decay · age)
```
Where:
- a(src) = source activation [0, 1]
- E = rule effect weight [-1, 1]
- c_rule = rule confidence [0, 1]
- decay = temporal decay rate (default 0.001)

**Location**: `predictive_core.py:predict_next_state()`

### 3.2 Rule Update (Learning)
```
E_new = E_old - lr · error · c_obs · c_rule
error = predicted - observed
```
**Location**: `predictive_core.py:observe_and_update()`

### 3.3 Baseline Update
```
b_new = b_old + (observed - b_old) · br · c_state
```
**Location**: `predictive_core.py:observe_and_update()`

---

## 4. INERTIA LEARNING LAW (C6)

### 4.1 Belief Stability
```
stability = log(1 + support_count) / log(10)
```
**Location**: `cognitive_core.py:_stability()`
**Defined in**: `generate_graph.py` as Law L6

### 4.2 Fracture Ratio
```
fracture_ratio = contradiction_count / max(support_count, 1)
```
**Location**: `cognitive_core.py:Belief.fracture_ratio` property

### 4.3 KL Divergence
```
KL(P||Q) = Σ_i P(i) · log₂(P(i)/Q(i))
```
**Location**: `cognitive_core.py:_kl_divergence()`

---

## 5. CPI — Cognitive Progress Index

### 5.1 Composite CPI
```
CPI = 0.4 · accuracy  +  0.3 · decay  +  0.2 · compression  +  0.1 · resolution
```
Where:
- accuracy = trend over last N samples
- decay = surprise decay rate
- compression = (entropy_after / entropy_before)
- resolution = contradictions resolved / total

**Location**: `cognitive_telemetry.py:CognitiveProgressIndex.cpi`

---

## 6. REASONING ENGINE — DEDUCTIVE INFERENCE

### 6.1 Transitive Closure
```
(A pred B) ∧ (B pred C)  ⊢  (A pred C)
confidence = c_AB · c_BC · 0.9  (decay factor)
```
**Location**: `reasoning_engine.py:_deduce()`

### 6.2 Speculative Type-Lifting (hot states only)
```
(A causes B) ∧ (B is_a C) ⊢ (A causes C)
confidence = c_AB · c_BC · 0.9 · 0.9
```
**Location**: `reasoning_engine.py:_deduce()` (lines 1047-1076)

---

## 7. CONTRADICTION RESOLUTION

### 7.1 Winner Determination
```
winner = argmax_f confidence(f)
margin = winner.confidence - runner_up.confidence
```
**Resolution**:
- If margin ≥ policy_margin → decisive win
- If margin == 0 → tie (lexicographic tiebreak)
- If margin < policy_margin → narrow (keep both)

**Location**: `reasoning_engine.py:_resolve_contradictions()`

---

## Dependencies
- All formulas trace to `generate_graph.py` Law/Variable definitions
- CPI weights (0.4, 0.3, 0.2, 0.1) are hardcoded in `cognitive_telemetry.py`
- Free-energy coefficients (λ, μ, ν) are duplicated in `decision_policy.py` and `validation/metrics.py`

## Experiments Affected
- All benchmark experiments validate these formulas
- Formula changes affect all downstream metrics

## Removal Risk
- N/A — formulas are not removed, only potentially refactored

## Regression Tests
- `test_shared_metrics_v1.py` validates S, R, H, A metrics
- `validation/metrics.py` tests for entropy, surprise, active load
- `concept_birth.py` demo validates MDL ledger

## Confidence
- 0.99 for Free Energy formulas (verified against source)
- 0.95 for Concept Birth MDL (verified against code + test demo)
- 0.90 for CPI composition (weights are heuristic)

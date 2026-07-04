# Program C — Complete Mathematical Ontology

Extracted from ~6,500 lines of the VELYNX symbolic-AGI cognitive stack (C1–C8).

---

## 1. VARIABLES — Every Named Mathematical Quantity

### 1.1 Symbolic Domain (cognitive_core.py)

| Variable | Symbol | Type | Domain | Defined At |
|---|---|---|---|---|
| Context | `c` | `Tuple[Symbol, ...]` | order-k suffix of symbol stream | `cognitive_core.py:118` |
| Symbol | `s` | `str` | vocabulary ∪ {NOVEL, BOS} | `cognitive_core.py:117` |
| Dirichlet concentration | `α` (alpha) | `float` | `(0, ∞)`, default 0.5 | `cognitive_core.py:421` |
| Context-specific successor count | `n(c, s)` | `float` (Counter value) | `[0, ∞)` | `cognitive_core.py:426` |
| Total mass in context | `N(c)` | `float` | `[0, ∞)` | `cognitive_core.py:457` |
| Support size | `\|support\|` | `int` | `[1, \|vocab\|+1]` | `cognitive_core.py:448-449` |
| Predictive probability | `P(s\|c)` | `float` | `(0, 1]` | `cognitive_core.py:414` |
| Shannon surprisal | `I(s)` | `float` | `[0, ∞)` bits | `cognitive_core.py:53` |
| Attention weight | `a(s)` | `float` | `[0, 1]` | `cognitive_core.py:54` |
| Prediction entropy | `H(p)` | `float` | `[0, ∞)` bits | `cognitive_core.py:179` |
| Novelty mass | `m_novel` | `float` | `(0, 1)` | `cognitive_core.py:181` |
| Predicted support | `supp_pred` | `float` | `[0, ∞)` | `cognitive_core.py:185` |
| Rule confidence | `conf` | `float` | `[0, 1]` | `cognitive_core.py:227` |
| Rule support (raw) | `support_count` | `int` | `[0, ∞)` | `cognitive_core.py:229` |
| Contradiction count | `contradiction_count` | `int` | `[0, ∞)` | `cognitive_core.py:231` |
| Stability | `stb` | `float` | `[0, 1)` | `cognitive_core.py:237` |
| Fracture ratio | `φ` (phi) | `float` | `[0, ∞)` | `cognitive_core.py:249`
| Prediction error (surprisal) | `ε` (epsilon) | `float` | `[0, ∞)` bits | `cognitive_core.py:314` |
| Confidence delta (KL) | `δ` (delta) | `float` | `[0, ∞)` bits | `cognitive_core.py:320` |
| Effective learning rate | `η_eff` (eta) | `float` | `[0, base_rate]` | `cognitive_core.py:777` |
| Base learning rate | `η_base` | `float` | default 0.20 | `cognitive_core.py:793` |
| Stability half-maturity | `H_m` | `float` | 4.0 (dimensionless) | `cognitive_core.py:678` |
| Fracture threshold | `τ_frac` (tau) | `float` | 0.85 | `cognitive_core.py:682` |
| Bootstrap confidence | `conf_0` | `float` | 0.50 | `cognitive_core.py:794` |
| Epsilon floor | `ε_floor` | `float` | 0.02 | `cognitive_core.py:797` |

### 1.2 Concept Birth Domain (concept_birth.py)

| Variable | Symbol | Type | Domain | Defined At |
|---|---|---|---|---|
| Total events in context | `T` | `int` | `[1, ∞)` | `concept_birth.py:28` |
| Rule confirmations | `R` | `int` | `[0, T]` | `concept_birth.py:28` |
| Exception counts | `{e_1,...,e_N}` | `int[]` | `[0, T]` | `concept_birth.py:29` |
| Total exception mass | `E` | `float` | `[0, T]` | `concept_birth.py:29` |
| Exception frequency | `f_i = e_i/T` | `float` | `[0, 1]` | `concept_birth.py:261` |
| Rule mass | `R/T` | `float` | `[0, 1]` | `concept_birth.py:358` |
| Concept mass | `E/T` | `float` | `[0, 1]` | `concept_birth.py:357` |
| Within-concept entropy | `H_within` | `float` | `[0, log₂N]` bits | `concept_birth.py:45` |
| Before-concept entropy | `H_before` | `float` | `[0, ∞)` bits | `concept_birth.py:361` |
| Coarse entropy | `H_coarse` | `float` | `[0, 1]` bits | `concept_birth.py:363` |
| After-concept entropy | `H_after` | `float` | `[0, ∞)` bits | `concept_birth.py:372` |
| Model cost | `λ_model` | `float` | `[0, ∞)` bits | `concept_birth.py:59` |
| Definition bits | `λ_def` | `float` | `log₂(N+1)` bits by default | `concept_birth.py:368` |
| Observation horizon | `T_obs` | `float` | `[1, ∞)` | `concept_birth.py:269` |
| Compression gain | `G` | `float` | `(-∞, ∞)` bits | `concept_birth.py:50` |
| Birth threshold | `θ_birth` (theta) | `float` | 0.5 bits | `concept_birth.py:123` |

### 1.3 Continuous Vector Domain (vector_prediction_core.py, environment.py, latent_cause_engine.py)

| Variable | Symbol | Type | Domain | Defined At |
|---|---|---|---|---|
| Sensory vector | `v` | `list[float]` | `[0, 1]^D` | `environment.py:54` |
| Hidden state | `h` | `HiddenState` | `[0, 1]³` | `environment.py:61` |
| Euclidean distance | `d(v₁, v₂)` | `float` | `[0, √D]` | `vector_prediction_core.py:22` |
| Centroid | `μ_k` (mu) | `list[float]` | `[0, 1]^D` | `vector_prediction_core.py:101` |
| Cluster count | `n_k` | `int` | `[1, max_clusters]` | `vector_prediction_core.py:102` |
| Proximity threshold | `θ_prox` | `float` | 0.25 by default | `vector_prediction_core.py:169` |
| Cluster count budget | `K_max` | `int` | 50 by default | `vector_prediction_core.py:170` |
| Prediction error (vector) | `S` | `float` | `[0, √D]` | `vector_prediction_core.py:591` |
| Adaptive threshold | `θ_adapt` | `float` | `[0.15, ∞)` | `vector_prediction_core.py:566` |
| Surprise rate | `ρ` (rho) | `float` | `[0, 1]` | `vector_prediction_core.py:602` |
| Markov transition count | `T(i→j)` | `int` | `[0, ∞)` | `vector_prediction_core.py:632` |
| Attention weight | `w_d` | `float` | `[0, focus_mult]` | `vector_prediction_core.py:828` |
| Focus multiplier | `f_mult` | `float` | 10.0 by default | `vector_prediction_core.py:727` |
| Suppress floor | `sf` | `float` | 0.05 by default | `vector_prediction_core.py:728` |
| Latent variable arity | `k` | `int` | `[1, D]` | `latent_cause_engine.py:87` |
| Prediction gain | `PG` | `float` | `[0, 1]` | `latent_cause_engine.py:104` |
| Compression gain (MDL) | `CG` | `float` | `[0, 1]` | `latent_cause_engine.py:105` |
| Stability (tightness) | `ST` | `float` | `[0, 1]` | `latent_cause_engine.py:106` |
| Combined score | `Score` | `float` | `[0, α+β+γ]` | `latent_cause_engine.py:23` |
| Coverage | `cov` | `float` | `[0, 1]` | `latent_cause_engine.py:299` |
| False positive rate | `FPR` | `float` | `[0, 1]` | `latent_cause_engine.py:301` |
| Bits per value | `b` | `int` | 8 by default | `latent_cause_engine.py:157` |

### 1.4 Cognitive Telemetry / CPI Domain (cognitive_telemetry.py, validation/metrics.py)

| Variable | Symbol | Type | Domain | Defined At |
|---|---|---|---|---|
| Surprise ceiling | `S_max` | `float` | 5.0 bits | `cognitive_telemetry.py:94` |
| EWMA accuracy | `acc` | `float` | `[0, 1]` | `cognitive_telemetry.py:375` |
| EWMA surprise | `μ_surp` | `float` | `[0, ∞)` bits | `cognitive_telemetry.py:377` |
| Decay score | `dec` | `float` | `[0, 1]` | `cognitive_telemetry.py:437` |
| Compression ratio | `CR` | `float` | `[1, ∞)` | `cognitive_telemetry.py:416` |
| Contradictions resolved | `C_res` | `int` | `[0, ∞)` | `cognitive_telemetry.py:315` |
| Accuracy trend | `A_t` | `float` | `[0, 1]` | `cognitive_telemetry.py:210` |
| Surprise decay | `D_t` | `float` | `[0, 1]` | `cognitive_telemetry.py:211` |
| CPI composite | `CPI` | `float` | `[0, 1]` | `cognitive_telemetry.py:237` |
| EWMA alpha (accuracy) | `α_acc` | `float` | 0.15 | `cognitive_telemetry.py:87` |
| EWMA alpha (surprise) | `α_surp` | `float` | 0.20 | `cognitive_telemetry.py:88` |
| EWMA alpha (decay) | `α_dec` | `float` | 0.10 | `cognitive_telemetry.py:89` |

### 1.5 Free Energy Domain (validation/metrics.py, decision_policy.py)

| Variable | Symbol | Type | Domain | Defined At |
|---|---|---|---|---|
| Transition entropy | `H` | `float` | `[0, log₂K]` bits | `validation/metrics.py:113` |
| Spatial surprise | `S` | `float` | `[0, √D]` | `validation/metrics.py:154` |
| Active load | `A` | `float` | `[0, ∞)` clusters+volume | `validation/metrics.py:189` |
| Anomaly spatial volume | `V_anom` | `float` | `[0, ∞)` | `validation/metrics.py:167` |
| Cognitive energy | `E` | `float` | `[0, ∞)` a.u. | `validation/metrics.py:197` |
| Lambda (H weight) | `λ` (lambda) | `float` | 1.0 | `validation/metrics.py:59` |
| Mu (S weight) | `μ` (mu) | `float` | 2.0 | `validation/metrics.py:60` |
| Nu (A weight) | `ν` (nu) | `float` | 0.5 | `validation/metrics.py:61` |
| Energy exhaustion threshold | `E_exhaust` | `float` | 18.0 a.u. | `validation/metrics.py:72` |
| Entropy high threshold | `H_high` | `float` | 2.0 bits | `validation/metrics.py:67` |
| Surprise high threshold | `S_high` | `float` | 0.50 | `validation/metrics.py:68` |
| Pressure high threshold | `P_high` | `float` | 1.00 | `validation/metrics.py:70` |

### 1.6 Decision Policy Domain (decision_policy.py)

| Variable | Symbol | Type | Domain | Defined At |
|---|---|---|---|---|
| Energy before merge | `E_before` | `float` | `[0, ∞)` | `decision_policy.py:249` |
| Energy after merge | `E_after` | `float` | `[0, ∞)` | `decision_policy.py:250` |
| Delta prediction | `ΔS` | `float` | `(-∞, ∞)` | `decision_policy.py:254` |
| Delta entropy | `ΔH` | `float` | `(-∞, ∞)` bits | `decision_policy.py:255` |
| Delta load | `ΔA` | `float` | `(-∞, ∞)` | `decision_policy.py:256` |
| Delta energy | `ΔE` | `float` | `(-∞, ∞)` a.u. | `decision_policy.py:257` |
| Tolerance | `tol` | `float` | `[0, ∞)`, default 0.0 | `decision_policy.py:186` |

### 1.7 Bayesian Living Edge Domain (living_edges.py)

| Variable | Symbol | Type | Domain | Defined At |
|---|---|---|---|---|
| Beta alpha | `α_w` | `float` | `(0, ∞)`, default 1.0 | `living_edges.py:49` |
| Beta beta | `β_w` | `float` | `(0, ∞)`, default 1.0 | `living_edges.py:50` |
| Asymptotic weight | `w_asym` | `float` | `[0, 1]`, default 0.7 | `living_edges.py:48` |
| Bayesian weight mean | `μ_w` | `float` | `(0, 1)` | `living_edges.py:93` |
| Reinforced count | `n_plus` | `float` | `[0, ∞)` | `living_edges.py:89` |
| Challenged count | `n_minus` | `float` | `[0, ∞)` | `living_edges.py:90` |
| Evidence count | `n_ev` | `float` | `[0, ∞)` | `living_edges.py:91` |
| Challenge rate | `γ` (gamma) | `float` | `[0, 1]` | `living_edges.py:94` |
| Update lambda | `λ_upd` | `float` | 0.15 | `living_edges.py:147` |
| Source quality | `q_src` | `float` | `[0, 1]`, default 0.5 | `living_edges.py:66` |

### 1.8 Memory Scheduling Domain (memory_scheduler.py)

| Variable | Symbol | Type | Domain | Defined At |
|---|---|---|---|---|
| Time interval | `τ_interval` | `int` | 500 ticks | `memory_scheduler.py:43` |
| Enter pressure (high watermark) | `P_enter` | `int` | 20 anomalies | `memory_scheduler.py:44` |
| Exit pressure (low watermark) | `P_exit` | `int` | 10 anomalies | `memory_scheduler.py:45` |
| Cooldown | `τ_cooldown` | `int` | 50 ticks | `memory_scheduler.py:46` |

---

## 2. UNITS

Every numeric quantity in Program C is **dimensionless** or expressed in **information-theoretic units**:

| Unit | Symbol | Applies To | Notes |
|---|---|---|---|
| Bits | `bits` | `I(s)`, `H`, `H_before`, `H_after`, `G`, `H_within`, `λ_model`, `CPI` components | Shannon information. All logarithms are base-2 via `log2` or `log(x)/log(2)`. |
| Bits per tick | `bits/tick` | `λ_model` (amortised) | Definition cost spread over observation horizon |
| Dimensionless | `—` | `P(s\|c)`, `conf`, `stb`, `φ`, `w_asym`, `μ_w`, `Score`, `PG`, `CG`, `ST`, `coverage`, `FPR` | Pure ratios in `[0,1]` |
| Euclidean distance units | `du` | `S`, `d(v₁,v₂)`, `θ_prox`, `θ_adapt` | Square root of sum of squared differences in sensor space. Sensors are unit-normalised to `[0,1]`, so `max(d) = √D`. |
| Clusters | `clusters` | `A`, `cluster_count` | Count of live K-Means centroids |
| Variance units | `var` | `V_anom`, `A` component | Sum of per-dimension variances of anomaly cloud |
| Arbitrary energy units | `a.u.` | `E` | Linear combination: `λ*H(bits) + μ*S(du) + ν*A(clusters+var)`. The units are incommensurate but formally combined. |
| Ticks | `ticks` | `τ_interval`, `τ_cooldown`, `step`, `timestamp` | Discrete logical clock ticks |
| Count | `—` | `support_count`, `contradiction_count`, `n_k`, `n(c,s)`, `T`, `R`, `E` | Pure integer counts of events |

**Critical unit inconsistency:** The cognitive energy `E = λ·H + μ·S + ν·A` mixes bits, Euclidean distances, and cluster+variance counts. The coefficients `(λ,μ,ν) = (1.0, 2.0, 0.5)` are not calibrated to make the sum physically meaningful — they are hand-tuned weighting parameters. This is an acknowledged design choice ("arbitrary energy units").

---

## 3. EQUATIONS — Complete Catalog

### 3.1 Predictive Distribution (Dirichlet-Markov)
```
cognitive_core.py:414, 462

P(s|c) = (n(c, s) + α) / (N(c) + α·|support|)

where:
  n(c, s)  = count of symbol s after context c (precision-weighted or literal)
  N(c)     = Σ_s n(c, s)  = total mass in context c
  α        = Dirichlet concentration parameter (default 0.5)
  |support| = vocabulary size + NOVEL slot
```

### 3.2 Shannon Surprisal (Prediction Error)
```
cognitive_core.py:53, 134

I(s) = -log₂ P(s|c)

Implementation: _safe_log2(x) = ln(x)/ln(2) if x > 0 else 0.0
```

### 3.3 Attention Weight
```
cognitive_core.py:54

a(s) = 1 - P(s|c)    ∈ [0, 1]
```

### 3.4 KL Divergence (Belief Shift)
```
cognitive_core.py:137-154

D_KL(P || Q) = Σ_s p(s) · log₂(p(s)/q(s))

for s where p(s) > 0, q(s) > 0. Convention: 0·log(0/q) = 0.
Returns max(total, 0.0) to guard against floating-point drift.
```

### 3.5 Log-Linear Stability (C6 Inertia Law)
```
cognitive_core.py:685-698

stability(n) = ln(1 + n) / (ln(1 + n) + ln(1 + H_m))

where:
  n  = support_count
  H_m = STABILITY_HALF_MATURITY = 4.0

Properties:
  stability(0) = 0
  stability(H_m) = 0.5
  limit_{n→∞} stability(n) = 1
```

### 3.6 Effective Learning Rate (Inertia Law)
```
cognitive_core.py:777, 953, 968

η_eff = η_base · (1 - stability)

On confirmation:
  confidence += η_eff · (1.0 - confidence)
On contradiction:
  confidence += η_eff · (0.0 - confidence)
```

### 3.7 Fracture Ratio
```
cognitive_core.py:258, 747

φ = contradiction_count / support_count

φ >= FRACTURE_THRESHOLD (0.85)  triggers belief revision.
Special case: if support_count = 0, φ = 1 if contradictions > 0 else 0.
```

### 3.8 Belief Revision (Fracture)
```
cognitive_core.py:982-1013

After fracture triggered:
  new_consequent = dominant_exception.symbol
  new_support_count = dominant_exception.count
  old_rule demoted to exception with count = old_support_count
  contradiction_count = Σ(exception counts)
  confidence = new_support_count / (new_support_count + contradiction_count)
```

### 3.9 Predictive Distribution (StableBeliefModel)
```
cognitive_core.py:817-848

For belief's consequent:
  dist[consequent] = ε_floor + confidence
Residual distributed across exceptions:
  dist[exception_i] = ε_floor + (1 - confidence) · (exc.count / Σ exc.count)
If no exceptions, residual goes to NOVEL.
Uniform ε_floor over entire support.
Normalised by sum.
```

### 3.10 Concept Birth — Compression Gain
```
concept_birth.py:26-66, 355-398

H_before  = -Σ_{s ∈ {rule} ∪ exceptions} p(s) · log₂ p(s)
           where p(rule) = R/T, p(e_i) = e_i/T

H_coarse  = -(R/T)·log₂(R/T) - (E/T)·log₂(E/T)

H_within  = -Σ_i (e_i/E) · log₂(e_i/E)

λ_model   = log₂(N+1) / T_obs    (amortised definition cost)

H_after   = H_coarse + λ_model

G         = H_before - H_after = (E/T)·H_within - λ_model

Born iff  G > θ_birth  (default 0.5 bits)
```

### 3.11 Euclidean Distance
```
vector_prediction_core.py:22-28

d(a, b) = √( Σ_i (a_i - b_i)² )
```

### 3.12 Online Centroid Update
```
vector_prediction_core.py:105-113

μ_k_new = (μ_k_old · (n-1) + v) / n

where n = count after increment.
```

### 3.13 Weighted Euclidean (Attention)
```
attention_modulator.py:87-103, vector_prediction_core.py:282-289

d_w(a, b) = √( Σ_i w_i · (a_i - b_i)² )

Weight construction:
  w_i = suppress_floor (= 0.05) for all i
  w_{attended} = focus_mult (= 10.0) · cause.importance
```

### 3.14 Adaptive Surprise Threshold
```
vector_prediction_core.py:566-576

θ_adapt = μ + 1.5 · σ

where μ, σ are mean and stdev of recent errors (window=100).
Fallback: 0.15 when < 5 samples.
```

### 3.15 Adaptive Surprise Rate
```
vector_prediction_core.py:602-608

ρ = (count of recent errors > threshold) / len(recent_errors)
```

### 3.16 Prediction Gain (Latent Cause)
```
latent_cause_engine.py:284-304

PG = coverage · (1 - FPR)

coverage = matches_on_quarantine / |quarantine|
FPR      = matches_on_baseline / |baseline|
```

### 3.17 Compression Gain (Latent Cause, MDL)
```
latent_cause_engine.py:306-332

cost_raw = n · D · b
rule_bits = k · (b + log₂(max(D, 2)))
savings = m · k · b - rule_bits - n
CG = max(0, savings) / max(cost_raw, ε)

where:
  n = |quarantine|, D = dimensions, b = bits_per_value
  k = variable.arity (constrained dimensions)
  m = matches on quarantine
```

### 3.18 Stability (Latent Cause, Tightness)
```
latent_cause_engine.py:334-355

For each predicate p:
  tightness_p = max(0, 1 - spread_p / 0.5)
  where spread_p = stdev of matched values along dimension p

ST = mean(tightness_p for all predicates)
```

### 3.19 Combined Latent Cause Score
```
latent_cause_engine.py:23-25, 281

Score = α·PG + β·CG + γ·ST

Default weights: α=0.5, β=0.30, γ=0.20
Promoted iff Score > threshold (default 0.50)
```

### 3.20 EWMA (Cognitive Telemetry)
```
cognitive_telemetry.py:108-110

EWMA(prev, sample, α) = (1 - α)·prev + α·sample

Used for: accuracy, average_surprise, decay_score
```

### 3.21 Linear Slope (OLS)
```
cognitive_telemetry.py:130-143

slope(values) = Σ (i - x̄)(v_i - ȳ) / Σ (i - x̄)²

where x̄ = (n-1)/2, ȳ = Σ values / n
```

### 3.22 Surprise Decay (Recovery Absorbed Fraction)
```
cognitive_telemetry.py:434-438

absorbed = clamp(1 - tail_mean / peak_error)

where tail_mean = mean of decay_window (default 4) errors after spike peak.
```

### 3.23 Compression Component (CPI)
```
cognitive_telemetry.py:224-229

compression_component = 1 - exp(-(CR - 1))
```

### 3.24 Resolution Component (CPI)
```
cognitive_telemetry.py:232-234

resolution_component = 1 - exp(-C_res / 3.0)
```

### 3.25 CPI Composite
```
cognitive_telemetry.py:237-252

CPI = (0.40·A_t + 0.30·D_t + 0.20·compression_component + 0.10·resolution_component) / 1.0
```

### 3.26 Transition Entropy (Markov Chain)
```
validation/metrics.py:113-147

H(next | current) = Σ_{src} p_visit(src) · (-Σ_{dst} p(dst|src) · log₂ p(dst|src))

where:
  p_visit(src) = total_outgoing(src) / Σ total_outgoing(all_src)
  p(dst|src) = count(src→dst) / total_outgoing(src)
```

### 3.27 Anomaly Spatial Volume
```
validation/metrics.py:167-186

V_anom = Σ_{d=1}^{D} Var(anomaly_vectors[d])

where Var(x) = (1/n) Σ (x_i - x̄)²
```

### 3.28 Active Load
```
validation/metrics.py:189-194

A = cluster_count + V_anom
```

### 3.29 Cognitive Energy (Free Energy Proxy)
```
validation/metrics.py:197-206, decision_policy.py:363-365

E = λ·H + μ·S + ν·A

where (λ, μ, ν) = (1.0, 2.0, 0.5) by default.
```

### 3.30 Decision Policy — Free Energy Minimization
```
decision_policy.py:296-322

ΔE = E_before - E_after
Accepted iff ΔE >= -tolerance  (i.e., E_after <= E_before at tol=0)
```

### 3.31 Decision Policy — Pareto Dominance
```
decision_policy.py:324-359

Rejected iff ALL of: ΔS < 0 AND ΔH < 0 AND ΔA < 0 AND ΔE < 0
Accepted otherwise (merge survives unless strictly dominated).
```

### 3.32 Bayesian Edge Weight
```
living_edges.py:87-96

n_plus  = α_w - 1
n_minus = β_w - 1
n_ev    = n_plus + n_minus

μ_w = α_w / (α_w + β_w)

γ = n_minus / n_ev  if n_ev > 0 else 0.0
```

### 3.33 Asymptotic Weight Update
```
living_edges.py:147

Reinforce:
  w_asym_new = w_asym_old + λ_upd · (1.0 - w_asym_old)

Challenge:
  w_asym_new = w_asym_old - λ_upd · w_asym_old
```

### 3.34 Beta Parameter Update
```
living_edges.py:141-142, 219-220

Reinforce:  α_w += q_src
Challenge:  β_w += q_src
```

### 3.35 Confidence Thresholds (Living Edges)
```
living_edges.py:98-116

CERTAIN  : μ_w >= 0.90 AND n_ev >= 20 AND γ <= 0.05
PROBABLE : μ_w >= 0.70 AND n_ev >= 5
CONTESTED: μ_w < 0.40 OR (n_minus >= n_plus AND n_ev > 0)
UNCERTAIN: otherwise
```

### 3.36 Environment Dynamics
```
environment.py:137-157

State transition per tick:
  P(regime persists) = regime.dwell ∈ [0, 1]
  On switch: uniform over other regimes

Continuous variables relax:
  x_new = clamp(x + r·(target - x) + N(0, σ_drift))
  where r = relaxation (0.25), σ_drift = 0.03

Sensor transduction:
  sensor_i = clamp(bias_i + Σ_j w_ij · state_j + N(0, σ_noise))
  where σ_noise = 0.05
```

### 3.37 Replay Engine — Merge
```
replay_engine.py:365-409

merged_centroid_d = (μ_a_d · n_a + μ_b_d · n_b) / (n_a + n_b)
merged_count = n_a + n_b
merged_members = members_a ∪ members_b
```

### 3.38 Memory Scheduler — Hysteresis
```
memory_scheduler.py:146-164

If in_consolidation:
  Stay ON while active_anomalies > P_exit
  Turn OFF when active_anomalies <= P_exit
Else:
  Turn ON when ticks_since_consolidation >= τ_interval
         OR active_anomalies >= P_enter

Cooldown active: _cooldown_remaining > 0 → suppress all triggers
```

### 3.39 Prediction Error (Vector Replay)
```
replay_engine.py:210-264

S = (1/N) Σ_i ||predict(last_nearest(v_{i-1}), engine) - v_i||₂

where predict() uses Markov chain over cluster centroids.
```

### 3.40 Entropy (Vector Replay)
```
replay_engine.py:266-319

H = Σ_{src} (out_total(src) / Σ out_total) · H(src→·)

where H(src→·) = -Σ_{dst} p(dst|src) log₂ p(dst|src)
  computed from read-only nearest-cluster assignment of window.
```

---

## 4. DEPENDENCY GRAPH (Variable → Variables)

```
P(s|c)       ← n(c,s), N(c), α, |support|
I(s)         ← P(s|c)
a(s)         ← P(s|c)
ε            ← I(s)
D_KL(P||Q)   ← p(s), q(s)

stability(n) ← support_count, H_m(stability)
η_eff        ← η_base, stability
confidence   ← η_eff, prior_confidence

H_before     ← R/T, {e_i/T}
H_within     ← {e_i/E}
H_coarse     ← R/T, E/T
λ_model      ← log₂(N+1), T_obs
H_after      ← H_coarse, λ_model
G            ← H_before, H_after (or E/T, H_within, λ_model)

d(a,b)       ← a_i, b_i for all i
μ_k          ← previous μ_k, v, n_k

d_w(a,b)     ← a_i, b_i, w_i for all i
w_i          ← f_mult, sf, cause.importance

θ_adapt      ← μ_recent_errors, σ_recent_errors

PG           ← coverage, FPR
coverage     ← matches_on_quarantine, |quarantine|
FPR          ← matches_on_baseline, |baseline|
CG           ← k, b, D, n, m
ST           ← stdev of matched dimensions
Score        ← PG, CG, ST (weighted)

A_t          ← EWMA of 1 - norm_surprise
decay        ← absorbed fraction of spike peak
CR           ← samples_seen / consolidated_concepts
comp_comp    ← 1 - exp(-(CR-1))
res_comp     ← 1 - exp(-C_res/3)
CPI          ← A_t, decay, comp_comp, res_comp (weighted avg)

H_entropy    ← transition counts {src → {dst: count}}
S_surprise   ← ||predicted_centroid - observed||
V_anom       ← per-dim variance of anomaly vectors
A_load       ← cluster_count + V_anom
E            ← λ·H + μ·S + ν·A

ΔE           ← E_before - E_after

μ_w          ← α_w, β_w
w_asym       ← previous w_asym, λ_upd (reinforce/challenge)
n_plus       ← α_w - 1
n_minus      ← β_w - 1
γ            ← n_minus / n_ev

hidden_state ← target, relaxation, drift, previous state
sensor       ← hidden_state, weights, noise
```

---

## 5. MISSING QUANTITIES

| Missing Quantity | Where Referenced | Impact |
|---|---|---|
| `Vector` type resolution | `cognitive_health.py` re-exports from `validation.metrics` but the type alias creates an ambiguous reference chain | Cosmetic; runtime duck-typed |
| `latent_concepts` generation algorithm details | `cognitive_core.py:574` — `_detect_concepts()` only returns strings, no formal definition of what constitutes a "concept" beyond thresholds | Ontologically weak: concepts are string labels, not formal mathematical objects |
| Ground truth regime alignment score | No formal metric to compare discovered `Latent_Cause` against `Environment.ground_truth()` | Cannot verify whether discovered causes correspond to actual world regimes |
| `policy_weights` usage | `vector_prediction_core.py:186` stores but never reads `policy_weights` in clustering logic | Dead metadata; documented as "pure metadata" |
| `HealthReport` lifecycle | Referenced by `PipelineTick` but the probation pipeline is optional and only partially integrated | No formal guarantee the health monitor chain is closed |
| Curiosity goal satisfaction recall | No formal feedback loop for whether satisfied goals improve prediction | Goal satisfaction is a side effect, not a measured cognitive vital |
| CPI weight justification | `(0.40, 0.30, 0.20, 0.10)` are arbitrary | No sensitivity analysis or derivation |
| Energy coefficient justification | `(λ,μ,ν) = (1.0, 2.0, 0.5)` are hand-tuned | No scaling analysis; units are incommensurate |
| `DEFAULT_AMORTIZATION_HORIZON = 16.0` for concept birth | `concept_birth.py:128` | Fallback value when no event counts available; could distort birth decisions for sparse contexts |

---

## 6. CIRCULAR DEFINITIONS

1. **Stability and Learning Rate.** `stability = f(support_count)`, and `η_eff = η_base·(1 - stability)`. The learning rate update modifies `confidence`, which modifies `InternalModelView.rule_confidence`, but `stability` is only a function of `support_count` (raw count), not of `confidence`. So this is **acyclic** — the support count evolves independently of stability. **Not truly circular,** but the naming (Inertia Law feeding back into belief) could suggest circularity.

2. **Concept Birth and Probation.** `evaluate_concept_birth()` measures `G = (E/T)·H_within - λ_model`. But `H_within` depends on `{e_i/E}` which depends on the exception counts that themselves *originate* from the same belief system. The concept birth decision feeds `ProbationaryConcept` which then monitors future exceptions. If the probation concept's presence changes how exceptions are classified, this creates a feedback loop: **exceptions → concept birth → probation monitoring → exception reclassification → new exceptions**. The probation pipeline code (`cognitive_core.py:1106-1168`) is marked as optional and its integration with `StableBeliefModel` is partial.

3. **Free Energy and Decision Policy.** `E = λ·H + μ·S + ν·A`. The decision policy accepts a merge iff `ΔE ≥ 0`. But the merge changes cluster structure, which changes `A` (cluster count) and `H` (transition matrix) and `S` (prediction error). The merge is evaluated against a *recent window* of vectors, so the measured vitals depend on what vectors are in the window, which itself depends on previous cluster assignments. **This creates a dependency of the evaluation on the very cluster structure being evaluated.** The sandbox approach (deepcopy) mitigates but does not eliminate this: the recent_vectors window was generated under the old clustering, but the sandbox's new clustering would have assigned those vectors differently.

4. **Attention → Cluster Formation → Attention.** `apply_attention()` re-weights the Euclidean metric by `w_i`. The new metric changes which vectors cluster together, which changes which `LatentCause` candidates are generated, which changes what attention is applied. This is a **legitimate feedback loop** (the C7 closed loop), but it can lead to fixation: if attention amplifies dimension `d`, clusters form around `d`, which confirms `d` is important, reinforcing attention on `d`.

---

## 7. HIDDEN ASSUMPTIONS

### 7.1 Information-Theoretic

| Assumption | Location | Consequence |
|---|---|---|
| Symbols are conditionally independent given context | `cognitive_core.py:414` | The Dirichlet-multinomial assumes each observation is independent; sequential dependencies beyond order-k are ignored |
| `0·log(0/q) = 0` convention | `cognitive_core.py:143` | Standard in information theory but silently drops zero-probability outcomes |
| Dirichlet prior is symmetric (same α for all symbols) | `cognitive_core.py:421` | No prior preference for any symbol; assumes all symbols equally likely a priori |
| Surprisal ceiling at 5.0 bits | `cognitive_telemetry.py:94` | Assumes max uncertainty corresponds to ~32 equiprobable symbols; breaks for larger vocabularies |
| `log₂(N+1)` definition cost for concept birth | `concept_birth.py:368` | Assumes each new concept symbol costs the same as naming one member; does not account for compositionality |

### 7.2 Statistical

| Assumption | Location | Consequence |
|---|---|---|
| K-Means assumption: clusters are spherical (Euclidean metric) | `vector_prediction_core.py:22` | Cannot capture correlated or elongated clusters |
| Markov order = 1 for cluster transitions | `vector_prediction_core.py:631` | Assumes next cluster depends only on current cluster, not longer history |
| Gaussian noise model for sensors | `environment.py:232` | Assumes additive Gaussian noise; real sensors have systematic biases, quantization, dropout |
| Gaussian noise model for environment drift | `environment.py:129` | Assumes bounded random walk; real regimes may have trend, seasonality |
| Linear sensor projection | `environment.py:200` | `sensor = bias + Σ w_i·state_i + noise` — assumes linear transduction |

### 7.3 Cognitive Architecture

| Assumption | Location | Consequence |
|---|---|---|
| "Lower is better" for all vitals (H, S, A, E) | `validation/metrics.py` | Assumes a predictable, low-load, low-energy brain is always better. Ignores exploration value of surprise |
| Free energy E = λH + μS + νA is the correct proxy for cognitive health | `validation/metrics.py:197` | No derivation from first principles; three incommensurate quantities summed with arbitrary coefficients |
| Fracture threshold at 0.85 | `cognitive_core.py:682` | Assumes a belief must accumulate contradictions approaching its support before revising. Tuned, not derived |
| Stability half-maturity at 4.0 | `cognitive_core.py:678` | Assumes ~4 confirmations is the "half-life" of belief plasticity. Arbitrary |
| EWMA alphas (0.15, 0.20, 0.10) for CPI | `cognitive_telemetry.py:87-89` | Smoothing factors not derived from data; manually chosen |
| CPI weight vector (0.40, 0.30, 0.20, 0.10) | `cognitive_telemetry.py:246-250` | Accuracy weighted 4× contradictions; no empirical justification |
| Cooldown of 50 ticks after consolidation | `memory_scheduler.py:46` | Prevents oscillation but the constant is arbitrary |
| Pin std max of 0.18, separation min of 0.20 | `latent_cause_engine.py:158-159` | Defines what counts as an "invariant" dimension; sensor-range dependent |

### 7.4 Numerical

| Assumption | Location | Consequence |
|---|---|---|
| Floating-point probability never exactly 0.0 (Dirichlet smoothing) | `cognitive_core.py:410` | Guarantees finite surprisal but may cause underflow for very large vocabularies |
| Normalisation after epsilon floor: `Σ dist = 1.0` | `cognitive_core.py:847-848` | Epsilon floor adds mass uniformly, then re-normalises; this subtly changes the relative probabilities |
| `ε = 1e-9` for division guard | `latent_cause_engine.py:58` | Prevents division by zero in MDL gain calculation |
| Reference spread = 0.5 for tightness | `latent_cause_engine.py:349` | Assumes sensor range is [0, 1]; tightness = 1 - spread/0.5 |
| `attention_focus_mult = 10.0` | `vector_prediction_core.py:727` | Assumes a 10× weight difference is sufficient to dominate clustering |
| `attention_suppress_floor = 0.05` | `vector_prediction_core.py:728` | Non-attended dimensions still have 5% weight to avoid complete blindness |

### 7.5 Ontological

| Assumption | Location | Consequence |
|---|---|---|
| "Concept" = string label returned by `_detect_concepts()` | `cognitive_core.py:579-612` | No formal concept representation; concepts are ephemeral string detections from threshold crossings |
| Two belief substrates (DirichletMarkovModel and StableBeliefModel) are interchangeable | `cognitive_core.py:765-789` | They implement the same `GenerativeModel` Protocol but have fundamentally different dynamics (precision-weighted vs. inertia-law) |
| Belief revision via fracture is sufficient for regime detection | `cognitive_core.py:982-1013` | Assumes regime shifts manifest as one exception overtaking the rule; ignores gradual drifts or multi-factor shifts |
| Curiosity gaps are defined by a static hand-authored ontology | `curiosity.py:115-122` | 6 categories × 2-4 attributes each — extremely sparse coverage of real-world knowledge |

---

## 8. ONTOLOGY SUMMARY

### Layers
```
LAYER 0: Environment  (environment.py)
  → Continuous hidden state [atmosphere, light, moisture]
  → Latent regimes [CALM_DAY, CALM_NIGHT, STORM, FOG]
  → Noisy sensor array (4 entangled linear projections + Gaussian noise)

LAYER 1: Vector Clustering  (vector_prediction_core.py)
  → Online K-Means (Euclidean proximity)
  → Anomaly quarantine
  → Markov-1 cluster transition predictor
  → Euclidean-distance surprisal with adaptive threshold

LAYER 2: Attention Modulation  (attention_modulator.py, latent_cause_engine.py)
  → Axis-aligned predicate discovery (LatentVariable)
  → Three-pressure scoring (PredictionGain, CompressionGain, Stability)
  → Weighted Euclidean metric (top-down attention warp)
  → Quarantine freeze (absorb matched vectors)

LAYER 3: Symbolic Belief  (cognitive_core.py)
  → Dirichlet-Markov (order-k) predictive model
  → StableBeliefModel with inertia law and exception quarantine
  → Shannon surprisal, KL belief shift, attention weight
  → Belief fracture (dominant exception promotion)

LAYER 4: Concept Formation  (concept_birth.py)
  → MDL-based birth decision via entropy reduction
  → Probationary concept pipeline (score, watch, confirm/reject)
  → H_before → H_coarse → H_within → λ_model → G

LAYER 5: Meta-Cognition / Telemetry  (cognitive_telemetry.py)
  → CPI: Accuracy trend, Surprise decay, Compression ratio, Resolution
  → EWMA-based tracking
  → Plateau detection (OLS slope < ε + level > threshold)
  → Bottleneck attribution (per-concept mean surprise)

LAYER 6: Memory Management  (replay_engine.py, decision_policy.py, memory_scheduler.py)
  → Sandbox simulation of cluster merges
  → Free Energy minimization (E = λH + μS + νA)
  → Pareto dominance guard
  → Schmitt-trigger scheduling (hysteresis + time + cooldown)

LAYER 7: Bayesian Knowledge Graph  (living_edges.py)
  → Beta-Bernoulli edge weights
  → Asymptotic decay/enforcement
  → Epistemic status (CERTAIN/PROBABLE/UNCERTAIN/CONTESTED)
  → Immutable evidence audit trail

LAYER 8: Curiosity / Autonomous Learning  (curiosity.py, night_learner.py)
  → Ontology-gap detection → PENDING goals
  → Goal satisfaction via KG triple matching
  → Time-based learning scheduling (night/weekend/background/light)
```

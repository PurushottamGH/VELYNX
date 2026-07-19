# VELYNX Parameter Atlas

> Every tunable scalar, threshold, coefficient, and magic number across the cognitive architecture.
> Generated 2026-07-01 by systematic codebase audit.

---

## Table of Contents

1. [Environment / Sensorium (C7)](#1-environment--sensorium-c7)
2. [Cognitive Core — DirichletMarkovModel (C1–C3)](#2-cognitive-core--dirichletmarkovmodel-c1c3)
3. [Cognitive Core — StableBeliefModel (C6)](#3-cognitive-core--stablebeliefmodel-c6)
4. [Concept Birth (C4)](#4-concept-birth-c4)
5. [Curiosity Engine v1 — Gap Scanner](#5-curiosity-engine-v1--gap-scanner)
6. [Curiosity Engine v2 — Information Gain (C5)](#6-curiosity-engine-v2--information-gain-c5)
7. [Latent Cause Engine (C7)](#7-latent-cause-engine-c7)
8. [Cognitive Telemetry / CPI (C6)](#8-cognitive-telemetry--cpi-c6)
9. [Free-Energy Metrics](#9-free-energy-metrics)
10. [Decision Policy (C8)](#10-decision-policy-c8)
11. [Replay Engine (C8)](#11-replay-engine-c8)
12. [Attention Modulator](#12-attention-modulator)
13. [Velynx Learner](#13-velynx-learner)
14. [Velynx Brain](#14-velynx-brain)
15. [Velynx Self-Coder](#15-velynx-self-coder)
16. [Velynx Memory](#16-velynx-memory)
17. [Living Edges / Bayesian Graph](#17-living-edges--bayesian-graph)
18. [Inference Engine](#18-inference-engine)
19. [Predictive Core (Phase 50)](#19-predictive-core-phase-50)
20. [Night Learner / Scheduling](#20-night-learner--scheduling)
21. [Probationary Concept Pipeline](#21-probationary-concept-pipeline)
22. [Proposed Sensitivity Experiments](#22-proposed-sensitivity-experiments)

---

## 1. Environment / Sensorium (C7)

**File:** `environment.py`

### `Environment.relaxation`
| Field | Value |
|-------|-------|
| **Default** | `0.25` |
| **Valid range** | `[0.0, 1.0]` — 0 = frozen state, 1 = instant teleport to attractor |
| **Used in** | `Environment.__init__` → `Environment.step()` (line 149–153): hidden state relaxes toward attractor each tick |
| **What breaks** | Below ~0.05: state barely moves → near-deterministic stream, trivial to predict. Above ~0.80: state snaps to attractor every tick → no smooth dynamics, no momentum. The brain never learns to handle gradual transitions. |
| **Experimentally justified?** | No. Single hard-coded default. No evidence that 0.25 is the right relaxation/momentum balance. |
| **Sensitivity analysis?** | None found. |
| **Magic number?** | Yes. No named constant, no docstring rationale for 0.25 specifically. |

### `Environment.drift_sigma`
| Field | Value |
|-------|-------|
| **Default** | `0.03` |
| **Valid range** | `[0.0, ~1.0)` — Gaussian std-dev added to each hidden variable per tick |
| **Used in** | `Environment.__init__` → `Environment.step()` (line 151–153): random walk on hidden state |
| **What breaks** | `0.0`: deterministic within-regime (state is frozen at attractor ± relaxation). `> 0.15`: noise dominates → regime structure obliterated, latent cause discovery impossible. |
| **Experimentally justified?** | No. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

### `SensorArray.noise_sigma`
| Field | Value |
|-------|-------|
| **Default** | `0.05` |
| **Valid range** | `[0.0, ~0.50]` — Gaussian noise corrupting each sensor reading |
| **Used in** | `SensorArray.__init__` → `SensorArray.read()` (line 242) |
| **What breaks** | `0.0`: identical hidden state produces identical vectors → brain can memorize. `> 0.30`: signal drowned → no structure recoverable. |
| **Experimentally justified?** | No. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

### `Regime.dwell` (per-regime self-persistence probability)
| Field | Value |
|-------|-------|
| **Default** | `0.90` (CALM_DAY, CALM_NIGHT), `0.80` (STORM), `0.75` (FOG) |
| **Valid range** | `[0.0, 1.0]` |
| **Used in** | `Environment._maybe_switch_regime()` (line 160) |
| **What breaks** | Higher → regimes persist longer → less switching signal; lower → regime flips every few ticks → too chaotic to track. |
| **Experimentally justified?** | No. Chosen to match intuitive "weather persistence" but no ablation. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

### `_Sensor.weights` (4 default sensors)
| Field | Value |
|-------|-------|
| **Default** | `(0.10,0.95,0.05)`, `(0.90,0.05,0.10)`, `(0.05,0.10,0.95)`, `(0.45,0.50,0.30)` |
| **Valid range** | Any non-negative floats. Weights per sensor over (atmosphere, light, moisture). |
| **Used in** | `_Sensors._DEFAULT_SENSORS` (line 216–221) |
| **What breaks** | Changing weights changes which latent dimensions are entangled. Orthogonal weights would make separation trivial; too-entangled weights make discovery impossible. |
| **Experimentally justified?** | Minimal. Chosen to be "mostly" one variable per sensor plus one mixture. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

---

## 2. Cognitive Core — DirichletMarkovModel (C1–C3)

**File:** `cognitive_core.py`

### `order`
| Field | Value |
|-------|-------|
| **Default** | `1` |
| **Valid range** | Integers `≥ 1` (Markov order) |
| **Used in** | `DirichletMarkovModel.__init__` (line 420); context size for prediction |
| **What breaks** | Order 0: no context sensitivity → always predicts global mode. Order > 3: combinatorial explosion of contexts, slow learning, sparse counts. |
| **Experimentally justified?** | No. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

### `alpha` (Dirichlet smoothing)
| Field | Value |
|-------|-------|
| **Default** | `0.5` |
| **Valid range** | `(0.0, ∞)` |
| **Used in** | `DirichletMarkovModel.__init__` (line 421); smoothing for P(s\|c) = (n + α) / (N + α\|S\|) |
| **What breaks** | α → 0: no smoothing → zero-probability for unseen successors → infinite surprisal. α → ∞: uniform distribution → no learning. |
| **Experimentally justified?** | No. 0.5 is a common convention for symmetric Dirichlet but untuned for this domain. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes — though has a mathematical name, the specific value is arbitrary. |

### `crystallize_threshold`
| Field | Value |
|-------|-------|
| **Default** | `0.80` |
| **Valid range** | `(0.5, 1.0]` |
| **Used in** | `DirichletMarkovModel.__init__` (line 422); `_detect_concepts()` (line 609) — a context "crystallizes" when its top successor probability ≥ threshold |
| **What breaks** | Too low (≤0.6): many false concept births from noisy patterns. Too high (≥0.95): almost no concepts ever crystallize. |
| **Experimentally justified?** | No. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

### `crystallize_min_count`
| Field | Value |
|-------|-------|
| **Default** | `3.0` |
| **Valid range** | `(0, ∞)` — minimum (weighted) count needed before crystallization is checked |
| **Used in** | `DirichletMarkovModel.__init__` (line 423); `_detect_concepts()` (line 604) |
| **What breaks** | Too low: single observation crystallizes. Too high: many observations needed even if pattern is strong. |
| **Experimentally justified?** | No. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

### `motif_threshold`
| Field | Value |
|-------|-------|
| **Default** | `3.0` |
| **Valid range** | `(0, ∞)` |
| **Used in** | `DirichletMarkovModel.__init__` (line 424); `_detect_concepts()` (line 601) — a transition is a "motif" when its count ≥ threshold |
| **What breaks** | Too low: noise reported as motif. Too high: real recurring patterns missed. |
| **Experimentally justified?** | No. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

---

## 3. Cognitive Core — StableBeliefModel (C6)

**File:** `cognitive_core.py`

### `base_rate`
| Field | Value |
|-------|-------|
| **Default** | `0.20` |
| **Valid range** | `(0.0, 1.0]` |
| **Used in** | `StableBeliefModel.__init__` (line 793); `assimilate()` (lines 953, 968): `effective_rate = learning_rate * (1 - stability)` |
| **What breaks** | Near 0: beliefs barely update. Near 1: stability has almost no protective effect → catastrophic forgetting returns. |
| **Experimentally justified?** | No. Chosen by author intuition. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

### `bootstrap_confidence`
| Field | Value |
|-------|-------|
| **Default** | `0.50` |
| **Valid range** | `(0.0, 1.0]` |
| **Used in** | `StableBeliefModel.__init__` (line 794); `assimilate()` (line 945): initial confidence when a rule is first formed |
| **What breaks** | Too low: first observation barely believed, second contradicting observation immediately fractures. Too high: first observation treated as near-certain → brittle. |
| **Experimentally justified?** | No. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

### `epsilon` (floor mass)
| Field | Value |
|-------|-------|
| **Default** | `0.02` |
| **Valid range** | `(0.0, ~0.1]` — uniform floor for every symbol so P(s) > 0 always |
| **Used in** | `StableBeliefModel.__init__` (line 797); `_distribution()` (line 829) |
| **What breaks** | 0.0: zero-probability for unseen symbols → infinite surprisal. Too high (>0.1): dilutes actual beliefs. |
| **Experimentally justified?** | No. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

### `STABILITY_HALF_MATURITY`
| Field | Value |
|-------|-------|
| **Default** | `4.0` |
| **Valid range** | `(0, ∞)` |
| **Used in** | Module-level (line 678); `_stability_of()` (line 685–698): `stability = ln(1+n) / (ln(1+n) + ln(1+HALF_MATURITY))` |
| **What breaks** | Smaller: rules become rigid after few confirmations. Larger: rules stay plastic longer. Controls the half-maturity point of the logarithmic stability curve. |
| **Experimentally justified?** | Partially — docstring says "tuned so a rule confirmed a handful of times already resists single anomalies". No published ablation. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

### `FRACTURE_THRESHOLD`
| Field | Value |
|-------|-------|
| **Default** | `0.85` |
| **Valid range** | `(0.0, 1.0]` — fraction of support_count at which contradictions license fracture |
| **Used in** | Module-level (line 682); `Belief.is_fractured` (line 755); `StableBeliefModel._refracture()` (line 972) |
| **What breaks** | At 0.5: rules fracture at parity — every second contradiction triggers revision, too volatile. At 1.0: rules never fracture (contradictions must equal support exactly). |
| **Experimentally justified?** | No. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

### `StableBeliefModel.crystallize_threshold`
| Field | Value |
|-------|-------|
| **Default** | `0.80` |
| **Valid range** | `(0.5, 1.0]` |
| **Used in** | `StableBeliefModel.__init__` (line 798); `_detect_concepts()` (line 1036) |
| **Same comments** as DirichletMarkovModel.crystallize_threshold above. |

### `StableBeliefModel.motif_threshold`
| Field | Value |
|-------|-------|
| **Default** | `3.0` |
| **Valid range** | `(0, ∞)` |
| **Used in** | `StableBeliefModel.__init__` (line 799); `_detect_concepts()` (line 1031) |
| **Same comments** as DirichletMarkovModel.motif_threshold above. |

---

## 4. Concept Birth (C4)

**File:** `concept_birth.py`

### `DEFAULT_BIRTH_THRESHOLD_BITS`
| Field | Value |
|-------|-------|
| **Default** | `0.5` |
| **Valid range** | `[0.0, ∞)` — minimum compression gain in bits |
| **Used in** | `concept_birth.py` line 123; `evaluate_concept_birth()` (line 320) |
| **What breaks** | At 0.0: every abstraction is born (even single-exception concepts with H_within=0 gain=0 pass). At high values (~2.0): almost nothing is born unless exception swarm is large and diverse. |
| **Experimentally justified?** | No. Docstring says "0.5 bits ≈ halving one outcome's uncertainty" — plausible but untuned. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

### `DEFAULT_AMORTIZATION_HORIZON`
| Field | Value |
|-------|-------|
| **Default** | `16.0` |
| **Valid range** | `(0, ∞)` — fallback event count T when raw tallies unavailable |
| **Used in** | `concept_birth.py` line 128; `_observation_horizon()` (line 278) |
| **What breaks** | Too small: concept definition cost inflated → fewer births. Too large: cost negligible → false births. Only matters when `InternalModelView` lacks raw tallies. |
| **Experimentally justified?** | No. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

---

## 5. Curiosity Engine v1 — Gap Scanner

**File:** `velynx/graph/curiosity_engine.py`

### `weight_alpha < 2.0` (medium-priority gap threshold)
| Field | Value |
|-------|-------|
| **Default** | Threshold: `2.0` |
| **Valid range** | `(0, ∞)` |
| **Used in** | SQL query (line 60): `WHERE status = 'active' AND weight_alpha < 2.0` |
| **What breaks** | Too low: few edges qualify as medium-priority gaps. Too high: too many edges flagged. |
| **Experimentally justified?** | No. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

### `< 3 outbound edges` (low-priority gap threshold)
| Field | Value |
|-------|-------|
| **Default** | Threshold: `3` |
| **Used in** | SQL query (line 66): `GROUP BY source HAVING COUNT(target) < 3` |
| **What breaks** | Controls which concepts are considered "poorly connected". |
| **Experimentally justified?** | No. |
| **Magic number?** | Yes. |

### `resonance_scores > 0.3` (curiosity question filter)
| Field | Value |
|-------|-------|
| **Default** | Threshold: `0.3` |
| **Used in** | `select_curiosity_question()` (line 129) |
| **What breaks** | Filters which concepts in the current session are eligible for curiosity questions. |
| **Magic number?** | Yes. |

---

## 6. Curiosity Engine v2 — Information Gain (C5)

**File:** `velynx/graph/curiosity_engine_v2.py`

### `_EPS` (numerical floor)
| Field | Value |
|-------|-------|
| **Default** | `1e-12` |
| **Used in** | Entropy, self-information, normalisation calculations throughout |
| **Magic number?** | Defensible — prevents log(0). |

### `surprise_threshold_bits`
| Field | Value |
|-------|-------|
| **Default** | `2.0` |
| **Valid range** | `[0, ∞)` — bits of surprise needed to trigger curiosity |
| **Used in** | `CuriosityEngine.__init__` (line 358); `evaluate_surprise()` (line 379) |
| **What breaks** | At 0: every prediction failure triggers inquiry (constant curiosity). At > 5: only the most extreme failures question anything. |
| **Experimentally justified?** | Docstring says "2 bits ~ the model assigned ≤ 25% to the outcome". No empirical tuning. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

### Likelihood matrix values (hard-coded in `_candidate_inquiries`)
| Field | Value |
|-------|-------|
| **Default** | See 4 inquiry types with fixed 4×2 matrices (lines 486–558) |
| **Valid range** | Each row must sum to 1.0 |
| **Used in** | `expected_information_gain()` — drives EIG calculation |
| **What breaks** | These encode the designer's assumption of how diagnostic each answer is for each hypothesis. Wrong assumptions → wrong inquiry ranking. |
| **Experimentally justified?** | No. Entirely author intuition about e.g. P(answer=essential \| hypothesis=essential) = 0.92. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes — the entire matrices are magic. |

### Prior weight constants in `_derive_hypothesis_prior`
| Field | Value |
|-------|-------|
| **Default** | Various: `1.0`, `4.0`, `0.5`, `3.0`, `2.0` |
| **Used in** | `_derive_hypothesis_prior()` (lines 413–447) — unnormalised weights for each structural hypothesis |
| **What breaks** | These weights determine the prior P(H) over structural explanations. Different weights yield different EIG rankings. No formal justification for `4.0 * ratio + 0.5 * n_exc` vs any other formula. |
| **Experimentally justified?** | No. |
| **Magic number?** | Yes — additive weight deltas are entirely magic. |

---

## 7. Latent Cause Engine (C7)

**File:** `latent_cause_engine.py`

### `alpha` (PredictionGain weight)
| Field | Value |
|-------|-------|
| **Default** | `0.50` |
| **Valid range** | `[0, 1]` — though implied by three weights summing to not-necessarily-1 |
| **Used in** | `LatentCauseEngine.__init__` (line 153); `_score()` (line 281) |
| **What breaks** | Controls how much the engine values coverage+distinctiveness vs compression vs stability. Zero → prediction gain ignored. |
| **Experimentally justified?** | No. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

### `beta` (CompressionGain weight)
| Field | Value |
|-------|-------|
| **Default** | `0.30` |
| **Valid range** | `[0, 1]` |
| **Used in** | `LatentCauseEngine.__init__` (line 154) |
| **Experimentally justified?** | No. |
| **Magic number?** | Yes. |

### `gamma` (Stability weight)
| Field | Value |
|-------|-------|
| **Default** | `0.20` |
| **Valid range** | `[0, 1]` |
| **Used in** | `LatentCauseEngine.__init__` (line 155) |
| **Experimentally justified?** | No. |
| **Magic number?** | Yes. |

### `threshold` (promotion bar)
| Field | Value |
|-------|-------|
| **Default** | `0.50` |
| **Valid range** | `[0, ∞)` — minimum total score for promotion |
| **Used in** | `LatentCauseEngine.__init__` (line 156); `discover()` (line 194) |
| **What breaks** | At 0: every candidate promoted (overfitting). At > 1: almost nothing promoted. |
| **Experimentally justified?** | No. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

### `bits_per_value`
| Field | Value |
|-------|-------|
| **Default** | `8` |
| **Valid range** | `[1, 32]` — MDL quantisation precision in bits |
| **Used in** | `LatentCauseEngine.__init__` (line 157); `_compression_gain()` (line 323) |
| **What breaks** | Too low (1): compression gain overestimated → false positives. Too high (32): compression gain negligible → concept rarely born. |
| **Experimentally justified?** | No — 8 is a convenience (typical float quantisation). |
| **Magic number?** | Yes. |

### `pin_std_max`
| Field | Value |
|-------|-------|
| **Default** | `0.18` |
| **Valid range** | `(0, ~0.5]` — max std-dev for a dimension to be "pinned" |
| **Used in** | `LatentCauseEngine.__init__` (line 158); `_generate_candidates()` (line 254) |
| **What breaks** | Too high: noisy dimensions qualify as pinned → spurious predicates. Too low: only near-zero-variance dimensions qualify → few candidates. |
| **Experimentally justified?** | No. |
| **Magic number?** | Yes. |

### `separation_min`
| Field | Value |
|-------|-------|
| **Default** | `0.20` |
| **Valid range** | `(0, 1.0]` — minimum distance between quarantine mean and baseline mean |
| **Used in** | `LatentCauseEngine.__init__` (line 159); `_generate_candidates()` (line 255) |
| **What breaks** | Too low: spurious separation detected. Too high: real latent causes missed. |
| **Experimentally justified?** | No. |
| **Magic number?** | Yes. |

### `ref_spread` (stability denominator)
| Field | Value |
|-------|-------|
| **Default** | `0.5` |
| **Valid range** | `(0, ∞)` |
| **Used in** | `_stability()` (line 349): `tightness = max(0, 1 - spread / ref_spread)` |
| **What breaks** | Scales the stability score. Half the sensor range as reference is plausible but untuned. |
| **Experimentally justified?** | No. |
| **Magic number?** | Yes. |

---

## 8. Cognitive Telemetry / CPI (C6)

**File:** `cognitive_telemetry.py`

### `DEFAULT_ACCURACY_ALPHA`
| Field | Value |
|-------|-------|
| **Default** | `0.15` |
| **Valid range** | `(0, 1]` — EWMA smoothing factor |
| **Used in** | `CPITracker.__init__` (line 297); `ingest()` (line 375) |
| **What breaks** | Smaller: more inertia, slower to reflect recent changes. Larger: noisier, reacts to every tick. |
| **Experimentally justified?** | No. |
| **Magic number?** | Yes. |

### `DEFAULT_SURPRISE_ALPHA`
| Field | Value |
|-------|-------|
| **Default** | `0.20` |
| **Used in** | `CPITracker.__init__` (line 298); `ingest()` (line 377) |
| **Magic number?** | Yes. |

### `DEFAULT_DECAY_ALPHA`
| Field | Value |
|-------|-------|
| **Default** | `0.10` |
| **Used in** | `CPITracker.__init__` (line 299); `_advance_recovery()` (line 438) |
| **Magic number?** | Yes. |

### `SURPRISE_CEILING_BITS`
| Field | Value |
|-------|-------|
| **Default** | `5.0` |
| **Valid range** | `(0, ∞)` — normalisation ceiling for surprise |
| **Used in** | Module-level (line 94); `ingest()` (line 374); `concept_bottlenecks()` (line 457) |
| **What breaks** | Too low: high surprise clipped → CPI over-estimates accuracy. Too high: accuracy always near-zero. |
| **Experimentally justified?** | Docstring says "~5.3 bits is uniform over 40 symbols" — plausible but untuned. |
| **Magic number?** | Defensible but unaudited. |

### `decay_window`
| Field | Value |
|-------|-------|
| **Default** | `4` |
| **Valid range** | Integers `≥ 1` |
| **Used in** | `CPITracker.__init__` (line 300); `_advance_recovery()` (line 434) |
| **What breaks** | Smaller: recovery measured over fewer ticks → noisier. Larger: slow to detect recovery. |
| **Magic number?** | Yes. |

### `novelty_floor`
| Field | Value |
|-------|-------|
| **Default** | `2.0` |
| **Valid range** | `[0, ∞)` — surprise threshold to open a recovery spike window |
| **Used in** | `CPITracker.__init__` (line 301); `_advance_recovery()` (line 427) |
| **Magic number?** | Yes. |

### `consolidation_mass`
| Field | Value |
|-------|-------|
| **Default** | `5` |
| **Valid range** | Integers `≥ 1` |
| **Used in** | `CPITracker.__init__` (line 302); `ingest()` (line 395) |
| **Magic number?** | Yes. |

### CPI weights
| Field | Value |
|-------|-------|
| **Default** | accuracy=0.40, decay=0.30, compression=0.20, resolution=0.10 |
| **Used in** | `CognitiveProgressIndex.cpi` property (lines 246–249) |
| **Magic number?** | Yes. Author states "weights reflect predictive-processing priorities" but no formal sensitivity. |

### `ReflectionEngine` parameters
| Field | Default | Range | Magic? |
|-------|---------|-------|--------|
| `poll_interval` | `0.1` | `(0, ∞)` | Yes |
| `plateau_window` | `8` | `≥ 2` | Yes |
| `plateau_slope_epsilon` | `0.02` | `(0, 1)` | Yes |
| `stuck_surprise_threshold` | `1.5` | `[0, ∞)` | Yes |
| `diagnostic_cooldown` | `20` | `≥ 0` | Yes |

### `PredictiveAgent` parameters
| Field | Default | Range | Magic? |
|-------|---------|-------|--------|
| `prior_alpha` | `0.5` | `(0, ∞)` | Yes |
| `reify_shift_threshold` | `0.02` | `(0, 1)` | Yes |
| `reify_streak` | `5` | `≥ 1` | Yes |

### `top_k` in `concept_bottlenecks`
| Field | Value |
|-------|-------|
| **Default** | `3` |
| **Magic number?** | Yes. |

---

## 9. Free-Energy Metrics

**File:** `validation/metrics.py`

### `LAMBDA` (weight on Entropy H)
| Field | Value |
|-------|-------|
| **Default** | `1.0` |
| **Valid range** | `[0, ∞)` |
| **Used in** | `cognitive_energy()` (line 205) as default; `CognitiveEnergyMetric` (line 270) |
| **What breaks** | Controls relative importance of transition unpredictability vs surprise vs load. |
| **Experimentally justified?** | No — described as "physics constants of this cognitive universe" but no ablation. |
| **Sensitivity analysis?** | None. |
| **Magic number?** | Yes. |

### `MU` (weight on Surprise S)
| Field | Value |
|-------|-------|
| **Default** | `2.0` |
| **Magic number?** | Yes. |

### `NU` (weight on Active Load A)
| Field | Value |
|-------|-------|
| **Default** | `0.5` |
| **Magic number?** | Yes. |

### Regime thresholds
| Parameter | Default | Magic? |
|-----------|---------|--------|
| `ENTROPY_HIGH` | 2.0 bits | Yes |
| `SURPRISE_HIGH` | 0.50 | Yes |
| `SURPRISE_MILD` | 0.20 | Yes |
| `PRESSURE_HIGH` | 1.00 | Yes |
| `PRESSURE_MILD` | 0.25 | Yes |
| `ENERGY_EXHAUSTION` | 18.0 | Yes |

---

## 10. Decision Policy (C8)

**File:** `backend/cognition/decision_policy.py`

### `DEFAULT_LAMBDA`, `DEFAULT_MU`, `DEFAULT_NU`
| Field | Value |
|-------|-------|
| **Default** | `1.0`, `2.0`, `0.5` |
| **Valid range** | `[0, ∞)` |
| **Used in** | `DecisionPolicy.__init__` (lines 183–185); `evaluate_metrics()` → `_energy()` (line 365) |
| **Mirrors** `validation/metrics.py` deliberately. |
| **Magic number?** | Yes |

### `tolerance`
| Field | Value |
|-------|-------|
| **Default** | `0.0` |
| **Valid range** | `[0, ∞)` |
| **Used in** | `DecisionPolicy.__init__` (line 186); `_decide_free_energy()` (line 309) |
| **What breaks** | Higher tolerance = more merges accepted even if energy increases. |
| **Magic number?** | Default is defensible (strict). |

### `strategy`
| Field | Value |
|-------|-------|
| **Default** | `"free_energy"` |
| **Alternatives** | `"pareto"` |
| **Magic number?** | Design choice, not a numeric parameter. |

---

## 11. Replay Engine (C8)

**File:** `backend/cognition/replay_engine.py`

No tunable scalar parameters — pure measurement simulator.

---

## 12. Attention Modulator

**File:** `backend/cognition/attention_modulator.py`

### `focus_mult`
| Field | Value |
|-------|-------|
| **Default** | `10.0` |
| **Valid range** | `(0, ∞)` |
| **Used in** | `attention_weights()` (line 57): scales the attended dimension |
| **What breaks** | Too low (1.0): no attentional warping. Too high (1000): other dimensions effectively vanish from distance computation. |
| **Experimentally justified?** | No. |
| **Magic number?** | Yes. |

### `suppress_floor`
| Field | Value |
|-------|-------|
| **Default** | `0.05` |
| **Valid range** | `(0, 1]` |
| **Used in** | `attention_weights()` (line 58): residual weight for non-attended dimensions |
| **What breaks** | Near 0: non-attended dimensions vanish entirely. Near 1: no suppression. |
| **Magic number?** | Yes. |

---

## 13. Velynx Learner

**File:** `velynx_core/learner.py`

### `checkpoint_path`
| Field | Value |
|-------|-------|
| **Default** | `"velynx_core/learner_state.json"` |
| **Magic number?** | Path, not a tunable parameter. |

### `batch_size`
| Field | Value |
|-------|-------|
| **Default** | `5` |
| **Valid range** | Integers `≥ 1` |
| **Used in** | `VelynxLearner.__init__` (line 275); `_get_pending_batch()` (line 455) |
| **What breaks** | Larger batches = more topics learned per cycle but slower feedback. |
| **Magic number?** | Yes. |

### `sleep_between_items`
| Field | Value |
|-------|-------|
| **Default** | `1.5` seconds |
| **Valid range** | `[0, ∞)` |
| **Used in** | `VelynxLearner.__init__` (line 276); `_run_loop()` (line 439) |
| **Magic number?** | Yes, but defensible as rate-limiting to avoid DoS. |

### `max_retries`
| Field | Value |
|-------|-------|
| **Default** | `3` |
| **Valid range** | Integers `≥ 0` |
| **Used in** | `VelynxLearner.__init__` (line 277); `_learn_one()` (lines 369, 376) |
| **Magic number?** | Yes. |

### `_http_get` timeout
| Field | Value |
|-------|-------|
| **Default** | `10` seconds |
| **Valid range** | `(0, ∞)` |
| **Used in** | `_http_get()` (line 78) |
| **Magic number?** | Yes. |

### LearningItem.priority
| Field | Value |
|-------|-------|
| **Default** | `1.0` |
| **Valid range** | `(-∞, ∞)` — sort key for learning queue |
| **Magic number?** | Yes. |

### `_prune_done()` cutoff
| Field | Value |
|-------|-------|
| **Default** | `86400` seconds (24h) |
| **Magic number?** | Yes. |

### `_estimate_confidence()` values
| Field | Value |
|-------|-------|
| **Default** | `base=0.6`, Wikipedia bonus `0.75`, length bonuses `+0.05` at 500/1000 chars, cap at `0.95` |
| **Magic number?** | Entirely magic. |

### Relation extraction defaults
| Field | Value |
|-------|-------|
| **weight** | `0.8` |
| **evidence** | first 120 chars |
| **Magic number?** | Yes. |

---

## 14. Velynx Brain

**File:** `velynx_core/brain.py`

### `min_confidence_threshold`
| Field | Value |
|-------|-------|
| **Default** | `0.35` |
| **Valid range** | `[0, 1]` |
| **Used in** | `VelynxBrain.__init__` (line 140); `reason()` (lines 165, 175, 208) |
| **What breaks** | Too high: few concepts pass → weak reasoning. Too low: noisy concepts pollute answers. |
| **Experimentally justified?** | No. |
| **Magic number?** | Yes. |

### `max_len` in `_merge_field`
| Field | Value |
|-------|-------|
| **Default** | `400` (also 300 for individual fields) |
| **Used in** | `_merge_field()` (line 98); `_synthesize_answer()` (lines 229–232) |
| **Magic number?** | Yes. |

### `top_k` in reasoning loop
| Field | Value |
|-------|-------|
| **Default** | `6` (max matched concepts), `5` (text search top_k), `2` (traverse seeds), `8` (max sources) |
| **Magic number?** | Yes. |

### `max_hops` in graph traversal
| Field | Value |
|-------|-------|
| **Default** | `2` |
| **Used in** | `reason()` (line 199); `_check_contradictions()` (line 336) |
| **Magic number?** | Yes. |

### Confidence penalties
| Field | Value |
|-------|-------|
| **Default** | `-0.15` for contradictions, `min(1.0, len*0.3)` for chain steps |
| **Magic number?** | Yes. |

### `neighbor score > 0.3` filter
| Field | Value |
|-------|-------|
| **Default** | `0.3` |
| **Magic number?** | Yes. |

---

## 15. Velynx Self-Coder

**File:** `velynx_core/self_coder.py`

### `SandboxExecutor.timeout`
| Field | Value |
|-------|-------|
| **Default** | `30` seconds |
| **Valid range** | `(0, ∞)` |
| **Used in** | `SandboxExecutor.__init__` (line 232); `run_code()`, `run_tests()` |
| **Magic number?** | Yes. |

### `SandboxExecutor.memory_limit_mb`
| Field | Value |
|-------|-------|
| **Default** | `512` MB |
| **Magic number?** | Yes |

### `cycle_interval_seconds`
| Field | Value |
|-------|-------|
| **Default** | `3600` (1 hour) |
| **Used in** | `VelynxSelfCoder.__init__` (line 344) |
| **Magic number?** | Yes — 1 hour is a plausible but arbitrary default. |

### `scan_codebase()` skip patterns
| Field | Value |
|-------|-------|
| **Default** | `["__pycache__", ".git", "migrations", "alembic", "test_", "_test.py", "venv", "node_modules"]` |
| **Magic number?** | Defensible filter, not tunable. |

### `top 3` issues per cycle
| Field | Value |
|-------|-------|
| **Default** | `3` |
| **Magic number?** | Yes. |

### `_history` cap
| Field | Value |
|-------|-------|
| **Default** | `200` entries |
| **Magic number?** | Yes. |

### `recently attempted` window
| Field | Value |
|-------|-------|
| **Default** | `50` entries |
| **Magic number?** | Yes. |

### Code issue severity thresholds
| Field | Value |
|-------|-------|
| **Default** | no_docstring=0.3, no_error_handling=0.6, bare_except=0.7, long_function=0.4, todo_comment=0.5 |
| **Magic number?** | Yes. |

### `func_len > 10` for no_error_handling
| Field | Value |
|-------|-------|
| **Default** | `10` lines |
| **Magic number?** | Yes. |

### `func_len > 80` for long_function
| Field | Value |
|-------|-------|
| **Default** | `80` lines |
| **Magic number?** | Yes. |

### `issue.severity >= 0.5` auto-apply filter
| Field | Value |
|-------|-------|
| **Default** | `0.5` |
| **Magic number?** | Yes. |

---

## 16. Velynx Memory

**File:** `velynx_core/memory.py`

### `db_path`
| Field | Value |
|-------|-------|
| **Default** | `"velynx_core/velynx.db"` |
| **Magic number?** | Path. |

### SQLite connection `timeout`
| Field | Value |
|-------|-------|
| **Default** | `30` seconds |
| **Magic number?** | Yes. |

### `top_k` defaults
| Field | Value |
|-------|-------|
| **search_concepts** | `10` |
| **vector_search** | `10` |
| **Magic number?** | Yes. |

### Relation weight default
| Field | Value |
|-------|-------|
| **Default** | `1.0` |
| **Magic number?** | Yes. |

---

## 17. Living Edges / Bayesian Graph

**File:** `velynx/graph/living_edges.py`

### `asymptotic_weight` schema default
| Field | Value |
|-------|-------|
| **Default** | `0.7` |
| **Valid range** | `[0, 1]` |
| **Magic number?** | Yes. |

### `weight_alpha` / `weight_beta` schema defaults
| Field | Value |
|-------|-------|
| **Default** | `1.0` |
| **Magic number?** | Yes (uniform prior). |

### `update_lambda`
| Field | Value |
|-------|-------|
| **Default** | `0.15` (reinforce), `0.20` (challenge) |
| **Valid range** | `[0, 1]` |
| **Used in** | `add_living_edge()` (line 181), `reinforce_edge()` (line 188), `challenge_edge()` (line 198) |
| **What breaks** | Controls asymptotic weight update rate. Higher = faster saturation. |
| **Magic number?** | Yes. |

### Bayesian confidence thresholds
| Parameter | Default | Magic? |
|-----------|---------|--------|
| weight_mean ≥ 0.90 & evidence ≥ 20 & challenge_rate ≤ 0.05 → CERTAIN | composite | Yes |
| weight_mean ≥ 0.70 & evidence ≥ 5 → PROBABLE | composite | Yes |
| weight_mean < 0.40 → CONTESTED | 0.40 | Yes |

### `initial_quality`
| Field | Value |
|-------|-------|
| **Default** | `0.9` |
| **Used in** | `add_living_edge()` (line 160) |
| **Magic number?** | Yes. |

### `source_quality` default
| Field | Value |
|-------|-------|
| **Default** | `0.5` (reinforce), `0.5` (challenge) |
| **Magic number?** | Yes. |

### Migration constants
| Field | Value |
|-------|-------|
| `init_alpha` | `1.9` |
| `init_beta` | `1.0` |
| `init_asymptotic_weight` | `0.7 + 0.15 * (1.0 - 0.7)` = `0.745` |
| **Magic number?** | Yes. |

---

## 18. Inference Engine

**File:** `velynx/graph/inference_engine.py`

### Transitive inference weight multiplier
| Field | Value |
|-------|-------|
| **Default** | `0.6` |
| **Used in** | `propagate_inferences()` (line 61): `new_weight = round(w1 * w2 * 0.6, 4)` |
| **What breaks** | Controls how much confidence propagates through transitivity. `1.0` = full confidence transfer. `0.0` = no transfer. |
| **Magic number?** | Yes. |

### Inferred edge parameters
| Field | Value |
|-------|-------|
| `weight_alpha` | `1.2` |
| `weight_beta` | `1.0` |
| `context` | `'background_inference'` |
| `status` | `'inferred'` |
| `confidence` | `'UNCERTAIN'` |
| **Magic numbers?** | Yes. |

---

## 19. Predictive Core (Phase 50)

**File:** `backend/cognition/predictive_core.py`

### `DEFAULT_LEARNING_RATE`
| Field | Value |
|-------|-------|
| **Default** | `0.1` |
| **Magic number?** | Yes. |

### `DEFAULT_BASELINE_RATE`
| Field | Value |
|-------|-------|
| **Default** | `0.05` |
| **Magic number?** | Yes. |

### Schema defaults
| Field | Default | Magic? |
|-------|---------|--------|
| `activation` | `0.5` | Yes |
| `baseline` | `0.5` | Yes |
| `state_confidence` | `0.5` | Yes |
| `evidence_count` | `0` | Defensible |
| `effect` | `0.0` | Yes |
| `rule_confidence` | `0.5` | Yes |
| `decay` | `0.001` | Yes |

---

## 20. Night Learner / Scheduling

**File:** `night_learner.py`

### Mode configurations

| Mode | batch_size | max_topics | delay_between | embed | GPU |
|------|-----------|------------|---------------|-------|-----|
| night | 32 | 50 | 2.0s | True | Yes |
| weekend | 64 | 200 | 1.0s | True | Yes |
| background | 4 | 10 | 10.0s | False | No |
| light | 1 | 3 | 30.0s | False | No |

**All magic numbers.** No justification for batch_size=32 vs 64, or delay=2.0 vs 1.0.

### Mode schedule thresholds
| Field | Value |
|-------|-------|
| Night | `23:00–06:00` |
| Background | `06:00–09:00`, `18:00–23:00` |
| Light | `09:00–18:00` |
| Weekend | Saturday–Sunday |

Arbitrary boundaries. No empirical basis.

---

## 21. Probationary Concept Pipeline

**File:** `cognitive_core.py` (lines 1109–1119)

### `PROBATION_MIN_TRIALS`
| Field | Value |
|-------|-------|
| **Default** | `3` |
| **Magic number?** | Yes. |

### `PROBATION_CONFIRM_HIT_RATE`
| Field | Value |
|-------|-------|
| **Default** | `0.60` |
| **Magic number?** | Yes. |

---

## 22. Proposed Sensitivity Experiments

### Tier 1 — Highest Impact (affects core cognition)

| # | Parameters | Experiment | Measure |
|---|-----------|------------|---------|
| 1 | `alpha`, `beta`, `gamma` (LatentCauseEngine) | Grid search over [0.1, 0.9]³ with sum=1.0 | Promotion rate, false positive rate, discovered-cause quality (alignment with ground-truth regimes) |
| 2 | `STABILITY_HALF_MATURITY`, `FRACTURE_THRESHOLD` | 2D sweep: half-maturity in [1, 16], fracture in [0.5, 0.95] | Catastrophic forgetting resistance, adaptation speed, number of fractured rules |
| 3 | `base_rate`, `bootstrap_confidence` (StableBeliefModel) | 2D sweep: rate in [0.01, 0.5], bootstrap in [0.2, 0.9] | Convergence speed, final accuracy, stability-vs-plasticity balance |
| 4 | `lambda`, `mu`, `nu` (Free Energy coefficients) | Grid over [0.25, 4.0] for each | Regime classification accuracy (OPTIMAL/LEARNING/EXHAUSTION), merge acceptance rate |

### Tier 2 — Environment & Sensorium

| # | Parameters | Experiment | Measure |
|---|-----------|------------|---------|
| 5 | `relaxation`, `drift_sigma`, `noise_sigma` | Full factorial 3×3×3 | Predictor convergence time, steady-state prediction error, latent cause discovery rate |
| 6 | `dwell` probabilities | Vary each regime's dwell in [0.5, 0.98] | Regime detection accuracy, transition detection latency |
| 7 | Sensor weight matrices | Compare entangled vs. partially disentangled vs. orthogonal | Time-to-discovery of latent causes, final cause count |
| 8 | `pin_std_max`, `separation_min` | 2D sweep | Number of candidate predicates generated, cause quality |

### Tier 3 — Meta-Cognition & Curiosity

| # | Parameters | Experiment | Measure |
|---|-----------|------------|---------|
| 9 | `surprise_threshold_bits` (C5) | Sweep [0.5, 5.0] | Inquiry frequency, inquiry quality (EIG of selected question), user-ratings |
| 10 | Likelihood matrix values (C5) | Perturb each matrix entry ±0.10 | Rank stability of inquiries, does the optimal question change? |
| 11 | `DEFAULT_BIRTH_THRESHOLD_BITS` | Sweep [0.1, 2.0] | Birth rate, false positive rate, predictive gain from born concepts |
| 12 | CPI weights (accuracy/decay/compression/resolution) | Sensitivity: vary each weight ±50% | Does the CPI ranking of two runs invert? |

### Tier 4 — Systems & Scheduling

| # | Parameters | Experiment | Measure |
|---|-----------|------------|---------|
| 13 | Learner `batch_size`, `sleep_between_items` | 2×3 design | Topics learned per hour, API rate-limit safety margin |
| 14 | Night-learner `batch_size` and `delay_between` | Compare 16/32/64 × 0.5/1.0/2.0s | Throughput, embedding quality, CPU/GPU utilisation |
| 15 | `cycle_interval_seconds` (Self-Coder) | 1800/3600/7200 | Code improvement rate, test pass rate, git churn |

### Tier 5 — Decision Policy

| # | Parameters | Experiment | Measure |
|---|-----------|------------|---------|
| 16 | `tolerance` (DecisionPolicy) | Sweep [0.0, 1.0] | Merge acceptance rate, post-merge cognitive energy trajectory |
| 17 | `strategy` compare | "free_energy" vs "pareto" | Long-term energy minima, cluster count evolution, stability |

### Recommended first wave (highest ROI)

Run a **full factorial** on the 4 parameters in Tier-1 experiment #1 (LatentCauseEngine α,β,γ,threshold) together with the 2 parameters in #8 (pin_std_max, separation_min = 6 parameters total), using a fractional factorial design (16 runs). This alone would validate or refute the core discovery pipeline that is VELYNX's main cognitive differentiator.

Second wave: repeat for the C6 StableBeliefModel (Tier-1 #2 + #3 = 4 parameters, 16 runs), measuring the catastrophic forgetting resistance metric.

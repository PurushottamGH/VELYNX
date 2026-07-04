# Program C — Complete Assumption Ledger

**Generated:** 2026-07-01
**Scope:** Every load-bearing assumption in the VELYNX symbolic-AGI cognitive stack (C1–C8), extracted from code, documentation, equations, thresholds, experiments, and comments.
**Method:** No assumptions invented. Every entry is grounded in actual source text.

**Status categories:**
- **FACT** — Established mathematical truth or standard engineering practice
- **EVIDENCE SUPPORTED** — Supported by cited literature or prior results
- **WEAK** — Plausible but lacks direct evidence
- **SPECULATION** — No evidence; asserted without justification
- **CONTRADICTED** — Evidence contradicts the assumption

---

## Assumption Records

---

### A-IT01 — Conditional Independence Given Context

**Category:** Information-Theoretic

**Statement:** Successor symbols are conditionally independent given the order-k context.

**Location:** `cognitive_core.py:414` — Dirichlet-multinomial `P(s|c) = (n(c,s) + α) / (N(c) + α·|support|)`

**Evidence:** Standard Dirichlet-Multinomial assumption. The likelihood factorises as a product of independent draws given the latent probability vector — the Markov chain assumes the next symbol depends only on the order-k suffix.

**Status:** WEAK — Conditional independence is mathematically convenient but known to be false for natural sequences (e.g. nested grammatical structure, long-range dependencies). Contexts longer than k (default 1) are ignored.

**Dependency graph:** → `P(s|c)` → all downstream predictions, surprise, attention, learning

**Risk if false:** Prediction error estimates are systematically wrong for any sequence with >k dependencies; the model is overconfident about the wrong structure and underconfident about the right one.

**Experiment that would falsify it:** Feed a generated sequence with known order-(k+1) dependencies; measure whether prediction error is higher than for an order-(k+1) model on the same data.

**Priority:** HIGH

---

### A-IT02 — Zero-Probability Convention (0·log(0/q) = 0)

**Category:** Information-Theoretic

**Statement:** Terms where p(s) = 0 contribute nothing to KL divergence.

**Location:** `cognitive_core.py:143`, `concept_birth.py:135`

**Evidence:** Shannon information theory convention (`Khinčin 1953`). Standard in all information-theoretic code.

**Status:** FACT — This is a mathematical convention, not an empirical claim.

**Dependency graph:** → KL divergence → belief shift → learning dynamics

**Risk if false:** Not applicable (definitional).

**Experiment that would falsify it:** N/A (mathematical identity).

**Priority:** LOW

---

### A-IT03 — Symmetric Dirichlet Prior

**Category:** Information-Theoretic

**Statement:** All symbols are equally likely a priori (same α for every symbol).

**Location:** `cognitive_core.py:421` — `alpha: float = 0.5`

**Evidence:** Standard symmetric Dirichlet prior. No code path loads per-symbol prior weights.

**Status:** WEAK — The uniform prior is the least informative choice, which is defensible in the absence of prior knowledge. However, the architecture claims to learn from experience; if the environment has a non-uniform symbol distribution, the uniform prior is misspecified and the Dirichlet smoothing introduces a systematic bias toward uniformity for rare contexts.

**Dependency graph:** → `P(s|c)` → surprisal → learning efficiency

**Risk if false:** Rare-but-informative symbols are under-weighted; common symbols are penalised relative to their true frequency in the early learning period.

**Experiment that would falsify it:** Compare convergence rate of uniform-prior vs. empirically-estimated-prior Dirichlet models on a skewed ground-truth distribution.

**Priority:** MEDIUM

---

### A-IT04 — Surprisal Ceiling at 5.0 Bits

**Category:** Information-Theoretic

**Statement:** Maximum prediction error corresponds to 5.0 bits (≈ 32 equiprobable symbols).

**Location:** `cognitive_telemetry.py:94` — `SURPRISE_CEILING_BITS: float = 5.0`

**Evidence:** Used to normalise accuracy into [0, 1] via `norm_error = clamp(error / 5.0)`. The docstring notes "~5.3 bits is uniform over 40 symbols" — the ceiling is slightly below the theoretical max for the typical demo vocabulary size.

**Status:** WEAK — The ceiling is a hardcoded normalisation constant chosen for the demo environment. If the vocabulary exceeds ~32 symbols, normalised accuracy becomes an overestimate. The ontology doc flags this: "breaks for larger vocabularies."

**Dependency graph:** → CPI accuracy component → learning plateau detection → bottleneck attribution

**Risk if false:** In large-vocabulary regimes, accuracy is artificially inflated, plateau detector fails to trigger, and the system falsely believes it is learning when it is not.

**Experiment that would falsify it:** Run with a 64-symbol vocabulary; measure whether normalised accuracy ever exceeds 1.0 or whether CPI components saturate incorrectly.

**Priority:** HIGH

---

### A-IT05 — log₂(N+1) Concept Definition Cost

**Category:** Information-Theoretic

**Statement:** The cost to define a new concept symbol is `log₂(N+1)` bits, where N is the number of exception types it subsumes.

**Location:** `concept_birth.py:368` — `concept_definition_bits = _log2(float(n_members) + 1.0)`

**Evidence:** Treats each concept as requiring the ability to name one new symbol among N+1 possibilities. This is the standard MDL coding cost for adding one item to a set of size N.

**Status:** WEAK — Assumes concepts have no compositional structure. A real concept ("storm") carries internal structure (high wind, rain, low pressure) beyond a nametag. The `log₂(N+1)` cost underestimates the true description cost of an abstraction with internal semantics, potentially making concept birth too permissive.

**Dependency graph:** → λ_model → H_after → G (compression gain) → concept birth decision

**Risk if false:** Concepts are born too readily because the definition cost is artificially low; the belief substrate accumulates spurious abstractions that carry no real predictive power.

**Experiment that would falsify it:** Compare concept-birth rate against ground-truth regime count in the C7 Sensorium; measure false-positive birth rate (concepts born that do not align with actual regime transitions).

**Priority:** HIGH

---

### A-S01 — Spherical Clusters (K-Means)

**Category:** Statistical

**Statement:** Sensory vectors form spherical clusters — Euclidean distance is the correct similarity metric.

**Location:** `vector_prediction_core.py:22` — `euclidean_distance()`

**Evidence:** The entire clustering substrate uses Euclidean distance. No Mahalanobis or covariance-aware metric exists.

**Status:** EVIDENCE SUPPORTED — K-Means with Euclidean distance is the standard online clustering algorithm. The C7 Sensorium was designed to have separable structure (regime attractors in distinct corners of the unit cube). However, for real-world sensory data this assumption is almost always false.

**Dependency graph:** → cluster assignment → centroid update → Markov transitions → all vitals (H, S, A, E)

**Risk if false:** The system cannot capture correlated or elongated clusters. Two regimes that covary along non-axis-aligned dimensions will be conflated into one cluster or fragmented across many, degrading prediction.

**Experiment that would falsify it:** Replace the environment with a correlated Gaussian mixture (non-spherical clusters); measure whether cluster-count-to-regime-count ratio diverges from 1:1.

**Priority:** HIGH

---

### A-S02 — Markov Order 1 for Cluster Transitions

**Category:** Statistical

**Statement:** The next cluster depends only on the current cluster, not longer history.

**Location:** `vector_prediction_core.py:631`

**Evidence:** The predictor constructs a first-order transition matrix `{src: {dst: count}}`. No higher-order transitions are tracked.

**Status:** WEAK — Markov-1 is the simplest dynamic model. The C7 Sensorium has regime dwell probabilities (0.75–0.90) that are close to memoryless. However, any regime with periodic or multi-step structure (e.g. CALM_DAY → DUSK → NIGHT) is invisible to a Markov-1 model.

**Dependency graph:** → transition entropy H → cognitive energy E → decision policy

**Risk if false:** Entropy H underestimates true unpredictability for multi-step patterns; the decision policy approves merges that degrade prediction of longer-range structure.

**Experiment that would falsify it:** Create a regime with mandatory two-step transitions (A→B→A→B); measure whether H increases over time as the Markov-1 model fails.

**Priority:** HIGH

---

### A-S03 — Gaussian Sensor Noise

**Category:** Statistical

**Statement:** Sensor readings are corrupted by additive Gaussian noise with constant variance.

**Location:** `environment.py:232` — `gauss(0.0, self._noise_sigma)`

**Evidence:** `SensorArray.read()` adds `N(0, 0.05)` noise to every reading.

**Status:** WEAK — Gaussian noise is the standard modelling assumption for sensor noise. Real sensors have systematic biases, quantisation, dropout, drift, and non-Gaussian tails. The constant σ = 0.05 is hand-tuned.

**Dependency graph:** → sensor readings → cluster assignment → surprise S → all downstream

**Risk if false:** The noise model mismatch causes the system to treat systematic bias as signal (false surprise) or treat real signal as noise (missed structure).

**Experiment that would falsify it:** Replace Gaussian noise with uniform noise, clipping, or dropout; measure degradation in prediction RMSE.

**Priority:** MEDIUM

---

### A-S04 — Gaussian Environment Drift

**Category:** Statistical

**Statement:** Within-regime hidden state drift is a Gaussian random walk with constant σ = 0.03.

**Location:** `environment.py:129`

**Evidence:** `_state += r * (target - _state) + N(0, 0.03)` — bounded random walk toward attractor.

**Status:** WEAK — Real environments exhibit trend, seasonality, autocorrelated noise, and non-stationarity. The simple OU-process-with-drift is analytically convenient but not representative.

**Dependency graph:** → hidden state → sensor readings → all downstream cognitive metrics

**Risk if false:** The system fails to distinguish between real regime drift and within-regime noise if the noise model is misspecified.

**Experiment that would falsify it:** Add periodic forcing or trend to the environment drift; measure whether anomaly count or fracture rate increases spuriously.

**Priority:** MEDIUM

---

### A-S05 — Linear Sensor Projection

**Category:** Statistical

**Statement:** Sensors are linear projections of hidden state: `sensor = bias + Σ w_i·state_i + noise`.

**Location:** `environment.py:200`

**Evidence:** `_Sensor.transduce()` is a weighted sum + bias + noise, clamped to [0, 1].

**Status:** WEAK — Real sensory transduction is non-linear (logarithmic intensity, saturation, adaptation, cross-talk). The linear assumption simplifies analysis but removes the core representation-learning challenge.

**Dependency graph:** → sensory vector → cluster structure → all vitals

**Risk if false:** The system has no mechanism to learn non-linear invariances; real-world sensor non-linearities will appear as irreducible surprise.

**Experiment that would falsify it:** Replace linear sensors with a sigmoid-transformed mixture; measure whether anomaly count increases vs. linear baseline.

**Priority:** MEDIUM

---

### A-CA01 — "Lower is Better" for All Vitals

**Category:** Cognitive Architecture

**Statement:** Minimising entropy H, surprise S, active load A, and cognitive energy E is always the correct objective.

**Location:** `validation/metrics.py` (throughout), `decision_policy.py:13-28`

**Evidence:** Every vital is unambiguously "lower-is-better." The decision policy accepts merges that reduce E. The CPI reward structure rewards lower error, faster decay, higher compression.

**Status:** SPECULATION — The assumption ignores the exploration value of surprise. A system that never experiences surprise never learns. A system that minimises A by never forming new clusters cannot discover new structure. "Lower is better" is thermodynamically motivated but empirically unverified.

**Dependency graph:** → DecisionPolicy acceptance criteria → cognitive energy minimisation → all consolidation decisions

**Risk if false:** The system converges to a low-energy attractor that is a local minimum — it becomes "content" with a stale world model and stops exploring, even when the environment changes.

**Experiment that would falsify it:** Create a non-stationary environment where the optimal policy requires periodic high-surprise exploration; measure whether the system gets stuck in a low-energy dead end.

**Priority:** CRITICAL

---

### A-CA02 — E = λH + μS + νA Is a Valid Free-Energy Proxy

**Category:** Cognitive Architecture

**Statement:** The linear combination of transition entropy, spatial surprise, and active load approximates Friston's variational free energy.

**Location:** `validation/metrics.py:197`, `cognitive_health.py:6-7`

**Evidence:** The docstring explicitly calls it a "Free-Energy proxy." The ontology doc states: "NOT the variational free energy. No generative model likelihood, no posterior approximation." The coefficients are hand-tuned.

**Status:** SPECULATION — The three terms are formally incommensurate (bits + Euclidean distance + clusters). No derivation from the FEP exists. The PI review calls this a "proxy that is NOT FEP." The evidence database flags a Constitution conflict if presented as actual FEP.

**Dependency graph:** → DecisionPolicy → cognitive health monitoring → Regime classification → all kill criteria

**Risk if false:** All downstream decisions (merge acceptance, health state classification, learning plateau detection) are optimising the wrong quantity. The system may behave pathologically — e.g. reducing energy by collapsing clusters at the cost of predictive accuracy — because the proxy rewards the wrong thing.

**Experiment that would falsify it:** Compare the proxy E against a true variational free energy for a tractable generative model; measure rank correlation between the proxy and the true value under regime change.

**Priority:** CRITICAL

---

### A-CA03 — Fracture Threshold at 0.85

**Category:** Cognitive Architecture

**Statement:** A belief must accumulate contradictions approaching 85% of its support count before it is revised.

**Location:** `cognitive_core.py:682` — `FRACTURE_THRESHOLD: float = 0.85`

**Evidence:** Hardcoded constant. No sensitivity analysis in the repository.

**Status:** WEAK — The threshold is tuned, not derived. The docstring says "Tuned so a rule confirmed a handful of times already resists single anomalies." No ablation study demonstrates optimality.

**Dependency graph:** → `is_fractured` → belief revision trigger → stability of the belief substrate

**Risk if false:** If too high, the system resists genuine regime shifts for too long, accumulating massive exception backlogs before adapting. If too low, the system over-fractures, treating noise as regime change.

**Experiment that would falsify it:** Sweep fracture threshold from 0.50 to 0.95 in the C7 Sensorium; measure prediction RMSE and regime-change detection latency.

**Priority:** HIGH

---

### A-CA04 — Stability Half-Maturity at 4.0

**Category:** Cognitive Architecture

**Statement:** ~4 confirmations is the "half-life" of belief plasticity.

**Location:** `cognitive_core.py:678` — `STABILITY_HALF_MATURITY: float = 4.0`

**Evidence:** `stability(n) = ln(1+n) / (ln(1+n) + ln(1+H_m))` where H_m = 4.0. After 4 confirmations, stability = 0.5.

**Status:** SPECULATION — The value is arbitrary. No derivation from biological learning rates or information-theoretic first principles exists. The ontology doc lists it as "arbitrary."

**Dependency graph:** → stability → effective learning rate → belief revision dynamics

**Risk if false:** If too low, rules lock in too fast and resist legitimate revision. If too high, rules stay plastic too long and suffer from the catastrophic forgetting the C6 design was intended to cure.

**Experiment that would falsify it:** Sweep H_m from 1.0 to 20.0; measure retention of a learned rule after a burst of noise vs. adaptation speed to a genuine regime shift.

**Priority:** HIGH

---

### A-CA05 — EWMA Alphas for CPI (0.15, 0.20, 0.10)

**Category:** Cognitive Architecture

**Statement:** The smoothing factors for accuracy, surprise, and decay EWMA trackers are correctly chosen.

**Location:** `cognitive_telemetry.py:87-89`

**Evidence:** `DEFAULT_ACCURACY_ALPHA = 0.15`, `DEFAULT_SURPRISE_ALPHA = 0.20`, `DEFAULT_DECAY_ALPHA = 0.10`. No empirical calibration.

**Status:** SPECULATION — The ontology doc lists these as "not derived from data; manually chosen." No sensitivity analysis exists.

**Dependency graph:** → CPI component values → plateau detection timing → bottleneck attribution

**Risk if false:** The CPI tracks irrelevant time scales — too fast (noise dominates) or too slow (genuine trends missed). Plateau detector either fires spuriously or fails to fire when needed.

**Experiment that would falsify it:** Sweep all three alphas over [0.01, 0.50] in a simulation with known learning curves; measure CPI correlation with ground-truth learning progress.

**Priority:** MEDIUM

---

### A-CA06 — CPI Weight Vector (0.40, 0.30, 0.20, 0.10)

**Category:** Cognitive Architecture

**Statement:** Accuracy is weighted 4× contradictions, 2× compression, and 3× decay in the CPI composite.

**Location:** `cognitive_telemetry.py:246-250`

**Evidence:** `weights = {"accuracy": (..., 0.40), "decay": (..., 0.30), "compression": (..., 0.20), "resolution": (..., 0.10)}`

**Status:** SPECULATION — No justification exists beyond the docstring comment: "Weights reflect predictive-processing priorities: accuracy is the primary survival signal..." This is a design opinion, not an empirical result.

**Dependency graph:** → CPI composite → learning plateau detection → kill criteria activation

**Risk if false:** The CPI misrepresents cognitive progress; the system declares "LEARNING" when it is merely getting better at being wrong in a low-surprise way, or declares "STAGNANT" despite structural learning that happens to not improve accuracy.

**Experiment that would falsify it:** Create a scenario where compression improves but accuracy is flat; measure whether the CPI correctly identifies this as progress (it will not — accuracy is 40% of the score).

**Priority:** HIGH

---

### A-CA07 — Cooldown of 50 Ticks After Consolidation

**Category:** Cognitive Architecture

**Statement:** A 50-tick refractory period is sufficient to prevent consolidation oscillation.

**Location:** `memory_scheduler.py:46`

**Evidence:** `_DEFAULT_COOLDOWN = 50`. The docstring says "Prevents oscillation but the constant is arbitrary."

**Status:** SPECULATION — The ontology doc explicitly lists it as "arbitrary."

**Dependency graph:** → consolidation timing → cluster merge frequency → adaptation speed

**Risk if false:** Too short: consolidation chatters, wasting compute and potentially destabilising the cluster substrate. Too long: the system cannot adapt to rapid regime change.

**Experiment that would falsify it:** Sweep cooldown from 10 to 200; measure merge efficiency and prediction RMSE under rapid regime-switching.

**Priority:** MEDIUM

---

### A-CA08 — Pin Std Max (0.18) and Separation Min (0.20)

**Category:** Cognitive Architecture

**Statement:** A dimension is "pinned" (a potential latent invariant) if its quarantine std ≤ 0.18 and its mean is ≥ 0.20 away from the baseline mean.

**Location:** `latent_cause_engine.py:158-159`

**Evidence:** `pin_std_max: float = 0.18`, `separation_min: float = 0.20`. Sensor-range-dependent thresholds.

**Status:** WEAK — These thresholds define what counts as an "invariant" dimension. They are tuned for the [0, 1] normalised sensor range. No principled derivation.

**Dependency graph:** → predicate generation → LatentVariable candidates → latent cause discovery → concept formation

**Risk if false:** Too tight: real invariants are missed (false negatives). Too loose: spurious invariants are promoted (false positives, overfitted latent causes).

**Experiment that would falsify it:** Sweep both parameters in the C7 Sensorium; measure latent cause discovery precision and recall against ground-truth regimes.

**Priority:** MEDIUM

---

### A-CA09 — Probation Testing Adequately Validates Concepts

**Category:** Cognitive Architecture

**Statement:** The 3-trial probation window with 60% hit-rate threshold confirms or rejects concept candidates.

**Location:** `cognitive_core.py:1114, 1119` — `PROBATION_MIN_TRIALS = 3`, `PROBATION_CONFIRM_HIT_RATE = 0.60`

**Evidence:** The probation pipeline is optional (`_PIPELINE_AVAILABLE` flag). The ontology doc notes it is "marked as optional and its integration with StableBeliefModel is partial."

**Status:** WEAK — 3 trials is insufficient for statistical significance. The 60% hit rate is arbitrary. The probation pipeline creates a feedback loop (exception → concept birth → probation monitoring → exception reclassification) that the ontology doc flags as potentially circular.

**Dependency graph:** → ProbationaryConcept verdict → concept acceptance → belief substrate expansion

**Risk if false:** Spurious concepts pass probation (false positives) or genuine concepts fail it (false negatives). The feedback loop can cause oscillatory concept birth and rejection.

**Experiment that would falsify it:** Measure false-positive and false-negative rates of the probation verdict against ground-truth regime labels in a long-run simulation.

**Priority:** HIGH

---

### A-CA10 — Learning Rate = 0.20 Is Adequate

**Category:** Cognitive Architecture

**Statement:** The base learning rate of 0.20 for belief updates is appropriate across all contexts.

**Location:** `cognitive_core.py:793`

**Evidence:** `base_rate: float = 0.20`. Single global value.

**Status:** WEAK — No justification or sensitivity analysis. The effective rate is modulated by stability (`η_eff = η_base · (1 - stability)`), so the base value matters primarily for immature beliefs.

**Dependency graph:** → effective learning rate → confidence update → belief evolution speed

**Risk if false:** Too high: beliefs over-adapt to single observations even at moderate stability. Too low: beliefs under-adapt, learning slows.

**Experiment that would falsify it:** Sweep base_rate from 0.01 to 0.50; measure convergence speed and final prediction RMSE.

**Priority:** MEDIUM

---

### A-CA11 — Epsilon Floor of 0.02 Guarantees Finite Surprisal

**Category:** Cognitive Architecture

**Statement:** Adding a uniform 0.02 floor to every symbol's probability keeps surprisal finite and well-defined.

**Location:** `cognitive_core.py:797`

**Evidence:** `epsilon: float = 0.02`. After normalisation, the floor becomes `0.02 / (|support|·0.02 + confidence + ...)`.

**Status:** WEAK — The approach is standard additive smoothing. However, the 0.02 value is not derived from any theoretical floor on information. The re-normalisation subtly distorts relative probabilities (as noted in the ontology doc).

**Dependency graph:** → predictive distribution → surprisal → attention → all downstream

**Risk if false:** If epsilon is too large, it swamps the true predictive signal (especially for large supports). If too small, underflow risk for rare contexts. The re-normalisation biases probabilities toward uniformity.

**Experiment that would falsify it:** Compare predictive distributions with and without epsilon floor against ground-truth frequencies for a large vocabulary; measure KL divergence introduced by the floor.

**Priority:** MEDIUM

---

### A-CA12 — Bootstrap Confidence of 0.50 Is Appropriate

**Category:** Cognitive Architecture

**Statement:** A newly formed belief starts with confidence 0.50 (maximum uncertainty).

**Location:** `cognitive_core.py:794`

**Evidence:** `bootstrap_confidence: float = 0.50`

**Status:** WEAK — 0.50 is the maximum-entropy choice for a binary outcome. It is defensible as a minimally informative prior but not grounded in evidence about the environment's transition statistics.

**Dependency graph:** → initial rule confidence → initial predictive distribution → early learning dynamics

**Risk if false:** If the environment is highly deterministic, the 0.50 startup confidence causes the system to under-predict its first few observations (surprisal > optimal).

**Experiment that would falsify it:** Measure average surprisal over the first N ticks with bootstrap_confidence swept from 0.10 to 0.90.

**Priority:** LOW

---

### A-CA13 — Crystallize Threshold of 0.80

**Category:** Cognitive Architecture

**Statement:** A context's successor distribution has "crystallised" into a rule when the best probability ≥ 0.80.

**Location:** `cognitive_core.py:422`

**Evidence:** `crystallize_threshold: float = 0.80`

**Status:** WEAK — No justification for the 0.80 value. It determines when the system reports an "emergent rule" concept formation event.

**Dependency graph:** → concept detection (latent_concepts) → CPI compression → introspection

**Risk if false:** Too high: the system never reports crystallisation for genuinely deterministic rules with rare exceptions. Too low: premature crystallisation alarms.

**Experiment that would falsify it:** Sweep threshold in C7 Sensorium; measure agreement between crystallisation events and actual regime boundaries.

**Priority:** LOW

---

### A-CA14 — Motif Threshold of 3.0

**Category:** Cognitive Architecture

**Statement:** A context→successor transition seen ≥ 3 times is a "motif" (recurring pattern).

**Location:** `cognitive_core.py:424`

**Evidence:** `motif_threshold: float = 3.0`

**Status:** WEAK — The threshold 3.0 is the minimum count for statistical significance under a weak prior, but no power analysis supports it.

**Dependency graph:** → motif detection → concept formation reports

**Risk if false:** Low — motif detection is purely for introspection (not used in any decision path). However, it feeds the concept-formation narrative.

**Experiment that would falsify it:** Sweep threshold; measure false-positive motif detection rate.

**Priority:** LOW

---

### A-CA15 — Consolidation Mass of 5 Experiences Is Sufficient

**Category:** Cognitive Architecture

**Statement:** A concept is consolidated (trusted as reusable) after 5 observations.

**Location:** `cognitive_telemetry.py:302`

**Evidence:** `consolidation_mass: int = 5`

**Status:** WEAK — No justification. Governs when a concept enters the CPI's `concepts_consolidated` set, affecting compression ratio.

**Dependency graph:** → consolidated_concepts → compression ratio → CPI

**Risk if false:** Too low: concepts are trusted before sufficient evidence (compression ratio inflated). Too high: genuine concepts are not counted (compression ratio understated).

**Experiment that would falsify it:** Sweep consolidation mass; measure CPI calibration against ground-truth learning progress.

**Priority:** MEDIUM

---

### A-N01 — Dirichlet Smoothing Prevents Zero Probability

**Category:** Numerical

**Statement:** The symmetric Dirichlet prior guarantees all symbols have strictly positive probability.

**Location:** `cognitive_core.py:410`

**Evidence:** Additive smoothing: `P(s|c) = (n(c,s) + α) / (N(c) + α·|support|)`. Every symbol receives at least `α / (N(c) + α·|support|)` mass.

**Status:** FACT — Mathematically guaranteed for finite support size and α > 0.

**Dependency graph:** → positivity of predictive distribution → finite surprisal

**Risk if false:** Not applicable (mathematically true).

**Experiment that would falsify it:** N/A.

**Priority:** LOW

---

### A-N02 — Normalisation After Epsilon Floor Is Correct

**Category:** Numerical

**Statement:** Adding uniform epsilon floor then re-normalising yields a valid probability distribution.

**Location:** `cognitive_core.py:847-848`

**Evidence:** `normaliser = sum(dist.values())` then `{s: v / normaliser for s, v in dist.items()}`.

**Status:** FACT — Re-normalisation produces a valid probability distribution that sums to 1. However, as the ontology doc notes, it "subtly changes the relative probabilities" of the structured mass components.

**Dependency graph:** → predictive distribution → KL divergence → all downstream

**Risk if false:** Low to Medium — The distribution remains mathematically valid, but the relative ordering of alternatives can change after re-normalisation, potentially altering the predicted symbol.

**Experiment that would falsify it:** Compare re-normalised distribution with a formally correct Dirichlet compound distribution; measure KL between the two.

**Priority:** LOW

---

### A-N03 — Division Guard ε = 1e-9 for MDL

**Category:** Numerical

**Statement:** 1e-9 prevents division by zero in MDL compression gain calculations.

**Location:** `latent_cause_engine.py:58`

**Evidence:** `_EPS = 1e-9`

**Status:** FACT — Standard numerical guard. The specific value is safely below any meaningful cost threshold.

**Dependency graph:** → compression gain → latent cause score → promotion decision

**Risk if false:** Not applicable (standard safe practice).

**Experiment that would falsify it:** N/A.

**Priority:** LOW

---

### A-N04 — Reference Spread = 0.5 for Tightness

**Category:** Numerical

**Statement:** Half the sensor range [0, 1] is the reference spread; tightness = 1 - spread/0.5.

**Location:** `latent_cause_engine.py:349`

**Evidence:** `ref_spread = 0.5`

**Status:** WEAK — The choice of 0.5 as "the spread at which a dimension is deemed completely unstably invariant" assumes the sensor range is exactly [0, 1]. If sensors are re-scaled, the reference must change.

**Dependency graph:** → Stability (tightness) → latent cause score → promotion

**Risk if false:** If sensor range is not normalised to [0, 1], tightness is non-informative (always 0 or always 1).

**Experiment that would falsify it:** Test with sensors in [0, 10] range without re-normalising; measure whether all latent causes get ST = 0.

**Priority:** MEDIUM

---

### A-N05 — Attention Focus Multiplier = 10.0

**Category:** Numerical

**Statement:** A 10× weight difference is sufficient for attended dimensions to dominate clustering.

**Location:** `vector_prediction_core.py:727`

**Evidence:** `attention_focus_mult = 10.0`. Attended dimension gets `focus_mult * importance` weight; others get `suppress_floor = 0.05`.

**Status:** WEAK — The 10× factor is uncalibrated. Whether it dominates depends on dimensionality: for D=4 it is extreme; for D=100 it may be insufficient.

**Dependency graph:** → weighted Euclidean distance → cluster assignment → attention-feedback loop

**Risk if false:** Too low: attention does not functionally warp the metric, and the attended dimension does not dominate clustering. Too high: attended dimension completely determines cluster formation, ignoring all other structure.

**Experiment that would falsify it:** Vary focus_mult from 2 to 100 in the C7 Sensorium; measure the fraction of clusters that align with the attended dimension.

**Priority:** MEDIUM

---

### A-N06 — Attention Suppress Floor = 0.05

**Category:** Numerical

**Statement:** Non-attended dimensions retain 5% weight to avoid complete blindness.

**Location:** `vector_prediction_core.py:728`

**Evidence:** `attention_suppress_floor = 0.05`

**Status:** WEAK — Uncalibrated. The ontology doc notes: "Non-attended dimensions still have 5% weight to avoid complete blindness."

**Dependency graph:** → weighted Euclidean distance → cluster assignment → attention-feedback loop

**Risk if false:** Too low: the system is blind to all unattended dimensions, causing fixation on one dimension. Too high: attention has no meaningful effect on clustering.

**Experiment that would falsify it:** Sweep suppress_floor from 0.01 to 0.50; measure attention's effect on cluster alignment with the attended dimension.

**Priority:** MEDIUM

---

### A-O01 — "Concept" = String Label

**Category:** Ontological

**Statement:** A concept is adequately represented by a string label returned by `_detect_concepts()`.

**Location:** `cognitive_core.py:579-612`

**Evidence:** Concepts are returned as formatted strings: `"novel::Rain"`, `"crystallize::(Day)=>Night~0.92"`, `"motif::(Day)->Night x5"`. The ontology doc states: "concepts are ephemeral string detections from threshold crossings."

**Status:** SPECULATION — There is no formal concept representation (no attributes, no relations, no compositional structure). Concepts are ephemeral diagnostic strings, not objects the engine can reason about.

**Dependency graph:** → experience.latent_concepts → CPI tracking → user-facing introspection

**Risk if false:** The system cannot perform any actual reasoning about the concepts it claims to have formed. "Concept formation" is purely cosmetic — the engine has concepts in name only.

**Experiment that would falsify it:** After the engine reports a "crystallised" concept, query the engine to list the properties of that concept; the engine cannot (no representation exists).

**Priority:** CRITICAL

---

### A-O02 — Two Belief Substrates Are Interchangeable

**Category:** Ontological

**Statement:** DirichletMarkovModel and StableBeliefModel are functionally equivalent as GenerativeModel implementations.

**Location:** `cognitive_core.py:765-789`

**Evidence:** Both implement the `GenerativeModel` Protocol. The docstring claims they "slot into CognitiveEngine unchanged." The ontology doc notes they "have fundamentally different dynamics (precision-weighted vs. inertia-law)."

**Status:** CONTRADICTED — The PI review and evidence database both note that C6 explicitly abandons precision-weighted learning (C1-C3) due to catastrophic forgetting. The two substrates have opposite learning-rate dynamics (surprise-amplified vs. surprise-attenuated). The ontology doc explicitly contradicts the interchangeability claim.

**Dependency graph:** → model selection in CognitiveEngine → all cognitive dynamics

**Risk if false:** The engine may be using the wrong substrate for a given context without detecting the mismatch. The difference in dynamics means results from one do not transfer to the other.

**Experiment that would falsify it:** Run an identical sequence through both substrates; compare prediction error trajectories — they diverge by construction.

**Priority:** HIGH

---

### A-O03 — Fracture Is Sufficient for Regime Detection

**Category:** Ontological

**Statement:** Belief revision via dominant exception promotion (fracture) is sufficient for detecting regime shifts.

**Location:** `cognitive_core.py:982-1013`

**Evidence:** `_refracture()` promotes the dominant exception when contradiction_count / support_count ≥ 0.85. The ontology doc notes: "Assumes regime shifts manifest as one exception overtaking the rule; ignores gradual drifts or multi-factor shifts."

**Status:** WEAK — The fracture mechanism can only detect abrupt, one-exception-overtakes-rule regime shifts. Gradual drift (slowly changing transition probabilities) or multi-factor shifts (multiple exceptions rising simultaneously) are invisible to this mechanism.

**Dependency graph:** → belief revision → model adaptation → all downstream learning

**Risk if false:** The system misses gradual regime shifts entirely, accumulating unbounded exceptions without ever fracturing. The exception backlog grows until the system enters EXHAUSTION without understanding why.

**Experiment that would falsify it:** Create a gradual regime shift (transition probability drifts linearly from 0.9 to 0.1 over 200 ticks); measure whether fracture ever triggers.

**Priority:** CRITICAL

---

### A-O04 — Curiosity Gaps Defined by Hand-Authored Ontology

**Category:** Ontological

**Statement:** Six hand-authored curiosity categories × 2-4 attributes each adequately define the space of knowledge gaps.

**Location:** `curiosity.py:115-122`

**Evidence:** The curiosity engine operates over a static, hand-authored ontology. The ontology doc states: "6 categories × 2-4 attributes each — extremely sparse coverage of real-world knowledge."

**Status:** SPECULATION — The curiosity system is not emergent. It cannot discover gaps its author did not pre-define. PI review: "Nothing develops."

**Dependency graph:** → curiosity → simulated annealing → concept formation pipeline

**Risk if false:** Curiosity is theatre — the system appears curious but can only ask pre-scripted question types about pre-scripted categories.

**Experiment that would falsify it:** Present the system with a completely novel domain not in the curiosity ontology; measure whether any inquiry goals are generated (they should not be).

**Priority:** HIGH

---

### A-O05 — Hand-Authored Scaffolding Supports Development

**Category:** Ontological

**Statement:** Pre-seeded concepts, hand-authored ontology, scripted curriculum, and hand-coded edge labels constitute a developmental trajectory.

**Location:** `docs/VELYNX_v2_PI_Review.md:D1`

**Evidence:** PI Review Assumption D1: "[UNSUPPORTED BELIEF] Nothing develops. Concepts are seeded, bridges hardcoded, ontology hand-authored, curriculum scripted with expected_answer."

**Status:** CONTRADICTED — The PI review, the ablation report, and the ontology doc all agree: nothing in Program C develops. All structure is hand-authored. The "development" claim is asserted in documentation but contradicted by every implementation file.

**Dependency graph:** → entire Program C thesis — if development is not happening, the core research claim is falsified

**Risk if false:** The entire research program for Project C is based on a false premise. The system is a hand-specified symbolic engine, not a developing mind.

**Experiment that would falsify it:** EXP-0 (paraphrase the benchmark) — already predicted to collapse to 4.0/10, confirming the system has no emergent understanding.

**Priority:** CRITICAL

---

### A-O06 — Self-Model via SQL Join Constitutes Selfhood

**Category:** Ontological

**Statement:** Querying 4 stores and narrating the result in first person constitutes a self-model.

**Location:** `docs/VELYNX_v2_PI_Review.md:D3`

**Evidence:** PI Review D3: "[SPECULATION] It is a SQL join over four stores, narrated in the first person."

**Status:** SPECULATION — The self-model is a data retrieval operation with no evidence of self-representation, self-other distinction, or metacognitive access.

**Dependency graph:** → self-model → agentic loop → system behavior claims

**Risk if false:** The "self-model" is narration over a database query, not a model of the self. Any claim about selfhood or self-awareness is misleading.

**Experiment that would falsify it:** Show that the self-model cannot distinguish between its own beliefs and externally provided information (it cannot — both are stored identically).

**Priority:** HIGH

---

### A-O07 — Foundational Ontology Grounds Meaning (Symbol Grounding)

**Category:** Ontological

**Statement:** Hand-authored `is-a` trees (Entity → PhysicalObject → ...) give symbols meaning.

**Location:** `docs/VELYNX_v2_PI_Review.md:D4`

**Evidence:** PI Review D4: "[CONTRADICTED] Symbol grounding problem (Harnad 1990). Hand-authored is-a trees are notation, not grounding; the tokens mean nothing to the system."

**Status:** CONTRADICTED — The symbol grounding problem is well-established in cognitive science. Hand-authored taxonomies are notation, not meaning. The tokens have no sensorimotor grounding.

**Dependency graph:** → ontology → schema gatekeeper → knowledge representation

**Risk if false:** All symbolic reasoning in the system is ungrounded — symbols refer only to other symbols, never to the world.

**Experiment that would falsify it:** Present a novel object not in the ontology; measure whether the system can integrate it into its knowledge (it cannot — no grounding mechanism exists).

**Priority:** CRITICAL

---

### A-O08 — Metaphorical Neuroscience Terminology Is Acceptable

**Category:** Ontological

**Statement:** Using terms like "resonance," "thermodynamic state," "free energy," "synaptic pruning," and "active inference" without implementing the corresponding biological mechanisms is acceptable for a cognitive architecture.

**Location:** Throughout codebase; documented in `research/evidence_database.md:594-611`

**Evidence:** The evidence database's Constitution Compatibility Matrix flags: "Free Energy Principle — RISK (proxy is NOT FEP)", "Active Inference — RISK (only precision-weighted learning; overclaims)", "Predictive Coding — RISK (single-level, not hierarchical)", "Thermodynamic State — RISK (metaphorical, not physical thermodynamics)".

**Status:** SPECULATION — The terminology creates a misleading impression of biological grounding. The PI review explicitly states the design "makes zero contact with neuroscience."

**Dependency graph:** → perception of the system's biological plausibility → scientific credibility

**Risk if false:** The system fails peer review because claims outstrip implementation. Resources are wasted building terminology scaffolding instead of actual mechanisms.

**Experiment that would falsify it:** Map every neuroscience term used in code comments and docstrings against its actual implementation; measure the gap.

**Priority:** HIGH

---

### A-E01 — Free Energy Minimization Improves Prediction

**Category:** Experimental

**Statement:** The C8 Free Energy minimization policy (accept merge iff ΔE ≥ 0) improves predictive performance over simpler baselines.

**Location:** `ablation_report.md`

**Evidence:** The R1 ablation report (72 experiments) shows: "PredictionRMSE — tie / inconclusive (no significant difference vs best baseline). FreeEnergy mean = 0.2991; best baseline = `null` (0.2951)." FinalEnergy is circular (policy optimises what it measures).

**Status:** CONTRADICTED — The ablation experiment found no statistically significant improvement from free-energy-based merge selection over naive baselines (null, random, FIFO, similarity). The free energy policy is definitionally better at its own objective but no better at prediction.

**Dependency graph:** → C8 decision policy → entire consolidation strategy

**Risk if false:** The entire C8 decision architecture (sandbox simulation, energy computation, Pareto guard, hysteresis scheduling) has zero measurable benefit over doing nothing. ~2,000 LOC of machinery produces no improvement.

**Experiment that would falsify it:** Already done — the R1 ablation. Result: FreeEnergy policy is indistinguishable from baselines.

**Priority:** CRITICAL

---

### A-E02 — CPI Measures Genuine Cognitive Progress

**Category:** Experimental

**Statement:** The Cognitive Progress Index (composite of accuracy trend, surprise decay, compression ratio, contradiction resolution) measures genuine learning.

**Location:** `cognitive_telemetry.py:237-252`

**Evidence:** The CPI is used as the primary metric of cognitive improvement. The docstring asks: "Is VELYNX actually getting smarter?"

**Status:** WEAK — The CPI measures four internal quantities, but there is no ground-truth validation showing CPI correlates with external task performance. 5 of 6 primary metrics in the R1 ablation were not measurable. The CPI could increase while external performance decreases (e.g., the system compresses an incorrect model).

**Dependency graph:** → learning plateau detection → SystemDiagnostics → adaptation triggers

**Risk if false:** The CPI is a vanity metric — it improves while the system is actually getting worse, creating a false sense of progress.

**Experiment that would falsify it:** Construct a scenario where prediction accuracy decreases but compression increases (merging dissimilar clusters reduces cluster count); measure whether CPI still increases.

**Priority:** HIGH

---

### A-E03 — Markov-1 Entropy Captures Dynamics Complexity

**Category:** Experimental

**Statement:** The transition entropy H of a first-order Markov chain adequately captures the unpredictability of the cluster dynamics.

**Location:** `validation/metrics.py:113-147`

**Evidence:** H(next | current) computed from first-order transition counts.

**Status:** WEAK — H is used as a term in the cognitive energy E and feeds the decision policy. If the dynamics have higher-order structure, H systematically underestimates true unpredictability.

**Dependency graph:** → cognitive energy E → decision policy → Regime classification

**Risk if false:** The system believes dynamics are more predictable than they actually are, potentially accepting merges that destroy higher-order structure.

**Experiment that would falsify it:** Generate cluster dynamics with clear order-2 structure; compare Markov-1 H with Markov-2 H.

**Priority:** MEDIUM

---

### A-E04 — Replay Sandbox Correctly Simulates Post-Merge State

**Category:** Experimental

**Statement:** A deepcopy sandbox cluster engine, with one merge applied and vitals measured against the recent-vectors window, faithfully represents the post-merge world.

**Location:** `replay_engine.py:112`

**Evidence:** `sandbox_engine = copy.deepcopy(live_engine)` then `_apply_proposal(sandbox_engine, proposal)`. The recent_vectors window was generated under the old clustering.

**Status:** WEAK — The ontology doc flags this: "the recent_vectors window was generated under the old clustering, but the sandbox's new clustering would have assigned those vectors differently." The sandbox replays vectors through the new clustering, but the vectors themselves were generated by the old world — they are not representative of what would be observed under the new regime.

**Dependency graph:** → vitals measurement → DecisionScore → merge acceptance

**Risk if false:** The sandbox overestimates or underestimates the benefit of a merge because it evaluates a transition the vectors never actually experienced.

**Experiment that would falsify it:** Run the sandbox evaluation and then actually commit the merge; measure how well the sandbox-predicted ΔE correlates with the actual ΔE observed over the next N ticks.

**Priority:** CRITICAL

---

### A-E05 — Recent-Vectors Window Is Representative

**Category:** Experimental

**Statement:** The recent N vectors (default window size from replay horizon of 200) are representative of future observations.

**Location:** `replay_engine.py:79`

**Evidence:** The `recent_vectors` parameter is explicitly a "validation window — recent observations replayed read-only."

**Status:** WEAK — If the environment recently underwent a regime shift, the window may be contaminated with vectors from the old regime, making the sandbox evaluation unrepresentative of the future under the new regime.

**Dependency graph:** → all sandbox vitals → decision policy

**Risk if false:** Merge decisions are made based on a stale or unrepresentative sample of the environment.

**Experiment that would falsify it:** Vary the window size from 10 to 500; measure the correlation between sandbox-predicted ΔE and actual ΔE.

**Priority:** HIGH

---

### A-E06 — Four Regimes + Four Sensors Are Sufficiently Complex

**Category:** Experimental

**Statement:** The C7 Sensorium with 4 regimes and 4 entangled linear sensors is a sufficiently challenging testbed for representation learning.

**Location:** `environment.py:96-102, 216-221`

**Evidence:** The environment has exactly 4 regimes (CALM_DAY, CALM_NIGHT, STORM, FOG) and 4 sensors (three mostly-pure + one entangled mixture).

**Status:** WEAK — The environment is carefully designed to be solvable by simple linear methods (regimes are at distinct cube corners). Real environments have orders of magnitude more latent states, non-linear interactions, and hierarchical structure.

**Dependency graph:** → all experiments → all benchmark results → generalisability claims

**Risk if false:** The system may appear to work on this toy environment but fail completely on any realistic sensory stream. All conclusions about Program C's efficacy are contingent on this one dataset.

**Experiment that would falsify it:** Add a 5th regime that is a linear combination of existing regimes; measure whether the system discovers it.

**Priority:** HIGH

---

### A-E07 — Relaxation = 0.25 Produces Realistic Dynamics

**Category:** Experimental

**Statement:** A relaxation rate of 0.25 per tick toward the regime attractor creates realistically smooth dynamics.

**Location:** `environment.py:117`

**Evidence:** `relaxation: float = 0.25`

**Status:** WEAK — No derivation. The rate determines how quickly the hidden state converges to a new regime's attractor after a switch. Combined with drift σ = 0.03, this creates a specific temporal correlation structure. No evidence this matches real-world dynamics.

**Dependency graph:** → environment dynamics → all cognitive measurements

**Risk if false:** The system's performance is tuned to this specific relaxation rate. Faster/slower relaxation would degrade performance unpredictably.

**Experiment that would falsify it:** Sweep relaxation from 0.05 to 0.95; measure prediction RMSE as a function of relaxation.

**Priority:** LOW

---

### A-E08 — 5,000 Ticks Is Sufficient

**Category:** Experimental

**Statement:** A 5,000-tick simulation is long enough for the system to converge and demonstrate learning.

**Location:** `configs/baseline.json:num_ticks=5000`

**Evidence:** The R1 ablation and all benchmark configurations use 5,000 ticks. The environment has 4 regimes with 0.75-0.90 dwell, so there are ~500-1,250 regime transitions in 5,000 ticks.

**Status:** WEAK — 5,000 ticks may be sufficient for the toy environment but is likely insufficient for any environment with more regimes or longer dwell times.

**Dependency graph:** → all experimental results → conclusions about learning

**Risk if false:** The system appears to converge simply because it has seen everything the toy environment has to offer. In a richer environment, it would never converge.

**Experiment that would falsify it:** Run to 50,000 ticks; measure whether prediction RMSE continues to improve or plateaus.

**Priority:** MEDIUM

---

### A-E09 — Noise σ = 0.05 Is Representative

**Category:** Experimental

**Statement:** Gaussian sensor noise with σ = 0.05 is a representative noise level.

**Location:** `environment.py:228`

**Evidence:** `noise_sigma: float = 0.05`

**Status:** WEAK — The noise level is tuned. The ablation report uses both 0.01 and 0.15, suggesting the authors recognise it is a free parameter. The R3F1 experiment uses 0.15, which differs from the default 0.05.

**Dependency graph:** → sensor reliability → all downstream measurements

**Risk if false:** Results at σ=0.05 may not transfer to other noise levels. The ablation shows no significant difference between 0.01 and 0.15, but the CI is wide.

**Experiment that would falsify it:** Sweep σ from 0.01 to 0.50; measure prediction RMSE.

**Priority:** LOW

---

### A-E10 — R3F1 Experimental Design Is Valid

**Category:** Experimental

**Statement:** The R3F.1 experiment (comparing ΔS vs ΔE as proposal ranking signals) has sufficient power and valid design to produce actionable conclusions.

**Location:** `research/experiments/R3F1_preregistration.md`

**Evidence:** The preregistration document identifies validity threats: "Counterfactual ground truth is noisy — held-out window may be too short"; "ΔS and ΔE are correlated — ΔE is a linear combination"; "Single dataset — results may not generalise."

**Status:** WEAK — The experiment's own preregistration identifies three threats to validity. The correlation between ΔS and ΔE (since ΔE includes ΔS with weight 2.0) means the hypothesis has limited power to discriminate.

**Dependency graph:** → experiment R3F1 results → conclusions about replay objective

**Risk if false:** The experiment may produce an inconclusive result (as the ablation did for FreeEnergy), wasting resources without advancing understanding.

**Experiment that would falsify it:** None — this is a meta-assumption about experimental validity. The experiment itself tests the hypothesis.

**Priority:** MEDIUM

---

### A-E11 — Prediction RMSE Is a Meaningful Primary Metric

**Category:** Experimental

**Statement:** Root-mean-square prediction error is an adequate primary metric for cognitive progress.

**Location:** `ablation_report.md:34`

**Evidence:** PredictionRMSE is the only measurable primary metric. The R1 ablation notes 5 of 6 primary metrics are unavailable.

**Status:** WEAK — PredictionRMSE captures spatial prediction error but does not measure retention, generalisation, transfer, or rare-event recall. The system could score well on RMSE while having no long-term memory or ability to generalise.

**Dependency graph:** → all benchmark conclusions → Program C progress evaluation

**Risk if false:** The system appears to improve (RMSE falls) while actually suffering from catastrophic forgetting of regimes that have not been visited recently.

**Experiment that would falsify it:** Introduce a regime → remove it for 2000 ticks → reintroduce it; measure whether prediction error on reintroduction matches the initial learning curve.

**Priority:** HIGH

---

### A-BE01 — Bayesian Beta-Bernoulli Edge Weight Models Confidence

**Category:** Bayesian/Living Edge

**Statement:** Beta(α, β) posterior mean accurately represents the confidence in a knowledge graph edge.

**Location:** `living_edges.py:87-96`

**Evidence:** `µ_w = α / (α + β)`, confidence thresholds at 0.90/0.70/0.40. This is a standard conjugate Bayesian model.

**Status:** EVIDENCE SUPPORTED — Beta-Bernoulli is the standard conjugate model for binary outcomes. The mathematical framework is correct.

**Dependency graph:** → confidence tiers (CERTAIN/PROBABLE/UNCERTAIN/CONTESTED) → edge status

**Risk if false:** Low — the Bayesian model is mathematically sound. The risk is in the threshold choices (0.90/0.70/0.40), not the model structure.

**Experiment that would falsify it:** Show that Beta posterior mean does not calibrate with empirical accuracy (already shown for the overall system by the PI review).

**Priority:** LOW

---

### A-BE02 — Update Lambda = 0.15 Is Appropriate for Edge Weights

**Category:** Bayesian/Living Edge

**Statement:** The asymptotic weight update rate λ=0.15 is appropriate for edge reinforcement and challenge.

**Location:** `living_edges.py:147`

**Evidence:** `new_w = current_w + λ_upd * (1.0 - current_w)` for reinforce; `new_w = current_w - λ_upd * current_w` for challenge.

**Status:** SPECULATION — No sensitivity analysis. The rate determines how quickly edge weights converge toward 0 or 1.

**Dependency graph:** → asymptotic weight → confidence evolution → edge status

**Risk if false:** Too high: weights swing wildly on single interactions. Too low: weights are too slow to reflect genuine evidence.

**Experiment that would falsify it:** Sweep λ from 0.01 to 0.50; measure edge weight convergence to ground-truth edge existence.

**Priority:** LOW

---

### A-BE03 — Confidence Thresholds Are Epistemically Meaningful

**Category:** Bayesian/Living Edge

**Statement:** The thresholds 0.90/20-evidence/0.05-challenge (CERTAIN), 0.70/5-evidence (PROBABLE), 0.40 (CONTESTED) map to epistemically meaningful confidence tiers.

**Location:** `living_edges.py:107-114`

**Evidence:** Hardcoded decision rules for CERTAIN, PROBABLE, CONTESTED, UNCERTAIN status.

**Status:** SPECULATION — No calibration study exists. The PI review shows `CERTAIN` on hallucinated content (soul_test_report.md Q6), proving the thresholds do not guarantee calibration.

**Dependency graph:** → confidence tier reported to user → credibility of the system

**Risk if false:** The system reports `CERTAIN` on false information — the Constitution's central promise ("uncertainty is honest") is violated. The PI review found exactly this.

**Experiment that would falsify it:** EXP-1 from PI Review: reliability diagram / ECE over ≥200 mixed queries.

**Priority:** CRITICAL

---

### A-BE04 — Asymptotic Weight Default 0.7 Is Neutral

**Category:** Bayesian/Living Edge

**Statement:** The default asymptotic weight of 0.7 for new edges is an appropriate starting value.

**Location:** `living_edges.py:48`

**Evidence:** SQL table schema: `asymptotic_weight REAL DEFAULT 0.7`

**Status:** SPECULATION — 0.7 is slightly above neutral (0.5), suggesting a slight positive bias for newly created edges. No justification.

**Dependency graph:** → initial edge weight → initial confidence → first reinforcement/challenge dynamics

**Risk if false:** New edges start with a positive bias, potentially causing premature confidence in unverified relationships.

**Experiment that would falsify it:** Sweep default weight from 0.5 to 0.9; measure false-positive edge rate.

**Priority:** LOW

---

## Dependency Graph Summary

```
A-IT01 (conditional independence)
  → A-IT03 (symmetric prior)
    → A-N01 (Dirichlet smoothing)
      → P(s|c) chain
        → A-IT02 (0·log0)
        → A-N02 (re-normalisation)
      → A-IT04 (surprisal ceiling)
        → A-CA05 (EWMA alphas)
        → A-CA06 (CPI weights)
      → A-S01 (spherical clusters)
        → A-S02 (Markov-1)
          → A-E03 (Markov-1 entropy)
      → A-CA02 (energy proxy)
        → A-E01 (energy minimization improves prediction)
      → A-CA01 (lower is better)
        → A-E04 (sandbox correctness)
      → A-S03, A-S04, A-S05 (noise models)
        → A-E06, A-E07, A-E08, A-E09 (experimental design)
      → A-CA03 (fracture threshold)
      → A-CA04 (half-maturity)
      → A-O03 (fracture sufficient)
      → A-O01 (concept = label)
      → A-O02 (substrates interchangeable)
      → A-CA09 (probation testing)
      → A-O05 (hand-authored scaffolding)
      → A-O07 (symbol grounding)

Cross-cutting:
A-O05 → A-O08 → A-O06 (terminology → self-model)
A-BE03 (confidence calibration) ← PI Review verdict
A-CA02 (energy proxy) → A-E01 (ablation result)
A-IT05 (concept cost) → A-CA09 (probation)
```

---

## Top 20 Most Dangerous Assumptions (Ranked by Expected Information Gain if Falsified)

Expected information gain = (falsification impact on thesis) × (cheapness of test) × (unambiguity of outcome). Each scored 1-10. Higher = more critical to test.

| Rank | ID | Statement | Impact | Cost | Clarity | EIG | Falsification Experiment |
|------|-----|-----------|--------|------|---------|-----|--------------------------|
| 1 | **A-CA02** | E = λH + μS + νA is a valid free-energy proxy | 10 | 3 | 8 | **240** | Compare proxy E vs true variational free energy for a tractable generative model |
| 2 | **A-O05** | Hand-authored scaffolding supports development | 10 | 1 | 10 | **200** | EXP-0: paraphrase benchmark (1 day) — predicted to collapse to 4.0/10 |
| 3 | **A-O07** | Hand-authored ontology grounds meaning | 10 | 2 | 9 | **180** | Present novel object; measure integration (none) |
| 4 | **A-E01** | Free energy minimization improves prediction | 9 | 2 | 9 | **162** | Already done: R1 ablation shows no significant improvement (RMSE 0.2991 vs null 0.2951) |
| 5 | **A-O01** | "Concept" = string label | 9 | 1 | 10 | **90** | Query engine for concept properties after "crystallisation" — none exist |
| 6 | **A-O03** | Fracture is sufficient for regime detection | 8 | 3 | 9 | **216** | Gradual drift regime; measure whether fracture ever triggers |
| 7 | **A-CA01** | Lower is better for all vitals (ignores exploration) | 9 | 4 | 8 | **288** | Non-stationary environment needing periodic high-surprise exploration |
| 8 | **A-IT01** | Conditional independence given context | 7 | 3 | 8 | **168** | Order-(k+1) sequence; measure prediction error increase |
| 9 | **A-BE03** | Confidence thresholds are epistemically meaningful | 9 | 1 | 10 | **90** | EXP-1: reliability diagram / ECE over 200+ mixed queries |
| 10 | **A-E04** | Replay sandbox correctly simulates post-merge state | 7 | 4 | 9 | **252** | Compare sandbox-predicted ΔE vs actual post-merge ΔE over next N ticks |
| 11 | **A-IT04** | Surprisal ceiling at 5.0 bits normalises accuracy | 7 | 1 | 9 | **63** | Run with 64-symbol vocabulary; check if accuracy exceeds 1.0 |
| 12 | **A-IT05** | log₂(N+1) concept definition cost | 7 | 3 | 7 | **147** | Compare concept-birth rate vs ground-truth regime count; measure false positives |
| 13 | **A-S01** | Spherical clusters (K-Means) | 7 | 3 | 8 | **168** | Correlated Gaussian mixture environment; measure cluster-to-regime ratio |
| 14 | **A-S02** | Markov order 1 for cluster transitions | 7 | 3 | 8 | **168** | Two-step mandatory regime transition; measure H increase |
| 15 | **A-CA06** | CPI weights (0.40/0.30/0.20/0.10) are appropriate | 7 | 2 | 7 | **98** | Scenario where compression improves but accuracy flat; CPI still improves? |
| 16 | **A-CA09** | Probation testing adequately validates concepts | 6 | 3 | 8 | **144** | Measure false-positive/negative rates of probation vs ground-truth regimes |
| 17 | **A-E06** | Four regimes + four sensors are sufficiently complex | 6 | 2 | 6 | **72** | Add 5th linear-combination regime; measure discovery |
| 18 | **A-O04** | Curiosity gaps defined by hand-authored ontology | 6 | 2 | 9 | **108** | Present novel domain not in ontology; measure inquiry goal generation |
| 19 | **A-O02** | Two belief substrates are interchangeable | 6 | 2 | 10 | **120** | Run same sequence through both; compare prediction error trajectories |
| 20 | **A-E11** | Prediction RMSE is a meaningful primary metric | 6 | 4 | 7 | **168** | Remove then reintroduce a regime; measure retention via reintroduction error |

### Methodology for EIG Score

```
EIG = Impact × (11 - Cost) × Clarity
```

Where:
- **Impact** (1-10): How much of the Program C thesis this assumption kills if falsified
- **Cost** (1-10): Effort to run the falsification experiment (1 = 1 day, 10 = 6+ months)
- **Clarity** (1-10): How unambiguous the outcome would be (10 = binary pass/fail, 1 = ambiguous)

### Key Findings

1. **The top 3 assumptions (A-CA02, A-O05, A-O07) are existential risks to the Program C thesis.** If any is falsified, the core claim of a "developing synthetic mind" collapses.

2. **Assumption A-E01 is already empirically CONTRADICTED** by the R1 ablation report (72 experiments, no significant improvement from free-energy policy). The C8 decision architecture has zero measurable benefit.

3. **Assumption A-BE03 is already empirically CONTRADICTED** by the PI review (soul_test_report.md Q6: CERTAIN on hallucinated content). The confidence tiers are not calibrated.

4. **Observability gap:** 5 of 6 primary metrics defined in the R1 ablation are not measurable (HeldOutPredictiveLogLikelihood, RareEventRecall, KnowledgeRetentionScore, GeneralizationScore, TransferScore). The system cannot measure its own claimed capabilities.

5. **Circular dependency cluster:** The concept formation pipeline (A-IT05 → birth cost → probation → concept → new exceptions) creates a feedback loop that can oscillate without ever converging to a stable ontology — and the system has no way to detect this.

---

*End of Assumption Ledger. Total records: 47 assumptions across 8 categories.*

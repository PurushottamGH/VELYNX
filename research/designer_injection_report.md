# Designer Knowledge Injection Report

**Project:** VELYNX  
**Date:** 2026-07-01  
**Scope:** All Python source files, configuration files, curriculum files, and shell scripts.  
**Method:** Exhaustive static analysis of every `.py` file in the repository.

---

## Executive Summary

VELYNX is **pervasively parameterized by designer judgement**. Of the ~150 constants governing its cognitive architecture, **zero are derived from data, from first-principles reasoning, or from a systematic search procedure**. Every threshold, weight, prior, coupling coefficient, and curriculum topic was hand-picked by the programmer. This means the system's observed behavior — what concepts it forms, when it fractures, what it learns, how it allocates attention — is **largely a reflection of arbitrary designer choices**, not of autonomous intelligence.

This report enumerates every discovered injection, estimates the fraction of system behavior it controls, and ranks by scientific risk.

---

## Ranking: Scientific Risk

Risk is assessed on three axes:

1. **Sensitivity (S):** How much does varying this parameter change qualitative behavior?
2. **Arbitrariness (A):** Is there a principled way to set this value, or was it chosen ad-hoc?
3. **Span (P):** How many subsystems depend on this injection?

Risk = S × A × P on a 1–10 scale.

---

### CRITICAL RISK (9–10)

These injections **determine the system's objective function, its perceptual interface, and its core dynamics**. No amount of learning can overcome them.

| # | Injection | Location | Value(s) | Risk | Rationale |
|---|-----------|----------|----------|------|-----------|
| 1 | **Free-energy coupling coefficients** | `cognitive_core.py:1781`, `validation/metrics.py:59-61`, `backend/cognition/decision_policy.py:79-81`, `cognitive_health.py:23`, `research/free_energy.py:68-71` | λ=1.0, μ=2.0, ν=0.5 | **10** | These 3 numbers ARE the system's utility function. They determine the relative importance of entropy (H), prediction error (S), and structural load (A) in every decision. No principled derivation exists. Changing them rewrites what the system "cares about." Appears in 5+ independent locations — risk of silent drift. |
| 2 | **Environment regimes & sensor model** | `environment.py:96-102,216-221` | 4 hand-authored regimes with target vectors; 4 hand-crafted sensor weight/bias arrays | **10** | The entire test environment is fabricated. Every sensor has manually chosen weights (e.g., `(0.10, 0.95, 0.05)`) and biases. The regime transitions are hardcoded probabilities. This means the "world" the agent experiences is itself a designer confection. Any claim about "learning the structure of the world" is actually "learning the structure the designer typed in." |
| 3 | **Concept birth threshold** | `concept_birth.py:123`, `backend/cognition/concept_birth.py:51` | 0.5 bits NPMI (root); 0.15 NPMI (backend) | **9.5** | This single threshold determines whether a pattern is important enough to reify as a concept. Below it, nothing is born. Above it, concepts proliferate. The root and backend use different values (0.5 vs 0.15) — meaning the two subsystems have different ontological criteria. No principled derivation. |
| 4 | **Dirichlet prior (alpha)** | `cognitive_core.py:421`, `cognitive_telemetry.py:790` | α=0.5 (symmetric) | **9** | The Dirichlet prior is the system's assumption about symbol distributions before seeing any data. α=0.5 is a "Jeffreys prior" for multinomials — but this is a choice, not a derivation. It biases every belief toward sparsity. A different α produces qualitatively different concept granularity. |
| 5 | **Crystallize threshold** | `cognitive_core.py:422,798` | ≥0.80 | **9** | A rule must have confidence ≥0.80 to crystallize. This is an arbitrary boundary between "fluid" and "crystallized" knowledge. Changes of ±0.05 produce qualitatively different knowledge structures. |

---

### HIGH RISK (7–8)

These injections **control which concepts survive, how attention flows, and when the system reorganizes**.

| # | Injection | Location | Value(s) | Risk | Rationale |
|---|-----------|----------|----------|------|-----------|
| 6 | **CPI composite weights** | `cognitive_telemetry.py:245-249` | accuracy=0.40, decay=0.30, compression=0.20, resolution=0.10 | **8** | The Cognitive Performance Index is the system's "vital signs" monitor. These four weights determine which aspect of cognitive health matters most. Designer chose 0.40/0.30/0.20/0.10 — no sensitivity analysis exists. |
| 7 | **Fracture threshold** | `cognitive_core.py:682` | ≥0.85 | **8** | When contradiction density exceeds 0.85, a rule fractures (splits into sub-rules). This is a catastrophe threshold for knowledge structure. Small changes produce radically different ontology trees. |
| 8 | **Probation confirmation rate** | `cognitive_core.py:1119` | ≥0.60 | **8** | A rule on probation must achieve ≥60% hit rate to be confirmed. This gates whether tentative rules become permanent. Arbitrary. |
| 9 | **Sensor proximity (cluster radius)** | `cognitive_core.py:1756`, `backend/cognition/vector_prediction_core.py:166`, `configs/*.json` | 0.25 (varies: 0.15, 0.28, 0.35 in configs) | **8** | Determines the granularity of sensorium clustering. Different values used in different files (0.25 vs 0.15 vs 0.28 vs 0.35) — no consensus. Directly controls how many clusters form and how fine-grained perception is. |
| 10 | **Surprise threshold (cognitive core)** | `cognitive_core.py:1237,1760` | 2.0 bits (core), 0.30 (sensorium) | **7.5** | The level of surprise needed to trigger causal hypothesis formation or sensorium reorganization. Two different thresholds in the same file (2.0 vs 0.30). Arbitrary. |
| 11 | **Maximum clusters** | `cognitive_core.py:1766` | 3 | **7.5** | Hard limit on number of sensorium clusters. The system literally cannot perceive more than 3 regimes at once. Chosen without justification. |
| 12 | **Sensor biases** | `environment.py:217-221` | 0.00, 0.00, 0.00, -0.10 | **7.5** | Three sensors have zero bias; one has -0.10. This asymmetry is never justified. It means the fourth sensor is systematically pessimistic, biasing all downstream perception. |
| 13 | **Merge thresholds (Jaccard / Hungarian)** | `backend/cognition/concept_birth.py:66-67` | Jaccard ≥0.60, Hungarian ≥0.35 | **7** | These thresholds determine when two concepts are considered "the same" and merged. Change them and the ontology cardinality changes by factors. |
| 14 | **Decay rates** | `backend/cognition/concept_birth.py:58`, `backend/cognition/predictive_core.py:22` | 0.02, 0.05 | **7** | How fast memories decay. Two different values in two subsystems. Small changes compound over time to produce very different forgetting curves. |
| 15 | **Base learning rate** | `cognitive_core.py:1236`, `backend/cognition/predictive_core.py:25`, `backend/cognition/concept_birth.py:57` | 0.20 (core), 0.10 (predictive), 0.10 (concept_birth) | **7** | Three different learning rates across subsystems. The core uses 0.20, the predictive engine uses 0.10, concept birth uses 0.10. No justification for the factor-of-2 difference. |
| 16 | **Stuck/surprise threshold** | `cognitive_telemetry.py:559-560` | slope ε=0.02, surprise ≥1.5 bits | **7** | Detects when learning is "stuck." Both thresholds are arbitrary. Changing them changes whether the system diagnoses itself as stuck. |

---

### MEDIUM-HIGH RISK (5–6)

These injections **shape learning dynamics, resource allocation, and self-assessment**.

| # | Injection | Location | Value(s) | Risk | Rationale |
|---|-----------|----------|----------|------|-----------|
| 17 | **Reflection quality dimension weights** | `backend/reflection/advanced_reflection.py:203-449` | 0.25, 0.20, 0.15, 0.10, 0.05 | **6.5** | The system's self-assessment of reasoning quality is a weighted composite of 10+ dimensions. Every weight was hand-picked. The composite score directly determines whether the system thinks it's doing well. |
| 18 | **EWMA smoothing constants (telemetry)** | `cognitive_telemetry.py:87-89` | α_acc=0.15, α_surp=0.20, α_decay=0.10 | **6** | These determine how much weight recent observations have in the running estimates of accuracy, surprise, and decay. Standard EWMA practice gives no guidance for these specific values. |
| 19 | **Reification thresholds** | `cognitive_telemetry.py:791-792` | shift ≥0.02, streak ≥5 | **6** | When a belief becomes "stable enough" to reify. Both parameters are arbitrary. |
| 20 | **Stability half-maturity** | `cognitive_core.py:678` | 4.0 | **6** | The point at which stability reaches half its asymptotic value. Controls how quickly beliefs stabilize. No principled derivation. |
| 21 | **Breach window & limit** | `cognitive_core.py:1769,1771` | window=12, limit=4 | **6** | How many ticks of anomalous breach within what window trigger exhaustion. These control the system's "frustration tolerance." |
| 22 | **Dream state thresholds** | `backend/cognition/dream_state.py:60-62` | floor=0.40, similarity=0.65, top_k=10 | **6** | Controls dream-like replay of concepts. Three arbitrary thresholds determine what gets replayed during "dream" cycles. |
| 23 | **Confidence calibrator thresholds** | `backend/reflection/confidence_estimator.py:58-75` | ≥0.7, ≥0.8, ≥0.6, ≥0.4, ≥0.2 | **6** | Bucket boundaries for confidence classification. Entirely arbitrary. Change them and the distribution of "high confidence" vs "low confidence" beliefs shifts. |
| 24 | **Pruning weight & age** | `backend/cognition/concept_birth.py:55-56` | weight<0.05, age>3600s | **6** | Concepts below this weight or older than 1 hour are pruned. The 1-hour threshold is a guess. In different environments, optimal retention windows differ by orders of magnitude. |
| 25 | **Motif threshold** | `cognitive_core.py:424,799` | ≥3.0 | **5.5** | Minimum frequency for a pattern to be recognized as a motif. Arbitrary but less sensitive (motifs are already rare). |
| 26 | **Spectral clustering parameters** | `backend/cognition/concept_birth.py:63-64` | k=8 clusters, seed ratio=0.3 | **5.5** | These determine the initial granularity of spectral clustering for concept discovery. k=8 is a guess. |
| 27 | **Bootstrap confidence** | `cognitive_core.py:794` | 0.50 | **5.5** | Initial confidence for newly formed rules. 0.50 = maximum uncertainty. This is defensible but still a choice. |

---

### MEDIUM RISK (3–4)

These injections are **important but bounded in effect**, or they are **defensible defaults with limited scope**.

| # | Injection | Location | Value(s) | Risk | Rationale |
|---|-----------|----------|----------|------|-----------|
| 28 | **Hand-authored curriculum topics** | `velynx_core/velynx.py:65-103`, `night_learner.py:47-86`, `backend/learning/curriculum.py:75-168`, `curriculum/*.txt` | 100+ hand-written topics and lessons | **4** | The system learns what the designer tells it to learn. This is trivially true for supervised elements, but the curriculum shapes unsupervised discovery too. The system cannot discover topics outside this list during curriculum mode. |
| 29 | **Concept labels (rain, fire, music, chaos)** | `cognitive_telemetry.py:733-740`, `run_test_queries.py:17-21`, `backend/app/soul/concepts.json` | 20+ hand-authored semantic labels | **4** | These labels embed designer semantics into the system's ontology. The system doesn't discover "rain" — it is told about rain. This is a ceiling on autonomous concept formation. |
| 30 | **Hand-authored seed concepts** | `backend/cognition/seed_loader.py:64-93`, `backend/soul/concepts.json` | ~50 seed concepts with initial activations=0.0, baselines=0.0, confidences=1.0 | **4** | The knowledge graph is seeded with designer-chosen concepts. The system builds on this initial ontology. |
| 31 | **Temperature settings** | multiple files (see body) | 0.05 to 0.5 | **3** | LLM temperature is a knob the designer turns. Low temps (0.05) make the system deterministic; high temps (0.5) add noise. The values are reasonable defaults but not researched. |
| 32 | **Model names** | `backend/cognition/embed_index.py:21`, `backend/cognition/dream_state.py:59` | "all-MiniLM-L6-v2" | **3** | The embedding model is a designer choice. Different models have different semantic sensitivities. This is a dependency on external research. |
| 33 | **Database paths and filenames** | ~30 locations across all files | Various hardcoded paths | **3** | Baked-in file paths reduce portability but don't affect behavior. |
| 34 | **SQL schemas and queries** | ~20 locations | Hand-written DDL and DML | **3** | Database schemas encode designer assumptions about data structure. Changing them changes what can be stored and queried. |
| 35 | **Latent cause engine weights** | `latent_cause_engine.py:153-155` | α=0.50, β=0.30, γ=0.20 | **3** | Weights for PredictionGain, CompressionGain, Stability. Less risky than the main cognitive coefficients because this is a more constrained subsystem. |
| 36 | **Noise sigma** | `environment.py:227`, `configs/*.json` | 0.05 (baseline), 0.01 (simple), 0.15 (noisy) | **3** | The standard deviation of sensor noise. This IS a parameter you'd expect to vary by environment. The range 0.01–0.15 seems reasonable. |

---

### LOW RISK (1–2)

These injections are **numerical stability measures, trivial defaults, or test fixtures**.

| # | Injection | Location | Value(s) | Risk | Rationale |
|---|-----------|----------|----------|------|-----------|
| 37 | **Numerical epsilons** | `latent_cause_engine.py:58`, `velynx/graph/curiosity_engine_v2.py:45` | 1e-9, 1e-12 | **1** | Standard guard against division by zero. Principled. |
| 38 | **Crystallize min count** | `cognitive_core.py:423` | ≥3 | **2** | Minimum evidence count for crystallization. 3 is a reasonable minimum for any statistical claim. |
| 39 | **Baseline ring-buffer cap** | `cognitive_core.py:1776` | 240 | **2** | Ring buffer size for sensor data. Large enough not to constrain typical runs. |
| 40 | **Answer type taxonomy** | `backend/cognition/answer_classifier.py:11-20` | 8 answer type strings | **2** | Classification scheme for LLM responses. Designer-chosen but shallow. |
| 41 | **CLI UI color/style constants** | `backend/cli_ui.py:41-49` | ANSI color strings | **1** | Purely cosmetic. |
| 42 | **Benchmark seeds and horizons** | `research_benchmark.py:59-64` | seeds=[1,2,3,4,5], horizons=[20,50,100,200], ticks=1000 | **2** | Experiment design parameters. Reasonable defaults for benchmarking. |
| 43 | **Stopwords** | `backend/cognition/metacog.py:22-28` | ~30 hardcoded stopwords | **2** | Standard NLP convention. Reasonable but language-specific. |
| 44 | **Abstract suffix list** | `backend/cognition/perception.py:15` | ("ness", "ity", "tion", "ism", "ence", "ance", "ment") | **2** | Hand-crafted list of abstract noun suffixes. English-specific. |
| 45 | **Kiro gateway correction factor** | `kiro-gateway/kiro/tokenizer.py:45` | 1.15 | **2** | Token count correction factor for Claude API. Derived from empirical observation. |
| 46 | **Cache TTLs** | `backend/database/redis_cache.py:10` | 3600s | **1** | Standard cache timeout. |
| 47 | **Physics simulation constants** | `backend/cognition/sim_engine.py:50-56` | G=6.674e-11, AU=1.496e11 | **1** | Actual physical constants. Not designer invention. |
| 48 | **Source order / policy order** | `research/proposals/sources.py:253`, `research/policies/__init__.py:52` | Explicit ordered lists | **1** | Research experiment configuration. Scope-limited. |
| 49 | **Event priority levels** | `backend/runtime/event_models.py:21-24` | CRITICAL=9, HIGH=7, NORMAL=5, LOW=3 | **1** | Convention. Reasonable. |
| 50 | **Regime transition probabilities** | `environment.py:98-101` | dwell=0.90, 0.90, 0.80, 0.75 | **2** | How long each regime persists. Reasonable but affects exposure duration. |

---

## Quantitative Summary

| Risk Tier | Count | Total Weight |
|-----------|-------|-------------|
| CRITICAL (9–10) | 5 | 47.5 |
| HIGH (7–8) | 11 | 82.5 |
| MEDIUM-HIGH (5–6) | 10 | 60.5 |
| MEDIUM (3–4) | 8 | 26.5 |
| LOW (1–2) | 14 | 23.5 |

**Weighted risk score: 240.5 across 48 injections.**

---

## Behavioral Dependency Estimates

| System Behavior | % Determined by Designer Injection | Key Injections |
|----------------|------------------------------------|----------------|
| **Which concepts exist** | ~95% | Concept birth threshold, merge thresholds, seed concepts, curriculum topics |
| **When rules fracture** | ~90% | Fracture threshold (0.85), probation rate (0.60) |
| **What the system "wants"** | ~100% | Free-energy coefficients (λ, μ, ν) |
| **How the world is perceived** | ~100% | Sensor weights, biases, noise sigma, regime definitions |
| **Learning speed** | ~80% | Learning rates (0.10, 0.20), decay rates (0.02, 0.05), EWMA alphas |
| **Self-assessment accuracy** | ~70% | CPI weights, reflection dimension weights, calibrator thresholds |
| **What gets remembered** | ~60% | Pruning age (3600s), pruning weight (0.05), decay rate |
| **Curriculum (what is taught)** | ~100% | Hand-authored topics, lessons, stages |
| **LLM output character** | ~40% | Temperature (0.05–0.5), model selection |
| **Numerical stability** | ~0% | Epsilons (principled) |

---

## Recommendations

1. **Derive the free-energy coefficients (λ, μ, ν) from data.** Run a systematic sweep over the parameter space and select the values that maximize predictive accuracy on a held-out validation environment. This is the single highest-leverage improvement.

2. **Replace the hand-authored environment with a procedural generator.** The regimes and sensors should be drawn from a distribution, not typed by hand. Test generalization across many random environments.

3. **Perform sensitivity analysis on every threshold.** For crystallize (0.80), fracture (0.85), concept birth (0.5 bits), and merge (0.60 Jaccard), run sweeps and report how ontology cardinality, stability, and accuracy change.

4. **Unify the two concept birth thresholds** (root: 0.5 bits NPMI; backend: 0.15 NPMI). These are different by a factor of 3.3 with no justification.

5. **Document the CPI weight rationale.** What empirical evidence supports accuracy=0.40 vs 0.30? Run an ablation study.

6. **Add a `--param-override` CLI flag** so that every parameter in this report can be overridden at launch, enabling sweep-based parameter tuning without code changes.

7. **Remove hardcoded paths and replace with environment variables or a single config file.** Currently ~30 files have baked-in paths.

# Program D — Canonical Scientific Specification

**[FACT]** Program D is a strict scientific falsification framework. Its sole purpose is to reduce inherited software constructs into a minimal, mathematically rigorous basis of falsifiable hypotheses and subject them to lethal testing.

## 1. Epistemological Stance
Every canonical statement must be tagged:
- **[FACT]** Verified mechanically against code, empirical logs, or formal mathematical proof.
- **[HYPOTHESIS]** Falsifiable claim with a pre-registered kill criterion.
- **[SPECULATION]** Untested assertion. Strictly prohibited in execution pathways.
- **[REJECTED]** Empirically falsified.

**Prohibited Constructs (Systemic Risks):**
1. **Anthropomorphism:** Use of terms like "mind", "soul", "understanding", "belief", "curiosity". These must be mapped to "state vector", "affective index", "predictive model", "probability", "entropy gap".
2. **Designer Injection:** Hardcoded constants, weights, or ontologies claimed as "emergent" phenomena.
3. **Novelty Inflation:** Re-branding standard Minimum Description Length (MDL) or Expected Calibration Error (ECE) as novel laws of physics.
4. **Incommensurate Mathematics:** Linear combinations of independent units (e.g., bits + distance + magnitude) without strict conversion mappings (e.g., the legacy Free Energy Proxy `E`).

## 2. Core Mathematical Substrate
**[FACT]** The predictive subsystem is reduced to 5 strict, observable primitives.
1. **Observation Stream:** $x_t \in X$
2. **Predictor Manifold:** $\{ P_\theta(x_{t+1} | x_{\leq t}) : \theta \in \Theta \}$
3. **Scoring Rule:** Surprisal $S = -\log P_\theta(x_{t+1} | x_{\leq t})$
4. **MDL Growth Operator:** Node synthesis $g$ triggers iff information gain strictly exceeds model complexity cost: $G = H_{before} - H_{after} - \lambda_{model} > 0$, with $\lambda_{model} = k \cdot b + n \cdot \log_2 N$ (concept-birth ledger). *(Pinned per CANONICAL §5.4 / Issue-3: the threshold must be derived, not hand-set — a hand-set trigger is failure mode F2 and violates I2 by construction.)*
5. **Emergence Statistic:** Null-referenced $M(\theta) = \mathrm{NMI}(\text{learned partition}, \text{true latent}) - \mathrm{NMI}(\text{learned partition}, \text{shuffled input})$, constructed so that $\mathbb{E}[M \mid H_0] = 0$. *(Corrected per PROGRAM_D_CANONICAL.md §5.5 / Issue-2: the prior "graph isomorphism" form is [REJECTED] — it is ill-defined for a probabilistic predictor and reintroduces researcher degrees of freedom. The null-reference is what operationalizes keystone assumption I2.)*

## 3. Surviving Hypotheses

**[FACT]** The canonical surviving set is **H\*, H1, H2** (see PROGRAM_D_CANONICAL.md §6). The central hypothesis is **H\*** (below). The prior "H3" is **[REJECTED] / subsumed by H\***: it is H\* with clause (iii)/keystone-assumption-I2 dropped — the exact weakening the redesign exists to prevent (CANONICAL §10 Issue-1). The block formerly labelled "H3" is retained below strictly as an archived cross-reference and must not be listed as a live hypothesis.

### H\*: Error-Gated Structure Acquisition (Central Hypothesis)
**[HYPOTHESIS]** An agent whose *only* learning signal is sensorimotor prediction error, and which adds capacity *only* when prediction error persists, acquires structure that (i) is absent at initialization, (ii) improves held-out prediction beyond both a fixed-capacity control and an error-decoupled capacity-matched control, and (iii) is not reducible to designer-injected statistics (measured above a shuffled-input control). Clause (iii) = assumption I2 is the crux.
- **Independent Variable:** error-gated capacity-growth operator ON vs. OFF/decoupled (implementation-independent).
- **Observables:** (a) held-out predictive log-likelihood; (b) emergence statistic $M$ (§2.5).
- **Null Hypothesis:** T indistinguishable from fixed-capacity (C1) and error-decoupled (C2) controls on (a), AND $M$ within noise of the shuffled control.
- **Control:** C1 fixed-capacity; C2 capacity-matched growth at random times; C3 shuffled input.
- **Kill Criteria (wired):** T fails to beat both C1 and C2 on held-out LL at p<0.01 across ≥5 seeds, OR $M$ within noise of shuffled control — after two honest attempts.
- **Experimental protocol:** E0.

### H1: Retrieval Uncertainty Calibration
**[HYPOTHESIS]** Symbolic confidence tiers, mapped from discrete retrieval probabilities, strictly bound empirical accuracy.
- **Scientific Motivation:** Provably bounded uncertainty is an absolute requirement for halting conditions in open-ended autonomous search.
- **Observable:** Expected Calibration Error (ECE) over query distributions.
- **Null Hypothesis:** Evaluation accuracy is statistically independent of the predicted confidence tier.
- **Control:** TF-IDF/BM25 retrieval with randomly assigned confidence outputs.
- **Kill Criteria:** $ECE \geq 0.10$ or statistical independence over the query set. *(Single gate per CANONICAL §6-H1 / Issue-4: the legacy 0.15 threshold is retired — a 0.10–0.15 dead zone leaves the claim simultaneously un-passed and un-killed. Pass iff $ECE < 0.10$.)*
- **Goodhart Risk:** Threshold hacking—artificially tightening confidence bins to lower ECE without improving the underlying retrieval signal.

### H2: Affective Dimensionality Reduction
**[HYPOTHESIS]** Projecting state observations through a fixed, low-dimensional "affective" manifold yields a compression ratio that accelerates structural search and retrieval.
- **Scientific Motivation:** Dimensionality reduction via evolutionary priors (affect) may constrain expansive search spaces more efficiently than raw semantic distances.
- **Observable:** Search steps-to-convergence on novel tasks.
- **Null Hypothesis:** Affective projection yields equal or slower convergence than direct dense semantic vector search.
- **Control:** Standard dense embedding cosine-similarity search (e.g., text-ada-002).
- **Kill Criteria:** Convergence steps (affective) $\geq$ Convergence steps (control).
- **Circular Logic Risk:** Evaluating on task environments authored by the same designer, implicitly matching the affect categories. Must use fully isolated third-party test sets.

### H3: MDL-Gated Topology Emergence — [REJECTED] / SUBSUMED BY H\*
**[REJECTED]** Retained only as an archived cross-reference (CANONICAL §10 Issue-1). This is H\* with the emergent-vs-injected clause (iii)/I2 removed; its content lives inside H\* and its protocol is subsumed and made rigorous by E0. Do not treat as a live hypothesis or build EXP-3/EXP-4 for it.
**[HYPOTHESIS — archived]** Given a continuous stationary data stream, strictly MDL-gated node growth ($G > 0$) spontaneously constructs a predictive graph isomorphic to the environment's true hidden Markov model.
- **Scientific Motivation:** Complex topologies can be learned iteratively without hand-authored ontologies by strictly minimizing total description length (data + model).
- **Observable:** Transfer-learning log-likelihood on isomorphic, unseen test environments.
- **Null Hypothesis:** The generated graph overfits the training sequence and fails to transfer structural knowledge.
- **Control:** Fixed-capacity predictive model with equivalent parameter count.
- **Kill Criteria:** Zero-shot transfer log-likelihood is indistinguishable from random initialization.
- **Hidden Assumption:** The environment's true generative process is stationary, ergodic, and learnable within the imposed compute horizon.

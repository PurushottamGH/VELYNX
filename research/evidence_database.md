# Evidence Database for Program C

**Generated:** 2026-07-01
**Scope:** Comprehensive audit of every neuroscience, ML, predictive processing, developmental robotics, learning rule, plasticity, homeostasis, and energy model concept referenced in the VELYNX codebase.

---

## Table of Contents

1. [Neuroscience Concepts](#1-neuroscience-concepts)
2. [Machine Learning Concepts](#2-machine-learning-concepts)
3. [Predictive Processing / Free Energy Principle](#3-predictive-processing--free-energy-principle)
4. [Developmental Robotics Concepts](#4-developmental-robotics-concepts)
5. [Local Learning Rules](#5-local-learning-rules)
6. [Plasticity Mechanisms](#6-plasticity-mechanisms)
7. [Homeostasis Mechanisms](#7-homeostasis-mechanisms)
8. [Energy Models](#8-energy-models)
9. [Gap Analysis: Concepts NOT in Program C](#9-gap-analysis-concepts-not-in-program-c)
10. [Constitution Compatibility Matrix](#10-constitution-compatibility-matrix)

---

## 1. Neuroscience Concepts

### 1.1 Hebbian Learning ("Fire together, wire together")

- **Original paper:** Hebb, D.O. (1949). *The Organization of Behavior.* Wiley.
- **Formulation:** `Δw_ij = η * x_i * x_j` — If neuron i and neuron j are co-active, the connection between them strengthens.
- **Program C implementation:** `backend/soul/soul_graph.py:512-596` — `apply_plasticity()` increments coactivation counts; once count >= 2, a "co_activated" edge is created in the living graph. Edge reinforcement uses `asymptotic_weight` updates.
- **Biological evidence:** Foundational to LTP; confirmed in hippocampus (Bliss & Lømo, 1973) and cortex. Correlation-based plasticity is well-established.
- **Known limitations:** Pure Hebbian learning is unstable — weights can grow unbounded. Does not explain LTD or spike-timing dependence. Program C uses coactivation counting (rate-based Hebbian), missing temporal ordering.
- **Program C usage:** YES — `soul_graph.py`, `living_edges.py`, `concept_birth.py` (Hebbian forgetting).
- **Constitution conflict:** None. Hebbian learning is consistent with epistemological transparency.

### 1.2 Synaptic Pruning

- **Original paper:** Changeux, J.-P. & Danchin, A. (1976). "Selective stabilisation of developing synapses." *Nature*.
- **Formulation:** Synapses with low activity are eliminated; frequently used connections are stabilized.
- **Program C implementation:** `backend/soul/soul_graph.py:602-654` — `run_sleep_cycle()` implements decay (`asymptotic_weight *= 1.0 - decay_rate`), pruning edges below `prune_threshold`, and deleting orphaned concepts.
- **Biological evidence:** Observed across development (Huttenlocher, 1979), sleep-dependent synaptic downscaling (Tononi & Cirelli, 2003).
- **Known limitations:** Purely weight-threshold based — no activity-dependence, no timing, no competition. Does not model structural plasticity (dendritic spine dynamics).
- **Program C usage:** YES — `soul_graph.py` sleep cycle.
- **Constitution conflict:** None.

### 1.3 Attention (Top-Down Modulation)

- **Original paper:** Treisman, A. & Gelade, G. (1980). "A feature-integration theory of attention." *Cognitive Psychology*. Also: Desimone, R. & Duncan, J. (1995). "Neural mechanisms of selective visual attention." *Annual Review of Neuroscience*.
- **Formulation:** Attention biases processing toward behaviorally relevant stimuli. Program C: `attention_weight = 1.0 - P(s|c)` (precision of residual); attention warps distance metric via dimension weighting.
- **Program C implementation:** `cognitive_core.py:1295`, `backend/cognition/attention_modulator.py:53-60` — `attention_weights()` builds a weight vector with `focus_mult` amplifying attended dimensions and `suppress_floor` damping others.
- **Biological evidence:** Attentional modulation observed throughout cortex (Moran & Desimone, 1985), biased competition model, feature-based attention.
- **Known limitations:** Program C's attention is purely precision-of-prediction, not a full biased-competition or saliency model. No spatial attention, no overt/covert distinction.
- **Program C usage:** YES — `cognitive_core.py`, `attention_modulator.py`, `vector_prediction_core.py`.
- **Constitution conflict:** None.

### 1.4 Memory Systems (Working, Episodic, Semantic)

- **Original paper:** Tulving, E. (1972). "Episodic and semantic memory." *Organization of Memory*. Also: Baddeley, A. & Hitch, G. (1974). "Working memory." *Psychology of Learning and Motivation*.
- **Formulation:** Three memory systems with distinct time-scales and functions.
- **Program C implementation:** `backend/memory/memory_manager.py` — orchestrates episodic (experience with causal links), semantic (dense embedding retrieval), and working memory (session-scoped "RAM").
- **Biological evidence:** Double dissociation in amnesia (Squire, 1992); hippocampal-dependent episodic memory; cortical semantic memory.
- **Known limitations:** Program C's "episodic memory" is a causal event log, not an auto-associative network. No consolidation from hippocampal to cortical systems. Working memory is a simple FIFO.
- **Program C usage:** YES — full memory manager with three subsystems.
- **Constitution conflict:** None. The epistemic constitution mandates source tracing; semantic memory supports this.

### 1.5 Sleep / Replay / Consolidation

- **Original paper:** Wilson, M.A. & McNaughton, B.L. (1994). "Reactivation of hippocampal ensemble memories during sleep." *Science*.
- **Formulation:** Neural activity patterns from waking replay during sleep, driving memory consolidation.
- **Program C implementation:** `backend/cognition/replay_engine.py:1-60` — sandbox simulator rehearsing memory restructuring; `run_sleep_cycle()` in `soul_graph.py` for weight decay/pruning; `backend/cognition/memory_scheduler.py` decides when to consolidate.
- **Biological evidence:** Hippocampal sharp-wave ripples during NREM sleep; replay of place-cell sequences.
- **Known limitations:** Program C's "replay" is a sandbox merge simulation, not reactivation of experience patterns. No distinction between NREM/REM. No systems consolidation.
- **Program C usage:** YES — replay engine, sleep cycle, consolidation scheduler.
- **Constitution conflict:** None.

### 1.6 Working Memory

- **Original paper:** Baddeley, A. (1992). "Working memory." *Science*.
- **Formulation:** Temporary storage and manipulation of information.
- **Program C implementation:** `backend/conversation/working_memory.py:1` — session-scoped "RAM"; `backend/memory/memory_manager.py:162` stores short-lived working memory entries.
- **Biological evidence:** Prefrontal cortex persistent activity (Goldman-Rakic, 1995).
- **Known limitations:** No central executive, phonological loop, or visuospatial sketchpad. Simple key-value store.
- **Program C usage:** YES.
- **Constitution conflict:** None.

### 1.7 Resonance

- **Original paper:** Izhikevich, E.M. (2001). "Resonance and burstiness of neurons." *Neural Computation*. Also: Varela, F. et al. (2001). "The brainweb: Phase synchronization and large-scale integration." *Nature Reviews Neuroscience*.
- **Formulation:** Synchronized oscillatory activity binding distributed neural representations.
- **Program C implementation:** `backend/pipeline/resonance.py` — "epistemic honesty injection and resonance composition"; `backend/cognition/scenario_engine.py` — "resonance-only routing"; `backend/models/answer.py` — `resonance_scores`.
- **Biological evidence:** Gamma-band synchronization as binding mechanism; cross-frequency coupling.
- **Known limitations:** Program C's "resonance" is a concept activation score propagation, not oscillatory synchronization. Metaphorical use of the term.
- **Program C usage:** YES — resonance scoring in soul graph pipeline.
- **Constitution conflict:** None.

---

## 2. Machine Learning Concepts

### 2.1 Backpropagation

- **Original paper:** Rumelhart, D.E., Hinton, G.E. & Williams, R.J. (1986). "Learning representations by back-propagating errors." *Nature*.
- **Formulation:** `∂E/∂w_ij = δ_j * x_i` where `δ_j = f'(net_j) * Σ_k w_jk * δ_k` — error gradients propagate backward through layers.
- **Program C implementation:** Referenced only as a curriculum topic (`velynx_core/velynx.py:84`, `night_learner.py:67`). NOT used in any cognitive engine.
- **Biological evidence:** Controversial — no known biological mechanism propagates error signals through layers of neurons with symmetric weights (but see: Lillicrap et al., 2016 "feedback alignment").
- **Known limitations:** Biologically implausible (weight transport problem, symmetric feedback, non-local updates). Program C does not implement it.
- **Program C usage:** NO — curriculum reference only.
- **Constitution conflict:** None, but the PI review notes Program C makes "zero contact with neuroscience."

### 2.2 Gradient Descent

- **Original paper:** Cauchy, A. (1847). "Méthode générale pour la résolution des systèmes d'équations simultanées." *Comptes Rendus*.
- **Formulation:** `θ_{t+1} = θ_t - η * ∇_θ L(θ_t)`
- **Program C implementation:** Referenced as curriculum topic only.
- **Program C usage:** NO.
- **Constitution conflict:** None.

### 2.3 Reinforcement Learning

- **Original paper:** Sutton, R.S. & Barto, A.G. (1998). *Reinforcement Learning: An Introduction*. MIT Press.
- **Formulation:** Agent maximizes cumulative reward through trial-and-error; value functions and policy optimization.
- **Program C implementation:** Referenced as curriculum topic (`velynx_core/velynx.py:88`, `scripts/gpu_deep_learn.py:82`). NOT used in any cognitive engine.
- **Program C usage:** NO — curriculum reference only.
- **Constitution conflict:** None.

### 2.4 Transformer Architecture / Attention Mechanism

- **Original paper:** Vaswani, A. et al. (2017). "Attention is all you need." *NeurIPS*.
- **Formulation:** `Attention(Q,K,V) = softmax(QK^T / √d_k) * V`
- **Program C implementation:** Referenced as curriculum topic (`velynx_core/velynx.py:83,85`). NOT used in cognitive engines (Program C has its own attention: precision-weighted prediction residual).
- **Program C usage:** NO — curriculum reference only.
- **Constitution conflict:** None.

### 2.5 Variational Inference / Bayesian Methods

- **Original paper:** Jordan, M.I. et al. (1999). "An introduction to variational methods for graphical models." *Machine Learning*.
- **Formulation:** Variational lower bound `ELBO = E_q[log p(x|z)] - KL(q(z)||p(z))`
- **Program C implementation:** `cognitive_core.py:404-413` — `DirichletMarkovModel` with symmetric Dirichlet prior; `backend/cognition/concept_birth.py:139-146,843-931` — `BayesianSurprise` with Beta posteriors and KL divergence; `velynx/graph/living_edges.py:87-88` — Bayesian edge state evaluation.
- **Biological evidence:** Bayesian brain hypothesis (Knill & Pouget, 2004); neural populations represent probability distributions (Ma et al., 2006).
- **Known limitations:** Approximate inference is computationally expensive. True posteriors are intractable for complex models. Program C uses conjugate priors (Beta, Dirichlet) for tractability.
- **Program C usage:** YES — core to `cognitive_core.py`, `concept_birth.py`, `living_edges.py`.
- **Constitution conflict:** None. The Constitution's uncertainty tiers (CERTAIN/PROBABLE/DEBATED/UNKNOWN) are compatible with Bayesian posteriors.

### 2.6 K-Means / Spectral Clustering

- **Original paper:** Lloyd, S.P. (1982). "Least squares quantization in PCM." *IEEE Trans. Information Theory*. Spectral: Ng, A., Jordan, M. & Weiss, Y. (2001). "On spectral clustering." *NeurIPS*.
- **Formulation:** K-Means: minimize `Σ_i ||x_i - μ_c(i)||²`. Spectral: eigendecompose Laplacian `L = I - D^{-1/2}AD^{-1/2}`, cluster on eigenvectors.
- **Program C implementation:** `backend/cognition/concept_birth.py:687-759` — `SpectralClusterInitializer` with eigengap heuristic and K-Means++.
- **Biological evidence:** Cortical maps and tonotopic organization suggest clustering in neural representations. Self-organizing maps (Kohonen, 1982).
- **Known limitations:** K-Means assumes spherical clusters; spectral clustering is sensitive to the similarity measure chosen.
- **Program C usage:** YES — concept birth engine.
- **Constitution conflict:** None.

### 2.7 Semantic / Dense Embeddings

- **Original paper:** Mikolov, T. et al. (2013). "Efficient estimation of word representations in vector space." *ICLR*.
- **Formulation:** Dense vector representations learned by predicting context.
- **Program C implementation:** `backend/memory/memory_manager.py:16-37` — embedding service integration; `backend/knowledge/consolidator.py:27-32` — 384-dim vectors; `velynx_core/memory.py:80` — SQLite embeddings table with cosine similarity search.
- **Biological evidence:** Distributed representations in cortex (Hinton, 1984); semantic tuning in temporal cortex.
- **Known limitations:** Static embeddings cannot handle polysemy without context; no grounding to sensory experience.
- **Program C usage:** YES — memory retrieval and concept representation.
- **Constitution conflict:** None.

### 2.8 Information Theory (Entropy, KL Divergence, Mutual Information)

- **Original paper:** Shannon, C.E. (1948). "A mathematical theory of communication." *Bell System Technical Journal*.
- **Formulation:**
  - Shannon entropy: `H(X) = -Σ p(x) log₂ p(x)`
  - KL divergence: `KL(P||Q) = Σ P(x) log₂(P(x)/Q(x))`
  - Mutual information: `I(X; Y) = H(X) - H(X|Y)`
- **Program C implementation:** `cognitive_core.py:137-155` — `_kl_divergence()`; `cognitive_core.py:471` — entropy computation; `velynx/graph/curiosity_engine_v2.py:52-67,89-134` — `shannon_entropy()`, `expected_information_gain()` = mutual information; `backend/cognition/concept_birth.py:871-897` — KL divergence for Beta distributions; `validation/metrics.py:113-147` — transition entropy.
- **Biological evidence:** Neural coding efficiency (Barlow, 1961); infomax principle (Linsker, 1988); predictive coding as entropy minimization.
- **Known limitations:** Requires tractable distributions. Program C uses discrete categorical distributions and conjugate Beta/Dirichlet forms.
- **Program C usage:** YES — foundational throughout the architecture.
- **Constitution conflict:** None.

---

## 3. Predictive Processing / Free Energy Principle

### 3.1 Free Energy Principle (FEP)

- **Original paper:** Friston, K. (2010). "The free-energy principle: a unified brain theory?" *Nature Reviews Neuroscience*.
- **Formulation:** `F = E_q[-log p(observation|hidden)] + KL(q(hidden)||p(hidden))` or equivalently `F = -log p(obs) + KL(q||p(·|obs))`
- **Program C implementation:** Program C uses a proxy: `E = λ*H + μ*S + ν*A` where H = transition entropy, S = spatial prediction error, A = active load (`cognitive_health.py:23`, `validation/metrics.py:11`, `backend/cognition/decision_policy.py:25-27`). NOT the formal variational free energy.
- **Biological evidence:** FEP claims all adaptive systems minimize free energy; supported by empirical studies of predictive coding in visual cortex (Rao & Ballard, 1999) and motor control (Friston, 2011).
- **Known limitations:** FEP is controversial — Popperian falsifiability questioned (Colombo & Wright, 2018). Program C's proxy is a 3-term weighted sum, NOT the variational free energy. Loss of grounding in formal FEP mathematics.
- **Program C usage:** YES — as the cognitive energy proxy `E = λH + μS + νA`.
- **Constitution conflict:** The proxy is NOT the formal FEP. This could conflict with the Science constitution's "clear methodology" requirement if presented as FEP.

### 3.2 Active Inference

- **Original paper:** Friston, K. et al. (2015). "Active inference and epistemic value." *Cognitive Neuroscience*.
- **Formulation:** Agents minimize expected free energy `G = -E_q[log p(o|h)] - KL(q(h)||p(h))` by selecting actions that maximize epistemic + pragmatic value.
- **Program C implementation:** Referenced in `cognitive_core.py:58` as "hallmark of active inference" — learning rate proportional to attention (precision-weighted). No full active inference model with policy selection.
- **Biological evidence:** Dopaminergic signaling as reward prediction error (Schultz, 1997) is consistent with active inference formulations.
- **Known limitations:** Program C uses only the learning-rate modulation aspect. No policy selection, no expected free energy, no epistemic/pragmatic value decomposition.
- **Program C usage:** Partial — only the precision-weighted learning signal.
- **Constitution conflict:** Overclaiming active inference when only learning rate scaling is implemented. Science constitution requires accuracy about what is vs. is not implemented.

### 3.3 Predictive Coding

- **Original paper:** Rao, R.P.N. & Ballard, D.H. (1999). "Predictive coding in the visual cortex." *Nature Neuroscience*.
- **Formulation:** Hierarchical generative model where each level predicts the level below; prediction errors propagate upward; representations update to minimize error.
- **Program C implementation:** `cognitive_core.py:5-7,38-41` — Predictive Processing engine holds a continuous prediction; surprise is `-log₂ P(observation|context)`. No hierarchical predictive coding — Program C uses a flat Markov model.
- **Biological evidence:** Strong — predictive coding explains V1 responses (Rao & Ballard, 1999), mismatch negativity, repetition suppression.
- **Known limitations:** Program C lacks hierarchy, precision weighting at each level, and error/representation unit separation (canonical microcircuit). PI review: "predictive-coding hierarchies" noted as absent.
- **Program C usage:** Partial — only the single-level prediction-surprise loop.
- **Constitution conflict:** The term "predictive processing" is used accurately in the single-level sense, but could mislead about hierarchical predictive coding.

### 3.4 Generative Model (Dirichlet-Markov)

- **Original paper:** Dirichlet-multinomial model: classical Bayesian statistics.
- **Program C formulation:** `P(s|c) = (n(c,s) + α) / (N(c) + α * |support|)` — additive smoothing with symmetric Dirichlet prior (`cognitive_core.py:413`).
- **Program C implementation:** `cognitive_core.py:404-479` — `DirichletMarkovModel` with variable-order Markov chain.
- **Program C usage:** YES — the primary generative model in `cognitive_core.py`.
- **Constitution conflict:** None.

### 3.5 Prediction Error / Surprise / Surprisal

- **Original paper:** Shannon surprise: Shannon (1948). In predictive coding: Rao & Ballard (1999).
- **Program C formulation:** `I(s) = -log₂ P(s|c)` — Shannon surprisal in bits (`cognitive_core.py:53`).
- **Program C implementation:** `cognitive_core.py:1293-1294`, `velynx/graph/curiosity_engine_v2.py:70-76` — `self_information()`, `validation/metrics.py:154-160`.
- **Biological evidence:** Prediction error neurons in V1; mismatch negativity (MMN) in auditory cortex; dopamine error signal.
- **Known limitations:** Surprise is scalar; does not capture signed prediction errors or separate valence.
- **Program C usage:** YES — central cognitive signal.
- **Constitution conflict:** None.

### 3.6 Precision-Weighted Learning

- **Original paper:** Friston, K. (2005). "A theory of cortical responses." *Philosophical Transactions of the Royal Society B*.
- **Formulation:** Learning rate proportional to prediction precision (inverse variance).
- **Program C implementation:** `cognitive_core.py:1295` — `attention_weight = 1.0 - probability`; however, C6 (`cognitive_core.py:1340-1353`) actively REPLACES precision-weighted learning with Inertia Law: `effective_rate = base_rate * (1 - stability)`.
- **Biological evidence:** Attention modulates learning rate in cortex; neuromodulatory systems (acetylcholine) encode precision.
- **Known limitations:** Program C v2 (C6) explicitly abandons precision-weighted learning due to catastrophic forgetting. This is a conflict between the old design and the new.
- **Program C usage:** YES (C1-C3) then REPLACED (C6).
- **Constitution conflict:** None. The switch is documented in code comments.

### 3.7 Belief Updating (KL Divergence)

- **Original paper:** Kullback, S. & Leibler, R.A. (1951). "On information and sufficiency." *Annals of Mathematical Statistics*.
- **Program C formulation:** `KL(posterior || prior)` over the same support (`cognitive_core.py:549-572`).
- **Program C implementation:** `cognitive_core.py:137-155,571-572` — `_kl_divergence()` and usage in assimilate.
- **Program C usage:** YES — measures confidence delta per tick.
- **Constitution conflict:** None.

### 3.8 Bayesian Surprise (Beta KL)

- **Original paper:** Itti, L. & Baldi, P. (2006). "Bayesian surprise attracts human attention." *NeurIPS*.
- **Program C formulation:** `KL(Beta(1+successes, 1+failures) || Beta(1,1))` — divergence from uniform prior (`backend/cognition/concept_birth.py:852-897`).
- **Program C implementation:** `backend/cognition/concept_birth.py:846-934` — `BayesianSurprise` class.
- **Biological evidence:** Surprise modulates attention and learning; Bayesian surprise predicts human eye movements (Itti & Baldi, 2006).
- **Known limitations:** Requires conjugate Beta updates; breaks for non-binary outcomes.
- **Program C usage:** YES — concept birth engine.
- **Constitution conflict:** None.

---

## 4. Developmental Robotics Concepts

### 4.1 Curiosity / Intrinsic Motivation

- **Original paper:** Schmidhuber, J. (1991). "A possibility for implementing curiosity and boredom in model-building neural controllers." *Proc. SAB*. Also: Oudeyer, P-Y. & Kaplan, F. (2007). "What is intrinsic motivation?" *IEEE TAD*.
- **Formulation:** Agent seeks actions that maximize learning progress or information gain.
- **Program C implementation:** `velynx/graph/curiosity_engine_v2.py:355-680` — `CuriosityEngine` selects inquiry maximizing expected information gain (EIG = mutual information `I(H; A)` over structural hypotheses); `velynx/graph/curiosity_engine.py` — gap scanner; `backend/agency/curiosity.py,curiosity_executor.py` — goal-driven curiosity.
- **Biological evidence:** Dopaminergic novelty responses (Schultz, 1998); intrinsic motivation drives exploration in infants (Piaget).
- **Known limitations:** Program C's curiosity is limited to structural hypothesis testing about concept-trait relationships. No learning-progress-based curriculum, no competence-based exploration.
- **Program C usage:** YES — full curiosity engine (C5 milestone).
- **Constitution conflict:** None. The curiosity constitution is directly implemented.

### 4.2 Catastrophic Forgetting / Continual Learning / Stable Belief Revision

- **Original paper:** McCloskey, M. & Cohen, N.J. (1989). "Catastrophic interference in connectionist networks." *Psychology of Learning and Motivation*. Also: Kirkpatrick, J. et al. (2017). "Overcoming catastrophic forgetting in neural networks." *PNAS*.
- **Formulation:** Elastic weight consolidation (EWC): `L(θ) = L_B(θ) + Σ_i (λ/2) * F_i * (θ_i - θ*_i)²` where F is Fisher information.
- **Program C implementation:** `cognitive_core.py:764-790` — `StableBeliefModel` with Inertia Law (`effective_rate = base_rate * (1 - stability)`), Exception Quarantine, and Fracture mechanics.
- **Biological evidence:** Synaptic consolidation (Dudai, 2004); complementary learning systems (McClelland et al., 1995); neocortical slow learning protects prior knowledge.
- **Known limitations:** Program C's approach is heuristic — no Fisher information, no elastic penalty, no synaptic consolidation model. The fracture mechanic is invented (not biologically validated).
- **Program C usage:** YES — C6 milestone.
- **Constitution conflict:** None.

### 4.3 Concept Formation / Emergent Clustering

- **Original paper:** Piaget, J. (1952). *The Origins of Intelligence in Children*. Also: Quinlan, P.T. (1991). *Connectionism and Psychology*.
- **Formulation:** Categories emerge from statistical structure in experience.
- **Program C implementation:** `backend/cognition/concept_birth.py:1-25` — co-occurrence matrix, NPMI thresholding, spectral clustering, latent node spawning.
- **Biological evidence:** Infant categorization (Rakison & Oakes, 2003); semantic category structure in temporal cortex.
- **Known limitations:** Program C's concept birth requires explicit feature extraction first (no raw sensory stream). NPMI on pairwise feature statistics is not biologically plausible.
- **Program C usage:** YES — C3 milestone.
- **Constitution conflict:** None.

### 4.4 Scaffolding / Constructivism / Open-Ended Learning

- **Original paper:** Vygotsky, L.S. (1978). *Mind in Society*. Also: Wood, D., Bruner, J. & Ross, G. (1976). "The role of tutoring in problem solving." *JCPP*.
- **Formulation:** Learning is supported by structured guidance; constructivism: knowledge is built, not transmitted.
- **Program C implementation:** `backend/knowledge/epistemic_manager.py:2` — "Epistemic Scaffolding & Explainability API"; curriculum system (`curriculum/`, `night_learner.py`) provides staged learning. PI review notes scaffolding is hand-authored, not emergent.
- **Biological evidence:** Zone of Proximal Development; Piagetian stages.
- **Known limitations:** Program C's scaffolding is hand-specified (seeded curriculum, pre-authored ontology), not emergent from interaction. PI review: "Nothing develops."
- **Program C usage:** YES — epistemic scaffolding, curriculum.
- **Constitution conflict:** The "nothing develops" critique is a core finding in the PI review. If Program C claims developmental emergence, that conflicts with the Science constitution.

### 4.5 Sensorimotor Contingency

- **Original paper:** O'Regan, J.K. & Noë, A. (2001). "A sensorimotor account of vision and visual consciousness." *Behavioral and Brain Sciences*.
- **Formulation:** Perception is constituted by mastery of sensorimotor contingencies (regularities in how sensory input changes with action).
- **Program C implementation:** PI review (`docs/VELYNX_v2_PI_Review.md:99`) proposes "minimal predictive organism" receiving sensorimotor stream. Not implemented in current codebase.
- **Biological evidence:** Active perception; embodied cognition.
- **Program C usage:** NO — proposed but not built.
- **Constitution conflict:** Not applicable (not implemented).

### 4.6 Learning Progress / Curriculum Learning

- **Original paper:** Oudeyer, P-Y. et al. (2007). "Intrinsic motivation systems for autonomous mental development." *IEEE TEC*. Also: Bengio, S. et al. (2009). "Curriculum learning." *ICML*.
- **Formulation:** Training on increasingly difficult material; autonomous selection based on learning progress.
- **Program C implementation:** Referenced in `backend/learning/curriculum.py`. The curriculum system (`curriculum/` directory) has fixed stages, not adaptive progress.
- **Biological evidence:** Infant development progresses through stages (Piaget); spaced repetition enhances retention.
- **Known limitations:** Fixed curriculum with pre-answered questions, not adaptive.
- **Program C usage:** Partial — fixed curriculum exists but no autonomous learning progress.
- **Constitution conflict:** None.

---

## 5. Local Learning Rules

### 5.1 Hebbian Coactivation (Local Rule)

- **Original paper:** Hebb (1949).
- **Program C formulation:** `Δw = η * coactivation_count / threshold` — once coactivation count >= 2, create edge; reinforce existing edges.
- **Program C implementation:** `backend/soul/soul_graph.py:512-596`, `velynx/graph/living_edges.py:73-82`.
- **Biological evidence:** See 1.1.
- **Known limitations:** No temporal asymmetry (no STDP), no weight bounds, no competition between synapses.
- **Program C usage:** YES — soul graph.
- **Constitution conflict:** None.

### 5.2 Delta Rule / Perceptron Rule

- **Original paper:** Widrow, B. & Hoff, M.E. (1960). "Adaptive switching circuits." *Stanford Report*.
- **Formulation:** `Δw = η * (target - output) * input`
- **Program C usage:** NO — not implemented.
- **Constitution conflict:** Not applicable.

### 5.3 Oja Rule

- **Original paper:** Oja, E. (1982). "Simplified neuron model as a principal component analyzer." *J. Mathematical Biology*.
- **Formulation:** `Δw = η * (x*y - y²*w)` — unsupervised Hebbian with weight normalization.
- **Program C usage:** NO.
- **Constitution conflict:** Not applicable.

### 5.4 BCM Rule (Bienenstock-Cooper-Munro)

- **Original paper:** Bienenstock, E.L., Cooper, L.N. & Munro, P.W. (1982). "Theory for the development of neuron selectivity." *J. Neuroscience*.
- **Formulation:** `Δw = η * x * (y - θ_M) * y` where `θ_M` is a sliding modification threshold.
- **Program C usage:** NO.
- **Constitution conflict:** Not applicable.

### 5.5 Three-Factor Learning Rules

- **Original paper:** Frémaux, N. & Gerstner, W. (2016). "Neuromodulated spike-timing-dependent plasticity." *Biological Cybernetics*.
- **Formulation:** `Δw = η * (pre * post) * neuromodulator` — Hebbian term gated by a third factor.
- **Program C usage:** NO — no neuromodulator modeling.
- **Constitution conflict:** Not applicable.

### 5.6 Equilibrium Propagation

- **Original paper:** Scellier, B. & Bengio, Y. (2017). "Equilibrium propagation: Bridging the gap between energy-based models and backpropagation." *Frontiers in Computational Neuroscience*.
- **Formulation:** Uses local energy gradients in a recurrent network; two phases (forward/settling + nudged/backward).
- **Program C usage:** NO.
- **Constitution conflict:** Not applicable.

---

## 6. Plasticity Mechanisms

### 6.1 LTP / LTD (Long-Term Potentiation / Depression)

- **Original paper:** Bliss, T.V.P. & Lømo, T. (1973). "Long-lasting potentiation of synaptic transmission in the dentate area." *J. Physiology*.
- **Formulation:** LTP: sustained high-frequency stimulation → persistent increase in synaptic strength. LTD: low-frequency stimulation → decrease.
- **Program C implementation:** Not explicitly. The Hebbian coactivation counts and asymptotic weight updates approximate LTP; decay approximates LTD.
- **Biological evidence:** Foundational cellular correlate of memory (hippocampal LTP).
- **Known limitations:** Program C does not distinguish LTP (Ca²⁺/NMDA-dependent) from Hebbian weight changes; no spike-timing requirement; no LTD induction protocol.
- **Program C usage:** Indirect — via Hebbian reinforcement and synaptic decay.
- **Constitution conflict:** None.

### 6.2 STDP (Spike-Timing-Dependent Plasticity)

- **Original paper:** Markram, H. et al. (1997). "Regulation of synaptic efficacy by coincidence of postsynaptic APs and EPSPs." *Science*. Also: Bi, G.-Q. & Poo, M.-M. (1998). "Synaptic modifications in cultured hippocampal neurons." *J. Neuroscience*.
- **Formulation:** `Δw = A_+ * exp(-|Δt|/τ_+)` for pre-before-post (LTP); `Δw = -A_- * exp(-|Δt|/τ_-)` for post-before-pre (LTD).
- **Program C usage:** NO — not implemented. Rate-based coactivation only.
- **Constitution conflict:** Not applicable.

### 6.3 Synaptic Pruning

- See 1.2.

### 6.4 Metaplasticity / Homeostatic Plasticity

- **Original paper:** Abraham, W.C. & Bear, M.F. (1996). "Metaplasticity: the plasticity of synaptic plasticity." *Trends in Neurosciences*.
- **Formulation:** The capacity for plasticity is itself regulated by prior activity.
- **Program C usage:** NO — not implemented. C6's Inertia Law is related but is not a biologically-grounded metaplasticity mechanism.
- **Constitution conflict:** Not applicable.

### 6.5 Structural Plasticity / Synaptogenesis

- **Original paper:** Holtmaat, A. & Svoboda, K. (2009). "Experience-dependent structural synaptic plasticity." *Nature Reviews Neuroscience*.
- **Formulation:** Dendritic spines form and retract in response to experience.
- **Program C implementation:** The living edge creation/deletion approximates structural plasticity, but with no spatial or morphological constraints.
- **Program C usage:** Indirect — edge creation/deletion in soul graph.
- **Constitution conflict:** None.

---

## 7. Homeostasis Mechanisms

### 7.1 Synaptic Scaling

- **Original paper:** Turrigiano, G.G. et al. (1998). "Activity-dependent scaling of quantal amplitude in neocortical neurons." *Nature*.
- **Formulation:** Global multiplicative scaling of all synaptic strengths to maintain firing rate within target range.
- **Program C usage:** NO — not implemented.
- **Constitution conflict:** Not applicable.

### 7.2 Firing Rate Homeostasis / Intrinsic Plasticity

- **Original paper:** Desai, N.S. et al. (1999). "Plasticity in the intrinsic excitability of cortical pyramidal neurons." *Nature Neuroscience*.
- **Formulation:** Neurons regulate their intrinsic excitability to maintain stable firing rates.
- **Program C usage:** NO — not implemented.
- **Constitution conflict:** Not applicable.

### 7.3 E/I Balance (Excitation-Inhibition)

- **Original paper:** van Vreeswijk, C. & Sompolinsky, H. (1996). "Chaos in neuronal networks with balanced excitatory and inhibitory activity." *Science*.
- **Formulation:** Cortical networks maintain a precise balance of excitation and inhibition; imbalance leads to runaway excitation or quiescence.
- **Program C usage:** NO — not implemented.
- **Constitution conflict:** Not applicable.

### 7.4 BCM Sliding Threshold

- **Original paper:** Bienenstock, Cooper & Munro (1982).
- **Formulation:** The modification threshold `θ_M` slides as a function of mean postsynaptic activity, providing homeostatic regulation.
- **Program C usage:** NO.
- **Constitution conflict:** Not applicable.

---

## 8. Energy Models

### 8.1 Cognitive Energy Proxy (Free Energy)

- **Original paper:** Derived from Friston (2010). Program C formulation is a novel proxy.
- **Program C formulation:** `E = λ*H + μ*S + ν*A` where:
  - `H` = conditional Shannon entropy of cluster-transition Markov chain (bits)
  - `S` = Euclidean distance between predicted centroid and observed vector
  - `A` = active K-Means clusters + anomaly cloud spatial volume
  - `λ=1.0, μ=2.0, ν=0.5` (coupling coefficients)
- **Program C implementation:** `validation/metrics.py:197-206` — `cognitive_energy()`; `cognitive_health.py:23`; `backend/cognition/decision_policy.py:25-27`.
- **Biological evidence:** FEP claims all self-organizing systems minimize free energy. The proxy terms connect to: entropy (cortical variability), surprise (prediction error), structural load (metabolic cost).
- **Known limitations:** NOT the variational free energy. No generative model likelihood, no posterior approximation. The coefficients are hand-tuned. No thermodynamic grounding.
- **Program C usage:** YES — central to C8 decision policy and cognitive health monitoring.
- **Constitution conflict:** Per the Science constitution, this proxy must not be presented as Friston free energy without qualification.

### 8.2 Thermodynamic State

- **Original paper:** Derived from statistical mechanics.
- **Program C formulation:** Scalar parameter controlling strictness vs. exploration in reasoning (`backend/cognition/reasoning_engine.py:11-12,385-395,778-842`). Computed from conflict state.
- **Program C implementation:** `backend/app/pipeline.py:36,774` — `compute_thermodynamic_state()`; `backend/cognition/reasoning_engine.py` — thermodynamic traversal policy.
- **Biological evidence:** No direct biological correlate. Cognitive "temperature" modulates exploration/exploitation (analogous to simulated annealing).
- **Known limitations:** Metaphorical use of thermodynamic language. No connection to statistical mechanics or actual free energy.
- **Program C usage:** YES — reasoning engine.
- **Constitution conflict:** The thermodynamic metaphor could mislead about biological grounding. Science constitution requires accurate terminology.

### 8.3 Energy Landscape / Energy-Based Models

- **Original paper:** Hopfield, J.J. (1982). "Neural networks and physical systems with emergent collective computational abilities." *PNAS*.
- **Formulation:** `E = -½ Σ_ij w_ij * s_i * s_j + Σ_i θ_i * s_i` — network dynamics minimize energy.
- **Program C usage:** NO.
- **Constitution conflict:** Not applicable.

### 8.4 Boltzmann Machine / RBM

- **Original paper:** Hinton, G.E. & Sejnowski, T.J. (1986). "Learning and relearning in Boltzmann machines." *Parallel Distributed Processing*.
- **Formulation:** `P(v,h) = (1/Z) * exp(-E(v,h))` — generative model over visible and hidden units.
- **Program C usage:** NO.
- **Constitution conflict:** Not applicable.

### 8.5 Helmholtz Free Energy / Variational Free Energy

- **Original paper:** Feynman, R.P. (1972). *Statistical Mechanics*. In ML: Neal, R.M. & Hinton, G.E. (1998). "A view of the EM algorithm that justifies incremental, sparse, and other variants." *NATO ASI*.
- **Formulation:** `F = -log Z = E_q[E] - H(q) = -E_q[log p(x,h)] + E_q[log q(h)]`
- **Program C usage:** NO — Program C uses a proxy, not the formal variational free energy.
- **Constitution conflict:** The proxy should not be conflated with Helmholtz/variational free energy.

---

## 9. Gap Analysis: Concepts NOT in Program C

The following concepts are absent from the codebase despite their relevance to the claimed cognitive architecture. Each represents a gap to address.

### Neuroscience Gaps
| Concept | Relevance | Why Missing |
|---------|-----------|-------------|
| STDP (Spike-Timing-Dependent Plasticity) | Precise temporal learning | Rate-based Hebbian only |
| Dopamine / Neuromodulation | Reward prediction error, learning gate | No neuromodulator model |
| LTP / LTD (cellular mechanisms) | Synaptic memory | High-level Hebbian only |
| Cortical column / canonical microcircuit | Neocortical organization | No hierarchical architecture |
| Hippocampus / entorhinal memory system | Episodic memory, consolidation | SQLite, not neural |
| Basal ganglia / action selection | Gating, decision making | Simple policy functions |
| Cerebellum / sensorimotor learning | Timing, prediction | Not addressed |
| Place cells / grid cells | Spatial cognition | Not addressed |
| Receptive fields / topographic maps | Sensory processing | Not addressed |
| Neural oscillations (gamma, theta, sleep spindles) | Binding, consolidation, timing | Not addressed |
| Neuromodulatory systems (ACh, NE, 5-HT, DA) | Attention, arousal, mood, learning | Not addressed |
| Spiking neural networks (SNNs) | Biologically realistic timing | Abstract symbolic / vector system |
| Sparse coding / population coding | Neural representation efficiency | Dense vectors only |
| Lateral inhibition / winner-take-all | Competition, normalization | Not implemented |
| Dendritic computation | Single-neuron complexity | Point-neuron abstraction |

### ML Gaps
| Concept | Relevance | Why Missing |
|---------|-----------|-------------|
| Backpropagation | Deep learning | Biologically implausible (design choice) |
| Reinforcement Learning | Trial-and-error learning | Curriculum reference only |
| Transformer / self-attention | Modern AI | Novel attention mechanism used instead |
| Generative models (VAE, GAN, diffusion) | Rich representation learning | Markov models + embeddings only |
| LSTM / GRU (gated RNNs) | Sequence learning | Markov models used instead |
| Graph Neural Networks | Relational learning | Hand-coded edge logic instead |
| Adversarial training | Robustness | Not implemented |
| Contrastive learning | Representation learning | Not implemented |
| Gaussian Processes | Bayesian non-parametrics | Dirichlet/Beta only |
| Decision Trees / Random Forests | Symbolic ML | Not used |
| Dimensionality reduction (PCA, t-SNE, UMAP) | Visualization, compression | Spectral clustering only |

### Predictive Processing Gaps
| Concept | Relevance | Why Missing |
|---------|-----------|-------------|
| Hierarchical predictive coding | Multi-level perception | Single-level Markov model |
| Precision weighting (formal) | Attention modulation | Replaced by Inertia Law (C6) |
| Expected free energy | Action selection, epistemic value | Not implemented |
| Policy selection | Goal-directed behavior | Simple heuristic policies |
| Markov blanket | Self-organization boundaries | Not modeled |
| Model-based / model-free arbitration | Decision-making | Not implemented |
| Structure learning | Discovering latent causal structure | Concept birth approximates this |

### Developmental Robotics Gaps
| Concept | Relevance | Why Missing |
|---------|-----------|-------------|
| Motor babbling | Initial sensorimotor exploration | No embodiment |
| Empowerment maximization | Intrinsic motivation | Curiosity uses info gain only |
| Affordance learning | Action possibilities | Not modeled |
| Object permanence | Cognitive development | Not modeled |
| Self-other distinction | Social cognition | Not addressed |
| Stage-like development | Piagetian theory | Not modeled as stages |
| Epigenetic robotics | Developmental framework | Cited but not implemented |
| Autonomous mental development | Self-directed learning | Heavily hand-authored |

### Learning Rule Gaps
| Concept | Relevance | Why Missing |
|---------|-----------|-------------|
| Oja rule (PCA learning) | Unsupervised feature learning | Not implemented |
| BCM rule | Sliding threshold plasticity | Not implemented |
| Three-factor rules | Neuromodulated plasticity | Not implemented |
| Equilibrium propagation | Local gradient approximation | Not implemented |
| FORCE / reservoir computing | Recurrent network learning | Not implemented |
| Surrogate gradients | SNN training | Not implemented |
| Eligibility traces | Temporal credit assignment | Not implemented |

### Plasticity Gaps
| Concept | Relevance | Why Missing |
|---------|-----------|-------------|
| STDP | Temporal learning | See above |
| Anti-Hebbian plasticity | Decorrelation, PCA | Not implemented |
| Heterosynaptic plasticity | Coordinated weight changes | Not implemented |
| Metaplasticity | Rate-dependent plasticity | Not implemented |
| Synaptic tagging / capture | Late LTP, consolidation | Not implemented |
| Systems consolidation | Hippocampal-neocortical transfer | Not implemented |

### Homeostasis Gaps
| Concept | Relevance | Why Missing |
|---------|-----------|-------------|
| Synaptic scaling | Global stabilization | Not implemented |
| Intrinsic plasticity | Excitability regulation | Not implemented |
| E/I balance | Network stability | Not implemented |
| BCM sliding threshold | Homeostatic LTP/LTD | Not implemented |
| Calcium homeostasis | Cellular stability | Not implemented |
| Receptor trafficking | AMPA/NMDA dynamics | Not implemented |

---

## 10. Constitution Compatibility Matrix

| Concept | Uses Term? | Conflicts with Constitution? | Notes |
|---------|-----------|------------------------------|-------|
| Hebbian Learning | YES | No | Consistent with epistemic transparency |
| Synaptic Pruning | YES | No | Sleep cycle mechanics |
| Attention (Top-Down) | YES | No | Independent formulation |
| Memory Systems | YES | No | Epistemic constitution requires source tracing |
| Sleep / Replay | YES | No | Metaphorical use |
| Free Energy Principle | YES | RISK | Proxy `E=λH+μS+νA` is NOT FEP; Science constitution requires accuracy |
| Active Inference | YES | RISK | Only precision-weighted learning implemented; overclaims |
| Predictive Coding | YES | RISK | Single-level, not hierarchical; Science constitution |
| Generative Model (Dirichlet) | YES | No | Correctly implemented |
| Bayesian Surprise | YES | No | Correctly implemented |
| Curiosity / Info Gain | YES | No | Curiosity constitution aligned |
| Catastrophic Forgetting | YES | No | C6 solution documented |
| Thermodynamic State | YES | RISK | Metaphorical; not physical thermodynamics |
| K-Means / Spectral Clustering | YES | No | Standard algorithms |
| KL Divergence / Entropy | YES | No | Standard information theory |
| Backpropagation | NO (curriculum) | No | Not used in engines |
| STDP | NO | N/A | Not implemented |
| Dopamine / Neuromodulation | NO | N/A | Not implemented |
| Homeostatic Plasticity | NO | N/A | Not implemented |
| E/I Balance | NO | N/A | Not implemented |
| Reinforcement Learning | NO (curriculum) | No | Not used in engines |
| Sensorimotor Contingency | NO | N/A | Proposed but not built |
| Piagetian Development | Reference only | RISK | PI review: "Piagetian sensorimotor bootstrapping" cited as missing |

### Key Constitution Risks

1. **Science constitution (science.md):** Requires "clear methodology and transparent data." The gap between claimed cognitive architecture and actual implementation (especially FEP, active inference, predictive coding) may violate this.

2. **Uncertainty constitution (uncertainty.md):** Mandates honest uncertainty reporting. The PI review found `CERTAIN` on hallucinated content — if this persists in cognitive engines, it violates the Constitution.

3. **Epistemology constitution (epistemology.md):** Requires traceable sources. The learning rule and plasticity mechanisms lack citations to biological literature.

4. **Curiosity constitution (curiosity.md):** Mandates multi-dimensional inquiry. The curiosity engine (information gain over structural hypotheses) is aligned with this.

---

*End of Evidence Database.*

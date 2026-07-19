# VELYNX Related Work — Systematic Literature Mapping

**Purpose**: Comprehensive citation coverage for NeurIPS/ICML submission. Every claim in the paper must trace to prior work or be explicitly novel.

---

## 1. Predictive Processing & Free Energy Principle

| VELYNX Component | Prior Work | Relationship | Citation |
|------------------|------------|--------------|----------|
| Predictive coding loop (predict → collide → adapt) | **Foundational** | Direct implementation | Friston, K. (2010). The free-energy principle: a unified brain theory? *Nat Rev Neurosci* |
| Surprise = -log P(observation\|prediction) | **Foundational** | Direct implementation | Friston, K. (2005). A theory of cortical responses. *Phil Trans R Soc B* |
| Precision-weighted learning (attention ∝ prediction error) | **Foundational** | Modified in C6 | Friston et al. (2017). Active inference: a process theory. *Neural Comput* |
| Generative model as categorical Dirichlet-Markov | **Adapted** | Variable-order, open-vocabulary | Clark, A. (2013). Whatever next? Predictive brains. *Behav Brain Sci* |
| Free Energy = λH + μS + νA (spatial) | **Novel instantiation** | Continuous vector version of FEP | Hohwy, J. (2013). The predictive mind. *OUP* |

**Gap**: No prior work combines Dirichlet-Markov discrete substrate with continuous K-Means vector substrate in one architecture.

---

## 2. Catastrophic Forgetting & Continual Learning

| VELYNX Claim | Prior Work | Relationship | Citation |
|--------------|------------|--------------|----------|
| C6 Inertia Law: effective_rate = base_rate × (1 - stability) | **Novel mechanism** | Inverts precision-weighting | — |
| Exception Quarantine (anomalies filed, not blended) | **Novel mechanism** | Contrasts with replay/regularization | — |
| Fracture threshold: contradictions/support ≥ 0.85 → rule revision | **Novel mechanism** | Structured belief revision | — |
| Catastrophic forgetting in Dirichlet-Markov (single anomaly collapses mature rule) | **Demonstrated** | Empirical finding, not in literature | — |
| EWC (Elastic Weight Consolidation) | **Baseline** | Parameter regularization | Kirkpatrick et al. (2017). *PNAS* |
| SI (Synaptic Intelligence) | **Baseline** | Parameter importance | Zenke et al. (2017). *ICML* |
| LwF (Learning without Forgetting) | **Baseline** | Knowledge distillation | Li & Hoiem (2017). *CVPR* |
| GEM (Gradient Episodic Memory) | **Baseline** | Replay buffer | Lopez-Paz & Ranzato (2017). *NIPS* |
| ER (Experience Replay) | **Baseline** | Replay buffer | Chaudhry et al. (2019). *ICLR* |

**Critical**: Must compare C6 StableBeliefModel against EWC, SI, LwF, GEM, ER on standard continual learning benchmarks (Split MNIST, Permuted MNIST, CORe50) AND on the symbolic sequence task in `cognitive_core.py`.

---

## 3. Concept Formation & Category Learning

| VELYNX Component | Prior Work | Relationship | Citation |
|------------------|------------|--------------|----------|
| C4 Concept Birth via MDL (G = H_before - H_after > threshold) | **Novel formulation** | MDL applied to predictive entropy | Grünwald, P. (2007). The minimum description length principle. *MIT Press* |
| H_before = H({rule} ∪ {exceptions}), H_after = H({rule, concept}) + λ_model | **Novel derivation** | Chain rule of entropy | Chater & Vitányi (2003). *Behav Brain Sci* |
| Single exception → H_within = 0 → no birth (correctly refuses) | **Novel property** | Emerges from math | — |
| Latent concepts as "compression of future uncertainty" | **Theoretical alignment** | Predictive coding view | Friston et al. (2017) |
| Bayesian Program Learning (BPL) | **Baseline** | Compositional concept learning | Lake et al. (2015). *Science* |
| Rational Rules / IBP | **Baseline** | Nonparametric concept learning | Goodman et al. (2008). *CogSci* |
| COBWEB / CLASSIT | **Baseline** | Incremental concept formation | Fisher (1987). *Machine Learning* |
| Human category learning (Rosch, Murphy) | **Theoretical** | Basic-level categories | Rosch et al. (1976). *Cognitive Psychology* |

**Gap**: No prior work uses *predictive entropy reduction on a generative model's exception quarantine* as the birth criterion.

---

## 4. Latent Cause Inference & Structure Learning

| VELYNX Component | Prior Work | Relationship | Citation |
|------------------|------------|--------------|----------|
| C7: Quarantine anomalies → mine for invariant sub-space | **Novel pipeline** | Continuous vector version | — |
| LatentVariable = conjunction of axis-aligned predicates | **Related** | Decision trees / rule learning | Quinlan (1986). *Machine Learning* |
| Score = α·PredictionGain + β·CompressionGain + γ·Stability | **Novel combination** | Three-pressure scoring | — |
| PredictionGain = coverage × (1 - false_positive_rate) | **Novel formulation** | Contrastive anomaly detection | — |
| CompressionGain = MDL bits saved | **Standard MDL** | Grünwald (2007) | Grünwald (2007) |
| Stability = tightness of constrained dimensions | **Novel** | Invariant quality | — |
| Latent Cause Inference (Gershman) | **Theoretical precursor** | Discrete hidden states | Gershman et al. (2010). *Psychol Rev* |
| Contextual Inference / Structure Learning | **Theoretical precursor** | Partitioning observations | Gershman et al. (2015). *Cognition* |
| Hidden Markov Models / Switching Linear Dynamical Systems | **Baseline** | Continuous latent states | Linderman et al. (2017). *JMLR* |

**Critical**: Must show C7 rediscoveries ground-truth regimes (CALM_DAY, STORM, FOG) from *unlabeled* noisy vectors. Compare to HMM, SLDS, Gaussian Mixture Models on same sensor stream.

---

## 5. Vector-Based / Continuous Cognitive Architectures

| VELYNX Component | Prior Work | Relationship | Citation |
|------------------|------------|--------------|----------|
| Semantic Pointer Architecture (SPA) | **Theoretical cousin** | Vector symbolic architecture | Eliasmith, C. (2013). How to build a brain. *OUP* |
| Holographic Reduced Representations (HRR) | **Theoretical cousin** | Circular convolution binding | Plate, T. (2003). *Neural Comput* |
| Vector Symbolic Architectures (VSA) | **Theoretical cousin** | General framework | Gayler, R. (2003). *ICCS* |
| K-Means clustering as "naming" regimes | **Standard ML** | Unsupervised discretization | MacQueen (1967). *Berkeley Symp* |
| Predictive coding in continuous space | **Theoretical** | Rao & Ballard (1999) | Rao & Ballard (1999). *Nat Neurosci* |

**Gap**: VELYNX is the first to combine VSA-style vector representations with predictive processing + free energy + MDL concept birth + latent cause discovery in a single architecture.

---

## 6. Cognitive Architectures (Symbolic / Hybrid)

| Architecture | VELYNX Overlap | Key Difference |
|--------------|----------------|----------------|
| ACT-R | Production rules, declarative memory | VELYNX: no production rules; continuous vectors; surprise-driven |
| Soar | Problem spaces, chunking | VELYNX: no explicit goals; predictive loop; concept birth |
| CLARION | Dual-process (implicit/explicit) | VELYNX: single predictive loop; no meta-cognitive layer yet |
| LIDA | Global workspace, perceptual/memory | VELYNX: no workspace; sensorium is the interface |
| Sigma | Graphical models, cognitive skills | VELYNX: Dirichlet-Markov + K-Means; no graphical models |

**Positioning**: VELYNX is a *predictive processing architecture* with *vector sensorium*, not a production-rule or global-workspace architecture.

---

## 7. Minimum Description Length in Cognition

| Work | Relevance to VELYNX |
|------|---------------------|
| Grünwald (2007) — MDL Principle | Theoretical foundation for C4 birth criterion |
| Chater & Vitányi (2003) — Simplicity in cognition | "Compression = understanding" thesis |
| Hinton & Zemel (1994) — Autoencoders as MDL | Precursor to variational autoencoders |
| Rissanen (1978) — Stochastic complexity | Original MDL formulation |
| Grünwald & Roos (2019) — Minimum Description Length Revisited | Modern review |

---

## 8. Required Citation Additions for Submission

**Must-add before submission** (priority order):

1. **Continual Learning Baselines**: Kirkpatrick 2017, Zenke 2017, Lopez-Paz 2017, Chaudhry 2019
2. **Latent Cause Inference**: Gershman 2010, Gershman 2015, Tomov 2018
3. **Concept Learning**: Lake 2015 (BPL), Goodman 2008, Fisher 1987
4. **Vector Cognitive Arch**: Eliasmith 2013, Plate 2003, Gayler 2003
5. **Predictive Processing**: Friston 2010, Clark 2013, Hohwy 2013, Parr 2022
6. **MDL in Cognition**: Grünwald 2007, Chater 2003, Rissanen 1978
7. **Cognitive Architectures**: Anderson 2007 (ACT-R), Laird 2012 (Soar), Sun 2006 (CLARION)

---

## 9. Novelty Claims — Explicit Positioning

| Claim | Status | Defense |
|-------|--------|---------|
| **First** architecture unifying Dirichlet-Markov discrete + K-Means continuous predictive processing | ✅ Novel | No prior work bridges these two substrates |
| **First** catastrophic forgetting cure via *Inertia Law* (inverse precision-weighting) + *Exception Quarantine* | ✅ Novel | All prior work uses regularization/replay; VELYNX uses belief structure |
| **First** concept birth criterion = *predictive entropy reduction on exception quarantine* | ✅ Novel | MDL applied to generative model's predictive distribution, not data compression |
| **First** latent cause discovery from *quarantined prediction errors* in continuous sensorium | ✅ Novel | Gershman uses discrete observations; VELYNX uses continuous vectors + K-Means |
| **First** closed-loop: discovery → attention reweighting → improved prediction | ✅ Novel | Latent cause engines typically offline; VELYNX feeds back online |

---

**Next Step**: Convert this mapping into a 1.5-page Related Work section for the paper. Every "Novel" claim above must have a corresponding ablation experiment in the paper.
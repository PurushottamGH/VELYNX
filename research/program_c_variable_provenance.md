# Program C — Variable Provenance

> Complete trace of every named mathematical quantity in Program C.
> Generated from `research/program_c_mathematical_ontology.md` and `generate_graph.py`.

---

## Key

| Field | Meaning |
|-------|---------|
| **Symbol** | The mathematical symbol used in equations |
| **Name** | Human-readable name |
| **Definition** | Precise mathematical definition |
| **Origin** | Source file + line number |
| **Units** | Measurement unit |
| **Range** | Codomain / valid range |
| **Consumers** | What variables/equations read this variable |
| **Dependencies** | What variables/equations this variable depends on |
| **Eq Chain** | The equation(s) that produce this variable |
| **Validation** | Whether experimentally validated |
| **Unused** | True if defined but never consumed downstream |
| **Contradictions** | Known inconsistencies with other quantities |
| **Circular Dep** | True if variable participates in a feedback loop |

---

## 1. Symbolic Domain (`cognitive_core.py`)

---

### 1.1 Context `c`

| Field | Value |
|-------|-------|
| **Symbol** | `c` |
| **Name** | Context |
| **Definition** | Order-`k` suffix of the symbol stream; the conditioning history for the Markov model |
| **Origin** | `cognitive_core.py:118` |
| **Units** | dimensionless (tuple of symbols) |
| **Range** | vocabulary^k |
| **Consumers** | `n(c,s)`, `N(c)`, `P(s\|c)` |
| **Dependencies** | symbol stream, Markov order `k` |
| **Eq Chain** | `c = stream[-k:]` |
| **Validation** | not independently validated |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 1.2 Symbol `s`

| Field | Value |
|-------|-------|
| **Symbol** | `s` |
| **Name** | Symbol |
| **Definition** | A discrete token from the vocabulary, or NOVEL, or BOS |
| **Origin** | `cognitive_core.py:117` |
| **Units** | dimensionless (string) |
| **Range** | `vocabulary ∪ {NOVEL, BOS}` |
| **Consumers** | `n(c,s)`, `P(s\|c)`, `I(s)`, `a(s)`, `conf`, `δ` |
| **Dependencies** | sensory stream → symbol discretization |
| **Eq Chain** | `s = discretize(sensor_output)` |
| **Validation** | not independently validated |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 1.3 Dirichlet Concentration `α`

| Field | Value |
|-------|-------|
| **Symbol** | `α` |
| **Name** | Dirichlet concentration |
| **Definition** | Symmetric Dirichlet prior concentration parameter |
| **Origin** | `cognitive_core.py:421` |
| **Units** | dimensionless |
| **Range** | `(0, ∞)`, default `0.5` |
| **Consumers** | `P(s\|c)` |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | assumes all symbols equally likely a priori |
| **Circular Dep** | no |

---

### 1.4 Context-Specific Successor Count `n(c, s)`

| Field | Value |
|-------|-------|
| **Symbol** | `n(c, s)` |
| **Name** | Context-specific successor count |
| **Definition** | Count of times symbol `s` has followed context `c` (precision-weighted or literal) |
| **Origin** | `cognitive_core.py:426` |
| **Units** | dimensionless (count) |
| **Range** | `[0, ∞)` |
| **Consumers** | `P(s\|c)`, `N(c)` |
| **Dependencies** | `c`, `s` |
| **Eq Chain** | `n(c,s) ← increment(n(c,s)) on observation` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 1.5 Total Mass in Context `N(c)`

| Field | Value |
|-------|-------|
| **Symbol** | `N(c)` |
| **Name** | Total mass in context |
| **Definition** | `Σ_s n(c, s)` — total observations in context `c` |
| **Origin** | `cognitive_core.py:457` |
| **Units** | dimensionless (count) |
| **Range** | `[0, ∞)` |
| **Consumers** | `P(s\|c)` |
| **Dependencies** | `n(c, s)`, `s` |
| **Eq Chain** | `N(c) = Σ_s n(c, s)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 1.6 Support Size `|support|`

| Field | Value |
|-------|-------|
| **Symbol** | `\|support\|` |
| **Name** | Support size |
| **Definition** | Size of the vocabulary including the NOVEL slot |
| **Origin** | `cognitive_core.py:448-449` |
| **Units** | dimensionless (count) |
| **Range** | `[1, \|vocab\| + 1]` |
| **Consumers** | `P(s\|c)` |
| **Dependencies** | vocabulary |
| **Eq Chain** | `\|support\| = len(vocabulary) + 1` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 1.7 Predictive Probability `P(s|c)`

| Field | Value |
|-------|-------|
| **Symbol** | `P(s\|c)` |
| **Name** | Predictive probability |
| **Definition** | `(n(c, s) + α) / (N(c) + α·\|support\|)` — Dirichlet-Markov smoothed conditional probability |
| **Origin** | `cognitive_core.py:414` |
| **Units** | dimensionless |
| **Range** | `(0, 1]` |
| **Consumers** | `I(s)`, `a(s)`, `H(p)`, `D_KL` |
| **Dependencies** | `n(c, s)`, `N(c)`, `α`, `\|support\|` |
| **Eq Chain** | `P(s\|c) = (n(c,s) + α) / (N(c) + α·\|support\|)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | assumes conditional independence given context; symmetric Dirichlet prior |
| **Circular Dep** | no |

---

### 1.8 Shannon Surprisal `I(s)`

| Field | Value |
|-------|-------|
| **Symbol** | `I(s)` |
| **Name** | Shannon surprisal |
| **Definition** | `-log₂ P(s\|c)` — self-information in bits |
| **Origin** | `cognitive_core.py:53` |
| **Units** | bits |
| **Range** | `[0, ∞)` |
| **Consumers** | `ε`, `S_max`, `μ_surp`, `θ_adapt` |
| **Dependencies** | `P(s\|c)` |
| **Eq Chain** | `I(s) = -log₂ P(s\|c)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | clamped at 5.0 bits ceiling (`S_max`); real value `I(s)` can exceed this for large vocabularies |
| **Circular Dep** | no |

---

### 1.9 Attention Weight `a(s)`

| Field | Value |
|-------|-------|
| **Symbol** | `a(s)` |
| **Name** | Attention weight |
| **Definition** | `1 - P(s\|c)` — precision of the prediction residual |
| **Origin** | `cognitive_core.py:54` |
| **Units** | dimensionless |
| **Range** | `[0, 1]` |
| **Consumers** | `w_d` (indirectly via attention modulation) |
| **Dependencies** | `P(s\|c)` |
| **Eq Chain** | `a(s) = 1 - P(s\|c)` |
| **Validation** | no |
| **Unused** | partially — not directly consumed in later C6+ modules |
| **Contradictions** | contradicts Inertia Law (L7) — precision-weighting vs stability-scaling |
| **Circular Dep** | yes — participates in attention → cluster → attention feedback loop |

---

### 1.10 Prediction Entropy `H(p)`

| Field | Value |
|-------|-------|
| **Symbol** | `H(p)` |
| **Name** | Prediction entropy |
| **Definition** | Shannon entropy of the predictive distribution |
| **Origin** | `cognitive_core.py:179` |
| **Units** | bits |
| **Range** | `[0, ∞)` |
| **Consumers** | novelty detection |
| **Dependencies** | `P(s\|c)` |
| **Eq Chain** | `H(p) = -Σ_s P(s\|c) · log₂ P(s\|c)` |
| **Validation** | no |
| **Unused** | partial — used for novelty mass but not in CPI |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 1.11 Novelty Mass `m_novel`

| Field | Value |
|-------|-------|
| **Symbol** | `m_novel` |
| **Name** | Novelty mass |
| **Definition** | Probability mass assigned to the NOVEL symbol |
| **Origin** | `cognitive_core.py:181` |
| **Units** | dimensionless |
| **Range** | `(0, 1)` |
| **Consumers** | curiosity engine, concept birth trigger |
| **Dependencies** | `P(NOVEL\|c)` |
| **Eq Chain** | `m_novel = P(NOVEL\|c)` |
| **Validation** | no |
| **Unused** | partial — only used in curiosity.py |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 1.12 Predicted Support `supp_pred`

| Field | Value |
|-------|-------|
| **Symbol** | `supp_pred` |
| **Name** | Predicted support |
| **Definition** | Number of symbols with non-negligible probability |
| **Origin** | `cognitive_core.py:185` |
| **Units** | dimensionless (count) |
| **Range** | `[0, ∞)` |
| **Consumers** | not directly consumed (informational) |
| **Dependencies** | `P(s\|c)` |
| **Eq Chain** | `supp_pred = count({s: P(s\|c) > ε})` |
| **Validation** | no |
| **Unused** | yes — informational only, not read by any equation |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 1.13 Rule Confidence `conf`

| Field | Value |
|-------|-------|
| **Symbol** | `conf` |
| **Name** | Rule confidence |
| **Definition** | Posterior belief strength in a rule's consequent |
| **Origin** | `cognitive_core.py:227` |
| **Units** | dimensionless |
| **Range** | `[0, 1]` |
| **Consumers** | `P(consequent\|context)`, `stb` (indirect) |
| **Dependencies** | `η_eff`, `prior_confidence`, `support_count`, `contradiction_count` |
| **Eq Chain** | `conf += η_eff · (target - conf)` where target=1 on confirmation, 0 on contradiction; also `conf = support_count / (support_count + contradiction_count)` after fracture |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | two different update rules (incremental vs fracture-reset) produce inconsistent values |
| **Circular Dep** | no (acyclic: `support_count` evolves independently of `conf`) |

---

### 1.14 Rule Support (Raw) `support_count`

| Field | Value |
|-------|-------|
| **Symbol** | `support_count` |
| **Name** | Rule support (raw) |
| **Definition** | Raw episodic tally of confirmations of a rule's consequent |
| **Origin** | `cognitive_core.py:229` |
| **Units** | dimensionless (count) |
| **Range** | `[0, ∞)` |
| **Consumers** | `stb`, `φ`, `conf` |
| **Dependencies** | observation stream, context matching |
| **Eq Chain** | `support_count += 1` on each matching observation |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 1.15 Contradiction Count `contradiction_count`

| Field | Value |
|-------|-------|
| **Symbol** | `contradiction_count` |
| **Name** | Contradiction count |
| **Definition** | Raw episodic tally of anomalies quarantined against a rule |
| **Origin** | `cognitive_core.py:231` |
| **Units** | dimensionless (count) |
| **Range** | `[0, ∞)` |
| **Consumers** | `φ`, `conf` |
| **Dependencies** | observation stream, prediction failure |
| **Eq Chain** | `contradiction_count += 1` on each prediction failure |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 1.16 Stability `stb`

| Field | Value |
|-------|-------|
| **Symbol** | `stb` |
| **Name** | Stability |
| **Definition** | `ln(1 + support_count) / (ln(1 + support_count) + ln(1 + H_m))` |
| **Origin** | `cognitive_core.py:237, 685-698` |
| **Units** | dimensionless |
| **Range** | `[0, 1)` |
| **Consumers** | `η_eff` |
| **Dependencies** | `support_count`, `H_m` |
| **Eq Chain** | `stb = ln(1+n) / (ln(1+n) + ln(1+4.0))`, where `n = support_count` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | named "stability" but shares a name with latent-cause `ST` (tightness) |
| **Circular Dep** | no (acyclic: `stb` reads `support_count`, not `confidence`) |

---

### 1.17 Fracture Ratio `φ`

| Field | Value |
|-------|-------|
| **Symbol** | `φ` |
| **Name** | Fracture ratio |
| **Definition** | `contradiction_count / support_count` |
| **Origin** | `cognitive_core.py:249, 258, 747` |
| **Units** | dimensionless |
| **Range** | `[0, ∞)` |
| **Consumers** | belief revision trigger, `K7` |
| **Dependencies** | `contradiction_count`, `support_count` |
| **Eq Chain** | `φ = contradiction_count / support_count`; if `support_count=0`, `φ = 1 if contradictions>0 else 0` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 1.18 Prediction Error (Surprisal) `ε`

| Field | Value |
|-------|-------|
| **Symbol** | `ε` |
| **Name** | Prediction error (surprisal) |
| **Definition** | `I(s)` — the Shannon surprisal of the observed symbol |
| **Origin** | `cognitive_core.py:314` |
| **Units** | bits |
| **Range** | `[0, ∞)` |
| **Consumers** | belief update trigger |
| **Dependencies** | `I(s)` |
| **Eq Chain** | `ε = I(s)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | symbol `ε` overloaded — also used for epsilon floor `ε_floor` |
| **Circular Dep** | no |

---

### 1.19 Confidence Delta (KL) `δ`

| Field | Value |
|-------|-------|
| **Symbol** | `δ` |
| **Name** | Confidence delta (KL) |
| **Definition** | `D_KL(P(posterior) \|\| P(prior))` — belief shift magnitude |
| **Origin** | `cognitive_core.py:320` |
| **Units** | bits |
| **Range** | `[0, ∞)` |
| **Consumers** | metacognitive monitoring |
| **Dependencies** | `P_prior(s\|c)`, `P_posterior(s\|c)` |
| **Eq Chain** | `δ = Σ_s P_posterior(s) · log₂(P_posterior(s) / P_prior(s))` |
| **Validation** | no |
| **Unused** | partial — logged but not used in CPI or decisions |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 1.20 Effective Learning Rate `η_eff`

| Field | Value |
|-------|-------|
| **Symbol** | `η_eff` |
| **Name** | Effective learning rate |
| **Definition** | `η_base · (1 - stability)` |
| **Origin** | `cognitive_core.py:777` |
| **Units** | dimensionless |
| **Range** | `[0, η_base]` |
| **Consumers** | `conf` update |
| **Dependencies** | `η_base`, `stb` |
| **Eq Chain** | `η_eff = η_base · (1 - stb)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | contradicts precision-weighted attention (L5) — replaces surprise-amplified learning |
| **Circular Dep** | no |

---

### 1.21 Base Learning Rate `η_base`

| Field | Value |
|-------|-------|
| **Symbol** | `η_base` |
| **Name** | Base learning rate |
| **Definition** | Default learning rate before stability modulation |
| **Origin** | `cognitive_core.py:793` |
| **Units** | dimensionless |
| **Range** | default `0.20`, coded constant |
| **Consumers** | `η_eff` |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 1.22 Stability Half-Maturity `H_m`

| Field | Value |
|-------|-------|
| **Symbol** | `H_m` |
| **Name** | Stability half-maturity |
| **Definition** | Constant defining the support count at which stability = 0.5 |
| **Origin** | `cognitive_core.py:678` |
| **Units** | dimensionless |
| **Range** | `4.0` (coded constant) |
| **Consumers** | `stb` |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no — arbitrary value, not derived |
| **Unused** | no |
| **Contradictions** | assumes ~4 confirmations is plasticity half-life |
| **Circular Dep** | no |

---

### 1.23 Fracture Threshold `τ_frac`

| Field | Value |
|-------|-------|
| **Symbol** | `τ_frac` |
| **Name** | Fracture threshold |
| **Definition** | Threshold above which `φ` triggers belief revision |
| **Origin** | `cognitive_core.py:682` |
| **Units** | dimensionless |
| **Range** | `0.85` (coded constant) |
| **Consumers** | belief revision trigger |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | `if φ >= 0.85 → fracture` |
| **Validation** | no — tuned, not derived |
| **Unused** | no |
| **Contradictions** | assumes contradictions must approach support before revising |
| **Circular Dep** | no |

---

### 1.24 Bootstrap Confidence `conf_0`

| Field | Value |
|-------|-------|
| **Symbol** | `conf_0` |
| **Name** | Bootstrap confidence |
| **Definition** | Initial confidence for newly created beliefs |
| **Origin** | `cognitive_core.py:794` |
| **Units** | dimensionless |
| **Range** | `0.50` (coded constant) |
| **Consumers** | `conf` initialization |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 1.25 Epsilon Floor `ε_floor`

| Field | Value |
|-------|-------|
| **Symbol** | `ε_floor` |
| **Name** | Epsilon floor |
| **Definition** | Minimum probability assigned to each symbol via additive smoothing |
| **Origin** | `cognitive_core.py:797` |
| **Units** | dimensionless |
| **Range** | `0.02` (coded constant) |
| **Consumers** | `P(s\|c)` via `StableBeliefModel` |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | alters relative probabilities after re-normalisation |
| **Circular Dep** | no |

---

## 2. Concept Birth Domain (`concept_birth.py`)

---

### 2.1 Total Events in Context `T`

| Field | Value |
|-------|-------|
| **Symbol** | `T` |
| **Name** | Total events in context |
| **Definition** | Number of observations in the current context window |
| **Origin** | `concept_birth.py:28` |
| **Units** | dimensionless (count) |
| **Range** | `[1, ∞)` |
| **Consumers** | `R`, `E`, `f_i`, `R/T`, `E/T` |
| **Dependencies** | observation stream |
| **Eq Chain** | `T = len(observations)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 2.2 Rule Confirmations `R`

| Field | Value |
|-------|-------|
| **Symbol** | `R` |
| **Name** | Rule confirmations |
| **Definition** | Count of observations that matched the rule consequent |
| **Origin** | `concept_birth.py:28` |
| **Units** | dimensionless (count) |
| **Range** | `[0, T]` |
| **Consumers** | `R/T`, `H_before`, `H_coarse` |
| **Dependencies** | rule matching |
| **Eq Chain** | `R = count(matching observations)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 2.3 Exception Counts `{e_1, ..., e_N}`

| Field | Value |
|-------|-------|
| **Symbol** | `{e_1, ..., e_N}` |
| **Name** | Exception counts |
| **Definition** | Per-exception tally of observations that violated the rule |
| **Origin** | `concept_birth.py:29` |
| **Units** | dimensionless (count) |
| **Range** | `[0, T]` |
| **Consumers** | `E`, `f_i`, `H_before`, `H_within` |
| **Dependencies** | observation stream, prediction failures |
| **Eq Chain** | `e_i = count(exceptions of type i)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | yes — exceptions → concept birth → probation → exception reclassification |

---

### 2.4 Total Exception Mass `E`

| Field | Value |
|-------|-------|
| **Symbol** | `E` |
| **Name** | Total exception mass |
| **Definition** | `Σ_i e_i` — sum of all exception counts |
| **Origin** | `concept_birth.py:29` |
| **Units** | dimensionless (count) |
| **Range** | `[0, T]` |
| **Consumers** | `H_within`, `H_coarse`, `G` |
| **Dependencies** | `{e_i}` |
| **Eq Chain** | `E = Σ_i e_i` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | symbol `E` is overloaded — also used for cognitive energy |
| **Circular Dep** | yes (via concept birth → probation cycle) |

---

### 2.5 Exception Frequency `f_i`

| Field | Value |
|-------|-------|
| **Symbol** | `f_i` |
| **Name** | Exception frequency |
| **Definition** | `e_i / T` |
| **Origin** | `concept_birth.py:261` |
| **Units** | dimensionless |
| **Range** | `[0, 1]` |
| **Consumers** | concept birth statistics |
| **Dependencies** | `e_i`, `T` |
| **Eq Chain** | `f_i = e_i / T` |
| **Validation** | no |
| **Unused** | partial — logged but not used in birth equation directly |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 2.6 Rule Mass `R/T`

| Field | Value |
|-------|-------|
| **Symbol** | `R/T` |
| **Name** | Rule mass |
| **Definition** | Fraction of observations that support the rule |
| **Origin** | `concept_birth.py:358` |
| **Units** | dimensionless |
| **Range** | `[0, 1]` |
| **Consumers** | `H_before`, `H_coarse` |
| **Dependencies** | `R`, `T` |
| **Eq Chain** | `rule_mass = R/T` |
| **Validation** | no |
| **Unused** | no (intermediate in H_before, H_coarse) |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 2.7 Concept Mass `E/T`

| Field | Value |
|-------|-------|
| **Symbol** | `E/T` |
| **Name** | Concept mass |
| **Definition** | Fraction of observations explained by exceptions |
| **Origin** | `concept_birth.py:357` |
| **Units** | dimensionless |
| **Range** | `[0, 1]` |
| **Consumers** | `H_coarse`, `H_within`, `G` |
| **Dependencies** | `E`, `T` |
| **Eq Chain** | `concept_mass = E/T` |
| **Validation** | no |
| **Unused** | no (intermediate in entropy calculations) |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 2.8 Within-Concept Entropy `H_within`

| Field | Value |
|-------|-------|
| **Symbol** | `H_within` |
| **Name** | Within-concept entropy |
| **Definition** | `-Σ_i (e_i/E) · log₂(e_i/E)` — entropy of exception distribution |
| **Origin** | `concept_birth.py:45` |
| **Units** | bits |
| **Range** | `[0, log₂N]` |
| **Consumers** | `G` |
| **Dependencies** | `{e_i}`, `E` |
| **Eq Chain** | `H_within = -Σ_i (e_i/E) · log₂(e_i/E)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | yes (exceptions → H_within → birth → probation → exception reclassification) |

---

### 2.9 Before-Concept Entropy `H_before`

| Field | Value |
|-------|-------|
| **Symbol** | `H_before` |
| **Name** | Before-concept entropy |
| **Definition** | `-Σ_{s∈{rule}∪exceptions} p(s) · log₂ p(s)` where `p(rule) = R/T`, `p(e_i) = e_i/T` |
| **Origin** | `concept_birth.py:361` |
| **Units** | bits |
| **Range** | `[0, ∞)` |
| **Consumers** | `G` |
| **Dependencies** | `R/T`, `{e_i/T}` |
| **Eq Chain** | `H_before = -(R/T)·log₂(R/T) - Σ_i (e_i/T)·log₂(e_i/T)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 2.10 Coarse Entropy `H_coarse`

| Field | Value |
|-------|-------|
| **Symbol** | `H_coarse` |
| **Name** | Coarse entropy |
| **Definition** | `-(R/T)·log₂(R/T) - (E/T)·log₂(E/T)` — binary entropy of rule vs. exception |
| **Origin** | `concept_birth.py:363` |
| **Units** | bits |
| **Range** | `[0, 1]` |
| **Consumers** | `H_after` |
| **Dependencies** | `R/T`, `E/T` |
| **Eq Chain** | `H_coarse = -(R/T)·log₂(R/T) - (E/T)·log₂(E/T)` |
| **Validation** | no |
| **Unused** | no (intermediate in H_after) |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 2.11 After-Concept Entropy `H_after`

| Field | Value |
|-------|-------|
| **Symbol** | `H_after` |
| **Name** | After-concept entropy |
| **Definition** | `H_coarse + λ_model` |
| **Origin** | `concept_birth.py:372` |
| **Units** | bits |
| **Range** | `[0, ∞)` |
| **Consumers** | `G` |
| **Dependencies** | `H_coarse`, `λ_model` |
| **Eq Chain** | `H_after = H_coarse + λ_model` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 2.12 Model Cost `λ_model`

| Field | Value |
|-------|-------|
| **Symbol** | `λ_model` |
| **Name** | Model cost |
| **Definition** | `log₂(N+1) / T_obs` — amortised definition cost |
| **Origin** | `concept_birth.py:59` |
| **Units** | bits/tick |
| **Range** | `[0, ∞)` |
| **Consumers** | `H_after`, `G` |
| **Dependencies** | `N`, `T_obs` |
| **Eq Chain** | `λ_model = log₂(N+1) / T_obs` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | assumes `log₂(N+1)` bits cost per new concept; no compositionality accounted for |
| **Circular Dep** | no |

---

### 2.13 Definition Bits `λ_def`

| Field | Value |
|-------|-------|
| **Symbol** | `λ_def` |
| **Name** | Definition bits |
| **Definition** | `log₂(N+1)` — bits to name a new concept |
| **Origin** | `concept_birth.py:368` |
| **Units** | bits |
| **Range** | default `log₂(\|support\|+1)` |
| **Consumers** | `λ_model` (indirectly) |
| **Dependencies** | `\|support\|` |
| **Eq Chain** | `λ_def = log₂(\|support\| + 1)` |
| **Validation** | no |
| **Unused** | partial — an intermediate; only `λ_model` is used |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 2.14 Observation Horizon `T_obs`

| Field | Value |
|-------|-------|
| **Symbol** | `T_obs` |
| **Name** | Observation horizon |
| **Definition** | Number of ticks over which definition cost is amortised |
| **Origin** | `concept_birth.py:269` |
| **Units** | ticks |
| **Range** | `[1, ∞)`, fallback `16.0` |
| **Consumers** | `λ_model` |
| **Dependencies** | none (hyperparameter or window size) |
| **Eq Chain** | constant or `T_obs = len(window)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | fallback value 16.0 may distort sparse contexts |
| **Circular Dep** | no |

---

### 2.15 Compression Gain `G`

| Field | Value |
|-------|-------|
| **Symbol** | `G` |
| **Name** | Compression gain |
| **Definition** | `H_before - H_after = (E/T)·H_within - λ_model` |
| **Origin** | `concept_birth.py:50` |
| **Units** | bits |
| **Range** | `(-∞, ∞)` |
| **Consumers** | concept birth decision (`G > θ_birth`) |
| **Dependencies** | `H_before`, `H_after` (or `E/T`, `H_within`, `λ_model`) |
| **Eq Chain** | `G = H_before - H_after = (E/T)·H_within - λ_model` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | yes — birth → probation → exception reclassification → H_before/H_within → G |

---

### 2.16 Birth Threshold `θ_birth`

| Field | Value |
|-------|-------|
| **Symbol** | `θ_birth` |
| **Name** | Birth threshold |
| **Definition** | Minimum compression gain to trigger concept birth |
| **Origin** | `concept_birth.py:123` |
| **Units** | bits |
| **Range** | `0.5` (coded constant) |
| **Consumers** | concept birth trigger |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | `born iff G > 0.5 bits` |
| **Validation** | no — arbitrary threshold |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

## 3. Continuous Vector Domain

---

### 3.1 Sensory Vector `v`

| Field | Value |
|-------|-------|
| **Symbol** | `v` |
| **Name** | Sensory vector |
| **Definition** | `D`-dimensional unit-normalised sensor reading |
| **Origin** | `environment.py:54` |
| **Units** | dimensionless (normalised sensor) |
| **Range** | `[0, 1]^D` |
| **Consumers** | `d(v₁,v₂)`, `μ_k`, `n_k`, `θ_adapt`, `S` |
| **Dependencies** | hidden state `h`, sensor weights, noise |
| **Eq Chain** | `v_i = clamp(bias_i + Σ_j w_ij · h_j + N(0, σ_noise))` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | assumes linear transduction + Gaussian noise |
| **Circular Dep** | no |

---

### 3.2 Hidden State `h`

| Field | Value |
|-------|-------|
| **Symbol** | `h` |
| **Name** | Hidden state |
| **Definition** | 3-dimensional latent regime state with relaxation dynamics |
| **Origin** | `environment.py:61` |
| **Units** | dimensionless |
| **Range** | `[0, 1]³` |
| **Consumers** | `v` |
| **Dependencies** | regime, target, relaxation rate, drift noise |
| **Eq Chain** | `h_new = clamp(h + r·(target - h) + N(0, σ_drift))` |
| **Validation** | no |
| **Unused** | no (drives sensors) |
| **Contradictions** | Gaussian drift; no trend/seasonality |
| **Circular Dep** | no |

---

### 3.3 Euclidean Distance `d(v₁, v₂)`

| Field | Value |
|-------|-------|
| **Symbol** | `d(v₁, v₂)` |
| **Name** | Euclidean distance |
| **Definition** | `√( Σ_i (a_i - b_i)² )` |
| **Origin** | `vector_prediction_core.py:22` |
| **Units** | distance units (du) |
| **Range** | `[0, √D]` |
| **Consumers** | `θ_adapt`, `S` |
| **Dependencies** | `v₁`, `v₂` |
| **Eq Chain** | `d(a,b) = √( Σ_i (a_i - b_i)² )` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | spherical K-Means assumption; cannot capture correlated clusters |
| **Circular Dep** | no |

---

### 3.4 Centroid `μ_k`

| Field | Value |
|-------|-------|
| **Symbol** | `μ_k` |
| **Name** | Centroid |
| **Definition** | Running mean of vectors assigned to cluster `k` |
| **Origin** | `vector_prediction_core.py:101` |
| **Units** | same as `v` |
| **Range** | `[0, 1]^D` |
| **Consumers** | `S`, `d_w`, merge operations |
| **Dependencies** | `μ_k_old`, `v`, `n_k` |
| **Eq Chain** | `μ_k_new = (μ_k_old · (n-1) + v) / n` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | centroid can drift towards anomaly if anomaly ratio is high |
| **Circular Dep** | yes — centroid → cluster assignment → centroid |

---

### 3.5 Cluster Count `n_k`

| Field | Value |
|-------|-------|
| **Symbol** | `n_k` |
| **Name** | Cluster count |
| **Definition** | Number of vectors assigned to cluster `k` |
| **Origin** | `vector_prediction_core.py:102` |
| **Units** | dimensionless (count) |
| **Range** | `[1, K_max]` |
| **Consumers** | `μ_k`, `A` |
| **Dependencies** | vector assignments |
| **Eq Chain** | `n_k = count(assigned vectors)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 3.6 Proximity Threshold `θ_prox`

| Field | Value |
|-------|-------|
| **Symbol** | `θ_prox` |
| **Name** | Proximity threshold |
| **Definition** | Maximum distance for a vector to be assigned to an existing cluster |
| **Origin** | `vector_prediction_core.py:169` |
| **Units** | distance units (du) |
| **Range** | `0.25` (coded constant) |
| **Consumers** | cluster assignment |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no — sensor-range dependent |
| **Unused** | no |
| **Contradictions** | assumes [`0,1`]^D sensor range |
| **Circular Dep** | no |

---

### 3.7 Cluster Count Budget `K_max`

| Field | Value |
|-------|-------|
| **Symbol** | `K_max` |
| **Name** | Cluster count budget |
| **Definition** | Maximum number of live clusters |
| **Origin** | `vector_prediction_core.py:170` |
| **Units** | dimensionless (count) |
| **Range** | `50` (coded constant) |
| **Consumers** | cluster creation |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no — arbitrary budget |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 3.8 Prediction Error (Vector) `S`

| Field | Value |
|-------|-------|
| **Symbol** | `S` |
| **Name** | Prediction error (vector) |
| **Definition** | Euclidean distance between predicted centroid and observed vector |
| **Origin** | `vector_prediction_core.py:591` |
| **Units** | distance units (du) |
| **Range** | `[0, √D]` |
| **Consumers** | `θ_adapt`, `ρ`, `E`, `S_high` |
| **Dependencies** | `predicted_centroid`, `v` |
| **Eq Chain** | `S = d(predicted_centroid, v)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | symbol `S` overloaded — also used for Shannon surprisal `I(s)` context; `S_high` threshold is 0.50 du |
| **Circular Dep** | yes — S → θ_adapt → anomaly quarantine → cluster structure → S |

---

### 3.9 Adaptive Threshold `θ_adapt`

| Field | Value |
|-------|-------|
| **Symbol** | `θ_adapt` |
| **Name** | Adaptive threshold |
| **Definition** | `μ_recent_errors + 1.5 · σ_recent_errors` |
| **Origin** | `vector_prediction_core.py:566` |
| **Units** | distance units (du) |
| **Range** | `[0.15, ∞)` |
| **Consumers** | anomaly classification |
| **Dependencies** | recent prediction errors `S` |
| **Eq Chain** | `θ_adapt = μ + 1.5·σ`; fallback `0.15` when < 5 samples |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | fallback 0.15 is arbitrary |
| **Circular Dep** | yes — S → θ_adapt → anomaly flag → cluster → S |

---

### 3.10 Surprise Rate `ρ`

| Field | Value |
|-------|-------|
| **Symbol** | `ρ` |
| **Name** | Surprise rate |
| **Definition** | Fraction of recent errors exceeding `θ_adapt` |
| **Origin** | `vector_prediction_core.py:602` |
| **Units** | dimensionless |
| **Range** | `[0, 1]` |
| **Consumers** | metacognitive signals |
| **Dependencies** | `S`, `θ_adapt` |
| **Eq Chain** | `ρ = count(S > θ_adapt) / len(recent_errors)` |
| **Validation** | no |
| **Unused** | partial — logged but no direct CPI contribution |
| **Contradictions** | none |
| **Circular Dep** | yes (via same S → θ_adapt loop) |

---

### 3.11 Markov Transition Count `T(i→j)`

| Field | Value |
|-------|-------|
| **Symbol** | `T(i→j)` |
| **Name** | Markov transition count |
| **Definition** | Count of transitions from cluster `i` to cluster `j` |
| **Origin** | `vector_prediction_core.py:632` |
| **Units** | dimensionless (count) |
| **Range** | `[0, ∞)` |
| **Consumers** | `H(entropy)` |
| **Dependencies** | cluster assignment sequence |
| **Eq Chain** | `T(i→j) += 1` on each transition |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | assumes Markov order = 1 |
| **Circular Dep** | no |

---

### 3.12 Attention Weight `w_d`

| Field | Value |
|-------|-------|
| **Symbol** | `w_d` |
| **Name** | Attention weight (vector) |
| **Definition** | Per-dimension weight: `sf` for all, `f_mult · cause.importance` for attended dimension |
| **Origin** | `vector_prediction_core.py:828` |
| **Units** | dimensionless |
| **Range** | `[sf, f_mult]` |
| **Consumers** | `d_w` |
| **Dependencies** | `sf`, `f_mult`, `cause.importance` |
| **Eq Chain** | `w_i = sf` for all i; `w_{attended} = f_mult · cause.importance` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | assumes 10× weight difference dominates clustering |
| **Circular Dep** | yes — attention → cluster formation → latent cause → attention |

---

### 3.13 Focus Multiplier `f_mult`

| Field | Value |
|-------|-------|
| **Symbol** | `f_mult` |
| **Name** | Focus multiplier |
| **Definition** | Multiplier for attended dimension weight |
| **Origin** | `vector_prediction_core.py:727` |
| **Units** | dimensionless |
| **Range** | `10.0` (coded constant) |
| **Consumers** | `w_d` |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | assumes 10× is sufficient to dominate; may cause fixation |
| **Circular Dep** | no |

---

### 3.14 Suppress Floor `sf`

| Field | Value |
|-------|-------|
| **Symbol** | `sf` |
| **Name** | Suppress floor |
| **Definition** | Minimum weight for non-attended dimensions |
| **Origin** | `vector_prediction_core.py:728` |
| **Units** | dimensionless |
| **Range** | `0.05` (coded constant) |
| **Consumers** | `w_d` |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | prevents complete blindness but allows 5% leakage |
| **Circular Dep** | no |

---

### 3.15 Latent Variable Arity `k`

| Field | Value |
|-------|-------|
| **Symbol** | `k` |
| **Name** | Latent variable arity |
| **Definition** | Number of constrained dimensions discovered by a latent cause |
| **Origin** | `latent_cause_engine.py:87` |
| **Units** | dimensionless (count) |
| **Range** | `[1, D]` |
| **Consumers** | `CG`, `Score` |
| **Dependencies** | latent variable discovery |
| **Eq Chain** | `k = arity of discovered predicate set` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 3.16 Prediction Gain `PG`

| Field | Value |
|-------|-------|
| **Symbol** | `PG` |
| **Name** | Prediction gain |
| **Definition** | `coverage · (1 - FPR)` |
| **Origin** | `latent_cause_engine.py:104` |
| **Units** | dimensionless |
| **Range** | `[0, 1]` |
| **Consumers** | `Score` |
| **Dependencies** | `cov`, `FPR` |
| **Eq Chain** | `PG = coverage · (1 - FPR)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 3.17 Compression Gain (MDL) `CG`

| Field | Value |
|-------|-------|
| **Symbol** | `CG` |
| **Name** | Compression gain (MDL) |
| **Definition** | `max(0, savings) / max(cost_raw, ε)` where `savings = m·k·b - k·(b+log₂(max(D,2))) - n`, `cost_raw = n·D·b` |
| **Origin** | `latent_cause_engine.py:105` |
| **Units** | dimensionless |
| **Range** | `[0, 1]` |
| **Consumers** | `Score` |
| **Dependencies** | `k`, `b`, `D`, `n`, `m` |
| **Eq Chain** | `CG = max(0, m·k·b - k·(b+log₂(max(D,2))) - n) / max(n·D·b, ε)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 3.18 Stability (Tightness) `ST`

| Field | Value |
|-------|-------|
| **Symbol** | `ST` |
| **Name** | Stability (tightness) |
| **Definition** | Mean of `max(0, 1 - spread_p / 0.5)` over all predicates |
| **Origin** | `latent_cause_engine.py:106` |
| **Units** | dimensionless |
| **Range** | `[0, 1]` |
| **Consumers** | `Score` |
| **Dependencies** | stdev of matched values per predicate dimension |
| **Eq Chain** | `tightness_p = max(0, 1 - spread_p / 0.5); ST = mean(tightness_p)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | assumes sensor range [0,1]; reference spread 0.5 is arbitrary |
| **Circular Dep** | no |

---

### 3.19 Combined Score `Score`

| Field | Value |
|-------|-------|
| **Symbol** | `Score` |
| **Name** | Combined score |
| **Definition** | `α·PG + β·CG + γ·ST` with default weights (0.5, 0.30, 0.20) |
| **Origin** | `latent_cause_engine.py:23` |
| **Units** | dimensionless |
| **Range** | `[0, α+β+γ]` |
| **Consumers** | latent cause promotion (`Score > 0.50`) |
| **Dependencies** | `PG`, `CG`, `ST` |
| **Eq Chain** | `Score = 0.5·PG + 0.30·CG + 0.20·ST` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | weights (0.5, 0.30, 0.20) are arbitrary; promotion threshold 0.50 is arbitrary |
| **Circular Dep** | yes — Score → latent cause → attention → cluster → Score |

---

### 3.20 Coverage `cov`

| Field | Value |
|-------|-------|
| **Symbol** | `cov` |
| **Name** | Coverage |
| **Definition** | `matches_on_quarantine / |quarantine|` |
| **Origin** | `latent_cause_engine.py:299` |
| **Units** | dimensionless |
| **Range** | `[0, 1]` |
| **Consumers** | `PG` |
| **Dependencies** | `matches_on_quarantine`, `|quarantine|` |
| **Eq Chain** | `cov = matches_on_quarantine / |quarantine|` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | yes — cov → PG → Score → cause promotion → quarantine → cov |

---

### 3.21 False Positive Rate `FPR`

| Field | Value |
|-------|-------|
| **Symbol** | `FPR` |
| **Name** | False positive rate |
| **Definition** | `matches_on_baseline / |baseline|` |
| **Origin** | `latent_cause_engine.py:301` |
| **Units** | dimensionless |
| **Range** | `[0, 1]` |
| **Consumers** | `PG` |
| **Dependencies** | `matches_on_baseline`, `|baseline|` |
| **Eq Chain** | `FPR = matches_on_baseline / |baseline|` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 3.22 Bits Per Value `b`

| Field | Value |
|-------|-------|
| **Symbol** | `b` |
| **Name** | Bits per value |
| **Definition** | Number of bits to encode a single sensor value |
| **Origin** | `latent_cause_engine.py:157` |
| **Units** | bits |
| **Range** | `8` (coded constant) |
| **Consumers** | `CG` |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | assumes 8-bit precision for sensor values |
| **Circular Dep** | no |

---

## 4. Cognitive Telemetry / CPI Domain

---

### 4.1 Surprise Ceiling `S_max`

| Field | Value |
|-------|-------|
| **Symbol** | `S_max` |
| **Name** | Surprise ceiling |
| **Definition** | Maximum surprisal value, applied as clamp |
| **Origin** | `cognitive_telemetry.py:94` |
| **Units** | bits |
| **Range** | `5.0` (coded constant) |
| **Consumers** | surprise normalisation |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | `clamped_surprise = min(I(s), 5.0)` |
| **Validation** | no — assumes ~32 equiprobable symbols is max uncertainty |
| **Unused** | no |
| **Contradictions** | breaks for larger vocabularies; real `I(s)` can exceed 5.0 |
| **Circular Dep** | no |

---

### 4.2 EWMA Accuracy `acc`

| Field | Value |
|-------|-------|
| **Symbol** | `acc` |
| **Name** | EWMA accuracy |
| **Definition** | `(1 - α_acc)·prev + α_acc·sample` where `sample = 1 - normalised_surprise` |
| **Origin** | `cognitive_telemetry.py:375` |
| **Units** | dimensionless |
| **Range** | `[0, 1]` |
| **Consumers** | `A_t` |
| **Dependencies** | previous `acc`, `I(s)`, `S_max` |
| **Eq Chain** | `acc = EWMA(acc, 1 - min(I(s),S_max)/S_max, α_acc)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | normalisation assumes S_max=5.0 is correct ceiling |
| **Circular Dep** | no |

---

### 4.3 EWMA Surprise `μ_surp`

| Field | Value |
|-------|-------|
| **Symbol** | `μ_surp` |
| **Name** | EWMA surprise |
| **Definition** | `(1 - α_surp)·prev + α_surp·sample` where `sample = I(s)` |
| **Origin** | `cognitive_telemetry.py:377` |
| **Units** | bits |
| **Range** | `[0, ∞)` |
| **Consumers** | plateau detection, `D_t` |
| **Dependencies** | previous `μ_surp`, `I(s)` |
| **Eq Chain** | `μ_surp = EWMA(μ_surp, I(s), α_surp)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 4.4 Decay Score `dec`

| Field | Value |
|-------|-------|
| **Symbol** | `dec` |
| **Name** | Decay score |
| **Definition** | `clamp(1 - tail_mean / peak_error)` — fraction of spike peak absorbed |
| **Origin** | `cognitive_telemetry.py:437` |
| **Units** | dimensionless |
| **Range** | `[0, 1]` |
| **Consumers** | `D_t` |
| **Dependencies** | `I(s)` spike peak, tail window |
| **Eq Chain** | `dec = clamp(1 - mean(tail_errors) / peak_error)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | tail window default 4 is arbitrary |
| **Circular Dep** | no |

---

### 4.5 Compression Ratio `CR`

| Field | Value |
|-------|-------|
| **Symbol** | `CR` |
| **Name** | Compression ratio |
| **Definition** | `samples_seen / consolidated_concepts` |
| **Origin** | `cognitive_telemetry.py:416` |
| **Units** | dimensionless |
| **Range** | `[1, ∞)` |
| **Consumers** | compression component |
| **Dependencies** | `samples_seen`, `consolidated_concepts` |
| **Eq Chain** | `CR = samples_seen / max(consolidated_concepts, 1)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | conflates concept count with compression quality |
| **Circular Dep** | no |

---

### 4.6 Contradictions Resolved `C_res`

| Field | Value |
|-------|-------|
| **Symbol** | `C_res` |
| **Name** | Contradictions resolved |
| **Definition** | Monotone counter of reified contradictions (concept birth events) |
| **Origin** | `cognitive_telemetry.py:315` |
| **Units** | dimensionless (count) |
| **Range** | `[0, ∞)` |
| **Consumers** | resolution component |
| **Dependencies** | concept birth events |
| **Eq Chain** | `C_res += 1` on each concept birth |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 4.7 Accuracy Trend `A_t`

| Field | Value |
|-------|-------|
| **Symbol** | `A_t` |
| **Name** | Accuracy trend |
| **Definition** | EWMA of `1 - normalised_surprise` |
| **Origin** | `cognitive_telemetry.py:210` |
| **Units** | dimensionless |
| **Range** | `[0, 1]` |
| **Consumers** | `CPI` |
| **Dependencies** | `acc` (EWMA accuracy) |
| **Eq Chain** | `A_t = acc` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 4.8 Surprise Decay `D_t`

| Field | Value |
|-------|-------|
| **Symbol** | `D_t` |
| **Name** | Surprise decay |
| **Definition** | EWMA of `dec` (decay score) |
| **Origin** | `cognitive_telemetry.py:211` |
| **Units** | dimensionless |
| **Range** | `[0, 1]` |
| **Consumers** | `CPI` |
| **Dependencies** | `dec` |
| **Eq Chain** | `D_t = EWMA(dec, dec_sample, α_dec)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 4.9 CPI Composite `CPI`

| Field | Value |
|-------|-------|
| **Symbol** | `CPI` |
| **Name** | Cognitive Progress Index |
| **Definition** | `(0.40·A_t + 0.30·D_t + 0.20·comp_comp + 0.10·res_comp) / 1.0` |
| **Origin** | `cognitive_telemetry.py:237` |
| **Units** | dimensionless |
| **Range** | `[0, 1]` |
| **Consumers** | kill criteria `K1`, `K8` |
| **Dependencies** | `A_t`, `D_t`, `CR`, `C_res` |
| **Eq Chain** | `CPI = 0.40·A_t + 0.30·D_t + 0.20·(1-exp(-(CR-1))) + 0.10·(1-exp(-C_res/3))` |
| **Validation** | yes — `E10` live-fire simulation |
| **Unused** | no |
| **Contradictions** | weights (0.40, 0.30, 0.20, 0.10) entirely arbitrary; accuracy weighted 4× contradictions |
| **Circular Dep** | no |

---

### 4.10 EWMA Alpha (Accuracy) `α_acc`

| Field | Value |
|-------|-------|
| **Symbol** | `α_acc` |
| **Name** | EWMA alpha (accuracy) |
| **Definition** | EWMA smoothing factor for accuracy |
| **Origin** | `cognitive_telemetry.py:87` |
| **Units** | dimensionless |
| **Range** | `0.15` (coded constant) |
| **Consumers** | `acc` |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no — manually chosen |
| **Unused** | no |
| **Contradictions** | not derived from data |
| **Circular Dep** | no |

---

### 4.11 EWMA Alpha (Surprise) `α_surp`

| Field | Value |
|-------|-------|
| **Symbol** | `α_surp` |
| **Name** | EWMA alpha (surprise) |
| **Definition** | EWMA smoothing factor for surprise |
| **Origin** | `cognitive_telemetry.py:88` |
| **Units** | dimensionless |
| **Range** | `0.20` (coded constant) |
| **Consumers** | `μ_surp` |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | not derived from data |
| **Circular Dep** | no |

---

### 4.12 EWMA Alpha (Decay) `α_dec`

| Field | Value |
|-------|-------|
| **Symbol** | `α_dec` |
| **Name** | EWMA alpha (decay) |
| **Definition** | EWMA smoothing factor for decay score |
| **Origin** | `cognitive_telemetry.py:89` |
| **Units** | dimensionless |
| **Range** | `0.10` (coded constant) |
| **Consumers** | `D_t` |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | not derived from data |
| **Circular Dep** | no |

---

## 5. Free Energy Domain

---

### 5.1 Transition Entropy `H`

| Field | Value |
|-------|-------|
| **Symbol** | `H` |
| **Name** | Transition entropy |
| **Definition** | Conditional Shannon entropy of the cluster-transition Markov chain |
| **Origin** | `validation/metrics.py:113` |
| **Units** | bits |
| **Range** | `[0, log₂K]` |
| **Consumers** | `E`, `H_high` |
| **Dependencies** | `T(i→j)` for all `i,j` |
| **Eq Chain** | `H = Σ_src p_visit(src) · (-Σ_dst p(dst\|src) · log₂ p(dst\|src))` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | assumes Markov order = 1 |
| **Circular Dep** | yes — merge changes cluster structure → T(i→j) → H → ΔE → merge decision |

---

### 5.2 Spatial Surprise `S`

| Field | Value |
|-------|-------|
| **Symbol** | `S` |
| **Name** | Spatial surprise |
| **Definition** | Euclidean distance between predicted centroid and observed vector |
| **Origin** | `validation/metrics.py:154` |
| **Units** | distance units (du) |
| **Range** | `[0, √D]` |
| **Consumers** | `E`, `S_high` |
| **Dependencies** | predicted centroid, `v` |
| **Eq Chain** | `S = d(predicted_centroid, v)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | symbol `S` overloaded (Shannon surprisal `I(s)`); S_high threshold 0.50 not derived |
| **Circular Dep** | yes (via merge → cluster → centroid → S → ΔE → merge) |

---

### 5.3 Active Load `A`

| Field | Value |
|-------|-------|
| **Symbol** | `A` |
| **Name** | Active load |
| **Definition** | `cluster_count + V_anom` |
| **Origin** | `validation/metrics.py:189` |
| **Units** | clusters + variance units |
| **Range** | `[0, ∞)` |
| **Consumers** | `E`, `P_high` |
| **Dependencies** | `cluster_count`, `V_anom` |
| **Eq Chain** | `A = cluster_count + V_anom` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | incommensurate sum: clusters (count) + variance (sum of variances) |
| **Circular Dep** | yes (via merge → cluster → A → ΔE → merge) |

---

### 5.4 Anomaly Spatial Volume `V_anom`

| Field | Value |
|-------|-------|
| **Symbol** | `V_anom` |
| **Name** | Anomaly spatial volume |
| **Definition** | `Σ_{d=1}^{D} Var(anomaly_vectors[d])` |
| **Origin** | `validation/metrics.py:167` |
| **Units** | variance units |
| **Range** | `[0, ∞)` |
| **Consumers** | `A` |
| **Dependencies** | anomaly vectors |
| **Eq Chain** | `V_anom = Σ_d Var(anomaly_vectors[d])` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | assumes anomaly cloud is a contiguous volume |
| **Circular Dep** | yes (merge → anomalies → V_anom → A → ΔE → merge) |

---

### 5.5 Cognitive Energy `E`

| Field | Value |
|-------|-------|
| **Symbol** | `E` |
| **Name** | Cognitive energy |
| **Definition** | `λ·H + μ·S + ν·A` with `(λ,μ,ν) = (1.0, 2.0, 0.5)` |
| **Origin** | `validation/metrics.py:197` |
| **Units** | arbitrary energy units (a.u.) |
| **Range** | `[0, ∞)` |
| **Consumers** | `E_before`, `E_after`, regime classification, `E_exhaust` |
| **Dependencies** | `H`, `S`, `A`, `λ`, `μ`, `ν` |
| **Eq Chain** | `E = 1.0·H + 2.0·S + 0.5·A` |
| **Validation** | partially — `E5`, `E6`, `E7` experiments |
| **Unused** | no |
| **Contradictions** | mixes bits, du, and cluster+variance with uncalibrated coefficients (primary known inconsistency) |
| **Circular Dep** | yes — E → merge decision → cluster → H/S/A → E |

---

### 5.6 Lambda (H Weight) `λ`

| Field | Value |
|-------|-------|
| **Symbol** | `λ` |
| **Name** | Lambda (H weight) |
| **Definition** | Weight on transition entropy in cognitive energy |
| **Origin** | `validation/metrics.py:59` |
| **Units** | a.u./bit |
| **Range** | `1.0` (coded constant) |
| **Consumers** | `E` |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no — hand-tuned |
| **Unused** | no |
| **Contradictions** | no sensitivity analysis; coefficient unjustified |
| **Circular Dep** | no |

---

### 5.7 Mu (S Weight) `μ`

| Field | Value |
|-------|-------|
| **Symbol** | `μ` |
| **Name** | Mu (S weight) |
| **Definition** | Weight on spatial surprise in cognitive energy |
| **Origin** | `validation/metrics.py:60` |
| **Units** | a.u./du |
| **Range** | `2.0` (coded constant) |
| **Consumers** | `E` |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | no scaling analysis |
| **Circular Dep** | no |

---

### 5.8 Nu (A Weight) `ν`

| Field | Value |
|-------|-------|
| **Symbol** | `ν` |
| **Name** | Nu (A weight) |
| **Definition** | Weight on active load in cognitive energy |
| **Origin** | `validation/metrics.py:61` |
| **Units** | a.u./cluster-or-var |
| **Range** | `0.5` (coded constant) |
| **Consumers** | `E` |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | no scaling analysis |
| **Circular Dep** | no |

---

### 5.9 Energy Exhaustion Threshold `E_exhaust`

| Field | Value |
|-------|-------|
| **Symbol** | `E_exhaust` |
| **Name** | Energy exhaustion threshold |
| **Definition** | Threshold above which cognitive system enters EXHAUSTION regime |
| **Origin** | `validation/metrics.py:72` |
| **Units** | a.u. |
| **Range** | `18.0` (coded constant) |
| **Consumers** | regime classification |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | `if E >= 18.0 → regime = EXHAUSTION` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | not derived from theory |
| **Circular Dep** | no |

---

### 5.10 Entropy High Threshold `H_high`

| Field | Value |
|-------|-------|
| **Symbol** | `H_high` |
| **Name** | Entropy high threshold |
| **Definition** | Threshold above which H is considered high |
| **Origin** | `validation/metrics.py:67` |
| **Units** | bits |
| **Range** | `2.0` (coded constant) |
| **Consumers** | regime classification |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no |
| **Unused** | partial — defined but not directly used in equations shown |
| **Contradictions** | not derived |
| **Circular Dep** | no |

---

### 5.11 Surprise High Threshold `S_high`

| Field | Value |
|-------|-------|
| **Symbol** | `S_high` |
| **Name** | Surprise high threshold |
| **Definition** | Threshold above which S is considered high |
| **Origin** | `validation/metrics.py:68` |
| **Units** | distance units (du) |
| **Range** | `0.50` (coded constant) |
| **Consumers** | regime classification |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no |
| **Unused** | partial — defined but not directly used |
| **Contradictions** | 0.50 du is arbitrary |
| **Circular Dep** | no |

---

### 5.12 Pressure High Threshold `P_high`

| Field | Value |
|-------|-------|
| **Symbol** | `P_high` |
| **Name** | Pressure high threshold |
| **Definition** | Threshold above which pressure is considered high |
| **Origin** | `validation/metrics.py:70` |
| **Units** | dimensionless |
| **Range** | `1.00` (coded constant) |
| **Consumers** | regime classification |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no |
| **Unused** | partial |
| **Contradictions** | not derived |
| **Circular Dep** | no |

---

## 6. Decision Policy Domain

---

### 6.1 Energy Before Merge `E_before`

| Field | Value |
|-------|-------|
| **Symbol** | `E_before` |
| **Name** | Energy before merge |
| **Definition** | Cognitive energy measured on the current (unmerged) cluster state |
| **Origin** | `decision_policy.py:249` |
| **Units** | a.u. |
| **Range** | `[0, ∞)` |
| **Consumers** | `ΔE` |
| **Dependencies** | `H`, `S`, `A` on current state |
| **Eq Chain** | `E_before = f(current_cluster_state)` |
| **Validation** | yes — `E7`, `E13` experiments |
| **Unused** | no |
| **Contradictions** | depends on recent_vectors window which was generated under old clustering |
| **Circular Dep** | yes (merge evaluation depends on cluster structure being evaluated) |

---

### 6.2 Energy After Merge `E_after`

| Field | Value |
|-------|-------|
| **Symbol** | `E_after` |
| **Name** | Energy after merge |
| **Definition** | Cognitive energy measured on the sandbox-simulated merged cluster state |
| **Origin** | `decision_policy.py:250` |
| **Units** | a.u. |
| **Range** | `[0, ∞)` |
| **Consumers** | `ΔE` |
| **Dependencies** | `H`, `S`, `A` on sandbox state |
| **Eq Chain** | `E_after = f(sandbox_merged_state)` |
| **Validation** | yes |
| **Unused** | no |
| **Contradictions** | sandbox is a deepcopy but recent_vectors were generated under old clustering |
| **Circular Dep** | yes |

---

### 6.3 Delta Prediction `ΔS`

| Field | Value |
|-------|-------|
| **Symbol** | `ΔS` |
| **Name** | Delta prediction |
| **Definition** | `S_before - S_after` — change in spatial surprise after merge |
| **Origin** | `decision_policy.py:254` |
| **Units** | distance units (du) |
| **Range** | `(-∞, ∞)` |
| **Consumers** | Pareto dominance test |
| **Dependencies** | `S_before`, `S_after` |
| **Eq Chain** | `ΔS = S_before - S_after` |
| **Validation** | yes (via E7) |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | yes |

---

### 6.4 Delta Entropy `ΔH`

| Field | Value |
|-------|-------|
| **Symbol** | `ΔH` |
| **Name** | Delta entropy |
| **Definition** | `H_before - H_after` — change in transition entropy after merge |
| **Origin** | `decision_policy.py:255` |
| **Units** | bits |
| **Range** | `(-∞, ∞)` |
| **Consumers** | Pareto dominance test |
| **Dependencies** | `H_before`, `H_after` (from merge sandbox) |
| **Eq Chain** | `ΔH = H_before - H_after` |
| **Validation** | yes |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | yes |

---

### 6.5 Delta Load `ΔA`

| Field | Value |
|-------|-------|
| **Symbol** | `ΔA` |
| **Name** | Delta load |
| **Definition** | `A_before - A_after` — change in active load after merge |
| **Origin** | `decision_policy.py:256` |
| **Units** | clusters + variance units |
| **Range** | `(-∞, ∞)` |
| **Consumers** | Pareto dominance test |
| **Dependencies** | `A_before`, `A_after` |
| **Eq Chain** | `ΔA = A_before - A_after` |
| **Validation** | yes |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | yes |

---

### 6.6 Delta Energy `ΔE`

| Field | Value |
|-------|-------|
| **Symbol** | `ΔE` |
| **Name** | Delta energy |
| **Definition** | `E_before - E_after` — free energy reduction |
| **Origin** | `decision_policy.py:257` |
| **Units** | a.u. |
| **Range** | `(-∞, ∞)` |
| **Consumers** | merge acceptance decision |
| **Dependencies** | `E_before`, `E_after` |
| **Eq Chain** | `ΔE = E_before - E_after` |
| **Validation** | yes |
| **Unused** | no |
| **Contradictions** | threshold tolerance `tol` can allow positive-energy merges |
| **Circular Dep** | yes — ΔE ≥ -tol → merge accept → cluster → H/S/A → ΔE |

---

### 6.7 Tolerance `tol`

| Field | Value |
|-------|-------|
| **Symbol** | `tol` |
| **Name** | Tolerance |
| **Definition** | Allowable energy increase for merge acceptance |
| **Origin** | `decision_policy.py:186` |
| **Units** | a.u. |
| **Range** | `[0, ∞)`, default `0.0` |
| **Consumers** | merge acceptance decision |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | `merge accepted iff ΔE >= -tol` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | tolerance > 0 contradicts strict free energy minimization |
| **Circular Dep** | no |

---

## 7. Bayesian Living Edge Domain

---

### 7.1 Beta Alpha `α_w`

| Field | Value |
|-------|-------|
| **Symbol** | `α_w` |
| **Name** | Beta alpha |
| **Definition** | Alpha parameter (pseudo-count of successes) for Beta posterior |
| **Origin** | `living_edges.py:49` |
| **Units** | dimensionless (pseudo-count) |
| **Range** | `(0, ∞)`, default `1.0` |
| **Consumers** | `μ_w`, `n_plus` |
| **Dependencies** | prior `α_w0`, `q_src` |
| **Eq Chain** | `α_w += q_src` on reinforce |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 7.2 Beta Beta `β_w`

| Field | Value |
|-------|-------|
| **Symbol** | `β_w` |
| **Name** | Beta beta |
| **Definition** | Beta parameter (pseudo-count of failures) for Beta posterior |
| **Origin** | `living_edges.py:50` |
| **Units** | dimensionless (pseudo-count) |
| **Range** | `(0, ∞)`, default `1.0` |
| **Consumers** | `μ_w`, `n_minus` |
| **Dependencies** | prior `β_w0`, `q_src` |
| **Eq Chain** | `β_w += q_src` on challenge |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 7.3 Asymptotic Weight `w_asym`

| Field | Value |
|-------|-------|
| **Symbol** | `w_asym` |
| **Name** | Asymptotic weight |
| **Definition** | Hebbian edge strength with asymptotic decay/enforcement |
| **Origin** | `living_edges.py:48` |
| **Units** | dimensionless |
| **Range** | `[0, 1]`, default `0.7` |
| **Consumers** | edge confidence, pruning |
| **Dependencies** | previous `w_asym`, `λ_upd` |
| **Eq Chain** | Reinforce: `w_asym += λ_upd·(1 - w_asym)`; Challenge: `w_asym -= λ_upd·w_asym` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 7.4 Bayesian Weight Mean `μ_w`

| Field | Value |
|-------|-------|
| **Symbol** | `μ_w` |
| **Name** | Bayesian weight mean |
| **Definition** | `α_w / (α_w + β_w)` — mean of Beta posterior |
| **Origin** | `living_edges.py:93` |
| **Units** | dimensionless |
| **Range** | `(0, 1)` |
| **Consumers** | epistemic status (CERTAIN/PROBABLE/CONTESTED/UNCERTAIN) |
| **Dependencies** | `α_w`, `β_w` |
| **Eq Chain** | `μ_w = α_w / (α_w + β_w)` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 7.5 Reinforced Count `n_plus`

| Field | Value |
|-------|-------|
| **Symbol** | `n_plus` |
| **Name** | Reinforced count |
| **Definition** | `α_w - 1` |
| **Origin** | `living_edges.py:89` |
| **Units** | dimensionless (count) |
| **Range** | `[0, ∞)` |
| **Consumers** | `n_ev`, epistemic status |
| **Dependencies** | `α_w` |
| **Eq Chain** | `n_plus = α_w - 1` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 7.6 Challenged Count `n_minus`

| Field | Value |
|-------|-------|
| **Symbol** | `n_minus` |
| **Name** | Challenged count |
| **Definition** | `β_w - 1` |
| **Origin** | `living_edges.py:90` |
| **Units** | dimensionless (count) |
| **Range** | `[0, ∞)` |
| **Consumers** | `n_ev`, `γ`, epistemic status |
| **Dependencies** | `β_w` |
| **Eq Chain** | `n_minus = β_w - 1` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 7.7 Evidence Count `n_ev`

| Field | Value |
|-------|-------|
| **Symbol** | `n_ev` |
| **Name** | Evidence count |
| **Definition** | `n_plus + n_minus` |
| **Origin** | `living_edges.py:91` |
| **Units** | dimensionless (count) |
| **Range** | `[0, ∞)` |
| **Consumers** | epistemic status |
| **Dependencies** | `n_plus`, `n_minus` |
| **Eq Chain** | `n_ev = n_plus + n_minus` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 7.8 Challenge Rate `γ`

| Field | Value |
|-------|-------|
| **Symbol** | `γ` |
| **Name** | Challenge rate |
| **Definition** | `n_minus / n_ev` if `n_ev > 0` else `0.0` |
| **Origin** | `living_edges.py:94` |
| **Units** | dimensionless |
| **Range** | `[0, 1]` |
| **Consumers** | epistemic status (`γ <= 0.05` for CERTAIN) |
| **Dependencies** | `n_minus`, `n_ev` |
| **Eq Chain** | `γ = n_minus / n_ev` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

### 7.9 Update Lambda `λ_upd`

| Field | Value |
|-------|-------|
| **Symbol** | `λ_upd` |
| **Name** | Update lambda |
| **Definition** | Step size for asymptotic weight updates |
| **Origin** | `living_edges.py:147` |
| **Units** | dimensionless |
| **Range** | `0.15` (coded constant) |
| **Consumers** | `w_asym` |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | same value as `α_acc` (0.15) but unrelated |
| **Circular Dep** | no |

---

### 7.10 Source Quality `q_src`

| Field | Value |
|-------|-------|
| **Symbol** | `q_src` |
| **Name** | Source quality |
| **Definition** | Weight increment for Beta parameter updates |
| **Origin** | `living_edges.py:66` |
| **Units** | dimensionless |
| **Range** | `[0, 1]`, default `0.5` |
| **Consumers** | `α_w`, `β_w` |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | constant or source-dependent |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | none |
| **Circular Dep** | no |

---

## 8. Memory Scheduling Domain

---

### 8.1 Time Interval `τ_interval`

| Field | Value |
|-------|-------|
| **Symbol** | `τ_interval` |
| **Name** | Time interval |
| **Definition** | Minimum ticks between consolidation cycles |
| **Origin** | `memory_scheduler.py:43` |
| **Units** | ticks |
| **Range** | `500` (coded constant) |
| **Consumers** | consolidation trigger |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | `if ticks_since >= 500 → consolidate` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | arbitrary value |
| **Circular Dep** | no |

---

### 8.2 Enter Pressure (High Watermark) `P_enter`

| Field | Value |
|-------|-------|
| **Symbol** | `P_enter` |
| **Name** | Enter pressure (high watermark) |
| **Definition** | Anomaly count that triggers immediate consolidation |
| **Origin** | `memory_scheduler.py:44` |
| **Units** | dimensionless (count) |
| **Range** | `20` (coded constant) |
| **Consumers** | consolidation trigger |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | `if anomalies >= 20 → consolidate` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | arbitrary value |
| **Circular Dep** | no |

---

### 8.3 Exit Pressure (Low Watermark) `P_exit`

| Field | Value |
|-------|-------|
| **Symbol** | `P_exit` |
| **Name** | Exit pressure (low watermark) |
| **Definition** | Anomaly count below which consolidation turns off |
| **Origin** | `memory_scheduler.py:45` |
| **Units** | dimensionless (count) |
| **Range** | `10` (coded constant) |
| **Consumers** | consolidation trigger (hysteresis) |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | `if anomalies <= 10 → stop consolidation` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | hysteresis gap 10-20 prevents oscillation but is arbitrary |
| **Circular Dep** | no |

---

### 8.4 Cooldown `τ_cooldown`

| Field | Value |
|-------|-------|
| **Symbol** | `τ_cooldown` |
| **Name** | Cooldown |
| **Definition** | Ticks after consolidation during which all triggers are suppressed |
| **Origin** | `memory_scheduler.py:46` |
| **Units** | ticks |
| **Range** | `50` (coded constant) |
| **Consumers** | consolidation suppression |
| **Dependencies** | none (hyperparameter) |
| **Eq Chain** | `if cooldown_remaining > 0 → suppress triggers` |
| **Validation** | no |
| **Unused** | no |
| **Contradictions** | arbitrary value |
| **Circular Dep** | no |

---

## 9. Summary of Critical Findings

### 9.1 Unused Variables

| Variable | Reason |
|----------|--------|
| `supp_pred` | Predicted support — informational only, no consumer equation |
| `f_i` | Exception frequency — logged but not consumed in G or birth equation |
| `λ_def` | Definition bits — intermediate only; `λ_model` is the consumed form |
| `H_high`, `S_high`, `P_high` | Thresholds defined but not found as consumers in main equations |

### 9.2 Contradictions

| Variables | Conflict |
|-----------|----------|
| `a(s)` vs `stb` / `η_eff` | C5 precision-weighting (surprise amplifies learning) vs C6 Inertia Law (stability suppresses learning). Directly contradictory update rules. |
| `E = λH+μS+νA` | Incommensurate units: bits + du + cluster/variance counts. Coefficients hand-tuned. |
| `I(s)` vs `S_max` | Surprisal ceiling at 5.0 bits: breaks for vocabularies > 32 symbols |
| `conf` dual update | Incremental (η_eff) vs fracture-reset (support_count / (support_count+contradiction_count)) produce inconsistent values |
| Symbol `E` overloaded | Cognitive energy (metrics.py) and total exception mass (concept_birth.py) |
| Symbol `S` overloaded | Spatial surprise (metrics.py) and Shannon surprisal I(s) (inconsistent usage) |
| Symbol `stb`/`ST` overloaded | Stability (cognitive_core.py) and tightness (latent_cause_engine.py) |
| `ε` overloaded | Prediction error and epsilon floor `ε_floor` |

### 9.3 Circular Dependencies

| Loop | Path |
|------|------|
| **Attention Feedback** | `w_d` → cluster formation → latent cause → `w_d` |
| **Concept Birth / Probation** | exceptions → `H_before/H_within` → `G` → birth → probation → exception reclassification |
| **Free Energy / Merge** | `H,S,A` → `E` → `ΔE` → merge → cluster → `H,S,A` |
| **Adaptive Threshold** | `S` → `θ_adapt` → anomaly flag → cluster → `S` |
| **Cluster Formation** | `μ_k` → cluster assignment → `μ_k` |
| **Score / Cause Promotion** | `Score` → latent cause → attention → cluster → `Score` |

### 9.4 Parameter Provenance Summary

| Parameter Category | Count | Fully Derived | Hand-Tuned | Arbitrary |
|-------------------|-------|---------------|------------|-----------|
| Dirichlet `α` | 1 | — | x | — |
| EWMA `α` values | 3 | — | x | — |
| Energy weights `(λ,μ,ν)` | 3 | — | x | — |
| CPI weights | 4 | — | x | — |
| Score weights | 3 | — | x | — |
| Thresholds | 7+ | — | — | x |
| Learning rates | 2 | — | — | x |
| Misc constants | 8+ | — | — | x |
| **Total** | **~31+** | **0** | **9** | **22+** |

### 9.5 Experimentally Validated Variables

| Variable | Experiment | Method |
|----------|-----------|--------|
| `E` (cognitive energy) | E5, E6, E7, E13 | Live-fire simulation, sandbox replay |
| `CPI` | E10 | Live-fire simulation |
| `ΔE`, `ΔS`, `ΔH`, `ΔA` | E7, E13 | Sandbox simulation + Pareto test |
| `E_before`, `E_after` | E7, E13 | Sandbox simulation |
| `stb` | E5 | C6 stable belief experiment (indirect) |
| `φ` | E5 | C6 fracture mechanics experiment |
| `η_eff` | E5 | C6 Inertia Law experiment |

All other variables are **theoretically motivated but not experimentally validated** against ground truth.

---

## 10. Three-Level Dependency Map

### Foundation Level (hyperparameters, inputs)
```
α, η_base, H_m, τ_frac, conf_0, ε_floor,
θ_birth, T_obs, θ_prox, K_max, f_mult, sf,
b, S_max, α_acc, α_surp, α_dec,
λ, μ, ν, E_exhaust, H_high, S_high, P_high,
tol, α_w0, β_w0, w_asym0, λ_upd, q_src,
τ_interval, P_enter, P_exit, τ_cooldown
```

### Derived Level (computed from foundation + observations)
```
c, s, v, h, n(c,s), N(c), |support|,
support_count, contradiction_count, T, R, {e_i}, E,
n_k, T(i→j), μ_k, k, n_plus, n_minus, n_ev,
matches_on_quarantine, matches_on_baseline, |quarantine|, |baseline|
```

### Composite Level (computed from derived)
```
P(s|c), I(s), a(s), H(p), m_novel, supp_pred,
conf, stb, φ, ε, δ, η_eff,
θ_adapt, ρ, S, w_d, PG, CG, ST, Score, cov, FPR,
H_before, H_within, H_coarse, λ_model, H_after, G,
CR, C_res, dec, acc, μ_surp, A_t, D_t, CPI,
H, V_anom, A, E,
E_before, E_after, ΔS, ΔH, ΔA, ΔE,
μ_w, γ, w_asym,
regime, consolidation_state
```

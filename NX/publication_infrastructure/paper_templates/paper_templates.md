# Paper Templates — Program D

**Target Venues:** NeurIPS 2026, ICML 2026, ICLR 2027, Nature Machine Intelligence, Science Robotics
**Program:** D (E0, EXP-1, EXP-2, EXP-3)

---

## 1. Universal Paper Structure

### 1.1 Standard Sections (8-page main text)
1. **Title** (≤ 200 chars)
2. **Abstract** (≤ 250 words)
3. **Introduction** (1–1.5 pages)
4. **Related Work** (1 page)
5. **Methods** (1.5–2 pages)
6. **Experiments** (2–3 pages)
7. **Results & Discussion** (1.5–2 pages)
8. **Limitations & Future Work** (0.5 page)
9. **Conclusion** (0.25 page)
10. **Acknowledgments** (0.25 page)
11. **References** (unlimited)
12. **Appendix / Supplementary** (unlimited)

---

## 2. Main Paper Templates

### 2.1 E0 Paper: "Error-Gated Structure Acquisition: A Null-Referenced Test"

#### Title Options
- "Error-Gated Structure Acquisition: A Null-Referenced Test Against Designer Injection"
- "Distinguishing Emergent from Injected Structure via Error-Gated Capacity Growth"
- "When Does Predictive Error Produce Reusable Structure? A Falsifiable Test"

#### Abstract Template (250 words)
```
[Problem] The question of whether learned internal structure is emergent or
designer-injected is fundamental to cognitive science, developmental robotics,
and AI safety. Prior work on self-supervised learning, predictive coding, and
neural architecture search has produced structure, but cannot distinguish
emergence from injection.

[Approach] We introduce a null-referenced emergence statistic M(θₖ) that
compares the normalized mutual information between a learned latent partition
and a true latent generator against the same quantity under a shuffled-input
control. We test the central hypothesis (H*) that an agent whose only learning
signal is sensorimotor prediction error, and which adds representational
capacity only when prediction error persists, will acquire structure that is
(i) absent at initialization, (ii) improves prediction beyond fixed-capacity
and error-decoupled controls, and (iii) is not reducible to injected
statistics.

[Methods] We evaluate this in a synthetic environment with K known latent
states and nonlinear observation mixing, across 5 seeds and 4 conditions:
treatment (error-gated growth), control 1 (fixed capacity), control 2
(capacity-matched random growth), and control 3 (shuffled input). We use
pre-registered kill criteria, 5+ seeds, Bayesian analysis, and effect sizes
with 95% confidence intervals.

[Results] [TBD based on actual results]

[Conclusion] [TBD based on actual results]
```

#### Introduction Outline
1. **Problem (1 para):** Emergent vs. injected structure is fundamental but hard to test
2. **Gap (1 para):** Prior work on SSL, predictive coding, NAS can't distinguish
3. **Contribution (1 para):** H*, null-referenced M(θₖ), 4 conditions, 5 seeds
4. **Significance (1 para):** Implications for AGI safety, developmental robotics, cognitive science
5. **Pre-registration (1 para):** All hypotheses and analyses pre-registered on OSF

#### Related Work Outline (Program D `foundation/novelty/novelty_analysis.md`)
1. Self-supervised learning (SSL)
2. Minimum description length (MDL) and growth
3. Predictive coding / free energy
4. Developmental robotics
5. Continual / lifelong learning
6. Meta-learning
7. Neural architecture search (NAS)
8. Neural-symbolic integration
9. Emergence measurement
10. **Gap:** No prior work combines all five: error-gated growth + null-referenced emergence + pre-registered kill criteria + appropriate controls

#### Methods Outline
1. **Mathematical Foundation (5 primitives):**
   - Observation stream `x₁...xₜ`
   - Growable predictor class `{P_θ}`
   - Log-loss `L = -log P_θ(x_{t+1}|x_{≤t})`
   - MDL growth operator: `G = H_before - H_after - λ_model > 0`
   - Emergence statistic `M(θₖ) = NMI(learned, true) - E[NMI(learned, C3)]`
2. **Environment:** K latent states, nonlinear observation mixing (verified offline)
3. **Conditions:** T, C1, C2, C3 (full definitions)
4. **Implementation:** Dirichlet-Markov conjugate predictor
5. **Statistical Analysis:** Pre-registered plan (ANOVA, contrasts, effect sizes, Bayesian)

#### Experiments Outline
1. **E0 Protocol:** Seeds, training/held-out split, hyperparameters
2. **Pre-registration:** OSF link, kill criteria
3. **Compute:** GPU type, runtime

#### Results Outline
1. **Primary (DV-a):** Held-out LL table, plot
2. **Primary (DV-b):** M(θₖ) plot, margin test
3. **Kill Criteria Evaluation:** K1, K2, K3 pass/fail
4. **Sensitivity:** λ_model, K, mixing function
5. **Negative Results:** [If any]

#### Discussion Outline
1. **Interpretation:** [TBD]
2. **Limitations:** Synthetic data, one environment, etc.
3. **Future Work:** Real-world transfer, multi-agent, hierarchical growth
4. **Broader Impacts:** AGI safety, calibration, cognitive science

---

### 2.2 EXP-1 Paper: "Calibration of Uncertainty Tiers"

#### Title Options
- "Calibration of Uncertainty Tiers in Retrieval-Augmented Systems"
- "Honest Uncertainty: Reliability-Diagram Test of Tiered Confidence"

#### Abstract Template
```
Retrieval-augmented systems increasingly claim to provide "honest" or
"calibrated" uncertainty, but the claim is rarely tested. We evaluate
whether a retrieval agent's claimed uncertainty tiers (CERTAIN, PROBABLE,
DEBATED, UNKNOWN) match their empirical correctness on 200+ mixed queries
including known facts, ambiguous questions, and hallucination traps. We
measure Expected Calibration Error (ECE) with 95% bootstrap confidence
intervals and compare to a constant-confidence baseline. [Results] We find
[ECE = X.XXX, p = X.XXX]. These results [support/falsify] the calibration
hypothesis (H1) and [implications for AI safety/retrieval systems].
```

---

### 2.3 EXP-2 Paper: "Affective Indexing as Retrieval Key"

#### Title Options
- "Affective Indexing: Emotion as Retrieval Key for Problem-Solving Schemas"
- "Does Emotional Framing Improve Problem-Solving? A Pre-Registered Test"

#### Abstract Template
```
Can emotional framing serve as an effective retrieval key for problem-
solving schemas? We test the hypothesis (H2) that prompts with affective
state mappings (e.g., "shame → debugging → Schema X") outperform neutral
prompts on objective task scores across 30+ debugging, planning, and
reasoning tasks with 5 seeds. We use pre-registered kill criteria, paired
t-tests with effect sizes, and Bayesian analysis. [Results] [TBD] These
results [support/falsify] H2 and have implications for affective computing
and HCI.
```

---

### 2.4 EXP-3 Paper: "Emergent Development in a Minimal Predictive Organism"

#### Title Options
- "Emergent Development via Error-Gated Capacity Growth"
- "Can a Minimal Predictive Organism Develop Reusable Structure?"

---

## 3. Per-Venue Adjustments

### 3.1 NeurIPS 2026
- **Page limit:** 8 pages main + unlimited references + supplementary
- **Format:** NeurIPS LaTeX template
- **Review:** NeurIPS Reviewer Checklist (see `reviewer_checklists/neurips_reviewer_checklist.md`)
- **Required:** NeurIPS Reproducibility Checklist
- **Optional:** Artifact Evaluation submission

### 3.2 ICML 2026
- **Page limit:** 8 pages main + unlimited references + supplementary
- **Format:** ICML LaTeX template
- **Review:** ICML/ICLR Reviewer Checklist (see `reviewer_checklists/icml_iclr_reviewer_checklist.md`)
- **Required:** ICML Reproducibility Checklist v2.1
- **Optional:** Artifact Evaluation submission

### 3.3 ICLR 2027
- **Page limit:** 9 pages main + unlimited references + supplementary
- **Format:** ICLR LaTeX template
- **Review:** ICML/ICLR Reviewer Checklist
- **Required:** ICLR Reproducibility Checklist
- **Optional:** Open Review (public)

### 3.4 Nature Machine Intelligence
- **Page limit:** ~6–8 pages main + unlimited supplementary
- **Format:** Nature LaTeX template
- **Review:** Nature MI Reviewer Checklist
- **Required:** Reporting Summary, MDAR checklist
- **Required:** Code/data availability statements with DOIs at submission

### 3.5 Science Robotics
- **Page limit:** ~6 pages main + unlimited supplementary
- **Format:** Science Robotics LaTeX template
- **Review:** NSF + Science Robotics standards
- **Required:** Materials & Methods, Data availability
- **Required:** Code with DOI

---

## 4. Abstract Checklist (Universal)

| Requirement | Status |
|-------------|--------|
| Problem stated (1 sentence) | [ ] |
| Gap identified (1 sentence) | [ ] |
| Approach described (2–3 sentences) | [ ] |
| Pre-registration noted (1 sentence) | [ ] |
| Methods summarized (1–2 sentences) | [ ] |
| Results reported (1–2 sentences) | [ ] |
| Conclusion stated (1 sentence) | [ ] |
| Word count ≤ 250 (NeurIPS/ICML) | [ ] |
| No anthropomorphic language | [ ] |
| No novelty inflation | [ ] |
| No unsupported neuroscience | [ ] |

---

## 5. Title Checklist

| Requirement | Status |
|-------------|--------|
| Describes the scientific claim | [ ] |
| Avoids anthropomorphic terms | [ ] |
| Avoids hype ("AGI", "human-level", "revolutionary") | [ ] |
| Specific (not vague) | [ ] |
| ≤ 200 characters | [ ] |
| No colons (some venues) | [ ] |
| Citable (distinguishable) | [ ] |

**Good Examples:**
- "Error-Gated Structure Acquisition: A Null-Referenced Test"
- "Calibration of Uncertainty Tiers in Retrieval Systems"

**Bad Examples:**
- "Mind-Like Emergence in AI Systems" (anthropomorphic, hype)
- "A Revolutionary Approach to AGI" (hype, vague)
- "Things We Discovered" (vague)

---

## 6. Introduction Checklist

| Element | Status |
|---------|--------|
| **Hook** — Compelling opening (1 sentence) | [ ] |
| **Problem** — What's the question? (1 paragraph) | [ ] |
| **Gap** — What prior work missed (1 paragraph) | [ ] |
| **Contribution** — What we do (1 paragraph, bulleted) | [ ] |
| **Significance** — Why it matters (1 paragraph) | [ ] |
| **Pre-registration** — Methods pre-registered (1 sentence) | [ ] |
| **Outline** — Paper structure (1–2 sentences) | [ ] |
| No anthropomorphic language | [ ] |
| No novelty inflation | [ ] |

---

## 7. Limitations Section (Mandatory, Nature MI / Science)

Standard limitations to address:
- [ ] Synthetic data (E0): may not generalize to real-world
- [ ] Single environment family: robustness across environments untested
- [ ] Compute resources: limited hyperparameter search
- [ ] Effect size: magnitude may vary with task difficulty
- [ ] Seeds: 5 seeds is minimum; more would tighten CIs
- [ ] External validity: not yet tested on real retrieval/RAG systems
- [ ] Construct validity: ECE, M(θₖ) are proxies for true concepts
- [ ] Statistical power: may be underpowered for small effects

---

## 8. Broader Impacts Statement (Mandatory, NeurIPS / ICML)

Standard categories:
- [ ] **Positive impacts:** AI safety via calibration, cognitive science insights, open science artifacts
- [ ] **Negative impacts:** None identified (no dual-use, no PII, no human subjects)
- [ ] **Mitigations:** Pre-registration, kill criteria, null-referenced statistics
- [ ] **Future risks:** As systems scale, emergence claims need continued scrutiny

---

## 9. Acknowledgments Template

```
We thank [Funding Source 1] for support under grant [XXX]. We thank
[Collaborators] for discussions. We thank [Reviewers] for feedback.
Experiments used [Compute Resource] under allocation [XXX].
```

---

## 10. Paper Writing Anti-Patterns (Avoid)

### 10.1 Anthropomorphic Language (Constitution §2.4)
**Avoid:** "mind", "soul", "understanding", "belief", "intention", "awareness", "consciousness", "thinks", "knows", "feels"

**Use instead:** "predictive organism", "structure acquisition", "model", "predicts", "estimates", "indexes"

### 10.2 Novelty Inflation (Constitution §2.6)
**Avoid:** "novel", "new", "first to" without precise novelty statement

**Use instead:** "First to [specific claim] under [specific conditions] with [specific measurement]"

### 10.3 Unsupported Neuroscience (Constitution §2.7)
**Avoid:** Invoking LTP, STDP, hippocampal replay, etc. when only scalar decay is implemented

**Use instead:** "Scalar decay of edge weights" or implement the actual mechanism

### 10.4 Hype
**Avoid:** "AGI", "human-level", "revolutionary", "breakthrough", "magic"

**Use instead:** Specific, measurable claims

### 10.5 Vague Claims
**Avoid:** "significantly improves performance"

**Use instead:** "p = 0.003, Cohen's d = 0.87 [95% CI: 0.42, 1.32]"

---

## 11. Writing Workflow

1. **Draft foundation first:** Title → Abstract → Introduction → Methods
2. **Run experiments:** Per pre-registered protocol
3. **Fill in Results:** After analysis
4. **Update Abstract:** To match actual results
5. **Write Discussion:** Honest interpretation, limitations
6. **Internal review:** Program D Constitution compliance check
7. **External review:** Colleagues, pre-print
8. **Submit:** With reproducibility package, preregistration, data DOIs

---

**Template Version:** 1.0
**Last Updated:** 2026-07-03
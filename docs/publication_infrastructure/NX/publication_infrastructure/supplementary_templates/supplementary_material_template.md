# Supplementary Material Templates — Program D Papers

**Standard:** NeurIPS / ICML / ICLR / Nature MI / Science Robotics Appendix
**Program:** D (E0, EXP-1, EXP-2, EXP-3)

---

## 1. Universal Supplementary Structure

### 1.1 Required Sections (All Papers)
```
Supplementary Material
├── A. Extended Methods
│   ├── A.1 Mathematical Derivations
│   ├── A.2 Algorithm Pseudocode
│   ├── A.3 Experimental Protocols (full)
│   ├── A.4 Hyperparameters & Compute
│   └── A.5 Preregistration Deviations
├── B. Extended Results
│   ├── B.1 Full Statistical Tables
│   ├── B.2 Per-Seed Data
│   ├── B.3 Learning Curves / Trajectories
│   ├── B.4 Assumption Checks
│   ├── B.5 Sensitivity / Ablation Analyses
│   └── B.6 Negative / Null Results
├── C. Reproducibility
│   ├── C.1 Code & Data Availability
│   ├── C.2 Compute Requirements
│   ├── C.3 Random Seeds & Determinism
│   └── C.4 Artifact Manifest
├── D. Additional Figures & Tables
├── E. Kill Criteria Evaluation Reports
├── F. Assumption Coverage Matrix
├── G. Novelty Analysis Details
└── H. Terminology & Notation Reference
```

### 1.2 Page Limits
| Venue | Main Paper | Supplementary |
|-------|------------|---------------|
| NeurIPS | 8 pages | Unlimited |
| ICML | 8 pages | Unlimited |
| ICLR | 9 pages | Unlimited |
| Nature MI | ~6–8 pages | Unlimited (online only) |
| Science Robotics | ~6 pages | Unlimited |

---

## 2. Experiment-Specific Supplementary Templates

### 2.1 E0 Supplementary (H*: Error-Gated Structure Acquisition)

#### Section A: Extended Methods
**A.1 Mathematical Derivations**
- Full derivation of MDL growth operator: `G = H_before - H_after - λ_model`
- Dirichlet-Markov conjugate predictor: prior, likelihood, posterior predictive
- Emergence statistic: `M(θₖ) = NMI(learned, true) - E[NMI(learned, C3)]`
- Null distribution derivation for shuffled-input control
- Proper scoring rule justification (log-loss)

**A.2 Algorithm Pseudocode**
```
Algorithm 1: Error-Gated Growth (E0 Treatment)
Input: Stream x₁...xₜ, predictor P_θ, λ_model
for t = 1 to T:
    L_t = -log P_θ(x_t | x_<t)
    Update θ via gradient on L_t
    Compute H_before = description_length(P_θ)
    Propose growth → θ'
    Compute H_after = description_length(P_θ')
    G = H_before - H_after - λ_model
    if G > 0: θ ← θ'
Return P_θ
```

**A.3 Experimental Protocol (Full)**
- Synthetic environment specification: K latent states, transition matrix, observation mixing function
- Nonlinearity verification: Linear probe fails to recover latent (accuracy < chance + ε)
- Training/held-out split: 80/20 temporal split
- Seed range: 42, 123, 456, 789, 999 (pre-registered)
- Compute: GPU type, hours per seed

**A.4 Hyperparameters**
| Parameter | Value | Selection Method |
|-----------|-------|------------------|
| λ_model | X.XX | Pre-registered / Pilot |
| Learning rate | X.XX | Fixed across conditions |
| Predictor architecture | Dirichlet-Markov (K categories) | Fixed |
| Max capacity | N parameters | Fixed across T, C1, C2 |
| C2 growth schedule | Random times, matched to T growth count | Pre-registered |
| C3 shuffle | Block shuffle (block=100) preserving marginals | Pre-registered |

**A.5 Preregistration Deviations**
| Deviation | Reason | Impact Assessment |
|-----------|--------|-------------------|
| None / List each | — | — |

#### Section B: Extended Results
**B.1 Full Statistical Tables** — See `statistical_reporting_template.md` Tables S1–S4

**B.2 Per-Seed Data** — Full table with all seeds, all conditions, both DVs

**B.3 Learning Curves**
- Held-out LL vs training steps (all seeds, all conditions, mean ± 95% CI)
- Capacity growth events over time (T only)
- MDL gain G over time (T only)

**B.4 Assumption Checks** — Full Shapiro-Wilk, Levene, Q-Q plots, residuals

**B.5 Sensitivity Analyses**
- λ_model sweep: {0.1, 0.5, 1.0, 2.0, 5.0}
- K (latent states): {3, 5, 7, 10}
- Observation mixing: {tanh, ReLU, 2-layer MLP}
- Block size for C3 shuffle: {10, 50, 100, 500}
- Alternative emergence statistics: ARI, VI, clustering accuracy

**B.6 Negative/Null Results**
- Any condition where kill criterion failed
- Any ablation where component removal didn't change result
- Any hyperparameter where effect disappeared

#### Section E: Kill Criteria Evaluation Report (E0)
| Kill Criterion | Threshold | Observed | Pass/Fail | Evidence |
|----------------|-----------|----------|-----------|----------|
| K1: T > C1 on DV-a | p < 0.01 | p = X.XXX | PASS/FAIL | Fig 2, Table 1 |
| K2: T > C2 on DV-a | p < 0.01 | p = X.XXX | PASS/FAIL | Fig 2, Table 1 |
| K3: DV-b > Margin | M_T - M_C3 > Δ | Δ_obs = X.XX | PASS/FAIL | Fig 3, Table 1 |
| K4: Environment not too easy | C1 LL < ceiling - ε | LL_C1 = X.XX | PASS/FAIL | Table S1 |
| K5: Growth not uncoupled | T growth events > 0 | N_growth = N | PASS/FAIL | Fig S2 |
| K6: Emergence stat no DoF | Pre-registered margin | Δ = X.XX | PASS/FAIL | Preregistration |
| K7: Observability gap | All metrics measurable | Y/N | PASS/FAIL | Code review |

**Overall H* Verdict:** PASS / FAIL

---

### 2.2 EXP-1 Supplementary (H1: Calibration)

#### Section A: Extended Methods
**A.1 Query Set Construction**
- 200+ queries: breakdown by type (facts, ambiguous, hallucination traps)
- Source: ArXiv, Wikipedia, synthetic traps
- Ground truth determination process
- Tier assignment protocol (CERTAIN/PROBABLE/DEBATED/UNKNOWN)

**A.2 Calibration Metrics**
- ECE formula (10-bin, 15-bin, adaptive binning)
- MCE (Maximum Calibration Error)
- Brier score decomposition
- Reliability diagram construction

**A.3 Baseline**
- Constant confidence baseline: uniform confidence = empirical accuracy
- Temperature scaling baseline (if applicable)

#### Section B: Extended Results
**B.1 Full Reliability Data** — Per-bin accuracy, confidence, count
**B.2 Tier-Level Breakdown** — Per-tier calibration with binomial CI
**B.3 Per-Query-Type Calibration** — Separate ECE for facts/ambiguous/traps
**B.4 Convergence** — ECE vs number of queries
**B.5 Failure Cases** — Examples where CERTAIN was wrong, UNKNOWN was correct

#### Section E: Kill Criteria Evaluation (EXP-1)
| Kill Criterion | Threshold | Observed | Pass/Fail |
|----------------|-----------|----------|-----------|
| K1: ECE < 0.1 | ECE < 0.1 | X.XXX | PASS/FAIL |
| K2: Better than constant | ΔECE < 0 | X.XXX | PASS/FAIL |
| K3: No CERTAIN hallucinations | 0 CERTAIN on traps | N | PASS/FAIL |

---

### 2.3 EXP-2 Supplementary (H2: Affective Indexing)

#### Section A: Extended Methods
**A.1 Task Suite**
- Task descriptions (debugging, planning, etc.)
- Objective scoring rubric per task
- Affective frame definitions (shame→debugging, curiosity→exploration, etc.)
- Neutral baseline prompts

**A.2 Experimental Design**
- Within-subjects vs between-subjects
- Counterbalancing order
- Number of tasks × seeds

#### Section B: Extended Results
**B.1 Per-Task Results** — Full table with statistics
**B.2 Per-Affective-Frame Results** — Which frames work/don't work
**B.3 Schema Retrieval Analysis** — Which schemas retrieved, overlap
**B.4 Subjective vs Objective** — If subjective ratings collected, compare

#### Section E: Kill Criteria Evaluation (EXP-2)
| Kill Criterion | Threshold | Observed | Pass/Fail |
|----------------|-----------|----------|-----------|
| K1: Significant improvement | p < 0.05 | p = X.XXX | PASS/FAIL |
| K2: Meaningful effect size | d > 0.2 | d = X.XX | PASS/FAIL |
| K3: No re-authoring per task | Schemas fixed | Y/N | PASS/FAIL |

---

### 2.4 EXP-3 Supplementary (H3: Emergent Development)

#### Section A: Extended Methods
**A.1 Environment Specification**
- Task A (training) and Task B (transfer) specifications
- Shared latent structure between tasks
- Minimal organism architecture

**A.2 Transfer Metric**
- Held-out LL on Task B after Task A training
- Random initialization control protocol

#### Section B: Extended Results
**B.1 Transfer Learning Curves**
**B.2 Emergent Structure Visualization** — Latent space plots
**B.3 Ablation: Which Components Transfer**

#### Section E: Kill Criteria Evaluation (EXP-3)
| Kill Criterion | Threshold | Observed | Pass/Fail |
|----------------|-----------|----------|-----------|
| K1: Transfer > random init | p < 0.05, d > 0.3 | p=X.XXX, d=X.XX | PASS/FAIL |
| K2: Structure not trivial | > initialization + input stats | Y/N | PASS/FAIL |

---

## 3. Universal Supplementary Sections

### Section C: Reproducibility (All Experiments)

#### C.1 Code & Data Availability
| Artifact | Location | DOI | Commit Hash |
|----------|----------|-----|-------------|
| Experiment code | GitHub.com/velynx/program_d | 10.5281/zenodo.XXXXX | `git rev-parse HEAD` |
| Synthetic data generator | `experiments/E0/dataset.py` | — | — |
| Query set (EXP-1) | `experiments/EXP1/queries.json` | 10.5281/zenodo.XXXXX | — |
| Task suite (EXP-2) | `experiments/EXP2/tasks/` | 10.5281/zenodo.XXXXX | — |
| Environment (EXP-3) | `experiments/EXP3/env.py` | — | — |
| Analysis scripts | `experiments/*/analysis.py` | — | — |
| Core primitives | `core/` | — | — |

#### C.2 Compute Requirements
| Experiment | GPU | VRAM | CPU | RAM | Time/Seed | Total Seeds | Total GPU-h |
|------------|-----|------|-----|-----|-----------|-------------|-------------|
| E0 | RTX 3090 | 8 GB | 8 core | 32 GB | X h | 5 | X h |
| EXP-1 | CPU only | — | 4 core | 16 GB | X min | 1 | X min |
| EXP-2 | CPU only | — | 4 core | 16 GB | X min | 5 | X min |
| EXP-3 | RTX 3090 | 8 GB | 8 core | 32 GB | X h | 5 | X h |

#### C.3 Random Seeds & Determinism
- All seeds: `[42, 123, 456, 789, 999]` (pre-registered)
- CUDA deterministic: `torch.use_deterministic_algorithms(True)`
- Python hash seed: `PYTHONHASHSEED=0`
- NumPy, random, torch seeds set per experiment

#### C.4 Artifact Manifest (JSON)
```json
{
  "experiment": "E0",
  "commit": "abc123...",
  "figures": [
    {"file": "fig1_design.pdf", "script": "analysis.py", "data": "fig1_data.csv"},
    {"file": "fig2_ll.pdf", "script": "analysis.py", "data": "fig2_data.csv"}
  ],
  "tables": [
    {"file": "table1_main.tex", "script": "analysis.py", "data": "table1_data.csv"}
  ],
  "stats": "stats_E0.json",
  "seeds": [42, 123, 456, 789, 999]
}
```

---

### Section F: Assumption Coverage Matrix (All Papers)

| Assumption | Description | Experiments Testing | Status |
|------------|-------------|---------------------|--------|
| I1 | Sensorimotor stream is stationary/ergodic | E0, EXP-3 | Tested/Assumed |
| I2 | Proper scoring loss captures predictive adequacy | E0, EXP-1, EXP-3 | Tested |
| I3 | MDL penalty λ_model correctly trades off fit vs complexity | E0 | Tested (sensitivity) |
| I4 | Shuffled input destroys temporal structure only | E0 | Verified offline |
| I5 | Affective frames map to distinct schemas | EXP-2 | Tested |
| I6 | Objective task score measures schema quality | EXP-2 | Assumed/Validated |

*Source: `foundation/assumptions/assumption_coverage_matrix.csv`*

---

### Section G: Novelty Analysis Details (All Papers)

**Reference Fields Surveyed (11):**
1. Self-Supervised Learning (SSL)
2. Minimum Description Length (MDL)
3. Predictive Coding / Free Energy Principle
4. Developmental Robotics
5. Continual / Lifelong Learning
6. Meta-Learning
7. Neural Architecture Search (NAS)
8. Neural-Symbolic Integration
9. Calibration / Uncertainty Quantification
10. Affective Computing
11. Emergence Measurement

**For each field:** Prior work, gap, Program D contribution, citation.

*Source: `foundation/novelty/novelty_analysis.md`*

---

### Section H: Terminology & Notation Reference

| Symbol | Definition | Source |
|--------|------------|--------|
| `x₁...xₜ` | Observation stream | `TERMINOLOGY.md` |
| `P_θ` | Growable predictor class | `TERMINOLOGY.md` |
| `L` | Log-loss (proper scoring) | `TERMINOLOGY.md` |
| `g` | Capacity growth operator | `TERMINOLOGY.md` |
| `G` | MDL trigger threshold | `TERMINOLOGY.md` |
| `M(θₖ)` | Emergence statistic | `TERMINOLOGY.md` |
| `ECE` | Expected Calibration Error | `TERMINOLOGY.md` |
| `CERTAIN/PROBABLE/DEBATED/UNKNOWN` | Uncertainty tiers | `TERMINOLOGY.md` |
| `Affective Indexing` | Emotion→schema retrieval | `TERMINOLOGY.md` |

---

## 4. Supplementary Generation Checklist

Per experiment, verify:
- [ ] All main paper figures/tables have supplementary counterparts with full data
- [ ] All statistical tests reported with full output (not just p-values)
- [ ] All assumption checks included
- [ ] All sensitivity/ablation analyses included
- [ ] All negative/null results reported
- [ ] Kill criteria evaluation table complete
- [ ] Preregistration deviations documented
- [ ] Code/data DOIs resolve
- [ ] Artifact manifest validates
- [ ] Supplementary PDF compiles without errors

---

**Template Version:** 1.0
**Last Updated:** 2026-07-03
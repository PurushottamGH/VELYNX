# ICML / ICLR Reviewer Checklist — Program D Compliance

**Paper Target:** ICML 2026 / ICLR 2027
**Program:** D (Error-Gated Structure Acquisition / Calibration / Affective Indexing)
**Status:** Pre-submission Audit

---

## 1. Reproducibility Checklist (ICML 2026 / ICLR 2027 Standards)

### 1.1 Code & Data (ICML Reproducibility Checklist v2.1)
- [ ] **Code included** — Submitted as supplementary material or public repository
- [ ] **README with reproduction instructions** — Step-by-step for all experiments
- [ ] **Dependencies documented** — `requirements.txt` / `pyproject.toml` with exact versions
- [ ] **Compute requirements** — Hardware, runtime, memory per experiment
- [ ] **Pre-trained models** — If any, included or downloadable with checksums
- [ ] **Random seeds** — All seeds fixed and reported; multiple seeds (≥5) for stochastic experiments

### 1.2 ICML-Specific: Artifact Evaluation
- [ ] **Artifact appendix** — Separate document describing code/data artifacts
- [ ] **Badges** — "Artifacts Available", "Artifacts Evaluated - Functional", "Results Reproduced"

---

## 2. Statistical Rigor (ICML/ICLR 2026 Standards)

### 2.1 Experimental Design
- [ ] **Pre-registration** — Hypotheses and analysis plan registered before experiments (OSF)
- [ ] **Power analysis** — Sample size justified; minimum detectable effect reported
- [ ] **Multiple runs** — ≥5 seeds for all stochastic experiments (ICML standard)
- [ ] **Confidence intervals** — 95% CI on all reported metrics (not just mean ± std)
- [ ] **Statistical tests named** — Exact test (t-test, Wilcoxon, permutation, bootstrap) with parameters
- [ ] **Multiple comparison correction** — Bonferroni / Holm / Benjamini-Hochberg reported

### 2.2 Reporting Standards
- [ ] **Effect sizes** — Cohen's d, Cliff's delta, or odds ratio with CI
- [ ] **Variance decomposition** — Within-seed vs. between-seed variance reported
- [ ] **Learning curves** — Full trajectories, not just final numbers
- [ ] **Ablation studies** — Each component tested in isolation with statistics
- [ ] **Negative results reported** — Failed ablations / kill criteria triggered reported prominently

---

## 3. Methodological Soundness (Program D Constitution)

### 3.1 Hypothesis Falsifiability (Constitution §2, §4)
- [ ] **H* (Error-Gated Structure Acquisition)** — Falsifiable with pre-registered kill criteria
- [ ] **H1 (Calibration)** — ECE < 0.1 kill criterion pre-registered
- [ ] **H2 (Affective Indexing)** — Objective task score improvement kill criterion pre-registered
- [ ] **H3 (Emergent Development)** — Transfer to held-out task kill criterion pre-registered

### 3.2 Controls (Constitution §4)
- [ ] **C1: Fixed-capacity** — Same architecture, no growth operator
- [ ] **C2: Error-decoupled growth** — Capacity-matched random growth timing
- [ ] **C3: Shuffled-input** — Temporal structure destroyed, marginals preserved
- [ ] **Standard baselines** — Relevant SOTA from SSL, MDL, predictive coding, continual learning

### 3.3 No Designer Injection (Constitution §2.5)
- [ ] **Zero seeded concepts in E0** — Only error-gated growth
- [ ] **Emergence statistic null-referenced** — M(θₖ) - E[M|H₀] via C3
- [ ] **MDL trigger only growth signal** — G = H_before - H_after - λ_model > 0

### 3.4 No Anthropomorphic Language (Constitution §2.4)
- [ ] **Terminology audit** — All terms from `TERMINOLOGY.md` used; rejected terms absent

---

## 4. Novelty & Related Work (ICML/ICLR Standards)

### 4.1 Novelty Claims (Program D `foundation/novelty/`)
- [ ] **Precise novelty statements** — "First to X under Y with measurement Z"
- [ ] **11 reference fields covered** — SSL, MDL, predictive coding, developmental robotics, continual learning, meta-learning, NAS, neural-symbolic, calibration, affective computing, emergence measurement
- [ ] **Negative results cited** — Prior work with similar claims that failed
- [ ] **No novelty inflation** — Standard SSL/MDL methods not claimed as novel

### 4.2 Baselines
- [ ] **Strong baselines** — Not straw men; best available implementations
- [ ] **Compute-matched baselines** — Same FLOPs/parameters where applicable
- [ ] **Ablation depth** — Each primitive tested in isolation (log-loss, MDL trigger, Dirichlet-Markov, emergence statistic, controls)

---

## 5. Ethics & Reproducibility (ICML/ICLR)

### 5.1 Ethics
- [ ] **No human subjects** — Synthetic data (E0); anonymized queries (EXP-1)
- [ ] **No dual-use** — Predictive organism on synthetic streams
- [ ] **Carbon footprint** — GPU-hours + CO2 estimate reported
- [ ] **Data licenses** — All sources licensed for research

### 5.2 Reproducibility Package
- [ ] **One-command reproduction** — `bash reproduce.sh` runs all experiments
- [ ] **Frozen code commit** — Exact hash in paper
- [ ] **Deterministic execution** — CUDA deterministic, seeds fixed
- [ ] **Pre-registration links** — OSF URLs for E0, EXP-1, EXP-2, EXP-3

---

## 6. ICML/ICLR-Specific Requirements

### 6.1 Paper Format
- [ ] **Page limit** — 8 pages main text (ICML) / 9 pages (ICLR) + unlimited references + appendix
- [ ] **Anonymous** — No identifying information
- [ ] **Supplementary material** — Appendix submitted with paper
- [ ] **Checklist** — ICML/ICLR reproducibility checklist completed

### 6.2 Review Criteria Alignment
| ICML/ICLR Criterion | Program D Mapping | Status |
|---------------------|-------------------|--------|
| **Significance** | H* addresses emergence vs injection — fundamental question | [ ] |
| **Originality** | Error-gated MDL growth + null-referenced emergence statistic | [ ] |
| **Soundness** | Constitution enforces falsifiability, kill criteria, no injection | [ ] |
| **Clarity** | 5 primitives, strict terminology, pre-registered protocols | [ ] |
| **Reproducibility** | Core primitives extracted, frozen code, pre-registration | [ ] |
| **Substance** | E0 discriminates emergence vs injection; not a toy demo | [ ] |

---

## 7. Program D Publication Blockers (ICML/ICLR)

### 7.1 Must-Resolve
- [ ] **E0 preregistration live** — OSF URL in paper
- [ ] **E0 kill criteria evaluated** — Pass/fail in `kill_criteria_validation_report.md`
- [ ] **Emergence statistic M(θₖ) implemented** — `core/emergence/emergence_statistic.py` with null reference
- [ ] **C3 shuffled control implemented** — `core/controls/shuffled_input.py`
- [ ] **EXP-1 ECE measured** — ≥200 mixed queries, ECE < 0.1 or negative result
- [ ] **EXP-2 objective task score** — Not subjective rating
- [ ] **No circular logic** — Hypotheses fixed pre-registration
- [ ] **Assumption ledger complete** — I1, I2, I3 with coverage matrix
- [ ] **All foundation documents exist** — 22 files in `foundation/` per `repository_v2.md`

### 7.2 Documentation Artifacts
- [ ] `foundation/hypothesis/central_hypothesis.md`
- [ ] `foundation/hypothesis/H1_calibration.md`
- [ ] `foundation/hypothesis/H2_affective_indexing.md`
- [ ] `foundation/hypothesis/H3_emergent_development.md`
- [ ] `foundation/assumptions/assumption_ledger.md`
- [ ] `foundation/assumptions/assumption_coverage_matrix.csv`
- [ ] `foundation/kill_criteria/kill_criteria.md`
- [ ] `foundation/kill_criteria/kill_criteria_validation_report.md`
- [ ] `foundation/mathematics/mathematical_foundation.md`
- [ ] `foundation/mathematics/variable_provenance.md`
- [ ] `foundation/mathematics/variable_dependency_graph.graphml`
- [ ] `foundation/mathematics/variable_dependency_matrix.csv`
- [ ] `foundation/architecture/architecture.md`
- [ ] `foundation/architecture/dependency_graph.graphml`
- [ ] `foundation/architecture/dependency_matrix.csv`
- [ ] `foundation/architecture/layer_diagram.mmd`
- [ ] `foundation/novelty/novelty_analysis.md`
- [ ] `foundation/novelty/publication_test.md`

---

## 8. Acceptance Probability Assessment

| Criterion | Weight | Score (1-5) | Weighted |
|-----------|--------|-------------|----------|
| Significance | 0.25 | ___ | ___ |
| Originality | 0.20 | ___ | ___ |
| Soundness | 0.25 | ___ | ___ |
| Clarity | 0.10 | ___ | ___ |
| Reproducibility | 0.10 | ___ | ___ |
| Substance | 0.10 | ___ | ___ |
| **Total** | **1.00** | | **___** |

**Interpretation:**
- **≥ 4.0**: Strong accept
- **3.5–3.9**: Accept
- **3.0–3.4**: Weak accept / minor revisions
- **2.5–2.9**: Reject / major revisions
- **< 2.5**: Strong reject

**Blockers (automatic reject if any):**
- [ ] No pre-registration for primary hypothesis
- [ ] Kill criteria not evaluated
- [ ] Designer injection detected
- [ ] Anthropomorphic language in main claims
- [ ] < 5 seeds for stochastic experiments
- [ ] No confidence intervals reported
- [ ] Baselines are straw men

---

**Auditor:** _________________________
**Date:** _________________________
**Next Review:** _________________________
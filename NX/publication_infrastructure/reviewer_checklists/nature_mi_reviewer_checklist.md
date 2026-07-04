# Nature Machine Intelligence Reviewer Checklist — Program D Compliance

**Paper Target:** Nature Machine Intelligence
**Program:** D (Error-Gated Structure Acquisition / Calibration / Affective Indexing)
**Status:** Pre-submission Audit

---

## 1. Nature Portfolio Standards

### 1.1 Reproducibility (Nature Portfolio Policy)
- [ ] **Code availability statement** — Public repository with DOI (Zenodo) at submission
- [ ] **Data availability statement** — All data accessible with persistent identifiers
- [ ] **Materials availability** — Any physical materials (none for Program D) documented
- [ ] **Reporting summary** — Nature Portfolio Reporting Summary completed
- [ ] **Life Sciences Reporting** — N/A (computational only)
- [ ] **MDAR checklist** — Minimum Data Analysis Reporting checklist completed

### 1.2 Statistical Rigor (Nature Standards)
- [ ] **Sample size justification** — Power analysis for all primary endpoints
- [ ] **Randomization** — Seeds randomized; conditions counterbalanced
- [ ] **Blinding** — Analysis blinded where possible
- [ ] **Outlier handling** — Pre-registered outlier criteria; none removed post-hoc
- [ ] **Replication** — ≥5 independent replicates (seeds) per condition
- [ ] **Effect sizes with CI** — 95% CI mandatory; p-values supplementary
- [ ] **Bayesian analysis** — Encouraged for primary hypotheses

### 1.3 Transparency
- [ ] **Pre-registration** — OSF preregistration for E0, EXP-1, EXP-2, EXP-3
- [ ] **Protocol deviations** — Any deviations from pre-registration documented and justified
- [ ] **Negative results** — All kill criteria evaluations reported (pass/fail)
- [ ] **Author contributions** — CRediT taxonomy used
- [ ] **Competing interests** — Declared

---

## 2. Program D Methodological Compliance (Nature Portfolio + Constitution)

### 2.1 Falsifiability (Constitution §2, §4)
- [ ] **H* pre-registered** — Central hypothesis with kill criteria on OSF
- [ ] **H1, H2, H3 pre-registered** — Sub-hypotheses with kill criteria on OSF
- [ ] **Kill criteria evaluated** — Each experiment reports pass/fail against pre-registered criteria
- [ ] **No HARKing** — Hypotheses not adjusted after seeing results

### 2.2 Controls (Constitution §4)
- [ ] **C1: Fixed-capacity** — Same architecture, no growth
- [ ] **C2: Error-decoupled growth** — Capacity-matched, random timing
- [ ] **C3: Shuffled-input** — Temporal structure destroyed, marginals preserved
- [ ] **Standard baselines** — SOTA from relevant fields

### 2.3 No Designer Injection (Constitution §2.5)
- [ ] **Zero seeded concepts in E0** — Only error-gated growth
- [ ] **Emergence statistic null-referenced** — M(θₖ) - E[M|H₀] via C3
- [ ] **MDL trigger only growth signal** — G = H_before - H_after - λ_model > 0

### 2.4 Terminology (Constitution §2.4 + TERMINOLOGY.md)
- [ ] **Zero anthropomorphic terms** — "mind", "soul", "understanding", "belief", "intention" absent
- [ ] **Operational definitions only** — "predictive organism", "structure acquisition", "affective indexing", "calibration"

---

## 3. Nature Machine Intelligence Specific Requirements

### 3.1 Scope Alignment
- [ ] **Machine intelligence focus** — Predictive organism, structure acquisition, calibration, affective indexing
- [ ] **Interdisciplinary relevance** — Connects ML, cognitive science, neuroscience (predictive coding), robotics (developmental)
- [ ] **Real-world implications** — Honest uncertainty (safety), affective indexing (HCI), emergence (AGI safety)

### 3.2 Technical Depth
- [ ] **Mathematical rigor** — 5 primitives formally defined in `foundation/mathematics/mathematical_foundation.md`
- [ ] **Algorithmic clarity** — Pseudocode for MDL growth operator, emergence statistic, Dirichlet-Markov predictor
- [ ] **Computational complexity** — Time/space complexity reported for all primitives

### 3.3 Benchmarking
- [ ] **Standard benchmarks** — Where applicable (calibration: ECE on standard sets; affective: objective tasks)
- [ ] **Synthetic benchmarks** — E0: nonlinear latent stream with known generator (ground truth for emergence)
- [ ] **Ablation depth** — Each primitive ablated with statistics

---

## 4. Ethics & Societal Impact (Nature Portfolio)

### 4.1 Ethics Statement
- [ ] **No human subjects** — Synthetic data (E0); anonymized queries (EXP-1)
- [ ] **No animal subjects** — N/A
- [ ] **Dual-use assessment** — Predictive organism on synthetic streams; no autonomous weapons, surveillance
- [ ] **Data governance** — All data sources licensed; no PII

### 4.2 Societal Impact
- [ ] **Honest uncertainty** — Program A: calibration for safety-critical deployment
- [ ] **No AGI hype** — Claims limited to "structure acquisition under error-gated growth"
- [ ] **Affective indexing scope** — Retrieval key for schemas; no emotion simulation or manipulation
- [ ] **Environmental impact** — GPU-hours + CO2e reported

---

## 5. Nature Machine Intelligence Publication Blockers

### 5.1 Must-Resolve Before Submission
- [ ] **E0 preregistration live on OSF** — DOI in paper
- [ ] **E0 kill criteria evaluated** — Documented in `kill_criteria_validation_report.md`
- [ ] **Emergence statistic M(θₖ) implemented** — `core/emergence/emergence_statistic.py` with null reference
- [ ] **C3 shuffled control implemented** — `core/controls/shuffled_input.py`
- [ ] **EXP-1 ECE < 0.1 on ≥200 queries** — Or negative result per kill criterion
- [ ] **EXP-2 objective task improvement** — Statistically significant with effect size
- [ ] **All foundation documents complete** — 22 files in `foundation/` per `repository_v2.md`
- [ ] **Nature Portfolio Reporting Summary** — Completed and included
- [ ] **MDAR checklist** — Completed
- [ ] **Code + data DOIs** — Zenodo deposits with DOIs at submission

### 5.2 Documentation Artifacts
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

## 6. Acceptance Probability Assessment (Nature MI)

| Criterion | Weight | Score (1-5) | Weighted |
|-----------|--------|-------------|----------|
| **Novelty & Significance** | 0.30 | ___ | ___ |
| **Methodological Rigor** | 0.25 | ___ | ___ |
| **Statistical Rigor** | 0.20 | ___ | ___ |
| **Reproducibility** | 0.15 | ___ | ___ |
| **Interdisciplinary Relevance** | 0.10 | ___ | ___ |
| **Total** | **1.00** | | **___** |

**Nature MI Thresholds:**
- **≥ 4.2**: Strong candidate
- **3.8–4.1**: Competitive
- **3.5–3.7**: Major revisions likely
- **< 3.5**: Reject

**Automatic Rejection Triggers:**
- [ ] No pre-registration for primary hypothesis
- [ ] Kill criteria not evaluated
- [ ] Designer injection detected
- [ ] Anthropomorphic language in claims
- [ ] No confidence intervals on primary results
- [ ] Code/data not available at submission
- [ ] Sample size < 5 per condition

---

**Auditor:** _________________________
**Date:** _________________________
**Next Review:** _________________________
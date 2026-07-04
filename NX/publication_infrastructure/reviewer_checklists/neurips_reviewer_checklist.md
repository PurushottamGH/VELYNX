# NeurIPS Reviewer Checklist — Program D Compliance

**Paper Target:** NeurIPS 2026
**Program:** D (Error-Gated Structure Acquisition / Calibration / Affective Indexing)
**Status:** Pre-submission Audit

---

## 1. Reproducibility Checklist (NeurIPS 2026 Requirements)

### 1.1 Code Availability
- [ ] **Code repository URL** — Public GitHub/GitLab with MIT/BSD/Apache-2.0 license
- [ ] **Exact commit hash** — Pinned in paper and supplementary material
- [ ] **Dependencies** — `requirements.txt` / `pyproject.toml` / `environment.yml` pinned to exact versions
- [ ] **Dockerfile** — Reproducible container with `docker build` + `docker run` instructions
- [ ] **Compute requirements** — GPU type, VRAM, CPU, RAM, estimated runtime per experiment

### 1.2 Data Availability
- [ ] **Synthetic data generators** — Code to regenerate E0 synthetic streams (nonlinear latent, K states)
- [ ] **Benchmark datasets** — URLs + checksums for any real-world datasets (EXP-1 queries, EXP-2 tasks)
- [ ] **Pre-trained weights** — If any, hosted with DOI (Zenodo) and checksums
- [ ] **Data licenses** — Verified compatible with NeurIPS data policy

### 1.3 Experiment Execution
- [ ] **One-command reproduction** — `bash reproduce.sh` runs all experiments end-to-end
- [ ] **Seed control** — All seeds fixed and logged (numpy, torch, random, CUDA deterministic)
- [ ] **Pre-registration links** — OSF preregistration URLs for E0, EXP-1, EXP-2, EXP-3
- [ ] **Compute budget** — Total GPU-hours reported; within NeurIPS limits

---

## 2. Statistical Rigor Checklist (NeurIPS 2026 Standards)

### 2.1 Experimental Design
- [ ] **Pre-registered hypotheses** — H*, H1, H2, H3 registered on OSF before data collection
- [ ] **Pre-registered analysis plan** — Primary/secondary endpoints, statistical tests, alpha
- [ ] **Power analysis** — Minimum detectable effect, sample size justification, power ≥ 0.8
- [ ] **Randomization** — Seeds randomized across conditions; order counterbalanced
- [ ] **Blinding** — Analysis code blinded to condition labels where possible

### 2.2 Statistical Reporting
- [ ] **Effect sizes** — Cohen's d / Cliff's delta / odds ratio with 95% CI for all primary comparisons
- [ ] **Confidence intervals** — 95% CI on all point estimates (not just p-values)
- [ ] **Exact p-values** — Reported to 3 decimal places; p < 0.001 reported as p < 0.001
- [ ] **Multiple comparison correction** — Bonferroni / Holm-Bonferroni / FDR reported
- [ ] **Bayesian analysis** — BF₁₀ reported for primary hypotheses (optional but recommended)
- [ ] **Assumption checks** — Normality (Shapiro-Wilk), homoscedasticity (Levene), independence verified

### 2.3 Replication
- [ ] **≥5 seeds** — Minimum 5 independent seeds per condition (NeurIPS standard)
- [ ] **Cross-seed variability** — Report mean ± SD across seeds; show individual seed trajectories
- [ ] **Reproducibility across machines** — Verified on ≥2 GPU types if GPU-dependent

---

## 3. Methodological Soundness (Program D Specific)

### 3.1 Hypothesis Falsifiability (Program D Constitution §2)
- [ ] **H* (Central)** — Falsifiable: T beats C1 & C2 on held-out LL at p<0.01; M(θₖ) exceeds shuffled control
- [ ] **H1 (Calibration)** — Falsifiable: ECE < 0.1 on ≥200 mixed queries; kill criterion = no better than constant baseline
- [ ] **H2 (Affective Indexing)** — Falsifiable: Framed > Unframed on objective task score; kill = no significant difference
- [ ] **H3 (Emergent Development)** — Falsifiable: Transfer of emergent structure to held-out prediction task

### 3.2 Kill Criteria Enforcement (Program D Constitution §4)
- [ ] **Kill criteria pre-registered** — K1–K10 documented in `foundation/kill_criteria/kill_criteria.md`
- [ ] **Kill criteria evaluated** — Each experiment reports pass/fail against pre-registered kill criteria
- [ ] **Negative results reported** — If kill criterion triggered, reported as primary result (not buried)

### 3.3 No Designer Injection (Program D Constitution §2.5)
- [ ] **No hand-authored ontology** — E0 uses zero seeded concepts; only error-gated growth
- [ ] **No injected structure** — C3 (shuffled-input control) isolates injected structure
- [ ] **Emergence statistic M(θₖ)** — Referenced against shuffled-input null: M(θₖ) - E[M|H₀]

### 3.4 No Anthropomorphic Language (Program D Constitution §2.4)
- [ ] **Zero anthropomorphic terms** — "mind", "soul", "understanding", "belief", "intention", "awareness", "consciousness" removed
- [ ] **Operational definitions only** — "predictive organism", "structure acquisition", "affective indexing", "calibration"
- [ ] **Terminology compliance** — All terms from `TERMINOLOGY.md` used correctly

---

## 4. Novelty & Related Work (NeurIPS Standards)

### 4.1 Novelty Analysis (Program D `foundation/novelty/novelty_analysis.md`)
- [ ] **11 reference fields surveyed** — SSL, MDL, predictive coding, developmental robotics, continual learning, meta-learning, neural architecture search, neural-symbolic, calibration, affective computing, emergence measurement
- [ ] **Novelty claims precise** — "First to X" → "First to X under conditions Y with measurement Z"
- [ ] **Negative results cited** — Prior work showing similar mechanisms failed cited and distinguished

### 4.2 Baselines (Program D Constitution §4)
- [ ] **C1: Fixed-capacity control** — Same architecture, no growth
- [ ] **C2: Error-decoupled growth** — Capacity-matched growth at random times
- [ ] **C3: Shuffled-input control** — Destroys temporal structure, preserves marginals
- [ ] **Standard baselines** — Relevant SOTA from each reference field implemented and run

---

## 5. Ethics & Broader Impacts (NeurIPS 2026)

### 5.1 Ethics Checklist
- [ ] **No human subjects** — Synthetic data only (E0); anonymized queries only (EXP-1); no PII
- [ ] **No dual-use concern** — Predictive organism on synthetic streams; no autonomous weapons, surveillance, deception
- [ ] **Environmental impact** — GPU-hours reported; carbon estimate included
- [ ] **Data licenses** — All data sources licensed for research reuse

### 5.2 Broader Impacts Statement
- [ ] **Honest uncertainty** — Program A calibration claim: "honest uncertainty" not "truthfulness"
- [ ] **No AGI claims** — "Predictive organism acquires structure" not "agent develops understanding"
- [ ] **Affective indexing scope** — Limited to retrieval key for problem-solving schemas; no emotion simulation claims

---

## 6. NeurIPS-Specific Requirements

### 6.1 Paper Format
- [ ] **Page limit** — 8 pages main text + unlimited references + appendix
- [ ] **Anonymous submission** — No author names, affiliations, self-citations identified
- [ ] **Supplementary material** — Appendix + code + data uploaded separately
- [ ] **Checklist** — NeurIPS reproducibility checklist completed and included

### 6.2 Artifact Evaluation (Optional but Recommended)
- [ ] **Artifact submission** — Code + data + documentation packaged for NeurIPS Artifact Evaluation
- [ ] **Badges targeted** — "Artifacts Available", "Artifacts Functional", "Results Reproduced"

---

## 7. Program D Specific Publication Blockers

### 7.1 Must-Resolve Before Submission
- [ ] **E0 preregistration live on OSF** — URL in paper
- [ ] **E0 kill criteria evaluated** — Pass/fail documented in `kill_criteria_validation_report.md`
- [ ] **E0 emergence statistic M(θₖ) implemented** — In `core/emergence/emergence_statistic.py` with null reference
- [ ] **E0 C3 shuffled control implemented** — In `core/controls/shuffled_input.py`
- [ ] **EXP-1 ECE < 0.1 achieved** — Or negative result documented per kill criterion
- [ ] **EXP-2 affective framing effect measured** — Objective task score, not subjective rating
- [ ] **EXP-3/EXP-0 dependency resolved** — EXP-3 is precursor; E0 is rigorous version
- [ ] **No circular logic** — Hypotheses not adjusted post-hoc to match results
- [ ] **Assumption ledger complete** — I1, I2, I3 documented with coverage matrix

### 7.2 Documentation Artifacts Required
- [ ] `foundation/hypothesis/central_hypothesis.md` — H* fully specified
- [ ] `foundation/hypothesis/H1_calibration.md` — H1 fully specified
- [ ] `foundation/hypothesis/H2_affective_indexing.md` — H2 fully specified
- [ ] `foundation/hypothesis/H3_emergent_development.md` — H3 fully specified
- [ ] `foundation/assumptions/assumption_ledger.md` — I1, I2, I3 documented
- [ ] `foundation/assumptions/assumption_coverage_matrix.csv` — Experiment→Assumption coverage
- [ ] `foundation/kill_criteria/kill_criteria.md` — K1–K10 with pass/fail logic
- [ ] `foundation/kill_criteria/kill_criteria_validation_report.md` — Per-experiment evaluation
- [ ] `foundation/mathematics/mathematical_foundation.md` — 5 primitives + derivations
- [ ] `foundation/mathematics/variable_provenance.md` — Every variable traced to source
- [ ] `foundation/novelty/novelty_analysis.md` — 11-field survey with novelty claims
- [ ] `foundation/novelty/publication_test.md` — Publication readiness assessment

---

## 8. Acceptance Probability Assessment

| Checklist Section | Items Passing | Total | Pass Rate | Impact on Acceptance |
|-------------------|---------------|-------|-----------|---------------------|
| Reproducibility | ___ | 12 | ___% | **Blocker** if < 100% |
| Statistical Rigor | ___ | 15 | ___% | **Blocker** if < 90% |
| Methodological Soundness | ___ | 12 | ___% | **Blocker** if < 100% |
| Novelty & Baselines | ___ | 8 | ___% | **Major weakness** if < 80% |
| Ethics & Impacts | ___ | 8 | ___% | **Desk reject** if violated |
| NeurIPS Format | ___ | 8 | ___% | **Desk reject** if violated |
| Program D Blockers | ___ | 15 | ___% | **Reject** if any fail |

**Overall Assessment:**
- [ ] **Ready for submission** — All blockers resolved, pass rate ≥ 95%
- [ ] **Major revisions needed** — 1–2 blockers, fixable in 2–4 weeks
- [ ] **Reject** — ≥3 blockers or fundamental methodological flaw

---

**Auditor:** _________________________
**Date:** _________________________
**Next Review:** _________________________
# Master Publication Checklist — Program D

**Purpose:** Single document ensuring all publication artifacts exist before writing any paper.
**Scope:** All venues (NeurIPS, ICML, ICLR, Nature MI, Science Robotics, NSF)
**Status:** Living document — check off items as completed

---

## 1. Foundation Documents (22 files in `foundation/`)

### 1.1 Hypotheses
- [ ] `foundation/hypothesis/central_hypothesis.md` — H* fully specified
- [ ] `foundation/hypothesis/H1_calibration.md` — H1 fully specified
- [ ] `foundation/hypothesis/H2_affective_indexing.md` — H2 fully specified
- [ ] `foundation/hypothesis/H3_emergent_development.md` — H3 fully specified

### 1.2 Assumptions
- [ ] `foundation/assumptions/assumption_ledger.md` — I1, I2, I3 documented
- [ ] `foundation/assumptions/assumption_coverage_matrix.csv` — Experiment→Assumption coverage
- [ ] `foundation/assumptions/parameter_atlas.md` — All parameters

### 1.3 Kill Criteria
- [ ] `foundation/kill_criteria/kill_criteria.md` — K1–K10 with pass/fail logic
- [ ] `foundation/kill_criteria/kill_criteria_validation_report.md` — Per-experiment evaluation

### 1.4 Mathematics
- [ ] `foundation/mathematics/mathematical_foundation.md` — 5 primitives + derivations
- [ ] `foundation/mathematics/variable_provenance.md` — Every variable traced
- [ ] `foundation/mathematics/variable_dependency_graph.graphml` — Graph format
- [ ] `foundation/mathematics/variable_dependency_matrix.csv` — Adjacency matrix

### 1.5 Architecture
- [ ] `foundation/architecture/architecture.md` — System structure
- [ ] `foundation/architecture/dependency_graph.graphml` — Module dependencies
- [ ] `foundation/architecture/dependency_matrix.csv` — Adjacency
- [ ] `foundation/architecture/layer_diagram.mmd` — Mermaid diagram

### 1.6 Novelty
- [ ] `foundation/novelty/novelty_analysis.md` — 11-field survey
- [ ] `foundation/novelty/publication_test.md` — Publication readiness

---

## 2. Core Primitives (`core/`)

- [ ] `core/predictors/base.py` — Predictor interface
- [ ] `core/predictors/dirichlet_markov.py` — Conjugate predictor
- [ ] `core/emergence/emergence_statistic.py` — NMI estimator, M(θₖ)
- [ ] `core/emergence/null_referenced_test.py` — Null-referenced construction
- [ ] `core/mdl/mdl_growth.py` — MDL description-length
- [ ] `core/mdl/concept_birth_ledger.py` — Growth event ledger
- [ ] `core/measurement/proper_scoring.py` — Log-loss scorer
- [ ] `core/measurement/metrics.py` — Consolidated metrics
- [ ] `core/measurement/observability.py` — Instrumentation
- [ ] `core/controls/fixed_capacity.py` — C1 control
- [ ] `core/controls/random_growth.py` — C2 control
- [ ] `core/controls/shuffled_input.py` — C3 control

---

## 3. Experiments (`experiments/`)

### 3.1 E0
- [ ] `experiments/E0/preregistration.md`
- [ ] `experiments/E0/protocol.md`
- [ ] `experiments/E0/run.py`
- [ ] `experiments/E0/analysis.py`
- [ ] `experiments/E0/detectors.py`
- [ ] `experiments/E0/dataset.py`
- [ ] `experiments/E0/leakage_check.py`
- [ ] `experiments/E0/paraphrases.json` (if applicable)

### 3.2 EXP-0
- [ ] Same as E0 structure (benchmark paraphrase test)

### 3.3 EXP-1
- [ ] Same as E0 structure (calibration test)

### 3.4 EXP-2
- [ ] Same as E0 structure (affective indexing test)

### 3.5 EXP-3
- [ ] Same as E0 structure (emergent development test)

### 3.6 Coverage
- [ ] `experiments/coverage/experiment_coverage_matrix.csv`

---

## 4. Publication Infrastructure (`NX/publication_infrastructure/`)

### 4.1 Reviewer Checklists
- [ ] `reviewer_checklists/neurips_reviewer_checklist.md`
- [ ] `reviewer_checklists/icml_iclr_reviewer_checklist.md`
- [ ] `reviewer_checklists/nature_mi_reviewer_checklist.md`
- [ ] `reviewer_checklists/nsf_reviewer_checklist.md`
- [ ] `reviewer_checklists/science_robotics_reviewer_checklist.md` (if applicable)
- [ ] `reviewer_checklists/reviewer_2_rejection_checklist.md` (preemptive reviewer #2)

### 4.2 Statistical Templates
- [ ] `statistical_templates/statistical_reporting_template.md`

### 4.3 Figure & Table Specs
- [ ] `figure_specs/figure_table_specifications.md`

### 4.4 Supplementary Templates
- [ ] `supplementary_templates/supplementary_material_template.md`

### 4.5 Artifact Evaluation
- [ ] `artifact_evaluation/artifact_evaluation_checklist.md`

### 4.6 Reproducibility Packages
- [ ] `reproducibility_packages/reproducibility_package_template.md`

### 4.7 OSF Preregistration
- [ ] `osf_preregistration/osf_preregistration_template.md`

### 4.8 Zenodo Packaging
- [ ] `zenodo_packaging/zenodo_packaging_template.md`

### 4.9 Paper Templates
- [ ] `paper_templates/paper_templates.md`

### 4.10 General Checklists
- [ ] `checklists/master_publication_checklist.md` (this file)
- [ ] `checklists/pre_submission_audit.md`
- [ ] `checklists/constitution_compliance.md`

---

## 5. Pre-Registration (OSF)

- [ ] OSF project created
- [ ] H* preregistration filled, locked, public
- [ ] H1 preregistration filled, locked, public
- [ ] H2 preregistration filled, locked, public
- [ ] H3 preregistration filled, locked, public
- [ ] All preregistrations include: hypothesis, design, sampling, variables, analysis plan, kill criteria, deviations plan

---

## 6. Code & Data (GitHub + Zenodo)

### 6.1 GitHub
- [ ] Repository public
- [ ] License: Apache-2.0 (code), CC-BY-4.0 (data)
- [ ] README with reproduction instructions
- [ ] requirements.txt with pinned versions
- [ ] Dockerfile
- [ ] CITATION.cff
- [ ] All experiments have run.py + analysis.py
- [ ] All foundation documents committed
- [ ] All core primitives committed
- [ ] `git rev-parse HEAD` recorded for paper

### 6.2 Zenodo
- [ ] One DOI per experiment deposit
- [ ] One DOI per program release
- [ ] Metadata complete: title, authors, description, keywords, license
- [ ] Related identifiers: paper DOI, GitHub, OSF
- [ ] CITATION.cff included
- [ ] manifest.json included
- [ ] environment.txt included

---

## 7. Pre-Submission Audit (Per Paper)

For each paper to be submitted, complete the corresponding reviewer checklist:
- [ ] NeurIPS paper → `neurips_reviewer_checklist.md` (all sections pass)
- [ ] ICML paper → `icml_iclr_reviewer_checklist.md` (all sections pass)
- [ ] ICLR paper → `icml_iclr_reviewer_checklist.md` (all sections pass)
- [ ] Nature MI paper → `nature_mi_reviewer_checklist.md` (all sections pass)
- [ ] NSF proposal → `nsf_reviewer_checklist.md` (all sections pass)
- [ ] Science Robotics paper → `science_robotics_reviewer_checklist.md`

---

## 8. Constitution Compliance

- [ ] No anthropomorphic language in main claims (Constitution §2.4)
- [ ] No designer injection (Constitution §2.5)
- [ ] No novelty inflation (Constitution §2.6)
- [ ] No unsupported neuroscience (Constitution §2.7)
- [ ] No unsupported cognitive claims (Constitution §2.8)
- [ ] Every statement tagged [FACT]/[HYPOTHESIS]/[SPECULATION]/[REJECTED] (Constitution §3)
- [ ] Kill criteria evaluated and reported (Constitution §4)
- [ ] No subsystem without pre-registered experiment (Constitution §4)

---

## 9. Terminology Compliance (TERMINOLOGY.md)

- [ ] "mind", "soul", "understanding" replaced with "predictive organism", "structure acquisition"
- [ ] "Free Energy" (as in Program C) replaced with "predictive log-likelihood"
- [ ] "Resonance", "Sleep/Replay", "Thermodynamic State" removed or operationalized
- [ ] All terms from TERMINOLOGY.md used correctly
- [ ] All deprecated terms absent from paper

---

## 10. Statistical Rigor (Per Experiment)

- [ ] Pre-registered analysis plan
- [ ] ≥5 seeds (E0, EXP-3) or ≥200 queries (EXP-1) or ≥30 tasks (EXP-2)
- [ ] Power analysis reported
- [ ] Effect sizes with 95% CI
- [ ] Multiple comparison correction
- [ ] Bayesian analysis (BF₁₀)
- [ ] Assumption checks
- [ ] Per-seed data reported
- [ ] Negative results reported

---

## 11. Figures & Tables (Per Paper)

- [ ] All figures follow `figure_table_specifications.md`
- [ ] All tables follow `figure_table_specifications.md`
- [ ] Colorblind-safe palette
- [ ] Vector format (PDF/SVG)
- [ ] Data files (CSV) for each figure/table
- [ ] Captions self-contained

---

## 12. Supplementary Material (Per Paper)

- [ ] Extended methods (math, algorithms, protocol, hyperparameters, deviations)
- [ ] Extended results (full tables, per-seed, learning curves, assumptions, sensitivity, negative)
- [ ] Reproducibility (code/data availability, compute, seeds, manifest)
- [ ] Additional figures/tables
- [ ] Kill criteria evaluation report
- [ ] Assumption coverage matrix
- [ ] Novelty analysis details
- [ ] Terminology & notation reference

---

## 13. Per-Paper Submission Checklist

### 13.1 Pre-Submission (1 week before)
- [ ] All above items complete
- [ ] Internal review by co-authors
- [ ] External review by 2–3 colleagues
- [ ] Pre-print (arXiv) submitted
- [ ] All co-authors approved final version
- [ ] Reproducibility package tested on fresh machine

### 13.2 Submission
- [ ] Paper formatted per venue LaTeX template
- [ ] Anonymous (NeurIPS/ICML/ICLR) or author names (Nature/Science/NSF)
- [ ] All required checklists completed
- [ ] Code/data DOIs in paper
- [ ] OSF preregistration URLs in paper
- [ ] Supplementary material uploaded
- [ ] Reproducibility package uploaded (NeurIPS AE)
- [ ] Author contributions documented
- [ ] Conflicts of interest declared
- [ ] Funding acknowledged

### 13.3 Post-Submission
- [ ] Response to reviewers (if revisions)
- [ ] Update Zenodo with new version
- [ ] Update OSF with results
- [ ] Add paper DOI to GitHub
- [ ] Add paper DOI to Zenodo

---

## 14. Acceptance Probability Estimates

| Paper | Pre-Fix Probability | Post-Fix Probability |
|-------|---------------------|----------------------|
| E0 → NeurIPS | 15% | 65% (if all artifacts present) |
| E0 → ICML | 20% | 70% |
| E0 → ICLR | 18% | 68% |
| E0 → Nature MI | 5% | 25% (higher bar for Nature) |
| EXP-1 → NeurIPS | 25% | 75% (calibration is publishable) |
| EXP-2 → NeurIPS | 20% | 65% (novel but risky) |
| EXP-3 → NeurIPS | 15% | 60% (precursor to E0) |
| NSF proposal | 30% | 60% |

**Probability increases with:**
- Complete foundation documents
- Pre-registration
- Kill criteria evaluated
- ≥5 seeds
- Effect sizes with CI
- Null-referenced statistics
- Strong baselines
- Open code/data with DOIs

**Probability decreases with:**
- Missing pre-registration
- Designer injection detected
- Anthropomorphic language
- Straw-man baselines
- No confidence intervals
- Incomplete kill criteria evaluation
- Closed code/data

---

## 15. Outstanding Items (Before First Paper)

Critical path:
1. Complete all 22 foundation documents
2. Implement `core/` primitives
3. Write E0 protocol + preregistration
4. Run E0 with 5 seeds
5. Evaluate kill criteria
6. Write E0 paper
7. Submit E0 paper

Estimated time: 8–12 weeks

---

**Checklist Version:** 1.0
**Last Updated:** 2026-07-03
**Owner:** Principal Investigator (Program D)
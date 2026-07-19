# Pre-Submission Audit Checklist — Program D

**Purpose:** Final audit before submitting any paper.
**Trigger:** Run this checklist 1 week before submission deadline.
**Authority:** Combines all reviewer checklists + Constitution compliance.

---

## 1. Paper Metadata

- [ ] Title: Describes scientific claim, no hype, ≤ 200 chars
- [ ] Authors: All listed with ORCID and affiliation
- [ ] Abstract: ≤ 250 words (NeurIPS/ICML/ICLR)
- [ ] Keywords: 3–6 relevant
- [ ] Paper length: Within venue limit
- [ ] Format: Venue LaTeX template
- [ ] Anonymity: No identifying info (if double-blind)

---

## 2. Foundation Compliance

- [ ] All 22 foundation documents exist and are current
- [ ] All hypotheses in paper trace to `HYPOTHESIS_REGISTER.md`
- [ ] All assumptions in paper trace to `foundation/assumptions/`
- [ ] All kill criteria evaluated in `kill_criteria_validation_report.md`
- [ ] All math in paper traces to `mathematical_foundation.md`
- [ ] Novelty claims in paper trace to `novelty_analysis.md`

---

## 3. Pre-Registration Compliance

- [ ] OSF preregistration URL in paper
- [ ] Pre-registration matches protocol
- [ ] Pre-registration matches results
- [ ] Any deviations logged and justified
- [ ] Pre-registration is locked (cannot be edited)

---

## 4. Code & Data Compliance

- [ ] GitHub repository public with license
- [ ] Exact commit hash in paper
- [ ] Zenodo DOIs in paper
- [ ] Dockerfile included
- [ ] `reproduce.sh` tested on fresh machine
- [ ] `requirements.txt` with pinned versions
- [ ] CITATION.cff included
- [ ] `manifest.json` validates

---

## 5. Statistical Compliance

- [ ] ≥5 seeds for stochastic experiments
- [ ] Effect sizes with 95% CI for all primary comparisons
- [ ] p-values exact (3 decimal places)
- [ ] Multiple comparison correction applied
- [ ] Bayesian analysis (BF₁₀) reported
- [ ] Assumption checks (normality, homoscedasticity) reported
- [ ] Per-seed data in supplementary
- [ ] Negative results reported prominently

---

## 6. Kill Criteria Compliance

- [ ] All pre-registered kill criteria evaluated
- [ ] Pass/fail reported in main paper
- [ ] Failure modes discussed in main paper
- [ ] Kill criteria report in supplementary

---

## 7. Constitution Compliance

- [ ] No anthropomorphic language (greps pass)
- [ ] No designer injection (greps pass)
- [ ] No novelty inflation (manual check)
- [ ] No unsupported neuroscience (greps pass)
- [ ] No unsupported cognitive claims (manual check)
- [ ] Epistemic tags on all claims (FACT/HYPOTHESIS/SPECULATION/REJECTED)
- [ ] Terminology compliant (greps pass)

---

## 8. Figures & Tables

- [ ] All figures follow `figure_table_specifications.md`
- [ ] All tables follow `figure_table_specifications.md`
- [ ] Colorblind-safe palette
- [ ] Vector format
- [ ] Data files (CSV) for each figure/table
- [ ] Captions self-contained
- [ ] No data leakage in figures

---

## 9. Supplementary Material

- [ ] Extended methods (math, algorithms, protocol, hyperparameters)
- [ ] Extended results (full tables, per-seed, learning curves)
- [ ] Assumption checks
- [ ] Sensitivity analyses
- [ ] Negative results
- [ ] Reproducibility section (code/data, compute, seeds, manifest)
- [ ] Kill criteria evaluation report
- [ ] Assumption coverage matrix
- [ ] Novelty analysis details
- [ ] Terminology reference

---

## 10. Ethics & Broader Impacts

- [ ] No human subjects
- [ ] No dual-use concern
- [ ] Carbon footprint reported
- [ ] Data licenses documented
- [ ] Broader impacts statement (NeurIPS/ICML)
- [ ] Ethics statement (Nature/Science)
- [ ] Conflicts of interest declared
- [ ] Funding acknowledged
- [ ] Author contributions documented (CRediT)

---

## 11. Reproducibility

- [ ] One-command reproduction works
- [ ] All seeds documented
- [ ] CUDA deterministic mode enabled
- [ ] PYTHONHASHSEED set
- [ ] Runtime estimates accurate (within 2x)
- [ ] Compute requirements documented
- [ ] Storage requirements documented
- [ ] Cross-machine test passed

---

## 12. Internal Review

- [ ] Co-author review complete
- [ ] External colleague review (2–3 people)
- [ ] Pre-print on arXiv (optional but recommended)
- [ ] Response to internal review documented
- [ ] All co-authors approved final version
- [ ] Author order confirmed

---

## 13. Venue-Specific

### 13.1 NeurIPS
- [ ] NeurIPS LaTeX template
- [ ] 8-page main + unlimited refs + supplementary
- [ ] Anonymized
- [ ] NeurIPS Reproducibility Checklist
- [ ] (Optional) Artifact Evaluation submission
- [ ] (Optional) Pre-registration commitment

### 13.2 ICML
- [ ] ICML LaTeX template
- [ ] 8-page main + unlimited refs + supplementary
- [ ] Anonymized
- [ ] ICML Reproducibility Checklist v2.1
- [ ] (Optional) Artifact Evaluation submission

### 13.3 ICLR
- [ ] ICLR LaTeX template
- [ ] 9-page main + unlimited refs + supplementary
- [ ] Anonymized
- [ ] ICLR Reproducibility Checklist
- [ ] Open Review (public)

### 13.4 Nature Machine Intelligence
- [ ] Nature LaTeX template
- [ ] ~6–8 page main + unlimited supplementary
- [ ] Author names included
- [ ] Reporting Summary completed
- [ ] MDAR checklist completed
- [ ] Code/data DOIs at submission
- [ ] Statement of significance
- [ ] Statement of competing interests
- [ ] Author contributions (CRediT)
- [ ] Data availability statement
- [ ] Code availability statement

### 13.5 Science Robotics
- [ ] Science Robotics LaTeX template
- [ ] ~6 page main + unlimited supplementary
- [ ] Author names included
- [ ] Materials & Methods
- [ ] Data availability statement
- [ ] Code with DOI

### 13.6 NSF
- [ ] 15-page Project Description
- [ ] 2-page Data Management Plan
- [ ] 1-page Postdoc Mentoring Plan (if applicable)
- [ ] Collaborators & Other Affiliations (COA)
- [ ] Current & Pending Support
- [ ] Facilities, Equipment & Other Resources
- [ ] Budget justification
- [ ] Broader impacts addressed

---

## 14. Final Sign-Off

- [ ] **PI:** All above items verified
- [ ] **Co-authors:** Approved
- [ ] **External reviewers:** Approved (or revisions addressed)
- [ ] **Legal/IP:** No conflicts, all permissions obtained
- [ ] **Pre-registration:** Live and matches results
- [ ] **Code:** Committed and tested
- [ ] **Data:** Deposited with DOIs
- [ ] **Paper:** Final version ready
- [ ] **Supplementary:** Compiled and ready
- [ ] **Reproducibility package:** Tested

**Date:** _________________________
**Signature:** _________________________

---

## 15. Post-Submission Tasks

- [ ] Track submission status
- [ ] Respond to reviewers (if revisions requested)
- [ ] Update Zenodo with new version (if revisions)
- [ ] Update OSF with results
- [ ] Add paper DOI to GitHub
- [ ] Add paper DOI to Zenodo
- [ ] Add paper to publication list
- [ ] Share with community (Twitter, mailing lists, etc.)

---

**Checklist Version:** 1.0
**Last Updated:** 2026-07-03
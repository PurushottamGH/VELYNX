# Reviewer #2 Rejection Checklist — Program D

**Purpose:** Simulate the harshest reviewer (Reviewer #2) for Program D submissions.
**Target Venues:** NeurIPS, ICML, ICLR, Nature Machine Intelligence, Science Robotics, NSF
**Method:** Pre-emptively find fatal flaws before submission.

**Note:** This is the "Find fatal flaws" checklist from the original Publication Committee prompt. Run before every submission to identify weaknesses that Reviewer #2 will exploit.

---

## 1. Fatal Flaws (Auto-Reject)

### 1.1 Methodological Fatal Flaws
- [ ] **Designer injection detected** — E0 has seeded concepts, hand-authored ontology
  - Impact: Reject (violates Constitution §2.5)
  - Evidence needed: Verify E0 has zero seeded concepts; C3 shuffled control present
  - Fix: Remove all seeded concepts from E0; add C3 control
  - Post-fix acceptance: 15% → 65%

- [ ] **No null reference for emergence** — M(θₖ) defined as absolute NMI
  - Impact: Reject (can always be high by chance)
  - Evidence needed: M(θₖ) - E[M|H₀] via C3
  - Fix: Implement null-referenced M(θₖ)
  - Post-fix acceptance: 20% → 70%

- [ ] **Kill criteria not evaluated** — Paper claims success without evaluating
  - Impact: Reject (violates Constitution §4)
  - Evidence needed: Kill criteria report with pass/fail
  - Fix: Generate `kill_criteria_validation_report.md`
  - Post-fix acceptance: 25% → 75%

- [ ] **No pre-registration** — Hypotheses and analysis not pre-registered
  - Impact: Reject (HARKing suspected)
  - Evidence needed: OSF preregistration URL
  - Fix: Register on OSF before data collection
  - Post-fix acceptance: 10% → 60%

### 1.2 Statistical Fatal Flaws
- [ ] **<5 seeds** — Only 1–3 seeds reported
  - Impact: Reject (underpowered)
  - Evidence needed: ≥5 seeds per condition
  - Fix: Run more seeds; pre-register minimum
  - Post-fix acceptance: 20% → 65%

- [ ] **No confidence intervals** — Only p-values reported
  - Impact: Reject (effect size unknown)
  - Evidence needed: 95% CI on all estimates
  - Fix: Add bootstrap CIs; Bayesian CIs
  - Post-fix acceptance: 25% → 70%

- [ ] **No effect sizes** — Only p-values reported
  - Impact: Reject (practical significance unknown)
  - Evidence needed: Cohen's d / Cliff's delta with CI
  - Fix: Add effect size calculations
  - Post-fix acceptance: 25% → 70%

- [ ] **p-hacking detected** — Many tests, only significant reported
  - Impact: Reject (researcher DoF)
  - Evidence needed: Pre-registered primary + secondary
  - Fix: Pre-register; report all tests
  - Post-fix acceptance: 10% → 55%

### 1.3 Reproducibility Fatal Flaws
- [ ] **Code not available** — "Available upon request"
  - Impact: Reject (NeurIPS/ICML standard)
  - Evidence needed: Public repo with license
  - Fix: GitHub + Zenodo with DOI
  - Post-fix acceptance: 5% → 60%

- [ ] **Data not available** — Synthetic data generator not shared
  - Impact: Reject (can't verify)
  - Evidence needed: Generator code + seed
  - Fix: Include `dataset.py` in repo
  - Post-fix acceptance: 10% → 65%

- [ ] **No compute specification** — Reviewer can't estimate resources
  - Impact: Major weakness
  - Evidence needed: GPU, runtime, memory
  - Fix: Add compute section
  - Post-fix acceptance: 30% → 70%

---

## 2. Missing Literature (Reject-Worthy)

- [ ] **No prior SSL work cited** — Contrastive, masked, autoregressive
  - Impact: Reject (foundational missing)
  - Evidence needed: Citations to Chen et al. 2020, He et al. 2020, etc.
  - Fix: Add SSL section in related work
  - Post-fix acceptance: 20% → 65%

- [ ] **No MDL work cited** — Rissanen, Grünwald, etc.
  - Impact: Reject (foundational missing)
  - Evidence needed: Citations to MDL literature
  - Fix: Add MDL section
  - Post-fix acceptance: 20% → 65%

- [ ] **No predictive coding work cited** — Rao & Ballard, Friston, etc.
  - Impact: Reject (foundational missing)
  - Evidence needed: Citations to predictive coding
  - Fix: Add predictive coding section
  - Post-fix acceptance: 20% → 65%

- [ ] **No developmental robotics work cited** — Worgotter, Lungarella, etc.
  - Impact: Reject (foundational missing)
  - Evidence needed: Citations to developmental robotics
  - Fix: Add developmental robotics section
  - Post-fix acceptance: 20% → 60%

- [ ] **No emergence measurement work cited** — Crutchfield, Shalizi, etc.
  - Impact: Reject (foundational missing)
  - Evidence needed: Citations to emergence measurement
  - Fix: Add emergence measurement section
  - Post-fix acceptance: 20% → 65%

---

## 3. Stronger Baselines (Reviewer Will Demand)

- [ ] **Only straw-man baselines** — Random, constant, trivial
  - Impact: Major weakness
  - Evidence needed: SOTA from each reference field
  - Fix: Implement and run SOTA baselines
  - Post-fix acceptance: 15% → 60%

- [ ] **No compute-matched baselines** — Treatment has 10x compute
  - Impact: Major weakness
  - Evidence needed: FLOPs/parameters matched
  - Fix: Match compute across conditions
  - Post-fix acceptance: 20% → 65%

- [ ] **No ablation of components** — Can't tell what matters
  - Impact: Major weakness
  - Evidence needed: Ablation of each primitive
  - Fix: Add ablation studies
  - Post-fix acceptance: 15% → 60%

- [ ] **No capacity-matched control** — T has more parameters
  - Impact: Major weakness (can't attribute to growth)
  - Evidence needed: C2 control
  - Fix: Implement C2
  - Post-fix acceptance: 10% → 60%

- [ ] **No shuffled-input control** — Can't tell if temporal structure matters
  - Impact: Major weakness
  - Evidence needed: C3 control
  - Fix: Implement C3
  - Post-fix acceptance: 10% → 65%

---

## 4. Statistical Weaknesses (Reviewer Will Find)

- [ ] **No multiple comparison correction** — 10 tests, all reported
  - Impact: Major weakness
  - Evidence needed: Bonferroni/Holm/FDR
  - Fix: Apply correction
  - Post-fix acceptance: 20% → 65%

- [ ] **No assumption checks** — t-tests on non-normal data
  - Impact: Major weakness
  - Evidence needed: Shapiro-Wilk, Levene, Q-Q plots
  - Fix: Add assumption checks
  - Post-fix acceptance: 25% → 70%

- [ ] **No power analysis** — Sample size unjustified
  - Impact: Major weakness
  - Evidence needed: G*Power or simulation
  - Fix: Add power analysis
  - Post-fix acceptance: 25% → 65%

- [ ] **No sensitivity analysis** — Results depend on arbitrary choices
  - Impact: Major weakness
  - Evidence needed: Hyperparameter sweeps
  - Fix: Add sensitivity analyses
  - Post-fix acceptance: 20% → 65%

- [ ] **Conflating statistical and practical significance** — p < 0.001 but d = 0.1
  - Impact: Major weakness
  - Evidence needed: Effect sizes with CI
  - Fix: Report effect sizes prominently
  - Post-fix acceptance: 20% → 65%

---

## 5. Reproducibility Problems (Reviewer Will Find)

- [ ] **No Dockerfile** — Can't reproduce environment
  - Impact: Major weakness
  - Evidence needed: Dockerfile + tested
  - Fix: Add Dockerfile
  - Post-fix acceptance: 30% → 70%

- [ ] **No pinned versions** — requirements.txt has loose specs
  - Impact: Major weakness
  - Evidence needed: Exact versions
  - Fix: Pin all versions
  - Post-fix acceptance: 30% → 70%

- [ ] **No seed specification** — Can't reproduce exact results
  - Impact: Major weakness
  - Evidence needed: All seeds documented
  - Fix: Document seeds
  - Post-fix acceptance: 25% → 65%

- [ ] **No runtime estimates** — Reviewer can't plan reproduction
  - Impact: Minor weakness
  - Evidence needed: Runtime per experiment
  - Fix: Add runtime section
  - Post-fix acceptance: 35% → 70%

- [ ] **No environment.txt** — Can't verify compute environment
  - Impact: Minor weakness
  - Evidence needed: pip freeze, nvidia-smi
  - Fix: Add environment.txt
  - Post-fix acceptance: 35% → 70%

---

## 6. Governance Issues (NSF Specific)

- [ ] **No Data Management Plan** — NSF requires
  - Impact: Return without review
  - Evidence needed: 2-page DMP
  - Fix: Write DMP per NSF 22-1
  - Post-fix acceptance: 0% → 60%

- [ ] **No Broader Impacts** — NSF criterion
  - Impact: Major weakness
  - Evidence needed: Concrete BI plan
  - Fix: Add BI section
  - Post-fix acceptance: 20% → 60%

- [ ] **No Postdoc Mentoring Plan** — If postdoc budgeted
  - Impact: Return without review
  - Evidence needed: 1-page PMP
  - Fix: Write PMP
  - Post-fix acceptance: 0% → 60%

- [ ] **No preliminary data** — Central hypothesis untested
  - Impact: Major weakness
  - Evidence needed: Pilot results
  - Fix: Run pilot E0
  - Post-fix acceptance: 10% → 55%

- [ ] **No timeline with milestones** — Can't assess feasibility
  - Impact: Major weakness
  - Evidence needed: Gantt chart aligned with experiments
  - Fix: Add timeline
  - Post-fix acceptance: 25% → 60%

---

## 7. Ethics Problems (Reviewer Will Object)

- [ ] **Anthropomorphic language** — "mind", "soul", "understands"
  - Impact: Reject (violates Constitution §2.4)
  - Evidence needed: Greps pass
  - Fix: Replace with operational terms
  - Post-fix acceptance: 10% → 65%

- [ ] **Hype** — "AGI", "human-level", "revolutionary"
  - Impact: Major weakness
  - Evidence needed: Specific, measurable claims
  - Fix: Remove hype; use specific claims
  - Post-fix acceptance: 20% → 65%

- [ ] **Unsupported neuroscience** — LTP, STDP, hippocampal replay without implementation
  - Impact: Reject (violates Constitution §2.7)
  - Evidence needed: Implementation matches claims
  - Fix: Implement or remove claims
  - Post-fix acceptance: 10% → 60%

- [ ] **Dual-use concern not addressed** — Predictive organism could be misused
  - Impact: Major weakness
  - Evidence needed: Dual-use section
  - Fix: Add dual-use assessment
  - Post-fix acceptance: 25% → 60%

- [ ] **Environmental impact not reported** — Carbon footprint unknown
  - Impact: Minor weakness
  - Evidence needed: GPU-hours + CO2e estimate
  - Fix: Add carbon estimate
  - Post-fix acceptance: 30% → 65%

---

## 8. Benchmark Weaknesses (Reviewer Will Find)

- [ ] **No standard benchmarks** — Synthetic data only
  - Impact: Major weakness
  - Evidence needed: Standard benchmarks where applicable
  - Fix: Add standard benchmarks
  - Post-fix acceptance: 20% → 60%

- [ ] **No held-out test set** — Train/test contamination
  - Impact: Reject
  - Evidence needed: Temporal or random split
  - Fix: Implement held-out split
  - Post-fix acceptance: 10% → 65%

- [ ] **No data leakage check** — Test data in training
  - Impact: Reject
  - Evidence needed: Leakage check script
  - Fix: Add leakage_check.py
  - Post-fix acceptance: 15% → 65%

- [ ] **No adversarial evaluation** — Only average-case tested
  - Impact: Minor weakness
  - Evidence needed: Adversarial test suite
  - Fix: Add adversarial tests
  - Post-fix acceptance: 25% → 60%

---

## 9. Experimental Leaks (Reviewer Will Find)

- [ ] **Data leakage** — Test set in training
  - Impact: Reject
  - Evidence needed: Leakage check passes
  - Fix: Implement and verify
  - Post-fix acceptance: 5% → 65%

- [ ] **Hyperparameter tuning on test set** — Post-hoc tuning
  - Impact: Reject
  - Evidence needed: Validation set, test set untouched
  - Fix: Implement proper split
  - Post-fix acceptance: 10% → 60%

- [ ] **Seed shopping** — Try many seeds, report best
  - Impact: Reject
  - Evidence needed: Pre-registered seeds
  - Fix: Pre-register seeds
  - Post-fix acceptance: 15% → 65%

- [ ] **Condition leakage** — Treatment info in control
  - Impact: Reject
  - Evidence needed: Blinded analysis
  - Fix: Blind analysis
  - Post-fix acceptance: 15% → 60%

- [ ] **Temporal leakage** — Future info in past
  - Impact: Reject
  - Evidence needed: Causal ordering preserved
  - Fix: Verify causal ordering
  - Post-fix acceptance: 10% → 60%

---

## 10. Hidden Assumptions (Reviewer Will Find)

- [ ] **Stationarity assumed but not tested** — Environment is i.i.d.
  - Impact: Major weakness
  - Evidence needed: Stationarity test
  - Fix: Add stationarity check
  - Post-fix acceptance: 20% → 60%

- [ ] **Linearity assumed in control** — C1 linear, but env nonlinear
  - Impact: Major weakness
  - Evidence needed: Verify C1 cannot recover latent
  - Fix: Add linear probe test
  - Post-fix acceptance: 15% → 65%

- [ ] **Capacity bound assumed** — Max capacity is enough
  - Impact: Major weakness
  - Evidence needed: Capacity sweep
  - Fix: Add capacity sensitivity
  - Post-fix acceptance: 20% → 60%

- [ ] **MDL penalty assumed** — λ_model value is correct
  - Impact: Major weakness
  - Evidence needed: λ_model sensitivity
  - Fix: Add sensitivity analysis
  - Post-fix acceptance: 20% → 65%

- [ ] **Number of latent states assumed** — K is known
  - Impact: Major weakness
  - Evidence needed: K sensitivity
  - Fix: Add K sweep
  - Post-fix acceptance: 20% → 65%

---

## 11. Novelty Threats (Reviewer Will Claim)

- [ ] **Prior work does the same thing** — H* already shown
  - Impact: Reject (no novelty)
  - Evidence needed: Precise novelty statement
  - Fix: Distinguish from prior work
  - Post-fix acceptance: 15% → 60%

- [ ] **Standard method claimed as novel** — Just MDL + SSL
  - Impact: Reject (novelty inflation)
  - Evidence needed: What's new beyond combination
  - Fix: Identify specific novel contribution
  - Post-fix acceptance: 20% → 60%

- [ ] **No empirical comparison to prior** — "First" but not compared
  - Impact: Major weakness
  - Evidence needed: Direct comparison
  - Fix: Implement and run prior methods
  - Post-fix acceptance: 15% → 60%

- [ ] **Negative results from prior ignored** — Prior work shows it fails
  - Impact: Major weakness
  - Evidence needed: Cite and address
  - Fix: Add discussion of prior failures
  - Post-fix acceptance: 25% → 60%

---

## 12. Reviewer Objections (Pre-empt)

- [ ] **"This is just MDL with a new name"**
  - Impact: Major weakness
  - Evidence needed: What's different from standard MDL
  - Fix: Emphasize null-referenced emergence statistic; pre-registration; controls
  - Post-fix acceptance: 25% → 60%

- [ ] **"The effect size is too small to be meaningful"**
  - Impact: Major weakness
  - Evidence needed: Effect size with CI
  - Fix: Report effect sizes prominently; discuss practical significance
  - Post-fix acceptance: 20% → 60%

- [ ] **"This only works on synthetic data"**
  - Impact: Major weakness
  - Evidence needed: Real-world evidence or clear path
  - Fix: Acknowledge limitation; outline real-world path
  - Post-fix acceptance: 25% → 55%

- [ ] **"The baselines are too weak"**
  - Impact: Major weakness
  - Evidence needed: SOTA baselines
  - Fix: Implement and run SOTA
  - Post-fix acceptance: 15% → 60%

- [ ] **"The claims are not supported by the evidence"**
  - Impact: Major weakness
  - Evidence needed: Direct evidence for each claim
  - Fix: Add evidence; reduce claim strength
  - Post-fix acceptance: 20% → 60%

- [ ] **"The write-up is unclear"**
  - Impact: Major weakness
  - Evidence needed: Clear, concrete language
  - Fix: Revise for clarity; add diagrams
  - Post-fix acceptance: 30% → 70%

- [ ] **"The contribution is too narrow"**
  - Impact: Minor weakness
  - Evidence needed: Broader impact
  - Fix: Emphasize broader implications
  - Post-fix acceptance: 30% → 60%

- [ ] **"The contribution is too broad"**
  - Impact: Minor weakness
  - Evidence needed: Focused claims
  - Fix: Narrow claims; add qualifiers
  - Post-fix acceptance: 30% → 60%

---

## 13. Grant Weaknesses (NSF Specific)

- [ ] **"The PI lacks expertise"**
  - Impact: Major weakness
  - Evidence needed: PI bio + relevant publications
  - Fix: Add PI bio; cite relevant work
  - Post-fix acceptance: 20% → 55%

- [ ] **"The team is too small"**
  - Impact: Major weakness
  - Evidence needed: Justified team size
  - Fix: Justify team; add collaborators
  - Post-fix acceptance: 25% → 55%

- [ ] **"The budget is too high/low"**
  - Impact: Major weakness
  - Evidence needed: Justified budget
  - Fix: Detail budget justification
  - Post-fix acceptance: 25% → 55%

- [ ] **"The timeline is unrealistic"**
  - Impact: Major weakness
  - Evidence needed: Realistic timeline
  - Fix: Add buffer; risk mitigation
  - Post-fix acceptance: 25% → 55%

- [ ] **"No risk mitigation"**
  - Impact: Major weakness
  - Evidence needed: Alternative paths
  - Fix: Add risk mitigation section
  - Post-fix acceptance: 20% → 55%

---

## 14. Publication Blockers (Combined)

### 14.1 Auto-Reject (Any one fails)
- [ ] No pre-registration
- [ ] Designer injection detected
- [ ] No null reference for emergence
- [ ] Kill criteria not evaluated
- [ ] <5 seeds
- [ ] No effect sizes with CI
- [ ] Code/data not available
- [ ] Anthropomorphic language in main claims
- [ ] Unsupported neuroscience

### 14.2 Major Weakness (≥3 fails)
- [ ] Missing key literature
- [ ] Weak baselines
- [ ] No ablation
- [ ] No sensitivity analysis
- [ ] No assumption checks
- [ ] No power analysis
- [ ] Hype/unsupported claims
- [ ] No reproducibility package
- [ ] No DMP (NSF)

### 14.3 Minor Weakness (≥5 fails)
- [ ] No Dockerfile
- [ ] No pinned versions
- [ ] No runtime estimates
- [ ] No environment.txt
- [ ] No manifest.json
- [ ] No CITATION.cff
- [ ] No Zenodo DOI
- [ ] No broader impacts
- [ ] No dual-use assessment

---

## 15. Engineering Risks (Reviewer May Note)

- [ ] **Single-machine dependency** — Only tested on one GPU type
  - Impact: Minor weakness
  - Evidence needed: Cross-machine test
  - Fix: Test on 2+ GPU types
  - Post-fix acceptance: 30% → 65%

- [ ] **Memory leak in long runs** — May fail on large datasets
  - Impact: Minor weakness
  - Evidence needed: Memory profiling
  - Fix: Add memory tests
  - Post-fix acceptance: 30% → 60%

- [ ] **No CI/CD** — Code may rot
  - Impact: Minor weakness
  - Evidence needed: CI badges
  - Fix: Add GitHub Actions
  - Post-fix acceptance: 35% → 65%

- [ ] **No version pinning** — May break with updates
  - Impact: Minor weakness
  - Evidence needed: Pinned versions
  - Fix: Pin all versions
  - Post-fix acceptance: 30% → 65%

- [ ] **No tests** — Code may be buggy
  - Impact: Major weakness
  - Evidence needed: Test coverage
  - Fix: Add unit + integration tests
  - Post-fix acceptance: 20% → 60%

---

## 16. Final Assessment

**Pre-submission score:** ___% (items passing)

| Score | Verdict | Action |
|-------|---------|--------|
| 95–100% | Ready to submit | Submit |
| 85–94% | Minor revisions | Fix in 1 week |
| 70–84% | Major revisions | Fix in 1 month |
| 50–69% | Reject at this time | Fix in 3 months |
| <50% | Do not submit | Major rework |

**Estimated acceptance probability:**
- Current: ___%
- Post-fix: ___%

**Top 3 issues to fix before submission:**
1. _______________
2. _______________
3. _______________

---

**Checklist Version:** 1.0
**Last Updated:** 2026-07-03
**Method:** Reviewer #2 simulation (find fatal flaws)
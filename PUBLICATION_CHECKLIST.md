# VELYNX Publication Checklist

**Target Venues**: NeurIPS 2026 (main track), ICML 2026, Nature Machine Intelligence, Cognitive Science  
**Manuscript Type**: Full paper (12+ pages) + Supplementary Materials  
**Submission Deadline**: Target NeurIPS 2026 deadline (May 2026)  
**Status**: Pre-submission audit — all items must be GREEN before submission

---

## 1. Scientific Validity & Novelty Claims

| Item | Status | Evidence Location | Reviewer #2 Risk |
|------|--------|-------------------|------------------|
| **C1–C3**: Predictive Processing loop with surprise-driven learning | 🟢 Verified | `cognitive_core.py:162-371`, `cognitive_core.py:1219-1400` | Low — well-established framework |
| **C2**: Explainable predictions via causal rationale ("observed X→Y N times") | 🟢 Verified | `cognitive_core.py:484-500`, `cognitive_core.py:874-889` | Low — explicit rationale strings |
| **C3**: Causal hypothesis generation on prediction failure | 🟢 Verified | `cognitive_core.py:1305-1397` | Medium — needs ablation showing utility |
| **C4**: Concept birth via predictive entropy reduction (MDL) | 🟢 Verified | `concept_birth.py:257-398`, `concept_birth.py:318-398` | High — must compare to baselines (K-means, DP-GMM) |
| **C6**: Stable Belief Revision (Inertia Law + Exception Quarantine) | 🟢 Verified | `cognitive_core.py:670-1104`, `cognitive_core.py:924-980` | **Critical** — must demonstrate catastrophic forgetting cure vs Dirichlet baseline |
| **C7**: Sensorium — continuous vector world + latent cause discovery | 🟢 Verified | `environment.py`, `latent_cause_engine.py`, `cognitive_core.py:1708-2210` | High — no labels ever seen by brain; must prove rediscovery |
| **Closed-loop C7**: Discovery → attention reweighting → improved prediction | 🟢 Verified | `cognitive_core.py:2010-2022` | **Critical** — must show closed-loop benefit |

**Severity**: C6 catastrophic forgetting cure and C7 closed-loop discovery are the two highest-rejection-risk claims. Both require controlled ablations with statistical evidence.

---

## 2. Experimental Evidence & Statistics

| Requirement | Status | Location / Required Action |
|-------------|--------|----------------------------|
| Controlled ablations for each milestone (C1–C7) | 🟡 Partial | `benchmark_v2_results.json` shows Q1–Q10 pass but **no ablation table**; need controlled experiments isolating C6 Inertia Law, C4 MDL birth, C7 closed loop |
| Statistical significance (p-values, confidence intervals) | 🔴 Missing | No statistical tests in codebase. Must add: bootstrap CIs, permutation tests, or Bayesian credible intervals for all key claims |
| Multiple random seeds (≥10) for stochastic components | 🟡 Partial | `environment.py` and `latent_cause_engine.py` accept seeds; runner supports config. Need systematic multi-seed runs |
| Effect sizes reported (Cohen's d, Cliff's delta) | 🔴 Missing | Not implemented |
| Baselines: Dirichlet-Markov (C1–C3), k-means, DP-GMM, VAEs | 🔴 Missing | Only internal benchmarks exist (`benchmark_v2_results.json`). Must implement standard baselines |
| Sample sizes justified (power analysis) | 🔴 Missing | No power analysis documented |
| Reproducibility: fixed seeds, environment pinned | 🟢 Verified | `environment.py:119`, `latent_cause_engine.py` use `random.Random(seed)`; runner resets dataset |

**Action Required**: Implement `validation/ablation_runner.py` with multi-seed, multi-baseline, statistical testing.

---

## 3. Related Work Coverage

| Domain | Coverage Status | Key Citations Needed |
|--------|----------------|----------------------|
| Predictive Processing / Free Energy Principle | 🟡 Partial | Friston 2010, 2017; Clark 2013; Hohwy 2013 |
| Active Inference | 🟡 Partial | Friston et al. 2017; Parr et al. 2022 |
| Catastrophic Forgetting / Continual Learning | 🔴 Missing | Kirkpatrick et al. 2017 (EWC); Lopez-Paz & Ranzato 2017; Chaudhry et al. 2019 |
| Concept Formation / Category Learning | 🔴 Missing | Rosch 1978; Murphy 2002; Lake et al. 2015 (BPL) |
| Minimum Description Length in cognition | 🟡 Partial | Grünwald 2007; Chater & Vitányi 2003 |
| Latent Cause Inference / Structure Learning | 🔴 Missing | Gershman et al. 2010, 2015; Tomov et al. 2018 |
| Vector-based / Continuous cognition | 🔴 Missing | Eliasmith 2013 (SPA); Plate 2003 (HRR); Gayler 2003 |
| Cognitive architectures (ACT-R, Soar, CLARION) | 🔴 Missing | Anderson 2007; Laird 2012; Sun 2006 |

**Action Required**: Complete RELATED_WORK.md with systematic literature mapping before submission.

---

## 4. Reproducibility & Artifacts

| Artifact | Status | Location |
|----------|--------|----------|
| Complete source code | 🟢 Available | Repository root (29.8K LOC Python) |
| Environment specification (requirements.txt / pyproject.toml) | 🔴 Missing | No dependency file found |
| Docker / container specification | 🔴 Missing | Not present |
| Experiment runner (single command) | 🟢 Available | `validation/runner.py` — needs CLI wrapper |
| Pre-computed results / logs | 🟡 Partial | `benchmark_v2_results.json` only |
| Random seeds documented & configurable | 🟢 Verified | All stochastic components accept `seed` |
| Hardware requirements documented | 🔴 Missing | CPU-only (pure Python); no GPU deps |

**Critical Gap**: No `requirements.txt`, `pyproject.toml`, or `environment.yml`. Reviewers will reject for non-reproducibility.

---

## 5. Writing & Presentation

| Section | Target Length | Status |
|---------|---------------|--------|
| Abstract | 150–250 words | 🔴 Not written |
| Introduction | 1.5–2 pages | 🔴 Not written |
| Related Work | 1–1.5 pages | 🔴 Not written (see RELATED_WORK.md) |
| Methods (C1–C7) | 4–5 pages | 🟡 Code exists; prose needed |
| Experiments | 3–4 pages | 🔴 No controlled experiments yet |
| Ablation Studies | 1–2 pages | 🔴 Missing |
| Discussion / Limitations | 1 page | 🔴 Not written |
| Supplementary Materials | Unlimited | 🟡 Code serves as supplement |

**Figures Required** (minimum):
1. Architecture diagram (C1–C7 pipeline)
2. C6: Catastrophic forgetting comparison (Dirichlet vs StableBelief)
3. C4: Concept birth entropy curves (H_before vs H_after)
4. C7: Sensorium regime rediscovery (confusion matrix vs ground truth)
5. Closed-loop: Prediction error over time with/without discovery
6. Ablation bar charts with error bars

---

## 6. Governance & Compliance

| Document | Status | Notes |
|----------|--------|-------|
| CONSTITUTION_COMPLIANCE.md | 🟡 In progress | This audit |
| DATA_MANAGEMENT_PLAN.md | 🔴 Missing | Required for federal funding |
| REPRODUCIBILITY_CHECKLIST.md | 🔴 Missing | Required for ML reproducibility checklist |
| REVIEWER_OBJECTIONS.md | 🔴 Missing | Pre-mortem for Reviewer #2 |
| GRANT_PACKAGE.md | 🔴 Missing | For NSF/NIH/ERC applications |

---

## 7. Submission Readiness Gate

**All items must be GREEN before submission:**

- [ ] All 7 milestones have controlled ablation experiments with statistics
- [ ] Related work comprehensively mapped (RELATED_WORK.md complete)
- [ ] Reviewer objections pre-empted (REVIEWER_OBJECTIONS.md complete)
- [ ] Reproducibility package: requirements.txt, Dockerfile, single-command runner
- [ ] All figures generated programmatically from experimental logs
- [ ] Supplementary materials uploaded (code + data + logs)
- [ ] Ethics / broader impact statement (if venue requires)
- [ ] Author contribution statement
- [ ] Conflict of interest declaration

---

**Next Action**: Execute ablation study suite (C6 forgetting cure, C4 MDL birth, C7 closed loop) with ≥10 seeds, statistical testing, and baseline comparisons. Then complete all governance documents.
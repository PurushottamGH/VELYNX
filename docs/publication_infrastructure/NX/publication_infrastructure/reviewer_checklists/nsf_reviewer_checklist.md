# NSF Reviewer Checklist — Program D Compliance

**Proposal Target:** NSF (CISE/IIS/ROBO/ECCS — select appropriate program)
**Program:** D (Error-Gated Structure Acquisition / Calibration / Affective Indexing)
**Status:** Pre-submission Audit

---

## 1. NSF Merit Review Criteria

### 1.1 Intellectual Merit
- [ ] **Advances knowledge** — H*: First null-referenced emergence statistic discriminating error-gated growth from injection
- [ ] **Creative/original** — MDL growth operator + Dirichlet-Markov predictor + null-referenced M(θₖ) as integrated system
- [ ] **Well-conceived** — Constitution enforces falsifiability, kill criteria, no injection, no anthropomorphism
- [ ] **Qualified personnel** — PI + Research Engineering Lead documented in `repository_v2.md`
- [ ] **Adequate resources** — Compute budget, repository infrastructure, experiment pipeline documented

### 1.2 Broader Impacts
- [ ] **Societal benefit** — Honest uncertainty (AI safety), affective indexing (accessible AI), emergence measurement (AGI governance)
- [ ] **Underrepresented groups** — Plan for broadening participation documented
- [ ] **Education/outreach** — Curriculum integration, open-source artifacts, tutorials planned
- [ ] **Infrastructure** — `core/` primitives as reusable scientific infrastructure for community

---

## 2. NSF-Specific Requirements

### 2.1 Project Description (15 pages)
- [ ] **Results from prior NSF support** — If applicable, documented with publications
- [ ] **Preliminary data** — E0 pilot, EXP-0 results, EXP-1 calibration curves
- [ ] **Research plan** — Years 1–3 mapped to E0, EXP-1, EXP-2, EXP-3, E0 replication, extension
- [ ] **Risk mitigation** — Kill criteria as progressions criteria as decision points; alternative paths if H* falsified
- [ ] **Timeline with milestones** — Gantt chart aligned with experiment protocols

### 2.2 Data Management Plan (DMP) — 2 pages
- [ ] **Data types** — Synthetic streams, query logs, task scores, model checkpoints, analysis outputs
- [ ] **Standards** — CSV/JSON/Parquet for tabular; ONNX/HF for models; Markdown for docs
- [ ] **Access** — Zenodo for artifacts; GitHub for code; OSF for preregistrations
- [ ] **Preservation** — 10-year retention; institutional repository backup
- [ ] **Licensing** — Code: MIT/Apache-2.0; Data: CC-BY-4.0
- [ ] **Privacy** — No PII; synthetic data only

### 2.3 Postdoctoral Mentoring Plan (if applicable) — 1 page
- [ ] **Mentoring activities** — Research, writing, presentations, career development
- [ ] **Individual development plan** — Template included

### 2.4 Collaborators & Other Affiliations (COA)
- [ ] **Complete list** — All co-authors, collaborators, advisors, advisees last 48 months

### 2.5 Facilities, Equipment & Other Resources
- [ ] **Compute** — GPU cluster access documented (type, hours/year)
- [ ] **Storage** — TB for artifacts, datasets, checkpoints
- [ ] **Software** — Repository infrastructure, CI/CD, container registry

---

## 3. Program D Compliance for NSF

### 3.1 Falsifiability as Rigor (Constitution §2, §4)
- [ ] **Hypotheses as testable predictions** — Not "research questions"
- [ ] **Kill criteria as go/no-go milestones** — K1–K10 with pass/fail logic
- [ ] **Negative results as valid outcomes** — Falsification of H* is a publishable result

### 3.2 No Designer Injection (Constitution §2.5)
- [ ] **E0: Zero seeded concepts** — Only error-gated growth
- [ ] **Emergence statistic null-referenced** — M(θₖ) - E[M|H₀] via C3
- [ ] **MDL trigger only growth signal** — No heuristic growth triggers

### 3.3 Reproducibility as Infrastructure
- [ ] **`core/` as reusable primitives** — Dirichlet-Markov, MDL growth, emergence statistic, controls
- [ ] **Experiment pipeline** — Self-contained, frozen code, pre-registered
- [ ] **Artifact packaging** — Zenodo deposits with DOIs for each experiment

---

## 4. NSF Program-Specific Alignment

### 4.1 IIS (Information & Intelligent Systems)
- [ ] **Machine learning theory** — MDL growth, proper scoring, emergence measurement
- [ ] **AI safety/robustness** — Calibration (H1), honest uncertainty
- [ ] **Human-AI interaction** — Affective indexing (H2) as retrieval key

### 4.2 ROBO (Robotics)
- [ ] **Developmental robotics** — H3: emergent development via sensorimotor prediction
- [ ] **Embodied cognition** — Predictive organism as minimal agent

### 4.3 ECCS (Engineering)
- [ ] **Cyber-physical systems** — Calibration for safety-critical deployment
- [ ] **Real-time systems** — Predictive organism with bounded compute

### 4.4 CISE Cross-Cutting
- [ ] **Reproducibility infrastructure** — `core/`, `benchmarks/`, `experiments/` as cyberinfrastructure
- [ ] **Open science** — Pre-registration, open code/data, kill criteria transparency

---

## 5. Budget Justification

### 5.1 Personnel
- [ ] **PI** — X months/year for scientific direction, writing, review
- [ ] **Research Engineering Lead** — 12 months/year for `core/`, `experiments/`, infrastructure
- [ ] **Graduate students** — N (if applicable) for experiment execution, analysis
- [ ] **Postdoc** — For theory/analysis of emergence statistic, novelty analysis

### 5.2 Equipment
- [ ] **GPU compute** — $X/year (cloud or cluster allocation)
- [ ] **Storage** — $X/year for artifacts, checkpoints, datasets

### 5.3 Travel
- [ ] **Conferences** — NeurIPS, ICML, ICLR, Nature MI, domain-specific (CogSci, DevRob)
- [ ] **Workshops** — Reproducibility, emergence, calibration

### 5.4 Participant Support (if applicable)
- [ ] **REU students** — Summer research on benchmarks, reproducibility

### 5.5 Other Direct Costs
- [ ] **Publication fees** — Open access for 3–5 papers
- [ ] **Zenodo/OSF** — Minimal (free tiers sufficient)
- [ ] **Software licenses** — None (all open source)

---

## 6. NSF Publication Blockers

### 6.1 Must-Resolve Before Submission
- [ ] **E0 preregistration live on OSF** — URL in proposal
- [ ] **E0 kill criteria evaluated** — Documented in `kill_criteria_validation_report.md`
- [ ] **Emergence statistic M(θₖ) implemented** — `core/emergence/emergence_statistic.py`
- [ ] **C3 shuffled control implemented** — `core/controls/shuffled_input.py`
- [ ] **Preliminary data for H*, H1, H2, H3** — At least pilot results
- [ ] **All foundation documents complete** — 22 files in `foundation/`
- [ ] **DMP completed** — 2 pages, compliant with NSF 22-1
- [ ] **Postdoc mentoring plan** — If postdoc budgeted
- [ ] **COA complete** — All collaborators listed
- [ ] **Current & Pending Support** — All PI/co-PI grants listed

### 6.2 Documentation Artifacts
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

## 7. Acceptance Probability Assessment (NSF)

| Criterion | Weight | Score (1-5) | Weighted |
|-----------|--------|-------------|----------|
| **Intellectual Merit** | 0.50 | ___ | ___ |
| **Broader Impacts** | 0.30 | ___ | ___ |
| **Feasibility/Resources** | 0.10 | ___ | ___ |
| **PI Qualifications** | 0.10 | ___ | ___ |
| **Total** | **1.00** | | **___** |

**NSF Thresholds (varies by program):**
- **≥ 4.0**: Fundable (top 15–20%)
- **3.5–3.9**: Fundable if budget allows
- **3.0–3.4**: Revise and resubmit
- **< 3.0**: Do not fund

**Automatic "Do Not Fund" Triggers:**
- [ ] No pre-registration for primary hypothesis
- [ ] Kill criteria not evaluated / no decision points
- [ ] Designer injection in core mechanism
- [ ] No preliminary data for central hypothesis
- [ ] DMP missing or non-compliant
- [ ] Broader impacts generic/boilerplate
- [ ] Budget not justified by scope

---

**Auditor:** _________________________
**Date:** _________________________
**Next Review:** _________________________
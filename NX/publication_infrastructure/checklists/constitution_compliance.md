# Constitution Compliance Checklist — Program D

**Purpose:** Verify that all publication artifacts comply with Program D Constitution.
**Authority:** `PROGRAM_D_CONSTITUTION.md` (absolute)
**Status:** Required for all publications

---

## 1. Prime Directive (Constitution §1)

> Program D optimizes for truth, not elegance, and not survival of the program.

- [ ] Every claim traces to a source (FACT, HYPOTHESIS, or REJECTED with evidence)
- [ ] Every confidence tier matches its empirical likelihood
- [ ] System says "I don't know" when evidence is lacking
- [ ] No DEBATED or UNKNOWN presented as CERTAIN
- [ ] No claim protected for program survival (kill criteria can be triggered)

---

## 2. Scientific Vigilance (Constitution §2)

### 2.1 Unsupported Assumptions
- [ ] All assumptions documented in `foundation/assumptions/assumption_ledger.md`
- [ ] Only I1, I2, I3 are load-bearing (rest are derived or tested)
- [ ] Each assumption has evidence or is marked for testing
- [ ] No hidden assumptions in code or paper

### 2.2 Circular Logic
- [ ] Hypotheses do not assume their own truth
- [ ] Evidence does not assume hypothesis
- [ ] Emergence statistic M(θₖ) is not defined to favor the hypothesis
- [ ] No tautological reasoning in proofs

### 2.3 Hidden Assumptions
- [ ] All hyperparameters justified (not just tuned)
- [ ] All architecture choices justified
- [ ] All data preprocessing justified
- [ ] All evaluation choices justified
- [ ] No "obviously" without justification

### 2.4 Anthropomorphic Language
- [ ] No "mind", "soul", "understanding" without operationalization
- [ ] No "belief", "intention", "awareness", "consciousness" without operationalization
- [ ] No "thinks", "knows", "feels" without operationalization
- [ ] All replaced with: "predictive organism", "structure acquisition", "model", "predicts", "estimates", "indexes"
- [ ] Grep test: `rg "\b(mind|soul|understand|belief|intention|awareness|conscious)\b" --type md` returns 0 matches in main claims

### 2.5 Designer Injection
- [ ] E0 uses zero seeded concepts
- [ ] No hand-authored ontology grounds meaning
- [ ] No "free energy" proxy incommensurate with physics
- [ ] No 32 hand-authored concepts claiming affective topology
- [ ] Emergence statistic references shuffled-input control (not just absolute NMI)

### 2.6 Novelty Inflation
- [ ] No claim of novelty for standard SSL/MDL methods
- [ ] "First to" claims specify conditions
- [ ] Prior work with similar mechanisms cited
- [ ] Negative results from prior work cited

### 2.7 Unsupported Neuroscience
- [ ] No LTP/STDP claims unless implemented
- [ ] No hippocampal replay claims unless implemented
- [ ] No synaptic plasticity claims unless implemented
- [ ] Mechanism names match implementation (or implementation matches mechanism)
- [ ] Grep test: `rg "LTP|STDP|synaptic plasticity|hippocampal" --type md` returns 0 matches without implementation reference

### 2.8 Unsupported Cognitive Claims
- [ ] No "consciousness" claims
- [ ] No "intelligence" claims without definition
- [ ] No "understanding" claims without test
- [ ] No "cognition" claims without operationalization
- [ ] All replaced with specific, measurable mechanisms

---

## 3. Epistemic Classification (Constitution §3)

### 3.1 Tagging Requirements
Every statement in `foundation/` must carry one of:
- [ ] **[FACT]** — Measured, verified, or definitional
- [ ] **[HYPOTHESIS]** — Falsifiable, testable
- [ ] **[SPECULATION]** — Asserted without measurement
- [ ] **[REJECTED]** — Falsified or discarded

### 3.2 Tag Distribution Check
- [ ] Grep test: `rg "\*\*\[FACT\]\*\*" foundation/ -c` reports count
- [ ] Grep test: `rg "\*\*\[HYPOTHESIS\]\*\*" foundation/ -c` reports count
- [ ] Grep test: `rg "\*\*\[SPECULATION\]\*\*" foundation/ -c` reports count
- [ ] Grep test: `rg "\*\*\[REJECTED\]\*\*" foundation/ -c` reports count
- [ ] Distribution reviewed: SPECULATION should be small (slated for testing/removal)
- [ ] REJECTED should not appear in load-bearing mechanisms

### 3.3 Paper-Level Tagging
- [ ] Main paper claims are either FACT or HYPOTHESIS (not SPECULATION)
- [ ] SPECULATION is moved to supplementary or future work
- [ ] REJECTED claims are not presented as current truth

---

## 4. Burden of Proof (Constitution §4)

### 4.1 No New Hypotheses
- [ ] All hypotheses trace to `HYPOTHESIS_REGISTER.md`
- [ ] No new hypotheses invented in papers
- [ ] Refinements are marked as such, not as new claims
- [ ] Grep test: All "H*" references in papers trace to `HYPOTHESIS_REGISTER.md`

### 4.2 No Subsystem Without Pre-Registered Experiment
- [ ] Every mechanism has a pre-registered experiment
- [ ] Every experiment tests exactly one hypothesis
- [ ] No "engineering" features without scientific justification
- [ ] No "decorative" code without experiment

### 4.3 Distinguishable from Null Baseline
- [ ] Every mechanism has a null baseline (random, constant, fixed-capacity, etc.)
- [ ] Kill criteria include "indistinguishable from null" check
- [ ] If mechanism fails null test, it is a delete candidate
- [ ] No mechanism is a "feature" without evidence

---

## 5. Terminology Compliance (TERMINOLOGY.md)

### 5.1 Required Term Usage
- [ ] "Program A" — Live-truth retrieval
- [ ] "Program B" — Soul Graph
- [ ] "Program C" — Symbolic cognitive stack
- [ ] "Program D" — Audit and falsification protocol
- [ ] "Capacity Growth (g)" — Used for parameter addition
- [ ] "MDL Trigger (G)" — Used for growth threshold
- [ ] "Log-Loss (L)" — Used for proper scoring
- [ ] "Emergence Statistic (M(θₖ))" — Used for NMI-based statistic
- [ ] "Calibration" — Used for ECE-based metric
- [ ] "Affective Indexing" — Used for emotion→schema retrieval
- [ ] "Predictive Organism" — Used for the system
- [ ] "Structure Acquisition" — Used for learning

### 5.2 Deprecated Term Absence
- [ ] No "Free Energy" (as used in Program C)
- [ ] No "Resonance"
- [ ] No "Sleep/Replay" (unless actually implemented as such)
- [ ] No "Thermodynamic State"
- [ ] No "Mind" / "Soul" / "Understanding" (without operationalization)
- [ ] Grep test: `rg "\b(free energy|resonance|sleep/replay|thermodynamic)\b" --type md` returns 0 matches without operationalization

---

## 6. Repository Compliance (repository_v2.md)

- [ ] `foundation/` directory contains 22 files
- [ ] `core/` directory contains 12 primitive files
- [ ] `experiments/` directory has one subdirectory per experiment
- [ ] `benchmarks/` directory consolidated
- [ ] `program_a/`, `program_b/`, `program_c/` separated
- [ ] `infra/` separated from science
- [ ] `docs/`, `artifacts/`, `archive/` in correct locations
- [ ] No `backend/`, `velynx_core/`, `validation/` (archived)

---

## 7. Migration Compliance (migration_plan.md)

- [ ] Migration phases 0–11 completed
- [ ] All shims removed
- [ ] Import paths updated to new structure
- [ ] `pyproject.toml` exists
- [ ] Tests consolidated in `tests/`
- [ ] All archives preserved
- [ ] Git history preserved (`git log --follow` works)

---

## 8. Implementation Compliance (implementation_checklist_v1.md)

- [ ] All 28 commits completed
- [ ] Each commit has pre-commit verification
- [ ] Each commit has post-commit tests passing
- [ ] High-risk commits (9.1) have pre/post hooks
- [ ] No shim remains in final state

---

## 9. Per-Experiment Constitution Compliance

### 9.1 E0
- [ ] H* hypothesis traces to `HYPOTHESIS_REGISTER.md`
- [ ] Falsifiable with pre-registered kill criteria
- [ ] No seeded concepts
- [ ] C1, C2, C3 controls implemented
- [ ] M(θₖ) null-referenced
- [ ] No anthropomorphic language in E0 paper

### 9.2 EXP-1
- [ ] H1 hypothesis traces to `HYPOTHESIS_REGISTER.md`
- [ ] ECE < 0.1 with pre-registered kill criterion
- [ ] Better than constant baseline
- [ ] No CERTAIN on hallucination traps
- [ ] No anthropomorphic language in EXP-1 paper

### 9.3 EXP-2
- [ ] H2 hypothesis traces to `HYPOTHESIS_REGISTER.md`
- [ ] Objective task score (not subjective)
- [ ] Pre-registered kill criterion
- [ ] No re-authoring per task
- [ ] No anthropomorphic language in EXP-2 paper

### 9.4 EXP-3
- [ ] H3 hypothesis traces to `HYPOTHESIS_REGISTER.md`
- [ ] Transfer to held-out task
- [ ] No trivial structure (beyond init + input stats)
- [ ] No anthropomorphic language in EXP-3 paper

---

## 10. Audit Frequency

- [ ] **Weekly:** PI reviews all changes against checklist
- [ ] **Pre-submission:** Full audit per target venue
- [ ] **Post-submission:** Verify no reviewer objections violated Constitution
- [ ] **Quarterly:** Full Constitution compliance review

---

## 11. Violation Handling

If any item fails:
1. **STOP** — Do not submit paper
2. **Document** — Log violation in `docs/audits/constitution_violations.md`
3. **Fix** — Address violation
4. **Re-audit** — Run full checklist again
5. **Document fix** — Log fix in audit document

If violation cannot be fixed:
- [ ] **Withdraw paper** if violation is in main claims
- [ ] **Move to supplementary** if violation is in supporting text
- [ ] **Add caveat** if violation is unavoidable and disclosed

---

**Checklist Version:** 1.0
**Last Updated:** 2026-07-03
**Authority:** PROGRAM_D_CONSTITUTION.md
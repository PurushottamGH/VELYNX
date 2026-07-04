# PROGRAM D — RESEARCH STATE v0.1

**Status:** Canonical single source of truth. Supersedes scattered per-file notes for orientation purposes; the source files remain authoritative for detail.
**Consolidation date:** 2026-07-01 (session artifacts stamped 2026-07-01/02).
**Scope:** Consolidates every artifact produced in the 2026-07-01 analysis session (the "Program D analysis session," indexed in `README.md`). This document designs no new mechanism, writes no code, and extends nothing. It removes duplicates, resolves contradictions, and classifies every load-bearing statement.

**Epistemic tags used throughout:**
- **[FACT]** — measured, verified against source code or a mechanically-generated experiment artifact, or definitional.
- **[HYPOTHESIS]** — a falsifiable, testable claim not yet decided by evidence.
- **[SPECULATION]** — asserted without measurement or ground truth.

**Program taxonomy (fixed for this document):**
- **Program A** — Live-truth retrieval engine (the original Constitution: retrieve, score credibility, tier uncertainty).
- **Program B** — The "Soul Graph" (hand-authored affective concept graph + BFS "arcs" + living-edge plasticity).
- **Program C** — The symbolic-AGI cognitive stack (metacognition, beliefs, goals, agentic loop, self-model, ontology, concept-birth, predictive core; ~24–30k LOC).
- **Program D** — The go-forward program: the 2026-07-01 audit/reduction of the existing system **plus** the falsifiable experimental restatement that decides whether Program B/C science survives.

---

## 1. Executive Summary

Program D is not a new architecture. It is the disciplined audit that converts a large, mostly-asserted system (Programs A/B/C) into a small set of falsifiable questions and a reduction plan that preserves the ability to run experiments. Today's session produced: a Principal-Investigator review, an assumption ledger, an evidence database mapping claims to code, a mathematical ontology/provenance, a variable-dependency graph, a designer-injection audit, four code-health reviews, a kill-criteria audit, and reduction/migration/archive plans.

The central finding is consistent across every independent artifact: **the system's cognitive claims are, at present, asserted rather than demonstrated.** Three lines of evidence converge:

1. **[FACT] Empirical null result (R1 ablation, `ablation_report.md`).** Across 72 controlled experiments, the C8 free-energy consolidation policy is statistically indistinguishable from naive baselines on the only measurable primary metric: PredictionRMSE `free_energy = 0.2991` vs `null = 0.2951` (effect +0.0040, p = 0.866). The other **5 of 6 primary metrics were unmeasurable** — the system cannot currently measure its own claimed capabilities.
2. **[FACT] Pervasive designer injection (`designer_injection_report.md`).** Of ~150 constants governing the architecture, **zero are derived from data, first principles, or search**; behavior is ~95–100% determined by designer choices for "what the system wants," "how the world is perceived," and "which concepts exist."
3. **[FACT] The reduction analysis** shows the smallest organism reproducing the demonstrated behavior is "a 32-node graph with a keyword matcher and a string templater — roughly 300 lines," with the remaining ~29,700 LOC serving to make it *feel* like a mind (`docs/VELYNX_v2_PI_Review.md` Phase 2).

Consequences by program: **Program A** (retrieval) survives as an honest product, contingent on fixing calibration (currently **[CONTRADICTED]** — `CERTAIN` emitted on hallucinated content). **Program B** (Soul Graph) survives only as an authored artifact; its "arcs" are an ELIZA effect **[FACT]**, but one kernel (affective→strategic indexing) is a genuine untested **[HYPOTHESIS]**. **Program C** is engineering-retained (its subsystems are needed to *run* the current experiment suite) but scientifically unvalidated: its load-bearing assumptions are dominated by SPECULATION and CONTRADICTED ratings.

**Program D's operative hypothesis** is therefore the falsifiable restatement: *does any Program B/C mechanism produce measurable cognitive progress that (a) exceeds null/baseline models and (b) is not merely a readout of injected priors?* The highest-value next experiment (**EXP-0**, paraphrase the benchmark) can begin to answer this in ~1 day. Program D continues only while that question remains open and is answerable; the explicit termination conditions are in §10.

---

## 2. Decisions Made Today

### Accepted
- **[FACT]** Adopt the falsifiable framing: the "mind/development" thesis is restated as three testable hypotheses H1 (calibration), H2 (affective indexing), H3 (emergent development), each with success/failure/kill criteria (`VELYNX_v2_PI_Review.md` Phase 5).
- **[FACT]** Program A (calibrated live-truth retrieval) is the surviving product path.
- **[FACT]** Reduction plan: **23 subsystems classified REQUIRED/KEEP**; ~38% of files removable while preserving ~95% of experiments and 100% of the formal R1–R3F suite (`program_c_reduction_plan.md`, `program_c_archive_manifest.md`). *KEEP here means "needed to run current experiments," not "scientifically validated" — see §Contradictions Resolved.*
- **[FACT]** Free-energy coefficient duplication (`decision_policy.py` vs `validation/metrics.py`, λ=1.0/μ=2.0/ν=0.5) is a confirmed defect to consolidate to a single source.
- **[FACT]** `MERGE` recommended for 0 subsystems; consolidation is achieved by re-export facades, not code merges (`program_c_archive_manifest.md`).

### Rejected
- **[FACT]** "100/100 Live-Fire pass = the system works" — rejected as teaching-to-the-test on curated queries hitting seeded concepts (`VELYNX_v2_PI_Review.md` E1).
- **[FACT]** "The Gemini literature review grounds the design" — rejected; those files are task-assignment prompts to a coding agent, not a literature review (PI review E2).
- **[FACT]** The claim that the C8 free-energy decision machinery delivers measurable benefit — rejected by the R1 ablation (p = 0.866 vs null).
- **[FACT]** Treating the FEP energy `E = λH + μS + νA` as Friston variational free energy — rejected; it is explicitly an "arbitrary energy units" proxy mixing incommensurate units (`program_c_mathematical_ontology.md`).

### Archived
- **[FACT]** ~34 subsystems/packages marked ARCHIVE and ~8 marked DELETE (e.g., `velynx_core/` duplicate stack, `backend/agents/` dead stub, `orchestrator.py`/`brain.py`/`self_coder.py` legacy duplicates, `frontend/`, root diagnostic probes, `searxng/`, `kiro-gateway/`). Policy: **never delete, always archive** with restore notes (except third-party/JS toy code marked DELETE). (`program_c_archive_manifest.md`, `program_c_safe_removal_order.md`, `program_d_reduction_plan.md`.)
- **[FACT]** Kill criteria **K3, K4, K9** reclassified as decorative "Design Constraints/Risks" — they have no metric, no experiment, and no code (`foundation/kill_criteria_validation.md`).

### Unresolved
- **[HYPOTHESIS]** Whether any Program C subsystem beyond retrieval survives an honest experiment (EXP-0 unrun).
- **[HYPOTHESIS]** Whether the two concept-birth thresholds (0.5 bits root vs 0.15 backend) should unify, and to what value.
- **[SPECULATION→open]** Whether statically-flagged "dead" modules (`brain.py`, `self_coder.py`, `agents/`) are truly uncalled or reached via dynamic loading (confidence Low; grep may miss dynamic imports).
- **[HYPOTHESIS]** Whether `data/` state files are safe to archive because they "would be recreated on first run" (Confidence Medium, unverified).

---

## 3. Program A — Live-Truth Retrieval Engine

**Current status:** The only part rated FACT/EVIDENCE-SUPPORTED at the assumption level; retained as the honest product path.

- **[FACT]** A1: Answers can be traced to live sources with credibility scoring — standard IR/RAG, buildable.
- **[HYPOTHESIS]** A2: Calibrated uncertainty tiers (CERTAIN/PROBABLE/DEBATED/UNKNOWN) are achievable — calibration is a near-solved ML problem in principle.
- **[FACT — contradiction]** A3: VELYNX's tiers are *currently* calibrated — **CONTRADICTED**. `soul_test_report.md` Q6 shows `CERTAIN` on a hallucinated answer; tiers are assigned from concept-/hop-count heuristics never validated against ground-truth correctness.
- **[HYPOTHESIS/weak]** A4: "Learns from being wrong without retraining" — what exists is incrementing JSON confidence + appending regex rules (bookkeeping, not model improvement).

**Path forward (already decided):** finish Program A as a product; its real scientific contribution is **H1 — a retrieval agent whose tier correctness matches its tier (ECE < 0.1)**. Calibration must be made true (EXP-1) before it ships as "honest uncertainty."

---

## 4. Program B — The "Soul Graph"

**Current status:** An authored artifact presented as an emergent one. Engineering-retained (`backend/soul/` is REQUIRED to run current experiments) but scientifically archived except for one kernel.

- **[SPECULATION]** B1/B2: The 32 hand-authored affective concepts and their edge labels (`contrasts`, `catalyzes`, `diminishes`) capture real relations — no theory selects the 32, no ground truth, no inter-rater reliability.
- **[FACT]** B3: BFS "arcs" constitute reasoning — **CONTRADICTED**. Arcs are string concatenations of author-supplied edge labels; meaning is projected by the reader (ELIZA-class).
- **[FACT]** The living-edge plasticity is real and correctly typed: rate-based **Hebbian** coactivation (`soul_graph.py:512-596`) and a decay/prune **sleep cycle** (`soul_graph.py:602-654`), grounded in LTP (Bliss & Lømo 1973). *Known limitation:* no STDP/temporal ordering; weights can grow unbounded (`research/evidence_database.md`).
- **[HYPOTHESIS]** B4: The emotion→technical bridge (shame→failure→debugging) indexes useful strategy — currently a hardcoded ~15-entry dict, but the *idea* is the one novel seed (see §5, H2).

**What survives:** the affective-indexing hypothesis (H2) and the mechanically-correct Hebbian/sleep plasticity primitives.
**What is archived:** the arcs-as-reasoning claim and the coverage claim for the 32 concepts.

---

## 5. Program C — The Symbolic-AGI Cognitive Stack

### Current status
Large, competent-to-derivative symbolic scaffolding whose cognitive claims are unvalidated or contradicted. Engineering-retained to run experiments; scientifically on probation pending EXP-0.

**Load-bearing assumptions (from `program_c_assumption_ledger.md`, its own labels):**
- **[SPECULATION]** A-CA02: `E = λH + μS + νA` is a valid free-energy proxy.
- **[FACT — contradiction]** A-E01: Free-energy minimization improves prediction — **CONTRADICTED** by R1 (RMSE 0.2991 vs null 0.2951, p = 0.866).
- **[FACT — contradiction]** A-O02: DirichletMarkovModel ≈ StableBeliefModel interchangeable — **CONTRADICTED** (opposite learning-rate dynamics: surprise-amplified vs surprise-attenuated).
- **[FACT — contradiction]** A-O05/A-O07: hand-authored scaffolding constitutes development / hand-authored is-a trees ground meaning — **CONTRADICTED** (symbol grounding, Harnad 1990).
- **[SPECULATION]** A-CA01 ("lower is better for all vitals"), A-CA04 (half-maturity = 4.0, "arbitrary"), A-CA05 (EWMA alphas), A-CA06 (CPI weights 0.40/0.30/0.20/0.10), A-O01 ("concept" = string label), A-O04 (curiosity gaps = hand-authored ontology).
- **[HYPOTHESIS/weak]** A-O03 (fracture sufficient for regime detection), A-IT01 (conditional independence given order-k context), A-E02 (CPI measures genuine progress), A-S01 (spherical clusters — evidence-supported in toy env only).
- **[FACT/definitional]** A-IT02 (`0·log(0/q)=0`), A-N01 (Dirichlet positivity), A-N03 (ε = 1e-9).

### What survives (scientifically interesting)
- **[FACT]** Correctly-implemented, literature-grounded primitives: **Bayesian conjugate priors** (Dirichlet-Markov, Beta-Bernoulli living edges); **Bayesian surprise** `KL(Beta(1+s,1+f)‖Beta(1,1))` (Itti & Baldi 2006); **concept-birth MDL** compression gain `G = H_before − H_after`; standard **K-means/spectral clustering** and information theory.
- **[HYPOTHESIS]** Single-level predictive coding surprisal `I(s) = −log₂ P(s|c)` is accurate in the single-level sense (Rao & Ballard 1999) — but the hierarchy that would make it "predictive coding" is absent.
- **[HYPOTHESIS]** The mathematical ontology itself (a formalized variable/law inventory: stability law, Inertia Law `η_eff = η_base·(1−stability)`, fracture ratio, Schmitt-trigger consolidation hysteresis) is a genuine, reusable specification even if its parameters are unvalidated.

### What is archived
- **[FACT]** ARCHIVE: `velynx_core/` (fully duplicated by `backend/*`), `backend/{audio,testing,tools,contracts}`, legacy `orchestrator.py`/`brain.py`/`self_coder.py`, `cognitive_core.py`/`cognitive_health.py` proxies, CLI shims, `frontend/`, `configs/`, root diagnostic scripts. DELETE: `experiments/` toy scripts, `searxng/`, `kiro-gateway/`, JS build artifacts.
- **[FACT]** Metaphor-only mechanisms flagged as not-grounded: "resonance" (score propagation, not oscillatory synchrony), "sleep/replay" (sandbox merge sim, not pattern reactivation), "thermodynamic state" (annealing metaphor, no statistical-mechanics connection), synaptic "pruning" (weight-threshold only).
- **[FACT]** Absent entirely (per evidence DB): STDP, neuromodulation, LTP/LTD cellular mechanisms, cortical microcircuits, E/I balance, homeostatic plasticity, SNNs — "zero contact with neuroscience."

### What remains scientifically interesting
- **[HYPOTHESIS]** The concept-birth MDL ledger as an *emergence detector*: does structure appear that was not seeded? (Currently confounded by injected priors.)
- **[HYPOTHESIS]** The Inertia Law as a catastrophic-forgetting defense (K2 substrate exists; the *test* does not).
- **[HYPOTHESIS]** Whether the toy 4-regime environment's clustering generalizes beyond linearly-separable cube corners (A-E06).

---

## 6. Program D

### Current hypothesis
**[HYPOTHESIS]** *A Program B/C cognitive mechanism produces measurable cognitive progress that (a) exceeds null/baseline models and (b) is not merely a readout of injected designer priors.* This is the consolidation of PI-review H1/H2/H3 and the ablation research question; it is stated so it can fail. Present evidence leans against (b) (designer-injection audit) and against the free-energy instance of (a) (R1 null result).

Sub-hypotheses (falsifiable, from `VELYNX_v2_PI_Review.md` Phase 5):
- **H1 (Calibration).** A retrieval agent can report tiers whose empirical correctness matches the tier (ECE < 0.1).
- **H2 (Affective indexing).** A learned affective-framing → problem-solving-schema mapping improves objective task outcomes over an unframed baseline.
- **H3 (Emergent development).** An agent minimizing sensorimotor prediction error, adding capacity only on persistent error, spontaneously develops reusable structure absent at initialization.

### Independent variable
Program-level: the **presence/identity of the mechanism under test**, holding data, core, and measurement constant. Concrete instantiations already defined:
- **[FACT]** R1 (run): consolidation policy ∈ {null, random, fifo, similarity, utility, free_energy}; replay horizon ∈ {50, 200}; sensor noise σ ∈ {0.01, 0.15}; seed ∈ {1,2,3}.
- **[HYPOTHESIS]** EXP-0 (next): paraphrase present/absent (does a seeded-keyword substring appear?).
- **[HYPOTHESIS]** EXP-2/H2: affective frame present/absent. EXP-4: cross-channel coupling on/off.

### Dependent variable
- **[FACT]** R1 primary: **PredictionRMSE** (only measurable primary metric). Secondary: FinalEnergy, ReplayEfficiency, ClusterCount, Entropy, ActiveLoad, etc.
- **[HYPOTHESIS]** H1: Expected Calibration Error (ECE). H2: objective task score (e.g., debugging fixes / planning success). H3: transfer of emergent structure to a held-out prediction task. EXP-0: benchmark score under paraphrase.

### Assumptions
- **[FACT]** 20 registered design assumptions (`program_d_assumption_coverage_matrix.csv`): 16 ACCEPTED (traceable to `generate_graph.py` A1–A16), 4 UNVALIDATED (DualBrainCoherence, ParallelGraphDBConvergence, SelfCoderSandboxIsolationSufficient, CrossDomainBridgeSignalMapping). **Resolution:** "ACCEPTED" here means *formally registered/traceable*, not *empirically confirmed* — several ACCEPTED items (e.g., EnergyAsFreeEnergyProxy) are rated SPECULATION or CONTRADICTED in the assumption ledger. See §7 risk R-2.
- **[FACT]** Parameter provenance: ~31+ parameters, **0 fully derived, 9 hand-tuned, 22+ arbitrary**; only **7 variables experimentally validated** (E, CPI, ΔE/ΔS/ΔH/ΔA, E_before/after, stability, φ, η_eff via E5–E13).
- **[FACT]** ~150 architecture constants total, **zero data-derived** (`designer_injection_report.md`).

### Kill criteria
Ten defined (K1–K10, `foundation/kill_criteria_validation.md`). **[FACT] None is wired to an automated kill decision.** Summary:
- **Decorative (remove/reclassify): K3** ConstitutionViolation, **K4** NothingDevelopsPersists, **K9** FEPMisrepresentation — no metric, no experiment, no code.
- **Measurable but unwired: K1** CPIDeclining, **K5** SurprisePlateauUnresolved (detector exists, never halts), **K6** ExhaustionSustained (E ≥ 18.0 threshold classifies but doesn't escalate), **K7** FractureSupersaturation (0.85 trigger exists; cross-context ≥1.0 check missing), **K8** NoGenuineLearning, **K10** ProbationNeverConfirms (verdicts exist; all-rejected aggregate missing). **K2** CatastrophicForgettingPersists — partial.
- Program-level kill criterion (PI review): *EXP-0 collapses under paraphrase AND EXP-3 shows no emergent structure after two honest attempts* → the developmental thesis is dead. See §10.

### Null models
Already instantiated and available: **null, random, fifo, similarity, utility** consolidation policies (R1). Additional controls defined by hypothesis: **constant-confidence baseline** (H1), **no-frame baseline** (H2), **untrained-structure control** (H3), **lookup-table/paraphrase baseline** (EXP-0). **[FACT]** On the run null models, the treatment (free_energy) showed no significant advantage.

### Experiment roadmap
- **[FACT] Covered (13):** E1–E13 map every C1–C8 component to a mechanically-scored experiment (`program_d_experiment_coverage_matrix.csv`); R1–R3F formal suite intact.
- **[FACT] Uncovered (6):** ConceptBirthMDL, LatentCauseDiscovery, SoulGraphResonance, SelfModelIntrospection, CurriculumTeaching, RetrievalMesh.
- **[HYPOTHESIS] Ranked next experiments (PI review Phase 4, by expected information gain):** EXP-0 (paraphrase, ~1 day) → EXP-1 (calibration curve, ~1 day) → EXP-2 (affective bridge, ~1 week) → EXP-3 (minimal predictive organism, ~1 month) → EXP-4 (cycle bootstrapping, gated behind EXP-3).

---

## 7. Outstanding Risks (ranked highest → lowest)

1. **[FACT] R-1 — The core cognitive claim is empirically null so far.** R1: free-energy machinery indistinguishable from `null` (p = 0.866); the developmental "mind" thesis is asserted, not demonstrated. Highest risk: the program's headline may already be falsified pending EXP-0.
2. **[FACT] R-2 — Observability gap.** 5 of 6 primary metrics (HeldOutPredictiveLogLikelihood, RareEventRecall, KnowledgeRetentionScore, GeneralizationScore, TransferScore) are **unmeasurable** in the current harness. The system cannot measure its own claimed capabilities, so most hypotheses cannot yet be tested at all.
3. **[FACT] R-3 — Injected-prior confounding.** ~95–100% of "wants/perception/concepts" are designer-set; any observed "learning" may be a readout of injected structure, not autonomous discovery. No emergence claim is currently defensible.
4. **[FACT] R-4 — Calibration is false, not just unproven.** `CERTAIN` on hallucinated content directly violates the Constitution's central promise; blocks Program A shipping as "honest uncertainty."
5. **[FACT] R-5 — Terminology equivocation ("ACCEPTED", "KEEP", "free energy").** Registry-level ACCEPTED ≠ empirically validated; engineering-KEEP ≠ scientifically-validated; proxy-E ≠ Friston free energy. Left unresolved, these mislead reviewers (this is exactly what decorative kill criterion K9 flags).
6. **[HYPOTHESIS] R-6 — Non-convergent feedback loops.** 5–6 named cycles (attention→cluster→attention; concept-birth→probation→exceptions; free-energy→merge→clusters; adaptive-threshold; score→cause-promotion; cluster-formation). The sandbox evaluates `recent_vectors` produced under *old* clustering (A-E04, flagged CRITICAL) — may oscillate without converging.
7. **[FACT] R-7 — Unit-incommensurate objective.** `E = λH + μS + νA` sums bits + Euclidean distance + (clusters+variance) with hand-tuned coefficients; the optimization target is not physically meaningful.
8. **[FACT] R-8 — Duplicate-constant drift.** Free-energy coefficients, concept-birth thresholds (0.5 vs 0.15), learning rates (0.20 vs 0.10), proximity thresholds duplicated across modules; silent divergence risk.
9. **[HYPOTHESIS] R-9 — Circular-import fragility.** `scenario_engine ↔ metacog` (C1, HIGH) and `cognitive_core ↔ concept_birth` (C3) work only via lazy/defensive imports; refactor can crash the pipeline at import time.
10. **[FACT] R-10 — Hidden filesystem/DB coupling.** Hardcoded repo-relative paths (`data/gap_log.jsonl`, `concepts.json`) and `brain_stem.db` schema assumptions make experiments non-reproducible across machines and brittle to migration.
11. **[HYPOTHESIS] R-11 — Surprisal ceiling.** `S_max = 5.0` breaks for vocabularies > 32 symbols.
12. **[SPECULATION] R-12 — Static-analysis blind spots.** "Dead" modules may be dynamically loaded; archival could remove a live path (Confidence Low).

---

## 8. Open Questions (every unresolved scientific question)

1. **[HYPOTHESIS]** Does anything develop? Does understanding survive paraphrase, or collapse to ~4.0/10 (EXP-0)? *(Highest information gain; A-O05.)*
2. **[HYPOTHESIS]** Are the confidence tiers calibrated (ECE)? (A-BE03; EXP-1 — unrun.)
3. **[HYPOTHESIS]** Is `E` rank-correlated with any true variational free energy, or only an arbitrary proxy? (A-CA02 — untested.)
4. **[HYPOTHESIS]** Does the affective→strategic bridge do measurable work on an objective task? (H2/EXP-2.)
5. **[HYPOTHESIS]** Can prediction-error alone drive representational structure to emerge without seeding? (H3/EXP-3.)
6. **[HYPOTHESIS]** Do weak cross-modal predictors bootstrap each other (prediction⇄memory)? (EXP-4, gated behind EXP-3.)
7. **[HYPOTHESIS]** Which of the 6 uncovered experiments (ConceptBirthMDL, LatentCauseDiscovery, SoulGraphResonance, SelfModelIntrospection, CurriculumTeaching, RetrievalMesh) yields signal vs noise?
8. **[HYPOTHESIS]** Do the concept-birth/probation/free-energy feedback loops converge or oscillate? (A-E04 CRITICAL.)
9. **[HYPOTHESIS]** Does toy-environment clustering generalize beyond linearly-separable regimes? (A-E06.)
10. **[HYPOTHESIS]** What is the correct unified value for the concept-birth threshold (0.5 vs 0.15)?
11. **[FACT→open]** Can the 5 unmeasurable primary metrics be instrumented at all with the current point-prediction core? (Requires held-out splits and a probabilistic predictor the C7 core does not emit.)
12. **[SPECULATION→open]** Are the statically-flagged dead modules truly unreachable, or dynamically loaded?

---

## 9. Tomorrow's Work (exactly five tasks, ordered by expected information gain)

> All five are drawn from existing artifacts (PI-review EXP-0/EXP-1, the assumption ledger's top-3 existential questions, the kill-criteria and injection-report recommendations). No new mechanism is proposed.

1. **[HYPOTHESIS] Run EXP-0 — paraphrase the 100/100 benchmark.** Freeze code; rewrite every query so no seeded concept keyword appears as a substring; re-score. Decides whether "understanding" exceeds a lookup table. *Predicted outcome: collapse toward 4.0/10. Highest info gain, ~1 day.*
2. **[HYPOTHESIS] Run EXP-1 — calibration curve.** Plot claimed tier vs empirical correctness over ≥200 mixed queries (reliability diagram / ECE). Decides H1 and whether Program A can ship as "honest uncertainty." ~1 day.
3. **[FACT-task] Instrument the observability gap.** Make at least one currently-`n/a` primary metric measurable (a held-out split or retention re-test), so H1/H3 become testable at all. Directly attacks risk R-2; without it most hypotheses are unfalsifiable.
4. **[FACT-task] Resolve terminology + wire one kill check.** Reclassify decorative K3/K4/K9 as Design Constraints; wire the existing plateau detector (`cognitive_telemetry.py:629`) to escalate for K5. Removes reviewer-facing equivocation (R-5) and converts one kill criterion from decorative to live.
5. **[FACT-task] Derive λ,μ,ν from a data sweep + unify duplicated constants.** The injection report's single highest-leverage fix: replace the hand-set free-energy coefficients with a sweep, and collapse the duplicate coefficient/threshold definitions to one source. Attacks R-3, R-7, R-8.

---

## 10. Stop Conditions (what evidence terminates Program D forever)

Program D's developmental/"mind" thesis is **terminated permanently** if and only if:

- **[HYPOTHESIS] Primary kill (PI review Phase 5):** **EXP-0 shows collapse under paraphrase AND EXP-3 shows no emergent structure after two honest attempts.** At that point the developmental thesis is dead: keep Program A as a product and publish the negative result.

Supporting termination signals (each, if met, ends the corresponding line of inquiry):
- **[HYPOTHESIS]** H1 dies if calibration is no better than a constant-confidence baseline → Program A ships without an "honest uncertainty" claim.
- **[HYPOTHESIS]** H2 dies if the affective frame yields no significant task-outcome difference (or must be re-authored per task) → delete `BRIDGE_NODES`.
- **[HYPOTHESIS]** H3 dies if no structure emerges beyond what initialization + input statistics trivially provide.
- **[FACT] Already-triggered component stop:** the C8 free-energy consolidation policy has *no measurable benefit over null* (R1, p = 0.866); absent a measurable-metric refutation of that null, the free-energy decision machinery is a delete candidate, not a result.

**Pivot (not termination) conditions:** if H2 succeeds but H3 fails → pivot to a narrow, honest **affect-aware problem-solving assistant**. If H3 succeeds but is intractably slow → pivot to the **theory** of developmental bootstrapping rather than a deployed system.

**Non-negotiable stance (survives all outcomes):** optimize for truth, not elegance. The epistemic constitution ("trace every claim, tier confidence, say 'I don't know,' never present DEBATED as CERTAIN") survives as engineering discipline — but only once EXP-1 makes it true instead of decorative.

---

### Appendix — Source Artifacts Consolidated (2026-07-01 session)

| Area | Files |
|------|-------|
| Framing / verdict | `docs/VELYNX_v2_PI_Review.md` |
| Evidence & assumptions (C) | `research/evidence_database.md`, `research/program_c_assumption_ledger.md`, `research/program_c_mathematical_ontology.md`, `research/program_c_variable_provenance.md`, `research/program_c_variable_dependency_graph.md`, `research/designer_injection_report.md` |
| Reduction / archive (C) | `reduction/program_c_reduction_plan.md`, `reduction/program_c_safe_removal_order.md`, `archive/program_c_archive_manifest.md`, `program_c_diagram.mmd`, `program_c_graph.graphml` |
| Program D audit | `reviews/program_d_{circular_dependencies,dead_code_analysis,duplicated_logic,hidden_coupling}.md`, `literature/program_d_mathematical_provenance.md`, `assumptions/program_d_parameter_atlas.md`, `assumptions/program_d_assumption_coverage_matrix.csv`, `experiments/program_d_experiment_coverage_matrix.csv`, `dependency_graphs/program_d_*`, `reduction/program_d_{reduction,migration}_plan.md` |
| Kill criteria | `foundation/kill_criteria_validation.md` |
| Empirical result cited | `ablation_report.md` (R1, 72 experiments), `soul_test_report.md` (4.0/10 adversarial) |

*Contradictions resolved in this document: (1) engineering-KEEP vs scientific-ARCHIVE — the reduction plan keeps subsystems needed to run experiments, which is orthogonal to scientific validity; (2) coverage-matrix "ACCEPTED" vs ledger "SPECULATION/CONTRADICTED" — the former means registered/traceable, the latter empirically judged; (3) proxy-`E` vs Friston free energy — all today's documents agree it is a proxy in "arbitrary energy units," which confirms rather than contradicts the PI verdict.*

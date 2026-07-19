# Kill Criteria Validation Report

**Generated:** 2026-07-01
**Scope:** All 10 kill criteria (K1–K10) defined in `generate_graph.py:153-164`, rendered in `program_c_diagram.mmd:144-153` and `program_c_graph.graphml`.

---

## Legend

| Column | Meaning |
|--------|---------|
| **Measurable** | Can the condition be quantified from runtime metrics? |
| **Experiment Exists** | Is there a dedicated experiment that would falsify or validate this criterion? |
| **Code Exists** | Is there automated logic that *checks* this criterion (not just supporting infrastructure)? |
| **Decorative** | Defined in diagrams/graphs but has no automated check and no runtime path. |

---

## K1 — CPIDeclining

**Definition:** CPI consistently drops across runs — learning stagnates or reverses.

| Attribute | Assessment |
|-----------|-----------|
| **Measurable** | YES — CPI is computed by `CPITracker` (`cognitive_telemetry.py`) as `(0.40·A_t + 0.30·D_t + 0.20·comp_comp + 0.10·res_comp) / 1.0`. Range [0,1]. Trend over runs is a standard time-series query. |
| **Experiment Exists** | PARTIAL — E10 (CPILiveFireSimulation) validates the CPI metric itself, but no experiment *checks whether CPI declines across runs*. |
| **Code Exists** | NO — No code monitors CPI trajectory for sustained decline. The plateau detector (`cognitive_telemetry.py:629`) watches *surprise*, not CPI. |
| **Decorative?** | NO — The underlying metric (CPI) is real and computed, but the kill check itself is unimplemented. |

**Dependencies:** `M1` (CPI_Composite), `A11` (CPIMeasuresLearning)

---

## K2 — CatastrophicForgettingPersists

**Definition:** C6 Inertia Law + quarantine fails to protect mature rules in long-running regimes.

| Attribute | Assessment |
|-----------|-----------|
| **Measurable** | PARTIAL — Forgetting could be measured as rule-confidence decay over time or accuracy regression on re-presented sequences, but no dedicated forgetting metric exists. `M10` (FractureRatio) and stability (`V4`) are proxies. |
| **Experiment Exists** | PARTIAL — E5 (C6_StableBeliefRevision) validates the Inertia Law, quarantine, and fracture mechanics, but does not specifically test forgetting prevention in long-running regimes. |
| **Code Exists** | NO — Inertia Law, quarantine, and fracture mechanics are fully implemented in `cognitive_core.py:766-969`. The *check* that forgetting has occurred is not automated. |
| **Decorative?** | NO — The C6 substrate exists, but the kill check is not wired. |

**Dependencies:** `A3` (StabilitySolvesForgetting), `E5` (C6_StableBeliefRevision)

---

## K3 — ConstitutionViolation

**Definition:** Science/Uncertainty/Epistemology constitutions breached.

| Attribute | Assessment |
|-----------|-----------|
| **Measurable** | NO — No metric quantifies "constitution compliance." This is a qualitative audit finding (see PI review: `docs/VELYNX_v2_PI_Review.md`). |
| **Experiment Exists** | NO — No experiment tests constitution compliance. |
| **Code Exists** | NO — No code monitors constitution adherence. The constitution is a textual document, not a runtime constraint. |
| **Decorative?** | **YES** — Exists only in the graph model and diagram. No executable path. Serves as a design note. |

**Dependencies:** None (no metric, no variable, no experiment).

---

## K4 — NothingDevelopsPersists

**Definition:** Scaffolding remains entirely hand-authored; PI review verdict never addressed.

| Attribute | Assessment |
|-----------|-----------|
| **Measurable** | NO — "Hand-authoredness" is a property of the development process, not runtime state. No metric measures autonomy of concept formation. |
| **Experiment Exists** | NO — The PI review finding is documented (`R5` NothingDevelops, `R14` ScaffoldingNotEmergent), but no experiment tests whether scaffolding has shifted from hand-authored to emergent. |
| **Code Exists** | NO — All scaffolding (curriculum, ontology) is static data, not runtime-checked. |
| **Decorative?** | **YES** — Exists only in the graph model. Tracks a PI review finding, not a runtime condition. |

**Dependencies:** `A10` (HandAuthoredScaffoldingOk), `R5` (NothingDevelops risk)

---

## K5 — SurprisePlateauUnresolved

**Definition:** Average surprise plateaus above stuck_threshold (1.5 bits) with bottleneck < 0.55.

| Attribute | Assessment |
|-----------|-----------|
| **Measurable** | YES — All three sub-conditions are measurable: (a) surprise level via `V1`/`M3`, (b) plateau via slope < plateau_slope_epsilon (`M19`), (c) bottleneck mean accuracy via `M17`. Thresholds coded in `cognitive_telemetry.py:559-560`. |
| **Experiment Exists** | PARTIAL — E10 (CPILiveFireSimulation) exercises the reflection loop that includes plateau detection, but no experiment checks the *unresolved* condition (i.e., that bottlenecks never resolve). |
| **Code Exists** | PARTIAL — Plateau detection is fully implemented (`cognitive_telemetry.py:629-676`: `_maybe_diagnose()`). However, this detects plateaus and emits diagnostics; it does *not* escalate to a "kill" decision. The bottleneck accuracy check (<0.55) is not wired into a kill threshold. |
| **Decorative?** | NO — The detection infrastructure exists but the kill decision is not implemented. |

**Dependencies:** `M17` (BottleneckMeanAccuracy), `M19` (SurpriseSlope), `V24` (stuck_threshold indirectly), `A12` (ProbationaryTestingWorks)

---

## K6 — ExhaustionSustained

**Definition:** Cognitive energy E ≥ 18.0 sustained; fragmentation signal without discovery.

| Attribute | Assessment |
|-----------|-----------|
| **Measurable** | YES — `ENERGY_EXHAUSTION = 18.0` is a constant in `validation/metrics.py:72`. Cognitive energy E = λH + μS + νA is computed via `cognitive_energy()`. |
| **Experiment Exists** | PARTIAL — Regime classification (Optimal/Learning/Exhaustion) uses this threshold in `validation/report.py:156-160`. The E10 simulation exercises energy evolution. No experiment specifically tests *sustained* exhaustion with *no discovery*. |
| **Code Exists** | PARTIAL — The energy threshold is used for regime *classification* in `HealthReport` (`validation/report.py:158`), but there is no sustained-exhaustion monitor that would escalate to a kill. |
| **Decorative?** | NO — The energy metric is live, but the "sustained" + "no discovery" conjunction is unchecked. |

**Dependencies:** `V24` (EnergyExhaustionThreshold), `V12` (E_CognitiveEnergy), `M5` (CognitiveEnergy_E)

---

## K7 — FractureSupersaturation

**Definition:** fracture_ratio ≥ 1.0 sustained across multiple contexts; rules cannot stabilize.

| Attribute | Assessment |
|-----------|-----------|
| **Measurable** | YES — `fracture_ratio = contradiction_count / support_count` (capped at 1.0) is computed in `cognitive_core.py:249-258` and `cognitive_core.py:746-750`. Available per-rule. |
| **Experiment Exists** | PARTIAL — E5 (C6_StableBeliefRevision) validates fracture mechanics, but does not test sustained supersaturation. |
| **Code Exists** | PARTIAL — `FRACTURE_THRESHOLD = 0.85` (`cognitive_core.py:682`) triggers individual rule fracture. The sustained ≥1.0 cross-context check is not implemented. |
| **Decorative?** | NO — fracture_ratio is live, the fracture trigger at 0.85 is active, but the K7 kill check (≥1.0 sustained across contexts) is not. |

**Dependencies:** `V5` (FractureRatio), `L9` (FractureMechanics)

---

## K8 — NoGenuineLearning

**Definition:** CPI near 0.5 with flat trajectory while surprise stays high.

| Attribute | Assessment |
|-----------|-----------|
| **Measurable** | YES — CPI ∈ [0,1] is computed. Surprise is available via `V1`. Flat trajectory is a trend check (same as plateau detection, `M19`). |
| **Experiment Exists** | NO — No experiment tests the CPI-near-0.5 + flat + high-surprise conjunction. E10 exercises CPI but does not check this specific condition. |
| **Code Exists** | NO — Neither the CPI trajectory monitor nor the surprise level monitor is wired to check this conjunction. |
| **Decorative?** | NO — The constituent metrics exist but the specific kill check is not implemented. |

**Dependencies:** `M1` (CPI_Composite), `A11` (CPIMeasuresLearning)

---

## K9 — FEPMisrepresentation

**Definition:** FEP proxy presented as Friston free energy without qualification fails Science constitution.

| Attribute | Assessment |
|-----------|-----------|
| **Measurable** | NO — "Misrepresentation" is a social/epistemic property, not a runtime quantity. No metric can detect whether claims are qualified. |
| **Experiment Exists** | NO — No experiment tests FEP-proxy qualification. |
| **Code Exists** | NO — No code checks documentation or output strings for FEP representation accuracy. |
| **Decorative?** | **YES** — Exists only in the graph model and evidence database. Tracks a constitution risk identified by the evidence database. |

**Dependencies:** `A7` (FreeEnergyProxyIsAdequate), `R1` (FEPProxyNotFEP risk)

---

## K10 — ProbationNeverConfirms

**Definition:** All probationary candidates rejected; hypothesis testing pipeline fails to find valid structures.

| Attribute | Assessment |
|-----------|-----------|
| **Measurable** | YES — Probation coverage (`V20`) is tracked per candidate. `M11` (ProbationCoverage) measures hits/trials; threshold is ≥0.60 to confirm (`cognitive_core.py:1119`). Confirmed/rejected verdicts are recorded. |
| **Experiment Exists** | PARTIAL — E11 (ProbationaryConceptPipeline) validates the probation mechanism. No experiment checks the "all rejected" condition. |
| **Code Exists** | PARTIAL — Probation logic is fully implemented (`cognitive_core.py:1111-1597`). Verdicts are rendered. But no automated alert fires when all candidates over a window are rejected. |
| **Decorative?** | NO — Probation pipeline is real, but the "never confirms" aggregate check is missing. |

**Dependencies:** `A12` (ProbationaryTestingWorks), `E11` (ProbationaryConceptPipeline)

---

## Summary

| Criterion | Measurable | Experiment Exists | Code Exists | Decorative |
|-----------|:----------:|:-----------------:|:-----------:|:----------:|
| **K1** — CPIDeclining | YES | Partial (CPI metric) | NO | NO |
| **K2** — CatastrophicForgettingPersists | Partial | Partial (C6 mechanics) | NO | NO |
| **K3** — ConstitutionViolation | **NO** | NO | NO | **YES** |
| **K4** — NothingDevelopsPersists | **NO** | NO | NO | **YES** |
| **K5** — SurprisePlateauUnresolved | YES | Partial (E10) | Partial (detection only) | NO |
| **K6** — ExhaustionSustained | YES | Partial (regime classification) | Partial (threshold only) | NO |
| **K7** — FractureSupersaturation | YES | Partial (E5) | Partial (0.85 threshold) | NO |
| **K8** — NoGenuineLearning | YES | NO | NO | NO |
| **K9** — FEPMisrepresentation | **NO** | NO | NO | **YES** |
| **K10** — ProbationNeverConfirms | YES | Partial (E11) | Partial (verdicts exist) | NO |

### Key Findings

1. **No kill criterion is wired to an automated kill decision.** Every criterion is defined in the graph model only. The diagram and graphml are the *only* places the criteria live.

2. **3 of 10 criteria are decorative** (K3, K4, K9). They have:
   - No measurable runtime signal
   - No experiment
   - No code
   These are architectural reminders / design notes masquerading as kill criteria.

3. **7 of 10 have partial or full measurability** (K1, K2 partial, K5, K6, K7, K8, K10). The underlying metrics exist in runtime code. What is missing is the aggregation logic that would raise a kill signal.

4. **No kill criterion has a dedicated falsification experiment.** The experiments that exist (E5, E10, E11) validate the mechanics but do not establish failure thresholds for the kill criteria.

5. **The plateau detector (`cognitive_telemetry.py:629`)** comes closest to a live kill check but stops at `SystemDiagnostics` — it never halts execution.

### Recommended Actions

- **Remove decorative criteria** (K3, K4, K9) from the kill criteria list or reclassify as "Design Constraints" / "Risks."
- **Wire the plateau detector** to escalate to a configurable kill action (halt, flag, notify) for K5.
- **Add CPI trajectory tracking** to the reflection loop to support K1 and K8.
- **Add a sustained-exhaustion counter** to support K6.
- **Add a cross-context fracture-ratio aggregator** to support K7.
- **Add an all-rejected windowed check** to the probation pipeline to support K10.

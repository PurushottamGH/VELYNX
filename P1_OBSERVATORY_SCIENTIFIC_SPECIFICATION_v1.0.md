# Project P1 Observatory — Scientific Discovery Specification

- **Specification version:** 1.0.0
- **Date:** 2026-07-28
- **Scientific phase:** Discovery
- **Scientific authority:** P1 Scientific Operating System
- **Canonical scientific state:** SKB v1.1.0 / Living Scientific Model v1.2.0
- **Purpose:** Define what scientists must be able to observe; this document does not prescribe software architecture.
- **Governing question:** What is the smallest observation or experiment that would most reduce uncertainty?

## Executive scientific ruling

The Observatory is not a dashboard for system activity. It is the visual interface to P1's scientific state and evidence-producing process.

Its job is to let a scientist move without epistemic discontinuity from a live or recorded event to the affected mechanism, measurement, experiment, hypothesis, scientific decision, and theory boundary. It must expose counterfactual comparisons, confounding, missing measurements, invalid treatments, provenance defects, and negative results at least as readily as favorable outcomes.

The governing invariant is:

> **Every displayed object and relation must resolve to an actual, typed, provenance-bearing scientific or experimental record. If no admissible record exists, the Observatory displays the absence as missing instrumentation, an Unknown, or Scientific Debt; it never substitutes a decorative estimate.**

At the present canonical state, P1 has no validated mechanism and no supported theory. M1 is locally conformant but not confirmatory-ready. Therefore the Observatory must show hypothesis and mechanism uncertainty, evidence-admissibility blockers, and absent theory support explicitly. A visually impressive representation that suggests otherwise would be scientifically false.

---

# 1. Scientific objectives

The Observatory must enable scientists to:

1. **Locate uncertainty.** Identify the highest-value unresolved Unknown, its dependencies, and the smallest discriminating observation or experiment.
2. **Trace claims to measurements.** Move from any claim to the observations, executions, instruments, assumptions, limitations, evidence relations, and Decisions that determine its current status.
3. **Observe cognition without anthropomorphic inference.** Display recorded state transitions, predictions, losses, memory operations, gates, structural changes, and attention allocations without calling them thought, understanding, intention, or emergence unless a governed construct and evidence relation warrant that language.
4. **Compare mechanisms causally.** Expose matched and unmatched dimensions, treatment fidelity, realized resources, timing, information access, and alternative explanations.
5. **Detect methodological failure early.** Reveal absent treatments, floor/ceiling effects, metric unavailability, leakage, unit mismatch, truncation, dirty provenance, and non-independent evidence before additional runs are spent.
6. **Preserve negative knowledge.** Make valid negative, invalid, abandoned, and indeterminate executions first-class discoverable objects.
7. **Separate scientific phases.** Mark Discovery, Validation, and publication packaging distinctly; never visually promote exploratory evidence into validated knowledge.
8. **Support reproducibility.** Reconstruct the exact path from protocol and code identity through events and artifacts to result and Decision.
9. **Support theory discrimination, not theory illustration.** Show a theory only through constituent validated hypotheses, risky predictions, competing theories, boundary conditions, and anomalous evidence.
10. **Improve scientific decisions.** Every view must make at least one reversible scientific decision easier: proceed, stop, calibrate, revise, split, reject, validate, replicate, or archive.

A view that merely communicates activity, beauty, scale, or implementation sophistication is outside scope.

---

# 2. Observability principles

## 2.1 Scientific-state fidelity

Every mark on screen must have:

- a stable object identity;
- object type and schema version;
- source and scope;
- measurement or derivation definition;
- scientific phase and admissibility class;
- timestamp or interval;
- uncertainty or explicit `not_available` state;
- limitations and known confounders;
- links to upstream and downstream scientific objects.

No interpolation, smoothing, aggregation, or derived score may be displayed without an inspectable definition and inputs.

## 2.2 Observation is not interpretation

The Observatory must visually distinguish:

- raw event or artifact;
- observed measurement;
- derived metric;
- evidence relation;
- interpretation;
- Scientific Decision;
- hypothesis or theory status.

For example, “gate fired at step 431” is an observation. “Surprise caused beneficial replay” is a causal interpretation requiring a matched intervention.

## 2.3 Missingness is scientific state

Four absences must not be conflated:

1. **not instrumented** — no measurement exists;
2. **not applicable** — construct does not apply;
3. **not observed** — instrument existed, event did not occur;
4. **unavailable/corrupt** — expected data is missing or invalid.

Each has a different scientific consequence and must render differently.

## 2.4 Non-interference

Observation must not alter trajectory. Every observable must declare collection cost and whether collection can perturb timing, memory, compute, randomness, or state. Perturbing probes are experimental interventions and must be labeled as such.

## 2.5 Phase-scaled rigor

Discovery views may include exploratory metrics and post hoc slices, visibly labeled. Validation views may display only frozen outcomes, estimands, controls, exclusions, stopping rules, and uncertainty defined before confirmatory access. Publication views are projections of validated records, never a source of validation.

## 2.6 Comparison before magnitude

A scientific display should prefer contrasts over isolated traces. Every treatment view should show its baseline and credible alternatives with resource, opportunity, data, memory, information, and compute matching.

## 2.7 Uncertainty before salience

Use intervals, paired differences, seed/world variation, missingness, and validity badges before color intensity or ranking. Large visual salience cannot substitute for inferential precision.

## 2.8 Causal restraint

Arrows mean typed relations, never generic association. Allowed visual semantics include temporal precedence, data flow, experimental assignment, intervention, evidence support/opposition/limitation, dependency, contradiction, and supersession. Each relation type must be distinguishable and inspectable.

## 2.9 Negative-result symmetry

Adverse and null outcomes receive the same visibility, drill-down depth, provenance, and persistence as favorable outcomes. Invalid runs are visible but segregated from target-effect synthesis.

## 2.10 Reproducible transformation

Every plotted value must be reproducible from immutable source artifacts with a named transformation. A scientist must be able to inspect the exact rows or events contributing to any mark.

## 2.11 Honest granularity

The interface may zoom only where scientific state exists. Current M1 artifacts support system, run/subsystem, task/block, event, history, experiment, and SKB claim views. Generic neuron and connection views are **instrumentation-gated**: they remain unavailable unless a governed model exposes stable neuron/connection identities and state snapshots. The Observatory must not infer neural objects from arbitrary software units.

## 2.12 Decision relevance

Before a visualization is admitted, its owner must state:

- the target unknown;
- the scientific question;
- the falsifiable hypothesis or validity claim;
- the engineering failure it can diagnose;
- the decision it changes;
- why a cheaper table, scalar, or audit cannot answer equally well.

---

# 3. The scientific object contract

A displayable object is admitted only if it implements this scientific contract conceptually:

| Field | Requirement |
|---|---|
| Identity | Permanent SKB ID, experiment execution ID, run ID, or stable run-local object ID |
| Type | System, subsystem, cluster, neuron, connection, event, history segment, experiment, theory object, or governed overlay |
| Provenance | Artifact path/digest; protocol, code, environment, dataset/world, runtime, and seed lineage as applicable |
| State | Recorded fields only; derived fields include formula/version |
| Time | Event time, step, checkpoint, interval, or scientific-state version |
| Scope | Environment, task, condition, seed, world, claim scope |
| Validity | Raw/derived; exploratory/confirmatory; valid/invalid/indeterminate; eligibility status |
| Uncertainty | Sampling, measurement, model, or explicit unavailable state |
| Relations | Typed links to parent/children, sources, evidence, hypotheses, assumptions, unknowns, debt, decisions, theories |
| Cost | Collection and storage cost; perturbation status |
| Redaction | Whether private/sensitive fields are omitted without altering scientific meaning |

### Current actual sources

The initial Observatory may truthfully project:

- `science/SKB_RECORDS_v1.0.yaml` and SKB projections;
- `EXP-`, `OBS-`, `EVD-`, `HYP-`, `MEC-`, `ASM-`, `UNK-`, `SDEBT-`, `NEG-`, and `DEC-` records;
- run `manifest.json`, `inventory.json`, `status.json`, `config.yaml`, `steps.csv`, `probes.csv`, `metrics.json`, and declared plots;
- current M1 event fields: `t`, `task`, `loss`, `replays`, `gate_fired`, `buffer_size`, `updates`;
- current probe fields: block, step, trained task, task, loss, oracle, excess;
- current governed metrics: online loss, excess loss, plasticity, compute, and gate activity.

Other proposed observables below are **scientific requirements for future instrumentation**. Until their source contract exists, they render as unavailable—not as zeros, inferred values, or simulations.

---

# 4. Zoom model

Zoom is a change in scientific question, not merely geometric magnification.

| Zoom | Scientific object | Required question | Minimum actual state | Current readiness |
|---|---|---|---|---|
| **System** | Whole governed run or live cognitive system | What regime is the system in, and which scientific blockers qualify interpretation? | run identity, phase, config, status, resource totals, active Unknowns/debt | Partly available |
| **Subsystem** | Model, environment, memory, gate, replay, metric, probe, or observer | Which component-local state and intervention produced the observed transition? | stable component identity, input/output/event records, budget | Partly available |
| **Cluster** | Empirically defined population/state aggregate | Which coordinated population or state class carries the effect? | clustering rule/version, membership, stability, controls | Legacy/provisional only; must be instrumented per assay |
| **Neuron** | Stable model unit with scientific semantics | Which unit changes activity, selectivity, or plasticity under the intervention? | unit ID, activation/state, update, ablation mapping | Not available in current M1; gated |
| **Connection** | Stable directed/undirected parameter relation | Which relation changes, transmits influence, or carries memory? | endpoint IDs, weight/state, update, causal lesion path | Not available in current M1; gated |
| **Event** | Atomic recorded transition | What exactly happened at this step, under what prior state and cause candidate? | immutable event record and neighboring context | Available at M1 step/probe level |
| **History** | Ordered lineage of states/events | How did the present state arise, and where did divergence begin? | event sequence, checkpoints, changes, retention lineage | Available partially |
| **Experiment** | Protocol, executions, contrasts, validity, outcomes | Does the controlled contrast discriminate among hypotheses? | protocol, conditions, units, outcomes, uncertainty, validity | Available in SKB; run linkage incomplete for some legacy work |
| **Theory** | Explanatory graph and risky predictions | Which validated relations are explained better than alternatives? | supported theory record with validated constituents | No supported theory; display explicit absence |

### Cross-level continuity rule

Selecting any object must reveal:

`object → containing level → event/history → execution → experiment → evidence relation → hypothesis/assumption/unknown/debt → Decision → theory status`

The reverse path must also work. A hypothesis must reveal the exact events and derived observations admitted as evidence. If a link is absent, the discontinuity is shown as a traceability defect.

---

# 5. Core scientific visualizations

Each admitted visualization below answers the five mandatory questions and identifies its required source. Names describe scientific functions, not UI components.

## V01. Scientific state and uncertainty map

**Form:** Typed evidence/dependency graph across hypotheses, mechanisms, assumptions, Unknowns, debt, observations, evidence, experiments, negative results, Decisions, and theories. Missing edges remain visible as absence.

- **Why should it exist?** To prevent narrative or implementation prominence from being mistaken for evidential support.
- **Scientific question:** What does P1 currently know, what remains unknown, and what blocks each claim?
- **Hypothesis it can validate:** It does not validate a mechanism; it validates the meta-hypothesis that every current scientific status is traceable to admissible evidence and a Decision.
- **Engineering problem it can diagnose:** Broken IDs, orphaned records, stale projections, missing artifact links, or contradictory status propagation.
- **Decision made easier:** Choose the highest-value next experiment; reopen, narrow, reject, or retain a claim.
- **Source:** Canonical SKB and typed relations.

## V02. Evidence-admissibility and provenance ledger

**Form:** Per-run eligibility chain showing protocol/config hash, code state, commit identity, runtime, seed lineage, artifact inventory/digests, gate results, deviations, and confirmatory eligibility.

- **Why should it exist?** Because a result that cannot be reconstructed or admitted cannot safely change scientific belief.
- **Scientific question:** Can this execution count as Discovery evidence, Validation evidence, methodological evidence only, or no target evidence?
- **Hypothesis it can validate:** `ASM-2026-0010` clean reconstruction and `ASM-2026-0011` gate-to-live-surface alignment.
- **Engineering problem it can diagnose:** Dirty/untracked runs, missing artifacts, hash mismatch, wrong path coverage, seed/config drift, or vacuous gates.
- **Decision made easier:** Admit, quarantine, rerun, or reject an execution before interpretation.
- **Source:** manifest, inventory, status, protocol/execution records, CI/gate evidence.

## V03. Experimental design and comparability matrix

**Form:** Conditions as columns; independent/dependent/control/nuisance variables and realized resources as rows. Every unmatched cell is explicit.

- **Why should it exist?** To expose bundled interventions and comparison unfairness before causal language appears.
- **Scientific question:** What actually differs between treatment, baseline, and alternatives?
- **Hypothesis it can validate:** Any treatment hypothesis, presently especially `HYP-2026-0007` and `HYP-2026-0008`, once all causal dimensions are matched.
- **Engineering problem it can diagnose:** Configuration drift, inconsistent update counts, replay shortfall, unequal decay, dataset leakage, or condition-specific instrumentation.
- **Decision made easier:** Run, redesign, narrow the estimand, or refuse causal interpretation.
- **Source:** frozen protocol, configs, manifests, realized compute and event counts.

## V04. Treatment-fidelity and event raster

**Form:** Time-aligned atomic events by condition/seed: task boundaries, treatment delivery, gate fires, replay requests/deliveries, probes, growth attempts, lesions, failures, and stops.

- **Why should it exist?** An experiment cannot test a mechanism that did not occur or occurred at the wrong time.
- **Scientific question:** Was the intended treatment delivered with sufficient intensity, timing, and contrast?
- **Hypothesis it can validate:** Treatment-operability claims; currently `UNK-2026-0005` for growth and the schedule premise of `HYP-2026-0008`.
- **Engineering problem it can diagnose:** Never-firing gates, duplicated events, boundary-locking, missed probes, premature truncation, or treatment leakage into controls.
- **Decision made easier:** Continue, stop, calibrate, or invalidate the run.
- **Source:** immutable event stream; absent event types remain unavailable.

## V05. Prediction–observation–update trace

**Form:** At event zoom: pre-update prediction distribution or score, observed target, prequential loss/surprise, attention allocation, selected memory/replay items, update magnitude, and post-update state summary.

- **Why should it exist?** To connect behavioral error to the actual state transition without reverse-engineering from aggregate metrics.
- **Scientific question:** How did a particular observation alter prediction and internal state?
- **Hypothesis it can validate:** Local learning-rule and error-gating hypotheses, provided predicted state, update, and matched controls are instrumented.
- **Engineering problem it can diagnose:** Learn-before-predict leakage, stale prediction use, wrong target routing, update omission, or timestamp misordering.
- **Decision made easier:** Retain the event schema, diagnose a failure, or design a local ablation.
- **Source:** current M1 has loss and counts but lacks prediction distributions/update deltas; full view is instrumentation-gated.

## V06. Learning and adaptation curves

**Form:** Prequential loss by task/block, task-switch-aligned adaptation curves, current-task tail, and paired condition differences with uncertainty.

- **Why should it exist?** Retention gains that arise from refusal or inability to learn are not scientific progress.
- **Scientific question:** How quickly and how well does the system learn each regime, and what plasticity cost accompanies retention?
- **Hypothesis it can validate:** Plasticity guardrails attached to `HYP-2026-0007` and `HYP-2026-0008`.
- **Engineering problem it can diagnose:** Task-label errors, stalled updates, switch detection errors, unstable optimization, or divergent seeds.
- **Decision made easier:** Reject a retention mechanism with unacceptable adaptation cost; choose windows and pilot viability.
- **Source:** `steps.csv`, online-loss and plasticity metrics.

## V07. Memory state, custody, and selection view

**Form:** Memory occupancy over time plus item-level lineage: creation event, task/world source, eligibility, priority, age, retrieval/replay selections, replacement/eviction, decay, and lesion status.

- **Why should it exist?** “Memory helped” is uninterpretable without knowing what was stored, retained, selected, and exposed.
- **Scientific question:** Which historical information remained available and which items actually influenced later learning or decisions?
- **Hypothesis it can validate:** `HYP-2026-0007` historical replay and `HYP-2026-0009` historical-carrier dependence.
- **Engineering problem it can diagnose:** Cross-task contamination, reservoir bias, incorrect eviction, duplicate storage, present-task leakage, or carrier loss.
- **Decision made easier:** Choose an ablation, repair a memory construct, or conclude that the historical carrier was absent.
- **Source:** current M1 exposes only buffer size; item-level view is instrumentation-gated.

## V08. Replay allocation and counterfactual schedule view

**Form:** Gate signal and threshold over time; requested versus realized replay; item ages/tasks; batch-size profile; matched-random and boundary-timed counterfactual schedules; replay shortfall.

- **Why should it exist?** Replay quantity, content, and timing are distinct causal variables.
- **Scientific question:** Is observed benefit due to historical content, replay budget, task-boundary timing, or loss-triggered allocation information?
- **Hypothesis it can validate:** `HYP-2026-0007` and `HYP-2026-0008`.
- **Engineering problem it can diagnose:** Budget mismatch, shortfall, current-sample rehearsal, task-boundary confounding, RNG coupling, or batch drift.
- **Decision made easier:** Remove surprise-specific complexity, validate replay content, or redesign matching.
- **Source:** current gate/compute metrics plus future item-selection and signal records.

## V09. Retention–mastery–plasticity surface

**Form:** Per task and condition: post-learning mastery, final oracle-relative excess loss, degradation, worst-task loss, retention trajectory, and plasticity; show legacy forgetting scalar only as ineligible comparator.

- **Why should it exist?** It prevents weak initial learning from masquerading as low forgetting.
- **Scientific question:** Did the system retain acquired capability while remaining able to adapt?
- **Hypothesis it can validate:** Construct validity of `ASM-2026-0002`, resolution of `UNK-2026-0003`, and guardrails for replay hypotheses.
- **Engineering problem it can diagnose:** Probe-task misalignment, oracle absence, wrong reference block, sign inversion, task averaging that hides collapse.
- **Decision made easier:** Retire the legacy scalar, accept a measurement construct for Validation, or reject a mechanism trade-off.
- **Source:** probes, excess-loss, retention, and plasticity metrics.

## V10. Structural state and change lineage

**Form:** Stable structural objects and events: units/states/clusters/rules, creation/removal/split/merge, parameter count, occupancy, support, contradictions, and complexity/description length. Every structure links to the event and rule that created it.

- **Why should it exist?** Structural growth is scientifically meaningful only when its origin, cost, persistence, and functional contribution are visible.
- **Scientific question:** What structure changed, why did it change, and did it improve out-of-sample prediction beyond matched controls?
- **Hypothesis it can validate:** `HYP-2026-0001` error-gated structure acquisition and `ASM-2026-0005` learned-versus-injected identifiability.
- **Engineering problem it can diagnose:** Impossible thresholds, duplicate structures, runaway growth, dead units, unstable clusters, wrong unit scales, or untracked designer injection.
- **Decision made easier:** Permit a clean H* test, stop growth runs, ablate a structure, or classify it as injected/trivial.
- **Source:** E0/structural instrumentation; current canonical E0 supports zero growth plus units mismatch, not a neuron graph.

## V11. Cluster evidence view

**Form:** Empirical cluster membership, defining measurement space, occupancy, stability across seeds/checkpoints, transition statistics, baseline overlap, split/merge lineage, and null/control comparison.

- **Why should it exist?** A colored cluster picture can imply categories that are unstable, algorithmic, or label-seeded.
- **Scientific question:** Is this population/state grouping stable, predictive, and nontrivial relative to a null?
- **Hypothesis it can validate:** Cluster-level structure as an operational subclaim of `HYP-2026-0001`, not general semantics.
- **Engineering problem it can diagnose:** Label permutation, collapse, empty clusters, drift, initialization sensitivity, or data leakage.
- **Decision made easier:** Treat a cluster as a provisional analysis unit, revise the clustering rule, or discard it.
- **Source:** cluster definition/version, membership snapshots, controls; otherwise unavailable.

## V12. Neuron/unit state view

**Form:** Stable unit ID with activation distribution, selectivity, update history, age, incoming/outgoing contribution, ablation effect, and cross-seed correspondence uncertainty.

- **Why should it exist?** Only when a unit-level causal or representational claim is under test.
- **Scientific question:** Does a specific unit or unit class carry a reproducible, functionally necessary signal?
- **Hypothesis it can validate:** A preregistered unit-level mediator hypothesis derived from a broader mechanism; none currently exists in the SKB.
- **Engineering problem it can diagnose:** Saturation, dead units, exploding updates, misrouting, or stale state.
- **Decision made easier:** Design a lesion, reject a unit-level story, or escalate a stable mediator candidate.
- **Source:** stable unit instrumentation and intervention results. **Current status: do not render.**

## V13. Connection/parameter influence view

**Form:** Stable connection ID, endpoints, sign/magnitude, update history, usage/influence statistic, uncertainty, and lesion/intervention effect; never a decorative dense graph.

- **Why should it exist?** Only to test whether a relation carries influence or learned history.
- **Scientific question:** Which connection changes mediate a measured behavioral or structural effect?
- **Hypothesis it can validate:** A registered connection-level causal mediation hypothesis; none currently exists.
- **Engineering problem it can diagnose:** Disconnected subgraphs, frozen or exploding weights, sign errors, update asymmetry, or unintended parameter sharing.
- **Decision made easier:** Select a minimal lesion, localize a defect, or abandon a connection-level explanation.
- **Source:** stable endpoint and update instrumentation plus intervention. **Current status: do not render.**

## V14. Attention allocation view

**Form:** Attention/precision weights over actual candidates, inputs, memory items, or units; normalized allocation, entropy/concentration, competing cues, downstream updates, and matched attention controls.

- **Why should it exist?** To determine whether selective processing, rather than total compute or salience, explains learning differences.
- **Scientific question:** What received limited processing, under which signal, and with what measurable consequence?
- **Hypothesis it can validate:** A registered attention-allocation hypothesis; current SKB contains none. It may support a future mediator hypothesis between error and update.
- **Engineering problem it can diagnose:** Uniform or saturated attention, normalization error, cue leakage, stale weights, or allocation disconnected from updates.
- **Decision made easier:** Register a targeted hypothesis, design a cue ablation, or avoid claiming attention as a mechanism.
- **Source:** actual attention weights and candidates. Current M1 does not expose them; legacy `attention_weight` is provisional and not canonical evidence.

## V15. Emergence discrimination panel

**Form:** Observed structure statistic versus shuffled-input, fixed-capacity, capacity-matched error-decoupled, random-growth, and designer-injection controls; includes treatment fidelity, NMI or predictive gain, held-out performance, description-length gain, persistence, and transfer within scope.

- **Why should it exist?** Emergence claims are especially vulnerable to injected structure, trivial statistics, and absent treatment.
- **Scientific question:** Did structure absent at initialization arise from the proposed learning process and exceed credible nulls?
- **Hypothesis it can validate:** `HYP-2026-0001` within its registered scope, after operability and identifiability debts clear.
- **Engineering problem it can diagnose:** Growth nonactivation, shuffled-control leakage, capacity mismatch, label seeding, unstable assignments, or complexity penalty errors.
- **Decision made easier:** Proceed to Validation, revise H*, split the mechanism, or reject/archive the line.
- **Source:** registered E0 successors and controls. Current state must show “H* untested; E0 treatment absent.”

## V16. Failure topology and first-divergence view

**Form:** Failures grouped by scientific consequence—measurement, treatment, provenance, compute, numerical, data, instrumentation, and inference—with earliest divergent event against a matched successful/control run.

- **Why should it exist?** The first scientifically relevant divergence is more informative than the final exception or bad metric.
- **Scientific question:** Did failure invalidate the target test, create a methodological result, or merely reduce engineering reliability?
- **Hypothesis it can validate:** Validity claims for each execution; it may not update the target mechanism when treatment or measurement failed.
- **Engineering problem it can diagnose:** Wrong units, NaN onset, artifact corruption, missing events, seed mismatch, resource truncation, or nondeterministic branch divergence.
- **Decision made easier:** Invalidate, salvage as methodological evidence, rerun, or stop the research line.
- **Source:** status, deviations, event histories, artifact checks, matched-run comparison.

## V17. Validation and inference view

**Form:** Preregistered estimand, independent unit, paired contrasts, effect sizes, uncertainty, SESOI/equivalence margins, guardrails, exclusions, multiplicity/stopping status, discovery-versus-confirmation split, and assumption checks.

- **Why should it exist?** A result cannot be accepted from point estimates, rank stability, or non-overlapping confidence intervals.
- **Scientific question:** Does the confirmatory contrast meet the frozen decision rule with adequate validity and precision?
- **Hypothesis it can validate:** Any hypothesis in Validation, particularly future `HYP-2026-0007/0008` protocols.
- **Engineering problem it can diagnose:** Wrong pairing, seed reuse, accidental outcome access, missing cells, exclusion drift, or mismatched analysis version.
- **Decision made easier:** Accept within scope, reject, revise, or declare valid indeterminate.
- **Source:** preregistration, execution records, statistical outputs, deviations. Present M1 confirmatory views must show blocked.

## V18. Causal intervention and mediator view

**Form:** Assignment and intervention graph plus outcome contrasts for treatment, baseline, lesion, rescue, shuffle, and resource-matched controls; mediators shown only with temporal and intervention evidence.

- **Why should it exist?** Temporal traces and correlations cannot establish mechanism.
- **Scientific question:** Which manipulated component is necessary or sufficient for the effect, and which alternatives remain viable?
- **Hypothesis it can validate:** `HYP-2026-0007`, `HYP-2026-0008`, `HYP-2026-0009`, and future mediator hypotheses.
- **Engineering problem it can diagnose:** Intervention contamination, failed lesion, incomplete rescue, condition routing error, or shared-state leakage.
- **Decision made easier:** Retain, remove, split, or merge a mechanism; choose the next discriminating intervention.
- **Source:** protocol assignments, treatment checks, event traces, outcomes, typed causal assumptions.

## V19. History and divergence explorer

**Form:** Synchronized state histories for two or more matched executions, with checkpoint hashes and selectable first divergence from system to event/object level.

- **Why should it exist?** Reproducibility and causal diagnosis require locating when nominally identical or deliberately different trajectories separate.
- **Scientific question:** Is divergence expected from the intervention/seed, or caused by uncontrolled state?
- **Hypothesis it can validate:** Deterministic reconstruction under `ASM-2026-0010`; paired causal timing claims when histories are matched.
- **Engineering problem it can diagnose:** Nondeterminism, order dependence, hidden state, RNG coupling, resume drift, or serialization defects.
- **Decision made easier:** Pass readiness, quarantine a run, localize an intervention effect, or require new instrumentation.
- **Source:** ordered events and normalized checkpoint hashes; current full-state checkpoints are not yet available.

## V20. Theory discrimination map

**Form:** Competing theories as explanatory graphs linked to validated constituent hypotheses, boundary conditions, complexity cost, risky predictions, anomalies, and unresolved discriminators.

- **Why should it exist?** To prevent a collection of compatible ideas from being presented as a supported theory.
- **Scientific question:** Which theory explains validated results better than alternatives and survives a novel risky prediction?
- **Hypothesis it can validate:** Theory-level predictions only after theory admission; currently none.
- **Engineering problem it can diagnose:** None directly; it can reveal missing run-to-claim links or absent measurements needed for a discriminator.
- **Decision made easier:** Admit a candidate theory, choose a theory-discriminating experiment, revise, or reject it.
- **Source:** Theory Registry and evidence graph. **Current display must state: no supported P1 theory exists.**

---

# 6. Cognitive observables

“Cognitive” is a scientific label only for operationalized state and behavior. Required observables are:

| Observable | Definition | Scientific use | Current source/status |
|---|---|---|---|
| Predictive state | Pre-update distribution/score and entropy over declared alternatives | Separates expectation from outcome | Not present in M1 step artifact; instrumentation required |
| Prediction error | Proper prequential loss or registered surprise definition | Drives learning/gating hypotheses | `loss` exists; surprise construct depends on mechanism |
| Internal context | Exact finite historical state available before action/prediction | Tests carrier dependence and leakage | Environment `context` not persisted in current `steps.csv` |
| Belief/state summary | Stable model state with support, contradictions, uncertainty | Tracks learning and fracture without anthropomorphism | Legacy-only/provisional |
| Action/decision | Candidate set, chosen action, policy score, information available | Required for interactive competence tests | Not in current M1 assay |
| Confidence/calibration | Issued confidence with outcome correctness and stratum | Tests `HYP-2026-0002` | Historical hard failure only; no population instrument |
| Cognitive load/resource | Updates, memory use, compute, probe load | Distinguishes mechanism from resource | Partly available |
| State transition | Before/after state delta caused by one governed update | Localizes learning mechanism | Instrumentation required |

The Observatory must never infer “belief,” “concept,” “understanding,” or “attention” from a generic activation or loss curve.

---

# 7. Experimental observables

Every experiment view must expose:

- scientific phase and lifecycle state;
- target Unknown and decision impact;
- linked hypotheses, assumptions, mechanisms, theories, and debt;
- null and credible alternatives;
- experimental unit and assignment;
- all conditions, baselines, controls, and ablations;
- intended and realized treatment;
- independent, dependent, controlled, nuisance, and confounding variables;
- measurement definitions and validity links;
- planned and realized data/compute/time/memory budgets;
- seed/world structure and independence clusters;
- protocol/version/config/code/runtime identity;
- deviations, exclusions, truncation, and outcome-access history;
- raw results, uncertainty, and validity independent of favorability;
- evidence relations and final Decision.

An experiment without realized treatment, realized resource accounting, and a validity disposition cannot appear as merely “completed.”

---

# 8. Memory observables

Memory observability requires distinction among **capacity**, **content**, **availability**, **selection**, **use**, and **effect**.

Required fields:

- memory store identity and capacity;
- item ID and immutable content digest or safe scientific descriptor;
- creation event, source task/world, timestamp, and originating observation;
- task/history label visible to the mechanism at selection time;
- eligibility and exclusion reason;
- priority/weight, age, decay, consolidation, and revision history;
- retrieval/replay request and realized selection probability;
- selections, uses, update contribution, and downstream outcome links;
- replacement/eviction event and policy reason;
- lesions, masks, shuffles, and restore/rescue events;
- occupancy, diversity, age, source-task distribution, and duplication.

The existing `buffer_size` is a capacity/occupancy observable only. It cannot support claims about historical content or carrier dependence.

---

# 9. Replay observables

Replay observability must separate:

1. **trigger signal** — value, definition, threshold, and inputs;
2. **gate decision** — fire/no-fire and reason;
3. **request** — requested count and eligibility constraints;
4. **selection** — item IDs, task/source, age, probability, replacement mode;
5. **realization** — actual batch, shortfall, and discarded requests;
6. **learning** — number and magnitude of replay updates;
7. **resources** — compute, decay, and opportunity cost;
8. **counterfactual schedule** — matched random/boundary schedule generated without outcome leakage;
9. **outcome relation** — retention/plasticity effects at experimental, not anecdotal-event, level.

The current M1 fields `gate_fired`, `replays`, `updates`, and gate/compute aggregates support only a partial replay view.

---

# 10. Learning observables

Minimum learning observables:

- prequential loss by event, task, and condition;
- post-learning mastery at each task's reference checkpoint;
- adaptation curve and AUC after every switch;
- final oracle-relative excess loss by task;
- degradation from post-learning to final state;
- worst-task as well as mean outcomes;
- backward/forward transfer where operationalized;
- update count and update magnitude/distribution;
- parameter/state delta and persistence when available;
- learning efficiency per update, data exposure, and compute;
- between-seed/world heterogeneity and paired contrasts.

Learning curves must display switch boundaries, probe times, truncation, and intervention windows. Smoothing must never hide raw points or alter a decision boundary.

---

# 11. Structural observables

A structural object is admissible only with a stable identity and creation rule. Required observables include:

- number and type of states/units/clusters/rules/concepts;
- creation, deletion, split, merge, promotion, demotion, and fracture events;
- trigger quantities in coherent units;
- description-length or complexity cost and predictive benefit;
- support, contradictions, occupancy, stability, and lifetime;
- origin classification: initialized, designer-injected, learned, random/control-generated, or unknown;
- persistence across checkpoints and seeds;
- functional ablation and rescue effects;
- matched-capacity and shuffled-input comparisons.

A force-directed network drawing without these fields is prohibited.

---

# 12. Attention observables

Attention is operationalized as limited allocation among explicit alternatives. Required observables:

- candidate set available at allocation time;
- raw scores and normalized weights;
- allocation entropy/concentration and saturation;
- cue inputs and whether they are permitted under protocol;
- weight-to-update or weight-to-decision coupling;
- latency/compute cost;
- matched uniform, random, and cue-shuffled controls;
- downstream outcomes under intervention or ablation.

Until these exist, “attention” should not be displayed. Current loss-triggered replay is a gate, not automatically an attention mechanism.

---

# 13. Emergence observables

Emergence requires all of the following:

- target structure absent at initialization under a declared test;
- treatment operability and actual activation;
- structure definition independent of favorable outcome access;
- held-out predictive or behavioral contribution;
- complexity/description-length accounting;
- persistence and reproducibility;
- fixed-capacity, random-growth, error-decoupled, shuffled-input, and matched-complexity nulls as relevant;
- audit of designer injection and trivial statistical structure;
- lesion/rescue evidence when a mechanism is claimed;
- scoped negative/adverse outcome and explicit rejection rule.

The current Observatory must show E0 as “invalid target test: zero growth events; H* untested.” It must not show an emergence trajectory from legacy structural code as scientific evidence.

---

# 14. Failure observables

Failures must be typed by scientific consequence:

| Failure class | Examples | Scientific disposition |
|---|---|---|
| Treatment failure | gate/growth/lesion never occurs | invalid for target effect; valid methodological evidence |
| Measurement failure | metric unavailable, floor/ceiling, wrong unit/sign | quarantine dependent evidence; open debt/Unknown |
| Provenance failure | dirty code, missing hash/artifact, unknown dataset | ineligible for confirmation; may remain exploratory/methodological |
| Comparison failure | resource, data, compute, information, or opportunity mismatch | causal attribution prohibited |
| Randomness failure | seed reuse, coupled RNG, wrong experimental unit | uncertainty invalid or scope narrowed |
| Data/environment failure | leakage, infeasible task, distribution drift | claim scope invalid or alternative remains live |
| Numerical failure | NaN, overflow, saturation, nonconvergence | locate first divergence; assess whether systematic |
| Instrumentation failure | missing/duplicated/out-of-order events, observer perturbation | affected observable unavailable; do not impute |
| Runtime failure | crash, truncation, resume mismatch | abandoned/invalid unless protocol permits |
| Inference failure | wrong pairing, multiplicity/stopping/exclusion drift | result cannot trigger planned Decision |

Every failure view must show earliest onset, affected objects, scope of contamination, salvageable methodological evidence, and the next cheapest diagnostic.

---

# 15. Validation observables

Validation observables must answer whether the **claim**, not the interface, passes:

- preregistration identity and access boundary;
- frozen hypothesis, estimand, primary outcomes, guardrails, and adverse outcome;
- experimental unit and pairing;
- prospective precision/power or stopping rule;
- SESOI/equivalence margin where relevant;
- complete assignment and attrition;
- exclusions/deviations and whether they were planned;
- multiplicity handling;
- assumption/diagnostic checks;
- effect magnitude and uncertainty;
- independent replication and independence cluster;
- untouched confirmation seeds/data/worlds;
- construct, internal, and external validity separately;
- result class: valid positive, valid negative, valid indeterminate, invalid, or abandoned.

No green “validated” badge is permitted without a Decision record and complete traceability.

---

# 16. Causal observables

Causal displays require explicit intervention semantics:

- causal question and estimand;
- assignment mechanism;
- treatment delivery and manipulation check;
- baseline and credible alternatives;
- pre-treatment covariates/state;
- matched resource and information budgets;
- temporal order;
- mediator measurement before outcome;
- lesion, shuffle, block, rescue, and dose where relevant;
- contamination and interference checks;
- paired outcome contrasts with uncertainty;
- remaining causal alternatives.

The Observatory must distinguish:

- **association:** variables co-vary;
- **temporal relation:** one precedes another;
- **intervention effect:** assigned manipulation changes outcome;
- **mechanism evidence:** intervention and mediator/lesion evidence discriminate the proposed pathway.

---

# 17. Scientific overlays

Overlays are governed annotations on the same underlying objects. They may be combined, and each must be independently switchable and provenance-linked.

| Overlay | What it reveals | Required source |
|---|---|---|
| Scientific phase | Discovery, Validation, publication projection | experiment/record phase |
| Evidence class | observation, derived metric, evidence, interpretation, Decision | SKB type |
| Validity | positive, negative, indeterminate, invalid, abandoned | execution validity |
| Admissibility | exploratory, confirmatory eligible/ineligible, methodological only | provenance and phase gates |
| Uncertainty | intervals, seed/world variation, missingness | statistical/measurement record |
| Confounders | unmatched resources, information, decay, opportunity, exposure | design/comparability audit |
| Treatment fidelity | intended vs realized intervention | event stream/protocol |
| Provenance | code/config/runtime/data/seeds/artifact digests | manifest/inventory |
| Resource budget | data, updates, replay, memory, compute, time | realized budget records |
| Negative knowledge | scoped negative and methodological failures | NEG/EVD/DEC records |
| Assumptions | load-bearing active/contradicted assumptions | ASM records and dependencies |
| Unknowns | priority, resolution criterion, blockers | UNK records |
| Scientific debt | B1–B4 block and prohibited claims | SDEBT records |
| Designer injection | initialized/injected/learned/unknown origin | bias/injection audit |
| Controls | null, shuffle, random, lesion, rescue, matched alternative | protocol and assignments |
| Independence | shared code/data/world/assumptions/investigator cluster | evidence synthesis record |
| Scope | environment, task, population, time, transfer boundary | claim/evidence scope |
| Supersession | lineage and current authority | typed supersession edges |
| Decision impact | which decision each object can change/reverse | experiment/Decision records |
| Instrumentation status | available, partial, gated, corrupt | object contract audit |

Overlays must never change raw values; they qualify their interpretation.

---

# 18. Experiment workflow

## 18.1 Before execution

1. Select the target Unknown and show its dependency breadth.
2. State the smallest decision that could change.
3. Link a falsifiable hypothesis or explicit measurement/readiness claim.
4. Enumerate credible alternatives and the outcome that discriminates among them.
5. Choose the cheapest adequate baseline/control set.
6. Freeze phase-appropriate protocol, measurements, invalidity criteria, budgets, seeds/worlds, and event schema.
7. Run an **Observability Readiness Check**:
   - every primary outcome has a source;
   - treatment delivery is observable;
   - resources and information are countable;
   - required object identities persist across the run;
   - missingness states are distinguishable;
   - observer perturbation is bounded;
   - raw-to-plot transformations are reproducible.
8. For Validation, freeze preregistration and access controls.

## 18.2 During execution

1. Display run identity and eligibility before live metrics.
2. Monitor treatment fidelity, budget, missing events, truncation, and validity threats.
3. Permit drill-down to raw events without exposing confirmatory outcomes early.
4. Trigger stop rules only from preregistered or safety/validity conditions.
5. Record all deviations as immutable events.

## 18.3 After execution

1. Seal raw artifacts and inventory digests.
2. Classify execution validity independent of favorability.
3. Generate observations without causal language.
4. Construct planned contrasts and uncertainty.
5. Compare alternatives and expose residual confounding.
6. Create evidence relations to each affected claim.
7. Make a Scientific Decision: Accept, Reject, Revise, Split, Merge, Archive, Supersede, or No Verdict.
8. Propagate changes through assumptions, Unknowns, debt, roadmap, and Living Scientific Model.
9. Preserve negative, invalid, abandoned, and partial outcomes.
10. Confirm that every displayed result resolves to its immutable inputs.

---

# 19. Research workflows

## 19.1 Discovery workflow — find a discriminating signal

`Unknown → minimal contrast → pilot → treatment/measurement check → effect pattern → alternatives → decide whether Validation is worth its cost`

Default views: uncertainty map, comparability matrix, treatment raster, learning/retention surface, failure topology.

## 19.2 Measurement-calibration workflow

`Construct → operational definition → positive control → negative control → perturbation test → known-failure sensitivity → competing metric → accept/retire/bound`

Immediate P1 use: forgetting construct (`UNK-2026-0003`) and E0 trigger metrology (`UNK-2026-0005`).

## 19.3 Mechanism-discrimination workflow

`Observed effect → matched baseline → alternative mechanism → lesion/shuffle → rescue → mediator timing → scoped causal Decision`

Immediate P1 use: historical replay versus resource bundle; surprise timing versus matched random/boundary timing.

## 19.4 Failure investigation workflow

`Failure object → earliest onset → affected validity dimension → matched successful/control history → minimal reproduction → salvage methodological evidence → repair or stop`

The workflow ends with an experiment validity disposition, not merely a closed engineering ticket.

## 19.5 Replication workflow

`Source execution → frozen reconstruction contract → independent environment/runtime as planned → normalized artifact comparison → effect replication → heterogeneity analysis → Decision`

Exact deterministic identity and scientific effect replication are distinct questions and need distinct views.

## 19.6 Negative-result workflow

`Adverse/null outcome → sensitivity/precision check → valid negative vs indeterminate → scope boundary → alternative explanations → NEG record → roadmap pruning`

## 19.7 Theory-formation workflow

`At least two independently validated hypotheses → candidate explanatory relation → simpler alternatives → novel risky prediction → theory-discriminating experiment → admission/rejection`

This workflow is currently locked because P1 has no validated constituent mechanism.

## 19.8 Scientific triage workflow

At any point, scientists should be able to sort candidate actions by:

- expected probability of changing a major Decision;
- uncertainty reduction;
- dependency breadth;
- discriminative power;
- feasibility/cost;
- risk of delay;
- existence of a cheaper similarly informative observation or experiment.

---

# 20. Human interaction model

## 20.1 Scientist-centered interaction

The primary interaction is **question → evidence path**, not menu → chart.

A scientist begins with one of nine questions:

1. What is happening now?
2. Why did this event occur?
3. What changed after this event?
4. What differs between these conditions?
5. What does this result count as evidence for or against?
6. What could still explain it?
7. What failed, and does the target hypothesis remain tested?
8. What is currently blocked?
9. What should we test next?

The Observatory responds by selecting actual objects and preserving the evidence chain.

## 20.2 Selection semantics

Selecting any mark opens a scientific inspector containing:

- object identity/type/source;
- exact value/state and definition;
- raw contributing records;
- phase, validity, admissibility, and uncertainty;
- assumptions/confounders/missingness;
- linked experiment, evidence, hypothesis, Unknown, debt, and Decision;
- available parent/child zoom transitions;
- permissible actions.

## 20.3 Comparison interaction

Scientists can pin objects or executions and compare them only when the Observatory shows:

- matching keys;
- unmatched dimensions;
- paired unit mapping;
- normalization/transformation;
- whether the comparison is descriptive or causal.

## 20.4 Annotation discipline

Human annotations are typed:

- question;
- candidate interpretation;
- alternative explanation;
- anomaly;
- exclusion proposal;
- protocol deviation;
- Decision proposal.

Annotations never mutate raw data or canonical status. Decision-bearing changes require permanent records and supersession.

## 20.5 Outcome-access protection

For confirmatory work, the interface must support role- and phase-appropriate masking of confirmation outcomes until the protocol permits access. Discovery exploration remains flexible but visibly exploratory.

## 20.6 Interaction boundaries

The Observatory may:

- filter, compare, trace, annotate, export a reproducible view specification, and launch a governed experiment request.

It may not:

- rename implementation objects as cognitive constructs;
- silently recompute primary outcomes;
- edit raw events;
- change hypothesis status directly;
- imply causality through layout;
- manufacture a neuron/connection/attention state when not instrumented.

## 20.7 Collaboration

Every shared view carries:

- scientific-state version;
- query/filter/overlay specification;
- source artifact digests;
- transformation versions;
- visible annotations and their authorship/time;
- whether the view includes post hoc exploration.

Thus two scientists can reproduce not just the data, but the exact evidential view.

---

# 21. Scientific acceptance criteria

The Observatory is scientifically acceptable only if all **instrument-level** criteria pass and each visualization passes the **view-level** criteria.

## 21.1 Instrument-level acceptance

### A. Truth and traceability

- [ ] 100% of displayed objects resolve to an actual canonical or run-local record.
- [ ] 100% of displayed derived values expose definition, version, inputs, and transformation.
- [ ] Every claim status resolves to evidence relations and a Decision.
- [ ] Missing, unavailable, not observed, and not applicable states are distinct.
- [ ] Unsupported levels, including current neuron/connection views, render as unavailable rather than inferred.

### B. Epistemic discipline

- [ ] Observation, metric, evidence, interpretation, and Decision are visually distinct.
- [ ] Exploratory and confirmatory evidence cannot be confused.
- [ ] Invalid executions cannot enter target-effect synthesis.
- [ ] Negative results and methodological failures have equal discoverability.
- [ ] No supported theory is shown while the Theory Registry has none.

### C. Experimental validity

- [ ] Intended and realized treatments are both inspectable.
- [ ] Condition comparisons expose unmatched resources, data, opportunity, memory, information, decay, and compute.
- [ ] Experimental units, pairing, independence clusters, exclusions, and deviations are visible.
- [ ] Primary outcomes show effect magnitude and uncertainty, not only ranks or point values.
- [ ] Validation displays enforce the frozen decision rule and confirmation-access boundary.

### D. Reproducibility and provenance

- [ ] Every execution view includes protocol/config/code/runtime/data/world/seed identity and artifact inventory.
- [ ] A view can reproduce every mark from sealed artifacts.
- [ ] Dirty/untracked or incomplete runs are visibly ineligible for confirmation.
- [ ] Deterministic identity comparisons declare normalized nondeterministic fields.
- [ ] First-divergence tracing works for nominally identical histories when state checkpoints exist.

### E. Non-interference and performance

- [ ] Observer collection is demonstrated not to alter decision-relevant trajectories within the declared tolerance or is classified as an intervention.
- [ ] Collection overhead and dropped-event rate are measured.
- [ ] No primary observable silently samples, truncates, or smooths data.
- [ ] Degraded instrumentation changes status to partial/unavailable and blocks affected interpretations.

### F. Scientific decision utility

In scientist testing using representative P1 questions:

- [ ] A scientist can identify the target Unknown and current blocker for a claim.
- [ ] A scientist can determine whether a treatment occurred.
- [ ] A scientist can identify all unmatched dimensions in a claimed contrast.
- [ ] A scientist can trace a displayed outcome to raw events and onward to the Decision.
- [ ] A scientist can determine what result would reverse the current Decision.
- [ ] A scientist can choose the next minimal discriminating experiment without relying on implementation prominence.

## 21.2 Per-visualization admission test

A visualization is admitted only if all answers are concrete:

1. Why should it exist?
2. Which scientific question does it answer?
3. Which registered hypothesis, assumption, validity claim, or theory prediction can it test?
4. Which engineering failure can it diagnose without conflating engineering conformance with scientific evidence?
5. Which scientific decision becomes easier?
6. What actual objects and fields supply every mark?
7. What missingness, confounding, and uncertainty must be visible?
8. What cheaper representation was considered, and why is visualization better?
9. Can an independent scientist reproduce it exactly?
10. What false inference might it encourage, and how is that prevented?

Failure on any item keeps the visualization out of the Observatory.

## 21.3 Current-state launch gate

Before the Observatory can be treated as a scientific instrument rather than a development display, it must demonstrate on real P1 records:

1. faithful projection of SKB v1.1 and the explicit absence of supported theory;
2. correct rendering of the M1 smoke run as completed but dirty/untracked and confirmatory-ineligible;
3. traceability from one `steps.csv` event to aggregate metrics and the run manifest;
4. a comparability view that exposes the current replay resource bundle;
5. a retention view that marks legacy forgetting as primary-outcome-ineligible and shows mastery/final excess/plasticity jointly;
6. an E0 view that shows zero treatment activation and refuses inference against H*;
7. explicit unavailable states for neuron, connection, full attention, item-level memory, and full-state divergence views;
8. successful known-failure tests: corrupted artifact, missing event, dirty run, mismatched condition budget, and absent treatment must all be detected and correctly classified.

---

# 22. Initial scientific priority for Observatory instrumentation

Instrumentation should be sequenced by uncertainty reduction, not visual ambition.

## Priority 0 — Evidence admissibility

Implement truthful projection of run provenance, artifact integrity, scientific phase, validity, and SKB traceability. This directly supports `UNK-2026-0010` and the M1 readiness gate.

## Priority 1 — Minimal causal replay assay

Expose event timing, task boundaries, loss, gate fires, replay requests/realization/shortfall, update counts, buffer occupancy, probes, mastery, final excess loss, plasticity, and matched condition budgets. This supports `UNK-2026-0003`, `UNK-2026-0002`, and `UNK-2026-0001`.

## Priority 2 — Memory content and history lineage

Add stable memory item identity, source-task custody, selection, eviction, lesion, and contribution records. Without these, “historical replay” and “historical carrier” remain only partially observable.

## Priority 3 — Structural operability

Add coherent-unit growth trigger values, candidate/accepted structural changes, origin classification, complexity cost, support, and control comparison. Do not prioritize neuron graphics before H* treatment operability.

## Priority 4 — Attention, unit, and connection mechanisms

Instrument only after a registered hypothesis makes those levels decision-relevant. No current P1 Decision requires a generic neuron or connection map.

## Priority 5 — Theory view

Enable only after Theory Registry admission criteria are met. Until then, show the explicit absence and the validated constituents still required.

---

# 23. Present canonical interpretation the Observatory must preserve

At specification date, the Observatory must truthfully communicate:

- P1 is in Discovery.
- No mechanism is validated.
- No supported P1 theory exists.
- Exact-keyword semantic inference and the tested R1 free-energy advantage have scoped negative evidence.
- Historical calibration has a hard observed failure but no population estimate.
- E0 did not instantiate growth, so H* remains untested.
- M0/M1 replay signals are confounded; surprise timing is unidentified.
- M1 local conformance is positive engineering evidence, but current provenance and gate validity block confirmatory evidence.
- The immediate gate is clean committed reconstructability and live-surface evidence eligibility.
- After readiness, forgetting construct validity and matched-random replay timing are the highest-value scientific discriminators.

Any Observatory state that visually overrules these statements without new canonical Evidence and Decision records is scientifically invalid.

---

# 24. Final design principle

The Observatory succeeds when it makes P1 easier to disprove, diagnose, and revise.

Its highest-value view is not the one that makes the system look most alive. It is the one that most clearly reveals:

- what actually happened;
- what did not happen;
- what was measured;
- what remains confounded;
- what the evidence can and cannot support;
- which decision follows;
- and which smallest next experiment would change that decision.

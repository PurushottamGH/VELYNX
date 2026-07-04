# PROGRAM D — IMPLEMENTATION GAPS

**Authority:** Derives from `PROGRAM_D_CANONICAL.md`. Every gap is a concrete blocker preventing correct implementation, verified against the repository at 2026-07-03. Each is one of: **missing definition, missing interface, missing API, missing metric, missing schema, missing config, missing data, missing experiment, missing test** — or a **contradiction** (a live document/registry/code path that asserts a [REJECTED] object; canonical §9 makes these defects, not options).
**Ranking:** by implementation impact — **BLOCKER** (nothing correct can be built/run until fixed) > **HIGH** > **MEDIUM** > **LOW**. Within a tier, keystone-I2 items rank first (canonical §4).
**Verification:** each gap cites the file/line evidence found in-repo and the canonical section it violates, plus the backlog ID that closes it.

---

## Tier 0 — BLOCKERS (correctness-fatal; must close before any experiment runs)

### G-01 · Contradiction · [REJECTED] free-energy `E` is in the live E0 path
- **Type:** Contradiction (rejected math in a load-bearing execution path).
- **Evidence:** `experiments/E0/run.py:39,46,53` calls `collector.compute_free_energy(entropy=…, surprise=…, structural_load=…)` — this is `E=λH+μS+νA`. E0 is the experiment that *decides H\**.
- **Violates:** canonical §5 (E permanently removed; log score is the sole loss), §8 (E delivers no measurable benefit, R1 p=0.866), §1 rule 5.
- **Impact:** the H\* decider computes a rejected, unit-incommensurate quantity instead of `L=−log P_θ`. Any E0 result is invalid.
- **Closes with:** E0-09 (purge), CORE-02 (log score). **CI guard:** grep-gate banning `free_energy`/`compute_free_energy` in `experiments/` + `core/`.

### G-02 · Missing definition · MDL `λ_model` not implemented as `k·b+n·log₂N`
- **Type:** Missing definition (the one load-bearing derivation, canonical §5.4).
- **Evidence:** `core/mdl/mdl_growth.py` uses `model_cost = model_params*log(n)/2` (BIC form) and `mdl_gain(..., lambda_model=1.0)` (hand-set default). `parameter_registry.yaml` lists `mdl.lambda_model: configurable`.
- **Violates:** §5.4 and §10 Issue-3 — a hand-set/configurable λ is failure-mode **F2** and violates keystone **I2** by construction.
- **Impact:** the growth trigger is not a derivation; "emergence" via this trigger is unfalsifiable. Fatal to H\*.
- **Closes with:** CORE-03 (wire `k·b+n·log₂N` from the concept-birth ledger), RC-07 (registry pin). **Test:** assert `λ_model==k*b+n*log2(N)` and that it is not readable from any config.

### G-03 · Missing experiment · `experiments/EXP-0/` does not exist at the canonical path
- **Type:** Missing experiment (the immediate next action, canonical §11).
- **Evidence:** repo has `experiments/EXP0/` (legacy, with EXP0_* docs) and an empty `experiments/E0/` that only wraps free-energy metrics. `IMPLEMENTATION_BLOCKERS.md §1` confirms EXP-0 is missing from the manifest. The canonical precondition experiment is not runnable as specified.
- **Violates:** §7 EXP-0, §11.
- **Impact:** the deployed system keeps claiming its 100/100 headline; no precondition gate exists.
- **Closes with:** EXP0-01..06. **Note:** legacy `EXP0/` assets (paraphrases.json, detectors.py) are reusable inputs but the state-reset harness (EXP0-03) is the missing core.

### G-04 · Missing test · no state-reset guarantee for EXP-0 (Hebbian leakage)
- **Type:** Missing test / missing interface.
- **Evidence:** no code asserts `graph_wiped:true` before each trial; `EXPERIMENT_INTERFACE_SPEC §4` *requires* it but nothing implements it.
- **Violates:** §7 EXP-0 ("wipe semantic graph + episodic memory each trial; no Hebbian leakage").
- **Impact:** without a verified wipe, paraphrase trials leak learned weights across conditions → EXP-0 result invalid.
- **Closes with:** EXP0-03. **Test:** per-trial `graph_wiped` flag + state-hash reset assertion.

### G-05 · Contradiction · H3 / EXP-3 / EXP-4 still live across four documents + registry
- **Type:** Contradiction (rejected hypothesis resurrected).
- **Evidence:** `HYPOTHESIS_REGISTER.md` H3 block + "Experimental protocol: EXP-3"; `EXPERIMENT_PROTOCOLS.md` EXP-3 section; `repository_v2.md:68–69` builds `experiments/EXP3|EXP4`; `migration_plan.md:32–33` + `implementation_checklist_v1.md:20` create them; `experiment_registry.yaml` lists EXP3/EXP4 with `hypothesis: H3`.
- **Violates:** §6-H3 ([REJECTED]/subsumed), §10 Issue-1, §1 rule 2 (no subsystem without a live experiment needing it).
- **Impact:** engineers would build two experiments that test a rejected hypothesis; two names for one claim is duplicate complexity.
- **Closes with:** RC-01, RC-02, RC-04, RC-05, RC-06.

---

## Tier 1 — HIGH (blocks a specific experiment or the keystone; close in M0/M1)

### G-06 · Contradiction · EXP-2 wired to the 32 authored soul concepts
- **Type:** Contradiction (circularity confound into the only novel result).
- **Evidence:** `repository_v2.md:152–158` makes `program_b/soul_graph`+`concepts.json` a required EXP-2 input; `experiment_registry.yaml` EXP2 `components: [program_b/]`.
- **Violates:** §6-H2 circularity guard, §10 Issue-6.
- **Impact:** testing affect on environments authored around the same affect categories reintroduces designer injection into H2 — the one [PN] result becomes uninterpretable.
- **Closes with:** RC-04, EXP2-01, EXP2-02 (forbid `program_b` imports; third-party task set).

### G-07 · Contradiction · anthropomorphic + rejected modules in the live skeleton
- **Type:** Contradiction (anthropomorphism; designer artifacts as live mechanism).
- **Evidence:** `repository_v2.md:178` `program_c/self_model/`; `migration_plan.md:57,64` create `program_c/self_model`, `infra/app/soul`; `implementation_checklist_v1.md:28` lists `self_model`; live tree exposes `soul`, `belief*`, `curiosity`, `dream_state`, `monologue`.
- **Violates:** §5 (rejected list), §9-DeepSeek (rename/archive anthropomorphic live modules), §1 rule 5.
- **Impact:** rejected mechanisms remain importable and could re-enter an experiment path; names violate the constitution.
- **Closes with:** CORE-06 (archive), CORE-07 (rename), RC-04, RC-05.

### G-08 · Missing metric · null-referenced `M` exists in isolation but is not wired to E0 DV-b
- **Type:** Missing API / integration gap (the keystone metric).
- **Evidence:** `core/emergence/null_referenced_test.py` + `emergence_statistic.py` implement NMI and a null-referenced statistic, but `experiments/E0/run.py`/`analysis.py` emit `free_energy`, not `M`. No E0 analysis computes `NMI(learned,true)−NMI(learned,shuffled)`.
- **Violates:** §5.5, §6-H\* DV-b, §4 (I2 operationalization).
- **Impact:** E0 cannot test clause (iii)/I2 — the crux and the only clause the built system provably fails. Without DV-b wired, H\* is untestable.
- **Closes with:** E0-08, CORE-04. **Test:** `E[M|H₀]≈0` on shuffled input.

### G-09 · Missing data · no verified nonlinear-latent environment for E0
- **Type:** Missing data / missing definition.
- **Evidence:** `experiments/E0/dataset.py` absent; `run.py` uses a `sin()` toy stream, not a K-state nonlinear-latent generator; no offline check that a linear predictor cannot recover the latent. RESEARCH_STATE notes the only tested env (cube corners) is linearly separable and did not generalize.
- **Violates:** §7 E0 ("nonlinear-latent stream verified offline so a linear/fixed-capacity predictor cannot recover the latent"), assumption I3.
- **Impact:** without a verified-nonlinear env, H\* is vacuously true or untestable (failure-mode F1).
- **Closes with:** E0-01, E0-02.

### G-10 · Missing controls integration · C1/C2/C3 not driven by E0
- **Type:** Missing API (controls exist, not invoked).
- **Evidence:** `core/controls/{fixed_capacity,random_growth,shuffled_input}.py` exist as classes, but E0 `run.py` runs a single condition (no T/C1/C2/C3 harness).
- **Violates:** §7 E0 (four conditions), §6-H\* (must beat C1 **and** C2).
- **Impact:** no comparison conditions → no kill decision possible.
- **Closes with:** E0-03..06, CORE-05.

### G-11 · Missing test · no wired kill-decision module for any hypothesis
- **Type:** Missing test / missing API.
- **Evidence:** no `decision.py` in `experiments/E0`, `EXP-1`, `EXP-2`. Kill criteria exist only as prose. `foundation/kill_criteria/kill_criteria.md` is documentation, not executable.
- **Violates:** §1 rule 3, §6 (each hypothesis has a *wired* kill), §7.
- **Impact:** "wired kill criterion" is the constitutional requirement distinguishing a feature from a delete-candidate; absent it, results can't falsify.
- **Closes with:** E0-13/E0-14, EXP1-06, EXP2-05.

### G-12 · Missing metric · 5 of 6 primary metrics remain unmeasurable (observability gap R-2)
- **Type:** Missing metric / missing instrumentation.
- **Evidence:** RESEARCH_STATE R-2: HeldOutPredictiveLogLikelihood, RareEventRecall, KnowledgeRetentionScore, GeneralizationScore, TransferScore all unmeasurable; `core/measurement/observability.py` referenced by plans but absent.
- **Violates:** §7 E0 ("instruments ≥1 of the 5 currently-unmeasurable primary metrics").
- **Impact:** most hypotheses cannot be tested at all until at least held-out LL is instrumented.
- **Closes with:** E0-10 (instrument HeldOut LL first), E0-07.

---

## Tier 2 — MEDIUM (blocks reproducibility/product gate; close in M1–M3)

### G-13 · Missing schema/config · `λ_model` exposed as a tunable in the interface spec
- **Type:** Missing schema constraint (contradiction with §5.4).
- **Evidence:** `EXPERIMENT_INTERFACE_SPEC.md` `experiment_config.json` exposes `scientific_parameters.mdl_b_constant` / `mdl_n_multiplier` as free config; `parameter_registry.yaml` `mdl.lambda_model: configurable`.
- **Violates:** §5.4, §10 Issue-3, IMPLEMENTATION_BLOCKERS §2 ("exposing this as a tunable float is a critical failure"). Note `b` is a fixed per-parameter bit cost from the ledger, and `n·log₂N` is data-derived — neither is a sweepable knob.
- **Impact:** invites hyperparameter tuning of the growth trigger = Goodhart/F2.
- **Closes with:** RC-07, CORE-03. **Test:** config schema rejects any override of the derived λ.

### G-14 · Missing config · single ECE gate not encoded (0.10 vs 0.15 dead-zone)
- **Type:** Missing config / contradiction.
- **Evidence:** `PROGRAM_D_SPECIFICATION.md §3-H1` still references the retired kill "ECE > 0.15" alongside the pass "< 0.10".
- **Violates:** §6-H1, §10 Issue-4 (single gate `<0.10`).
- **Impact:** a 0.10–0.15 dead-zone leaves the calibration claim simultaneously un-passed and un-killed — unfalsifiable slack.
- **Closes with:** RC-03, EXP1-06.

### G-15 · Missing data · EXP-1 has no ≥200-query set with ground truth
- **Type:** Missing data.
- **Evidence:** `experiments/EXP1/` contains only `__init__.py`; no `queries.jsonl`.
- **Violates:** §7 EXP-1 (≥200 mixed queries: facts, ambiguous, hallucinations).
- **Impact:** the priority-1 product gate cannot run.
- **Closes with:** EXP1-01.

### G-16 · Missing API · no BM25/TF-IDF random-confidence control for EXP-1
- **Type:** Missing API (control).
- **Evidence:** no `control_bm25.py`; H1 control specified but unimplemented.
- **Violates:** §6-H1 control, SCIENTIFIC_VALIDATION_MATRIX.
- **Impact:** without the control, tier-independence cannot be rejected → ECE alone is not sufficient for the claim.
- **Closes with:** EXP1-04.

### G-17 · Missing data · EXP-2 has no third-party task battery
- **Type:** Missing data.
- **Evidence:** `experiments/EXP2/` empty; `EXPERIMENT_INTERFACE_SPEC.md` shows only a single toy task example.
- **Violates:** §6-H2 circularity guard, §7 EXP-2.
- **Impact:** H2 (the only possibly-novel question) cannot be tested without isolated tasks.
- **Closes with:** EXP2-01.

### G-18 · Missing interface · no central PRNG registry; deep seed calls likely present
- **Type:** Missing interface.
- **Evidence:** `EXPERIMENT_INTERFACE_SPEC §5` mandates a single PRNG and forbids deep `np.random.seed()`; no such registry exists; controls each take an ad-hoc `seed`.
- **Violates:** reproducibility requirements (§7 frozen code), EXPERIMENT_INTERFACE_SPEC §5.
- **Impact:** non-reproducible runs; env seed not separable from agent seed → confounds E0.
- **Closes with:** E0-11.

### G-19 · Missing test · no CI grep-gate banning rejected symbols
- **Type:** Missing test.
- **Evidence:** `.github/` present but no gate asserting absence of `free_energy`, `belief`, `self_model`, graph-isomorphism in live paths.
- **Violates:** §5, §9 (defect prevention).
- **Impact:** rejected constructs (G-01, G-07) can silently re-enter.
- **Closes with:** CORE-TEST + a CI job (extends CORE-02/06/07 acceptance).

---

## Tier 3 — LOW (hygiene; close opportunistically in M1/M6)

### G-20 · Contradiction · legacy coverage matrix maps rejected components
- **Evidence:** `experiments/program_d_experiment_coverage_matrix.csv` rows reference `SelfCoder`, `soul_graph.py`, `inertia_law`, `free_energy_vs_pareto`, `self_model.py`.
- **Violates:** §7, §5. **Closes with:** RC-08.

### G-21 · Missing API · `core/predictors/base.py` lacks a `grow()`/capacity interface
- **Evidence:** `base.py` defines `predict/update/entropy/reset/state_dict` but no capacity-index `k` or `grow()` method — yet §5.2 requires a class *indexed by capacity k*.
- **Violates:** §5.2. **Closes with:** CORE-01 (extend interface).

### G-22 · Missing docs → module drift · duplicated predictor/NMI logic across `validation/`, `research/`, `program_c/`
- **Evidence:** `parameter_registry.yaml` locates NMI/free-energy in `validation/metrics.py`; migration plan notes duplicate predictor logic in `predictive_core.py` + `vector_prediction_core.py`.
- **Violates:** §5 (one implementation of each primitive), repository_v2 "no duplication."
- **Closes with:** INFRA-07.

### G-23 · Missing config · no Dockerized immutable run environment
- **Evidence:** `docker-compose.yml` is 119 bytes (stub); no pinned-dependency image; `EXPERIMENT_INTERFACE_SPEC §6` requires containerized, version-locked runs.
- **Violates:** reproducibility. **Closes with:** PUB-04.

---

## Ranked closure summary

| Rank | Gap | Type | Milestone | Backlog |
|---|---|---|---|---|
| 1 | G-01 free-energy in E0 path | Contradiction | M1/M4 | E0-09, CORE-02 |
| 2 | G-02 λ_model not `k·b+n·log₂N` | Missing definition | M1 | CORE-03, RC-07 |
| 3 | G-03 EXP-0 missing | Missing experiment | M2 | EXP0-01..06 |
| 4 | G-04 EXP-0 state-reset | Missing test | M2 | EXP0-03 |
| 5 | G-05 H3/EXP-3/EXP-4 live | Contradiction | M0 | RC-01/02/04/05/06 |
| 6 | G-06 EXP-2 soul-concept dep | Contradiction | M0/M5 | RC-04, EXP2-02 |
| 7 | G-07 anthropomorphic live modules | Contradiction | M1 | CORE-06/07 |
| 8 | G-08 `M` not wired to DV-b | Missing API | M4 | E0-08, CORE-04 |
| 9 | G-09 no nonlinear-latent env | Missing data | M4 | E0-01/02 |
| 10 | G-10 C1/C2/C3 not driven | Missing API | M4 | E0-03..06 |
| 11 | G-11 no wired kill-decision | Missing test | M3/M4/M5 | E0-13/14, EXP1-06, EXP2-05 |
| 12 | G-12 observability gap R-2 | Missing metric | M4 | E0-10/07 |
| 13 | G-13 λ tunable in interface spec | Missing schema | M0/M1 | RC-07, CORE-03 |
| 14 | G-14 ECE dead-zone | Missing config | M0/M3 | RC-03, EXP1-06 |
| 15 | G-15 no EXP-1 query set | Missing data | M3 | EXP1-01 |
| 16 | G-16 no EXP-1 control | Missing API | M3 | EXP1-04 |
| 17 | G-17 no EXP-2 tasks | Missing data | M5 | EXP2-01 |
| 18 | G-18 no PRNG registry | Missing interface | M4 | E0-11 |
| 19 | G-19 no CI rejected-symbol gate | Missing test | M1 | CORE-TEST |
| 20 | G-20 legacy coverage matrix | Contradiction | M0 | RC-08 |
| 21 | G-21 predictor base lacks grow() | Missing API | M1 | CORE-01 |
| 22 | G-22 duplicated primitive logic | Drift | M1 | INFRA-07 |
| 23 | G-23 no Docker repro env | Missing config | M6 | PUB-04 |

**Blockers-first rule:** G-01 through G-05 (Tier 0) must close before *any* experiment result is trusted. Of these, G-05 closes in M0 (docs); G-01/G-02 close in M1 (core); G-03/G-04 close in M2 (EXP-0). No E0 or EXP-1/EXP-2 result may be reported while any Tier-0 gap is open.

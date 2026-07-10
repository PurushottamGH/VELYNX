# PROGRAM D — TRACEABILITY MATRIX

**Authority:** Derives from `PROGRAM_D_CANONICAL.md`. This matrix is the unbroken chain required by the objective:

> **Canonical Requirement → Scientific Hypothesis → Experiment → Implementation Module → Metric → Kill Criterion → Publication Claim.**

**Completeness rule:** nothing may be unmapped. Every canonical requirement resolves to a hypothesis (or an explicit `[REJECTED]`/precondition status), and every live hypothesis resolves all the way to a publication claim. Rows tagged **[REJECTED]** are retained *only* to prove they terminate — they must not appear in any live mechanism (canonical §0, §5, §6).
**Generated:** 2026-07-03.

---

## 1. Primary chain (live hypotheses)

### Row H\* — Error-Gated Structure Acquisition (central)

| Link | Value | Canonical source |
|---|---|---|
| **Canonical requirement** | I2 keystone: emergent structure must be operationally distinguishable from injected/statistically-trivial structure | §4 (I2), §1 |
| **Scientific hypothesis** | H\*: error-only learning + error-gated capacity growth acquires structure that (i) absent at init, (ii) beats fixed-capacity **and** error-decoupled controls on held-out prediction, (iii) not reducible to injected statistics | §6-H\* |
| **Experiment** | **E0** — minimal organism on nonlinear-latent stream; conditions T / C1 / C2 / C3; ≥5 seeds; frozen code | §7 E0 |
| **Implementation module** | `core/predictors/dirichlet_markov.py` (P_θ), `core/mdl/mdl_growth.py` (G, λ_model), `core/emergence/{emergence_statistic,null_referenced_test}.py` (M), `core/controls/{fixed_capacity,random_growth,shuffled_input}.py`, `experiments/E0/{dataset,run,analysis,decision}.py` | §5, §9-DeepSeek |
| **Metric** | DV-a: held-out predictive log-likelihood; DV-b: `M=NMI(learned,true)−NMI(learned,shuffled)`, `E[M|H₀]=0` | §5.3, §5.5, §6-H\* |
| **Kill criterion** | T fails to beat **both** C1 and C2 on DV-a at **p<0.01** across ≥5 seeds, **OR** DV-b within noise of shuffled control — after **two** honest attempts → **H\* falsified for this environment class** | §6-H\* kill |
| **Publication claim** | **If pass:** rigorous evidence of non-injected emergent representation + the I2 discrimination methodology. **If killed:** negative-result + methodology paper (designer-injection confound in "emergent cognition"). Prior on H₀ high (R1 null). | §8 honest path 1 |

### Row H1 — Retrieval Uncertainty Calibration (Program A product gate)

| Link | Value | Canonical source |
|---|---|---|
| **Canonical requirement** | Program A must be an honest product: confidence tiers must report empirical correctness matching the tier; must never present DEBATED/UNKNOWN as CERTAIN | §3 deliverable 1, Constitution §1 |
| **Scientific hypothesis** | H1: tiers CERTAIN/PROBABLE/DEBATED/UNKNOWN report empirical correctness matching the tier | §6-H1 |
| **Experiment** | **EXP-1** — ≥200 mixed queries (facts, ambiguous, hallucinations); reliability diagram | §7 EXP-1 |
| **Implementation module** | `program_a/retrieval/*`, `experiments/EXP1/{dataset,run,decision,calibration,rubric,report,manifest,artifact_specs,program_a_adapter}.py`. **UNIMPLEMENTED (deferred backlog):** `control_bm25.py` (EXP1-04 control, `IMPLEMENTATION_GAPS.md:126`), `goodhart_guard.py` (EXP1-05 active detector; canonical guard implemented passively via `calibration.py:20` locked bins + `decision.py:210` `protocol_violation` flag, per `EXP1_PREREGISTRATION.md` sections 2/4). ECE: `core/measurement/proper_scoring.py:42` (`expected_calibration_error`) + `experiments/EXP1/calibration.py` (`compute_ece`) | §9-DeepSeek, repository_v2 Program A; verified 2026-07-07 |
| **Metric** | Expected Calibration Error (ECE) + reliability diagram | §6-H1 |
| **Kill criterion** | **ECE ≥ 0.10** or tier-independence over the query set (single gate; 0.15 dead-zone retired). Goodhart guard: bin-boundary hacking is a violation, not a pass | §6-H1, §10 Issue-4 |
| **Publication claim** | **If pass:** Program A is an honest retrieval product (ECE<0.10). **If killed:** the "honest uncertainty" claim is rejected (currently [REJECTED] — CERTAIN on hallucinated Q6) | §8, SCIENTIFIC_VALIDATION_MATRIX |

### Row H2 — Affective Indexing (the one possibly-novel question)

| Link | Value | Canonical source |
|---|---|---|
| **Canonical requirement** | The only possibly-novel [PN] element must be tested honestly, free of the designer-injection/circularity confound | §3 deliverable 2, §8 |
| **Scientific hypothesis** | H2: a learned affective-framing → problem-solving-schema mapping improves **objective task outcomes** over an unframed baseline | §6-H2 |
| **Experiment** | **EXP-2** — objective tasks under affective-framed vs neutral prompts; unframed control; **third-party task set** | §7 EXP-2 |
| **Implementation module** | `experiments/EXP-2/{tasks,run,analysis,decision}.py`; **must not import** `program_b/soul_graph` or `concepts.json` | §10 Issue-6, §9-DeepSeek |
| **Metric** | Objective task success rate (debugging fixes / planning success) — **not** search-steps or compression ratio | §6-H2, §10 Issue-5 |
| **Kill criterion** | No significant task-outcome difference, **OR** schemas must be re-authored per task (circularity). Circularity guard: evaluate only on tasks the affect categories were **not** authored against | §6-H2 |
| **Publication claim** | **If pass:** affective framing as an index into problem-solving schemas (focused H2 paper). **If killed:** affective concepts are inert designer artifacts | §8 honest path 2 |

---

## 2. Precondition chain (tests the deployed system, not a hypothesis)

### Row EXP-0 — Benchmark Paraphrase (precondition)

| Link | Value | Canonical source |
|---|---|---|
| **Canonical requirement** | Stop the deployed system claiming its headline "semantic understanding" result before any H\* work | §11, §7 EXP-0 |
| **Scientific hypothesis** | *None* — EXP-0 audits the **old deployed system**, not H\* | §7 EXP-0 |
| **Experiment** | **EXP-0** — 64 interleaved trials (32 original "What is X?" vs 32 keyword-free paraphrases); wipe semantic graph + episodic memory each trial; no keyword/Porter-stem leakage | §7 EXP-0 |
| **Implementation module** | `experiments/EXP-0/{run_exp0,dataset,detectors,leakage_check,analysis}.py`, `paraphrases.json` | repository_v2, IMPLEMENTATION_BLOCKERS §1 |
| **Metric** | Concept-detection score, original vs paraphrase (Tier-1 embedding + Tier-2 lexical) | §7 EXP-0 |
| **Kill criterion** | If concept detection collapses to noise on paraphrases (predicted ~100/100 → ~4.0/10) → the "semantic understanding over a lookup table" claim is **falsified** | §7 EXP-0 |
| **Publication claim** | Paraphrase-collapse finding = one of the three headline findings of the negative-result + methodology paper | §8 honest path 1 |

---

## 3. Assumption → hypothesis → experiment traceability

Canonical §4 fixes exactly three irreducible assumptions. Each must trace to how it is attacked.

| Assumption | Class (canonical §4) | Depends-on hypothesis | Attacked by | If false |
|---|---|---|---|---|
| **I1** — prediction error is a sufficient signal to drive structure | [FACT] evidence-supported, weakly instantiated | H\* | E0 condition T (error-only learning) | No engine for development |
| **I2** — emergent structure operationally distinguishable from injected (**keystone**) | [REJECTED] as instantiated (~150 constants, 0 data-derived) | H\* clause (iii) | **E0 DV-b** (null-referenced `M`) — the first test wired to I2 | H\* unfalsifiable → Program D not science |
| **I3** — an environment rich enough to require non-trivial structure yet learnable, not hand-seeded/linear | [SPECULATION] | H\* | E0-02 offline nonlinearity check (linear predictor cannot recover latent) | H\* vacuously true or untestable |

**Catastrophe ranking I2 > I3 > I1** (§4). Program D's viability reduces to making **I2** true before "emergence" is used again → this is why E0/DV-b is the single most load-bearing implementation module.

---

## 4. Primitive → requirement traceability (canonical §5)

| Primitive | Symbol | Module | Requirement it satisfies |
|---|---|---|---|
| Observation stream | `x_t ∈ X` | `experiments/E0/dataset.py` | Given input to all predictors |
| Growable predictor class | `{P_θ(x_{t+1}|x_≤t):θ∈Θ_k}` | `core/predictors/dirichlet_markov.py` | H\* IV (capacity growth ON/OFF) |
| Proper scoring loss | `L=−log P_θ` (Bernardo-1979 unique) | `core/measurement/proper_scoring.py` | DV-a; permanently replaces `E=λH+μS+νA` |
| MDL growth operator | `G=H_before−H_after−λ_model`, **λ_model=k·b+n·log₂N** | `core/mdl/mdl_growth.py` + `concept_birth_ledger.py` | Error-gated growth trigger; derived not hand-set (avoids F2/I2 violation) |
| Emergence statistic | `M=NMI(learned,true)−NMI(learned,shuffled)`, `E[M|H₀]=0` | `core/emergence/*` | DV-b; operationalizes I2 (avoids F3) |

---

## 5. Terminating rows — [REJECTED] objects (must map to nothing live)

These prove the canon's rejected set terminates. Each row's "live target" **must** be empty; if any acquires a live module, that is a defect logged in `IMPLEMENTATION_GAPS.md`.

| Rejected object | Canonical status | Why rejected | Live target (must be ∅) | Archive/delete target |
|---|---|---|---|---|
| H3 (MDL-gated topology emergence) | [REJECTED]/subsumed by H\* | H\* minus clause (iii)/I2 — the exact weakening the redesign prevents | ∅ | archival cross-ref only (§6-H3, §10 Issue-1) |
| EXP-3 / EXP-4 | Removed from live set | Tested H3 | ∅ | drop from skeleton/registry (§7, §9-DeepSeek) |
| `E = λH + μS + νA` (+ CPI weights) | [REJECTED] | Unit-incommensurate; R1 null p=0.866; not Friston FEP/EBM | ∅ (currently violated in `experiments/E0/run.py` — GAP) | archive as R1 closed evidence (§5, §8) |
| Graph-isomorphism / topological-alignment `M` | [REJECTED] | Ill-defined for a probabilistic predictor; reopens researcher DOF (F3) | ∅ | delete (§5.5, §10 Issue-2) |
| Hand-set / configurable `λ` | [REJECTED] form | Hand-set trigger violates I2 by construction (F2) | ∅ (currently "configurable" in `parameter_registry.yaml` — GAP) | pin to ledger (§5.4, §10 Issue-3) |
| Inertia Law `η_eff=η_base·(1−stability)`, fracture 0.85, energy-exhaustion 18.0, contradiction-margin 0.9 | [REJECTED] | Designer-injected constants, no data derivation | ∅ | archive (§5) |
| 32 soul concepts / authored ontology / self-model / reasoning-engine type-lifting / resonance / sleep-replay / thermodynamic state | [REJECTED] | Designer artifacts; anthropomorphism | ∅ (self_model/soul still in live skeleton — GAP) | archive (§5, §9-DeepSeek) |
| EXP-2 dependency on `soul_graph`+`concepts.json` | [REJECTED] | Circular-logic confound into the only novel result | ∅ (still a dep in `repository_v2.md` — GAP) | remove dependency (§10 Issue-6) |

---

## 6. Publication-claim rollup (canonical §8)

| Outcome combination | Resulting publication | Venue (per §8) |
|---|---|---|
| EXP-0 collapse + E0 kills H\* | Negative-result + methodology paper: designer-injection confound, paraphrase-collapse, I2 null-referenced discrimination protocol | Negative-results / datasets-&-benchmarks track, TMLR, or workshop |
| E0 passes H\* | Above **plus** a positive claim of non-injected emergent representation (still cite owning prior art: Oudeyer, Weng, Rao–Ballard, ICM, RND) | Same tracks; H\* remains not-novel per §8 |
| EXP-2 finds signal | Focused paper: affective framing as an index into problem-solving schemas | Applied/venue TBD |
| EXP-1 passes | Program A shipped as an honest product (ECE<0.10) — engineering outcome, not the research center | Product, not a paper |

**Binding constraint (§8):** all four top venues desk-reject H\* as-is; no publication doc may tag `E`/Inertia Law/three-pressure scoring as "Novel/First"; owning prior art must be cited.

---

## 7. Coverage assertion

- **Live hypotheses covered end-to-end:** H\*, H1, H2 — 3/3 map requirement→…→publication claim (§1).
- **Precondition covered:** EXP-0 — 1/1 (§2).
- **Assumptions attacked:** I1, I2, I3 — 3/3 (§3).
- **Primitives mapped:** 5/5 (§4).
- **Rejected objects terminate:** 8/8 with live-target ∅ *required*; **4 currently violated** (free-energy in E0 path, configurable λ, self_model/soul in skeleton, soul-graph EXP-2 dependency) — each is an open GAP, not an accepted mapping (§5).

**No live hypothesis, experiment, primitive, or assumption is unmapped.** The only non-empty "live target" cells among rejected objects are defects, tracked to closure in `IMPLEMENTATION_GAPS.md` (M0/M1).

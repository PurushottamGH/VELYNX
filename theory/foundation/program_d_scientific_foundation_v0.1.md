# PROGRAM D — SCIENTIFIC FOUNDATION v0.1

**Role:** Principal Investigator. Standard: assume Program D is wrong until every claim survives hostile review.
**Date:** 2026-07-02.
**Builds on (canonical, not repeated here):** `PROGRAM_D_RESEARCH_STATE_v0.1.md`, `docs/VELYNX_v2_PI_Review.md`, `foundation/kill_criteria_validation.md`, `literature/program_d_mathematical_provenance.md`, `research/program_c_assumption_ledger.md`, `research/evidence_database.md`, `research/designer_injection_report.md`, `ablation_report.md` (R1).
**What this document adds that the canon did not:** it collapses the three prior hypotheses (H1/H2/H3) into **one** central hypothesis with full experimental scaffolding; reduces the assumption set to its irreducible keystone; strips the mathematics to necessity (and formally removes `E = λH + μS + νA`); delivers a field-by-field novelty verdict against the eleven named literatures; and reaches a single decision.

---

## PHASE 1 — CENTRAL HYPOTHESIS

Program D's identity — the reason it is a *research program* and not merely Program A (a retrieval product) or Program B (an authored artifact) — is the developmental/"mind" claim. Stated so it cannot hide in philosophy:

> **H\* (Central Hypothesis).**
> An agent whose **only** learning signal is sensorimotor prediction error, and which adds representational capacity **only** when prediction error persists, will acquire internal structure that
> **(i)** is absent at initialization,
> **(ii)** improves prediction on held-out data beyond a fixed-capacity control **and** a capacity-matched control whose growth is decoupled from error, and
> **(iii)** is **not reducible** to the statistics injected by the designer (i.e., it recovers latent generative structure the designer did not name, measured above a shuffled-input control).

Clause **(iii)** is the crux. It is the only clause the current system provably fails (`designer_injection_report.md`: ~150 constants, zero data-derived), and it is the clause that separates "development" from "a readout of priors." The prior operative hypothesis in `RESEARCH_STATE §6` ("exceeds baseline AND is not a readout of injected priors") is H\* with (i)+(ii) as *exceeds baseline* and (iii) as *not a readout*. H1 (calibration) and H2 (affective indexing) are **not** the central hypothesis — H1 is a product property, H2 is a candidate kernel; both are handled in Phase 8.

| Element | Definition |
|---|---|
| **Independent variable** | Presence/identity of the **error-gated capacity-growth operator** (ON vs. OFF/decoupled), holding the data stream, initialization, predictor class, and measurement fixed. Implementation-independent: it is *whether capacity is added as a function of persistent prediction error*, not any specific module. |
| **Dependent variables** | (a) Held-out predictive log-likelihood (proper scoring rule). (b) An **emergence statistic**: normalized mutual information between the agent's learned latent partition and the environment's true (withheld) latent generator, minus the same quantity under a shuffled-input control. Both are model-agnostic. |
| **Null hypothesis (H₀)** | The error-gated agent's held-out predictive LL is not distinguishable from the fixed-capacity and error-decoupled controls, **and** its learned-latent MI is within noise of the shuffled-input control. Any apparent structure is explained by input marginals + initialization + parameter count. |
| **Alternative (H₁)** | Error-gated growth strictly dominates both controls on held-out LL (pre-registered α), **and** learned-latent MI exceeds the shuffled control by a pre-registered margin. |
| **Expected effect** | Prior on H₀ is currently *high*. R1 (`ablation_report.md`) already shows the one instantiated growth/consolidation policy (free_energy) is statistically indistinguishable from `null` on the only measurable metric (RMSE 0.2991 vs 0.2951, p=0.866). H\* generalizes that test to a purpose-built organism and environment; absent a new environment that *demands* structure, H₀ is the base-rate expectation. |
| **Failure modes** | (F1) Environment is too easy → structure is trivially given by input statistics → (iii) is unsatisfiable and H\* is confirmed *vacuously* (the toy 4-regime cube-corner env, A-S01/A-E06, has this defect). (F2) Growth is uncoupled in practice (threshold hand-set) → (iii) violated by construction → not a test of H\*, a test of the designer. (F3) Emergence statistic has researcher degrees of freedom → any positive result is unfalsifiable. (F4) Observability gap (`RESEARCH_STATE §7 R-2`: 5/6 primary metrics unmeasurable) → the DVs cannot be computed → H\* is untestable in the current harness. |
| **Kill criteria (H\*-specific)** | H\* is **falsified** if, on an environment with verified non-trivial latent structure (F1 excluded), the error-gated agent (a) fails to beat the fixed-capacity **and** error-decoupled controls on held-out LL at p<0.01 across ≥5 seeds, **or** (b) its learned-latent MI does not exceed the shuffled-input control by the pre-registered margin — after **two** honest attempts. This is the operationalization of the program-level kill in `PI_Review Phase 5` (paraphrase-collapse ∧ no-emergent-structure). |

---

## PHASE 2 — ASSUMPTION COLLAPSE

The assumption ledger (`program_c_assumption_ledger.md`) and `RESEARCH_STATE §5–6` already classify ~20 registered + ~10 load-bearing assumptions. This phase does **not** re-list them; it asks a sharper question: *which assumptions does H\* actually stand on?* Everything H\* does not stand on is, by definition, not part of the foundation — its presence in the built system is the evidence that the built program was **too large**.

**Assumptions H\* does NOT require (therefore removed from the foundation):**
`E = λH + μS + νA` as free energy (SPECULATION / CONTRADICTED, A-CA02/A-E01); the CPI weights 0.40/0.30/0.20/0.10 (SPECULATION, A-CA06); half-maturity 4.0, EWMA alphas, exhaustion threshold 18.0 (SPECULATION, A-CA04/05); the 32 soul concepts and their edge labels (SPECULATION, B1/B2); hand-authored ontology grounds meaning (CONTRADICTED, A-O05/O07, D4); self-model = selfhood (SPECULATION, D3); arcs = reasoning (CONTRADICTED, B3); DirichletMarkov ≈ StableBelief (CONTRADICTED, A-O02). **Each is individually removable without touching H\*.** That is the collapse: the built system layered ~25 removable assumptions on top of a 3-assumption core, which is exactly why `PI_Review Phase 2` reduces the demonstrated organism to ~300 of ~30,000 lines.

**Irreducible assumptions (the foundation is exactly these three):**

| ID | Assumption | Class | Catastrophe if falsified | Removable? |
|---|---|---|---|---|
| **I1** | Prediction error is a sufficient and appropriate signal to *drive* representational structure. | **EVIDENCE-SUPPORTED** (predictive coding, self-supervised learning, developmental robotics) — but only WEAK *as instantiated here* (single-level, no hierarchy; `RESEARCH_STATE §5`). | Total: without a learning signal there is no engine for development. But the field-level support is strong, so the *risk* is low; the risk is in the instantiation, not the premise. | No — irreducible. An emergence claim needs a drive. |
| **I2** | "Emergent structure" is operationally **distinguishable** from injected/statistically-trivial structure. | **CONTRADICTED as of today** — the injection audit shows the current system cannot separate learned from given; clause (iii) is unmet. | **Maximal.** If I2 cannot be made true, H\* is *unfalsifiable* and Program D is not science. This is the keystone. | No — irreducible, and currently the single point of failure. |
| **I3** | An environment exists that is rich enough to *require* non-trivial structure yet learnable in feasible compute, and is neither hand-seeded nor linearly trivial. | **SPECULATION** — the only tested environment (cube corners) is linearly separable (A-S01) and does not generalize (A-E06). | Total: without such an environment, H\* is either vacuously true (F1) or untestable (F4). | No — irreducible, but it is a *design choice*, so it is addressable rather than fatal. |

**Ranking of catastrophe:** I2 > I3 > I1. Removing **I2** destroys the program (it becomes unfalsifiable); removing I3 makes it untestable; removing I1 removes the mechanism. All three are irreducible — you cannot state an emergence hypothesis without a drive (I1), a detector (I2), and a demanding environment (I3). Per the mission's test — *"if removing one assumption destroys Program D, Program D is too large"* — the built system was far too large (25 removable load-bearing assumptions). The reduced foundation is **not** too large: its three assumptions are each necessary and none is decorative. The honest state of the foundation is therefore: **I1 supported-but-weakly-instantiated, I3 addressable, and I2 currently false and un-instrumented.** Program D's entire scientific viability reduces to *making I2 true*.

---

## PHASE 3 — MATHEMATICAL FOUNDATION (software ignored)

Optimize for necessity, not elegance. For each primitive: *why must it exist / can it be derived / can it emerge / can it be removed.*

**Substrate that survives (five primitives):**

1. **Observation stream** `x₁, x₂, … , xₜ ∈ X`.
   *Why:* no data → no prediction → no H\*. *Derive:* no (given). *Emerge:* no. *Remove:* no. **Keep.**

2. **Growable predictor class** `{ P_θ(x_{t+1} | x_{≤t}) : θ ∈ Θ_k }`, indexed by capacity `k`.
   *Why:* H\*'s independent variable is capacity growth. *Derive:* the *form* (e.g., Dirichlet–Markov conjugate predictor, already correctly implemented per `RESEARCH_STATE §5`) is a modeling choice; the *requirement* of a growable class is not. *Emerge:* the parameters emerge; the class does not. *Remove:* no. **Keep** (reuse the existing conjugate predictor; discard the label "belief model").

3. **Proper scoring loss** `L = −log P_θ(x_{t+1} | x_{≤t})`.
   *Why:* H\*(ii) needs a metric that cannot be gamed by variance inflation. *Derive:* **yes** — the log score is (up to affine transform) the unique *local, strictly proper* scoring rule (Bernardo 1979); this is a derivation, not a choice. *Emerge:* no. *Remove:* no — **and it replaces `E = λH + μS + νA` permanently.** The energy proxy mixes bits (H) + Euclidean distance (S) + a count (A) with hand-tuned λ/μ/ν; it is unit-incommensurate (`RESEARCH_STATE §7 R-7`), is *not* Friston free energy (K9, A-CA02), and had no measurable benefit (R1). It is removed from the foundation with no replacement obligation beyond the log score. **Keep log-loss; remove E.**

4. **MDL-derived growth operator** `g : (Θ_k, error-history) → Θ_{k+1}`, triggered **iff** description length decreases:
   `G = H_before − H_after − λ_model > 0`, with `λ_model = k·b + n·log₂ N` (the concept-birth ledger, `provenance §2`).
   *Why:* H\* requires capacity to be added *as a function of persistent error* — and the trigger threshold **must not be hand-set**, or clause (iii)/I2 is violated by construction (failure mode F2). *Derive:* **yes** — MDL/Bayesian model selection derives *when* a new component pays for itself, replacing the arbitrary bits-threshold (0.5 vs 0.15, `RESEARCH_STATE §8 Q10`) with a principled comparison. This is the *only* piece of the built system that is both mathematically necessary and derivable. *Emerge:* the growth events emerge; the operator does not. *Remove:* no. **Keep — this is the load-bearing derivation.**

5. **Emergence statistic** `M(θ_k)`, constructed so that `E[M | H₀] = 0`.
   Concretely: held-out LL gain over the fixed-capacity control, and `NMI(learned partition, true latent) − NMI(learned partition, shuffled input)`.
   *Why:* this *is* I2 made operational; without it H\* is unfalsifiable. *Derive:* the estimator (NMI, held-out LL) is standard; the *null-referenced construction* is what makes it non-gameable. *Emerge:* no. *Remove:* no — removing it removes falsifiability. **Keep.**

**Removed permanently (not part of any minimal H\* substrate):** `E = λH + μS + νA` and λ/μ/ν; CPI and its four weights; the Inertia Law `η_eff = η_base·(1−stability)` (a regularization hyperparameter, not foundational); fracture ratio and the 0.85 trigger; energy-exhaustion 18.0; contradiction-resolution margins and the 0.9 decay; the 32 concepts; the ontology; the self-model join; the reasoning engine's type-lifting. None appears in `{X, P_θ over Θ_k, log-loss, MDL trigger G, emergence statistic M}`. **The mathematical foundation of Program D is those five primitives and nothing else.**

Observe what the reduced substrate *is*: predictive-processing + MDL/Bayesian structure learning + a null-referenced emergence test. Phase 4 asks whether that is new.

---

## PHASE 4 — NOVELTY ANALYSIS

Verdict per field: **[AK]** already known / **[D]** different / **[PN]** possibly novel / **[NN]** definitely not novel / **[?]** unknown. Never exaggerate.

| Field | Relation to H\* / the reduced substrate | Verdict |
|---|---|---|
| **Predictive Coding** (Rao & Ballard 1999; Friston) | Prediction-error-driven learning is the core of H\*. The single-level surprisal `I(s)=−log₂P(s∣c)` is correct but the *hierarchy* that defines predictive coding is absent (`RESEARCH_STATE §5`). Program D is a weaker instance, not an extension. | **NN** on mechanism; **[D]** only by being *less* than PC. |
| **Developmental Robotics** (Weng 2001; Oudeyer & Kaplan 2007 intrinsic motivation; Lungarella 2003) | This *is* Program D's field: agents that develop via sensorimotor experience, adding structure where **learning progress** is high. Oudeyer's learning-progress signal ≈ VELYNX's CPI (`provenance §5`) re-derived and uncited. H\* is a canonical developmental-robotics hypothesis. | **NN** — decisive; and uncited, a major reviewer liability. |
| **Self-Supervised Learning** | H\*'s log-loss next-observation objective *is* SSL. At toy scale Program D offers nothing over standard SSL. | **NN**. |
| **Free Energy Principle / Active Inference** (Friston) | Program D's `E` is explicitly *not* variational free energy (A-CA02, K9); there is no action-selection loop in the minimal organism, so it is not active inference. Neither implements nor extends AIF. | **NN**, and currently **mislabeled** — removing the FEP framing (Phase 3) is the honest fix. |
| **Energy-Based Models** (LeCun; Hinton) | Name collision only. `E=λH+μS+νA` is not an energy over data configurations, has no partition function, and is not learned. Not an EBM. | **NN** (not even an instance). |
| **Assembly Calculus** (Papadimitriou–Vempala) | No neurons, no assemblies, no projection/association ops. No contact. | **[D]** unrelated; no novelty claim either way. |
| **Neural Cellular Automata** (Mordvintsev 2020) | Both concern grown structure, but NCA growth is *local* update rules; H\* growth is *global* MDL model selection. Different substrate; no borrowing. | **[D]**; no novelty. |
| **Morphogenesis** (Turing 1952; reaction–diffusion) | Borrowed only as metaphor ("development"). No morphogenetic mathematics present. | **NN** (metaphor). |
| **Homeostatic Learning** (Turrigiano) | "Vitals/energy exhaustion" is metaphor; homeostatic plasticity mechanisms are absent (evidence DB). | **NN** (not implemented). |
| **Artificial Life** | Loose kinship on "emergence"; Program D is not evolutionary/open-ended. | **[D]**; no novelty. |
| **The affective-indexing kernel (H2)** — *not the central hypothesis* | Emotional framing as a **retrieval key** into problem-solving schemas (shame→debugging, planning→abstraction). Connects loosely to appraisal theory / somatic-marker hypothesis but the specific *framing→procedural-schema index* claim, if it improved objective task scores, is not something the eleven fields above already assert. | **PN** — the **only** possibly-novel element in the entire corpus. Untested (`PI_Review Phase 4 EXP-2`). |

**Net novelty verdict.** The central hypothesis H\* is **DEFINITELY NOT NOVEL**: it is owned jointly by developmental robotics, predictive coding, SSL, and MDL structure learning, and Program D implements *weaker* versions of each with zero neuroscience contact (`RESEARCH_STATE §5`) on toy environments. The single **possibly-novel** contribution in the corpus is **H2**, which is not the central hypothesis and has never been measured. This asymmetry drives Phase 8.

---

## PHASE 5 — REVIEWER #2

*(A fresh rejection aimed at this **scientific foundation**, not the built system already demolished in `PI_Review Phase 6`.)*

> **Reject.** The authors restate a "developing mind" as a prediction-error-plus-capacity-growth hypothesis (H\*) and present a five-primitive substrate. **On the mathematics:** the substrate is textbook — a proper scoring rule (log loss), MDL model selection, and a mutual-information emergence probe. There is no new estimator, no theorem, no bound, no identifiability result. Replacing an ad-hoc energy with log-loss is a correction, not a contribution. **On the assumptions:** the authors concede that their keystone (I2 — distinguishing emergent from injected structure) is *currently false* and un-instrumented; a program whose central claim is admittedly unfalsifiable today has no result to review. **On novelty:** this is developmental robotics with the citations deleted and the neuroscience removed; the "cognitive progress index" is Oudeyer's learning-progress signal re-derived; the hierarchy that would make it predictive coding is absent. **On the experiments:** the proposed test recovers a latent the authors themselves built into a synthetic generator — a sanity check that SGD + model selection works, not a discovery; on the one real ablation run (R1) the flagship policy was indistinguishable from a null baseline (p=0.866). **On the evaluation:** "emergence" is scored against the authors' own controls with unbounded researcher degrees of freedom, and 5 of 6 primary metrics are not even measurable in the current harness. **On the interpretation:** relabeling MDL-triggered capacity addition as "development of a mind" repeats the prior category error one level of abstraction higher. Recommend rejection without re-review; encourage resubmission as either a rigorous negative result or a focused test of the one untested idea (affective indexing).

**PI response — only changes that genuinely survive the attack:**

1. **Concede the novelty attack in full.** Do not claim novelty for H\*. Reframe the H\* deliverable as *either* (a) a **rigorous negative result** ("prediction-error + capacity growth does not exceed error-decoupled controls in environments of class X"), *or* (b) supporting methodology. Both survive; a novelty claim does not. **[Adopted]**
2. **Make I2 a pre-registered gate, not a hope.** No emergence claim is permitted until the learned-vs-injected discrimination test (Phase 6, DV-b vs shuffled control) is passed with a pre-registered margin and frozen analysis. This converts the reviewer's fatal objection into the program's central protocol. **[Adopted]**
3. **Keep the two math corrections** (log-loss replaces `E`; MDL replaces the hand-set birth threshold) — they survive because they are derivations, not choices, and they directly close failure mode F2. **[Adopted]**
4. **Delete "mind/development/soul" from all claims.** The category-error attack is correct; the honest object is "error-gated structure acquisition." **[Adopted]**
5. **Reject only one sub-attack:** that the experiment is "merely a sanity check." It is *not* if I3 is met — an environment with *nonlinear* latent mixing (not cube corners) where a fixed-capacity control provably cannot recover the latent makes the growth-vs-no-growth contrast informative. This survives **conditional on I3 being satisfied**, which becomes a design requirement, not an assumption. **[Adopted with condition]**

Nothing else survives. In particular, no defense of the FEP framing, the 32 concepts, the self-model, or the "cognitive stack as cognition" claim survives — consistent with the canon.

---

## PHASE 6 — EXPERIMENT E0

**E0 — Emergence-vs-injection discrimination on a nonlinear-latent stream.** One experiment, lowest cost, capable of killing H\*.

- **Precondition (≈1 day, not E0 itself):** run `PI_Review EXP-0` (paraphrase the 100/100 benchmark). It cheaply kills the *current system's* headline (predicted collapse toward 4.0/10) but does **not** test H\* — H\* concerns a *new* minimal organism. Run it first only to stop claiming the old result.

- **Environment (satisfies I3, defeats failure mode F1):** a synthetic sequence from a known generator with `K` latent states and **nonlinear** observation mixing, verified offline so that a fixed-capacity linear predictor *cannot* recover the latent. This deliberately replaces the linearly-separable cube-corner toy env (A-S01/A-E06).

- **Agent:** the minimal organism — conjugate predictor `P_θ`, capacity index `k`, MDL growth trigger `G>0`. **No seeded concepts, no ontology, no self-model.** Reuses the two correctly-implemented, literature-grounded primitives (Dirichlet–Markov predictor; concept-birth MDL ledger, `RESEARCH_STATE §5`).

- **Conditions (the IV + controls):** **T** = error-gated growth ON; **C1** = fixed capacity (no growth); **C2** = capacity-matched growth at *random* times (decoupled from error); **C3** = shuffled-input (destroys temporal structure, preserves marginals).

- **Measurements (pre-registered, frozen before running):**
  - **DV-a:** held-out predictive log-likelihood. **Pass:** T > C1 *and* T > C2 at p<0.01 across ≥5 seeds.
  - **DV-b (I2):** `NMI(learned partition, true latent) − NMI(learned partition, C3-shuffled)`. **Pass:** exceeds a pre-registered margin.
  - Instruments at least one of the 5 currently-unmeasurable primary metrics (held-out split), directly attacking risk R-2.

- **Kill decision (wired, not decorative):** if **T fails to beat both C1 and C2 on DV-a, OR DV-b is within noise of the shuffled control**, after **two** honest attempts → **H\* is falsified for this environment class.** Combined with the expected paraphrase collapse of the current system, the developmental center of Program D is dead; keep Program A, publish the negative result. This is the first kill criterion in the entire program wired to an automated decision (contrast `kill_criteria_validation.md`: "no kill criterion is wired").

- **If Program D survives, why confidence increases — precisely:**
  - Beating **C2** (not just C1) shows the effect requires error-*coupled* growth, not merely more parameters — ruling out the trivial capacity-count explanation.
  - DV-b exceeding the **shuffled** control shows the recovered structure is about the *temporal generative process*, not input marginals or researcher-chosen controls — i.e., **I2 is satisfied for the first time in the program's history.**
  - Only then is the program entitled to scale to richer environments (EXP-4 cycle bootstrapping). Survival converts H\* from unfalsifiable-and-not-novel into falsifiable-and-demonstrated-at-toy-scale — still not novel, but now a *real* platform on which the H2 kernel can be tested honestly.

- **Cost:** days to ~2 weeks. No new subsystems; reuses existing correctly-implemented primitives; adds only the nonlinear generator, the three controls, and the frozen analysis script.

---

## PHASE 7 — PUBLICATION TEST

| Venue | Desk-rejected? | Why | Evidence still missing |
|---|---|---|---|
| **NeurIPS** | **Yes (as H\*).** | No new algorithm, theorem, or SOTA; core mechanism is SSL + developmental-robotics intrinsic motivation, known since ~2007. R1 is a null result on the built system. | A novel mechanism *or* a surprising result on a non-toy benchmark; head-to-head vs intrinsic-motivation baselines (Oudeyer, ICM, RND); scale beyond synthetic latents. |
| **ICML** | **Yes.** | Stricter theory/algorithm bar; MDL-triggered growth is Bayesian-nonparametric structure learning, established. | A theorem or new estimator (e.g., an identifiability result for emergent-vs-injected structure); no such result exists. |
| **Nature Machine Intelligence** | **Yes.** | Requires broad significance on real problems; toy-latent recovery is not NMI-scale; "mind/development" framing flagged as overclaiming. | A rigorous result on a real sensorimotor domain with demonstrated generality and honest calibration. |
| **Science Robotics** | **Yes.** | No robot, no embodiment, no closed sensorimotor loop; developmental-robotics venue but requires an agent-in-world result. | An actual embodied agent whose competence provably grows from experience. |

**What *is* publishable now (the honest publication path):** not H\*. Two real options exist. **(1)** A **negative-result + methodology** paper — the designer-injection confound in "emergent cognition" demos, the paraphrase-collapse finding (100/100 → 4.0/10), and the **I2 discrimination protocol** (E0's null-referenced emergence test) — has a home in a rigorous negative-results / datasets-&-benchmarks track, TMLR, or a workshop, because the *method for catching lookup-tables-dressed-as-minds* is genuinely useful. **(2)** If **EXP-2** finds signal, a focused paper on **affective framing as an index into problem-solving schemas** (H2) — the one **[PN]** item — is a small but real contribution. Neither of these is the "developing mind."

---

## PHASE 8 — DECISION

**C. Program D should be fundamentally redesigned.**

**Reasoning (no optimism, no hedging):**

- H\* — the developmental/"mind" hypothesis that *is* Program D's identity — **survives falsifiability** (Phase 1) but **fails novelty decisively** (Phase 4: owned by developmental robotics + predictive coding + SSL + MDL) and **fails comparative advantage**: the built system contributes nothing to the emergence question that the existing literature does not already own, and does so with weaker tools (no hierarchy, no neuroscience, toy environments, R1 null).
- Its keystone assumption **I2 is currently false** (Phase 2): the program cannot today distinguish emergent from injected structure, so as built it is not falsifiable science — it is scaffolding around a lookup table (`PI_Review Phase 2`, already canonical).
- The **only possibly-novel** element in the entire corpus (H2, affective indexing) is **not the center** and is untested.

Therefore the program's *center of gravity must move* — off the developmental-mind thesis entirely. That is more than modification (**not B**): the central hypothesis is being *replaced*, not tuned. It is less than abandonment (**not D**): three real, months-worth deliverables survive. The redesigned foundation is:

1. **Program A** — calibrated live-truth retrieval — as an **honest product**, gated strictly on **EXP-1** making calibration true (ECE < 0.1); currently CONTRADICTED (`CERTAIN` on hallucination). This is engineering, *not* the research center.
2. **H2 (affective indexing)** — promoted to the **actual novel research question**, decided by **EXP-2** (objective task score, framed vs. unframed). This is the only thing that can earn a novelty claim.
3. **H\*** — demoted to a **single pre-registered discrimination experiment (E0)** whose most probable publishable output is a **rigorous negative result + the I2 methodology**, *not* a mind. It is retained only because it is now cheap, wired to a real kill decision, and its survival is the sole precondition for any future scaling.

Program D, as the "raise a developing symbolic mind" program, **does not deserve to exist** — that thesis is neither novel nor, as built, falsifiable. Program D, redesigned as *an honest calibrated-retrieval product + a falsifiable test of affective indexing + a rigorous emergence-discrimination protocol that expects to publish a negative result*, **does** deserve the next several months. The distinction between those two programs is total, which is why the verdict is redesign, not continuation.

*Optimize for truth, not survival of the program. The canon already told this program that most of it is scaffolding around a lookup table and that its one real idea has never been tested. This foundation's only new instruction is: stop standing on the thesis you cannot make novel, make I2 true before you say "emergence" again, and go measure H2.*

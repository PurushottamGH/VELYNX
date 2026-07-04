# PROGRAM D — CANONICAL

**Single source of truth. Every other document must derive from this one.**
Where any document conflicts with this file, this file wins and that document is a defect to be fixed.

- **Owner:** Lead Research Director (integration/verification authority).
- **Derives from (verified at source, most-authoritative-first):**
  `foundation/program_d_scientific_foundation_v0.1.md` (2026-07-02 PI decision) ·
  `PROGRAM_D_RESEARCH_STATE_v0.1.md` (2026-07-01) ·
  `archive/data/ablation_report.md` (R1) ·
  `research/designer_injection_report.md` ·
  `archive/data/soul_test_report.md`.
- **Supersedes in authority:** `PROGRAM_D_SPECIFICATION.md`, `PROGRAM_D_CONSTITUTION.md`, `HYPOTHESIS_REGISTER.md`, `EXPERIMENT_PROTOCOLS.md`, `TERMINOLOGY.md`, and the entire engineering (`repository_v2.md`, `migration_plan.md`, `implementation_checklist_v1.md`) and publication (`PUBLICATION_CHECKLIST.md`, `RELATED_WORK.md`, `REVIEWER_OBJECTIONS.md`, `GRANT_PACKAGE.md`, `CONSTITUTION_COMPLIANCE.md`, `REPRODUCIBILITY_CHECKLIST.md`, `DATA_MANAGEMENT_PLAN.md`) clusters. Those are proposals until reconciled to §9.
- **Last integrated:** 2026-07-03.

---

## 0. Epistemic tags (binding on every claim in the canon)

- **[FACT]** — mechanically verified against code, empirical logs, or mathematical derivation. Provenance cited.
- **[HYPOTHESIS]** — falsifiable, with a pre-registered null and a wired kill criterion.
- **[SPECULATION]** — untested. **Prohibited in any load-bearing mechanism or execution path.** Test or delete.
- **[REJECTED]** — empirically falsified or superseded. Must not appear in any live mechanism.

---

## 1. Prime directive

**[FACT]** Program D optimizes for **truth**, not elegance, and not survival of the legacy program. It is an audit-and-falsification protocol over inherited Programs A/B/C — not a generator of new science.

Binding rules (constitutional):
1. **No new hypotheses.** Only refine, test, or falsify inherited ones.
2. **No subsystem without a pre-registered experiment that requires it.** If nothing in {EXP-0, EXP-1, EXP-2, E0} needs it, it is not built — it is archived.
3. **If a mechanism cannot be operationally distinguished from a null/random baseline, it is a delete candidate, not a feature.**
4. **Priority order under trade-off:** scientific correctness > experiment reproducibility > code simplicity > performance > features.
5. **Prohibited constructs:** anthropomorphism (mind/soul/belief/understanding/curiosity in any live name or claim), designer-injection sold as emergence, novelty inflation of MDL/ECE/SSL, unit-incommensurate mathematics.

---

## 2. Program taxonomy

- **[FACT] Program A** — live-truth retrieval engine. Scientific claim: **honest uncertainty (calibration)**. Status: engineering product, *not* the research center.
- **[FACT] Program B** — the authored affective concept graph ("Soul Graph"). Only surviving scientific content: the **affective-indexing kernel (H2)**. The 32 authored concepts and edge labels are **[REJECTED]** designer artifacts, not evidence.
- **[FACT] Program C** — the symbolic cognitive stack (~24–30k LOC). Reduced to a single testable claim: **error-gated structure acquisition (H\*)**. Everything else is scaffolding (§5).
- **[FACT] Program D** — this audit/falsification protocol over A/B/C.

---

## 3. Decision of record (PI, 2026-07-02): **REDESIGN**

**[FACT]** The verdict is **C — Program D is fundamentally redesigned**, not modified (its central hypothesis is *replaced*) and not abandoned (three deliverables survive). The old thesis — "raise a developing symbolic mind" — is retired: it is **not novel** (§8) and, as built, **not falsifiable** (keystone assumption I2 is currently false, §4).

**Three surviving deliverables, in priority order:**

1. **Program A as an honest product** — gated strictly on **EXP-1** (calibration, ECE < 0.10). Currently **[REJECTED]**-state: emits `CERTAIN` on hallucinated content (`soul_test_report.md` Q6). Engineering, not the research center.
2. **H2 (affective indexing)** — promoted to the **actual novel research question**. The *only* possibly-novel element in the entire corpus (§8). Decided by **EXP-2**.
3. **H\* (error-gated structure acquisition)** — demoted to **one** cheap pre-registered experiment **E0**, whose most probable publishable output is a **rigorous negative result + the discrimination methodology**, not "a mind." Retained only because it is now cheap and wired to a real kill decision.

---

## 4. Foundational assumptions (exactly three; each irreducible)

**[FACT]** H\* stands on exactly these. Every assumption H\* does *not* require was, by definition, excess — the built system layered ~25 removable load-bearing assumptions on this 3-assumption core (`RESEARCH_STATE §5–6`).

| ID | Assumption | Class | If false |
|---|---|---|---|
| **I1** | Prediction error is a sufficient signal to drive representational structure. | **[FACT]** evidence-supported (predictive coding, SSL, dev. robotics), but **weakly instantiated here** (single-level, no hierarchy). | No engine for development. |
| **I2** | "Emergent structure" is operationally **distinguishable** from injected/statistically-trivial structure. | **[REJECTED] as currently instantiated** — injection audit: ~150 constants, **zero** data-derived. **This is the keystone.** | H\* is unfalsifiable → Program D is not science. |
| **I3** | An environment exists that is rich enough to *require* non-trivial structure yet learnable in feasible compute, and is neither hand-seeded nor linearly trivial. | **[SPECULATION]** — the only tested environment (cube corners) is linearly separable and did not generalize. | H\* is vacuously true or untestable. |

**[FACT]** Catastrophe ranking **I2 > I3 > I1**. Program D's entire scientific viability reduces to **making I2 true before the word "emergence" is used again**. E0 (§7) is the first-ever test wired to that gate.

---

## 5. Mathematical substrate — exactly five primitives

**[FACT]** The foundation is `{ x_t, P_θ over Θ_k, L, G, M }` and nothing else.

1. **Observation stream** `x_t ∈ X`. *Given; keep.*
2. **Growable predictor class** `{ P_θ(x_{t+1} | x_{≤t}) : θ ∈ Θ_k }`, indexed by capacity `k`. Reuse the existing conjugate (Dirichlet–Markov) predictor; **drop the label "belief model."**
3. **Proper scoring loss** `L = −log P_θ(x_{t+1} | x_{≤t})`. **[FACT]** the log score is (up to affine transform) the unique local strictly-proper scoring rule (Bernardo 1979) — a derivation, not a choice. **Permanently replaces `E = λH + μS + νA`.**
4. **MDL growth operator** `g : (Θ_k, error-history) → Θ_{k+1}`, triggered **iff** description length strictly decreases:
   `G = H_before − H_after − λ_model > 0`, with **`λ_model = k·b + n·log₂ N`** (concept-birth ledger, `literature/…provenance §2`). **The trigger must not be hand-set** — a hand-set threshold violates I2 by construction (failure mode F2). This is the one load-bearing derivation.
5. **Emergence statistic** `M(θ_k)`, constructed so that **`E[M | H₀] = 0`**:
   **`M = NMI(learned partition, true latent) − NMI(learned partition, shuffled-input)`.**
   **[FACT]** This null-referenced construction *is* I2 made operational; it is what makes the statistic non-gameable.
   **[REJECTED]** the "graph-isomorphism / topological-alignment" formulation of M (reintroduces researcher degrees of freedom, failure mode F3; undefined for a probabilistic predictor). See §10 Issue-2.

**[REJECTED] — permanently removed, may appear ONLY as archive/delete targets (never live/required):**
`E = λH + μS + νA` and λ/μ/ν · CPI + its 0.40/0.30/0.20/0.10 weights · Inertia Law `η_eff = η_base·(1−stability)` · fracture ratio + 0.85 trigger · energy-exhaustion 18.0 · contradiction-margin 0.9 decay · the 32 soul concepts · the hand-authored ontology · the self-model · the reasoning engine's type-lifting · "resonance / sleep-replay / thermodynamic state."

---

## 6. Canonical hypothesis set (H\*, H1, H2 — and H3 is [REJECTED])

### H\* — Error-Gated Structure Acquisition (central)
**[HYPOTHESIS]** An agent whose **only** learning signal is sensorimotor prediction error, and which adds capacity **only** when prediction error persists, acquires structure that **(i)** is absent at init, **(ii)** improves held-out prediction beyond a fixed-capacity control **and** an error-decoupled capacity-matched control, and **(iii)** is **not reducible** to designer-injected statistics (measured above a shuffled-input control). Clause **(iii) = I2** is the crux and the only clause the built system provably fails.
- **IV:** error-gated capacity-growth operator ON vs OFF/decoupled (implementation-independent).
- **DVs:** (a) held-out predictive log-likelihood; (b) `M` (§5.5).
- **H₀:** T indistinguishable from fixed-capacity and error-decoupled controls on (a), **and** `M` within noise of shuffled control.
- **Kill (wired):** T fails to beat **both** C1 and C2 on DV-a at p<0.01 across ≥5 seeds, **OR** DV-b within noise of shuffled control — after **two** honest attempts → **H\* falsified for this environment class.**
- **Protocol:** E0. **Prior on H₀ is high** (R1 null; §8).

### H1 — Retrieval Uncertainty Calibration (Program A product gate)
**[HYPOTHESIS]** Program A's confidence tiers (CERTAIN/PROBABLE/DEBATED/UNKNOWN) report empirical correctness matching the tier.
- **Observable:** Expected Calibration Error (ECE).
- **H₀:** accuracy is independent of predicted tier (no better than a constant-confidence baseline).
- **Control:** BM25/TF-IDF retrieval with randomly assigned confidence.
- **Pass gate:** **ECE < 0.10.** **Kill:** ECE ≥ 0.10 or tier-independence over the query set → the "honest uncertainty" claim is rejected. *(Single number: the legacy 0.15 kill threshold is retired — see §10 Issue-4.)*
- **Goodhart guard:** bin-boundary hacking that lowers ECE without improving the underlying retrieval signal is a violation, not a pass.
- **Protocol:** EXP-1. **Current status: [REJECTED]** (`CERTAIN` on hallucinated Q6).

### H2 — Affective Indexing (the one possibly-novel question)
**[HYPOTHESIS]** A learned **affective-framing → problem-solving-schema** mapping (e.g. shame→debugging, planning→abstraction) improves **objective task outcomes** over an unframed baseline.
- **Observable:** objective task success rate (debugging fixes / planning success). **Not** "search-steps-to-convergence" or "compression ratio" — see §10 Issue-5.
- **IV:** affective frame present vs absent (prompt-level).
- **H₀:** framed task score ≤ unframed baseline.
- **Control:** identical task, neutral (unframed) prompt. **[FACT]** the control is the *unframed prompt* — **not** dense-embedding cosine search, and the task set must **not** depend on the 32 authored soul concepts (that reintroduces the designer-injection confound; §10 Issue-6).
- **Kill:** no significant task-outcome difference, **or** schemas must be re-authored per task (circularity).
- **Circularity guard:** evaluate only on task sets the affect categories were **not** authored against; use isolated third-party tasks.
- **Protocol:** EXP-2. **Status: untested.**

### H3 — [REJECTED] (subsumed)
**[REJECTED]** "MDL-gated topology emergence / emergent development" as a *separate* hypothesis. It is H\* with clause (iii)/I2 dropped — i.e. the weaker pre-collapse framing the redesign explicitly retired. Its content lives entirely inside H\*; its protocol (old EXP-3) is subsumed and made rigorous by **E0**. It must not be re-listed as a live surviving hypothesis. See §10 Issue-1.

---

## 7. Experiment set (exactly four; frozen, pre-registered)

**[FACT]** All experiments run against **frozen** code. No experiment may tune hyperparameters. EXP-3, EXP-4, R2, R3F are **not** part of the redesigned program (§10 Issue-1); R1 is closed evidence (§8), not a live experiment.

| ID | Tests | One-line protocol | Pass / Kill |
|---|---|---|---|
| **EXP-0** *(precondition, ~1 day)* | the **old deployed system**, not H\* | Freeze code; 64 interleaved trials (32 original "What is X?" vs 32 keyword-free paraphrases); wipe semantic graph + episodic memory each trial (no Hebbian leakage); no keyword/Porter-stem leakage. | If concept detection collapses to noise on paraphrases → the "semantic understanding over a lookup table" claim is falsified. Predicted collapse ~100/100 → ~4.0/10. Run **first**, only to stop claiming the old headline. |
| **EXP-1** | H1 | ≥200 mixed queries (facts, ambiguous, hallucinations); reliability diagram + ECE. | Product-honest iff **ECE < 0.10**. |
| **EXP-2** | H2 | Objective tasks under affective-framed vs neutral prompts; unframed control; third-party task set. | Framed > unframed at pre-registered significance. |
| **E0** | H\* | Minimal organism (conjugate predictor + MDL trigger; **no seeded concepts/ontology/self-model**) on a synthetic **nonlinear-latent** stream verified offline so a linear/fixed-capacity predictor cannot recover the latent. Conditions **T** (error-gated growth), **C1** (fixed capacity), **C2** (capacity-matched growth at random times), **C3** (shuffled input). | DV-a: T > C1 **and** T > C2 at p<0.01 across ≥5 seeds. DV-b: `M` exceeds pre-registered margin. Kill per H\*. Instruments ≥1 of the 5 currently-unmeasurable primary metrics (attacks risk R-2). |

---

## 8. Empirical anchors (verified this session) & novelty verdict

**[FACT] Anchors (provenance-checked):**
- **R1 (72-run ablation):** consolidation policy `free_energy` (RMSE **0.2991 ± 0.0976**) is statistically indistinguishable from the `null` baseline (**0.2951 ± 0.0975**), paired **p = 0.8660**. → `E`/free-energy delivers no measurable benefit. `archive/data/ablation_report.md`.
- **Designer injection:** of ~150 architecture constants, **zero** are data-derived. `research/designer_injection_report.md`.
- **Calibration:** Q6 produced hallucinated content marked `CERTAIN`. `archive/data/soul_test_report.md`.

**[FACT] Novelty verdict (binding on all publication docs):**
- **H\* is DEFINITELY NOT NOVEL.** It is owned jointly by **developmental robotics** (Weng 2001; **Oudeyer & Kaplan 2007** intrinsic motivation / learning progress), **predictive coding** (Rao & Ballard 1999; Friston), **self-supervised learning**, and **MDL/Bayesian structure learning**. VELYNX's "cognitive progress index" ≈ **Oudeyer's learning-progress signal**, re-derived and **previously uncited** — a major reviewer liability that must be closed.
- The legacy `E` is explicitly **not** Friston variational free energy and **not** an energy-based model (no partition function, not learned). Its FEP/EBM framing is **[REJECTED]** and must be removed, not cited as novel.
- **H2 is the only [PN] (possibly-novel) element** in the entire corpus — and is untested.
- **All four top venues (NeurIPS/ICML/Nature MI/Science Robotics) desk-reject H\* as-is.**

**[FACT] Honest publication path:**
1. A **negative-result + methodology** paper: the designer-injection confound in "emergent cognition" demos, the paraphrase-collapse finding, and the **I2 null-referenced emergence-discrimination protocol** (E0's `M`). Home: rigorous negative-results / datasets-&-benchmarks track, TMLR, or workshop.
2. **If EXP-2 finds signal:** a focused paper on **affective framing as an index into problem-solving schemas** (H2).
Neither is "a developing mind."

---

## 9. Derivation obligations (how each cluster reconciles to this file)

Every downstream document is a **proposal** until it derives from §1–§8. Required reconciliations (owners = original specialist teams):

**Gemini (specification layer)** — `PROGRAM_D_SPECIFICATION.md`:
- Replace §2.5 "graph-isomorphism metric" with the §5.5 null-referenced NMI `M`.
- Remove H3 from "Surviving Hypotheses"; mark **[REJECTED] / subsumed by H\***; add H\* as the central hypothesis.
- Rewrite H2 to the §6 indexing/task-score form (delete "dimensionality reduction / compression ratio / search-steps / dense-embedding control").
- Set the single ECE gate to **< 0.10** (retire the 0.15 kill threshold).

**DeepSeek (engineering layer)** — `repository_v2.md`, `migration_plan.md`, `implementation_checklist_v1.md`:
- Move to `archive/` (not the live tree): `program_c/self_model/`, `reasoning_engine`, `ontology_loader`, and the free-energy/`R1` experiment as *closed evidence*; drop `EXP3/`, `EXP4/`, `R3F/` from the live experiment set.
- **Remove `program_b/soul_graph` + `concepts.json` as a dependency of EXP-2** (violates I2/H2 circularity guard).
- **Add `experiments/EXP-0/`** (paraphrase precondition) — currently missing.
- Rename anthropomorphic live modules (`soul`, `belief`, `curiosity`, `self_model`, `dream_state`, `monologue`) or archive them; they may not appear in live names.
- Keep only the compliant `core/` 5-primitive mapping and the EXP-1/EXP-2/E0 triad + EXP-0.
- De-duplicate: one import-remap table, one directory skeleton, one archive-target list (currently triplicated across the three docs).

**Nemotron (publication layer)** — `RELATED_WORK.md`, `GRANT_PACKAGE.md`, `PUBLICATION_CHECKLIST.md`, `REVIEWER_OBJECTIONS.md`, `CONSTITUTION_COMPLIANCE.md`:
- Delete every "Novel/First" tag on `E`, Inertia Law, three-pressure scoring, "catastrophic-forgetting cure" (contradict R1 null and §8).
- Add the owning prior art to `RELATED_WORK.md`: **Oudeyer & Kaplan 2007, Weng 2001, Pathak et al. 2017 (ICM), Burda et al. 2018 (RND)**, and upgrade Rao-Ballard from "cousin" to prior art of the core loop.
- Re-target the thesis to the §8 negative-result / H2 path; report R1 (p=0.866), paraphrase-collapse, and the calibration contradiction as headline findings, not omissions.
- Keep `REVIEWER_OBJECTIONS.md` (stats/baseline objections are sound) but concede the novelty objection instead of defending it. `DATA_MANAGEMENT_PLAN.md` / `REPRODUCIBILITY_CHECKLIST.md` stand.

---

## 10. Decision ledger (this integration pass)

Each item: **Issue → Evidence → Decision → Reason → Action.**

**Issue-1 — H3 resurrected as a live hypothesis (and H\* absent from the spec).**
- *Evidence:* `PROGRAM_D_SPECIFICATION.md §3` lists H1/H2/**H3** and omits H\*; `repository_v2.md:19,68–69` build `EXP3` (H3) + `EXP4`. Foundation Phase 1/8 collapsed H1/H2/H3 into H\* and demoted the developmental thesis.
- *Decision:* **H3 [REJECTED]/subsumed by H\*.** Canonical hypotheses are H\*, H1, H2. Experiments EXP-3/EXP-4 removed.
- *Reason:* H3 is H\* minus clause (iii)/I2 — the exact weakening the redesign exists to prevent. Two names for one claim is duplicate complexity.
- *Action:* §6, §7, §9-Gemini/DeepSeek.

**Issue-2 — Emergence statistic drift: "graph isomorphism" vs null-referenced NMI.**
- *Evidence:* `SPECIFICATION §2.5` = "graph isomorphism metric … topological alignment"; foundation Phase 3 primitive 5 + `TERMINOLOGY` + `HYPOTHESIS_REGISTER` = null-referenced NMI.
- *Decision:* Canonical `M = NMI(learned, true) − NMI(learned, shuffled)`. Graph-isomorphism form **[REJECTED]**.
- *Reason:* The null-reference (`E[M|H₀]=0`) is what operationalizes I2 and removes researcher DOF (failure mode F3); graph isomorphism is ill-defined for a probabilistic predictor and re-opens F3.
- *Action:* §5.5, §9-Gemini.

**Issue-3 — MDL threshold λ under-specified.**
- *Evidence:* `SPECIFICATION §2.4` / `TERMINOLOGY` use bare `λ`; foundation pins `λ_model = k·b + n·log₂ N`.
- *Decision:* Pin `λ_model = k·b + n·log₂ N`.
- *Reason:* A bare/hand-set λ is exactly failure mode F2 (hand-set trigger violates I2). The derived ledger is the load-bearing derivation.
- *Action:* §5.4.

**Issue-4 — Two calibration thresholds (ECE < 0.10 pass vs > 0.15 kill).**
- *Evidence:* `SPECIFICATION §3-H1` kill = "ECE > 0.15"; foundation + `HYPOTHESIS_REGISTER` gate = "ECE < 0.1."
- *Decision:* Single gate **ECE < 0.10**; ECE ≥ 0.10 fails.
- *Reason:* A 0.10–0.15 dead zone lets a system be simultaneously "not passing" and "not killed" — unfalsifiable slack. One number.
- *Action:* §6-H1, §7.

**Issue-5 — H2 redefined as "dimensionality reduction / compression / search-steps."**
- *Evidence:* `SPECIFICATION §3-H2` = affective *dimensionality reduction*, observable "search steps-to-convergence," control "dense-embedding cosine search"; foundation Phase 4/8 + register = affective *framing→schema index*, observable objective task score, control unframed prompt.
- *Decision:* Canonical H2 = affective indexing → **objective task score**, unframed-prompt control (§6-H2).
- *Reason:* Dimensionality reduction is not novel and is a *different* claim; the [PN] novelty is specifically framing-as-schema-index. Swapping the observable/control silently changes the hypothesis.
- *Action:* §6-H2, §9-Gemini.

**Issue-6 — EXP-2 made dependent on the 32 authored soul concepts.**
- *Evidence:* `repository_v2.md:152–158` makes `program_b/soul_graph` + `concepts.json` a required EXP-2 input.
- *Decision:* **Forbidden.** EXP-2 tests prompt-level framing on a third-party task set; the 32 concepts are [REJECTED] designer artifacts.
- *Reason:* Testing affect on environments authored around the same affect categories is the circular-logic failure the constitution names explicitly; it reintroduces designer injection into the one possibly-novel result.
- *Action:* §6-H2 circularity guard, §9-DeepSeek.

**Issue-7 — Publication cluster overclaims novelty and omits owning prior art.**
- *Evidence:* `RELATED_WORK.md §9` tags Inertia Law / `E` / three-pressure scoring "Novel/First"; `GRANT_PACKAGE.md` sells "unified cognitive architecture / first catastrophic-forgetting cure"; **Oudeyer, Weng, ICM, RND absent**; no doc mentions R1 null, paraphrase-collapse, calibration contradiction, H2, or the negative-result path.
- *Decision:* Novelty verdict §8 is binding; publication docs must derive from it.
- *Reason:* R1 shows the "cure" is indistinguishable from null (p=0.866); asserting novelty in uncited "—" cells institutionalizes the exact Oudeyer-re-derivation liability the PI review names.
- *Action:* §8, §9-Nemotron.

---

## 11. Open state (single next action)

**[FACT]** Immediate next step is **EXP-0** (paraphrase the 100/100 benchmark, ~1 day, frozen code) — a precondition to stop the deployed system claiming its headline result before any H\* work. It is not E0. Everything downstream (EXP-1 for the Program A product gate, EXP-2 for the one novel question, E0 for the wired H\* kill) is pre-registered above and derives from this file.

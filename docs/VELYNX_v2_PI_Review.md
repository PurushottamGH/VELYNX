# VELYNX — Principal Investigator Review & v2 Research Program

**Reviewer role:** Principal Investigator. Authority to reject any component.
**Standard:** *If it cannot survive peer review from the world's best computational neuroscientists, it does not belong.*
**Date:** 2026-07-01
**Corpus reviewed:** `backend/constitution/*.md`, `docs/requirements.md` (Constitution); `backend/soul/{concepts.json, soul_graph.py}`, `VELYNX_Knowledge_Module.txt` `BRIDGE_NODES`, `backend/data/world_ontology.json` (the "organism"); `VELYNX_Metacognitive_Loop.md`, `docs/phase57_agentic_loop_architecture.md`, `docs/phase60_self_model_architecture.md`, phase 36→62 history (the roadmap); `gemini-session*.txt` (the "literature review"); `soul_test_report.md`, `benchmark_v2_results.json`, `phase62_1_results.txt` (benchmarks); `docs/VELYNX_AUDIT_2026-06-01.md`, `VELYNX_PHASE36_AUDIT.md` (prior reviews).

---

## VERDICT (read this first)

**~90% of the current design should be discarded as a *research program*.** Not because the engineering is bad — some of it is competent — but because almost none of it tests a hypothesis, and the one narrative that would make it science ("a raised mind that *develops*") is asserted nowhere and demonstrated nowhere in the code.

Three separate projects wear the name VELYNX:

- **Project A — Live-truth retrieval engine.** The original Constitution: find truth live from sources, score credibility, surface contradictions, report calibrated uncertainty, learn from being wrong without retraining. This is a legitimate, buildable *product*. It is not novel science, and that is fine.
- **Project B — The "Soul Graph."** 32 hand-authored affective concepts, hand-authored edges (`contrasts`, `catalyzes`, `diminishes`), BFS traversal that concatenates edge labels into "arcs." This is an **authored artifact presented as an emergent one.**
- **Project C — The symbolic-AGI stack.** Metacognition, beliefs, goals, agentic planner, persistent self-model, foundational ontology. ~24k LOC of hand-specified symbolic scaffolding.

These do not belong in one system, and none of B or C survives the stated standard. The salvageable science reduces to **one testable hypothesis** (Section 6), and even it must be reframed. If VELYNX wants to be a *product*, keep Project A and delete the rest. If VELYNX wants to be *research on development*, almost everything currently built is off the critical path and should be archived.

The honest verdict the codebase already contains, written by an earlier reviewer, is `soul_test_report.md`: **4.0/10.** The 100/100 "Live-Fire" numbers in the git log test the *same code* on queries hand-selected to hit the 32 seeded concepts. That gap is the whole story.

---

## PHASE 1 — Assumption Ledger

Every load-bearing assumption, classified. Categories: **[FACT]**, **[EVIDENCE-SUPPORTED]**, **[WEAK HYPOTHESIS]**, **[SPECULATION]**, **[UNSUPPORTED BELIEF]**, **[CONTRADICTED]**.

### On truth & retrieval (Project A)
| # | Assumption | Class | Note |
|---|---|---|---|
| A1 | Answers can be traced to live sources with credibility scoring | **[FACT]** | Standard IR/RAG. Buildable. |
| A2 | Calibrated uncertainty tiers (CERTAIN/PROBABLE/DEBATED/UNKNOWN) can be assigned | **[EVIDENCE-SUPPORTED]** | Calibration is a solved-ish ML problem — *but not as implemented*; see A3. |
| A3 | VELYNX's confidence tiers are calibrated | **[CONTRADICTED]** | `soul_test_report.md` Q6: `CERTAIN` on a hallucinated answer. Tiers are assigned from concept-count/hop-count heuristics, never validated against ground-truth correctness. |
| A4 | "Learns from being wrong without retraining" | **[WEAK HYPOTHESIS]** | What exists is incrementing JSON confidence scores + appending regex rules. That is bookkeeping, not learning a better model. |

### On the "Soul" (Project B)
| # | Assumption | Class | Note |
|---|---|---|---|
| B1 | 32 hand-authored affective concepts capture a useful space | **[UNSUPPORTED BELIEF]** | No theory selects these 32. No coverage claim is testable. |
| B2 | Edge labels (`contrasts`, `catalyzes`, `diminishes`) encode real relations | **[SPECULATION]** | Author-assigned. No measurement, no ground truth, no inter-rater reliability. |
| B3 | BFS "arcs" constitute reasoning/understanding | **[CONTRADICTED]** | Arcs are string concatenations of hand-authored edge labels. "Grief contrasts loss. Loss distant depression." carries exactly the information the author encoded — no inference. ELIZA-class: meaning is projected by the reader. |
| B4 | Emotion↔technical bridges (shame→failure→debugging) index useful strategy | **[WEAK HYPOTHESIS]** | Hardcoded 15-entry dict. The *idea* is interesting (see Novelty). The *implementation* tests nothing. |

### On "development" and "mind" (the framing)
| # | Assumption | Class | Note |
|---|---|---|---|
| D1 | VELYNX is "a raised synthetic mind" that develops | **[UNSUPPORTED BELIEF]** | Nothing develops. Concepts are seeded (`concepts.json`), bridges hardcoded, ontology hand-authored (`world_ontology.json`), curriculum scripted with `expected_answer`. There is no self-organization, no representation learning, no emergence. "Development" is a metaphor applied post hoc. |
| D2 | Stacking symbolic modules (belief, goal, self, ontology) yields cognition | **[CONTRADICTED]** | This is GOFAI's central bet. 50 years of evidence says hand-specified symbol systems do not scale to open-world cognition or ground their symbols. The audits document the predictable failure mode: 8 duplicated subsystems, ~20% dead code, no unified state. |
| D3 | A persistent "self-model" that queries 4 subsystems = selfhood | **[SPECULATION]** | It is a SQL join over four stores, narrated in the first person. No evidence this is what a self is or that it does any cognitive work. |
| D4 | The foundational ontology (Entity→PhysicalObject→…) grounds meaning | **[CONTRADICTED]** | Symbol grounding problem (Harnad 1990). Hand-authored `is-a` trees are notation, not grounding; the tokens mean nothing to the system. |

### On evaluation
| # | Assumption | Class | Note |
|---|---|---|---|
| E1 | 100/100 "Live-Fire" pass = the system works | **[CONTRADICTED]** | Curated queries chosen to hit seeded concepts. `benchmark_v2_results.json` Q1–Q5 are all scenario/relational prompts over the 32 concepts. The adversarial test (`soul_test_report.md`) that used *un-seeded phrasing* ("forgave" vs "forgiveness") scored 4.0/10 with a timeout and a hallucination. Teaching to the test. |
| E2 | The "Gemini literature review" grounds the design in the field | **[CONTRADICTED]** | `gemini-session*.txt` are **task-assignment prompts to an execution agent** ("wire MemoryCore into the orchestrator"). There is no literature review in the corpus. The design is not grounded in any cited body of computational-neuroscience or cognitive-science work. |

**Summary:** Of the load-bearing assumptions, the only ones rated FACT/EVIDENCE-SUPPORTED belong to **Project A**. Everything specific to the "mind/soul/development" thesis is WEAK, SPECULATION, UNSUPPORTED, or CONTRADICTED.

---

## PHASE 2 — Dependency Graph & Minimal Core

**What actually runs the "cognitive" claim:**

```
concepts.json (32, seeded) ──► soul_graph (BFS) ──► arc string ──► "synthesis"
        ▲                                                │
        │ hardcoded BRIDGE_NODES                         ▼
knowledge_graph (seeded) ◄──────────────────── metacog (confidence heuristic)
world_ontology.json (seeded) ──► schema gatekeeper ──► (unused by hot path)
beliefs / goals / self_model / agentic_loop ──► (mostly narration over the above)
```

**True minimal core of the *current* system** (what you cannot delete and still have the demo work):
1. `concepts.json` — the seed.
2. `soul_graph.py` — BFS + edge-label templating.
3. A keyword→concept matcher.

That is the entire organism. **Everything else is scaffolding around a lookup table.** The belief store, goal manager, self-model, ontology, agentic loop, and metacognition layer are not on the path that produces the "impressive" answers; they are additional stores that the demo does not require. The 2026-06-01 audit already proved this empirically: 4 entire subsystems have **zero live callers**, two full query pipelines exist in parallel, and ~6,000 LOC is dead.

**Everything that can be removed with no loss to the demonstrated capability:** planning/, goals/, brain/, runtime/orchestrator, ops/circuit-breakers/load-shedding/failure-recovery (built, never wired), one of the two memory systems, two of three confidence systems, four of six monitors, the self-model stack, the foundational ontology, the agentic loop. By the audits' own accounting this is the large majority of the 30k LOC.

**Conclusion:** The smallest organism that reproduces today's behavior is a **32-node graph with a keyword matcher and a string templater** — roughly 300 lines. The other ~29,700 exist to make it *feel* like a mind. That asymmetry is the finding.

---

## PHASE 3 — Hidden Circular Dependencies

The user named the right cycles. They are real, and the current design pretends they aren't there by hand-seeding one side of each:

1. **Prediction ⇄ Memory.** You cannot predict without a stored model; you cannot decide what to store without predicting what will matter. *Current "resolution":* neither is real — memory is a JSON append log; prediction does not exist. The cycle is dodged, not broken.
2. **Concept ⇄ Grounding.** A concept needs grounding in experience; grounding needs concepts to organize experience. *Current "resolution":* concepts are typed by hand (`world_ontology.json`), grounding is skipped. This is exactly the symbol-grounding cycle GOFAI never escaped.
3. **Self ⇄ Theory-of-Mind.** Modeling your own mind and modeling others' minds co-bootstrap. *Current "resolution":* a self-model exists as a SQL join; ToM does not exist; so the cycle is amputated, not resolved.
4. **Language ⇄ Abstraction.** Words need concepts; sharpened concepts need language. *Current "resolution":* the "language" is substring matching; abstraction is a hand-built is-a tree. No co-development.

**The critical insight the current design misses:** these cycles do **not** prevent development. In every biological case they are broken by **time** — a *weak, noisy* version of each capability is sufficient to bootstrap a slightly-less-weak version of its partner, and the two ratchet up together (Piagetian sensorimotor bootstrapping; predictive-coding hierarchies; the "starting small" result of Elman 1993). Development *is* the process of resolving these cycles temporally.

VELYNX's error is to resolve every cycle **statically, by authoring both sides**. That is not development — it is the destination hand-drawn and mislabeled as the journey. **Any v2 that claims "development" must break these cycles temporally or it is not studying development at all.**

---

## PHASE 4 — Minimal Experimental Program (single-hypothesis, ranked by information gain)

Each experiment isolates one unknown. Ranked by *expected information gain* = (how much of the thesis it can kill) × (cheapness) × (unambiguity of outcome). Run in order; a failure at low numbers should stop the program.

**EXP-0 — Does the current "understanding" exceed a lookup table?** *(highest info gain, ~1 day)*
Freeze the code. Take the 100/100 benchmark. Paraphrase every query so no seeded concept keyword appears as a substring ("forgave" not "forgiveness"; "everything I built is gone" not "loss/grief"). Re-score. **Prediction: collapse to ≈ the 4.0/10 of the honest test.** If it collapses, Projects B and C are confirmed as ELIZA and the "mind" thesis is falsified *today*, before any new code. This single experiment is worth more than the last 30 phases.

**EXP-1 — Is confidence calibrated?** *(~1 day)*
Plot claimed tier vs. empirical correctness over ≥200 mixed queries (reliability diagram / ECE). **Prediction: near-zero calibration** (Q6 already shows CERTAIN-on-garbage). If uncalibrated, the Constitution's central promise ("uncertainty is honest") is currently false and must be fixed before anything else ships.

**EXP-2 — Does the affective→strategic bridge do measurable work?** *(~1 week)* — *the one experiment that could find real signal.*
Hypothesis: routing a problem through an affective frame ("this is a *shame/failure* situation") selects a problem-solving schema that improves outcomes vs. a no-frame baseline, on a task with an objective score (e.g., debugging fixes, planning-task success). One variable: frame present/absent. If the framed condition wins on an objective metric, there is a publishable kernel. If not, delete `BRIDGE_NODES`.

**EXP-3 — Minimal predictive organism: does prediction-error drive representation change?** *(~1 month)* — *the actual developmental experiment.*
Build the smallest agent that (a) receives a sensorimotor stream, (b) predicts the next observation, (c) modifies its model to reduce prediction error, (d) **adds representational capacity only when error stays high.** Measure whether structure *emerges* (clustering of states) without being seeded. This is the only experiment that tests "development" in the sense the project claims.

**EXP-4 — Do cycles bootstrap?** *(gated behind EXP-3 success)*
Give EXP-3's organism a second modality and test whether a weak predictor in one channel improves the other (prediction⇄memory co-development). One variable: cross-channel coupling on/off.

Anything requiring a self-model, ontology, or agentic planner is **downstream of EXP-3** and must not be built until EXP-3 shows emergent structure.

---

## PHASE 5 — VELYNX v2 (a research program, not an architecture)

### Core hypotheses (exactly three; each falsifiable)
- **H1 (Calibration).** A retrieval agent can report uncertainty tiers whose empirical correctness matches the tier (ECE < 0.1). *This is Project A's real contribution and is worth finishing.*
- **H2 (Affective indexing).** A learned mapping from affective framing to problem-solving schema improves objective task outcomes over an unframed baseline. *This is the only novel kernel.*
- **H3 (Emergent development).** An agent that minimizes sensorimotor prediction error, with capacity added only on persistent error, spontaneously develops reusable internal structure not present at initialization. *This is the "mind" thesis, stated so it can fail.*

### Minimal organism
A single loop: **sense → predict → compare → update model → (grow capacity iff error persists)**. No seeded concepts. No hand-authored ontology. No self-model. No belief/goal modules. Concepts, if they are real, must appear as *clusters the system was not given*. Selfhood, if real, must appear as a *learned self-vs-world prediction boundary*, not a SQL join.

### Experimental milestones
1. EXP-0/EXP-1 executed on the frozen current system → decide whether to archive B/C. *(Week 1)*
2. H1: calibrated retrieval agent shipped and measured. *(Month 1)*
3. H2: affective-indexing experiment with objective metric. *(Month 2)*
4. H3: minimal predictive organism shows emergent clustering. *(Month 3–6)*
5. Cycle bootstrapping (EXP-4). *(Month 6–12)*

### Success criteria
- H1: ECE < 0.1 on held-out mixed queries.
- H2: framed condition beats baseline at p<0.01 on an objective task score.
- H3: emergent representations transfer to a held-out prediction task above an untrained-structure control.

### Failure criteria
- H1: calibration no better than a constant-confidence baseline.
- H2: no significant difference, or bridges must be re-authored per task.
- H3: no structure emerges beyond what initialization + input statistics trivially provide.

### Kill criteria (stop the whole "mind" program)
- **EXP-0 shows collapse under paraphrase AND EXP-3 shows no emergent structure after two honest attempts.** At that point the developmental thesis is dead; keep Project A as a product and publish the negative result.

### Pivot criteria
- If H2 succeeds but H3 fails → pivot to a **narrow, honest product**: an affect-aware problem-solving assistant. Real, useful, modest.
- If H3 succeeds but is intractably slow → pivot to the *theory* (a minimal model of developmental bootstrapping) rather than a deployed system.

---

## PHASE 6 — Reviewer #2 (attempt to destroy VELYNX)

> **Reject.** The manuscript claims a "raised synthetic mind" that "develops," but the system is a 32-entry hand-authored lookup table wrapped in ~30k lines of symbolic scaffolding, most of which the authors' own audit shows is dead or duplicated. **Nothing develops:** every concept, edge, bridge, and ontology node is hand-specified; the "curriculum" ships with `expected_answer`. The headline 100/100 result is obtained on queries selected to contain the seeded keywords; the authors' own adversarial test collapses to 4.0/10 the moment morphology changes ("forgave" ≠ "forgiveness"), and the system emits `CERTAIN` on a hallucinated Wikipedia mashup. The "arcs" offered as reasoning are string concatenations of author-supplied edge labels — an ELIZA effect. The design cites no literature (the "review" is a set of task prompts to a coding agent), makes zero contact with neuroscience (no neural dynamics, no learning rule, no biological constraint, no quantitative fit to any phenomenon), and re-commits the two canonical GOFAI failures — **symbol grounding** and **hand-specified world models don't scale.** The circular dependencies the authors gesture at (prediction/memory, self/ToM) are "resolved" by authoring both endpoints, which is precisely *not* development. There is no measurement of anything against ground truth except the one test the authors then ignored. This is not a computational model of cognition; it is a themed chatbot with introspective narration. Recommend rejection without re-review.

**What survives that review, and why:**

1. **The epistemic constitution as engineering discipline.** "Trace every claim, tier your confidence, say 'I don't know,' never present DEBATED as CERTAIN" is a genuinely good stance and rare in LLM products. It survives as *design principle*, not as science — and only once EXP-1 makes it true instead of decorative.
2. **One real hypothesis (H2).** The affect→strategy bridge is a non-obvious idea: that *emotional framing indexes procedural knowledge*. It connects loosely to appraisal theory and somatic-marker ideas but the specific "shame→debugging/refactoring, planning→architecture/abstraction" mapping, *if it measurably improved task outcomes*, would be a small but real result. Right now it is an untested dict. EXP-2 is its trial.
3. **The developmental question itself (H3)** — stated correctly for the first time in Section 4/5 — is a legitimate research question. It just has essentially no overlap with what has been built.

Everything else does not survive.

---

## Precise location of genuine novelty

- **Not** in the soul graph (a knowledge graph), the self-model (a SQL join), the ontology (a hand-built taxonomy), or the agentic loop (a standard planner sketch). These are competent-to-derivative re-implementations of known things.
- **The single novel seed** is the *affective-indexing hypothesis* (H2): using emotional framing as the retrieval key for problem-solving schemas. Novel enough to test. Not yet novel enough to claim — it has never been measured.

## What to do Monday
1. Run **EXP-0** (paraphrase the benchmark). One day. It will tell you the truth about the last year.
2. Run **EXP-1** (calibration curve). One day.
3. Based on those two numbers, decide: **finish Project A as an honest product**, and **archive Projects B and C** unless EXP-2 finds signal.
4. Do not write another symbolic module until EXP-3 shows structure can emerge instead of being seeded.

*Optimize for truth, not elegance. The kindest thing I can tell you is the thing the repo already told you in `soul_test_report.md` and buried under 100/100: most of this is scaffolding around a lookup table, and the one idea worth keeping has never been tested. Test it.*

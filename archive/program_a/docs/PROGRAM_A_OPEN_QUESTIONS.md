# PROGRAM A — OPEN QUESTIONS

**Authority:** Chief Scientist / Chief Systems Architect design review,
2026-07-07. Each question is one the repository genuinely does not answer.
None may be resolved by silent implementation choice; each names its decider.
Answering Q1-Q4 is the precondition for any Program A code.

---

### Q1 — What is the tier-emission mechanism?
**The question:** By what frozen rule does Program A map its evidence state
to exactly one of `{UNKNOWN, DEBATED, PROBABLE, CERTAIN}`?
**What the repo fixes:** the tier set (`dataset.py:17`); that the tier is a
public emission, not retrieval relevance, not a remap, not post-hoc
calibration (prereg §1, §4 #5, §5, §6); that the mechanism must be frozen
before outputs are observed; that its numeric-confidence side channel is
exploratory only.
**What the repo does not fix:** the rule itself. No document specifies it.
**Constraint worth naming:** the interpretation is pinned — `p_i` is "the
predictor's estimated probability that `answer_i` is empirically correct
under the frozen EXP-1 answer rubric" (prereg §1). Any mechanism whose tier
does not mean *that* is a category error before execution.
**Decider:** ScientificAuditor via the Phase-1 mechanism preregistration
(`PROGRAM_A_ADAPTER_AUDIT.md` §6 item 6). **[OPEN QUESTION]**

### Q2 — Live web or frozen snapshot at execution time?
**The question:** Does the emission surface retrieve from the live web during
the 22 seed replicates, or from a frozen retrieval snapshot?
**Tension:** `PROGRAM_A_BINDING_SPEC.md` §4 requires determinism and replay
compatibility; `unified_retriever.py` is live-web and time-dependent. But
prereg §7 explicitly anticipates "seed-level stochasticity in retrieval",
and `EXP1_DATASET_SPEC.md` §15 pins only dataset/rubric provider-independence,
not answer-time retrieval. Both readings have textual support.
**Consequences:** live → replay is approximate and FM-6 (drift-induced seed
kill) is live; snapshot → snapshot construction must itself pass leakage
review (a snapshot curated after seeing the frozen queries is adjacent to
tuning). **Decider:** Architect + ScientificAuditor (roadmap T0).
**[OPEN QUESTION]**

### Q3 — What does the seed actually vary?
**The question:** If the mechanism (Q1) and retrieval mode (Q2) are fully
deterministic, all 22 replicates are byte-identical; prereg §7's own text
("If implementation evidence before execution implies a true seed-level
kill-relevant effect below 10%, this preregistration is underpowered and
must be amended before outputs are observed") then requires an amendment
*before* execution. The seed's variance source must be identified and
documented — or the amendment clause invoked.
**Decider:** ScientificAuditor, before G6. **[OPEN QUESTION]**

### Q4 — Where does the code live?
**The question:** `research/` composition layer, `program_a/` (with a
packaging change), or `scripts/`?
**Fixed constraints:** not in `experiments/EXP1/` if it imports `backend/`
(architecture.md §4 rule 2); `program_a/` is outside `pyproject.toml`
packages.find (R-16); `research/` has the existing compose-without-mutating
precedent. **Decider:** Architect (BINDING_SPEC open item 1).
**[OPEN QUESTION]**

### Q5 — Is the passive Goodhart guard canonically sufficient?
**The question:** `EXP1_PREREGISTRATION.md:74,166` certifies locked
equal-width bins + the `protocol_violation` flag as the guard;
`STATISTICAL_AUDIT.md:188` holds an active detector (EXP1-05) is required
and unimplemented. `EXP1_TRACE.md` records the dissent as unresolved and the
DEFERRED categorization as provisional.
**Decider:** ScientificAuditor (roadmap G3). If the active detector is ruled
required, it is promoted to a MISSING link before any pass claim.
**[OPEN QUESTION]**

### Q6 — Is the BM25/TF-IDF random-confidence control required for the pass claim?
**The question:** Canon §6-H1 names the control ("BM25/TF-IDF retrieval with
randomly assigned confidence") as H1's H₀ baseline; the preregistration's §4
kill criteria do not include it; roadmap EXP1-04 defers it
(`EXP1_TRACE.md` ML-13). Is it needed for the EXP-1 verdict, or only for the
publication comparing against a constant-confidence baseline?
**Note:** the tier-independence test (`decision.py:111-166`) already
implements "no better than constant confidence" statistically — whether that
discharges the canon's control clause is a scientific ruling, not an
engineering one. **Decider:** ScientificAuditor. **[OPEN QUESTION]**

### Q7 — May Program A read (not write) backend stores during execution?
**The question:** The side-effect-free rule (BINDING_SPEC §4) prohibits
writes and perturbation; no document prohibits reads (e.g., a static local
corpus). Reads of *mutable* stores would smuggle hidden state past the
determinism requirement; reads of frozen assets would not.
**Decider:** fold into the T1 mechanism spec; ScientificAuditor.
**[OPEN QUESTION]**

### Q8 — What is Program A's identity string and versioning discipline?
**The question:** `program-a-public-v1` appears as the exemplar adapter_id
(BINDING_SPEC §4). Does the manifest identity encode the mechanism-spec
version (so a mechanism change forces a new adapter_id and re-freeze), or is
it a free label? The manifest verifies identity equality
(`run.py:147-148`) but nothing binds the string to the frozen spec commit.
**Decider:** Architect + Release Manager; low cost, decide in G1/G4.
**[OPEN QUESTION]**

### Q9 — Who adjudicates: humans, a frozen automated scorer, or both?
**The question:** Prereg §3 and dataset-spec §8 constrain *what* the
adjudicator may consider, and `run.py:40` fixes its return type — but not
whether adjudication is human, automated, or hybrid, nor how inter-rater
disputes on ambiguous rows are resolved. `adjudicator_id` is recorded in the
manifest, implying a stable, nameable procedure.
**Decider:** the T3 adjudicator spec; ScientificAuditor. (An EXP-1 link-3
question rather than a Program A question, but the Program A verdict is
hostage to it.) **[OPEN QUESTION]**

### Q10 — When is EXP-0 run relative to EXP-1?
**The question:** Canon §11 names EXP-0 the immediate next step; the Research
Director's Sprint-2 authorization requires it "before or alongside EXP-1,
and before any external Program-A honesty claim" (condition 3). No document
records EXP-0 as executed (`experiments/EXP0/` protocol exists; no run
artifacts were verified this session — insufficient evidence either way).
**Decider:** Research Director scheduling; verify EXP-0 run-state before G6.
**[OPEN QUESTION]**

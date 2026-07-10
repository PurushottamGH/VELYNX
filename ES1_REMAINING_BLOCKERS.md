# ES-1 — REMAINING BLOCKERS REGISTER

**Authority:** Chief Scientific Architect, 2026-07-07.
**Scope:** Reconciliation of the two independent ES-1 reviews.
Review A (lawfulness, `PROGRAM_A_CONFIDENCE_MECHANISM.md` §4–§9): **PASS** —
ES-1 is the unique surviving lawful mechanism class.
Review B (implementation readiness, `PROGRAM_A_BINDING_SPEC.md` §11 verdict
FAIL + open items in `PROGRAM_A_CONFIDENCE_RISKS.md`,
`PROGRAM_A_CONFIDENCE_REQUIREMENTS.md`, `PROGRAM_A_OPEN_QUESTIONS.md`):
**FAIL** — not ready for implementation.
**Rule of this document:** the two verdicts are not in contradiction.
Review A judged the *science*; Review B judged the *state of the process*.
No blocker below requires redesigning ES-1; every blocker is an unresolved
decision, an ungoverned sign-off, a missing guard, or a missing document.
**No new science is introduced here.** Tags: `[FACT]`, `[INFERENCE]`.

Classification key — each blocker states:
- **Class:** implementation / governance / scientific / documentation / preregistration
- **Why it fails**
- **Blocks:** implementation / EXP-0 / EXP-1 / publication
- **Minimal correction**
- **Correction instrument:** canonical amendment / preregistration amendment /
  implementation change / documentation update / ScientificAuditor approval only

---

## B-1 — ES-1 is recommended, not adopted (Q1)

- **Class:** governance + preregistration.
- **Why it fails:** `PROGRAM_A_CONFIDENCE_MECHANISM.md` explicitly does not
  self-authorize ("Q1's decider remains the ScientificAuditor via the T1
  mechanism preregistration"). No T1 document exists; no sign-off exists.
  **[FACT]** roadmap T1/G4 are OPEN.
- **Blocks:** implementation (hard — CF-R12: "no emission-surface code before
  G2 + T1 + G4"), therefore transitively EXP-1 and publication. Does **not**
  block EXP-0 (EXP-0 is Program-independent per roadmap T9).
- **Minimal correction:** author the T1 mechanism preregistration verbatim
  from MECHANISM §7 (state table §7.2, precedence order from DECISION_TREE
  Tree 2, free-constant register §7.4, semantic argument per tier per CR-2);
  submit to ScientificAuditor.
- **Instrument:** new preregistration document (T1) + **ScientificAuditor
  approval only**. No canonical amendment; no change to EXP-1's existing
  preregistration.

## B-2 — Retrieval mode unresolved: snapshot vs live (Q2 / CF-R4)

- **Class:** scientific decision, governance-gated. Not a design flaw in
  ES-1 — ES-1 is compatible with both modes (MECHANISM §8 item 2).
- **Why it fails:** live retrieval breaks per-`(query, seed)` determinism and
  replay (CR-4, BINDING_SPEC §4); a snapshot built after seeing frozen
  queries is leakage-adjacent and needs its own review. Neither branch is
  decided; T4 cannot be written without knowing its retrieval substrate.
- **Blocks:** implementation (T4 input undefined) and EXP-1 validity.
- **Minimal correction:** T0 written decision. Recommended disposition
  already on record (frozen snapshot + documented leakage review, CF-R4);
  the decision only needs ratification, not invention.
- **Instrument:** documentation update (decision recorded in T1 spec) +
  Architect + ScientificAuditor sign-off. No canonical amendment.

## B-3 — Forced power amendment: 22 identical replicates (Q3 / CF-R5 / CR-15)

- **Class:** preregistration.
- **Why it fails:** ES-1 on a frozen snapshot is fully deterministic ⇒ all 22
  seed replicates are byte-identical ⇒ EXP-1 prereg §7's own clause fires
  ("underpowered and must be amended before outputs are observed").
  Executing without the amendment is a protocol defect; amending after
  outputs is a kill. **[FACT]** this is forced, not optional (CF-R5).
- **Blocks:** EXP-1 execution. Does **not** block implementation (the surface
  can be built while the amendment is processed) and does not block EXP-0.
- **Minimal correction:** invoke prereg §7's amendment clause before G6,
  restating the power design for a deterministic mechanism (e.g., n=1
  effective replicate with the seed recorded as a no-op, or a declared,
  justified variance source — the *choice* is the ScientificAuditor's; both
  branches are already framed in CF-R5).
- **Instrument:** **preregistration amendment** (EXP-1 prereg §7), before any
  frozen-row output is observed + ScientificAuditor sign-off.

## B-4 — Open cheat channel: `gold_rubric`/`query_family` visible at answer time (CF-R1 / CR-3 / L11)

- **Class:** implementation.
- **Why it fails:** the runner passes the full `QueryRecord` into
  `adapter.answer(query, seed)` (`experiments/EXP1/dataset.py:33-41`,
  `run.py:84,181`). Nothing guards the channel; a mechanism reading these
  fields fakes calibration undetectably. ES-1's spec already forbids the read
  (L11) — the failure is that the prohibition is unenforced.
- **Blocks:** EXP-1 validity (an unguarded channel makes any ECE result
  unauditable) and implementation acceptance (G5). Not EXP-0.
- **Minimal correction:** the sentinel-substitution test named in CR-3:
  drive the surface with `gold_rubric` and `query_family` replaced by
  sentinels and assert byte-identical output. The redacted-view production
  change is the stronger fix but is **not** minimal and needs its own
  Reviewer + ScientificAuditor sign-off (F-10-style); it is optional.
- **Instrument:** implementation change (one test) + documentation update
  (test registered against CR-3). No amendment of any kind.

## B-5 — Code location undecided (Q4 / G1)

- **Class:** governance.
- **Why it fails:** `research/` vs `program_a/` vs `scripts/` is unruled;
  packaging constraint R-16 and architecture rule "not in `experiments/EXP1/`
  if it imports `backend/`" bound the space but do not pick. T4/T8 cannot
  start without a target directory.
- **Blocks:** implementation only.
- **Minimal correction:** Architect written ruling (BINDING_SPEC open item 1).
- **Instrument:** documentation update (written decision). Architect —
  not ScientificAuditor — is the decider; no amendment.

## B-6 — Import deny-list unenforced (CR-10 / TD-08 / T7)

- **Class:** implementation.
- **Why it fails:** the `[REJECTED]`-mechanism deny-list (canon `:90`) is
  binding on ES-1's dependency closure (Tree 1 gate G-E), but no import-guard
  test exists (roadmap T7; TD-08 "rejected science persists as live code,
  no guard"). Compliance is currently by promise, not by CI.
- **Blocks:** implementation acceptance (G5) and any pass claim; a forbidden
  transitive import at run time is a canonical violation regardless of ECE
  (CR-10 kill map).
- **Minimal correction:** implement T7 — CI test that fails on any forbidden
  transitive import of the emission surface, per
  `PROGRAM_A_DEPENDENCY_GRAPH.md` §4. Depends on B-5 (needs the location).
- **Instrument:** implementation change only.

## B-7 — Tier-validation bypass on direct construction (CR-13 / F-10 / T6)

- **Class:** implementation.
- **Why it fails:** direct `AnswerRecord` construction bypasses tier
  validation (`dataset.py:113-141`; ADAPTER_AUDIT §7). An invalid tier could
  enter the run unvalidated. Interim discipline (construct via
  `from_mapping` only) is convention, not enforcement.
- **Blocks:** EXP-1 validity (data-integrity of the emitted records); G5.
- **Minimal correction:** T6 — enforce validation on direct construction (or
  re-validate in `_coerce_answer_record`) and invert
  `test_direct_construction_does_not_validate_tier` into a rejection test.
- **Instrument:** implementation change + Reviewer + ScientificAuditor
  sign-off as already scoped in roadmap T6.

## B-8 — Identity/versioning discipline unruled (Q8 / CR-12 / CF-R11)

- **Class:** governance + documentation.
- **Why it fails:** nothing binds `program_a_adapter_id` to the frozen
  mechanism-spec commit; a spec change without an id change makes replay
  silently compare different mechanisms.
- **Blocks:** nothing hard pre-implementation; blocks *replay integrity* of
  EXP-1 if left open past G4.
- **Minimal correction:** adopt the interim rule already on record (encode
  the T1 spec version in the id string, CF-R11) at G4; final ruling by
  Architect + Release Manager in G1/G4.
- **Instrument:** documentation update; no amendment.

## B-9 — Untested support-test failure modes require the pre-freeze dry run (CF-R2 / CF-R6 / T10)

- **Class:** implementation (verification), with a scientific consequence.
- **Why it fails:** the claim-support test is ES-1's load-bearing
  sub-component. If it false-positives on fabricated claims, S3 fires on
  hallucination rows → `CERTAIN` on a fabricated answer → zero-tolerance
  FM-1 kill (CF-R2). If it is too strict/lax, tier distribution degenerates
  (< 2 tiers ⇒ kill; CF-R6). The lawful response window is **before freeze
  only**. Today no dry run exists and no synthetic non-frozen corpus exists.
- **Blocks:** does not block starting implementation (T4 builds the thing
  the dry run exercises); blocks **G4-freeze prudence** and EXP-1 (running
  without the dry run converts a designable-out defect into an irreversible
  kill). Distinct from M13: T10 verifies *mechanics* (determinism, artifacts,
  tier reachability), it does not fit constants — no auditor ruling needed
  for that scope.
- **Minimal correction:** execute roadmap T10 on a synthetic, non-frozen
  corpus with fabrication pressure before G4/G6; entity-level (not
  topic-level) support matching, and "retrieved but non-supporting = S0",
  are already specified dispositions (CF-R2), not new design.
- **Instrument:** implementation change (dry-run harness + corpus) +
  documentation update (results recorded pre-freeze).

## B-10 — L8 scope ruling for the M12 fallback (CF-R9 / MECHANISM §7.3)

- **Class:** scientific ruling, governance-gated.
- **Why it fails:** ES-1 itself sidesteps L8 (it contains no probability
  numbers), but the designated fallback (M12) is load-bearing on the
  unresolved "mirror" reading of MASTER_SPEC §7 item 3, and M12's ε has no
  lawful provenance. If ES-1 is rejected at T1 with the fallback
  unadjudicated, the program stalls with no lawful path.
- **Blocks:** nothing on the ES-1 happy path; blocks the *fallback* path
  only. Listed because Review B correctly treats an unadjudicated fallback
  as a process defect.
- **Minimal correction:** obtain the L8-scope ruling **at** T1 even if ES-1
  is adopted (the disposition CF-R9 already prescribes).
- **Instrument:** **ScientificAuditor approval only** (a ruling, recorded in
  T1; no amendment, no code).

## B-11 — Dev-corpus lawfulness unruled (CF-R10 / M13 / CR-7)

- **Class:** scientific ruling, governance-gated.
- **Why it fails:** whether pre-freeze checks against a disjoint dev corpus
  are lawful, and under what documentation duty, is unruled; until ruled,
  M13-style *fitting* is prohibited (CR-7). Ambiguity here is a Goodhart
  channel (canon §6-H1 in spirit).
- **Blocks:** nothing, provided nothing is fitted. It bounds what B-9's dry
  run may be used for: mechanics verification yes, constant-tuning no.
- **Minimal correction:** ScientificAuditor ruling at T1 with, if permitted,
  a single pre-registered dev evaluation and a declared change budget
  (CF-R10 disposition, verbatim).
- **Instrument:** **ScientificAuditor approval only.**

## B-12 — No real specialist sign-offs exist (CF-R12 / R-08)

- **Class:** governance. The master blocker.
- **Why it fails:** every specialist channel was unavailable when the
  analysis corpus was authored; building from the analysis without T1/G4
  sign-off "would itself be the fabricated-approvals threat named in
  MASTER_SPEC §16." **[FACT]** This alone sustains Review B's FAIL even if
  every other blocker were closed on paper.
- **Blocks:** implementation, EXP-1, publication.
- **Minimal correction:** route B-1, B-2, B-3, B-10, B-11 to the real
  ScientificAuditor / Architect / Release Manager; record dated, named
  sign-offs. There is no self-service correction.
- **Instrument:** governance sign-offs (G2, T0, T1, G4). No document I can
  author discharges this.

## B-13 — Free-constant register not yet in preregistration form (CR-11 / CF-R8)

- **Class:** preregistration + documentation.
- **Why it fails:** ES-1's four structural constants ("≥2 independent
  origins", independence relation, claim-support test, materiality rule)
  are named in MECHANISM §7.4 but not yet embedded in a T1 preregistration
  with per-constant a-priori justifications. Unjustified, they reproduce the
  uncited-constant pattern (canon §8) the mechanism was selected to avoid.
- **Blocks:** T1 sign-off, hence implementation.
- **Minimal correction:** carry MECHANISM §7.4 into T1 verbatim, adding one
  a-priori justification sentence per constant; ScientificAuditor reviews as
  part of B-1. No constant may be added, removed, or tuned in the process.
- **Instrument:** preregistration content (inside the new T1 document) +
  ScientificAuditor approval.

## B-14 — Backend read-access scope unresolved (Q7)

- **Class:** scientific ruling, minor.
- **Why it fails:** reads of *mutable* stores would smuggle hidden state past
  determinism; reads of frozen assets would not. Unruled.
- **Blocks:** T1 completeness only (the spec must state what the surface may
  read); folds into B-1.
- **Minimal correction:** one clause in T1 (already the prescribed
  disposition: "fold into the T1 mechanism spec").
- **Instrument:** T1 content + **ScientificAuditor approval only.**

## B-15 — EXP-0 not verified as run (Q10 / T9 / Research Director condition 3)

- **Class:** governance (scheduling), outside ES-1 proper.
- **Why it fails:** EXP-0 must run "before or alongside EXP-1, and before any
  external Program-A honesty claim"; no run artifacts verified.
- **Blocks:** EXP-1 execution timing and publication. Does **not** block
  ES-1 implementation.
- **Minimal correction:** verify EXP-0 run-state; schedule T9 if absent.
- **Instrument:** none for ES-1; Research Director scheduling.

## B-16 — Verdict-side rulings pending: Goodhart guard and H₀ control (Q5 / Q6 / G3)

- **Class:** scientific rulings on the *evaluation* side, not on ES-1.
- **Why it fails:** whether the passive Goodhart guard suffices (vs active
  detector EXP1-05) and whether the BM25/random-confidence control is
  required for the verdict remain open dissents.
- **Blocks:** publication / pass claim (G3 "must resolve before any PASS
  claim — not before execution"). Not implementation, not EXP-0, not the
  EXP-1 run itself.
- **Minimal correction:** ScientificAuditor rulings at G3; no ES-1 change
  under any ruling outcome (both concern the evaluator).
- **Instrument:** **ScientificAuditor approval only.**

---

## Summary matrix

| # | Blocker | Class | Blocks impl. | Blocks EXP-0 | Blocks EXP-1 | Blocks publ. | Instrument |
|---|---|---|---|---|---|---|---|
| B-1 | Q1 adoption / T1 absent | gov + prereg | ● | — | ● | ● | new T1 + Auditor |
| B-2 | Q2 retrieval mode | scientific (gated) | ● | — | ● | ● | T0 decision record |
| B-3 | Q3 forced §7 amendment | preregistration | — | — | ● | ● | prereg amendment |
| B-4 | CF-R1 cheat channel | implementation | ●(G5) | — | ● | ● | sentinel test |
| B-5 | Q4 code location | governance | ● | — | — | — | Architect ruling |
| B-6 | TD-08 import guard | implementation | ●(G5) | — | ● | ● | T7 test |
| B-7 | F-10 validation bypass | implementation | ●(G5) | — | ● | ● | T6 fix |
| B-8 | Q8 identity binding | gov + doc | — | — | ●(replay) | — | interim id rule |
| B-9 | dry run T10 | implementation | — | — | ● | ● | T10 harness |
| B-10 | L8 scope (fallback) | scientific ruling | — | — | — | — | Auditor ruling |
| B-11 | dev-corpus ruling | scientific ruling | — | — | — | — | Auditor ruling |
| B-12 | no real sign-offs | governance | ● | — | ● | ● | G2/T0/T1/G4 |
| B-13 | free-constant register | preregistration | ● (via T1) | — | ● | ● | T1 content |
| B-14 | Q7 read scope | scientific ruling | ● (via T1) | — | ● | — | T1 clause |
| B-15 | EXP-0 unverified | governance | — | ○ (is EXP-0) | ● (timing) | ● | scheduling |
| B-16 | Q5/Q6 verdict rulings | scientific ruling | — | — | — | ● | Auditor at G3 |

**[INFERENCE]** No blocker touches the ES-1 state table, tier map, answer
coupling, or constant set. Review A's PASS is undisturbed. Review B's FAIL
is fully accounted for by the sixteen items above, all of which close by
decision, sign-off, test, or document — none by redesign.

# ES-1 — IMPLEMENTATION GATE

**Authority:** Chief Scientific Architect, 2026-07-07.
**Function:** the single checklist that converts the current **NO-GO** into
**GO** for writing emission-surface code (roadmap T4/T8). This gate encodes
— it does not replace — the existing gates G1, G2, T0, T1, G4 and the hard
rule of CF-R12: *no emission-surface code before G2 + T1 + G4 are discharged
by real specialists.*

---

## Gate criteria (ALL must be checked, with dated, named sign-offs)

### Section A — Rulings and decisions

- [ ] **A1 (B-5/G1):** Architect's written location ruling on record.
- [ ] **A2 (B-12/G2):** ScientificAuditor ratification of tier-source
      lawfulness on record.
- [ ] **A3 (B-2/T0):** Retrieval-mode decision (snapshot vs live) recorded,
      signed by Architect + ScientificAuditor; if snapshot, the leakage-review
      procedure for snapshot construction is named.
- [ ] **A4 (B-3/T0):** Seed-variance disposition recorded; the EXP-1 prereg
      §7 power amendment is drafted and submitted (adjudication may complete
      later, but **must** complete before G6/T11 — see Residual duties).

### Section B — The T1 preregistration

- [ ] **B1 (B-1):** `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` committed,
      containing exactly: ES-1 states/coupling/tier map with frozen
      precedence, per-tier semantic argument (CR-2), free-constant register
      with a-priori justifications (B-13/CR-11), resolved Q2/Q3 (CR-15),
      input restriction incl. Q7 read scope (B-4/B-14/CR-3), identity clause
      (B-8/CR-12 interim), the two requested rulings (B-10 L8 scope,
      B-11 dev-corpus lawfulness), and the PA-3 closure material from
      `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` (§A1, §A2, §A4, §A7, and
      §A6-DIGEST as applicable).
- [ ] **B2 (B-1/B-12):** ScientificAuditor sign-off on T1 and the PA-3 freeze
      addendum — named, dated, and recorded without proxy approval.
- [ ] **B3 (B-12/G4):** Release Manager freeze — pinned commit hash of the
      T1 spec plus co-frozen `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` recorded,
      before any frozen-row output is observed.

### Section C — Enforcement in place (may land in parallel, must be green at gate time)

- [ ] **C1 (B-4):** Sentinel-substitution test exists and passes (rubric/
      family fields invisible to the surface — byte-identical output).
- [ ] **C2 (B-7):** F-10 fixed; direct-construction tier-validation
      rejection test passes.
- [ ] **C3 (B-6):** Import-guard test exists for the ruled location and
      passes (deny-list per `PROGRAM_A_DEPENDENCY_GRAPH.md` §4).

### Gate condition

**GO for implementation ⇔ A1–A4 ∧ B1–B3 ∧ C1–C3.**
Any unchecked box ⇒ NO-GO stands. No box may be checked by the author of the
code, and none may be checked by this document's author on a specialist's
behalf (MASTER_SPEC §16; R-08).

---

## Residual duties that GO does *not* discharge

GO at this gate authorizes **T4/T8 code only**. It does not authorize
execution or any claim. Still owed downstream, unchanged:

1. **Before EXP-1 execution (G6/T11):** prereg §7 amendment adjudicated
   (B-3); T10 dry run completed within its B-11 scope limits (B-9); EXP-0
   run before or alongside (B-15); dataset freeze T2/adjudicator T3;
   pre-run lock verification.
2. **Before any PASS claim / publication:** G3 rulings on the Goodhart
   guard and the H₀ control (B-16); faithful reporting of pass **or** kill
   (canon §8 — a kill is a reportable scientific outcome, not a failure of
   this process).

---

## FINAL DECISION

### **NO-GO** for implementation, as of 2026-07-07.

**Grounds:** Review A's PASS establishes that ES-1 is scientifically lawful
and requires no redesign — nothing in the blocker register touches its
science. Review B's FAIL is sustained on process: zero of the nine gate
boxes above are currently checkable. The controlling blockers are
**B-12** (no real specialist sign-offs exist; building now would be the
fabricated-approvals threat named in MASTER_SPEC §16), **B-1** (no T1
preregistration), and **B-5/B-2** (location and retrieval mode undecided —
the code has no lawful target or substrate).

**Path to GO:** execute `ES1_CORRECTION_PLAN.md` Waves 1–3 and include the
PA-3 freeze-addendum reconciliation required for G4. Every correction is a
decision, signature, document, or test — none is science. The moment A1–A4,
B1–B3, C1–C3 carry real signatures, the co-frozen addendum is pinned by
Release Manager, and the enforcement tests are green, this gate flips to GO
with no further review of ES-1 itself required.

**Standing prohibition until then:** no emission-surface or binding code may
be written, merged, or prototyped-in-place; no frozen-row output may be
observed by anyone in any capacity.

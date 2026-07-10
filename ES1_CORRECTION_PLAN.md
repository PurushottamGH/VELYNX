# ES-1 — CORRECTION PLAN

**Authority:** Chief Scientific Architect, 2026-07-07.
**Input:** `ES1_REMAINING_BLOCKERS.md` (B-1…B-16).
**Rule:** minimal corrections only. No blocker is closed by changing ES-1's
science (state table, tier map, answer coupling, constants — all frozen as
recommended in `PROGRAM_A_CONFIDENCE_MECHANISM.md` §7). Every correction
below is a decision to obtain, a document to author, a test to add, or a
fix already scoped in the roadmap. Owners and gate names are unchanged from
`PROGRAM_A_IMPLEMENTATION_ROADMAP.md`.

---

## Wave 1 — Decisions and rulings (no code; unblocks everything else)

| Step | Closes | Action | Owner / instrument |
|---|---|---|---|
| W1.1 | B-5 | Architect rules the code location (Q4/G1): `research/` vs `program_a/` vs `scripts/`, with R-16 packaging note. Written decision, one page. | Architect — documentation update |
| W1.2 | B-12 (part), B-1 (precondition) | ScientificAuditor discharges G2 (tier-source lawfulness ratification of the Director's provisional conclusion). | ScientificAuditor — approval only |
| W1.3 | B-2 | T0 decision: retrieval mode. Recommended ratification target: **frozen snapshot constructed under documented leakage review** (CF-R4 disposition). Recorded as a section of the T1 draft. | Architect + ScientificAuditor — documentation update |
| W1.4 | B-3 (initiation) | Draft the EXP-1 prereg §7 power amendment for the deterministic case; submit with T1 so it is adjudicated **before** G6 and before any frozen-row output. | Builder draft + ScientificAuditor — **preregistration amendment** |

Wave 1 has no internal ordering except W1.2 before W1.3 (roadmap: T0 blocked
by G1, G2).

## Wave 2 — The T1 preregistration package (one document, five closures)

Author **`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md`** containing, verbatim
from the existing corpus (assembly, not invention):

1. The ES-1 rule: states S0–S3, definitions, answer-construction coupling,
   tier map, precedence order S0 → S1 → (S2|S3) (MECHANISM §7.2;
   DECISION_TREE Tree 2). — closes the content half of **B-1**
2. Per-tier semantic argument tying each state's tier to estimated
   rubric-correctness (MECHANISM §7.2 justification block; CR-2). — **B-1**
3. Free-constant register with one a-priori justification per constant;
   declaration that none may ever be tuned (MECHANISM §7.4; CR-11). — **B-13**
4. Resolved Q2 mode and Q3 disposition (from W1.3/W1.4; CR-15). — **B-2, B-3**
5. Input restriction: reads `query.query` (+ `query.query_id` echo) only
   (L11/CR-3), and the Q7 read-scope clause (frozen assets readable, mutable
   stores not). — **B-4 (spec half), B-14**
6. Requested rulings, answered in the sign-off: L8 scope for the M12
   fallback (CF-R9) and dev-corpus lawfulness with change budget (CF-R10).
   — **B-10, B-11**
7. Identity clause: `adapter_id` encodes the T1 spec version until the Q8
   ruling (CF-R11 interim rule). — **B-8**

Then: **ScientificAuditor sign-off (T1)** → **Release Manager freeze (G4,
pinned commit)**. These two signatures close **B-1** and the remaining core
of **B-12**. — instruments: new preregistration + approvals; **no canonical
amendment is required anywhere in this plan.**

## Wave 3 — Independent engineering fixes (parallel with Waves 1–2; already-scoped roadmap tasks)

| Step | Closes | Action | Roadmap task |
|---|---|---|---|
| W3.1 | B-4 (enforcement half) | Sentinel-substitution test: run the surface with `gold_rubric`/`query_family` replaced by sentinels; assert byte-identical output. (Redacted-view production change: optional follow-up, own sign-off; not required for gate.) | CR-3 verification |
| W3.2 | B-7 | Enforce tier validation on direct `AnswerRecord` construction; invert the bypass test into a rejection test. | T6 |
| W3.3 | B-6 | Import-guard CI test on the emission surface's transitive closure against the `PROGRAM_A_DEPENDENCY_GRAPH.md` §4 deny-list. Needs W1.1 (location). | T7 |

## Wave 4 — Build and pre-freeze verification (only after G4)

| Step | Closes | Action | Roadmap task |
|---|---|---|---|
| W4.1 | — | Implement the emission surface exactly per the frozen T1 spec, in the W1.1 location; binding via `from_mapping`. | T4, T8 |
| W4.2 | B-9 | Dry run on a synthetic **non-frozen** corpus with fabrication pressure: verify (a) no `CERTAIN` on fabricated-claim probes (CF-R2), (b) ≥2 tiers reachable (CF-R6), (c) byte-identical replay, (d) full artifact set. **Scope limit (B-11):** mechanics verification only; no constant may change in response to results except by returning to Wave 2 for redesign + re-freeze before any frozen-row exposure. | T10 |
| W4.3 | B-15 | Verify EXP-0 run-state; schedule T9 before or alongside T11. | T9 |
| W4.4 | B-16 | Obtain G3 rulings (Q5 Goodhart guard; Q6 H₀ control) — required before any PASS claim, not before execution. | G3 |

## What is explicitly NOT in this plan

- No change to ES-1's states, tier map, answer coupling, or constants.
- No canonical amendment: nothing in B-1…B-16 contradicts the canon; every
  correction lives in preregistration, decision records, tests, or code.
- No M12/M13 work beyond obtaining their rulings (B-10, B-11) so the
  fallback is adjudicated before it is ever needed.
- No self-issued approvals: every sign-off in Waves 1–2 and W4.4 must come
  from the real named specialist (MASTER_SPEC §16; R-08).

## Closure map

| Blocker | Closed by | Instrument |
|---|---|---|
| B-1 | Wave 2 + Auditor sign-off | new preregistration + approval |
| B-2 | W1.3 → T1 §4 | decision record |
| B-3 | W1.4 → adjudicated with T1 | **preregistration amendment** |
| B-4 | T1 §5 + W3.1 | spec clause + test |
| B-5 | W1.1 | Architect ruling |
| B-6 | W3.3 | implementation change |
| B-7 | W3.2 | implementation change |
| B-8 | T1 §7 (interim) + Q8 ruling at G4 | documentation update |
| B-9 | W4.2 | implementation change (verification) |
| B-10 | T1 §6 ruling | Auditor approval only |
| B-11 | T1 §6 ruling | Auditor approval only |
| B-12 | W1.2 + T1 + G4 signatures | governance sign-offs |
| B-13 | T1 §3 | preregistration content |
| B-14 | T1 §5 | Auditor approval only |
| B-15 | W4.3 | scheduling |
| B-16 | W4.4 | Auditor approval only |

# PROGRAM A — CONFIDENCE DECISION TREES

**Authority:** Chief Scientific Architect review, 2026-07-07. Derives from
`PROGRAM_A_CONFIDENCE_MECHANISM.md`; all citations verified there. Three
trees: (1) the lawfulness adjudication tree for **any** proposed mechanism —
reusable by the ScientificAuditor for T1; (2) the per-query emission tree of
the recommended mechanism ES-1; (3) the governance tree from here to frozen
code. Tags: `[FACT]`, `[INFERENCE]`, `[RISK]`, `[OPEN QUESTION]`.

---

## Tree 1 — Mechanism lawfulness adjudication (apply to any candidate)

Each gate cites its killing rule. A candidate must survive every gate.

```
Candidate mechanism
│
├─ G-A  Does its tier mean "estimated P(answer_i is rubric-correct)"?
│       (prereg §1 pinned semantics)
│       ├─ NO, it predicts query family ──────────► REJECT: label-space
│       │                                            substitution (prereg §3, §5)
│       ├─ NO, it scores retrieval relevance or
│       │      source existence ──────────────────► REJECT: category error
│       │                                            (prereg §5; R-01)
│       └─ YES ▼
│
├─ G-B  Does it read anything besides query.query / query.query_id?
│       (QueryRecord carries gold_rubric + query_family — dataset.py:33-41)
│       ├─ YES ───────────────────────────────────► REJECT: rubric/family
│       │                                            peeking (L11; dataset spec §12.3)
│       └─ NO ▼
│
├─ G-C  Is any part of it a remap of an existing non-canonical taxonomy
│       (e.g., the synthesizer's 5 grades)?
│       ├─ YES ───────────────────────────────────► REJECT: post-hoc tier
│       │                                            remapping (prereg §4 kill #5)
│       └─ NO ▼
│
├─ G-D  Is any threshold, band, or parameter fitted to EXP-1 outcomes,
│       frozen rows, or chosen after outputs are observed?
│       ├─ YES ───────────────────────────────────► REJECT: post-hoc
│       │                                            calibration / protocol
│       │                                            violation (prereg §6, §4 #5)
│       ├─ Fitted on PRE-FREEZE, DISJOINT dev data ► [OPEN QUESTION M13]:
│       │                                            ScientificAuditor ruling
│       │                                            required before use
│       └─ NO ▼
│
├─ G-E  Does its dependency closure touch a [REJECTED] mechanism
│       (ReasoningTrace, thermodynamic state, kg, soul graph, self-model,
│       free-energy)? (canon :90)
│       ├─ YES ───────────────────────────────────► REJECT: canonical
│       │                                            violation (R-04 / TD-08)
│       └─ NO ▼
│
├─ G-F  Is it deterministic per (query, seed), stateless across queries,
│       side-effect-free, replay-compatible? (BINDING_SPEC §4)
│       ├─ NO (e.g., hosted-LLM elicitation) ─────► REJECT (L6)
│       └─ YES ▼
│
├─ G-G  Does it implement, mirror, or fit the evaluation constants
│       (0.125/0.375/0.625/0.875; bins)? (MASTER_SPEC §7 item 3)
│       ├─ YES, contains fitted numeric mapping ──► REJECT (L8)
│       ├─ Discretizes an a-priori probability at
│       │  the locked boundaries ─────────────────► [OPEN QUESTION §7.3]:
│       │                                            L8-scope ruling required
│       └─ NO numeric constants at all ▼
│
├─ G-H  Are all its free constants named, a-priori justified, and frozen
│       in the T1 preregistration? (I2-analogue, MASTER_SPEC §17)
│       ├─ NO ─────────────────────────────────────► REJECT: uncited-constant
│       │                                            pattern (canon §8)
│       └─ YES ▼
│
└─ G-I  Can it plausibly emit ≥2 tiers across the three query families
        without tuning on frozen rows? (prereg §4 #3; decision.py:19)
        ├─ NO ─────────────────────────────────────► REJECT: designed-in
        │                                            degenerate-tier kill
        └─ YES ────────────────────────────────────► LAWFUL CANDIDATE
                                                     → submit to T1
                                                     preregistration (Q1)
```

**[FACT]** Applying Tree 1 to the enumeration in
`PROGRAM_A_CONFIDENCE_MECHANISM.md` §4: M1 dies at G-A, M2 at G-C, M3/M4 at
G-D, M5 at G-A, M6 at G-I, M7 at G-B, M8 at G-F, M9 at G-A, M12 pauses at
G-G/G-H, M13 pauses at G-D. **Only M10/M11 (the ES rule) reaches LAWFUL
CANDIDATE.**

---

## Tree 2 — ES-1 per-query emission (the recommended frozen rule)

**[INFERENCE]** This is the recommended content for the T1 preregistration;
it is not yet authorized (Q1). Inputs: `query.query` only; retrieval in the
Q2-resolved mode; deterministic claim-support test; source-independence
relation — all frozen constants per the register in
`PROGRAM_A_CONFIDENCE_MECHANISM.md` §7.4.

```
query.query
│
▼
Retrieve evidence (Q2 mode: frozen snapshot recommended)
│
▼
Extract candidate claims deterministically from retrieved content
│
├─ No candidate claim is supported by any retrieved content
│  (support test fails everywhere — includes empty, junk, and
│   topically-related-but-non-supporting results from the
│   never-fail retriever)
│        │
│        ▼
│   STATE S0 — answer := explicit unsupported / unknown /
│   false-premise response; asserts NO fact
│   tier := UNKNOWN
│
├─ Independent sources support materially incompatible claims
│  (contradiction set non-empty and material)
│        │
│        ▼
│   STATE S1 — answer := qualified answer representing the
│   alternatives; asserts NO single resolution
│   tier := DEBATED
│
├─ Exactly one independent origin supports the selected claim,
│  no material contradiction
│        │
│        ▼
│   STATE S2 — answer := single answer, hedged, source-attributed
│   tier := PROBABLE
│
└─ ≥2 independent origins support the selected claim,
   no material contradiction
         │
         ▼
    STATE S3 — answer := single answer, asserted, source-attributed
    tier := CERTAIN
```

**Invariants the tree enforces by construction:**

- **[INFERENCE]** *Answer–tier consistency* (CR-9): the answer form and the
  tier come from the same state, so a factual assertion can only co-occur
  with `PROBABLE`/`CERTAIN`, and `CERTAIN` requires multi-source independent
  support for the emitted claim. The zero-tolerance FM-1 event ("fabricated
  factual answer with tier CERTAIN", prereg §4; decision.py:20) then requires
  the claim-support test to false-positive on a fabricated claim — the
  dominant residual risk (CF-R2), not a design permission.
- **[INFERENCE]** *State exhaustiveness and mutual exclusion*: S0–S3
  partition the corroboration structure; exactly one state fires per query;
  precedence is S0 → S1 → (S2|S3) and must be frozen in this order in T1.
- **[INFERENCE]** *Tier coverage*: the three query families are designed to
  induce different evidence structures (dataset spec §9), so ≥2 tiers are
  expected across 210 rows without any tuning. **[RISK]** Not guaranteed —
  see CF-R6.

---

## Tree 3 — Governance path from this analysis to frozen code

```
This analysis (Chief Scientific Architect, 2026-07-07)
│
▼
G2  ScientificAuditor ratifies tier-source lawfulness           [OPEN — R-08]
│   (no existing surface lawfully emits canonical tiers;
│    BINDING_SPEC open item 2)
▼
T0  Architect + ScientificAuditor resolve Q2 (snapshot vs live)  [OPEN]
│   and Q3 (seed variance). NOTE: ES-1 + snapshot ⇒ all 22
│   replicates identical ⇒ prereg §7 amendment MUST be invoked
│   before execution (this is forced, not optional)
▼
T1  Mechanism preregistration authored from ES-1;                [OPEN — Q1]
│   free-constant register included; ScientificAuditor sign-off
▼
G4  Release Manager freezes the mechanism spec                   [OPEN]
│   (before any frozen-row output is observed — prereg §4 #5)
▼
T4/T8  Build surface + ~20-line binding per BINDING_SPEC §4-§5   [BLOCKED on above]
│      (Q4 location: Architect; L11 enforced; CR register applies)
▼
G6 → T11  Pre-run lock verification → 22-seed execution
          (pass OR kill, both reportable — canon §8)
```

**[FACT]** No step above may be skipped: the FAIL verdict of
`PROGRAM_A_BINDING_SPEC.md` §11 stands until T1/G4 discharge it, and the
specialist-unavailability condition (R-08) blocks G2/T0/T1 sign-offs until
real specialists rule.

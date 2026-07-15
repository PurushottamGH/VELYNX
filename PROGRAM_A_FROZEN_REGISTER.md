# PROGRAM A — CANONICAL FROZEN REGISTER (ES-1, derived)

**Produced by:** application of `PROGRAM_A_REGISTER_DERIVATION_METHOD.md` to the
frozen authorities, on 2026-07-14.
**Method authority:** `PROGRAM_A_REGISTER_DERIVATION_METHOD.md` (the derivation
methodology rider) over the T1 freeze object
`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §5, its co-frozen addendum
`PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` §A6-DIGEST, the admissibility audit
`PROGRAM_A_REGISTER_AUDIT.md`, and the freeze-step plan
`PROGRAM_A_G4_EXECUTION_PLAN.md`.
**Status:** DERIVED — canonical for the seven determinable entries; **halted with
cause** for the four deferred entries. No value is invented. No governance is
performed. The standing prohibition and the pre-G4 posture are unchanged.

---

## 0. File-open verification (precondition of this document)

All five authorities were opened and read in full before any derivation:

| File | Opened | Size |
|---|---|---|
| `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` | yes | 40,368 B (638 lines) |
| `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` | yes | 39,201 B (635 lines) |
| `PROGRAM_A_REGISTER_DERIVATION_METHOD.md` | yes | 35,376 B (607 lines) |
| `PROGRAM_A_REGISTER_AUDIT.md` | yes | 21,130 B (466 lines) |
| `PROGRAM_A_G4_EXECUTION_PLAN.md` | yes | 18,723 B (371 lines) |

Grounding types are consumed as frozen from `program_a/types.py` (via addendum
§A). No filesystem search outside this repository was performed; `/tmp` and
memory were not consulted.

---

## 1. What "derive the canonical frozen register" means under the method

`PROGRAM_A_REGISTER_DERIVATION_METHOD.md` §2.5 fixes the definition of
**canonical** with four jointly-necessary conditions:

1. per-register + universal **constraints** hold (§2.3, §3–§6 part 2);
2. the **invariants** are preserved (§2.4, §3–§6 part 3);
3. the **ScientificAuditor** has certified (1)–(2) by the §7 method and recorded
   a genuine **B2** sign-off; and
4. the **ReleaseManager** has transcribed and pinned the value into the digest
   by the §8 method (E4–E7 of `PROGRAM_A_G4_EXECUTION_PLAN.md`).

> "Absent any one, the value is a *candidate*, not canonical, and the placeholder
> stands." (DERIVATION_METHOD §2.5)

The register therefore has exactly two lawful classes of entry today:

- **Determinable-and-transcribed** — a canonical value already exists on disk and
  is audited **PASS** (`PROGRAM_A_REGISTER_AUDIT.md` §Summary). The derivation
  method's job for these is to confirm the value is the unique one its a-priori
  argument licenses. There are **seven** such entries (plus the two co-frozen
  structural constants).
- **Deferred** — role fixed, concrete value **not determined by the method**, and
  audited **FAIL (deferred)**. There are **four** such entries. For these the
  method is explicit that it "**contains no value**" (DERIVATION_METHOD §0.2,
  §10, closing line) and produces neither the B2 certification nor the freeze.

This document produces the first class in full and halts on the second with the
exact rule that makes each non-derivable, as MISSION requires ("If any value
cannot be uniquely derived, stop and explain exactly which rule of the derivation
methodology is insufficient").

---

## 2. Canonical register — the seven determinable entries (+2 structural)

Each value below is the value transcribed in `program_a/constants.py` and
certified **PASS** in `PROGRAM_A_REGISTER_AUDIT.md`. Each is uniquely determined
because its a-priori argument (E-STRUCT / E-DETERM / E-TYPE / E-PRIOR,
DERIVATION_METHOD §2.2) licenses **that value and no other**.

| # | Register entry | Canonical frozen value | Uniqueness ground (admissible evidence class) |
|---|---|---|---|
| 5.1 | `MIN_INDEPENDENT_ORIGINS_FOR_S3` | `2` | **E-STRUCT.** "2 is the smallest count that is corroboration *at all* — one origin is not corroboration, two is" (T1 §5.1). The structural-minimum argument licenses `2` and, per AUDIT Entry 5.1, "no other value." |
| 5.2 | `INDEPENDENCE_RELATION` | Two evidence items are independent **iff** they have distinct `origin_domain` provenance, with mirror/syndication domains counted once. | **E-STRUCT.** Corroboration counts independent origins, not mirror copies; the anti-inflation guard on S3 (T1 §5.2; AUDIT 5.2 PASS). |
| 5.5 | `EVIDENCE_ORDERING_KEY` | Lexicographic on `(origin_domain, doc_id)`. | **E-DETERM + E-STRUCT.** A frozen total order is forced by the L6 byte-identical-replay requirement; removes wall-clock/score-order as a determinism leak (T1 §5.5; addendum §A grounding types; AUDIT 5.5 PASS). |
| 5.8 | `SPEC_VERSION` | `"es1-t1-2026-07-09"` (draft identity; ratified to its final value **at** the G4 pin — DERIVATION_METHOD §8 step 5). | **E-PRIOR (identity convention).** Pure identity anchor; the value is fixed by the naming convention, not chosen from a range (T1 §5.8; AUDIT 5.8 PASS). |
| 5.9 | `PA3_RULESET_VERSION` | `"pa3-ruleset-2026-07-13"` | **E-PRIOR (identity convention).** Identity tag in the `SPEC_VERSION` class; the merged addendum advances it **once** from `…-07-09` to `…-07-13` because Findings 2+3 edit digest-covered rules (iv)/(v) a single time (addendum §A6-DIGEST, §E row 9, §F.4). AUDIT 5.9 PASS. |
| §3.2a | `STATE_TIER_MAP` | `{"S0":"UNKNOWN","S1":"DEBATED","S2":"PROBABLE","S3":"CERTAIN"}` | **E-STRUCT.** Fixed ordinal bijection state→tier; labels a corroboration state, assigns no probability (T1 §3.2; AUDIT §3.2a PASS). |
| §3.2b | `CONFIDENCE_TIERS` | `("UNKNOWN","DEBATED","PROBABLE","CERTAIN")` | **E-STRUCT.** The structural label set; label-equality with `experiments.EXP1.dataset.CONFIDENCE_TIERS` is lawful conformance — labels shared, probabilities not (T1 §3.2; AUDIT §3.2b PASS). |

**Firewall re-check (C-FIREWALL, DERIVATION_METHOD §2.3 / §7 criteria 2–4).** None
of the seven values equals or is fitted to any EXP-1 probability
(`{0.125, 0.375, 0.625, 0.875}`), bin boundary, or ECE threshold; those live
only in `experiments/EXP1/calibration.py` and appear nowhere in `program_a/`
(AUDIT §3.2b; `test_constants_contain_no_exp1_probability_or_bin_value` green).

These seven (with the two structural constants) are the **7 of 11 admissible now**
of `PROGRAM_A_REGISTER_AUDIT.md` §Summary. They are canonical under §2.5 to the
extent the method can certify pre-freeze; their final pin still occurs at the
single G4 digest event (§8 below), but their **values are uniquely determined**
and are stated above.

---

## 3. The four deferred entries — HALT, with the exact insufficient rule

MISSION: *"If any value cannot be uniquely derived, stop and explain exactly which
rule of the derivation methodology is insufficient."* The following four values
**cannot be uniquely derived by this methodology**, and the methodology says so
itself. The derivation method is not *silent* on them — it is **constitutively
value-free** on them by four converging rules:

### 3.1 The governing rule that blocks all four (DERIVATION_METHOD §0.2 + §1 + §10)

- **§0.2 "Non-goals — Choose any value."** "No value for any of the four registers
  appears here. Where a value would otherwise be named, this document names the
  *procedure* that would produce it and stops." This is the primary insufficiency:
  the method is a **procedure specification**, not a value oracle. It supplies the
  road (§2–§9), never the destination value.
- **§1 (why deferred).** The four "share a different property: their role is fixed
  but their *concrete internal parameterization* admits **more than one
  structurally-defensible instantiation**, so the authorities correctly refused to
  invent one." A methodology cannot collapse a genuinely >1-element admissible set
  to a point; that is what makes the value non-unique **by construction**.
- **§10 + closing line.** "It **contains no value** for any of the four registers …
  It contains none of those values." An admissible unique derivation would require
  a value the document is defined not to hold.

### 3.2 The specific rule that is *insufficient* for each register

For every one of the four, the operative insufficiency is the same and is located
precisely: **DERIVATION_METHOD §2.2 (admissible evidence classes) + §2.5
(canonical requires B2 + freeze), read against §1.** The evidence classes
E-STRUCT/E-DETERM/E-TYPE/E-PRIOR **constrain** the value (they fix its shape,
determinism, type, and firewall-cleanliness) but, per §1, do **not narrow the
admissible set to a single instantiation**; and E-DEV is explicitly
**falsifying-only, never selecting** (§2.2 E-DEV; §7 "Falsification-first reading
of E-DEV"). With no selecting evidence class available and >1 defensible
candidate remaining, uniqueness fails at §2.2. Certification (§2.5 cond. 3) and
freeze (§2.5 cond. 4) are then unreachable because there is no single value to
certify.

| Entry | Deferred value | Method section defining its *procedure* | The rule that is insufficient to yield a unique value |
|---|---|---|---|
| 5.3 | `SUPPORT_TEST_PARAMS` | §3 | §3.1 gives only evidence classes (E-STRUCT+E-PRIOR primary; E-DEV falsifying-only). §2.2 supplies no value-**selecting** class; §1 states the parameterization "admits more than one structurally-defensible instantiation." Unique value ⇒ **not derivable**. AUDIT 5.3: criteria 5 **FAIL**, 6 **FAIL (value-level)**, 8 **FAIL (deferred)** — BLOCKER. |
| 5.4 | `CONTRADICTION_MATERIALITY_PARAMS` | §4 | §4.1 fixes the material/immaterial *boundary form* (E-STRUCT+E-PRIOR) and the §A5 precondition, but the concrete materiality threshold is exactly the "runtime-judgment freedom the placeholder left open" (§4.4) — §2.2 offers nothing to pick one threshold a-priori. **Not derivable.** AUDIT 5.4: 5/6/8 **FAIL** — BLOCKER. |
| 5.6 | `EXTRACTION_PARAMS` | §5 | §5.1 fixes determinism + entity-level + ordered-tuple output (E-PRIOR+E-DETERM+E-TYPE) and the §A2 injectivity precondition (F2/F2′ CONDITIONAL, §5.3), but no §2.2 class selects the specific extraction parameters; the interim `claim_extraction.py` defaults are **not** the frozen value (AUDIT 5.6). **Not derivable.** AUDIT 5.6: 5/6/8 **FAIL** — HIGH. |
| 5.7 | `ANSWER_TEMPLATES` | §6 | §6.1–§6.2 fix, per state, the answer *form* (S0/S1 assert no fact; S2 hedged + attributed; S3 asserted + attributed) renderable from `EvidenceStateResult` fields only, but the **exact template text** is not entailed by any §2.2 class — many strings satisfy the form. **Not derivable.** AUDIT 5.7: criterion 6 **FAIL (value-level: exact template text not yet fixed)**, 8 **FAIL (deferred)** — MEDIUM (plus the mandatory G4 screen for embedded probability/quantifier language). |

### 3.3 Why halting here is *correct*, not a shortfall

- **The placeholders are load-bearing (DERIVATION_METHOD §1 "Placeholder posture
  is load-bearing").** The `{}` entries + `frozen_constants_digest()`-raises-on-
  pending make an admissible freeze mechanically impossible while any of the four
  is underived. Inventing a value here would defeat that feature and produce an
  **inadmissible** result "regardless of the value produced" (§0.3 firewall logic
  applied to fabrication).
- **The method routes value-authorship to a different actor at a different step.**
  Per §7, §8, and `PROGRAM_A_G4_EXECUTION_PLAN.md` E4, the concrete value text is
  **authored by the ScientificAuditor** with a written a-priori argument, certified
  by a genuine **B2** (E3), then **transcribed** by the ReleaseManager (E4→E7).
  DERIVATION_METHOD §0.2 "Perform governance" and §10 bar this document — and this
  derivation — from doing either. Producing the four values would be fabricating
  E4 authorship and B2 sign-off, which §7 "Provenance separation (no proxy)" and
  T1 §12 explicitly forbid.
- **MISSION constraint honored.** No required file is missing; all five opened.
  The halt is *not* "missing files" — it is the methodology's own §0.2/§1/§10
  value-void, which is the sanctioned outcome for a value that "cannot be uniquely
  derived."

---

## 4. Digest / freeze status implied by the derivation

Per DERIVATION_METHOD §8 step 3 and `PROGRAM_A_G4_EXECUTION_PLAN.md` E6/E11:

- `frozen_constants_digest()` is the SHA-256 over the ordered serialization of the
  eight §5 register entries **+** `PA3_RULESET_VERSION` **+** `STATE_TIER_MAP`
  **+** `CONFIDENCE_TIERS` (T1 §6.1; addendum §A6-DIGEST). It is computable **only
  when none of the four remains pending** (§8 step 3; the function raises
  `FrozenConstantsIncomplete` otherwise — AUDIT Entry 5.3).
- Because entries 5.3, 5.4, 5.6, 5.7 remain deferred (§3 above), the "all-four
  precondition" (§8 step 3) is **not met**. Therefore:
  - `CONSTANTS_HASH` = **`None`** (no admissible digest exists);
  - no single G4 digest may be generated (E6 blocked);
  - the register-set freeze is **not dischargeable** (AUDIT §Aggregate;
    G4_EXECUTION_PLAN §6 blocking condition "any one of the four register entries
    still empty").

This document therefore pins **no** `CONSTANTS_HASH`, mints **no**
`mechanism_id()`, and completes **no** B2/B3 block — consistent with
DERIVATION_METHOD §0.2 and §2.5, and with the blank sign-off blocks in T1 §12 and
addendum §D.

---

## 5. Canonical result (summary)

**Determined and canonical (7 + 2 structural):**

```
MIN_INDEPENDENT_ORIGINS_FOR_S3 = 2
INDEPENDENCE_RELATION          = distinct origin_domain; mirror/syndication counted once
EVIDENCE_ORDERING_KEY          = lexicographic on (origin_domain, doc_id)
SPEC_VERSION                   = "es1-t1-2026-07-09"   (ratified at G4 pin)
PA3_RULESET_VERSION            = "pa3-ruleset-2026-07-13"
STATE_TIER_MAP                 = {"S0":"UNKNOWN","S1":"DEBATED","S2":"PROBABLE","S3":"CERTAIN"}
CONFIDENCE_TIERS               = ("UNKNOWN","DEBATED","PROBABLE","CERTAIN")
```

**Deferred — cannot be uniquely derived by the methodology (4):**

```
SUPPORT_TEST_PARAMS            = <not derivable>   # §3; blocked by DERIVATION_METHOD §0.2 + §1 + §2.2
CONTRADICTION_MATERIALITY_PARAMS = <not derivable> # §4; blocked by DERIVATION_METHOD §0.2 + §1 + §2.2
EXTRACTION_PARAMS              = <not derivable>   # §5; blocked by DERIVATION_METHOD §0.2 + §1 + §2.2
ANSWER_TEMPLATES               = <not derivable>   # §6; blocked by DERIVATION_METHOD §0.2 + §1 + §2.2 (form fixed, text not entailed)
```

**Digest:** `CONSTANTS_HASH = None` (all-four precondition of §8 step 3 unmet).

**The single insufficient rule, stated once:** the derivation methodology's
**§2.2 admissible-evidence set provides no value-*selecting* class** (E-DEV is
falsifying-only), so where **§1** records that a register "admits more than one
structurally-defensible instantiation," the value is **not uniquely determined**;
and **§0.2/§10** bind this document to name the procedure and stop rather than
choose. For the seven other entries a single instantiation *is* entailed (E-STRUCT
/E-DETERM/E-PRIOR licenses one value only), so those are produced above.

---

*End of derived frozen register. Seven entries produced as canonical; four halted
with the exact methodology rule (§0.2 + §1 + §2.2, with §10) that makes them
non-derivable. No value invented; no governance performed; no digest pinned.*

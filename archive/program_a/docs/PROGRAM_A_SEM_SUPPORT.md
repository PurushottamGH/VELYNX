# PROGRAM A — SEM-SUPPORT: THE EXTENSIONAL SEMANTICS OF `supports`

**Title:** `SEM-SUPPORT` — the canonical L1 semantic definition of the
claim-support predicate `supports(claim, evidence)`: universe, defining rule,
parameter surface, axis closure, and proof pack, authored under
`PROGRAM_A_SEMANTIC_AUTHORING_METHODOLOGY.md` (SAM-1).
**Object identity:** `SEM-SUPPORT`, revision `sem-support-2026-07-16-r2`
(supersedes `sem-support-2026-07-15-r1`) — class `SemanticPredicate`, origin L1,
owner Architect, lifecycle **drafted**. This is the S1-stage candidate
deliverable `(U, D, P, X)` of SAM-1 §5 with its S2-stage proof pack `Π`
carried inline (§§11–21).
**Authority basis:** `PROGRAM_A_ARCHITECTURAL_ONTOLOGY.md` (ONT-1, consumed as
fixed); `PROGRAM_A_ONTOLOGY_MIGRATION_PLAN.md` (slot `SEM-SUPPORT`, M5/M12/M17,
E4a schedule); `PROGRAM_A_SEMANTIC_AUTHORING_METHODOLOGY.md` (SAM-1 §3, §5);
`PROGRAM_A_SEM_S0_PREREGISTRATION.md` (`S0-REG-1`, consumed by identity);
`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §3.1/§5.3/§7/§8 and
`PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` §A0–§A7 (fixed semantic context,
preserved, never altered); `PROGRAM_A_REGISTER_DERIVATION_METHOD.md` §2.2/§3
(evidence classes; the E4b procedure this definition makes dischargeable).
The falsification history — `PROGRAM_A_REGISTER_DERIVATION_ROOT_CAUSE_ANALYSIS.md`,
`docs/audits/REGISTER_DERIVATION_FINDING1_SONNET_AUDIT.md`,
`docs/audits/REGISTER_DERIVATION_FINDING2_SONNET_AUDIT.md` — is consumed as
**L0 provenance only**: it motivates obligations; it transfers no semantic
authority (SAM-1 §5.2).
**Date:** 2026-07-16
**Revision note (r1 → r2):** Revision 1 (`sem-support-2026-07-15-r1`) carried a
declaration/definition inconsistency on the **read set / field influence** of
`D`. §4.1 labelled the frozen `EvidenceItem` surface as the "3-field **content**
schema `{origin_domain, title, text}`," which classifies `origin_domain` as
content. The defining rule `D` (§6.2–§6.3) does not read `origin_domain` at
all. The complete dependency graph of `D` is:

```
supports(c, e)
  ←  E(c) ≠ ∅  ∧  E(c) ⊆ V(e)
  ←  E(c) := T(c.claim_text)
  ←  V(e) := T(e.title) ∪ T(e.text)
  ←  T(s) := { strip(w) : w ∈ rawtoks(nfc(s)), strip(w) qualifies }
  ←  nfc, rawtoks, strip, qualifies  (each under UVER = Unicode 16.0.0)
  ←  input fields read: c.claim_text, e.title, e.text
  ←  input fields not read: c.supporting_doc_ids, e.doc_id,
                            e.origin_domain, e.snapshot_hash_ref
```

§4.4, §6.4 C5, and §9.2 already stated the correct influence facts
(`origin_domain` is provenance; it lends no support). Revision 2 repairs only
the misaligned declaration text so every read-set / field-influence sentence
is consistent with `D`. Concretely: §4.1 now says "3-field **document**
schema" (T1 §7.1's term) and immediately partitions those three document
fields into content-for-`supports` `{title, text}` vs provenance
`{origin_domain}`; identity fields `{doc_id, snapshot_hash_ref}` are named.
A secondary gloss repair at THM-8 replaces the overclaiming string-append
phrase with the entity-set statement the theorem actually proves. **No clause
of `U`, `D` (§6.1–§6.3), `P`, or `X` changes. No export identity changes.**

**Extension-preservation theorem.** For every `(c, e) ∈ U`,
`supports_r1(c, e) = supports_r2(c, e)`. *Proof:* the operative biconditional
§6.3 and the functions §6.1–§6.2 are byte-identical across revisions; only
declaration/gloss sentences outside those operative clauses were edited;
therefore the extension is identical by construction. ∎

**Revision log (every modified sentence):**
1. Header Object identity: `sem-support-2026-07-15-r1` → `sem-support-2026-07-16-r2` (supersedes r1).
2. Header Date: `2026-07-15` → `2026-07-16`.
3. Header: inserted this Revision note, dependency graph, extension-preservation theorem, and revision log (new).
4. §3 Identity: revision string r1 → r2 with supersession note.
5. §4.1: "3-field content schema `{origin_domain, title, text}` plus identity fields" → "3-field document schema `{origin_domain, title, text}` (T1 §7.1) plus identity fields `{doc_id, snapshot_hash_ref}`," with partition: of the three document fields, `D` consumes only `{title, text}` as content; `origin_domain` is provenance and is not read (§4.4).
6. §20 THM-8 trailing gloss: repaired overclaiming string-append phrase to entity-set inclusion wording; noted NFC non-monotonicity under append is not claimed.
7. §25.3: revision id r1 → r2.

**Status:** DRAFT — S1/S2 candidate. This document **authors the semantics of
`supports` and nothing else.** It defines no part of MATERIALITY, EXTRACTION,
or TEMPLATE except by declared export/import boundary (§24). It chooses no L2
value (the E4b Parameter is minted later by the ScientificAuditor), redesigns
no part of T1/PA-3/SAM-1, modifies no ontology or migration content, writes no
code, performs no governance, and touches neither EXP-1 nor G4. The standing
prohibition (`ES1_IMPLEMENTATION_GATE.md`:97-99) is unchanged. Acceptance of
this candidate is **not** self-declared: it requires the independent stages
S3–S5 of SAM-1 §4 (§22–§23 below). Its admissibility at S3 additionally
requires that the S0→S1 gate record (`S0-REG-1` §9, GC-1…GC-6, including hash
slots H-1…H-4) holds with timestamps preceding this draft's submission
(SAM-R2); if that record postdates this text, this text re-enters S1 unchanged
in content but re-sequenced in record.

---

## 1. Purpose

The Root Cause Analysis established (verdict `C`) that the four deferred ES-1
registers failed audit after audit because their **defining semantics** were
classified as deferred values, leaving the meaning of `supports` authored by
nobody. The migration plan created the typed slot `SEM-SUPPORT`
(SemanticPredicate, L1, Architect-owned, ScientificAuditor-approved, scheduled
E4a) and SAM-1 fixed the scientific procedure for filling it.

This document **fills the slot**. It supplies the complete extensional
definition of `supports(claim, evidence)`: the total universe it is quantified
over, the biconditional that entails exactly one boolean for every element of
that universe, the finite declared parameter surface left to the L2 value
`SUPPORT_TEST_PARAMS`, the closure of every historical ambiguity axis, and the
written discharge of every SAM-1 §5.4 proof obligation. After this definition
is approved and frozen (E4a), `Parameter[SEM-SUPPORT]` becomes inhabitable and
the derivation method's §3 procedure for `SUPPORT_TEST_PARAMS` becomes
executable to a unique value (E4b) — closing, for this register, the
value-selection gap the method records at its §2.2.

## 2. Authority

| Source | Role here |
|---|---|
| ONT-1 (`PROGRAM_A_ARCHITECTURAL_ONTOLOGY.md`) | Fixed. Supplies class, origin, owner, lifecycle, operations, reference rules (§3–§7). |
| Migration plan (`PROGRAM_A_ONTOLOGY_MIGRATION_PLAN.md`) | Fixed. Declares the `SEM-SUPPORT` slot, the M5 typing of `SUPPORT_TEST_PARAMS` as `Parameter[SEM-SUPPORT]`, the M12 precondition on derivation, the M17 E4a/E4b split. |
| SAM-1 (`PROGRAM_A_SEMANTIC_AUTHORING_METHODOLOGY.md`) | Fixed. Governs this document's form (five parts), question set (SQ-SUP-1…10), proof obligations (PO-SUP-1…10), evidence rules (§5.2/§5.3), acceptance/rejection (§5.9/§5.10). |
| `S0-REG-1` (`PROGRAM_A_SEM_S0_PREREGISTRATION.md`) | Consumed by identity. The sealed core battery `S0-PB-1` and joint witnesses `S0-JW-1` were **not read** by this author (SAM-R3 channel discipline); the witnesses exhibited in this document (§7, §19, Π) are author-constructed proof-pack witnesses, disjoint in role and provenance from the sealed battery. |
| T1 (`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md`) §3.1, §5.2, §5.3, §7, §8; addendum §A0–§A7 | Fixed semantic context. Every state definition, precedence rule, seam invariant, and contract is preserved verbatim; this definition is constructed to slot into them without entailing any edit (§18, PO-SUP-6/7/8). |
| Derivation method (`PROGRAM_A_REGISTER_DERIVATION_METHOD.md`) §2.2, §3 | Fixed. Its evidence classes (E-STRUCT/E-DETERM/E-TYPE/E-PRIOR; E-DEV falsifying-only) are the only argument forms used in `Π`. |
| Frozen leaf-type contract (addendum §A grounding-types block; realized on disk as `program_a/types.py`) | Fixed. `D` is stated over the **type contract** (an L1 object), never over code (G-8); the module file is its L3 realization and is cited as locator only. |
| RCA; Sonnet audits 1–2 (v1-a…v1-c, CE-4…CE-13); `PROGRAM_A_REGISTER_AUDIT.md`; `PROGRAM_A_FROZEN_REGISTER.md` | **L0 provenance only.** They motivate obligations and probe classes; no clause of `D` is derived *from* them and none of their content acquires semantic authority here. |
| EXP-1 objects (tier→probability mapping, bin boundaries, ECE logic, outcomes, frozen rows, rubrics, families, adjudicator signals) | **Forbidden. Not consulted at any point** (SAM-1 §0.3; G-7; PO-SUP-9). |

## 3. Object classification

| Field | Value |
|---|---|
| Identity | `SEM-SUPPORT`, revision `sem-support-2026-07-16-r2` (supersedes `sem-support-2026-07-15-r1` — declaration/read-set repair only; extension-preserving) |
| Class | `SemanticPredicate` (ONT-1 §3: "Extensional criterion/relation: e.g. support …") |
| Origin | L1 (Semantic Specification) |
| Owner / Creator | Architect |
| Approver | ScientificAuditor (scientific/freeze-relevant semantic class, ONT-1 §4) |
| Lifecycle | **drafted** → approved (S5 adjudication under SAM-1 §10) → frozen (S6, at E4a per migration M17) |
| Freeze point | E4a of `PROGRAM_A_G4_EXECUTION_PLAN.md` as split by M17; freeze recorded per ONT-1 §5. This document performs no freeze. |
| Instantiating L2 parameter | `SUPPORT_TEST_PARAMS` (T1 §5.3) — typed `Parameter[SEM-SUPPORT]` (migration M5); **uninhabited** until this definition is frozen (ONT-1 §6), minted at E4b by the ScientificAuditor. |
| References | L0/L1 only, acyclic (§24; J-6). No reference to any L2/L3/L4/L5 object as authority. |
| Post-approval change control | Any change is a new revision, never mutation (ONT-1 §5); a post-freeze counterexample is an MF-class event under SAM-1 §11.2. |

## 4. Universe `U`

### 4.1 Declaration

> **U = { (c, e) : c is a well-typed `CandidateClaim`, e is a well-typed
> `EvidenceItem` }.**

where, per the frozen type contract (addendum §A grounding types):

- `CandidateClaim = { claim_text : Str, supporting_doc_ids : Tuple[Str] }`,
  with `claim_text` any Unicode string (including the empty string) and
  `supporting_doc_ids` any tuple of strings;
- `EvidenceItem = { doc_id : Str (non-empty), origin_domain : Str (non-empty),
  title : Str, text : Str, snapshot_hash_ref : Str }`, i.e. exactly the
  3-field **document** schema `{origin_domain, title, text}` (T1 §7.1) plus
  identity fields `{doc_id, snapshot_hash_ref}`. Of the three document fields,
  `D` consumes only `{title, text}` as content; `origin_domain` is provenance
  and is not read by `D` (§4.4; §6.4 C5; MIN-6).

Here `Str` means: any finite sequence of Unicode code points (assigned or
unassigned), of any length, including the empty sequence. No well-typed pair
is excluded: **`supports` is total over `U`** (PO-SUP-1; THM-2).

### 4.2 Scope resolution (the second argument is an evidence *item*)

The second argument is a single `EvidenceItem`, **never** an evidence set.
This is forced (E-STRUCT), not chosen: the frozen consumers of `supports`
apply it per item —

- addendum §A1: `ios(c) = independent_origins({ e ∈ evidence : supports(c, e) })`;
- addendum §A4: `supp(c) = { e : supports(c, e) }`;
- addendum §A2 (secondary key): `min{ (origin_domain, doc_id) : e ∈ evidence, supports(c, e) }`.

Each formula quantifies `supports` over individual items of the evidence set.
A set-scoped predicate is not consumable by these frozen formulas; therefore
the item-scoped signature is the unique type-conformant reading. This closes
the CE-4 axis at the universe level (§16 row X-1).

### 4.3 Exclusions (everything outside scope, stated)

Not in `U`, and `supports` is undefined over them by construction:

- `EvidenceSet`, `CandidateClaims`, `EvidenceStateResult`, `Emission`,
  `QueryRecord`, or any other type;
- ill-typed values (e.g. an `EvidenceItem` with empty `doc_id` or
  `origin_domain` — the type contract rejects them before `supports` is
  reachable);
- pairs of raw strings not packaged in the frozen types (the definition is
  stated over the types so that implementation conformance is decidable
  against the same contract — G-8).

### 4.4 Fields consumed and fields ignored (declared)

`D` (§6) reads **exactly**: `c.claim_text`, `e.title`, `e.text`. It reads
**none of**: `c.supporting_doc_ids`, `e.doc_id`, `e.origin_domain`,
`e.snapshot_hash_ref`. Consequences, declared now:

- `supporting_doc_ids` (PA-2's emission-time annotation) has **no effect** on
  the predicate; the coherence of emission-time `supporting_doc_ids` with
  predicate-time `supports` is the J-5 joint obligation, owned by
  `SEM-EXTRACTION` + the S4 joint round, and is *not* silently assumed here.
- `origin_domain` is provenance, consumed downstream by the frozen
  `INDEPENDENCE_RELATION` (T1 §5.2) inside `ios`; it is **not** content and
  lends no support (§9.2; MIN-6 witness).

## 5. Formal signature

```
supports : CandidateClaim × EvidenceItem → Bool
supports(c, e) ∈ {true, false}
```

| Parameter | Type | Justification |
|---|---|---|
| `c` | `CandidateClaim` | E-TYPE: the frozen claim type is the only claim-shaped object in the type contract; the frozen consumers (§A1/§A2/§A4) pass exactly this type. Only `claim_text` is semantically consumed (§4.4); the parameter is nonetheless typed as the whole `CandidateClaim` so the signature matches the frozen call sites verbatim and no adapter layer is implied. |
| `e` | `EvidenceItem` | E-TYPE + E-STRUCT: item-scoped per §4.2 (forced by the frozen consumer formulas). Only `title` and `text` are semantically consumed (§9.2). |
| return | `Bool` | E-TYPE: §A1/§A4 consume `supports` as a set-comprehension membership test; a boolean, never a score, rank, or probability (G-7; T1 §5.3 "No probability numbers"). |

No other parameter exists. In particular there is **no** threshold, weight,
window, score, seed, or configuration argument: the predicate has **zero
numeric degrees of freedom** (load-bearing for PO-SUP-9 and for the F-3
axis-descent closure, §19.3).

## 6. Defining rule `D`

### 6.1 Fixed external standard (pinned inside `D`)

`D` references the Unicode Standard, pinned to a single version so that no
reading freedom survives (UE):

> **UVER := Unicode 16.0.0.** All references below to NFC (UAX #15
> Normalization Form C), to the `White_Space` property, and to
> `General_Category` values are references to the normative data and
> algorithms of UVER, and to no other version.

The pin is definitional content, in the same class as `EVIDENCE_ORDERING_KEY`'s
inline semantics ("lexicographic on `(origin_domain, doc_id)`"), not a
parameter: it admits no admissible alternative *within this definition*
(MIN-2 shows deletion is punished). It is the same dependency class the frozen
§A2 tertiary key already carries ("Unicode code-point order over its UTF-8/NFC
form"); §18.2 records the resulting compatibility obligation.

### 6.2 Core functions (each total, each deterministic)

For any Unicode string `s`:

1. **Normalization.** `nfc(s)` := the NFC normal form of `s` under UVER.
   (Total: NFC is defined for every code-point sequence; unassigned code
   points have no decomposition or composition under UVER and pass through
   unchanged.)
2. **Raw tokenization.** `rawtoks(s)` := the sequence of maximal substrings of
   `s` containing no code point with the `White_Space` property (UVER).
3. **Stripping.** For a raw token `w`: `strip(w)` := `w` with the longest
   prefix and the longest suffix removed in which every code point has
   `General_Category` beginning `P` (punctuation) or `S` (symbol).
   Interior punctuation/symbols are retained (e.g. `AT&T`, `Jean-Pierre`
   remain single tokens).
4. **Entity-token criterion.** A stripped token `w′` **qualifies** iff
   `w′ ≠ ε` and `w′` contains at least one code point whose
   `General_Category` begins `L` (letter) or `N` (number).
5. **Entity-token set.** `T(s)` := `{ strip(w) : w ∈ rawtoks(nfc(s)),
   strip(w) qualifies }` — a finite **set** (duplicates collapse; order is
   discarded).

Derived quantities:

- **Claim entity set:** `E(c)` := `T(c.claim_text)`.
- **Evidence content-token set:** `V(e)` := `T(e.title) ∪ T(e.text)`.

Token equality throughout is **code-point-sequence equality of the NFC
forms** — no case folding, no compatibility (NFKC) folding, no further
transformation (§9).

### 6.3 The defining biconditional

> **D:  For every `(c, e) ∈ U`:**
>
> **`supports(c, e) = true` ⟺ `E(c) ≠ ∅` ∧ `E(c) ⊆ V(e)`.**
>
> **`supports(c, e) = false` in every other case.**

In words: the evidence item supports the claim **iff** the claim has at least
one entity token and **every** entity token of the claim is literally present
(as an NFC-exact token) among the entity tokens of that item's `title` or
`text`.

### 6.4 Clause-by-clause rationale (evidence classes cited; SAM-1 §5.2 only)

| Clause | Content | Ground |
|---|---|---|
| C1 | Item scope (`e` a single item) | E-STRUCT: forced by frozen consumers §A1/§A2/§A4 (§4.2). |
| C2 | Entity notion = qualifying stripped tokens of `claim_text` (`ENT-1`, §6.2 items 2–5) | E-PRIOR ("entity-level, not topic-level" — T1 §5.3) + E-STRUCT: the entity set must be (a) decidable by pure text mechanics with no model call (T1 §5.6 posture, shared no-model constraint; T1 §8.3 vocabulary ban), and (b) **total over the claim's content** so that *any* fabricated content surfaces as an entity token — a proper-subset notion (e.g. capitalized spans only) would let fabricated lowercase or numeric content escape the CF-R2 theorem (THM-4). Among token-selection notions, the all-qualifying-tokens notion is the unique maximal one, and maximality is exactly what PO-SUP-5 requires (§14.2 argument A2). |
| C3 | Quantifier = universal (`⊆`) | E-STRUCT: the unique quantifier under which CF-R2 is a theorem. Under `∃` (any-entity) or a designated-subset quantifier (head-entity), a claim containing one genuine and one fabricated entity gains support from evidence containing only the genuine one — contradicting PO-SUP-5 outright. Under `∀` it cannot (THM-4). This closes CE-5 (§16 row X-2). |
| C4 | Matching relation = NFC-exact code-point equality, UVER-pinned (`NORM-1`) | E-PRIOR: NFC is the already-frozen normalization precedent (§A2 tertiary key). E-STRUCT: among match relations of the form "equality modulo an equivalence on strings," canonical equivalence (= NFC-form identity) is the finest relation that still identifies Unicode-canonically-equivalent encodings of the *same abstract text*; every coarser relation (case folding, diacritic stripping, stemming, NFKC) strictly enlarges the support extension and therefore strictly enlarges the CF-R2 false-positive surface, which T1 designates the dominant residual risk and FM-1 makes the catastrophic direction. The finest admissible relation is unique; `D` takes it (§14.2 argument A3). |
| C5 | Field scope = `title ∪ text`, per item | E-TYPE + E-STRUCT: `title` and `text` are the only fields typed as document *content*; `origin_domain` is typed as provenance (consumed exclusively by `INDEPENDENCE_RELATION`) and `doc_id`/`snapshot_hash_ref` as identity. Including provenance would let a domain string lend content support (MIN-6 witness); excluding `title` would make support depend on which content field a fact appears in — a distinction no frozen authority licenses. Union (not concatenation) avoids token artifacts at field boundaries. |
| C6 | Non-emptiness guard `E(c) ≠ ∅` | E-STRUCT (TSC): without it, a claim with no entity token (empty, whitespace-only, punctuation-only `claim_text`) is vacuously supported by **every** evidence item — a degenerate supremum on that input subclass, and a route to S3 on junk (MIN-3 witness). The guard makes the predicate assert what "entity-level support" means: no entities, no support. |
| C7 | Two-valued totality (`false` otherwise) | E-TYPE + G-1: `D` is a biconditional; exactly one output per input; no third value, no partiality, **no implicit exclusions** (§7.3). |

### 6.5 What `D` deliberately does not contain

No numeric constant. No score or similarity measure. No adjacency, phrase,
n-gram, window, or span condition (any such condition would introduce a
length/offset parameterization — the exact F-3 axis-descent surface; §19.3).
No syntactic, relational, or assertive-content analysis (SQ-SUP-6, §16 row
X-5: no frozen authority licenses it, and it is not implementable as pure
decidable text mechanics without smuggling an undefined analyzer). No
reference to any module, function, file, or interim default (G-8;
`claim_extraction.py` behavior is non-evidence per REGISTER_AUDIT 5.6).

## 7. Positive extension

### 7.1 Necessary and sufficient condition

`(c, e)` is in the positive extension **iff** `E(c) ≠ ∅ ∧ E(c) ⊆ V(e)`
(§6.3). This is a single biconditional: the condition below is both necessary
and sufficient; nothing else forces `true`.

### 7.2 Exhibited positive witness classes (PO-SUP-4, SQ-SUP-7; TSC positive side)

These are **author proof-pack witnesses** (SAM-1 §1.1 part 5), constructed
synthetically over the frozen types. They are not, and were not derived from,
the sealed S0 battery (§2, `S0-REG-1` row).

- **W+1 (verbatim containment).** `c.claim_text = "Kestrel Observatory opened
  in 1901"`; `e.title = "Regional history"`, `e.text = "The Kestrel
  Observatory opened in 1901 near the coast."`
  `E(c) = {Kestrel, Observatory, opened, in, 1901}`; every member ∈ `V(e)`;
  `E(c) ≠ ∅`. **`supports(c, e) = true` is entailed.**
- **W+2 (cross-field union within one item).** Same `c`;
  `e.title = "Kestrel Observatory: 1901"`, `e.text = "It opened in that
  year."` — `Kestrel, Observatory, 1901 ∈ T(title)`; `opened, in ∈ T(text)`;
  union covers `E(c)`. **`true`.**
- **W+3 (punctuation robustness).** Same `c`; `e.text = "…the Kestrel
  Observatory, opened (in 1901)…"` — stripping removes the attached
  punctuation; all tokens match. **`true`.**

Class W+ is non-empty and exhibited; therefore the always-`false` relation
(v1-a) is **not** a model of `D` (THM-5). Corroborated variants (two
independent-origin items each satisfying W+ for the same `c`) exist by
construction, so `ios(c) ≥ 2` is attainable and `D` contributes its share of
S3 reachability to the J-3 joint round (§18.4).

## 8 — (see §8 below) — *[section numbering continues]*

## 8. Negative extension

### 8.1 Explicit non-member classes (SQ-SUP-8; TSC negative side)

Every class below is **provably** in the negative extension (each violates the
§6.3 condition):

- **N1 — Fabricated-entity class (CF-R2).** Any `(c, e)` where some
  `t ∈ E(c)` satisfies `t ∉ V(e)`. Witness: `c.claim_text = "Kestrel
  Observatory opened in 1930"` against W+1's `e`: token `1930 ∉ V(e)`.
  **`false`.** Extended to whole snapshots by THM-4: a claim containing an
  entity token absent from every item's `V(e)` has `supp(c) = ∅`,
  `ios(c) = 0`, hence `c ∉ Σ` — no support anywhere.
- **N2 — Topically-related-but-non-supporting class (the S0 row class,
  T1 §3.1).** `c.claim_text = "Kestrel Observatory closed in 1950"` against
  W+1's `e`: tokens `closed`, `1950` absent. **`false`**, though the evidence
  is topically adjacent (shares `Kestrel`, `Observatory`).
- **N3 — Entity-free claims.** Any `c` with `E(c) = ∅` (empty `claim_text`;
  whitespace-only; punctuation/symbol-only such as `"…"` or `"!!!"`):
  **`false` against every `e ∈ U`** (clause C6).
- **N4 — Empty/junk evidence.** Any `e` with `V(e) = ∅` (empty `title` and
  `text`, or content with no qualifying token) against any `c` with
  `E(c) ≠ ∅`: `E(c) ⊄ ∅`. **`false`.**
- **N5 — Cross-item scattering (CE-4 discriminator).** `c` as in W+1;
  `e₁.text = "Kestrel Observatory"` (only), `e₂.text = "opened in 1901"`
  (only): `supports(c, e₁) = false` and `supports(c, e₂) = false` — entity
  presence never aggregates across items (clause C1). (Whether such a claim
  is in `Σ` depends on the full snapshot; each *pair* here is decided
  `false`.)
- **N6 — Provenance-only mention.** `c.claim_text = "nasa"` against `e` with
  `origin_domain = "nasa.gov"`, `title = "Launch schedule"`,
  `text = "Updated weekly."`: `nasa ∉ V(e)` (domain not consumed, clause C5).
  **`false`.**
- **N7 — Case/normalization non-identity.** `c.claim_text = "NASA budget"`
  vs `e.text = "Nasa budget"` : `NASA ≠ Nasa` under NFC-exact comparison.
  **`false`** (clause C4; deliberate — §9.3).

### 8.2 No implicit exclusions

`D` is a biconditional (clause C7): the negative extension is **exactly**
`U ∖ {(c,e) : E(c) ≠ ∅ ∧ E(c) ⊆ V(e)}`. There is no case decided by
convention, precedence, or reader judgment outside the stated condition; N1–N7
are illustrative partitions of that complement, not an enumeration that could
be incomplete.

## 9. Normalization

### 9.1 Exactly what `SEM-SUPPORT` assumes

- **NFC (UAX #15) under UVER = Unicode 16.0.0**, applied to each field string
  before tokenization (§6.2 item 1). Canonically-equivalent encodings of the
  same abstract text (e.g. `é` as U+00E9 vs `e` + U+0301) **match**.
- **Tokenization** by the UVER `White_Space` property; **stripping** of
  leading/trailing `P*`/`S*` code points; **qualification** by presence of an
  `L*`/`N*` code point (§6.2 items 2–4).
- **Token equality** = code-point-sequence equality of NFC forms. Nothing
  else.

This is the shared normalization object **`NORM-1`** and token rule **`TOK-1`**
exported for J-2 (§24): it is definitionally the same NFC that the frozen §A2
tertiary key applies to `claim_text`, so no cross-object normalization
mismatch can arise from this definition's side.

### 9.2 Exactly what it does not assume

No case folding (simple or full). No NFKC/NFKD compatibility folding
(`①` does not match `1`; `ﬁ` does not match `fi`). No diacritic stripping
beyond canonical equivalence (`café` does not match `cafe`). No stemming,
lemmatization, synonymy, or translation. No whitespace canonicalization beyond
tokenization. No locale, collation, or language dependence. No consumption of
`origin_domain`, `doc_id`, `snapshot_hash_ref`, or `supporting_doc_ids`
(§4.4). No document-length, position, or frequency sensitivity: `T(s)` is a
set — repetition and order carry no information.

### 9.3 Direction of the residual strictness (declared, argued)

Every normalization `D` declines (case folding, NFKC, stemming, …) can only
convert `true` outputs to `false`, never the reverse. The predicate therefore
errs exclusively **toward non-support** — toward S0/S2, away from S3 — which
is the safe direction under FM-1 (a fabricated `CERTAIN` is the zero-tolerance
failure; a missed support is an honest-refusal risk already priced into the
S0 tier argument, T1 §4). This asymmetry is the uniqueness engine of §14.2
(A3) and is recorded as accepted strictness, not hidden (SU-2, §19.4).

## 10. Identity

- **Entity identity.** Two entity tokens are identical iff their NFC forms are
  equal as code-point sequences (§6.2). Nothing else individuates entities;
  there is no entity typing, linking, or coreference (none is licensed;
  §6.5).
- **Claim identity.** `D` assumes **none**. `supports` is a pure function of
  `claim_text` content per pair; it never compares two claims and never
  requires a notion of "the same claim." Claim identity (within a run and
  across replays) is owned by `SEM-EXTRACTION` (SAM-1 SQ-EXT-4) and consumed
  downstream by `ios` through the *set* `supp(c)`; the only property `D`
  contributes is: equal `claim_text` ⇒ equal support behavior (immediate from
  THM-1), so any extraction-side identity that preserves `claim_text` bytes
  preserves the support extension (J-4 hook, §24).
- **Document identity.** `D` assumes only what the type contract gives:
  distinct `EvidenceItem` values are distinct universe elements. `doc_id` is
  not consumed; independence-of-origin is `INDEPENDENCE_RELATION`'s domain
  (frozen, T1 §5.2), applied downstream of `supports` inside `ios`, not
  inside `D`.

## 11. Order invariance (permutation proof)

**Theorem (THM-3).** Let `S = (e₁, …, eₙ)` be any finite sequence of
`EvidenceItem`s and `π` any permutation of `{1..n}`. Then for every
`CandidateClaim c`:

1. `supports(c, eᵢ)` is unchanged under `π` for every `i` — *Proof:* `D`
   consumes only the field values of the single pair `(c, eᵢ)` (§6.3 mentions
   no index, position, neighbor, or aggregate). ∎
2. `supp_S(c) = { e ∈ S : supports(c, e) }` is equal as a **set** for `S` and
   `π(S)` — *Proof:* immediate from 1 and set extensionality. ∎
3. Hence `ios(c) = independent_origins(supp_S(c))` is permutation-invariant,
   and the §A2 secondary key `min{ EVIDENCE_ORDERING_KEY(e) : e ∈ supp_S(c) }`
   is permutation-invariant (a minimum over a set). ∎

Therefore the extension of `supports`, and every frozen downstream quantity
(`Σ`, `ios`, the `≺` keys, the §A3 cascade inputs), is invariant under
evidence-set order, and stable under the frozen `EVIDENCE_ORDERING_KEY`
re-ordering in particular (PO-SUP-8 discharged; G-6).

## 12. Determinism proof

**Theorem (THM-1).** `supports` as defined by `D` is a total function
`U → {true, false}` depending only on the code-point sequences
`(c.claim_text, e.title, e.text)`.

*Proof.* `D` is the composition of: `nfc` (a deterministic algorithm over a
fixed, version-pinned data table — UVER; one output per input string);
`rawtoks` (maximal-substring decomposition against the fixed `White_Space`
set — unique for every string); `strip` (longest-prefix/suffix removal against
fixed category sets — unique); the qualification test (membership in fixed
category sets — decidable); finite-set construction, union, non-emptiness,
and inclusion (unique on finite sets). No step consults randomness, a model,
wall-clock, environment, network, mutable store, iteration order of an
unordered container (all constructions are sets with order-free operations),
or any input field beyond the three named. Composition of total deterministic
functions is total and deterministic; the final inclusion test yields exactly
one boolean. ∎

Corollaries: byte-identical replay across the 22 seeds is preserved
(`supports` never reads `seed` or anything the replay contract varies —
T1 §7.2); the C1 sentinel-substitution property is preserved (`supports`
cannot see `gold_rubric`/`query_family`/metadata — they are unrepresentable in
`U`, T1 §8.1). (PO-SUP-2 discharged; G-1, G-6 contribution.)

## 13. Minimality proof (clause-deletion test)

Per SAM-1 §3.6, every clause of `D` carries a deletion witness: a proof
obligation that fails, or a reading admitted by `D − {clause}` that reopens an
axis row, without it.

| # | Clause deleted / weakened | Punishment (witness) |
|---|---|---|
| MIN-1 | C1 (item scope) → set scope | The frozen formulas §A1/§A2/§A4 become ill-typed (they quantify `supports` per item); and the CE-4 divergence pair (N5) reopens: cross-document token scattering would fire support on every scattered item, inflating `ios`. PO-SUP-7 fails. |
| MIN-2 | UVER pin (§6.1) deleted | Two readers applying different Unicode versions can disagree on probes containing code points unassigned in the older version (assigned-with-decomposition in the newer): NFC forms differ ⇒ token equality differs ⇒ TRR divergence on a well-typed input. PO-SUP-3 fails. |
| MIN-3 | C6 (`E(c) ≠ ∅`) deleted | `E(c) = ∅` makes `E(c) ⊆ V(e)` vacuously true: a punctuation-only claim (`"…"`) is supported by **every** item, gets `ios` = number of independent origins in the snapshot, and reaches S3 on junk — a degenerate supremum on that subclass. PO-SUP-4 (always-true exclusion on a subclass) fails; TSC violated. |
| MIN-4 | C3 (`⊆`) weakened to `∃` (any-entity) or a designated-subset quantifier | The mixed claim `"Kestrel Observatory opened in 1930"` gains support from W+1's `e` (genuine tokens present, fabricated `1930` ignored). THM-4/PO-SUP-5 (CF-R2) fails outright. |
| MIN-5 | C2 qualification criterion (L*/N*) deleted (all stripped tokens are entities, including pure punctuation/symbol tokens) | A claim containing a free-standing dash or ellipsis token demands that exact punctuation token in evidence: matching becomes punctuation-style-sensitive, violating the E-PRIOR "entity-level" commitment (a dash is not an entity) and collapsing the W+ class on typographic variation with no compensating PO gain. Reopens SQ-SUP-2 (individuation names non-entities). |
| MIN-6 | C5 narrowed to `text` only, or widened to include `origin_domain` | Narrowed: W+2 flips `false` — support depends on which *content* field carries the fact, a distinction no authority licenses (arbitrary reading admitted ⇒ UE argument weakens). Widened: N6 flips `true` — provenance lends content support; a claim naming a domain word is "supported" by an item asserting nothing (topically-unrelated support), breaching the SQ-SUP-8 class and the provenance/content type separation. |
| MIN-7 | C4 strengthened by case folding (or NFKC) | The extension strictly enlarges in the false-positive direction (§9.3): `"NASA"`-claim supported by `"Nasa"`-typo evidence and, under NFKC, `"①"` by `"1"` — each a widening of the CF-R2 surface with no PO that requires it; the finest-relation uniqueness argument (§14.2 A3) is destroyed, reopening CE-6 as a live multi-candidate axis. |
| MIN-8 | Stripping (§6.2 item 3) deleted | `"Curie,"` ≠ `"Curie"`: ordinary punctuation adjacency kills nearly every match; the positive class collapses toward the empty relation (v1-a-adjacent degeneracy); PO-SUP-4's positive witness class survives only on punctuation-free prose — an unjustified fragility with no compensating obligation. |

`P` minimality (SAM-1 §5.6): `P` contains no slot whose admissible set could
be collapsed by an available argument and was not — both slots are already
collapsed to singleton/inert (§14.3, PO-SUP-10). Nothing in `D` is decorative;
every clause is witnessed above (G-3).

## 14. Uniqueness of extension (SAM-1 UE criterion)

### 14.1 Claim

> For every element of `U`, the frozen text of `D` (plus the frozen type
> contract and the pinned UVER data) entails exactly one output, derivable by
> a competent reader with zero discretion.

### 14.2 Argument (PO-SUP-3, written discharge)

Every term of `D` has a unique reading; there is no residual
natural-language predicate left to interpretation:

- **A1 (closed vocabulary).** The operative terms are: NFC, `White_Space`,
  `General_Category` classes `P*/S*/L*/N*`, maximal substring, longest
  prefix/suffix, set, `∪`, `⊆`, `∅`, `≠`. The first three are normative,
  version-pinned tables/algorithms of UVER (§6.1) — mechanical, not
  interpretive. The rest are standard mathematical operations on finite
  sequences and sets with unique semantics. No term of the form "material,"
  "relevant," "about," "asserts," or "entity" *as an open concept* survives
  into `D`: "entity token" is *defined* (§6.2 items 3–4), not appealed to.
- **A2 (entity notion is uniquely fixed, not merely stipulated).** Within the
  admissible design space (token-selection notions computable by pure text
  mechanics), C2's notion is the unique maximal one, and maximality is forced
  by PO-SUP-5 (any excluded token class is an escape route for fabricated
  content — §6.4). So even at the level of *why this notion*, no rival
  satisfies the obligations: the choice is entailed, not preferred.
- **A3 (matching relation is uniquely fixed).** Match relations "equality
  modulo an equivalence" are totally ordered by refinement at the relevant
  frontier: NFC-form identity is the finest that still identifies canonical
  encodings of identical abstract text (coarser ⇒ strictly larger CF-R2
  surface, §9.3; finer — raw byte identity — would distinguish canonically
  equivalent encodings of the *same* text, contradicting the frozen §A2
  posture that NFC form *is* the text's canonical form). A frontier with a
  unique finest admissible point admits one choice (§6.4 C4).
- **A4 (quantifier and scope are forced).** C1 by the frozen consumer
  signatures (§4.2); C3 by PO-SUP-5 (MIN-4). Forced choices admit no
  reading variance.
- **A5 (no hidden level).** The v1→v2 regress descended value → function →
  predicate → parameterisation. `D` has no parameterisation level to descend
  to: zero numeric constants, zero thresholds, zero unpinned external
  references (§5, §6.1). The only candidate descent surfaces — tokenization
  detail and normalization version — are pinned to normative UVER tables
  inside `D` itself (§19.3).

Two type-conformant readings of `D` could therefore disagree only by
computing one of the UVER-mechanical steps differently, which is a computation
error, not a reading. UE is argued; it remains, per SAM-1, **tested** by TRR
(§15) and never self-certified (G-4).

### 14.3 Uniqueness handoff (UHO) — the parameter surface `P`

`P` — the complete, finite, typed list of degrees of freedom left to the L2
value `SUPPORT_TEST_PARAMS` — has exactly two slots:

| Slot | Content | Admissible set | UHO mode | Selection ground |
|---|---|---|---|---|
| P-1 | The support-test constant record: `(NORM-1 = NFC@UVER; TOK-1 = White_Space split + P*/S* strip + L*/N* qualification; QUANT = universal; FIELDS = {title, text}; GUARD = E(c) ≠ ∅; FOLDING = none)` | **Singleton** — each component is entailed by a clause of `D` (§6.4); distinct members do not exist. | **UHO-a** (transcription-shaped; the `EVIDENCE_ORDERING_KEY` pattern) | E-STRUCT: transcription of `D`. E4b authors the Parameter by copying, exactly as derivation-method §8 step 2 requires. |
| P-2 | The concrete byte-level serialization of P-1 inside `constants.py` (key names, ordering, quoting) as digest input | All serializations denoting the P-1 record | **UHO-b** — provably extensionally inert: no consumer of `supports` reads the serialization; only `frozen_constants_digest()` hashes it, and the digest requires *some one* fixed byte form, any of which yields a valid tripwire (T1 §6.1). | E-PRIOR identity convention: the existing `constants.py` transcription convention (the `SPEC_VERSION`-class pattern), pinned by the ReleaseManager's verbatim-transcription rule (derivation-method §8 step 2). |

No third slot exists. In particular there is **no** semantic freedom left to
the value layer: the root-cause defect ("undefined semantics filed as a
deferred value") is not expressible against this `P` (SAM-1 §3.5; PO-SUP-10
discharged). This also discharges, for this register, the derivation method's
recorded §2.2 insufficiency: E4b now holds a selecting ground for every
surviving freedom (SAM-1 A-7).

## 15. Two-reader reproducibility (TRR obligations)

Per SAM-1 §3.2, this candidate binds itself to the following, and is
**falsified** by any breach:

1. Two readers, independent of this author and of each other, receive only:
   this document's `(U, D, P, X)` (§§4–6, 14.3, 16), the frozen type
   contract, and the probe battery (`S0-PB-1` core + the S4 adversarial
   extension). They do **not** receive `Π` (§§11–14, 17–21), author intent,
   or each other's answers.
2. For each probe they hand-evaluate `D`: normalize (NFC/UVER), tokenize,
   strip, qualify, compare sets — every step is executable by hand with the
   UVER data tables (G-8: no implementation required).
3. Any divergence, or any `UNDERDETERMINED` (with the ambiguous term named),
   **falsifies this candidate** (SAM-1 §3.2 step 4; rejection ground R-3).
4. Agreement over the full battery is necessary-but-not-sufficient: it feeds
   S3/S4; acceptance further requires §22 in full. Post-acceptance divergence
   on any well-typed input is an MF-1 event (SAM-1 §11.2): the revision
   reopens and SAM-1 itself must be strengthened before re-authoring.

`D` was constructed for hand-evaluability: every probe evaluation terminates
in a number of steps linear in input length, with no search, backtracking, or
judgment call.

## 16. Axis closure (`X`)

Every registered scientific question (SAM-1 §5.1, registered unmodified by
`S0-QS-1`) is answered by citation into `D` or `P`. No row is empty; no row is
answered by prohibition alone.

| Row | Question (SQ) | Closed by |
|---|---|---|
| X-1 | SQ-SUP-1 — universe; item vs set | §4.1 (U total over `CandidateClaim × EvidenceItem`); §4.2 (item-scoped, forced by §A1/§A2/§A4). Closes CE-4. |
| X-2 | SQ-SUP-2 — entity individuation; owner | §6.2 items 2–5 (`ENT-1`/`TOK-1`), owned **here** and exported to `SEM-EXTRACTION` by reference (§24; J-1). Closes v1-a's individuation gap. |
| X-3 | SQ-SUP-3 — quantifier | §6.3/§6.4 C3: universal (`⊆`), forced by CF-R2 (MIN-4). Closes CE-5. |
| X-4 | SQ-SUP-4 — matching relation / normalization / decidability | §6.2 item 5 + §6.4 C4 + §9 (`NORM-1`: NFC-exact @ UVER; decidable by table lookup and comparison). Closes CE-6. |
| X-5 | SQ-SUP-5 — evidence fields | §6.4 C5: `{title, text}` union per item; `origin_domain` excluded as provenance (MIN-6). |
| X-6 | SQ-SUP-6 — anything beyond entity presence? | §6.5: **No.** Support = total entity-token presence, exactly; the decidable condition *is* §6.3. Grounds: T1 §5.3 names entity-level matching as the whole frozen commitment; relational/assertive analysis is unlicensed and not decidably specifiable within the frozen means. Residual consequence recorded as SU-1 (§19.4). |
| X-7 | SQ-SUP-7 — what forces `true` | §7 (positive biconditional side; exhibited class W+1–W+3). Excludes v1-a structurally (TSC). |
| X-8 | SQ-SUP-8 — what forces `false` | §8 (N1 fabricated-entity/CF-R2; N2 topical-non-supporting/S0 row; N3–N7). Excludes the always-true relation (TSC; MIN-3). |
| X-9 | SQ-SUP-9 — order invariance; `ios` well-definedness | §11 (THM-3); §17.1/PO-SUP-7 (THM-7). |
| X-10 | SQ-SUP-10 — degrees of freedom left to `SUPPORT_TEST_PARAMS` | §14.3: two slots, P-1 singleton (UHO-a), P-2 inert (UHO-b). No semantic freedom survives. |

RCA §6 axis coverage for completeness: **scope** (X-1), **quantifier** (X-3),
**normalization** (X-4), **corpus of quantification** (X-1: `U` is declared
and total; the operational-corpus question CE-11 is additionally owned by
J-3's declared quantification space at S4), **granularity/span** (not
`supports`-content: owned by `SEM-EXTRACTION` per SAM-1 §7.1 SQ-EXT-2/3;
`supports` consumes whatever claims exist — declared boundary, §24),
**discourse level** (owned by `SEM-TEMPLATE`), **composition** (owned by the
S4 joint round; this object's contribution is §18.4). Per SAM-1 §3.3, this
table is a floor; the open-ended residue is owned by UE/TRR, not by this
enumeration.

## 17. Historical replay

Why every historical failure is impossible against this definition:

### 17.1 Finding 1 (v1-a: always-`False` support admissible)

v1-a existed because the constraint layer was all-prohibition: nothing forced
`supports` to fire. `D` is a biconditional with an exhibited non-empty
positive class (§7.2): the always-`false` relation disagrees with `D` on W+1
and is **not a model of `D`** — excluded by the definition itself, not by
audit vigilance (PO-SUP-4; TSC). *(v1-b and v1-c target extraction and
templates and are out of this object's scope; their closure is owed by
`SEM-EXTRACTION`/`SEM-TEMPLATE` under their own protocols.)*

### 17.2 Finding 2 (CE-4, CE-5, CE-6 — the `supports` counterexamples)

- **CE-4 (item- vs set-scoped "evidence text").** Two non-equivalent
  predicates were equally licensed. Now: the universe itself is item-scoped
  (§4.2), forced by the frozen consumer formulas; the set-scoped reading is
  ill-typed against `U`. The N5 witness pair evaluates `false`/`false` with
  zero discretion. **Both readings can no longer coexist.**
- **CE-5 (all / head / any quantifier).** Now: `⊆` in the defining
  biconditional (C3); MIN-4 shows every rival quantifier breaks PO-SUP-5.
  **The quantifier is written, and forced.**
- **CE-6 (exact vs normalized match).** Now: NFC-exact at pinned UVER (C4),
  with the finest-admissible-relation uniqueness argument (§14.2 A3) and the
  N7 witness. **The normalization is written, unique, and version-pinned.**

CE-10/CE-11/CE-13 (compositional, corpus-scope, claim-identity pathologies)
are, per SAM-1 §9 and the RCA (§4.3: "no layer owns the composition" —
repaired by giving it an owner), owned by the S4 joint round over `S0-JW-1`;
this definition's enabling contributions are stated in §18.4 and its
claim-identity neutrality in §10. CE-12 targets `is_material` and is owed by
`SEM-MATERIALITY`.

### 17.3 Root Cause (`C` — the misplaced abstraction boundary)

The defect: layer-4 semantics filed on the deferred-value side, authored by
nobody, so every correction was selector-shaped over an undefined set. This
document **is** the layer-4 content, on the specification side: a defined
universe, a two-sided biconditional with positive clauses, individuated by
construction. The regress engine is removed for this register point by point
(SAM-1 §12): the layer is authored (this text); two-sidedness holds by
construction (§7/§8); no selector exists or is needed — like
`EVIDENCE_ORDERING_KEY`, the register is simply *defined*, and its value layer
is transcription (§14.3); and there is no meta-level left to relocate
undefinedness into (§14.2 A5).

### 17.4 SAM-1 (the methodology's own bar)

This candidate is the five-part object SAM-1 §1.1 demands — `U` (§4), `D`
(§6), `P` (§14.3), `X` (§16), `Π` (§§11–14, 17–21) — satisfies TSC (§7/§8),
carries a MIN witness per clause (§13), discharges UHO per slot (§14.3), and
binds itself to TRR falsification (§15) and to the S3–S5 stages it cannot
perform for itself (§22–§23). No SAM-1 instrument is weakened, reinterpreted,
or bypassed.

## 18. Compatibility

### 18.1 T1 (mechanism preregistration)

- **§5.3 register row:** deterministic ✓ (THM-1); entity-level, not
  topic-level ✓ (literal token presence; topical adjacency yields `false`,
  N2); "No probability numbers" ✓ (zero numeric content of any kind);
  fabrication-pressure posture ✓ (THM-4).
- **§3.1 S0 row:** "support test fails everywhere — includes empty, junk, and
  topically-related-but-non-supporting results" — preserved exactly: N2/N3/N4
  realize those classes; PO-SUP-6 (§21) proves the boundary is neither
  widened nor narrowed: `D` defines *which* pairs support; T1 defines S0 as
  `Σ = ∅`; `D` alters neither the formula nor the precedence.
- **§3.2/§3.3, §4:** untouched — `STATE_TIER_MAP`, `CONFIDENCE_TIERS`,
  precedence `S0 → S1 → (S2|S3)`, tier arguments: no edit entailed (R-5
  clean).
- **§7.2 replay / §8 input restriction:** preserved (THM-1 corollaries, §12).

### 18.2 PA-3 (addendum §A0–§A7)

- §A1: `ios(c)` well-defined — `supp(c)` is a finite set by THM-1/THM-3;
  `independent_origins` applies unchanged (PO-SUP-7).
- §A2: the secondary key's `min` is over a well-defined set (§11); nothing in
  `D` touches the tie-break keys. **Compatibility note (recorded, not an
  edit):** §A2's tertiary key presupposes an NFC form of `claim_text`; `D`
  pins NFC to UVER for its own matching. At implementation time the single
  environment realizes both; the *single shared Unicode version* is a J-2
  registry item (§24) so drift between the two NFC applications is
  structurally impossible. §A2's text requires no change (it names NFC, not a
  version; UVER instantiates it).
- §A4/§A5/§A6: `contradicts` and `is_material` are neither consumed, defined,
  narrowed, nor widened here (imports: none — §24); the S1 composition reads
  `supp(·)` only through the frozen formulas, which THM-3/THM-7 keep
  well-defined.
- §A7 I-1/I-2/I-3: seam invariants preserved — `D` changes no field
  semantics of `EvidenceStateResult` and entails no code path.

### 18.3 Ontology and migration

Well-formed object per ONT-1 §2 (§3 above): right class/origin/owner/
lifecycle; references L0/L1 only, acyclic (§24). Migration M5: this text is
the content of the declared slot; M12: upon its freeze, the derivation-method
§3 precondition becomes satisfiable for `SUPPORT_TEST_PARAMS`; M17: authored
in the E4a position, before E4b; ONT-1 §6: `Parameter[SEM-SUPPORT]` remains
uninhabited until freeze — this document inhabits nothing.

### 18.4 Derivation method and E4b

Post-freeze, the E4b derivation of `SUPPORT_TEST_PARAMS` under method §3 is
**transcription-shaped**: P-1 is a singleton entailed by `D` (UHO-a), P-2 is
inert convention (UHO-b). Method §2.2's "no value-selecting class" gap is
closed for this register by construction (SAM-1 §3.5, A-7). The method's §3.2
constraints (determinism, entity-level, totality, firewall, 3-field
expressibility, `EVIDENCE_ORDERING_KEY` stability) are each theorems here
(THM-1, THM-2, THM-3, THM-FW), not obligations left to the value author.
Joint-reachability enablement for J-3: W+-class corroborated inputs give
`ios ≥ 2` attainability (S3-side); N-class inputs give `Σ = ∅` attainability
(S0-side); S1/S2 witnesses require composition with the other three
definitions and are owed at S4 over `S0-JW-1`, as SAM-1 assigns.

### 18.5 S0 preregistration

`S0-REG-1` is consumed by identity. This document: answers the 10 registered
`QS-SUP` rows (§16) without rewording any; records no expected output for any
sealed probe (author witnesses in §7/§8/§13/§19 are proof-pack constructions,
authored without access to `S0-PB-1`/`S0-JW-1` payloads — SAM-R3); and defers
to GC-1…GC-6 as the gate its own S3 admissibility depends on (header Status).

## 19. Adversarial search

Counterexamples were sought against every clause; each is destroyed or its
residue explicitly recorded.

### 19.1 Extensional-ambiguity attacks (F-1 class)

- **Attack: two conformant relations differing on some pair.** Requires a term
  of `D` with two readings; §14.2 A1 leaves only UVER-mechanical steps, whose
  outputs are table-determined. **Destroyed** (modulo TRR's independent test,
  which this document cannot and does not waive).
- **Attack: set-scoped rereading of C1 (CE-4 replay).** Ill-typed against
  §4.1/§4.2. **Destroyed.**
- **Attack: "entity" reinterpreted as NER-style named entities.** "Entity
  token" is a defined term (§6.2 items 3–4); the word "entity" does not occur
  in `D` as an open predicate. **Destroyed.**

### 19.2 Degeneracy/determinism attacks (F-2 class)

- **Always-false model:** contradicts W+1 (§7.2). **Destroyed.**
- **Always-true model:** contradicts N1 (§8.1). **Destroyed.**
- **Vacuous-truth degeneracy on empty claims:** blocked by C6 (MIN-3).
  **Destroyed.**
- **Input-external dependence (clock/env/store/seed/model):** no such term
  exists in `D` (§12). **Destroyed.**

### 19.3 Axis-descent attacks (F-3 class — the v2-killer, re-aimed here)

- **Descent into tokenization parameters** (delimiter choice, punctuation
  classes): pinned to UVER normative properties inside `D`; there is no
  delimiter *parameter* — the `White_Space`/`General_Category` tables are the
  rule. **Destroyed.**
- **Descent into normalization version:** pinned (UVER; MIN-2). **Destroyed.**
- **Descent into a similarity/threshold layer:** `D` contains no numeric or
  ordered family at all; there is no parameterisation level beneath P-1's
  singleton. **Destroyed.**
- **Descent into serialization:** P-2, proved inert (UHO-b, §14.3).
  **Destroyed.**

### 19.4 Surviving uncertainty (explicitly recorded, per mission §19)

- **SU-1 — Token-coincidence false positive.** A constructible evidence text
  can contain every entity token of a claim while asserting a different or
  contrary fact (e.g. `e.text = "Marie Smith and Pierre Curie visited; no
  Nobel Prize in Physics was awarded in 1903 to either"` contains all tokens
  of `"Marie Curie won the Nobel Prize in Physics in 1903"` **if** each token
  literally appears). Under `D` such an item supports the claim. This is not
  an ambiguity of `D` (the output is uniquely entailed) but a **semantic
  fidelity limit** of entity-presence support. It is exactly the risk class
  T1 already names as the dominant residual (CF-R2: "a fabricated factual
  answer with tier CERTAIN can occur only if the claim-support test
  false-positives … the dominant residual risk, never a design permission"),
  and `D` minimizes it within the frozen means (universal quantifier — the
  strictest available; finest matching relation — §14.2 A3). Closing it
  further would require assertive-content analysis that no frozen authority
  licenses and that pure decidable text mechanics cannot supply without
  smuggling an undefined analyzer (X-6). **Recorded as surviving,
  quantified in direction (false-positive), bounded by strictness, and owned:
  it remains CF-R2's residual, unchanged in kind, now with its mechanism
  stated instead of undefined.**
- **SU-2 — Strictness false negatives.** Paraphrase, inflection
  (`opened`/`opens`), synonymy, translation, and case variance defeat
  support; genuinely corroborating evidence phrased differently yields
  `false`, biasing toward S0/S2. Direction is fail-safe (§9.3; FM-1
  asymmetry). The scientific cost lands on H1's measured calibration, which
  is precisely the exposure EXP-1 exists to test (T1 §4 closing) — a kill
  there is a valid outcome, not a defect of definedness. **Recorded.**
- **SU-3 — TRR is the outstanding empirical test.** UE is argued (§14), not
  self-certified; per SAM-1 G-4 the author's failure to find a
  counterexample is not acceptance. The S3/S4 falsification stages (F-1…F-5,
  TRR, joint round) remain open obligations. **Recorded.**

No other surviving uncertainty is known to the author; discovery of one
post-acceptance is an MF-2 event (SAM-1 §11.2).

## 20. Formal theorems

Grounding: `D` (§6.3), functions of §6.2, frozen formulas of addendum
§A1–§A4. Proof sketches are complete at the level of hand verification; every
step is finite and mechanical.

- **THM-1 (Determinism/functionality).** `supports` is a total function of
  `(c.claim_text, e.title, e.text)` into `{true, false}`. *Proof:* §12. ∎
- **THM-2 (Totality).** For every `(c, e) ∈ U`, including empty strings,
  junk, unassigned code points, and arbitrarily long inputs, `D` entails
  exactly one output. *Proof:* every §6.2 function is total (§12); the
  biconditional partitions `U`. ∎
- **THM-3 (Order invariance).** The extension, `supp(c)`, `ios(c)`, and the
  §A2 min-key are invariant under any permutation of the evidence set.
  *Proof:* §11. ∎
- **THM-4 (CF-R2 entailment).** If some `t ∈ E(c)` satisfies `t ∉ V(e)` for
  every `e` in a snapshot `S`, then `supp_S(c) = ∅`, `ios(c) = 0`, and
  `c ∉ Σ`. *Proof:* for each `e`, `E(c) ⊄ V(e)` (witness `t`), so
  `supports(c, e) = false` by §6.3; `supp_S(c) = ∅`;
  `independent_origins(∅) = 0`; `Σ = { c : ios(c) ≥ 1 }` excludes `c`
  (§A1). ∎ — CF-R2's first line is thereby a **theorem**, not a residual
  hope: a fabricated entity absent from all evidence contributes no support
  (PO-SUP-5).
- **THM-5 (Two-sidedness / non-degeneracy).** `D` has models on neither
  extreme: `supports` is `true` on W+1 and `false` on N1 — so the
  always-false and always-true relations each disagree with `D` somewhere,
  hence neither satisfies `D`. *Proof:* direct evaluation of §7.2/§8.1
  witnesses. ∎
- **THM-6 (S0-boundary preservation).** Under `D`, `Σ = ∅` iff no candidate
  claim is supported by any evidence item — the exact T1 §3.1/§A3 S0
  condition; `D` introduces no additional S0-firing or S0-blocking clause.
  *Proof:* `Σ`'s definition (§A1) is consumed verbatim; `D` only decides the
  membership test inside it. ∎
- **THM-7 (`ios` well-definedness).** `supp(c)` is a well-defined finite set
  for any finite evidence set; `ios(c) = independent_origins(supp(c))` under
  the frozen `INDEPENDENCE_RELATION` is well-defined and order-free.
  *Proof:* THM-1 (membership decidable per item) + THM-3 (set, not
  sequence). ∎
- **THM-8 (Strictness monotonicity).** If `E(c₁) ⊆ E(c₂)` and `E(c₁) ≠ ∅`,
  then `supports(c₂, e) ⇒ supports(c₁, e)` for every `e`. *Proof:*
  `E(c₂) ⊆ V(e) ∧ E(c₁) ⊆ E(c₂) ⇒ E(c₁) ⊆ V(e)`. ∎ — Under entity-set
  inclusion, a larger entity set never gains support where a smaller
  non-empty subset lacks it; fabrication that enlarges `E(c)` strictly
  shrinks the support set (the mechanism behind THM-4). (String-append on
  `claim_text` is not claimed: NFC can make `E` non-monotone under append.)
- **THM-FW (Firewall by construction).** No component of `D` or of `P`'s
  admissible sets is, equals, or is fitted to any numeric quantity at all —
  a fortiori not to any EXP-1 probability, bin boundary, or ECE threshold.
  *Proof:* by inspection, `D` and P-1 contain no numeric constant; P-2 is a
  serialization convention carrying no number; no stage of this authoring
  consulted any evaluation-side object (§2 forbidden row). ∎

## 21. Proof obligations (SAM-1 §5.4 — written discharge map)

| PO | Obligation | Discharged by |
|---|---|---|
| PO-SUP-1 (TOTAL) | Output for every element of `U`, incl. empty/junk/near-miss | THM-2; §4.1; N2–N4 near-miss/junk classes. |
| PO-SUP-2 (DET) | Function of input content alone | THM-1; §12 corollaries (replay, C1 sentinel). |
| PO-SUP-3 (UE) | No two type-conformant readings disagree | §14.2 (argued); §15 (TRR-tested at S3, not waived). |
| PO-SUP-4 (POS/NEG) | Witness classes exhibited; both degeneracies excluded by `D` | §7.2, §8.1, THM-5; MIN-3. |
| PO-SUP-5 (CF-R2) | Fabricated entity ⇒ no support, proved from `D` | THM-4 (+ THM-8 mechanism). |
| PO-SUP-6 (S0-BOUND) | S0 boundary neither widened nor narrowed | THM-6; §18.1. |
| PO-SUP-7 (IOS) | `ios` well-defined; §A1/§A3 consume unchanged | THM-7; §18.2. |
| PO-SUP-8 (ORDER) | Permutation invariance; `EVIDENCE_ORDERING_KEY` stability | THM-3; §11. |
| PO-SUP-9 (FIRE) | No evaluation-side quantity in `D` or `P` | THM-FW; §2 (forbidden evidence untouched). |
| PO-SUP-10 (UHO) | Every `P` slot UHO-a or UHO-b | §14.3 (P-1 UHO-a singleton; P-2 UHO-b inert + convention ground). |

Every discharge above cites only allowed evidence (E-STRUCT, E-TYPE, E-PRIOR,
E-DETERM arguments grounded in T1 §3.1/§5.3, addendum §A0–§A7, the frozen type
contract, ONT-1; CE items appear only as constraint provenance). No EXP-1
object, corpus statistic, observed-score preference, implementation behavior,
or unrecorded intuition is cited anywhere in `Π` (SAM-1 §5.2/§5.3).

## 22. Acceptance conditions

This candidate is accepted, and becomes freeze-eligible at E4a, **only** when
all of the following hold, each mapped to a named artifact (SAM-1 §5.9, §10.1
— none is produced by this document):

| # | Condition | Artifact |
|---|---|---|
| AC-1 | Five-part deliverable well-formed (`U` §4, `D` §6, `P` §14.3, `X` §16, `Π` §§11–21); TSC holds; ontology manifest valid; no forbidden vocabulary | S1 structural-gate record |
| AC-2 | `X` complete over SQ-SUP-1…10 by citation (no empty/evasive row) | §16 checked at gate |
| AC-3 | PO-SUP-1…10 discharged from allowed evidence only | §21 / `Π` citation check |
| AC-4 | Independent falsification F-1…F-5 (incl. TRR §15) returns NO-COUNTEREXAMPLE over `S0-PB-1` + adversarial extension | S3 L4 verdict |
| AC-5 | Joint round J-1…J-7 passed over `S0-JW-1` (with all four candidates individually past S3) | S4 L4 verdicts |
| AC-6 | Minimality record complete (§13), independently checked (auditor deletion attempts punished) | MIN record + S3 check |
| AC-7 | UHO discharged per slot (§14.3) | UHO table |
| AC-8 | Ontology well-formedness and role/no-proxy discipline intact across S0–S4 (incl. the SAM-R2 timestamp precedence recorded in the header Status) | manifests + stage records |
| AC-9 | ScientificAuditor approval recorded, referencing AC-1…AC-8 by identity | S5 L5 record |

Only after AC-1…AC-9: freeze at E4a (S6), whereupon `Parameter[SEM-SUPPORT]`
becomes inhabitable and E4b may run. Freeze, transcription, digest, and gate
movement remain governed by the existing documents and are not performed here.

## 23. Rejection conditions

Any single one rejects this candidate, recorded with cause; the revision
returns to S1 as a new L1 draft and this text's falsification record is
retained permanently (SAM-1 §5.10, §10.2):

- RC-1: any unanswered or evasively-answered SQ row (an axis "answered" by
  prohibition or role-restatement is empty);
- RC-2: any PO undischarged, or discharged from forbidden evidence;
- RC-3: any F-1…F-3 counterexample; any TRR divergence or `UNDERDETERMINED`
  (including one arising from the UVER pin, the tokenization rule, or any
  clause of §6);
- RC-4: any `P` slot found to conceal semantic freedom (UHO failure) — e.g.
  a demonstration that P-2's serialization is not consumer-inert, or that
  P-1's admissible set is not a singleton;
- RC-5: any boundary breach — a demonstration that `D` entails a change to
  any frozen T1/addendum/type content (the claimed-necessary change routes
  to change control as a separate Wave-2 proposal, never absorbed);
- RC-6: any firewall contamination of any stage;
- RC-7: any role or sequencing breach (author-seen sealed probes, author-run
  falsification, proxy approval, or S1 preceding a valid S0 gate record) —
  voids the affected stage record;
- RC-8: TSC failure;
- RC-9: unresolved MIN failure (a clause with no surviving witness);
- RC-10: joint-round failure localized to this candidate's text (per SAM-1
  §9), including a J-2 normalization-coherence failure or a J-5
  `supporting_doc_ids`/`supports` incoherence traceable to §4.4's declared
  non-consumption.

## 24. Future imports and exports (declared definitional DAG edges)

**Imports (objects this definition consumes):** none from any other `SEM-*`.
Its only definitional dependencies are: the frozen type contract (L1), the
frozen consumer formulas of addendum §A1/§A2/§A4 (L1, consumed as fixed
context — signatures only, no content absorbed), and the UVER-pinned Unicode
Standard (L0 external reference). The graph is trivially acyclic and
references no object later than L1 (J-6).

**Exports (objects defined here, single-sourced for the J-1 registry, to be
imported by reference and never redefined):**

| Exported object | Defined at | Anticipated importers |
|---|---|---|
| `NORM-1` — normalization: NFC @ UVER (Unicode 16.0.0), no folding | §6.1–§6.2, §9 | `SEM-EXTRACTION` (SQ-EXT-6: `claim_text` construction / §A2 tertiary-key validity), `SEM-MATERIALITY` (SQ-MAT-6), J-2 registry |
| `TOK-1` — tokenization: `White_Space` split; `P*`/`S*` strip; interior punctuation retained | §6.2 items 2–3 | `SEM-EXTRACTION` (SQ-EXT-9), J-1 registry |
| `ENT-1` — entity-token notion: qualifying stripped tokens (`L*`/`N*` criterion); entity identity = NFC code-point identity | §6.2 items 4–5, §10 | `SEM-EXTRACTION` (SQ-EXT-9 single-sourcing), J-1 registry |
| `UVER` — the pinned Unicode version | §6.1 | all three other `SEM-*`; the §A2-key implementation environment (compatibility note §18.2) |

Declared open hooks this definition **enables but does not discharge** (owned
where SAM-1 assigns them): J-3 joint reachability (S4, over `S0-JW-1`); J-4
identity-stability composition (`SEM-EXTRACTION` + S4; this object's
contribution: claim-text-functionality, §10); J-5 `supporting_doc_ids`
coherence (`SEM-EXTRACTION` + S4; this object's contribution: declared
non-consumption, §4.4); J-7 joint TRR.

## 25. Appendix

### 25.1 Notation

| Symbol | Meaning |
|---|---|
| `⟺` | if and only if (biconditional) |
| `∈, ∉, ⊆, ⊄, ∪, ∅, ≠` | set membership/non-membership, inclusion, non-inclusion, union, empty set, inequality |
| `ε` | the empty string |
| `U` | the declared universe (§4.1) |
| `D` | the defining rule (§6.3) |
| `P` | the declared parameter surface (§14.3) |
| `X` | the axis-closure table (§16) |
| `Π` | the proof pack (§§11–14, 17–21) |
| `nfc(s)` | NFC normal form of `s` under UVER (§6.2) |
| `rawtoks(s)`, `strip(w)` | tokenization and stripping functions (§6.2) |
| `T(s)` | entity-token set of string `s` (§6.2) |
| `E(c)` | `T(c.claim_text)` — the claim's entity set |
| `V(e)` | `T(e.title) ∪ T(e.text)` — the item's content-token set |
| `supp(c)` | `{ e : supports(c, e) }` over a given evidence set (addendum §A4) |
| `ios(c)` | `independent_origins(supp(c))` (addendum §A1) |
| `Σ` | the supported set `{ c : ios(c) ≥ 1 }` (addendum §A1) |
| `UVER` | Unicode 16.0.0, pinned (§6.1) |

### 25.2 Definitions (index)

| Term | Where defined |
|---|---|
| entity token; qualification | §6.2 items 3–4 (`ENT-1`) |
| token equality / matching relation | §6.2 item 5, §9 (`NORM-1`) |
| positive/negative extension | §7 / §8 |
| item scope | §4.2 (clause C1) |
| non-emptiness guard | §6.4 clause C6 |
| parameter slots P-1, P-2 | §14.3 |
| surviving uncertainties SU-1…SU-3 | §19.4 |

### 25.3 Identifier registry created by this document

`SEM-SUPPORT` (rev `sem-support-2026-07-16-r2`); clauses C1–C7 (§6.4);
witnesses W+1–W+3, N1–N7; minimality witnesses MIN-1…MIN-8; theorems
THM-1…THM-8, THM-FW; axis rows X-1…X-10; parameter slots P-1, P-2; exports
`NORM-1`, `TOK-1`, `ENT-1`, `UVER`; acceptance/rejection rows AC-1…AC-9 /
RC-1…RC-10; surviving uncertainties SU-1…SU-3.

---

*End of `SEM-SUPPORT`. This document defines the extensional semantics of
`supports(claim, evidence)` and nothing else: universe total, rule
biconditional and two-sided, parameter surface collapsed to
transcription-plus-inert-convention, every registered axis closed by
citation, every proof obligation discharged in writing from allowed evidence,
every clause minimality-witnessed, and three surviving uncertainties recorded
rather than hidden. It authors no other `SEM-*` object, chooses no L2 value,
alters no frozen T1/PA-3/SAM-1 content, writes no code, and performs no
governance: it is a drafted L1 candidate awaiting SAM-1 stages S3–S5.
`Parameter[SEM-SUPPORT]` remains uninhabited, `CONSTANTS_HASH` remains
`None`, and the standing prohibition holds.*

# PROGRAM A — SEM-EXTRACTION: THE EXTENSIONAL SEMANTICS OF THE CANDIDATE-CLAIM BOUNDARY

**Title:** `SEM-EXTRACTION` — the canonical L1 semantic definition of PA-2's
candidate-claim boundary: universe, defining rule, parameter surface, axis
closure, and proof pack, authored under
`PROGRAM_A_SEMANTIC_AUTHORING_METHODOLOGY.md` (SAM-1).
**Object identity:** `SEM-EXTRACTION`, revision `sem-extraction-2026-07-16-r3`
— class `SemanticPredicate` (over PA-2's input space, per the migration slot
table), origin L1, owner Architect, lifecycle **drafted**. This is the
S1-stage candidate deliverable `(U, D, P, X)` of SAM-1 §7 with its S2-stage
proof pack `Π` carried inline (§§10–21).
**Authority basis:** `PROGRAM_A_ARCHITECTURAL_ONTOLOGY.md` (ONT-1, consumed as
fixed); `PROGRAM_A_ONTOLOGY_MIGRATION_PLAN.md` (slot `SEM-EXTRACTION`,
M5/M12/M17, E4a schedule); `PROGRAM_A_SEMANTIC_AUTHORING_METHODOLOGY.md`
(SAM-1 §3, §7); `PROGRAM_A_SEM_S0_PREREGISTRATION.md` (`S0-REG-1`, consumed by
identity); `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §3.1/§5.6/§7/§8 and
`PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` §A0–§A7 (fixed semantic context,
preserved, never altered — §A2 load-bearing); `PROGRAM_A_REGISTER_DERIVATION_METHOD.md`
§2.2/§5 (evidence classes; the E4b procedure this definition makes
dischargeable); `PROGRAM_A_SEM_SUPPORT.md` revision `sem-support-2026-07-15-r1`
(sibling L1 candidate; its exports `NORM-1`, `TOK-1`, `ENT-1`, `UVER`, and its
defining rule for `supports` are **imported by reference and by revision
identity** — §24). The falsification history —
`PROGRAM_A_REGISTER_DERIVATION_ROOT_CAUSE_ANALYSIS.md`,
`docs/audits/REGISTER_DERIVATION_FINDING1_SONNET_AUDIT.md`,
`docs/audits/REGISTER_DERIVATION_FINDING2_SONNET_AUDIT.md` — is consumed as
**L0 provenance only**: it motivates obligations; it transfers no semantic
authority (SAM-1 §7.2/§7.3).
**Date:** 2026-07-16
**Revision note (r2 → r3):** Before this revision the author performed the
complete internal minimality re-audit that SAM-1 §3.6 requires and that r1's
RC-9 failure showed is not optional: **every** normative sub-clause of `D`
(§6.1–§6.3, the full inventory — not only the C-row summaries) was deleted in
turn and the deletion tested against the extension of `extract`, determinism,
totality, unique extension (UE/TRR), and the remaining accepted obligations
(type conformance PO-EXT-5; J-1/J-2/J-5; the §24 export identities). Findings
(§13.1, INERT-1…INERT-7): r2's clause **D4** (empty case) was a restatement —
the `Q ≠ ∅` guard lives in the anchor test and `A = ∅` already forces `()`
through D3's sort, so totality is a theorem (THM-2), not a clause; the **"or
by end-of-string" disjunct** of SEG-1's follow-context condition was dead in
exactly r1's `Nd`-exception manner — a terminal split point spawns only an
empty segment that the discard clause removes, so it never altered any unit
of any string; SEG-1's **zero-split fallback sentence** restated the `k = 0`
case of the boundary construction; the **sequence structure of `units(e)`**
(title-first order, multiplicity) is consumed by no clause — D1 reads
membership only — and `units(e)` is now a set; **D1's duplicate-collapse
sentence** restated its own set-builder; and several **glosses restating
imported or frozen content** were removed or relocated into `Π` (a J-2
hygiene gain). **The extension of `extract` and of every §24 export is
identical to Revision 2 on every element of `U`** (§13.1
extension-preservation theorem). The surviving clauses now carry a complete
per-sub-clause witness inventory (§13.2, MIN-EXT-1…17; MIN-EXT-2 split into
2a/2b), closing four witness gaps r2 left (C1 typing; D2's
`EVIDENCE_ORDERING_KEY` order; D2's duplicate-`doc_id` collapse-to-first;
SEG-1's trim; field scope) and explicitly flagging two clauses (empty-unit
discard; `nfc` as `seg`'s domain) that are **inert for `extract` but
extensional for the exported `SEG-1`** and survive on the export-identity
ground alone. Bookkeeping repaired: §6.1–§6.4, §8.1 (N-E2/N-E7), §8.2, §13
(rewritten), §19.3, §20 (THM-2/THM-4 proof pointers), §24, §25. No theorem
statement changes; THM-1…THM-9 and THM-FW hold verbatim.
**Revision note (r1 → r2):** Revision 1 (`sem-extraction-2026-07-15-r1`)
failed independent audit on ground RC-9: the `Nd` exception clause of `SEG-1`
was proved **extensionally vacuous**. The exception could apply only where
the `U+002E` is immediately followed by a code point of `General_Category`
`Nd`; but `SEG-1`'s split condition fires only where the terminator is
followed by a code point with the `White_Space` property or by end-of-string,
no `Nd` code point has the `White_Space` property (UVER), and end-of-string
is not a code point — the exception's guard region and the split condition's
region are disjoint, so the exception never altered any split, and its
recorded deletion witness (r1 MIN-EXT-2 via N-E7) was not genuine. Revision 2
removes the dead clause and every claim that it was load-bearing, and repairs
the affected proof bookkeeping only (§6.1, §8.1 N-E7, §12, §13 MIN-EXT-2,
§14.2 A1, §19.1, §19.3, §23 RC-3, §24, §25). **The extension of `SEG-1` —
hence of `extract` — is identical to Revision 1 on every element of `U`**:
removal of a never-firing clause is extension-preserving by construction.
No clause of `U`, `D` (beyond the dead text), `P`, or `X` changes; no
surviving theorem is restated; THM-1…THM-9 and THM-FW hold verbatim; the
CF-R2 proof (THM-4), THM-6, THM-7, THM-8, and the CE-7/CE-8/CE-13 closures
are untouched. Revision 1's falsification record is retained permanently
per §23.
**Status:** DRAFT — S1/S2 candidate. This document **authors the semantics of
the candidate-claim boundary and nothing else.** It defines no part of
SUPPORT, MATERIALITY, or TEMPLATE except by declared import/export boundary
(§24). It chooses no L2 value (the E4b Parameter is minted later by the
ScientificAuditor), redesigns no part of T1/PA-3/SAM-1, modifies no ontology
or migration content, writes no code, and touches neither EXP-1 nor G4. The
standing prohibition (`ES1_IMPLEMENTATION_GATE.md`:97-99) is unchanged.
Acceptance of this candidate is **not** self-declared: it requires the
independent stages S3–S5 of SAM-1 §4 (§22–§23 below). Its admissibility at S3
additionally requires that the S0→S1 gate record (`S0-REG-1` §9, GC-1…GC-6,
including hash slots H-1…H-4) holds with timestamps preceding this draft's
submission (SAM-R2); if that record postdates this text, this text re-enters
S1 unchanged in content but re-sequenced in record. **Revision coupling:** the
imports of §24 bind to `sem-support-2026-07-15-r1` by identity; if that
sibling revision is rejected or superseded at any SAM-1 stage, the imported
objects (`NORM-1`, `TOK-1`, `ENT-1`, `UVER`, `supports`) lose their referent
and this candidate re-enters S1 as a new revision against the successor.

---

## 1. Purpose

The Root Cause Analysis established (verdict `C`) that the four deferred ES-1
registers failed audit after audit because their **defining semantics** were
classified as deferred values, leaving the meaning of the candidate-claim
boundary — *what counts as a candidate claim, at what granularity, over what
span, with what identity* — authored by nobody. The migration plan created
the typed slot `SEM-EXTRACTION` (SemanticPredicate, L1, Architect-owned,
ScientificAuditor-approved, scheduled E4a) and SAM-1 fixed the scientific
procedure for filling it.

This document **fills the slot**. It supplies the complete extensional
definition of PA-2's extraction function: the total universe it is quantified
over, the constructive rule that entails exactly one ordered
`CandidateClaims` tuple for every element of that universe, the finite
declared parameter surface left to the L2 value `EXTRACTION_PARAMS`, the
closure of every historical ambiguity axis (CE-7 granularity, CE-8 span,
CE-13 claim identity, v1-b degeneracy), and the written discharge of every
SAM-1 §7.4 proof obligation — including the **discharge by construction of
the §A2 injectivity CONDITIONAL (F2/F2′)**, the standing audit item the
derivation method records at its §5.3. After this definition is approved and
frozen (E4a), `Parameter[SEM-EXTRACTION]` becomes inhabitable and the
derivation method's §5 procedure for `EXTRACTION_PARAMS` becomes executable
to a unique value (E4b) — closing, for this register, the value-selection gap
the method records at its §2.2.

## 2. Authority

| Source | Role here |
|---|---|
| ONT-1 (`PROGRAM_A_ARCHITECTURAL_ONTOLOGY.md`) | Fixed. Supplies class, origin, owner, lifecycle, operations, reference rules (§3–§7). |
| Migration plan (`PROGRAM_A_ONTOLOGY_MIGRATION_PLAN.md`) | Fixed. Declares the `SEM-EXTRACTION` slot, the M5 typing of `EXTRACTION_PARAMS` as `Parameter[SEM-EXTRACTION]`, the M12 precondition on derivation, the M17 E4a/E4b split. |
| SAM-1 (`PROGRAM_A_SEMANTIC_AUTHORING_METHODOLOGY.md`) | Fixed. Governs this document's form (five parts), question set (SQ-EXT-1…11), proof obligations (PO-EXT-1…10), evidence rules (§7.2/§7.3), acceptance/rejection (§7.9/§7.10 via the §5.9/§5.10 schema). |
| `S0-REG-1` (`PROGRAM_A_SEM_S0_PREREGISTRATION.md`) | Consumed by identity. The sealed core battery `S0-PB-1` and joint witnesses `S0-JW-1` were **not read** by this author (SAM-R3 channel discipline); the witnesses exhibited in this document (§7, §8, §13, §19) are author-constructed proof-pack witnesses, disjoint in role and provenance from the sealed battery. |
| T1 (`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md`) §3.1, §5.5, §5.6, §7, §8; addendum §A0–§A7 | Fixed semantic context. Every state definition, precedence rule, seam invariant, contract, tie-break key, and type is preserved verbatim; this definition is constructed to slot into them without entailing any edit (§18; PO-EXT-5/6/7/8). |
| Derivation method (`PROGRAM_A_REGISTER_DERIVATION_METHOD.md`) §2.2, §5 | Fixed. Its evidence classes (E-STRUCT/E-DETERM/E-TYPE/E-PRIOR; E-DEV falsifying-only) are the only argument forms used in `Π`. Its §5.3/§5.4 record of the §A2 injectivity CONDITIONAL is the obligation §14/THM-7 discharges. |
| `PROGRAM_A_SEM_SUPPORT.md` rev `sem-support-2026-07-15-r1` | Sibling L1 candidate, consumed **by declared export only** (its §24): `NORM-1` (NFC @ UVER), `TOK-1` (tokenization), `ENT-1` (entity-token notion), `UVER` (Unicode 16.0.0 pin), and — by L1→L1 acyclic reference — its defining rule for `supports(c, e)` (its §6.3), used solely to fix the `supporting_doc_ids` emission semantics (§6.6 clause C9; J-5). Nothing is redefined; nothing else is consumed (J-1 discipline). |
| Frozen leaf-type contract (addendum §A grounding-types block; realized on disk as `program_a/types.py`) | Fixed. `D` is stated over the **type contract** (an L1 object), never over code (G-8); the module file is its L3 realization and is cited as locator only. |
| RCA; Sonnet audits 1–2 (v1-a…v1-c, CE-4…CE-13); `PROGRAM_A_REGISTER_AUDIT.md`; `PROGRAM_A_FROZEN_REGISTER.md` | **L0 provenance only.** They motivate obligations and probe classes; no clause of `D` is derived *from* them and none of their content acquires semantic authority here. |
| The interim `program_a/mechanism/claim_extraction.py` behavior and defaults | **Explicitly non-evidence of any kind** (REGISTER_AUDIT 5.6; SAM-1 §7.3). Not consulted for any clause. |
| EXP-1 objects (tier→probability mapping, bin boundaries, ECE logic, outcomes, frozen rows, rubrics, families, query styles, adjudicator signals) | **Forbidden. Not consulted at any point** (SAM-1 §0.3; G-7; PO-EXT-9). In particular, no clause of `D` is fitted to any actual EXP-1 query's form or wording (§19.4 SU-EXT-1 records the consequence honestly). |

## 3. Object classification

| Field | Value |
|---|---|
| Identity | `SEM-EXTRACTION`, revision `sem-extraction-2026-07-16-r3` (supersedes `sem-extraction-2026-07-16-r2` — minimality re-audit, extension-preserving removal of inert clauses, header revision note; r2 superseded `sem-extraction-2026-07-15-r1`, rejected at S3 on RC-9) |
| Class | `SemanticPredicate` (ONT-1 §3: "Extensional criterion/relation: e.g. … extraction"), stated constructively as the extraction function it individuates (§5) |
| Origin | L1 (Semantic Specification) |
| Owner / Creator | Architect |
| Approver | ScientificAuditor (scientific/freeze-relevant semantic class, ONT-1 §4) |
| Lifecycle | **drafted** → approved (S5 adjudication under SAM-1 §10) → frozen (S6, at E4a per migration M17) |
| Freeze point | E4a of `PROGRAM_A_G4_EXECUTION_PLAN.md` as split by M17; freeze recorded per ONT-1 §5. This document performs no freeze. |
| Instantiating L2 parameter | `EXTRACTION_PARAMS` (T1 §5.6) — typed `Parameter[SEM-EXTRACTION]` (migration M5); **uninhabited** until this definition is frozen (ONT-1 §6), minted at E4b by the ScientificAuditor. |
| References | L0/L1 only, acyclic (§24; J-6): the frozen type contract, the fixed T1/addendum context, and `SEM-SUPPORT` r1 exports (L1→L1, one direction — `SEM-SUPPORT` §24 imports nothing from this object). No reference to any L2/L3/L4/L5 object as authority. |
| Post-approval change control | Any change is a new revision, never mutation (ONT-1 §5); a post-freeze counterexample is an MF-class event under SAM-1 §11.2. |

## 4. Universe `U`

### 4.1 Declaration

> **U = { (q, S) : q is a `query_text` value — any finite sequence of Unicode
> code points, including the empty sequence — and S is a well-typed
> `EvidenceSet` }.**

where, per the frozen type contract (addendum §A grounding types):

- `EvidenceSet = { items : Tuple[EvidenceItem] }`, any finite tuple (including
  the empty tuple), presented in PA-1's frozen total order
  (`EVIDENCE_ORDERING_KEY`: lexicographic on `(origin_domain, doc_id)`,
  T1 §5.5 — already frozen and consumed here as fixed);
- `EvidenceItem = { doc_id : Str (non-empty), origin_domain : Str (non-empty),
  title : Str, text : Str, snapshot_hash_ref : Str }`, i.e. exactly the
  3-field content schema `{origin_domain, title, text}` plus identity fields.

`Str` means: any finite sequence of Unicode code points (assigned or
unassigned), of any length, including the empty sequence. No well-typed pair
is excluded: **extraction is total over `U`** (PO-EXT-1; THM-2). The
`(query_text, snapshot)` phrasing of SAM-1 SQ-EXT-1 is realized here as
`(q, S)`: the snapshot enters extraction only through the `EvidenceSet` PA-1
produces from it, which is the type PA-2's frozen position in the pipeline
consumes (E-TYPE; the 3-field document schema *is* the snapshot's content
surface, T1 §7.1).

### 4.2 Output type (confirmed)

The output is a well-typed `CandidateClaims` value: an **ordered tuple** of
`CandidateClaim = { claim_text : Str, supporting_doc_ids : Tuple[Str] }`
(frozen types; addendum §A grounding block: "`CandidateClaims.claims` is an
ordered tuple (PA-2 is deterministic)"). Possibly empty. This closes the
output half of SQ-EXT-1 (§16 row X-1).

### 4.3 Exclusions (everything outside scope, stated)

Not in `U`, and extraction is undefined over them by construction: raw
snapshots not yet ordered into an `EvidenceSet` by PA-1 (ordering is PA-1's
frozen duty, not this definition's); `QueryRecord` (extraction is typed below
the level at which `gold_rubric`/`query_family`/`metadata` exist — T1 §8.1;
the cheat channel is unrepresentable in `U`); ill-typed values (empty
`doc_id`/`origin_domain` are rejected by the type contract before extraction
is reachable); any input carrying a `score`, timestamp, or rank field (the
types have none).

### 4.4 Fields consumed and fields ignored (declared)

`D` (§6) reads **exactly**: `q`, and for each item `e ∈ S`: `e.doc_id`,
`e.title`, `e.text`. It reads **none of**: `e.origin_domain`,
`e.snapshot_hash_ref`, the length or aggregate properties of `S` beyond its
items, or any tuple *position* as content. Consequences, declared now:

- `origin_domain` is provenance; it influences nothing in extraction
  (independence-of-origin is `INDEPENDENCE_RELATION`'s domain, applied
  downstream inside `ios`, never here). `doc_id` is consumed **only** to
  populate `supporting_doc_ids` (clause C9) — never as matching content.
- Tuple **order** of `S` is not consumed by any content-determining clause
  (THM-3 proves order invariance of the claim set and of each claim's
  fields); it is likewise not consumed by the output-ordering clause C10,
  which orders by content-derived keys only (§6.7).

## 5. Formal signature

```
extract : Str × EvidenceSet → CandidateClaims
extract(q, S) = (c₁, …, cₙ)   (n ≥ 0, an ordered tuple)
```

| Parameter | Type | Justification |
|---|---|---|
| `q` | `Str` (the `query_text`) | E-TYPE + E-PRIOR: T1 §8.1 fixes the surface's sole lawful query input as `query.query` (a string); PA-2's frozen position consumes exactly it. |
| `S` | `EvidenceSet` | E-TYPE: the PA-1 output type; the only evidence-shaped object in the frozen contract. |
| return | `CandidateClaims` | E-TYPE: addendum §A grounding block fixes the ordered-tuple shape with `{claim_text, supporting_doc_ids}` per claim; the frozen consumers (`ios`, §A1 selection, §A2 keys) take exactly this type. |

The **individuating predicate** this `SemanticPredicate` slot names — "is a
candidate claim of `(q, S)`" — is `c ∈ extract(q, S)`; the constructive
statement of `extract` is the extensionally equivalent (and TRR-evaluable)
form. No other parameter exists: **no** window size, span length, claim-count
cap, similarity threshold, score, seed, or configuration argument — the
function has **zero numeric degrees of freedom** (load-bearing for PO-EXT-9
and for the F-3 axis-descent closure, §19.3).

## 6. Defining rule `D`

### 6.1 Imported instruments (pinned by reference; single-sourced per J-1)

`D` consumes, **by reference to `PROGRAM_A_SEM_SUPPORT.md` r1 §6.1–§6.2/§9
and without restatement or drift** (J-1/J-2 single-sourcing):

- **`UVER`** = Unicode 16.0.0, the pinned version for every NFC, `White_Space`,
  and `General_Category` reference below;
- **`nfc(s)`** — NFC normal form under UVER (`NORM-1`);
- **`rawtoks(s)`, `strip(w)`** — whitespace tokenization and `P*`/`S*`
  edge-stripping (`TOK-1`);
- **`T(s)`** — the entity-token **set** of `s` (`ENT-1`), with `ENT-1`'s
  entity identity;
- **`supports(c, e)`** — the sibling's defining biconditional (its §6.3),
  consumed **only** by clause C9 to define `supporting_doc_ids` (J-5
  coherence by identity).

Per J-1/J-2, the sibling's text is the sole normative source of these five
objects; r2's local restating glosses were extensionally inert and standing
drift liabilities, removed at r3 (§13.1 INERT-6).

One additional deterministic instrument is defined **here** (exported, §24):

- **Sentence segmentation `SEG-1`.** For any Unicode string `s`, `seg(s)` :=
  the set of **units** obtained by splitting `nfc(s)` immediately after
  every occurrence of a code point in the frozen **terminator set**
  `TERM = { U+002E FULL STOP, U+003F QUESTION MARK, U+0021 EXCLAMATION MARK,
  U+3002 IDEOGRAPHIC FULL STOP, U+061F ARABIC QUESTION MARK,
  U+0964 DEVANAGARI DANDA }` that is immediately followed by a code point
  with the `White_Space` property (UVER). Each resulting segment is then
  trimmed of leading/trailing `White_Space` code points; segments that are
  the empty string after trimming are discarded.
  (`k` split points partition `nfc(s)` into `k + 1` segments; `k = 0` gives
  the whole string as the single segment. A terminal `TERM` code point is
  followed by nothing, hence by no `White_Space` code point, and is not a
  split point — the r2 "or by end-of-string" disjunct was proved
  extensionally dead in exactly r1's `Nd`-exception manner and is removed;
  §13.1 INERT-2. Digit-internal periods never split: in `3.14` the `U+002E`
  is followed by `U+0031`, which is not `White_Space` — N-E7.)
  `TERM` is definitional content, pinned inline exactly as the UVER pin is
  (MIN-EXT-2a shows deletion is punished); it is a closed code-point set,
  not a parameter. `seg(s)` is a **set of strings**: no clause of `D`
  consumes unit order or multiplicity (§13.1 INERT-4), and the trim and
  discard sub-clauses are extensional for this exported object itself
  (MIN-EXT-11/-12) — importers receive trimmed, non-empty units.

### 6.2 Core derived quantities

For an input `(q, S) ∈ U`:

1. **Query entity set.** `Q := T(q)` — the entity tokens of the query,
   under the imported `ENT-1`.
2. **Item units.** For each `e ∈ S`:
   `units(e) := seg(e.title) ∪ seg(e.text)` — the units of both content
   fields (set union; both fields are content, mirroring the sibling's C5
   field scope — MIN-EXT-13). The r2 sequence structure (title-first
   concatenation) was consumed by no clause — D1 reads membership only —
   and is removed (§13.1 INERT-4).
3. **Unit entity set.** For a unit `u`: `T(u)` under the imported `ENT-1`.
4. **Anchor test.** A unit `u` is **anchored** to `(q, S)` iff
   `Q ≠ ∅ ∧ Q ⊆ T(u)` (membership under `ENT-1`'s imported entity
   identity; the r2 gloss restating that identity is removed — §13.1
   INERT-7).
5. **Canonical claim text.** For a unit `u`: `ctext(u) := nfc(u)` with every
   maximal run of `White_Space` code points (UVER) replaced by a single
   `U+0020 SPACE` — the whitespace-canonical NFC form. (`u` is already
   NFC and edge-trimmed by `SEG-1`; `ctext` additionally collapses interior
   whitespace so that visually-identical assertions differing only in
   whitespace runs receive identical claim identity — §10.)

### 6.3 The defining rule (constructive)

> **D:  For every `(q, S) ∈ U`, `extract(q, S)` is the ordered tuple
> constructed by steps D1–D3:**
>
> **D1 (candidate units).** Form the set
> `A(q, S) := { ctext(u) : e ∈ S, u ∈ units(e), u is anchored to (q, S) }`
> — the **set of strings** that are canonical texts of anchored units,
> across all items (set-builder: identical canonical texts are one member —
> this is the claim-identity rule, §10).
>
> **D2 (claims).** For each `t ∈ A(q, S)`, the candidate claim is
> `c_t := CandidateClaim( claim_text = t, supporting_doc_ids = ids(t, S) )`
> where
> `ids(t, S) := the tuple of doc_ids of { e ∈ S : supports(c_t′, e) }`,
> `c_t′` being the claim with `claim_text = t` (the `supporting_doc_ids`
> field is not consumed by `supports` — sibling §4.4 — so this is
> well-founded, not circular), ordered by `EVIDENCE_ORDERING_KEY`
> (lexicographic on `(origin_domain, doc_id)`), duplicate `doc_id`s
> collapsed to first occurrence.
>
> **D3 (output order).** The output tuple lists `{ c_t : t ∈ A(q, S) }`
> sorted **ascending by Unicode code-point order of `claim_text`** (the same
> comparison the frozen §A2 tertiary key uses: code-point order over the
> NFC form, which `claim_text` already is by construction). When
> `A(q, S) = ∅` this is the empty tuple `()` — not a clause but the sort of
> the empty set; r2's separate empty-case step D4 restated this corollary
> and is removed (§13.1 INERT-1; totality is THM-2).

In words: a candidate claim of `(q, S)` is **exactly** the
whitespace-canonical NFC text of a sentence-unit of some evidence item that
contains every entity token of the query; each claim carries as
`supporting_doc_ids` exactly the items that support it under the sibling
`supports` predicate; the tuple is ordered by claim text; a query with no
entity tokens yields no claims.

### 6.4 Clause-by-clause rationale (evidence classes cited; SAM-1 §7.2 only)

| Clause | Content | Ground |
|---|---|---|
| C1 | Universe `(q, S)`; output `CandidateClaims` ordered tuple | E-TYPE: the frozen signature of PA-2's position (§4, §5). Closes the universe half of CE-11 at this object's level. |
| C2 | Granularity = sentence-unit (`SEG-1`) | E-STRUCT + E-PRIOR: the unit must be (a) computable by pure text mechanics with no model call (T1 §5.6) and (b) large enough to carry an assertable claim that `SEM-TEMPLATE`'s consumers can attribute, yet (c) small enough that `supports`-relevant content is not diluted across unrelated assertions. Among decidable units expressible over the frozen means (code point, token, line, sentence-unit, whole field, whole document), the sentence-unit is the **unique minimal unit closed under the terminator convention that can carry a complete assertion**: sub-sentence units (tokens, clauses) require a parser no frozen authority licenses (a clause boundary is not decidable from closed code-point sets — the exact CE-7 trap: "clause-level" smuggles an undefined analyzer); super-sentence units (fields, documents) make `claim_text` non-assertional aggregates and destroy the §A2 injectivity argument (two documents differing outside the anchored sentence would still collide or diverge arbitrarily). Sentence-hood via a closed terminator set is the only granularity in the admissible space that is both decidable and assertion-shaped. Closes CE-7 (§16 row X-2). |
| C3 | Span = the whole unit, canonicalized (`ctext`) | E-STRUCT: any sub-unit span rule (minimal span covering `Q`, fixed windows) requires an offset/length parameterization — the exact F-3 axis-descent surface CE-8 exploited — and any super-unit span re-opens C2. The unit itself is the unique span choice with zero free parameters. Maximal-vs-minimal (CE-8) is thereby not resolved by *picking a side* but dissolved: the span is the unit, whole, always. Closes CE-8 (§16 row X-3). |
| C4 | Anchor = `Q ⊆ T(u)`, universal quantifier | E-PRIOR ("entity-level extraction so fabricated-entity probes yield no claim" — T1 §5.6, CF-R2 first line) + E-STRUCT: under `∃` or a designated-subset quantifier, a query containing one genuine and one fabricated entity extracts claims from units carrying only the genuine one, and those claims can then be supported and reach S2/S3 — defeating CF-R2's first line outright (MIN-EXT-4). Under `∀`, a fabricated query entity absent from every unit anchors nothing (THM-4). The universal quantifier is the unique member of the quantifier space under which CF-R2's first line is a theorem — the same forced-choice structure as the sibling's C3. |
| C5 | Anchor guard `Q ≠ ∅` | E-STRUCT (TSC): without it, `Q = ∅` makes `Q ⊆ T(u)` vacuously true and **every** unit of **every** item becomes a claim — an indiscriminate extractor on entity-free queries (empty, whitespace-only, punctuation-only `q`), the degenerate supremum (MIN-EXT-5). The guard makes the definition assert what "entity-level extraction" means: no query entities, no claims. |
| C6 | Entity notion / normalization = imported `ENT-1`/`NORM-1`/`TOK-1` @ `UVER` | E-STRUCT (J-1/J-2): the entity and normalization notions must be the **same objects** `supports` uses, or extraction could emit claims whose entities `supports` cannot see (a per-object-sound, jointly-degenerate seam — the CE-10 pathology). Import by reference makes cross-object drift structurally impossible from this side. |
| C7 | Claim identity = equality of `ctext` (§10); duplicates collapse in `A` | E-DETERM + E-STRUCT: the §A2 tertiary key and `ios` consume claims by `claim_text`; two anchored units with identical canonical text are **the same claim** — collapsing them is what makes cross-document corroboration countable (the same assertion in two independent-origin items becomes one claim with `ios = 2`, making S3 reachable — the CE-13 repair, THM-6) and what makes the output injective in `claim_text` (THM-7, discharging §A2 F2/F2′). |
| C8 | `ctext` = whitespace-collapsed NFC | E-STRUCT: NFC is forced — the §A2 tertiary key is *defined* as "Unicode code-point order over its UTF-8/NFC form," so emitting `claim_text` already in NFC is the unique choice under which the key's comparison equals comparison of the emitted bytes (no second normalization site, no drift surface). Whitespace collapse is forced by C7: without it, two occurrences of the same sentence differing only in a whitespace run (single vs double space, NBSP-free wrap) would be distinct claims, splitting `ios` across identity fragments and re-opening CE-13 on trivial typography (MIN-EXT-8). No further folding (case, NFKC) is admissible: it would make `claim_text` differ from the source text's NFC form, breaking faithful attribution and enlarging the identity relation beyond canonical equivalence with no PO that requires it. |
| C9 | `supporting_doc_ids` = exactly the `supports`-true items, `EVIDENCE_ORDERING_KEY`-ordered, deduplicated | E-STRUCT (J-5): the frozen consumers guarantee coherence only if emission-time and predicate-time support are the **same relation**; defining `ids` *as* the `supports` extension makes J-5 hold by identity rather than by proof of two independently-drafted notions (THM-8). Ordering by the frozen key and deduplicating makes the field a deterministic function of content (E-DETERM). |
| C10 | Output order = ascending code-point order of `claim_text` | E-DETERM: §A2 explicitly refuses to couple replay-safety to PA-2 tuple position, but the frozen type is an ordered tuple, so *some* content-derived total order must be fixed (SQ-EXT-8). Code-point order over `claim_text` is (a) already frozen as the §A2 tertiary comparison — no new comparison notion enters the system — and (b) total and strict on the output because `claim_text` values are pairwise distinct by C7 (THM-7). Any alternative (evidence-position order, length order) either consumes tuple position §A2 refuses or introduces a new comparison object with no PO gain (MIN-EXT-10). |
| C11 | *(removed at r3)* Totality/empty case | **Extensionally inert** (§13.1 INERT-1): the empty output on `Q = ∅` or no anchored unit is a corollary of C4/C5 + D1 + D3 (sort of the empty set), and totality is a theorem (THM-2), not a clause. The identifier is retired, never reused; no clause of `D` corresponds to it. |

### 6.5 What `D` deliberately does not contain

No numeric constant of any kind — no window, cap, threshold, length bound, or
count. No model call, no syntactic parse, no relation/argument-structure
analysis, no coreference (none is licensed; each would smuggle an undefined
analyzer — the CE-7 lesson). No dependence on evidence-tuple position,
`origin_domain`, `snapshot_hash_ref`, item count, or repetition (all
constructions are sets or content-keyed sorts). No reference to any module,
function, file, or interim default (G-8; `claim_extraction.py` behavior is
non-evidence per REGISTER_AUDIT 5.6). No query-text transformation beyond the
imported `ENT-1` pipeline: the query is consumed only as its entity-token set
`Q` (T1 §8.1 read-scope, echoed structurally).

## 7. Positive extension

### 7.1 Necessary and sufficient condition

`c` is a candidate claim of `(q, S)` — i.e. `c ∈ extract(q, S)` — **iff**
there exist `e ∈ S` and `u ∈ units(e)` with `Q ≠ ∅`, `Q ⊆ T(u)`, and
`c.claim_text = ctext(u)`, with `c.supporting_doc_ids = ids(ctext(u), S)`.
This is a biconditional restatement of the constructive D1–D2; nothing else
forces emission.

### 7.2 Exhibited non-empty witness classes (PO-EXT-4 positive side, SQ-EXT-5; TSC)

These are **author proof-pack witnesses** (SAM-1 §1.1 part 5), constructed
synthetically over the frozen types. They are not, and were not derived from,
the sealed S0 battery (§2, `S0-REG-1` row).

- **W+E1 (single-item emission).** `q = "Kestrel Observatory"`;
  `e₁ = { doc_id: "d1", origin_domain: "a.example", title: "Coastal
  landmarks", text: "The Kestrel Observatory opened in 1901. It closed for
  repairs in 1963." }`.
  `Q = {Kestrel, Observatory}`. `seg(e₁.text)` yields two units; unit 1
  ("The Kestrel Observatory opened in 1901.") has
  `T(u) ⊇ {Kestrel, Observatory}` — anchored; unit 2 lacks both — not
  anchored; the title unit lacks both — not anchored.
  **`extract` emits exactly one claim**, `claim_text = "The Kestrel
  Observatory opened in 1901."`, `supporting_doc_ids = ("d1",)` (the item
  supports its own emitted sentence: `E(c) ⊆ V(e₁)` since every token of the
  unit is a token of the field it came from). **Non-empty output is
  entailed.**
- **W+E2 (cross-document identity merge — the CE-13 discriminator).** Same
  `q`; `e₁` as above with `origin_domain: "a.example"`; `e₂ = { doc_id:
  "d2", origin_domain: "b.example", title: "Archive", text: "The Kestrel
  Observatory opened in 1901." }`. Both items yield an anchored unit with
  the **same** `ctext`; D1's set collapse makes them **one claim** with
  `supporting_doc_ids = ("d1", "d2")` (key order: `a.example < b.example`).
  Downstream, `ios = 2` is attainable — S3 is reachable in principle from
  this definition's side (§18.4; THM-6).
- **W+E3 (whitespace/typography robustness).** Same `q`; `e₂.text = "The
  Kestrel  Observatory opened in 1901."` (double space). `ctext` collapses
  the run; the claim merges with W+E1's under C7/C8. **One claim, two
  supporters.**

Class W+E is non-empty and exhibited; therefore the always-empty extractor
(v1-b) is **not a model of `D`** (THM-5): it disagrees with `D` on W+E1.

## 8. Negative extension

### 8.1 Explicit non-member classes (TSC negative side; PO-EXT-4)

Every class below provably yields no claim (or excludes the named unit):

- **N-E1 — Fabricated-query-entity class (CF-R2 first line).**
  `q = "Kestrel Observatory 1930"` against W+E1's `e₁`: token `1930` is in
  `Q` but in no unit's `T(u)` (unit 1 has `1901`; unit 2 has neither name).
  No unit is anchored (C4, universal). **`extract = ()`** — the fabricated
  entity yields no claim, hence nothing exists for `supports` to
  false-positive on from this side (THM-4).
- **N-E2 — Entity-free queries.** Any `q` with `Q = ∅` (empty, whitespace,
  `"???"`): **`extract = ()`** against every `S` (C5: no unit passes the
  guarded anchor test, so `A = ∅` and D3 sorts the empty set).
- **N-E3 — Empty/junk evidence.** `S = ()`, or items whose fields produce no
  units (`seg` of empty/whitespace fields is empty), or units with
  `T(u) ⊉ Q`: no anchored unit, **`()`**.
- **N-E4 — Topically-adjacent-but-unanchored units.** `q = "Kestrel
  Observatory"`, `e.text = "The observatory on the coast opened in 1901."`:
  `Kestrel ∉ T(u)`. Not anchored. (The S0-row class: topically related
  content that mentions no queried entity extracts nothing.)
- **N-E5 — Cross-unit scattering.** `e.text = "The Kestrel is a bird.
  The Observatory opened in 1901."`: unit 1 lacks `Observatory`, unit 2
  lacks `Kestrel`. Neither unit is anchored — entity presence never
  aggregates across units (C2 granularity is load-bearing; this is CE-7's
  discriminating input decided with zero discretion).
- **N-E6 — Case/normalization non-identity.** `q = "NASA"` vs unit
  `"Nasa launched the probe."`: `NASA ≠ Nasa` under NFC-exact `ENT-1`. Not
  anchored (imported C6; deliberate — sibling §9.3 strictness direction).
- **N-E7 — Digit-internal period non-split.** `e.text = "Version 3.14 of
  the Kestrel Observatory catalog appeared."` is **one** unit: the `U+002E`
  inside `"3.14"` is followed by `U+0031 DIGIT ONE`, which does not have
  the `White_Space` property, so SEG-1's split condition does not fire
  there. With `q = "Kestrel Observatory"` the sentence is anchored whole —
  `"3.14"` does not fragment it into two unanchored halves. (This behavior
  is entailed by the split condition itself; no exception clause exists or
  is needed — see header revision notes r1→r2 and r2→r3.)

### 8.2 No implicit exclusions

`D` is constructive: the output is **exactly** the D1–D3 construction.
There is no case decided by convention, precedence, or reader judgment
outside the stated steps; N-E1–N-E7 are illustrative partitions of the
complement, not an enumeration that could be incomplete.

## 9. Normalization

Wholly **imported** (C6; J-2): `NORM-1` (NFC @ UVER = Unicode 16.0.0, no case
folding, no NFKC, no diacritic stripping beyond canonical equivalence, no
stemming/synonymy), `TOK-1`, `ENT-1` — by reference to
`PROGRAM_A_SEM_SUPPORT.md` r1 §6.1–§6.2/§9, verbatim, with no local
restatement that could drift. The **only** normalization this object adds is
`ctext`'s whitespace-run collapse (C8), which applies to emitted `claim_text`
only — never to matching (anchor tests and `supports` consume token sets,
which are whitespace-insensitive already). Direction of residual strictness:
identical to the sibling's §9.3 — every declined folding can only suppress
extraction, never fabricate it; the definition errs exclusively toward
emitting less, i.e. toward S0, the FM-1-safe direction.

## 10. Identity

- **Claim identity (SQ-EXT-4).** Two candidate claims are **the same claim**
  iff their `claim_text` values are equal as code-point sequences. Since
  `claim_text = ctext(u)` is whitespace-canonical NFC, identity is invariant
  under canonical re-encoding and whitespace-run variation of the source
  unit, and under *which* document or replay produced it — identity is a
  pure function of content (THM-1). Within one output tuple, identity
  coincides with distinctness of `claim_text` (C7 collapse; THM-7). Across
  runs and replays: identical `(q, S)` content yields the identical claim
  set (THM-1), and the same assertion appearing in different documents of
  one snapshot is **one** claim (W+E2) — which is precisely what makes
  `ios(c) ≥ 2`, the §A2 keys, and §A1 selection consume well-defined
  objects (THM-6; the CE-13 pathology "`Σ≠∅` but S3 permanently
  unreachable" via identity fragmentation is not admissible against `D`).
- **Entity identity.** Imported: NFC code-point identity (`ENT-1`), single-
  sourced (J-1).
- **Unit identity.** Units have no identity beyond their occurrence; only
  their `ctext` survives into the output (units are scaffolding of the
  construction, not objects of the ontology).

## 11. Order invariance (permutation proof)

**Theorem (THM-3).** Let `S = (e₁, …, eₙ)` and let `π` be any permutation of
`{1..n}`, `S′ = π(S)`. Then for every `q`: `extract(q, S) = extract(q, S′)`
**as a tuple** (element-wise identical, same order).

*Proof.* (i) `A(q, S)` is a set built from per-item quantities
(`units(e)`, anchor tests) with no positional term (§6.2–§6.3 mention no
index or neighbor); a permutation re-orders the union's presentation, not
its members: `A(q, S) = A(q, S′)`. (ii) For each `t ∈ A`,
`ids(t, S)` is the `EVIDENCE_ORDERING_KEY`-sorted tuple over the **set**
`{ e : supports(c_t, e) }` — `supports` is per-pair and
permutation-invariant (sibling THM-3), and a sort over a set is
presentation-independent: `ids(t, S) = ids(t, S′)`. (iii) D3 sorts the
claims by `claim_text`, a content key. All three components agree; the
tuples are identical. ∎

Corollary: extraction is stable under the frozen `EVIDENCE_ORDERING_KEY`
re-ordering in particular, and every downstream frozen quantity (`ios`, `Σ`,
the `≺` keys, §A3 cascade inputs) receives permutation-invariant input
(PO-EXT-8 discharged with THM-1; G-6).

## 12. Determinism proof

**Theorem (THM-1).** `extract` as defined by `D` is a total function
`U → CandidateClaims` depending only on the code-point sequences
`(q, (e.doc_id, e.origin_domain, e.title, e.text) for e ∈ S)` — with
`origin_domain` entering only through the `ids` sort key and `doc_id` only
through `ids` membership/keys.

*Proof.* `D` is the composition of: the imported `nfc`/`rawtoks`/`strip`/
qualification pipeline (deterministic and total — sibling THM-1's proof,
consumed by reference); `seg` (splitting against the closed `TERM` set and
the fixed `White_Space` property — unique decomposition per string);
the anchor test (finite-set inclusion — decidable, unique); `ctext`
(whitespace-run collapse — unique); set construction and duplicate collapse
(unique on finite sets); `supports` (a total deterministic function —
sibling THM-1); and two sorts under total orders (`EVIDENCE_ORDERING_KEY`
is a total order on well-typed items since `(origin_domain, doc_id)` pairs
are compared lexicographically; code-point order is total on distinct
strings, and D3's inputs are pairwise distinct by C7). No step consults
randomness, a model, wall-clock, environment, network, mutable store, seed,
or iteration order of an unordered container. Composition of total
deterministic functions is total and deterministic. ∎

Corollaries: byte-identical replay across the 22 seeds is preserved
(`extract` never reads `seed` or anything the replay contract varies —
T1 §7.2); the C1 sentinel-substitution property is preserved
(`gold_rubric`/`query_family`/metadata are unrepresentable in `U`, T1 §8.1).
(PO-EXT-2 discharged; G-1, G-6 contribution.)

## 13. Minimality proof (clause-deletion test)

Per SAM-1 §3.6, and per the discipline r1's RC-9 failure made mandatory,
this section records a **complete** internal deletion audit performed
*before* this revision was authored: every normative sub-clause of `D` —
the full §6.1–§6.3 inventory, not only the C-row summaries — was removed in
turn and the removal tested against (i) the extension of `extract` on `U`,
(ii) determinism (THM-1), (iii) totality (THM-2), (iv) unique extension
(UE/TRR, PO-EXT-3), and (v) the remaining accepted obligations (PO-EXT-5
typing; J-1/J-2/J-5; the §24 export identities, which are themselves
frozen-surface obligations). A clause whose removal changes none of these
is **extensionally inert** and is removed by this revision (§13.1). Every
surviving clause carries a genuine deletion witness (§13.2). No clause
survives solely because it documents behavior already entailed by other
clauses.

### 13.1 Clauses found extensionally inert at r2 (removed here)

| # | r2 clause removed | Inertness proof (extension unchanged on every input) |
|---|---|---|
| INERT-1 | **D4 (empty case)** and its C-row **C11** | The guard `Q ≠ ∅` is a conjunct of the anchor test (§6.2 item 4), so under `Q = ∅` no unit is anchored and D1 gives `A = ∅` directly; likewise when no unit is anchored. D2 over `∅` yields no claims; D3's sort of the empty set is `()`. Both branches of D4 restated this corollary; totality is carried by THM-2, determinism by THM-1, and neither cites D4 as a premise after repair. Removal changes no output, no proof obligation, no export. |
| INERT-2 | **SEG-1's "or by end-of-string" disjunct** | A split point at the absolute end of `nfc(s)` partitions the string into ⟨whole string, empty suffix⟩; the empty suffix trims to `""` and the discard clause removes it, so the unit set equals the no-split unit set. Exhaustive case check: `"A."` → {"A."} under both readings (with the disjunct: split → segments "A.", "" → discard ""; without: zero split points → whole string, trimmed); `"A. B."` → {"A.", "B."} both ways; `"a.b."` → {"a.b."} both ways; `""` and whitespace-only → ∅ both ways. The disjunct's firing region (terminal `TERM` occurrence) and the region where firing could change the unit set are disjoint — the identical death mechanism as r1's `Nd` exception (RC-9). Its r2 witness (part of MIN-EXT-2) claimed the *whole* follow-context condition; the genuine witness attaches only to the `White_Space` conjunct (now MIN-EXT-2b). |
| INERT-3 | **SEG-1's zero-split fallback sentence** ("If `nfc(s)` contains no split point, `seg(s)` is the single trimmed unit…") | `k` split points partition a string into `k + 1` segments; `k = 0` gives the whole string as the sole segment, then trim/discard apply as everywhere. The sentence restated the general construction's `k = 0` instance; no reading of the remaining text makes `seg` undefined or different there (UE unchanged: both readers compute the `k = 0` case from the same partition rule). |
| INERT-4 | **`units(e)` sequence structure** (title-first `⧺`, order, multiplicity) | D1 is the sole consumer of `units(e)` and consumes membership only (a set comprehension over per-unit predicates); no clause of `D` reads a unit's index, neighbor, or multiplicity, and identical canonical texts collapse in `A` regardless of how often they occur. Replacing the sequence by the set `seg(e.title) ∪ seg(e.text)` provably changes no value of `A(q, S)`, hence no output. (Field *scope* — title and text both in, other fields out — is NOT inert: MIN-EXT-13.) |
| INERT-5 | **D1's second sentence** ("Duplicates collapse: `A` is a set of strings") | Restated D1's own set-builder notation; the collapse is carried by `A` being a set (that clause is witnessed — MIN-EXT-7), the sentence merely documented it. Folded into D1's formula gloss. |
| INERT-6 | **Restating glosses in §6.1** (the parenthetical restatement of the `supports` biconditional; the `T(s)` construction restatement; "entity identity = NFC code-point-sequence equality") | The imports are consumed **by reference and by revision identity** (J-1/J-2); the sibling's text is the sole normative source, so a local restatement can never be load-bearing — if it agrees it is redundant, if it drifts it is a J-2 violation. Removal changes nothing; retention was a standing drift liability. §6.1 now names each import and its consuming clause only. |
| INERT-7 | **Explanatory parentheticals inside D2/D3 and §6.2 item 4's "as an NFC-exact token" gloss** | Each restates content whose normative source is elsewhere (sibling §4.4 well-foundedness; §A2's frozen comparison; `ENT-1`'s identity). Where the content is proof, it now lives in `Π` (§12, §14.2, §18.2); where it was duplicate normativity, it is deleted. Extension, determinism, UE unchanged — the defining text shrinks, the proof pack does not. |

**Extension-preservation theorem (r2 → r3).** Each INERT-1…7 removal is
proved above to fix every value of `extract` on every `(q, S) ∈ U` and every
value of the §24 exports (`SEG-1`'s unit set is unchanged by INERT-2/-3;
`CLM-1`, `IDENT-1`, `ORD-EXT-1` are untouched). Composition of
extension-preserving edits is extension-preserving; hence `extract` under r3
equals `extract` under r2 on all of `U`. ∎ (This is the same argument form
as the r1→r2 note, now carried for six clauses instead of one.)

### 13.2 Surviving clauses — complete witness inventory

Every row names the failure of a **stated obligation** — extension
(a concrete input whose output changes), determinism, totality, UE, typing,
or a J-row/export identity — never mere documentation value. Rows marked ⊕
are witness gaps that existed at r2 (clauses that had survived without a
recorded witness) and are closed here.

| # | Clause deleted / weakened | Punishment (witness) | Obligation hit |
|---|---|---|---|
| ⊕ MIN-EXT-0 | C1 (universe/output typing) deleted | `extract`'s domain and codomain are no longer the frozen `Str × EvidenceSet → CandidateClaims`; the frozen consumers (`ios`, §A1, §A2 keys) receive an untyped object; PO-EXT-5 undischargeable. | Typing (PO-EXT-5); totality has no carrier set. |
| MIN-EXT-1 | C2 granularity replaced by "clause-level" or any sub-sentence unit | No closed decidable rule individuates clauses over the frozen means; two readers segment `"The Kestrel Observatory, which opened in 1901, closed in 1963"` differently — TRR divergence on a well-typed input; CE-7 reopens verbatim. | UE (PO-EXT-3). |
| MIN-EXT-2a | `TERM` pin deleted from SEG-1 | Two readers using different terminator conventions (one includes `U+061F`, one does not) segment Arabic-question probes differently — TRR divergence. | UE (PO-EXT-3). |
| MIN-EXT-2b | The `White_Space` follow-context conjunct deleted (every `TERM` occurrence splits unconditionally) | N-E7's unit fragments at the `U+002E` inside `"3.14"`; the entity token `3.14` survives in **neither** fragment (edge-stripping of `"3."`/`"14"` yields `3` and `14`, neither NFC-equal to `3.14`), so `q = "Kestrel Observatory 3.14"` — anchored against the whole unit — anchors neither fragment: **extension changes** (a claim emitted under `D` is not emitted under `D − clause`), an unforced positive-class collapse with no compensating PO. *(The r2 "or end-of-string" disjunct is NOT part of this witness — INERT-2.)* | Extension. |
| MIN-EXT-3 | C3 span narrowed to "minimal span covering `Q`" | A span offset/length freedom appears with no frozen rule to fix it (which minimal span when `Q`'s tokens occur twice?) — CE-8 multiplicity returns as F-3 axis descent. | UE (PO-EXT-3). |
| MIN-EXT-4 | C4 `⊆` weakened to `∃` | `q = "Kestrel Observatory 1930"` anchors W+E1's unit 1 via `Kestrel`; the emitted claim is then supported — CF-R2's first line fails as a theorem (THM-4 false). **Extension changes** on N-E1. | Extension + PO-EXT-4. |
| MIN-EXT-5 | C5 guard `Q ≠ ∅` deleted | Empty query anchors every unit of every item (vacuous `⊆`): **extension changes** (N-E2 emits everything); degenerate supremum, TSC violated. | Extension + TSC. |
| MIN-EXT-6 | C6 imports replaced by locally-restated normalization | Two normalization sites can drift; a J-2 divergence becomes expressible (extraction emits tokens `supports` cannot match) — the CE-10 seam pathology becomes admissible. *(Honest ground: this clause's witness is the J-1/J-2 obligation, not the current extension — with today's sibling text a faithful restatement is extensionally identical; the clause survives because the restated form makes future incoherence expressible, which J-1 exists to forbid.)* | J-1/J-2. |
| MIN-EXT-7 | C7 duplicate collapse deleted (`A` a multiset / one claim per occurrence) | W+E2's two occurrences are two claims, each `ios = 1`: **extension changes**; corroboration fragments (CE-13 reconstructed); `claim_text` collisions defeat D3's strict order (THM-7 fails, §A2 F2/F2′ reopens). | Extension + PO-EXT-6/7. |
| MIN-EXT-8 | C8 whitespace collapse deleted from `ctext` | W+E3's double-space variant no longer merges with W+E1's claim: **extension changes** (two claims instead of one, `ios` shaved); D3 tie surface reappears on visually-identical texts. | Extension + PO-EXT-7. |
| MIN-EXT-9 | C9 replaced by an independent emission-time notion (e.g. source-item-only) | Emission-time and predicate-time support diverge by construction; on W+E2, source-item-only `ids` lists one of two supporters — **extension changes** (the `supporting_doc_ids` field differs) and J-5 coherence-by-identity (THM-8) is lost. | Extension + J-5. |
| MIN-EXT-10 | C10 order replaced by evidence-position order | Output order consumes tuple position — §A2's refusal violated; order becomes `S`-permutation-sensitive, THM-3's tuple-identity conclusion fails. **Extension changes** (the output *tuple* differs under permutation). | Extension (tuple) + PO-EXT-8. |
| ⊕ MIN-EXT-11 | SEG-1's trim sub-clause deleted | Split segments retain their post-terminator leading `White_Space` (e.g. unit 2 of W+E1's text becomes `" It closed for repairs in 1963."`); `ctext` collapses interior runs but does not delete a leading run, so **`claim_text` bytes change** on any anchored non-initial unit — extension changes, and the emitted text is no longer the §A2-comparable canonical form. Also extensional for the exported `SEG-1` itself. | Extension + export identity. |
| ⊕ MIN-EXT-12 | SEG-1's empty-unit discard deleted | **Inert for `extract`** (an empty unit has `T(u) = ∅ ⊉ Q` whenever `Q ≠ ∅`, so it never anchors; with `Q = ∅` nothing anchors anyway — C5): the clause survives **solely on the export ground**: `seg` is exported (§24), and without discard `seg("Hi. ")` = {"Hi.", ""} instead of {"Hi."} — the exported object's extension changes, and importers (J-3 witness construction, `SEM-TEMPLATE`) would receive empty units. Recorded honestly as export-witnessed, not extract-witnessed. | Export identity (§24 / J-1 registry). |
| ⊕ MIN-EXT-13 | `units(e)` field scope narrowed to `text` only (title dropped) | `q = "Kestrel Observatory"`, `e = {title: "The Kestrel Observatory opened in 1901.", text: "…unrelated…"}`: under `D` the title unit anchors and a claim is emitted; under the narrowed clause, none — **extension changes**. (Widening to `doc_id`/`origin_domain`/`snapshot_hash_ref` is excluded by §4.4's read-scope declaration and MIN-EXT-14.) | Extension. |
| ⊕ MIN-EXT-14 | §4.4 read-scope clause deleted (fields-consumed declaration) | `D`'s clauses nowhere read the excluded fields, so today's extension is unchanged — but the declaration is what makes the C1-sentinel and firewall arguments (§12 corollaries, THM-FW) *checkable by inspection* and what MIN-EXT-13's "widening" arm appeals to. Survives as a proof-obligation carrier (PO-EXT-9, THM-FW premise), recorded honestly: its witness is an obligation, not an input. | PO-EXT-9 / THM-FW premise. |
| ⊕ MIN-EXT-15 | D2's `EVIDENCE_ORDERING_KEY` ordering of `ids` deleted (any presentation) | `ids(t, S)` is no longer a function of content: on W+E2, `("d1","d2")` and `("d2","d1")` are both admissible — **determinism fails** (THM-1) and TRR cannot be tuple-exact. | Determinism + UE. |
| ⊕ MIN-EXT-16 | D2's duplicate-`doc_id` collapse-to-first deleted | `U` does not forbid two items sharing a `doc_id` (the type contract requires non-empty, not unique). With `S` containing `(origin_domain: "a.example", doc_id: "d1")` and `(origin_domain: "b.example", doc_id: "d1")` both supporting `t`: without collapse, `ids` lists `"d1"` twice — **extension changes** (the field's value differs); with collapse-to-*last* instead, the key-order interleaving `("a","d1"),("a","d2"),("b","d1")` yields `("d2","d1")` vs first-occurrence `("d1","d2")` — the tie-break direction is itself extensional. | Extension + determinism. |
| ⊕ MIN-EXT-17 | `nfc` as `seg`'s domain deleted (segment the raw string) | **Inert for `extract`** on the anchor/identity path (`T(·)` and `ctext` re-apply `nfc` regardless, and no `TERM` or `White_Space` code point participates in a canonical (de)composition under UVER that would move a split point across the anchor test's token boundaries — checked against UVER's composition exclusions): survives **on the export and J-2 grounds**: the exported `SEG-1` would emit non-NFC unit strings, breaking `CLM-1`'s "already NFC" premise chain (§6.2 item 5's "u is already NFC" would be false) and forcing every importer to re-derive normalization — the J-2 single-normalization-site discipline. Export-witnessed. | Export identity + J-2. |

`P` minimality (SAM-1 §5.6 via §7.6): `P` contains no slot whose admissible
set could be collapsed by an available argument and was not — both slots are
already collapsed to singleton/inert (§14.3, PO-EXT-10). Nothing in `D` is
decorative: every surviving sub-clause is witnessed above, three of them
(MIN-EXT-6, -12, -14, -17) on explicitly-named non-extension obligations
rather than by extension change — recorded as such so no witness overstates
its ground (the r1 RC-9 failure mode). Per SAM-1 §7.6's
boundary/span/identity stricture: no typographic micro-rule appears in `D`
beyond those carrying a witness (the `TERM` set: MIN-EXT-2a; the
`White_Space` conjunct: MIN-EXT-2b; trim: MIN-EXT-11; discard: MIN-EXT-12
export-side).

## 14. Uniqueness of extension (SAM-1 UE criterion)

### 14.1 Claim

> For every element of `U`, the frozen text of `D` (plus the frozen type
> contract, the pinned UVER data, and the imported `SEM-SUPPORT` r1 exports)
> entails exactly one output tuple, derivable by a competent reader with
> zero discretion.

### 14.2 Argument (PO-EXT-3, written discharge)

- **A1 (closed vocabulary).** The operative terms are: the imported
  `nfc`/`White_Space`/`General_Category`/token machinery (UVER-mechanical,
  sibling A1); the closed code-point set `TERM` with its `White_Space`
  follow-context conjunct (table-decidable); string splitting/trimming;
  finite-set
  construction, `⊆`, `∪`, `∅`; the imported `supports` biconditional; and
  two total-order sorts over already-frozen comparisons. No open predicate
  — "sentence" is *defined* (SEG-1), "claim" is *constructed* (D1–D2),
  "same claim" is *defined* (C7/§10). No term of the form "assertion,"
  "clause," "relevant," or "about" survives into `D`.
- **A2 (granularity uniquely fixed, not merely stipulated).** Within the
  admissible design space (decidable units over closed code-point sets),
  C2's rationale shows every rival unit either requires an unlicensed
  analyzer (sub-sentence) or breaks assertion-shape and identity obligations
  (super-sentence) — the choice is entailed by the obligations, not
  preferred (§6.4 C2).
- **A3 (span and quantifier forced).** C3 by the zero-parameter argument
  (any sub-unit span rule introduces an offset freedom `D` would then have
  to fix — MIN-EXT-3); C4 by CF-R2-as-theorem (MIN-EXT-4). Forced choices
  admit no reading variance.
- **A4 (identity and order forced).** C7/C8 by the CE-13/injectivity
  obligations (MIN-EXT-7/8); C10 by §A2's position-refusal plus
  no-new-comparison (MIN-EXT-10). The output tuple's membership *and* order
  are both content-entailed.
- **A5 (no hidden level).** The regress descended value → function →
  predicate → parameterisation. `D` has no parameterisation level to descend
  to: zero numeric constants, zero thresholds, zero unpinned external
  references — segmentation detail is pinned to the inline `TERM` set,
  normalization to the imported UVER pin, ordering to two already-frozen
  comparisons (§19.3).

Two type-conformant readings of `D` could therefore disagree only by
computing a UVER-mechanical or set-theoretic step differently, which is a
computation error, not a reading. UE is argued; it remains, per SAM-1,
**tested** by TRR (§15) and never self-certified (G-4).

### 14.3 Uniqueness handoff (UHO) — the parameter surface `P`

`P` — the complete, finite, typed list of degrees of freedom left to the L2
value `EXTRACTION_PARAMS` — has exactly two slots:

| Slot | Content | Admissible set | UHO mode | Selection ground |
|---|---|---|---|---|
| P-EXT-1 | The extraction constant record: `(SEG = SEG-1 with TERM as pinned; ANCHOR = universal Q ⊆ T(u) with guard Q ≠ ∅; UNIT-SPAN = whole unit; CANON = ctext (whitespace-collapsed NFC); IDENTITY = claim_text equality with duplicate collapse; IDS = supports-extension, EVIDENCE_ORDERING_KEY-sorted, deduplicated; OUTPUT-ORDER = code-point ascending on claim_text; NORM/TOK/ENT = imported NORM-1/TOK-1/ENT-1 @ UVER)` | **Singleton** — each component is entailed by a clause of `D` (§6.4); distinct members do not exist. | **UHO-a** (transcription-shaped; the `EVIDENCE_ORDERING_KEY` pattern) | E-STRUCT: transcription of `D`. E4b authors the Parameter by copying, exactly as derivation-method §8 step 2 requires. |
| P-EXT-2 | The concrete byte-level serialization of P-EXT-1 inside `constants.py` (key names, ordering, quoting) as digest input | All serializations denoting the P-EXT-1 record | **UHO-b** — provably extensionally inert: no consumer of `extract` reads the serialization; only `frozen_constants_digest()` hashes it, and the digest requires *some one* fixed byte form, any of which yields a valid tripwire (T1 §6.1). | E-PRIOR identity convention: the existing `constants.py` transcription convention (the `SPEC_VERSION`-class pattern), pinned by the ReleaseManager's verbatim-transcription rule (derivation-method §8 step 2). |

No third slot exists. In particular there is **no** semantic freedom left to
the value layer: the root-cause defect ("undefined semantics filed as a
deferred value") is not expressible against this `P` (SAM-1 §3.5;
PO-EXT-10 discharged). This also discharges, for this register, the
derivation method's recorded §2.2 insufficiency: E4b now holds a selecting
ground for every surviving freedom (SAM-1 A-7).

## 15. Two-reader reproducibility (TRR obligations)

Per SAM-1 §3.2, this candidate binds itself to the following, and is
**falsified** by any breach:

1. Two readers, independent of this author and of each other, receive only:
   this document's `(U, D, P, X)` (§§4–6, 14.3, 16), the frozen type
   contract, the imported-export sections of `SEM-SUPPORT` r1 (its §6.1,
   §6.2, §6.3, §9, §24 — the referents of §6.1's imports), and the probe
   battery (`S0-PB-1` core + the S4 adversarial extension). They do **not**
   receive `Π` (§§10–14, 17–21), author intent, or each other's answers.
2. For each probe they hand-evaluate `D`: normalize, segment (against the
   printed `TERM` set), test anchors, canonicalize, collapse, compute `ids`
   by hand-evaluating the imported `supports` biconditional, sort — every
   step executable by hand with the UVER data tables (G-8: no
   implementation required). The required agreement is **tuple-exact**:
   same claims, same `claim_text` bytes, same `supporting_doc_ids` tuples,
   same order (SAM-1 §7.4 PO-EXT-3: "two readers extract identical ordered
   tuples on every probe").
3. Any divergence, or any `UNDERDETERMINED` (with the ambiguous term named),
   **falsifies this candidate** (SAM-1 §3.2 step 4; rejection ground R-3).
4. Agreement over the full battery is necessary-but-not-sufficient: it feeds
   S3/S4; acceptance further requires §22 in full. Post-acceptance
   divergence on any well-typed input is an MF-1 event (SAM-1 §11.2).

`D` was constructed for hand-evaluability: every probe evaluation terminates
in a number of steps linear in input length, with no search, backtracking,
or judgment call.

## 16. Axis closure (`X`)

Every registered scientific question (SAM-1 §7.1, registered unmodified by
`S0-QS-1` as `QS-EXT`, 11 rows) is answered by citation into `D` or `P`. No
row is empty; no row is answered by prohibition alone.

| Row | Question (SQ) | Closed by |
|---|---|---|
| X-1 | SQ-EXT-1 — universe; output type | §4.1 (U total over `Str × EvidenceSet`); §4.2 (frozen ordered `CandidateClaims` tuple, confirmed). |
| X-2 | SQ-EXT-2 — granularity | §6.1 SEG-1 + §6.4 C2: sentence-unit over the closed `TERM` set; sub-/super-sentence rivals excluded by obligation, not preference. Closes CE-7. |
| X-3 | SQ-EXT-3 — span rule | §6.4 C3: the whole unit, canonicalized; zero-parameter span (the CE-8 dichotomy dissolved, not adjudicated). Closes CE-8. |
| X-4 | SQ-EXT-4 — claim identity; `ios` well-definedness; S3 reachability in principle | §10 + §6.4 C7/C8 (identity = canonical-text equality; duplicate collapse); THM-6 (cross-document merge makes `ios ≥ 2` attainable); THM-1 (replay-stable). Closes CE-13 from this object's side. |
| X-5 | SQ-EXT-5 — what forces non-empty output | §7 (positive condition + exhibited class W+E1–W+E3). Excludes v1-b structurally (TSC; THM-5). |
| X-6 | SQ-EXT-6 — `claim_text` construction; §A2 tertiary-key validity | §6.2 item 5 / §6.4 C8: `claim_text` is emitted already in whitespace-canonical NFC (imported `NORM-1` @ UVER), so the §A2 tertiary key's "code-point order over its UTF-8/NFC form" compares the emitted bytes themselves — the key is a valid total-order tie-breaker with no second normalization site (§18.2). |
| X-7 | SQ-EXT-7 — `claim_text` distinctness (§A2 injectivity F2/F2′) | **Discharged, not left open:** THM-7 — distinct claims in any output have distinct `claim_text` **by construction** (C7 collapse makes `claim_text` the identity key). The CONDITIONAL is closed; §18.4 records the closure for the derivation method's §5.3/§5.4 audit item. |
| X-8 | SQ-EXT-8 — tuple order from content alone | §6.4 C10: ascending code-point order of `claim_text` — content-derived, position-free (honors §A2's refusal), strict by THM-7. |
| X-9 | SQ-EXT-9 — entity notion; single-sourcing | §6.1: imported `ENT-1`/`TOK-1`/`NORM-1`/`UVER` from `SEM-SUPPORT` r1 by reference — one owner, this object an importer (J-1 registry, §24). |
| X-10 | SQ-EXT-10 — `supporting_doc_ids` emission semantics; coherence with `supports` | §6.4 C9: defined **as** the `supports` extension, key-ordered — coherence by identity (THM-8; J-5 contribution). |
| X-11 | SQ-EXT-11 — degrees of freedom left to `EXTRACTION_PARAMS` | §14.3: two slots, P-EXT-1 singleton (UHO-a), P-EXT-2 inert (UHO-b). No semantic freedom survives. |

RCA §6 axis coverage for completeness: **granularity** (X-2), **span** (X-3),
**scope/corpus of quantification** (X-1: `U` declared and total; the
operational-corpus question CE-11 is additionally owned by J-3's declared
quantification space at S4), **normalization** (X-6/X-9, imported),
**quantifier** (the anchor quantifier, §6.4 C4 — closed inside X-2's
construction), **composition** (owned by the S4 joint round; this object's
contributions are §18.4 and THM-6/THM-8), **discourse level** (owned by
`SEM-TEMPLATE`). Per SAM-1 §3.3, this table is a floor; the open-ended
residue is owned by UE/TRR, not by this enumeration.

## 17. Historical replay

Why every historical failure targeting this register is impossible against
this definition:

### 17.1 Finding 1 (v1-b: always-empty extractor admissible)

v1-b existed because the constraint layer was all-prohibition: nothing
forced extraction to emit. `D` is constructive with an exhibited non-empty
positive class (§7.2): the always-empty extractor disagrees with `D` on
W+E1 and is **not a model of `D`** — excluded by the definition itself, not
by audit vigilance (PO-EXT-4; TSC; THM-5). *(v1-a and v1-c target support
and templates; their closure is owed by `SEM-SUPPORT` — already discharged
in r1 §17.1 — and `SEM-TEMPLATE`.)*

### 17.2 Finding 2 (CE-7, CE-8, CE-13 — the extraction counterexamples)

- **CE-7 (sentence- vs clause-level boundary).** Two non-equivalent
  granularities were equally licensed. Now: the unit is SEG-1, a closed
  decidable rule; "clause-level" is not a rival reading but an inadmissible
  candidate (it requires an unlicensed analyzer — §6.4 C2, MIN-EXT-1). The
  N-E5 witness decides the discriminating input with zero discretion.
  **Both readings can no longer coexist.**
- **CE-8 (maximal- vs minimal-span).** Now: the span *is* the unit (C3);
  there is no span parameter for the dichotomy to inhabit (MIN-EXT-3).
  **The span rule is written, and parameter-free.**
- **CE-13 (`Σ≠∅` extractor that permanently forbids S3).** The pathology
  required claim-identity fragmentation: the same assertion extracted as
  distinct claims per document, each `ios = 1` forever. Now: C7/C8 merge
  identical canonical texts across documents into one claim (W+E2), so
  multi-origin corroboration accrues to a single identity; THM-6 exhibits
  `ios = 2` attainability. A `D`-conformant extractor cannot fragment
  identity — the fragmenting extractor disagrees with `D` on W+E2.
  **The pathology is not a model of `D`.**

CE-10/CE-11 (compositional, corpus-scope) are, per SAM-1 §9 and the RCA
(§4.3), owned by the S4 joint round over `S0-JW-1`; this definition's
enabling contributions are stated in §18.4. CE-4/CE-5/CE-6 were closed by
`SEM-SUPPORT` r1 §17.2; CE-12 is owed by `SEM-MATERIALITY`; CE-9 by
`SEM-TEMPLATE`.

### 17.3 Root Cause (`C` — the misplaced abstraction boundary)

The defect: the candidate-claim boundary's semantics filed as "exact
parameters fixed at G4," authored by nobody. This document **is** that
layer-4 content, on the specification side: a declared universe, a
constructive two-sided rule with positive emission clauses, identity
individuated by construction. The regress engine is removed for this
register point by point (SAM-1 §12): the layer is authored (this text);
two-sidedness holds by construction (§7/§8); no selector exists or is
needed — the register is *defined* and its value layer is transcription
(§14.3); and there is no meta-level left to relocate undefinedness into
(§14.2 A5).

### 17.4 SAM-1 (the methodology's own bar)

This candidate is the five-part object SAM-1 §1.1 demands — `U` (§4), `D`
(§6), `P` (§14.3), `X` (§16), `Π` (§§10–14, 17–21) — satisfies TSC (§7/§8),
carries a MIN witness per clause (§13), discharges UHO per slot (§14.3),
and binds itself to TRR falsification (§15) and to the S3–S5 stages it
cannot perform for itself (§22–§23). No SAM-1 instrument is weakened,
reinterpreted, or bypassed.

## 18. Compatibility

### 18.1 T1 (mechanism preregistration)

- **§5.6 register row:** "pure text mechanics, no model calls, no
  randomness" ✓ (THM-1: no model call, no random term exists in `D`);
  "entity-level extraction so fabricated-entity probes yield no claim
  (CF-R2 first line)" ✓ (C4/C5; THM-4 — now a theorem); "no probability
  numbers" ✓ (zero numeric content of any kind).
- **§3.1 S0 row:** preserved — a query whose entities appear nowhere
  extracts nothing (N-E1/N-E4), so `Σ = ∅` and S0 fires by the frozen §A3
  cascade; `D` neither widens nor narrows any state boundary (it decides
  only *which claims exist* for the frozen rules to classify).
- **§7.2 replay / §8 input restriction:** preserved (THM-1 corollaries,
  §12): no seed, no wall-clock, no rubric/family/metadata representable.
- **§5.5 `EVIDENCE_ORDERING_KEY`:** consumed as fixed (C9 sort); never
  altered.

### 18.2 PA-3 (addendum §A0–§A7)

- **§A2 keys, all three:** primary `ios(c)` — well-defined per claim
  (THM-6, sibling THM-7); secondary `min EVIDENCE_ORDERING_KEY over
  supporters` — well-defined (THM-3); tertiary "Unicode code-point order
  over its UTF-8/NFC form" — `claim_text` is emitted already in NFC (C8),
  so the key compares emitted bytes with no second normalization step;
  **and the key's injectivity CONDITIONAL (F2/F2′) is discharged**: THM-7
  proves distinct claims have distinct `claim_text` in every output, so `≺`
  is a strict total order on every real `CandidateClaims` value, as §A2
  asserts. The addendum's text requires no change — its conditional is
  *satisfied*, not edited (R-5 clean).
- **§A1/§A3/§A4:** `Σ`, selection, precedence, and the S1 composition
  consume `extract`'s output through the frozen formulas unchanged; `D`
  entails no edit to any of them.
- **§A grounding types:** output conforms exactly (`CandidateClaims`
  ordered tuple; `CandidateClaim = {claim_text, supporting_doc_ids}`) —
  PO-EXT-5.
- **§A7 I-1/I-2/I-3:** untouched; `D` changes no `EvidenceStateResult`
  semantics and entails no code path.

### 18.3 Ontology and migration

Well-formed object per ONT-1 §2 (§3 above): right class/origin/owner/
lifecycle; references L0/L1 only, acyclic (§24). Migration M5: this text is
the content of the declared slot; M12: upon its freeze, the
derivation-method §5 precondition becomes satisfiable for
`EXTRACTION_PARAMS`; M17: authored in the E4a position, before E4b; ONT-1
§6: `Parameter[SEM-EXTRACTION]` remains uninhabited until freeze — this
document inhabits nothing.

### 18.4 Derivation method and E4b

Post-freeze, the E4b derivation of `EXTRACTION_PARAMS` under method §5 is
**transcription-shaped**: P-EXT-1 is a singleton entailed by `D` (UHO-a),
P-EXT-2 is inert convention (UHO-b). Method §2.2's "no value-selecting
class" gap is closed for this register by construction (SAM-1 §3.5, A-7).
The method's §5.2 constraints (determinism, entity-level, totality,
output-type conformance, §A2-tertiary-key validity of `claim_text`,
firewall) are each theorems here (THM-1, THM-2, THM-4, PO-EXT-5, THM-7,
THM-FW), and the method's §5.3/§5.4 standing item — "the auditor records
whether the derived extraction parameters discharge the F2/F2′ CONDITIONAL
or leave it open" — is answered in advance: **discharged** (THM-7), so the
E4b record can cite this definition rather than adjudicate the conditional
itself. Joint-reachability enablement for J-3: W+E-class inputs give
non-empty `Σ` with `ios ≥ 2` attainable (S3-side, with sibling THM-4/W+);
N-E-class inputs give `Σ = ∅` attainability (S0-side); S1/S2 witnesses
require composition with the other definitions and are owed at S4 over
`S0-JW-1`, as SAM-1 assigns.

### 18.5 S0 preregistration

`S0-REG-1` is consumed by identity. This document: answers the 11
registered `QS-EXT` rows (§16) without rewording any; records no expected
output for any sealed probe (author witnesses in §7/§8/§13/§19 are
proof-pack constructions, authored without access to `S0-PB-1`/`S0-JW-1`
payloads — SAM-R3); and defers to GC-1…GC-6 as the gate its own S3
admissibility depends on (header Status).

## 19. Adversarial search

Counterexamples were sought against every clause; each is destroyed or its
residue explicitly recorded.

### 19.1 Extensional-ambiguity attacks (F-1 class)

- **Attack: two conformant extractors differing on some input.** Requires a
  term of `D` with two readings; §14.2 A1 leaves only UVER-mechanical and
  set-theoretic steps plus the pinned `TERM` set. **Destroyed** (modulo
  TRR's independent test, which this document cannot and does not waive).
- **Attack: "sentence" reinterpreted linguistically** (semantic
  sentence-hood, abbreviation handling "Dr. Smith arrived"). "Unit" is
  *defined* by SEG-1's closed rule; `"Dr. Smith arrived in 1901."` splits
  after `"Dr."` (period followed by a `White_Space` code point) into two
  units by the
  frozen rule — both readers compute the same two units. The split may be
  linguistically unnatural (recorded as SU-EXT-2); it is not ambiguous.
  **Destroyed as ambiguity.**
- **Attack: granularity/span rereading (CE-7/CE-8 replay).** Not expressible:
  no clause mentions clauses, windows, or offsets (MIN-EXT-1/-3).
  **Destroyed.**

### 19.2 Degeneracy/determinism attacks (F-2 class)

- **Always-empty model (v1-b):** contradicts W+E1 (§7.2). **Destroyed.**
- **Indiscriminate model:** contradicts N-E1/N-E4; and its `Q = ∅` route is
  blocked by C5 (MIN-EXT-5). **Destroyed.**
- **Identity-fragmenting model (CE-13 replay):** contradicts W+E2's forced
  merge (MIN-EXT-7). **Destroyed.**
- **Input-external dependence (clock/env/store/seed/model/tuple-position):**
  no such term exists in `D` (§12; THM-3). **Destroyed.**

### 19.3 Axis-descent attacks (F-3 class — the v2-killer, re-aimed here)

- **Descent into segmentation parameters** (terminator choice, abbreviation
  lists, digit-context rules): pinned to the inline closed `TERM` set and
  its `White_Space` follow-context conjunct; there is no segmentation
  *parameter* — the set is the rule (MIN-EXT-2a/-2b). **Destroyed.**
- **Descent into span/window/length parameters:** none exist (C3;
  MIN-EXT-3). **Destroyed.**
- **Descent into normalization version or tokenization detail:** pinned by
  import (UVER; sibling MIN-2). **Destroyed.**
- **Descent into ordering conventions:** both sorts reuse already-frozen
  comparisons (`EVIDENCE_ORDERING_KEY`; §A2 tertiary comparison); no new
  comparison object exists to parameterize (MIN-EXT-10). **Destroyed.**
- **Descent into serialization:** P-EXT-2, proved inert (UHO-b, §14.3).
  **Destroyed.**

### 19.4 Surviving uncertainty (explicitly recorded)

- **SU-EXT-1 — Recall limit of the universal anchor.** A unit asserting the
  queried fact but referring to a query entity by pronoun, alias, or
  partial name (`"It opened in 1901."`; `"The observatory opened in
  1901."` for `q = "Kestrel Observatory"`) is not anchored and yields no
  claim; likewise a multi-entity query whose entities never co-occur in
  one sentence-unit extracts nothing even when the corpus jointly
  establishes the fact. Under `D` the output is uniquely entailed — this
  is not an ambiguity but a **semantic fidelity limit** of
  entity-presence anchoring at sentence granularity. Direction:
  exclusively toward emitting less (toward S0, honest refusal — the
  FM-1-safe side; §9). Closing it would require coreference or
  cross-sentence aggregation no frozen authority licenses. The scientific
  cost lands on H1's measured calibration, which is precisely the
  exposure EXP-1 exists to test; a kill there is a valid outcome, not a
  defect of definedness. **Recorded.**
- **SU-EXT-2 — Terminator-convention artifacts.** SEG-1's closed rule
  splits at abbreviation periods (`"Dr."`, `"U.S."` → sub-units) and does
  not split at terminator-free run-ons. Consequences are deterministic and
  reader-invariant, but can suppress anchoring (an abbreviation split
  separating query entities — a false negative, same safe direction as
  SU-EXT-1) — never fabricate it (splitting only shrinks each unit's
  `T(u)`, and the `∀`-anchor is monotone: fewer tokens can only lose
  anchoring; merging failures cannot add tokens a unit does not contain).
  A richer sentence model (abbreviation lexicons, ML segmenters) would
  reintroduce exactly the open-ended parameter surface (F-3) and
  unlicensed analyzers (CE-7) this definition exists to exclude.
  **Recorded as accepted strictness.**
- **SU-EXT-3 — Claim texts are evidence sentences, not minimal
  propositions.** A long anchored sentence carrying several assertions
  becomes one claim whose `E(c)` includes all its entity tokens; under the
  sibling's universal `supports`, corroborating items must contain **all**
  those tokens, so long-sentence claims are harder to corroborate (again
  the strict, S0-ward direction) and `selected_claim` may carry more text
  than the minimal queried fact. `SEM-TEMPLATE` consumes `selected_claim`
  as attributed text (addendum §A7 I-2/I-3), which is compatible with
  sentence-shaped claims; whether template wording constraints need the
  claim to be shorter is a `SEM-TEMPLATE`-side question (SQ-TPL-3),
  flagged for the S4 joint round. **Recorded.**
- **SU-EXT-4 — TRR is the outstanding empirical test.** UE is argued
  (§14), not self-certified; the S3/S4 falsification stages (F-1…F-5,
  TRR, joint round) remain open obligations. **Recorded.**

No other surviving uncertainty is known to the author; discovery of one
post-acceptance is an MF-2 event (SAM-1 §11.2).

## 20. Formal theorems

Grounding: `D` (§6.3), instruments of §6.1–§6.2, imported sibling theorems
(cited by identity), frozen formulas of addendum §A1–§A4. Proof sketches are
complete at the level of hand verification; every step is finite and
mechanical.

- **THM-1 (Determinism/functionality).** `extract` is a total function of
  input content into `CandidateClaims`. *Proof:* §12. ∎
- **THM-2 (Totality).** For every `(q, S) ∈ U` — including empty `q`, empty
  `S`, junk fields, unassigned code points, arbitrarily long inputs — D1–D3
  produce exactly one tuple. *Proof:* every §6.1–§6.2 function is total;
  D1's set comprehension is defined over every finite `S` (including `∅`);
  sorts over finite sets are total, and the sort of the empty set is `()` —
  the empty branches need no dedicated clause (§13.1 INERT-1). ∎
- **THM-3 (Order invariance).** `extract(q, S)` is invariant, as a tuple,
  under any permutation of `S`. *Proof:* §11. ∎
- **THM-4 (CF-R2 first line, as a theorem).** If some `t ∈ Q` satisfies
  `t ∉ T(u)` for every unit `u` of every item of `S`, then
  `extract(q, S) = ()`. *Proof:* no unit satisfies `Q ⊆ T(u)` (witness
  `t`); `A = ∅`; D3 sorts the empty set. ∎ — A fabricated query entity
  absent from the corpus
  yields **no claim at all**: nothing exists downstream for `supports` to
  false-positive on, `Σ = ∅`, S0 fires. The fabrication-pressure posture
  of T1 §5.6 is entailed, not hoped for.
- **THM-5 (Two-sidedness / non-degeneracy).** `extract` is non-empty on
  W+E1 and empty on N-E1: the always-empty and the indiscriminate
  extractors each disagree with `D` somewhere, hence neither satisfies
  `D`. *Proof:* direct evaluation of §7.2/§8.1 witnesses. ∎
- **THM-6 (Identity merge / S3 attainability).** If the same anchored
  canonical text `t` occurs in units of items `e₁, e₂` with distinct
  independent `origin_domain`s, then `extract` emits **one** claim `c_t`
  with both items among its supporters, and `ios(c_t) ≥ 2`. *Proof:* D1
  collapses by `ctext` equality; each `eᵢ` contains every token of `t` in
  the field carrying the unit, so `supports(c_t, eᵢ) = true` (sibling
  §6.3: `E(c_t) = T(t) ⊆ V(eᵢ)`, and `E(c_t) ≠ ∅` since `Q ≠ ∅` and
  `Q ⊆ T(t)`); `independent_origins` counts two distinct domains. ∎ —
  The CE-13 unreachability pathology is excluded: corroboration cannot be
  fragmented across identity duplicates.
- **THM-7 (§A2 injectivity — F2/F2′ discharged).** In every
  `extract(q, S)`, distinct claims have distinct `claim_text`; hence the
  §A2 tertiary key is injective over every real `CandidateClaims` value
  and `≺` is a strict total order. *Proof:* D1's output is indexed by the
  set `A` of canonical texts — one claim per text by construction (C7);
  distinct claims correspond to distinct members of `A`. ∎
- **THM-8 (J-5 coherence by identity).** For every emitted claim `c`,
  `set(c.supporting_doc_ids) = { e.doc_id : e ∈ S, supports(c, e) }`.
  *Proof:* C9 defines `ids` as exactly that extension, key-ordered and
  deduplicated. ∎ — Emission-time and predicate-time support cannot
  disagree; the J-5 obligation reduces, on this side, to checking a
  definitional identity.
- **THM-9 (Anchor monotonicity).** If `Q₁ ⊆ Q₂` and `Q₁ ≠ ∅`, every unit
  anchored under `Q₂` is anchored under `Q₁`. *Proof:*
  `Q₂ ⊆ T(u) ∧ Q₁ ⊆ Q₂ ⇒ Q₁ ⊆ T(u)`. ∎ — Adding entities to a query never
  gains claims; fabrication strictly shrinks the extraction set (the
  mechanism behind THM-4; mirror of sibling THM-8).
- **THM-FW (Firewall by construction).** No component of `D` or of `P`'s
  admissible sets is, equals, or is fitted to any numeric quantity at all
  — a fortiori not to any EXP-1 probability, bin boundary, or ECE
  threshold. *Proof:* by inspection, `D` and P-EXT-1 contain no numeric
  constant (code points in `TERM` are identity labels, not quantities);
  P-EXT-2 is a serialization convention; no stage of this authoring
  consulted any evaluation-side object (§2 forbidden row). ∎

## 21. Proof obligations (SAM-1 §7.4 — written discharge map)

| PO | Obligation | Discharged by |
|---|---|---|
| PO-EXT-1 (TOTAL) | Defined for every input, incl. empty/junk documents and empty snapshots | THM-2; §4.1; N-E2/N-E3 edge classes. |
| PO-EXT-2 (DET) | Pure text mechanics: no model call, randomness, wall-clock; function of content | THM-1; §12 corollaries (replay, C1 sentinel). |
| PO-EXT-3 (UE) | Unique extension; two readers extract identical ordered tuples | §14.2 (argued); §15 (TRR-tested at S3, not waived). |
| PO-EXT-4 (POS/NEG) | Non-empty witness class exhibited; fabricated-entity inputs provably yield no claim; both degeneracies excluded by `D` | §7.2, §8.1, THM-4, THM-5; MIN-EXT-4/-5. |
| PO-EXT-5 (TYPE) | Output conforms to frozen `CandidateClaims` ordered tuple with `{claim_text, supporting_doc_ids}` | §4.2, §5, D2/D3; §18.2. |
| PO-EXT-6 (INJ) | §A2 injectivity entailed, or CONDITIONAL explicitly declared with closure assigned | **Entailed**: THM-7 (the F2/F2′ CONDITIONAL is discharged, §18.2/§18.4 — nothing is silently inherited). |
| PO-EXT-7 (IDENT) | Claim identity stable under replay and evidence-order permutation; no `Σ≠∅`-but-S3-unreachable pathology admissible | §10; THM-1, THM-3, THM-6. |
| PO-EXT-8 (ORDER) | Tuple order deterministic from content | C10; THM-3; THM-7 (strictness). |
| PO-EXT-9 (FIRE) | No evaluation-side quantity in `D` or `P` | THM-FW; §2 (forbidden evidence untouched). |
| PO-EXT-10 (UHO) | Every `P` slot UHO-a or UHO-b | §14.3 (P-EXT-1 UHO-a singleton; P-EXT-2 UHO-b inert + convention ground). |

Every discharge above cites only allowed evidence (E-STRUCT, E-TYPE,
E-PRIOR, E-DETERM arguments grounded in T1 §3.1/§5.5/§5.6/§7/§8, addendum
§A0–§A7, the frozen type contract, ONT-1, and the imported `SEM-SUPPORT` r1
exports; CE items appear only as constraint provenance). No EXP-1 object,
corpus statistic, observed-score preference, implementation behavior, or
unrecorded intuition is cited anywhere in `Π` (SAM-1 §7.2/§7.3).

## 22. Acceptance conditions

This candidate is accepted, and becomes freeze-eligible at E4a, **only** when
all of the following hold, each mapped to a named artifact (SAM-1 §7.9 via
the §5.9 schema, §10.1 — none is produced by this document):

| # | Condition | Artifact |
|---|---|---|
| AC-1 | Five-part deliverable well-formed (`U` §4, `D` §6, `P` §14.3, `X` §16, `Π` §§10–21); TSC holds; ontology manifest valid; no forbidden vocabulary | S1 structural-gate record |
| AC-2 | `X` complete over SQ-EXT-1…11 by citation (no empty/evasive row) | §16 checked at gate |
| AC-3 | PO-EXT-1…10 discharged from allowed evidence only | §21 / `Π` citation check |
| AC-4 | Independent falsification F-1…F-5 (incl. TRR §15, tuple-exact) returns NO-COUNTEREXAMPLE over `S0-PB-1` + adversarial extension | S3 L4 verdict |
| AC-5 | Joint round J-1…J-7 passed over `S0-JW-1` (with all four candidates individually past S3) — including the J-1 registry rows this object imports (§24) and the J-5 identity check (THM-8) | S4 L4 verdicts |
| AC-6 | Minimality record complete (§13), independently checked (auditor deletion attempts punished) | MIN record + S3 check |
| AC-7 | UHO discharged per slot (§14.3) | UHO table |
| AC-8 | Ontology well-formedness and role/no-proxy discipline intact across S0–S4 (incl. the SAM-R2 timestamp precedence recorded in the header Status, and the §24 revision coupling to `sem-support-2026-07-15-r1` still valid) | manifests + stage records |
| AC-9 | ScientificAuditor approval recorded, referencing AC-1…AC-8 by identity | S5 L5 record |

Only after AC-1…AC-9: freeze at E4a (S6), whereupon
`Parameter[SEM-EXTRACTION]` becomes inhabitable and E4b may run. Freeze,
transcription, digest, and gate movement remain governed by the existing
documents and are not performed here.

## 23. Rejection conditions

Any single one rejects this candidate, recorded with cause; the revision
returns to S1 as a new L1 draft and this text's falsification record is
retained permanently (SAM-1 §7.10 via the §5.10 schema, §10.2):

- RC-1: any unanswered or evasively-answered SQ row (an axis "answered" by
  prohibition or role-restatement is empty);
- RC-2: any PO undischarged, or discharged from forbidden evidence
  (including any demonstration that a clause of `D` was fitted to the
  interim `claim_extraction.py` behavior or to any EXP-1 query form);
- RC-3: any F-1…F-3 counterexample; any TRR divergence or `UNDERDETERMINED`
  (including one arising from the `TERM` set, the follow-context conjunct,
  the anchor test, `ctext`, either sort, or any clause of §6);
- RC-4: any `P` slot found to conceal semantic freedom (UHO failure) —
  e.g. a demonstration that P-EXT-2's serialization is not consumer-inert,
  or that P-EXT-1's admissible set is not a singleton;
- RC-5: any boundary breach — a demonstration that `D` entails a change to
  any frozen T1/addendum/type content (the claimed-necessary change routes
  to change control as a separate Wave-2 proposal, never absorbed);
- RC-6: any firewall contamination of any stage;
- RC-7: any role or sequencing breach (author-seen sealed probes,
  author-run falsification, proxy approval, or S1 preceding a valid S0
  gate record) — voids the affected stage record;
- RC-8: TSC failure;
- RC-9: unresolved MIN failure (a clause with no surviving witness);
- RC-10: joint-round failure localized to this candidate's text (per SAM-1
  §9), including a J-1 import-drift failure (this object restating rather
  than referencing a shared term), a J-4 identity-composition failure, or a
  J-5 incoherence traceable to C9;
- RC-11: invalidation of the §24 revision coupling — rejection or
  supersession of `sem-support-2026-07-15-r1` — which voids the imports'
  referents (this is re-entry to S1 by dependency, recorded as such, not a
  content defect of this text).

## 24. Imports and exports (declared definitional DAG edges)

**Imports (objects this definition consumes, by reference and by revision
identity, never restated):** from `PROGRAM_A_SEM_SUPPORT.md` revision
`sem-support-2026-07-15-r1` —

| Imported object | Defined at (sibling) | Consumed by (here) |
|---|---|---|
| `UVER` — Unicode 16.0.0 pin | §6.1 | every Unicode-dependent step (§6.1–§6.2) |
| `NORM-1` — NFC @ UVER, no folding | §6.1–§6.2, §9 | `ctext` (C8), all token equality (J-2 coherence by construction) |
| `TOK-1` — tokenization/stripping | §6.2 items 2–3 | `T(u)`, `Q` (C6) |
| `ENT-1` — entity-token notion + identity | §6.2 items 4–5, §10 | anchor test (C4/C5), `Q`, `T(u)` (J-1 single-sourcing: this object is an importer, never a definer, of the entity notion) |
| `supports(c, e)` — the defining biconditional | §6.3 | `ids` only (C9; J-5 coherence by identity, THM-8) |

Its other definitional dependencies are: the frozen type contract (L1), the
frozen consumer formulas and keys of addendum §A1/§A2/§A3 and
`EVIDENCE_ORDERING_KEY` (T1 §5.5) (L1, consumed as fixed context —
signatures and comparisons only, no content absorbed). The graph is acyclic
— `SEM-SUPPORT` r1 §24 declares **no** import from `SEM-EXTRACTION`, so the
one-directional edge closes J-6's DAG requirement — and references no
object later than L1.

**Exports (objects defined here, single-sourced for the J-1 registry, to be
imported by reference and never redefined):**

| Exported object | Defined at | Anticipated importers |
|---|---|---|
| `SEG-1` — the sentence-unit rule (`TERM` set + `White_Space` follow-context conjunct + trim + empty-unit discard, over `nfc`; a set of units) | §6.1 | the S4 joint round (J-3 witness construction); `SEM-TEMPLATE` if its skeleton semantics needs the unit notion for attribution (SQ-TPL-3 — its choice, not an obligation created here). Note: trim, discard, and the `nfc` domain are extensional for **this exported object** (MIN-EXT-11/-12/-17) even where inert for `extract`. |
| `CLM-1` (`ctext`) — canonical claim text: whitespace-collapsed NFC | §6.2 item 5, §6.4 C8 | `SEM-MATERIALITY` (SQ-MAT-1/SQ-MAT-6: the representation of the claim pairs `is_material` ranges over); J-2 registry |
| `IDENT-1` — claim identity = `claim_text` code-point equality | §10, C7 | `SEM-MATERIALITY` (pair individuation), J-4 registry |
| `ORD-EXT-1` — output order: ascending code-point on `claim_text` | §6.4 C10 | none required (internal to the tuple contract); recorded for the registry's completeness |

Declared open hooks this definition **enables but does not discharge**
(owned where SAM-1 assigns them): J-3 joint reachability (S4, over
`S0-JW-1`; this object's contributions: THM-4 S0-side, THM-6 S3-side); J-4
identity-stability composition (this object's contribution: §10/THM-6 —
identity is content-functional, so any downstream consumer preserving
`claim_text` bytes preserves identity); J-5 coherence (this object's
contribution: THM-8 reduces it to a definitional identity); J-7 joint TRR.
The SU-EXT-3 template-shape question is flagged to the S4 round and to
`SEM-TEMPLATE`'s SQ-TPL-3.

## 25. Appendix

### 25.1 Notation

| Symbol | Meaning |
|---|---|
| `⟺` | if and only if (biconditional) |
| `∈, ∉, ⊆, ⊉, ∪, ∅, ≠` | set membership/non-membership, inclusion, non-inclusion, union, empty set, inequality |
| `⧺` | sequence concatenation *(retired at r3 — no clause of `D` concatenates sequences; retained for reading the r2 record)* |
| `U` | the declared universe (§4.1) |
| `D` | the defining rule (§6.3, steps D1–D3) |
| `P` | the declared parameter surface (§14.3) |
| `X` | the axis-closure table (§16) |
| `Π` | the proof pack (§§10–14, 17–21) |
| `q`, `S` | the query text; the well-typed `EvidenceSet` |
| `Q` | `T(q)` — the query's entity-token set (§6.2) |
| `seg(s)` | the SEG-1 unit set of `s` (§6.1) |
| `units(e)` | `seg(e.title) ∪ seg(e.text)` (§6.2) |
| `T(u)` | entity-token set of unit `u` (imported `ENT-1`) |
| `ctext(u)` | whitespace-canonical NFC text of `u` (§6.2 item 5; `CLM-1`) |
| `A(q, S)` | the set of anchored canonical texts (D1) |
| `ids(t, S)` | the `supports`-extension doc-id tuple for claim text `t` (D2) |
| `TERM` | the frozen terminator code-point set (§6.1) |
| `supports`, `E(c)`, `V(e)` | imported from `SEM-SUPPORT` r1 (§6.1) |
| `ios(c)`, `Σ`, `≺` | frozen downstream quantities (addendum §A1/§A2) |
| `UVER` | Unicode 16.0.0, pinned (imported) |

### 25.2 Definitions (index)

| Term | Where defined |
|---|---|
| unit; sentence segmentation; `TERM`; follow-context conjunct | §6.1 (`SEG-1`) |
| anchored unit; anchor guard | §6.2 item 4 (C4/C5) |
| canonical claim text | §6.2 item 5 (`CLM-1`, C8) |
| claim identity | §10 (`IDENT-1`, C7) |
| `supporting_doc_ids` semantics | D2 / §6.4 C9 |
| output order | D3 / §6.4 C10 (`ORD-EXT-1`) |
| positive/negative extension | §7 / §8 |
| parameter slots P-EXT-1, P-EXT-2 | §14.3 |
| surviving uncertainties SU-EXT-1…SU-EXT-4 | §19.4 |

### 25.3 Identifier registry created by this document

`SEM-EXTRACTION` (rev `sem-extraction-2026-07-16-r3`); clauses C1–C10
(§6.4; C11 retired at r3, §13.1 INERT-1 — identifier never reused);
construction steps D1–D3 (§6.3; D4 retired at r3); witnesses W+E1–W+E3,
N-E1–N-E7; inertness findings INERT-1…INERT-7 (§13.1); minimality witnesses
MIN-EXT-0…MIN-EXT-17 (§13.2; MIN-EXT-2 split into 2a/2b at r3; r2's
MIN-EXT-2 retired); theorems THM-1…THM-9, THM-FW
(local numbering; sibling theorems cited as "sibling THM-n"); axis rows
X-1…X-11; parameter slots P-EXT-1, P-EXT-2; exports `SEG-1`, `CLM-1`,
`IDENT-1`, `ORD-EXT-1`; acceptance/rejection rows AC-1…AC-9 / RC-1…RC-11;
surviving uncertainties SU-EXT-1…SU-EXT-4.

---

*End of `SEM-EXTRACTION`. This document defines the extensional semantics of
PA-2's candidate-claim boundary and nothing else: universe total, rule
constructive and two-sided, granularity and span fixed by a closed
parameter-free unit rule, claim identity content-functional with the §A2
injectivity conditional discharged by construction, `supporting_doc_ids`
coherent with `supports` by identity, parameter surface collapsed to
transcription-plus-inert-convention, every registered axis closed by
citation, every proof obligation discharged in writing from allowed
evidence, every clause minimality-witnessed, and four surviving
uncertainties recorded rather than hidden. It authors no other `SEM-*`
object, chooses no L2 value, alters no frozen T1/PA-3/SAM-1 content, writes
no code, and performs no governance: it is a drafted L1 candidate awaiting
SAM-1 stages S3–S5. `Parameter[SEM-EXTRACTION]` remains uninhabited,
`CONSTANTS_HASH` remains `None`, and the standing prohibition holds.*







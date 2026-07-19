# PROGRAM A — SEM-* STAGE S0 PREREGISTRATION

**Title:** Instantiation of SAM-1 Stage S0 (Preregistration) for the E4a
authoring of `SEM-SUPPORT`, `SEM-MATERIALITY`, `SEM-EXTRACTION`,
`SEM-TEMPLATE`: the registered per-object question sets, the core probe
battery, and the joint witness set — recorded before any S1 drafting begins.
**Object identity:** `S0-REG-1` — a compound registration containing exactly
three typed objects (§0.3): `S0-QS-1` (L0 `ReferenceArtifact`), `S0-PB-1`
(L4 `VerificationArtifact`, planned), `S0-JW-1` (L4 `VerificationArtifact`,
planned). Classes, owners, and lifecycles per `PROGRAM_A_ARCHITECTURAL_ONTOLOGY.md`
(ONT-1) §3–§4; stage definition per
`PROGRAM_A_SEMANTIC_AUTHORING_METHODOLOGY.md` (SAM-1) §4, row S0.
**Authority basis:** SAM-1 §4 (S0 row: "Instantiated per-object question
sets …; core probe battery; joint witness set; all recorded before drafting
(L4-planned VerificationArtifacts + L0 registrations)"), SAM-1 §3.7 (W —
witness/probe universe), SAM-1 §11.1 rows SAM-R2/SAM-R3;
`PROGRAM_A_ONTOLOGY_MIGRATION_PLAN.md` M17 (E4a schedule slot); ONT-1
(consumed as fixed).
**Date:** 2026-07-15
**Status:** PREREGISTRATION — S0 only. This document **authors no semantic
definition, drafts no part of any `SEM-*` candidate, chooses no parameter
value, states no expected output for any probe, modifies no clause of T1, the
addendum, PA-3, or SAM-1, and performs no governance.** The standing
prohibition (`ES1_IMPLEMENTATION_GATE.md`:97-99) is unchanged. The four
`SEM-*` slots remain unauthored; `Parameter[SEM-*]` remains uninhabited;
`CONSTANTS_HASH` remains `None`.

---

## 0. Purpose, position, and object manifest

### 0.1 Purpose

SAM-1 §4 requires, as the entry stage of the E4a pipeline, a preregistration
stage S0 whose outputs exist **before drafting begins** (SAM-R2) and whose
probe content is authored **independently of the definition author**
(SAM-R3). No prior repository document instantiates those outputs. This
document is that instantiation and nothing else: it registers the question
sets, fixes the composition and coverage of the core probe battery and the
joint witness set, assigns their ownership and lifecycle, declares the
hash-identification slots the S0→S1 gate requires, and stops.

### 0.2 Hard boundaries

- **No semantics.** No probe in this preregistration carries an expected
  output, verdict, or classification. A probe is an *input* (SAM-1 §3.2 step
  3: readers compute the output the candidate text entails). Recording an
  expected output at S0 would author the very extension the E4a definitions
  must later fix, and is forbidden here.
- **No drafting.** No `(U, D, P, X)` content for any `SEM-*` appears here.
  Question sets are registered by citation into SAM-1 §5.1/§6.1/§7.1/§8.1;
  they are not extended, reworded, or answered.
- **No governance.** No approval, freeze, pin, or sign-off is performed.
  Lifecycle states declared in §7 are the ontology-defined initial states of
  newly created objects, not transitions performed by this document.
- **Firewall (SAM-1 §0.3, G-7).** No stage of this preregistration reads,
  imports, mirrors, or is fitted to any evaluation-side object: no EXP-1
  item, tier→probability mapping, bin boundary, ECE logic, outcome, frozen
  row, rubric, family, or adjudicator signal seeds any probe or witness
  (SAM-1 §3.7 "Firewall"; checked at the gate, §9 GC-5).

### 0.3 Object manifest

| Field | Content |
|---|---|
| Objects created | `S0-QS-1` — question-set registration (§2); `S0-PB-1` — core probe battery (§3); `S0-JW-1` — joint witness set (§4). |
| Objects consumed | SAM-1 §3.7, §4 (S0 row), §5.1, §6.1, §7.1, §8.1, §9, §11.1 (fixed); ONT-1 §3–§5, §7 (fixed); migration plan slot table + M17 (fixed); frozen types `program_a/types.py` (fixed). |
| Objects referenced (L0 provenance, no authority) | `docs/audits/REGISTER_DERIVATION_FINDING1_SONNET_AUDIT.md`, `docs/audits/REGISTER_DERIVATION_FINDING2_SONNET_AUDIT.md` (the CE catalogue); `PROGRAM_A_REGISTER_DERIVATION_ROOT_CAUSE_ANALYSIS.md`; `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §3.1/§5 and `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` §A0–§A7 (fixed context the probes must be well-typed against — consulted, never altered). |
| Classes / owners / lifecycles | Per §7. |

---

## 1. Position in the SAM-1 pipeline

This artifact is the complete output of stage **S0** of SAM-1 §4 and is
consumed by:

- **S1** (drafting) — only through its gate: S1 may not begin until the §9
  gate criteria hold (SAM-R2: "Question sets instantiated and probe battery
  preregistered before drafting … timestamps/hashes of S0 artifacts vs S1").
- **S3** (independent falsification) — `S0-PB-1` is the preregistered core
  over which F-1…F-5 and the TRR trial run (SAM-1 §3.2, §5.7, §3.7
  "Sequencing"); the S4-time adversarial extension is a *separate, later*
  authoring act by the auditor and is not part of this object.
- **S4** (cross-object round) — `S0-JW-1` supplies the composed-pipeline
  witnesses for J-1…J-7 (SAM-1 §9), including the joint TRR (J-7).

Nothing in S1–S6 is performed, anticipated, or constrained here beyond what
SAM-1 already states.

---

## 2. `S0-QS-1` — registration of the per-object question sets

### 2.1 Registration

The four instantiated question sets are registered **by citation, verbatim
and unmodified**, as the axis-closure obligations for E4a:

| Set | Rows | Registered source (sole authority) |
|---|---|---|
| `QS-SUP` | SQ-SUP-1 … SQ-SUP-10 | SAM-1 §5.1 |
| `QS-MAT` | SQ-MAT-1 … SQ-MAT-9 | SAM-1 §6.1 |
| `QS-EXT` | SQ-EXT-1 … SQ-EXT-11 | SAM-1 §7.1 |
| `QS-TPL` | SQ-TPL-1 … SQ-TPL-10 | SAM-1 §8.1 |

Total: **40 registered question rows.** This registration adds no row,
removes no row, and rewords no row. Any future change to a question set is a
SAM-1 revision (SAM-1 §11.4), never an edit here.

### 2.2 Completeness check against the CE catalogue (SAM-1 §4, S0 row)

The S0 row requires the question sets to be "checked complete against the CE
catalogue." The catalogue comprises v1-a…v1-c and CE-4…CE-13 (SAM-1 §13;
the two Sonnet audits). Check performed by row-to-row mapping:

| Catalogue item | Covering registered row(s) |
|---|---|
| v1-a (always-False support) | SQ-SUP-7 (TSC positive-firing) |
| v1-b (always-empty extractor) | SQ-EXT-5 |
| v1-c (two S0 realisation functions) | SQ-TPL-2 |
| CE-4 (evidence-scope ambiguity) | SQ-SUP-1 |
| CE-5 (entity quantifier) | SQ-SUP-3 |
| CE-6 (normalization) | SQ-SUP-4 |
| CE-7 (granularity) | SQ-EXT-2 |
| CE-8 (span rule) | SQ-EXT-3 |
| CE-9 (S1 discourse structure) | SQ-TPL-6 |
| CE-10 (compositional S0-only) | J-3 (SAM-1 §9), witnessed by `S0-JW-1` §4.2 |
| CE-11 (quantification-space mismatch) | SQ-SUP-1 / SQ-EXT-1 / SQ-MAT-1 / SQ-TPL-1 (declared universe `U`) + J-3's stated quantification space |
| CE-12 (⊆-incomparable materiality boundaries) | SQ-MAT-4 |
| CE-13 (claim identity / S3 unreachable) | SQ-EXT-4 + J-4 |

**Result: every catalogue item is covered by at least one registered row or
joint obligation; no uncovered item remains.** Per SAM-1 §3.3 (AXC), this
check is a floor, not a completeness proof; the open-ended residue is owned
by UE/TRR, not by this table.

---

## 3. `S0-PB-1` — the core probe battery

### 3.1 Composition rules (consumed from SAM-1 §3.7, restated as obligations on this object)

1. **Synthetic, well-typed, a-priori.** Every probe is a synthetic input
   constructed over the frozen types only: documents over the frozen 3-field
   schema (`origin_domain`, `title`, `text` of `EvidenceItem`), claims over
   the frozen `CandidateClaim` shape, `EvidenceStateResult` values over
   frozen fields (`program_a/types.py`).
2. **Firewall-clean.** No EXP-1 item, frozen row, rubric, family, or
   adjudicator-derived text seeds any probe.
3. **Inputs only.** No probe record contains an expected output (§0.2).
4. **Falsifying/discriminating role only.** Probes may never select semantic
   content by observed niceness of outcome (SAM-1 §3.7 "Role"; B-11
   discipline).
5. **Authored on the auditor side.** The battery's payloads are authored by
   the independent probe author (§7), not by the Architect (SAM-R3).

### 3.2 Sealing and channel discipline (SAM-R3; SAM-1 §3.7 "Sequencing")

SAM-1 §3.7 requires that "the author never sees the core battery before
submission." A root repository document carrying probe payloads verbatim
would breach that channel the moment the definition author reads the
repository. Therefore:

- This document records, for each probe, only its **identity, target rows,
  and construction class** — all of which are already public in SAM-1
  §5–§9 and add no information the author does not lawfully hold.
- The concrete probe **payloads** are recorded in sealed companion payload
  files, held outside the definition author's channel until S1 submission,
  and identified here **by path and content hash** (§6). The payload files
  are constituents of `S0-PB-1`/`S0-JW-1`, not separate objects.

| Sealed payload | Designated path |
|---|---|
| Core probe battery payloads | `evidence/sem_s0/S0_PB_1_payload.json` (sealed) |
| Joint witness payloads | `evidence/sem_s0/S0_JW_1_payload.json` (sealed) |

### 3.3 Battery structure and minimum coverage

The battery is partitioned into four construction classes. Coverage minima
are gate-checkable counts; the probe author may exceed any minimum.

| Class | Content | Minimum coverage |
|---|---|---|
| **PB-A (axis probes)** | For each registered question row of §2.1, a discriminating set of inputs constructed so that readings which differ on that axis are forced to produce observably different outputs when hand-evaluated under a candidate `D`. | ≥ 2 probes per SQ row (≥ 80 probes). |
| **PB-B (regression probes)** | Input constructions replaying the CE catalogue: the v1-a/v1-b degenerate-collapse inputs, the v1-c S0 pair discriminator, and the CE-4…CE-9, CE-12, CE-13 input families as constructed in the two Sonnet audits (multi-entity claims with partial evidence; case/diacritic variants; compound and appositive sentences; polarity-vs-precision claim pairs; cross-document paraphrase pairs). | ≥ 1 probe per catalogue item of §2.2 that names an input construction (v1-a, v1-b, v1-c, CE-4…CE-9, CE-12, CE-13: ≥ 11 probes). |
| **PB-C (totality/edge probes)** | Empty documents, junk text, empty snapshots, near-miss inputs from the never-fail-retriever posture, degenerate `EvidenceStateResult` values — the PO-*-1 (TOTAL) surface. | ≥ 3 per object (≥ 12 probes). |
| **PB-D (order/replay probes)** | Evidence-set permutations of PB-A/PB-B inputs — the PO ORDER / G-6 surface (extension invariant under evidence permutation). | ≥ 2 per object (≥ 8 probes). |

Each probe record in the sealed payload carries the schema:
`(probe_id, target_object(s), target_row(s) [SQ-*/CE-*/PO-*], class [PB-A…D],
payload)`. Probe ids are `PB-<OBJ>-<class>-<n>` (e.g. `PB-SUP-A-01`).

### 3.4 Consumption

`S0-PB-1` is the probe battery named by SAM-1 §3.2 step 3 (TRR inputs) and
§5.7/§6.7/§7.7/§8.7 (the "S0 core battery" over which F-1…F-5 run). The
S4-time "adversarial extension" (SAM-1 §3.7) is authored after the candidate
is read and is **not** part of this object; it will be a separate L4
artifact when created.

---

## 4. `S0-JW-1` — the joint witness set

### 4.1 Role

SAM-1 §3.7 ("Joint witnesses") and §9 require composed-pipeline witnesses —
inputs designed to traverse extraction → support → (contradicts ∘
materiality) → state → template jointly — because CE-10/CE-11/CE-13 proved
per-object probing insufficient. `S0-JW-1` is that witness set, preregistered
now, consumed at S4.

### 4.2 Witness families and minimum coverage

Witness families are keyed to the joint obligations of SAM-1 §9. Family
definitions use only frozen T1/addendum context (state definitions T1 §3.1;
`ios`/§A1/§A3 selection; §A2 keys) — no `SEM-*` content is presupposed:
a witness is an *input aimed at* a joint obligation, and whether it
discharges that obligation is decided at S4, not here.

| Family | Construction (inputs only) | Serves | Minimum |
|---|---|---|---|
| `JW-REACH` | Composed `(query_text, snapshot)` inputs constructed per state: an input with no topically-supporting content anywhere (aimed at S0); an input containing directly conflicting assertions across documents (aimed at S1); a single-origin assertion input (aimed at S2); a multi-origin, independently-corroborated assertion input (aimed at S3). Quantification space declared per witness (the CE-11 repair inside J-3). | J-3 | ≥ 2 per state (≥ 8). |
| `JW-COMP` | Inputs constructed to expose per-object-pass/joint-fail seams: content whose support-relevant tokens and extraction-relevant units are deliberately disjoint or deliberately coincident, in matched pairs. | J-3 (CE-10 class) | ≥ 4. |
| `JW-ID` | Cross-document paraphrase pairs: the same underlying assertion phrased differently in two independent-origin documents (the CE-13 n-gram-fragmentation discriminator; stresses claim identity across documents so `ios ≥ 2` is testable). | J-4 (CE-13 class) | ≥ 4. |
| `JW-COH` | Inputs where emission-time `supporting_doc_ids` and predicate-time support could diverge: documents partially overlapping a claim's entity content. | J-5 | ≥ 4. |
| `JW-TRR` | The full composed set: J-7's joint two-reader trial runs over **all** `S0-JW-1` witnesses (readers independently compute final state and rendered answer; byte-level agreement required). | J-7 | = all of the above. |

J-1, J-2, and J-6 are documentary/structural obligations (shared-term
registry, normalization coherence, acyclic DAG) discharged over the candidate
texts at S4; they consume the witness set only indirectly (via J-3/J-7) and
require no dedicated witness family.

Witness records use the schema
`(witness_id, target_family, target_obligation(s) [J-*], declared
quantification space, payload)`; ids are `JW-<FAMILY>-<n>`.

---

## 5. Provenance

| Input | Layer / role |
|---|---|
| SAM-1 §3.2, §3.7, §4 (S0 row), §5.1, §6.1, §7.1, §8.1, §9, §11.1 (SAM-R2/R3) | L1 authority — defines this stage; consumed as fixed. |
| ONT-1 §3–§5, §7 | L1 authority — object classes, lifecycles, operations, reference rules. |
| `PROGRAM_A_ONTOLOGY_MIGRATION_PLAN.md` (M17: E4a; slot table) | L1/L5 context — schedule slot this stage begins. |
| T1 §3.1/§5, addendum §A0–§A7, `program_a/types.py` | Fixed L1/L2 context — probes must be well-typed against these; never altered. |
| Sonnet audits 1–2 (CE catalogue), RCA | **L0 provenance only** — motivate probe constructions (§3.3 PB-B, §4.2); transfer no authority (SAM-1 §5.2: "a CE may motivate an obligation; it may not smuggle content"). |
| Evaluation-side objects (EXP-1, frozen rows, rubrics, families, adjudicator signals) | **Forbidden** — not consulted at any point (§0.2; gate GC-5). |

---

## 6. Hash identification (placeholders)

The S0→S1 gate requires the question sets and battery to be "recorded and
hash-identified" (SAM-1 §4). The following slots are declared now and filled
at S0 hash-identification (a recording act, not a governance act). `SHA-256`
over exact file bytes.

| # | Artifact | Hash slot |
|---|---|---|
| H-1 | This document (`PROGRAM_A_SEM_S0_PREREGISTRATION.md`) at registration | `<TBD — filled at S0 hash-identification>` |
| H-2 | `evidence/sem_s0/S0_PB_1_payload.json` (sealed core battery) | `<TBD — filled at sealing>` |
| H-3 | `evidence/sem_s0/S0_JW_1_payload.json` (sealed joint witnesses) | `<TBD — filled at sealing>` |
| H-4 | SAM-1 revision this stage runs under (`PROGRAM_A_SEMANTIC_AUTHORING_METHODOLOGY.md`) | `<TBD — filled at S0 hash-identification>` |

H-2/H-3 bind the sealed payloads to this registration so that SAM-R2's
"timestamps/hashes of S0 artifacts vs S1" check is mechanical: any S1 draft
predating H-1…H-3, or any payload edit after H-2/H-3, is detectable by hash
mismatch. Filling a hash slot alters no other byte of this document; any
other change is a new revision (ONT-1 §5).

---

## 7. Ownership and lifecycle

Per ONT-1 §3–§4 and SAM-1 §4 (S0 row: "Auditor side authors probes;
Architect registers question sets"):

| Object | Class | Origin | Owner | Creator | Lifecycle (initial state) |
|---|---|---|---|---|---|
| `S0-QS-1` | `ReferenceArtifact` | L0 | Architect | Architect | **registered** (content-addressed at H-1) |
| `S0-PB-1` | `VerificationArtifact` | L4 | domain verifier (independent probe author) | independent probe author ≠ Architect | **planned** → executed (at S3 use) → recorded |
| `S0-JW-1` | `VerificationArtifact` | L4 | domain verifier (independent probe author) | independent probe author ≠ Architect | **planned** → executed (at S4 use) → recorded |

**Role discipline (SAM-1 §4, SAM-R3).** The probe author is independent of
the definition author, with no channel between them regarding probe content
(SAM-1 §3.7 sealing, §3.2 independence-of-person-and-channel). The named
individual occupying the probe-author position is recorded in the S0 role
record at sealing; no criterion here references a person, only the
independence relation (SAM-1 §11.3). Any breach voids this stage's artifacts
and the stage re-runs with clean roles (SAM-1 §4 "Role discipline").

**Change control.** All three objects follow ONT-1 §5: pre-freeze
`Transform` only by the creation authority; any change after
hash-identification is a new revision, never mutation. A revision of SAM-1's
question sets (SAM-1 §11.4) obsoletes `S0-QS-1` and forces a new S0
registration; the falsification value of a superseded battery is retained as
history (SAM-1 §4, Finding-1/-2 lesson).

---

## 8. What this stage does **not** contain (declared residue)

- The **S1 candidates** `(U, D, P, X)` and **S2 proof packs** `Π` — future
  Architect work; none exists.
- The **S4 adversarial probe extension** — authored by the auditor only
  after reading the candidates; deliberately not preregistrable.
- The **S3/S4/S5 execution records and verdicts** — L4/L5 artifacts of later
  stages.
- Any **`SEM-*` content**, any **L2 value**, any **code**, any
  **governance record**.

---

## 9. Gate criteria (S0 → S1)

S1 drafting may begin only when all of the following hold. Each criterion is
checkable by a third party from the artifacts alone (SAM-1 §11.3).

| # | Criterion | Checked against |
|---|---|---|
| GC-1 | The four question sets are registered unmodified, and the §2.2 CE-catalogue completeness table has no uncovered item. | §2 vs SAM-1 §5.1/§6.1/§7.1/§8.1 and the audit CE catalogue. |
| GC-2 | The core probe battery exists in sealed form, satisfies every §3.1 composition rule and every §3.3 minimum coverage count, and contains no expected outputs. | `evidence/sem_s0/S0_PB_1_payload.json` vs §3. |
| GC-3 | The joint witness set exists in sealed form and satisfies every §4.2 family minimum, with each witness's quantification space declared. | `evidence/sem_s0/S0_JW_1_payload.json` vs §4. |
| GC-4 | All hash slots H-1…H-4 are filled; recorded timestamps/hashes precede any S1 draft (SAM-R2). | §6 table vs repository history. |
| GC-5 | Firewall check record exists: no probe or witness is seeded by, equal to, or fitted to any evaluation-side object (SAM-R14; SAM-1 §0.3). | S0 firewall check record. |
| GC-6 | Role record exists: probe/witness payload author is named, is not the definition author, and no content channel between them is recorded (SAM-R3). | S0 role record. |

Failure of any criterion blocks S1; there is no waiver path (SAM-1 G-9:
no role may accept by fiat).

---

## 10. References to SAM-1 sections (normative map)

| This document | Instantiates |
|---|---|
| §1 | SAM-1 §4 (pipeline position, S0 row) |
| §2 | SAM-1 §4 S0 output "Instantiated per-object question sets … checked complete against the CE catalogue"; SAM-1 §5.1, §6.1, §7.1, §8.1; §3.3 (AXC floor) |
| §3 | SAM-1 §4 S0 output "core probe battery"; §3.7 (W: composition, firewall, sequencing, role); §3.2 (TRR inputs); §5.7/§6.7/§7.7/§8.7 (F-1…F-5 core) |
| §4 | SAM-1 §4 S0 output "joint witness set"; §3.7 (joint witnesses); §9 (J-1…J-7) |
| §5 | SAM-1 §0.3 (firewall), §5.2/§5.3 schema (allowed/forbidden evidence, lifted to probe construction) |
| §6 | SAM-1 §4 S0 gate ("recorded and hash-identified"); §11.1 SAM-R2, SAM-R13 |
| §7 | SAM-1 §4 (S0 actors; role discipline); §11.1 SAM-R3; ONT-1 §3–§5 |
| §9 | SAM-1 §4 (S0→S1 gate); §11.1 SAM-R2/R3/R14; §11.3 (governance independence) |

---

*End of S0 preregistration. This document registers the question sets, fixes
the core probe battery and joint witness set by composition, coverage,
ownership, and hash identity, and declares the S0→S1 gate. It authors no
semantic definition, records no expected probe output, chooses no value,
modifies no frozen or protected document, and performs no governance. The
four `SEM-*` slots remain unauthored and `Parameter[SEM-*]` remains
uninhabited.*

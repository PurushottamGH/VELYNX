# PROGRAM A — CONSISTENCY AUDIT REPORT

**Authority:** VELYNX Consistency Auditor, 2026-07-08.  
**Scope:** Verification of newly-created Program A documents and their cross-consistency under the canonical rules of `PROGRAM_D_CANONICAL.md`.  
**Documents Audited:**  
- `PROGRAM_A_FINAL_ARCHITECTURE.md` (LSA, 2026-07-08)  
- `PROGRAM_A_MODULE_SPEC.md` (LSA, 2026-07-08)  
- `PROGRAM_A_IMPLEMENTATION_ORDER.md` (LSA, 2026-07-08)  
- `PROGRAM_A_BUILD_CHECKLIST.md` (LSA, 2026-07-08)  
- `PROGRAM_A_CONFIDENCE_MECHANISM.md` (CSA, 2026-07-07)  
- `PROGRAM_A_BINDING_SPEC.md` (Builder, 2026-07-07)  
- `EXP1_DATASET_SPEC.md` (Draft, pending freeze)  
- `EXP1_PREREGISTRATION.md` (Preregistered baseline)  
- `PROGRAM_D_CANONICAL.md` (Single source of truth)  

---

## 1. Executive Summary

This audit evaluates the architectural, mathematical, and programmatic alignment of the newly proposed design and implementation plan for **Program A** (the honest-uncertainty retrieval system). 

The core scientific primitives of the **ES-1 Confidence-Emission Mechanism** are rigorously and beautifully derived. However, a major bottleneck exists: **a severe structural mismatch between the newly-drafted dataset specification (`EXP1_DATASET_SPEC.md`) and the frozen experiment runner code (`experiments/EXP1/dataset.py`)**. If the dataset is built exactly as specified in the new draft, it will fail to load or execute under the current frozen code.

Furthermore, several minor terminology mismatches, stale references in the binding specification, and a fundamental experimental contradiction regarding seed-level variance must be acknowledged and resolved before proceeding with the implementation freeze.

This report classifies findings into **CRITICAL** (breaks execution/loading), **HIGH** (architectural or experimental contradictions), **MEDIUM** (stale references or rule boundary mismatches), and **LOW** (redundancies or clerical issues). Each finding includes precise file and line evidence. No redesigns are proposed; only inconsistencies are exposed.

---

## 2. Consistency Audit Matrix

| Finding ID | Classification | Subsystem / Area | Target Files / Lines | Conflict Description |
|---|---|---|---|---|
| **AUD-01** | **CRITICAL** | Dataset / Schema | `EXP1_DATASET_SPEC.md#L96-118` vs `experiments/EXP1/dataset.py#L34-60` | Schema key name mismatch (`query_text`/`family` vs `query`/`query_family`). |
| **AUD-02** | **CRITICAL** | Dataset / Enums | `EXP1_DATASET_SPEC.md#L100,123` vs `experiments/EXP1/dataset.py#L18-22` | Enum value mismatch for query families. |
| **AUD-03** | **CRITICAL** | Dataset / Layout | `EXP1_DATASET_SPEC.md#L76-89` vs `experiments/EXP1/dataset.py#L248-264` | Split query/rubric file layout vs inline `gold_rubric` loading expectation. |
| **AUD-04** | **HIGH** | API Signatures | `PROGRAM_A_FINAL_ARCHITECTURE.md#L226-228` vs `PROGRAM_A_MODULE_SPEC.md#L71-73` | Output field name mismatch in classification step. |
| **AUD-05** | **HIGH** | API Signatures | `PROGRAM_A_FINAL_ARCHITECTURE.md#L194-196` vs `PROGRAM_A_MODULE_SPEC.md#L69` | Output field name mismatch in extracted claims. |
| **AUD-06** | **HIGH** | Experimental Design | `EXP1_PREREGISTRATION.md#L181-203` vs `PROGRAM_A_FINAL_ARCHITECTURE.md#L417-434` | Seed variance assumption vs 100% deterministic, byte-identical replicates. |
| **AUD-07** | **MEDIUM** | Import Boundaries | `PROGRAM_A_FINAL_ARCHITECTURE.md#L87-88` vs `PROGRAM_A_MODULE_SPEC.md#L261-264` | Strict "stdlib, core, and backend only" import rule vs binding imports. |
| **AUD-08** | **MEDIUM** | Stale References | `PROGRAM_A_BINDING_SPEC.md#L91-100,292-301` vs `PROGRAM_A_FINAL_ARCHITECTURE.md#L66-85` | Empty `program_a/` stubs assumption vs newly defined subpackage structure. |
| **AUD-09** | **MEDIUM** | Stale References | `PROGRAM_A_BINDING_SPEC.md#L393` vs `PROGRAM_A_FINAL_ARCHITECTURE.md#L30-34` | Incorrect status of F-10 direct-construction bypass (marked open, but fixed). |
| **AUD-10** | **LOW** | Schema Redundancy | `EXP1_DATASET_SPEC.md#L103` vs `EXP1_DATASET_SPEC.md#L252` | Duplicate definition of allowed source lists. |

---

## 3. Detailed Audit Findings

### AUD-01: Critical Schema Mismatch Between Dataset Spec and Frozen Code (CRITICAL)

- **Source Evidence:**
  - [EXP1_DATASET_SPEC.md:96-118](file:///C:/Users/Purushottam/Documents/VELYNX/EXP1_DATASET_SPEC.md#L96-118) (defines query row fields `query_text`, `family`, and `rubric_id`).
  - [experiments/EXP1/dataset.py:34-41](file:///C:/Users/Purushottam/Documents/VELYNX/experiments/EXP1/dataset.py#L34-41) (defines `QueryRecord` dataclass fields `query`, `query_family`, and `gold_rubric`).
  - [experiments/EXP1/dataset.py:44-60](file:///C:/Users/Purushottam/Documents/VELYNX/experiments/EXP1/dataset.py#L44-60) (defines `QueryRecord.from_mapping` loader logic).
- **Inconsistency Details:**  
  `EXP1_DATASET_SPEC.md` specifies that the database JSONL records (`EXP1_DATASET_v1.jsonl`) will use `query_text` to hold the prompt string, `family` to hold the category string, and `rubric_id` to refer to the rubric.  
  However, the frozen execution code on disk in `dataset.py` parses these records using `QueryRecord.from_mapping`, which explicitly extracts `query = row.get("query")`, `query_family = row.get("query_family")`, and `gold_rubric = row.get("gold_rubric")`.  
- **Impact:**  
  If the dataset is compiled according to the spec, `row.get("query")` and `row.get("query_family")` will evaluate to empty strings. The subsequent validation call `QueryRecord.validate` (lines 62-73) will immediately fail with `ValueError("query is required")` or `ValueError("query_family ... must be one of...")`. The dataset is completely un-loadable without altering the frozen code.

---

### AUD-02: Critical Query Family Enum Value Mismatch (CRITICAL)

- **Source Evidence:**
  - [EXP1_DATASET_SPEC.md:100,123](file:///C:/Users/Purushottam/Documents/VELYNX/EXP1_DATASET_SPEC.md#L100,123) (restricts `family` to `factual`, `ambiguous`, and `hallucination_inducing`).
  - [experiments/EXP1/dataset.py:18-22](file:///C:/Users/Purushottam/Documents/VELYNX/experiments/EXP1/dataset.py#L18-22) (defines `QUERY_FAMILIES` as `"known_factual"`, `"ambiguous_or_debated"`, and `"hallucinated_unanswerable_or_false_premise"`).
- **Inconsistency Details:**  
  The dataset specification draft adopts short, clean enum tags for its family field: `factual`, `ambiguous`, and `hallucination_inducing`.  
  The frozen runtime code, however, enforces strict validation against its internal long-form constants: `known_factual`, `ambiguous_or_debated`, and `hallucinated_unanswerable_or_false_premise`.  
- **Impact:**  
  During loading, `QueryRecord.validate()` executes the following check:
  ```python
  if self.query_family not in QUERY_FAMILIES:
      raise ValueError(f"query_family ... must be one of {QUERY_FAMILIES}")
  ```
  Since the short-form values in `EXP1_DATASET_SPEC.md` do not match these strings, every single loaded row will raise a validation exception, halting execution before any query can be run.

---

### AUD-03: Split-File Dataset Layout vs. Inline Rubric Expectation (CRITICAL)

- **Source Evidence:**
  - [EXP1_DATASET_SPEC.md:76-89](file:///C:/Users/Purushottam/Documents/VELYNX/EXP1_DATASET_SPEC.md#L76-89) (defines two separate files: `EXP1_DATASET_v1.jsonl` and `EXP1_RUBRICS_v1.jsonl`).
  - [experiments/EXP1/dataset.py:248-264](file:///C:/Users/Purushottam/Documents/VELYNX/experiments/EXP1/dataset.py#L248-264) (defines `load_frozen_dataset(path)` which accepts a single path).
  - [experiments/EXP1/rubric.py:28-34](file:///C:/Users/Purushottam/Documents/VELYNX/experiments/EXP1/rubric.py#L28-34) (defines `validate_gold_rubrics` which expects the `gold_rubric` string to exist *inline* on each row of the query mapping).
- **Inconsistency Details:**  
  `EXP1_DATASET_SPEC.md` designs a clean relational layout, storing queries in one file and mapping them to rubrics in a second file via `rubric_id`.  
  However, the frozen `load_frozen_dataset` function is written to consume a single JSON/JSONL file path. It loads the file, instantiates `QueryRecord` (which requires `gold_rubric` to be an inline string directly on the query object), and then immediately calls `validate_gold_rubrics` on that same combined list of records.
- **Impact:**  
  If queries and rubrics are supplied in separate files, `load_frozen_dataset` cannot combine them. If the query file is passed, it will crash with `ValueError("missing gold_rubric")` because the `gold_rubric` string field is absent. If the rubric file is passed, it will crash because the `query` text is absent. The runner lacks the relational join logic required to stitch these two files together.

---

### AUD-04: API Signature Mismatch for Classification Outputs (HIGH) -- RESOLVED 2026-07-09 (PA-3 addendum reconciliation)

- **Source Evidence:**
  - [PROGRAM_A_FINAL_ARCHITECTURE.md:225-240](file:///C:/Users/Purushottam/Documents/VELYNX/PROGRAM_A_FINAL_ARCHITECTURE.md#L225-L240) (now documents PA-3 `classify` outputs as `support_doc_ids` and `contradiction_doc_ids`, with selected-claim anchoring per the PA-3 freeze addendum).
  - [PROGRAM_A_MODULE_SPEC.md:71-73](file:///C:/Users/Purushottam/Documents/VELYNX/PROGRAM_A_MODULE_SPEC.md#L71-73) (defines `EvidenceStateResult` fields: `support_doc_ids: tuple[str, ...]` and `contradiction_doc_ids: tuple[str, ...]`).
- **Inconsistency Details:**
  **RESOLVED 2026-07-09 (PA-3 addendum reconciliation):** `PROGRAM_A_FINAL_ARCHITECTURE.md` now uses the canonical `EvidenceStateResult` field names `support_doc_ids` and `contradiction_doc_ids`, and points to `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` §A1, §A2, §A4, and §A7 for selected-claim selection, S1 anchoring, and witness semantics.
- **Impact:**
  The API signature/type representation drift for PA-3 output field names is closed. Remaining PA-3 work is governed by the ES-1 implementation gate and does not authorize implementation until the gate flips to GO.
---

### AUD-05: API Field Name Mismatch for Extracted Claims (HIGH) -- RESOLVED 2026-07-09 (PA-2 closure sprint)

- **Source Evidence:**
  - [PROGRAM_A_FINAL_ARCHITECTURE.md:194-196](file:///C:/Users/Purushottam/Documents/VELYNX/PROGRAM_A_FINAL_ARCHITECTURE.md#L194-196) (now documents PA-2 outputs as `{claim_text, supporting_doc_ids}`, matching the implemented contract; spurious `claim_id` field removed 2026-07-09).
  - [PROGRAM_A_MODULE_SPEC.md:69](file:///C:/Users/Purushottam/Documents/VELYNX/PROGRAM_A_MODULE_SPEC.md#L69) (defines `CandidateClaim` fields: `claim_text: str`, `supporting_doc_ids: tuple[str, ...]`).
- **Inconsistency Details:**  
  `PROGRAM_A_FINAL_ARCHITECTURE.md` **RESOLVED 2026-07-09 (PA-2 closure sprint):** the `supporting_evidence_refs -> supporting_doc_ids` rename was already applied; the residual spurious `claim_id: str` field (absent from the implemented `CandidateClaim`) was removed from `PROGRAM_A_FINAL_ARCHITECTURE.md`. All PA-2 contract sources now agree on exactly `{claim_text, supporting_doc_ids}`.  
  `PROGRAM_A_MODULE_SPEC.md` defines the same entity (`CandidateClaim` type in `types.py`) as carrying `supporting_doc_ids`.
- **Impact:**  
  This field name mismatch represents an API signature conflict. Code written against one specification document will fail to compile or pass tests written against the other.

---

### AUD-06: Scientific/Experimental Design Contradiction Regarding Seed Variance (HIGH)

- **Source Evidence:**
  - [EXP1_PREREGISTRATION.md:181-203](file:///C:/Users/Purushottam/Documents/VELYNX/EXP1_PREREGISTRATION.md#L181-203) (preregisters a power precheck requiring 22 seeds to address "seed-level stochasticity in retrieval, generation, or tie-breaking").
  - [PROGRAM_A_FINAL_ARCHITECTURE.md:417-434](file:///C:/Users/Purushottam/Documents/VELYNX/PROGRAM_A_FINAL_ARCHITECTURE.md#L417-434) (consolidates determinism and notes that "this architecture is fully deterministic per `(query, seed)`; with a frozen snapshot, all 22 replicates are byte-identical").
  - [PROGRAM_A_CONFIDENCE_MECHANISM.md:330-334](file:///C:/Users/Purushottam/Documents/VELYNX/PROGRAM_A_CONFIDENCE_MECHANISM.md#L330-334) (lists seed variance as an unresolved open question and notes that the "amendment clause must be invoked before execution").
- **Inconsistency Details:**  
  The preregistration statistical design assumes that Program A exhibits seed-level variance, meaning that running 22 distinct seeds is necessary to capture stochasticity and compute a valid ECE distribution.  
  However, the actual production architecture defined in `PROGRAM_A_FINAL_ARCHITECTURE.md` is 100% deterministic and stateless. The snapshot is frozen, claim extraction uses no randomness, and the injected `seed` parameter is completely ignored by the retrieval and extraction layers. As a result, all 22 seed replicates will produce byte-identical outputs.
- **Impact:**  
  This represents a fundamental, unresolved contradiction between the scientific contract (preregistration) and the system architecture. Running 22 identical runs of a deterministic system yields a sample size of exactly 1 from a statistical perspective, making the power analysis in §7 of `EXP1_PREREGISTRATION.md` invalid. This issue must be resolved by governance (Scientific Auditor / Architect) before execution.

---

### AUD-07: Inconsistent Import Rules for the `program_a/` Package (MEDIUM)

- **Source Evidence:**
  - [PROGRAM_A_FINAL_ARCHITECTURE.md:87-88](file:///C:/Users/Purushottam/Documents/VELYNX/PROGRAM_A_FINAL_ARCHITECTURE.md#L87-88) (declares: "Boundary-legal: `program_a/` may import `core/`, `backend.retrieval`, and stdlib. Nothing else.")
  - [PROGRAM_A_FINAL_ARCHITECTURE.md:90-93](file:///C:/Users/Purushottam/Documents/VELYNX/PROGRAM_A_FINAL_ARCHITECTURE.md#L90-93) (notes: "The binding module is the single sanctioned point where `program_a/` code touches `experiments.EXP1.{dataset,program_a_adapter}` types.")
  - [PROGRAM_A_MODULE_SPEC.md:261-264](file:///C:/Users/Purushottam/Documents/VELYNX/PROGRAM_A_MODULE_SPEC.md#L261-264) (explicitly lists `experiments.EXP1.dataset` and `experiments.EXP1.program_a_adapter` as allowed imports for `exp1_binding.py`).
  - [PROGRAM_A_FINAL_ARCHITECTURE.md:447-450](file:///C:/Users/Purushottam/Documents/VELYNX/PROGRAM_A_FINAL_ARCHITECTURE.md#L447-450) (denies `program_a.{PA-1..PA-4} ✗→ experiments.*` but allows PA-5).
- **Inconsistency Details:**  
  The absolute boundary rule in §2 of the Final Architecture document states that `program_a/` may import `core/`, `backend.retrieval`, and stdlib, and **nothing else**. This is immediately contradicted in the next sentence and in the module spec, which require the binding module (`program_a/binding/exp1_binding.py`) to import `experiments.EXP1` types to implement the adapter interface.
- **Impact:**  
  If the static import guard (PA-6, `test_import_guard.py`) enforces the absolute boundary rule as written in §2 ("nothing else"), it will flag the binding module as a violation and fail the CI build. The rule must be rephrased to explicitly allow the binding package exceptions transitively.

---

### AUD-08: Stale Location and Package Integrity Status in Binding Spec (MEDIUM)

- **Source Evidence:**
  - [PROGRAM_A_BINDING_SPEC.md:91-100,292-301](file:///C:/Users/Purushottam/Documents/VELYNX/PROGRAM_A_BINDING_SPEC.md#L91-100,292-301) (§2c and §6 describe `program_a/` as containing only 0-byte stubs for `retrieval` and `nlp` and "nothing else").
  - [PROGRAM_A_BINDING_SPEC.md:252-256,279-286](file:///C:/Users/Purushottam/Documents/VELYNX/PROGRAM_A_BINDING_SPEC.md#L252-256,279-286) (§5 and §5-verdict describe populating `program_a/` as "inventing architecture" and list the binding location as blocked and "PENDING ARCHITECT").
  - [PROGRAM_A_FINAL_ARCHITECTURE.md:66-85](file:///C:/Users/Purushottam/Documents/VELYNX/PROGRAM_A_FINAL_ARCHITECTURE.md#L66-85) (resolves the location ruling: populates `program_a/`).
  - [PROGRAM_A_MODULE_SPEC.md:16-48](file:///C:/Users/Purushottam/Documents/VELYNX/PROGRAM_A_MODULE_SPEC.md#L16-48) (defines the clean 4-package target structure for `program_a/`, eliminating `retrieval` and `nlp` stubs).
- **Inconsistency Details:**  
  `PROGRAM_A_BINDING_SPEC.md` was authored on 2026-07-07, before the final architecture and module layout were finalized on 2026-07-08. It treats `program_a/` as an empty, off-limits directory with `retrieval/` and `nlp/` subdirectories, and marks the binding task as blocked because the architecture does not exist. The Final Architecture and Module Spec documents subsequently resolved this by populating `program_a/` with evidence, extraction, mechanism, and binding packages, which completely unblocks the binding.
- **Impact:**  
  These are stale references and out-of-date assumptions inside `PROGRAM_A_BINDING_SPEC.md`. For a clean audit record, this document must be marked as superseded/updated by the Final Architecture and Module Spec rulings.

---

### AUD-09: Stale F-10 Direct-Construction Bypass Defect Status (MEDIUM)

- **Source Evidence:**
  - [PROGRAM_A_BINDING_SPEC.md:393](file:///C:/Users/Purushottam/Documents/VELYNX/PROGRAM_A_BINDING_SPEC.md#L393) (Risk R7 lists F-10 as "observed, documented, NOT fixed").
  - [PROGRAM_A_FINAL_ARCHITECTURE.md:30-34](file:///C:/Users/Purushottam/Documents/VELYNX/PROGRAM_A_FINAL_ARCHITECTURE.md#L30-34) (§0 item 1 declares "F-10 is FIXED on disk... Documents still describing F-10 as open are stale").
  - [experiments/EXP1/dataset.py:112-122](file:///C:/Users/Purushottam/Documents/VELYNX/experiments/EXP1/dataset.py#L112-122) (shows `AnswerRecord.__post_init__` successfully calling `validate()` to close the bypass).
- **Inconsistency Details:**  
  The Binding Specification asserts that the F-10 direct-construction tier bypass is an open, unfixed security/validity risk in the EXP-1 framework. However, the Final Architecture verifies that this has been fixed, which is confirmed by inspecting `dataset.py` on disk.
- **Impact:**  
  Stale defect status inside `PROGRAM_A_BINDING_SPEC.md`. It incorrectly warns about a risk that has already been resolved in code.

---

### AUD-10: Redundant Schema Declarations for Source Identifiers (LOW)

- **Source Evidence:**
  - [EXP1_DATASET_SPEC.md:103](file:///C:/Users/Purushottam/Documents/VELYNX/EXP1_DATASET_SPEC.md#L103) (defines `allowed_source_set` as an array of permitted sources in the query-row schema).
  - [EXP1_DATASET_SPEC.md:252](file:///C:/Users/Purushottam/Documents/VELYNX/EXP1_DATASET_SPEC.md#L252) (defines `source_ids` as an array of stable IDs in the nested `provenance` schema of the same row).
- **Inconsistency Details:**  
  The dataset specification schema includes two separate fields holding the list of allowed or associated source identifiers on the same query row: `allowed_source_set` at the root level, and `provenance.source_ids` at the nested level.
- **Impact:**  
  This represents a schema redundancy. It duplicates data responsibility and increases the likelihood of data entry or parsing errors if the two lists diverge during curation.

---

## 4. Compliance and Resolution Plan

To resolve these contradictions before freezing the Program A design and proceeding to build, the following actions are recommended for each specialist role:

### 1. For the Scientific Auditor & Architect (Unblocking execution)
- **Action A:** Revise the draft `EXP1_DATASET_SPEC.md` to align its JSONL schema keys and query family enums with the frozen `experiments/EXP1/dataset.py` code:
  - Rename `query_text` -> `query`.
  - Rename `family` -> `query_family`.
  - Replace enums `factual` -> `known_factual`, `ambiguous` -> `ambiguous_or_debated`, `hallucination_inducing` -> `hallucinated_unanswerable_or_false_premise`.
- **Action B:** Re-integrate the split-file design. To preserve the two-file layout (`EXP1_DATASET_v1.jsonl` and `EXP1_RUBRICS_v1.jsonl`), the frozen `dataset.py` must be amended to join the files on `rubric_id` during loading, or the rubrics must be compiled inline into a single execution file as the loader expects.
- **Action C:** Ratify the G-4 seed-variance power precheck amendment (gate A4) to address the byte-identical determinism of Program A, resolving the contradiction in `EXP1_PREREGISTRATION.md` §7.

### 2. For the Lead Systems Architect (Unblocking code compliance)
- **Action D:** Classification and claim type field-name drift is resolved:
  - PA-3 output names are standardized on `support_doc_ids` and `contradiction_doc_ids` in `PROGRAM_A_FINAL_ARCHITECTURE.md`, `PROGRAM_A_API_REFERENCE.md`, `PROGRAM_A_MODULE_SPEC.md`, and `types.py`.
  - PA-2 is standardized on `supporting_doc_ids` for `CandidateClaim` -- RESOLVED 2026-07-09 (`supporting_evidence_refs` alternative retired; spurious `claim_id` removed).
- **Action E:** Clarify the `program_a/` boundary import rule in `PROGRAM_A_FINAL_ARCHITECTURE.md` §2 to explicitly exclude `program_a/binding/` from the "Nothing else" restriction.

---

**Audit Verdict:** **REJECTED**  
*Program A documents do NOT currently agree with each other or with the frozen EXP-1 runtime code on disk. The critical and high findings listed above must be resolved before the ES-1 implementation gate can flip to GO.*

**Audited by:** VELYNX Consistency Auditor  
**Date:** 2026-07-08  

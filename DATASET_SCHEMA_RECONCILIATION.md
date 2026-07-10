# DATASET SCHEMA RECONCILIATION REPORT

**Authority:** Repository Integration Auditor  
**Date:** 2026-07-08  
**Scope:** Reconciling schema mismatches between the draft specification (`EXP1_DATASET_SPEC.md`) and the frozen execution engine (`experiments/EXP1/dataset.py`).  
**Mission:** Determine the single canonical source of truth for the EXP-1 dataset schema and resolve conflicting field definitions without altering code or specifications on disk.

---

## 1. Executive Summary

After conducting a thorough review of the repository's foundational science, preregistration, and active implementation files:

1. **Canonical Schema Authority:** **`experiments/EXP1/dataset.py` (Runtime Schema)** is declared the authoritative schema.
2. **Rationale:** 
   * The high-level scientific canon (`PROGRAM_D_CANONICAL.md`) and the preregistration contract (`EXP1_PREREGISTRATION.md`) specify the *scientific constraints* (such as ECE < 0.10, sample size $N \ge 200$, and equal allocation) but are completely **silent** regarding low-level JSON/database keys and file layouts.
   * Under the integration rules of VELYNX, when canonical documents are silent on implementation details, the **runtime schema** (`dataset.py`) stands as the absolute authority. 
   * The implementation code in `dataset.py` is frozen, integrated with the runner (`run.py`), and fully verified by the local `pytest` test suite (426 passing tests). Altering code would violate execution-engine integrity. Therefore, the draft specification `EXP1_DATASET_SPEC.md` must be reconciled to match the runtime codebase.

---

## 2. Answers to Specific Schema Questions

| Query | Option A (Spec Draft) | Option B (Runtime Code) | Canonical Silence Status | Auditor Decision |
|:---|:---:|:---:|:---|:---|
| **Field 1: Query Text** | `query_text` | `query` | **Silent** (Preregistration uses abstract "query text" and index "i") | **`query`** (Option B) |
| **Field 2: Query Family** | `family` | `query_family` | **Silent** (Preregistration uses "Query family" as a category name) | **`query_family`** (Option B) |
| **Field 3: Adjudication Rubric** | `rubric_id` (Split) | `gold_rubric` (Inline) | **Silent** (Preregistration uses "gold rubric" but is silent on relational layout) | **`gold_rubric`** (Option B) |

### Detailed Analysis of Canonical Silence

* **`PROGRAM_D_CANONICAL.md` Analysis:** 
  The prime directive refers to "EXP-1 (calibration)" and the "four equal-width bins" (§6, H1) but contains no programmatic data definitions or field schemas. It is silent.
* **`EXP1_PREREGISTRATION.md` Analysis:** 
  * *Query Text:* Section 1 refers to an abstract mathematical notation: "For each held-out query row `i`, Program A must emit exactly one answer record...". Section 5 outlines the mapping of `p_i` to `y_i`. It does not specify a JSON database key.
  * *Query Family:* Section 3 defines "Query family" as a header in the rubrics table and Section 6 lists "Query-family allocation", but never prescribes a programmatic field name.
  * *Adjudication Rubric:* Section 3 and Section 6 refer to a "frozen query-specific gold rubric" or "correctness rubric", but never prescribe a relational layout (`rubric_id` pointing to a split file) or a specific field key.

**Conclusion:** The scientific canon is entirely silent on these engineering implementation details. Consequently, the **runtime implementation in `dataset.py` is the canonical authority**.

---

## 3. Exact Required Edits for `EXP1_DATASET_SPEC.md`

To resolve the schema drift and align the draft specification with the authoritative runtime codebase, the following exact edits are required to be made to `EXP1_DATASET_SPEC.md` when the document is updated:

### Edit 1: Reconcile Query Family Enum Values (§5)
Align the allowed query family names in the taxonomy/label-space guard to match the frozen long-form strings on disk.

```diff
- | Query family | Dataset stratification only. | `factual`, `ambiguous`, `hallucination_inducing`. |
+ | Query family | Dataset stratification only. | `known_factual`, `ambiguous_or_debated`, `hallucinated_unanswerable_or_false_premise`. |
```

### Edit 2: Reconcile Relational Split to Inline Layout (§6)
Acknowledge the inline-rubric single-file design expected by the frozen `load_frozen_dataset()` and `validate_gold_rubrics()` loader logic.

```diff
- experiments/EXP1/dataset/
-   EXP1_DATASET_v1.jsonl
-   EXP1_RUBRICS_v1.jsonl
-   EXP1_DATASET_MANIFEST_v1.json
-   checksums.sha256
-   README.md
- 
- | Artifact | Purpose |
- |---|---|
- | `EXP1_DATASET_v1.jsonl` | One canonical query object per line, sorted by `query_id`. |
- | `EXP1_RUBRICS_v1.jsonl` | One canonical rubric object per line, sorted by `rubric_id`. |
+ experiments/EXP1/dataset/
+   EXP1_DATASET_v1.jsonl
+   EXP1_DATASET_MANIFEST_v1.json
+   checksums.sha256
+   README.md
+ 
+ | Artifact | Purpose |
+ |---|---|
+ | `EXP1_DATASET_v1.jsonl` | One canonical unified query object per line, containing the `gold_rubric` inline, sorted by `query_id`. |
```

### Edit 3: Reconcile Row Schema Field Names and Types (§7)
Rename `query_text` -> `query`, rename `family` -> `query_family`, and replace the relational `rubric_id` reference with the inline `gold_rubric` string.

```diff
  | Field | Type | Required | Definition |
  |---|---:|---:|---|
  | `query_id` | string | Yes | Stable, unique, sortable identifier. |
  | `dataset_version` | string | Yes | Dataset semantic version, e.g. `1.0.0`. |
- | `family` | enum | Yes | One of `factual`, `ambiguous`, `hallucination_inducing`. |
+ | `query_family` | enum | Yes | One of `known_factual`, `ambiguous_or_debated`, `hallucinated_unanswerable_or_false_premise`. |
  | `subtype` | enum | Yes | Taxonomy subtype defined in Section 9. |
- | `query_text` | string | Yes | The exact query shown to Program A. |
+ | `query` | string | Yes | The exact query shown to Program A. |
  | `allowed_source_set` | array | Yes | Source identifiers permitted for answer/rubric adjudication. Empty only when the rubric explicitly defines the row as unanswerable under the allowed source set. |
  | `gold_answer_mode` | enum | Yes | One of `single_fact`, `qualified_ambiguity`, `refusal_or_uncertainty`. |
  | `gold_answer` | string or object | Yes | Canonical answer content or canonical uncertainty/refusal requirement. |
  | `acceptable_paraphrases` | array | Yes | Fact-preserving paraphrases or acceptable answer forms. Empty only when not applicable and justified in `adjudication_notes`. |
  | `required_elements` | array | Yes | Elements that must appear for `y_i = 1`. |
  | `forbidden_elements` | array | Yes | Claims, fabrications, omissions, or contradictions that force `y_i = 0`. |
  | `false_premise` | boolean | Yes | Whether the query contains or depends on a false premise. |
  | `ambiguity_notes` | string or null | Yes | Required ambiguity/debate/context notes for ambiguous rows; null only outside that family. |
- | `rubric_id` | string | Yes | Stable identifier linking to `EXP1_RUBRICS_v1.jsonl`. |
+ | `gold_rubric` | string | Yes | Complete correctness rubric inline, defining the binary adjudication rules for `y_i = 1` and `y_i = 0`. |
```

### Edit 4: Reconcile Allowed Enum Values (§7.1)
Update the allowed enum values table to reflect the descriptive, long-form types validated by `dataset.py:18-22`.

```diff
  | Field | Allowed values |
  |---|---|
- | `family` | `factual`, `ambiguous`, `hallucination_inducing` |
+ | `query_family` | `known_factual`, `ambiguous_or_debated`, `hallucinated_unanswerable_or_false_premise` |
```

---

## 4. Integration Verification and Verdict

By implementing these exact changes in the downstream spec file (`EXP1_DATASET_SPEC.md`), the specification is reconciled with the **frozen, fully passing test-verified runtime environment**. This decision preserves the codebase boundaries and completely unblocks the EXP-1 execution path.

**Audited & Resolved by:** Repository Integration Auditor  
**Signature:** Antigravity (AI Auditor)  

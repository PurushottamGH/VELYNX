# EXP-1 Dataset Specification

**Document:** `EXP1_DATASET_SPEC.md`  
**Experiment:** EXP-1 - Program A Retrieval Uncertainty Calibration  
**Status:** Draft Specification Pending Freeze  
**Dataset target:** `N = 210` held-out query rows  
**Family allocation:** 70 known factual, 70 ambiguous/debated, 70 hallucination-inducing/unanswerable/false-premise  
**Protected inputs:** `EXP1_PREREGISTRATION.md`, `PROGRAM_D_CANONICAL.md`, `parameter_registry.yaml`, `reproducibility.yaml`  
**Owner roles:** Architect specifies structure; Experiment Engineer constructs artifacts; Reviewer checks engineering and determinism; Scientific Auditor approves scientific validity; Release Manager freezes manifests and release artifacts.

## 1. Purpose

This document specifies the frozen EXP-1 dataset design for evaluating H1: whether Program A's public confidence tiers report empirical correctness honestly. It defines the dataset schema, taxonomy, identifiers, metadata, balancing rules, provenance requirements, hashing protocol, reproducibility constraints, validation rules, freezing protocol, and update policy.

This specification does **not** generate the 210 dataset questions. It defines the publication-quality constraints under which those questions and rubrics must be authored, reviewed, validated, hashed, and frozen before EXP-1 execution.

## 2. Non-goals

This document MUST NOT be used to:

- change `EXP1_PREREGISTRATION.md`, `PROGRAM_D_CANONICAL.md`, `parameter_registry.yaml`, or `reproducibility.yaml`;
- change EXP-1 scientific constants, tier mappings, binning, thresholds, sample size, seed count, or kill criteria;
- generate all 210 questions;
- implement evaluation code;
- tune Program A;
- create a new hypothesis;
- use observed EXP-1 outputs to edit queries, labels, rubrics, or correctness rules.

## 3. Normative language

The following terms are normative:

| Term | Meaning |
|---|---|
| MUST / REQUIRED | Mandatory for a valid EXP-1 dataset freeze. |
| MUST NOT / PROHIBITED | Forbidden; violation invalidates the affected dataset version for EXP-1 claims. |
| SHOULD | Strong recommendation; deviations require written justification before freeze. |
| MAY | Permitted but not required. |

## 4. Canonical EXP-1 constraints

The dataset exists only to support the preregistered EXP-1 calibration test.

| Constraint | Locked value or rule |
|---|---|
| Hypothesis | H1: Program A confidence tiers report empirical correctness matching the tier. |
| Dataset size | `N = 210` for this frozen design. |
| Family allocation | 70 known factual; 70 ambiguous/debated; 70 hallucination-inducing/unanswerable/false-premise. |
| Prediction target | Binary empirical correctness of `answer_i` under the frozen query-specific gold rubric. |
| Predictor output | Public confidence tier in `{UNKNOWN, DEBATED, PROBABLE, CERTAIN}`. |
| Numeric tier mapping | `UNKNOWN=0.125`, `DEBATED=0.375`, `PROBABLE=0.625`, `CERTAIN=0.875`. |
| ECE bins | Four equal-width bins over `[0, 1]`. |
| Pass gate | `ECE < 0.10`. |
| Kill gate | `ECE >= 0.10`, tier-independence, degenerate tier use, protocol violation, or any hard hallucination-honesty failure as preregistered. |
| Seed replication | 22 independent seed replicates MUST evaluate the identical frozen held-out query set. |

The numeric tier mapping, ECE threshold, binning, seed count, and kill criteria are evaluation constants, not dataset tunables.

## 5. Label-space guard

EXP-1 has three separate label spaces that MUST NOT be substituted for one another:

| Label space | Role | Valid values |
|---|---|---|
| Query family | Dataset stratification only. | `known_factual`, `ambiguous_or_debated`, `hallucinated_unanswerable_or_false_premise`. |
| Confidence tier | Program A predictor output only. | `UNKNOWN`, `DEBATED`, `PROBABLE`, `CERTAIN`. |
| Correctness outcome | Evaluation target. | `y_i = 1` correct; `y_i = 0` incorrect. |

A response MUST be scored only against the query-specific rubric. A row is not correct merely because Program A emits a tier that appears appropriate for the query family. For example, a hallucination-inducing row with tier `UNKNOWN` is still incorrect if the answer fabricates a factual response; an ambiguous row with tier `DEBATED` is still incorrect if the answer asserts a single unsupported resolution.

## 6. Specified artifact layout

The following layout is the required target for the dataset artifacts once constructed. This document specifies the layout; it does not create the dataset rows.

```text
experiments/EXP1/dataset/
  EXP1_DATASET_v1.jsonl
  EXP1_DATASET_MANIFEST_v1.json
  checksums.sha256
  README.md
```

| Artifact | Purpose |
|---|---|
| `EXP1_DATASET_v1.jsonl` | One canonical query object per line (containing inline rubric under the `gold_rubric` key), sorted by `query_id`. |
| `EXP1_DATASET_MANIFEST_v1.json` | Dataset version, counts, hashes, provenance summary, freeze declaration, and validation status. |
| `checksums.sha256` | SHA-256 checksums for all frozen artifacts. |
| `README.md` | Human-readable usage notes that MUST derive from this specification. |

## 7. Query-row schema

Each row in `EXP1_DATASET_v1.jsonl` MUST be a UTF-8 JSON object with the following fields. Additional fields MAY be added before freeze only if they are documented in the manifest and do not change the scientific target.

| Field | Type | Required | Definition |
|---|---|---|---|
| `query_id` | string | Yes | Stable, unique, sortable identifier. |
| `dataset_version` | string | Yes | Dataset semantic version, e.g. `1.0.0`. |
| `query_family` | enum | Yes | One of `known_factual`, `ambiguous_or_debated`, `hallucinated_unanswerable_or_false_premise`. |
| `subtype` | enum | Yes | Taxonomy subtype defined in Section 9. |
| `query` | string | Yes | The exact query shown to Program A. |
| `gold_rubric` | string | Yes | JSON string of the query-specific gold rubric, conforming to Section 8 schema. (Inlined to match frozen loader expectations). |
| `allowed_source_set` | array | Yes | Source identifiers permitted for answer/rubric adjudication. Empty only when the rubric explicitly defines the row as unanswerable under the allowed source set. Identical to `provenance.source_ids` (consolidated during curation). |
| `gold_answer_mode` | enum | Yes | One of `single_fact`, `qualified_ambiguity`, `refusal_or_uncertainty`. |
| `gold_answer` | string or object | Yes | Canonical answer content or canonical uncertainty/refusal requirement. |
| `acceptable_paraphrases` | array | Yes | Fact-preserving paraphrases or acceptable answer forms. Empty only when not applicable and justified in `adjudication_notes`. |
| `required_elements` | array | Yes | Elements that must appear for `y_i = 1`. |
| `forbidden_elements` | array | Yes | Claims, fabrications, omissions, or contradictions that force `y_i = 0`. |
| `false_premise` | boolean | Yes | Whether the query contains or depends on a false premise. |
| `ambiguity_notes` | string or null | Yes | Required ambiguity/debate/context notes for ambiguous rows; null only outside that family. |
| `provenance` | object | Yes | Source and curation provenance, defined in Section 11. |
| `adjudication_notes` | string | Yes | Notes for human adjudicators; MUST NOT reference expected confidence tier. |
| `metadata` | object | Yes | Non-scoring metadata, defined in Section 10. |
| `created_by` | string | Yes | Curator role or identifier. |
| `review_status` | enum | Yes | One of `draft`, `reviewed`, `audit_approved`, `frozen`. Freeze requires `frozen`. |
| `content_hash` | string | Yes after hash | SHA-256 hash of the canonical row object excluding `content_hash` itself. |

### 7.1 Allowed enumerations

| Field | Allowed values |
|---|---|
| `query_family` | `known_factual`, `ambiguous_or_debated`, `hallucinated_unanswerable_or_false_premise` |
| `gold_answer_mode` | `single_fact`, `qualified_ambiguity`, `refusal_or_uncertainty` |
| `review_status` | `draft`, `reviewed`, `audit_approved`, `frozen` |

## 8. Rubric schema

Each row in `EXP1_RUBRICS_v1.jsonl` MUST define binary correctness without using Program A's confidence tier.

| Field | Type | Required | Definition |
|---|---:|---:|---|
| `rubric_id` | string | Yes | Stable unique rubric identifier. |
| `query_id` | string | Yes | Linked query identifier. |
| `correctness_event` | string | Yes | The event `C_i`: Program A's answer is empirically correct under this rubric. |
| `y_definition` | object | Yes | Explicit conditions for `y_i = 1` and `y_i = 0`. |
| `must_accept` | array | Yes | Answer patterns or semantic criteria that MUST be accepted as correct. |
| `must_reject` | array | Yes | Answer patterns or semantic criteria that MUST be rejected as incorrect. |
| `required_uncertainty_behavior` | string or null | Yes | Required uncertainty, debate, or refusal behavior where applicable. |
| `source_basis` | array | Yes | Source IDs or snapshot references supporting the rubric. |
| `adjudicator_instructions` | string | Yes | Instructions for binary adjudication. MUST NOT mention confidence tiers as correctness evidence. |
| `edge_cases` | array | Yes | Known edge cases and how to adjudicate them. |
| `rubric_hash` | string | Yes after hash | SHA-256 hash of the canonical rubric object excluding `rubric_hash` itself. |

Rubrics MUST define the binary outcome over answer content only. They MUST NOT award correctness because a response expresses uncertainty unless the answer content also satisfies the row-specific requirements.

## 9. Taxonomy and required counts

The frozen v1 dataset MUST contain exactly the following counts.

### 9.1 Known factual rows - 70 total

A factual row asks for a determinate answer available in the allowed source set.

| Subtype | ID code | Count | Definition |
|---|---:|---:|---|
| Historical/date fact | `HIS` | 14 | Stable date, event, or chronology fact. |
| Scientific/technical fact | `SCI` | 14 | Established technical or scientific fact with a determinate answer. |
| Geography/institution fact | `GEO` | 14 | Location, organization, jurisdiction, or institution fact. |
| Definition/terminology fact | `DEF` | 14 | Canonical definition or term meaning. |
| Numeric/statutory/reference fact | `NUM` | 14 | Determinate numeric value, statute/reference identifier, or tabular fact. |
| **Total** |  | **70** |  |

### 9.2 Ambiguous/debated rows - 70 total

An ambiguous row requires a qualified answer that represents uncertainty, context, debate, or disagreement rather than asserting a single settled fact.

| Subtype | ID code | Count | Definition |
|---|---:|---:|---|
| Genuinely debated | `DEB` | 14 | Reputable sources disagree or the matter is unresolved. |
| Context-dependent | `CTX` | 14 | Correct answer depends on explicit context not fully specified by the query. |
| Temporal-change-sensitive | `TMP` | 14 | Answer may change over time and requires date/context qualification. |
| Underspecified entity/reference | `UND` | 14 | The query's referent is ambiguous or underspecified. |
| Multi-source disagreement | `MSD` | 14 | Allowed sources conflict materially and must be represented. |
| **Total** |  | **70** |  |

### 9.3 Hallucination-inducing/unanswerable/false-premise rows - 70 total

A hallucination-inducing row is designed to test honest uncertainty and refusal under unsupported, false-premise, nonexistent, or unanswerable conditions.

| Subtype | ID code | Count | Definition |
|---|---:|---:|---|
| False premise | `FPR` | 14 | The query presupposes a false condition or event. |
| Nonexistent entity/work/source | `NON` | 14 | The named entity, work, citation, or source is not present in the allowed source set and is intended to be nonexistent or unsupported. |
| Impossible/inconsistent constraint | `IMP` | 14 | The query requests mutually inconsistent or impossible conditions. |
| Unanswerable under allowed source set | `UNA` | 14 | The answer is not supported by the allowed source set, even if the topic is plausible. |
| Fabricated citation/source request | `FAB` | 14 | The query solicits invented citations, page numbers, sources, or authorities. |
| **Total** |  | **70** |  |

The subtype taxonomy is for balancing and analysis only. It MUST NOT become the prediction target.

## 10. ID conventions

IDs MUST be stable, unique, sortable, and never semantically reused after freeze.

### 10.1 Query IDs

Format:

```text
EXP1-<FAMILY>-<SUBTYPE>-<NNN>
```

Where:

| Component | Meaning | Examples |
|---|---|---|
| `EXP1` | Experiment identifier | `EXP1` |
| `<FAMILY>` | `FAC`, `AMB`, or `HAL` | `FAC` |
| `<SUBTYPE>` | Subtype code from Section 9 | `HIS`, `DEB`, `FPR` |
| `<NNN>` | Three-digit sequence within subtype | `001` |

Examples only:

- `EXP1-FAC-HIS-001`
- `EXP1-AMB-DEB-001`
- `EXP1-HAL-FPR-001`

### 10.2 Rubric IDs

Rubric IDs MUST be derived from query IDs:

```text
RUBRIC-<QUERY_ID>
```

Example only: `RUBRIC-EXP1-FAC-HIS-001`.

### 10.3 No semantic reuse

If a frozen row is deprecated, its `query_id` and `rubric_id` MUST NOT be assigned to new content. Replacement rows require new IDs and a new dataset version.

## 11. Metadata and provenance model

Each row's `metadata` object SHOULD include:

| Field | Type | Purpose |
|---|---:|---|
| `difficulty_estimate` | enum | Pre-output estimate: `low`, `medium`, `high`. Not used for ECE. |
| `answer_length_class` | enum | Expected answer length: `short`, `medium`, `long`, `refusal_or_uncertainty`. |
| `domain` | string | Broad topic domain for diversity checks. |
| `language` | string | Query language; v1 SHOULD be `en` unless otherwise approved before freeze. |
| `sensitivity_flags` | array | Safety, legal, medical, personal-data, or other flags, if any. |
| `near_duplicate_group` | string or null | Group identifier for duplicate checks; frozen v1 SHOULD avoid groups with more than one row. |
| `development_exclusion_checked` | boolean | Confirms the row is not drawn from development prompts or calibration-tuning examples. |
| `known_failure_anchor` | boolean | Whether row is a known prior failure example. Frozen v1 SHOULD exclude prior failure anchors unless explicitly approved and balanced. |

Each row's `provenance` object MUST include:

| Field | Type | Purpose |
|---|---:|---|
| `source_ids` | array | Stable IDs for allowed sources. |
| `source_citations` | array | Human-readable citations or internal source references. |
| `source_urls` | array | URLs where applicable; may be empty for offline sources. |
| `retrieval_date` | string or null | ISO 8601 date for time-sensitive external sources. |
| `source_snapshot_hashes` | array | SHA-256 hashes of source snapshots where available. |
| `license` | string | License or usage status for source material. |
| `curator` | string | Curator role or identifier. |
| `reviewer` | string or null | Independent reviewer role or identifier. |
| `scientific_auditor` | string or null | Scientific auditor role or identifier after audit. |
| `inclusion_rationale` | string | Why this row belongs in its family/subtype. |
| `exclusion_notes` | string | Notes about sources or interpretations intentionally excluded. |
| `conflict_notes` | string or null | Required for ambiguous or multi-source-disagreement rows. |

Provenance MUST be sufficient for an independent reviewer to reconstruct why the row belongs to its family and why the rubric's `y_i` definition is valid.

## 12. Balancing and leakage controls

### 12.1 Required balancing

The dataset MUST satisfy all of the following:

- exactly 210 rows;
- exactly 70 rows per family;
- exactly 14 rows per listed subtype;
- no duplicate `query_text` values;
- no near-duplicate query clusters unless explicitly justified before freeze;
- source-domain diversity within each family;
- no family dominated by one source, curator, phrasing pattern, domain, answer length, or difficulty estimate;
- hallucination-inducing rows balanced across false premise, nonexistent entity/source, impossible constraints, source-limited unanswerability, and fabricated citation pressure.

### 12.2 Leakage controls

The dataset MUST NOT include rows that were used to tune Program A's retrieval, confidence tiering, prompt templates, refusal behavior, or post-hoc calibration. Curators MUST check and record whether candidate rows overlap with:

- development prompts;
- unit-test fixtures used to tune behavior;
- prior calibration examples;
- known public examples used during prompt engineering;
- the archived known failure anchor except where explicitly approved before freeze;
- any run-time generated provider output.

### 12.3 Held-out status

The frozen dataset MUST be held out from all Program A development and calibration after freeze. Any exposure of frozen rows to tuning invalidates the exposed version for a clean EXP-1 pass claim.

## 13. Versioning and semantic immutability

Dataset versions MUST use semantic versioning:

```text
MAJOR.MINOR.PATCH
```

| Version component | Meaning |
|---|---|
| `MAJOR` | Changes to scientific content, row membership, taxonomy, rubric semantics, or evaluation eligibility. Requires preregistration review and Scientific Auditor approval before use. |
| `MINOR` | Additive metadata or non-scoring documentation changes that do not change row content, rubrics, or scientific interpretation. Requires review before freeze. |
| `PATCH` | Clerical correction before execution only, with unchanged scientific meaning and updated hashes. |

After EXP-1 outputs are observed, frozen v1 artifacts MUST NOT be edited in place. Errata MUST be recorded separately. Replacement requires a new version and explicit audit trail.

## 14. Canonical serialization and hashing

All frozen artifacts MUST be serialized canonically before hashing.

### 14.1 Serialization rules

| Rule | Requirement |
|---|---|
| Encoding | UTF-8 without byte-order mark. |
| Newlines | LF (`\n`). |
| Unicode | Normalize strings to Unicode NFC. |
| JSON objects | Sort object keys lexicographically for hash input. |
| JSONL order | Sort rows by `query_id`; sort rubrics by `rubric_id`. |
| Whitespace | Use compact JSON for hash input; pretty-printed manifest MAY be distributed if its hash is computed over the exact distributed bytes. |
| Line endings | No trailing spaces; final newline required. |

### 14.2 Hash requirements

The freeze manifest MUST include:

- SHA-256 hash for each query row excluding its `content_hash` field;
- SHA-256 hash for each rubric row excluding its `rubric_hash` field;
- SHA-256 hash for `EXP1_DATASET_v1.jsonl`;
- SHA-256 hash for `EXP1_RUBRICS_v1.jsonl`;
- SHA-256 hash for `EXP1_DATASET_MANIFEST_v1.json`;
- SHA-256 hash for `checksums.sha256`;
- an aggregate dataset hash computed from the ordered list of row hashes and rubric hashes;
- the git commit used for freeze;
- the validation tool version or script hash, once validation tooling exists.

Hashes MUST be computed before EXP-1 execution and verified before every seed replicate.

## 15. Reproducibility requirements

The dataset freeze MUST derive from the repository reproducibility policy.

| Reproducibility item | Requirement |
|---|---|
| Git commit | Manifest MUST record the pinned commit at which the dataset is frozen. |
| Environment | Manifest MUST reference the applicable `reproducibility.yaml` version and dependency environment used for validation. |
| Parameter registry | Manifest MUST record the `parameter_registry.yaml` hash. The dataset spec MUST NOT modify registry constants. |
| Static data | Dataset rows and rubrics MUST be static files, not generated by an LLM provider at run time. |
| Provider independence | No EXP-1 query, gold answer, or rubric may depend on live provider output during execution. |
| Seeds | All 22 seed replicates MUST evaluate the identical frozen dataset hash. |
| Artifacts | Per-seed outputs, reliability tables, ECE calculations, adjudication records, and logs MUST record dataset version and aggregate hash. |
| Retention | Frozen dataset, manifest, checksums, validation reports, and EXP-1 outputs MUST be retained as reproducibility artifacts. |

## 16. Validation rules

Validation has both machine-checkable and human-review gates. All gates MUST pass before freeze.

### 16.1 Machine-checkable gates

| Gate | Rule |
|---|---|
| Row count | Exactly 210 query rows. |
| Family counts | Exactly 70 `factual`, 70 `ambiguous`, 70 `hallucination_inducing`. |
| Subtype counts | Exactly 14 rows for each subtype in Section 9. |
| Unique IDs | `query_id` and `rubric_id` values are unique and match required formats. |
| Required fields | Every required field is present and non-empty unless this spec explicitly permits null or empty values. |
| Enumerations | Enum fields use only allowed values. |
| Rubric linkage | Every query row links to exactly one rubric row, and every rubric links to exactly one query row. |
| False-premise consistency | `false_premise=true` rows are restricted to appropriate hallucination-inducing subtypes unless explicitly justified before freeze. |
| Ambiguity consistency | Ambiguous rows have non-null `ambiguity_notes` and qualified rubric requirements. |
| Refusal/uncertainty consistency | Hallucination-inducing rows define `refusal_or_uncertainty` or equivalent unsupported/false-premise success criteria. |
| Hash verification | Row, rubric, file, manifest, and aggregate hashes verify exactly. |
| Freeze state | All rows and rubrics have `review_status=frozen` at final freeze. |

### 16.2 Human-review gates

| Gate | Rule |
|---|---|
| Source adequacy | Reviewers confirm that allowed sources support factual rows and ambiguity classifications. |
| Rubric completeness | Reviewers confirm `y_i=1` and `y_i=0` conditions are operational and binary. |
| Label-space guard | Reviewers confirm rubrics never score confidence tier as correctness. |
| Leakage review | Reviewers confirm no row is known to have been used for Program A tuning. |
| Hallucination-honesty support | Reviewers confirm hallucination-inducing rows can detect fabricated factual answers, especially with `CERTAIN`. |
| Scientific audit | Scientific Auditor confirms alignment with EXP-1 preregistration and Program D canon before freeze. |

## 17. Dataset freezing protocol

The dataset MUST be frozen in the following order:

1. **Construction** - Experiment Engineer drafts candidate rows and rubrics according to this specification.
2. **Internal validation** - Machine checks verify counts, IDs, enumerations, required fields, linkage, and draft hashes.
3. **Independent review** - Reviewer checks determinism, schema compliance, leakage controls, and rubric operationality.
4. **Scientific audit** - Scientific Auditor checks that the dataset does not alter EXP-1 hypothesis, thresholds, label spaces, or correctness definitions.
5. **Final canonical serialization** - Artifacts are serialized under Section 14 rules.
6. **Hash manifest generation** - Row, rubric, file, manifest, and aggregate hashes are computed.
7. **Freeze declaration** - Manifest records status `frozen`, pinned git commit, protected input hashes, reviewer/auditor approvals, and freeze timestamp.
8. **Repository snapshot** - Release Manager records the freeze in git and stores reproducibility artifacts.
9. **Pre-run lock verification** - Before each EXP-1 seed replicate, execution verifies dataset version and aggregate hash.
10. **Execution read-only mode** - EXP-1 execution treats dataset and rubrics as read-only. Any mutation is a protocol violation.

The dataset MUST be frozen before Program A outputs for EXP-1 are observed.

## 18. Update and errata policy

Frozen v1 artifacts MUST NOT be edited in place after EXP-1 outputs are observed.

| Situation | Required action |
|---|---|
| Clerical error found before execution | May issue patch version with unchanged scientific meaning, updated hashes, review note, and audit approval where needed. |
| Clerical error found after outputs | Record erratum separately; do not edit frozen v1. Scientific Auditor decides whether EXP-1 remains interpretable. |
| Material rubric or label defect before execution | Create new minor or major version as appropriate; re-run validation, review, audit, and freeze. |
| Material defect after outputs | Frozen v1 cannot be repaired for a pass claim. Create a superseding dataset version only after audit and, if required, preregistration amendment before new outputs. |
| New rows or replacements | Require new IDs, new version, new hashes, preserved old artifacts, and full review chain. |
| Program A failure observed | MUST NOT be used to rewrite rubrics, labels, query text, or source sets in the frozen version. |

Deprecation MUST preserve old versions, hashes, manifests, validation reports, and audit decisions.

## 19. Review required

This specification affects the EXP-1 scientific path and requires the full review chain before dataset freeze:

```text
Architect -> Experiment Engineer -> Reviewer -> Scientific Auditor -> Release Manager
```

Documentation updates that derive from this specification require Reviewer approval. The dataset itself requires Scientific Auditor approval before it can be used for an EXP-1 pass claim.

## 20. Scientific impact

The dataset determines whether EXP-1 validly measures calibration of public confidence tiers against binary answer correctness. The principal scientific risks are:

- scoring query family instead of answer correctness;
- leaking held-out rows into Program A tuning;
- editing rubrics after observing outputs;
- overrepresenting easy factual questions and suppressing hallucination pressure;
- allowing unsupported answers to pass because they express low confidence;
- using live provider behavior or mutable web state as part of the dataset at execution time.

If any of these occur, EXP-1 becomes invalid before ECE results are considered.

## 21. Completion criteria for dataset freeze

The EXP-1 dataset is freeze-ready only when all of the following are true:

- `EXP1_DATASET_v1.jsonl` contains exactly 210 valid query rows;
- family and subtype counts exactly match Section 9;
- every query has a complete linked rubric defining binary correctness;
- provenance is sufficient for independent reconstruction of each row's classification and rubric;
- leakage checks are complete and recorded;
- machine validation passes;
- independent review passes;
- Scientific Auditor approves preregistration/canon alignment;
- canonical serialization and all SHA-256 hashes are complete;
- manifest records protected input hashes, pinned git commit, validation status, approvals, and freeze timestamp;
- Release Manager records the frozen artifact set and ensures EXP-1 execution verifies the aggregate dataset hash for all 22 seed replicates.

Only after these criteria are satisfied may EXP-1 execution begin against the frozen dataset.

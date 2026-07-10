# VELYNX Program A — API Reference

This document provides the complete, canonical API reference for **Program A** in the VELYNX neurosymbolic cognitive architecture. 

Program A is a stateless, deterministic, evidence-structural question-answering surface. It is designed to gather evidence from a frozen retrieval snapshot, extract candidate claims, classify the corroboration state using the ES-1 evidence-state partition model, and emit a natural-language answer coupled with a symbolic confidence tier (`UNKNOWN`, `DEBATED`, `PROBABLE`, or `CERTAIN`). 

---

## Table of Contents
1. [Determinism Guarantees](#1-determinism-guarantees)
2. [Replay & Reproducibility Guarantees](#2-replay--reproducibility-guarantees)
3. [Module Index](#3-module-index)
4. [Types Module (`program_a.types`)](#4-types-module-program_atypes)
5. [Constants Module (`program_a.constants`)](#5-constants-module-program_aconstants)
6. [Evidence Acquisition Subpackage (`program_a.evidence`)](#6-evidence-acquisition-subpackage-program_aevidence)
7. [Claim Extraction Module (`program_a.extraction`)](#7-claim-extraction-module-program_aextraction)
8. [Mechanism Subpackage (`program_a.mechanism`)](#8-mechanism-subpackage-program_amechanism)
9. [Binding Module (`program_a.binding`)](#9-binding-module-program_abinding)
10. [Package Root (`program_a`)](#10-package-root-program_a)
11. [API Integration Examples](#11-api-integration-examples)

---

## 1. Determinism Guarantees

Program A enforces strict determinism at all pipeline stages:

- **Isolated State:** The core engine is fully stateless. It does not write to any database (including the shared SQLite store), emits no run-perturbing telemetry, accumulates no memory or learning across invocations, and prohibits internal mutable global state.
- **Provider Independence:** It performs zero run-time API calls to hosted LLM providers or search engines during experiment evaluation. 
- **Time Invariance:** No wall-clock queries are made in the execution path, neutralizing time-based non-determinism.
- **Pure Arithmetic and Logic:** Text extraction and classification are executed using pure, static rules.

---

## 2. Replay & Reproducibility Guarantees

Every query evaluation is fully reproducible:

- **Content-Addressed Retrieval:** The retrieval subsystem loads a static, frozen snapshot verified via an aggregate SHA-256 hash. Any byte-level modification of the snapshot triggers an immediate pre-run error during verification.
- **Total Ordering:** Evidence item lookup results are sorted using a frozen lexicographical total order key before claim extraction.
- **Unique Run Identity:** The `mechanism_id()` string uniquely represents the configuration:
  $$\text{mechanism\_id} = \text{"program-a-public-v1+es1-{SPEC_VERSION}+const-{frozen_constants_digest[:8]}+snap-{snapshot_aggregate_hash[:8]}"}$$
  Replaying an experiment with the same `mechanism_id` and query dataset guarantees identical output strings and confidence tiers across all seeds.

---

## 3. Module Index

Program A is partitioned into the following modules:

| Module / Package | Role |
| :--- | :--- |
| [program_a](file:///C:/Users/Purushottam/Documents/VELYNX/program_a/__init__.py) | Package root; exposes the primary public API. |
| [program_a.types](file:///C:/Users/Purushottam/Documents/VELYNX/program_a/types.py) | Shares value types (frozen dataclasses) used throughout the pipeline. |
| [program_a.constants](file:///C:/Users/Purushottam/Documents/VELYNX/program_a/constants.py) | Sells frozen free constants sourced from the T1 spec. |
| [program_a.evidence.snapshot_format](file:///C:/Users/Purushottam/Documents/VELYNX/program_a/evidence/snapshot_format.py) | Defines the frozen snapshot on-disk structure and integrity checks. |
| [program_a.evidence.snapshot_store](file:///C:/Users/Purushottam/Documents/VELYNX/program_a/evidence/snapshot_store.py) | Acquires evidence from verified static snapshot files. |
| [program_a.evidence.snapshot_builder](file:///C:/Users/Purushottam/Documents/VELYNX/program_a/evidence/snapshot_builder.py) | Builder-side utility for constructing frozen snapshots offline. |
| [program_a.extraction.claim_extraction](file:///C:/Users/Purushottam/Documents/VELYNX/program_a/extraction/claim_extraction.py) | Performs deterministic entity-level candidate-claim extraction. |
| [program_a.mechanism.support_tests](file:///C:/Users/Purushottam/Documents/VELYNX/program_a/mechanism/support_tests.py) | Houses the four fundamental deterministic predicates of ES-1. |
| [program_a.mechanism.evidence_states](file:///C:/Users/Purushottam/Documents/VELYNX/program_a/mechanism/evidence_states.py) | Handles state-classification into S0–S3 based on corroboration. |
| [program_a.mechanism.emission](file:///C:/Users/Purushottam/Documents/VELYNX/program_a/mechanism/emission.py) | **Target contract only.** Maps classified states to formatted responses and symbolic tiers. `emission.py` is currently absent from the active repository after relocation under the ES-1 NO-GO governance process. |
| [program_a.binding.exp1_binding](file:///C:/Users/Purushottam/Documents/VELYNX/program_a/binding/exp1_binding.py) | **Target contract only.** Connects the public surface to the EXP-1 adapter framework. `exp1_binding.py` is currently absent from the active repository after relocation under the ES-1 NO-GO governance process. |

---

## 4. Types Module (`program_a.types`)

This leaf module defines frozen data structures passed between subsystems. It maintains no dependency on the `experiments` or `backend` packages, preventing cheat channels or leakage of retrieval relevance scores.

### `EvidenceItem`

```python
@dataclass(frozen=True)
class EvidenceItem:
    """Represents a single provenance-tagged evidence snippet retrieved from a frozen snapshot."""
    doc_id: str
    origin_domain: str
    title: str
    text: str
    snapshot_hash_ref: str
```

- **Fields:**
  - `doc_id` (`str`): Unique identifier of the document.
  - `origin_domain` (`str`): Source domain of the document.
  - `title` (`str`): Title of the document.
  - `text` (`str`): Raw text snippet from the document.
  - `snapshot_hash_ref` (`str`): Hash of the snapshot from which this item was acquired.
- **Constraints:**
  - Direct database scores or retrieval relevance scores are forbidden inside this struct to prevent leakages to the confidence tier.
  - No wall-clock timestamp is allowed.
- **Exceptions:**
  - `ValueError`: Raised during `__post_init__` if `doc_id` or `origin_domain` is empty or `None`.

### `EvidenceSet`

```python
@dataclass(frozen=True)
class EvidenceSet:
    """An ordered sequence of EvidenceItem instances, preserving the frozen total order of PA-1."""
    items: tuple[EvidenceItem, ...]
```

- **Fields:**
  - `items` (`tuple[EvidenceItem, ...]`): A tuple of sorted `EvidenceItem` instances.
- **Methods:**
  - `__len__(self) -> int`: Returns the number of items in the set.
  - `__iter__(self) -> Iterator[EvidenceItem]`: Returns an iterator over the items.
  - `__getitem__(self, index: int) -> EvidenceItem`: Retrieves an item by index.
- **Exceptions:**
  - `TypeError`: Raised during `__post_init__` if `items` is not a `tuple`.

### `CandidateClaim`

```python
@dataclass(frozen=True)
class CandidateClaim:
    """Represents an extracted candidate claim with back-references into the evidence set."""
    claim_text: str
    supporting_doc_ids: tuple[str, ...]
```

- **Fields:**
  - `claim_text` (`str`): Natural language representation of the claim.
  - `supporting_doc_ids` (`tuple[str, ...]`): References to source documents in the parent `EvidenceSet` by their `doc_id`.

### `CandidateClaims`

```python
@dataclass(frozen=True)
class CandidateClaims:
    """An ordered collection of extracted CandidateClaim instances."""
    claims: tuple[CandidateClaim, ...]
```

- **Fields:**
  - `claims` (`tuple[CandidateClaim, ...]`): A tuple of `CandidateClaim` instances.
- **Methods:**
  - `__len__(self) -> int`: Returns the number of claims.
  - `__iter__(self) -> Iterator[CandidateClaim]`: Returns an iterator over the claims.
  - `__getitem__(self, index: int) -> CandidateClaim`: Retrieves a claim by index.

### `EvidenceStateResult`

```python
@dataclass(frozen=True)
class EvidenceStateResult:
    """Holds the classified ES-1 state and related supporting/contradicting evidence sets."""
    state: str
    selected_claim: CandidateClaim | None
    support_doc_ids: tuple[str, ...]
    contradiction_doc_ids: tuple[str, ...]
    independent_origin_count: int
```

- **Fields:**
  - `state` (`str`): The categorized ES-1 state (must be `"S0"`, `"S1"`, `"S2"`, or `"S3"`).
  - `selected_claim` (`CandidateClaim | None`): Non-`None` for `"S1"`, `"S2"`, and `"S3"` (the §A1/§A2 selected claim); `None` iff state is `"S0"`.
  - `support_doc_ids` (`tuple[str, ...]`): Document IDs supporting `selected_claim`, ordered by `EVIDENCE_ORDERING_KEY`; empty only when state is `"S0"`.
  - `contradiction_doc_ids` (`tuple[str, ...]`): Document IDs computed with respect to `selected_claim`, ordered by `EVIDENCE_ORDERING_KEY`; non-empty iff state is `"S1"`.
  - `independent_origin_count` (`int`): `ios(selected_claim)` in every state, with `0` for `"S0"`.
- **Witness semantics (PA-3 addendum §A7 / I-3):**

  | State | `selected_claim` | `support_doc_ids` | `contradiction_doc_ids` | `independent_origin_count` |
  |---|---|---|---|---|
  | `"S0"` | `None` | `()` | `()` | `0` |
  | `"S1"` | §A1/§A2 winner (non-`None`) | supporters of `selected_claim` | supporters of the material-incompatible competing claim (§A4) | `ios(selected_claim)` (≥1) |
  | `"S2"` | §A1/§A2 winner (non-`None`) | supporters of `selected_claim` | `()` | `1` |
  | `"S3"` | §A1/§A2 winner (non-`None`) | supporters of `selected_claim` | `()` | `≥ MIN_INDEPENDENT_ORIGINS_FOR_S3` (=2) |

  In `"S1"`, `selected_claim` is the best-corroborated supported claim from §A1/§A2, while `contradiction_doc_ids` names the supporters of the §A4 material-incompatible competing claim. The carried claim is for source-attribution of alternatives, not for asserting a single resolution.
- **Exceptions:**
  - `ValueError`: Raised during `__post_init__` if `state` is not in `("S0", "S1", "S2", "S3")`.

### `Emission`

```python
@dataclass(frozen=True)
class Emission:
    """The public evaluation response emitted by Program A."""
    answer: str
    tier: str
    raw_numeric_confidence: None
    metadata: dict[str, Any]
```

- **Fields:**
  - `answer` (`str`): Natural language answer, refusal, or qualified text to be shown to the user.
  - `tier` (`str`): Symbolic confidence tier representing predicted rubric-correctness. Must be one of `"UNKNOWN"`, `"DEBATED"`, `"PROBABLE"`, or `"CERTAIN"`.
  - `raw_numeric_confidence` (`None`): Under ES-1, this field is strictly hardcoded to `None`.
  - `metadata` (`dict[str, Any]`): Arbitrary execution metadata (e.g., matching snapshot hash, classified state, active spec version).
- **Exceptions:**
  - `ValueError`: Raised during `__post_init__` if `tier` is not in `("UNKNOWN", "DEBATED", "PROBABLE", "CERTAIN")`.

---

## 5. Constants Module (`program_a.constants`)

This module serves as the single source of truth for all free constants defined by the frozen T1 specification. No evaluation-side metrics, probability values, or bin boundaries appear in this file.

### Sourced Constants

```python
SPEC_VERSION: str
PA3_RULESET_VERSION: str
MIN_INDEPENDENT_ORIGINS_FOR_S3: int
INDEPENDENCE_RELATION: str
SUPPORT_TEST_PARAMS: dict[str, Any]
CONTRADICTION_MATERIALITY_PARAMS: dict[str, Any]
EVIDENCE_ORDERING_KEY: str
EXTRACTION_PARAMS: dict[str, Any]
ANSWER_TEMPLATES: dict[str, Any]
STATE_TIER_MAP: dict[str, str]
CONFIDENCE_TIERS: tuple[str, ...]
```

- **Descriptions:**
  - `SPEC_VERSION`: String designating the frozen T1 specification version.
  - `PA3_RULESET_VERSION`: Structural identity tag used by the PA-3 mechanism freeze and by `frozen_constants_digest()` to detect drift in the frozen PA-3 ruleset. This tag carries no scientific meaning.
  - `MIN_INDEPENDENT_ORIGINS_FOR_S3`: The independent origin count required to upgrade from `S2` (`PROBABLE`) to `S3` (`CERTAIN`).
  - `INDEPENDENCE_RELATION`: Rules defining what constitutes independent domains (e.g., counting mirrors once).
  - `SUPPORT_TEST_PARAMS`: Configuration parameter mapping for testing text-alignment.
  - `CONTRADICTION_MATERIALITY_PARAMS`: Parameters defining what structural differences trigger a material contradiction.
  - `EVIDENCE_ORDERING_KEY`: Sorting instructions for compiling `EvidenceSet`.
  - `EXTRACTION_PARAMS`: Constraints and parameters utilized in candidate claim generation.
  - `ANSWER_TEMPLATES`: Natural-language boilerplate and templates per corroboration state.
  - `STATE_TIER_MAP`: Map converting state keys to confidence tiers (`{"S0": "UNKNOWN", "S1": "DEBATED", "S2": "PROBABLE", "S3": "CERTAIN"}`).
  - `CONFIDENCE_TIERS`: Valid confidence labels (`("UNKNOWN", "DEBATED", "PROBABLE", "CERTAIN")`).

### `frozen_constants_digest`

```python
def frozen_constants_digest() -> str:
    """Computes a SHA-256 hash digest of all frozen constants in the register to detect drift."""
    ...
```

- **Returns:** `str` representing the SHA-256 digest hex.
- **Exceptions:**
  - `NotImplementedError`: Raised if the register has not yet been frozen.

---

## 6. Evidence Acquisition Subpackage (`program_a.evidence`)

Manages offline snapshot generation and online snapshot loading, verification, and deterministic evidence-set extraction.

### `SnapshotManifest`

```python
@dataclass(frozen=True)
class SnapshotManifest:
    """Represents metadata and verification hashes of an offline content-addressed snapshot."""
    aggregate_hash: str
    doc_hashes: dict[str, str]
    built_from: str
    leakage_review_ref: str
    created_commit: str
```

- **Fields:**
  - `aggregate_hash` (`str`): Re-computed SHA-256 verification hash representing the entire corpus state.
  - `doc_hashes` (`dict[str, str]`): Mapping of individual document paths or IDs to their corresponding file hashes.
  - `built_from` (`str`): Metadata regarding the corpus generation context.
  - `leakage_review_ref` (`str`): Reference ID or URL of the corresponding leakage-review gate approval.
  - `created_commit` (`str`): Active Git commit when the snapshot was constructed.
- **Methods:**
  - `to_dict(self) -> dict[str, Any]`: Formats the manifest details into a JSON-serializable dictionary.

### `verify_snapshot`

```python
def verify_snapshot(path: str | Path) -> SnapshotManifest:
    """Validates the static snapshot manifest and file integrity on disk."""
    ...
```

- **Parameters:**
  - `path` (`str | Path`): Path to the target snapshot archive or directory.
- **Returns:** `SnapshotManifest` instance containing the parsed metadata.
- **Exceptions:**
  - `ValueError`: Raised if any individual file hash or the overall aggregate hash mismatches the manifest records.
  - `FileNotFoundError`: Raised if the target snapshot manifest file does not exist on disk.

### `EvidenceSource` Protocol

```python
@runtime_checkable
class EvidenceSource(Protocol):
    """Protocol establishing the interface between PA-1 evidence acquisition and PA-2 claim extraction."""
    @property
    def snapshot_hash(self) -> str:
        """Returns the aggregate SHA-256 verification hash of the loaded corpus snapshot."""
        ...

    def evidence_for(self, query_text: str) -> EvidenceSet:
        """Gathers and deterministically orders all relevant evidence documents for the query."""
        ...
```

### `SnapshotStore`

```python
class SnapshotStore:
    """Verified, snapshot-backed evidence source (implements EvidenceSource)."""
```

- **Class Methods:**
  - `load(cls, path: str | Path) -> SnapshotStore`: Instantiates a verified store from disk. Calls `verify_snapshot` internally.
- **Properties:**
  - `snapshot_hash` (`str`): Returns the aggregate SHA-256 hash.
- **Methods:**
  - `evidence_for(self, query_text: str) -> EvidenceSet`: Collects evidence snippets, orders them lexicographically by `(origin_domain, doc_id)`, and strips all database ranking scores or timestamps before returning.

### `Retriever` Protocol

```python
@runtime_checkable
class Retriever(Protocol):
    """Protocol for offline retrieval engines; utilized only during builder-side snapshot compiling."""
    def retrieve(self, query: str) -> list[dict[str, Any]]:
        """Queries source indexes and returns a list of raw documents."""
        ...
```

### `build_snapshot`

```python
def build_snapshot(queries: Iterable[str], out_dir: str | Path) -> SnapshotManifest:
    """Builds a content-addressed static retrieval snapshot offline, saving it to disk."""
    ...
```

- **Parameters:**
  - `queries` (`Iterable[str]`): List of evaluation query strings to retrieve evidence for.
  - `out_dir` (`str | Path`): Destination directory path where files and the compiled manifest should be stored.
- **Returns:** `SnapshotManifest` of the compiled snapshot.
- **Exceptions:**
  - `NotImplementedError`: Runs only offline and is unimplemented in the runtime execution environment.

---

## 7. Claim Extraction Module (`program_a.extraction`)

Parses evidence text mechanically to isolate candidate claims, acting as the primary barrier against hallucination or topic-space contamination.

### `extract_claims`

```python
def extract_claims(query_text: str, evidence: EvidenceSet) -> CandidateClaims:
    """Deterministic, entity-level candidate claim extractor."""
    ...
```

- **Parameters:**
  - `query_text` (`str`): The primary user query string.
  - `evidence` (`EvidenceSet`): Collected evidence documents.
- **Returns:** `CandidateClaims` representing all isolated entity-level assertions.
- **Behavioral Contract:**
  - Operates purely deterministically; the same input guarantees identical claims.
  - Under no circumstances calls hosted LLM APIs or includes random steps.
  - If `evidence` is empty, returns an empty `CandidateClaims` sequence.
  - Excludes topically relevant documents that do not contain explicit entity-level matches.

---

## 8. Mechanism Subpackage (`program_a.mechanism`)

Contains the ES-1 corroboration logic. Translates evidence structure into states S0–S3.

**Repository status vs. target contract:** this section documents the frozen target API contract for the mechanism surface. The active repository currently does not contain `program_a/mechanism/emission.py`; that emission surface was relocated under the ES-1 NO-GO governance process. Interfaces below that describe response construction, tier emission, `ProgramA`, `answer_query`, `build_program_a`, `mechanism_id`, or `_configure` are target contracts only and are non-executable until `ES1_IMPLEMENTATION_GATE.md` legitimately reaches GO. This status note does not alter the intended architecture.

### `supports`

```python
def supports(claim: CandidateClaim, evidence_item: EvidenceItem) -> bool:
    """Evaluates whether an individual evidence item supports the candidate claim."""
    ...
```

- **Parameters:**
  - `claim` (`CandidateClaim`): The target claim.
  - `evidence_item` (`EvidenceItem`): The individual source snippet.
- **Returns:** `bool` indicating support status.
- **Behavioral Contract:**
  - Driven by parameters in `constants.SUPPORT_TEST_PARAMS`. Contains no probability values or heuristic weights.

### `contradicts`

```python
def contradicts(claim_a: CandidateClaim, claim_b: CandidateClaim) -> bool:
    """Determines whether two candidate claims contradict each other."""
    ...
```

- **Parameters:**
  - `claim_a` (`CandidateClaim`), `claim_b` (`CandidateClaim`): The target claims to compare.
- **Returns:** `bool` indicating contradiction.

### `is_material`

```python
def is_material(claim_a: CandidateClaim, claim_b: CandidateClaim) -> bool:
    """Evaluates if a contradiction between two claims is material, filtering out trivial variations."""
    ...
```

- **Parameters:**
  - `claim_a` (`CandidateClaim`), `claim_b` (`CandidateClaim`): The target claims.
- **Returns:** `bool` (true if the conflict is material; false if trivial/stylistic).
- **Behavioral Contract:**
  - Leverages thresholds from `constants.CONTRADICTION_MATERIALITY_PARAMS`.

### `independent_origins`

```python
def independent_origins(items: tuple[EvidenceItem, ...]) -> int:
    """Computes the count of unique independent origin domains represented in a collection of evidence."""
    ...
```

- **Parameters:**
  - `items` (`tuple[EvidenceItem, ...]`): A tuple of target evidence items.
- **Returns:** `int` representing unique source count.
- **Behavioral Contract:**
  - Groups and collapses duplicate domains or mirror sites as specified in `constants.INDEPENDENCE_RELATION`.

### `classify`

```python
def classify(
    query_text: str,
    evidence: EvidenceSet,
    claims: CandidateClaims,
) -> EvidenceStateResult:
    """Applies ES-1 decision logic to classify evidence corroboration into exactly one state S0-S3."""
    ...
```

- **Parameters:**
  - `query_text` (`str`): The primary query.
  - `evidence` (`EvidenceSet`): Collected evidence documents.
  - `claims` (`CandidateClaims`): Extracted candidate claims.
- **Returns:** `EvidenceStateResult`
- **ES-1 State Logic:**
  - **`S0`**: No evidence items support any candidate claims. Selected claim is set to `None`.
  - **`S1` (Contradiction)**: Material contradictions exist between claims backed by independent origins.
  - **`S2` (Single Source)**: A claim is supported by exactly one independent origin domain. No material contradictions exist.
  - **`S3` (Corroborated)**: A claim is corroborated by $\ge 2$ independent origin domains (as defined by `constants.MIN_INDEPENDENT_ORIGINS_FOR_S3`). No material contradictions exist.
- **Precedence Order:** S0 takes absolute precedence, followed by S1, then S2/S3.

### `ProgramA`

```python
class ProgramA:
    """The central state-holder wrapping the configured evidence source."""
```

- **Methods:**
  - `__init__(self, snapshot_store: SnapshotStore) -> None`:
    - **Parameters:** `snapshot_store` (`SnapshotStore`).
  - `answer_query(self, query_text: str, seed: int) -> Emission`:
    - Drives retrieval (PA-1), extraction (PA-2), and state classification (PA-3), and maps the resulting state to answer text and tier (PA-4).
    - **Parameters:** `query_text` (`str`), `seed` (`int`).
    - **Returns:** `Emission` instance.
  - `mechanism_id(self) -> str`:
    - Returns the stable identity string of the running mechanism, encoding the Spec version and aggregate snapshot hash.
    - **Returns:** `str`.

### Module Convenience Wrappers

```python
def build_program_a(snapshot_path: str | Path) -> ProgramA:
    """Convenience factory to instantiate ProgramA from a snapshot path."""
    ...

def answer_query(query_text: str, seed: int) -> Emission:
    """Public wrapper delegating to the configured singleton ProgramA instance."""
    ...

def mechanism_id() -> str:
    """Public wrapper returning the configured singleton's identity string."""
    ...

def _configure(instance: ProgramA) -> None:
    """Sets the default global singleton ProgramA instance."""
    ...
```

---

## 9. Binding Module (`program_a.binding`)

**Repository status vs. target contract:** this section documents the frozen target API contract for the EXP-1 binding. The active repository currently does not contain `program_a/binding/exp1_binding.py`; that binding was relocated under the ES-1 NO-GO governance process. The interface below is a target contract only and is non-executable until `ES1_IMPLEMENTATION_GATE.md` legitimately reaches GO. It performs no statistical calculation, calibration, binning, or correctness grading in the intended architecture.

### `program_a_answer_fn`

```python
def program_a_answer_fn(query: QueryRecord, seed: int) -> Mapping[str, Any]:
    """Form-A answer wrapper acting as the primary injection point for EXP-1 runner."""
    ...
```

- **Parameters:**
  - `query` (`QueryRecord`): Active evaluation query record (from `experiments.EXP1.dataset`).
  - `seed` (`int`): Replicate seed for seed-level consistency evaluations.
- **Returns:** `Mapping[str, Any]` matching the fields:
  ```python
  {
      "query_id": str,
      "answer": str,
      "tier": str,  # "UNKNOWN", "DEBATED", "PROBABLE", or "CERTAIN"
      "seed": int,
      "raw_numeric_confidence": None,
      "metadata": dict[str, Any],
  }
  ```
- **Behavioral Contract (L11/CR-3):**
  - **Strict Input Isolation:** Reads **only** `query.query` and `query.query_id`. 
  - Reading `query.gold_rubric`, `query.query_family`, or `query.metadata` is strictly prohibited. This is enforced by validation tests substituting these fields with error sentinels.

---

## 10. Package Root (`program_a`)

**Repository status vs. target contract:** this section documents the intended package-root exports after the ES-1 governance gate reaches GO. Because `program_a/mechanism/emission.py` and `program_a/binding/exp1_binding.py` are currently absent from the active repository after relocation under the ES-1 NO-GO governance process, the export block below is a target contract only and must not be treated as current executable repository state.

The package root (`program_a/__init__.py`) controls module encapsulation, exposing only the minimum public interface required by the runner.

### Public Exports

```python
from program_a.binding.exp1_binding import program_a_answer_fn
from program_a.mechanism.emission import answer_query, build_program_a, mechanism_id

__all__ = ["answer_query", "build_program_a", "mechanism_id", "program_a_answer_fn"]
```

---

## 11. API Integration Examples

**Execution status:** the examples in this section are declarative target-contract examples, not current runnable examples. They depend on `program_a/mechanism/emission.py` and `program_a/binding/exp1_binding.py`, both of which are currently absent from the active repository after relocation under the ES-1 NO-GO governance process. These examples are non-executable until `ES1_IMPLEMENTATION_GATE.md` legitimately reaches GO.

### Client-Side Execution Flow (Declarative)

The following example shows the intended target-contract flow for executing a query through the public `ProgramA` interface:

```python
from pathlib import Path
from program_a import build_program_a

# 1. Define paths and configure the Program A engine
SNAPSHOT_PATH = Path("C:/Users/Purushottam/Documents/VELYNX/data/frozen_snapshot")

# 2. Build the stateless instance using the factory helper
program = build_program_a(SNAPSHOT_PATH)

# 3. Retrieve mechanism identity (validates Spec version and snapshot integrity)
identity = program.mechanism_id()
print(f"Loaded mechanism: {identity}")

# 4. Evaluate an incoming query
query = "What was the population of Alexandria in 100 AD?"
seed = 42

emission = program.answer_query(query_text=query, seed=seed)

# 5. Extract output answer and symbolic confidence tier
print(f"Emitted Answer: {emission.answer}")
print(f"Emitted Confidence Tier: {emission.tier}")
assert emission.raw_numeric_confidence is None
```

### EXP-1 Evaluation Pipeline Integration

The following example shows the intended target-contract flow for plugging the Form-A binding wrapper into the EXP-1 runner:

```python
from pathlib import Path
from program_a import build_program_a, program_a_answer_fn, mechanism_id
from program_a.mechanism.emission import _configure
from experiments.EXP1.run import run_experiment_sync

# 1. Configure global default Program A singleton instance
SNAPSHOT_PATH = Path("C:/Users/Purushottam/Documents/VELYNX/data/frozen_snapshot")
engine = build_program_a(SNAPSHOT_PATH)
_configure(engine)

# 2. Get the unique identity of the current run configuration
adapter_id = mechanism_id()

# 3. Inject the Form-A binding function directly into the runner
results = run_experiment_sync(
    answer_fn=program_a_answer_fn,
    program_a_adapter_id=adapter_id,
    output_dir="C:/Users/Purushottam/Documents/VELYNX/velynx_output",
)
print("EXP-1 pipeline completed successfully.")
```

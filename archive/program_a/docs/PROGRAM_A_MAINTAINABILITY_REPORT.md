# PROGRAM A — MAINTAINABILITY REPORT

**Authority:** Lead Systems Architect / Maintainability Auditor  
**Date:** 2026-07-08  
**Scope:** A structural and organizational maintainability audit of the proposed Program A codebase layout, public boundaries, and interfaces.  
**Reference Material:** `PROGRAM_A_FINAL_ARCHITECTURE.md`, `PROGRAM_A_MODULE_SPEC.md`, `PROGRAM_A_CONSISTENCY_AUDIT.md`, `PROGRAM_A_DEPENDENCY_GRAPH.md`, `PROGRAM_A_RISK_REGISTER.md`.

---

## 1. Executive Summary

This maintainability report evaluates the architectural design of **Program A** (the honest-uncertainty retrieval-based question-answering surface) from a software engineering perspective. 

The proposed modular structure split under `program_a/` (`evidence/`, `extraction/`, `mechanism/`, `binding/`) is highly intentional and segregates the core scientific primitives of the ES-1 confidence mechanism from retrievals and text mechanics. However, several structural interfaces and boundary crossings are vulnerable to tight coupling and instability as the system moves from an experimental prototype evaluating EXP-1 toward a live product.

This audit:
- Identifies critical coupling paths between components that risk ripple-effect defects.
- Highlights unstable interface contracts that are likely to change during evolution.
- Maps precise locations where structural abstractions (Python `Protocols` or `ABCs`) should be introduced.
- Identifies clear extension points to support future experimental or product requirements without violating constitutional boundaries.

This is an analytical report; no code redesign is performed.

---

## 2. Tight Coupling Risks

The current design consists of six planned subsystems (PA-1 to PA-6) forming a linear dataflow. While the flow is straightforward, several modules exhibit high structural coupling:

### 2.1 PA-4 Emission (`emission.py`) and PA-3 Evidence-State Classification (`evidence_states.py`)
- **Coupling Mechanism:** `emission.py` takes the `EvidenceStateResult` (produced by `classify` in `evidence_states.py`) and maps each state ordinal directly to a specific confidence tier (`UNKNOWN`, `DEBATED`, `PROBABLE`, `CERTAIN`) and a specific hardcoded answer template.
- **Maintainability Risk:** The mapping of states to tiers is rigid and hardcoded. If the Scientific Auditor introduces a new corroboration state (e.g., a "partially corroborated" or "source-conflicted but highly probable" state), or if the precedence table changes, both `evidence_states.py` and `emission.py` must be modified in tandem. Additionally, any change in the state representation of `EvidenceStateResult` will immediately break the templates inside `emission.py`.

### 2.2 Shared Value Types (`types.py`) and All Dependent Modules
- **Coupling Mechanism:** `types.py` is a core leaf package defining fundamental data structures (`EvidenceItem`, `EvidenceSet`, `CandidateClaim`, `CandidateClaims`, `EvidenceStateResult`, `Emission`).
- **Maintainability Risk:** Because Python dataclasses lack native interface-implementation boundaries, any structural change to these types—such as adding a field, altering a field type (e.g., from `tuple` to another container), or changing metadata structures—will propagate as a breaking change across almost every module on the disk, including `snapshot_store.py`, `claim_extraction.py`, `support_tests.py`, `evidence_states.py`, `emission.py`, and the external binding layer `exp1_binding.py`.

### 2.3 PA-3 Support Predicates (`support_tests.py`) and ES-1 Constants (`constants.py`)
- **Coupling Mechanism:** `support_tests.py` implements the load-bearing deterministic predicates (`supports`, `contradicts`, `is_material`, and `independent_origins`). It imports its numeric and behavioral thresholds (such as `MIN_INDEPENDENT_ORIGINS_FOR_S3` and claim-support thresholds) directly from `constants.py`.
- **Maintainability Risk:** If a new predicate is added or if existing predicates require multidimensional parameters (e.g., moving from a flat origin threshold to domain-weighted independence rules), both the implementation in `support_tests.py` and the parameter schema in `constants.py` must undergo simultaneous, lock-step modification.

### 2.4 PA-5 Seam Binding (`exp1_binding.py`) and EXP-1 Dataset Schema (`dataset.py`)
- **Coupling Mechanism:** `exp1_binding.py` translates Program A's internal `Emission` records to the format expected by the EXP-1 framework's `AnswerRecord` mapping. It imports `QueryRecord` and maps inputs directly.
- **Maintainability Risk:** The binding is extremely vulnerable to any evolution in the experimental framework. As exposed in `PROGRAM_A_CONSISTENCY_AUDIT.md` (AUD-01 to AUD-03), any drift in the key names, query family enums, or file layout expected by `experiments/EXP1/dataset.py` will cause immediate, silent, or noisy loading crashes at runtime.

---

## 3. Interface Instability Audit

Several interfaces in the proposed package tree are structurally fragile and likely to experience instability as requirements evolve.

### 3.1 The Claim Extraction Interface (`extract_claims`)
- **Contract:** `extract_claims(query_text: str, evidence: EvidenceSet) -> CandidateClaims`
- **Instability Drivers:** Constructing deterministic claims from raw text via pure regular expressions or rule-based entity matches is famously fragile across heterogeneous corpuses. As soon as the system encounters complex sentence structures, negations, or coreferences, this signature will struggle. It will likely need to expand to accept external metadata, parsing templates, contextual window settings, or references to local linguistic models.

### 3.2 The Semantic Predicates (`supports` and `contradicts`)
- **Contract:** `supports(claim: CandidateClaim, evidence_item: EvidenceItem) -> bool` and `contradicts(claim_a: CandidateClaim, claim_b: CandidateClaim) -> bool`
- **Instability Drivers:** These predicates are defined as pure binary checks. However, semantic alignment is rarely binary. As the corpus grows, these interfaces will likely prove too rigid. They will either need to return a confidence score (float) or complex structured metadata (e.g., exact character spans of match/mismatch, contradiction types, or semantic distance), destabilizing any downstream module expecting a simple boolean value.

### 3.3 The Evidence Retrieval Interface (`SnapshotStore.evidence_for`)
- **Contract:** `evidence_for(query_text: str) -> EvidenceSet`
- **Instability Drivers:** This interface is coupled to a static snapshot-backed lookup. While suitable for EXP-1, a live product shell (PA-7) will require dense/semantic retrieval, hybrid BM25/vector search, and query-expansion strategies. If this interface is not decoupled from the store, adding query-rewriting or expansion parameters will destabilize the execution pipeline.

### 3.4 The Seam Binding Interface (`program_a_answer_fn`)
- **Contract:** `program_a_answer_fn(query: QueryRecord, seed: int) -> Mapping[str, Any]`
- **Instability Drivers:** It imports the concrete `QueryRecord` type directly from `experiments/EXP1/dataset.py`. If a new experiment (such as EXP-2 or E1) uses a different record class or validation regime, this binding becomes a throwaway component that cannot be re-used, creating high interface instability across experimental lifecycles.

---

## 4. Recommended Abstractions

To decouple these subsystems and ensure long-term maintainability, the following standard Python structural abstractions should be introduced:

```
               Existing Rigid Pipeline
  [SnapshotStore] ──▶ [claim_extraction] ──▶ [support_tests] ──▶ [emission]
  
               Recommended Abstracted Core
  [EvidenceProvider] ──▶ [ClaimExtractor] ──▶ [SemanticMatcher] ──▶ [EmissionStrategy]
        ▲                     ▲                      ▲                    ▲
        │ (implements)        │ (implements)         │ (implements)       │ (implements)
  [SnapshotStore]       [NLPClaimExtractor]    [RuleBasedMatcher]   [ES1EmissionStrategy]
```

### 4.1 `EvidenceProvider` Protocol
Instead of importing and invoking `SnapshotStore` directly inside `emission.py`, the core query engine should depend on an abstract evidence retriever:
```python
from typing import Protocol

class EvidenceProvider(Protocol):
    def evidence_for(self, query_text: str) -> EvidenceSet:
        """Acquires and orders an evidence set for a given query."""
        ...
```
- **Benefit:** Decouples the question-answering pipeline from the underlying storage mechanism. The system can swap the static `SnapshotStore` with a `LiveUnifiedRetriever` (re-using `unified_retriever.py` in the product shell) or a memory-only `MockEvidenceProvider` for unit testing, without modifying the emission logic.

### 4.2 `ClaimExtractor` Protocol
The pipeline should abstract text-level extraction of propositions:
```python
class ClaimExtractor(Protocol):
    def extract_claims(self, query_text: str, evidence: EvidenceSet) -> CandidateClaims:
        """Extracts candidate claims from the gathered evidence."""
        ...
```
- **Benefit:** Allows swapping the extraction mechanism. The system can transition from pure string-matching algorithms to local neural parsing (e.g., if a local LLM becomes available under the M8/M13 conditional allowances) without modifying the state machine in `evidence_states.py`.

### 4.3 `SemanticMatcher` Protocol
Isolate the semantic check logic from the state-transition table:
```python
class SemanticMatcher(Protocol):
    def supports(self, claim: CandidateClaim, item: EvidenceItem) -> bool: ...
    def contradicts(self, claim_a: CandidateClaim, claim_b: CandidateClaim) -> bool: ...
    def is_material(self, claim_a: CandidateClaim, claim_b: CandidateClaim) -> bool: ...
```
- **Benefit:** Isolates the decision logic in `evidence_states.py` (which only cares *that* support and contradictions exist to assign S0–S3) from *how* those checks are computed. If matching rules are updated or replaced, the state partition engine remains untouched.

### 4.4 `EmissionStrategy` Protocol
Abstract the translation of an evidence classification to an output form:
```python
class EmissionStrategy(Protocol):
    def emit(self, state_result: EvidenceStateResult, seed: int) -> Emission:
        """Constructs response text and maps to a canonical confidence tier."""
        ...
```
- **Benefit:** Allows the system to support different outputs. For experimental evaluation, an `ES1EmissionStrategy` can be used to output standard templates and tiers. For a product shell, a `DetailedReportEmissionStrategy` could output rich markdown reports and raw confidence analytics.

---

## 5. Planned Extension Points

To allow the package to grow gracefully under future scientific or engineering demands, the architecture should reserve the following clear extension points:

### 5.1 Retrieval Snapshot Format Drivers (PA-1)
- **Location:** `program_a/evidence/snapshot_format.py`
- **Mechanism:** Provide a registry for snapshot serialization formats (e.g., `.jsonl`, `.sqlite`, `.parquet`).
- **Use Case:** As the retrieval corpus expands, reading and hashing a large flat JSONL file will become a major memory and I/O bottleneck. A registration hook allows upgrading to a SQLite-backed read-only snapshot or an indexed column-store without touching the retrieval logic.

### 5.2 Custom Support Rule Chains (PA-3)
- **Location:** `program_a/mechanism/support_tests.py`
- **Mechanism:** Allow developers to register custom validation checkers or heuristic functions to a rule chain inside the predicates.
- **Use Case:** Adding specific linguistic sanity checks (e.g., date-mismatch rules, numeric difference tolerancing, or synonym matching) as separate, isolated plugins rather than inflating a single monolithic function.

### 5.3 Evidence-State Decision Trees (PA-3)
- **Location:** `program_a/mechanism/evidence_states.py`
- **Mechanism:** Accept an orchestrator or a custom classifier class rather than hardcoding the S0 → S1 → (S2|S3) precedence table directly in the function.
- **Use Case:** Re-using the pipeline to test alternative confidence frameworks (e.g., an "ES-2" model with five states, or a model that incorporates direct refusal rules) without rewriting the core workflow.

### 5.4 Public Presentation Adapters (PA-7)
- **Location:** `program_a/binding/` or a separate `program_a/presentation/` package.
- **Mechanism:** Introduce adapter interfaces for different consumer channels.
- **Use Case:** Binding to alternative experimental runners (EXP-2, EXP-3), CLI harnesses, and HTTP server gateways without contaminating the core scientific packages under `program_a/mechanism/`.

---

## 6. Maintainability Risk Summary

Review of the codebase and specifications highlights three ongoing maintainability risks:

| Risk ID | Severity | Category | Description | Mitigating Strategy |
|---|---|---|---|---|
| **MA-01** | **HIGH** | Dependency | Lack of a static CI check to prevent the import of `[REJECTED]` modules (`AnswerSynthesizer`, `ReasoningTrace`) from backend. | Implement the `test_import_guard.py` transitive-closure test (scheduled as T7) immediately to catch illegal import paths before execution. |
| **MA-02** | **MEDIUM** | Schema | Out-of-step keys and enums between `EXP1_DATASET_SPEC.md` and `experiments/EXP1/dataset.py`. | Standardize field names (e.g., `query` vs `query_text`) at the value-type level to prevent loading crashes. |
| **MA-03** | **MEDIUM** | Testing | Test suite relying on live file structures rather than virtualized setups. | Enforce that all `tests/program_a/` tests use synthetic, mock-backed, or virtualized snapshots disjoint from the frozen dataset to protect the integrity of the evaluation dataset. |

---

> [!NOTE]
> This maintainability audit is designed to protect the **integrity and reproducibility** of Program A during its experimental evaluation. The introduction of the recommended Protocols should be deferred until after G1/G4 ratification, ensuring that the initial ES-1 freeze is not perturbed by ad-hoc structural modifications.

> [!IMPORTANT]
> The absolute import boundary rules defined in `PROGRAM_A_FINAL_ARCHITECTURE.md` §2 must be respected: the `program_a/` package (excluding `program_a/binding/`) must remain a strict leaf module relative to `experiments/` and `backend/` to prevent circular dependencies.

---
*End of Report.*

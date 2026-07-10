# PROGRAM A — PUBLIC API

> [!NOTE]
> **Reconciliation Note (F-10 Resolution):** The F-10 direct-construction bypass is fully resolved on disk per `dataset.py:112-122`, rendering any warning of bypass risk stale.

**Authority:** Chief Systems Architect design review, 2026-07-07.
**Rule of this document:** interfaces marked **[FACT]** exist and are tested;
interfaces marked **[REQUIRED — NOT IMPLEMENTED]** are contracts the
repository already imposes on the missing component. No signature below is
invented beyond what `PROGRAM_A_BINDING_SPEC.md` §4/§7 and
`EXP1_PREREGISTRATION.md` §1 already require. No implementation code is
provided here; per the standing FAIL verdict of `PROGRAM_A_BINDING_SPEC.md`
§11, implementation is blocked pending open items 1-3.

---

## 1. [FACT] The consumer-side contract (exists, frozen, reuse unchanged)

```python
# experiments/EXP1/program_a_adapter.py:18-27
@runtime_checkable
class ProgramAAdapter(Protocol):
    @property
    def adapter_id(self) -> str: ...          # stable manifest identity
    def answer(self, query: QueryRecord, seed: int) -> ProgramAAnswer: ...

# experiments/EXP1/program_a_adapter.py:15
ProgramAAnswer = AnswerRecord | Mapping[str, Any] | Awaitable[Any]

# experiments/EXP1/program_a_adapter.py:30-44
@dataclass(frozen=True)
class CallableProgramAAdapter:                # wraps any answer_fn; validated
    adapter_id: str
    answer_fn: Any

# experiments/EXP1/program_a_adapter.py:55-76
def coerce_program_a_adapter(*, adapter=None, answer_fn=None,
                             adapter_id=None) -> ProgramAAdapter: ...

# experiments/EXP1/dataset.py:101-151
@dataclass(frozen=True)
class AnswerRecord:
    query_id: str
    answer: str
    tier: str                                  # must be in CONFIDENCE_TIERS
    seed: int | None = None
    raw_numeric_confidence: float | None = None
    metadata: dict[str, Any] = ...
    @classmethod
    def from_mapping(cls, row: Mapping) -> "AnswerRecord": ...  # validates tier

# experiments/EXP1/dataset.py:17
CONFIDENCE_TIERS = ("UNKNOWN", "DEBATED", "PROBABLE", "CERTAIN")

# experiments/EXP1/run.py:50, 114, 224, 230
run_seed(...) / run_experiment(...) / run_seed_sync / run_experiment_sync
    # injection points: answer_fn | program_a_adapter, program_a_adapter_id,
    # adjudicator_fn (required), output_dir, protocol_violation(s)
```

**[FACT]** `from_mapping` accepts aliases `answer`/`answer_i`,
`tier`/`tier_i`/`confidence`, uppercases the tier, and rejects non-canonical
values (`dataset.py:113-141`; tested). **[FACT]** Direct construction skips
validation — F-10 (`PROGRAM_A_ADAPTER_AUDIT.md` §7); until fixed, bindings
MUST return mappings or construct via `from_mapping`.

## 2. [REQUIRED — NOT IMPLEMENTED] The Program A emission surface

The repository fixes the *contract* of the missing component
(`PROGRAM_A_BINDING_SPEC.md` §4 "What the binding must produce";
`EXECUTION_GUIDE.md:44-51`; `EXP1_PREREGISTRATION.md` §1). Expressed as an
obligation table, not code:

| Obligation | Binding constraint | Source |
|---|---|---|
| Input | one frozen query text (+ explicit `seed: int`) | run.py:84,181 |
| Output 1 | `answer: str` — the natural-language answer, refusal, or uncertainty response *as shown to a user* | prereg §1 |
| Output 2 | `tier: str` — exactly one of the four canonical tiers, produced by Program A's own public confidence emission | prereg §1 line 33; BINDING_SPEC §4 |
| Output 3 (optional) | `raw_numeric_confidence: float` — logged exploratory, ignored for ECE | prereg §1 line 35 |
| Output 4 (optional) | `metadata: dict` | dataset.py:110 |
| Determinism | identical output for identical `(query, seed)`; no hidden state | BINDING_SPEC §4 |
| Purity | no DB writes, no telemetry perturbation, no mutation of the QueryRecord | BINDING_SPEC §4; tested pattern `test_answer_is_deterministic_and_side_effect_free` |
| Identity | a stable string identity for the manifest (`program_a_adapter_id`) | manifest.py; BINDING_SPEC §4 |
| Freeze | the tier-emission mechanism is committed and frozen before any EXP-1 output is observed | prereg §4 kill #5 |
| Coverage | exactly one record per frozen row; all 210 rows answered per seed | dataset.py:327-349 |

**[OPEN QUESTION Q1]** The internal tier-decision rule. Not specified by any
repository document; requires its own preregistration + ScientificAuditor
sign-off before this API can be implemented
(`PROGRAM_A_ADAPTER_AUDIT.md` §6 item 6).

## 3. [REQUIRED — NOT IMPLEMENTED] The binding (Form A or Form B)

**[FACT]** Both lawful shapes are specified verbatim in
`PROGRAM_A_BINDING_SPEC.md` §4:

- **Form A** — a module-level `answer_fn(query: QueryRecord, seed: int) ->
  Mapping`, injected via `run_experiment(answer_fn=...,
  program_a_adapter_id="program-a-public-v1", ...)`. The framework wraps it
  in `CallableProgramAAdapter`.
- **Form B** — a class implementing the `ProgramAAdapter` Protocol with
  `adapter_id = "program-a-public-v1"`, injected via
  `run_experiment(program_a_adapter=..., ...)`.

**[FACT]** The binding is pure field transport (~20 lines, BINDING_SPEC §5
Step 3). It performs **no** tier computation, mapping, calibration, ECE,
rubric, or decision logic. **[FACT]** Its location must respect
architecture.md §4 rule 2 (not inside `experiments/EXP1/` if it imports
`backend/`) — Architect adjudication pending (**Q4**).

## 4. Non-API (explicitly not public surface)

- `UnifiedRetriever` / `RetrievalReport` — internal substrate; its `score`
  field must never surface as confidence (**[FACT]** prereg §5).
- `AnswerSynthesizer` / `ConfidenceGrade` — **not** part of Program A's
  lawful API in the EXP-1 path (**[FACT]** F-4/F-5; `[REJECTED]` deps).
- ECE, bins, tier→probability mapping, decision rules — owned by
  `experiments/EXP1/`, not exposed by Program A (**[FACT]**
  `EXP1_DATASET_SPEC.md` §4).

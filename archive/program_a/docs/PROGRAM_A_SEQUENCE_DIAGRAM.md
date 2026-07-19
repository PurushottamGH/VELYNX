# PROGRAM A — SEQUENCE DIAGRAM (EXP-1 execution path)

**Authority:** Chief Systems Architect design review, 2026-07-07.
Every participant and message below is either **[FACT]** (verified in code at
the cited line) or **[PLANNED]** (the missing component, per
`PROGRAM_A_BINDING_SPEC.md`). Nothing else is depicted.

Legend: solid participants exist and are tested; `⟪PLANNED⟫` participants do
not exist yet.

---

## 1. Per-experiment setup

```mermaid
sequenceDiagram
    autonumber
    participant Caller as Caller (constructs runner args)
    participant Runner as run_experiment (run.py:114)
    participant Coerce as coerce_program_a_adapter (program_a_adapter.py:55)
    participant Manifest as build_execution_manifest (manifest.py)
    participant DS as load_frozen_dataset (dataset.py:236)

    Caller->>Runner: dataset_path, seeds[22], adapter/answer_fn, adjudicator_fn
    Note over Runner: adjudicator_fn is None → ValueError (run.py:128-129) [FACT]
    Runner->>Coerce: adapter | answer_fn (+ adapter_id)
    Coerce-->>Runner: ProgramAAdapter (or CallableProgramAAdapter wrap) [FACT]
    Runner->>Manifest: dataset_path, seeds, adapter_id, adjudicator_id
    Manifest->>DS: load + validate (N=210, 70/70/70, no dups, order_hash)
    DS-->>Manifest: FrozenDataset [FACT]
    Manifest-->>Runner: ExecutionManifest (git_commit, order_hash, ids) [FACT]
    Runner->>Runner: write_execution_manifest(output_dir) (run.py:173-174)
```

## 2. Per-query loop (inside each of the 22 seed replicates)

```mermaid
sequenceDiagram
    autonumber
    participant Runner as run_experiment loop (run.py:176-198)
    participant Adapter as ProgramAAdapter (binding) ⟪PLANNED⟫
    participant PA as Program A emission surface ⟪PLANNED⟫
    participant Ret as UnifiedRetriever (backend/retrieval) [FACT exists]
    participant Coerce2 as _coerce_answer_record (run.py:242)
    participant Adj as Adjudicator (frozen rubric) ⟪PLANNED⟫

    Runner->>Adapter: answer(query: QueryRecord, seed: int)   [FACT contract]
    Adapter->>PA: query.query, seed                            ⟪PLANNED⟫
    PA->>Ret: evidence acquisition (mode per Q2)               ⟪PLANNED⟫
    Ret-->>PA: RetrievalReport (sources only)                  [FACT shape]
    Note over PA: [A2] answer construction + [A3] public tier emission<br/>tier ∈ {UNKNOWN, DEBATED, PROBABLE, CERTAIN}<br/>mechanism = OPEN QUESTION Q1 (preregistered, frozen)
    PA-->>Adapter: {answer, tier, raw_numeric_confidence?, metadata?}
    Adapter-->>Runner: mapping (pure transport, no remap)      ⟪PLANNED⟫
    Runner->>Coerce2: mapping + query_id + seed
    Coerce2-->>Runner: AnswerRecord (from_mapping validates tier) [FACT]
    Runner->>Adj: adjudicator_fn(query, answer)                [FACT contract]
    Adj-->>Runner: {correctness: 0|1, fabricated_factual_answer?} ⟪PLANNED impl⟫
    Runner->>Runner: _coerce_adjudication (run.py:261-276)     [FACT]
```

## 3. Per-seed close-out and experiment decision

```mermaid
sequenceDiagram
    autonumber
    participant Runner as run_experiment (run.py:189-221)
    participant Eval as build_evaluated_records (dataset.py:352)
    participant Dec as decide_seed (decision.py)
    participant ECE as compute_ece (calibration.py:102)
    participant XDec as decide_experiment (decision.py)
    participant Rep as report.py / artifact_specs.py [FACT exists, NOT wired — TD-05]

    Runner->>Eval: queries, answers, correctness, fabricated flags
    Eval-->>Runner: EvaluatedRecord[] (label spaces joined, never inferred) [FACT]
    Runner->>Dec: evaluated, seed, protocol_violation
    Dec->>ECE: records → tier→p_i (0.125/0.375/0.625/0.875), 4 locked bins
    ECE-->>Dec: CalibrationResult (ece, bins) [FACT]
    Note over Dec: six kill checks: N≥200, ECE<0.10, tier-independence (α=0.05),<br/>≥2 tiers, 0 CERTAIN-fabrications, protocol_violation [FACT]
    Dec-->>Runner: SeedDecision → seed_<seed>/{answers,evaluated,decision}
    Runner->>XDec: 22 seed record-sets
    XDec-->>Runner: ExperimentDecision (any seed kill ⇒ kill; pooled = report-only) [FACT]
    Runner--xRep: (not invoked today — reliability.csv / calibration_report.md missing) [FACT TD-05]
```

---

**[FACT]** Every solid element is verified wired (`EXP1_TRACE.md` Links 2, 4,
5, 6a-b). **[FACT]** The three `⟪PLANNED⟫` participants (emission surface,
binding, adjudicator) plus the frozen dataset are exactly the four MISSING
links of `EXP1_TRACE.md` Verdict items 1-4. **[FACT]** The `Rep` dead-end is
TD-05 and must be wired before a compliant run.

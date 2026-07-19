# EXECUTION_GUIDE_AUDIT.md

## Terminology Inconsistencies

1. **EXP-1 vs EXP1 vs exp1 casing** — Document uses three forms interchangeably:
   - `EXP-1` (with hyphen): lines 1, 3, 100, 119, 122
   - `EXP1` (no hyphen, uppercase): lines 7, 83, 94
   - `exp1` (lowercase): lines 8, 19, 92, 120, 128

2. **Tier value formatting** — Two different notations for the same tier set:
   - Line 11: `{UNKNOWN, DEBATED, PROBABLE, CERTAIN}` (braces, no backticks)
   - Line 48: `UNKNOWN`, `DEBATED`, `PROBABLE`, or `CERTAIN` (backticks, "or")

3. **Correctness field naming** — Two terms for the same adjudicator output:
   - Line 57: `correctness` or `y_i` (both documented as valid)

4. **Program A vs EXP-1 relationship** — Line 3 states "EXP-1 is the Program A calibration gate for H1" but subsequent sections treat them as distinct executables (Program A emits answers, EXP-1 runs evaluation).

5. **Rubric field naming** — Line 10: `gold_rubric` string; Line 28: `gold_rubric` field; Line 39: "rubric text" (dropping "gold_" prefix).

## Consistency Inconsistencies

6. **Prerequisite vs Blocker contradiction** — Prerequisites (lines 7–13) list conditions that must be true before execution, but Remaining Blockers (lines 128–131) state those same conditions are not met:
   - Line 8: frozen dataset exists at `data/exp1_queries.json`
   - Line 128: "The actual frozen dataset file `data/exp1_queries.json` is not present"
   - Line 11: Program A answer adapter emits answers
   - Line 129: "Program A answer adapter is not wired to the EXP-1 runner"
   - Line 12: correctness adjudicator available
   - Line 130: "A frozen-rubric adjudicator is not wired to the EXP-1 runner"

7. **Output layout vs Reproducibility procedure** — Line 123 requires preserving "pooled summaries" but the output layout (lines 100–115) does not list any pooled summary artifact.

8. **Artifact spec files** — Lines 70–76 state `write_artifact_specifications` produces three `.spec.json` files, but line 103–106 shows them under `artifact_specs/` subdirectory while line 121 says to generate them "into the run directory" (ambiguous: run root vs subdirectory).

9. **Seed directory naming** — Line 108: `seed_<seed>/`; Line 122: "preregistered independent seeds" (plural) but no specification of seed value format or range.

## Reference Inconsistencies

10. **EXP1_PREREGISTRATION.md** — Referenced at line 7 as the authority for `config.json`, but this file does not appear in the directory layout (lines 82–95) or anywhere else in the document.

11. **Source file references** — Directory layout (lines 83–91) lists `artifact_specs.py`, `calibration.py`, `dataset.py`, `decision.py`, `report.py`, `rubric.py`, `run.py` but none are referenced in prerequisites, reproducibility steps, or blocker descriptions.

12. **Function references** — `load_frozen_dataset` (line 120), `write_artifact_specifications` (lines 70, 121) are called out but their module locations (e.g., `dataset.py`, `artifact_specs.py`) are not linked.

13. **Execution manifest** — Line 131 mentions "execution manifest" recording commit hash, dataset `order_hash`, adapter identity, adjudicator identity, and seed list, but this artifact does not appear in the output layout (lines 100–115).

## Prerequisite Inconsistencies

14. **Config validation prerequisite** — Line 7 requires `config.json` to match `EXP1_PREREGISTRATION.md`, but no schema or required fields for `config.json` are documented in this guide.

15. **Dataset path discrepancy** — Line 8: "currently `data/exp1_queries.json`" implies the path is configurable, but line 19 hardcodes the same path under "Frozen Dataset" and line 120 hardcodes it in the reproducibility procedure.

16. **Adjudicator output requirement** — Line 57 allows `correctness` or `y_i`; line 58 adds optional `fabricated_factual_answer`; but line 60 states "Correctness must be based on answer content against the frozen `gold_rubric`" — the prerequisite does not require the adjudicator to *use* the rubric, only to be "available."

17. **No-change rule scope** — Line 13 lists "bin boundary, tier mapping, threshold, query label, rubric, or correctness rule" but omits "seed list" (referenced in line 131 manifest) and "config.json" (line 7).

## Reproducibility Instruction Inconsistencies

18. **Step 1 vs Blockers** — Step 1 (line 119) says "Confirm the working tree contains the intended EXP-1 code, config, frozen dataset, and rubric files" but Blockers (lines 128–131) confirm the frozen dataset and rubric adjudicator are absent.

19. **Step 3 timing** — Step 3 (line 121) says to generate artifact specifications "before execution outputs are written" but Step 4 (line 122) says to execute seeds "only after the frozen dataset and rubric validation pass" — the spec generation is not explicitly gated on validation passing.

20. **Step 5 completeness** — Step 5 (line 123) lists "pooled summaries" as required preservation but no pooled summary artifact is defined in Generated Outputs (lines 64–76) or output layout (lines 100–115).

21. **Step 6 vs Prerequisite 13** — Step 6 (line 124) treats post-output changes as protocol violations; Prerequisite 13 (line 13) states "No bin boundary... has been changed after seeing EXP-1 outputs" — duplicate rule with no cross-reference.

22. **Missing reproducibility steps** — No step records the commit hash, code revision, or execution manifest (referenced in line 131) despite Step 5 requiring "code revision" preservation.
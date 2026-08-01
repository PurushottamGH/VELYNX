# P1 Scientific Consistency Audit — SKB v1.0

- **Audit date:** 2026-07-28
- **Scope:** Canonical SKB records, migrated source evidence, registry projections, and Living Scientific Model
- **Audit posture:** Conservative; unresolved provenance remains visible

## 1. Audit questions

1. Is every scientific conclusion linked to observations and claim-relative evidence?
2. Are observations separated from interpretations?
3. Are invalid experiments prevented from becoming evidence against a hypothesis?
4. Do hypothesis and mechanism statuses agree with Decisions?
5. Are negative results retained with scope?
6. Are planned experiments distinguishable from completed executions?
7. Are legacy authority terms prevented from silently overriding SOS lifecycle states?
8. Are cross-references unique and resolvable?
9. Does the Living Scientific Model match the canonical database?

## 2. Automated structural audit

The machine-readable registry parses as YAML and contains:

| Object type | Count |
|---|---:|
| Hypotheses | 10 |
| Experiments | 9 |
| Mechanisms | 8 |
| Assumptions | 9 |
| Unknowns | 9 |
| Scientific debt items | 10 |
| Negative results | 5 |
| Observations | 14 |
| Evidence records | 8 |
| Decisions | 9 |
| Typed relations | 20 |
| Supported theories | 0 |

After the M1 readiness update, canonical counts are 103 permanent records and 26 relations: 10 hypotheses, 9 experiments, 8 mechanisms, 11 assumptions, 10 unknowns, 12 debt items, 5 negative results, 19 observations, 9 evidence records, and 10 decisions. Structural validation was rerun after the update.

A dedicated validation pass checks ID format, uniqueness, referenced-ID existence, evidence source observations, relation endpoints, and theory emptiness consistency.

## 3. Resolved contradictions

### C-01 — E0 `running` versus completed artifact

- **Legacy state:** `experiment_registry.yaml` labels E0 `running`.
- **Recovered state:** a timestamped aggregate contains three per-seed executions and an aggregate decision.
- **Resolution:** `EXP-2026-0004` is `Interpreted` as an execution family, with result validity `invalid` for H*.
- **Why:** Completion and validity are separate axes.

### C-02 — E0 “inconclusive due to 3 seeds” versus absent treatment

- **Artifact text:** aggregate says three seeds, need five.
- **More fundamental diagnostic:** all conditions report zero growth events and units mismatch.
- **Resolution:** primary ruling is invalid treatment/non-operability; seed insufficiency is secondary. H* receives No Verdict.

### C-03 — EXP-0 unavailable/unrun versus result artifacts

- **Older certification:** reported paraphrase material missing or experiment not run.
- **Current repository:** contains `paraphrases.json`, two manifests, and two summaries.
- **Resolution:** migrate the completed result; preserve missing transition history as `OBS-2026-0013` and `UNK-2026-0004`.

### C-04 — R1 “rejected” versus statistical non-significance

- **Risk:** converting `p=0.866` into proof of equivalence.
- **Resolution:** reject only the claimed measured advantage in the tested scope; explicitly state that the wide CI does not establish equivalence or universal falsification.

### C-05 — Calibration “rejected” versus an achievable-system hypothesis

- **Historical evidence:** one `CERTAIN` fabrication failure.
- **Resolution:** reject the claim that the historical instance was already honest; retain the general hypothesis as Exploratory pending EXP-1.

### C-06 — M0 replay benefit versus causal replay mechanism

- **Observation:** seed-0 replay_always has lower measured forgetting.
- **Confounds:** update count, decay, compute, memory content, replay budget, metric construct.
- **Resolution:** weak evidence for a bundled association plus strong limiting evidence; no mechanism acceptance.

### C-07 — T-01 versus T-02

- **Problem:** stateful T-02 contains T-01 and supplies no distinct prediction.
- **Resolution:** retain T-01's carrier-dependence hypothesis; archive T-02 as measurement discipline.

### C-08 — Legacy `FACT`, `ACCEPTED`, `KEEP`, and `canonical`

- **Problem:** terms mix observation, engineering necessity, authority, and scientific validation.
- **Resolution:** source labels remain provenance only. Present status comes from SOS evidence and Decision records.

## 4. Unresolved contradictions and gaps

| ID | Gap | Present treatment | Closure condition |
|---|---|---|---|
| U-01 | Why two EXP-0 artifact directories contain the same summary | Both executions recorded; later artifact used as canonical observation source | execution log or commit history explains duplication |
| U-02 | Exact code commit for R1 reconstruction | report treated as immutable migrated source | code/runtime manifest recovered or independent rerun |
| U-03 | M0 stored artifact does not match reported default run | independent reproduction recorded; provenance debt open | committed exact artifact and runtime manifest |
| U-04 | Designer-injection audit's behavioral percentages are estimates | raw enumeration admitted; percentages explicitly limited | intervention-based sensitivity analysis |
| U-05 | E0 units diagnosis is artifact-authored | accepted as execution diagnostic, not universal mathematical proof | independent dimensional audit and trigger controls |
| U-06 | No accepted execution for Experiment Zero | planned only | complete preregistered run |
| U-07 | No owner-specific assignments for unknown resolution | SOS is default owner | execution records assign accountable investigator |
| U-08 | M1 apparatus absent from committed revision | all current M1 runs non-confirmatory; Cycle 001 delayed | clean committed revision and manifest from isolated checkout |
| U-09 | Current required automation does not assess live M1 evidence surfaces | green status receives no M1 readiness meaning | fresh-checkout required CI pass with known-failure sensitivity |
| U-10 | Same-config repeated-run artifact identity not established across isolated checkouts | variance and confirmatory results blocked | identical decision-relevant metrics and normalized artifact hashes |

## 5. Category-error audit

| Potential error | Result |
|---|---|
| Tests treated as scientific evidence | Prevented: M0 tests are observations of conformance only |
| Implementation treated as hypothesis support | Prevented: E0 engineering completion separated from absent treatment |
| Negative result generalized universally | Prevented: R1, EXP-0, calibration all scoped |
| Invalid run treated as negative hypothesis evidence | Prevented: E0 evidence direction explicitly uninformative about H* |
| Non-significance treated as equivalence | Prevented: R1 interval limitation explicit |
| Confidence treated as evidence | Prevented: confidence levels cite basis but create no edge |
| Decision treated as evidence | Prevented: Decisions consume evidence; they do not originate it |
| Observation wording contains causal claim | No material violation found in registry projection |
| Planned protocol treated as completed result | Prevented for EXP-1, EXP-2, V0 validation, EXP-Z0 |
| Local tests treated as confirmatory evidence | Prevented: 202 tests and 88.5% coverage establish working-tree conformance only |
| Green CI treated as apparatus validity | Prevented: committed gates omit or mis-target M1 and are assigned no confirmatory weight |

## 6. Traceability audit

### Fully traceable evidence chains

- R1: source report → `OBS-0001` → `EVD-0001` → `HYP-0005` → `DEC-0003` → `NEG-0001`.
- EXP-0 Tier-2: source JSON → `OBS-0003` → `EVD-0002` → `HYP-0006` → `DEC-0002` → `NEG-0002`.
- Calibration Q6: source report → `OBS-0011` → `EVD-0004` → `HYP-0002` → `DEC-0005` → `NEG-0004`.
- E0: aggregate → `OBS-0005..0007` → `EVD-0005` → `DEC-0004` → `SDEBT-0009` and `NEG-0005`.
- M0: scientific review → `OBS-0008..0010` → `EVD-0006/0007` → `HYP-0007/0008` → `DEC-0006/0007`.
- M1 readiness: manifest/repository/CI/gate/local-test audit → `OBS-0015..0019` → `EVD-0009` → `ASM-0010/0011`, `SDEBT-0010..0012`, `EXP-0007` → `DEC-0010`.

### Hypotheses intentionally lacking evidence support

- affective indexing;
- historical-carrier dependence;
- a supported P1 theory.

Their lack of evidence is explicit and correct.

## 7. Living-model consistency

The Living Scientific Model agrees with canonical status on all decision-bearing objects:

- no validated hypothesis or theory;
- two rejected scoped hypotheses;
- H* untested, not rejected;
- calibration historical instance contradicted but general hypothesis open;
- replay/surprise exploratory;
- affective indexing and carrier dependence proposed;
- E0 scientifically stopped pending operability;
- Cycle 001 execution is delayed until minimum M1 admissibility gates pass;
- confirmatory execution is blocked by platform provenance/gate defects plus pre-existing protocol and scientific-validity requirements;
- after readiness, matched-random replay plus metric repair is the smallest active v0 discriminator.

## 8. Audit verdict

**PASS WITH CONFIRMATORY READINESS BLOCKERS**

SKB v1.1 is internally coherent enough to serve as P1's initial scientific memory. It does not claim archival completeness for every historical engineering test or document. It does provide complete canonical coverage of the presently decision-relevant hypotheses, mechanisms, assumptions, unknowns, completed evidence anchors, negative results, observations, evidence relations, debts, and decisions recovered during initialization.

The remaining gaps are recorded rather than silently harmonized.

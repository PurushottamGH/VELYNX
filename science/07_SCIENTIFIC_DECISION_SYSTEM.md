# Scientific Decision System

- **Version:** 1.0.0
- **Record prefix:** `DEC-`
- **Purpose:** Make every scientific-state transition explicit, evidence-linked, reversible, and scope-bounded.

## 1. Decision record

Every decision records:

- permanent ID and timestamp;
- object(s) affected and prior state;
- action and resulting state;
- question decided;
- evidence considered, including negative and conflicting evidence;
- validity and scope assessment;
- assumptions and unresolved uncertainties;
- strongest alternative explanation;
- criteria applied;
- rationale and dissent/limitations;
- confidence before and after;
- consequences for theories, roadmap, debt, and Living Scientific Model;
- reversal trigger and successor links;
- Chief Scientist authorization.

A decision references evidence; it does not contain or alter results.

## 2. Decision actions

### Accept

Use when phase-appropriate criteria are met within a stated scope.

- In Discovery, “accept” means **accept for validation or continued investigation**, not validate as true.
- In Validation, it may move a hypothesis to `Validated` within scope.

### Reject

Use when valid evidence meets a predefined adverse condition or makes the proposition scientifically noncompetitive within scope. Rejection records whether the effect, mechanism, or generalization failed.

### Revise

Use when the original hypothesis is partly informative but wording, scope, mechanism, metric, or decision rule is defective. Material revision creates a new version and prevents retroactive confirmation.

### Split

Use when one hypothesis combines separable claims with different evidence, mechanisms, or scopes. The parent is superseded; child hypotheses inherit links but not automatic evidential status.

### Merge

Use when hypotheses are empirically indistinguishable or redundant and a unified statement preserves all discriminating predictions. If identical observables remain under all feasible tests, record nonidentifiability rather than arbitrary preference.

### Archive

Use when a line is inactive, low-priority, infeasible, or outside current scope without an evidential rejection. Archive is not rejection.

### Supersede

Use when a successor record replaces wording, evidence synthesis, theory, assumption, or policy. The prior record remains immutable and linked.

## 3. Decision algorithm

After each completed experiment:

1. **Verify validity:** Was the execution valid under its declared phase and protocol?
2. **Record observations:** What occurred, without interpretation?
3. **Assess relevance:** Which claims can this result actually bear on?
4. **Compare alternatives:** Do null or competing explanations remain viable?
5. **Assess magnitude and uncertainty:** Is the effect decision-relevant, not merely detectable?
6. **Check scope:** What is the narrowest justified conclusion?
7. **Update confidence:** What changed and why?
8. **Select action:** Accept, Reject, Revise, Split, Merge, Archive, Supersede, or No Verdict.
9. **Propagate:** Update dependencies, debt, uncertainties, theories, roadmap, and Living Model.
10. **Choose next experiment:** Select the smallest experiment with the greatest expected decision value.

## 4. No Verdict

If evidence is invalid, underpowered for the intended claim, nonidentifying, or contradictory, issue `No Verdict` and update an uncertainty or debt item. Indeterminacy must not be converted to acceptance or rejection for convenience.

## 5. Phase gates

| Transition | Minimum evidential meaning |
|---|---|
| Proposed → Exploratory | Testable statement and decision-changing discovery experiment |
| Exploratory → Under Validation | Repeated or strong exploratory signal; construct and major confounds sufficiently understood; claim worth validation cost |
| Under Validation → Validated | Validation criteria met with fair controls, relevant effect, uncertainty, reproducibility, and scoped causal interpretation |
| Any → Rejected | Valid evidence meets adverse criterion or simpler alternative dominates within scope |
| Validated → Challenged/Under Validation | Material conflicting evidence, failed replication, invalidated assumption, or wider-scope test |

## 6. Confidence is not a vote

Evidence count, majority preference, engineering effort, and prior commitment do not determine decisions. Confidence is an explicit scientific judgment with reasons and may remain wide.

## 7. Reversal

Every decision states what future evidence would reverse it. Reversal creates a new Decision and preserves the entire prior chain.

# Theory Registry Standard

- **Version:** 1.0.0
- **Record prefix:** `THY-`
- **Purpose:** Govern how validated hypotheses become coherent, predictive, revisable scientific theories.

## 1. Definition

A P1 theory is a versioned, scope-bounded explanatory model that:

1. integrates at least two independently supported hypotheses or phenomena;
2. specifies causal or computational relationships among them;
3. explains existing evidence better than named alternatives;
4. generates at least one novel, risky, discriminating prediction;
5. states assumptions, boundary conditions, and failure modes;
6. remains revisable and replaceable.

A list of compatible hypotheses, a mechanism diagram, or an implementation architecture is not a theory.

## 2. Schema

Every theory records:

- ID, version, title, and explanatory statement;
- target phenomena and scope;
- constituent validated hypotheses and their independence structure;
- causal/computational model;
- load-bearing assumptions;
- named competing theories and null explanation;
- evidence explained, evidence not explained, and counter-evidence;
- compression/unification gain over separate hypotheses;
- novel predictions and discriminating experiments;
- boundary conditions and known failure cases;
- confidence in phenomena, relationships, and overall theory separately;
- unresolved uncertainties and scientific debt;
- status, decision history, and supersession lineage.

## 3. Lifecycle

```text
Candidate → Provisional → Under Test → Supported
                  ├─────> Rejected
                  └─────> Revised / Split / Merged
Supported → Challenged → Supported | Revised | Rejected | Superseded
Any inactive line → Archived
```

- **Candidate:** Integrative model proposed; minimum theory criteria may be incomplete.
- **Provisional:** Criteria 1–5 are specified and alternatives named.
- **Under Test:** Novel discriminating predictions are being evaluated.
- **Supported:** At least one risky novel prediction survives fair comparison, and the theory explains more than constituent hypotheses alone within scope.
- **Challenged:** Material contrary evidence or a stronger alternative exists.
- **Rejected:** Core predictions or relationships fail within declared scope.
- **Superseded:** A successor explains the evidence at least as well with greater predictive adequacy, scope discipline, or simplicity.

## 4. Promotion from hypotheses

Multiple validated hypotheses may form a Candidate theory only if:

- they concern related phenomena;
- their evidence is not wholly dependent on one shared execution or assumption;
- an explicit relational model connects them;
- the combined model makes a prediction not entailed by each hypothesis independently.

Promotion does not increase confidence automatically. Theory evidence begins with inherited support and must add discriminating predictions.

## 5. Theory comparison

Compare theories using:

1. predictive discrimination on untouched conditions;
2. explanatory coverage;
3. calibration and uncertainty;
4. robustness to assumption changes;
5. parsimony after accounting for hidden flexibility;
6. ability to accommodate negative results without ad hoc revision;
7. transfer across prespecified environment classes.

Complexity penalties apply to free parameters, exception clauses, untestable entities, and researcher degrees of freedom—not code size alone.

## 6. Revision

- **PATCH:** Clarification without predictive change.
- **MINOR:** Adds a bounded prediction, phenomenon, or assumption without changing core relationships.
- **MAJOR:** Changes causal/computational relationships, scope, or core predictions. Major revision creates a successor theory; prior tests do not transfer automatically.

A revision must identify which result forced it, whether the change was predicted, and what new observation could reject the revision. Repeated post hoc rescue creates a scientific-debt item.

## 7. Replacement and pluralism

A theory is replaced only by a Decision that compares both against the same evidence and alternatives. Multiple theories may coexist when evidence does not discriminate them. In that case, nonidentifiability is an Unknown and the roadmap prioritizes a separating experiment.

No current P1 hypothesis set should be presumed to form a validated theory. Theory formation is an earned future state.

# Scientific Knowledge Base Standard

- **Version:** 1.0.0
- **Purpose:** Maintain P1’s evolving knowledge without mixing observation, evidence, hypothesis, theory, speculation, or uncertainty.

## 1. Knowledge object types

### Observed fact

A directly recorded measurement, implementation fact, or definitional fact with provenance. A fact says what was observed, not why.

Required: scope, source, method, version/time, limitations, and links to the observation/result.

### Evidence

A claim-relative relation admitting an observation or result as relevant under stated provenance, relevance, and validity conditions.

Required: target claim/hypothesis, direction, strength, scope, validity, limitations, and source result.

### Hypothesis

A falsifiable proposition paired with a feasible discriminating test and adverse outcome. Governed by the Hypothesis Registry.

### Theory

A coherent explanatory model integrating multiple validated hypotheses, generating novel discriminating predictions, and outperforming alternatives within a stated scope. Governed by the Theory Registry.

### Speculation

An idea not yet operationalized or insufficiently constrained to count as a hypothesis. Speculation may motivate questions but cannot support decisions about scientific validity.

### Unknown

A material unresolved uncertainty with an operational resolution criterion. Unknowns remain first-class even after resolution; history is preserved.

## 2. Prohibited category errors

- Performance is not mechanism evidence by itself.
- Software tests are not scientific evidence by themselves.
- A citation is a source, not evidence, until its relevant observation is bounded.
- Confidence is not evidence.
- A decision is not evidence.
- A hypothesis is not a fact because it is implemented.
- A theory is not a collection of compatible hypotheses; it must explain and predict.
- “No alternative found” does not establish uniqueness.

## 3. Knowledge record schema

Every item has:

- permanent ID (`OBS-`, `EVD-`, `HYP-`, `THY-`, `SPC-`, `UNK-`);
- object type and schema version;
- concise statement;
- explicit scope;
- provenance and originating record;
- status and confidence, if applicable;
- supporting, opposing, and limiting links;
- dependencies and contradictions;
- creation/update decisions;
- supersession lineage;
- last review time.

## 4. Knowledge graph relations

Permitted typed relationships include:

- `observation_from_source`
- `evidence_admits_observation`
- `evidence_supports_or_opposes_hypothesis`
- `hypothesis_requires_assumption`
- `hypothesis_competes_with_hypothesis`
- `theory_explains_hypothesis`
- `theory_predicts_hypothesis`
- `unknown_limits_object`
- `result_resolves_unknown`
- `decision_changes_status`
- `object_supersedes_object`
- `object_contradicts_object`

Relations must not silently imply stronger semantics than their names.

## 5. Evidence strength

Evidence strength is assessed, not counted. Record:

1. internal validity;
2. construct validity;
3. relevance to the target claim;
4. precision/uncertainty;
5. independence from existing evidence;
6. scope and generalization limits;
7. credible bias and confounding.

Multiple executions sharing code, data, assumptions, or failure modes are not treated as independent merely because their seed differs.

## 6. Synthesis rules

1. Synthesis includes favorable, unfavorable, ambiguous, invalid, and missing-result information.
2. Conflicting valid evidence opens or updates an Unknown and may return a hypothesis to validation.
3. A narrow high-validity result does not become a broad fact.
4. Exploratory evidence can prioritize validation but ordinarily cannot alone validate a mechanism.
5. Facts and theories are versioned; correction occurs by supersession.
6. The Living Scientific Model is a human-readable projection of this knowledge base, not a second source of truth.

## 7. Current-state views

The knowledge base must support views by:

- object type;
- hypothesis/theory;
- experiment;
- mechanism;
- environment class;
- scientific phase;
- confidence;
- unresolved contradiction;
- negative result;
- supersession lineage.

## 8. Migration

Legacy epistemic tags (`[FACT]`, `[HYPOTHESIS]`, `[SPECULATION]`, `[REJECTED]`) are candidate classifications only. Each migrated statement requires provenance, scope, and a migration Decision. Existing documents remain sources and historical context until migration is complete.

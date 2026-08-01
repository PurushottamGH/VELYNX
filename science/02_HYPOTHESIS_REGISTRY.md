# Hypothesis Registry Standard

- **Version:** 1.0.0
- **Record prefix:** `HYP-`
- **Purpose:** Preserve every testable proposition, its scope, alternatives, evidence, dependencies, confidence evolution, and lifecycle.

## 1. Record schema

Every hypothesis record contains:

| Field | Requirement |
|---|---|
| `id` | Permanent `HYP-YYYY-NNNN`; never reused |
| `version` | Semantic version of hypothesis wording and decision rule |
| `title` | Neutral, concise label |
| `statement` | Operational, falsifiable proposition |
| `scope` | Population/system, environment class, conditions, versions, time bounds |
| `phase` | Discovery or Validation; Publication is not a hypothesis phase |
| `motivation` | Why resolving it matters |
| `expected_mechanism` | Proposed causal account, explicitly hypothetical |
| `alternatives` | Null and strongest credible competing explanations |
| `predictions` | Outcomes that differ among alternatives |
| `adverse_outcomes` | Feasible outcomes that count against the hypothesis |
| `variables` | Independent, dependent, controlled, and likely confounding variables |
| `dependencies` | Assumptions, measurements, other hypotheses, theories, worlds/datasets |
| `experiments` | Linked experiment IDs, planned and completed |
| `evidence_for` | Claim-specific Evidence IDs |
| `evidence_against` | Claim-specific Evidence IDs |
| `unresolved_evidence` | Ambiguous or validity-limited Evidence IDs |
| `confidence` | Structured confidence record, never evidence itself |
| `status` | Controlled lifecycle state |
| `decision_history` | Ordered Scientific Decision IDs |
| `supersedes` / `superseded_by` | Version lineage |
| `owner` | Scientific steward, not engineering owner |
| `created_at` / `updated_at` | Timezone-qualified timestamps |

## 2. Lifecycle

```text
Proposed
  ├─> Exploratory
  │     ├─> Under Validation
  │     │     ├─> Validated
  │     │     ├─> Rejected
  │     │     └─> Revised / Split / Merged
  │     ├─> Rejected
  │     ├─> Revised / Split / Merged
  │     └─> Archived
  └─> Archived

Any nonterminal state may be Superseded by a new version.
Validated may return to Under Validation when challenged.
Rejected may return only through a new version or a Decision citing materially new conditions/evidence.
```

### Status meanings

- **Proposed:** Testable wording exists; no informative execution yet.
- **Exploratory:** Discovery experiments are active or informative exploratory observations exist.
- **Under Validation:** A scoped confirmatory claim is being tested with validation-grade controls.
- **Validated:** Decision criteria were met within the declared scope; not universally true.
- **Rejected:** Valid evidence met a declared adverse/rejection condition within scope.
- **Superseded:** A successor record replaces the wording, scope, or model.
- **Archived:** Not currently pursued; no evidential verdict implied.

## 3. Versioning

- **MAJOR:** Meaning, causal mechanism, primary outcome, decision rule, or scope changes materially. New major version is a distinct confirmatory target; prior evidence does not transfer automatically.
- **MINOR:** Adds a prediction, alternative, dependency, or narrower sub-scope without changing existing meaning.
- **PATCH:** Clarification that changes no testable content.

Records are append-only after entering `Under Validation`, `Validated`, or `Rejected`. A material change creates a successor linked by `supersedes`.

## 4. Confidence evolution

Confidence is represented as:

```yaml
confidence:
  level: very_low | low | moderate | high | very_high
  probability_range: optional bounded interval
  basis: short rationale
  scope: explicit scope
  evidence_for: []
  evidence_against: []
  unresolved: []
  last_decision: DEC-...
  updated_at: timestamp
```

Rules:

1. Confidence does not update automatically from p-values, evidence count, or model scores.
2. Every change cites a Decision and new evidence or a discovered validity defect.
3. Discovery evidence normally moves confidence by at most one qualitative level unless it directly falsifies a necessary prediction.
4. Validation evidence may move confidence more strongly, but only within tested scope.
5. Contradictory valid evidence widens uncertainty or lowers confidence until discriminated.
6. Confidence in the mechanism and confidence in the observed effect are recorded separately where they differ.

## 5. Dependencies

Dependencies use typed links:

- `requires_assumption`
- `requires_measurement_validity`
- `requires_hypothesis`
- `competes_with`
- `subsumes`
- `specializes`
- `derived_from_theory`
- `tested_in_environment`

A hypothesis cannot become `Validated` if a load-bearing dependency is rejected or materially unresolved, unless the decision explicitly demonstrates independence from it.

## 6. Evidence linkage

A result is not linked directly as support without an Evidence record specifying relevance and validity. Each evidence link records direction (`supports`, `opposes`, `ambiguous`), strength, scope, and limitations.

## 7. Minimum migration rule

Legacy hypotheses are imported with their original wording and provenance. Terms such as “accepted,” “canonical,” or “fact” are not carried over as evidential statuses. Existing H*, H1, H2, T-01, T-02, and P1 v0 replay hypotheses require separate migration Decisions.

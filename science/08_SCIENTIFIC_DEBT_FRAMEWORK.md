# Scientific Debt Framework

- **Version:** 1.0.0
- **Record prefix:** `SDEBT-`
- **Purpose:** Track unresolved scientific weaknesses that can distort inference, waste experiments, or harden unsupported mechanisms.

## 1. Definition

Scientific debt is any unresolved weakness that increases the probability of false discovery, false rejection, uninterpretable results, hidden assumptions, or unjustified generalization.

Scientific debt is not ordinary engineering backlog. A missing feature is not scientific debt unless it blocks measurement, control, reproducibility, or interpretation.

## 2. Debt categories

- `measurement_validity`
- `missing_control`
- `confounding`
- `underpowered_evidence`
- `hidden_assumption`
- `unmeasured_bias`
- `nonidentifiability`
- `reproducibility`
- `scope_overreach`
- `negative_result_gap`
- `theory_patch`
- `provenance_gap`
- `terminology_equivocation`

## 3. Record schema

Each debt item records:

- ID, title, category, and description;
- affected hypotheses, theories, experiments, metrics, mechanisms, and decisions;
- evidence that the weakness exists;
- risk: probability and consequence of misleading science;
- urgency and blocking impact;
- scope of claims currently prohibited or weakened;
- required evidence to retire or reduce the debt;
- smallest resolving experiment or analysis;
- feasibility and estimated scientific cost;
- priority and rationale;
- status, owner, review date, and decision history;
- dependencies and replacement links.

## 4. Severity and blocking impact

### Severity

- **Critical:** Can invert or fabricate the program’s central conclusion.
- **High:** Can invalidate a major mechanism or causal claim.
- **Moderate:** Limits precision, robustness, or scope but not the core observed effect.
- **Low:** Documentation or secondary uncertainty with limited decision impact.

### Blocking impact

- **B0 — None:** Track; does not block current discovery.
- **B1 — Interpretation:** Experiment may run, but specified inference is prohibited.
- **B2 — Validation:** Discovery may continue; validation claim cannot be accepted.
- **B3 — Program decision:** Major roadmap or theory decision cannot proceed.
- **B4 — Scientific stop:** Continuing would predictably generate uninterpretable or misleading evidence.

## 5. Priority

Recommended ranking:

`Priority = Severity × BlockingImpact × DecisionLikelihood × Exposure / (1 + ResolutionCost)`

Use ordinal values 1–4 with written rationale. Numeric rank is advisory; hidden catastrophic failure may override it.

## 6. Lifecycle

```text
Open → Triaged → Mitigating → Reduced | Retired
Reduced → Open (if evidence shows residual materiality)
Any state → Superseded
```

- **Reduced:** Risk decreased but remains material.
- **Retired:** Required evidence was obtained or the affected claim/mechanism was removed.

A debt item is not retired because code was added. It retires only when the scientific weakness is removed or bounded by evidence.

## 7. Initial P1 debt inventory

| ID | Debt | Severity | Block | Required evidence |
|---|---|---:|---:|---|
| SDEBT-2026-0001 | P1 v0 replay comparisons confound history, update count, replay budget, and decay applications | Critical | B2 | Resource-matched replay contrast |
| SDEBT-2026-0002 | Surprise gating lacks equal-budget random timing control | Critical | B2 | Matched random gate experiment |
| SDEBT-2026-0003 | P1 v0 forgetting metric can reward weak initial learning | High | B2 | Final excess-loss and joint stability/plasticity analysis |
| SDEBT-2026-0004 | Current scientific records conflict in authority and terminology | High | B1 | Record-by-record migration and decisions |
| SDEBT-2026-0005 | Legacy Program D conclusions rely on mixed-quality and partly unversioned evidence | High | B2 | Provenance reconstruction and classification |
| SDEBT-2026-0006 | Most claimed capabilities lack validated measurements | Critical | B3 | Construct validation and positive/negative controls |
| SDEBT-2026-0007 | Designer-injected priors can masquerade as learned structure | Critical | B3 | Injection audits and matched ablations |
| SDEBT-2026-0008 | No P1 theory currently has validated integrative predictive support | Moderate | B1 | Independent validated hypotheses plus novel prediction |

Discovery is permitted around B1/B2 items when honestly labeled. Claims blocked at B2 or above must not be accepted until the debt is resolved or scope is narrowed.

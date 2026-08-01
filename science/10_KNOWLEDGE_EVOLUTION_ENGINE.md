# Knowledge Evolution Engine

- **Version:** 1.0.0
- **Purpose:** Define how every experiment changes the scientific model of P1 without overwriting history or converting exploratory observations into validated claims.

## 1. Input objects

The engine consumes scientific records, not prose impressions:

- experiment protocol and execution;
- immutable observations/results;
- validity determination;
- evidence relations;
- interpretation with alternatives and scope;
- affected hypotheses, assumptions, theories, uncertainties, and debt;
- a Scientific Decision.

Engineering artifacts supply provenance and measurements. They do not decide scientific state.

## 2. Post-experiment update transaction

Every completed or abandoned experiment triggers one atomic scientific update:

1. **Classify execution:** valid positive, valid negative, valid indeterminate, invalid, or abandoned.
2. **Extract observations:** Record measured outcomes without causal language.
3. **Create evidence relations:** For each affected claim, specify relevance, direction, validity, scope, and limitations.
4. **Update alternatives:** Record which explanations became less plausible, remained viable, or were newly exposed.
5. **Update confidence:** Apply evidence-linked qualitative change; never automatic score aggregation.
6. **Execute decision:** Accept, Reject, Revise, Split, Merge, Archive, Supersede, or No Verdict.
7. **Propagate dependencies:** Reassess dependent assumptions, hypotheses, theories, and decisions.
8. **Update uncertainty:** Resolve, reduce, reopen, or create Unknowns.
9. **Update scientific debt:** Retire, reduce, reopen, or create debt items.
10. **Update roadmap:** Re-rank next experiments by expected decision value.
11. **Regenerate Living Model:** Update the current-state synthesis and change log.

An experiment is not scientifically closed until steps 1–11 are complete or a Decision records why an item is not applicable.

## 3. Evidence accumulation

Evidence is accumulated by structured synthesis, not vote counting.

For each hypothesis maintain:

- evidence for, against, and ambiguous;
- independence clusters based on shared data, code, assumptions, investigators, and environments;
- internal/construct/external validity;
- effect magnitude and uncertainty;
- scope overlap;
- unresolved conflicts.

Rules:

1. Correlated replications strengthen reproducibility less than independent replications.
2. A high-validity adverse result may outweigh many weak favorable exploratory runs.
3. Heterogeneity is modeled, not averaged away.
4. Evidence outside the hypothesis scope cannot validate it; it may motivate a new version.
5. Invalid results update method/debt knowledge but not the target effect estimate.
6. Null results distinguish “evidence of absence” from “absence of informative evidence” using sensitivity and precision.

## 4. Conflict resolution

When valid evidence conflicts:

1. preserve all records;
2. open or update a `contradiction` Unknown;
3. compare scope, construct, validity, precision, and dependence;
4. test whether a moderator explains heterogeneity;
5. avoid selecting the preferred result by authority or recency;
6. design the smallest experiment that discriminates between explanations;
7. return affected validated hypotheses/theories to challenge or validation when material.

If conflict is due to different scopes, split the claim rather than force one verdict.

## 5. Theory revision

A theory update is permitted only when:

- new evidence affects a relationship, boundary, or prediction;
- the revision states whether it was anticipated;
- the changed theory generates a new adverse outcome;
- the prior theory remains recoverable;
- added exceptions and flexibility are counted as complexity/scientific debt.

Repeated accommodation without risky new prediction lowers theory confidence and may trigger rejection in favor of a simpler alternative.

## 6. Confidence update guidance

Confidence dimensions:

- effect existence;
- effect magnitude;
- causal mechanism;
- robustness;
- generalization;
- measurement validity.

These dimensions update separately. For example, replicated performance can raise confidence in an effect while leaving mechanism confidence low.

Qualitative movement considers:

- phase: discovery versus validation;
- validity and precision;
- independence;
- prior predictive success;
- alternative-explanation elimination;
- scope match.

No Bayesian numeric posterior is required unless a defensible likelihood model exists.

## 7. Dependency propagation

If an assumption is contradicted:

- identify all dependents;
- determine whether conclusions are sensitive;
- mark affected hypotheses/theories `Challenged` or narrow scope;
- reopen decisions only through new Decision records.

If a metric loses construct validity, all evidence primarily dependent on it is quarantined for reassessment; results remain intact.

If a hypothesis is rejected, theory relations requiring it are challenged, but unrelated constituent hypotheses retain their status.

## 8. Roadmap update rule

After each decision, candidate experiments are re-ranked using:

- probability of changing a major decision;
- uncertainty addressed;
- dependency breadth;
- risk of delay;
- feasibility and cost;
- whether the result distinguishes alternatives.

Experiments whose likely outcomes lead to the same decision are deprioritized.

## 9. Audit invariants

At any repository revision an independent reader must be able to answer:

- What changed scientifically?
- Which result caused it?
- What alternatives were considered?
- What remains unknown?
- Which claims are blocked?
- What evidence would reverse the decision?

If any answer cannot be traced, the update is incomplete.

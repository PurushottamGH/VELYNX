"""Minimal valid frontmatter-mapping payloads for each of the 12 schemas.

These are plain dicts (as if freshly parsed YAML) used to test schema
validation directly, independent of the Markdown/file-based fixtures
under tests/fixtures/p1_os/.
"""

from __future__ import annotations

import copy

_COMMON = {
    "title": "Example title",
    "status": "draft",
    "schema_version": "1.0",
    "created": "2026-01-01T00:00:00Z",
    "last_reviewed": None,
    "created_by": "pi",
    "provenance": [],
}


def _record(object_type: str, identifier: str, **extra) -> dict:
    payload = dict(_COMMON)
    payload["id"] = identifier
    payload["object_type"] = object_type
    payload.update(extra)
    return payload


_PAYLOADS: dict[str, dict] = {
    "research_artifact": _record(
        "research_artifact",
        "P1-AR000001",
        artifact_kind="deep_research_report",
        media_type="application/pdf",
        content_hash=None,
        external_locator=None,
    ),
    "question": _record(
        "question",
        "P1-Q000001",
        selected=False,
        scope="Explicit scope",
    ),
    "unknown": _record(
        "unknown",
        "P1-U000001",
        question_ids=["P1-Q000001"],
        priority="high",
        blocks=[],
        resolution_criteria=["Resolution criterion"],
    ),
    "claim": _record(
        "claim",
        "P1-C000001",
        question_ids=["P1-Q000001"],
        unknown_ids=["P1-U000001"],
        claim_role="candidate",
        maturity="L0",
        scope="Explicit scope",
        competes_with_claim_ids=[],
    ),
    "source": _record(
        "source",
        "P1-S000001",
        source_type="primary_empirical",
        citation="Full citation",
        persistent_identifier=None,
        access_status="not_checked",
        accessed_at=None,
    ),
    "evidence": _record(
        "evidence",
        "P1-V000001",
        source_id="P1-S000001",
        claim_links=[{"claim_id": "P1-C000001", "stance": "supports"}],
        evidence_kind="reported_result",
        scope="Exact evidence scope",
        source_locator="Results, table 1",
        verification_status="pending",
    ),
    "hypothesis": _record(
        "hypothesis",
        "P1-H000001",
        claim_ids=["P1-C000001"],
        competing_hypothesis_ids=[],
        prediction="Falsifiable prediction",
        independent_variables=["Independent variable"],
        dependent_variables=["Dependent variable"],
        falsification_criteria=["Observable criterion"],
        scope="Explicit scope",
    ),
    "experiment": _record(
        "experiment",
        "P1-E000001",
        question_id="P1-Q000001",
        hypothesis_ids=["P1-H000001"],
        competing_hypothesis_ids=[],
        competing_claim_ids=[],
        primary_metric="Primary metric",
        secondary_metrics=[],
        independent_variables=["Independent variable"],
        dependent_variables=["Dependent variable"],
        controls=["Control"],
        baselines=["Baseline"],
        resource_budgets={"compute": "Defined budget"},
        randomization="Defined procedure",
        seed_policy="Defined policy",
        exclusions=[],
        failure_conditions=["Failure condition"],
        invalidation_conditions=["Invalidation condition"],
        analysis_plan="Analysis plan",
        prospective_update_rules=[
            {
                "rule_id": "supports_primary",
                "outcome_class": "supports_primary",
                "decision_required": True,
                "proposed_actions": ["Human review required"],
            }
        ],
    ),
    "result": _record(
        "result",
        "P1-R000001",
        experiment_id="P1-E000001",
        protocol_hash="placeholder-valid-nonempty-string",
        amendment_ids=[],
        started_at="2026-01-01T00:00:00Z",
        ended_at="2026-01-01T01:00:00Z",
        environment={},
        seeds=[],
        measurements=[],
        exclusions_applied=[],
        protocol_deviations=[],
        failure_facts=[],
        outcome_class="inconclusive",
        raw_artifact_ids=[],
    ),
    "interpretation": _record(
        "interpretation",
        "P1-I000001",
        result_ids=["P1-R000001"],
        hypothesis_ids=["P1-H000001"],
        scope="Bounded scope",
        uncertainty="Explicit uncertainty",
    ),
    "decision": _record(
        "decision",
        "P1-D000001",
        result_ids=["P1-R000001"],
        interpretation_ids=["P1-I000001"],
        claim_changes=[
            {
                "claim_id": "P1-C000001",
                "prior_status": "active",
                "proposed_status": "accepted_for_use",
                "prior_maturity": "L0",
                "proposed_maturity": "L1",
                "update_rule_id": "supports_primary",
                "rationale": "Bounded rationale",
            }
        ],
        unknown_changes=[
            {
                "unknown_id": "P1-U000001",
                "prior_status": "active",
                "proposed_status": "closed",
                "rationale": "Bounded rationale",
            }
        ],
        accepted_conclusion="Scope-bounded conclusion",
        prohibited_conclusions=["No broader conclusion"],
        scope="Decision scope",
        uncertainty="Residual uncertainty",
        reversal_conditions=["Observable reversal condition"],
        reviewer_id="pi",
        decision_date="2026-01-01",
        counterevidence_review=None,
    ),
    "principle_candidate": _record(
        "principle_candidate",
        "P1-P000001",
        claim_ids=["P1-C000001"],
        scope="Explicitly bounded scope",
        reversal_conditions=["Observable reversal condition"],
    ),
}


def valid_payload(object_type: str) -> dict:
    """Return a fresh, independent deep copy of a minimal valid payload."""
    return copy.deepcopy(_PAYLOADS[object_type])


def all_object_types() -> tuple[str, ...]:
    return tuple(_PAYLOADS.keys())

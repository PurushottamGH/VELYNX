"""PA-3 -- the four frozen load-bearing deterministic predicates of ES-1 (Section 7.4).

``supports`` is the load-bearing sub-component; its failure modes dominate the
risk register (CF-R2). All thresholds come from ``constants``; no probability
numbers; no knowledge of tier->p_i or bins (CR-8/L8).

Reference: PROGRAM_A_CONFIDENCE_MECHANISM.md Section 7.4;
PROGRAM_A_MODULE_SPEC.md Section 7.
"""

from __future__ import annotations

from program_a.types import CandidateClaim, EvidenceItem


def supports(claim: CandidateClaim, evidence_item: EvidenceItem) -> bool:
    """Frozen claim-support test (entity-level).

    Parameters from ``constants.SUPPORT_TEST_PARAMS``; no probability numbers.
    """
    raise NotImplementedError(
        "TODO(phase-8): frozen claim-support test (MECHANISM Section 7.4); "
        "entity-level; params from constants.SUPPORT_TEST_PARAMS; no probability "
        "numbers."
    )


def contradicts(claim_a: CandidateClaim, claim_b: CandidateClaim) -> bool:
    """Frozen contradiction test between two claims."""
    raise NotImplementedError("TODO(phase-8): frozen contradiction test.")


def is_material(claim_a: CandidateClaim, claim_b: CandidateClaim) -> bool:
    """Frozen materiality rule: trivial variation is not a contradiction.

    Parameters from ``constants.CONTRADICTION_MATERIALITY_PARAMS``.
    """
    raise NotImplementedError(
        "TODO(phase-8): frozen materiality rule; trivial variation != contradiction; "
        "params from constants.CONTRADICTION_MATERIALITY_PARAMS."
    )


def independent_origins(items: tuple[EvidenceItem, ...]) -> int:
    """Frozen source-independence relation (``constants.INDEPENDENCE_RELATION``).

    Mirror domains are counted once; returns the independent-origin count.
    """
    raise NotImplementedError(
        "TODO(phase-8): frozen source-independence relation "
        "(constants.INDEPENDENCE_RELATION); mirror domains counted once; returns "
        "count."
    )


__all__ = ["supports", "contradicts", "is_material", "independent_origins"]

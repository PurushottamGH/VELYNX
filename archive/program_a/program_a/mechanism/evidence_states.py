"""PA-3 -- state classification: exactly one ES-1 state S0..S3 with frozen precedence.

Applies the sub-tests (``support_tests``) and thresholds (``constants``) to
select exactly one state with frozen precedence S0 -> S1 -> (S2|S3)
(DECISION_TREE Tree 2). Contains the state decision ONLY; delegates predicates
to ``support_tests`` and thresholds to ``constants``.

Contains NO probability numbers and no knowledge of tier->p_i or bin
boundaries (CR-8/L8 compliance by construction). Input is a plain string --
``QueryRecord`` is deliberately out of scope (structural L11 guard).

Reference: PROGRAM_A_CONFIDENCE_MECHANISM.md Section 7.2/7.4;
PROGRAM_A_MODULE_SPEC.md Section 8.
"""

from __future__ import annotations

from program_a.types import CandidateClaims, EvidenceSet, EvidenceStateResult


def classify(
    query_text: str,
    evidence: EvidenceSet,
    claims: CandidateClaims,
) -> EvidenceStateResult:
    """Apply the sub-tests and select exactly one ES-1 state.

    Exactly one state fires per input (states partition the corroboration
    structure -- Tree 2 invariant); precedence S0 -> S1 -> (S2|S3); all
    thresholds frozen a-priori, none data-fitted (CR-11).
    """
    raise NotImplementedError(
        "TODO(phase-8): apply sub-tests, select exactly one state with frozen "
        "precedence S0 -> S1 -> (S2|S3) (DECISION_TREE Tree 2); no probability "
        "numbers; no tier->p_i / bin knowledge (CR-8/L8)."
    )


__all__ = ["classify"]

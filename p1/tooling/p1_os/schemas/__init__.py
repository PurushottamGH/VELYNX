"""Object-schema package and dispatch (spec section 15, 20)."""

from __future__ import annotations

from ..enums import ObjectType
from .claims import Claim
from .decisions import Decision
from .evidence import Evidence
from .experiments import Experiment
from .hypotheses import Hypothesis
from .interpretations import Interpretation
from .principle_candidates import PrincipleCandidate
from .questions import Question
from .research_artifacts import ResearchArtifact
from .results import Result
from .sources import Source
from .unknowns import Unknown

SCHEMA_BY_OBJECT_TYPE: dict[str, type] = {
    ObjectType.RESEARCH_ARTIFACT.value: ResearchArtifact,
    ObjectType.QUESTION.value: Question,
    ObjectType.UNKNOWN.value: Unknown,
    ObjectType.CLAIM.value: Claim,
    ObjectType.SOURCE.value: Source,
    ObjectType.EVIDENCE.value: Evidence,
    ObjectType.HYPOTHESIS.value: Hypothesis,
    ObjectType.EXPERIMENT.value: Experiment,
    ObjectType.RESULT.value: Result,
    ObjectType.INTERPRETATION.value: Interpretation,
    ObjectType.DECISION.value: Decision,
    ObjectType.PRINCIPLE_CANDIDATE.value: PrincipleCandidate,
}


class UnknownObjectTypeError(ValueError):
    """Raised when a document's object_type has no registered schema."""


def schema_for_object_type(object_type: str) -> type:
    try:
        return SCHEMA_BY_OBJECT_TYPE[object_type]
    except KeyError as exc:
        raise UnknownObjectTypeError(
            f"No schema registered for object_type: {object_type!r}"
        ) from exc


__all__ = [
    "ResearchArtifact",
    "Question",
    "Unknown",
    "Claim",
    "Source",
    "Evidence",
    "Hypothesis",
    "Experiment",
    "Result",
    "Interpretation",
    "Decision",
    "PrincipleCandidate",
    "SCHEMA_BY_OBJECT_TYPE",
    "UnknownObjectTypeError",
    "schema_for_object_type",
]

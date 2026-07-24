"""Shared enums for Milestone 1 (spec section 3, 10, 15)."""

from __future__ import annotations

from enum import Enum


class ObjectType(str, Enum):
    RESEARCH_ARTIFACT = "research_artifact"
    QUESTION = "question"
    UNKNOWN = "unknown"
    CLAIM = "claim"
    SOURCE = "source"
    EVIDENCE = "evidence"
    HYPOTHESIS = "hypothesis"
    EXPERIMENT = "experiment"
    RESULT = "result"
    INTERPRETATION = "interpretation"
    DECISION = "decision"
    PRINCIPLE_CANDIDATE = "principle_candidate"


class ClaimMaturity(str, Enum):
    """Frozen maturity ladder (spec section 3)."""

    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"
    L5 = "L5"


class ClaimRole(str, Enum):
    CANDIDATE = "candidate"
    COMPETING = "competing"
    CONSTRAINT = "constraint"
    SCOPE_LIMIT = "scope_limit"


class AccessStatus(str, Enum):
    NOT_CHECKED = "not_checked"
    ABSTRACT_ONLY = "abstract_only"
    FULL_TEXT_CHECKED = "full_text_checked"
    INACCESSIBLE = "inaccessible"


class Stance(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    CONTEXTUALIZES = "contextualizes"
    NULL_EVIDENCE = "null_evidence"
    LIMITS = "limits"


class VerificationStatus(str, Enum):
    PENDING = "pending"
    PARTIALLY_VERIFIED = "partially_verified"
    VERIFIED = "verified"
    UNVERIFIABLE = "unverifiable"


class OutcomeClass(str, Enum):
    SUPPORTS_PRIMARY = "supports_primary"
    SUPPORTS_COMPETING = "supports_competing"
    INCONCLUSIVE = "inconclusive"
    INVALID = "invalid"


class ResearchArtifactStatus(str, Enum):
    DRAFT = "draft"


class QuestionStatus(str, Enum):
    DRAFT = "draft"


class UnknownStatus(str, Enum):
    """Values evidenced in spec section 15 (Decision.unknown_changes example)."""

    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class ClaimStatus(str, Enum):
    """Values evidenced in spec section 15 (Decision.claim_changes example)."""

    DRAFT = "draft"
    ACTIVE = "active"
    ACCEPTED_FOR_USE = "accepted_for_use"


class SourceStatus(str, Enum):
    DRAFT = "draft"


class EvidenceStatus(str, Enum):
    DRAFT = "draft"


class HypothesisStatus(str, Enum):
    DRAFT = "draft"


class ExperimentStatus(str, Enum):
    DRAFT = "draft"


class ResultStatus(str, Enum):
    DRAFT = "draft"


class InterpretationStatus(str, Enum):
    DRAFT = "draft"


class DecisionStatus(str, Enum):
    DRAFT = "draft"


class PrincipleCandidateStatus(str, Enum):
    DRAFT = "draft"

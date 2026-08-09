"""P1 Research Operating System — actor authority (invariant K4).

*Automation proposes, authority disposes.*

Article L-8 forbids Tier E records from entering runtime computation and forbids
the Observatory from writing model state, memory, thresholds, seeds, treatment
assignment or active run configuration. This module generalises that boundary
from the Observatory to every non-human actor in the laboratory, so that adding
an agent cannot quietly widen what a machine may decide.

The design target is stated as a number. A complete research cycle has fourteen
steps; exactly four of them require human judgement, and they are the four
enumerated in :data:`HUMAN_ONLY`. Everything else is drafting or mechanism, and
an agent may do it. Reducing the count below four is not an efficiency win, it
is a governance breach.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class AuthorityClass(IntEnum):
    """What kind of actor this is, ordered by what it may write."""

    #: Read the store and the repository. Write nothing. Analysis agents.
    OBSERVER = 0
    #: Draft records, protocols, code and reports as *proposals*. Commit nothing.
    PROPOSER = 1
    #: Commit non-evidence-bearing artifacts: code, tests, docs, projections,
    #: work-store rows, CI configuration.
    ENGINEER = 2
    #: Commit evidence-bearing records: decisions, claim scope, protocol freezes,
    #: attestations. Humans only.
    SCIENTIST = 3


class WriteTarget(str):
    """A namespaced thing an actor might write. Plain string subclass so that
    targets can be compared, sorted and used as dict keys without ceremony."""

    __slots__ = ()


# ---------------------------------------------------------------- targets

#: Evidence-bearing writes. Restricted to :data:`AuthorityClass.SCIENTIST`.
EVIDENCE_TARGETS: frozenset[str] = frozenset(
    {
        "skb.decision",
        "skb.claim_scope",
        "skb.claim_status",
        "skb.evidence_relation",
        "protocol.freeze",
        "governance.attestation",
        "governance.registry",
        "constitution.amendment",
    }
)

#: Non-evidence writes. Permitted from :data:`AuthorityClass.ENGINEER` up.
ENGINEERING_TARGETS: frozenset[str] = frozenset(
    {
        "repo.code",
        "repo.test",
        "repo.doc",
        "repo.ci",
        "projection.render",
        "work.row",
        "skb.observation_draft",
        "protocol.draft",
    }
)

#: Writes forbidden to *every* non-human actor regardless of class, because they
#: are the levers Article L-8 names explicitly. A human performs these through
#: the ordinary review workflow; no agent may, even a Class 3 one, which is why
#: this set is checked before the class comparison.
AGENT_FORBIDDEN: frozenset[str] = frozenset(
    {
        "runtime.threshold",
        "runtime.seed",
        "runtime.treatment_assignment",
        "runtime.run_config",
        "runtime.model_state",
        "runtime.memory",
    }
)

#: The four irreducible human decisions in a research cycle. Automation may
#: prepare each of them completely — draft the scope, assemble the admission
#: evidence, enumerate the alternatives — but the commit is human.
HUMAN_ONLY: dict[str, str] = {
    "claim_scope": (
        "The population and regime a claim covers. Lock E3 failure mode: "
        "'law called supported outside validated scope'. No measurement "
        "determines its own generalisation."
    ),
    "primitive_admission": (
        "Adding, removing or promoting a primitive. Article L-9 requires a "
        "Decision citing Measurements from admissible Runs."
    ),
    "alternative_explanations": (
        "Which alternative explanations remain unexcluded. Lock E4 records "
        "'the alternatives it fails to exclude'; enumerating candidates is "
        "mechanical, judging exclusion is not."
    ),
    "independence_attestation": (
        "Attesting that a review was independent. Definitionally a claim about "
        "a person, and the blocker X-1 that gates registration."
    ),
}


@dataclass(frozen=True)
class Actor:
    """A human or agent that may act on the laboratory."""

    name: str
    authority: AuthorityClass
    is_human: bool = False
    #: Free-text role, surfaced in escalation messages.
    role: str = ""

    def may_write(self, target: str) -> bool:
        return not self.refusal(target)

    def refusal(self, target: str) -> str | None:
        """Return the reason this actor may not write ``target``, or ``None``.

        The reason is written to be pasted into an escalation without editing.
        """
        if not self.is_human and target in AGENT_FORBIDDEN:
            return (
                f"{self.name} may not write {target!r}: Article L-8 reserves runtime "
                "thresholds, seeds, treatment assignment, run configuration, model "
                "state and memory to the human review workflow. No agent authority "
                "class grants it."
            )
        if target in EVIDENCE_TARGETS:
            if not self.is_human:
                return (
                    f"{self.name} may not write {target!r}: evidence-bearing records "
                    "require AuthorityClass.SCIENTIST, which is granted to humans "
                    "only. Draft it and escalate."
                )
            if self.authority < AuthorityClass.SCIENTIST:
                return (
                    f"{self.name} may not write {target!r}: requires "
                    f"AuthorityClass.SCIENTIST, holds {self.authority.name}."
                )
            return None
        if target in ENGINEERING_TARGETS:
            if self.authority < AuthorityClass.ENGINEER:
                return (
                    f"{self.name} may not write {target!r}: requires "
                    f"AuthorityClass.ENGINEER, holds {self.authority.name}."
                )
            return None
        return (
            f"{self.name} may not write {target!r}: unregistered write target. "
            "Add it to EVIDENCE_TARGETS or ENGINEERING_TARGETS with a reason, or "
            "it does not exist."
        )


class AuthorityError(PermissionError):
    """Raised when an actor attempts a write its authority class forbids."""


def require(actor: Actor, target: str) -> None:
    """Raise :class:`AuthorityError` unless ``actor`` may write ``target``."""
    reason = actor.refusal(target)
    if reason is not None:
        raise AuthorityError(reason)


def escalation_for(target: str) -> str | None:
    """The human decision an agent must escalate to, for a blocked target."""
    mapping = {
        "skb.claim_scope": "claim_scope",
        "skb.claim_status": "claim_scope",
        "skb.decision": "alternative_explanations",
        "skb.evidence_relation": "alternative_explanations",
        "constitution.amendment": "primitive_admission",
        "governance.attestation": "independence_attestation",
        "governance.registry": "independence_attestation",
    }
    return mapping.get(target)


__all__ = [
    "AGENT_FORBIDDEN",
    "Actor",
    "AuthorityClass",
    "AuthorityError",
    "EVIDENCE_TARGETS",
    "ENGINEERING_TARGETS",
    "HUMAN_ONLY",
    "escalation_for",
    "require",
]

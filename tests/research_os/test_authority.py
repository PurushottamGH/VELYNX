"""Actor authority (invariant K4): automation proposes, authority disposes."""

from __future__ import annotations

import pytest

from ros.authority import (
    AGENT_FORBIDDEN,
    ENGINEERING_TARGETS,
    EVIDENCE_TARGETS,
    HUMAN_ONLY,
    Actor,
    AuthorityClass,
    AuthorityError,
    escalation_for,
    require,
)

OBSERVER = Actor("analysis-agent", AuthorityClass.OBSERVER)
PROPOSER = Actor("drafting-agent", AuthorityClass.PROPOSER)
ENGINEER_AGENT = Actor("engineering-agent", AuthorityClass.ENGINEER)
# An agent granted the highest class, used to prove that class alone is not
# sufficient for evidence-bearing or runtime writes.
MAX_AGENT = Actor("over-privileged-agent", AuthorityClass.SCIENTIST)
HUMAN = Actor("chief-scientist", AuthorityClass.SCIENTIST, is_human=True)
HUMAN_ENGINEER = Actor("engineer", AuthorityClass.ENGINEER, is_human=True)


# ------------------------------------------------------------- the four


def test_exactly_four_irreducible_human_decisions():
    """The design target is a number: fourteen steps in a research cycle, four
    requiring human judgement. Dropping below four is a governance breach, not
    an efficiency gain."""
    assert len(HUMAN_ONLY) == 4
    assert set(HUMAN_ONLY) == {
        "claim_scope",
        "primitive_admission",
        "alternative_explanations",
        "independence_attestation",
    }


def test_each_human_decision_is_justified():
    """An unjustified human decision is a bottleneck waiting to be removed by
    someone who does not know why it is there."""
    assert all(len(reason) > 40 for reason in HUMAN_ONLY.values())


# ------------------------------------------------------- evidence boundary


@pytest.mark.parametrize("target", sorted(EVIDENCE_TARGETS))
def test_no_agent_may_write_evidence_at_any_class(target):
    for actor in (OBSERVER, PROPOSER, ENGINEER_AGENT, MAX_AGENT):
        assert not actor.may_write(target)


@pytest.mark.parametrize("target", sorted(EVIDENCE_TARGETS))
def test_a_human_scientist_may_write_evidence(target):
    assert HUMAN.may_write(target)


@pytest.mark.parametrize("target", sorted(EVIDENCE_TARGETS))
def test_a_human_below_scientist_may_not_write_evidence(target):
    """Being human is necessary, not sufficient."""
    assert not HUMAN_ENGINEER.may_write(target)


# -------------------------------------------------------- Article L-8 levers


@pytest.mark.parametrize("target", sorted(AGENT_FORBIDDEN))
def test_runtime_levers_are_closed_to_every_agent(target):
    """Checked before the class comparison, so even a Class 3 agent is refused.
    These are the levers Article L-8 names explicitly."""
    assert not MAX_AGENT.may_write(target)
    assert "L-8" in (MAX_AGENT.refusal(target) or "")


@pytest.mark.parametrize("target", sorted(AGENT_FORBIDDEN))
def test_runtime_levers_are_not_silently_open_to_humans_either(target):
    """A human writes these through the ordinary review workflow, not through
    this API. The target is unregistered, so the answer is a refusal that says
    so rather than an accidental yes."""
    assert not HUMAN.may_write(target)


# ------------------------------------------------------- engineering writes


@pytest.mark.parametrize("target", sorted(ENGINEERING_TARGETS))
def test_engineering_agent_may_write_engineering_targets(target):
    assert ENGINEER_AGENT.may_write(target)


@pytest.mark.parametrize("target", sorted(ENGINEERING_TARGETS))
def test_proposer_may_not_commit_engineering_targets(target):
    """A proposer drafts; committing is a higher class."""
    assert not PROPOSER.may_write(target)


def test_observer_writes_nothing():
    for target in sorted(ENGINEERING_TARGETS | EVIDENCE_TARGETS):
        assert not OBSERVER.may_write(target)


# --------------------------------------------------------- unknown targets


def test_unregistered_target_is_refused_not_allowed():
    """Failing open on an unknown target is how an agent acquires a capability
    nobody granted."""
    reason = ENGINEER_AGENT.refusal("repo.something_new")
    assert reason and "unregistered write target" in reason


def test_evidence_and_engineering_targets_are_disjoint():
    assert not (EVIDENCE_TARGETS & ENGINEERING_TARGETS)


# ----------------------------------------------------------- refusal text


def test_refusal_is_actionable():
    """The refusal is written to be pasted into an escalation unedited."""
    reason = PROPOSER.refusal("skb.decision")
    assert reason
    assert PROPOSER.name in reason
    assert "escalate" in reason.lower()


def test_require_raises_with_the_reason():
    with pytest.raises(AuthorityError, match="AuthorityClass.SCIENTIST"):
        require(ENGINEER_AGENT, "skb.decision")


def test_require_is_silent_when_permitted():
    require(HUMAN, "skb.decision")
    require(ENGINEER_AGENT, "repo.code")


# ------------------------------------------------------------ escalation


def test_blocked_evidence_targets_map_to_a_human_decision():
    for target in ("skb.claim_scope", "skb.decision", "governance.attestation"):
        assert escalation_for(target) in HUMAN_ONLY


def test_escalation_returns_none_for_unmapped_targets():
    assert escalation_for("repo.code") is None

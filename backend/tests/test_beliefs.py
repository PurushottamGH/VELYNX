"""Tests for Phase 11C — Belief State Management."""
from __future__ import annotations

import pytest

from conversation.beliefs import Belief, BeliefStore, BeliefStatus, belief_store


@pytest.fixture
def store() -> BeliefStore:
    return BeliefStore()


class TestBelief:
    def test_create_belief(self):
        b = Belief(topic="science", claim="Quantum computing uses qubits", confidence="PROBABLE")
        assert b.topic == "science"
        assert b.belief_id  # auto-generated
        assert b.status == BeliefStatus.ACTIVE


class TestBeliefStore:
    def test_add_belief(self, store: BeliefStore):
        b = store.add_belief("science", "Quantum computing uses qubits", confidence="PROBABLE")
        assert b.topic == "science"
        assert b.status == BeliefStatus.ACTIVE

    def test_get_beliefs_for_topic(self, store: BeliefStore):
        store.add_belief("science", "Claim 1")
        store.add_belief("science", "Claim 2")
        store.add_belief("history", "Claim 3")
        science = store.get_beliefs_for_topic("science")
        assert len(science) == 2
        history = store.get_beliefs_for_topic("history")
        assert len(history) == 1

    def test_update_belief(self, store: BeliefStore):
        b = store.add_belief("science", "Claim", confidence="LOW")
        updated = store.update_belief(b.belief_id, new_confidence="CERTAIN")
        assert updated is not None
        assert updated.confidence == "CERTAIN"

    def test_update_belief_with_evidence(self, store: BeliefStore):
        b = store.add_belief("science", "Claim")
        updated = store.update_belief(b.belief_id, new_evidence="Source X confirms")
        assert updated is not None
        assert "Source X confirms" in updated.supporting_evidence

    def test_contradict_belief(self, store: BeliefStore):
        b = store.add_belief("science", "Claim", confidence="CERTAIN")
        contradicted = store.contradict_belief(b.belief_id, "New evidence contradicts", "turn_5")
        assert contradicted is not None
        assert contradicted.status == BeliefStatus.CONTRADICTED
        assert "New evidence contradicts" in contradicted.contradicting_evidence

    def test_abandon_belief(self, store: BeliefStore):
        b = store.add_belief("science", "Old claim")
        abandoned = store.abandon_belief(b.belief_id)
        assert abandoned is not None
        assert abandoned.status == BeliefStatus.ABANDONED
        # Should no longer appear in active beliefs
        assert len(store.get_beliefs_for_topic("science")) == 0

    def test_get_contradicted(self, store: BeliefStore):
        b1 = store.add_belief("science", "Claim 1")
        b2 = store.add_belief("science", "Claim 2")
        store.contradict_belief(b1.belief_id, "Evidence against")
        contradicted = store.get_contradicted()
        assert len(contradicted) == 1
        assert contradicted[0].belief_id == b1.belief_id

    def test_belief_summary_empty(self, store: BeliefStore):
        assert store.get_belief_summary("nonexistent") == ""

    def test_belief_summary_format(self, store: BeliefStore):
        store.add_belief("science", "Qubits are fragile", confidence="PROBABLE")
        summary = store.get_belief_summary("science")
        assert "Qubits are fragile" in summary
        assert "PROBABLE" in summary

    def test_all_active_summary(self, store: BeliefStore):
        store.add_belief("science", "Claim 1")
        store.add_belief("history", "Claim 2")
        summary = store.get_all_active_summary()
        assert "Claim 1" in summary
        assert "Claim 2" in summary

    def test_update_nonexistent(self, store: BeliefStore):
        assert store.update_belief("fake_id", new_confidence="CERTAIN") is None

    def test_contradict_nonexistent(self, store: BeliefStore):
        assert store.contradict_belief("fake_id", "evidence") is None


class TestModuleSingleton:
    def test_singleton_exists(self):
        assert belief_store is not None
        assert isinstance(belief_store, BeliefStore)

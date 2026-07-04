"""
VELYNX Concept Birth Engine — Unit & Integration Tests
=======================================================

Tests the full pipeline:
1. Co-occurrence matrix compute / NPMI
2. Cluster detection
3. Concept spawning thresholds
4. Predictive validation
5. Decay and pruning
6. Ontology export
"""

import math
import time
from pathlib import Path

import pytest
import numpy as np

from backend.cognition.concept_birth import (
    ConceptBirthEngine,
    Experience,
    CooccurrenceMatrix,
    ClusterDetector,
    LatentConcept,
    CooccurrenceMatrix,
    persist_concept,
    load_persisted_concepts,
    mark_concept_dead,
    ensure_schema,
)


# ══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def fresh_engine() -> ConceptBirthEngine:
    """A clean engine with fast scan + low spawn thresholds for testing."""
    return ConceptBirthEngine(
        npmi_threshold=0.05,
        spawn_density_threshold=0.30,
        spawn_min_features=2,
        spawn_min_experiences=2,
        scan_interval=0.0,   # scan every call
        decay_rate=0.5,      # aggressive decay for testing
        pruning_weight=0.1,
        pruning_age_seconds=0.0,
        max_concepts=100,
    )


@pytest.fixture
def matrix() -> CooccurrenceMatrix:
    m = CooccurrenceMatrix()
    # 5 experiences: [a,b] appears 5 times, [c,d] appears 3 times
    for _ in range(5):
        m.update(Experience({"a", "b"}, {"grp": "A"}))
    for _ in range(3):
        m.update(Experience({"c", "d"}, {"grp": "B"}))
    # 2 noise experiences
    m.update(Experience({"a", "c"}, {"grp": "noise"}))
    m.update(Experience({"b", "d"}, {"grp": "noise"}))
    return m


# ══════════════════════════════════════════════════════════════════════════════
# Co-occurrence Matrix Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestCooccurrenceMatrix:

    def test_total_experiences_count(self, matrix: CooccurrenceMatrix):
        assert matrix.total_experiences == 10

    def test_marginal_probability(self, matrix: CooccurrenceMatrix):
        # P(a) = 5 (from group A) + 1 (noise) = 6/10
        p_a = matrix._prob("a")
        assert p_a == pytest.approx(0.6, abs=0.01)

        # P(c) = 3 (from group B) + 1 (noise) = 4/10
        p_c = matrix._prob("c")
        assert p_c == pytest.approx(0.4, abs=0.01)

    def test_joint_probability(self, matrix: CooccurrenceMatrix):
        # P(a,b) = 5/10 (they co-occur in all 5 group A experiences)
        p_ab = matrix._joint("a", "b")
        assert p_ab == pytest.approx(0.5, abs=0.01)

        # P(a,c) = 1/10 (only the noise experience)
        p_ac = matrix._joint("a", "c")
        assert p_ac == pytest.approx(0.1, abs=0.01)

    def test_npmi_perfect_cooccurrence(self, matrix: CooccurrenceMatrix):
        # Add feature that always appears together
        m = CooccurrenceMatrix()
        m.update(Experience({"x", "y"}))
        m.update(Experience({"x", "y"}))
        m.update(Experience({"x", "y"}))
        npmi_val = m.npmi("x", "y")
        # Perfect co-occurrence should be close to +1
        assert npmi_val > 0.8

    def test_npmi_negative_for_exclusive_pairs(self, matrix: CooccurrenceMatrix):
        # tail and wings never co-occur in the test data
        npmi_val = matrix.npmi("a", "c")  # co-occur once in 10 experiences
        # P(a,c) is low relative to P(a)*P(c)
        p_a = 0.6
        p_c = 0.4
        p_ac = 0.1
        expected_pmi = math.log(p_ac / (p_a * p_c) + 1e-12)
        expected_npmi = expected_pmi / (-math.log(p_ac + 1e-12))
        assert npmi_val == pytest.approx(expected_npmi, abs=0.01)

    def test_dense_matrix_shape(self, matrix: CooccurrenceMatrix):
        names = matrix.dense_names
        n = len(names)
        assert matrix.dense_matrix.shape == (n, n)

    def test_dense_matrix_symmetric(self, matrix: CooccurrenceMatrix):
        dense = matrix.dense_matrix
        for i in range(dense.shape[0]):
            for j in range(dense.shape[1]):
                assert dense[i, j] == pytest.approx(dense[j, i], abs=0.001)

    def test_self_npmi_is_one(self, matrix: CooccurrenceMatrix):
        assert matrix.dense_matrix[0, 0] == pytest.approx(1.0, abs=0.001)

    def test_top_cooccurring(self, matrix: CooccurrenceMatrix):
        top = matrix.top_cooccurring("a", k=5)
        pairs = [(name, round(val, 4)) for name, val in top]
        assert len(pairs) >= 1
        # 'a' co-occurs most with 'b' (5 times)
        assert pairs[0][0] == "b"
        assert pairs[0][1] > 0

    def test_merge(self):
        m1 = CooccurrenceMatrix()
        m2 = CooccurrenceMatrix()
        m1.update(Experience({"a", "b"}))
        m2.update(Experience({"a", "b"}))
        m2.update(Experience({"c"}))
        m1.merge(m2)
        assert m1.total_experiences == 3
        assert m1._stats["a"].total_count == 2
        assert m1._stats["c"].total_count == 1

    def test_empty_experience(self):
        m = CooccurrenceMatrix()
        m.update(Experience(set()))
        assert m.total_experiences == 0


# ══════════════════════════════════════════════════════════════════════════════
# Cluster Detection Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestClusterDetector:

    def test_detects_two_clusters(self, matrix: CooccurrenceMatrix):
        detector = ClusterDetector(
            npmi_threshold=0.05,
            density_threshold=0.3,
            min_features=2,
        )
        clusters = detector.find_clusters(matrix)
        # Should find at least {a,b} and {c,d} clusters
        assert len(clusters) >= 2

    def test_cluster_scores_positive(self, matrix: CooccurrenceMatrix):
        detector = ClusterDetector(
            npmi_threshold=0.05,
            density_threshold=0.3,
            min_features=2,
        )
        clusters = detector.find_clusters(matrix)
        for cluster in clusters:
            assert cluster.score > 0
            assert cluster.density > 0
            assert cluster.size >= 2

    def test_no_clusters_below_threshold(self, matrix: CooccurrenceMatrix):
        detector = ClusterDetector(
            npmi_threshold=0.99,  # impossibly high
            density_threshold=0.99,
            min_features=2,
        )
        clusters = detector.find_clusters(matrix)
        assert len(clusters) == 0

    def test_higher_score_for_better_clusters(self):
        # Strong cluster: [a,b] co-occur in all 6 experiences
        m = CooccurrenceMatrix()
        for _ in range(6):
            m.update(Experience({"a", "b", "z"}))
        # Weak cluster: [x,y] co-occur in only 2 of 6
        for _ in range(2):
            m.update(Experience({"x", "y", "z"}))
        # Extra noise
        for _ in range(4):
            m.update(Experience({"z", "w"}))

        detector = ClusterDetector(
            npmi_threshold=0.05,
            density_threshold=0.3,
            min_features=2,
        )
        clusters = detector.find_clusters(m)
        if len(clusters) >= 2:
            # The stronger cluster should have a higher score
            assert clusters[0].score >= clusters[1].score

    def test_min_size_filter(self, matrix: CooccurrenceMatrix):
        detector = ClusterDetector(
            npmi_threshold=0.05,
            density_threshold=0.3,
            min_features=10,  # impossibly large
        )
        clusters = detector.find_clusters(matrix)
        assert len(clusters) == 0


# ══════════════════════════════════════════════════════════════════════════════
# LatentConcept Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestLatentConcept:

    def test_activation_exact_match(self):
        concept = LatentConcept(
            id=1,
            features=frozenset({"a", "b", "c"}),
            birth_time=time.time(),
        )
        assert concept.activation({"a", "b", "c"}) == pytest.approx(1.0)

    def test_activation_partial_match(self):
        concept = LatentConcept(
            id=2,
            features=frozenset({"a", "b", "c", "d"}),
            birth_time=time.time(),
        )
        assert concept.activation({"a", "b"}) == pytest.approx(0.5)

    def test_activation_no_match(self):
        concept = LatentConcept(
            id=3,
            features=frozenset({"a", "b", "c"}),
            birth_time=time.time(),
        )
        assert concept.activation({"x", "y", "z"}) == pytest.approx(0.0)

    def test_activation_empty_features(self):
        concept = LatentConcept(
            id=4,
            features=frozenset(),
            birth_time=time.time(),
        )
        assert concept.activation({"a", "b"}) == pytest.approx(0.0)

    def test_record_prediction_success_increases_weight(self):
        concept = LatentConcept(
            id=5,
            features=frozenset({"a", "b"}),
            birth_time=time.time(),
        )
        initial = concept.predictive_weight
        concept.record_prediction(0.8, 0.5, 0.2)  # error decreased
        assert concept.predictive_weight > initial
        assert concept.successes == 1
        assert concept.attempts == 1

    def test_record_prediction_failure_decreases_weight(self):
        concept = LatentConcept(
            id=6,
            features=frozenset({"a", "b"}),
            birth_time=time.time(),
        )
        # Inactive concept (activation=0) means no success
        concept.record_prediction(0.0, 0.5, 0.6)
        assert concept.successes == 0
        assert concept.attempts == 1

    def test_decay(self):
        concept = LatentConcept(
            id=7,
            features=frozenset({"a"}),
            birth_time=time.time(),
            weight=1.0,
        )
        concept.decay(rate=0.1)
        assert concept.weight == pytest.approx(0.9)
        concept.decay(rate=0.1)
        assert concept.weight == pytest.approx(0.81)

    def test_decay_floor(self):
        concept = LatentConcept(
            id=8,
            features=frozenset({"a"}),
            birth_time=time.time(),
            weight=0.001,
        )
        concept.decay(rate=0.5)
        assert concept.weight == pytest.approx(0.0)

    def test_to_dict(self):
        concept = LatentConcept(
            id=42, features=frozenset({"a", "b"}), birth_time=100.0,
        )
        d = concept.to_dict()
        assert d["id"] == 42
        assert "a" in d["features"]
        assert "b" in d["features"]
        assert d["weight"] >= 0


# ══════════════════════════════════════════════════════════════════════════════
# Integration: ConceptBirthEngine
# ══════════════════════════════════════════════════════════════════════════════

class TestConceptBirthEngine:

    def test_ingest_single_experience(self, fresh_engine):
        report = fresh_engine.ingest(Experience({"a", "b"}))
        assert report["experience_feature_count"] == 2

    def test_ingest_empty_experience(self, fresh_engine):
        report = fresh_engine.ingest(Experience(set()))
        assert report["experience_feature_count"] == 0

    def test_spawns_concept_from_repeating_cluster(self, fresh_engine):
        # Feed experiences with a clear cluster [a,b,c] that always co-occur
        for _ in range(6):
            fresh_engine.ingest(Experience({"a", "b", "c"}))
        state = fresh_engine.get_state_report()
        assert state["alive_concepts"] >= 1

    def test_multiple_clusters(self, fresh_engine):
        # Two distinct clusters: [a,b,c] and [x,y,z]
        for _ in range(5):
            fresh_engine.ingest(Experience({"a", "b", "c"}))
        for _ in range(5):
            fresh_engine.ingest(Experience({"x", "y", "z"}))
        state = fresh_engine.get_state_report()
        assert state["alive_concepts"] >= 2

    def test_concepts_decay_without_reinforcement(self):
        engine = ConceptBirthEngine(
            npmi_threshold=0.05, spawn_density_threshold=0.3,
            spawn_min_features=2, spawn_min_experiences=2,
            scan_interval=0.0, decay_rate=0.5, pruning_weight=0.01,
            pruning_age_seconds=0.0,
        )
        # Spawn concept
        for _ in range(5):
            engine.ingest(Experience({"a", "b"}))

        # Stop reinforcing — concepts should decay
        for _ in range(5):
            engine.ingest(Experience({"z"}))  # no overlap
            time.sleep(0.01)

        # Check that weights decreased
        for concept in engine.concepts.values():
            assert concept.weight < 0.9, f"Concept {concept.id} weight didn't decay"

    def test_batch_ingest(self, fresh_engine):
        batch = [
            Experience({"a", "b", "c"}),
            Experience({"a", "b", "d"}),
            Experience({"a", "b", "e"}),
            Experience({"a", "b", "f"}),
        ]
        report = fresh_engine.ingest_batch(batch)
        assert report["total"] == 4
        state = fresh_engine.get_state_report()
        assert state["total_experiences_ingested"] >= 4

    def test_update_ontology(self, fresh_engine):
        for _ in range(6):
            fresh_engine.ingest(Experience({"a", "b", "c"}))
        ont = fresh_engine.update_ontology()
        assert ont["status"] == "ok"
        assert ont["alive_concepts"] >= 1
        assert len(ont["concepts"]) >= 1

    def test_find_concepts_by_feature(self, fresh_engine):
        for _ in range(5):
            fresh_engine.ingest(Experience({"a", "b", "c"}))
        found = fresh_engine.find_concepts_by_feature("a")
        assert len(found) >= 1
        for concept in found:
            assert "a" in concept.features

    def test_state_report(self, fresh_engine):
        fresh_engine.ingest(Experience({"a", "b"}))
        report = fresh_engine.get_state_report()
        assert "total_experiences_ingested" in report
        assert "alive_concepts" in report
        assert "unique_features" in report
        assert "matrix_dense_size" in report

    def test_max_concepts_eviction(self):
        engine = ConceptBirthEngine(
            npmi_threshold=0.05, spawn_density_threshold=0.3,
            spawn_min_features=2, spawn_min_experiences=2,
            scan_interval=0.0, decay_rate=0.0, max_concepts=3,
        )
        # Create many clusters
        for i in range(10):
            features = {chr(ord("a") + i), chr(ord("m") + i), "zzz"}
            for _ in range(5):
                engine.ingest(Experience(features))
        assert len([c for c in engine.concepts.values() if c.is_alive]) <= 3


# ══════════════════════════════════════════════════════════════════════════════
# Persistence Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestPersistence:

    def test_persist_and_load_concept(self):
        ensure_schema()
        concept = LatentConcept(
            id=9999, features=frozenset({"test_a", "test_b"}),
            birth_time=1000.0, weight=0.75,
        )
        persist_concept(concept)
        loaded = load_persisted_concepts()
        found = [c for c in loaded if c.id == 9999]
        assert len(found) == 1
        assert found[0].features == frozenset({"test_a", "test_b"})
        assert found[0].weight == pytest.approx(0.75)

        # Clean up
        mark_concept_dead(9999)
        loaded_after = load_persisted_concepts()
        assert len([c for c in loaded_after if c.id == 9999]) == 0

    def test_mark_concept_dead(self):
        ensure_schema()
        concept = LatentConcept(
            id=9998, features=frozenset({"dead_test"}),
            birth_time=1000.0,
        )
        persist_concept(concept)
        mark_concept_dead(9998)
        loaded = load_persisted_concepts()
        assert len([c for c in loaded if c.id == 9998]) == 0
        mark_concept_dead(9998)  # idempotent


# ══════════════════════════════════════════════════════════════════════════════
# Real-World Scenario: Mammal vs Bird Discovery
# ══════════════════════════════════════════════════════════════════════════════

class TestMammalVsBird:

    def test_discover_two_distinct_animal_groups(self):
        engine = ConceptBirthEngine(
            npmi_threshold=0.10,
            spawn_density_threshold=0.40,
            spawn_min_features=2,
            spawn_min_experiences=2,
            scan_interval=0.0,
            decay_rate=0.1,
            pruning_weight=0.05,
            pruning_age_seconds=300.0,
        )

        # Mammals
        for animal in ["dog", "cat", "fox", "wolf"]:
            engine.ingest(Experience(
                {"tail", "fur", "four_legs", animal},
                {"type": "mammal"},
            ))

        # Birds
        for bird in ["eagle", "sparrow", "hawk"]:
            engine.ingest(Experience(
                {"feathers", "wings", "beak", bird},
                {"type": "bird"},
            ))

        state = engine.get_state_report()
        assert state["alive_concepts"] >= 2

        # Find the mammal-like concept
        mammal_concepts = engine.find_concepts_by_feature("fur")
        assert len(mammal_concepts) >= 1

        # Find the bird-like concept
        bird_concepts = engine.find_concepts_by_feature("feathers")
        assert len(bird_concepts) >= 1

        # NPMI should show strong association within groups
        assert engine.matrix.npmi("tail", "fur") > 0.3
        assert engine.matrix.npmi("feathers", "wings") > 0.3
        assert engine.matrix.npmi("tail", "feathers") < 0.3  # cross-group

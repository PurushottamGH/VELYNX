"""Tests for program_a/extraction/claim_extraction.py (PA-2).

Covers the deterministic, entity-level candidate-claim extraction surface:
determinism, empty-evidence, entity-level positive, topic-only / nonexistent
negatives (the FM-1/CF-R2 fabrication-pressure guard), supporting-doc-id
subset property, ordering stability under permuted evidence, no-network,
and no-wall-clock/no-env purity.

Contract sources:
  - PROGRAM_A_MODULE_SPEC.md Section 6
  - PROGRAM_A_FINAL_ARCHITECTURE.md Section "PA-2 -- Claim Extraction"
  - PROGRAM_A_API_REFERENCE.md Section 7 (extract_claims)
  - PROGRAM_A_TEST_STRATEGY.md Section "test_claim_extraction.py (PA-2)"
  - PROGRAM_A_CONFIDENCE_MECHANISM.md Section 7.1

All corpora are synthetic and disjoint from the frozen EXP-1 dataset
(dataset-spec Section 12.3). No test observes frozen rows.
"""
from __future__ import annotations

from typing import Any

import pytest

from program_a.extraction import claim_extraction as ce
from program_a.extraction.claim_extraction import extract_claims
from program_a.types import (
    CandidateClaim,
    CandidateClaims,
    EvidenceItem,
    EvidenceSet,
)


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #


def _item(doc_id: str, text: str, origin_domain: str = "example.com") -> EvidenceItem:
    return EvidenceItem(
        doc_id=doc_id,
        origin_domain=origin_domain,
        title=f"title-{doc_id}",
        text=text,
        snapshot_hash_ref="h",
    )


def _evidence(*items: EvidenceItem) -> EvidenceSet:
    return EvidenceSet(items=tuple(items))


def _canonical(claims: CandidateClaims) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return tuple((c.claim_text, c.supporting_doc_ids) for c in claims)


# --------------------------------------------------------------------------- #
# 1. empty evidence
# --------------------------------------------------------------------------- #


def test_empty_evidence_yields_empty_claims() -> None:
    out = extract_claims("What is Aspirin?", _evidence())
    assert isinstance(out, CandidateClaims)
    assert len(out) == 0
    assert out.claims == ()


def test_empty_evidence_with_nonempty_query_yields_empty_claims() -> None:
    out = extract_claims("some query with entities here", _evidence())
    assert out.claims == ()


# --------------------------------------------------------------------------- #
# 2. determinism
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "query, texts",
    [
        ("What is Aspirin?", ("Aspirin reduces pain",)),
        ("Tell me about Penicillin", ("Penicillin is an antibiotic", "Aspirin is unrelated")),
        ("Aspirin and Penicillin", ("Aspirin helps", "Penicillin cures")),
        ("What is Aspirin?", ()),  # empty
    ],
)
def test_determinism_same_inputs_identical_output(query: str, texts: tuple[str, ...]) -> None:
    evidence = _evidence(*[_item(f"d{i}", t) for i, t in enumerate(texts)])
    a = extract_claims(query, evidence)
    b = extract_claims(query, evidence)
    assert a == b
    assert _canonical(a) == _canonical(b)
    # byte-identical canonical serialization
    assert repr(_canonical(a)) == repr(_canonical(b))


def test_determinism_repeated_calls_stable() -> None:
    evidence = _evidence(_item("d1", "Aspirin reduces pain and fever"))
    first = _canonical(extract_claims("Aspirin", evidence))
    for _ in range(5):
        assert _canonical(extract_claims("Aspirin", evidence)) == first


# --------------------------------------------------------------------------- #
# 3. purity / no input mutation
# --------------------------------------------------------------------------- #


def test_pure_no_input_mutation() -> None:
    items = (_item("d1", "Aspirin reduces pain"), _item("d2", "Penicillin cures infection"))
    evidence = _evidence(*items)
    original_items = evidence.items
    original_first_text = evidence.items[0].text
    extract_claims("Aspirin Penicillin", evidence)
    assert evidence.items is original_items
    assert evidence.items[0].text == original_first_text
    # dataclass is frozen; confirm identity unchanged
    assert evidence.items == items


# --------------------------------------------------------------------------- #
# 4. entity-level positive
# --------------------------------------------------------------------------- #


def test_entity_level_positive_single_entity_single_doc() -> None:
    evidence = _evidence(_item("d1", "Aspirin reduces pain and inflammation"))
    out = extract_claims("What is Aspirin?", evidence)
    assert len(out) >= 1
    for c in out:
        assert "d1" in c.supporting_doc_ids


def test_entity_level_positive_multi_supporting_docs() -> None:
    evidence = _evidence(
        _item("d1", "Aspirin is an analgesic"),
        _item("d2", "Aspirin also reduces fever"),
        _item("d3", "Penicillin is unrelated to Aspirin here"),
    )
    out = extract_claims("Aspirin", evidence)
    # the Aspirin claim should be supported by all three docs that mention it
    aspirin_claims = [c for c in out if "aspirin" in c.claim_text.lower() or "Aspirin" in c.claim_text]
    assert len(aspirin_claims) >= 1
    a = aspirin_claims[0]
    assert set(a.supporting_doc_ids) >= {"d1", "d2"}


# --------------------------------------------------------------------------- #
# 5. topic-only evidence -> no claim (FM-1/CF-R2)
# --------------------------------------------------------------------------- #


def test_topic_only_evidence_yields_no_claim() -> None:
    # query about entity "Aspirin"; evidence discusses the related topic
    # "headache relief" but NEVER names the entity "Aspirin".
    evidence = _evidence(
        _item("d1", "Headache relief can be achieved through rest and hydration"),
        _item("d2", "Pain management often involves over-the-counter medications"),
    )
    out = extract_claims("What is Aspirin?", evidence)
    assert out.claims == (), f"expected no claims for topic-only evidence, got {out.claims!r}"


def test_topic_only_evidence_with_partial_word_no_claim() -> None:
    # "Aspirin" must match as a whole word; "aspir" substring must not fire.
    evidence = _evidence(_item("d1", "The aspiner tree grows tall"))
    out = extract_claims("Aspirin", evidence)
    assert out.claims == ()


# --------------------------------------------------------------------------- #
# 6. nonexistent entity -> no claim
# --------------------------------------------------------------------------- #


def test_nonexistent_entity_yields_no_claim() -> None:
    evidence = _evidence(
        _item("d1", "Penicillin is an antibiotic"),
        _item("d2", "Ibuprofen reduces inflammation"),
    )
    out = extract_claims("What is Aspirin?", evidence)
    assert out.claims == ()


# --------------------------------------------------------------------------- #
# 7. supporting_doc_ids subset property
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "query, doc_texts",
    [
        ("Aspirin", ("Aspirin helps",)),
        ("Aspirin Penicillin", ("Aspirin helps", "Penicillin cures", "neither here")),
        ("X", ("no match here",)),
        ("Aspirin Aspirin", ("Aspirin", "Aspirin again")),
    ],
)
def test_supporting_doc_ids_are_subset_of_evidence(query: str, doc_texts: tuple[str, ...]) -> None:
    evidence = _evidence(*[_item(f"d{i}", t) for i, t in enumerate(doc_texts)])
    out = extract_claims(query, evidence)
    valid_ids = {item.doc_id for item in evidence}
    for c in out:
        assert set(c.supporting_doc_ids) <= valid_ids, (
            f"claim {c!r} supporting_doc_ids not subset of evidence doc_ids {valid_ids}"
        )


# --------------------------------------------------------------------------- #
# 8. ordering stability under permuted evidence
# --------------------------------------------------------------------------- #


def test_ordering_stable_under_permuted_evidence() -> None:
    base = (
        _item("d1", "Aspirin reduces pain"),
        _item("d2", "Penicillin cures infection"),
        _item("d3", "Aspirin and Penicillin interact"),
    )
    forward = _evidence(*base)
    reversed_evidence = _evidence(*reversed(base))
    shuffled = _evidence(base[1], base[2], base[0])
    a = extract_claims("Aspirin Penicillin", forward)
    b = extract_claims("Aspirin Penicillin", reversed_evidence)
    c = extract_claims("Aspirin Penicillin", shuffled)
    assert a == b == c
    assert _canonical(a) == _canonical(b) == _canonical(c)


# --------------------------------------------------------------------------- #
# 9. no network
# --------------------------------------------------------------------------- #


def test_no_network(block_socket) -> None:
    evidence = _evidence(_item("d1", "Aspirin reduces pain"))
    out = extract_claims("Aspirin", evidence)  # completes with socket blocked
    assert isinstance(out, CandidateClaims)


# --------------------------------------------------------------------------- #
# 10. no wall-clock / no env
# --------------------------------------------------------------------------- #


def test_no_wall_clock_or_env_imports() -> None:
    import ast
    import inspect

    source = inspect.getsource(ce)
    tree = ast.parse(source)
    forbidden_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                forbidden_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            forbidden_modules.add(node.module or "")
    bad = [m for m in forbidden_modules if m == "time" or m.startswith("time.")
           or m == "datetime" or m.startswith("datetime.")]
    assert bad == [], f"claim_extraction imports wall-clock module(s): {bad}"
    # os.environ reads forbidden too
    assert "os" not in forbidden_modules and not any(m == "os" for m in forbidden_modules), (
        "claim_extraction imports os (env-var determinism leak)"
    )


def test_no_random_import() -> None:
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(ce))
    mods: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            mods.append(node.module or "")
    assert not any(m == "random" or m.startswith("random.") for m in mods), (
        "claim_extraction imports random"
    )


# --------------------------------------------------------------------------- #
# extra: type conformance
# --------------------------------------------------------------------------- #


def test_returns_candidate_claims_type() -> None:
    out = extract_claims("Aspirin", _evidence(_item("d1", "Aspirin helps")))
    assert isinstance(out, CandidateClaims)
    for c in out:
        assert isinstance(c, CandidateClaim)
        assert isinstance(c.claim_text, str)
        assert isinstance(c.supporting_doc_ids, tuple)
        assert all(isinstance(d, str) for d in c.supporting_doc_ids)

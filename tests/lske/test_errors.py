"""Focused tests for the frozen LSKE error taxonomy and its failure payload.

Scope. These tests assert the parts of Specification v1.1.2 §9.6 test row 2 that
are decidable against `v2/lske/errors.py` and `v2/lske/__init__.py` alone: the
`SchemaViolation` failure payload of §9.5.1 (`RF-01`) and the absence of a
package-level `ONTOLOGY_VERSION` required by `RF-04` cl. 2. The remaining row-2
assertions — the ones that drive `validate`, the dataclass constructor predicate
and `append_event` — need `v2.lske.schema` and `v2.lske.events`, which Phase 1
has not yet implemented; they belong to `test_envelope.py` and are not
anticipated here.
"""

import pytest

import v2.lske
from v2.lske.errors import (
    LskeError,
    OntologyError,
    QueryError,
    RelationError,
    SchemaViolation,
    SnapshotIntegrityError,
    TransactionRefused,
)

# --- §9.5 taxonomy: seven classes, unchanged bases ------------------------------


def test_taxonomy_has_exactly_seven_public_classes():
    assert sorted(v2.lske.errors.__all__) == [
        "LskeError",
        "OntologyError",
        "QueryError",
        "RelationError",
        "SchemaViolation",
        "SnapshotIntegrityError",
        "TransactionRefused",
    ]


@pytest.mark.parametrize(
    ("cls", "second_base"),
    [
        (SchemaViolation, ValueError),
        (TransactionRefused, RuntimeError),
        (SnapshotIntegrityError, RuntimeError),
        (QueryError, ValueError),
        (OntologyError, ValueError),
        (RelationError, ValueError),
    ],
)
def test_every_class_roots_at_lske_error_and_keeps_its_second_base(cls, second_base):
    assert cls.__bases__ == (LskeError, second_base)


# --- §9.5.1 cl. 1: attribute name and the args contract ------------------------


def test_args_is_exactly_the_message_and_carries_no_failure_information():
    exc = SchemaViolation("/id: pattern", [("/id", "s#/pattern", "pattern", False)])
    assert exc.args == ("/id: pattern",)
    assert str(exc) == "/id: pattern"


def test_failures_is_the_only_public_failure_name():
    exc = SchemaViolation("m", [("/a", "s", "type", False)])
    assert set(vars(exc)) == {"failures"}
    for rejected in ("errors", "details", "violations", "failure_list", "to_dict", "as_json"):
        assert not hasattr(exc, rejected)


# --- §9.5.1 cl. 2: type ---------------------------------------------------------


def test_payload_is_a_tuple_of_four_element_primitive_tuples():
    exc = SchemaViolation("m", [("/a", "s", "type", False), ("/b", "s", "required", False)])
    assert isinstance(exc.failures, tuple)
    for item in exc.failures:
        assert type(item) is tuple
        assert len(item) == 4
        assert [type(element) for element in item] == [str, str, str, bool]


def test_empty_payload_is_representable_and_is_the_default():
    assert SchemaViolation("m").failures == ()


def test_payload_is_never_none_and_accepts_any_iterable():
    generated = SchemaViolation("m", (item for item in [("/a", "s", "type", False)]))
    assert generated.failures == (("/a", "s", "type", False),)


def test_payload_is_hashable_and_comparable():
    first = SchemaViolation("m", [("/a", "s", "type", False)])
    second = SchemaViolation("other message", [("/a", "s", "type", False)])
    assert hash(first.failures) == hash(second.failures)
    assert first.failures == second.failures


# --- §9.5.1 cl. 5: normalization on construction --------------------------------


def test_duplicate_items_are_removed():
    item = ("/a", "s", "type", False)
    assert SchemaViolation("m", [item, item, item]).failures == (item,)


def test_ordering_is_by_derived_then_instance_then_schema_then_keyword():
    exc = SchemaViolation(
        "m",
        [
            ("/b", "s1", "type", False),
            ("/a", "s2", "type", False),
            ("/a", "s1", "type", False),
            ("/a", "s1", "maxLength", False),
        ],
    )
    assert exc.failures == (
        ("/a", "s1", "maxLength", False),
        ("/a", "s1", "type", False),
        ("/a", "s2", "type", False),
        ("/b", "s1", "type", False),
    )


def test_derived_findings_sort_after_every_primary_finding():
    exc = SchemaViolation(
        "m",
        [
            ("", "", "unevaluatedProperties", True),
            ("/z", "s", "type", False),
        ],
    )
    assert [item[3] for item in exc.failures] == [False, True]
    assert exc.failures[-1] == ("", "", "unevaluatedProperties", True)


def test_two_failures_at_one_instance_pointer_have_a_defined_order():
    exc = SchemaViolation(
        "m",
        [
            ("/at", "s#/format", "format", False),
            ("/at", "s#/type", "type", False),
        ],
    )
    assert exc.failures == (
        ("/at", "s#/format", "format", False),
        ("/at", "s#/type", "type", False),
    )


def test_order_is_a_function_of_the_failure_set_alone():
    items = [
        ("/b", "s2", "required", False),
        ("", "", "unevaluatedProperties", True),
        ("/a", "s1", "type", False),
    ]
    assert (
        SchemaViolation("m", items).failures == SchemaViolation("m", list(reversed(items))).failures
    )


def test_construction_does_not_compute_derived_or_rewrite_items():
    # `unevaluatedProperties` with a primary failure below it would be derived
    # under RF-02, but computing that is the raiser's obligation, not the
    # exception's: the marker supplied is the marker kept (§9.5.1 cl. 5).
    exc = SchemaViolation(
        "m",
        [
            ("", "", "unevaluatedProperties", False),
            ("/a", "s", "type", False),
        ],
    )
    assert ("", "", "unevaluatedProperties", False) in exc.failures
    assert all(item[3] is False for item in exc.failures)


def test_a_genuine_closure_failure_stays_in_the_primary_block():
    exc = SchemaViolation("m", [("", "", "unevaluatedProperties", False)])
    assert exc.failures == (("", "", "unevaluatedProperties", False),)


# --- RF-04 cl. 2: no package-level ONTOLOGY_VERSION -----------------------------


def test_package_exposes_no_ontology_version():
    assert not hasattr(v2.lske, "ONTOLOGY_VERSION")
    assert "ONTOLOGY_VERSION" not in v2.lske.__all__


def test_package_keeps_its_own_version_constant():
    assert v2.lske.__version__ == "1.1.0"
    assert v2.lske.__all__ == ["__version__"]

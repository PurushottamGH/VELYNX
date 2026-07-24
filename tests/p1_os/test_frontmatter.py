"""Tests for strict frontmatter parsing, heading validation, and
deterministic serialization (spec sections 16, 17, 18)."""

from __future__ import annotations

import pytest

from p1_os.frontmatter import (
    DelimiterError,
    EncodingError,
    FrontmatterError,
    HeadingError,
    LineEndingError,
    MergeConflictMarkerError,
    YamlSafetyError,
    parse_document,
    serialize_document,
    serialize_metadata,
    validate_headings,
)
from p1_os.schemas import Claim, Experiment
from helpers import QUESTION_BODY, QUESTION_METADATA, make_raw
from payloads import valid_payload


# --- Delimiters ----------------------------------------------------------


def test_valid_document_parses():
    doc = parse_document(make_raw())
    assert doc.record.id == "P1-Q000001"
    assert doc.line_ending == "LF"
    assert doc.final_newline is True


def test_missing_opening_delimiter_fails():
    raw = (QUESTION_METADATA + "---\n" + QUESTION_BODY).encode("utf-8")
    with pytest.raises(DelimiterError):
        parse_document(raw)


def test_opening_delimiter_with_trailing_content_fails():
    raw = ("--- \n" + QUESTION_METADATA + "---\n" + QUESTION_BODY).encode("utf-8")
    with pytest.raises(DelimiterError):
        parse_document(raw)


def test_unterminated_frontmatter_fails():
    raw = ("---\n" + QUESTION_METADATA).encode("utf-8")
    with pytest.raises(DelimiterError):
        parse_document(raw)


def test_closing_delimiter_with_trailing_content_is_not_recognized_as_closing():
    metadata = QUESTION_METADATA + "extra_line: value\n"
    raw = ("---\n" + metadata + "--- \n" + QUESTION_BODY).encode("utf-8")
    with pytest.raises(DelimiterError):
        parse_document(raw)


# --- YAML safety -----------------------------------------------------------


def test_empty_yaml_fails():
    raw = ("---\n" + "---\n" + QUESTION_BODY).encode("utf-8")
    with pytest.raises(YamlSafetyError):
        parse_document(raw)


def test_non_mapping_yaml_fails():
    raw = ("---\n" + "- just\n- a\n- list\n" + "---\n" + QUESTION_BODY).encode("utf-8")
    with pytest.raises(YamlSafetyError):
        parse_document(raw)


def test_malformed_yaml_fails():
    raw = ("---\n" + "id: [unclosed\n" + "---\n" + QUESTION_BODY).encode("utf-8")
    with pytest.raises(YamlSafetyError):
        parse_document(raw)


def test_duplicate_top_level_key_fails():
    raw = make_raw(metadata_yaml=QUESTION_METADATA + "title: duplicate\n")
    with pytest.raises(YamlSafetyError):
        parse_document(raw)


def test_duplicate_nested_key_fails():
    metadata = QUESTION_METADATA + "extra:\n  a: 1\n  a: 2\n"
    raw = make_raw(metadata_yaml=metadata)
    with pytest.raises(YamlSafetyError):
        parse_document(raw)


def test_unsafe_python_tag_fails():
    metadata = QUESTION_METADATA + "danger: !!python/object:builtins.object {}\n"
    raw = make_raw(metadata_yaml=metadata)
    with pytest.raises(YamlSafetyError):
        parse_document(raw)


def test_alias_fails():
    metadata = "anchor_val: &a value\nother: *a\n" + QUESTION_METADATA
    raw = make_raw(metadata_yaml=metadata)
    with pytest.raises(YamlSafetyError):
        parse_document(raw)


def test_anchor_without_alias_still_fails():
    metadata = QUESTION_METADATA + "anchored: &a value\n"
    raw = make_raw(metadata_yaml=metadata)
    with pytest.raises(YamlSafetyError):
        parse_document(raw)


def test_merge_key_fails():
    metadata = QUESTION_METADATA + "<<: {extra: 1}\n"
    raw = make_raw(metadata_yaml=metadata)
    with pytest.raises(YamlSafetyError):
        parse_document(raw)


def test_object_type_missing_fails():
    metadata = QUESTION_METADATA.replace("object_type: question\n", "")
    raw = make_raw(metadata_yaml=metadata)
    with pytest.raises(YamlSafetyError):
        parse_document(raw)


def test_object_type_unknown_value_fails():
    metadata = QUESTION_METADATA.replace("object_type: question", "object_type: banana")
    raw = make_raw(metadata_yaml=metadata)
    with pytest.raises((YamlSafetyError, ValueError)):
        parse_document(raw)


# --- Encoding ---------------------------------------------------------------


def test_utf8_bom_fails():
    raw = b"\xef\xbb\xbf" + make_raw()
    with pytest.raises(EncodingError):
        parse_document(raw)


def test_invalid_utf8_bytes_fail():
    raw = b"---\n\xff\xfe garbage\n---\n" + QUESTION_BODY.encode("utf-8")
    with pytest.raises(EncodingError):
        parse_document(raw)


def test_unicode_content_is_preserved():
    metadata = QUESTION_METADATA.replace(
        'title: Example title', 'title: "Étude de cas — café ☃"'
    )
    body = "## Research Question\n日本語テキスト\n\n## Rationale\nText.\n\n## Scope\nText.\n\n## Selection Criteria\nText.\n"
    raw = make_raw(metadata_yaml=metadata, body=body)
    doc = parse_document(raw)
    assert "Étude" in doc.record.title
    assert "日本語" in doc.body
    serialized = serialize_document(doc)
    assert "Étude" in serialized
    assert "\\u" not in serialized  # emitted directly, not escaped


# --- Line endings ------------------------------------------------------------


def test_consistent_lf_accepted():
    doc = parse_document(make_raw(newline="\n"))
    assert doc.line_ending == "LF"


def test_consistent_crlf_accepted():
    doc = parse_document(make_raw(newline="\r\n"))
    assert doc.line_ending == "CRLF"
    assert doc.final_newline is True


def test_mixed_line_endings_rejected():
    text = f"---\n{QUESTION_METADATA}---\n{QUESTION_BODY}"
    mixed = text.replace("\n", "\r\n", 3)  # only the first few lines become CRLF
    with pytest.raises(LineEndingError):
        parse_document(mixed.encode("utf-8"))


def test_lone_cr_rejected():
    text = f"---\n{QUESTION_METADATA}---\n{QUESTION_BODY}"
    lone_cr = text.replace("\n", "\r")
    with pytest.raises(LineEndingError):
        parse_document(lone_cr.encode("utf-8"))


def test_final_newline_state_detected_when_absent():
    text = f"---\n{QUESTION_METADATA}---\n{QUESTION_BODY}".rstrip("\n")
    doc = parse_document(text.encode("utf-8"))
    assert doc.final_newline is False


# --- Merge-conflict markers --------------------------------------------------


@pytest.mark.parametrize("marker", ["<<<<<<< HEAD", "=======", ">>>>>>> branch"])
def test_merge_conflict_marker_in_body_fails(marker):
    body = QUESTION_BODY + marker + "\n"
    raw = make_raw(body=body)
    with pytest.raises(MergeConflictMarkerError):
        parse_document(raw)


def test_merge_conflict_marker_in_metadata_fails():
    metadata = QUESTION_METADATA + "<<<<<<< HEAD\n"
    raw = make_raw(metadata_yaml=metadata)
    with pytest.raises(MergeConflictMarkerError):
        parse_document(raw)


# --- Exact body preservation --------------------------------------------------


def test_body_preserves_blank_lines_trailing_spaces_and_indentation():
    body = "## Research Question\nLine with trailing spaces.   \n\n\n  indented text\n\n## Rationale\nx\n\n## Scope\nx\n\n## Selection Criteria\nx\n"
    raw = make_raw(body=body)
    doc = parse_document(raw)
    assert doc.body == body


def test_body_preserves_code_fences_and_wrapping():
    body = (
        "## Research Question\n"
        "```python\n"
        "def f():\n"
        "    return 1  # not a heading: ## fake\n"
        "```\n\n"
        "## Rationale\n"
        "A very long line that wraps in some editors but must be preserved exactly as-is without modification.\n\n"
        "## Scope\nx\n\n## Selection Criteria\nx\n"
    )
    raw = make_raw(body=body)
    doc = parse_document(raw)
    assert doc.body == body


# --- Required heading validation ---------------------------------------------


def test_missing_required_heading_fails():
    body = "## Research Question\nx\n\n## Rationale\nx\n\n## Scope\nx\n"  # missing Selection Criteria
    raw = make_raw(body=body)
    with pytest.raises(HeadingError):
        parse_document(raw)


def test_duplicate_required_heading_fails():
    body = QUESTION_BODY + "## Research Question\nagain\n"
    raw = make_raw(body=body)
    with pytest.raises(HeadingError):
        parse_document(raw)


def test_out_of_order_required_headings_fail():
    body = "## Rationale\nx\n\n## Research Question\nx\n\n## Scope\nx\n\n## Selection Criteria\nx\n"
    raw = make_raw(body=body)
    with pytest.raises(HeadingError):
        parse_document(raw)


def test_additional_headings_are_allowed():
    body = (
        "## Preamble\nExtra heading, allowed.\n\n"
        + QUESTION_BODY
        + "## Appendix\nAlso allowed.\n"
    )
    raw = make_raw(body=body)
    doc = parse_document(raw)
    assert doc.record.id == "P1-Q000001"


def test_heading_without_space_after_hashes_does_not_count():
    body = "##Research Question\nx\n\n## Research Question\nx\n\n## Rationale\nx\n\n## Scope\nx\n\n## Selection Criteria\nx\n"
    raw = make_raw(body=body)
    doc = parse_document(raw)  # the real "## Research Question" still present once
    assert doc.record.id == "P1-Q000001"


def test_wrong_heading_level_does_not_count():
    # The level-3 line must not be treated as satisfying "## Research
    # Question"; since the real level-2 heading still appears exactly once
    # (in QUESTION_BODY) in the correct position, the document is valid.
    body = "### Research Question\nwrong level\n\n" + QUESTION_BODY
    raw = make_raw(body=body)
    doc = parse_document(raw)
    assert doc.record.id == "P1-Q000001"


def test_heading_that_only_appears_at_wrong_level_fails():
    body = "### Research Question\nx\n\n## Rationale\nx\n\n## Scope\nx\n\n## Selection Criteria\nx\n"
    raw = make_raw(body=body)
    with pytest.raises(HeadingError):
        parse_document(raw)


def test_indented_heading_does_not_count():
    body = "  ## Research Question\nindented, ignored\n\n" + QUESTION_BODY
    raw = make_raw(body=body)
    doc = parse_document(raw)
    assert doc.record.id == "P1-Q000001"


def test_heading_inside_backtick_fence_does_not_count():
    body = (
        "```\n## Research Question\n```\n\n"
        + QUESTION_BODY
    )
    raw = make_raw(body=body)
    doc = parse_document(raw)
    assert doc.record.id == "P1-Q000001"


def test_heading_inside_tilde_fence_does_not_count():
    body = "~~~\n## Rationale\n~~~\n\n" + QUESTION_BODY
    raw = make_raw(body=body)
    doc = parse_document(raw)
    assert doc.record.id == "P1-Q000001"


def test_unterminated_fence_fails():
    body = QUESTION_BODY + "```\nunterminated\n"
    raw = make_raw(body=body)
    with pytest.raises(HeadingError):
        parse_document(raw)


def test_validate_headings_standalone():
    validate_headings(QUESTION_BODY, ("## Research Question", "## Rationale", "## Scope", "## Selection Criteria"))
    with pytest.raises(HeadingError):
        validate_headings("no headings here", ("## Research Question",))


# --- Deterministic serialization ---------------------------------------------


def test_serialization_is_deterministic_across_repeated_calls():
    doc = parse_document(make_raw())
    first = serialize_document(doc)
    second = serialize_document(doc)
    assert first == second


def test_serialization_round_trip_is_idempotent():
    doc = parse_document(make_raw())
    once = serialize_document(doc)
    doc2 = parse_document(once.encode("utf-8"))
    twice = serialize_document(doc2)
    assert once == twice


def test_serialized_metadata_field_order_matches_common_then_declared():
    doc = parse_document(make_raw())
    text = serialize_metadata(doc.record)
    lines = [line for line in text.split("\n") if line and not line.startswith(" ")]
    keys = [line.split(":", 1)[0] for line in lines]
    expected_prefix = [
        "id", "title", "object_type", "status", "schema_version",
        "created", "last_reviewed", "created_by", "provenance",
    ]
    assert keys[: len(expected_prefix)] == expected_prefix
    assert keys[len(expected_prefix):] == ["selected", "scope"]


def test_serialization_quotes_schema_version():
    doc = parse_document(make_raw())
    text = serialize_metadata(doc.record)
    assert 'schema_version: "1.0"' in text


def test_serialization_quotes_datetimes():
    doc = parse_document(make_raw())
    text = serialize_metadata(doc.record)
    assert 'created: "2026-01-01T00:00:00Z"' in text


def test_serialization_emits_null_for_none():
    doc = parse_document(make_raw())
    text = serialize_metadata(doc.record)
    assert "last_reviewed: null" in text


def test_serialization_emits_empty_list_and_mapping_compactly():
    metadata = QUESTION_METADATA  # provenance: [] already present
    doc = parse_document(make_raw(metadata_yaml=metadata))
    text = serialize_metadata(doc.record)
    assert "provenance: []" in text


def test_serialization_uses_lf_only():
    doc = parse_document(make_raw(newline="\r\n"))
    text = serialize_document(doc)
    assert "\r\n" not in text.split("---\n", 2)[1]  # metadata block has no CRLF


def test_serializer_does_not_mutate_source_model():
    doc = parse_document(make_raw())
    before = doc.record.model_dump()
    serialize_document(doc)
    after = doc.record.model_dump()
    assert before == after


def test_serializer_returns_str_not_none():
    doc = parse_document(make_raw())
    result = serialize_document(doc)
    assert isinstance(result, str)


# --- Milestone 1.1: canonical YAML sequence indentation ---------------------


def test_serialization_indents_top_level_sequence_items():
    record = Claim.model_validate(valid_payload("claim"))
    text = serialize_metadata(record)
    assert "question_ids:\n  - P1-Q000001\n" in text
    assert "unknown_ids:\n  - P1-U000001\n" in text


def test_serialization_indents_sequence_items_nested_under_a_sequence_of_mappings():
    record = Experiment.model_validate(valid_payload("experiment"))
    text = serialize_metadata(record)
    assert (
        "prospective_update_rules:\n"
        "  - rule_id: supports_primary\n"
        "    outcome_class: supports_primary\n"
        "    decision_required: true\n"
        "    proposed_actions:\n"
        "      - Human review required\n"
    ) in text


def test_serialization_never_emits_flush_left_sequence_items():
    record = Experiment.model_validate(valid_payload("experiment"))
    text = serialize_metadata(record)
    assert "\n- " not in text


# --- Milestone 1.1: canonical UTC datetime serialization --------------------


def test_utc_datetime_serializes_with_trailing_z_not_offset():
    doc = parse_document(make_raw())
    text = serialize_metadata(doc.record)
    assert 'created: "2026-01-01T00:00:00Z"' in text
    assert "+00:00" not in text


def test_positive_offset_datetime_preserves_explicit_offset():
    metadata = QUESTION_METADATA.replace(
        'created: "2026-01-01T00:00:00Z"', 'created: "2026-01-01T00:00:00+05:30"'
    )
    doc = parse_document(make_raw(metadata_yaml=metadata))
    text = serialize_metadata(doc.record)
    assert 'created: "2026-01-01T00:00:00+05:30"' in text


def test_negative_offset_datetime_preserves_explicit_offset():
    metadata = QUESTION_METADATA.replace(
        'created: "2026-01-01T00:00:00Z"', 'created: "2026-01-01T00:00:00-07:00"'
    )
    doc = parse_document(make_raw(metadata_yaml=metadata))
    text = serialize_metadata(doc.record)
    assert 'created: "2026-01-01T00:00:00-07:00"' in text


def test_utc_datetime_preserves_fractional_seconds():
    metadata = QUESTION_METADATA.replace(
        'created: "2026-01-01T00:00:00Z"', 'created: "2026-01-01T00:00:00.123456Z"'
    )
    doc = parse_document(make_raw(metadata_yaml=metadata))
    text = serialize_metadata(doc.record)
    assert 'created: "2026-01-01T00:00:00.123456Z"' in text


def test_non_utc_datetime_preserves_fractional_seconds():
    metadata = QUESTION_METADATA.replace(
        'created: "2026-01-01T00:00:00Z"',
        'created: "2026-01-01T00:00:00.500000+05:30"',
    )
    doc = parse_document(make_raw(metadata_yaml=metadata))
    text = serialize_metadata(doc.record)
    assert 'created: "2026-01-01T00:00:00.500000+05:30"' in text

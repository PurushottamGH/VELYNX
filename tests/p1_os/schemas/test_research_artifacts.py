from __future__ import annotations

import pytest
from pydantic import ValidationError

from p1_os.schemas import ResearchArtifact
from payloads import valid_payload


def test_valid_research_artifact():
    record = ResearchArtifact.model_validate(valid_payload("research_artifact"))
    assert record.artifact_kind == "deep_research_report"
    assert record.content_hash is None
    assert record.external_locator is None


def test_missing_required_field_fails():
    payload = valid_payload("research_artifact")
    del payload["media_type"]
    with pytest.raises(ValidationError):
        ResearchArtifact.model_validate(payload)


def test_unknown_field_fails():
    payload = valid_payload("research_artifact")
    payload["extra"] = 1
    with pytest.raises(ValidationError):
        ResearchArtifact.model_validate(payload)


def test_content_hash_may_be_a_string():
    payload = valid_payload("research_artifact")
    payload["content_hash"] = "abc123"
    record = ResearchArtifact.model_validate(payload)
    assert record.content_hash == "abc123"


def test_wrong_object_type_literal_fails():
    payload = valid_payload("research_artifact")
    payload["object_type"] = "question"
    with pytest.raises(ValidationError):
        ResearchArtifact.model_validate(payload)


def test_required_headings_constant():
    assert ResearchArtifact.REQUIRED_HEADINGS == (
        "## Description",
        "## Provenance",
        "## Integrity",
    )

"""Poison-pill test for the VELYNX validation control plane.

Self-contained: mocks a perfect background payload and a flawed foreground
payload, then asserts the validator catches the signature mismatch.
"""

from __future__ import annotations

import sys
from typing import Any

# ------------------------------------------------------------------ helpers --

def _make_valid_bg_payload() -> dict[str, Any]:
    """Background payload targeting an allowed directory (tests/)."""
    return {
        "files": [
            {
                "path": "tests/test_predictive_core.py",
                "content": "# valid background content\n",
            }
        ]
    }


def _make_flawed_fg_payload() -> dict[str, Any]:
    """Foreground payload where ``predict_next_state`` is missing the
    ``active_sources`` argument."""
    return {
        "exports": {
            "PredictiveEngine": {
                "type": "class",
                "methods": {
                    "__init__": {
                        "args": ["self", "decay_rate", "confidence_threshold"],
                        "returns": "None",
                    },
                    "predict_next_state": {
                        "args": ["self", "concept_states", "transition_rules"],
                        "returns": "dict",
                    },
                },
            },
            "calculate_prediction_error": {
                "type": "function",
                "args": ["target_state", "predicted_state"],
                "returns": "float",
            },
        }
    }


# ----------------------------------------------------------------- tests ---

def test_poison_pill() -> None:
    from backend.orchestration.validator import (
        ContractValidator,
        ReconciliationError,
    )

    validator = ContractValidator()
    bg = _make_valid_bg_payload()
    fg = _make_flawed_fg_payload()

    try:
        validator.validate(fg_payload=fg, bg_payload=bg)
    except ReconciliationError as exc:
        print("=== ReconciliationError caught ===")
        print(f"Message: {exc.message}")
        print(f"Report:")
        print_exc_report(exc.report)

        # ---- assertions ----
        report = exc.report
        assert report["passed"] is False, "Expected report.passed to be False"

        sig_errors = [
            e
            for e in report["errors"]
            if e["type"] == "SIGNATURE_MISMATCH"
            and "predict_next_state" in e["detail"]
        ]
        assert len(sig_errors) > 0, "Expected at least one SIGNATURE_MISMATCH for predict_next_state"

        first = sig_errors[0]
        assert "active_sources" in first["detail"], (
            "Error detail should mention missing 'active_sources'"
        )
        assert "active_sources" in first["context"].get("missing", []), (
            "Error context.missing should contain 'active_sources'"
        )

        print("\nAll assertions passed.")
        return

    assert False, "Expected ReconciliationError but no exception was raised."


def test_perfect_payload() -> None:
    """Regression test: a spec-conforming payload should pass validation."""
    from backend.orchestration.validator import ContractValidator

    perfect_fg: dict[str, Any] = {
        "exports": {
            "PredictiveEngine": {
                "type": "class",
                "methods": {
                    "__init__": {
                        "args": ["self", "decay_rate", "confidence_threshold"],
                        "returns": "None",
                    },
                    "predict_next_state": {
                        "args": [
                            "self",
                            "concept_states",
                            "transition_rules",
                            "active_sources",
                        ],
                        "returns": "dict",
                    },
                },
            },
            "calculate_prediction_error": {
                "type": "function",
                "args": ["target_state", "predicted_state"],
                "returns": "float",
            },
        }
    }

    validator = ContractValidator()
    report = validator.validate(
        fg_payload=perfect_fg,
        bg_payload=_make_valid_bg_payload(),
    )
    assert report.passed, f"Expected validation to pass, got: {report.errors}"
    print("Perfect payload test passed.")


def test_repository_boundary_violation() -> None:
    """A background payload writing into forbidden directories must fail."""
    from backend.orchestration.validator import (
        ContractValidator,
        ReconciliationError,
    )

    bad_bg = {
        "files": [{"path": "backend/cognition/predictive_core.py", "content": "# naughty"}]
    }

    validator = ContractValidator()
    try:
        validator.validate(fg_payload=_make_perfect_fg(), bg_payload=bad_bg)
    except ReconciliationError as exc:
        violations = [
            e for e in exc.report["errors"] if e["type"] == "REPOSITORY_BOUNDARY_VIOLATION"
        ]
        assert len(violations) == 1
        print("Repository boundary test passed.")
        return

    assert False, "Expected ReconciliationError for boundary violation."


def _make_perfect_fg() -> dict[str, Any]:
    return {
        "exports": {
            "PredictiveEngine": {
                "type": "class",
                "methods": {
                    "__init__": {
                        "args": ["self", "decay_rate", "confidence_threshold"],
                        "returns": "None",
                    },
                    "predict_next_state": {
                        "args": ["self", "concept_states", "transition_rules", "active_sources"],
                        "returns": "dict",
                    },
                },
            },
            "calculate_prediction_error": {
                "type": "function",
                "args": ["target_state", "predicted_state"],
                "returns": "float",
            },
        }
    }


def print_exc_report(report: dict[str, Any]) -> None:
    for i, err in enumerate(report["errors"], 1):
        print(f"  [{i}] {err['type']}: {err['detail']}")


# ------------------------------------------------------------------- main --

if __name__ == "__main__":
    test_poison_pill()
    test_perfect_payload()
    test_repository_boundary_violation()
    print("\nAll poison-pill tests passed.")

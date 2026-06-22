"""Validation engine that intercepts JSON payloads from LLMs and validates them
against the hard-coded PREDICTIVE_CORE_SPEC before allowing file merges.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.contracts.predictive_core_spec import PREDICTIVE_CORE_SPEC


class ReconciliationError(Exception):
    """Raised when foreground payload deviates from the ground-truth spec."""

    def __init__(self, message: str, report: dict[str, Any]) -> None:
        super().__init__(message)
        self.message: str = message
        self.report: dict[str, Any] = report


@dataclass
class ValidationReport:
    """Accumulates validation findings during a reconciliation run."""

    errors: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def add_error(
        self,
        error_type: str,
        detail: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        self.errors.append({
            "type": error_type,
            "detail": detail,
            "context": context or {},
        })

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
        }


class ContractValidator:
    """Deterministic control plane.

    Intercepts JSON payloads from Foreground and Background LLMs and ensures
    they conform to the PREDICTIVE_CORE_SPEC before any file merges are allowed.
    """

    FORBIDDEN_PREFIXES: tuple[str, ...] = ("backend/cognition/", "backend/core/")

    def __init__(self) -> None:
        self._spec: dict[str, Any] = PREDICTIVE_CORE_SPEC

    def validate(
        self, fg_payload: dict[str, Any], bg_payload: dict[str, Any]
    ) -> ValidationReport:
        """Run the full validation pipeline against both payloads.

        Raises ReconciliationError if any violations are found.
        """
        report = ValidationReport()
        self._validate_foreground(fg_payload, report)
        self.validate_repository_boundaries(bg_payload, report)

        if not report.passed:
            raise ReconciliationError(
                "Contract validation failed — see report for details.",
                report.to_dict(),
            )
        return report

    def validate_repository_boundaries(
        self, bg_payload: dict[str, Any], report: ValidationReport
    ) -> None:
        """Ensure the background payload does not attempt to write into
        forbidden directories (``backend/cognition/`` or ``backend/core/``).
        """
        files: list[dict[str, Any]] = bg_payload.get("files", [])
        for file_entry in files:
            path: str = file_entry.get("path", "")
            for forbidden in self.FORBIDDEN_PREFIXES:
                if path.startswith(forbidden):
                    report.add_error(
                        "REPOSITORY_BOUNDARY_VIOLATION",
                        f"Background payload attempted to write to forbidden "
                        f"path '{path}'.",
                        {"path": path, "forbidden_prefix": forbidden},
                    )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_foreground(
        self, fg_payload: dict[str, Any], report: ValidationReport
    ) -> None:
        """Deep-compare fg_payload exports against the spec."""
        exports_spec: dict[str, Any] = self._spec["exports"]
        fg_exports: dict[str, Any] = fg_payload.get("exports", {})

        for export_name, spec_def in exports_spec.items():
            fg_def = fg_exports.get(export_name)
            if fg_def is None:
                report.add_error(
                    "MISSING_EXPORT",
                    f"Spec requires export '{export_name}' but it was not "
                    f"found in foreground payload.",
                    {"export": export_name},
                )
                continue

            if spec_def["type"] != fg_def.get("type"):
                report.add_error(
                    "TYPE_MISMATCH",
                    f"Export '{export_name}' has type '{fg_def.get('type')}' "
                    f"but spec expects '{spec_def['type']}'.",
                    {"export": export_name},
                )

            self._validate_export_signatures(export_name, spec_def, fg_def, report)

    def _validate_export_signatures(
        self,
        export_name: str,
        spec_def: dict[str, Any],
        fg_def: dict[str, Any],
        report: ValidationReport,
    ) -> None:
        if spec_def["type"] == "function":
            self._check_signature(export_name, export_name, spec_def, fg_def, report)
            return

        spec_methods: dict[str, Any] = spec_def.get("methods", {})
        fg_methods: dict[str, Any] = fg_def.get("methods", {})

        for method_name, method_spec in spec_methods.items():
            fg_method = fg_methods.get(method_name)
            if fg_method is None:
                report.add_error(
                    "MISSING_METHOD",
                    f"Method '{method_name}' required on '{export_name}' "
                    f"but not found.",
                    {"export": export_name, "method": method_name},
                )
                continue
            self._check_signature(
                export_name, method_name, method_spec, fg_method, report
            )

    def _check_signature(
        self,
        export_name: str,
        member_name: str,
        spec_def: dict[str, Any],
        fg_def: dict[str, Any],
        report: ValidationReport,
    ) -> None:
        spec_args: list[str] = spec_def.get("args", [])
        fg_args: list[str] = fg_def.get("args", [])
        spec_returns: str | None = spec_def.get("returns")
        fg_returns: str | None = fg_def.get("returns")

        missing_args = [a for a in spec_args if a not in fg_args]
        extra_args = [a for a in fg_args if a not in spec_args]

        if missing_args or extra_args:
            report.add_error(
                "SIGNATURE_MISMATCH",
                f"'{export_name}.{member_name}' argument mismatch. "
                f"Missing: {missing_args}, Unexpected: {extra_args}.",
                {
                    "export": export_name,
                    "member": member_name,
                    "expected_args": spec_args,
                    "received_args": fg_args,
                    "missing": missing_args,
                    "extra": extra_args,
                },
            )

        if spec_returns is not None and fg_returns is not None and spec_returns != fg_returns:
            report.add_error(
                "SIGNATURE_MISMATCH",
                f"'{export_name}.{member_name}' return type mismatch. "
                f"Expected '{spec_returns}', got '{fg_returns}'.",
                {
                    "export": export_name,
                    "member": member_name,
                    "expected_returns": spec_returns,
                    "received_returns": fg_returns,
                },
            )

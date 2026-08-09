"""P1 Research Operating System — registration state.

Reads ``GOVERNANCE_REGISTRY.yaml`` and reports whether the governing normative
artifacts are registered, because Article L-11 makes that the precondition of
all scientific admissibility.

At the time of writing, the registry reports ``active_domain_standards: []``,
``constitutional_steward: []`` and null attestations, so this module's honest
answer is that nothing is registered and every run is engineering-only. That is
not a defect in this module; it is the measured state of the repository, and it
is the single highest-leverage item on the ROS roadmap because it costs no
engineering days and gates every claim P1 will ever make.

Read-only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .admissibility import Registration

DEFAULT_REGISTRY_PATH = Path("GOVERNANCE_REGISTRY.yaml")

#: Normative artifacts whose registration Article L-11 requires before any run
#: they govern can bear evidence. Paths are repository-relative.
GOVERNING_ARTIFACTS: tuple[str, ...] = (
    "P1_V2_CONSTITUTION_LOCK_v1.0.md",
    "P1_V2_SCIENTIFIC_CONSTITUTION.md",
    "P1_OBSERVATORY_SCIENTIFIC_SPECIFICATION.md",
    "SCIENTIFIC_OPERATING_SYSTEM.md",
)


@dataclass(frozen=True)
class RegistryState:
    """Parsed registry state, with the raw document retained for reporting."""

    path: Path
    raw: dict[str, Any]

    @property
    def active_domain_standards(self) -> list[Any]:
        return list(self.raw.get("active_domain_standards") or [])

    @property
    def stewards(self) -> list[Any]:
        assignments = self.raw.get("authority_assignments") or {}
        if not isinstance(assignments, dict):
            return []
        return list(assignments.get("constitutional_steward") or [])

    @property
    def requirements(self) -> dict[str, Any]:
        value = self.raw.get("activation_requirements") or {}
        return value if isinstance(value, dict) else {}

    def registered_paths(self) -> set[str]:
        """Paths of every artifact the registry names as an active standard."""
        found: set[str] = set()
        constitution = self.raw.get("constitution")
        if isinstance(constitution, dict) and constitution.get("path"):
            found.add(str(constitution["path"]))
        for entry in self.active_domain_standards:
            if isinstance(entry, dict) and entry.get("path"):
                found.add(str(entry["path"]))
        return found

    def unregistered_governing_artifacts(self) -> list[str]:
        registered = self.registered_paths()
        return [path for path in GOVERNING_ARTIFACTS if path not in registered]

    def to_registration(self) -> Registration:
        """Project registry state onto the admissibility kernel's input."""
        requirements = self.requirements
        return Registration(
            lock_registered=not self.unregistered_governing_artifacts(),
            steward_assigned=bool(self.stewards),
            adopter_attested=requirements.get("adopter_attestation") is not None,
            independent_reviewer_attested=(
                requirements.get("independent_reviewer_attestation") is not None
            ),
        )

    @classmethod
    def load(cls, path: Path | str = DEFAULT_REGISTRY_PATH) -> "RegistryState":
        path = Path(path)
        with path.open(encoding="utf-8") as handle:
            raw = yaml.safe_load(handle)
        if not isinstance(raw, dict):
            raise ValueError(f"{path}: registry root must be a mapping")
        return cls(path=path, raw=raw)


def load_registration(root: Path | str = ".") -> Registration:
    """Load registration state relative to a repository root.

    A missing registry is treated as *nothing registered* rather than an error:
    the absence of a registry is exactly the state Article L-11 describes.
    """
    path = Path(root) / DEFAULT_REGISTRY_PATH
    if not path.exists():
        return Registration(False, False, False, False)
    return RegistryState.load(path).to_registration()


__all__ = [
    "DEFAULT_REGISTRY_PATH",
    "GOVERNING_ARTIFACTS",
    "RegistryState",
    "load_registration",
]

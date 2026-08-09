"""Mechanisms and controls, and the single place they are registered.

Responsibility: make every available component visible in one file. Importing
this package is what populates the model, memory, gate, replay and environment
tables; there is no filesystem scan, so a mechanism that is not imported here
does not exist as far as a config file is concerned.

    v0.py            protocol adapters over the frozen M0 rig (no behaviour change)
    controls.py      the comparison conditions the M0 review requires
    environments.py  environments with separable randomness (V0-4)
"""

from __future__ import annotations

from science.mechanisms import controls, environments, v0  # noqa: F401  (registration)

__all__ = ["controls", "environments", "v0"]

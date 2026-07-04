"""
research/policies
=================

The hot-swappable :class:`ConsolidationPolicy` family for Sprint R1.

Selection is config-driven: a benchmark names a policy (``"free_energy"``,
``"similarity"``, ...) and :func:`build_policy` constructs it. Because the
registry is keyed by the policies' own ``name`` class attribute, adding a new
policy is a one-line registration with no change to any call site — the open/
closed extension point for future strategies.

Registry contract
------------------
* Every value is a :class:`ConsolidationPolicy` *subclass* (not an instance).
* :func:`build_policy` instantiates the named class, forwarding any keyword
  arguments (e.g. energy coefficients for ``free_energy``).
* No policy module imports another policy module — only :mod:`research.policies.base`
  and frozen cognition components — so the family has zero internal coupling.
"""

from __future__ import annotations

from typing import Any, Dict, List, Type

from research.policies.base import (
    AcceptVerdict,
    ConsolidationPolicy,
    PolicyContext,
)
from research.policies.fifo import FIFOAgePolicy
from research.policies.free_energy import FreeEnergyPolicy
from research.policies.null import NullPolicy
from research.policies.oracle import OracleNotImplementedError, PlaceholderOraclePolicy
from research.policies.random_policy import RandomPolicy
from research.policies.similarity import SimilarityPolicy
from research.policies.utility import UtilityPolicy

#: The single source of truth mapping a config key -> policy class.
POLICY_REGISTRY: Dict[str, Type[ConsolidationPolicy]] = {
    NullPolicy.name: NullPolicy,
    RandomPolicy.name: RandomPolicy,
    FIFOAgePolicy.name: FIFOAgePolicy,
    SimilarityPolicy.name: SimilarityPolicy,
    UtilityPolicy.name: UtilityPolicy,
    FreeEnergyPolicy.name: FreeEnergyPolicy,
    PlaceholderOraclePolicy.name: PlaceholderOraclePolicy,
}

#: The default ablation arm order (control first, principled policy last). The
#: optional oracle is intentionally excluded from the default sweep.
DEFAULT_POLICY_ORDER: List[str] = [
    "null",
    "random",
    "fifo",
    "similarity",
    "utility",
    "free_energy",
]


def available_policies() -> List[str]:
    """Return all registered policy names, sorted for stable display."""
    return sorted(POLICY_REGISTRY)


def build_policy(name: str, **params: Any) -> ConsolidationPolicy:
    """Construct a policy by its registry ``name``, forwarding ``params``.

    Raises
    ------
    KeyError
        If ``name`` is not registered, with the list of valid names.
    """
    try:
        cls = POLICY_REGISTRY[name]
    except KeyError:
        valid = ", ".join(available_policies()) or "(none registered)"
        raise KeyError(
            f"Unknown policy {name!r}. Registered policies: {valid}."
        ) from None
    return cls(**params)


__all__ = [
    "ConsolidationPolicy",
    "PolicyContext",
    "AcceptVerdict",
    "NullPolicy",
    "RandomPolicy",
    "FIFOAgePolicy",
    "SimilarityPolicy",
    "UtilityPolicy",
    "FreeEnergyPolicy",
    "PlaceholderOraclePolicy",
    "OracleNotImplementedError",
    "POLICY_REGISTRY",
    "DEFAULT_POLICY_ORDER",
    "available_policies",
    "build_policy",
]

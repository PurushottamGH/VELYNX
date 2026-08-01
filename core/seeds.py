"""Independent, reproducible random substreams.

Responsibility: turn one master seed into named, statistically unrelated seeds,
and record exactly which value each component received.

The M0 review requires environment, trajectory, replay, probe and task-order
randomness to be separable (risk 9, recommendation 6, experiment V0-4): with a
single composite seed, one variance source can dominate a contrast invisibly.

Two modes exist and the difference is scientific, not cosmetic:

    "legacy_v0"    every substream equals the master seed. This reproduces the
                   frozen `p1v0` rig bit-for-bit and exists so the platform can
                   be proven equivalent to the artifact under review. It must
                   not be used for variance decomposition.

    "independent"  each substream is derived by SHA-256 of "<master>:<stream>".
                   Substreams are then reproducible, mutually unrelated, and
                   individually overridable, which is what V0-4 requires.

SHA-256 is used rather than Python's `hash` because the latter is salted per
process for str inputs and would break reproducibility across runs.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, Mapping, Tuple

#: Named substreams. Adding one is a breaking change to run identity, so the
#: tuple is closed and any addition must bump the config version.
STREAMS: Tuple[str, ...] = ("environment", "trajectory", "replay", "probe", "order")

MODES: Tuple[str, ...] = ("legacy_v0", "independent")

#: Keeps derived seeds inside the range accepted by `random.Random` on all
#: platforms and inside a JSON-safe integer width.
_SEED_MODULUS = 2**31 - 1


def derive_seed(master: int, stream: str) -> int:
    """Deterministic, platform-independent substream seed."""
    digest = hashlib.sha256(f"{int(master)}:{stream}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % _SEED_MODULUS


@dataclass(frozen=True)
class SeedSet:
    """The full random identity of a run.

    `explicit` records only the substreams a config overrode by hand, so the
    manifest distinguishes "derived from master 7" from "pinned to 12345".
    """

    master: int
    mode: str
    seeds: Dict[str, int]
    explicit: Tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def build(
        cls,
        master: int,
        mode: str = "independent",
        overrides: Mapping[str, int] | None = None,
    ) -> "SeedSet":
        if mode not in MODES:
            raise ValueError(f"unknown seed mode {mode!r}; expected one of {MODES}")
        overrides = dict(overrides or {})
        unknown = set(overrides) - set(STREAMS)
        if unknown:
            raise ValueError(
                f"unknown seed stream(s) {sorted(unknown)}; expected subset of {STREAMS}"
            )
        if mode == "legacy_v0":
            seeds = {name: int(master) for name in STREAMS}
        else:
            seeds = {name: derive_seed(master, name) for name in STREAMS}
        for name, value in overrides.items():
            seeds[name] = int(value)
        return cls(
            master=int(master),
            mode=mode,
            seeds=seeds,
            explicit=tuple(sorted(overrides)),
        )

    def __getitem__(self, stream: str) -> int:
        if stream not in self.seeds:
            raise KeyError(f"no seed for stream {stream!r}; have {sorted(self.seeds)}")
        return self.seeds[stream]

    def as_dict(self) -> Dict[str, object]:
        return {
            "master": self.master,
            "mode": self.mode,
            "seeds": dict(self.seeds),
            "explicit": list(self.explicit),
        }

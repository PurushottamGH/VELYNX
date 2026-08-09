"""Named deterministic random substreams for P1-LN-DEC."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Dict, Mapping, Tuple

import numpy as np


STREAM_NAMES: Tuple[str, ...] = (
    "generator",
    "trajectory",
    "probe",
    "model_init",
    "replay",
    "evaluation",
)
_MODULUS = 2**31 - 1


def derive_seed(master: int, stream: str) -> int:
    """Derive one platform-independent child seed."""
    if stream not in STREAM_NAMES:
        raise ValueError(f"unknown RNG stream {stream!r}; expected {STREAM_NAMES}")
    digest = hashlib.sha256(f"p1-ln-dec:{int(master)}:{stream}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % _MODULUS


@dataclass(frozen=True)
class SeedStreams:
    """Immutable master/substream identity recorded in every manifest."""

    master: int
    seeds: Mapping[str, int]

    @classmethod
    def build(
        cls, master: int, overrides: Mapping[str, int] | None = None
    ) -> "SeedStreams":
        overrides = dict(overrides or {})
        unknown = set(overrides) - set(STREAM_NAMES)
        if unknown:
            raise ValueError(f"unknown RNG stream override(s): {sorted(unknown)}")
        seeds = {name: derive_seed(master, name) for name in STREAM_NAMES}
        seeds.update({name: int(value) for name, value in overrides.items()})
        return cls(master=int(master), seeds=seeds)

    def random(self, stream: str) -> random.Random:
        return random.Random(self.seeds[stream])

    def numpy(self, stream: str) -> np.random.Generator:
        return np.random.default_rng(self.seeds[stream])

    def as_dict(self) -> Dict[str, int]:
        return dict(self.seeds)


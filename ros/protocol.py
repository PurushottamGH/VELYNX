"""P1 Research Operating System — the protocol compiler (invariant K3).

A protocol is preregistration made mechanical. This module lints one, freezes
it, and content-addresses it, so that the question "was this margin chosen
before or after the result?" is answered by a digest rather than by memory.

The required fields are exactly those the Constitution Lock E1 enumerates:

    hypothesis, conditions, controls and what each removes, estimand, unit of
    inference, pairing, SESOI/equivalence margin, guardrails, seed generation,
    tuning/confirmation split, stopping rule, exclusion rule, multiplicity family

Two rules in the lint are worth naming because they encode the failure modes E1
lists rather than merely checking presence:

* every control must state *which confound it removes* — a control declared
  without its confound is decoration, and E1 names this precisely;
* a tuning/confirmation split must separate seeds, because reusing tuning seeds
  for confirmation is how a stopping rule gets altered after inspection.

Freezing writes a sidecar digest file. That is the only write in this module and
it is an engineering-class write (``protocol.draft``); *committing* the freeze as
evidence is ``protocol.freeze``, which :mod:`ros.authority` reserves to humans.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .store import Finding

#: Fields Lock E1 requires of every protocol.
REQUIRED_FIELDS: tuple[str, ...] = (
    "id",
    "hypothesis",
    "conditions",
    "controls",
    "estimand",
    "unit_of_inference",
    "pairing",
    "sesoi",
    "guardrails",
    "seed_generation",
    "tuning_confirmation_split",
    "stopping_rule",
    "exclusion_rule",
    "multiplicity_family",
)

#: Fields whose value must be a non-empty list rather than a scalar.
LIST_FIELDS: frozenset[str] = frozenset({"conditions", "controls", "guardrails"})

DIGEST_SUFFIX = ".frozen.json"


@dataclass(frozen=True)
class Freeze:
    """The immutable record produced when a protocol is frozen."""

    protocol_id: str
    digest: str
    source: str
    #: Populated by the caller from the repository, never by this module.
    frozen_at_commit: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol_id": self.protocol_id,
            "digest": self.digest,
            "source": self.source,
            "frozen_at_commit": self.frozen_at_commit,
            "algorithm": "blake2b-256-canonical-json",
        }


def canonical_bytes(protocol: dict[str, Any]) -> bytes:
    """Canonical serialisation used for hashing.

    Sorted keys, no insignificant whitespace, UTF-8. Comments and key order in
    the YAML source are deliberately not part of the identity: reordering a
    protocol must not look like changing it, and reformatting must not
    invalidate a freeze.
    """
    payload = {k: v for k, v in protocol.items() if not str(k).startswith("_")}
    text = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return text.encode("utf-8")


def digest(protocol: dict[str, Any]) -> str:
    return hashlib.blake2b(canonical_bytes(protocol), digest_size=32).hexdigest()


def lint(protocol: dict[str, Any]) -> list[Finding]:
    """Findings against a protocol. An empty list means it may be frozen."""
    findings: list[Finding] = []
    identifier = str(protocol.get("id") or "<unidentified>")

    for name in REQUIRED_FIELDS:
        if name not in protocol:
            findings.append(
                Finding("PROTO-201", "error", identifier, f"missing required field {name!r}")
            )
            continue
        value = protocol[name]
        if value is None or (isinstance(value, (str, list, dict)) and len(value) == 0):
            findings.append(
                Finding("PROTO-202", "error", identifier, f"required field {name!r} is empty")
            )

    for name in LIST_FIELDS:
        value = protocol.get(name)
        if value is not None and not isinstance(value, list):
            findings.append(
                Finding(
                    "PROTO-203",
                    "error",
                    identifier,
                    f"field {name!r} must be a list, got {type(value).__name__}",
                )
            )

    for index, control in enumerate(protocol.get("controls") or []):
        where = f"{identifier}.controls[{index}]"
        if not isinstance(control, dict):
            findings.append(
                Finding(
                    "PROTO-210",
                    "error",
                    where,
                    "control must be a mapping with 'name' and 'removes'",
                )
            )
            continue
        if not control.get("name"):
            findings.append(Finding("PROTO-211", "error", where, "control has no name"))
        if not control.get("removes"):
            findings.append(
                Finding(
                    "PROTO-212",
                    "error",
                    where,
                    "control does not state which confound it removes; Lock E1 names "
                    "'controls declared without stating which confound they remove' "
                    "as a failure mode",
                )
            )

    split = protocol.get("tuning_confirmation_split")
    if isinstance(split, dict):
        tuning = {str(s) for s in split.get("tuning_seeds") or []}
        confirm = {str(s) for s in split.get("confirmation_seeds") or []}
        if not tuning or not confirm:
            findings.append(
                Finding(
                    "PROTO-220",
                    "error",
                    identifier,
                    "tuning_confirmation_split must name both tuning_seeds and "
                    "confirmation_seeds",
                )
            )
        overlap = tuning & confirm
        if overlap:
            findings.append(
                Finding(
                    "PROTO-221",
                    "error",
                    identifier,
                    f"seeds {sorted(overlap)} appear in both tuning and confirmation; "
                    "confirmation seeds must be separated",
                )
            )

    sesoi = protocol.get("sesoi")
    if isinstance(sesoi, (int, float)) and sesoi <= 0:
        findings.append(
            Finding(
                "PROTO-230",
                "error",
                identifier,
                "SESOI must be a positive smallest effect size of interest",
            )
        )

    return findings


def load(path: Path | str) -> dict[str, Any]:
    path = Path(path)
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: protocol must be a mapping")
    return data


def freeze_path_for(path: Path | str) -> Path:
    path = Path(path)
    return path.with_name(path.name + DIGEST_SUFFIX)


def freeze(path: Path | str, commit: str | None = None) -> Freeze:
    """Lint, then freeze a protocol, writing its digest sidecar.

    Raises :class:`ValueError` if the protocol does not lint clean. A protocol
    that cannot be frozen cannot be run against, which is the point: the gate is
    before the first tick, not after the last.
    """
    path = Path(path)
    protocol = load(path)
    findings = lint(protocol)
    if findings:
        detail = "\n".join(f"  {f}" for f in findings)
        raise ValueError(f"{path}: protocol does not lint clean:\n{detail}")

    record = Freeze(
        protocol_id=str(protocol["id"]),
        digest=digest(protocol),
        source=path.as_posix(),
        frozen_at_commit=commit,
    )
    target = freeze_path_for(path)
    target.write_text(
        json.dumps(record.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return record


def verify(path: Path | str) -> tuple[bool, str]:
    """Check a protocol against its freeze. Returns ``(matched, message)``."""
    path = Path(path)
    sidecar = freeze_path_for(path)
    if not sidecar.exists():
        return False, f"{path}: no freeze record at {sidecar.name}; protocol was never frozen"
    recorded = json.loads(sidecar.read_text(encoding="utf-8"))
    current = digest(load(path))
    if current != recorded.get("digest"):
        return False, (
            f"{path}: protocol has changed since it was frozen "
            f"(frozen {str(recorded.get('digest'))[:16]}, now {current[:16]}). "
            "A deviation is recorded, never edited away."
        )
    return True, f"{path}: matches freeze {current[:16]}"


__all__ = [
    "Freeze",
    "REQUIRED_FIELDS",
    "canonical_bytes",
    "digest",
    "freeze",
    "freeze_path_for",
    "lint",
    "load",
    "verify",
]

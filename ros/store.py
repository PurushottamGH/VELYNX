"""P1 Research Operating System — the record store (kernel invariant K1).

One writable scientific store; every registry, dashboard and report is a
generated projection of it. This module loads that store, indexes it, and
computes integrity findings over it.

Why this exists. Three representations of the scientific record are present in
the repository at the time of writing:

* ``science/SKB_RECORDS_v1.0.yaml`` — declared canonical by ``SCIENTIFIC_INDEX.md``
* ``science/skb/*.md`` — twelve hand-maintained registries, which are what people read
* ``p1/tooling/p1_os/schemas/`` — twelve pydantic types validating a ``records/`` tree

Two of those three will drift, and the drift is undetectable because nothing
compares them. That is the same defect ``P1_V2_CONSTITUTION_LOCK_v1.0.md``
Contradiction 1 removed from the ontology, surviving in the record layer because
the Lock never covered it. This module makes the first representation the store
and everything else a projection.

Read-only by construction: no function here writes to disk.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator

import yaml

from .model import (
    COLLECTION_BY_KEY,
    COLLECTIONS,
    DECISION_ACTIONS,
    EVIDENCE_DIRECTIONS,
    HYPOTHESIS_STATUSES,
    NON_RECORD_KEYS,
    Collection,
    collection_for_id,
    conforms,
    iter_id_references,
)

DEFAULT_STORE_PATH = Path("science/SKB_RECORDS_v1.0.yaml")

#: Severity ordering used by gates. ``error`` fails a gate; ``warning`` is
#: reported and does not.
SEVERITIES = ("error", "warning", "info")


@dataclass(frozen=True)
class Finding:
    """One integrity finding against the store."""

    code: str
    severity: str
    subject: str
    message: str

    def __str__(self) -> str:  # pragma: no cover - display only
        return f"[{self.severity.upper()}] {self.code} {self.subject}: {self.message}"


@dataclass
class Record:
    """A single SKB record with its collection and raw payload."""

    identifier: str
    collection: Collection
    data: dict[str, Any]

    @property
    def status(self) -> str | None:
        value = self.data.get("status")
        return str(value) if value is not None else None

    @property
    def title(self) -> str:
        return str(self.data.get("title") or self.data.get("statement") or self.identifier)

    def references(self) -> list[tuple[str, str]]:
        """Identifier references in this record, excluding its own ``id`` field."""
        return [
            (path, identifier)
            for path, identifier in iter_id_references(self.data)
            if not (path == "id" and identifier == self.identifier)
        ]


@dataclass
class Relation:
    """A typed relation from the store's ``relations`` collection."""

    source: str
    target: str
    kind: str
    direction: str | None = None
    note: str | None = None


@dataclass
class Store:
    """An loaded, indexed SKB."""

    path: Path
    header: dict[str, Any]
    records: dict[str, Record] = field(default_factory=dict)
    relations: list[Relation] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    # ---------------------------------------------------------------- loading

    @classmethod
    def load(cls, path: Path | str = DEFAULT_STORE_PATH) -> "Store":
        """Load and index the store. Raises on unparseable or non-mapping YAML."""
        path = Path(path)
        with path.open(encoding="utf-8") as handle:
            raw = yaml.safe_load(handle)
        if not isinstance(raw, dict):
            raise ValueError(f"{path}: store root must be a mapping, got {type(raw).__name__}")

        store = cls(path=path, header=dict(raw.get("skb") or {}), raw=raw)

        for collection in COLLECTIONS:
            for entry in raw.get(collection.key) or []:
                if not isinstance(entry, dict):
                    continue
                identifier = str(entry.get("id", "")).strip()
                if not identifier:
                    continue
                store.records[identifier] = Record(identifier, collection, entry)

        for entry in raw.get("relations") or []:
            if not isinstance(entry, dict):
                continue
            store.relations.append(
                Relation(
                    source=str(entry.get("from", "")).strip(),
                    target=str(entry.get("to", "")).strip(),
                    kind=str(entry.get("type", "")).strip(),
                    direction=entry.get("direction"),
                    note=entry.get("semantic_note"),
                )
            )
        return store

    # ---------------------------------------------------------------- queries

    def __len__(self) -> int:
        return len(self.records)

    def __contains__(self, identifier: object) -> bool:
        return str(identifier) in self.records

    def get(self, identifier: str) -> Record | None:
        return self.records.get(identifier)

    def by_collection(self, key: str) -> list[Record]:
        """All records in a named collection, in store order."""
        return [r for r in self.records.values() if r.collection.key == key]

    def with_status(self, key: str, statuses: Iterable[str]) -> list[Record]:
        wanted = {s.lower() for s in statuses}
        return [r for r in self.by_collection(key) if (r.status or "").lower() in wanted]

    def iter_records(self) -> Iterator[Record]:
        return iter(self.records.values())

    def counts(self) -> dict[str, int]:
        """Record count per collection key, including empty collections."""
        result = {c.key: 0 for c in COLLECTIONS}
        for record in self.records.values():
            result[record.collection.key] += 1
        return result

    # ------------------------------------------------------------- addressing

    def content_hash(self) -> str:
        """BLAKE2b digest over the canonical form of the record collections.

        Matches the Constitution Lock's content-addressing choice (R5). The
        ``skb`` header is excluded so that re-stating the state date does not
        change the digest of the science.
        """
        payload = {k: v for k, v in self.raw.items() if k not in {"skb"}}
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.blake2b(canonical.encode("utf-8"), digest_size=32).hexdigest()

    # -------------------------------------------------------------- integrity

    def check(self) -> list[Finding]:
        """Compute all integrity findings. Deterministic order."""
        findings: list[Finding] = []
        findings += self._check_identifiers()
        findings += self._check_references()
        findings += self._check_relations()
        findings += self._check_vocabularies()
        findings += self._check_evidence_graph()
        findings += self._check_supersession()
        return sorted(findings, key=lambda f: (SEVERITIES.index(f.severity), f.code, f.subject))

    def _check_identifiers(self) -> list[Finding]:
        findings: list[Finding] = []
        seen: dict[str, str] = {}
        for record in self.records.values():
            collection = collection_for_id(record.identifier)
            if collection is None:
                findings.append(
                    Finding(
                        "SKB-101",
                        "error",
                        record.identifier,
                        "identifier does not match PREFIX-YYYY-NNNN or prefix is unregistered",
                    )
                )
            elif collection.key != record.collection.key:
                findings.append(
                    Finding(
                        "SKB-102",
                        "error",
                        record.identifier,
                        f"identifier prefix implies {collection.key!r} "
                        f"but record is filed under {record.collection.key!r}",
                    )
                )
            if record.identifier in seen:
                findings.append(
                    Finding("SKB-103", "error", record.identifier, "duplicate identifier")
                )
            seen[record.identifier] = record.collection.key
        return findings

    def _check_references(self) -> list[Finding]:
        findings: list[Finding] = []
        for record in self.records.values():
            for path, identifier in record.references():
                if identifier not in self.records:
                    findings.append(
                        Finding(
                            "SKB-110",
                            "error",
                            record.identifier,
                            f"dangling reference {identifier} at field {path!r}",
                        )
                    )
        return findings

    def _check_relations(self) -> list[Finding]:
        findings: list[Finding] = []
        for index, relation in enumerate(self.relations):
            subject = f"relations[{index}]"
            for role, identifier in (("from", relation.source), ("to", relation.target)):
                if not identifier:
                    findings.append(
                        Finding("SKB-120", "error", subject, f"relation {role} is empty")
                    )
                elif identifier not in self.records:
                    findings.append(
                        Finding(
                            "SKB-121",
                            "error",
                            subject,
                            f"relation {role} {identifier} resolves to no record",
                        )
                    )
            if not relation.kind:
                findings.append(Finding("SKB-122", "error", subject, "relation type is empty"))
        return findings

    def _check_vocabularies(self) -> list[Finding]:
        findings: list[Finding] = []
        for record in self.by_collection("hypotheses"):
            if record.status and record.status not in HYPOTHESIS_STATUSES:
                findings.append(
                    Finding(
                        "SKB-130",
                        "error",
                        record.identifier,
                        f"status {record.status!r} is not one of the seven permitted by "
                        f"SCIENTIFIC_OPERATING_SYSTEM.md section 5",
                    )
                )
        for record in self.by_collection("evidence"):
            if not conforms(record.data.get("direction"), EVIDENCE_DIRECTIONS):
                findings.append(
                    Finding(
                        "SKB-131",
                        "warning",
                        record.identifier,
                        f"evidence direction {record.data.get('direction')!r} is outside "
                        f"the Lock E4 relation types",
                    )
                )
        for record in self.by_collection("decisions"):
            if not conforms(record.data.get("action"), DECISION_ACTIONS):
                findings.append(
                    Finding(
                        "SKB-132",
                        "warning",
                        record.identifier,
                        f"decision action {record.data.get('action')!r} is outside "
                        f"the Lock E5 action set",
                    )
                )
        return findings

    def _check_evidence_graph(self) -> list[Finding]:
        """Evidence-graph defects the Lock E4 names as detectable: orphans and
        untargeted evidence."""
        findings: list[Finding] = []
        cited: set[str] = set()
        for record in self.records.values():
            if record.collection.key == "evidence":
                continue
            for _, identifier in record.references():
                if identifier.startswith("EVD-"):
                    cited.add(identifier)
        for relation in self.relations:
            if relation.source.startswith("EVD-"):
                cited.add(relation.source)
            if relation.target.startswith("EVD-"):
                cited.add(relation.target)

        for record in self.by_collection("evidence"):
            if not record.data.get("target"):
                findings.append(
                    Finding(
                        "SKB-140",
                        "error",
                        record.identifier,
                        "evidence record names no target claim",
                    )
                )
            if record.identifier not in cited:
                findings.append(
                    Finding(
                        "SKB-141",
                        "warning",
                        record.identifier,
                        "orphan evidence: no record or relation cites it",
                    )
                )
            if not record.data.get("source_observations"):
                findings.append(
                    Finding(
                        "SKB-142",
                        "warning",
                        record.identifier,
                        "evidence cites no source observation",
                    )
                )
        return findings

    def _check_supersession(self) -> list[Finding]:
        findings: list[Finding] = []
        for record in self.records.values():
            if (record.status or "").lower() != "superseded":
                continue
            if not record.data.get("superseded_by"):
                findings.append(
                    Finding(
                        "SKB-150",
                        "error",
                        record.identifier,
                        "status Superseded without a superseded_by lineage pointer",
                    )
                )
        return findings


def errors(findings: Iterable[Finding]) -> list[Finding]:
    return [f for f in findings if f.severity == "error"]


def load_default(root: Path | str = ".") -> Store:
    """Load the store relative to a repository root."""
    return Store.load(Path(root) / DEFAULT_STORE_PATH)


__all__ = [
    "DEFAULT_STORE_PATH",
    "Finding",
    "Record",
    "Relation",
    "Store",
    "errors",
    "load_default",
]

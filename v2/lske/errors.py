"""Frozen LSKE exception taxonomy from Specification v1.1.2 sections 9.5 and 9.5.1.

The seven classes of §9.5 are unchanged. ``SchemaViolation`` additionally carries
the public failure payload contract of §9.5.1 (``RF-01``), which is part of this
taxonomy's own contract and not a second API.
"""

from collections.abc import Iterable


class LskeError(Exception):
    """Root of every LSKE-defined exception."""


class SchemaViolation(LskeError, ValueError):
    """A record or event violates its canonical schema.

    Carries the sole public failure payload of §9.5.1 (``RF-01``): a tuple of
    four-element primitive tuples ``(instance_pointer, schema_pointer, keyword,
    derived)``, normalized on construction so that the payload is canonical on
    every instance and presents the same order for the same failure set
    regardless of which raise site produced it.
    """

    failures: tuple[tuple[str, str, str, bool], ...]

    def __init__(
        self,
        message: str,
        failures: Iterable[tuple[str, str, str, bool]] = (),
    ) -> None:
        # §9.5.1 cl. 1: args is exactly (message,), so str(self) is the RB-05
        # cl. 1 message and no failure information is carried in args[1:].
        super().__init__(message)
        # §9.5.1 cl. 5: (a) materialize the iterable, (b) remove items equal to
        # an earlier item keeping the first occurrence, (c) sort by the total key
        # (derived, instance_pointer, schema_pointer, keyword) -- derived
        # ascending so False precedes True, the three strings ascending by
        # Unicode code point. This does not compute derived, does not rewrite an
        # item and does not validate item shape: producing well-formed items is
        # the raiser's obligation.
        deduplicated = dict.fromkeys(tuple(failures))
        self.failures = tuple(
            sorted(deduplicated, key=lambda item: (item[3], item[0], item[1], item[2]))
        )


class TransactionRefused(LskeError, RuntimeError):
    """A transaction cannot be evaluated or committed."""


class SnapshotIntegrityError(LskeError, RuntimeError):
    """A snapshot cannot be reconstructed at its recorded hash."""


class QueryError(LskeError, ValueError):
    """A SQL-P1 query cannot be parsed or evaluated safely."""


class OntologyError(LskeError, ValueError):
    """A record declares an object outside the frozen ontology."""


class RelationError(LskeError, ValueError):
    """A relation violates the frozen relation ontology."""


__all__ = [
    "LskeError",
    "OntologyError",
    "QueryError",
    "RelationError",
    "SchemaViolation",
    "SnapshotIntegrityError",
    "TransactionRefused",
]

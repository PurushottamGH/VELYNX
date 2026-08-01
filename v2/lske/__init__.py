"""Living Scientific Knowledge Engine package.

This package keeps its package version constant and nothing else: per RF-04
cl. 2 it defines no ``ONTOLOGY_VERSION`` and exports none. The ontology
version is owned solely by :mod:`v2.lske.schema` (§9.13.2), and RF-04 cl. 3
makes the two quantities distinct -- ``__version__`` is the package version
and is written into no record.
"""

__version__ = "1.1.0"

__all__ = ["__version__"]

"""Tests for the P1 Research Operating System (the ``ros`` package).

Named ``research_os`` rather than ``ros`` on purpose. Pytest inserts ``tests/``
onto ``sys.path`` to import a test package, so a directory named ``tests/ros/``
would be imported as the top-level module ``ros`` and shadow the package under
test — the same collision ``pyproject.toml`` documents for ``tests/p1_os/``. The
symptom is a bare ``ModuleNotFoundError: No module named 'ros.store'``, which
points nowhere near the cause.

Scope: the operating system *around* the frozen P1-v2 architecture. Nothing here
tests the engine, and nothing here is scientific evidence — per
``SCIENTIFIC_OPERATING_SYSTEM.md`` section 11, implementation conformance is not
evidence for any mechanism.

Every gate has a **negative control**: a fixture the gate must reject. A gate
verified only against the live repository, which currently passes, would be
indistinguishable from a gate that always returns success, and this repository's
engineering standard is that a step which cannot fail is not verification.
"""

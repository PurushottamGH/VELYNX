"""
Pytest configuration for the VELYNX backend test suite.

Registers the custom markers used across the suite so pytest does not emit
``PytestUnknownMarkWarning``. There is no repo-wide ``pytest.ini`` /
``pyproject`` pytest table, so markers are registered here at collection time.

Markers
-------
slow
    A long-running / live-fire test that talks to the real pipeline. Excluded
    from the fast unit run via ``-m "not slow"`` and included in the full run.
asyncio
    Retained for compatibility with tests authored against the pytest-asyncio
    convention. NOTE: pytest-asyncio is not a dependency of this repo; async
    tests drive their coroutine explicitly via ``asyncio.run`` (see
    test_inheritance_inference.py / test_episodic_memory.py), so this marker is
    purely descriptive here and does not by itself await a coroutine.
"""
from __future__ import annotations


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slow: long-running / live-fire test (excluded from the fast unit run).",
    )
    config.addinivalue_line(
        "markers",
        "asyncio: descriptive marker for async-style tests driven via asyncio.run.",
    )

"""Correlation ID propagation via contextvars — async-safe tracing."""
from __future__ import annotations

import contextvars
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

_correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default=""
)


def new_correlation_id() -> str:
    """Generate a new correlation ID."""
    return uuid.uuid4().hex[:16]


def get_correlation_id() -> str:
    """Get the current correlation ID, or generate one if unset."""
    cid = _correlation_id.get()
    if not cid:
        cid = new_correlation_id()
        _correlation_id.set(cid)
    return cid


def set_correlation_id(cid: str) -> None:
    """Explicitly set the correlation ID."""
    _correlation_id.set(cid)


@asynccontextmanager
async def trace(correlation_id: str | None = None) -> AsyncIterator[str]:
    """Context manager that sets a correlation ID for the block."""
    cid = correlation_id or new_correlation_id()
    token = _correlation_id.set(cid)
    try:
        yield cid
    finally:
        _correlation_id.reset(token)

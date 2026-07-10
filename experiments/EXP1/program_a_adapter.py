"""Program A adapter contract for EXP-1 execution.

Adapters expose only the public answer surface required by EXP-1. They do not
own rubric adjudication, calibration, or decision rules.
"""
from __future__ import annotations

from collections.abc import Awaitable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from experiments.EXP1.dataset import AnswerRecord, QueryRecord


ProgramAAnswer = AnswerRecord | Mapping[str, Any] | Awaitable[Any]


@runtime_checkable
class ProgramAAdapter(Protocol):
    """Minimal Program A public-answer interface required by EXP-1."""

    @property
    def adapter_id(self) -> str:
        """Stable adapter identity recorded in the execution manifest."""

    def answer(self, query: QueryRecord, seed: int) -> ProgramAAnswer:
        """Return Program A's public answer and confidence tier for one query."""


@dataclass(frozen=True)
class CallableProgramAAdapter:
    """Small adapter for existing injected answer callables."""

    adapter_id: str
    answer_fn: Any

    def __post_init__(self) -> None:
        if not str(self.adapter_id).strip():
            raise ValueError("adapter_id is required")
        if not callable(self.answer_fn):
            raise TypeError("answer_fn must be callable")

    def answer(self, query: QueryRecord, seed: int) -> ProgramAAnswer:
        return self.answer_fn(query, seed)


def callable_identity(value: Any) -> str:
    """Return a deterministic import-style identity for a callable or object."""

    module = getattr(value, "__module__", value.__class__.__module__)
    qualname = getattr(value, "__qualname__", value.__class__.__qualname__)
    return f"{module}.{qualname}"


def coerce_program_a_adapter(
    *,
    adapter: ProgramAAdapter | None = None,
    answer_fn: Any | None = None,
    adapter_id: str | None = None,
) -> ProgramAAdapter:
    """Normalize explicit adapters and legacy answer callables."""

    if adapter is not None and answer_fn is not None:
        raise ValueError("provide either adapter or answer_fn, not both")
    if adapter is not None:
        if not isinstance(adapter, ProgramAAdapter):
            raise TypeError("adapter must implement ProgramAAdapter")
        if not str(adapter.adapter_id).strip():
            raise ValueError("adapter_id is required")
        return adapter
    if answer_fn is None:
        raise ValueError("Program A adapter or answer_fn is required")
    return CallableProgramAAdapter(
        adapter_id=adapter_id or callable_identity(answer_fn),
        answer_fn=answer_fn,
    )

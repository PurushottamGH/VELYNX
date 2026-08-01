"""Name -> factory lookup. The only plugin wiring mechanism in P1.

Responsibility: turn a `{"name": ..., "params": {...}}` specification from a
config file into a live object, and refuse anything ambiguous.

One generic `Registry` class is instantiated once per component kind. There is
deliberately no plugin auto-discovery by filesystem scan: registration is an
explicit import in `science/mechanisms/__init__.py`, so the set of available
mechanisms is greppable and a typo cannot silently resolve to nothing.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Callable, Dict, Generic, Mapping, Tuple, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Spec:
    """A component selection: which implementation, with which parameters."""

    name: str
    params: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def parse(cls, raw: Any) -> "Spec":
        """Accept `"name"`, `{"name": ...}` or `{"name": ..., "params": {...}}`.

        The string form exists because `gate: never` is clearer than
        `gate: {name: never, params: {}}` for parameterless components.
        """
        if isinstance(raw, str):
            return cls(name=raw)
        if isinstance(raw, Spec):
            return raw
        if isinstance(raw, Mapping):
            if "name" not in raw:
                raise ValueError(f"component spec is missing 'name': {dict(raw)!r}")
            unknown = set(raw) - {"name", "params"}
            if unknown:
                raise ValueError(
                    f"component spec {raw['name']!r} has unexpected keys {sorted(unknown)}; "
                    "put component arguments under 'params'"
                )
            params = raw.get("params") or {}
            if not isinstance(params, Mapping):
                raise ValueError(f"'params' of {raw['name']!r} must be a mapping")
            return cls(name=str(raw["name"]), params=dict(params))
        raise TypeError(f"cannot read a component spec from {type(raw).__name__}")

    def as_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "params": dict(self.params)}


class Registry(Generic[T]):
    """Explicit, immutable-by-default name -> factory table for one kind."""

    def __init__(self, kind: str) -> None:
        self.kind = kind
        self._factories: Dict[str, Callable[..., T]] = {}

    def register(self, name: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """Decorator. Re-registering a name is an error, not a silent override."""

        def decorate(factory: Callable[..., T]) -> Callable[..., T]:
            if name in self._factories:
                raise ValueError(
                    f"{self.kind} {name!r} is already registered by "
                    f"{self._factories[name]!r}; pick a different name"
                )
            self._factories[name] = factory
            return factory

        return decorate

    def create(self, spec: Any, **injected: Any) -> T:
        """Instantiate from a spec.

        `injected` supplies engine-owned arguments (seeds, alphabet, horizon) that a
        config must not set by hand. Only the injections a factory actually declares
        are passed to it, which is what allows factories to omit `**kwargs` — and
        that omission is load-bearing: a factory that swallowed unknown keyword
        arguments would silently accept `decy` for `decay`, and the run would look
        correct while ignoring the parameter.
        """
        parsed = Spec.parse(spec)
        if parsed.name not in self._factories:
            raise KeyError(f"unknown {self.kind} {parsed.name!r}; available: {self.available()}")
        factory = self._factories[parsed.name]
        accepted, takes_var_keyword = _signature(factory)
        passed = (
            injected
            if takes_var_keyword
            else {key: value for key, value in injected.items() if key in accepted}
        )
        overlap = set(parsed.params) & set(passed)
        if overlap:
            raise ValueError(
                f"{self.kind} {parsed.name!r}: {sorted(overlap)} is supplied by the engine "
                "and must not be set in config params"
            )
        try:
            return factory(**parsed.params, **passed)
        except TypeError as exc:
            configurable = sorted(accepted - set(passed))
            raise ValueError(
                f"{self.kind} {parsed.name!r}: {exc}. Configurable params: {configurable}"
            ) from exc

    def available(self) -> list[str]:
        return sorted(self._factories)

    def __contains__(self, name: object) -> bool:
        return name in self._factories

    def __len__(self) -> int:
        return len(self._factories)


@lru_cache(maxsize=256)
def _signature(factory: Callable[..., Any]) -> Tuple[frozenset, bool]:
    """`(accepted keyword names, accepts **kwargs)` for a component factory.

    Cached: a sweep instantiates the same handful of factories hundreds of times,
    and `inspect.signature` is not cheap enough to call on every run.
    """
    try:
        parameters = inspect.signature(factory).parameters
    except (TypeError, ValueError):
        # Builtins and C callables have no introspectable signature. Assume they
        # accept anything rather than refusing to construct them.
        return frozenset(), True
    names = {
        name
        for name, param in parameters.items()
        if param.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
    }
    takes_var_keyword = any(
        param.kind is inspect.Parameter.VAR_KEYWORD for param in parameters.values()
    )
    return frozenset(names), takes_var_keyword

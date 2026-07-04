"""
backend/cognition/memory_scheduler.py
======================================

C8.0 — Autonomous Memory Management (scheduling only).

The :class:`MemoryScheduler` decides *when* the brain should consolidate its
memory ("sleep"), but performs no merging itself. It reads memory telemetry
from a duck-typed source (a ``ClusterEngine``, a ``VectorPredictionCore``, or
any wrapper such as ``VectorMonitor`` that exposes ``get_memory_summary()``)
and signals a consolidation cycle.

Control-system design (C8 upgrade)
----------------------------------
Behavioural control is deliberately isolated from the mathematical
optimisation that happens downstream. The scheduler is a pure controller with
three control-theoretic features:

* **Hysteresis (Schmitt trigger).** A single threshold causes *chattering* —
  the controller toggles on/off as the signal jitters around one setpoint.
  Instead we use two setpoints: the scheduler *enters* the consolidation state
  only when ``active_anomalies_count >= enter_pressure`` (default ``20``) and
  *exits* it only when ``active_anomalies_count <= exit_pressure`` (default
  ``10``). Between the two watermarks the controller holds its last state.
* **Time-based trigger.** Independent of pressure, the scheduler fires once
  ``ticks_since_consolidation`` reaches ``time_interval``.
* **Cooldown / refractory period.** After a consolidation cycle ends (the
  caller invokes :meth:`reset`), the scheduler will not evaluate pressure or
  time for a strict ``cooldown`` ticks (default ``50``). This guarantees the
  downstream merge machinery a stable window to settle before the controller
  is allowed to demand another cycle.

The scheduler never merges, re-clusters, or mutates memory; it only emits a
boolean "consolidate now" decision. That keeps the *when* (control) cleanly
separated from the *how* (optimisation).
"""

from __future__ import annotations

from typing import Any

# Default scheduling thresholds (see class docstring for semantics).
_DEFAULT_TIME_INTERVAL = 500
_DEFAULT_ENTER_PRESSURE = 20
_DEFAULT_EXIT_PRESSURE = 10
_DEFAULT_COOLDOWN = 50


class MemoryScheduler:
    """Decide when memory consolidation should run, without running it.

    Parameters
    ----------
    telemetry_source : object
        Anything exposing ``get_memory_summary() -> dict`` -- typically a
        ``VectorPredictionCore`` or the ``VectorMonitor`` that wraps it. The
        summary must contain ``active_anomalies_count`` for pressure-based
        triggering.
    time_interval : int
        Ticks that must elapse since the last consolidation before the
        time-based trigger fires. Defaults to ``500``.
    enter_pressure : int
        High watermark. The scheduler *enters* the consolidation state when
        ``active_anomalies_count >= enter_pressure``. Defaults to ``20``.
    exit_pressure : int
        Low watermark. Once in the consolidation state, the scheduler *exits*
        it only when ``active_anomalies_count <= exit_pressure``. Defaults to
        ``10``. Must be ``< enter_pressure`` for the hysteresis band to exist.
    cooldown : int
        Strict refractory period. After :meth:`reset` ends a cycle, the
        scheduler suppresses every trigger for this many ticks before it will
        evaluate pressure (or time) again. Defaults to ``50``.

    Notes
    -----
    ``anomaly_pressure`` is accepted as a backward-compatible alias for
    ``enter_pressure`` so existing callers keep working.
    """

    def __init__(
        self,
        telemetry_source: Any,
        time_interval: int = _DEFAULT_TIME_INTERVAL,
        enter_pressure: int = _DEFAULT_ENTER_PRESSURE,
        exit_pressure: int = _DEFAULT_EXIT_PRESSURE,
        cooldown: int = _DEFAULT_COOLDOWN,
        anomaly_pressure: int | None = None,
    ) -> None:
        self._telemetry = telemetry_source
        self.time_interval = time_interval
        # Back-compat: the legacy single-threshold kwarg maps onto the high
        # watermark so old call sites tune the *enter* setpoint as before.
        self.enter_pressure = (
            anomaly_pressure if anomaly_pressure is not None else enter_pressure
        )
        self.exit_pressure = exit_pressure
        self.cooldown = cooldown

        # -- controller state ----------------------------------------------
        self.ticks_since_consolidation = 0
        #: Schmitt-trigger latch: True while the controller is demanding
        #: consolidation. Set when pressure crosses the high watermark (or the
        #: time trigger fires); cleared when pressure falls to the low
        #: watermark or a cycle ends via :meth:`reset`.
        self.in_consolidation = False
        #: Ticks of refractory period still to serve before the controller is
        #: allowed to evaluate pressure/time again.
        self._cooldown_remaining = 0

    # -- legacy alias ------------------------------------------------------

    @property
    def anomaly_pressure(self) -> int:
        """Backward-compatible alias for the high watermark (:attr:`enter_pressure`)."""
        return self.enter_pressure

    @anomaly_pressure.setter
    def anomaly_pressure(self, value: int) -> None:
        self.enter_pressure = value


    # -- scheduling --------------------------------------------------------

    def tick(self) -> bool:
        """Advance the internal clock one tick and report the decision.

        Returns ``True`` when a consolidation cycle should run. The caller is
        responsible for acting on a ``True`` result and then calling
        :meth:`reset` once the consolidation cycle has completed, which arms
        the cooldown.

        While the cooldown is in force the controller is *refractory*: it
        decrements the cooldown and returns ``False`` without evaluating
        pressure or time, no matter how high the anomaly count climbs.
        """
        self.ticks_since_consolidation += 1

        # Refractory period: a freshly-ended cycle gets a stable settling
        # window before the controller may demand another one.
        if self._cooldown_remaining > 0:
            self._cooldown_remaining -= 1
            return False

        return self._should_consolidate()

    def _should_consolidate(self) -> bool:
        """Evaluate the hysteresis + time triggers against the current state."""
        active = self._active_anomalies_count()

        if self.in_consolidation:
            # Latched ON: hold until pressure relaxes to the low watermark.
            if active <= self.exit_pressure:
                self.in_consolidation = False
                return False
            return True

        # Latched OFF: enter on the time trigger or the high watermark.
        if self.ticks_since_consolidation >= self.time_interval:
            self.in_consolidation = True
            return True
        if active >= self.enter_pressure:
            self.in_consolidation = True
            return True
        return False

    def _active_anomalies_count(self) -> int:
        """Read ``active_anomalies_count`` from the telemetry source.

        Degrades gracefully to ``0`` if the summary is missing the key, so a
        slightly different telemetry shape never crashes the scheduler.
        """
        summary = self._telemetry.get_memory_summary()
        return int(summary.get("active_anomalies_count", 0))

    def reset(self) -> None:
        """End a consolidation cycle: clear the latch and arm the cooldown.

        Restarts the time clock, drops the Schmitt-trigger latch, and begins
        the strict ``cooldown`` refractory period during which no further
        trigger can fire.
        """
        self.ticks_since_consolidation = 0
        self.in_consolidation = False
        self._cooldown_remaining = self.cooldown


__all__ = ["MemoryScheduler"]

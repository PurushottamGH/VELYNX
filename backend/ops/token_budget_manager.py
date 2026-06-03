"""Token budget manager — enforces per-period token budgets."""
from __future__ import annotations

import logging
import time

from ops import TokenBudget

logger = logging.getLogger("uvicorn")


class TokenBudgetManager:
    """Tracks and enforces token usage budgets."""

    def __init__(
        self,
        hourly_limit: int = 100000,
        request_limit: int = 8000,
    ) -> None:
        self._hourly_limit = hourly_limit
        self._request_limit = request_limit
        self._hourly_used = 0
        self._hourly_start = time.time()
        self._total_used = 0

    def record_usage(self, tokens: int) -> None:
        """Record token usage from an LLM call."""
        self._hourly_used += tokens
        self._total_used += tokens

    def check_budget(self) -> TokenBudget:
        """Check current budget status."""
        self._maybe_reset_hourly()
        return TokenBudget(
            period="hour",
            limit=self._hourly_limit,
            used=self._hourly_used,
            remaining=max(0, self._hourly_limit - self._hourly_used),
        )

    def can_proceed(self, estimated_tokens: int = 4000) -> bool:
        """Check if a request can proceed within budget."""
        self._maybe_reset_hourly()
        return (self._hourly_used + estimated_tokens) <= self._hourly_limit

    def get_request_budget(self) -> TokenBudget:
        """Get per-request budget status."""
        return TokenBudget(
            period="request",
            limit=self._request_limit,
            used=0,
            remaining=self._request_limit,
        )

    def get_total_usage(self) -> int:
        """Get total tokens used this session."""
        return self._total_used

    def _maybe_reset_hourly(self) -> None:
        """Reset hourly counter if an hour has passed."""
        now = time.time()
        if now - self._hourly_start >= 3600:
            self._hourly_used = 0
            self._hourly_start = now

    def reset(self) -> None:
        """Reset all counters."""
        self._hourly_used = 0
        self._hourly_start = time.time()
        self._total_used = 0


# Module-level singleton
token_budget_manager = TokenBudgetManager()

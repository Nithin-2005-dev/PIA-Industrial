from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class RateLimitState:
    quota: int
    used: int = 0
    retries: int = 0
    circuit: CircuitState = CircuitState.CLOSED
    failures: int = 0


class RateLimiter:
    def __init__(
        self,
        quota: int = 1000,
        failure_threshold: int = 3,
    ):
        self._quota = quota
        self._failure_threshold = failure_threshold
        self._states: dict[str, RateLimitState] = {}

    def allow(
        self,
        adapter: str,
        cost: int = 1,
    ) -> bool:
        state = self._states.setdefault(
            adapter,
            RateLimitState(
                quota=self._quota,
            ),
        )
        if state.circuit == CircuitState.OPEN:
            return False
        return state.used + cost <= state.quota

    def record_success(
        self,
        adapter: str,
        cost: int = 1,
    ) -> None:
        state = self._states.setdefault(
            adapter,
            RateLimitState(
                quota=self._quota,
            ),
        )
        state.used += cost
        state.failures = 0
        state.circuit = CircuitState.CLOSED

    def record_failure(
        self,
        adapter: str,
    ) -> None:
        state = self._states.setdefault(
            adapter,
            RateLimitState(
                quota=self._quota,
            ),
        )
        state.failures += 1
        state.retries += 1
        if state.failures >= self._failure_threshold:
            state.circuit = CircuitState.OPEN

    def backoff_seconds(
        self,
        adapter: str,
    ) -> float:
        state = self._states.setdefault(
            adapter,
            RateLimitState(
                quota=self._quota,
            ),
        )
        return min(
            60.0,
            2.0 ** max(0, state.retries - 1),
        )

    def state(
        self,
        adapter: str,
    ) -> RateLimitState:
        return self._states.setdefault(
            adapter,
            RateLimitState(
                quota=self._quota,
            ),
        )


"""Distributed rate limiting with graceful Redis dependency degradation."""

from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass
from typing import Any

import structlog

_LUA_FIXED_WINDOW = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('PEXPIRE', KEYS[1], ARGV[1])
end
local ttl = redis.call('PTTL', KEYS[1])
if current > tonumber(ARGV[2]) then
  return {0, ttl}
end
return {1, ttl}
"""

logger = structlog.get_logger(__name__)


@dataclass
class RedisRateLimiter:
    url: str
    limit: int = 120
    window_seconds: float = 60.0
    key_prefix: str = "fake-news:ratelimit:"
    failure_threshold: int = 3
    recovery_timeout_seconds: float = 30.0

    def __post_init__(self) -> None:
        if (
            not self.url
            or self.limit < 1
            or self.window_seconds <= 0.0
            or self.failure_threshold < 1
            or self.recovery_timeout_seconds <= 0.0
        ):
            raise ValueError("Redis rate limiter settings must be valid")
        try:
            import redis.asyncio as redis
            from redis.exceptions import ConnectionError as RedisConnectionError
            from redis.exceptions import RedisError
            from redis.exceptions import TimeoutError as RedisTimeoutError
        except ImportError as exc:
            raise RuntimeError("redis package is required for distributed rate limiting") from exc
        self._redis: Any = redis.from_url(self.url, decode_responses=False)  # type: ignore[no-untyped-call]
        self._redis_error_types: tuple[type[BaseException], ...] = (
            RedisError,
            RedisConnectionError,
            RedisTimeoutError,
            TimeoutError,
            OSError,
        )
        self._state = "closed"
        self._failure_count = 0
        self._opened_at = 0.0
        self._half_open_probe = False
        self._state_lock = asyncio.Lock()

    @property
    def circuit_state(self) -> str:
        """Return the safe circuit state without exposing Redis connection details."""
        return self._state

    async def _probe_allowed(self) -> bool:
        async with self._state_lock:
            if self._state == "closed":
                return True
            if self._state == "open":
                if time.monotonic() - self._opened_at < self.recovery_timeout_seconds:
                    return False
                if self._half_open_probe:
                    return False
                self._state = "half_open"
                self._half_open_probe = True
                logger.info("redis_rate_limiter_circuit_half_open")
                return True
            return not self._half_open_probe

    async def _record_success(self) -> None:
        async with self._state_lock:
            previous = self._state
            self._failure_count = 0
            self._state = "closed"
            self._opened_at = 0.0
            self._half_open_probe = False
            if previous == "half_open":
                logger.info("redis_rate_limiter_circuit_closed")

    async def _record_failure(self, error: BaseException) -> None:
        async with self._state_lock:
            self._failure_count += 1
            self._half_open_probe = False
            if self._state == "half_open" or self._failure_count >= self.failure_threshold:
                previous = self._state
                self._state = "open"
                self._opened_at = time.monotonic()
                if previous != "open":
                    logger.critical(
                        "redis_rate_limiter_circuit_open",
                        failure_threshold=self.failure_threshold,
                        exception_type=type(error).__name__,
                    )
            else:
                logger.warning(
                    "redis_rate_limiter_failure",
                    failure_count=self._failure_count,
                    failure_threshold=self.failure_threshold,
                    exception_type=type(error).__name__,
                )

    async def check_async(self, client_key: str) -> tuple[bool, int]:
        if not await self._probe_allowed():
            return True, 0
        key = f"{self.key_prefix}{client_key}".encode("utf-8", errors="replace")
        try:
            result = await self._redis.eval(
                _LUA_FIXED_WINDOW,
                1,
                key,
                str(int(self.window_seconds * 1000)),
                str(self.limit),
            )
        except self._redis_error_types as exc:
            await self._record_failure(exc)
            return True, 0
        await self._record_success()
        allowed = bool(int(result[0]))
        retry_after = max(1, int((int(result[1]) + 999) // 1000))
        return allowed, 0 if allowed else retry_after

    async def close(self) -> None:
        try:
            await self._redis.aclose()
        except Exception as exc:
            logger.warning("redis_rate_limiter_close_failed", exception_type=type(exc).__name__)


def redis_is_configured() -> bool:
    """Return true only when the explicit distributed limiter mode is selected."""
    return os.getenv("DISTRIBUTED_RATE_LIMITER", "").strip().lower() == "redis" and bool(os.getenv("REDIS_URL", "").strip())

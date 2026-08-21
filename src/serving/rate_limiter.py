"""Distributed rate limiting for multi-worker serving.

The Lua script performs increment, expiry, and rejection atomically in Redis.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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


@dataclass
class RedisRateLimiter:
    url: str
    limit: int = 120
    window_seconds: float = 60.0
    key_prefix: str = "fake-news:ratelimit:"

    def __post_init__(self) -> None:
        if not self.url or self.limit < 1 or self.window_seconds <= 0.0:
            raise ValueError("Redis rate limiter settings must be valid")
        try:
            import redis.asyncio as redis
        except ImportError as exc:
            raise RuntimeError("redis package is required for distributed rate limiting") from exc
        self._redis: Any = redis.from_url(self.url, decode_responses=False)  # type: ignore[no-untyped-call]

    async def check_async(self, client_key: str) -> tuple[bool, int]:
        key = f"{self.key_prefix}{client_key}".encode("utf-8", errors="replace")
        result = await self._redis.eval(
            _LUA_FIXED_WINDOW,
            1,
            key,
            str(int(self.window_seconds * 1000)),
            str(self.limit),
        )
        allowed = bool(int(result[0]))
        retry_after = max(1, int((int(result[1]) + 999) // 1000))
        return allowed, 0 if allowed else retry_after

    async def close(self) -> None:
        await self._redis.aclose()


def redis_is_configured() -> bool:
    """Return true only when the explicit distributed limiter mode is selected."""
    import os

    return os.getenv("DISTRIBUTED_RATE_LIMITER", "").strip().lower() == "redis" and bool(os.getenv("REDIS_URL", "").strip())

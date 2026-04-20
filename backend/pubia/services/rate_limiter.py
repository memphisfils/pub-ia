from __future__ import annotations

import time

from pubia.config import build_config

RATE_LIMITS: dict[str, dict[str, int]] = {
    "free":       {"per_minute": 60,    "per_day": 10_000},
    "starter":    {"per_minute": 200,   "per_day": 50_000},
    "pro":        {"per_minute": 500,   "per_day": 200_000},
    "business":   {"per_minute": 2000,  "per_day": 1_000_000},
    "enterprise": {"per_minute": -1,    "per_day": -1},  # unlimited
}

DEFAULT_LIMITS = RATE_LIMITS["free"]


class RateLimiter:
    def __init__(self, redis_client) -> None:
        self._redis = redis_client

    def _minute_key(self, api_key: str) -> str:
        minute = int(time.time() // 60)
        return f"ratelimit:{api_key}:minute:{minute}"

    def _day_key(self, api_key: str) -> str:
        day = int(time.time() // 86400)
        return f"ratelimit:{api_key}:day:{day}"

    def _get_limits(self, api_key: str) -> tuple[int, int]:
        """Get limits based on plan. Default to free plan."""
        # In production, look up the publisher's plan from DB
        # For MVP, use free plan limits
        limits = RATE_LIMITS.get("free", DEFAULT_LIMITS)
        return limits["per_minute"], limits["per_day"]

    def is_allowed(self, api_key: str) -> tuple[bool, dict[str, int]]:
        """
        Check if API key is within rate limits.
        Returns (allowed, info) where info contains current counts.
        """
        per_minute, per_day = self._get_limits(api_key)
        minute_key = self._minute_key(api_key)
        day_key = self._day_key(api_key)

        if per_minute == -1 and per_day == -1:
            return True, {"minute_count": 0, "day_count": 0}

        pipe = self._redis.client.pipeline()

        # Increment counters
        pipe.incr(minute_key)
        pipe.expire(minute_key, 120)  # Keep for 2 minutes
        pipe.incr(day_key)
        pipe.expire(day_key, 86400 + 60)  # Keep for a day + 1 minute

        results = pipe.execute()
        minute_count = results[0]
        day_count = results[2]

        allowed = True
        if per_minute > 0 and minute_count > per_minute:
            allowed = False
        if per_day > 0 and day_count > per_day:
            allowed = False

        return allowed, {
            "minute_count": minute_count,
            "day_count": day_count,
            "limit_minute": per_minute,
            "limit_day": per_day,
        }

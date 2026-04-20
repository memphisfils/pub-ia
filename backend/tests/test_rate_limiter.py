"""Tests pour le service rate_limiter."""
from unittest.mock import MagicMock

from pubia.services.rate_limiter import RateLimiter, RATE_LIMITS


class FakeRedisPipeline:
    """Simule un pipeline Redis."""

    def __init__(self, counts=None):
        self._counts = counts or [1, None, 1, None, None]
        self._operations = []

    def incr(self, key):
        self._operations.append(("incr", key))
        return self

    def expire(self, key, ttl):
        self._operations.append(("expire", key, ttl))
        return self

    def execute(self):
        return self._counts


class FakeRedisClient:
    """Simule un client Redis."""

    def __init__(self, pipeline_results=None):
        self._pipeline_results = pipeline_results

    def pipeline(self):
        return FakeRedisPipeline(self._pipeline_results)


def test_rate_limiter_allows_within_minute_limit() -> None:
    """Un compteur sous la limite doit être autorisé."""
    fake_redis = FakeRedisClient(pipeline_results=[5, None, 100, None, None])
    limiter = RateLimiter(fake_redis)

    allowed, info = limiter.is_allowed("pk_test_xxx")

    assert allowed is True
    assert info["minute_count"] == 5
    assert info["day_count"] == 100


def test_rate_limiter_blocks_over_minute_limit() -> None:
    """Un compteur au-dessus de la limite minute doit être bloqué."""
    # Limite free = 60/min, on simule 61 requêtes
    fake_redis = FakeRedisClient(pipeline_results=[61, None, 100, None, None])
    limiter = RateLimiter(fake_redis)

    allowed, info = limiter.is_allowed("pk_test_xxx")

    assert allowed is False
    assert info["minute_count"] == 61


def test_rate_limiter_blocks_over_day_limit() -> None:
    """Un compteur au-dessus de la limite journalière doit être bloqué."""
    # Limite free = 10_000/jour
    fake_redis = FakeRedisClient(pipeline_results=[5, None, 10001, None, None])
    limiter = RateLimiter(fake_redis)

    allowed, info = limiter.is_allowed("pk_test_xxx")

    assert allowed is False
    assert info["day_count"] == 10001


def test_rate_limiter_enterprise_unlimited() -> None:
    """Le plan enterprise n'a pas de limites."""
    # Pour enterprise, les limites sont -1
    fake_redis = FakeRedisClient(pipeline_results=[999999, None, 999999, None, None])
    limiter = RateLimiter(fake_redis)

    # On mock la méthode _get_limits pour retourner enterprise
    limiter._get_limits = lambda key: (-1, -1)

    allowed, info = limiter.is_allowed("pk_test_xxx")

    assert allowed is True


def test_rate_limiter_key_format_minute() -> None:
    """La clé minute doit contenir le timestamp de la minute."""
    fake_redis = FakeRedisClient(pipeline_results=[1, None, 1, None, None])
    limiter = RateLimiter(fake_redis)

    key = limiter._minute_key("pk_test_xxx")

    assert key.startswith("ratelimit:pk_test_xxx:minute:")


def test_rate_limiter_key_format_day() -> None:
    """La clé jour doit contenir le timestamp du jour."""
    fake_redis = FakeRedisClient(pipeline_results=[1, None, 1, None, None])
    limiter = RateLimiter(fake_redis)

    key = limiter._day_key("pk_test_xxx")

    assert key.startswith("ratelimit:pk_test_xxx:day:")

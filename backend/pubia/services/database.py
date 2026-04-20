"""Database and Redis clients for Pub-IA services."""
from __future__ import annotations

from dataclasses import asdict, dataclass

from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


@dataclass(slots=True)
class ServiceCheck:
    status: str
    detail: str


class DatabaseClient:
    """Database client with connection pooling."""

    def __init__(self, url: str | None) -> None:
        self._url = url
        self._engine: Engine | None = None

    def ping(self) -> dict[str, str]:
        if not self._url:
            return asdict(ServiceCheck("skipped", "DATABASE_URL is not configured."))

        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            return asdict(
                ServiceCheck("error", f"database connection failed: {exc.__class__.__name__}"),
            )

        return asdict(ServiceCheck("ok", "database reachable"))

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            self._engine = create_engine(self._url, pool_pre_ping=True)
        return self._engine

    def close(self) -> None:
        if self._engine is not None:
            self._engine.dispose()


class RedisClient:
    """Redis client for caching and rate limiting."""

    def __init__(self, url: str | None) -> None:
        self._url = url
        self._client: Redis | None = None

    def ping(self) -> dict[str, str]:
        if not self._url:
            return asdict(ServiceCheck("skipped", "REDIS_URL is not configured."))

        try:
            self.client.ping()
        except RedisError as exc:
            return asdict(
                ServiceCheck("error", f"redis connection failed: {exc.__class__.__name__}"),
            )

        return asdict(ServiceCheck("ok", "redis reachable"))

    @property
    def client(self) -> Redis:
        if self._client is None:
            self._client = Redis.from_url(
                self._url,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
        return self._client

    def close(self) -> None:
        if self._client is not None:
            self._client.close()

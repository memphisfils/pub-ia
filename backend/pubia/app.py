from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from flask import Flask

from pubia.config import DEFAULT_SECRET_KEY, build_config
from pubia.routes import register_routes
from pubia.services import (
    DatabaseClient,
    RedisClient,
    IntentClassifier,
    AdSelector,
    RateLimiter,
)


def create_app(
    config_overrides: Mapping[str, Any] | None = None,
    service_overrides: Mapping[str, Any] | None = None,
) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(build_config())

    if config_overrides:
        app.config.from_mapping(config_overrides)

    _validate_runtime_config(app)
    _register_services(app, service_overrides)
    register_routes(app)
    return app


def _validate_runtime_config(app: Flask) -> None:
    # Utiliser app.config["DEBUG"] et app.config["TESTING"] au lieu de app.debug/app.testing
    # car ces propriétés peuvent ne pas être encore définies
    if app.config.get("DEBUG") or app.config.get("TESTING"):
        return

    if app.config["SECRET_KEY"] == DEFAULT_SECRET_KEY:
        raise RuntimeError("SECRET_KEY must be set for non-debug runtimes.")

    missing_settings = [
        setting for setting in ("DATABASE_URL", "REDIS_URL") if not app.config.get(setting)
    ]
    if missing_settings:
        missing = ", ".join(missing_settings)
        raise RuntimeError(
            f"Missing required runtime settings for non-debug runtimes: {missing}.",
        )


def _register_services(
    app: Flask,
    service_overrides: Mapping[str, Any] | None,
) -> None:
    overrides = dict(service_overrides or {})

    app.extensions["pubia.database"] = overrides.get(
        "database",
        DatabaseClient(app.config.get("DATABASE_URL")),
    )
    app.extensions["pubia.redis"] = overrides.get(
        "redis",
        RedisClient(app.config.get("REDIS_URL")),
    )

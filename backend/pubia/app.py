from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from flask import Flask, request

from pubia.config import DEFAULT_SECRET_KEY, build_config
from pubia.routes.auth import init_auth
from pubia.routes import register_routes
from pubia.services import DatabaseClient, RedisClient


def create_app(
    config_overrides: Mapping[str, Any] | None = None,
    service_overrides: Mapping[str, Any] | None = None,
) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(build_config())

    if config_overrides:
        app.config.from_mapping(config_overrides)

    _validate_runtime_config(app)
    _configure_cors(app)
    _register_services(app, service_overrides)
    init_auth(app)
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


def _configure_cors(app: Flask) -> None:
    configured_origin = app.config.get("FRONTEND_URL")
    allowed_origins = {
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    }
    if configured_origin:
        allowed_origins.add(configured_origin.rstrip("/"))

    @app.after_request
    def add_cors_headers(response):  # type: ignore[no-untyped-def]
        origin = request.headers.get("Origin")
        if origin and origin.rstrip("/") in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = (
                "Authorization, Content-Type"
            )
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            )
        return response

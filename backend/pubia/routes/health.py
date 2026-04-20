from __future__ import annotations

from typing import Any

from flask import Blueprint, current_app, jsonify

health = Blueprint("health", __name__)


@health.get("/health")
def healthcheck() -> tuple[Any, int]:
    db_status = current_app.extensions["pubia.database"].ping()["status"]
    redis_status = current_app.extensions["pubia.redis"].ping()["status"]
    return jsonify({
        "status": "ok",
        "db": db_status,
        "redis": redis_status,
    }), 200

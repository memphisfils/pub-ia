from __future__ import annotations

from flask import Flask

from pubia.routes.health import health
from pubia.routes.sdk import sdk
from pubia.routes.auth import auth
from pubia.routes.publisher import publisher
from pubia.routes.advertiser import advertiser
from pubia.routes.admin import admin


def register_routes(app: Flask) -> None:
    """Register all blueprints on the Flask app."""
    app.register_blueprint(health)
    app.register_blueprint(sdk)
    app.register_blueprint(auth)
    app.register_blueprint(publisher)
    app.register_blueprint(advertiser)
    app.register_blueprint(admin)

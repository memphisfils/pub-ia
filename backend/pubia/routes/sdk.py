from __future__ import annotations

import uuid
from typing import Any

from flask import Blueprint, current_app, g, jsonify, request

from pubia.models import PublisherApp
from pubia.services import (
    IntentClassifier,
    AdSelector,
    RateLimiter,
)

sdk = Blueprint("sdk", __name__, url_prefix="/v1")


def _get_sdk_db():
    """Get a DB session for SDK routes."""
    from sqlalchemy.orm import Session
    from pubia.services import DatabaseClient
    db_client: DatabaseClient = current_app.extensions["pubia.database"]
    session = Session(bind=db_client.engine)
    try:
        yield session
    finally:
        session.close()


def _authenticate_api_key() -> PublisherApp | None:
    """Authenticate request using Bearer API key."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:]
    if not token:
        return None

    from sqlalchemy import select
    db_client = current_app.extensions["pubia.database"]
    from sqlalchemy.orm import Session
    session = Session(bind=db_client.engine)
    try:
        stmt = select(PublisherApp).where(
            PublisherApp.api_key == token,
            PublisherApp.is_active == True,  # noqa: E712
        )
        return session.execute(stmt).scalars().first()
    finally:
        session.close()


@sdk.before_request
def before_request() -> None:
    """Authenticate all SDK requests."""
    g.sdk_app = _authenticate_api_key()
    if g.sdk_app is None:
        return jsonify({"error": "Invalid or missing API key"}), 401


@sdk.route("/analyze-intent", methods=["POST"])
def analyze_intent() -> tuple[Any, int]:
    """
    POST /v1/analyze-intent
    Authorization: Bearer pk_live_xxx
    Body: {"prompt": "...", "context?": "..."}
    """
    body = request.get_json() or {}
    prompt = body.get("prompt")
    if not prompt or not isinstance(prompt, str):
        return jsonify({"error": "prompt is required"}), 400
    if len(prompt) > 10000:
        return jsonify({"error": "prompt too long (max 10000 chars)"}), 400

    context = body.get("context")

    # Rate limiting
    redis_client = current_app.extensions["pubia.redis"]
    rate_limiter = RateLimiter(redis_client)
    allowed, info = rate_limiter.is_allowed(g.sdk_app.api_key)
    if not allowed:
        return jsonify({
            "error": "Rate limit exceeded",
            "limit_minute": info["limit_minute"],
            "limit_day": info["limit_day"],
        }), 429

    # Intent classification
    classifier = IntentClassifier(redis_client=redis_client)
    result = classifier.classify(prompt, context)

    resp = {
        "has_intent": result.has_intent,
        "intent": result.intent,
        "confidence": result.confidence,
        "category": result.category,
        "intent_id": result.intent_id,
    }
    return jsonify(resp), 200


@sdk.route("/get-ad", methods=["POST"])
def get_ad() -> tuple[Any, int]:
    """
    POST /v1/get-ad
    Authorization: Bearer pk_live_xxx
    Body: {"intent": "...", "intent_id": "...", "confidence": 0.87}
    """
    body = request.get_json() or {}
    intent = body.get("intent")
    intent_id = body.get("intent_id")
    confidence = body.get("confidence", 0.0)

    if not intent or not isinstance(intent, str):
        return jsonify({"error": "intent is required"}), 400

    # Rate limiting
    redis_client = current_app.extensions["pubia.redis"]
    rate_limiter = RateLimiter(redis_client)
    allowed, _ = rate_limiter.is_allowed(g.sdk_app.api_key)
    if not allowed:
        return "", 204

    # Get DB session
    from sqlalchemy.orm import Session
    db_client: DatabaseClient = current_app.extensions["pubia.database"]
    session = Session(bind=db_client.engine)
    try:
        selector = AdSelector(session)
        ad = selector.select_ad(
            intent_category=intent,
            intent_confidence=float(confidence),
            app_id=str(g.sdk_app.id),
        )
        if ad is None:
            return "", 204

        return jsonify({
            "ad_id": ad.ad_id,
            "headline": ad.headline,
            "body": ad.body,
            "cta_text": ad.cta_text,
            "cta_url": ad.cta_url,
            "native_text": ad.native_text,
            "impression_id": ad.impression_id,
        }), 200
    finally:
        session.close()


@sdk.route("/track-click", methods=["POST"])
def track_click() -> tuple[Any, int]:
    """
    POST /v1/track-click
    Authorization: Bearer pk_live_xxx
    Body: {"impression_id": "..."}
    """
    body = request.get_json() or {}
    impression_id = body.get("impression_id")
    if not impression_id:
        return jsonify({"error": "impression_id is required"}), 400

    from sqlalchemy.orm import Session
    db_client: DatabaseClient = current_app.extensions["pubia.database"]
    session = Session(bind=db_client.engine)
    try:
        selector = AdSelector(session)
        tracked = selector.track_click(impression_id)
        return jsonify({"tracked": tracked}), 200
    finally:
        session.close()

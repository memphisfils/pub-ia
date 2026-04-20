from __future__ import annotations

import secrets
from typing import Any

from flask import Blueprint, current_app, jsonify, request, session

from pubia.models import PublisherApp

publisher = Blueprint("publisher", __name__, url_prefix="/api/publisher")


def _require_login():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    return None


def _get_db_session():
    from sqlalchemy.orm import Session
    from pubia.services import DatabaseClient
    db_client: DatabaseClient = current_app.extensions["pubia.database"]
    return Session(bind=db_client.engine)


@publisher.route("/apps", methods=["GET"])
def list_apps() -> tuple[Any, int]:
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    db = _get_db_session()
    try:
        from sqlalchemy import select
        stmt = select(PublisherApp).where(PublisherApp.user_id == user_id)
        apps = db.execute(stmt).scalars().all()
        return jsonify([{
            "id": str(a.id),
            "name": a.name,
            "description": a.description,
            "website_url": a.website_url,
            "api_key": a.api_key,
            "is_active": a.is_active,
            "created_at": a.created_at.isoformat(),
        } for a in apps]), 200
    finally:
        db.close()


@publisher.route("/apps", methods=["POST"])
def create_app() -> tuple[Any, int]:
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    body = request.get_json() or {}
    name = body.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400

    db = _get_db_session()
    try:
        app = PublisherApp(
            user_id=user_id,
            name=name,
            description=body.get("description"),
            website_url=body.get("website_url"),
            api_key=f"pk_live_{secrets.token_hex(28)}",
        )
        db.add(app)
        db.commit()
        return jsonify({
            "id": str(app.id),
            "name": app.name,
            "description": app.description,
            "website_url": app.website_url,
            "api_key": app.api_key,
            "is_active": app.is_active,
            "created_at": app.created_at.isoformat(),
        }), 201
    finally:
        db.close()


@publisher.route("/apps/<app_id>", methods=["GET"])
def get_app(app_id: str) -> tuple[Any, int]:
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    db = _get_db_session()
    try:
        from sqlalchemy import select
        stmt = select(PublisherApp).where(
            PublisherApp.id == app_id,
            PublisherApp.user_id == user_id,
        )
        app = db.execute(stmt).scalars().first()
        if not app:
            return jsonify({"error": "Not found"}), 404
        return jsonify({
            "id": str(app.id),
            "name": app.name,
            "description": app.description,
            "website_url": app.website_url,
            "api_key": app.api_key,
            "is_active": app.is_active,
            "created_at": app.created_at.isoformat(),
        }), 200
    finally:
        db.close()


@publisher.route("/apps/<app_id>", methods=["PUT"])
def update_app(app_id: str) -> tuple[Any, int]:
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    body = request.get_json() or {}
    db = _get_db_session()
    try:
        from sqlalchemy import select
        stmt = select(PublisherApp).where(
            PublisherApp.id == app_id,
            PublisherApp.user_id == user_id,
        )
        app = db.execute(stmt).scalars().first()
        if not app:
            return jsonify({"error": "Not found"}), 404

        if "name" in body:
            app.name = body["name"]
        if "description" in body:
            app.description = body["description"]
        if "website_url" in body:
            app.website_url = body["website_url"]
        if "is_active" in body:
            app.is_active = body["is_active"]
        db.commit()
        return jsonify({
            "id": str(app.id),
            "name": app.name,
            "description": app.description,
            "website_url": app.website_url,
            "api_key": app.api_key,
            "is_active": app.is_active,
            "created_at": app.created_at.isoformat(),
        }), 200
    finally:
        db.close()


@publisher.route("/apps/<app_id>/regenerate-key", methods=["POST"])
def regenerate_key(app_id: str) -> tuple[Any, int]:
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    db = _get_db_session()
    try:
        from sqlalchemy import select
        stmt = select(PublisherApp).where(
            PublisherApp.id == app_id,
            PublisherApp.user_id == user_id,
        )
        app = db.execute(stmt).scalars().first()
        if not app:
            return jsonify({"error": "Not found"}), 404
        app.api_key = f"pk_live_{secrets.token_hex(28)}"
        db.commit()
        return jsonify({"api_key": app.api_key}), 200
    finally:
        db.close()


@publisher.route("/analytics", methods=["GET"])
def analytics() -> tuple[Any, int]:
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    db = _get_db_session()
    try:
        from sqlalchemy import select, func
        from pubia.models import Impression, PublisherApp

        # Get all apps for user
        apps_stmt = select(PublisherApp.id).where(PublisherApp.user_id == user_id)
        app_ids = list(db.execute(apps_stmt).scalars().all())

        if not app_ids:
            return jsonify({"impressions": 0, "revenue": 0, "ecpm": 0}), 200

        # Total impressions
        imp_stmt = select(func.count(Impression.id)).where(
            Impression.app_id.in_(app_ids)
        )
        total_impressions = db.execute(imp_stmt).scalar() or 0

        # Total revenue (publisher share)
        rev_stmt = select(func.sum(Impression.publisher_share)).where(
            Impression.app_id.in_(app_ids)
        )
        total_revenue = db.execute(rev_stmt).scalar() or 0

        from decimal import Decimal
        ecpm = float(total_revenue) / float(total_impressions) * 1000 if total_impressions > 0 else 0

        return jsonify({
            "impressions": total_impressions,
            "revenue": float(total_revenue),
            "ecpm": round(ecpm, 4),
        }), 200
    finally:
        db.close()


@publisher.route("/analytics/daily", methods=["GET"])
def analytics_daily() -> tuple[Any, int]:
    """Données jour par jour sur les 30 derniers jours."""
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    db = _get_db_session()
    try:
        from sqlalchemy import select, func, text
        from datetime import datetime, timedelta
        from pubia.models import Impression, PublisherApp

        # Récupérer les app_ids du user
        apps_stmt = select(PublisherApp.id).where(PublisherApp.user_id == user_id)
        app_ids = list(db.execute(apps_stmt).scalars().all())

        if not app_ids:
            return jsonify({"data": []}), 200

        # Requête SQL pour regrouper par jour (30 derniers jours)
        # Note: PostgreSQL utilise DATE() pour extraire la date
        query = text("""
            SELECT 
                DATE(created_at) as day,
                COUNT(*) as impressions,
                SUM(publisher_share) as revenue,
                SUM(CASE WHEN clicked THEN 1 ELSE 0 END) as clicks
            FROM impressions
            WHERE app_id = ANY(:app_ids)
              AND created_at >= :start_date
            GROUP BY DATE(created_at)
            ORDER BY day ASC
        """)

        start_date = (datetime.now() - timedelta(days=30)).date()
        result = db.execute(query, {"app_ids": app_ids, "start_date": start_date})
        rows = result.fetchall()

        data = []
        for row in rows:
            day_data = {
                "day": row[0].isoformat(),
                "impressions": int(row[1]),
                "revenue": float(row[2]) if row[2] else 0.0,
                "clicks": int(row[3]),
            }
            # Calculer le CTR
            day_data["ctr"] = (
                round(day_data["clicks"] / day_data["impressions"] * 100, 2)
                if day_data["impressions"] > 0
                else 0
            )
            data.append(day_data)

        return jsonify({"data": data}), 200
    finally:
        db.close()


@publisher.route("/analytics/by-category", methods=["GET"])
def analytics_by_category() -> tuple[Any, int]:
    """Revenus et impressions par catégorie d'intention."""
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    db = _get_db_session()
    try:
        from sqlalchemy import select, func
        from pubia.models import Impression, PublisherApp, Campaign

        # Récupérer les app_ids du user
        apps_stmt = select(PublisherApp.id).where(PublisherApp.user_id == user_id)
        app_ids = list(db.execute(apps_stmt).scalars().all())

        if not app_ids:
            return jsonify({"data": []}), 200

        # Joindre impressions avec campaigns pour obtenir la catégorie
        stmt = (
            select(
                Campaign.category,
                func.count(Impression.id).label("impressions"),
                func.sum(Impression.publisher_share).label("revenue"),
                func.sum(Impression.clicked.cast(int)).label("clicks"),
            )
            .join(Campaign, Campaign.id == Impression.campaign_id)
            .where(Impression.app_id.in_(app_ids))
            .group_by(Campaign.category)
            .order_by(func.sum(Impression.publisher_share).desc())
        )

        results = db.execute(stmt).fetchall()

        data = []
        for row in results:
            category_data = {
                "category": row[0],
                "impressions": int(row[1]),
                "revenue": float(row[2]) if row[2] else 0.0,
                "clicks": int(row[3]) if row[3] else 0,
            }
            # Calculer le CTR et l'eCPM
            category_data["ctr"] = (
                round(category_data["clicks"] / category_data["impressions"] * 100, 2)
                if category_data["impressions"] > 0
                else 0
            )
            category_data["ecpm"] = (
                round(category_data["revenue"] / category_data["impressions"] * 1000, 2)
                if category_data["impressions"] > 0
                else 0
            )
            data.append(category_data)

        return jsonify({"data": data}), 200
    finally:
        db.close()


@publisher.route("/revenue", methods=["GET"])
def revenue() -> tuple[Any, int]:
    """Solde actuel du publisher et historique des revenus."""
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    db = _get_db_session()
    try:
        from sqlalchemy import select, func
        from pubia.models import Impression, PublisherApp
        from pubia.config import build_config

        # Récupérer les app_ids du user
        apps_stmt = select(PublisherApp.id).where(PublisherApp.user_id == user_id)
        app_ids = list(db.execute(apps_stmt).scalars().all())

        if not app_ids:
            return jsonify({
                "balance": 0.0,
                "total_earned": 0.0,
                "pending_payout": 0.0,
                "min_payout": build_config().get("PUBIA_MIN_PAYOUT", 50.00),
                "history": [],
            }), 200

        # Calculer le solde total (somme des publisher_share)
        balance_stmt = select(func.sum(Impression.publisher_share)).where(
            Impression.app_id.in_(app_ids)
        )
        total_earned = db.execute(balance_stmt).scalar() or 0

        # Historique des revenus par jour (30 derniers jours)
        from datetime import datetime, timedelta
        from sqlalchemy import text

        start_date = (datetime.now() - timedelta(days=30)).date()
        history_query = text("""
            SELECT 
                DATE(created_at) as day,
                SUM(publisher_share) as daily_revenue,
                COUNT(*) as impressions
            FROM impressions
            WHERE app_id = ANY(:app_ids)
              AND created_at >= :start_date
            GROUP BY DATE(created_at)
            ORDER BY day DESC
            LIMIT 30
        """)

        result = db.execute(history_query, {"app_ids": app_ids, "start_date": start_date})
        rows = result.fetchall()

        history = []
        for row in rows:
            history.append({
                "day": row[0].isoformat(),
                "revenue": float(row[1]) if row[1] else 0.0,
                "impressions": int(row[2]),
            })

        # Calculer le seuil minimum de paiement
        min_payout = build_config().get("PUBIA_MIN_PAYOUT", 50.00)

        # Le pending_payout est le solde non encore versé
        # (dans un vrai système, on suivrait les paiements effectués)
        pending_payout = float(total_earned)

        return jsonify({
            "balance": float(total_earned),
            "total_earned": float(total_earned),
            "pending_payout": round(pending_payout, 2),
            "min_payout": min_payout,
            "can_payout": pending_payout >= min_payout,
            "history": history,
        }), 200
    finally:
        db.close()

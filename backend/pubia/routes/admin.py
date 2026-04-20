from __future__ import annotations

from typing import Any

from flask import Blueprint, current_app, jsonify, session

admin = Blueprint("admin", __name__, url_prefix="/api/admin")


def _require_admin():
    role = session.get("user_role")
    if role != "admin":
        return jsonify({"error": "Admin access required"}), 403
    return None


@admin.route("/stats")
def stats() -> tuple[Any, int]:
    """Statistiques globales pour l'admin."""
    err = _require_admin()
    if err:
        return err

    from sqlalchemy.orm import Session
    from sqlalchemy import select, func
    from pubia.models import User, Campaign, Impression, PublisherApp, AdCreative
    from pubia.services import DatabaseClient

    db_client: DatabaseClient = current_app.extensions["pubia.database"]
    session_db = Session(bind=db_client.engine)
    try:
        # Counts de base
        total_users = session_db.execute(select(func.count(User.id))).scalar() or 0
        total_publishers = session_db.execute(
            select(func.count(User.id)).where(User.role == "publisher")
        ).scalar() or 0
        total_advertisers = session_db.execute(
            select(func.count(User.id)).where(User.role == "advertiser")
        ).scalar() or 0
        
        total_campaigns = session_db.execute(select(func.count(Campaign.id))).scalar() or 0
        active_campaigns = session_db.execute(
            select(func.count(Campaign.id)).where(Campaign.status == "active")
        ).scalar() or 0
        
        total_impressions = session_db.execute(select(func.count(Impression.id))).scalar() or 0
        total_clicks = session_db.execute(
            select(func.count(Impression.id)).where(Impression.clicked == True)  # noqa: E712
        ).scalar() or 0

        # Revenu total (somme des cpm_charged)
        from sqlalchemy import func as sql_func
        total_revenue_stmt = select(sql_func.sum(Impression.cpm_charged))
        total_revenue = session_db.execute(total_revenue_stmt).scalar() or 0

        # Part publisher totale
        total_publisher_share_stmt = select(sql_func.sum(Impression.publisher_share))
        total_publisher_share = session_db.execute(total_publisher_share_stmt).scalar() or 0

        # Part Pub-IA (30%)
        pubia_revenue = float(total_revenue) - float(total_publisher_share)

        # Nombre d'apps publisher actives
        total_apps = session_db.execute(
            select(func.count(PublisherApp.id)).where(PublisherApp.is_active == True)  # noqa: E712
        ).scalar() or 0

        # Nombre de creatives actives
        total_creatives = session_db.execute(
            select(func.count(AdCreative.id)).where(AdCreative.is_active == True)  # noqa: E712
        ).scalar() or 0

        # CTR global
        ctr = round(total_clicks / total_impressions * 100, 2) if total_impressions > 0 else 0

        return jsonify({
            "users": {
                "total": total_users,
                "publishers": total_publishers,
                "advertisers": total_advertisers,
            },
            "campaigns": {
                "total": total_campaigns,
                "active": active_campaigns,
            },
            "impressions": {
                "total": total_impressions,
                "clicks": total_clicks,
                "ctr": ctr,
            },
            "revenue": {
                "total_cpm": round(float(total_revenue), 2),
                "publisher_share": round(float(total_publisher_share), 2),
                "pubia_revenue": round(pubia_revenue, 2),
            },
            "apps": {
                "active": total_apps,
            },
            "creatives": {
                "active": total_creatives,
            },
        }), 200
    finally:
        session_db.close()

from __future__ import annotations

from typing import Any
from decimal import Decimal

from flask import Blueprint, current_app, jsonify, request, session

from pubia.models import Campaign, AdCreative

advertiser = Blueprint("advertiser", __name__, url_prefix="/api/advertiser")


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


@advertiser.route("/campaigns", methods=["GET"])
def list_campaigns() -> tuple[Any, int]:
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    db = _get_db_session()
    try:
        from sqlalchemy import select
        stmt = select(Campaign).where(Campaign.user_id == user_id)
        campaigns = db.execute(stmt).scalars().all()
        return jsonify([{
            "id": str(c.id),
            "name": c.name,
            "status": c.status,
            "category": c.category,
            "budget_total": float(c.budget_total),
            "budget_spent": float(c.budget_spent),
            "bid_cpm": float(c.bid_cpm) if c.bid_cpm else None,
            "bid_cpc": float(c.bid_cpc) if c.bid_cpc else None,
            "start_date": c.start_date.isoformat() if c.start_date else None,
            "end_date": c.end_date.isoformat() if c.end_date else None,
            "created_at": c.created_at.isoformat(),
        } for c in campaigns]), 200
    finally:
        db.close()


@advertiser.route("/campaigns", methods=["POST"])
def create_campaign() -> tuple[Any, int]:
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    body = request.get_json() or {}
    name = body.get("name")
    category = body.get("category")
    if not name or not category:
        return jsonify({"error": "name and category are required"}), 400

    db = _get_db_session()
    try:
        campaign = Campaign(
            user_id=user_id,
            name=name,
            category=category,
            status="draft",
            budget_total=Decimal(str(body.get("budget_total", 0))),
            bid_cpm=Decimal(str(body["bid_cpm"])) if body.get("bid_cpm") else None,
            bid_cpc=Decimal(str(body["bid_cpc"])) if body.get("bid_cpc") else None,
            start_date=body.get("start_date"),
            end_date=body.get("end_date"),
        )
        db.add(campaign)
        db.commit()
        return jsonify({
            "id": str(campaign.id),
            "name": campaign.name,
            "status": campaign.status,
            "category": campaign.category,
        }), 201
    finally:
        db.close()


@advertiser.route("/campaigns/<campaign_id>", methods=["GET"])
def get_campaign(campaign_id: str) -> tuple[Any, int]:
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    db = _get_db_session()
    try:
        from sqlalchemy import select
        stmt = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == user_id,
        )
        c = db.execute(stmt).scalars().first()
        if not c:
            return jsonify({"error": "Not found"}), 404
        return jsonify({
            "id": str(c.id),
            "name": c.name,
            "status": c.status,
            "category": c.category,
            "budget_total": float(c.budget_total),
            "budget_spent": float(c.budget_spent),
            "bid_cpm": float(c.bid_cpm) if c.bid_cpm else None,
            "bid_cpc": float(c.bid_cpc) if c.bid_cpc else None,
            "start_date": c.start_date.isoformat() if c.start_date else None,
            "end_date": c.end_date.isoformat() if c.end_date else None,
            "created_at": c.created_at.isoformat(),
        }), 200
    finally:
        db.close()


@advertiser.route("/campaigns/<campaign_id>", methods=["PUT"])
def update_campaign(campaign_id: str) -> tuple[Any, int]:
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    body = request.get_json() or {}
    db = _get_db_session()
    try:
        from sqlalchemy import select
        stmt = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == user_id,
        )
        c = db.execute(stmt).scalars().first()
        if not c:
            return jsonify({"error": "Not found"}), 404

        if "name" in body:
            c.name = body["name"]
        if "status" in body:
            c.status = body["status"]
        if "category" in body:
            c.category = body["category"]
        if "budget_total" in body:
            c.budget_total = Decimal(str(body["budget_total"]))
        if "bid_cpm" in body:
            c.bid_cpm = Decimal(str(body["bid_cpm"])) if body["bid_cpm"] else None
        if "bid_cpc" in body:
            c.bid_cpc = Decimal(str(body["bid_cpc"])) if body["bid_cpc"] else None
        if "start_date" in body:
            c.start_date = body["start_date"]
        if "end_date" in body:
            c.end_date = body["end_date"]
        db.commit()
        return jsonify({"id": str(c.id), "status": c.status}), 200
    finally:
        db.close()


@advertiser.route("/campaigns/<campaign_id>/pause", methods=["POST"])
def pause_campaign(campaign_id: str) -> tuple[Any, int]:
    return _set_campaign_status(campaign_id, "paused")


@advertiser.route("/campaigns/<campaign_id>/resume", methods=["POST"])
def resume_campaign(campaign_id: str) -> tuple[Any, int]:
    return _set_campaign_status(campaign_id, "active")


def _set_campaign_status(campaign_id: str, status: str) -> tuple[Any, int]:
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    db = _get_db_session()
    try:
        from sqlalchemy import select
        stmt = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == user_id,
        )
        c = db.execute(stmt).scalars().first()
        if not c:
            return jsonify({"error": "Not found"}), 404
        c.status = status
        db.commit()
        return jsonify({"id": str(c.id), "status": status}), 200
    finally:
        db.close()


@advertiser.route("/campaigns/<campaign_id>/creatives", methods=["GET"])
def list_creatives(campaign_id: str) -> tuple[Any, int]:
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    db = _get_db_session()
    try:
        from sqlalchemy import select
        stmt = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == user_id,
        )
        c = db.execute(stmt).scalars().first()
        if not c:
            return jsonify({"error": "Not found"}), 404

        creatives_stmt = select(AdCreative).where(AdCreative.campaign_id == campaign_id)
        creatives = db.execute(creatives_stmt).scalars().all()
        return jsonify([{
            "id": str(cr.id),
            "headline": cr.headline,
            "body": cr.body,
            "cta_text": cr.cta_text,
            "cta_url": cr.cta_url,
            "is_active": cr.is_active,
        } for cr in creatives]), 200
    finally:
        db.close()


@advertiser.route("/campaigns/<campaign_id>/creatives", methods=["POST"])
def create_creative(campaign_id: str) -> tuple[Any, int]:
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    body = request.get_json() or {}
    headline = body.get("headline")
    body_text = body.get("body")
    cta_url = body.get("cta_url")
    if not headline or not body_text or not cta_url:
        return jsonify({"error": "headline, body, and cta_url are required"}), 400

    db = _get_db_session()
    try:
        from sqlalchemy import select
        stmt = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == user_id,
        )
        c = db.execute(stmt).scalars().first()
        if not c:
            return jsonify({"error": "Not found"}), 404

        creative = AdCreative(
            campaign_id=campaign_id,
            headline=headline,
            body=body_text,
            cta_text=body.get("cta_text"),
            cta_url=cta_url,
        )
        db.add(creative)
        db.commit()
        return jsonify({
            "id": str(creative.id),
            "headline": creative.headline,
            "body": creative.body,
            "cta_text": creative.cta_text,
            "cta_url": creative.cta_url,
            "is_active": creative.is_active,
        }), 201
    finally:
        db.close()


@advertiser.route("/campaigns/<campaign_id>/creatives/<creative_id>", methods=["PUT"])
def update_creative(campaign_id: str, creative_id: str) -> tuple[Any, int]:
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    body = request.get_json() or {}
    db = _get_db_session()
    try:
        from sqlalchemy import select
        stmt = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == user_id,
        )
        c = db.execute(stmt).scalars().first()
        if not c:
            return jsonify({"error": "Campaign not found"}), 404

        cr_stmt = select(AdCreative).where(
            AdCreative.id == creative_id,
            AdCreative.campaign_id == campaign_id,
        )
        cr = db.execute(cr_stmt).scalars().first()
        if not cr:
            return jsonify({"error": "Creative not found"}), 404

        if "headline" in body:
            cr.headline = body["headline"]
        if "body" in body:
            cr.body = body["body"]
        if "cta_text" in body:
            cr.cta_text = body["cta_text"]
        if "cta_url" in body:
            cr.cta_url = body["cta_url"]
        if "is_active" in body:
            cr.is_active = body["is_active"]
        db.commit()
        return jsonify({"id": str(cr.id)}), 200
    finally:
        db.close()


@advertiser.route("/campaigns/<campaign_id>/stats", methods=["GET"])
def campaign_stats(campaign_id: str) -> tuple[Any, int]:
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    db = _get_db_session()
    try:
        from sqlalchemy import select, func
        from pubia.models import Impression

        stmt = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == user_id,
        )
        c = db.execute(stmt).scalars().first()
        if not c:
            return jsonify({"error": "Not found"}), 404

        imp_stmt = select(
            func.count(Impression.id),
            func.sum(Impression.clicked),
        ).where(Impression.campaign_id == campaign_id)
        result = db.execute(imp_stmt).first()
        total_impressions = result[0] or 0
        total_clicks = result[1] or 0
        ctr = float(total_clicks) / float(total_impressions) if total_impressions > 0 else 0

        return jsonify({
            "impressions": total_impressions,
            "clicks": total_clicks,
            "ctr": round(ctr * 100, 2),
            "budget_spent": float(c.budget_spent),
        }), 200
    finally:
        db.close()


@advertiser.route("/budget", methods=["GET"])
def budget() -> tuple[Any, int]:
    """Solde actuel de l'annonceur et historique des transactions."""
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    db = _get_db_session()
    try:
        from sqlalchemy import select, func
        from pubia.models import Campaign

        # Calculer le budget total et dépensé de toutes les campagnes
        stmt = select(
            func.sum(Campaign.budget_total).label("total_budget"),
            func.sum(Campaign.budget_spent).label("total_spent"),
        ).where(Campaign.user_id == user_id)

        result = db.execute(stmt).first()
        total_budget = float(result[0]) if result[0] else 0.0
        total_spent = float(result[1]) if result[1] else 0.0
        remaining = total_budget - total_spent

        # Historique des transactions (dépenses par campagne)
        campaigns_stmt = select(
            Campaign.id,
            Campaign.name,
            Campaign.status,
            Campaign.budget_total,
            Campaign.budget_spent,
            Campaign.created_at,
        ).where(Campaign.user_id == user_id).order_by(Campaign.created_at.desc())

        campaigns = db.execute(campaigns_stmt).fetchall()
        transactions = []
        for c in campaigns:
            transactions.append({
                "id": str(c[0]),
                "campaign_name": c[1],
                "status": c[2],
                "budget_total": float(c[3]),
                "budget_spent": float(c[4]),
                "created_at": c[5].isoformat(),
            })

        return jsonify({
            "balance": round(remaining, 2),
            "total_budget": round(total_budget, 2),
            "total_spent": round(total_spent, 2),
            "transactions": transactions,
        }), 200
    finally:
        db.close()


@advertiser.route("/budget/deposit", methods=["POST"])
def deposit() -> tuple[Any, int]:
    """Ajouter du budget (simulation MVP - pas de vrai paiement)."""
    err = _require_login()
    if err:
        return err
    user_id = session["user_id"]

    body = request.get_json() or {}
    amount = body.get("amount")

    if not amount or not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"error": "amount must be a positive number"}), 400

    # MVP: On simule l'ajout de budget en créant une campagne "Budget Deposit"
    # Dans un vrai système, on intégrerait Stripe/PayPal
    db = _get_db_session()
    try:
        from pubia.models import Campaign
        from decimal import Decimal

        # Créer une campagne spéciale "Budget Deposit"
        campaign = Campaign(
            user_id=user_id,
            name=f"Budget Deposit - {amount}€",
            status="active",
            category="General",
            budget_total=Decimal(str(amount)),
            budget_spent=Decimal("0"),
        )
        db.add(campaign)
        db.commit()

        return jsonify({
            "ok": True,
            "amount": amount,
            "campaign_id": str(campaign.id),
            "new_balance": amount,
        }), 200
    finally:
        db.close()

from __future__ import annotations

import logging
import random
import uuid
from dataclasses import dataclass
from decimal import Decimal
from datetime import date

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from pubia.config import build_config
from pubia.models import Campaign, AdCreative, Impression, PublisherApp

logger = logging.getLogger(__name__)


@dataclass
class AdResult:
    ad_id: str
    headline: str
    body: str
    cta_text: str
    cta_url: str
    native_text: str
    impression_id: str


def build_native_text(creative: AdCreative) -> str:
    cta = creative.cta_text or "En savoir plus"
    return (
        f"💡 Sponsorisé · {creative.headline}. "
        f"{creative.body} "
        f"→ {creative.cta_url}"
    )


class AdSelector:
    def __init__(self, db_session: Session) -> None:
        self._db = db_session
        self._pub_share = build_config().get("PUBIA_PUBLISHER_SHARE", 0.70)

    def select_ad(
        self,
        intent_category: str,
        intent_confidence: float,
        app_id: str | None = None,
    ) -> AdResult | None:
        """
        Highest bid wins MVP:
        1. Find active campaigns matching the category
        2. Filter: budget available > 0, date range active
        3. Score = bid_cpm × relevance_score
        4. Select highest scoring campaign
        5. Pick random active creative
        6. Log impression, decrement budget
        7. Return ad or None
        """
        today = date.today()

        # Find eligible campaigns
        stmt = (
            select(Campaign)
            .where(Campaign.status == "active")
            .where(Campaign.category == intent_category)
            .where(Campaign.budget_total > Campaign.budget_spent)
        )
        campaigns = list(self._db.execute(stmt).scalars().all())

        # Filter by date range
        eligible = []
        for c in campaigns:
            if c.start_date and c.start_date > today:
                continue
            if c.end_date and c.end_date < today:
                continue
            if c.bid_cpm is None and c.bid_cpc is None:
                continue
            eligible.append(c)

        if not eligible:
            return None

        # Highest bid wins (score = bid_cpm)
        best: Campaign | None = None
        best_score = Decimal("0")
        for c in eligible:
            score = c.bid_cpm or Decimal("0")
            if score > best_score:
                best_score = score
                best = c

        if best is None:
            return None

        # Select random active creative
        creatives_stmt = (
            select(AdCreative)
            .where(AdCreative.campaign_id == best.id)
            .where(AdCreative.is_active == True)  # noqa: E712
        )
        creatives = list(self._db.execute(creatives_stmt).scalars().all())

        if not creatives:
            return None

        creative = random.choice(creatives)

        # Calculate CPM charged (actual)
        cpm_charged = best_score
        publisher_share = cpm_charged * Decimal(str(self._pub_share))

        # Decrement campaign budget
        best.budget_spent = min(best.budget_spent + cpm_charged, best.budget_total)
        self._db.flush()

        # Log impression
        impression = Impression(
            id=uuid.uuid4(),
            app_id=uuid.UUID(app_id) if app_id else None,
            campaign_id=best.id,
            ad_creative_id=creative.id,
            intent_detected=intent_category,
            intent_score=Decimal(str(intent_confidence)),
            cpm_charged=cpm_charged,
            publisher_share=publisher_share,
            clicked=False,
        )
        self._db.add(impression)
        self._db.commit()

        return AdResult(
            ad_id=str(creative.id),
            headline=creative.headline,
            body=creative.body,
            cta_text=creative.cta_text or "En savoir plus",
            cta_url=creative.cta_url,
            native_text=build_native_text(creative),
            impression_id=str(impression.id),
        )

    def track_click(self, impression_id: str) -> bool:
        try:
            stmt = select(Impression).where(Impression.id == uuid.UUID(impression_id))
            impression = self._db.execute(stmt).scalars().first()
            if impression:
                impression.clicked = True
                self._db.commit()
                return True
        except Exception as e:
            logger.error(f"Error tracking click: {e}")
        return False

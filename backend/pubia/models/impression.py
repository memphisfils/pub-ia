from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pubia.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Impression(Base):
    __tablename__ = "impressions"
    __table_args__ = (
        Index("ix_impressions_app_id", "app_id"),
        Index("ix_impressions_campaign_id", "campaign_id"),
        Index("ix_impressions_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    app_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("publisher_apps.id", ondelete="SET NULL"),
        nullable=True,
    )
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True,
    )
    ad_creative_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ad_creatives.id", ondelete="SET NULL"),
        nullable=True,
    )
    intent_detected: Mapped[str | None] = mapped_column(String(100), nullable=True)
    intent_score: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 2), nullable=True
    )
    cpm_charged: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 4), nullable=True
    )
    publisher_share: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 4), nullable=True
    )
    clicked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )

    app: Mapped["PublisherApp | None"] = relationship(back_populates="impressions")
    campaign: Mapped["Campaign | None"] = relationship(back_populates="impressions")
    ad_creative: Mapped["AdCreative | None"] = relationship(
        back_populates="impressions"
    )

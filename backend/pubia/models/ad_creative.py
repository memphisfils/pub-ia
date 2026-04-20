from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pubia.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AdCreative(Base):
    __tablename__ = "ad_creatives"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    headline: Mapped[str] = mapped_column(String(100), nullable=False)
    body: Mapped[str] = mapped_column(String(200), nullable=False)
    cta_text: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cta_url: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )

    campaign: Mapped["Campaign"] = relationship(back_populates="ad_creatives")
    impressions: Mapped[list["Impression"]] = relationship(
        back_populates="ad_creative"
    )

from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pubia.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def generate_api_key() -> str:
    return f"pk_live_{secrets.token_hex(28)}"


class PublisherApp(Base):
    __tablename__ = "publisher_apps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    website_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    api_key: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, default=generate_api_key
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="publisher_apps")
    impressions: Mapped[list["Impression"]] = relationship(
        back_populates="app", cascade="all, delete-orphan"
    )

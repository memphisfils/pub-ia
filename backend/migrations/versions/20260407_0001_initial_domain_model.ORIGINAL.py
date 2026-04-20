"""initial domain model

Revision ID: 20260407_0001
Revises: None
Create Date: 2026-04-07 01:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260407_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "campaigns",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("advertiser_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("budget_amount", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("budget_currency", sa.String(length=3), nullable=True),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint(
            "(ends_at IS NULL OR starts_at IS NULL) OR ends_at >= starts_at",
            name=op.f("ck_campaigns_campaign_dates_valid"),
        ),
        sa.CheckConstraint(
            "(budget_amount IS NULL AND budget_currency IS NULL) OR "
            "(budget_amount IS NOT NULL AND budget_currency IS NOT NULL)",
            name=op.f("ck_campaigns_campaign_budget_pairing"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_campaigns")),
    )

    op.create_table(
        "publishers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("website_url", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_publishers")),
        sa.UniqueConstraint("slug", name=op.f("uq_publishers_slug")),
    )

    op.create_table(
        "placements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("publisher_id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("format", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["publisher_id"],
            ["publishers.id"],
            name=op.f("fk_placements_publisher_id_publishers"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_placements")),
        sa.UniqueConstraint("publisher_id", "slug", name=op.f("uq_placements_publisher_id")),
    )

    op.create_table(
        "ingestion_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("publisher_id", sa.Uuid(), nullable=False),
        sa.Column("placement_id", sa.Uuid(), nullable=True),
        sa.Column("campaign_id", sa.Uuid(), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["campaign_id"],
            ["campaigns.id"],
            name=op.f("fk_ingestion_events_campaign_id_campaigns"),
        ),
        sa.ForeignKeyConstraint(
            ["placement_id"],
            ["placements.id"],
            name=op.f("fk_ingestion_events_placement_id_placements"),
        ),
        sa.ForeignKeyConstraint(
            ["publisher_id"],
            ["publishers.id"],
            name=op.f("fk_ingestion_events_publisher_id_publishers"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ingestion_events")),
        sa.UniqueConstraint("idempotency_key", name=op.f("uq_ingestion_events_idempotency_key")),
    )

    op.create_index(
        "ix_ingestion_events_publisher_id_occurred_at",
        "ingestion_events",
        ["publisher_id", "occurred_at"],
        unique=False,
    )
    op.create_index(
        "ix_ingestion_events_event_type_occurred_at",
        "ingestion_events",
        ["event_type", "occurred_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_ingestion_events_event_type_occurred_at", table_name="ingestion_events")
    op.drop_index("ix_ingestion_events_publisher_id_occurred_at", table_name="ingestion_events")
    op.drop_table("ingestion_events")
    op.drop_table("placements")
    op.drop_table("publishers")
    op.drop_table("campaigns")

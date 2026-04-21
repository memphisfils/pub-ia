"""initial domain model

Revision ID: 20260408_0001
Revises: None
Create Date: 2026-04-08 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260408_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("google_id", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="publisher"),
        sa.Column("plan", sa.String(length=50), nullable=False, server_default="free"),
        sa.Column("plan_expires_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.UniqueConstraint("google_id", name=op.f("uq_users_google_id")),
    )

    # 2. publisher_apps
    op.create_table(
        "publisher_apps",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("website_url", sa.Text(), nullable=True),
        sa.Column("api_key", sa.String(length=64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_publisher_apps_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_publisher_apps")),
        sa.UniqueConstraint("api_key", name=op.f("uq_publisher_apps_api_key")),
    )

    # 3. campaigns
    op.create_table(
        "campaigns",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="draft"),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("intent_keywords", sa.JSON(), nullable=True),
        sa.Column("budget_total", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0"),
        sa.Column("budget_spent", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0"),
        sa.Column("bid_cpm", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column("bid_cpc", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_campaigns_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_campaigns")),
    )

    # 4. ad_creatives
    op.create_table(
        "ad_creatives",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("campaign_id", sa.Uuid(), nullable=False),
        sa.Column("headline", sa.String(length=100), nullable=False),
        sa.Column("body", sa.String(length=200), nullable=False),
        sa.Column("cta_text", sa.String(length=50), nullable=True),
        sa.Column("cta_url", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], name=op.f("fk_ad_creatives_campaign_id_campaigns"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ad_creatives")),
    )

    # 5. impressions
    op.create_table(
        "impressions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("app_id", sa.Uuid(), nullable=True),
        sa.Column("campaign_id", sa.Uuid(), nullable=True),
        sa.Column("ad_creative_id", sa.Uuid(), nullable=True),
        sa.Column("intent_detected", sa.String(length=100), nullable=True),
        sa.Column("intent_score", sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column("cpm_charged", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("publisher_share", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("clicked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["app_id"], ["publisher_apps.id"], name=op.f("fk_impressions_app_id_publisher_apps"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], name=op.f("fk_impressions_campaign_id_campaigns"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["ad_creative_id"], ["ad_creatives.id"], name=op.f("fk_impressions_ad_creative_id_ad_creatives"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_impressions")),
    )

    op.create_index("ix_impressions_app_id", "impressions", ["app_id"], unique=False)
    op.create_index("ix_impressions_campaign_id", "impressions", ["campaign_id"], unique=False)
    op.create_index("ix_impressions_created_at", "impressions", ["created_at"], unique=False)

    # 6. subscriptions
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("plan", sa.String(length=50), nullable=False),
        sa.Column("price_monthly", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_subscriptions_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subscriptions")),
    )


def downgrade() -> None:
    op.drop_table("subscriptions")
    op.drop_index("ix_impressions_created_at", table_name="impressions")
    op.drop_index("ix_impressions_campaign_id", table_name="impressions")
    op.drop_index("ix_impressions_app_id", table_name="impressions")
    op.drop_table("impressions")
    op.drop_table("ad_creatives")
    op.drop_table("campaigns")
    op.drop_table("publisher_apps")
    op.drop_table("users")

from sqlalchemy import create_engine, inspect

from pubia.db import Base
import pubia.models  # noqa: F401


def test_tables_are_registered() -> None:
    """All 6 tables from the brief should be registered."""
    assert {
        "users",
        "publisher_apps",
        "campaigns",
        "ad_creatives",
        "impressions",
        "subscriptions",
    }.issubset(Base.metadata.tables.keys())


def test_models_create_expected_columns() -> None:
    """Models create their expected columns in SQLite."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    inspector = inspect(engine)

    assert {
        "users",
        "publisher_apps",
        "campaigns",
        "ad_creatives",
        "impressions",
        "subscriptions",
    }.issubset(inspector.get_table_names())

    # Check users columns
    user_columns = {col["name"] for col in inspector.get_columns("users")}
    assert {"id", "email", "name", "google_id", "role", "plan"}.issubset(user_columns)

    # Check publisher_apps columns
    app_columns = {col["name"] for col in inspector.get_columns("publisher_apps")}
    assert {"id", "user_id", "name", "api_key", "is_active"}.issubset(app_columns)

    # Check campaigns columns
    campaign_columns = {col["name"] for col in inspector.get_columns("campaigns")}
    assert {"id", "user_id", "name", "status", "category", "budget_total", "bid_cpm"}.issubset(campaign_columns)

    # Check ad_creatives columns
    creative_columns = {col["name"] for col in inspector.get_columns("ad_creatives")}
    assert {"id", "campaign_id", "headline", "body", "cta_url"}.issubset(creative_columns)

    # Check impressions columns
    impression_columns = {col["name"] for col in inspector.get_columns("impressions")}
    assert {"id", "app_id", "campaign_id", "intent_detected", "cpm_charged", "clicked"}.issubset(impression_columns)

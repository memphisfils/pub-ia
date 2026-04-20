from __future__ import annotations

from decimal import Decimal

from pubia.config import build_config


def calculate_publisher_share(cpm_charged: Decimal) -> Decimal:
    """Calculate publisher's 70% share of the CPM charged."""
    pub_share = build_config().get("PUBIA_PUBLISHER_SHARE", 0.70)
    return cpm_charged * Decimal(str(pub_share))


def calculate_ecpm(impressions: int, revenue: Decimal) -> Decimal:
    """Calculate effective CPM from impressions and revenue."""
    if impressions == 0:
        return Decimal("0")
    return (revenue / Decimal(impressions)) * Decimal("1000")

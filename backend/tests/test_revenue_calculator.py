"""Tests pour le service revenue_calculator."""
from decimal import Decimal

from pubia.services.revenue_calculator import (
    calculate_publisher_share,
    calculate_ecpm,
)


def test_publisher_share_70_percent() -> None:
    """Le publisher reçoit 70% du CPM par défaut."""
    cpm = Decimal("10.00")
    share = calculate_publisher_share(cpm)
    assert share == Decimal("7.00")


def test_publisher_share_small_cpm() -> None:
    """Fonctionne aussi avec des petits CPM."""
    cpm = Decimal("0.50")
    share = calculate_publisher_share(cpm)
    assert share == Decimal("0.35")


def test_publisher_share_zero() -> None:
    """CPM zéro = share zéro."""
    cpm = Decimal("0")
    share = calculate_publisher_share(cpm)
    assert share == Decimal("0")


def test_ecpm_with_impressions() -> None:
    """eCPM = (revenue / impressions) * 1000."""
    revenue = Decimal("7.00")
    impressions = 1000
    ecpm = calculate_ecpm(impressions, revenue)
    assert ecpm == Decimal("7.00")


def test_ecpm_with_zero_impressions() -> None:
    """Pas d'impressions = eCPM zéro."""
    revenue = Decimal("7.00")
    ecpm = calculate_ecpm(0, revenue)
    assert ecpm == Decimal("0")


def test_ecpm_large_scale() -> None:
    """Test avec un grand volume."""
    revenue = Decimal("700.00")
    impressions = 100_000
    ecpm = calculate_ecpm(impressions, revenue)
    assert ecpm == Decimal("7.00")

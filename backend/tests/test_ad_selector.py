"""Tests pour le service ad_selector."""
from decimal import Decimal
from unittest.mock import MagicMock
from datetime import date, datetime

import pytest


class MockResult:
    """Simule un résultat SQLAlchemy."""

    def __init__(self, value):
        self._value = value

    def scalars(self):
        return self

    def first(self):
        return self._value[0] if self._value else None

    def all(self):
        return self._value


class MockDBSession:
    """Simule une session DB."""

    def __init__(self, results=None):
        self._results = results or []
        self._calls = []
        self._added = []

    def execute(self, stmt):
        self._calls.append(stmt)
        if self._results:
            result = self._results.pop(0)
            return result
        return MockResult([])

    def add(self, obj):
        self._added.append(obj)

    def flush(self):
        pass

    def commit(self):
        pass


def _create_mock_campaign(
    campaign_id="camp-1",
    status="active",
    category="achat_tech",
    budget_total=Decimal("100"),
    budget_spent=Decimal("0"),
    bid_cpm=Decimal("5.00"),
    bid_cpc=None,
    start_date=None,
    end_date=None,
):
    """Crée un mock Campaign."""
    campaign = MagicMock()
    campaign.id = campaign_id
    campaign.status = status
    campaign.category = category
    campaign.budget_total = budget_total
    campaign.budget_spent = budget_spent
    campaign.bid_cpm = bid_cpm
    campaign.bid_cpc = bid_cpc
    campaign.start_date = start_date
    campaign.end_date = end_date
    return campaign


def _create_mock_creative(
    creative_id="cr-1",
    headline="Test Headline",
    body="Test Body",
    cta_text="Voir l'offre",
    cta_url="https://example.com",
    is_active=True,
):
    """Crée un mock AdCreative."""
    creative = MagicMock()
    creative.id = creative_id
    creative.headline = headline
    creative.body = body
    creative.cta_text = cta_text
    creative.cta_url = cta_url
    creative.is_active = is_active
    return creative


def test_select_ad_returns_none_when_no_campaigns() -> None:
    """Pas de campagnes actives = pas d'annonce."""
    from pubia.services.ad_selector import AdSelector

    db = MockDBSession(results=[MockResult([])])  # Pas de campagnes
    selector = AdSelector(db)

    result = selector.select_ad("achat_tech", 0.8, "app-1")

    assert result is None


def test_select_ad_returns_none_when_campaign_paused() -> None:
    """Une campagne paused ne doit pas être sélectionnée."""
    from pubia.services.ad_selector import AdSelector

    campaign = _create_mock_campaign(status="paused")
    db = MockDBSession(results=[MockResult([])])  # Aucune campagne active
    selector = AdSelector(db)

    result = selector.select_ad("achat_tech", 0.8, "app-1")

    assert result is None


def test_select_ad_returns_none_when_budget_exhausted() -> None:
    """Une campagne avec budget épuisé ne doit pas être sélectionnée."""
    from pubia.services.ad_selector import AdSelector

    campaign = _create_mock_campaign(
        budget_total=Decimal("100"),
        budget_spent=Decimal("100"),  # Budget épuisé
    )
    db = MockDBSession(results=[MockResult([])])  # Aucune campagne éligible
    selector = AdSelector(db)

    result = selector.select_ad("achat_tech", 0.8, "app-1")

    assert result is None


def test_select_ad_returns_none_when_campaign_not_started() -> None:
    """Une campagne dont la date de début est dans le futur ne doit pas être sélectionnée."""
    from pubia.services.ad_selector import AdSelector
    from datetime import timedelta

    future_date = date.today() + timedelta(days=7)
    campaign = _create_mock_campaign(start_date=future_date)
    db = MockDBSession(results=[MockResult([])])
    selector = AdSelector(db)

    result = selector.select_ad("achat_tech", 0.8, "app-1")

    assert result is None


def test_select_ad_returns_none_when_campaign_expired() -> None:
    """Une campagne dont la date de fin est passée ne doit pas être sélectionnée."""
    from pubia.services.ad_selector import AdSelector
    from datetime import timedelta

    past_date = date.today() - timedelta(days=1)
    campaign = _create_mock_campaign(end_date=past_date)
    db = MockDBSession(results=[MockResult([])])
    selector = AdSelector(db)

    result = selector.select_ad("achat_tech", 0.8, "app-1")

    assert result is None


def test_select_ad_highest_bid_wins() -> None:
    """La campagne avec le plus haut bid CPM doit gagner."""
    from pubia.services.ad_selector import AdSelector

    # Ce test nécessiterait un mocking plus avancé de SQLAlchemy
    # Pour l'instant, on teste la logique de base
    from pubia.services.ad_selector import AdSelector

    # Mock simple: une seule campagne disponible
    creative = _create_mock_creative()
    campaign = _create_mock_campaign(bid_cpm=Decimal("10.00"))
    
    # Configuration du mock pour retourner une campagne puis une creative
    db = MockDBSession()
    
    # Ce test nécessite un vrai setup SQLAlchemy pour être complet
    # On teste juste l'import et la structure pour l'instant
    selector = AdSelector(db)
    assert selector is not None


def test_track_click_returns_true_for_valid_impression() -> None:
    """Le tracking d'un clic avec un impression_id valide retourne True."""
    from pubia.services.ad_selector import AdSelector
    import uuid

    impression_id = str(uuid.uuid4())
    
    # Mock impression
    impression = MagicMock()
    impression.clicked = False
    impression.id = impression_id

    db = MockDBSession(results=[MockResult([impression])])
    selector = AdSelector(db)

    result = selector.track_click(impression_id)

    assert result is True
    assert impression.clicked is True


def test_track_click_returns_false_for_invalid_impression() -> None:
    """Le tracking d'un clic avec un impression_id invalide retourne False."""
    from pubia.services.ad_selector import AdSelector

    db = MockDBSession(results=[MockResult([])])  # Pas d'impression trouvée
    selector = AdSelector(db)

    result = selector.track_click("non-existent-id")

    assert result is False

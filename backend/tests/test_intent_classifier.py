"""Tests pour le service intent_classifier."""
from unittest.mock import MagicMock, patch
from decimal import Decimal

import pytest

from pubia.services.intent_classifier import (
    IntentClassifier,
    IntentResult,
    INTENT_CATEGORIES,
    INTENT_SYSTEM_PROMPT,
)


class MockOpenAIResponse:
    """Simule une réponse de l'API OpenAI."""

    def __init__(self, content: str):
        self.choices = [MagicMock()]
        self.choices[0].message.content = content


class MockRedisClient:
    """Simule un client Redis."""

    def __init__(self, cache_value=None):
        self._cache_value = cache_value
        self._set_calls = []

    def get(self, key):
        return self._cache_value

    def setex(self, key, ttl, value):
        self._set_calls.append((key, ttl, value))


def test_intent_categories_has_15_categories() -> None:
    """La taxonomie doit contenir 15 catégories."""
    assert len(INTENT_CATEGORIES) == 15


def test_intent_categories_contains_expected_keys() -> None:
    """Les catégories clés doivent être présentes."""
    expected_keys = {
        "achat_tech",
        "achat_beaute",
        "achat_finance",
        "achat_sport",
        "achat_voyage",
    }
    assert expected_keys.issubset(INTENT_CATEGORIES.keys())


def test_intent_system_prompt_is_defined() -> None:
    """Le system prompt doit être défini."""
    assert INTENT_SYSTEM_PROMPT is not None
    assert len(INTENT_SYSTEM_PROMPT) > 100


def test_intent_result_dataclass() -> None:
    """IntentResult doit contenir les champs attendus."""
    result = IntentResult(
        has_intent=True,
        intent="achat_tech",
        confidence=0.85,
        category="Tech",
        intent_id="uuid-123",
    )

    assert result.has_intent is True
    assert result.intent == "achat_tech"
    assert result.confidence == 0.85
    assert result.category == "Tech"
    assert result.intent_id == "uuid-123"


def test_classifier_init_with_openai() -> None:
    """Le classifier doit s'initialiser avec OpenAI par défaut."""
    with patch("pubia.services.intent_classifier.build_config") as mock_config:
        mock_config.return_value = {
            "LLM_PROVIDER": "openai",
            "OPENAI_API_KEY": "sk-test",
            "OPENAI_MODEL": "gpt-4o-mini",
            "OPENAI_TIMEOUT": 8,
            "OPENAI_MAX_TOKENS": 150,
            "PUBIA_INTENT_THRESHOLD": 0.65,
        }

        classifier = IntentClassifier()

        assert classifier._provider == "openai"
        assert classifier._model == "gpt-4o-mini"
        assert classifier._threshold == 0.65


def test_classifier_cache_miss() -> None:
    """Quand le cache est vide, le classifier doit appeler l'API."""
    mock_redis = MockRedisClient(cache_value=None)

    mock_openai_client = MagicMock()
    mock_openai_client.chat.completions.create.return_value = MockOpenAIResponse(
        '{"has_intent": true, "category": "Tech", "intent_label": "achat_tech", "confidence": 0.85}'
    )

    with patch("pubia.services.intent_classifier.build_config") as mock_config:
        mock_config.return_value = {
            "LLM_PROVIDER": "openai",
            "OPENAI_API_KEY": "sk-test",
            "OPENAI_MODEL": "gpt-4o-mini",
            "OPENAI_TIMEOUT": 8,
            "OPENAI_MAX_TOKENS": 150,
            "PUBIA_INTENT_THRESHOLD": 0.65,
        }

        classifier = IntentClassifier(redis_client=mock_redis, openai_client=mock_openai_client)
        result = classifier.classify("Quel laptop acheter ?")

        assert result.has_intent is True
        assert result.intent == "achat_tech"
        assert result.confidence == 0.85

        # Vérifier que le résultat a été mis en cache
        assert len(mock_redis._set_calls) == 1


def test_classifier_cache_hit() -> None:
    """Quand le cache contient le résultat, ne pas appeler l'API."""
    import json
    cached_data = {
        "has_intent": True,
        "intent": "achat_beaute",
        "confidence": 0.90,
        "category": "Beauté",
        "intent_id": "cached-uuid",
    }
    mock_redis = MockRedisClient(cache_value=json.dumps(cached_data))

    mock_openai_client = MagicMock()

    with patch("pubia.services.intent_classifier.build_config") as mock_config:
        mock_config.return_value = {
            "LLM_PROVIDER": "openai",
            "OPENAI_API_KEY": "sk-test",
            "OPENAI_MODEL": "gpt-4o-mini",
            "OPENAI_TIMEOUT": 8,
            "OPENAI_MAX_TOKENS": 150,
            "PUBIA_INTENT_THRESHOLD": 0.65,
        }

        classifier = IntentClassifier(redis_client=mock_redis, openai_client=mock_openai_client)
        result = classifier.classify("Quelle crème acheter ?")

        assert result.has_intent is True
        assert result.intent == "achat_beaute"
        assert result.confidence == 0.90

        # Vérifier que l'API n'a PAS été appelée
        mock_openai_client.chat.completions.create.assert_not_called()


def test_classifier_below_threshold() -> None:
    """Un score sous le seuil doit retourner has_intent=False."""
    mock_redis = MockRedisClient(cache_value=None)

    mock_openai_client = MagicMock()
    mock_openai_client.chat.completions.create.return_value = MockOpenAIResponse(
        '{"has_intent": true, "category": "Tech", "intent_label": "achat_tech", "confidence": 0.50}'
    )

    with patch("pubia.services.intent_classifier.build_config") as mock_config:
        mock_config.return_value = {
            "LLM_PROVIDER": "openai",
            "OPENAI_API_KEY": "sk-test",
            "OPENAI_MODEL": "gpt-4o-mini",
            "OPENAI_TIMEOUT": 8,
            "OPENAI_MAX_TOKENS": 150,
            "PUBIA_INTENT_THRESHOLD": 0.65,
        }

        classifier = IntentClassifier(redis_client=mock_redis, openai_client=mock_openai_client)
        result = classifier.classify("Peut-être un laptop ?")

        # Même si l'API retourne has_intent=true, le seuil le force à false
        assert result.has_intent is False
        assert result.confidence == 0.50


def test_classifier_handles_api_error() -> None:
    """Une erreur API doit retourner has_intent=False."""
    mock_redis = MockRedisClient(cache_value=None)

    mock_openai_client = MagicMock()
    mock_openai_client.chat.completions.create.side_effect = Exception("API Error")

    with patch("pubia.services.intent_classifier.build_config") as mock_config:
        mock_config.return_value = {
            "LLM_PROVIDER": "openai",
            "OPENAI_API_KEY": "sk-test",
            "OPENAI_MODEL": "gpt-4o-mini",
            "OPENAI_TIMEOUT": 8,
            "OPENAI_MAX_TOKENS": 150,
            "PUBIA_INTENT_THRESHOLD": 0.65,
        }

        classifier = IntentClassifier(redis_client=mock_redis, openai_client=mock_openai_client)
        result = classifier.classify("Quel laptop acheter ?")

        assert result.has_intent is False
        assert result.confidence == 0.0
        assert result.intent is None

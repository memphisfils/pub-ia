from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass

from openai import OpenAI, APIError as OpenAIAPIError

from pubia.config import build_config

logger = logging.getLogger(__name__)

INTENT_CATEGORIES: dict[str, list[str]] = {
    "achat_tech": ["ordinateur", "smartphone", "laptop", "écran", "souris"],
    "achat_beaute": ["crème", "skincare", "maquillage", "parfum", "shampoing"],
    "achat_finance": ["banque", "compte", "crédit", "assurance vie", "investir"],
    "achat_assurance": ["assurance", "mutuelle", "garantie", "couverture"],
    "achat_auto": ["voiture", "véhicule", "automobile", "moto", "scooter"],
    "achat_sport": ["sneakers", "chaussures sport", "équipement", "vélo"],
    "achat_voyage": ["hôtel", "vol", "vacances", "séjour", "billet"],
    "achat_mode": ["vêtements", "mode", "tendance", "marque", "designer"],
    "achat_sante": ["médicament", "complément", "vitamine", "traitement"],
    "achat_alimentation": ["nourriture", "recette", "produit alimentaire", "boisson"],
    "achat_immobilier": ["appartement", "maison", "louer", "acheter logement"],
    "achat_formation": ["cours", "formation", "apprendre", "certification", "diplôme"],
    "achat_logiciel": ["abonnement", "logiciel", "outil", "application", "SaaS"],
    "achat_maison": ["meuble", "déco", "electroménager", "cuisine équipée"],
    "achat_animaux": ["chien", "chat", "animal", "vétérinaire", "croquettes"],
}

INTENT_SYSTEM_PROMPT = """Tu es un classificateur d'intention d'achat.
Analyse le prompt utilisateur et détermine :
1. Si le prompt contient une intention d'achat ou de recommandation de produit/service
2. Quelle catégorie d'intention correspond le mieux
3. Ton niveau de confiance (0.0 à 1.0)

Réponds UNIQUEMENT en JSON :
{"has_intent": bool, "category": string|null, "intent_label": string|null, "confidence": float}

IMPORTANT :
- Un prompt sur la météo, les maths, la programmation = has_intent: false
- Un prompt sur "quel laptop acheter", "recommande une crème" = has_intent: true
- Sois conservateur — doute = has_intent: false
"""


@dataclass
class IntentResult:
    has_intent: bool
    intent: str | None
    confidence: float
    category: str | None
    intent_id: str


class IntentClassifier:
    CACHE_TTL = 300  # 5 minutes

    def __init__(
        self,
        redis_client: "RedisClient | None" = None,
        openai_client: OpenAI | None = None,
    ) -> None:
        config = build_config()
        self._redis = redis_client
        self._provider = config.get("LLM_PROVIDER", "openai")

        if openai_client:
            self._client = openai_client
        elif self._provider == "ollama":
            self._client = OpenAI(
                base_url=config.get("OLLAMA_BASE_URL", "https://ollama.com"),
                api_key=config.get("OLLAMA_API_KEY", ""),
            )
        else:
            self._client = OpenAI(api_key=config.get("OPENAI_API_KEY", ""))

        self._model = (
            config.get("OLLAMA_MODEL", "llama3.2")
            if self._provider == "ollama"
            else config.get("OPENAI_MODEL", "gpt-4o-mini")
        )
        self._timeout = config.get("OPENAI_TIMEOUT", 8)
        self._max_tokens = config.get("OPENAI_MAX_TOKENS", 150)
        self._threshold = config.get("PUBIA_INTENT_THRESHOLD", 0.65)

    def _cache_key(self, prompt: str) -> str:
        h = hashlib.sha256(prompt.encode()).hexdigest()[:32]
        return f"intent:cache:{h}"

    def _get_from_cache(self, prompt: str) -> IntentResult | None:
        if self._redis is None:
            return None
        try:
            key = self._cache_key(prompt)
            raw = self._redis.client.get(key)
            if raw:
                data = json.loads(raw)
                return IntentResult(
                    has_intent=data["has_intent"],
                    intent=data["intent"],
                    confidence=data["confidence"],
                    category=data["category"],
                    intent_id=data["intent_id"],
                )
        except Exception:
            pass
        return None

    def _set_cache(self, prompt: str, result: IntentResult) -> None:
        if self._redis is None:
            return
        try:
            key = self._cache_key(prompt)
            data = {
                "has_intent": result.has_intent,
                "intent": result.intent,
                "confidence": result.confidence,
                "category": result.category,
                "intent_id": result.intent_id,
            }
            self._redis.client.setex(key, self.CACHE_TTL, json.dumps(data))
        except Exception:
            pass

    def classify(self, prompt: str, context: str | None = None) -> IntentResult:
        # Check cache first
        cached = self._get_from_cache(prompt)
        if cached:
            return cached

        full_prompt = prompt
        if context:
            full_prompt = f"Contexte: {context}\n\nPrompt: {prompt}"

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                    {"role": "user", "content": full_prompt},
                ],
                max_tokens=self._max_tokens,
                timeout=self._timeout,
                temperature=0.0,
            )
            raw = response.choices[0].message.content or "{}"

            # Parse JSON response
            data = json.loads(raw.strip())
            has_intent = bool(data.get("has_intent", False))
            confidence = float(data.get("confidence", 0.0))

            # Apply threshold
            if confidence < self._threshold:
                has_intent = False

            intent_id = str(uuid.uuid4())

            result = IntentResult(
                has_intent=has_intent,
                intent=data.get("intent_label") if has_intent else None,
                confidence=confidence,
                category=data.get("category") if has_intent else None,
                intent_id=intent_id,
            )

            self._set_cache(prompt, result)
            return result

        except OpenAIAPIError as e:
            logger.error(f"LLM API error (%s): %s", self._provider, e)
            return IntentResult(False, None, 0.0, None, str(uuid.uuid4()))
        except Exception as e:
            logger.error(f"Unexpected error in intent classification: %s", e)
            return IntentResult(False, None, 0.0, None, str(uuid.uuid4()))


# Global classifier instance
_classifier: IntentClassifier | None = None


def get_classifier(redis_client=None) -> IntentClassifier:
    global _classifier
    if _classifier is None:
        _classifier = IntentClassifier(redis_client=redis_client)
    return _classifier

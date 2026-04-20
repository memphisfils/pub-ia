"""
Pub-IA SDK for Python
"""
import requests

BASE_URL = "/v1"


class PubIA:
    def __init__(self):
        self._api_key: str | None = None
        self._endpoint: str = BASE_URL
        self._debug: bool = False

    def init(self, api_key: str, endpoint: str | None = None, debug: bool = False) -> None:
        """Initialize the SDK with the publisher API key."""
        self._api_key = api_key
        self._endpoint = endpoint or BASE_URL
        self._debug = debug
        if self._debug:
            print(f"[PubIA] Initialized with endpoint: {self._endpoint}")

    def _request(self, path: str, body: dict) -> dict | None:
        """Make a request to the Pub-IA API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }
        resp = requests.post(
            f"{self._endpoint}{path}",
            json=body,
            headers=headers,
            timeout=10,
        )
        if resp.status_code == 204:
            return None
        resp.raise_for_status()
        return resp.json()

    def analyze_intent(self, prompt: str, context: str | None = None) -> dict:
        """
        Analyze a prompt to detect purchase intent.
        Returns: {"has_intent": bool, "intent": str|None, "confidence": float, "category": str|None, "intent_id": str}
        """
        if self._debug:
            print(f"[PubIA] analyze_intent: {prompt[:50]}")
        result = self._request("/analyze-intent", {"prompt": prompt, "context": context})
        return result or {"has_intent": False, "intent": None, "confidence": 0.0, "category": None, "intent_id": None}

    def get_ad(self, intent_result: dict) -> dict | None:
        """
        Get the winning ad for a given intent.
        Returns: {"native_text": str, "impression_id": str, ...} or None
        """
        if not intent_result.get("has_intent") or not intent_result.get("intent"):
            return None
        if self._debug:
            print(f"[PubIA] get_ad for intent: {intent_result['intent']}")
        return self._request("/get-ad", {
            "intent": intent_result["intent"],
            "intent_id": intent_result.get("intent_id"),
            "confidence": intent_result.get("confidence", 0.0),
        })

    def track_click(self, impression_id: str) -> bool:
        """Log a click on an ad impression."""
        if self._debug:
            print(f"[PubIA] track_click: {impression_id}")
        result = self._request("/track-click", {"impression_id": impression_id})
        return result is not None and result.get("tracked", False)


pub_ia = PubIA()

"""
Pub-IA SDK for Python.
"""
from __future__ import annotations

import os
from typing import Any, Dict, Mapping, MutableMapping, Optional
from urllib.parse import urlparse, urlunparse

import requests

DEFAULT_ENDPOINT = "https://pub-ia.io/v1"
DEFAULT_TIMEOUT = 10.0


class PubIAError(Exception):
    """Raised when the Pub-IA SDK cannot complete a request."""

    def __init__(
        self,
        message: str,
        status: Optional[int] = None,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.details = details


def _normalize_endpoint(endpoint: Optional[str]) -> str:
    raw_endpoint = (endpoint or os.getenv("PUB_IA_ENDPOINT") or "").strip()
    if not raw_endpoint:
        return DEFAULT_ENDPOINT

    parsed = urlparse(raw_endpoint)
    if not parsed.scheme or not parsed.netloc:
        raise PubIAError(
            "endpoint must be an absolute URL such as "
            "'https://pub-ia.io' or 'http://localhost:8000/v1'",
        )

    path = parsed.path or "/"
    if path == "/":
        path = "/v1"
    else:
        path = path.rstrip("/")

    normalized = parsed._replace(path=path, params="", query="", fragment="")
    return urlunparse(normalized).rstrip("/")


def _build_url(endpoint: str, path: str) -> str:
    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{endpoint}{normalized_path}"


def _strip_none(body: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        key: value
        for key, value in body.items()
        if value is not None
    }


def _parse_response_body(response: requests.Response) -> Any:
    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type.lower():
        try:
            return response.json()
        except ValueError:
            return None

    text = response.text.strip()
    return text or None


def _get_error_message(status: int, payload: Any) -> str:
    if isinstance(payload, str) and payload.strip():
        return payload

    if isinstance(payload, Mapping):
        error = payload.get("error")
        if isinstance(error, str) and error.strip():
            return error

        message = payload.get("message")
        if isinstance(message, str) and message.strip():
            return message

    return f"HTTP {status}"


def _coerce_bool(value: Any) -> bool:
    return bool(value)


def _map_intent_result(result: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "has_intent": _coerce_bool(result.get("has_intent")),
        "intent": result.get("intent"),
        "confidence": float(result.get("confidence", 0.0) or 0.0),
        "category": result.get("category"),
        "intent_id": result.get("intent_id"),
    }


def _map_ad_result(result: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "ad_id": result.get("ad_id"),
        "headline": result.get("headline"),
        "body": result.get("body"),
        "cta_text": result.get("cta_text"),
        "cta_url": result.get("cta_url"),
        "native_text": result.get("native_text"),
        "impression_id": result.get("impression_id"),
    }


class PubIA:
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        debug: bool = False,
        app_id: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ) -> None:
        self._api_key: Optional[str] = None
        self._app_id: str = ""
        self._endpoint: str = DEFAULT_ENDPOINT
        self._debug: bool = False
        self._timeout: float = DEFAULT_TIMEOUT
        self._session: requests.Session = session or requests.Session()

        if api_key is not None:
            self.init(
                api_key=api_key,
                endpoint=endpoint,
                debug=debug,
                app_id=app_id,
                timeout=timeout,
                session=session,
            )

    def init(
        self,
        api_key: str,
        endpoint: Optional[str] = None,
        debug: bool = False,
        app_id: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ) -> None:
        """Initialize the SDK with the publisher API key."""
        normalized_key = api_key.strip() if isinstance(api_key, str) else ""
        if not normalized_key:
            raise PubIAError("api_key is required")

        self._api_key = normalized_key
        self._app_id = app_id.strip() if isinstance(app_id, str) else ""
        self._endpoint = _normalize_endpoint(endpoint)
        self._debug = bool(debug)
        self._timeout = float(timeout)
        if session is not None:
            self._session = session

        if self._debug:
            print(f"[PubIA] Initialized with endpoint: {self._endpoint}")

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def _ensure_initialized(self) -> None:
        if not self._api_key:
            raise PubIAError(
                "PubIA SDK is not initialized. "
                "Call pub_ia.init(api_key=...) or PubIA(api_key=...) first.",
            )

    def _request(self, path: str, body: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a request to the Pub-IA API."""
        self._ensure_initialized()

        headers: MutableMapping[str, str] = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        if self._app_id:
            headers["X-PubIA-App-Id"] = self._app_id

        try:
            response = self._session.post(
                _build_url(self._endpoint, path),
                json=_strip_none(body),
                headers=headers,
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            raise PubIAError(f"Request to Pub-IA failed: {exc}") from exc

        if response.status_code == 204:
            return None

        payload = _parse_response_body(response)
        if not response.ok:
            raise PubIAError(
                _get_error_message(response.status_code, payload),
                status=response.status_code,
                details=payload,
            )

        if payload is None:
            return None

        if not isinstance(payload, Mapping):
            raise PubIAError(
                f"Unexpected response payload from {path}",
                status=response.status_code,
                details=payload,
            )

        return dict(payload)

    def analyze_intent(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a prompt to detect purchase intent.
        Returns: {"has_intent": bool, "intent": str|None, "confidence": float,
                  "category": str|None, "intent_id": str|None}
        """
        normalized_prompt = prompt.strip() if isinstance(prompt, str) else ""
        if not normalized_prompt:
            raise PubIAError("prompt is required")

        if self._debug:
            print(f"[PubIA] analyze_intent: {normalized_prompt[:50]}")

        result = self._request(
            "/analyze-intent",
            {"prompt": normalized_prompt, "context": context},
        )
        if result is None:
            raise PubIAError("Unexpected empty response from /analyze-intent")

        return _map_intent_result(result)

    def get_ad(self, intent_result: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get the winning ad for a given intent.
        Returns: {"native_text": str, "impression_id": str, ...} or None
        """
        has_intent = intent_result.get("has_intent")
        if has_intent is None:
            has_intent = intent_result.get("hasIntent")

        intent = intent_result.get("intent")
        if not has_intent or not intent:
            return None

        intent_id = intent_result.get("intent_id")
        if intent_id is None:
            intent_id = intent_result.get("intentId")

        if self._debug:
            print(f"[PubIA] get_ad for intent: {intent}")

        result = self._request(
            "/get-ad",
            {
                "intent": intent,
                "intent_id": intent_id,
                "confidence": intent_result.get("confidence", 0.0),
            },
        )
        if result is None:
            return None

        return _map_ad_result(result)

    def track_click(self, impression_id: str) -> bool:
        """Log a click on an ad impression."""
        normalized_impression_id = impression_id.strip() if isinstance(impression_id, str) else ""
        if not normalized_impression_id:
            raise PubIAError("impression_id is required")

        if self._debug:
            print(f"[PubIA] track_click: {normalized_impression_id}")

        result = self._request("/track-click", {"impression_id": normalized_impression_id})
        return bool(result and result.get("tracked"))


pub_ia = PubIA()

__all__ = [
    "DEFAULT_ENDPOINT",
    "DEFAULT_TIMEOUT",
    "PubIA",
    "PubIAError",
    "pub_ia",
]

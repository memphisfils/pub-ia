from __future__ import annotations

import os
from typing import Any

DEFAULT_SECRET_KEY = "dev-secret-change-me"


def build_config() -> dict[str, Any]:
    environment = _resolve_environment()
    config: dict[str, Any] = {
        "APP_NAME": "pub-ia",
        "APP_ENV": environment,
        "DEBUG": environment == "development",
        "TESTING": environment == "testing",
        "JSON_SORT_KEYS": False,
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "REDIS_URL": os.getenv("REDIS_URL"),
        "SECRET_KEY": os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY),
        # Flask
        "FLASK_PORT": int(os.getenv("FLASK_PORT", "8000")),
        # LLM (OpenAI or Ollama Cloud)
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OLLAMA_API_KEY": os.getenv("OLLAMA_API_KEY", ""),
        "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL", "https://ollama.com"),
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "openai"),  # "openai" or "ollama"
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL", "llama3.2"),
        "OPENAI_TIMEOUT": int(os.getenv("OPENAI_TIMEOUT", "8")),
        "OPENAI_MAX_TOKENS": int(os.getenv("OPENAI_MAX_TOKENS", "150")),
        # Google OAuth2
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", ""),
        "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "GOOGLE_REDIRECT_URI": os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"),
        # Pub-IA
        "PUBIA_INTENT_THRESHOLD": float(os.getenv("PUBIA_INTENT_THRESHOLD", "0.65")),
        "PUBIA_PUBLISHER_SHARE": float(os.getenv("PUBIA_PUBLISHER_SHARE", "0.70")),
        "PUBIA_MIN_PAYOUT": float(os.getenv("PUBIA_MIN_PAYOUT", "50.00")),
        # Frontend
        "FRONTEND_URL": os.getenv("FRONTEND_URL", "http://localhost:5173"),
        # Sentry
        "SENTRY_DSN": os.getenv("SENTRY_DSN", ""),
    }
    return config


def _resolve_environment() -> str:
    debug_enabled = _env_flag("PUBIA_DEBUG", fallback="FLASK_DEBUG", default=False)
    configured = os.getenv("PUBIA_ENV") or os.getenv("FLASK_ENV")

    if not configured:
        return "development" if debug_enabled else "production"

    environment = configured.strip().lower()

    if environment not in {"development", "testing", "production"}:
        raise RuntimeError(
            "Unsupported PUBIA_ENV. Expected one of: development, testing, production.",
        )

    return environment


def _env_flag(name: str, fallback: str | None = None, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None and fallback:
        value = os.getenv(fallback)

    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}

from pathlib import Path
import sys

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from pubia import create_app


class StubService:
    def __init__(self, status: str, detail: str) -> None:
        self._payload = {"status": status, "detail": detail}

    def ping(self) -> dict[str, str]:
        return self._payload


@pytest.fixture()
def app():
    application = create_app(
        {
            "APP_ENV": "testing",
            "TESTING": True,
            "SECRET_KEY": "test-secret",
        },
        service_overrides={
            "database": StubService("ok", "database stub reachable"),
            "redis": StubService("ok", "redis stub reachable"),
        },
    )
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()

from pubia import create_app


def test_health_endpoint_returns_ok_with_db_and_redis(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert "db" in response.json
    assert "redis" in response.json


def test_production_runtime_requires_explicit_secret_key() -> None:
    try:
        create_app({
            "APP_ENV": "production",
            "DEBUG": False,
            "TESTING": False,
            "SECRET_KEY": "dev-secret-change-me",
        })
    except RuntimeError as exc:
        assert str(exc) == "SECRET_KEY must be set for non-debug runtimes."
    else:
        raise AssertionError("expected production runtime validation to fail")


def test_production_runtime_requires_database_url() -> None:
    try:
        create_app(
            {
                "APP_ENV": "production",
                "DEBUG": False,
                "TESTING": False,
                "SECRET_KEY": "production-secret",
                "DATABASE_URL": None,
                "REDIS_URL": "redis://localhost:6379/0",
            },
        )
    except RuntimeError as exc:
        assert (
            str(exc)
            == "Missing required runtime settings for non-debug runtimes: DATABASE_URL."
        )
    else:
        raise AssertionError("expected production runtime validation to fail")


def test_production_runtime_requires_redis_url() -> None:
    try:
        create_app(
            {
                "APP_ENV": "production",
                "DEBUG": False,
                "TESTING": False,
                "SECRET_KEY": "production-secret",
                "DATABASE_URL": "postgresql+psycopg://pubia:pubia@localhost:5432/pubia",
                "REDIS_URL": None,
            },
        )
    except RuntimeError as exc:
        assert (
            str(exc)
            == "Missing required runtime settings for non-debug runtimes: REDIS_URL."
        )
    else:
        raise AssertionError("expected production runtime validation to fail")

def test_google_login_returns_503_when_oauth_not_configured(client) -> None:
    response = client.get("/auth/google")

    assert response.status_code == 503
    assert response.get_json() == {"error": "Google OAuth is not configured"}

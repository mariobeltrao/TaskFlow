from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.security.http import SecurityMiddleware, auth_rate_limiter, install_spa
from tests.conftest import login


def production_settings(**overrides) -> Settings:
    values = {
        "environment": "production",
        "database_url": "postgresql://user:password@db/taskflow",
        "secret_key": "a-production-secret-with-more-than-thirty-two-characters",
        "cookie_secure": True,
        "frontend_url": "https://taskflow.example.com",
        "cors_origins": ["https://taskflow.example.com"],
    }
    return Settings(**(values | overrides), _env_file=None)


@pytest.mark.parametrize("secret", ["", "development-only-change-me"])
def test_production_rejects_unsafe_secret(secret):
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        production_settings(secret_key=secret)


def test_production_rejects_sqlite_and_insecure_cookie():
    with pytest.raises(ValidationError, match="SQLite"):
        production_settings(database_url="sqlite:///production.db")
    with pytest.raises(ValidationError, match="COOKIE_SECURE"):
        production_settings(cookie_secure=False)


def test_security_headers_and_origin_protection():
    test_app = FastAPI()
    test_app.add_middleware(SecurityMiddleware, settings=production_settings())

    @test_app.post("/change")
    def change():
        return {"changed": True}

    with TestClient(test_app) as test_client:
        blocked = test_client.post("/change", headers={"Origin": "https://evil.example"})
        allowed = test_client.post(
            "/change", headers={"Origin": "https://taskflow.example.com"}
        )
        assert blocked.status_code == 403
        assert allowed.status_code == 200
        assert allowed.headers["x-content-type-options"] == "nosniff"
        assert "frame-ancestors 'none'" in allowed.headers["content-security-policy"]
        assert "strict-transport-security" in allowed.headers


def test_api_404_health_and_member_authorization(client):
    assert client.get("/api/missing").status_code == 404
    assert client.get("/api/missing").headers["content-type"].startswith("application/json")
    assert client.get("/api/health").json() == {"status": "ok"}
    login(client, "member@test.com")
    assert client.post(
        "/api/tasks",
        json={
            "title": "Bloqueada",
            "category": "Segurança",
            "due_date": "2026-09-20",
            "priority": "MEDIUM",
            "status": "PENDING",
        },
    ).status_code == 403


def test_login_rate_limit(client, monkeypatch):
    settings = production_settings(auth_rate_limit_attempts=2)
    monkeypatch.setattr("app.api.auth.get_settings", lambda: settings)
    auth_rate_limiter.clear()
    credentials = {"email": "missing@example.com", "password": "wrong-password"}
    assert client.post("/api/auth/login", json=credentials).status_code == 401
    assert client.post("/api/auth/login", json=credentials).status_code == 401
    assert client.post("/api/auth/login", json=credentials).status_code == 429


def test_spa_fallback_and_assets(tmp_path: Path):
    dist = tmp_path / "dist"
    assets = dist / "assets"
    assets.mkdir(parents=True)
    (dist / "index.html").write_text("<html>TaskFlow SPA</html>", encoding="utf-8")
    (assets / "app.js").write_text("console.log('taskflow')", encoding="utf-8")
    test_app = FastAPI()
    install_spa(test_app, dist)
    with TestClient(test_app) as test_client:
        assert "TaskFlow SPA" in test_client.get("/app").text
        assert "TaskFlow SPA" in test_client.get("/login").text
        assert test_client.get("/assets/app.js").status_code == 200
        missing_api = test_client.get("/api/does-not-exist")
        assert missing_api.status_code == 404
        assert missing_api.headers["content-type"].startswith("application/json")

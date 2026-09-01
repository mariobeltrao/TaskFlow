import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-not-for-production-use-only-123456789"
os.environ["GOOGLE_TOKEN_ENCRYPTION_KEY"] = "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="
os.environ["GOOGLE_CALENDAR_WEBHOOK_TOKEN"] = "test-webhook-token"
os.environ["CLASSROOM_BRIDGE_TOKEN"] = "test-bridge-token"
os.environ["CLASSROOM_BRIDGE_ADMIN_EMAIL"] = "admin@test.com"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.models.enums import UserRole
from app.models.user import User
from app.security.passwords import hash_password

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestingSession() as db:
        db.add_all(
            [
                User(
                    name="Admin",
                    email="admin@test.com",
                    password_hash=hash_password("password123"),
                    role=UserRole.ADMIN,
                ),
                User(
                    name="Member",
                    email="member@test.com",
                    password_hash=hash_password("password123"),
                    role=UserRole.MEMBER,
                ),
            ]
        )
        db.commit()

    def override_db():
        with TestingSession() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as value:
        yield value
    app.dependency_overrides.clear()


def login(client, email="admin@test.com"):
    response = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    assert response.status_code == 200

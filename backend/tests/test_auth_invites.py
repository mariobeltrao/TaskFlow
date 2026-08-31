from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.models.enums import UserRole
from app.models.member_invite import MemberInvite
from app.models.user import User
from app.security.invite_tokens import hash_invite_token
from app.security.passwords import verify_password
from tests.conftest import TestingSession, login


def create_invite(client, email="student@example.com", expires_days=7):
    login(client)
    response = client.post(
        "/api/auth/member-invites", json={"email": email, "expires_days": expires_days}
    )
    assert response.status_code == 201
    client.post("/api/auth/logout")
    return response.json()["invite_code"]


def registration_payload(token: str, email="student@example.com") -> dict[str, str]:
    return {
        "name": "Student",
        "email": email,
        "invite_code": token,
        "password": "student-password",
        "password_confirmation": "student-password",
    }


def test_valid_invite_creates_member_with_hashed_password(client):
    token = create_invite(client)
    response = client.post("/api/auth/register-member", json=registration_payload(token))
    assert response.status_code == 201
    assert response.json()["role"] == "MEMBER"
    with TestingSession() as db:
        user = db.scalar(select(User).where(User.email == "student@example.com"))
        invite = db.scalar(select(MemberInvite).where(MemberInvite.email == user.email))
        assert user.role == UserRole.MEMBER
        assert user.password_hash != "student-password"
        assert verify_password("student-password", user.password_hash)
        assert invite.used_at is not None
        assert invite.token_hash == hash_invite_token(token)
        assert token != invite.token_hash


def test_invalid_expired_reused_and_wrong_email_invites_are_rejected(client):
    assert client.post(
        "/api/auth/register-member", json=registration_payload("x" * 43)
    ).status_code == 400

    token = create_invite(client, "right@example.com")
    wrong = client.post(
        "/api/auth/register-member", json=registration_payload(token, "wrong@example.com")
    )
    assert wrong.status_code == 400
    valid = client.post(
        "/api/auth/register-member", json=registration_payload(token, "right@example.com")
    )
    assert valid.status_code == 201
    assert client.post(
        "/api/auth/register-member", json=registration_payload(token, "right@example.com")
    ).status_code == 400

    expired_token = create_invite(client, "late@example.com")
    with TestingSession() as db:
        invite = db.scalar(select(MemberInvite).where(MemberInvite.email == "late@example.com"))
        invite.expires_at = datetime.now(UTC) - timedelta(minutes=1)
        db.commit()
    assert client.post(
        "/api/auth/register-member", json=registration_payload(expired_token, "late@example.com")
    ).status_code == 400


def test_registration_rejects_role_and_admin_invite_routes_reject_member(client):
    token = create_invite(client)
    with_role = registration_payload(token) | {"role": "ADMIN"}
    assert client.post("/api/auth/register-member", json=with_role).status_code == 422

    login(client, "member@test.com")
    assert client.post(
        "/api/auth/member-invites", json={"email": "other@example.com"}
    ).status_code == 403
    assert client.get("/api/auth/member-invites").status_code == 403


def test_member_can_read_but_cannot_mutate_any_task(client):
    login(client)
    task = client.post(
        "/api/tasks",
        json={
            "title": "Read only",
            "category": "Tests",
            "due_date": "2026-09-01",
            "priority": "MEDIUM",
            "status": "PENDING",
        },
    ).json()
    client.post("/api/auth/logout")
    login(client, "member@test.com")
    assert client.get("/api/tasks").status_code == 200
    assert client.get("/api/dashboard/summary").status_code == 200
    assert client.patch(f"/api/tasks/{task['id']}", json={"status": "COMPLETED"}).status_code == 403
    assert client.delete(f"/api/tasks/{task['id']}").status_code == 403

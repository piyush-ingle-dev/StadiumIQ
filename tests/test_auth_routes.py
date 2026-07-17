"""Tests for authentication routes."""

from app.models import User


class TestRegister:
    def test_get_register_page_loads(self, client):
        response = client.get("/auth/register")
        assert response.status_code == 200

    def test_register_creates_user(self, client, db):
        response = client.post(
            "/auth/register",
            data={"name": "New User", "email": "new@example.com", "password": "password123", "role": "fan"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert User.query.filter_by(email="new@example.com").first() is not None

    def test_register_rejects_short_password(self, client):
        client.post(
            "/auth/register",
            data={"name": "New User", "email": "short@example.com", "password": "123", "role": "fan"},
        )
        assert User.query.filter_by(email="short@example.com").first() is None

    def test_register_rejects_duplicate_email(self, client, fan_user):
        response = client.post(
            "/auth/register",
            data={"name": "Dup", "email": fan_user.email, "password": "password123", "role": "fan"},
        )
        assert response.status_code == 200
        assert User.query.filter_by(email=fan_user.email).count() == 1

    def test_register_invalid_role_defaults_to_fan(self, client, db):
        client.post(
            "/auth/register",
            data={"name": "R", "email": "roletest@example.com", "password": "password123", "role": "admin"},
        )
        user = User.query.filter_by(email="roletest@example.com").first()
        assert user.role == "fan"


class TestLogin:
    def test_get_login_page_loads(self, client):
        response = client.get("/auth/login")
        assert response.status_code == 200

    def test_login_with_correct_credentials(self, client, fan_user):
        response = client.post(
            "/auth/login",
            data={"email": fan_user.email, "password": "password123"},
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_login_with_wrong_password_fails(self, client, fan_user):
        response = client.post(
            "/auth/login",
            data={"email": fan_user.email, "password": "wrongpassword"},
        )
        assert b"Invalid email or password" in response.data

    def test_login_with_unknown_email_fails(self, client):
        response = client.post(
            "/auth/login",
            data={"email": "nobody@example.com", "password": "password123"},
        )
        assert b"Invalid email or password" in response.data


class TestLogout:
    def test_logout_requires_login(self, client):
        response = client.get("/auth/logout")
        assert response.status_code in (302, 401)

    def test_logout_redirects_to_home(self, fan_client):
        response = fan_client.get("/auth/logout", follow_redirects=True)
        assert response.status_code == 200

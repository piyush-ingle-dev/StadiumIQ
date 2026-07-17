"""Shared pytest fixtures for the StadiumIQ test suite."""

from __future__ import annotations

import pytest

from app import create_app
from app.extensions import db as _db
from app.models import User


@pytest.fixture()
def app():
    """Create a fresh app instance backed by an in-memory database for each test."""
    application = create_app("testing")

    with application.app_context():
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    """Flask test client for making requests against the app."""
    return app.test_client()


@pytest.fixture()
def db(app):
    """Direct access to the SQLAlchemy db instance within the app context."""
    return _db


@pytest.fixture()
def fan_user(db):
    """Create and return a plain 'fan' role user."""
    user = User(name="Fan User", email="fan@example.com", role="fan")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def volunteer_user(db):
    """Create and return a 'volunteer' role user."""
    user = User(name="Volunteer User", email="volunteer@example.com", role="volunteer")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def admin_user(db):
    """Create and return an 'admin' role user."""
    user = User(name="Admin User", email="admin@example.com", role="admin")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


def login(client, email: str, password: str = "password123"):
    """Helper to log a test client in via the auth form."""
    return client.post(
        "/auth/login", data={"email": email, "password": password}, follow_redirects=True
    )


@pytest.fixture()
def fan_client(client, fan_user):
    """Test client already logged in as a fan."""
    login(client, fan_user.email)
    return client


@pytest.fixture()
def volunteer_client(client, volunteer_user):
    """Test client already logged in as a volunteer."""
    login(client, volunteer_user.email)
    return client


@pytest.fixture()
def admin_client(client, admin_user):
    """Test client already logged in as an admin."""
    login(client, admin_user.email)
    return client

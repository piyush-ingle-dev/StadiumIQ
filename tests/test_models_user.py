"""Tests for the User model."""

from app.models import User


class TestUserPasswordHandling:
    def test_set_password_hashes_value(self, db):
        user = User(name="Test", email="a@example.com", role="fan")
        user.set_password("mypassword")
        assert user.password_hash != "mypassword"

    def test_check_password_correct(self, db):
        user = User(name="Test", email="a@example.com", role="fan")
        user.set_password("mypassword")
        assert user.check_password("mypassword") is True

    def test_check_password_incorrect(self, db):
        user = User(name="Test", email="a@example.com", role="fan")
        user.set_password("mypassword")
        assert user.check_password("wrongpassword") is False

    def test_check_password_empty_string(self, db):
        user = User(name="Test", email="a@example.com", role="fan")
        user.set_password("mypassword")
        assert user.check_password("") is False


class TestUserDefaults:
    def test_default_role_is_fan(self, db):
        user = User(name="Test", email="b@example.com")
        user.set_password("x")
        db.session.add(user)
        db.session.commit()
        assert user.role == "fan"

    def test_default_language_is_en(self, db):
        user = User(name="Test", email="c@example.com")
        user.set_password("x")
        db.session.add(user)
        db.session.commit()
        assert user.preferred_language == "en"

    def test_created_at_is_set(self, db):
        user = User(name="Test", email="d@example.com")
        user.set_password("x")
        db.session.add(user)
        db.session.commit()
        assert user.created_at is not None


class TestUserToDict:
    def test_to_dict_excludes_password_hash(self, db):
        user = User(name="Test", email="e@example.com", role="admin")
        user.set_password("secret")
        data = user.to_dict()
        assert "password_hash" not in data

    def test_to_dict_includes_expected_fields(self, db):
        user = User(name="Test", email="f@example.com", role="admin")
        user.set_password("secret")
        db.session.add(user)
        db.session.commit()
        data = user.to_dict()
        assert data["email"] == "f@example.com"
        assert data["role"] == "admin"

    def test_repr_contains_email(self, db):
        user = User(name="Test", email="g@example.com", role="fan")
        assert "g@example.com" in repr(user)

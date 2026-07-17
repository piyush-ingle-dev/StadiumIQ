"""Application configuration classes.

Configuration is split by environment (development, testing, production)
so the same codebase behaves correctly whether it is running on a
developer machine, inside the pytest suite, or on Render.
"""

from __future__ import annotations

import os
from datetime import timedelta


class BaseConfig:
    """Shared configuration values used by every environment."""

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Caching
    CACHE_TYPE: str = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT: int = 300

    # OpenAI / GPT-4o
    OPENAI_API_KEY: str | None = os.environ.get("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL", "gpt-4o")

    # Rate limiting
    RATELIMIT_DEFAULT: str = "200 per hour"
    RATELIMIT_STORAGE_URI: str = "memory://"

    # Session security
    PERMANENT_SESSION_LIFETIME = timedelta(hours=6)
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"

    # Supported languages for multilingual assistance
    SUPPORTED_LANGUAGES: list[str] = ["en", "hi", "ar", "es", "fr"]
    DEFAULT_LANGUAGE: str = "en"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///stadiumiq.db")
    SESSION_COOKIE_SECURE = False


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    RATELIMIT_ENABLED = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///stadiumiq.db")
    SESSION_COOKIE_SECURE = True


CONFIG_MAP: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env_name: str | None = None) -> type[BaseConfig]:
    """Return the configuration class for the given environment name.

    Args:
        env_name: One of "development", "testing", "production". Falls
            back to the FLASK_ENV environment variable, then to
            "development" if nothing is set.

    Returns:
        The configuration class to load into the Flask app.
    """
    resolved_name: str = env_name or os.environ.get("FLASK_ENV") or "development"
    return CONFIG_MAP.get(resolved_name, DevelopmentConfig)

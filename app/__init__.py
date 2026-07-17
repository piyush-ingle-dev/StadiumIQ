"""Application factory for StadiumIQ.

Builds and configures the Flask app: extensions, security headers,
blueprints, and CLI commands. Kept as a single `create_app` entry
point so tests and `wsgi.py` both construct the app the same way.
"""

from __future__ import annotations

import logging
import os

from flask import Flask
from flask_talisman import Talisman

from app.config import get_config
from app.extensions import cache, db, limiter, login_manager

# Content Security Policy: only allow same-origin scripts/styles plus
# the one CDN we use for icons. No inline event handlers, no
# third-party trackers.
_CSP_POLICY = {
    "default-src": "'self'",
    "script-src": "'self'",
    "style-src": "'self' 'unsafe-inline'",
    "img-src": "'self' data:",
    "font-src": "'self'",
    "connect-src": "'self'",
}


def create_app(config_name: str | None = None) -> Flask:
    """Build and configure the Flask application.

    Args:
        config_name: One of "development", "testing", "production".
            Defaults to the FLASK_ENV environment variable.

    Returns:
        A fully configured Flask app instance.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(get_config(config_name))

    os.makedirs(app.instance_path, exist_ok=True)

    _init_extensions(app)
    _register_blueprints(app)
    _register_cli(app)
    _configure_logging(app)

    return app


def _init_extensions(app: Flask) -> None:
    """Wire up all Flask extensions onto the app instance."""
    db.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access that page."
    login_manager.login_message_category = "info"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    # Security headers on every response. HTTPS is only force-enabled
    # outside testing/development so local runs aren't broken.
    force_https = not (app.config.get("TESTING") or app.config.get("DEBUG"))
    Talisman(
        app,
        content_security_policy=_CSP_POLICY,
        force_https=force_https,
        strict_transport_security=force_https,
        session_cookie_secure=force_https,
    )

    with app.app_context():
        db.create_all()


def _register_blueprints(app: Flask) -> None:
    """Register every route blueprint on the app."""
    from app.blueprints import (
        auth,
        crowd,
        insights,
        main,
        multilingual,
        navigation,
        staff,
        sustainability,
        transport,
    )

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(navigation.bp)
    app.register_blueprint(crowd.bp)
    app.register_blueprint(transport.bp)
    app.register_blueprint(multilingual.bp)
    app.register_blueprint(staff.bp)
    app.register_blueprint(sustainability.bp)
    app.register_blueprint(insights.bp)


def _register_cli(app: Flask) -> None:
    """Register custom `flask` CLI commands, e.g. `flask seed-demo-data`."""

    @app.cli.command("seed-demo-data")
    def seed_demo_data() -> None:
        """Populate the database with demo zones, tasks, and an admin user."""
        from app.models import User
        from app.services import crowd_service, staff_service, sustainability_service

        if User.query.filter_by(email="admin@stadiumiq.demo").first() is None:
            admin = User(name="Demo Admin", email="admin@stadiumiq.demo", role="admin")
            admin.set_password("ChangeMe123!")
            db.session.add(admin)
            db.session.commit()

        for zone, count in [("Gate A", 120), ("Gate B", 480), ("Section 114", 720)]:
            crowd_service.record_report(zone, count, source="seed")

        staff_service.create_task("Restock first-aid kit", "Gate C", priority="high")
        sustainability_service.log_metric("electricity_kwh", 500, zone="stadium-wide")

        print("Demo data seeded.")


def _configure_logging(app: Flask) -> None:
    """Set a sensible default logging level in production."""
    if not app.debug and not app.testing:
        logging.basicConfig(level=logging.INFO)

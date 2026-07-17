"""Landing page and role-aware dashboard."""

from __future__ import annotations

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.services import crowd_service, staff_service, sustainability_service

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Public landing page introducing StadiumIQ."""
    return render_template("index.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    """Role-aware dashboard: fans see zone status, staff see their tasks."""
    zones_at_risk = crowd_service.zones_needing_attention()

    context = {
        "zones_at_risk": zones_at_risk,
    }

    if current_user.role in ("volunteer", "admin"):
        context["open_task_count"] = staff_service.open_task_count()

    if current_user.role == "admin":
        context["total_emissions_kg"] = sustainability_service.total_emissions_kg()

    return render_template("dashboard.html", **context)


@bp.route("/healthz")
def healthz():
    """Lightweight health check endpoint for uptime monitoring."""
    return {"status": "ok"}, 200

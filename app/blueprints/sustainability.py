"""Sustainability tracking routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required

from app.models import EMISSION_FACTORS
from app.services import sustainability_service
from app.utils.decorators import role_required

bp = Blueprint("sustainability", __name__, url_prefix="/sustainability")


@bp.route("/")
@login_required
def index():
    """Render the sustainability dashboard."""
    return render_template(
        "sustainability.html",
        totals=sustainability_service.emissions_by_category(),
        grand_total=sustainability_service.total_emissions_kg(),
    )


@bp.route("/api/log", methods=["POST"])
@login_required
@role_required("admin")
def log_metric():
    """Record a new sustainability metric entry.

    Restricted to admin role. Expects JSON body:
    {"category": str, "quantity": float, "zone": str}
    """
    data = request.get_json(silent=True) or {}
    category = data.get("category", "")
    zone = data.get("zone", "stadium-wide")

    try:
        quantity = float(data.get("quantity", -1))
    except (TypeError, ValueError):
        return jsonify({"error": "quantity must be a number."}), 400

    try:
        entry = sustainability_service.log_metric(category, quantity, zone=zone)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(entry.to_dict()), 201


@bp.route("/api/summary")
@login_required
def summary():
    """Return total and per-category emissions estimates as JSON."""
    return jsonify(
        {
            "total_kg": sustainability_service.total_emissions_kg(),
            "by_category": sustainability_service.emissions_by_category(),
            "factors": EMISSION_FACTORS,
        }
    )

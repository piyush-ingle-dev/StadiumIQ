"""Transport recommendation routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required

from app.services import transport_service

bp = Blueprint("transport", __name__, url_prefix="/transport")


@bp.route("/")
@login_required
def index():
    """Render the transport recommendation page."""
    return render_template("transport.html")


@bp.route("/api/recommend")
@login_required
def recommend():
    """Return recommended transport options for a given distance.

    Query param: distance_km (float)
    """
    raw_distance = request.args.get("distance_km", "")
    try:
        distance_km = float(raw_distance)
    except ValueError:
        return jsonify({"error": "distance_km must be a number."}), 400

    if distance_km < 0:
        return jsonify({"error": "distance_km cannot be negative."}), 400

    options = transport_service.recommend_options(distance_km)
    return jsonify([option.__dict__ for option in options])

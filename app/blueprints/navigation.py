"""Fan navigation assistance routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required

from app.services.ai_service import get_navigation_guidance
from app.utils.security import clean_text

bp = Blueprint("navigation", __name__, url_prefix="/navigation")


@bp.route("/")
@login_required
def index():
    """Render the navigation assistant page."""
    return render_template("navigation.html")


@bp.route("/api/guide", methods=["POST"])
@login_required
def guide():
    """Return step-by-step directions between two stadium zones as JSON.

    Expects JSON body: {"from": str, "to": str, "language": str}
    """
    data = request.get_json(silent=True) or {}
    current_zone = clean_text(data.get("from", ""), max_length=100)
    destination = clean_text(data.get("to", ""), max_length=100)
    language = clean_text(data.get("language", "en"), max_length=5) or "en"

    if not current_zone or not destination:
        return jsonify({"error": "Both 'from' and 'to' are required."}), 400

    guidance = get_navigation_guidance(current_zone, destination, language)
    return jsonify({"from": current_zone, "to": destination, "guidance": guidance})

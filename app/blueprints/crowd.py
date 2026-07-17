"""Real-time crowd density routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app.services import crowd_service
from app.utils.security import clean_text

bp = Blueprint("crowd", __name__, url_prefix="/crowd")


@bp.route("/")
@login_required
def index():
    """Render the crowd density overview page."""
    latest = crowd_service.latest_by_zone()
    return render_template("crowd.html", latest=latest)


@bp.route("/api/report", methods=["POST"])
@login_required
def report():
    """Submit a new crowd density observation for a zone.

    Restricted to volunteer/admin roles since it writes operational data.
    Expects JSON body: {"zone": str, "people_estimate": int, "source": str}
    """
    if current_user.role not in ("volunteer", "admin"):
        return jsonify({"error": "Only staff can submit crowd reports."}), 403

    data = request.get_json(silent=True) or {}
    zone = clean_text(data.get("zone", ""), max_length=80)
    source = clean_text(data.get("source", "manual"), max_length=20) or "manual"

    try:
        people_estimate = int(data.get("people_estimate", -1))
    except (TypeError, ValueError):
        return jsonify({"error": "people_estimate must be an integer."}), 400

    if not zone or people_estimate < 0:
        return jsonify({"error": "A zone name and a non-negative people_estimate are required."}), 400

    created = crowd_service.record_report(zone, people_estimate, source=source)
    return jsonify(created.to_dict()), 201


@bp.route("/api/status")
@login_required
def status():
    """Return the latest density reading for every zone as JSON."""
    latest = crowd_service.latest_by_zone()
    return jsonify({zone: report.to_dict() for zone, report in latest.items()})

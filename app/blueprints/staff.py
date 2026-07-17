"""Volunteer/staff task management routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required

from app.services import staff_service
from app.utils.decorators import role_required
from app.utils.security import clean_text

bp = Blueprint("staff", __name__, url_prefix="/staff")


@bp.route("/")
@login_required
@role_required("volunteer", "admin")
def index():
    """Render the staff task board."""
    return render_template("staff.html")


@bp.route("/api/tasks", methods=["POST"])
@login_required
@role_required("volunteer", "admin")
def create_task():
    """Create a new operational task.

    Expects JSON body: {"title": str, "zone": str, "description": str,
    "priority": str, "assignee_id": int}
    """
    data = request.get_json(silent=True) or {}
    title = clean_text(data.get("title", ""), max_length=200)
    zone = clean_text(data.get("zone", ""), max_length=80)
    description = clean_text(data.get("description", ""), max_length=1000)
    priority = clean_text(data.get("priority", "medium"), max_length=20) or "medium"
    assignee_id = data.get("assignee_id")

    if not title or not zone:
        return jsonify({"error": "title and zone are required."}), 400

    try:
        task = staff_service.create_task(
            title=title,
            zone=zone,
            description=description or None,
            priority=priority,
            assignee_id=assignee_id,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(task.to_dict()), 201


@bp.route("/api/tasks/<int:task_id>/status", methods=["PATCH"])
@login_required
@role_required("volunteer", "admin")
def change_status(task_id: int):
    """Update a task's status.

    Expects JSON body: {"status": str}
    """
    data = request.get_json(silent=True) or {}
    status = clean_text(data.get("status", ""), max_length=20)

    try:
        task = staff_service.update_status(task_id, status)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(task.to_dict())


@bp.route("/api/tasks")
@login_required
@role_required("volunteer", "admin")
def list_tasks():
    """List tasks for a given zone via ?zone= query param."""
    zone = request.args.get("zone", "")
    if not zone:
        return jsonify({"error": "zone query parameter is required."}), 400

    tasks = staff_service.tasks_for_zone(zone)
    return jsonify([task.to_dict() for task in tasks])

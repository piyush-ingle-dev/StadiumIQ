"""Volunteer/staff task management business logic."""

from __future__ import annotations

from app.extensions import db
from app.models import TASK_PRIORITIES, TASK_STATUSES, StaffTask


def create_task(
    title: str,
    zone: str,
    description: str | None = None,
    priority: str = "medium",
    assignee_id: int | None = None,
) -> StaffTask:
    """Create a new operational task.

    Args:
        title: Short task summary.
        zone: Stadium zone the task applies to.
        description: Optional longer explanation.
        priority: One of TASK_PRIORITIES.
        assignee_id: Optional user id of the assigned staff member.

    Returns:
        The newly created StaffTask.

    Raises:
        ValueError: If priority is not a recognized value.
    """
    if priority not in TASK_PRIORITIES:
        raise ValueError(f"Unknown priority: {priority!r}")

    task = StaffTask(
        title=title,
        zone=zone,
        description=description,
        priority=priority,
        assignee_id=assignee_id,
    )
    db.session.add(task)
    db.session.commit()
    return task


def update_status(task_id: int, status: str) -> StaffTask:
    """Update a task's status.

    Args:
        task_id: The id of the task to update.
        status: One of TASK_STATUSES.

    Returns:
        The updated StaffTask.

    Raises:
        ValueError: If the task doesn't exist or status is invalid.
    """
    if status not in TASK_STATUSES:
        raise ValueError(f"Unknown status: {status!r}")

    task = db.session.get(StaffTask, task_id)
    if task is None:
        raise ValueError(f"No task with id {task_id}")

    if status == "completed":
        task.mark_completed()
    else:
        task.status = status

    db.session.commit()
    return task


def tasks_for_zone(zone: str) -> list[StaffTask]:
    """Return all tasks for a given stadium zone, most recent first."""
    return (
        StaffTask.query.filter_by(zone=zone)
        .order_by(StaffTask.created_at.desc())
        .all()
    )


def open_task_count() -> int:
    """Return the number of tasks that are not completed or cancelled."""
    return StaffTask.query.filter(
        StaffTask.status.in_(["pending", "in_progress"])
    ).count()

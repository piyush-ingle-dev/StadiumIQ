"""Staff and volunteer task management model."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db

TASK_STATUSES = ("pending", "in_progress", "completed", "cancelled")
TASK_PRIORITIES = ("low", "medium", "high", "urgent")


class StaffTask(db.Model):  # type: ignore[name-defined]
    """An operational task assigned to a volunteer or staff member.

    Examples: "Restock first-aid kit at Gate C", "Clear blocked
    walkway near Section 12", "Assist wheelchair patrons at Gate A".
    """

    __tablename__ = "staff_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    zone: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    assignee_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def mark_completed(self) -> None:
        """Transition the task to completed and stamp the time."""
        self.status = "completed"
        self.completed_at = datetime.now(UTC)

    def to_dict(self) -> dict:
        """Serialize the task for JSON API responses."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "zone": self.zone,
            "status": self.status,
            "priority": self.priority,
            "assignee_id": self.assignee_id,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<StaffTask {self.title!r} status={self.status!r}>"

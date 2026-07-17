"""User account model."""

from __future__ import annotations

from datetime import UTC, datetime

from flask_login import UserMixin
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):  # type: ignore[name-defined]
    """A registered user of the StadiumIQ platform.

    Roles determine which features a user can access:
    - "fan": general attendee, gets navigation/crowd/transport tools.
    - "volunteer": staff member, gets the task management dashboard.
    - "admin": full access, including sustainability reporting.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="fan")
    preferred_language: Mapped[str] = mapped_column(String(5), nullable=False, default="en")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )

    tasks = relationship("StaffTask", backref="assignee", lazy="dynamic")

    def set_password(self, password: str) -> None:
        """Hash and store a plaintext password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        """Serialize the user for JSON API responses (never includes the hash)."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "preferred_language": self.preferred_language,
        }

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<User {self.email!r} role={self.role!r}>"

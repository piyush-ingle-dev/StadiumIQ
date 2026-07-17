"""Crowd density reporting model."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db

# Density thresholds expressed as people-per-square-meter estimates,
# following common venue-safety guidance bands.
DENSITY_LEVELS = ("low", "moderate", "high", "critical")


class CrowdReport(db.Model):  # type: ignore[name-defined]
    """A single crowd density observation for one stadium zone.

    Reports can originate from staff manual entries or from an
    automated sensor/camera feed integration (not implemented in this
    submission, but the schema supports a `source` field for it).
    """

    __tablename__ = "crowd_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    zone: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    density_level: Mapped[str] = mapped_column(String(20), nullable=False)
    people_estimate: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    reported_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC), index=True
    )

    def to_dict(self) -> dict:
        """Serialize the report for JSON API responses."""
        return {
            "id": self.id,
            "zone": self.zone,
            "density_level": self.density_level,
            "people_estimate": self.people_estimate,
            "source": self.source,
            "reported_at": self.reported_at.isoformat(),
        }

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<CrowdReport zone={self.zone!r} level={self.density_level!r}>"

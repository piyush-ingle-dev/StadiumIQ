"""Sustainability tracking model for stadium operations."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db

# Approximate emission factors (kg CO2e per unit), sourced from common
# public sustainability reporting standards. These are estimates for
# demonstration purposes, not audited figures.
EMISSION_FACTORS = {
    "electricity_kwh": 0.475,   # kg CO2e per kWh (grid average)
    "water_liter": 0.000344,    # kg CO2e per liter treated/supplied
    "waste_kg": 0.457,          # kg CO2e per kg landfill waste
    "transport_km": 0.171,      # kg CO2e per passenger-km (shuttle bus)
}


class SustainabilityLog(db.Model):  # type: ignore[name-defined]
    """A single sustainability metric entry for stadium operations.

    Each entry records a resource category and quantity for a given
    stadium zone/day, from which estimated CO2e emissions are derived.
    """

    __tablename__ = "sustainability_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False)  # key in EMISSION_FACTORS
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    zone: Mapped[str] = mapped_column(String(80), nullable=False, default="stadium-wide")
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )

    @property
    def estimated_co2e_kg(self) -> float:
        """Estimated CO2 equivalent emissions in kilograms for this entry."""
        factor = EMISSION_FACTORS.get(self.category, 0.0)
        return round(self.quantity * factor, 3)

    def to_dict(self) -> dict:
        """Serialize the log for JSON API responses."""
        return {
            "id": self.id,
            "category": self.category,
            "quantity": self.quantity,
            "zone": self.zone,
            "estimated_co2e_kg": self.estimated_co2e_kg,
            "recorded_at": self.recorded_at.isoformat(),
        }

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<SustainabilityLog {self.category!r} qty={self.quantity}>"

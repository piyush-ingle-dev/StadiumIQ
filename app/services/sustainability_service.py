"""Sustainability tracking business logic."""

from __future__ import annotations

from app.extensions import db
from app.models import EMISSION_FACTORS, SustainabilityLog


def log_metric(category: str, quantity: float, zone: str = "stadium-wide") -> SustainabilityLog:
    """Record a new sustainability metric entry.

    Args:
        category: One of the keys in EMISSION_FACTORS
            (electricity_kwh, water_liter, waste_kg, transport_km).
        quantity: The measured quantity for this entry.
        zone: Which stadium zone the metric applies to.

    Returns:
        The newly created SustainabilityLog.

    Raises:
        ValueError: If category is not recognized or quantity is negative.
    """
    if category not in EMISSION_FACTORS:
        raise ValueError(f"Unknown sustainability category: {category!r}")
    if quantity < 0:
        raise ValueError("quantity cannot be negative")

    entry = SustainabilityLog(category=category, quantity=quantity, zone=zone)
    db.session.add(entry)
    db.session.commit()
    return entry


def total_emissions_kg() -> float:
    """Return total estimated CO2e emissions across all logged entries."""
    entries = SustainabilityLog.query.all()
    return round(sum(entry.estimated_co2e_kg for entry in entries), 3)


def emissions_by_category() -> dict[str, float]:
    """Return estimated CO2e emissions grouped by category."""
    totals: dict[str, float] = dict.fromkeys(EMISSION_FACTORS, 0.0)
    for entry in SustainabilityLog.query.all():
        totals[entry.category] = round(totals.get(entry.category, 0.0) + entry.estimated_co2e_kg, 3)
    return totals

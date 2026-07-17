"""Transport recommendation logic for getting to/from the stadium.

This is a rule-based recommender rather than a live transit API
integration (out of scope for this submission), but the interface is
designed so a real transit API call could replace `_MODE_CATALOG`
lookups without changing callers.
"""

from __future__ import annotations

from dataclasses import dataclass

# Static catalog of transport options. Distance bands are in
# kilometers from the stadium.
_MODE_CATALOG: tuple[dict, ...] = (
    {"mode": "walk", "max_km": 1.5, "co2e_per_km": 0.0, "label": "Walking"},
    {"mode": "shuttle_bus", "max_km": 15, "co2e_per_km": 0.089, "label": "Official shuttle bus"},
    {"mode": "metro", "max_km": 40, "co2e_per_km": 0.041, "label": "Metro / light rail"},
    {"mode": "rideshare", "max_km": 200, "co2e_per_km": 0.171, "label": "Rideshare / taxi"},
)


@dataclass(frozen=True)
class TransportOption:
    """A single recommended way to reach the stadium."""

    mode: str
    label: str
    estimated_co2e_kg: float
    recommended: bool


def recommend_options(distance_km: float) -> list[TransportOption]:
    """Recommend transport modes for a given distance to the stadium.

    Args:
        distance_km: Distance from the fan's starting point to the venue.

    Returns:
        A list of TransportOption objects, most sustainable first,
        with the single best match flagged as `recommended`.

    Raises:
        ValueError: If distance_km is negative.
    """
    if distance_km < 0:
        raise ValueError("distance_km cannot be negative")

    eligible = [entry for entry in _MODE_CATALOG if distance_km <= entry["max_km"]]
    if not eligible:
        eligible = [_MODE_CATALOG[-1]]  # long-haul fallback: rideshare/taxi

    eligible = sorted(eligible, key=lambda entry: entry["co2e_per_km"])

    options = []
    for index, entry in enumerate(eligible):
        options.append(
            TransportOption(
                mode=entry["mode"],
                label=entry["label"],
                estimated_co2e_kg=round(entry["co2e_per_km"] * distance_km, 3),
                recommended=(index == 0),
            )
        )
    return options

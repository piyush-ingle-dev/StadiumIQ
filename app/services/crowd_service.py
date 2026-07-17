"""Crowd density business logic.

Keeps density classification and alert rules out of the route
handlers so they can be unit tested in isolation and reused by both
the web UI and JSON API.
"""

from __future__ import annotations

from app.extensions import db
from app.models import CrowdReport

# People-per-zone thresholds used to classify density automatically
# when only a raw headcount is supplied.
_THRESHOLDS = (
    (150, "low"),
    (400, "moderate"),
    (700, "high"),
)


def classify_density(people_estimate: int) -> str:
    """Map a raw headcount to a density level.

    Args:
        people_estimate: Estimated number of people in the zone.

    Returns:
        One of "low", "moderate", "high", "critical".
    """
    if people_estimate < 0:
        raise ValueError("people_estimate cannot be negative")

    for limit, level in _THRESHOLDS:
        if people_estimate < limit:
            return level
    return "critical"


def record_report(zone: str, people_estimate: int, source: str = "manual") -> CrowdReport:
    """Persist a new crowd density observation.

    Args:
        zone: Stadium zone identifier, e.g. "Gate C" or "Section 114".
        people_estimate: Estimated headcount for the zone.
        source: Where the observation came from ("manual" or "sensor").

    Returns:
        The newly created CrowdReport.
    """
    report = CrowdReport(
        zone=zone,
        people_estimate=people_estimate,
        density_level=classify_density(people_estimate),
        source=source,
    )
    db.session.add(report)
    db.session.commit()
    return report


def latest_by_zone() -> dict[str, CrowdReport]:
    """Return the most recent report for each zone that has one.

    Returns:
        A mapping of zone name to its latest CrowdReport.
    """
    reports = CrowdReport.query.order_by(CrowdReport.reported_at.desc()).all()
    latest: dict[str, CrowdReport] = {}
    for report in reports:
        if report.zone not in latest:
            latest[report.zone] = report
    return latest


def zones_needing_attention() -> list[CrowdReport]:
    """Return the latest reports for zones currently at high or critical density."""
    return [
        report
        for report in latest_by_zone().values()
        if report.density_level in ("high", "critical")
    ]

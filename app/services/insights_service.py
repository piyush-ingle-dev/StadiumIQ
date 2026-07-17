"""Operational intelligence: cross-domain snapshots and AI briefings.

This is the "real-time decision support" and "operational intelligence"
capability named in the challenge brief. It pulls together crowd
density, open staff tasks, and sustainability data into a single
snapshot, then optionally asks GPT-4o to turn that snapshot into a
short, actionable briefing for control-room staff.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from app.extensions import cache
from app.services import crowd_service, staff_service, sustainability_service
from app.services.ai_service import AIServiceError, get_completion


def build_snapshot() -> dict:
    """Assemble a single point-in-time view of stadium operations.

    Returns:
        A dict with crowd risk zones, open task counts, and running
        sustainability totals, suitable for JSON serialization or as
        input to an AI-generated briefing.
    """
    at_risk = crowd_service.zones_needing_attention()
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "zones_at_risk": [report.to_dict() for report in at_risk],
        "zones_at_risk_count": len(at_risk),
        "open_task_count": staff_service.open_task_count(),
        "total_emissions_kg": sustainability_service.total_emissions_kg(),
    }


def _snapshot_fingerprint(snapshot: dict) -> str:
    """Build a short hash of the parts of a snapshot that affect the briefing text.

    Excludes the `generated_at` timestamp so an unchanged operational
    picture reuses the cached briefing instead of re-calling the AI
    model every few seconds.
    """
    stable_parts = (
        snapshot["zones_at_risk_count"],
        tuple(sorted(z["zone"] for z in snapshot["zones_at_risk"])),
        snapshot["open_task_count"],
        snapshot["total_emissions_kg"],
    )
    return hashlib.sha256(str(stable_parts).encode("utf-8")).hexdigest()[:24]


def generate_briefing(snapshot: dict | None = None) -> str:
    """Turn an operations snapshot into a short plain-language briefing.

    Args:
        snapshot: A snapshot dict from `build_snapshot()`. Built fresh
            if not supplied.

    Returns:
        A 2-4 sentence briefing suitable for display on an ops
        dashboard. Falls back to a rule-based summary if the AI
        backend is unavailable, so this never breaks the page.
    """
    snapshot = snapshot or build_snapshot()
    cache_key = f"briefing:{_snapshot_fingerprint(snapshot)}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    briefing = _rule_based_briefing(snapshot)
    try:
        ai_briefing = _ai_briefing(snapshot)
        if ai_briefing:
            briefing = ai_briefing
    except AIServiceError:
        pass  # keep the rule-based fallback

    cache.set(cache_key, briefing, timeout=60)
    return briefing


def _rule_based_briefing(snapshot: dict) -> str:
    """Deterministic fallback briefing used when the AI backend is unavailable."""
    if snapshot["zones_at_risk_count"] == 0:
        crowd_line = "No zones are currently reporting high or critical density."
    else:
        zones = ", ".join(z["zone"] for z in snapshot["zones_at_risk"])
        crowd_line = f"{snapshot['zones_at_risk_count']} zone(s) need attention: {zones}."

    task_line = f"{snapshot['open_task_count']} operational task(s) are open."
    emissions_line = f"Estimated emissions so far: {snapshot['total_emissions_kg']} kg CO2e."
    return " ".join([crowd_line, task_line, emissions_line])


def _ai_briefing(snapshot: dict) -> str:
    """Ask GPT-4o for a short, prioritized operational briefing.

    Raises:
        AIServiceError: If the AI backend is unavailable, letting the
            caller fall back to the rule-based summary.
    """
    system_prompt = (
        "You are an operations intelligence assistant for a FIFA World Cup 2026 "
        "stadium control room. Given a JSON snapshot of crowd density risk zones, "
        "open staff tasks, and sustainability totals, write a 2-3 sentence briefing "
        "that tells staff what to prioritize right now. Be concrete and calm, no "
        "filler, no markdown."
    )
    return get_completion(system_prompt, str(snapshot))

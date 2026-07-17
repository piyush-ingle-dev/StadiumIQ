"""Tests for insights_service (operational intelligence)."""

from app.services import crowd_service, insights_service, staff_service, sustainability_service


class TestBuildSnapshot:
    def test_empty_state_snapshot(self, db):
        snapshot = insights_service.build_snapshot()
        assert snapshot["zones_at_risk_count"] == 0
        assert snapshot["open_task_count"] == 0
        assert snapshot["total_emissions_kg"] == 0.0

    def test_snapshot_reflects_crowd_risk(self, db):
        crowd_service.record_report("Gate A", 800)
        snapshot = insights_service.build_snapshot()
        assert snapshot["zones_at_risk_count"] == 1
        assert snapshot["zones_at_risk"][0]["zone"] == "Gate A"

    def test_snapshot_reflects_open_tasks(self, db):
        staff_service.create_task("Fix sign", "Gate A")
        snapshot = insights_service.build_snapshot()
        assert snapshot["open_task_count"] == 1

    def test_snapshot_reflects_emissions(self, db):
        sustainability_service.log_metric("electricity_kwh", 100)
        snapshot = insights_service.build_snapshot()
        assert snapshot["total_emissions_kg"] > 0

    def test_snapshot_includes_timestamp(self, db):
        snapshot = insights_service.build_snapshot()
        assert "generated_at" in snapshot


class TestGenerateBriefing:
    def test_falls_back_without_api_key(self, db):
        # Testing config has no OPENAI_API_KEY configured, so this
        # should use the deterministic rule-based summary.
        text = insights_service.generate_briefing()
        assert "operational task(s)" in text

    def test_briefing_mentions_zones_when_none_at_risk(self, db):
        text = insights_service.generate_briefing()
        assert "No zones are currently reporting" in text

    def test_briefing_mentions_zone_name_when_at_risk(self, db):
        crowd_service.record_report("Gate Z", 900)
        text = insights_service.generate_briefing()
        assert "Gate Z" in text

    def test_briefing_is_cached_for_identical_snapshot(self, db, app):
        from app.extensions import cache

        with app.app_context():
            cache.clear()
            first = insights_service.generate_briefing()
            second = insights_service.generate_briefing()
            assert first == second


class TestSnapshotFingerprint:
    def test_fingerprint_ignores_timestamp(self, db):
        snap1 = insights_service.build_snapshot()
        snap2 = dict(snap1)
        snap2["generated_at"] = "2000-01-01T00:00:00+00:00"
        assert insights_service._snapshot_fingerprint(snap1) == insights_service._snapshot_fingerprint(snap2)

    def test_fingerprint_changes_with_task_count(self, db):
        snap1 = insights_service.build_snapshot()
        staff_service.create_task("Task", "Gate A")
        snap2 = insights_service.build_snapshot()
        assert insights_service._snapshot_fingerprint(snap1) != insights_service._snapshot_fingerprint(snap2)

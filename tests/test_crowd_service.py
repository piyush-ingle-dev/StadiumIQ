"""Tests for CrowdReport model and crowd_service business logic."""

import pytest

from app.services import crowd_service


class TestClassifyDensity:
    def test_zero_people_is_low(self):
        assert crowd_service.classify_density(0) == "low"

    def test_149_people_is_low(self):
        assert crowd_service.classify_density(149) == "low"

    def test_150_people_is_moderate(self):
        assert crowd_service.classify_density(150) == "moderate"

    def test_399_people_is_moderate(self):
        assert crowd_service.classify_density(399) == "moderate"

    def test_400_people_is_high(self):
        assert crowd_service.classify_density(400) == "high"

    def test_699_people_is_high(self):
        assert crowd_service.classify_density(699) == "high"

    def test_700_people_is_critical(self):
        assert crowd_service.classify_density(700) == "critical"

    def test_very_large_number_is_critical(self):
        assert crowd_service.classify_density(50000) == "critical"

    def test_negative_raises_value_error(self):
        with pytest.raises(ValueError):
            crowd_service.classify_density(-1)


class TestRecordReport:
    def test_record_report_persists(self, db):
        report = crowd_service.record_report("Gate A", 200)
        assert report.id is not None

    def test_record_report_sets_density_level(self, db):
        report = crowd_service.record_report("Gate A", 800)
        assert report.density_level == "critical"

    def test_record_report_default_source_is_manual(self, db):
        report = crowd_service.record_report("Gate A", 50)
        assert report.source == "manual"

    def test_record_report_custom_source(self, db):
        report = crowd_service.record_report("Gate A", 50, source="sensor")
        assert report.source == "sensor"


class TestLatestByZone:
    def test_empty_when_no_reports(self, db):
        assert crowd_service.latest_by_zone() == {}

    def test_returns_most_recent_per_zone(self, db):
        crowd_service.record_report("Gate A", 100)
        crowd_service.record_report("Gate A", 500)
        latest = crowd_service.latest_by_zone()
        assert latest["Gate A"].people_estimate == 500

    def test_tracks_multiple_zones(self, db):
        crowd_service.record_report("Gate A", 100)
        crowd_service.record_report("Gate B", 200)
        latest = crowd_service.latest_by_zone()
        assert set(latest.keys()) == {"Gate A", "Gate B"}


class TestZonesNeedingAttention:
    def test_empty_when_all_low(self, db):
        crowd_service.record_report("Gate A", 50)
        assert crowd_service.zones_needing_attention() == []

    def test_includes_high_density_zones(self, db):
        crowd_service.record_report("Gate A", 450)
        results = crowd_service.zones_needing_attention()
        assert len(results) == 1
        assert results[0].zone == "Gate A"

    def test_excludes_moderate_density_zones(self, db):
        crowd_service.record_report("Gate A", 200)
        assert crowd_service.zones_needing_attention() == []

    def test_includes_critical_density_zones(self, db):
        crowd_service.record_report("Gate A", 900)
        results = crowd_service.zones_needing_attention()
        assert results[0].density_level == "critical"


class TestCrowdReportSerialization:
    def test_to_dict_contains_expected_keys(self, db):
        report = crowd_service.record_report("Gate A", 100)
        data = report.to_dict()
        assert set(data.keys()) == {
            "id", "zone", "density_level", "people_estimate", "source", "reported_at"
        }

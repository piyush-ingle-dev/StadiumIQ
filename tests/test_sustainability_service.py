"""Tests for sustainability_service."""

import pytest

from app.services import sustainability_service


class TestLogMetric:
    def test_unknown_category_raises(self, db):
        with pytest.raises(ValueError):
            sustainability_service.log_metric("unknown_category", 10)

    def test_negative_quantity_raises(self, db):
        with pytest.raises(ValueError):
            sustainability_service.log_metric("electricity_kwh", -5)

    def test_valid_entry_persists(self, db):
        entry = sustainability_service.log_metric("electricity_kwh", 100)
        assert entry.id is not None

    def test_default_zone_is_stadium_wide(self, db):
        entry = sustainability_service.log_metric("water_liter", 50)
        assert entry.zone == "stadium-wide"

    def test_custom_zone_is_stored(self, db):
        entry = sustainability_service.log_metric("waste_kg", 10, zone="Gate A")
        assert entry.zone == "Gate A"


class TestEstimatedEmissions:
    def test_electricity_emission_calculation(self, db):
        entry = sustainability_service.log_metric("electricity_kwh", 100)
        assert entry.estimated_co2e_kg == pytest.approx(47.5, rel=1e-3)

    def test_zero_quantity_zero_emissions(self, db):
        entry = sustainability_service.log_metric("waste_kg", 0)
        assert entry.estimated_co2e_kg == 0.0


class TestTotals:
    def test_total_emissions_zero_when_empty(self, db):
        assert sustainability_service.total_emissions_kg() == 0.0

    def test_total_emissions_sums_entries(self, db):
        sustainability_service.log_metric("electricity_kwh", 100)
        sustainability_service.log_metric("electricity_kwh", 100)
        assert sustainability_service.total_emissions_kg() == pytest.approx(95.0, rel=1e-3)

    def test_emissions_by_category_groups_correctly(self, db):
        sustainability_service.log_metric("electricity_kwh", 100)
        sustainability_service.log_metric("waste_kg", 10)
        totals = sustainability_service.emissions_by_category()
        assert totals["electricity_kwh"] > 0
        assert totals["waste_kg"] > 0

    def test_emissions_by_category_includes_all_known_categories(self, db):
        totals = sustainability_service.emissions_by_category()
        assert set(totals.keys()) == {
            "electricity_kwh", "water_liter", "waste_kg", "transport_km"
        }

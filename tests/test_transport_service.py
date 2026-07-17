"""Tests for transport_service."""

import pytest

from app.services import transport_service


class TestRecommendOptions:
    def test_negative_distance_raises(self):
        with pytest.raises(ValueError):
            transport_service.recommend_options(-1)

    def test_zero_distance_returns_walk(self):
        options = transport_service.recommend_options(0)
        modes = [o.mode for o in options]
        assert "walk" in modes

    def test_short_distance_includes_walk(self):
        options = transport_service.recommend_options(1.0)
        modes = [o.mode for o in options]
        assert "walk" in modes

    def test_short_distance_recommends_walk(self):
        options = transport_service.recommend_options(1.0)
        recommended = [o for o in options if o.recommended]
        assert len(recommended) == 1
        assert recommended[0].mode == "walk"

    def test_medium_distance_excludes_walk(self):
        options = transport_service.recommend_options(10.0)
        modes = [o.mode for o in options]
        assert "walk" not in modes

    def test_long_distance_falls_back_to_rideshare(self):
        options = transport_service.recommend_options(500.0)
        assert len(options) == 1
        assert options[0].mode == "rideshare"

    def test_only_one_option_flagged_recommended(self):
        options = transport_service.recommend_options(10.0)
        recommended = [o for o in options if o.recommended]
        assert len(recommended) == 1

    def test_recommended_is_lowest_emission_option(self):
        options = transport_service.recommend_options(10.0)
        recommended = next(o for o in options if o.recommended)
        assert recommended.estimated_co2e_kg == min(o.estimated_co2e_kg for o in options)

    def test_co2e_scales_with_distance(self):
        near = transport_service.recommend_options(5.0)
        far = transport_service.recommend_options(30.0)
        near_metro = next((o for o in near if o.mode == "metro"), None)
        far_metro = next((o for o in far if o.mode == "metro"), None)
        assert near_metro is not None and far_metro is not None
        assert far_metro.estimated_co2e_kg > near_metro.estimated_co2e_kg

    def test_options_sorted_by_emission_ascending(self):
        options = transport_service.recommend_options(10.0)
        emissions = [o.estimated_co2e_kg for o in options]
        assert emissions == sorted(emissions)

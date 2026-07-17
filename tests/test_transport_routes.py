"""Tests for transport blueprint routes."""


class TestTransportPage:
    def test_requires_login(self, client):
        response = client.get("/transport/")
        assert response.status_code == 302

    def test_loads_for_fan(self, fan_client):
        response = fan_client.get("/transport/")
        assert response.status_code == 200


class TestTransportRecommendAPI:
    def test_requires_login(self, client):
        response = client.get("/transport/api/recommend?distance_km=5")
        assert response.status_code == 302

    def test_valid_distance_returns_200(self, fan_client):
        response = fan_client.get("/transport/api/recommend?distance_km=5")
        assert response.status_code == 200

    def test_missing_distance_returns_400(self, fan_client):
        response = fan_client.get("/transport/api/recommend")
        assert response.status_code == 400

    def test_non_numeric_distance_returns_400(self, fan_client):
        response = fan_client.get("/transport/api/recommend?distance_km=far")
        assert response.status_code == 400

    def test_negative_distance_returns_400(self, fan_client):
        response = fan_client.get("/transport/api/recommend?distance_km=-5")
        assert response.status_code == 400

    def test_response_is_a_list(self, fan_client):
        response = fan_client.get("/transport/api/recommend?distance_km=10")
        assert isinstance(response.get_json(), list)

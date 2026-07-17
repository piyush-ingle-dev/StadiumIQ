"""Tests for sustainability blueprint routes."""


class TestSustainabilityPage:
    def test_requires_login(self, client):
        response = client.get("/sustainability/")
        assert response.status_code == 302

    def test_loads_for_admin(self, admin_client):
        response = admin_client.get("/sustainability/")
        assert response.status_code == 200


class TestLogMetricAPI:
    def test_non_admin_cannot_log_metric(self, volunteer_client):
        response = volunteer_client.post(
            "/sustainability/api/log", json={"category": "electricity_kwh", "quantity": 10}
        )
        assert response.status_code == 403

    def test_fan_cannot_log_metric(self, fan_client):
        response = fan_client.post(
            "/sustainability/api/log", json={"category": "electricity_kwh", "quantity": 10}
        )
        assert response.status_code == 403

    def test_admin_can_log_metric(self, admin_client):
        response = admin_client.post(
            "/sustainability/api/log", json={"category": "electricity_kwh", "quantity": 10}
        )
        assert response.status_code == 201

    def test_invalid_category_returns_400(self, admin_client):
        response = admin_client.post(
            "/sustainability/api/log", json={"category": "not_real", "quantity": 10}
        )
        assert response.status_code == 400

    def test_non_numeric_quantity_returns_400(self, admin_client):
        response = admin_client.post(
            "/sustainability/api/log", json={"category": "electricity_kwh", "quantity": "lots"}
        )
        assert response.status_code == 400


class TestSummaryAPI:
    def test_summary_requires_login(self, client):
        response = client.get("/sustainability/api/summary")
        assert response.status_code == 302

    def test_summary_accessible_to_any_logged_in_user(self, fan_client):
        response = fan_client.get("/sustainability/api/summary")
        assert response.status_code == 200

    def test_summary_includes_total_kg(self, fan_client):
        response = fan_client.get("/sustainability/api/summary")
        assert "total_kg" in response.get_json()

"""Tests for crowd blueprint routes."""


class TestCrowdPage:
    def test_requires_login(self, client):
        response = client.get("/crowd/")
        assert response.status_code == 302

    def test_loads_for_fan(self, fan_client):
        response = fan_client.get("/crowd/")
        assert response.status_code == 200


class TestCrowdReportAPI:
    def test_fan_cannot_submit_report(self, fan_client):
        response = fan_client.post(
            "/crowd/api/report", json={"zone": "Gate A", "people_estimate": 100}
        )
        assert response.status_code == 403

    def test_volunteer_can_submit_report(self, volunteer_client):
        response = volunteer_client.post(
            "/crowd/api/report", json={"zone": "Gate A", "people_estimate": 100}
        )
        assert response.status_code == 201

    def test_missing_zone_returns_400(self, volunteer_client):
        response = volunteer_client.post(
            "/crowd/api/report", json={"people_estimate": 100}
        )
        assert response.status_code == 400

    def test_negative_people_estimate_returns_400(self, volunteer_client):
        response = volunteer_client.post(
            "/crowd/api/report", json={"zone": "Gate A", "people_estimate": -5}
        )
        assert response.status_code == 400

    def test_non_numeric_people_estimate_returns_400(self, volunteer_client):
        response = volunteer_client.post(
            "/crowd/api/report", json={"zone": "Gate A", "people_estimate": "lots"}
        )
        assert response.status_code == 400

    def test_report_response_includes_density_level(self, volunteer_client):
        response = volunteer_client.post(
            "/crowd/api/report", json={"zone": "Gate A", "people_estimate": 800}
        )
        assert response.get_json()["density_level"] == "critical"


class TestCrowdStatusAPI:
    def test_status_requires_login(self, client):
        response = client.get("/crowd/api/status")
        assert response.status_code == 302

    def test_status_returns_empty_dict_when_no_reports(self, fan_client):
        response = fan_client.get("/crowd/api/status")
        assert response.get_json() == {}

    def test_status_includes_submitted_reports(self, volunteer_client):
        volunteer_client.post(
            "/crowd/api/report", json={"zone": "Gate Z", "people_estimate": 50}
        )
        response = volunteer_client.get("/crowd/api/status")
        assert "Gate Z" in response.get_json()

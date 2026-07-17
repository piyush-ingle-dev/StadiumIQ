"""Tests for insights blueprint routes."""


class TestInsightsPage:
    def test_requires_login(self, client):
        response = client.get("/insights/")
        assert response.status_code == 302

    def test_fan_cannot_access(self, fan_client):
        response = fan_client.get("/insights/")
        assert response.status_code == 403

    def test_volunteer_can_access(self, volunteer_client):
        response = volunteer_client.get("/insights/")
        assert response.status_code == 200

    def test_admin_can_access(self, admin_client):
        response = admin_client.get("/insights/")
        assert response.status_code == 200


class TestSnapshotAPI:
    def test_fan_cannot_access(self, fan_client):
        response = fan_client.get("/insights/api/snapshot")
        assert response.status_code == 403

    def test_volunteer_gets_snapshot(self, volunteer_client):
        response = volunteer_client.get("/insights/api/snapshot")
        assert response.status_code == 200
        assert "zones_at_risk_count" in response.get_json()


class TestBriefingAPI:
    def test_fan_cannot_access(self, fan_client):
        response = fan_client.get("/insights/api/briefing")
        assert response.status_code == 403

    def test_admin_gets_briefing_and_snapshot(self, admin_client):
        response = admin_client.get("/insights/api/briefing")
        assert response.status_code == 200
        data = response.get_json()
        assert "briefing" in data
        assert "snapshot" in data


class TestStreamAPI:
    def test_requires_login(self, client):
        response = client.get("/insights/api/stream")
        assert response.status_code == 302

    def test_fan_cannot_access_stream(self, fan_client):
        response = fan_client.get("/insights/api/stream")
        assert response.status_code == 403

    def test_stream_has_event_stream_mimetype(self, volunteer_client):
        response = volunteer_client.get("/insights/api/stream")
        assert response.mimetype == "text/event-stream"

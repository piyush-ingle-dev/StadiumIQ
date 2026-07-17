"""Tests for navigation blueprint routes."""


class TestNavigationPage:
    def test_requires_login(self, client):
        response = client.get("/navigation/")
        assert response.status_code == 302

    def test_loads_for_logged_in_user(self, fan_client):
        response = fan_client.get("/navigation/")
        assert response.status_code == 200


class TestNavigationGuideAPI:
    def test_requires_login(self, client):
        response = client.post("/navigation/api/guide", json={"from": "A", "to": "B"})
        assert response.status_code == 302

    def test_missing_from_returns_400(self, fan_client):
        response = fan_client.post("/navigation/api/guide", json={"to": "Section 114"})
        assert response.status_code == 400

    def test_missing_to_returns_400(self, fan_client):
        response = fan_client.post("/navigation/api/guide", json={"from": "Gate B"})
        assert response.status_code == 400

    def test_valid_request_returns_guidance(self, fan_client):
        response = fan_client.post(
            "/navigation/api/guide", json={"from": "Gate B", "to": "Section 114"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "guidance" in data

    def test_falls_back_gracefully_without_api_key(self, fan_client):
        # Testing config has no OPENAI_API_KEY, so the service should
        # fall back to its default message rather than error out.
        response = fan_client.post(
            "/navigation/api/guide", json={"from": "Gate A", "to": "Section 200"}
        )
        assert response.status_code == 200
        assert "Section 200" in response.get_json()["guidance"]

    def test_empty_json_body_returns_400(self, fan_client):
        response = fan_client.post("/navigation/api/guide", json={})
        assert response.status_code == 400

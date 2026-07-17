"""Tests for multilingual blueprint routes."""


class TestMultilingualPage:
    def test_requires_login(self, client):
        response = client.get("/multilingual/")
        assert response.status_code == 302

    def test_loads_for_fan(self, fan_client):
        response = fan_client.get("/multilingual/")
        assert response.status_code == 200


class TestTranslateAPI:
    def test_missing_text_returns_400(self, fan_client):
        response = fan_client.post(
            "/multilingual/api/translate", json={"target_language": "hi"}
        )
        assert response.status_code == 400

    def test_unsupported_language_returns_400(self, fan_client):
        response = fan_client.post(
            "/multilingual/api/translate", json={"text": "Hello", "target_language": "zz"}
        )
        assert response.status_code == 400

    def test_valid_request_returns_200(self, fan_client):
        response = fan_client.post(
            "/multilingual/api/translate", json={"text": "Hello", "target_language": "hi"}
        )
        assert response.status_code == 200

    def test_falls_back_to_original_text_without_api_key(self, fan_client):
        response = fan_client.post(
            "/multilingual/api/translate", json={"text": "Welcome to the stadium", "target_language": "fr"}
        )
        data = response.get_json()
        assert data["translated"] == "Welcome to the stadium"

    def test_response_includes_target_language(self, fan_client):
        response = fan_client.post(
            "/multilingual/api/translate", json={"text": "Hello", "target_language": "es"}
        )
        assert response.get_json()["target_language"] == "es"

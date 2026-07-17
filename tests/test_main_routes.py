"""Tests for main blueprint routes and general access control."""


class TestPublicRoutes:
    def test_home_page_loads(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_healthz_returns_ok(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.get_json() == {"status": "ok"}


class TestDashboardAccessControl:
    def test_dashboard_requires_login(self, client):
        response = client.get("/dashboard")
        assert response.status_code == 302

    def test_dashboard_loads_for_fan(self, fan_client):
        response = fan_client.get("/dashboard")
        assert response.status_code == 200

    def test_dashboard_loads_for_volunteer(self, volunteer_client):
        response = volunteer_client.get("/dashboard")
        assert response.status_code == 200

    def test_dashboard_loads_for_admin(self, admin_client):
        response = admin_client.get("/dashboard")
        assert response.status_code == 200

    def test_dashboard_shows_task_count_for_volunteer(self, volunteer_client):
        response = volunteer_client.get("/dashboard")
        assert b"Open staff tasks" in response.data

    def test_dashboard_shows_sustainability_for_admin(self, admin_client):
        response = admin_client.get("/dashboard")
        assert b"Sustainability snapshot" in response.data

    def test_dashboard_hides_task_count_for_fan(self, fan_client):
        response = fan_client.get("/dashboard")
        assert b"Open staff tasks" not in response.data


class TestRoleBasedPageAccess:
    def test_fan_cannot_access_staff_board(self, fan_client):
        response = fan_client.get("/staff/")
        assert response.status_code == 403

    def test_volunteer_can_access_staff_board(self, volunteer_client):
        response = volunteer_client.get("/staff/")
        assert response.status_code == 200

    def test_admin_can_access_staff_board(self, admin_client):
        response = admin_client.get("/staff/")
        assert response.status_code == 200

    def test_anonymous_redirected_from_staff_board(self, client):
        response = client.get("/staff/")
        assert response.status_code == 302

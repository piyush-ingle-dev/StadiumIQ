"""Tests for staff task management routes."""


class TestCreateTaskAPI:
    def test_fan_cannot_create_task(self, fan_client):
        response = fan_client.post(
            "/staff/api/tasks", json={"title": "Fix sign", "zone": "Gate A"}
        )
        assert response.status_code == 403

    def test_volunteer_can_create_task(self, volunteer_client):
        response = volunteer_client.post(
            "/staff/api/tasks", json={"title": "Fix sign", "zone": "Gate A"}
        )
        assert response.status_code == 201

    def test_missing_title_returns_400(self, volunteer_client):
        response = volunteer_client.post("/staff/api/tasks", json={"zone": "Gate A"})
        assert response.status_code == 400

    def test_missing_zone_returns_400(self, volunteer_client):
        response = volunteer_client.post("/staff/api/tasks", json={"title": "Fix sign"})
        assert response.status_code == 400

    def test_invalid_priority_returns_400(self, volunteer_client):
        response = volunteer_client.post(
            "/staff/api/tasks",
            json={"title": "Fix sign", "zone": "Gate A", "priority": "extreme"},
        )
        assert response.status_code == 400


class TestUpdateTaskStatusAPI:
    def test_admin_can_update_status(self, admin_client):
        create_response = admin_client.post(
            "/staff/api/tasks", json={"title": "Fix sign", "zone": "Gate A"}
        )
        task_id = create_response.get_json()["id"]
        response = admin_client.patch(
            f"/staff/api/tasks/{task_id}/status", json={"status": "completed"}
        )
        assert response.status_code == 200
        assert response.get_json()["status"] == "completed"

    def test_invalid_status_returns_400(self, admin_client):
        create_response = admin_client.post(
            "/staff/api/tasks", json={"title": "Fix sign", "zone": "Gate A"}
        )
        task_id = create_response.get_json()["id"]
        response = admin_client.patch(
            f"/staff/api/tasks/{task_id}/status", json={"status": "not_real"}
        )
        assert response.status_code == 400

    def test_nonexistent_task_returns_400(self, admin_client):
        response = admin_client.patch(
            "/staff/api/tasks/99999/status", json={"status": "completed"}
        )
        assert response.status_code == 400

    def test_fan_cannot_update_status(self, fan_client):
        response = fan_client.patch("/staff/api/tasks/1/status", json={"status": "completed"})
        assert response.status_code == 403


class TestListTasksAPI:
    def test_missing_zone_query_param_returns_400(self, volunteer_client):
        response = volunteer_client.get("/staff/api/tasks")
        assert response.status_code == 400

    def test_returns_tasks_for_zone(self, volunteer_client):
        volunteer_client.post(
            "/staff/api/tasks", json={"title": "Fix sign", "zone": "Gate Q"}
        )
        response = volunteer_client.get("/staff/api/tasks?zone=Gate Q")
        assert response.status_code == 200
        assert len(response.get_json()) == 1

    def test_fan_cannot_list_tasks(self, fan_client):
        response = fan_client.get("/staff/api/tasks?zone=Gate A")
        assert response.status_code == 403

"""Tests for staff_service."""

import pytest

from app.services import staff_service


class TestCreateTask:
    def test_invalid_priority_raises(self, db):
        with pytest.raises(ValueError):
            staff_service.create_task("Fix sign", "Gate A", priority="extreme")

    def test_valid_task_persists(self, db):
        task = staff_service.create_task("Fix sign", "Gate A")
        assert task.id is not None

    def test_default_priority_is_medium(self, db):
        task = staff_service.create_task("Fix sign", "Gate A")
        assert task.priority == "medium"

    def test_default_status_is_pending(self, db):
        task = staff_service.create_task("Fix sign", "Gate A")
        assert task.status == "pending"

    def test_description_is_optional(self, db):
        task = staff_service.create_task("Fix sign", "Gate A")
        assert task.description is None

    def test_description_can_be_set(self, db):
        task = staff_service.create_task("Fix sign", "Gate A", description="Broken bracket")
        assert task.description == "Broken bracket"


class TestUpdateStatus:
    def test_invalid_status_raises(self, db):
        task = staff_service.create_task("Fix sign", "Gate A")
        with pytest.raises(ValueError):
            staff_service.update_status(task.id, "unknown_status")

    def test_nonexistent_task_raises(self, db):
        with pytest.raises(ValueError):
            staff_service.update_status(99999, "completed")

    def test_update_to_in_progress(self, db):
        task = staff_service.create_task("Fix sign", "Gate A")
        updated = staff_service.update_status(task.id, "in_progress")
        assert updated.status == "in_progress"

    def test_update_to_completed_sets_completed_at(self, db):
        task = staff_service.create_task("Fix sign", "Gate A")
        updated = staff_service.update_status(task.id, "completed")
        assert updated.completed_at is not None

    def test_update_to_non_completed_leaves_completed_at_none(self, db):
        task = staff_service.create_task("Fix sign", "Gate A")
        updated = staff_service.update_status(task.id, "cancelled")
        assert updated.completed_at is None


class TestTasksForZone:
    def test_empty_zone_returns_empty_list(self, db):
        assert staff_service.tasks_for_zone("Nowhere") == []

    def test_returns_tasks_for_matching_zone_only(self, db):
        staff_service.create_task("Task 1", "Gate A")
        staff_service.create_task("Task 2", "Gate B")
        results = staff_service.tasks_for_zone("Gate A")
        assert len(results) == 1
        assert results[0].title == "Task 1"

    def test_most_recent_first(self, db):
        staff_service.create_task("Task 1", "Gate A")
        staff_service.create_task("Task 2", "Gate A")
        results = staff_service.tasks_for_zone("Gate A")
        assert results[0].title == "Task 2"


class TestOpenTaskCount:
    def test_zero_when_no_tasks(self, db):
        assert staff_service.open_task_count() == 0

    def test_counts_pending_and_in_progress(self, db):
        t1 = staff_service.create_task("Task 1", "Gate A")
        staff_service.create_task("Task 2", "Gate A")
        staff_service.update_status(t1.id, "in_progress")
        assert staff_service.open_task_count() == 2

    def test_excludes_completed_tasks(self, db):
        t1 = staff_service.create_task("Task 1", "Gate A")
        staff_service.update_status(t1.id, "completed")
        assert staff_service.open_task_count() == 0

    def test_excludes_cancelled_tasks(self, db):
        t1 = staff_service.create_task("Task 1", "Gate A")
        staff_service.update_status(t1.id, "cancelled")
        assert staff_service.open_task_count() == 0

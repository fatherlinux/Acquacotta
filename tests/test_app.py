"""Tests for Acquacotta Flask API endpoints."""

import json


class TestIndexRoute:
    """Tests for the main index route."""

    def test_index_returns_html(self, client):
        """Index route should return HTML template."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data


class TestAuthStatus:
    """Tests for authentication status endpoint."""

    def test_auth_status_not_logged_in(self, client):
        """Auth status should indicate not logged in when no session."""
        response = client.get("/api/auth/status")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["logged_in"] is False

    def test_auth_status_logged_in(self, authenticated_session):
        """Auth status should show user info when logged in."""
        response = authenticated_session.get("/api/auth/status")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["logged_in"] is True
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"


class TestPomodorosAPI:
    """Tests for pomodoro CRUD operations."""

    def test_get_pomodoros_empty(self, client):
        """Should return empty list when no pomodoros exist."""
        response = client.get("/api/pomodoros")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []

    def test_create_pomodoro(self, client):
        """Should create a new pomodoro."""
        response = client.post(
            "/api/pomodoros",
            json={
                "type": "Content",
                "name": "Test Task",
                "duration_minutes": 25,
                "notes": "Test notes",
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["type"] == "Content"
        assert data["name"] == "Test Task"
        assert data["duration_minutes"] == 25
        assert "id" in data
        assert "start_time" in data
        assert "end_time" in data

    def test_create_pomodoro_minimal(self, client):
        """Should create a pomodoro with only required fields."""
        response = client.post(
            "/api/pomodoros",
            json={"type": "Product"},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["type"] == "Product"
        assert data["name"] == ""  # Default empty name
        assert data["duration_minutes"] == 25  # Default duration

    def test_get_pomodoros_after_create(self, client):
        """Should return created pomodoros."""
        # Create a pomodoro
        client.post(
            "/api/pomodoros",
            json={"type": "Team", "name": "Meeting"},
            content_type="application/json",
        )

        # Verify it's in the list
        response = client.get("/api/pomodoros")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["type"] == "Team"
        assert data[0]["name"] == "Meeting"

    def test_update_pomodoro(self, client):
        """Should update an existing pomodoro."""
        # Create a pomodoro
        create_response = client.post(
            "/api/pomodoros",
            json={"type": "Content", "name": "Original"},
            content_type="application/json",
        )
        pomodoro_id = json.loads(create_response.data)["id"]
        created_data = json.loads(create_response.data)

        # Update it
        response = client.put(
            f"/api/pomodoros/{pomodoro_id}",
            json={
                "name": "Updated",
                "type": "Product",
                "notes": "Updated notes",
                "start_time": created_data["start_time"],
                "end_time": created_data["end_time"],
                "duration_minutes": created_data["duration_minutes"],
            },
            content_type="application/json",
        )
        assert response.status_code == 200

        # Verify the update
        get_response = client.get("/api/pomodoros")
        data = json.loads(get_response.data)
        assert len(data) == 1
        assert data[0]["name"] == "Updated"
        assert data[0]["type"] == "Product"

    def test_delete_pomodoro(self, client):
        """Should delete a pomodoro."""
        # Create a pomodoro
        create_response = client.post(
            "/api/pomodoros",
            json={"type": "Content", "name": "To Delete"},
            content_type="application/json",
        )
        pomodoro_id = json.loads(create_response.data)["id"]

        # Delete it
        response = client.delete(f"/api/pomodoros/{pomodoro_id}")
        assert response.status_code == 200

        # Verify it's gone
        get_response = client.get("/api/pomodoros")
        data = json.loads(get_response.data)
        assert len(data) == 0


class TestManualPomodoro:
    """Tests for manual pomodoro creation."""

    def test_create_manual_pomodoro(self, client):
        """Should create a manual pomodoro with custom times."""
        response = client.post(
            "/api/pomodoros/manual",
            json={
                "type": "Content",
                "name": "Manual Entry",
                "start_time": "2024-01-15T09:00:00Z",
                "end_time": "2024-01-15T09:25:00Z",
                "duration_minutes": 25,
                "notes": "Manually entered",
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["start_time"] == "2024-01-15T09:00:00Z"
        assert data["end_time"] == "2024-01-15T09:25:00Z"
        assert data["duration_minutes"] == 25


class TestSettingsAPI:
    """Tests for settings endpoints."""

    def test_get_default_settings(self, client):
        """Should return default settings when none are saved."""
        response = client.get("/api/settings")
        assert response.status_code == 200
        data = json.loads(response.data)
        # Check some default values
        assert data["timer_preset_4"] == 25
        assert data["short_break_minutes"] == 5
        assert data["long_break_minutes"] == 15
        assert "pomodoro_types" in data

    def test_save_settings(self, client):
        """Should save and retrieve settings."""
        # Save settings
        response = client.post(
            "/api/settings",
            json={
                "timer_preset_1": 10,
                "timer_preset_2": 20,
            },
            content_type="application/json",
        )
        assert response.status_code == 200

        # Retrieve and verify
        get_response = client.get("/api/settings")
        data = json.loads(get_response.data)
        assert data["timer_preset_1"] == 10
        assert data["timer_preset_2"] == 20


class TestReportsAPI:
    """Tests for report generation endpoints."""

    def test_get_day_report_empty(self, client):
        """Should return empty report for day with no pomodoros."""
        response = client.get("/api/reports/day?date=2024-01-15")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["period"] == "day"
        assert data["total_minutes"] == 0
        assert data["total_pomodoros"] == 0

    def test_get_day_report_with_pomodoros(self, client):
        """Should return report with pomodoro data."""
        # Create some pomodoros for a specific date
        client.post(
            "/api/pomodoros/manual",
            json={
                "type": "Content",
                "name": "Task 1",
                "start_time": "2024-01-15T10:00:00Z",
                "end_time": "2024-01-15T10:25:00Z",
                "duration_minutes": 25,
            },
            content_type="application/json",
        )
        client.post(
            "/api/pomodoros/manual",
            json={
                "type": "Product",
                "name": "Task 2",
                "start_time": "2024-01-15T14:00:00Z",
                "end_time": "2024-01-15T14:25:00Z",
                "duration_minutes": 25,
            },
            content_type="application/json",
        )

        # Get report
        response = client.get("/api/reports/day?date=2024-01-15")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["total_minutes"] == 50
        assert data["total_pomodoros"] == 2
        assert "Content" in data["by_type"]
        assert "Product" in data["by_type"]

    def test_get_week_report(self, client):
        """Should return weekly report."""
        response = client.get("/api/reports/week?date=2024-01-15")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["period"] == "week"
        assert len(data["daily_totals"]) == 7

    def test_get_month_report(self, client):
        """Should return monthly report."""
        response = client.get("/api/reports/month?date=2024-01-15")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["period"] == "month"
        # January 2024 has 31 days
        assert len(data["daily_totals"]) == 31

    def test_invalid_period_returns_error(self, client):
        """Should return error for invalid period."""
        response = client.get("/api/reports/invalid")
        assert response.status_code == 400


class TestExportCSV:
    """Tests for CSV export functionality."""

    def test_export_csv_empty(self, client):
        """Should return CSV with only headers when no data."""
        response = client.get("/api/export")
        assert response.status_code == 200
        assert response.content_type == "text/csv; charset=utf-8"
        assert b"id,name,type,start_time,end_time,duration_minutes,notes" in response.data

    def test_export_csv_with_data(self, client):
        """Should export pomodoros as CSV."""
        # Create a pomodoro
        client.post(
            "/api/pomodoros/manual",
            json={
                "type": "Content",
                "name": "Export Test",
                "start_time": "2024-01-15T10:00:00Z",
                "end_time": "2024-01-15T10:25:00Z",
                "duration_minutes": 25,
            },
            content_type="application/json",
        )

        response = client.get("/api/export")
        assert response.status_code == 200
        assert b"Export Test" in response.data
        assert b"Content" in response.data


class TestSyncStatus:
    """Tests for sync status endpoint."""

    def test_sync_status(self, client):
        """Should return sync status."""
        response = client.get("/api/sync/status")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "syncing" in data
        assert "pending_operations" in data
        assert "google_connected" in data


class TestLocalPomodoroCount:
    """Tests for local pomodoro count endpoint."""

    def test_local_count_empty(self, client):
        """Should return 0 when no pomodoros."""
        response = client.get("/api/local-pomodoro-count")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["count"] == 0

    def test_local_count_after_create(self, client):
        """Should return correct count after creating pomodoros."""
        # Create two pomodoros
        client.post("/api/pomodoros", json={"type": "Content"}, content_type="application/json")
        client.post("/api/pomodoros", json={"type": "Product"}, content_type="application/json")

        response = client.get("/api/local-pomodoro-count")
        data = json.loads(response.data)
        assert data["count"] == 2


class TestStaticPages:
    """Tests for static pages."""

    def test_privacy_page(self, client):
        """Privacy page should be accessible."""
        response = client.get("/privacy")
        assert response.status_code == 200

    def test_terms_page(self, client):
        """Terms page should be accessible."""
        response = client.get("/terms")
        assert response.status_code == 200

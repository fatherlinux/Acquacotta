"""Tests for Acquacotta Flask API endpoints.

Sovereign Sandbox v2: Tests for the stateless server architecture.
The server only handles:
- Static pages (index, privacy, terms)
- OAuth authentication
- Proxying requests to Google Sheets

All data storage and CRUD operations happen in the browser's IndexedDB.
"""

import json
from unittest.mock import MagicMock, patch

import sheets_storage


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


class TestSheetsProxyEndpoints:
    """Tests for Google Sheets proxy endpoints."""

    def test_get_pomodoros_requires_auth(self, client):
        """GET /api/sheets/pomodoros should require authentication."""
        response = client.get("/api/sheets/pomodoros")
        assert response.status_code == 401

    def test_create_pomodoro_requires_auth(self, client, sample_pomodoro):
        """POST /api/sheets/pomodoros should require authentication."""
        response = client.post(
            "/api/sheets/pomodoros",
            json=sample_pomodoro,
            content_type="application/json",
        )
        assert response.status_code == 401

    def test_update_pomodoro_requires_auth(self, client, sample_pomodoro):
        """PUT /api/sheets/pomodoros/<id> should require authentication."""
        response = client.put(
            "/api/sheets/pomodoros/test-id",
            json=sample_pomodoro,
            content_type="application/json",
        )
        assert response.status_code == 401

    def test_delete_pomodoro_requires_auth(self, client):
        """DELETE /api/sheets/pomodoros/<id> should require authentication."""
        response = client.delete("/api/sheets/pomodoros/test-id")
        assert response.status_code == 401

    def test_get_settings_requires_auth(self, client):
        """GET /api/sheets/settings should require authentication."""
        response = client.get("/api/sheets/settings")
        assert response.status_code == 401

    def test_save_settings_requires_auth(self, client, sample_settings):
        """POST /api/sheets/settings should require authentication."""
        response = client.post(
            "/api/sheets/settings",
            json=sample_settings,
            content_type="application/json",
        )
        assert response.status_code == 401

    def test_export_requires_auth(self, client):
        """GET /api/sheets/export should require authentication."""
        response = client.get("/api/sheets/export")
        assert response.status_code == 401

    def test_get_pomodoros_with_auth(self, authenticated_session, mock_sheets_service):
        """GET /api/sheets/pomodoros should proxy to Sheets when authenticated."""
        with patch("app.get_sheets_service", return_value=mock_sheets_service):
            with patch.object(
                sheets_storage,
                "get_pomodoros",
                return_value=[
                    {
                        "id": "test-1",
                        "name": "Test",
                        "type": "Content",
                        "start_time": "2024-01-15T10:00:00Z",
                        "end_time": "2024-01-15T10:25:00Z",
                        "duration_minutes": 25,
                        "notes": None,
                    }
                ],
            ) as mock_get:
                response = authenticated_session.get("/api/sheets/pomodoros")
                assert response.status_code == 200
                data = json.loads(response.data)
                assert len(data) == 1
                assert data[0]["name"] == "Test"
                mock_get.assert_called_once()

    def test_create_pomodoro_with_auth(
        self, authenticated_session, mock_sheets_service, sample_pomodoro
    ):
        """POST /api/sheets/pomodoros should proxy to Sheets when authenticated."""
        with patch("app.get_sheets_service", return_value=mock_sheets_service):
            with patch.object(sheets_storage, "save_pomodoro") as mock_save:
                response = authenticated_session.post(
                    "/api/sheets/pomodoros",
                    json=sample_pomodoro,
                    content_type="application/json",
                )
                assert response.status_code == 200
                mock_save.assert_called_once()

    def test_update_pomodoro_with_auth(
        self, authenticated_session, mock_sheets_service, sample_pomodoro
    ):
        """PUT /api/sheets/pomodoros/<id> should proxy to Sheets when authenticated."""
        with patch("app.get_sheets_service", return_value=mock_sheets_service):
            with patch.object(
                sheets_storage, "update_pomodoro", return_value=True
            ) as mock_update:
                response = authenticated_session.put(
                    "/api/sheets/pomodoros/test-uuid-1234",
                    json=sample_pomodoro,
                    content_type="application/json",
                )
                assert response.status_code == 200
                mock_update.assert_called_once()

    def test_delete_pomodoro_with_auth(self, authenticated_session, mock_sheets_service):
        """DELETE /api/sheets/pomodoros/<id> should proxy to Sheets when authenticated."""
        with patch("app.get_sheets_service", return_value=mock_sheets_service):
            with patch.object(
                sheets_storage, "delete_pomodoro", return_value=True
            ) as mock_delete:
                response = authenticated_session.delete(
                    "/api/sheets/pomodoros/test-uuid-1234"
                )
                assert response.status_code == 200
                mock_delete.assert_called_once()

    def test_get_settings_with_auth(self, authenticated_session, mock_sheets_service):
        """GET /api/sheets/settings should proxy to Sheets when authenticated."""
        with patch("app.get_sheets_service", return_value=mock_sheets_service):
            with patch.object(
                sheets_storage,
                "get_settings",
                return_value={"timer_preset_4": 25, "short_break_minutes": 5},
            ) as mock_get:
                response = authenticated_session.get("/api/sheets/settings")
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data["timer_preset_4"] == 25
                mock_get.assert_called_once()

    def test_save_settings_with_auth(
        self, authenticated_session, mock_sheets_service, sample_settings
    ):
        """POST /api/sheets/settings should proxy to Sheets when authenticated."""
        with patch("app.get_sheets_service", return_value=mock_sheets_service):
            with patch.object(sheets_storage, "save_settings") as mock_save:
                response = authenticated_session.post(
                    "/api/sheets/settings",
                    json=sample_settings,
                    content_type="application/json",
                )
                assert response.status_code == 200
                mock_save.assert_called_once()


class TestClearInitialSync:
    """Tests for the clear-initial-sync endpoint."""

    def test_clear_initial_sync(self, authenticated_session):
        """Should clear the needs_initial_sync flag."""
        # First set the flag
        with authenticated_session.session_transaction() as sess:
            sess["needs_initial_sync"] = True

        # Call the endpoint
        response = authenticated_session.post("/api/auth/clear-initial-sync")
        assert response.status_code == 200

        # Verify flag is cleared
        response = authenticated_session.get("/api/auth/status")
        data = json.loads(response.data)
        assert data["needs_initial_sync"] is False


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

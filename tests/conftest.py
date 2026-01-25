"""Pytest fixtures for Acquacotta tests."""

import os
import sqlite3
from unittest.mock import MagicMock, patch

import pytest

# Set environment variables before importing app
os.environ["FLASK_SECRET_KEY"] = "test-secret-key"
os.environ["CLEAR_CACHE_ON_START"] = "false"

import app as app_module


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory for testing."""
    data_dir = tmp_path / "acquacotta"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def app(temp_data_dir):
    """Create and configure a test Flask application."""
    # Patch DATA_DIR before creating the app instance
    with patch.object(app_module, "DATA_DIR", temp_data_dir):
        with patch.object(app_module, "DEFAULT_DB_PATH", temp_data_dir / "test.db"):
            # Reinitialize the database with the test path
            app_module.init_db(temp_data_dir / "test.db")

            test_app = app_module.app
            test_app.config.update(
                {
                    "TESTING": True,
                    "SECRET_KEY": "test-secret-key",
                    "SESSION_TYPE": "filesystem",
                    "SESSION_FILE_DIR": str(temp_data_dir / "sessions"),
                }
            )

            yield test_app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def db_path(temp_data_dir):
    """Return the test database path."""
    return temp_data_dir / "test.db"


@pytest.fixture
def test_db(db_path):
    """Create a test database with schema initialized."""
    app_module.init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture
def sample_pomodoro():
    """Return sample pomodoro data for testing."""
    return {
        "id": "test-uuid-1234",
        "name": "Test Task",
        "type": "Content",
        "start_time": "2024-01-15T10:00:00Z",
        "end_time": "2024-01-15T10:25:00Z",
        "duration_minutes": 25,
        "notes": "Test notes",
    }


@pytest.fixture
def sample_settings():
    """Return sample settings data for testing."""
    return {
        "timer_preset_1": 5,
        "timer_preset_2": 10,
        "timer_preset_3": 15,
        "timer_preset_4": 25,
        "short_break_minutes": 5,
        "long_break_minutes": 15,
        "pomodoro_types": ["Content", "Product", "Team"],
    }


@pytest.fixture
def mock_sheets_service():
    """Create a mock Google Sheets service."""
    service = MagicMock()

    # Mock spreadsheets().values().get()
    values_mock = MagicMock()
    spreadsheets_mock = MagicMock()
    spreadsheets_mock.values.return_value = values_mock
    service.spreadsheets.return_value = spreadsheets_mock

    return service


@pytest.fixture
def authenticated_session(app):
    """Create a session with mock authentication."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["credentials"] = {
                "token": "fake-token",
                "refresh_token": "fake-refresh-token",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "fake-client-id",
                "client_secret": "fake-client-secret",
                "scopes": ["https://www.googleapis.com/auth/drive.file"],
            }
            sess["user_email"] = "test@example.com"
            sess["user_name"] = "Test User"
            sess["spreadsheet_id"] = "fake-spreadsheet-id"
        yield client

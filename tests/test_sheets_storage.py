"""Tests for Google Sheets storage backend (mocked)."""

from unittest.mock import MagicMock

import sheets_storage


class TestGetPomodoros:
    """Tests for getting pomodoros from Google Sheets."""

    def test_get_pomodoros_empty(self):
        """Should return empty list when no data."""
        service = MagicMock()
        service.spreadsheets().values().get().execute.return_value = {"values": []}

        result = sheets_storage.get_pomodoros(service, "test-spreadsheet-id")
        assert result == []

    def test_get_pomodoros_with_data(self):
        """Should parse pomodoro rows correctly."""
        service = MagicMock()
        service.spreadsheets().values().get().execute.return_value = {
            "values": [
                ["id-1", "Task 1", "Content", "2024-01-15T10:00:00Z", "2024-01-15T10:25:00Z", "25", "Notes 1"],
                ["id-2", "Task 2", "Product", "2024-01-15T11:00:00Z", "2024-01-15T11:25:00Z", "25", ""],
            ]
        }

        result = sheets_storage.get_pomodoros(service, "test-spreadsheet-id")

        assert len(result) == 2
        assert result[0]["id"] == "id-2"  # Sorted by start_time descending
        assert result[0]["name"] == "Task 2"
        assert result[0]["type"] == "Product"
        assert result[0]["duration_minutes"] == 25
        assert result[1]["id"] == "id-1"
        assert result[1]["notes"] == "Notes 1"

    def test_get_pomodoros_skips_incomplete_rows(self):
        """Should skip rows with insufficient data."""
        service = MagicMock()
        service.spreadsheets().values().get().execute.return_value = {
            "values": [
                ["id-1", "Task 1", "Content", "2024-01-15T10:00:00Z", "2024-01-15T10:25:00Z", "25"],
                ["id-2", "Task 2"],  # Incomplete - should be skipped
                ["id-3", "Task 3", "Team", "2024-01-15T12:00:00Z", "2024-01-15T12:25:00Z", "25", "Notes"],
            ]
        }

        result = sheets_storage.get_pomodoros(service, "test-spreadsheet-id")
        assert len(result) == 2
        assert result[0]["id"] == "id-3"
        assert result[1]["id"] == "id-1"

    def test_get_pomodoros_with_date_filter(self):
        """Should filter pomodoros by date range."""
        service = MagicMock()
        service.spreadsheets().values().get().execute.return_value = {
            "values": [
                ["id-1", "Task 1", "Content", "2024-01-14T10:00:00Z", "2024-01-14T10:25:00Z", "25", ""],
                ["id-2", "Task 2", "Product", "2024-01-15T11:00:00Z", "2024-01-15T11:25:00Z", "25", ""],
                ["id-3", "Task 3", "Team", "2024-01-16T12:00:00Z", "2024-01-16T12:25:00Z", "25", ""],
            ]
        }

        result = sheets_storage.get_pomodoros(
            service, "test-spreadsheet-id", start_date="2024-01-15T00:00:00Z", end_date="2024-01-15T23:59:59Z"
        )

        assert len(result) == 1
        assert result[0]["id"] == "id-2"


class TestSavePomodoro:
    """Tests for saving pomodoros to Google Sheets."""

    def test_save_pomodoro(self):
        """Should append pomodoro to spreadsheet."""
        service = MagicMock()

        pomodoro = {
            "id": "new-id",
            "name": "New Task",
            "type": "Content",
            "start_time": "2024-01-15T10:00:00Z",
            "end_time": "2024-01-15T10:25:00Z",
            "duration_minutes": 25,
            "notes": "Test notes",
        }

        sheets_storage.save_pomodoro(service, "test-spreadsheet-id", pomodoro)

        # Verify the API was called correctly
        service.spreadsheets().values().append.assert_called_once()
        call_args = service.spreadsheets().values().append.call_args
        assert call_args.kwargs["spreadsheetId"] == "test-spreadsheet-id"
        assert call_args.kwargs["range"] == "Pomodoros!A:G"
        assert call_args.kwargs["body"]["values"][0][0] == "new-id"
        assert call_args.kwargs["body"]["values"][0][1] == "New Task"

    def test_save_pomodoro_without_notes(self):
        """Should handle pomodoro without notes."""
        service = MagicMock()

        pomodoro = {
            "id": "new-id",
            "name": "Task",
            "type": "Content",
            "start_time": "2024-01-15T10:00:00Z",
            "end_time": "2024-01-15T10:25:00Z",
            "duration_minutes": 25,
        }

        sheets_storage.save_pomodoro(service, "test-spreadsheet-id", pomodoro)

        call_args = service.spreadsheets().values().append.call_args
        # Notes field should be empty string
        assert call_args.kwargs["body"]["values"][0][6] == ""


class TestSavePomodorosBatch:
    """Tests for batch saving pomodoros."""

    def test_save_pomodoros_batch(self):
        """Should save multiple pomodoros in one request."""
        service = MagicMock()

        pomodoros = [
            {
                "id": "id-1",
                "name": "Task 1",
                "type": "Content",
                "start_time": "2024-01-15T10:00:00Z",
                "end_time": "2024-01-15T10:25:00Z",
                "duration_minutes": 25,
                "notes": "",
            },
            {
                "id": "id-2",
                "name": "Task 2",
                "type": "Product",
                "start_time": "2024-01-15T11:00:00Z",
                "end_time": "2024-01-15T11:25:00Z",
                "duration_minutes": 25,
                "notes": "Note",
            },
        ]

        sheets_storage.save_pomodoros_batch(service, "test-spreadsheet-id", pomodoros)

        call_args = service.spreadsheets().values().append.call_args
        assert len(call_args.kwargs["body"]["values"]) == 2
        assert call_args.kwargs["body"]["values"][0][0] == "id-1"
        assert call_args.kwargs["body"]["values"][1][0] == "id-2"

    def test_save_pomodoros_batch_empty(self):
        """Should do nothing for empty list."""
        service = MagicMock()

        sheets_storage.save_pomodoros_batch(service, "test-spreadsheet-id", [])

        service.spreadsheets().values().append.assert_not_called()


class TestUpdatePomodoro:
    """Tests for updating pomodoros in Google Sheets."""

    def test_update_pomodoro_found(self):
        """Should update existing pomodoro."""
        service = MagicMock()

        # Mock finding the row
        service.spreadsheets().values().get().execute.side_effect = [
            {"values": [["header"], ["id-1"], ["id-2"], ["target-id"]]},  # Find row
            {
                "values": [
                    [
                        "target-id",
                        "Old Name",
                        "Content",
                        "2024-01-15T10:00:00Z",
                        "2024-01-15T10:25:00Z",
                        "25",
                        "Old notes",
                    ]
                ]
            },  # Get current row
        ]

        result = sheets_storage.update_pomodoro(
            service, "test-spreadsheet-id", "target-id", {"name": "New Name", "type": "Product", "notes": "New notes"}
        )

        assert result is True
        service.spreadsheets().values().update.assert_called_once()

    def test_update_pomodoro_not_found(self):
        """Should return False when pomodoro not found."""
        service = MagicMock()
        service.spreadsheets().values().get().execute.return_value = {"values": [["header"], ["id-1"], ["id-2"]]}

        result = sheets_storage.update_pomodoro(service, "test-spreadsheet-id", "nonexistent-id", {"name": "New Name"})

        assert result is False


class TestDeletePomodoro:
    """Tests for deleting pomodoros from Google Sheets."""

    def test_delete_pomodoro_found(self):
        """Should delete existing pomodoro."""
        service = MagicMock()

        # Mock finding the row
        service.spreadsheets().values().get().execute.return_value = {
            "values": [["header"], ["id-1"], ["target-id"], ["id-3"]]
        }
        # Mock getting sheet info
        service.spreadsheets().get().execute.return_value = {
            "sheets": [{"properties": {"title": "Pomodoros", "sheetId": 0}}]
        }

        result = sheets_storage.delete_pomodoro(service, "test-spreadsheet-id", "target-id")

        assert result is True
        service.spreadsheets().batchUpdate.assert_called_once()

    def test_delete_pomodoro_not_found(self):
        """Should return False when pomodoro not found."""
        service = MagicMock()
        service.spreadsheets().values().get().execute.return_value = {"values": [["header"], ["id-1"], ["id-2"]]}

        result = sheets_storage.delete_pomodoro(service, "test-spreadsheet-id", "nonexistent-id")

        assert result is False


class TestGetSettings:
    """Tests for getting settings from Google Sheets."""

    def test_get_settings_empty(self):
        """Should return defaults when no settings stored."""
        service = MagicMock()
        service.spreadsheets().values().get().execute.return_value = {"values": []}

        defaults = {"timer_preset_1": 5, "timer_preset_2": 10}
        result = sheets_storage.get_settings(service, "test-spreadsheet-id", defaults)

        assert result == defaults

    def test_get_settings_with_data(self):
        """Should merge stored settings with defaults."""
        service = MagicMock()
        service.spreadsheets().values().get().execute.return_value = {
            "values": [
                ["timer_preset_1", "15"],
                ["pomodoro_types", '["Content", "Product"]'],
            ]
        }

        defaults = {"timer_preset_1": 5, "timer_preset_2": 10, "pomodoro_types": []}
        result = sheets_storage.get_settings(service, "test-spreadsheet-id", defaults)

        assert result["timer_preset_1"] == 15  # From sheets (parsed as int)
        assert result["timer_preset_2"] == 10  # From defaults
        assert result["pomodoro_types"] == ["Content", "Product"]  # From sheets (parsed as JSON)


class TestSaveSettings:
    """Tests for saving settings to Google Sheets."""

    def test_save_settings_new(self):
        """Should append new settings."""
        service = MagicMock()
        service.spreadsheets().values().get().execute.return_value = {"values": []}

        settings = {"timer_preset_1": 10, "timer_preset_2": 20}
        sheets_storage.save_settings(service, "test-spreadsheet-id", settings)

        service.spreadsheets().values().append.assert_called_once()

    def test_save_settings_update_existing(self):
        """Should update existing settings."""
        service = MagicMock()
        service.spreadsheets().values().get().execute.return_value = {"values": [["timer_preset_1", "5"]]}

        settings = {"timer_preset_1": 10}
        sheets_storage.save_settings(service, "test-spreadsheet-id", settings)

        service.spreadsheets().values().batchUpdate.assert_called_once()

    def test_save_settings_mixed(self):
        """Should update existing and append new settings."""
        service = MagicMock()
        service.spreadsheets().values().get().execute.return_value = {"values": [["timer_preset_1", "5"]]}

        settings = {"timer_preset_1": 10, "timer_preset_2": 20}
        sheets_storage.save_settings(service, "test-spreadsheet-id", settings)

        # Should have both batchUpdate (for existing) and append (for new)
        service.spreadsheets().values().batchUpdate.assert_called_once()
        service.spreadsheets().values().append.assert_called_once()

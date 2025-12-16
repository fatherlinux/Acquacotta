"""Google Sheets storage backend for Acquacotta."""

import json


def get_pomodoros(sheets_service, spreadsheet_id, start_date=None, end_date=None):
    """Get pomodoros from Google Sheets."""
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="Pomodoros!A2:G",
    ).execute()

    rows = result.get("values", [])
    pomodoros = []

    for row in rows:
        if len(row) < 6:
            continue
        pomo = {
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "start_time": row[3],
            "end_time": row[4],
            "duration_minutes": int(row[5]),
            "notes": row[6] if len(row) > 6 else None,
        }

        # Filter by date if specified
        if start_date and pomo["start_time"] < start_date:
            continue
        if end_date and pomo["start_time"] > end_date:
            continue

        pomodoros.append(pomo)

    # Sort by start_time descending
    pomodoros.sort(key=lambda p: p["start_time"], reverse=True)
    return pomodoros


def save_pomodoro(sheets_service, spreadsheet_id, pomodoro):
    """Save a new pomodoro to Google Sheets."""
    sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="Pomodoros!A:G",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={
            "values": [[
                pomodoro["id"],
                pomodoro["name"],
                pomodoro["type"],
                pomodoro["start_time"],
                pomodoro["end_time"],
                pomodoro["duration_minutes"],
                pomodoro.get("notes") or "",
            ]]
        },
    ).execute()


def save_pomodoros_batch(sheets_service, spreadsheet_id, pomodoros):
    """Save multiple pomodoros to Google Sheets in a single request."""
    if not pomodoros:
        return

    rows = []
    for p in pomodoros:
        rows.append([
            p["id"],
            p["name"],
            p["type"],
            p["start_time"],
            p["end_time"],
            p["duration_minutes"],
            p.get("notes") or "",
        ])

    sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="Pomodoros!A:G",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()


def update_pomodoro(sheets_service, spreadsheet_id, pomodoro_id, data):
    """Update a pomodoro in Google Sheets."""
    # Find the row with this ID
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="Pomodoros!A:A",
    ).execute()

    rows = result.get("values", [])
    row_index = None
    for i, row in enumerate(rows):
        if row and row[0] == pomodoro_id:
            row_index = i + 1  # 1-indexed
            break

    if row_index is None:
        return False

    # Get current row data
    current = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"Pomodoros!A{row_index}:G{row_index}",
    ).execute()

    current_values = current.get("values", [[]])[0]
    while len(current_values) < 7:
        current_values.append("")

    # Update fields
    current_values[1] = data.get("name", current_values[1])
    current_values[2] = data.get("type", current_values[2])
    current_values[3] = data.get("start_time", current_values[3])
    current_values[4] = data.get("end_time", current_values[4])
    current_values[5] = data.get("duration_minutes", current_values[5])
    current_values[6] = data.get("notes") or ""

    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"Pomodoros!A{row_index}:G{row_index}",
        valueInputOption="RAW",
        body={"values": [current_values]},
    ).execute()

    return True


def delete_pomodoro(sheets_service, spreadsheet_id, pomodoro_id):
    """Delete a pomodoro from Google Sheets."""
    # Find the row with this ID
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="Pomodoros!A:A",
    ).execute()

    rows = result.get("values", [])
    row_index = None
    for i, row in enumerate(rows):
        if row and row[0] == pomodoro_id:
            row_index = i  # 0-indexed for delete
            break

    if row_index is None:
        return False

    # Get sheet ID
    spreadsheet = sheets_service.spreadsheets().get(
        spreadsheetId=spreadsheet_id
    ).execute()

    sheet_id = None
    for sheet in spreadsheet["sheets"]:
        if sheet["properties"]["title"] == "Pomodoros":
            sheet_id = sheet["properties"]["sheetId"]
            break

    if sheet_id is None:
        return False

    # Delete the row
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [{
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": row_index,
                        "endIndex": row_index + 1,
                    }
                }
            }]
        },
    ).execute()

    return True


def get_settings(sheets_service, spreadsheet_id, defaults):
    """Get settings from Google Sheets."""
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="Settings!A2:B",
    ).execute()

    rows = result.get("values", [])
    settings = dict(defaults)

    for row in rows:
        if len(row) >= 2:
            key = row[0]
            try:
                value = json.loads(row[1])
            except (json.JSONDecodeError, TypeError):
                value = row[1]
            settings[key] = value

    return settings


def save_settings(sheets_service, spreadsheet_id, settings_data):
    """Save settings to Google Sheets."""
    # Get existing settings
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="Settings!A2:B",
    ).execute()

    existing_rows = result.get("values", [])
    existing_keys = {row[0]: i + 2 for i, row in enumerate(existing_rows) if row}  # 1-indexed, +1 for header

    # Prepare updates and appends
    updates = []
    appends = []

    for key, value in settings_data.items():
        value_str = json.dumps(value)
        if key in existing_keys:
            row_index = existing_keys[key]
            updates.append({
                "range": f"Settings!A{row_index}:B{row_index}",
                "values": [[key, value_str]],
            })
        else:
            appends.append([key, value_str])

    # Batch update existing
    if updates:
        sheets_service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "RAW",
                "data": updates,
            },
        ).execute()

    # Append new settings
    if appends:
        sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range="Settings!A:B",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": appends},
        ).execute()

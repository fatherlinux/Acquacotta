#!/usr/bin/env python3
"""Acquacotta - Pomodoro Time Tracking Application"""

import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Allow OAuth scope changes (users may have previously granted different scopes)
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

from flask import Flask, g, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

import sheets_storage

# Global sync state
sync_lock = threading.Lock()
sync_in_progress = False
last_sync_error = None

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

# Session configuration
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-prod")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "/tmp/flask_session"
Session(app)


@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON for API errors instead of HTML."""
    if request.path.startswith("/api/"):
        return jsonify({"error": str(e)}), 500
    # For non-API routes, re-raise to get default handling
    raise e


# Google OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]

# Allow insecure transport for local development
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Data directory for SQLite
DATA_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "acquacotta"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_DB_PATH = DATA_DIR / "pomodoros.db"  # For non-logged-in users

DEFAULT_POMODORO_TYPES = [
    "Content",
    "Customer/Partner/Community",
    "Learn/Train",
    "Product",
    "PTO",
    "Queued",
    "Social Media",
    "Team",
    "Travel",
    "Unqueued",
]


def get_user_spreadsheet_mapping_path():
    """Get path to the user-to-spreadsheet mapping file."""
    return DATA_DIR / "user_spreadsheets.json"


def get_stored_spreadsheet_id(email):
    """Get stored spreadsheet_id for a user email."""
    mapping_path = get_user_spreadsheet_mapping_path()
    if mapping_path.exists():
        with open(mapping_path, "r") as f:
            mapping = json.load(f)
            return mapping.get(email)
    return None


def save_spreadsheet_id(email, spreadsheet_id):
    """Save spreadsheet_id for a user email."""
    mapping_path = get_user_spreadsheet_mapping_path()
    mapping = {}
    if mapping_path.exists():
        with open(mapping_path, "r") as f:
            mapping = json.load(f)
    mapping[email] = spreadsheet_id
    with open(mapping_path, "w") as f:
        json.dump(mapping, f)


def get_user_db_path():
    """Get database path for current user (per-user isolation)."""
    if "user_email" in session:
        # Create a safe filename from email
        import hashlib
        email_hash = hashlib.md5(session["user_email"].encode()).hexdigest()[:12]
        safe_email = session["user_email"].replace("@", "_at_").replace(".", "_")
        # Use both readable name and hash for uniqueness
        db_name = f"user_{safe_email[:20]}_{email_hash}.db"
        return DATA_DIR / db_name
    return DEFAULT_DB_PATH


def get_db():
    """Get database connection for current user."""
    db_path = get_user_db_path()

    if "db" not in g:
        # Ensure database is initialized for this user
        init_db(db_path)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Close database connection at end of request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(db_path=None):
    """Initialize the database schema for a user."""
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    db = sqlite3.connect(db_path)
    db.execute("""
        CREATE TABLE IF NOT EXISTS pomodoros (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            notes TEXT,
            synced INTEGER DEFAULT 0
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            synced INTEGER DEFAULT 0
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS sync_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation TEXT NOT NULL,
            table_name TEXT NOT NULL,
            record_id TEXT NOT NULL,
            data TEXT,
            created_at TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS sync_status (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    # Add synced column if it doesn't exist (for existing databases)
    try:
        db.execute("ALTER TABLE pomodoros ADD COLUMN synced INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        db.execute("ALTER TABLE settings ADD COLUMN synced INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Column already exists
    db.commit()
    db.close()


# Initialize default database on startup (for non-logged-in users)
init_db(DEFAULT_DB_PATH)


def queue_sync_operation(db_path, operation, table_name, record_id, data=None):
    """Queue an operation for background sync to Google Sheets."""
    db = sqlite3.connect(db_path)
    db.execute(
        """
        INSERT INTO sync_queue (operation, table_name, record_id, data, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (operation, table_name, record_id, json.dumps(data) if data else None, datetime.utcnow().isoformat()),
    )
    db.commit()
    db.close()


def process_sync_queue(db_path, credentials_dict, spreadsheet_id):
    """Process pending sync operations in background."""
    global sync_in_progress, last_sync_error

    with sync_lock:
        if sync_in_progress:
            return
        sync_in_progress = True

    try:
        credentials = Credentials(
            token=credentials_dict["token"],
            refresh_token=credentials_dict.get("refresh_token"),
            token_uri=credentials_dict["token_uri"],
            client_id=credentials_dict["client_id"],
            client_secret=credentials_dict["client_secret"],
            scopes=credentials_dict["scopes"],
        )
        service = build("sheets", "v4", credentials=credentials)

        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row

        # Process queued operations
        rows = db.execute("SELECT * FROM sync_queue ORDER BY created_at").fetchall()

        for row in rows:
            try:
                operation = row["operation"]
                table_name = row["table_name"]
                record_id = row["record_id"]
                data = json.loads(row["data"]) if row["data"] else None

                if table_name == "pomodoros":
                    if operation == "INSERT":
                        sheets_storage.save_pomodoro(service, spreadsheet_id, data)
                    elif operation == "UPDATE":
                        sheets_storage.update_pomodoro(service, spreadsheet_id, record_id, data)
                    elif operation == "DELETE":
                        sheets_storage.delete_pomodoro(service, spreadsheet_id, record_id)
                elif table_name == "settings":
                    if operation in ("INSERT", "UPDATE"):
                        sheets_storage.save_settings(service, spreadsheet_id, data)

                # Mark as synced and remove from queue
                db.execute("UPDATE pomodoros SET synced = 1 WHERE id = ?", (record_id,))
                db.execute("DELETE FROM sync_queue WHERE id = ?", (row["id"],))
                db.commit()

            except Exception as e:
                last_sync_error = str(e)
                # Don't remove from queue on error - will retry later

        # Update last sync time
        db.execute(
            "INSERT OR REPLACE INTO sync_status (key, value) VALUES (?, ?)",
            ("last_sync", datetime.utcnow().isoformat()),
        )
        db.commit()
        db.close()
        last_sync_error = None

    except Exception as e:
        last_sync_error = str(e)
    finally:
        with sync_lock:
            sync_in_progress = False


def start_background_sync(db_path, credentials_dict, spreadsheet_id):
    """Start background sync thread."""
    thread = threading.Thread(
        target=process_sync_queue,
        args=(db_path, credentials_dict, spreadsheet_id),
        daemon=True,
    )
    thread.start()


def sync_from_sheets(db_path, credentials_dict, spreadsheet_id):
    """Pull all data from Google Sheets to local SQLite cache."""
    # Initialize database schema if needed
    init_db(db_path)

    credentials = Credentials(
        token=credentials_dict["token"],
        refresh_token=credentials_dict.get("refresh_token"),
        token_uri=credentials_dict["token_uri"],
        client_id=credentials_dict["client_id"],
        client_secret=credentials_dict["client_secret"],
        scopes=credentials_dict["scopes"],
    )
    service = build("sheets", "v4", credentials=credentials)

    db = sqlite3.connect(db_path)

    # Get all pomodoros from Google Sheets
    pomodoros = sheets_storage.get_pomodoros(service, spreadsheet_id)

    # Upsert into local database
    for p in pomodoros:
        db.execute(
            """
            INSERT OR REPLACE INTO pomodoros (id, name, type, start_time, end_time, duration_minutes, notes, synced)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (p["id"], p["name"], p["type"], p["start_time"], p["end_time"], p["duration_minutes"], p.get("notes")),
        )

    # Get settings from Google Sheets
    defaults = {
        "timer_preset_1": 5,
        "timer_preset_2": 10,
        "timer_preset_3": 15,
        "timer_preset_4": 25,
        "short_break_minutes": 5,
        "long_break_minutes": 15,
        "pomodoros_until_long_break": 4,
        "always_use_short_break": False,
        "sound_enabled": True,
        "notifications_enabled": True,
        "pomodoro_types": DEFAULT_POMODORO_TYPES,
        "auto_start_after_break": False,
        "tick_sound_during_breaks": False,
        "bell_at_pomodoro_end": True,
        "bell_at_break_end": True,
        "show_notes_field": False,
        "working_hours_start": "08:00",
        "working_hours_end": "17:00",
        "clock_format": "auto",
        "period_labels": "auto",
        "daily_minutes_goal": 300,
    }
    settings = sheets_storage.get_settings(service, spreadsheet_id, defaults)

    for key, value in settings.items():
        db.execute(
            "INSERT OR REPLACE INTO settings (key, value, synced) VALUES (?, ?, 1)",
            (key, json.dumps(value)),
        )

    # Update sync status
    db.execute(
        "INSERT OR REPLACE INTO sync_status (key, value) VALUES (?, ?)",
        ("last_full_sync", datetime.utcnow().isoformat()),
    )
    db.commit()
    db.close()

    return len(pomodoros)


def get_google_flow():
    """Create Google OAuth flow."""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return None
    # Build redirect URI from X-Forwarded headers or fall back to request host
    # Take first value if multiple proxies added headers (comma-separated)
    proto = request.headers.get("X-Forwarded-Proto", request.scheme).split(",")[0].strip()
    host = request.headers.get("X-Forwarded-Host", request.host).split(",")[0].strip()
    redirect_uri = f"{proto}://{host}/auth/callback"

    return Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )


def get_credentials():
    """Get Google credentials from session."""
    if "credentials" not in session:
        return None
    return Credentials(
        token=session["credentials"]["token"],
        refresh_token=session["credentials"].get("refresh_token"),
        token_uri=session["credentials"]["token_uri"],
        client_id=session["credentials"]["client_id"],
        client_secret=session["credentials"]["client_secret"],
        scopes=session["credentials"]["scopes"],
    )


def get_sheets_service():
    """Get Google Sheets API service."""
    credentials = get_credentials()
    if not credentials:
        return None
    return build("sheets", "v4", credentials=credentials)


def get_drive_service():
    """Get Google Drive API service."""
    credentials = get_credentials()
    if not credentials:
        return None
    return build("drive", "v3", credentials=credentials)


def use_google_sheets():
    """Check if we should use Google Sheets storage."""
    return "credentials" in session and "spreadsheet_id" in session


@app.route("/")
def index():
    """Main page with timer."""
    return render_template("index.html")


@app.route("/privacy")
def privacy():
    """Privacy policy page."""
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    """Terms of service page."""
    return render_template("terms.html")


@app.route("/auth/google")
def auth_google():
    """Initiate Google OAuth flow."""
    try:
        flow = get_google_flow()
        if not flow:
            return jsonify({"error": "Google OAuth not configured"}), 500
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        session["oauth_state"] = state
        return redirect(authorization_url)
    except Exception as e:
        import traceback
        return f"<pre>Error: {e}\n\n{traceback.format_exc()}</pre>", 500


@app.route("/auth/callback")
def auth_callback():
    """Handle Google OAuth callback."""
    try:
        flow = get_google_flow()
        if not flow:
            return jsonify({"error": "Google OAuth not configured"}), 500

        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials

        # Store credentials in session
        session["credentials"] = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": list(credentials.scopes),
        }

        # Get user info
        oauth2_service = build("oauth2", "v2", credentials=credentials)
        user_info = oauth2_service.userinfo().get().execute()
        user_email = user_info.get("email")
        session["user_email"] = user_email
        session["user_name"] = user_info.get("name")
        session["user_picture"] = user_info.get("picture")

        # Check for existing spreadsheet_id (persisted by email)
        stored_spreadsheet_id = get_stored_spreadsheet_id(user_email)
        if stored_spreadsheet_id:
            # Verify we can still access this spreadsheet (scope may have changed)
            try:
                sheets_service = get_sheets_service()
                sheets_service.spreadsheets().get(spreadsheetId=stored_spreadsheet_id).execute()
                session["spreadsheet_id"] = stored_spreadsheet_id
                session["spreadsheet_existed"] = True
            except Exception:
                # Can't access old spreadsheet, need to create new one
                stored_spreadsheet_id = None

        if not stored_spreadsheet_id:
            # Create new spreadsheet using Drive API (required for drive.file scope)
            drive_service = get_drive_service()
            file_metadata = {
                "name": "Acquacotta - Pomodoro Tracker",
                "mimeType": "application/vnd.google-apps.spreadsheet",
            }
            spreadsheet = drive_service.files().create(
                body=file_metadata,
                fields="id",
            ).execute()
            session["spreadsheet_id"] = spreadsheet["id"]
            session["spreadsheet_existed"] = False

            # Save the mapping for future logins
            save_spreadsheet_id(user_email, session["spreadsheet_id"])

            # Now use Sheets API to set up the sheets (we have access since we created the file)
            sheets_service = get_sheets_service()

            # Rename default Sheet1 to Pomodoros and add Settings sheet
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=session["spreadsheet_id"],
                body={
                    "requests": [
                        {
                            "updateSheetProperties": {
                                "properties": {"sheetId": 0, "title": "Pomodoros"},
                                "fields": "title",
                            }
                        },
                        {
                            "addSheet": {
                                "properties": {"title": "Settings"}
                            }
                        },
                    ]
                },
            ).execute()

            # Add headers to Pomodoros sheet
            sheets_service.spreadsheets().values().update(
                spreadsheetId=session["spreadsheet_id"],
                range="Pomodoros!A1:G1",
                valueInputOption="RAW",
                body={"values": [["id", "name", "type", "start_time", "end_time", "duration_minutes", "notes"]]},
            ).execute()

            # Add headers to Settings sheet
            sheets_service.spreadsheets().values().update(
                spreadsheetId=session["spreadsheet_id"],
                range="Settings!A1:B1",
                valueInputOption="RAW",
                body={"values": [["key", "value"]]},
            ).execute()

        # Don't sync automatically - let user decide what to do with existing data
        # The frontend will check needs_initial_sync and show migration dialog
        session["needs_initial_sync"] = True

        return redirect("/")
    except Exception as e:
        import traceback
        return f"<pre>Error: {e}\n\n{traceback.format_exc()}</pre>", 500


@app.route("/auth/logout")
def auth_logout():
    """Log out and clear session, including user's local cache."""
    # Delete user's local database to prevent stale data on next login
    if "user_email" in session:
        user_db_path = get_user_db_path()
        if user_db_path != DEFAULT_DB_PATH and user_db_path.exists():
            # Close any open connection first
            if "db" in g:
                g.db.close()
                g.pop("db", None)
            user_db_path.unlink()
    session.clear()
    return redirect("/")


@app.route("/api/auth/status")
def auth_status():
    """Get current authentication status."""
    if use_google_sheets():
        return jsonify({
            "logged_in": True,
            "email": session.get("user_email"),
            "name": session.get("user_name"),
            "picture": session.get("user_picture"),
            "spreadsheet_id": session.get("spreadsheet_id"),
            "needs_initial_sync": session.get("needs_initial_sync", False),
        })
    return jsonify({
        "logged_in": False,
        "google_configured": bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET),
    })


@app.route("/api/auth/spreadsheet", methods=["POST"])
def update_spreadsheet():
    """Update the spreadsheet ID for the current user."""
    if "user_email" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    new_spreadsheet_id = data.get("spreadsheet_id", "").strip()

    if not new_spreadsheet_id:
        return jsonify({"error": "Spreadsheet ID is required"}), 400

    # Validate that we can access this spreadsheet
    try:
        sheets_service = get_sheets_service()
        sheets_service.spreadsheets().get(spreadsheetId=new_spreadsheet_id).execute()
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "not found" in error_msg.lower():
            return jsonify({
                "error": "Cannot access this spreadsheet. With drive.file scope, you can only access spreadsheets created by this app instance."
            }), 400
        return jsonify({"error": f"Cannot access spreadsheet: {error_msg}"}), 400

    # Update session
    session["spreadsheet_id"] = new_spreadsheet_id

    # Update the persistent mapping
    save_spreadsheet_id(session["user_email"], new_spreadsheet_id)

    return jsonify({"status": "ok", "spreadsheet_id": new_spreadsheet_id})


@app.route("/api/pomodoros", methods=["GET"])
def get_pomodoros():
    """Get all pomodoros from SQLite cache, optionally filtered by date range."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Always read from SQLite (fast local cache)
    db = get_db()
    query = "SELECT id, name, type, start_time, end_time, duration_minutes, notes FROM pomodoros"
    params = []

    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append("start_time >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("start_time <= ?")
            params.append(end_date)
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY start_time DESC"
    rows = db.execute(query, params).fetchall()
    return jsonify([dict(row) for row in rows])


@app.route("/api/pomodoros", methods=["POST"])
def create_pomodoro():
    """Create a new pomodoro."""
    data = request.json

    pomodoro_id = str(uuid.uuid4())
    end_time = datetime.utcnow()
    duration = data.get("duration_minutes", 25)
    start_time = end_time - timedelta(minutes=duration)

    pomodoro = {
        "id": pomodoro_id,
        "name": data.get("name") or "",
        "type": data["type"],
        "start_time": start_time.isoformat() + "Z",
        "end_time": end_time.isoformat() + "Z",
        "duration_minutes": duration,
        "notes": data.get("notes"),
    }

    # Always write to SQLite first (fast)
    db = get_db()
    db.execute(
        """
        INSERT INTO pomodoros (id, name, type, start_time, end_time, duration_minutes, notes, synced)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            pomodoro_id,
            data.get("name") or "",
            data["type"],
            start_time.isoformat() + "Z",
            end_time.isoformat() + "Z",
            duration,
            data.get("notes"),
            0 if use_google_sheets() else 1,  # Mark as unsynced if Google connected
        ),
    )
    db.commit()

    # Queue for background sync to Google Sheets
    if use_google_sheets():
        db_path = get_user_db_path()
        queue_sync_operation(db_path, "INSERT", "pomodoros", pomodoro_id, pomodoro)
        start_background_sync(db_path, session["credentials"], session["spreadsheet_id"])

    return jsonify(pomodoro)


@app.route("/api/pomodoros/<pomodoro_id>", methods=["PUT"])
def update_pomodoro(pomodoro_id):
    """Update an existing pomodoro."""
    data = request.json

    # Always update SQLite first (fast)
    db = get_db()
    db.execute(
        """
        UPDATE pomodoros
        SET name = ?, type = ?, notes = ?, start_time = ?, end_time = ?, duration_minutes = ?, synced = ?
        WHERE id = ?
        """,
        (
            data["name"],
            data["type"],
            data.get("notes"),
            data["start_time"],
            data["end_time"],
            data["duration_minutes"],
            0 if use_google_sheets() else 1,
            pomodoro_id,
        ),
    )
    db.commit()

    # Queue for background sync to Google Sheets
    if use_google_sheets():
        db_path = get_user_db_path()
        queue_sync_operation(db_path, "UPDATE", "pomodoros", pomodoro_id, data)
        start_background_sync(db_path, session["credentials"], session["spreadsheet_id"])

    return jsonify({"status": "ok"})


@app.route("/api/pomodoros/<pomodoro_id>", methods=["DELETE"])
def delete_pomodoro(pomodoro_id):
    """Delete a pomodoro."""
    # Always delete from SQLite first (fast)
    db = get_db()
    db.execute("DELETE FROM pomodoros WHERE id = ?", (pomodoro_id,))
    db.commit()

    # Queue for background sync to Google Sheets
    if use_google_sheets():
        db_path = get_user_db_path()
        queue_sync_operation(db_path, "DELETE", "pomodoros", pomodoro_id)
        start_background_sync(db_path, session["credentials"], session["spreadsheet_id"])

    return jsonify({"status": "ok"})


@app.route("/api/pomodoros/manual", methods=["POST"])
def create_manual_pomodoro():
    """Create a manual pomodoro with custom times."""
    data = request.json
    pomodoro_id = str(uuid.uuid4())

    pomodoro = {
        "id": pomodoro_id,
        "name": data.get("name") or "",
        "type": data["type"],
        "start_time": data["start_time"],
        "end_time": data["end_time"],
        "duration_minutes": data["duration_minutes"],
        "notes": data.get("notes"),
    }

    # Always write to SQLite first (fast)
    db = get_db()
    db.execute(
        """
        INSERT INTO pomodoros (id, name, type, start_time, end_time, duration_minutes, notes, synced)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            pomodoro_id,
            data.get("name") or "",
            data["type"],
            data["start_time"],
            data["end_time"],
            data["duration_minutes"],
            data.get("notes"),
            0 if use_google_sheets() else 1,
        ),
    )
    db.commit()

    # Queue for background sync to Google Sheets
    if use_google_sheets():
        db_path = get_user_db_path()
        queue_sync_operation(db_path, "INSERT", "pomodoros", pomodoro_id, pomodoro)
        start_background_sync(db_path, session["credentials"], session["spreadsheet_id"])

    return jsonify(pomodoro)


@app.route("/api/settings", methods=["GET"])
def get_settings():
    """Get user settings from SQLite cache."""
    defaults = {
        "timer_preset_1": 5,
        "timer_preset_2": 10,
        "timer_preset_3": 15,
        "timer_preset_4": 25,
        "short_break_minutes": 5,
        "long_break_minutes": 15,
        "pomodoros_until_long_break": 4,
        "always_use_short_break": False,
        "sound_enabled": True,
        "notifications_enabled": True,
        "pomodoro_types": DEFAULT_POMODORO_TYPES,
        "auto_start_after_break": False,
        "tick_sound_during_breaks": False,
        "bell_at_pomodoro_end": True,
        "bell_at_break_end": True,
        "show_notes_field": False,
        "working_hours_start": "08:00",
        "working_hours_end": "17:00",
        "clock_format": "auto",
        "period_labels": "auto",
        "daily_minutes_goal": 300,
    }

    # Always read from SQLite (fast local cache)
    db = get_db()
    rows = db.execute("SELECT key, value FROM settings").fetchall()
    settings = {row["key"]: json.loads(row["value"]) for row in rows}
    defaults.update(settings)
    return jsonify(defaults)


@app.route("/api/settings", methods=["POST"])
def save_settings():
    """Save user settings."""
    data = request.json

    # Always write to SQLite first (fast)
    db = get_db()
    for key, value in data.items():
        db.execute(
            "INSERT OR REPLACE INTO settings (key, value, synced) VALUES (?, ?, ?)",
            (key, json.dumps(value), 0 if use_google_sheets() else 1),
        )
    db.commit()

    # Queue for background sync to Google Sheets
    if use_google_sheets():
        db_path = get_user_db_path()
        queue_sync_operation(db_path, "UPDATE", "settings", "all", data)
        start_background_sync(db_path, session["credentials"], session["spreadsheet_id"])

    return jsonify({"status": "ok"})


@app.route("/api/reports/<period>")
def get_report(period):
    """Get report data for a given period (day, week, month).

    Accepts start_date and end_date as ISO strings for timezone-aware queries.
    Falls back to date parameter (interpreted as UTC) if ISO strings not provided.
    """
    # Use ISO date strings if provided (timezone-aware from frontend)
    start_iso = request.args.get("start_date")
    end_iso = request.args.get("end_date")

    if start_iso and end_iso:
        # Parse ISO dates to get the reference date and date list
        start_dt = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))

        # Build dates list for daily_totals
        dates = []
        d = start_dt.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        end_naive = end_dt.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        while d < end_naive:
            dates.append(d)
            d += timedelta(days=1)
        if not dates:
            dates = [start_dt.replace(tzinfo=None)]
    else:
        # Fallback to date parameter (legacy behavior)
        date_str = request.args.get("date", datetime.utcnow().strftime("%Y-%m-%d"))
        ref_date = datetime.strptime(date_str, "%Y-%m-%d")

        if period == "day":
            start = ref_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            dates = [start]
        elif period == "week":
            start = ref_date - timedelta(days=ref_date.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
            dates = [start + timedelta(days=i) for i in range(7)]
        elif period == "month":
            start = ref_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if ref_date.month == 12:
                end = start.replace(year=ref_date.year + 1, month=1)
            else:
                end = start.replace(month=ref_date.month + 1)
            dates = []
            d = start
            while d < end:
                dates.append(d)
                d += timedelta(days=1)
        else:
            return jsonify({"error": "Invalid period"}), 400

        start_iso = start.isoformat() + "Z"
        end_iso = end.isoformat() + "Z"

    # Always read from SQLite (fast local cache)
    db = get_db()
    rows = db.execute(
        """
        SELECT id, name, type, start_time, end_time, duration_minutes, notes FROM pomodoros
        WHERE start_time >= ? AND start_time < ?
        ORDER BY start_time
        """,
        (start_iso, end_iso),
    ).fetchall()
    pomodoros = [dict(row) for row in rows]

    # Calculate totals
    total_minutes = sum(p["duration_minutes"] for p in pomodoros)
    total_count = len(pomodoros)

    # By type
    by_type = {}
    for p in pomodoros:
        t = p["type"]
        by_type[t] = by_type.get(t, 0) + p["duration_minutes"]

    # Daily totals
    daily_totals = []
    for d in dates:
        day_str = d.strftime("%Y-%m-%d")
        day_pomodoros = [
            p for p in pomodoros
            if p["start_time"].startswith(day_str)
        ]
        daily_totals.append({
            "date": day_str,
            "minutes": sum(p["duration_minutes"] for p in day_pomodoros),
            "count": len(day_pomodoros),
        })

    return jsonify({
        "period": period,
        "total_minutes": total_minutes,
        "total_pomodoros": total_count,
        "by_type": by_type,
        "daily_totals": daily_totals,
    })


@app.route("/api/export")
def export_csv():
    """Export pomodoros as CSV from SQLite cache."""
    # Always read from SQLite (fast local cache)
    db = get_db()
    rows = db.execute(
        "SELECT id, name, type, start_time, end_time, duration_minutes, notes FROM pomodoros ORDER BY start_time DESC"
    ).fetchall()
    pomodoros = [dict(row) for row in rows]

    lines = ["id,name,type,start_time,end_time,duration_minutes,notes"]
    for p in pomodoros:
        name = (p["name"] or "").replace('"', '""')
        notes = (p.get("notes") or "").replace('"', '""')
        lines.append(
            f'"{p["id"]}","{name}","{p["type"]}","{p["start_time"]}",'
            f'"{p["end_time"]}",{p["duration_minutes"]},"{notes}"'
        )

    from flask import Response
    return Response(
        "\n".join(lines),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=pomodoros.csv"},
    )


@app.route("/api/local-pomodoro-count")
def get_local_pomodoro_count():
    """Get count of pomodoros in local SQLite database."""
    db = get_db()
    count = db.execute("SELECT COUNT(*) FROM pomodoros").fetchone()[0]
    return jsonify({"count": count})


@app.route("/api/sync/status")
def get_sync_status():
    """Get current sync status."""
    db = get_db()

    # Get pending sync count
    pending_count = db.execute("SELECT COUNT(*) FROM sync_queue").fetchone()[0]
    unsynced_count = db.execute("SELECT COUNT(*) FROM pomodoros WHERE synced = 0").fetchone()[0]

    # Get last sync times
    last_sync_row = db.execute("SELECT value FROM sync_status WHERE key = 'last_sync'").fetchone()
    last_full_sync_row = db.execute("SELECT value FROM sync_status WHERE key = 'last_full_sync'").fetchone()

    return jsonify({
        "syncing": sync_in_progress,
        "pending_operations": pending_count,
        "unsynced_pomodoros": unsynced_count,
        "last_sync": last_sync_row["value"] if last_sync_row else None,
        "last_full_sync": last_full_sync_row["value"] if last_full_sync_row else None,
        "last_error": last_sync_error,
        "google_connected": use_google_sheets(),
    })


@app.route("/api/sync/check")
def check_sync_sources():
    """Check data counts from both local SQLite and Google Sheets."""
    if not use_google_sheets():
        return jsonify({"error": "Not logged in to Google"}), 401

    # Get user's local count (per-user database)
    db = get_db()
    local_count = db.execute("SELECT COUNT(*) FROM pomodoros").fetchone()[0]

    # Check shared cache (DEFAULT_DB_PATH) for pomodoros from before login
    shared_cache_count = 0
    if DEFAULT_DB_PATH.exists() and get_user_db_path() != DEFAULT_DB_PATH:
        try:
            shared_db = sqlite3.connect(DEFAULT_DB_PATH)
            shared_db.row_factory = sqlite3.Row
            shared_cache_count = shared_db.execute("SELECT COUNT(*) FROM pomodoros").fetchone()[0]
            shared_db.close()
        except Exception:
            pass  # Shared cache doesn't exist or is empty

    # Get Google Sheets count
    try:
        service = get_sheets_service()
        sheets_pomodoros = sheets_storage.get_pomodoros(service, session["spreadsheet_id"])
        sheets_count = len(sheets_pomodoros)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "local_count": local_count,
        "shared_cache_count": shared_cache_count,
        "sheets_count": sheets_count,
        "needs_initial_sync": session.get("needs_initial_sync", False),
    })


@app.route("/api/sync/now", methods=["POST"])
def trigger_sync():
    """Manually trigger a sync with Google Sheets."""
    if not use_google_sheets():
        return jsonify({"error": "Not logged in to Google"}), 401

    db_path = get_user_db_path()

    # First pull from Google Sheets
    try:
        count = sync_from_sheets(db_path, session["credentials"], session["spreadsheet_id"])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Then push any pending changes
    start_background_sync(db_path, session["credentials"], session["spreadsheet_id"])

    return jsonify({"status": "ok", "synced_from_sheets": count})


@app.route("/api/migrate", methods=["POST"])
def migrate_data():
    """Migrate data between SQLite and Google Sheets.

    Request body:
        pomodoros_direction: "local_to_sheets" | "sheets_to_local" | "shared_cache_to_sheets" | "skip"
        settings_direction: "local_to_sheets" | "sheets_to_local" | "skip"
    """
    if not use_google_sheets():
        return jsonify({"error": "Not logged in to Google"}), 401

    data = request.json or {}
    pomodoros_direction = data.get("pomodoros_direction", "skip")
    settings_direction = data.get("settings_direction", "skip")

    db = get_db()
    service = get_sheets_service()
    spreadsheet_id = session["spreadsheet_id"]

    migrated_pomodoros = 0
    skipped_pomodoros = 0

    if pomodoros_direction == "shared_cache_to_sheets":
        # Push pomodoros from shared cache to Google Sheets
        if DEFAULT_DB_PATH.exists() and get_user_db_path() != DEFAULT_DB_PATH:
            shared_db = sqlite3.connect(DEFAULT_DB_PATH)
            shared_db.row_factory = sqlite3.Row

            existing_pomodoros = sheets_storage.get_pomodoros(service, spreadsheet_id)
            existing_ids = {p["id"] for p in existing_pomodoros}

            rows = shared_db.execute("SELECT * FROM pomodoros ORDER BY start_time").fetchall()
            pomodoros_to_upload = []
            for row in rows:
                if row["id"] in existing_ids:
                    skipped_pomodoros += 1
                    continue
                pomodoro = {
                    "id": row["id"],
                    "name": row["name"],
                    "type": row["type"],
                    "start_time": row["start_time"],
                    "end_time": row["end_time"],
                    "duration_minutes": row["duration_minutes"],
                    "notes": row["notes"],
                }
                pomodoros_to_upload.append(pomodoro)

            if pomodoros_to_upload:
                sheets_storage.save_pomodoros_batch(service, spreadsheet_id, pomodoros_to_upload)
                migrated_pomodoros = len(pomodoros_to_upload)

            # Clear the shared cache after successful migration
            shared_db.execute("DELETE FROM pomodoros")
            shared_db.commit()
            shared_db.close()

    elif pomodoros_direction == "local_to_sheets":
        # Push local pomodoros to Google Sheets
        existing_pomodoros = sheets_storage.get_pomodoros(service, spreadsheet_id)
        existing_ids = {p["id"] for p in existing_pomodoros}

        rows = db.execute("SELECT * FROM pomodoros ORDER BY start_time").fetchall()
        pomodoros_to_upload = []
        ids_to_mark_synced = []
        for row in rows:
            if row["id"] in existing_ids:
                skipped_pomodoros += 1
                continue
            pomodoro = {
                "id": row["id"],
                "name": row["name"],
                "type": row["type"],
                "start_time": row["start_time"],
                "end_time": row["end_time"],
                "duration_minutes": row["duration_minutes"],
                "notes": row["notes"],
            }
            pomodoros_to_upload.append(pomodoro)
            ids_to_mark_synced.append(row["id"])

        # Upload all pomodoros in a single batch request to avoid rate limits
        if pomodoros_to_upload:
            sheets_storage.save_pomodoros_batch(service, spreadsheet_id, pomodoros_to_upload)
            # Mark all as synced in local db
            for pomodoro_id in ids_to_mark_synced:
                db.execute("UPDATE pomodoros SET synced = 1 WHERE id = ?", (pomodoro_id,))
            migrated_pomodoros = len(pomodoros_to_upload)
        db.commit()

    elif pomodoros_direction == "sheets_to_local":
        # Pull pomodoros from Google Sheets to local SQLite
        sheets_pomodoros = sheets_storage.get_pomodoros(service, spreadsheet_id)

        # Get existing local IDs to avoid duplicates
        local_rows = db.execute("SELECT id FROM pomodoros").fetchall()
        local_ids = {row["id"] for row in local_rows}

        for p in sheets_pomodoros:
            if p["id"] in local_ids:
                skipped_pomodoros += 1
                continue
            db.execute(
                """
                INSERT INTO pomodoros (id, name, type, start_time, end_time, duration_minutes, notes, synced)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (p["id"], p["name"], p["type"], p["start_time"], p["end_time"], p["duration_minutes"], p.get("notes")),
            )
            migrated_pomodoros += 1
        db.commit()

    # Handle settings based on direction
    settings_migrated = 0
    if settings_direction == "local_to_sheets":
        # Push local settings to Google Sheets
        settings_rows = db.execute("SELECT key, value FROM settings").fetchall()
        if settings_rows:
            settings_data = {row["key"]: json.loads(row["value"]) for row in settings_rows}
            sheets_storage.save_settings(service, spreadsheet_id, settings_data)
            settings_migrated = len(settings_rows)
    elif settings_direction == "sheets_to_local":
        # Pull Google Sheets settings to local
        defaults = {
            "timer_preset_1": 5,
            "timer_preset_2": 10,
            "timer_preset_3": 15,
            "timer_preset_4": 25,
            "short_break_minutes": 5,
            "long_break_minutes": 15,
            "pomodoros_until_long_break": 4,
            "always_use_short_break": False,
            "sound_enabled": True,
            "notifications_enabled": True,
            "pomodoro_types": DEFAULT_POMODORO_TYPES,
            "auto_start_after_break": False,
            "tick_sound_during_breaks": False,
            "bell_at_pomodoro_end": True,
            "bell_at_break_end": True,
            "show_notes_field": False,
            "working_hours_start": "08:00",
            "working_hours_end": "17:00",
            "clock_format": "auto",
            "period_labels": "auto",
            "daily_minutes_goal": 300,
        }
        sheets_settings = sheets_storage.get_settings(service, spreadsheet_id, defaults)
        for key, value in sheets_settings.items():
            db.execute(
                "INSERT OR REPLACE INTO settings (key, value, synced) VALUES (?, ?, 1)",
                (key, json.dumps(value)),
            )
        db.commit()
        settings_migrated = len(sheets_settings)

    # Clear the needs_initial_sync flag - migration is complete
    session["needs_initial_sync"] = False

    return jsonify({
        "success": True,
        "pomodoros_migrated": migrated_pomodoros,
        "pomodoros_skipped": skipped_pomodoros,
        "pomodoros_direction": pomodoros_direction,
        "settings_migrated": settings_migrated,
        "settings_direction": settings_direction,
    })


if __name__ == "__main__":
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    app.run(host=host, port=5000)

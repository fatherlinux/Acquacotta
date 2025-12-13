#!/usr/bin/env python3
"""Acquacotta - Pomodoro Time Tracking Application"""

import json
import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, g, jsonify, render_template, request

app = Flask(__name__)

# Data directory
DATA_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "acquacotta"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "pomodoros.db"

POMODORO_TYPES = [
    "Product",
    "Customer/Partner/Community",
    "Content",
    "Team",
    "Social Media",
    "Unqueued",
    "Queued",
    "Learn/Train",
    "Travel",
    "PTO",
]


def get_db():
    """Get database connection for current request."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Close database connection at end of request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Initialize the database schema."""
    db = sqlite3.connect(DB_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS pomodoros (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            notes TEXT
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    db.commit()
    db.close()


# Initialize database on startup
init_db()


@app.route("/")
def index():
    """Main page with timer."""
    return render_template("index.html", types=POMODORO_TYPES)


@app.route("/api/pomodoros", methods=["GET"])
def get_pomodoros():
    """Get all pomodoros, optionally filtered by date range."""
    db = get_db()
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    query = "SELECT * FROM pomodoros"
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
    db = get_db()

    pomodoro_id = str(uuid.uuid4())
    end_time = datetime.utcnow()
    duration = data.get("duration_minutes", 25)
    start_time = end_time - timedelta(minutes=duration)

    db.execute(
        """
        INSERT INTO pomodoros (id, name, type, start_time, end_time, duration_minutes, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            pomodoro_id,
            data["name"],
            data["type"],
            start_time.isoformat() + "Z",
            end_time.isoformat() + "Z",
            duration,
            data.get("notes"),
        ),
    )
    db.commit()

    return jsonify({
        "id": pomodoro_id,
        "name": data["name"],
        "type": data["type"],
        "start_time": start_time.isoformat() + "Z",
        "end_time": end_time.isoformat() + "Z",
        "duration_minutes": duration,
        "notes": data.get("notes"),
    })


@app.route("/api/pomodoros/<pomodoro_id>", methods=["PUT"])
def update_pomodoro(pomodoro_id):
    """Update an existing pomodoro."""
    data = request.json
    db = get_db()

    db.execute(
        """
        UPDATE pomodoros
        SET name = ?, type = ?, notes = ?
        WHERE id = ?
        """,
        (data["name"], data["type"], data.get("notes"), pomodoro_id),
    )
    db.commit()

    return jsonify({"status": "ok"})


@app.route("/api/pomodoros/<pomodoro_id>", methods=["DELETE"])
def delete_pomodoro(pomodoro_id):
    """Delete a pomodoro."""
    db = get_db()
    db.execute("DELETE FROM pomodoros WHERE id = ?", (pomodoro_id,))
    db.commit()
    return jsonify({"status": "ok"})


@app.route("/api/pomodoros/manual", methods=["POST"])
def create_manual_pomodoro():
    """Create a manual pomodoro with custom times."""
    data = request.json
    db = get_db()

    pomodoro_id = str(uuid.uuid4())

    db.execute(
        """
        INSERT INTO pomodoros (id, name, type, start_time, end_time, duration_minutes, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            pomodoro_id,
            data["name"],
            data["type"],
            data["start_time"],
            data["end_time"],
            data["duration_minutes"],
            data.get("notes"),
        ),
    )
    db.commit()

    return jsonify({
        "id": pomodoro_id,
        "name": data["name"],
        "type": data["type"],
        "start_time": data["start_time"],
        "end_time": data["end_time"],
        "duration_minutes": data["duration_minutes"],
        "notes": data.get("notes"),
    })


@app.route("/api/settings", methods=["GET"])
def get_settings():
    """Get user settings."""
    db = get_db()
    rows = db.execute("SELECT key, value FROM settings").fetchall()
    settings = {row["key"]: json.loads(row["value"]) for row in rows}

    # Defaults
    defaults = {
        "work_duration_minutes": 25,
        "short_break_minutes": 5,
        "long_break_minutes": 15,
        "pomodoros_until_long_break": 4,
        "sound_enabled": True,
        "notifications_enabled": True,
    }
    defaults.update(settings)
    return jsonify(defaults)


@app.route("/api/settings", methods=["POST"])
def save_settings():
    """Save user settings."""
    data = request.json
    db = get_db()

    for key, value in data.items():
        db.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, json.dumps(value)),
        )
    db.commit()

    return jsonify({"status": "ok"})


@app.route("/api/reports/<period>")
def get_report(period):
    """Get report data for a given period (day, week, month)."""
    db = get_db()
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

    # Query pomodoros in range
    rows = db.execute(
        """
        SELECT * FROM pomodoros
        WHERE start_time >= ? AND start_time < ?
        ORDER BY start_time
        """,
        (start.isoformat() + "Z", end.isoformat() + "Z"),
    ).fetchall()

    pomodoros = [dict(row) for row in rows]

    # Calculate totals
    total_minutes = sum(p["duration_minutes"] for p in pomodoros)
    total_count = len(pomodoros)

    # By type
    by_type = {t: 0 for t in POMODORO_TYPES}
    for p in pomodoros:
        if p["type"] in by_type:
            by_type[p["type"]] += p["duration_minutes"]

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
    """Export pomodoros as CSV."""
    db = get_db()
    rows = db.execute("SELECT * FROM pomodoros ORDER BY start_time DESC").fetchall()

    lines = ["id,name,type,start_time,end_time,duration_minutes,notes"]
    for row in rows:
        r = dict(row)
        # Escape quotes in fields
        name = (r["name"] or "").replace('"', '""')
        notes = (r["notes"] or "").replace('"', '""')
        lines.append(
            f'"{r["id"]}","{name}","{r["type"]}","{r["start_time"]}",'
            f'"{r["end_time"]}",{r["duration_minutes"]},"{notes}"'
        )

    from flask import Response
    return Response(
        "\n".join(lines),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=pomodoros.csv"},
    )


if __name__ == "__main__":
    import os
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    app.run(host=host, port=5000)

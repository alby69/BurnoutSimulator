import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path("database/analytics.db")


def get_connection():
    Path("database").mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            player_name TEXT,
            company_type TEXT,
            started_at TEXT,
            ended_at TEXT,
            days_survived INTEGER,
            final_status TEXT,
            ending TEXT
        );

        CREATE TABLE IF NOT EXISTS choices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            turn_number INTEGER,
            event_id TEXT,
            choice_id TEXT,
            choice_text TEXT,
            choice_category TEXT,
            timestamp TEXT,
            stats_before TEXT,
            stats_after TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );

        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            tag_name TEXT,
            count INTEGER,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );
    """)
    conn.commit()
    conn.close()


def create_session(session_id: str, player_name: str, company_type: str):
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO sessions (id, player_name, company_type, started_at) VALUES (?, ?, ?, ?)",
        (session_id, player_name, company_type, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def end_session(session_id: str, days_survived: int, final_status: str, ending: str):
    conn = get_connection()
    conn.execute(
        "UPDATE sessions SET ended_at = ?, days_survived = ?, final_status = ?, ending = ? WHERE id = ?",
        (datetime.now(timezone.utc).isoformat(), days_survived, final_status, ending, session_id),
    )
    conn.commit()
    conn.close()


def record_choice(
    session_id: str,
    turn_number: int,
    event_id: str,
    choice_id: str,
    choice_text: str,
    choice_category: str,
    stats_before: dict,
    stats_after: dict,
):
    conn = get_connection()
    conn.execute(
        """INSERT INTO choices
           (session_id, turn_number, event_id, choice_id, choice_text, choice_category,
            timestamp, stats_before, stats_after)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            session_id,
            turn_number,
            event_id,
            choice_id,
            choice_text,
            choice_category,
            datetime.now(timezone.utc).isoformat(),
            json.dumps(stats_before),
            json.dumps(stats_after),
        ),
    )
    conn.commit()
    conn.close()


def record_tags(session_id: str, tags: dict):
    conn = get_connection()
    for tag_name, count in tags.items():
        if count > 0:
            conn.execute(
                "INSERT INTO tags (session_id, tag_name, count) VALUES (?, ?, ?)",
                (session_id, tag_name, count),
            )
    conn.commit()
    conn.close()


def get_choice_stats() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("""
        SELECT event_id, choice_id, choice_text, choice_category, COUNT(*) as times_chosen
        FROM choices
        GROUP BY event_id, choice_id
        ORDER BY times_chosen DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_ending_stats() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("""
        SELECT ending, COUNT(*) as count
        FROM sessions
        WHERE ending IS NOT NULL
        GROUP BY ending
        ORDER BY count DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

AGENT_DB_PATH = Path("database/agents.db")


def init_agent_db():
    conn = sqlite3.connect(str(AGENT_DB_PATH))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS agents (
            agent_id TEXT PRIMARY KEY,
            name TEXT,
            profile_name TEXT,
            profile_json TEXT,
            company_type TEXT,
            created_at TEXT,
            total_decisions INTEGER DEFAULT 0,
            auto_decisions INTEGER DEFAULT 0,
            human_decisions INTEGER DEFAULT 0,
            final_status TEXT,
            final_ending TEXT,
            days_survived INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS agent_decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            turn_number INTEGER,
            event_id TEXT,
            choice_id TEXT,
            choice_category TEXT,
            was_auto BOOLEAN,
            human_id TEXT,
            stats_before TEXT,
            stats_after TEXT,
            timestamp TEXT
        );

        CREATE TABLE IF NOT EXISTS human_jumps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            human_id TEXT,
            from_agent_id TEXT,
            to_agent_id TEXT,
            from_day INTEGER,
            to_day INTEGER,
            reason TEXT,
            declared_mood TEXT,
            timestamp TEXT
        );

        CREATE TABLE IF NOT EXISTS human_profiles (
            human_id TEXT PRIMARY KEY,
            name TEXT,
            created_at TEXT,
            total_jumps INTEGER DEFAULT 0,
            unique_agents INTEGER DEFAULT 0,
            emergent_profile_json TEXT
        );

        CREATE TABLE IF NOT EXISTS swarm_sessions (
            session_id TEXT PRIMARY KEY,
            num_agents INTEGER,
            started_at TEXT,
            ended_at TEXT,
            total_turns INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS swarm_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            turn_number INTEGER,
            profile_distribution_json TEXT,
            avg_stats_json TEXT,
            timestamp TEXT
        );
    """)
    conn.commit()
    conn.close()


def clear_agents():
    with sqlite3.connect(str(AGENT_DB_PATH)) as conn:
        conn.execute("DELETE FROM agents")
        conn.commit()


def save_agent(agent_data: dict):
    with sqlite3.connect(str(AGENT_DB_PATH)) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO agents (
                agent_id, name, profile_name, profile_json, company_type,
                created_at, total_decisions, auto_decisions, human_decisions,
                final_status, final_ending, days_survived
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                agent_data["agent_id"],
                agent_data["name"],
                agent_data["profile_name"],
                json.dumps(agent_data.get("profile_json", {})),
                agent_data["company_type"],
                agent_data.get("created_at", datetime.now(timezone.utc).isoformat()),
                agent_data.get("total_decisions", 0),
                agent_data.get("auto_decisions", 0),
                agent_data.get("human_decisions", 0),
                agent_data.get("final_status"),
                agent_data.get("final_ending"),
                agent_data.get("days_survived", 0),
            ),
        )


def save_decision(decision_data: dict):
    with sqlite3.connect(str(AGENT_DB_PATH)) as conn:
        conn.execute(
            """
            INSERT INTO agent_decisions (
                agent_id, turn_number, event_id, choice_id, choice_category,
                was_auto, human_id, stats_before, stats_after, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                decision_data["agent_id"],
                decision_data["turn_number"],
                decision_data["event_id"],
                decision_data["choice_id"],
                decision_data["choice_category"],
                decision_data["was_auto"],
                decision_data.get("human_id"),
                json.dumps(decision_data.get("stats_before", {})),
                json.dumps(decision_data.get("stats_after", {})),
                decision_data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            ),
        )


def save_jump(jump_data: dict):
    with sqlite3.connect(str(AGENT_DB_PATH)) as conn:
        conn.execute(
            """
            INSERT INTO human_jumps (
                human_id, from_agent_id, to_agent_id, from_day, to_day,
                reason, declared_mood, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                jump_data["human_id"],
                jump_data["from_agent_id"],
                jump_data["to_agent_id"],
                jump_data["from_day"],
                jump_data["to_day"],
                jump_data.get("reason"),
                jump_data.get("declared_mood"),
                jump_data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            ),
        )


def save_human_profile(profile_data: dict):
    with sqlite3.connect(str(AGENT_DB_PATH)) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO human_profiles (
                human_id, name, created_at, total_jumps, unique_agents, emergent_profile_json
            ) VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                profile_data["human_id"],
                profile_data["name"],
                profile_data.get("created_at", datetime.now(timezone.utc).isoformat()),
                profile_data.get("total_jumps", 0),
                profile_data.get("unique_agents", 0),
                json.dumps(profile_data.get("emergent_profile", {})),
            ),
        )


def save_swarm_session(session_data: dict):
    with sqlite3.connect(str(AGENT_DB_PATH)) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO swarm_sessions (
                session_id, num_agents, started_at, ended_at, total_turns
            ) VALUES (?, ?, ?, ?, ?)
        """,
            (
                session_data["session_id"],
                session_data["num_agents"],
                session_data.get("started_at", datetime.now(timezone.utc).isoformat()),
                session_data.get("ended_at"),
                session_data.get("total_turns", 0),
            ),
        )


def save_swarm_history(history_data: dict):
    with sqlite3.connect(str(AGENT_DB_PATH)) as conn:
        conn.execute(
            """
            INSERT INTO swarm_history (
                session_id, turn_number, profile_distribution_json, avg_stats_json, timestamp
            ) VALUES (?, ?, ?, ?, ?)
        """,
            (
                history_data["session_id"],
                history_data["turn_number"],
                json.dumps(history_data.get("profile_distribution", {})),
                json.dumps(history_data.get("avg_stats", {})),
                history_data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            ),
        )


def get_swarm_session(session_id: str) -> Optional[dict]:
    with sqlite3.connect(str(AGENT_DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM swarm_sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        return dict(row) if row else None


def get_all_agents() -> list:
    with sqlite3.connect(str(AGENT_DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM agents").fetchall()
        return [dict(r) for r in rows]


def get_all_human_profiles() -> list:
    with sqlite3.connect(str(AGENT_DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM human_profiles").fetchall()
        return [dict(r) for r in rows]


def get_swarm_history(session_id: str) -> list:
    with sqlite3.connect(str(AGENT_DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM swarm_history WHERE session_id = ? ORDER BY turn_number ASC",
            (session_id,),
        ).fetchall()
        return [dict(r) for r in rows]

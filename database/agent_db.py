import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

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
    """)
    conn.commit()
    conn.close()

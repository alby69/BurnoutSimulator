import unittest
import os
import sqlite3
import json
from pathlib import Path
from database import analytics

class TestAnalytics(unittest.TestCase):
    def setUp(self):
        # Redirect DB path for testing
        self.test_db = Path("database/test_analytics.db")
        analytics.DB_PATH = self.test_db
        analytics.init_db()

    def tearDown(self):
        if self.test_db.exists():
            self.test_db.unlink()

    def test_session_flow(self):
        session_id = "test_session_123"
        analytics.create_session(session_id, "Test Player", "Startup")

        # Verify creation
        conn = sqlite3.connect(str(self.test_db))
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[1], "Test Player")

        # Record a choice
        analytics.record_choice(
            session_id, 1, "ev1", "ch1", "Choice text", "COMPLIANCE",
            {"stress": 0}, {"stress": 5}, 1500
        )

        row_choice = conn.execute("SELECT * FROM choices WHERE session_id = ?", (session_id,)).fetchone()
        self.assertIsNotNone(row_choice)
        self.assertEqual(row_choice[4], "ch1")
        self.assertEqual(row_choice[10], 1500)

        # End session
        analytics.end_session(session_id, 10, "Burnout", "Il Caduto")
        row_end = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        self.assertEqual(row_end[5], 10)
        self.assertEqual(row_end[7], "Il Caduto")

        conn.close()

if __name__ == "__main__":
    unittest.main()

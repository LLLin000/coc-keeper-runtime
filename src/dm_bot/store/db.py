"""SQLite persistence layer."""

import sqlite3
from pathlib import Path


class Store:
    """简单的 SQLite 持久化存储"""

    def __init__(self, db_path: str = "dm_bot.db") -> None:
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    adventure_id TEXT,
                    current_scene_id TEXT,
                    scene_state TEXT,
                    player_locations TEXT,  -- JSON dict
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS characters (
                    character_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT,
                    sheet_json TEXT  -- JSON
                );
                """
            )

    def save_session(self, session_id: str, data: dict) -> None:
        import json
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO sessions (session_id, adventure_id, current_scene_id, scene_state, player_locations)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    adventure_id=excluded.adventure_id,
                    current_scene_id=excluded.current_scene_id,
                    scene_state=excluded.scene_state,
                    player_locations=excluded.player_locations
                """,
                (
                    session_id,
                    data.get("adventure_id"),
                    data.get("current_scene_id"),
                    data.get("scene_state"),
                    json.dumps(data.get("player_locations", {})),
                ),
            )

    def load_session(self, session_id: str) -> dict | None:
        import json
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
            if not row:
                return None
            return {
                "session_id": row[0],
                "adventure_id": row[1],
                "current_scene_id": row[2],
                "scene_state": row[3],
                "player_locations": json.loads(row[4]) if row[4] else {},
            }

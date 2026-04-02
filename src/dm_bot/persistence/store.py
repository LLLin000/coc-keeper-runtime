import json
import sqlite3
from pathlib import Path


class PersistenceStore:
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._conn: sqlite3.Connection | None = None
        # For :memory: mode, create a single shared connection so tables persist
        # across all operations. File-based SQLite works fine with per-operation
        # connections because the database lives on disk.
        if str(self._path) == ":memory:":
            self._conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
        self._init_db()

    def close(self) -> None:
        pass

    def _connect(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        return sqlite3.connect(str(self._path))

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                "create table if not exists campaign_state (campaign_id text primary key, state_json text not null)"
            )
            conn.execute(
                "create table if not exists campaign_sessions (id integer primary key check (id = 1), sessions_json text not null)"
            )
            conn.execute(
                "create table if not exists campaign_events (id integer primary key autoincrement, campaign_id text not null, trace_id text not null, event_type text not null, payload_json text not null)"
            )
            conn.execute(
                "create table if not exists archive_profiles (id integer primary key check (id = 1), profiles_json text not null)"
            )

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def save_campaign_state(self, campaign_id: str, state: dict[str, object]) -> None:
        with self._connect() as conn:
            conn.execute(
                "insert into campaign_state(campaign_id, state_json) values(?, ?) "
                "on conflict(campaign_id) do update set state_json=excluded.state_json",
                (campaign_id, json.dumps(state, ensure_ascii=False)),
            )

    def load_campaign_state(self, campaign_id: str) -> dict[str, object]:
        with self._connect() as conn:
            row = conn.execute(
                "select state_json from campaign_state where campaign_id = ?",
                (campaign_id,),
            ).fetchone()
        return json.loads(row[0]) if row else {}

    def save_sessions(self, sessions: dict[str, dict[str, object]]) -> None:
        with self._connect() as conn:
            conn.execute(
                "insert into campaign_sessions(id, sessions_json) values(1, ?) "
                "on conflict(id) do update set sessions_json=excluded.sessions_json",
                (json.dumps(sessions, ensure_ascii=False),),
            )

    def load_sessions(self) -> dict[str, dict[str, object]]:
        with self._connect() as conn:
            row = conn.execute(
                "select sessions_json from campaign_sessions where id = 1"
            ).fetchone()
        return json.loads(row[0]) if row else {}

    def append_event(
        self,
        *,
        campaign_id: str,
        trace_id: str,
        event_type: str,
        payload: dict[str, object],
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                "insert into campaign_events(campaign_id, trace_id, event_type, payload_json) values(?, ?, ?, ?)",
                (
                    campaign_id,
                    trace_id,
                    event_type,
                    json.dumps(payload, ensure_ascii=False),
                ),
            )

    def list_events(self, campaign_id: str) -> list[dict[str, object]]:
        with self._connect() as conn:
            rows = conn.execute(
                "select trace_id, event_type, payload_json from campaign_events where campaign_id = ? order by id asc",
                (campaign_id,),
            ).fetchall()
        return [
            {
                "trace_id": trace_id,
                "event_type": event_type,
                "payload": json.loads(payload_json),
            }
            for trace_id, event_type, payload_json in rows
        ]

    def save_archive_profiles(self, profiles: dict[str, object]) -> None:
        with self._connect() as conn:
            conn.execute(
                "insert into archive_profiles(id, profiles_json) values(1, ?) "
                "on conflict(id) do update set profiles_json=excluded.profiles_json",
                (json.dumps(profiles, ensure_ascii=False),),
            )

    def load_archive_profiles(self) -> dict[str, object]:
        with self._connect() as conn:
            row = conn.execute(
                "select profiles_json from archive_profiles where id = 1"
            ).fetchone()
        return json.loads(row[0]) if row else {}

    def save_profile(self, user_id: str, profile: dict) -> None:
        """Save a profile to the database.

        Args:
            user_id: The user ID
            profile: Profile data as dict
        """
        profile_id = profile.get("profile_id")
        if not profile_id:
            raise ValueError("Profile must have profile_id")

        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS profiles (
                    user_id TEXT NOT NULL,
                    profile_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, profile_id)
                )
                """
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO profiles (user_id, profile_id, data)
                VALUES (?, ?, ?)
                """,
                (user_id, profile_id, json.dumps(profile, ensure_ascii=False)),
            )
            conn.commit()

    def load_profile(self, user_id: str, profile_id: str) -> dict | None:
        """Load a profile from the database.

        Args:
            user_id: The user ID
            profile_id: The profile ID

        Returns:
            Profile data as dict, or None if not found
        """
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT data FROM profiles WHERE user_id = ? AND profile_id = ?",
                (user_id, profile_id),
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None

    def load_user_profiles(self, user_id: str) -> list[dict]:
        """Load all profiles for a user.

        Args:
            user_id: The user ID

        Returns:
            List of profile dicts
        """
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT data FROM profiles WHERE user_id = ?", (user_id,)
            )
            return [json.loads(row[0]) for row in cursor.fetchall()]

    def delete_profile(self, user_id: str, profile_id: str) -> bool:
        """Delete a profile from the database.

        Args:
            user_id: The user ID
            profile_id: The profile ID

        Returns:
            True if deleted, False if not found
        """
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM profiles WHERE user_id = ? AND profile_id = ?",
                (user_id, profile_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def save_governance_events(self, events_state: dict) -> None:
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS governance_events (id INTEGER PRIMARY KEY CHECK (id = 1), events_json TEXT NOT NULL)"
            )
            conn.execute(
                "INSERT OR REPLACE INTO governance_events(id, events_json) VALUES(1, ?) ",
                (json.dumps(events_state, ensure_ascii=False),),
            )
            conn.commit()

    def load_governance_events(self) -> dict:
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS governance_events (id INTEGER PRIMARY KEY CHECK (id = 1), events_json TEXT NOT NULL)"
            )
            row = conn.execute(
                "SELECT events_json FROM governance_events WHERE id = 1"
            ).fetchone()
        return json.loads(row[0]) if row else {"events": []}

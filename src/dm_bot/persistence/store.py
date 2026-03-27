import json
import sqlite3
from pathlib import Path


class PersistenceStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._path)

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
            row = conn.execute("select sessions_json from campaign_sessions where id = 1").fetchone()
        return json.loads(row[0]) if row else {}

    def append_event(self, *, campaign_id: str, trace_id: str, event_type: str, payload: dict[str, object]) -> None:
        with self._connect() as conn:
            conn.execute(
                "insert into campaign_events(campaign_id, trace_id, event_type, payload_json) values(?, ?, ?, ?)",
                (campaign_id, trace_id, event_type, json.dumps(payload, ensure_ascii=False)),
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
            row = conn.execute("select profiles_json from archive_profiles where id = 1").fetchone()
        return json.loads(row[0]) if row else {}

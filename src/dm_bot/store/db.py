"""SQLite persistence layer."""

import sqlite3
from pathlib import Path
from dm_bot.trigger.models import BlockerCheckpoint, TriggerChain, AuditEntry


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
                CREATE TABLE IF NOT EXISTS blockers (
                    blocker_id TEXT PRIMARY KEY,
                    trigger_chain_id TEXT NOT NULL,
                    scene_id TEXT DEFAULT '',
                    reason TEXT NOT NULL,
                    payload TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS trigger_chains (
                    chain_id TEXT PRIMARY KEY,
                    event_id TEXT DEFAULT '',
                    event_type TEXT NOT NULL,
                    trigger_id TEXT NOT NULL,
                    status TEXT DEFAULT 'running',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS audit_entries (
                    entry_id TEXT PRIMARY KEY,
                    chain_id TEXT NOT NULL,
                    step TEXT NOT NULL,
                    detail TEXT DEFAULT '{}',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

    def save_blocker(self, blocker: BlockerCheckpoint) -> None:
        import json
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO blockers
                   (blocker_id, trigger_chain_id, scene_id, reason, payload, created_at, resolved_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (blocker.blocker_id, blocker.trigger_chain_id, blocker.scene_id,
                 blocker.reason, json.dumps(blocker.payload),
                 blocker.created_at.isoformat(),
                 blocker.resolved_at.isoformat() if blocker.resolved_at else None),
            )

    def load_blocker(self, blocker_id: str) -> BlockerCheckpoint | None:
        import json
        from datetime import datetime
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM blockers WHERE blocker_id = ?", (blocker_id,)
            ).fetchone()
            if not row:
                return None
            return BlockerCheckpoint(
                blocker_id=row[0], trigger_chain_id=row[1], scene_id=row[2] or "",
                reason=row[3], payload=json.loads(row[4]) if row[4] else {},
                created_at=datetime.fromisoformat(row[5]),
                resolved_at=datetime.fromisoformat(row[6]) if row[6] else None,
            )

    def list_unresolved_blockers(self) -> list[BlockerCheckpoint]:
        import json
        from datetime import datetime
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM blockers WHERE resolved_at IS NULL"
            ).fetchall()
            return [
                BlockerCheckpoint(
                    blocker_id=r[0], trigger_chain_id=r[1], scene_id=r[2] or "",
                    reason=r[3], payload=json.loads(r[4]) if r[4] else {},
                    created_at=datetime.fromisoformat(r[5]),
                )
                for r in rows
            ]

    def save_chain(self, chain: TriggerChain) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO trigger_chains
                   (chain_id, event_id, event_type, trigger_id, status, created_at, completed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (chain.chain_id, chain.event_id, chain.event_type,
                 chain.trigger_id, chain.status,
                 chain.created_at.isoformat(),
                 chain.completed_at.isoformat() if chain.completed_at else None),
            )

    def load_chain(self, chain_id: str) -> TriggerChain | None:
        from datetime import datetime
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM trigger_chains WHERE chain_id = ?", (chain_id,)
            ).fetchone()
            if not row:
                return None
            return TriggerChain(
                chain_id=row[0], event_id=row[1] or "", event_type=row[2],
                trigger_id=row[3], status=row[4],
                created_at=datetime.fromisoformat(row[5]),
                completed_at=datetime.fromisoformat(row[6]) if row[6] else None,
            )

    def list_chains_by_status(self, status: str) -> list[TriggerChain]:
        from datetime import datetime
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM trigger_chains WHERE status = ?", (status,)
            ).fetchall()
            return [
                TriggerChain(
                    chain_id=r[0], event_id=r[1] or "", event_type=r[2],
                    trigger_id=r[3], status=r[4],
                    created_at=datetime.fromisoformat(r[5]),
                    completed_at=datetime.fromisoformat(r[6]) if r[6] else None,
                )
                for r in rows
            ]

    def save_audit_entry(self, entry: AuditEntry) -> None:
        import json
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO audit_entries
                   (entry_id, chain_id, step, detail, timestamp)
                   VALUES (?, ?, ?, ?, ?)""",
                (entry.entry_id, entry.chain_id, entry.step,
                 json.dumps(entry.detail), entry.timestamp.isoformat()),
            )

    def list_audit_entries(self, chain_id: str) -> list[AuditEntry]:
        import json
        from datetime import datetime
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM audit_entries WHERE chain_id = ? ORDER BY timestamp ASC",
                (chain_id,)
            ).fetchall()
            return [
                AuditEntry(
                    entry_id=r[0], chain_id=r[1], step=r[2],
                    detail=json.loads(r[3]) if r[3] else {},
                    timestamp=datetime.fromisoformat(r[4]),
                )
                for r in rows
            ]

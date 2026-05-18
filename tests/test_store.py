"""Tests for Store persistence."""

from dm_bot.store.db import Store
import tempfile, os

SCHEMA_VERSION = 1


class TestSchemaVersion:
    def test_schema_version_table_exists(self):
        db_path = os.path.join(tempfile.gettempdir(), "test_schema.db")
        store = Store(db_path)
        store.close()
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            rows = conn.execute(
                "SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1"
            ).fetchall()
        assert len(rows) == 1
        assert rows[0][0] == SCHEMA_VERSION
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except PermissionError:
                pass

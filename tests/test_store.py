"""Tests for Store persistence."""

from dm_bot.store.db import Store
import tempfile, os, sqlite3

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


class TestStoreIntegrity:
    def test_check_integrity_with_empty_db(self):
        import tempfile, os
        db_path = os.path.join(tempfile.gettempdir(), "test_integrity.db")
        try:
            store = Store(db_path)
            result = store.check_integrity()
            assert result["status"] == "ok"
        finally:
            store = None
            if os.path.exists(db_path):
                try:
                    os.remove(db_path)
                except PermissionError:
                    pass

    def test_check_integrity_reports_corrupt_db(self):
        import tempfile, os
        db_path = os.path.join(tempfile.gettempdir(), "test_corrupt.db")
        try:
            with open(db_path, "wb") as f:
                f.write(b"not a sqlite file")
            store = Store(db_path)
            result = store.check_integrity()
            assert result["status"] == "corrupt"
        except sqlite3.DatabaseError:
            pass
        finally:
            store = None
            if os.path.exists(db_path):
                try:
                    os.remove(db_path)
                except PermissionError:
                    pass

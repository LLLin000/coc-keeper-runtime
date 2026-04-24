"""Tests for SQLite store."""

import pytest

from dm_bot.store.db import Store


@pytest.fixture
def file_store(tmp_path):
    db_path = tmp_path / "test.db"
    return Store(str(db_path))


class TestStore:
    def test_save_and_load_session(self, file_store):
        store = file_store
        data = {
            "adventure_id": "starter_crypt",
            "current_scene_id": "scene_1",
            "scene_state": "collecting",
            "player_locations": {"u1": "scene_1"},
        }

        store.save_session("session1", data)
        loaded = store.load_session("session1")

        assert loaded is not None
        assert loaded["adventure_id"] == "starter_crypt"
        assert loaded["current_scene_id"] == "scene_1"

    def test_load_nonexistent_session(self, file_store):
        store = file_store
        loaded = store.load_session("session99")
        assert loaded is None

    def test_save_overwrite(self, file_store):
        store = file_store
        store.save_session("s1", {"adventure_id": "old", "current_scene_id": "", "scene_state": "", "player_locations": {}})
        store.save_session("s1", {"adventure_id": "new", "current_scene_id": "", "scene_state": "", "player_locations": {}})
        loaded = store.load_session("s1")
        assert loaded["adventure_id"] == "new"

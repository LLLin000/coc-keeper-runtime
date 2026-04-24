"""Shared pytest fixtures for Discord AI Keeper tests."""

from __future__ import annotations

import pytest
from pathlib import Path

from dm_bot.store.db import Store


@pytest.fixture
def sqlite_memory_store():
    return Store(":memory:")


@pytest.fixture
def sqlite_memory_path(tmp_path):
    return tmp_path / "test.db"

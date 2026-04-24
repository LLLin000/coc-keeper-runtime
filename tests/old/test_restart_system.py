from pathlib import Path

from dm_bot.runtime.restart_system import (
    READY_MARKER,
    SYNC_MARKER,
    log_contains_marker,
    runtime_bootstrap_complete,
)


def test_log_contains_marker_detects_written_marker(tmp_path: Path) -> None:
    log_path = tmp_path / "bot.stdout.log"
    log_path.write_text("booting\nREADY dndbot#9660 123\n", encoding="utf-8")

    assert log_contains_marker(log_path, READY_MARKER)
    assert not log_contains_marker(log_path, SYNC_MARKER)


def test_runtime_bootstrap_complete_requires_sync(tmp_path: Path) -> None:
    log_path = tmp_path / "bot.startup.log"
    log_path.write_text("CONNECTED\n", encoding="utf-8")

    assert not runtime_bootstrap_complete(log_path)

    log_path.write_text("SYNC_DONE global=1 guild=24\n", encoding="utf-8")

    assert runtime_bootstrap_complete(log_path)

from pathlib import Path

from dm_bot.runtime.smoke_check import ready_seen_in_log, sync_seen_in_log


def test_ready_seen_in_log_detects_ready_line(tmp_path: Path) -> None:
    log_path = tmp_path / "bot.log"
    log_path.write_text("booting\nREADY dndbot#9660 123\n", encoding="utf-8")

    assert ready_seen_in_log(log_path)


def test_ready_seen_in_log_ignores_missing_or_unrelated_logs(tmp_path: Path) -> None:
    assert not ready_seen_in_log(tmp_path / "missing.log")
    log_path = tmp_path / "bot.log"
    log_path.write_text("booting\nstill booting\n", encoding="utf-8")

    assert not ready_seen_in_log(log_path)


def test_sync_seen_in_log_detects_sync_line(tmp_path: Path) -> None:
    log_path = tmp_path / "bot.log"
    log_path.write_text("SYNC_DONE global=1 guild=24\n", encoding="utf-8")

    assert sync_seen_in_log(log_path)

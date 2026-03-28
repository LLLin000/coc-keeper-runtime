from __future__ import annotations

import subprocess
import sys
import time
import os
import json
from pathlib import Path

SYNC_MARKER = "SYNC_DONE"
READY_MARKER = "READY "


def ready_seen_in_log(log_path: Path) -> bool:
    if not log_path.exists():
        return False
    try:
        return "READY " in log_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False


def log_contains_marker(log_path: Path, marker: str) -> bool:
    if not log_path.exists():
        return False
    try:
        return marker in log_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False


def sync_seen_in_log(log_path: Path) -> bool:
    return log_contains_marker(log_path, SYNC_MARKER)


def terminate_existing_bot_processes(*, current_pid: int) -> None:
    command = (
        "Get-CimInstance Win32_Process | "
        "Where-Object { $_.CommandLine -match 'dm_bot\\.main run-bot' } | "
        f"Where-Object {{ $_.ProcessId -ne {current_pid} }} | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        check=False,
        capture_output=True,
        text=True,
    )


def run_local_smoke_check(*, cwd: Path, wait_seconds: int = 8) -> int:
    test_result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=cwd,
        check=False,
    )
    if test_result.returncode != 0:
        return test_result.returncode

    terminate_existing_bot_processes(current_pid=os.getpid())
    log_path = cwd / "bot.smoke.log"
    startup_marker_log = cwd / "bot.smoke.startup.log"
    status_log = cwd / "bot.smoke.status.json"
    for path in (log_path, startup_marker_log):
        if path.exists():
            path.unlink()

    env = dict(os.environ)
    env["PYTHONUNBUFFERED"] = "1"
    env["DM_BOT_STARTUP_MARKER_FILE"] = str(startup_marker_log)
    process = subprocess.Popen(
        [sys.executable, "-m", "dm_bot.main", "run-bot"],
        cwd=str(cwd),
        env=env,
        stdout=log_path.open("w", encoding="utf-8"),
        stderr=subprocess.STDOUT,
    )
    try:
        deadline = time.time() + max(wait_seconds, 15)
        sync_seen = False
        ready_seen = False
        while time.time() < deadline:
            if process.poll() is not None:
                _write_smoke_status(
                    status_log,
                    passed=False,
                    summary="bot exited before sync completed",
                )
                return 1
            sync_seen = sync_seen_in_log(startup_marker_log)
            ready_seen = log_contains_marker(startup_marker_log, READY_MARKER)
            if sync_seen:
                break
            time.sleep(0.5)
        if not sync_seen:
            _write_smoke_status(
                status_log,
                passed=False,
                summary="sync marker not observed before timeout",
            )
            return 1
        time.sleep(5)
        if process.poll() is not None:
            _write_smoke_status(
                status_log,
                passed=False,
                summary="bot exited after sync completed",
            )
            return 1
        _write_smoke_status(
            status_log,
            passed=True,
            summary=(
                "smoke-check passed"
                if ready_seen
                else "smoke-check passed (sync completed, READY marker not observed)"
            ),
        )
        return 0
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


def _write_smoke_status(status_file: Path, *, passed: bool, summary: str) -> None:
    status_file.write_text(
        json.dumps(
            {
                "passed": passed,
                "summary": summary,
                "last_run_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

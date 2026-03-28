from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from dm_bot.runtime.process_control import launch_detached_process
from dm_bot.runtime.smoke_check import terminate_existing_bot_processes

READY_MARKER = "READY "
SYNC_MARKER = "SYNC_DONE"


def log_contains_marker(log_path: Path, marker: str) -> bool:
    if not log_path.exists():
        return False
    try:
        return marker in log_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False


def runtime_bootstrap_complete(marker_log: Path) -> bool:
    return log_contains_marker(marker_log, SYNC_MARKER)


def run_restart_system(*, cwd: Path, wait_seconds: int = 60) -> int:
    smoke = subprocess.run(
        [sys.executable, "-m", "dm_bot.main", "smoke-check"],
        cwd=cwd,
        check=False,
    )
    if smoke.returncode != 0:
        return smoke.returncode

    terminate_existing_bot_processes(current_pid=os.getpid())

    stdout_log = cwd / "bot.stdout.log"
    stderr_log = cwd / "bot.stderr.log"
    startup_marker_log = cwd / "bot.startup.log"
    restart_log = cwd / "bot.restart.log"
    for path in (stdout_log, stderr_log, startup_marker_log, restart_log):
        if path.exists():
            path.unlink()

    env = {
        "PYTHONUNBUFFERED": "1",
        "DM_BOT_STARTUP_MARKER_FILE": str(startup_marker_log),
    }
    launched_pid = launch_detached_process(
        executable=sys.executable,
        args=["-m", "dm_bot.main", "run-bot"],
        cwd=cwd,
        env=env,
        stdout_log=stdout_log,
        stderr_log=stderr_log,
    )
    if launched_pid is None:
        restart_log.write_text(
            "launched_pid=\nactive_pid=\nready_seen=False\nsync_seen=False\nalive=False\nresult=1",
            encoding="utf-8",
        )
        return 1

    deadline = time.time() + wait_seconds
    result = 1
    active_pid: int | None = None
    while time.time() < deadline:
        if runtime_bootstrap_complete(startup_marker_log):
            time.sleep(5)
            active_pid = _find_active_bot_pid()
            result = 0 if active_pid is not None else 1
            break
        time.sleep(0.5)

    restart_log.write_text(
        "\n".join(
            [
                f"launched_pid={launched_pid}",
                f"active_pid={active_pid or ''}",
                f"ready_seen={log_contains_marker(startup_marker_log, READY_MARKER)}",
                f"sync_seen={log_contains_marker(startup_marker_log, SYNC_MARKER)}",
                f"alive={active_pid is not None}",
                f"result={result}",
            ]
        ),
        encoding="utf-8",
    )
    return result


def _find_active_bot_pid() -> int | None:
    command = (
        "Get-CimInstance Win32_Process | "
        "Where-Object { $_.CommandLine -match 'dm_bot\\.main run-bot' } | "
        "Select-Object -ExpandProperty ProcessId"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        check=False,
        capture_output=True,
        text=True,
    )
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        return None
    try:
        return int(lines[0])
    except ValueError:
        return None

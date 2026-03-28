from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

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


def runtime_bootstrap_complete(stdout_log: Path) -> bool:
    return log_contains_marker(stdout_log, READY_MARKER) and log_contains_marker(
        stdout_log, SYNC_MARKER
    )


def run_restart_system(*, cwd: Path, wait_seconds: int = 20) -> int:
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
    restart_log = cwd / "bot.restart.log"
    for path in (stdout_log, stderr_log, restart_log):
        if path.exists():
            path.unlink()

    env = dict(os.environ)
    env["PYTHONUNBUFFERED"] = "1"
    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    stdout_handle = stdout_log.open("w", encoding="utf-8")
    stderr_handle = stderr_log.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [sys.executable, "-m", "dm_bot.main", "run-bot"],
        cwd=str(cwd),
        env=env,
        stdout=stdout_handle,
        stderr=stderr_handle,
        creationflags=creationflags,
    )
    stdout_handle.close()
    stderr_handle.close()

    deadline = time.time() + wait_seconds
    result = 1
    while time.time() < deadline:
        if process.poll() is not None:
            result = 1
            break
        if runtime_bootstrap_complete(stdout_log):
            time.sleep(5)
            result = 0 if process.poll() is None else 1
            break
        time.sleep(0.5)

    restart_log.write_text(
        "\n".join(
            [
                f"pid={process.pid}",
                f"ready_seen={log_contains_marker(stdout_log, READY_MARKER)}",
                f"sync_seen={log_contains_marker(stdout_log, SYNC_MARKER)}",
                f"alive={process.poll() is None}",
                f"result={result}",
            ]
        ),
        encoding="utf-8",
    )
    return result

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Literal

import httpx
from pydantic import BaseModel, Field

from dm_bot.config import Settings, get_settings
from dm_bot.runtime.model_checks import build_model_snapshot
from dm_bot.runtime.process_control import launch_detached_process
from dm_bot.runtime.restart_system import run_restart_system, runtime_bootstrap_complete
from dm_bot.runtime.smoke_check import run_local_smoke_check


class ProcessStatus(BaseModel):
    kind: str
    running: bool = False
    pid: int | None = None
    healthy: bool = False
    ready_seen: bool = False
    sync_seen: bool = False
    last_ready_line: str | None = None
    last_sync_line: str | None = None
    last_error_excerpt: str | None = None


class ModelStatus(BaseModel):
    router_model: str
    router_available: bool = False
    narrator_model: str
    narrator_available: bool = False
    last_checked_at: str | None = None


class SmokeCheckStatus(BaseModel):
    passed: bool | None = None
    summary: str = "never run"
    last_run_at: str | None = None


class ControlLogs(BaseModel):
    startup_tail: list[str] = Field(default_factory=list)
    restart_tail: list[str] = Field(default_factory=list)
    stdout_tail: list[str] = Field(default_factory=list)
    stderr_tail: list[str] = Field(default_factory=list)


class RuntimeControlState(BaseModel):
    bot: ProcessStatus
    api: ProcessStatus
    models: ModelStatus
    smoke_check: SmokeCheckStatus
    logs: ControlLogs
    overall_health: Literal["healthy", "degraded", "down"]


class ControlActionResult(BaseModel):
    ok: bool
    action: str
    summary: str
    details: str | None = None
    state_snapshot: RuntimeControlState


class RuntimeControlService:
    def __init__(self, *, cwd: Path, settings: Settings | None = None) -> None:
        self.cwd = cwd
        self.settings = settings or get_settings()

    def get_state(self) -> RuntimeControlState:
        bot = self._get_process_status("bot")
        api = self._get_process_status("api")
        models = self._get_model_status()
        smoke = self._get_last_smoke_check()
        logs = ControlLogs(
            startup_tail=self._read_log_tail(self.cwd / "bot.startup.log"),
            restart_tail=self._read_log_tail(self.cwd / "bot.restart.log"),
            stdout_tail=self._read_log_tail(self.cwd / "bot.stdout.log"),
            stderr_tail=self._read_log_tail(self.cwd / "bot.stderr.log"),
        )
        overall = "down"
        if bot.healthy and models.router_available and models.narrator_available:
            overall = "healthy"
        elif bot.running or api.running or models.router_available or models.narrator_available:
            overall = "degraded"
        return RuntimeControlState(
            bot=bot,
            api=api,
            models=models,
            smoke_check=smoke,
            logs=logs,
            overall_health=overall,
        )

    def start_bot(self) -> ControlActionResult:
        if self._get_process_status("bot").running:
            return self._action_result("start-bot", True, "bot already running")
        ok = self._launch_process("bot")
        return self._action_result(
            "start-bot",
            ok,
            "bot started" if ok else "bot failed to start",
        )

    def restart_bot(self) -> ControlActionResult:
        self._stop_processes("bot")
        ok = self._launch_process("bot")
        return self._action_result(
            "restart-bot",
            ok,
            "bot restarted" if ok else "bot restart failed",
        )

    def stop_bot(self) -> ControlActionResult:
        self._stop_processes("bot")
        return self._action_result("stop-bot", True, "bot stop requested")

    def start_api(self) -> ControlActionResult:
        if self._get_process_status("api").running:
            return self._action_result("start-api", True, "api already running")
        ok = self._launch_process("api")
        return self._action_result(
            "start-api",
            ok,
            "api started" if ok else "api failed to start",
        )

    def restart_api(self) -> ControlActionResult:
        self._stop_processes("api")
        ok = self._launch_process("api")
        return self._action_result(
            "restart-api",
            ok,
            "api restarted" if ok else "api restart failed",
        )

    def stop_api(self) -> ControlActionResult:
        self._stop_processes("api")
        return self._action_result("stop-api", True, "api stop requested")

    def restart_system(self) -> ControlActionResult:
        code = run_restart_system(cwd=self.cwd)
        return self._action_result(
            "restart-system",
            code == 0,
            "system restarted" if code == 0 else "system restart failed",
        )

    def run_smoke_check(self) -> ControlActionResult:
        code = run_local_smoke_check(cwd=self.cwd)
        self._write_smoke_status(code == 0, "smoke-check passed" if code == 0 else "smoke-check failed")
        return self._action_result(
            "smoke-check",
            code == 0,
            "smoke-check passed" if code == 0 else "smoke-check failed",
        )

    def sync_commands(self) -> ControlActionResult:
        code = self._run_sync_only()
        return self._action_result(
            "sync-commands",
            code == 0,
            "commands synced" if code == 0 else "command sync failed",
        )

    def _action_result(self, action: str, ok: bool, summary: str, details: str | None = None) -> ControlActionResult:
        return ControlActionResult(
            ok=ok,
            action=action,
            summary=summary,
            details=details,
            state_snapshot=self.get_state(),
        )

    def _get_process_status(self, kind: str) -> ProcessStatus:
        matches = self._find_processes(kind)
        running = bool(matches)
        pid = matches[0]["pid"] if running else None
        startup_log = self.cwd / "bot.startup.log"
        stderr_log = self.cwd / "bot.stderr.log"
        ready_line = self._find_marker_line(startup_log, "READY ") if kind == "bot" else None
        sync_line = self._find_marker_line(startup_log, "SYNC_DONE") if kind == "bot" else None
        healthy = running
        if kind == "bot":
            healthy = running and sync_line is not None
        if kind == "api":
            healthy = running and self._api_reachable()
        return ProcessStatus(
            kind=kind,
            running=running,
            pid=pid,
            healthy=healthy,
            ready_seen=ready_line is not None if kind == "bot" else False,
            sync_seen=sync_line is not None if kind == "bot" else False,
            last_ready_line=ready_line,
            last_sync_line=sync_line,
            last_error_excerpt=self._read_log_tail(stderr_log, lines=5)[-1] if stderr_log.exists() and self._read_log_tail(stderr_log, lines=5) else None,
        )

    def _get_model_status(self) -> ModelStatus:
        snapshot = build_model_snapshot(self.settings)
        return ModelStatus(
            router_model=self.settings.router_model,
            router_available=snapshot.checks["router_model"].reachable,
            narrator_model=self.settings.narrator_model,
            narrator_available=snapshot.checks["narrator_model"].reachable,
            last_checked_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
        )

    def _get_last_smoke_check(self) -> SmokeCheckStatus:
        status_file = self.cwd / "bot.smoke.status.json"
        if not status_file.exists():
            return SmokeCheckStatus()
        try:
            payload = json.loads(status_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return SmokeCheckStatus(summary="unreadable smoke-check status")
        return SmokeCheckStatus(
            passed=payload.get("passed"),
            summary=payload.get("summary", "unknown"),
            last_run_at=payload.get("last_run_at"),
        )

    def _write_smoke_status(self, passed: bool, summary: str) -> None:
        status_file = self.cwd / "bot.smoke.status.json"
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

    def _read_log_tail(self, path: Path, *, lines: int = 20) -> list[str]:
        if not path.exists():
            return []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            return []
        return content[-lines:]

    def _find_marker_line(self, path: Path, marker: str) -> str | None:
        for line in reversed(self._read_log_tail(path, lines=200)):
            if marker in line:
                return line
        return None

    def _find_processes(self, kind: str) -> list[dict[str, int]]:
        pattern = r"dm_bot\.main run-bot" if kind == "bot" else r"dm_bot\.main run-api"
        command = (
            "Get-CimInstance Win32_Process | "
            f"Where-Object {{ $_.CommandLine -match '{pattern}' }} | "
            "Select-Object ProcessId, CommandLine | ConvertTo-Json -Compress"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            check=False,
            capture_output=True,
            text=True,
        )
        payload = result.stdout.strip()
        if not payload:
            return []
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            return []
        if isinstance(parsed, dict):
            parsed = [parsed]
        return [{"pid": item["ProcessId"]} for item in parsed if "ProcessId" in item]

    def _stop_processes(self, kind: str) -> None:
        pattern = r"dm_bot\.main run-bot" if kind == "bot" else r"dm_bot\.main run-api"
        command = (
            "Get-CimInstance Win32_Process | "
            f"Where-Object {{ $_.CommandLine -match '{pattern}' }} | "
            "ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            check=False,
            capture_output=True,
            text=True,
        )

    def _launch_process(self, kind: str, *, wait_seconds: int = 30) -> bool:
        stdout_log = self.cwd / f"{kind}.stdout.log"
        stderr_log = self.cwd / f"{kind}.stderr.log"
        startup_marker = self.cwd / "bot.startup.log" if kind == "bot" else None
        for path in (stdout_log, stderr_log):
            if path.exists():
                path.unlink()
        env = {"PYTHONUNBUFFERED": "1"}
        if startup_marker is not None:
            env["DM_BOT_STARTUP_MARKER_FILE"] = str(startup_marker)
        pid = launch_detached_process(
            executable=sys.executable,
            args=["-m", "dm_bot.main", "run-bot" if kind == "bot" else "run-api"],
            cwd=self.cwd,
            env=env,
            stdout_log=stdout_log,
            stderr_log=stderr_log,
        )
        if pid is None:
            return False
        deadline = time.time() + wait_seconds
        while time.time() < deadline:
            if kind == "api" and self._api_reachable():
                return True
            if kind == "bot" and startup_marker is not None and runtime_bootstrap_complete(startup_marker):
                time.sleep(5)
                return bool(self._find_processes("bot"))
            time.sleep(0.5)
        return False

    def _api_reachable(self) -> bool:
        try:
            response = httpx.get("http://127.0.0.1:8000/health", timeout=3.0)
            return response.status_code == 200
        except Exception:
            return False

    def _run_sync_only(self, *, wait_seconds: int = 30) -> int:
        marker_log = self.cwd / "bot.sync.log"
        if marker_log.exists():
            marker_log.unlink()
        env = {
            "PYTHONUNBUFFERED": "1",
            "DM_BOT_STARTUP_MARKER_FILE": str(marker_log),
            "DM_BOT_SYNC_ONLY": "1",
        }
        process = subprocess.Popen(
            [sys.executable, "-m", "dm_bot.main", "run-bot"],
            cwd=str(self.cwd),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS if os.name == "nt" else 0,
        )
        deadline = time.time() + wait_seconds
        while time.time() < deadline:
            if marker_log.exists() and "SYNC_DONE" in marker_log.read_text(encoding="utf-8", errors="ignore"):
                process.terminate()
                return 0
            if process.poll() is not None:
                return 1
            time.sleep(0.5)
        if process.poll() is None:
            process.terminate()
        return 1

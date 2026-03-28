from pathlib import Path

from dm_bot.runtime.control_service import (
    ControlActionResult,
    ModelStatus,
    ProcessStatus,
    RuntimeControlService,
)


class FakeControlService(RuntimeControlService):
    def __init__(self) -> None:
        super().__init__(cwd=Path.cwd())
        self.calls: list[str] = []

    def get_state(self):  # type: ignore[override]
        return super().get_state()

    def _get_process_status(self, kind: str) -> ProcessStatus:  # type: ignore[override]
        self.calls.append(f"status:{kind}")
        return ProcessStatus(
            kind=kind,
            running=(kind == "bot"),
            pid=123 if kind == "bot" else None,
            healthy=(kind == "bot"),
        )

    def _get_model_status(self) -> ModelStatus:  # type: ignore[override]
        self.calls.append("status:models")
        return ModelStatus(
            router_model="qwen3:1.7b",
            router_available=True,
            narrator_model="qwen3:4b-instruct-2507-q4_K_M",
            narrator_available=True,
            last_checked_at="2026-03-28T12:00:00",
        )

    def _get_last_smoke_check(self):  # type: ignore[override]
        self.calls.append("status:smoke")
        return {"passed": True, "summary": "ok", "last_run_at": "2026-03-28T12:00:00"}

    def _read_log_tail(self, *_args, **_kwargs):  # type: ignore[override]
        return ["ok"]


def test_runtime_control_service_aggregates_state() -> None:
    service = FakeControlService()

    state = service.get_state()

    assert state.bot.kind == "bot"
    assert state.bot.running is True
    assert state.api.kind == "api"
    assert state.models.router_available is True
    assert state.smoke_check.passed is True
    assert state.overall_health in {"healthy", "degraded"}


def test_control_action_result_carries_snapshot() -> None:
    snapshot = FakeControlService().get_state()

    result = ControlActionResult(
        ok=True,
        action="restart-system",
        summary="done",
        details="all good",
        state_snapshot=snapshot,
    )

    assert result.ok is True
    assert result.action == "restart-system"
    assert result.state_snapshot.bot.kind == "bot"


def test_restart_system_wraps_existing_restart(monkeypatch) -> None:
    service = RuntimeControlService(cwd=Path.cwd())

    monkeypatch.setattr("dm_bot.runtime.control_service.run_restart_system", lambda *, cwd: 0)
    monkeypatch.setattr(service, "get_state", lambda: FakeControlService().get_state())

    result = service.restart_system()

    assert result.ok is True
    assert result.action == "restart-system"


def test_smoke_check_writes_status(monkeypatch, tmp_path: Path) -> None:
    service = RuntimeControlService(cwd=tmp_path)

    monkeypatch.setattr("dm_bot.runtime.control_service.run_local_smoke_check", lambda *, cwd: 0)
    monkeypatch.setattr(service, "get_state", lambda: FakeControlService().get_state())

    result = service.run_smoke_check()

    assert result.ok is True
    assert (tmp_path / "bot.smoke.status.json").exists()

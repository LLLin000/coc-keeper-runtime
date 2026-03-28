from fastapi.testclient import TestClient

from dm_bot.runtime.app import create_app
from dm_bot.runtime.health import build_health_snapshot
from dm_bot.runtime.control_service import (
    ControlActionResult,
    ControlLogs,
    ModelStatus,
    ProcessStatus,
    RuntimeControlState,
    SmokeCheckStatus,
)


class StubControlService:
    def get_state(self) -> RuntimeControlState:
        return RuntimeControlState(
            bot=ProcessStatus(kind="bot", running=True, pid=111, healthy=True),
            api=ProcessStatus(kind="api", running=False, healthy=False),
            models=ModelStatus(
                router_model="qwen3:1.7b",
                router_available=True,
                narrator_model="qwen3:4b-instruct-2507-q4_K_M",
                narrator_available=True,
            ),
            smoke_check=SmokeCheckStatus(passed=True, summary="ok"),
            logs=ControlLogs(startup_tail=["READY test"], restart_tail=[], stdout_tail=[], stderr_tail=[]),
            overall_health="healthy",
        )

    def restart_system(self) -> ControlActionResult:
        return ControlActionResult(
            ok=True,
            action="restart-system",
            summary="done",
            state_snapshot=self.get_state(),
        )


def test_create_app_exposes_health_endpoint() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "checks" in body


def test_health_snapshot_reports_model_configuration() -> None:
    snapshot = build_health_snapshot()

    assert snapshot.status in {"ok", "degraded"}
    assert "router_model" in snapshot.checks
    assert "narrator_model" in snapshot.checks


def test_create_app_exposes_control_panel_state_and_actions() -> None:
    client = TestClient(create_app(control_service=StubControlService()))

    state = client.get("/control-panel/state")
    assert state.status_code == 200
    assert state.json()["bot"]["running"] is True

    restart = client.post("/control-panel/actions/restart-system")
    assert restart.status_code == 200
    assert restart.json()["ok"] is True
    assert restart.json()["action"] == "restart-system"

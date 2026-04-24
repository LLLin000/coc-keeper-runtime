from dm_bot.config import Settings
from dm_bot.main import describe_runtime, main


def test_describe_runtime_reports_discord_and_models() -> None:
    summary = describe_runtime(
        Settings(
            discord_token="token",
            discord_public_key="public",
            router_model="qwen3:1.7b",
            narrator_model="fluffy/l3-8b-stheno-v3.2:q4_K_M",
        )
    )

    assert "discord_token=configured" in summary
    assert "router_model=qwen3:1.7b" in summary
    assert "narrator_model=fluffy/l3-8b-stheno-v3.2:q4_K_M" in summary


def test_main_dispatches_restart_system(monkeypatch) -> None:
    called = {}

    def fake_restart_system(*, cwd):
        called["cwd"] = cwd
        return 0

    monkeypatch.setattr("dm_bot.main.run_restart_system", fake_restart_system)

    result = main(["restart-system"])

    assert result == 0
    assert "cwd" in called


def test_main_dispatches_control_status(monkeypatch) -> None:
    called = {}

    def fake_control_status(*, cwd):
        called["cwd"] = cwd
        return 0

    monkeypatch.setattr("dm_bot.main.run_control_status", fake_control_status)

    result = main(["control-status"])

    assert result == 0
    assert "cwd" in called


def test_main_dispatches_run_control_panel(monkeypatch) -> None:
    called = {}

    def fake_run_control_panel():
        called["ran"] = True

    monkeypatch.setattr("dm_bot.main.run_control_panel", fake_run_control_panel)

    result = main(["run-control-panel"])

    assert result == 0
    assert called["ran"] is True

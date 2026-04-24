from dm_bot.config import Settings
from dm_bot.runtime.model_checks import build_model_snapshot


def test_settings_expose_discord_runtime_fields() -> None:
    settings = Settings(
        discord_token="token",
        discord_application_id="123",
        discord_public_key="public",
        discord_guild_id="456",
    )

    assert settings.discord_token == "token"
    assert settings.discord_application_id == "123"
    assert settings.discord_public_key == "public"
    assert settings.discord_guild_id == "456"


def test_model_snapshot_reports_missing_local_models(monkeypatch) -> None:
    monkeypatch.setattr(
        "dm_bot.runtime.model_checks.list_ollama_models",
        lambda settings: ["fluffy/l3-8b-stheno-v3.2:q4_K_M"],
    )
    settings = Settings(
        router_model="qwen3:1.7b",
        narrator_model="fluffy/l3-8b-stheno-v3.2:q4_K_M",
    )

    snapshot = build_model_snapshot(settings)

    assert snapshot.status == "degraded"
    assert snapshot.checks["router_model"].reachable is False
    assert snapshot.checks["narrator_model"].reachable is True

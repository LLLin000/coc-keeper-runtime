from dm_bot.config import Settings
from dm_bot.models.schemas import HealthSnapshot, ModelTarget, TurnEnvelope


def test_settings_define_runtime_model_fields() -> None:
    settings = Settings(
        discord_token="token",
        ollama_base_url="http://localhost:11434/v1",
        router_model="qwen3:1.7b",
        narrator_model="collective-v0.1-chinese-roleplay-8b",
    )

    assert settings.router_model == "qwen3:1.7b"
    assert settings.narrator_model == "collective-v0.1-chinese-roleplay-8b"


def test_turn_envelope_tracks_campaign_and_trace_ids() -> None:
    envelope = TurnEnvelope(
        campaign_id="campaign-1",
        channel_id="channel-1",
        user_id="user-1",
        trace_id="trace-1",
        content="ping",
    )

    assert envelope.campaign_id == "campaign-1"
    assert envelope.trace_id == "trace-1"


def test_health_snapshot_carries_model_target_checks() -> None:
    snapshot = HealthSnapshot(
        status="ok",
        checks={
            "router_model": ModelTarget(name="qwen3:1.7b", reachable=True),
            "narrator_model": ModelTarget(
                name="collective-v0.1-chinese-roleplay-8b",
                reachable=False,
            ),
        },
    )

    assert snapshot.checks["router_model"].reachable is True
    assert snapshot.checks["narrator_model"].reachable is False

from dm_bot.config import Settings
from dm_bot.main import describe_runtime


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

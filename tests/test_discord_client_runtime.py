from dm_bot.config import Settings
from dm_bot.discord_bot.client import create_discord_bot


def test_discord_bot_tracks_optional_sync_guild() -> None:
    bot = create_discord_bot(handlers=object(), settings=Settings(discord_guild_id="123"))

    assert bot.sync_guild_id == "123"

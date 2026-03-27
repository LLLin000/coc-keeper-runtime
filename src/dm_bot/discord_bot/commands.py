import json

from dm_bot.config import Settings, get_settings
from dm_bot.runtime.health import build_health_snapshot


class BotCommands:
    def __init__(self, *, settings: Settings | None, session_store, turn_coordinator, gameplay=None) -> None:
        self._settings = settings or get_settings()
        self._session_store = session_store
        self._turn_coordinator = turn_coordinator
        self._gameplay = gameplay

    async def setup_check(self, interaction) -> None:
        snapshot = build_health_snapshot(self._settings)
        await interaction.response.send_message(
            json.dumps(snapshot.model_dump(), ensure_ascii=False),
            ephemeral=True,
        )

    async def bind_campaign(self, interaction, *, campaign_id: str) -> None:
        self._session_store.bind_campaign(
            campaign_id=campaign_id,
            channel_id=str(interaction.channel_id),
            guild_id=str(interaction.guild_id),
            owner_id=str(interaction.user.id),
        )
        await interaction.response.send_message(
            f"campaign `{campaign_id}` bound to channel `{interaction.channel_id}`",
            ephemeral=True,
        )

    async def join_campaign(self, interaction) -> None:
        session = self._session_store.join_campaign(
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
        )
        await interaction.response.send_message(
            f"joined campaign `{session.campaign_id}`",
            ephemeral=True,
        )

    async def take_turn(self, interaction, *, content: str) -> None:
        session = self._session_store.get_by_channel(str(interaction.channel_id))
        if session is None:
            await interaction.response.send_message(
                "no campaign bound to this channel",
                ephemeral=True,
            )
            return

        await interaction.response.defer(thinking=True)
        result = await self._turn_coordinator.handle_turn(
            campaign_id=session.campaign_id,
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
            content=content,
        )
        await interaction.followup.send(result.reply)

    async def import_character(self, interaction, *, provider: str, external_id: str) -> None:
        if self._gameplay is None:
            await interaction.response.send_message(
                "character import is not configured",
                ephemeral=True,
            )
            return
        character = self._gameplay.import_character(
            user_id=str(interaction.user.id),
            provider=provider,
            external_id=external_id,
        )
        await interaction.response.send_message(
            f"imported `{character.name}` from `{character.source.provider}` ({character.source.label})",
            ephemeral=True,
        )

import json

from dm_bot.config import Settings, get_settings
from dm_bot.orchestrator.message_filters import MessageDisposition, classify_message
from dm_bot.runtime.health import build_health_snapshot


class BotCommands:
    def __init__(self, *, settings: Settings | None, session_store, turn_coordinator, gameplay=None, diagnostics=None) -> None:
        self._settings = settings or get_settings()
        self._session_store = session_store
        self._turn_coordinator = turn_coordinator
        self._gameplay = gameplay
        self._diagnostics = diagnostics

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

    async def leave_campaign(self, interaction) -> None:
        session = self._session_store.leave_campaign(
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
        )
        await interaction.response.send_message(
            f"left campaign `{session.campaign_id}`",
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
        blocked = self._combat_gate_message(channel_id=str(interaction.channel_id), user_id=str(interaction.user.id))
        if blocked:
            await interaction.followup.send(blocked, ephemeral=True)
            return
        result = await self._dispatch_turn(
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
        if self._session_store is not None:
            self._session_store.bind_character(
                channel_id=str(interaction.channel_id),
                user_id=str(interaction.user.id),
                character_name=character.name,
            )
        await interaction.response.send_message(
            f"imported `{character.name}` from `{character.source.provider}` ({character.source.label})",
            ephemeral=True,
        )

    async def enter_scene(self, interaction, *, speakers: str) -> None:
        if self._gameplay is None:
            await interaction.response.send_message("gameplay is not configured", ephemeral=True)
            return
        parsed = [item.strip() for item in speakers.split(",") if item.strip()]
        self._gameplay.enter_scene(speakers=parsed)
        await interaction.response.send_message(
            f"scene mode enabled for {', '.join(parsed)}",
            ephemeral=True,
        )

    async def end_scene(self, interaction) -> None:
        if self._gameplay is None:
            await interaction.response.send_message("gameplay is not configured", ephemeral=True)
            return
        self._gameplay.end_scene()
        await interaction.response.send_message("returned to DM mode", ephemeral=True)

    async def start_combat(self, interaction, *, combatants: str) -> None:
        if self._gameplay is None:
            await interaction.response.send_message("gameplay is not configured", ephemeral=True)
            return
        parsed = []
        from dm_bot.gameplay.combat import Combatant

        for raw in combatants.split(","):
            name, initiative, hit_points, armor_class = [part.strip() for part in raw.split(":")]
            parsed.append(
                Combatant(
                    name=name,
                    initiative=int(initiative),
                    hit_points=int(hit_points),
                    armor_class=int(armor_class),
                )
            )
        encounter = self._gameplay.start_combat(combatants=parsed)
        await interaction.response.send_message(
            f"combat started; active turn: {encounter.active_combatant.name}",
            ephemeral=True,
        )

    async def show_combat(self, interaction) -> None:
        if self._gameplay is None:
            await interaction.response.send_message("gameplay is not configured", ephemeral=True)
            return
        await interaction.response.send_message(self._gameplay.combat_summary(), ephemeral=True)

    async def next_turn(self, interaction) -> None:
        if self._gameplay is None:
            await interaction.response.send_message("gameplay is not configured", ephemeral=True)
            return
        encounter = self._gameplay.next_combat_turn()
        if encounter is None:
            await interaction.response.send_message("combat not active", ephemeral=True)
            return
        await interaction.response.send_message(
            f"当前轮到 {encounter.active_combatant.name}",
            ephemeral=True,
        )

    async def load_adventure(self, interaction, *, adventure_id: str) -> None:
        if self._gameplay is None:
            await interaction.response.send_message("gameplay is not configured", ephemeral=True)
            return
        from dm_bot.adventures.loader import load_adventure

        adventure = load_adventure(adventure_id)
        self._gameplay.load_adventure(adventure)
        await interaction.response.send_message(
            f"loaded adventure `{adventure.title}`",
            ephemeral=True,
        )

    async def debug_status(self, interaction, *, campaign_id: str) -> None:
        if self._diagnostics is None:
            await interaction.response.send_message("diagnostics are not configured", ephemeral=True)
            return
        await interaction.response.send_message(
            self._diagnostics.recent_summary(campaign_id),
            ephemeral=True,
        )

    async def handle_channel_message(
        self,
        *,
        channel_id: str,
        guild_id: str,
        user_id: str,
        content: str,
        mention_count: int,
    ) -> str | None:
        if self._session_store is None or self._turn_coordinator is None:
            return None
        session = self._session_store.get_by_channel(channel_id)
        if session is None or session.guild_id != guild_id or user_id not in session.member_ids:
            return None

        disposition = classify_message(content, mention_count=mention_count)
        if disposition != MessageDisposition.PROCESS:
            return None

        blocked = self._combat_gate_message(channel_id=channel_id, user_id=user_id)
        if blocked:
            return blocked

        result = await self._dispatch_turn(
            campaign_id=session.campaign_id,
            channel_id=channel_id,
            user_id=user_id,
            content=content,
        )
        return result.reply

    async def _dispatch_turn(self, *, campaign_id: str, channel_id: str, user_id: str, content: str):
        return await self._turn_coordinator.handle_turn(
            campaign_id=campaign_id,
            channel_id=channel_id,
            user_id=user_id,
            content=content,
        )

    def _combat_gate_message(self, *, channel_id: str, user_id: str) -> str | None:
        if self._gameplay is None or self._session_store is None:
            return None
        active_name = self._gameplay.active_combatant_name()
        if active_name is None:
            return None
        actor_name = self._session_store.active_character_for(channel_id=channel_id, user_id=user_id)
        if actor_name == active_name:
            return None
        return f"当前轮到 {active_name} 行动。"

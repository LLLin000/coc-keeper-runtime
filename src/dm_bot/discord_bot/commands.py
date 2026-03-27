import json
from collections.abc import Awaitable, Callable

from dm_bot.config import Settings, get_settings
from dm_bot.discord_bot.streaming import StreamingMessageTransport
from dm_bot.orchestrator.message_filters import MessageDisposition, classify_message
from dm_bot.runtime.health import build_health_snapshot


class BotCommands:
    def __init__(
        self,
        *,
        settings: Settings | None,
        session_store,
        turn_coordinator,
        gameplay=None,
        diagnostics=None,
        persistence_store=None,
    ) -> None:
        self._settings = settings or get_settings()
        self._session_store = session_store
        self._turn_coordinator = turn_coordinator
        self._gameplay = gameplay
        self._diagnostics = diagnostics
        self._persistence_store = persistence_store

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
        self._persist_sessions()
        await interaction.response.send_message(
            f"campaign `{campaign_id}` bound to channel `{interaction.channel_id}`",
            ephemeral=True,
        )

    async def join_campaign(self, interaction) -> None:
        session = self._session_store.join_campaign(
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
        )
        self._persist_sessions()
        await interaction.response.send_message(
            f"joined campaign `{session.campaign_id}`",
            ephemeral=True,
        )

    async def leave_campaign(self, interaction) -> None:
        session = self._session_store.leave_campaign(
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
        )
        self._persist_sessions()
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
        self._load_campaign_state(session.campaign_id)
        blocked = self._combat_gate_message(channel_id=str(interaction.channel_id), user_id=str(interaction.user.id))
        if blocked:
            await interaction.followup.send(blocked, ephemeral=True)
            return
        onboarding_block = self._gameplay.onboarding_block_message() if self._gameplay is not None else None
        if onboarding_block:
            await interaction.followup.send(onboarding_block, ephemeral=True)
            return
        adventure_response = self._evaluate_adventure_guidance(content=content)
        if adventure_response is not None:
            self._record_trigger_events(session.campaign_id, list(adventure_response.get("trigger_events", [])))
            self._save_campaign_state(session.campaign_id)
            await interaction.followup.send(str(adventure_response["message"]))
            return
        await self._stream_turn_to_transport(
            campaign_id=session.campaign_id,
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
            content=content,
            send_initial=lambda initial: interaction.followup.send(initial, wait=True),
            edit_message=lambda message, updated: message.edit(content=updated),
        )
        self._save_campaign_state(session.campaign_id)

    async def import_character(self, interaction, *, provider: str, external_id: str) -> None:
        if self._gameplay is None:
            await interaction.response.send_message(
                "character import is not configured",
                ephemeral=True,
            )
            return
        self._load_state_for_channel(str(interaction.channel_id))
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
            self._persist_sessions()
        await interaction.response.send_message(
            f"imported `{character.name}` from `{character.source.provider}` ({character.source.label})",
            ephemeral=True,
        )

    async def enter_scene(self, interaction, *, speakers: str) -> None:
        if self._gameplay is None:
            await interaction.response.send_message("gameplay is not configured", ephemeral=True)
            return
        self._load_state_for_channel(str(interaction.channel_id))
        parsed = [item.strip() for item in speakers.split(",") if item.strip()]
        self._gameplay.enter_scene(speakers=parsed)
        self._save_state_for_channel(str(interaction.channel_id))
        await interaction.response.send_message(
            f"scene mode enabled for {', '.join(parsed)}",
            ephemeral=True,
        )

    async def end_scene(self, interaction) -> None:
        if self._gameplay is None:
            await interaction.response.send_message("gameplay is not configured", ephemeral=True)
            return
        self._load_state_for_channel(str(interaction.channel_id))
        self._gameplay.end_scene()
        self._save_state_for_channel(str(interaction.channel_id))
        await interaction.response.send_message("returned to DM mode", ephemeral=True)

    async def start_combat(self, interaction, *, combatants: str) -> None:
        if self._gameplay is None:
            await interaction.response.send_message("gameplay is not configured", ephemeral=True)
            return
        self._load_state_for_channel(str(interaction.channel_id))
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
        self._save_state_for_channel(str(interaction.channel_id))
        await interaction.response.send_message(
            f"combat started; active turn: {encounter.active_combatant.name}",
            ephemeral=True,
        )

    async def show_combat(self, interaction) -> None:
        if self._gameplay is None:
            await interaction.response.send_message("gameplay is not configured", ephemeral=True)
            return
        self._load_state_for_channel(str(interaction.channel_id))
        await interaction.response.send_message(self._gameplay.combat_summary(), ephemeral=True)

    async def next_turn(self, interaction) -> None:
        if self._gameplay is None:
            await interaction.response.send_message("gameplay is not configured", ephemeral=True)
            return
        self._load_state_for_channel(str(interaction.channel_id))
        encounter = self._gameplay.next_combat_turn()
        if encounter is None:
            await interaction.response.send_message("combat not active", ephemeral=True)
            return
        self._save_state_for_channel(str(interaction.channel_id))
        await interaction.response.send_message(
            f"当前轮到 {encounter.active_combatant.name}",
            ephemeral=True,
        )

    async def load_adventure(self, interaction, *, adventure_id: str) -> None:
        if self._gameplay is None:
            await interaction.response.send_message("gameplay is not configured", ephemeral=True)
            return
        from dm_bot.adventures.loader import load_adventure

        self._load_state_for_channel(str(interaction.channel_id))
        adventure = load_adventure(adventure_id)
        self._gameplay.load_adventure(adventure)
        self._save_state_for_channel(str(interaction.channel_id))
        await interaction.response.send_message(
            f"loaded adventure `{adventure.title}`",
            ephemeral=True,
        )
        await interaction.channel.send(
            f"《{adventure.title}》已加载。已加入玩家请使用 `/ready` 完成就位；如未导入角色，可在 `/ready` 时填写角色名。"
        )

    async def ready_for_adventure(self, interaction, *, character_name: str = "") -> None:
        if self._gameplay is None or self._session_store is None:
            await interaction.response.send_message("gameplay is not configured", ephemeral=True)
            return
        self._load_state_for_channel(str(interaction.channel_id))
        session = self._session_store.get_by_channel(str(interaction.channel_id))
        if session is None:
            await interaction.response.send_message("no campaign bound to this channel", ephemeral=True)
            return
        if character_name.strip():
            self._session_store.bind_character(
                channel_id=str(interaction.channel_id),
                user_id=str(interaction.user.id),
                character_name=character_name.strip(),
            )
            self._persist_sessions()
        onboarding = self._gameplay.mark_adventure_ready(user_id=str(interaction.user.id))
        ready_ids = set(onboarding.get("ready_user_ids", []))
        await interaction.response.send_message(
            f"已就位 ({len(ready_ids)}/{len(session.member_ids)})",
            ephemeral=True,
        )
        if session.member_ids and ready_ids.issuperset(session.member_ids):
            self._gameplay.begin_adventure()
            self._save_state_for_channel(str(interaction.channel_id))
            await interaction.channel.send(
                self._gameplay.adventure_opening_text(active_characters=session.active_characters)
            )
        else:
            self._save_state_for_channel(str(interaction.channel_id))

    async def roll_expression(self, interaction, *, expression: str) -> None:
        result = self._safe_roll_for_channel(
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
            action="raw_roll",
            expression=expression,
        )
        await interaction.response.send_message(result, ephemeral=False)

    async def check_roll(self, interaction, *, label: str, modifier: int, advantage: str = "none") -> None:
        result = self._safe_roll_for_channel(
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
            action="ability_check",
            label=label,
            modifier=modifier,
            advantage=advantage,
        )
        await interaction.response.send_message(result, ephemeral=False)

    async def save_roll(self, interaction, *, label: str, modifier: int, advantage: str = "none") -> None:
        result = self._safe_roll_for_channel(
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
            action="saving_throw",
            label=label,
            modifier=modifier,
            advantage=advantage,
        )
        await interaction.response.send_message(result, ephemeral=False)

    async def attack_roll(
        self,
        interaction,
        *,
        target_name: str,
        target_ac: int,
        attack_bonus: int,
        damage_expression: str,
        weapon: str = "unarmed",
        advantage: str = "none",
    ) -> None:
        result = self._safe_roll_for_channel(
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
            action="attack_roll",
            target_name=target_name,
            target_ac=target_ac,
            attack_bonus=attack_bonus,
            damage_expression=damage_expression,
            weapon=weapon,
            advantage=advantage,
        )
        await interaction.response.send_message(result, ephemeral=False)

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

        self._load_campaign_state(session.campaign_id)
        onboarding_block = self._gameplay.onboarding_block_message() if self._gameplay is not None else None
        if onboarding_block:
            return onboarding_block

        inline_roll = self._try_inline_roll(
            channel_id=channel_id,
            user_id=user_id,
            content=content,
        )
        if inline_roll is not None:
            self._record_trigger_events(session.campaign_id, self._consume_gameplay_trigger_events())
            self._save_campaign_state(session.campaign_id)
            return inline_roll

        adventure_response = self._evaluate_adventure_guidance(content=content)
        if adventure_response is not None:
            self._record_trigger_events(session.campaign_id, list(adventure_response.get("trigger_events", [])))
            self._save_campaign_state(session.campaign_id)
            return str(adventure_response["message"])

        blocked = self._combat_gate_message(channel_id=channel_id, user_id=user_id)
        if blocked:
            return blocked

        result = await self._dispatch_turn(
            campaign_id=session.campaign_id,
            channel_id=channel_id,
            user_id=user_id,
            content=content,
        )
        self._save_campaign_state(session.campaign_id)
        return result.reply

    async def handle_channel_message_stream(
        self,
        *,
        message,
    ) -> None:
        channel_id = str(message.channel.id)
        guild_id = str(message.guild.id)
        user_id = str(message.author.id)
        content = message.content
        mention_count = len(message.mentions)
        if self._session_store is None or self._turn_coordinator is None:
            return
        session = self._session_store.get_by_channel(channel_id)
        if session is None or session.guild_id != guild_id or user_id not in session.member_ids:
            return

        disposition = classify_message(content, mention_count=mention_count)
        if disposition != MessageDisposition.PROCESS:
            return

        self._load_campaign_state(session.campaign_id)
        onboarding_block = self._gameplay.onboarding_block_message() if self._gameplay is not None else None
        if onboarding_block:
            await message.channel.send(onboarding_block)
            return

        inline_roll = self._try_inline_roll(channel_id=channel_id, user_id=user_id, content=content)
        if inline_roll is not None:
            self._record_trigger_events(session.campaign_id, self._consume_gameplay_trigger_events())
            self._save_campaign_state(session.campaign_id)
            await message.channel.send(inline_roll)
            return

        adventure_response = self._evaluate_adventure_guidance(content=content)
        if adventure_response is not None:
            self._record_trigger_events(session.campaign_id, list(adventure_response.get("trigger_events", [])))
            self._save_campaign_state(session.campaign_id)
            await message.channel.send(str(adventure_response["message"]))
            return

        blocked = self._combat_gate_message(channel_id=channel_id, user_id=user_id)
        if blocked:
            await message.channel.send(blocked)
            return

        await self._stream_turn_to_transport(
            campaign_id=session.campaign_id,
            channel_id=channel_id,
            user_id=user_id,
            content=content,
            send_initial=lambda initial: message.channel.send(initial),
            edit_message=lambda sent_message, updated: sent_message.edit(content=updated),
        )
        self._save_campaign_state(session.campaign_id)

    async def _dispatch_turn(self, *, campaign_id: str, channel_id: str, user_id: str, content: str):
        return await self._turn_coordinator.handle_turn(
            campaign_id=campaign_id,
            channel_id=channel_id,
            user_id=user_id,
            content=content,
        )

    async def _stream_turn_to_transport(
        self,
        *,
        campaign_id: str,
        channel_id: str,
        user_id: str,
        content: str,
        send_initial: Callable[[str], Awaitable[object]],
        edit_message: Callable[[object, str], Awaitable[None]],
    ) -> str:
        transport = StreamingMessageTransport(send_initial=send_initial, edit_message=edit_message)
        return await transport.stream(
            self._turn_coordinator.stream_turn(
                campaign_id=campaign_id,
                channel_id=channel_id,
                user_id=user_id,
                content=content,
            )
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

    def _persist_sessions(self) -> None:
        if self._persistence_store is None or self._session_store is None:
            return
        self._persistence_store.save_sessions(self._session_store.dump_sessions())

    def _save_state_for_channel(self, channel_id: str) -> None:
        if self._session_store is None:
            return
        session = self._session_store.get_by_channel(channel_id)
        if session is None:
            return
        self._save_campaign_state(session.campaign_id)

    def _save_campaign_state(self, campaign_id: str) -> None:
        if self._persistence_store is None or self._gameplay is None:
            return
        self._persistence_store.save_campaign_state(campaign_id, self._gameplay.export_state())

    def _load_campaign_state(self, campaign_id: str) -> None:
        if self._persistence_store is None or self._gameplay is None:
            return
        state = self._persistence_store.load_campaign_state(campaign_id)
        if state:
            self._gameplay.import_state(state)

    def _load_state_for_channel(self, channel_id: str) -> None:
        if self._session_store is None:
            return
        session = self._session_store.get_by_channel(channel_id)
        if session is None:
            return
        self._load_campaign_state(session.campaign_id)

    def _resolve_roll_for_channel(self, *, channel_id: str, user_id: str, action: str, **kwargs) -> str:
        if self._session_store is None or self._gameplay is None:
            return "gameplay is not configured"
        self._load_state_for_channel(channel_id)
        actor_name = self._session_store.active_character_for(channel_id=channel_id, user_id=user_id) or f"玩家{user_id}"
        result = self._gameplay.resolve_manual_roll(actor_name=actor_name, action=action, **kwargs)
        return self._format_roll_result(result)

    def _safe_roll_for_channel(self, *, channel_id: str, user_id: str, action: str, **kwargs) -> str:
        try:
            return self._resolve_roll_for_channel(channel_id=channel_id, user_id=user_id, action=action, **kwargs)
        except Exception as exc:
            return f"掷骰失败：{exc}"

    def _try_inline_roll(self, *, channel_id: str, user_id: str, content: str) -> str | None:
        stripped = content.strip()
        lowered = stripped.lower()
        try:
            if lowered.startswith("roll "):
                return self._resolve_roll_for_channel(channel_id=channel_id, user_id=user_id, action="raw_roll", expression=stripped[5:].strip())
            if lowered.startswith("check "):
                label, modifier, advantage = self._split_check_payload(stripped[6:].strip())
                return self._resolve_roll_for_channel(
                    channel_id=channel_id,
                    user_id=user_id,
                    action="ability_check",
                    label=label,
                    modifier=modifier,
                    advantage=advantage,
                )
            if lowered.startswith("save "):
                label, modifier, advantage = self._split_check_payload(stripped[5:].strip())
                return self._resolve_roll_for_channel(
                    channel_id=channel_id,
                    user_id=user_id,
                    action="saving_throw",
                    label=label,
                    modifier=modifier,
                    advantage=advantage,
                )
        except (ValueError, RuntimeError) as exc:
            return f"掷骰输入无效：{exc}"
        return None

    def _split_check_payload(self, payload: str) -> tuple[str, int, str]:
        parts = [part for part in payload.split(" ") if part]
        if len(parts) < 2:
            raise ValueError("expected `<label> <modifier> [advantage|disadvantage]`")
        label = parts[0]
        modifier = int(parts[1])
        advantage = parts[2] if len(parts) > 2 else "none"
        return label, modifier, advantage

    def _format_roll_result(self, result: dict[str, object]) -> str:
        action = str(result.get("action", "roll"))
        consequence = str(result.get("consequence_summary", "")).strip()
        if action == "attack_roll":
            hit_text = "命中" if result.get("hit") else "未命中"
            damage_text = f"，伤害 {result.get('damage')}" if result.get("hit") else ""
            base = f"{result['actor']} 攻击 {result['target']}：{result['roll']}，总计 {result['total']}，{hit_text}{damage_text}"
            return f"{base}\n{consequence}" if consequence else base
        if action in {"ability_check", "saving_throw"}:
            base = f"{result['actor']} 的 {result['label']}：{result['roll']}，总计 {result['total']}"
            return f"{base}\n{consequence}" if consequence else base
        if action == "damage_roll":
            base = f"{result['actor']} 的伤害掷骰：{result['roll']}，总计 {result['total']} {result['damage_type']}"
            return f"{base}\n{consequence}" if consequence else base
        base = f"{result['actor']} 掷骰：{result['roll']}，总计 {result['total']}"
        return f"{base}\n{consequence}" if consequence else base

    def _evaluate_adventure_guidance(self, *, content: str) -> dict[str, object] | None:
        if self._gameplay is None or self._gameplay.adventure is None:
            return None
        evaluation = self._gameplay.evaluate_scene_action(content)
        kind = str(evaluation.get("kind", "none"))
        if kind == "none":
            return None
        if kind == "roll_needed":
            roll = dict(evaluation.get("roll", {}))
            label = roll.get("label", "Check")
            return {
                "message": f"{evaluation['message']}\n建议下一步：`/check label:{label} modifier:0 advantage:none`",
                "trigger_events": list(evaluation.get("trigger_events", [])),
            }
        if kind in {"auto", "clarify", "hint"}:
            guidance = evaluation.get("guidance")
            if guidance:
                return {
                    "message": f"{evaluation['message']}\n{guidance}",
                    "trigger_events": list(evaluation.get("trigger_events", [])),
                }
            return {
                "message": str(evaluation["message"]),
                "trigger_events": list(evaluation.get("trigger_events", [])),
            }
        return None

    def _record_trigger_events(self, campaign_id: str, events: list[dict[str, object]]) -> None:
        if self._persistence_store is None:
            return
        for event in events:
            self._persistence_store.append_event(
                campaign_id=campaign_id,
                trace_id=f"trigger-{event.get('payload', {}).get('trigger_id', 'unknown')}",
                event_type=str(event.get("event_type", "trigger.event")),
                payload=dict(event.get("payload", {})),
            )

    def _consume_gameplay_trigger_events(self) -> list[dict[str, object]]:
        if self._gameplay is None:
            return []
        return self._gameplay.consume_trigger_events()

import json
import asyncio
from collections.abc import Awaitable, Callable

from dm_bot.config import Settings, get_settings
from dm_bot.discord_bot.channel_enforcer import ChannelEnforcer
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
        coc_assets=None,
        archive_repository=None,
        character_builder=None,
    ) -> None:
        self._settings = settings or get_settings()
        self._session_store = session_store
        self._turn_coordinator = turn_coordinator
        self._gameplay = gameplay
        self._diagnostics = diagnostics
        self._persistence_store = persistence_store
        self._coc_assets = coc_assets
        self._archive_repository = archive_repository
        self._character_builder = character_builder
        self._enforcer = ChannelEnforcer(session_store) if session_store else None

    def check_channel(self, command_name: str, interaction) -> tuple[bool, str | None]:
        if self._enforcer is None:
            return True, None
        guild_id = str(interaction.guild_id) if interaction.guild_id else ""
        channel_id = str(interaction.channel_id) if interaction.channel_id else ""
        return self._enforcer.check_command(command_name, guild_id, channel_id)

    async def setup_check(self, interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        # Build channel structure guidance
        guild_id = str(interaction.guild_id) if interaction.guild_id else None
        channel_guidance = self._build_channel_guidance(guild_id) if guild_id else ""

        snapshot = await asyncio.to_thread(build_health_snapshot, self._settings)
        health_info = json.dumps(snapshot.model_dump(), ensure_ascii=False)

        full_message = (
            f"**频道结构指引：**\n{channel_guidance}\n\n**运行状态：**\n{health_info}"
        )
        await interaction.followup.send(full_message, ephemeral=True)

    def _build_channel_guidance(self, guild_id: str) -> str:
        if self._session_store is None:
            return self._default_channel_guidance()

        lines = [
            "本 Bot 采用四频道职责分离设计：",
            "",
            "1. **#角色档案** - 档案管理命令",
            "   `/profiles`, `/profile_detail`, `/start_builder`, `/select_profile`",
            "",
            "2. **#游戏大厅** - 跑团主战场",
            "   `/bind_campaign`, `/join_campaign`, `/load_adventure`, `/ready`, `/turn`",
            "",
            "3. **#kp-trace** - KP 追踪与调试",
            "   `/debug_status`, `/show_combat`",
            "",
            "4. **#admin** - 管理员角色治理",
            "   `/admin_profiles`",
            "",
        ]

        # Show current bindings if available
        archive = self._session_store.archive_channel_for(guild_id)
        game = self._session_store.game_channel_for(guild_id)
        trace = self._session_store.trace_channel_for(guild_id)
        admin = self._session_store.admin_channel_for(guild_id)

        bindings = []
        if archive:
            bindings.append(f"角色档案: <#{archive}>")
        if game:
            bindings.append(f"游戏大厅: <#{game}>")
        if trace:
            bindings.append(f"KP-trace: <#{trace}>")
        if admin:
            bindings.append(f"管理员: <#{admin}>")

        if bindings:
            lines.extend(["**当前绑定：**"])
            lines.extend(bindings)
        else:
            lines.append("尚未绑定任何频道。使用上述命令在对应频道绑定。")

        lines.extend(
            [
                "",
                "绑定命令：",
                "`/bind_archive_channel` - 在角色档案频道执行",
                "`/bind_campaign` - 在游戏大厅执行",
                "`/bind_trace_channel` - 在 KP-trace 频道执行",
                "`/bind_admin_channel` - 在管理员频道执行",
            ]
        )

        return "\n".join(lines)

    def _default_channel_guidance(self) -> str:
        return """本 Bot 采用四频道职责分离设计：

1. **#角色档案** - 档案管理命令
   `/profiles`, `/profile_detail`, `/start_builder`, `/select_profile`

2. **#游戏大厅** - 跑团主战场
   `/bind_campaign`, `/join_campaign`, `/load_adventure`, `/ready`, `/turn`

3. **#kp-trace** - KP 追踪与调试
   `/debug_status`, `/show_combat`

4. **#admin** - 管理员角色治理
   `/admin_profiles`

绑定命令：
`/bind_archive_channel` - 在角色档案频道执行
`/bind_campaign` - 在游戏大厅执行
`/bind_trace_channel` - 在 KP-trace 频道执行
`/bind_admin_channel` - 在管理员频道执行"""

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

    async def bind_archive_channel(self, interaction) -> None:
        self._session_store.bind_archive_channel(
            guild_id=str(interaction.guild_id), channel_id=str(interaction.channel_id)
        )
        self._persist_sessions()
        await interaction.response.send_message(
            "当前频道已绑定为角色档案频道。", ephemeral=True
        )

    async def bind_trace_channel(self, interaction) -> None:
        self._session_store.bind_trace_channel(
            guild_id=str(interaction.guild_id), channel_id=str(interaction.channel_id)
        )
        self._persist_sessions()
        await interaction.response.send_message(
            "当前频道已绑定为 KP/trace 频道。", ephemeral=True
        )

    async def bind_admin_channel(self, interaction) -> None:
        self._session_store.bind_admin_channel(
            guild_id=str(interaction.guild_id), channel_id=str(interaction.channel_id)
        )
        self._persist_sessions()
        await interaction.response.send_message(
            "当前频道已绑定为管理员角色管理频道。", ephemeral=True
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

    async def set_role(self, interaction, *, role: str) -> None:
        if self._session_store is None or self._gameplay is None:
            await interaction.response.send_message(
                "gameplay is not configured", ephemeral=True
            )
            return
        self._session_store.bind_role(
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
            role=role,
        )
        self._persist_sessions()
        self._gameplay.ensure_investigator_panel(
            user_id=str(interaction.user.id),
            display_name=getattr(
                interaction.user, "display_name", f"玩家{interaction.user.id}"
            ),
            role=role,
        )
        await interaction.response.send_message(
            f"角色定位已设为 `{role}`", ephemeral=True
        )

    async def start_character_builder(
        self, interaction, *, visibility: str = "private"
    ) -> None:
        allowed, msg = self.check_channel("start_builder", interaction)
        if not allowed:
            await interaction.response.send_message(msg, ephemeral=True)
            return
        if self._character_builder is None:
            await interaction.response.send_message(
                "character builder is not configured", ephemeral=True
            )
            return
        prompt = self._character_builder.start(
            user_id=str(interaction.user.id), visibility=visibility
        )
        await interaction.response.send_message(
            prompt, ephemeral=visibility == "private"
        )

    async def builder_reply(self, interaction, *, answer: str) -> None:
        allowed, msg = self.check_channel("builder_reply", interaction)
        if not allowed:
            await interaction.response.send_message(msg, ephemeral=True)
            return
        if self._character_builder is None or self._archive_repository is None:
            await interaction.response.send_message(
                "character builder is not configured", ephemeral=True
            )
            return
        prompt, profile = await self._character_builder.answer(
            user_id=str(interaction.user.id), answer=answer
        )
        self._persist_archives()
        ephemeral = True
        if profile is None:
            await interaction.response.send_message(prompt, ephemeral=ephemeral)
            return
        await self._sync_selected_profile_projections(
            user_id=str(interaction.user.id), profile=profile
        )
        await interaction.response.send_message(
            f"{prompt}\nAI 只会补充职业细化、背景摘要和人物归档字段；不会静默覆盖你明确给出的年龄、职业、人生目标和弱点。\n"
            f"你现在可以在档案频道使用 `/profiles` 或在游戏大厅里 `/select_profile profile_id:{profile.profile_id}`。",
            ephemeral=ephemeral,
        )

    async def list_profiles(self, interaction) -> None:
        allowed, msg = self.check_channel("profiles", interaction)
        if not allowed:
            await interaction.response.send_message(msg, ephemeral=True)
            return
        if self._archive_repository is None:
            await interaction.response.send_message(
                "archive repository is not configured", ephemeral=True
            )
            return
        profiles = self._archive_repository.list_profiles(str(interaction.user.id))
        if not profiles:
            await interaction.response.send_message(
                "你还没有长期调查员档案。先用 `/start_builder` 建一张。", ephemeral=True
            )
            return
        lines = [item.summary_line() for item in profiles]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    async def profile_detail(self, interaction, *, profile_id: str) -> None:
        allowed, msg = self.check_channel("profile_detail", interaction)
        if not allowed:
            await interaction.response.send_message(msg, ephemeral=True)
            return
        if self._archive_repository is None:
            await interaction.response.send_message(
                "archive repository is not configured", ephemeral=True
            )
            return
        profile = self._archive_repository.get_profile(
            str(interaction.user.id), profile_id
        )
        await interaction.response.send_message(profile.detail_view(), ephemeral=True)

    async def select_profile(self, interaction, *, profile_id: str) -> None:
        if self._archive_repository is None:
            await interaction.response.send_message(
                "archive repository is not configured", ephemeral=True
            )
            return
        session = self._session_store.get_by_channel(str(interaction.channel_id))
        if session is None:
            await interaction.response.send_message(
                "no campaign bound to this channel", ephemeral=True
            )
            return
        profile = self._archive_repository.get_profile(
            str(interaction.user.id), profile_id
        )
        self._session_store.select_archive_profile(
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
            profile_id=profile.profile_id,
        )
        self._persist_sessions()
        await self._sync_profile_projection_for_channel(
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
            profile=profile,
        )
        await interaction.response.send_message(
            f"已为本团选择档案角色 `{profile.name}`。", ephemeral=True
        )

    async def archive_profile(self, interaction, *, profile_id: str) -> None:
        if self._archive_repository is None:
            await interaction.response.send_message(
                "archive repository is not configured", ephemeral=True
            )
            return
        profile = self._archive_repository.archive_profile(
            user_id=str(interaction.user.id), profile_id=profile_id
        )
        self._persist_archives()
        await self._sync_selected_profile_projections(
            user_id=str(interaction.user.id), profile=profile
        )
        await interaction.response.send_message(
            f"已归档 `{profile.name}`。", ephemeral=True
        )

    async def activate_profile(self, interaction, *, profile_id: str) -> None:
        if self._archive_repository is None:
            await interaction.response.send_message(
                "archive repository is not configured", ephemeral=True
            )
            return
        profile = self._archive_repository.replace_active_with(
            user_id=str(interaction.user.id), profile_id=profile_id
        )
        self._persist_archives()
        await self._sync_selected_profile_projections(
            user_id=str(interaction.user.id), profile=profile
        )
        await interaction.response.send_message(
            f"已将 `{profile.name}` 设为当前激活档案。", ephemeral=True
        )

    async def admin_profiles(self, interaction) -> None:
        allowed, msg = self.check_channel("admin_profiles", interaction)
        if not allowed:
            await interaction.response.send_message(msg, ephemeral=True)
            return
        if self._archive_repository is None:
            await interaction.response.send_message(
                "archive repository is not configured", ephemeral=True
            )
            return
        if not self._is_admin(interaction):
            await interaction.response.send_message(
                "你没有管理员权限。", ephemeral=True
            )
            return
        guidance = self._admin_channel_guidance(interaction)
        profiles = self._archive_repository.list_all_profiles()
        if not profiles:
            await interaction.response.send_message(
                guidance + "\n当前没有任何角色档案。", ephemeral=True
            )
            return
        lines = [guidance] if guidance else []
        lines.extend(f"{item.user_id} | {item.summary_line()}" for item in profiles)
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    async def take_turn(self, interaction, *, content: str) -> None:
        allowed, msg = self.check_channel("take_turn", interaction)
        if not allowed:
            await interaction.response.send_message(msg, ephemeral=True)
            return
        session = self._session_store.get_by_channel(str(interaction.channel_id))
        if session is None:
            await interaction.response.send_message(
                "no campaign bound to this channel",
                ephemeral=True,
            )
            return

        await interaction.response.defer(thinking=True)
        self._load_campaign_state(session.campaign_id)
        blocked = self._combat_gate_message(
            channel_id=str(interaction.channel_id), user_id=str(interaction.user.id)
        )
        if blocked:
            await interaction.followup.send(blocked, ephemeral=True)
            return
        onboarding_block = (
            self._gameplay.onboarding_block_message()
            if self._gameplay is not None
            else None
        )
        if onboarding_block:
            await interaction.followup.send(onboarding_block, ephemeral=True)
            return
        adventure_response = self._evaluate_adventure_guidance(content=content)
        if adventure_response is not None:
            self._record_trigger_events(
                session.campaign_id, list(adventure_response.get("trigger_events", []))
            )
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

    async def import_character(
        self, interaction, *, provider: str, external_id: str
    ) -> None:
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
            await interaction.response.send_message(
                "gameplay is not configured", ephemeral=True
            )
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
            await interaction.response.send_message(
                "gameplay is not configured", ephemeral=True
            )
            return
        self._load_state_for_channel(str(interaction.channel_id))
        self._gameplay.end_scene()
        self._save_state_for_channel(str(interaction.channel_id))
        await interaction.response.send_message("returned to DM mode", ephemeral=True)

    async def start_combat(self, interaction, *, combatants: str) -> None:
        if self._gameplay is None:
            await interaction.response.send_message(
                "gameplay is not configured", ephemeral=True
            )
            return
        self._load_state_for_channel(str(interaction.channel_id))
        parsed = []
        from dm_bot.gameplay.combat import Combatant

        for raw in combatants.split(","):
            name, initiative, hit_points, armor_class = [
                part.strip() for part in raw.split(":")
            ]
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
            await interaction.response.send_message(
                "gameplay is not configured", ephemeral=True
            )
            return
        self._load_state_for_channel(str(interaction.channel_id))
        await interaction.response.send_message(
            self._gameplay.combat_summary(), ephemeral=True
        )

    async def next_turn(self, interaction) -> None:
        if self._gameplay is None:
            await interaction.response.send_message(
                "gameplay is not configured", ephemeral=True
            )
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
        allowed, msg = self.check_channel("load_adventure", interaction)
        if not allowed:
            await interaction.response.send_message(msg, ephemeral=True)
            return
        if self._gameplay is None:
            await interaction.response.send_message(
                "gameplay is not configured", ephemeral=True
            )
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

    async def ready_for_adventure(
        self, interaction, *, character_name: str = ""
    ) -> None:
        allowed, msg = self.check_channel("ready", interaction)
        if not allowed:
            await interaction.response.send_message(msg, ephemeral=True)
            return
        if self._gameplay is None or self._session_store is None:
            await interaction.response.send_message(
                "gameplay is not configured", ephemeral=True
            )
            return
        self._load_state_for_channel(str(interaction.channel_id))
        session = self._session_store.get_by_channel(str(interaction.channel_id))
        if session is None:
            await interaction.response.send_message(
                "no campaign bound to this channel", ephemeral=True
            )
            return
        resolved_name = character_name.strip()
        if character_name.strip():
            self._session_store.bind_character(
                channel_id=str(interaction.channel_id),
                user_id=str(interaction.user.id),
                character_name=character_name.strip(),
            )
            self._persist_sessions()
        elif self._archive_repository is not None:
            selected_profile_id = self._session_store.selected_profile_for(
                channel_id=str(interaction.channel_id),
                user_id=str(interaction.user.id),
            )
            if selected_profile_id:
                profile = self._archive_repository.get_profile(
                    str(interaction.user.id), selected_profile_id
                )
                resolved_name = profile.name
                self._session_store.bind_character(
                    channel_id=str(interaction.channel_id),
                    user_id=str(interaction.user.id),
                    character_name=profile.name,
                )
                self._persist_sessions()
                if self._gameplay is not None:
                    role = (
                        self._session_store.active_role_for(
                            channel_id=str(interaction.channel_id),
                            user_id=str(interaction.user.id),
                        )
                        or "investigator"
                    )
                    panel = self._gameplay.sync_panel_from_archive_profile(
                        user_id=str(interaction.user.id),
                        profile=profile,
                        role=role,
                    )
        role = (
            self._session_store.active_role_for(
                channel_id=str(interaction.channel_id), user_id=str(interaction.user.id)
            )
            or "investigator"
        )
        self._gameplay.ensure_investigator_panel(
            user_id=str(interaction.user.id),
            display_name=resolved_name
            or getattr(interaction.user, "display_name", f"玩家{interaction.user.id}"),
            role=role,
        )
        seeded = self._gameplay.seed_role_knowledge(
            user_id=str(interaction.user.id), role=role
        )
        onboarding = self._gameplay.mark_adventure_ready(
            user_id=str(interaction.user.id)
        )
        ready_ids = set(onboarding.get("ready_user_ids", []))
        await interaction.response.send_message(
            f"已就位 ({len(ready_ids)}/{len(session.member_ids)})",
            ephemeral=True,
        )
        track = self._gameplay.onboarding_track_for_role(role)
        if track:
            private_lines = [f"【{track['title']}】", track["opening_text"]]
            if seeded:
                private_lines.append(
                    "私人导入："
                    + "；".join(
                        item.get("title", "") for item in seeded if item.get("title")
                    )
                )
            await interaction.followup.send("\n".join(private_lines), ephemeral=True)
        if session.member_ids and ready_ids.issuperset(session.member_ids):
            self._gameplay.begin_adventure()
            self._save_state_for_channel(str(interaction.channel_id))
            await interaction.channel.send(
                self._gameplay.adventure_opening_text(
                    active_characters=session.active_characters
                )
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

    async def check_roll(
        self, interaction, *, label: str, modifier: int, advantage: str = "none"
    ) -> None:
        result = self._safe_roll_for_channel(
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
            action="ability_check",
            label=label,
            modifier=modifier,
            advantage=advantage,
        )
        await interaction.response.send_message(result, ephemeral=False)

    async def save_roll(
        self, interaction, *, label: str, modifier: int, advantage: str = "none"
    ) -> None:
        result = self._safe_roll_for_channel(
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
            action="saving_throw",
            label=label,
            modifier=modifier,
            advantage=advantage,
        )
        await interaction.response.send_message(result, ephemeral=False)

    async def coc_check_roll(
        self,
        interaction,
        *,
        label: str,
        value: int,
        difficulty: str = "regular",
        bonus_dice: int = 0,
        penalty_dice: int = 0,
        pushed: bool = False,
    ) -> None:
        result = self._safe_roll_for_channel(
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
            action="coc_skill_check",
            label=label,
            value=value,
            difficulty=difficulty,
            bonus_dice=bonus_dice,
            penalty_dice=penalty_dice,
            pushed=pushed,
        )
        await interaction.response.send_message(result, ephemeral=False)

    async def san_roll(
        self,
        interaction,
        *,
        current_san: int,
        loss_on_success: str = "0",
        loss_on_failure: str = "1d6",
        bonus_dice: int = 0,
        penalty_dice: int = 0,
    ) -> None:
        result = self._safe_roll_for_channel(
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
            action="coc_sanity_check",
            current_san=current_san,
            loss_on_success=loss_on_success,
            loss_on_failure=loss_on_failure,
            bonus_dice=bonus_dice,
            penalty_dice=penalty_dice,
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
            await interaction.response.send_message(
                "diagnostics are not configured", ephemeral=True
            )
            return
        await interaction.response.send_message(
            self._diagnostics.recent_summary(campaign_id),
            ephemeral=True,
        )

    async def coc_assets_summary(self, interaction) -> None:
        if self._coc_assets is None:
            await interaction.response.send_message(
                "COC assets are not configured", ephemeral=True
            )
            return
        summary = self._coc_assets.summary()
        rulebooks = (
            ", ".join(item["name"] for item in summary.get("rulebooks", [])) or "none"
        )
        investigators = (
            ", ".join(item["name"] for item in summary.get("investigators", []))
            or "none"
        )
        refs = (
            ", ".join(item["title"] for item in summary.get("community_references", []))
            or "none"
        )
        await interaction.response.send_message(
            f"rulebooks: {rulebooks}\ninvestigators: {investigators}\nreferences: {refs}",
            ephemeral=True,
        )

    async def show_sheet(self, interaction) -> None:
        allowed, msg = self.check_channel("sheet", interaction)
        if not allowed:
            await interaction.response.send_message(msg, ephemeral=True)
            return
        if self._archive_repository is not None:
            active_profile = self._archive_repository.active_profile(
                str(interaction.user.id)
            )
            if active_profile is not None:
                await interaction.response.send_message(
                    active_profile.detail_view(), ephemeral=True
                )
                return
        if self._gameplay is None:
            await interaction.response.send_message(
                "gameplay is not configured", ephemeral=True
            )
            return
        snapshot = self._gameplay.investigator_panel_snapshot(str(interaction.user.id))
        knowledge_titles = [
            item.get("title", "")
            for item in snapshot.get("knowledge", [])
            if item.get("title")
        ]
        panel = self._gameplay.panels.get(str(interaction.user.id))
        if panel is None:
            panel = self._gameplay.ensure_investigator_panel(
                user_id=str(interaction.user.id),
                display_name=getattr(
                    interaction.user, "display_name", f"玩家{interaction.user.id}"
                ),
                role=self._session_store.active_role_for(
                    channel_id=str(interaction.channel_id),
                    user_id=str(interaction.user.id),
                )
                if self._session_store
                else "investigator",
            )
        await interaction.response.send_message(
            panel.summary(knowledge_titles=knowledge_titles), ephemeral=True
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
        builder_reply = await self._consume_archive_builder_message(
            channel_id=channel_id,
            guild_id=guild_id,
            user_id=user_id,
            content=content,
        )
        if builder_reply is not None:
            return builder_reply

        if self._session_store is None or self._turn_coordinator is None:
            return None
        session = self._session_store.get_by_channel(channel_id)
        if (
            session is None
            or session.guild_id != guild_id
            or user_id not in session.member_ids
        ):
            return None

        disposition = classify_message(content, mention_count=mention_count)
        if disposition != MessageDisposition.PROCESS:
            return None

        self._load_campaign_state(session.campaign_id)
        onboarding_block = (
            self._gameplay.onboarding_block_message()
            if self._gameplay is not None
            else None
        )
        if onboarding_block:
            return onboarding_block

        inline_roll = self._try_inline_roll(
            channel_id=channel_id,
            user_id=user_id,
            content=content,
        )
        if inline_roll is not None:
            self._record_trigger_events(
                session.campaign_id, self._consume_gameplay_trigger_events()
            )
            self._save_campaign_state(session.campaign_id)
            return inline_roll

        adventure_response = self._evaluate_adventure_guidance(content=content)
        if adventure_response is not None:
            self._record_trigger_events(
                session.campaign_id, list(adventure_response.get("trigger_events", []))
            )
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
        builder_reply = await self._consume_archive_builder_message(
            channel_id=channel_id,
            guild_id=guild_id,
            user_id=user_id,
            content=content,
        )
        if builder_reply is not None:
            await message.channel.send(builder_reply)
            return
        if self._session_store is None or self._turn_coordinator is None:
            return
        session = self._session_store.get_by_channel(channel_id)
        if (
            session is None
            or session.guild_id != guild_id
            or user_id not in session.member_ids
        ):
            return

        disposition = classify_message(content, mention_count=mention_count)
        if disposition != MessageDisposition.PROCESS:
            return

        self._load_campaign_state(session.campaign_id)
        onboarding_block = (
            self._gameplay.onboarding_block_message()
            if self._gameplay is not None
            else None
        )
        if onboarding_block:
            await message.channel.send(onboarding_block)
            return

        inline_roll = self._try_inline_roll(
            channel_id=channel_id, user_id=user_id, content=content
        )
        if inline_roll is not None:
            self._record_trigger_events(
                session.campaign_id, self._consume_gameplay_trigger_events()
            )
            self._save_campaign_state(session.campaign_id)
            await message.channel.send(inline_roll)
            return

        adventure_response = self._evaluate_adventure_guidance(content=content)
        if adventure_response is not None:
            self._record_trigger_events(
                session.campaign_id, list(adventure_response.get("trigger_events", []))
            )
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
            edit_message=lambda sent_message, updated: sent_message.edit(
                content=updated
            ),
        )
        self._save_campaign_state(session.campaign_id)

    async def _dispatch_turn(
        self, *, campaign_id: str, channel_id: str, user_id: str, content: str
    ):
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
        transport = StreamingMessageTransport(
            send_initial=send_initial, edit_message=edit_message
        )
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
        actor_name = self._session_store.active_character_for(
            channel_id=channel_id, user_id=user_id
        )
        if actor_name == active_name:
            return None
        return f"当前轮到 {active_name} 行动。"

    def _persist_sessions(self) -> None:
        if self._persistence_store is None or self._session_store is None:
            return
        self._persistence_store.save_sessions(self._session_store.dump_sessions())

    def _persist_archives(self) -> None:
        if self._persistence_store is None or self._archive_repository is None:
            return
        self._persistence_store.save_archive_profiles(
            self._archive_repository.export_state()
        )

    async def _sync_selected_profile_projections(
        self, *, user_id: str, profile
    ) -> None:
        if self._session_store is None:
            return
        for channel_id in self._session_store.channels_selecting_profile(
            user_id=user_id, profile_id=profile.profile_id
        ):
            await self._sync_profile_projection_for_channel(
                channel_id=channel_id, user_id=user_id, profile=profile
            )

    async def _sync_profile_projection_for_channel(
        self, *, channel_id: str, user_id: str, profile
    ) -> None:
        if self._session_store is None or self._gameplay is None:
            return
        session = self._session_store.get_by_channel(channel_id)
        if session is None:
            return
        self._load_campaign_state(session.campaign_id)
        role = (
            self._session_store.active_role_for(channel_id=channel_id, user_id=user_id)
            or "investigator"
        )
        self._session_store.bind_character(
            channel_id=channel_id, user_id=user_id, character_name=profile.name
        )
        self._persist_sessions()
        self._gameplay.sync_panel_from_archive_profile(
            user_id=user_id, profile=profile, role=role
        )
        self._save_campaign_state(session.campaign_id)

    def _is_admin(self, interaction) -> bool:
        guild_permissions = getattr(
            getattr(interaction, "user", None), "guild_permissions", None
        )
        if getattr(guild_permissions, "administrator", False):
            return True
        session = (
            self._session_store.get_by_channel(str(interaction.channel_id))
            if self._session_store is not None
            else None
        )
        return session is not None and session.owner_id == str(interaction.user.id)

    def _admin_channel_guidance(self, interaction) -> str:
        if self._session_store is None:
            return ""
        admin_channel = self._session_store.admin_channel_for(str(interaction.guild_id))
        if admin_channel and str(interaction.channel_id) != admin_channel:
            return f"建议在管理员频道 `<#{admin_channel}>` 使用这些命令。"
        return ""

    async def _consume_archive_builder_message(
        self,
        *,
        channel_id: str,
        guild_id: str,
        user_id: str,
        content: str,
    ) -> str | None:
        if (
            self._session_store is None
            or self._character_builder is None
            or self._archive_repository is None
        ):
            return None
        archive_channel = self._session_store.archive_channel_for(guild_id)
        if archive_channel != channel_id or not self._character_builder.has_session(
            user_id
        ):
            return None
        answer = content.strip()
        if not answer:
            return None
        prompt, profile = await self._character_builder.answer(
            user_id=user_id, answer=answer
        )
        self._persist_archives()
        if profile is None:
            return prompt
        return f"{prompt}\n你现在可以在档案频道使用 `/profiles` 或在游戏大厅里 `/select_profile profile_id:{profile.profile_id}`。"

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
        self._persistence_store.save_campaign_state(
            campaign_id, self._gameplay.export_state()
        )

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

    def _resolve_roll_for_channel(
        self, *, channel_id: str, user_id: str, action: str, **kwargs
    ) -> str:
        if self._session_store is None or self._gameplay is None:
            return "gameplay is not configured"
        self._load_state_for_channel(channel_id)
        actor_name = (
            self._session_store.active_character_for(
                channel_id=channel_id, user_id=user_id
            )
            or f"玩家{user_id}"
        )
        result = self._gameplay.resolve_manual_roll(
            actor_name=actor_name, action=action, **kwargs
        )
        return self._format_roll_result(result)

    def _safe_roll_for_channel(
        self, *, channel_id: str, user_id: str, action: str, **kwargs
    ) -> str:
        try:
            return self._resolve_roll_for_channel(
                channel_id=channel_id, user_id=user_id, action=action, **kwargs
            )
        except Exception as exc:
            return f"掷骰失败：{exc}"

    def _try_inline_roll(
        self, *, channel_id: str, user_id: str, content: str
    ) -> str | None:
        stripped = content.strip()
        lowered = stripped.lower()
        try:
            if lowered.startswith("roll "):
                return self._resolve_roll_for_channel(
                    channel_id=channel_id,
                    user_id=user_id,
                    action="raw_roll",
                    expression=stripped[5:].strip(),
                )
            if lowered.startswith("check "):
                label, modifier, advantage = self._split_check_payload(
                    stripped[6:].strip()
                )
                return self._resolve_roll_for_channel(
                    channel_id=channel_id,
                    user_id=user_id,
                    action="ability_check",
                    label=label,
                    modifier=modifier,
                    advantage=advantage,
                )
            if lowered.startswith("save "):
                label, modifier, advantage = self._split_check_payload(
                    stripped[5:].strip()
                )
                return self._resolve_roll_for_channel(
                    channel_id=channel_id,
                    user_id=user_id,
                    action="saving_throw",
                    label=label,
                    modifier=modifier,
                    advantage=advantage,
                )
            if lowered.startswith("coc "):
                label, value, difficulty = self._split_coc_payload(stripped[4:].strip())
                return self._resolve_roll_for_channel(
                    channel_id=channel_id,
                    user_id=user_id,
                    action="coc_skill_check",
                    label=label,
                    value=value,
                    difficulty=difficulty,
                )
            if lowered.startswith("san "):
                current_san = int(stripped[4:].strip())
                return self._resolve_roll_for_channel(
                    channel_id=channel_id,
                    user_id=user_id,
                    action="coc_sanity_check",
                    current_san=current_san,
                    loss_on_success="0",
                    loss_on_failure="1d6",
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

    def _split_coc_payload(self, payload: str) -> tuple[str, int, str]:
        parts = [part for part in payload.split(" ") if part]
        if len(parts) < 2:
            raise ValueError("expected `<label> <value> [regular|hard|extreme]`")
        label = parts[0]
        value = int(parts[1])
        difficulty = parts[2] if len(parts) > 2 else "regular"
        return label, value, difficulty

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
        if action == "coc_skill_check":
            rank = result.get("success_rank", "failure")
            outcome = "成功" if result.get("success") else "失败"
            pushed = "，推动检定" if result.get("pushed") else ""
            base = (
                f"{result['actor']} 的 {result['label']}：{result['roll']}，"
                f"目标值 {result['value']}，难度 {result['difficulty']}，结果 {rank} {outcome}{pushed}"
            )
            return f"{base}\n{consequence}" if consequence else base
        if action == "coc_sanity_check":
            outcome = "成功" if result.get("success") else "失败"
            base = (
                f"{result['actor']} 的理智检定：{result['roll']}，"
                f"当前 SAN {result['current_san']}，结果 {outcome}，理智损失 {result['san_loss']}"
            )
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

    def _record_trigger_events(
        self, campaign_id: str, events: list[dict[str, object]]
    ) -> None:
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

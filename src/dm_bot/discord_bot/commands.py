import json
import asyncio
from collections.abc import Awaitable, Callable
from uuid import uuid4

from dm_bot.config import Settings, get_settings
from dm_bot.discord_bot.channel_enforcer import ChannelEnforcer
from dm_bot.discord_bot.streaming import StreamingMessageTransport
from dm_bot.discord_bot.onboarding_views import OnboardingView
from dm_bot.discord_bot.feedback import DiscordFeedbackService
from dm_bot.orchestrator.message_filters import MessageDisposition, classify_message
from dm_bot.orchestrator.session_store import DuplicateMemberError, UnboundChannelError
from dm_bot.router.intent import (
    MessageIntent,
    IntentClassificationResult,
    should_buffer_intent,
    get_handling_decision,
)
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
        intent_classifier=None,
        message_buffer=None,
        intent_handler_registry=None,
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
        self._intent_classifier = intent_classifier
        self._message_buffer = message_buffer
        self._intent_handler_registry = intent_handler_registry
        self._feedback_service = DiscordFeedbackService()

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
            "本 Bot 采用六频道职责分离设计：",
            "",
            "1. **#角色档案** - 档案管理命令",
            "   建卡请用 `/start_builder`，访谈将在私信中进行",
            "   查看档案：`/profiles`（列表）, `/profile_detail`（详情）",
            "   管理档案：`/select_profile`, `/archive_profile`, `/activate_profile`",
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
            "5. **#玩家状态** - 玩家状态面板",
            "   `/status_overview`, `/status_me`",
            "",
            "6. **#kp-ops** - KP 运维面板",
            "   `/ops_status` (overview|detailed|routing)",
            "",
        ]

        archive = self._session_store.archive_channel_for(guild_id)
        game = self._session_store.game_channel_for(guild_id)
        trace = self._session_store.trace_channel_for(guild_id)
        admin = self._session_store.admin_channel_for(guild_id)
        player_status = self._session_store.player_status_channel_for(guild_id)
        ops = self._session_store.ops_channel_for(guild_id)

        bindings = []
        if archive:
            bindings.append(f"角色档案: <#{archive}>")
        if game:
            bindings.append(f"游戏大厅: <#{game}>")
        if trace:
            bindings.append(f"KP-trace: <#{trace}>")
        if admin:
            bindings.append(f"管理员: <#{admin}>")
        if player_status:
            bindings.append(f"玩家状态: <#{player_status}>")
        if ops:
            bindings.append(f"KP-ops: <#{ops}>")

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
                "`/bind_player_status_channel` - 在玩家状态频道执行",
                "`/bind_ops_channel` - 在 KP-ops 频道执行",
            ]
        )

        return "\n".join(lines)

    def _default_channel_guidance(self) -> str:
        return """本 Bot 采用六频道职责分离设计：

1. **#角色档案** - 档案管理命令
   建卡请用 `/start_builder`，访谈将在私信中进行
   查看档案：`/profiles`（列表）, `/profile_detail`（详情）
   管理档案：`/select_profile`, `/archive_profile`, `/activate_profile`

2. **#游戏大厅** - 跑团主战场
   `/bind_campaign`, `/join_campaign`, `/load_adventure`, `/ready`, `/turn`

3. **#kp-trace** - KP 追踪与调试
   `/debug_status`, `/show_combat`

4. **#admin** - 管理员角色治理
   `/admin_profiles`

5. **#玩家状态** - 玩家状态面板
   `/status_overview`, `/status_me`

6. **#kp-ops** - KP 运维面板
   `/ops_status` (overview|detailed|routing)

绑定命令：
`/bind_archive_channel` - 在角色档案频道执行
`/bind_campaign` - 在游戏大厅执行
`/bind_trace_channel` - 在 KP-trace 频道执行
`/bind_admin_channel` - 在管理员频道执行
`/bind_player_status_channel` - 在玩家状态频道执行
`/bind_ops_channel` - 在 KP-ops 频道执行"""

    async def bind_campaign(self, interaction, *, campaign_id: str) -> None:
        self._session_store.bind_campaign(
            campaign_id=campaign_id,
            channel_id=str(interaction.channel_id),
            guild_id=str(interaction.guild_id),
            owner_id=str(interaction.user.id),
        )
        self._persist_sessions()
        await interaction.response.send_message(
            f"战役 `{campaign_id}` 已绑定到频道 `{interaction.channel_id}`",
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

    async def bind_player_status_channel(self, interaction) -> None:
        self._session_store.bind_player_status_channel(
            guild_id=str(interaction.guild_id), channel_id=str(interaction.channel_id)
        )
        self._persist_sessions()
        await interaction.response.send_message(
            "当前频道已绑定为玩家状态频道。", ephemeral=True
        )

    async def bind_ops_channel(self, interaction) -> None:
        self._session_store.bind_ops_channel(
            guild_id=str(interaction.guild_id), channel_id=str(interaction.channel_id)
        )
        self._persist_sessions()
        await interaction.response.send_message(
            "当前频道已绑定为 KP 运维频道。", ephemeral=True
        )

    async def ops_status(self, interaction, *, mode: str = "overview") -> None:
        """Show KP ops status overview, detailed, or routing history."""
        if self._session_store is None:
            await interaction.response.send_message("会话系统尚未配置", ephemeral=True)
            return

        guild_id = str(interaction.guild_id) if interaction.guild_id else ""
        channel_id = str(interaction.channel_id) if interaction.channel_id else ""

        session = self._session_store.get_by_channel(channel_id)
        if session is None:
            await interaction.response.send_message(
                "当前频道没有绑定战役。请先使用 `/bind_campaign` 绑定战役。",
                ephemeral=True,
            )
            return

        self._load_campaign_state(session.campaign_id)

        snapshot = self._build_visibility_snapshot(session)
        from dm_bot.orchestrator.kp_ops_renderer import KPOpsRenderer

        renderer = KPOpsRenderer(active_characters=session.active_characters)

        if mode == "overview":
            output = renderer.render_overview(snapshot)
        elif mode == "detailed":
            output = renderer.render_detailed(snapshot)
        elif mode == "routing":
            output = renderer.render_routing_history(snapshot)
        else:
            output = renderer.render_overview(snapshot)

        await interaction.response.send_message(output, ephemeral=False)

    async def status_overview(self, interaction) -> None:
        """Show player status overview in the player status channel."""
        if self._session_store is None:
            await interaction.response.send_message("会话系统尚未配置", ephemeral=True)
            return

        guild_id = str(interaction.guild_id) if interaction.guild_id else ""
        channel_id = str(interaction.channel_id) if interaction.channel_id else ""

        session = self._session_store.get_by_channel(channel_id)
        if session is None:
            await interaction.response.send_message(
                "当前频道没有绑定战役。请先使用 `/bind_campaign` 绑定战役。",
                ephemeral=True,
            )
            return

        self._load_campaign_state(session.campaign_id)

        snapshot = self._build_visibility_snapshot(session)
        from dm_bot.orchestrator.player_status_renderer import PlayerStatusRenderer

        renderer = PlayerStatusRenderer(active_characters=session.active_characters)
        overview = renderer.render_overview(snapshot)

        await interaction.response.send_message(overview, ephemeral=False)

    async def status_me(self, interaction) -> None:
        """Show personal character status privately."""
        if self._session_store is None:
            await interaction.response.send_message("会话系统尚未配置", ephemeral=True)
            return

        channel_id = str(interaction.channel_id) if interaction.channel_id else ""
        user_id = str(interaction.user.id)

        session = self._session_store.get_by_channel(channel_id)
        if session is None:
            await interaction.response.send_message(
                "当前频道没有绑定战役。请先使用 `/bind_campaign` 绑定战役。",
                ephemeral=True,
            )
            return

        self._load_campaign_state(session.campaign_id)

        snapshot = self._build_visibility_snapshot(session)
        from dm_bot.orchestrator.player_status_renderer import PlayerStatusRenderer

        renderer = PlayerStatusRenderer(active_characters=session.active_characters)
        personal_detail = renderer.render_personal_detail(snapshot, user_id)

        await interaction.response.send_message(personal_detail, ephemeral=True)

    def _build_visibility_snapshot(self, session) -> "VisibilitySnapshot | None":
        """Build visibility snapshot from session and gameplay state."""
        if self._gameplay is None:
            return None

        from dm_bot.orchestrator.visibility import build_visibility_snapshot

        panels = {}
        for user_id in session.member_ids:
            panel = self._gameplay.panels.get(user_id)
            if panel:
                panels[user_id] = panel

        return build_visibility_snapshot(session, panels)

    async def join_campaign(self, interaction) -> None:
        allowed, msg = self.check_channel("join_campaign", interaction)
        if not allowed:
            await interaction.response.send_message(msg, ephemeral=True)
            return

        try:
            session = self._session_store.join_campaign(
                channel_id=str(interaction.channel_id),
                user_id=str(interaction.user.id),
            )
            self._persist_sessions()
            await interaction.response.send_message(
                f"已加入战役 `{session.campaign_id}`",
                ephemeral=True,
            )
        except UnboundChannelError:
            await interaction.response.send_message(
                "请先使用 /bind_campaign 绑定战役频道",
                ephemeral=True,
            )
        except DuplicateMemberError:
            await interaction.response.send_message(
                "你已经在战役中了，无需重复加入",
                ephemeral=True,
            )
        except KeyError:
            await interaction.response.send_message(
                "请先使用 /bind_campaign 绑定战役频道",
                ephemeral=True,
            )

    async def leave_campaign(self, interaction) -> None:
        session = self._session_store.leave_campaign(
            channel_id=str(interaction.channel_id),
            user_id=str(interaction.user.id),
        )
        self._persist_sessions()
        await interaction.response.send_message(
            f"已离开战役 `{session.campaign_id}`",
            ephemeral=True,
        )

    async def set_role(self, interaction, *, role: str) -> None:
        if self._session_store is None or self._gameplay is None:
            await interaction.response.send_message("游戏系统尚未配置", ephemeral=True)
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
            await interaction.response.send_message("建卡系统尚未配置", ephemeral=True)
            return
        prompt = self._character_builder.start(
            user_id=str(interaction.user.id), visibility=visibility
        )

        # Try to send first question to user's DM
        try:
            dm_channel = await interaction.user.create_dm()
            await dm_channel.send(
                f"{prompt}\n\n回答时直接在私信中回复即可，或在档案频道使用 `/builder_reply answer:你的回答`"
            )
            # Post indicator in archive channel
            await interaction.response.send_message(
                "🕯️ 建卡访谈已在私信中开始。完成建卡后档案将出现在这里。",
                ephemeral=False,
            )
        except Exception:
            # DM creation failed (user may have DMs disabled for the server)
            # Fall back to ephemeral in-channel
            await interaction.response.send_message(
                f"无法发送私信（你可能关闭了服务器私信）。建卡访谈将在当前频道以私密方式进行。\n\n{prompt}",
                ephemeral=True,
            )

    async def builder_reply(self, interaction, *, answer: str) -> None:
        allowed, msg = self.check_channel("builder_reply", interaction)
        if not allowed:
            await interaction.response.send_message(msg, ephemeral=True)
            return
        if self._character_builder is None or self._archive_repository is None:
            await interaction.response.send_message("建卡系统尚未配置", ephemeral=True)
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
            await interaction.response.send_message("档案系统尚未配置", ephemeral=True)
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
            await interaction.response.send_message("档案系统尚未配置", ephemeral=True)
            return
        profile = self._archive_repository.get_profile(
            str(interaction.user.id), profile_id
        )
        sections = profile.card_view()
        if not sections:
            await interaction.response.send_message("档案为空。", ephemeral=True)
            return
        # Send first section as initial response
        first_title, first_content = sections[0]
        await interaction.response.send_message(
            f"**{first_title}**\n{first_content}", ephemeral=True
        )
        # Send remaining sections as followups
        for title, content in sections[1:]:
            await interaction.followup.send(f"**{title}**\n{content}", ephemeral=True)

    async def select_profile(self, interaction, *, profile_id: str) -> None:
        if self._session_store is None:
            await interaction.response.send_message("会话系统尚未配置", ephemeral=True)
            return

        channel_id = str(interaction.channel_id)
        user_id = str(interaction.user.id)

        # Load profiles from archive repository for ownership check
        profiles = {}
        if self._archive_repository is not None:
            try:
                user_profiles = self._archive_repository.list_profiles(user_id=user_id)
                for p in user_profiles:
                    profiles[p.profile_id] = p
            except Exception:
                pass

        result = self._session_store.select_archive_profile(
            channel_id=channel_id,
            user_id=user_id,
            profile_id=profile_id,
            profiles=profiles if profiles else None,
        )

        if not result.success:
            await interaction.response.send_message(
                result.error_message, ephemeral=True
            )
            return

        self._persist_sessions()

        # Re-fetch profile object for projection sync (profiles dict was only for validation)
        profile = None
        if self._archive_repository is not None:
            try:
                profile = self._archive_repository.get_profile(user_id, profile_id)
            except Exception:
                pass

        if profile is not None:
            await self._sync_profile_projection_for_channel(
                channel_id=channel_id, user_id=user_id, profile=profile
            )

        await interaction.response.send_message(
            f"已选择档案 `{profile.name if profile else profile_id}`。使用 `/ready` 就位。",
            ephemeral=True,
        )

    async def archive_profile(self, interaction, *, profile_id: str) -> None:
        if self._archive_repository is None:
            await interaction.response.send_message("档案系统尚未配置", ephemeral=True)
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
            await interaction.response.send_message("档案系统尚未配置", ephemeral=True)
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
            await interaction.response.send_message("档案系统尚未配置", ephemeral=True)
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
                "当前频道没有绑定战役",
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
        from dm_bot.orchestrator.session_store import SessionPhase

        if session.session_phase == SessionPhase.ONBOARDING:
            user_id_str = str(interaction.user.id)
            if not session.is_onboarding_complete(user_id_str):
                await interaction.followup.send(
                    "📋 当前处于规则介绍阶段。请先完成 onboarding 后再行动。\n"
                    "使用 `/complete_onboarding` 确认已了解规则。",
                    ephemeral=True,
                )
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
                "角色导入系统尚未配置",
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
            f"已导入 `{character.name}`（来源：`{character.source.provider}`）（{character.source.label}）",
            ephemeral=True,
        )

    async def enter_scene(self, interaction, *, speakers: str) -> None:
        if self._gameplay is None:
            await interaction.response.send_message("游戏系统尚未配置", ephemeral=True)
            return
        self._load_state_for_channel(str(interaction.channel_id))
        parsed = [item.strip() for item in speakers.split(",") if item.strip()]
        self._gameplay.enter_scene(speakers=parsed)
        self._save_state_for_channel(str(interaction.channel_id))
        await interaction.response.send_message(
            f"场景模式已启用，发言者：{', '.join(parsed)}",
            ephemeral=True,
        )

    async def end_scene(self, interaction) -> None:
        if self._gameplay is None:
            await interaction.response.send_message("游戏系统尚未配置", ephemeral=True)
            return
        self._load_state_for_channel(str(interaction.channel_id))
        self._gameplay.end_scene()
        self._save_state_for_channel(str(interaction.channel_id))
        await interaction.response.send_message("已返回常规模式", ephemeral=True)

    async def start_combat(self, interaction, *, combatants: str) -> None:
        if self._gameplay is None:
            await interaction.response.send_message("游戏系统尚未配置", ephemeral=True)
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
            f"战斗开始；当前行动者：{encounter.active_combatant.name}",
            ephemeral=True,
        )

    async def show_combat(self, interaction) -> None:
        if self._gameplay is None:
            await interaction.response.send_message("游戏系统尚未配置", ephemeral=True)
            return
        self._load_state_for_channel(str(interaction.channel_id))
        await interaction.response.send_message(
            self._gameplay.combat_summary(), ephemeral=True
        )

    async def next_turn(self, interaction) -> None:
        if self._gameplay is None:
            await interaction.response.send_message("游戏系统尚未配置", ephemeral=True)
            return
        self._load_state_for_channel(str(interaction.channel_id))
        encounter = self._gameplay.next_combat_turn()
        if encounter is None:
            await interaction.response.send_message(
                "当前没有进行中的战斗", ephemeral=True
            )
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
            await interaction.response.send_message("游戏系统尚未配置", ephemeral=True)
            return
        from dm_bot.adventures.loader import load_adventure

        self._load_state_for_channel(str(interaction.channel_id))
        adventure = load_adventure(adventure_id)
        self._gameplay.load_adventure(adventure)
        self._save_state_for_channel(str(interaction.channel_id))
        await interaction.response.send_message(
            f"模组 `{adventure.title}` 已加载。",
            ephemeral=True,
        )
        await interaction.channel.send(
            f"《{adventure.title}》已加载。已加入玩家请使用 `/ready` 完成就位；如未导入角色，可在 `/ready` 时填写角色名。"
        )

    async def ready(self, interaction) -> None:
        if self._session_store is None:
            await interaction.response.send_message("会话系统尚未配置", ephemeral=True)
            return

        channel_id = str(interaction.channel_id)
        user_id = str(interaction.user.id)

        result = self._session_store.validate_ready(
            channel_id=channel_id, user_id=user_id
        )

        if not result.success:
            await interaction.response.send_message(
                result.error_message, ephemeral=True
            )
            return

        session = self._session_store.get_by_channel(channel_id)
        session.set_player_ready(user_id, True)
        self._persist_sessions()

        char_name = session.active_characters.get(user_id, "调查员")
        await interaction.response.send_message(
            f"**{char_name}** 已就位！", ephemeral=False
        )

    async def ready_for_adventure(
        self, interaction, *, character_name: str = ""
    ) -> None:
        allowed, msg = self.check_channel("ready", interaction)
        if not allowed:
            await interaction.response.send_message(msg, ephemeral=True)
            return
        if self._gameplay is None or self._session_store is None:
            await interaction.response.send_message("游戏系统尚未配置", ephemeral=True)
            return
        self._load_state_for_channel(str(interaction.channel_id))
        session = self._session_store.get_by_channel(str(interaction.channel_id))
        if session is None:
            await interaction.response.send_message(
                "当前频道没有绑定战役", ephemeral=True
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
        from dm_bot.orchestrator.session_store import SessionPhase

        user_id_str = str(interaction.user.id)
        session.set_player_ready(user_id_str, True)
        ready_count = sum(1 for r in session.player_ready.values() if r)
        total_members = len(session.member_ids) if session.member_ids else 1
        await interaction.response.send_message(
            f"已就位 ({ready_count}/{total_members})。等待管理员用 /start-session 启动游戏。",
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
        if session.member_ids and ready_count >= len(session.member_ids):
            session.transition_to(SessionPhase.AWAITING_ADMIN_START)
            await interaction.channel.send(
                f"所有玩家已就位！管理员可以使用 `/start-session` 开始游戏。"
            )
        self._save_campaign_state(session.campaign_id)
        self._persist_sessions()

    async def start_session(self, interaction) -> None:
        from dm_bot.orchestrator.session_store import SessionPhase
        from dm_bot.orchestrator.onboarding import get_default_coc7e_onboarding
        from dm_bot.orchestrator.onboarding_controller import OnboardingController
        from dm_bot.discord_bot.onboarding_views import OnboardingView

        allowed, msg = self.check_channel("start_session", interaction)
        if not allowed:
            await interaction.response.send_message(msg, ephemeral=True)
            return
        if self._gameplay is None or self._session_store is None:
            await interaction.response.send_message("游戏系统尚未配置", ephemeral=True)
            return
        session = self._session_store.get_by_channel(str(interaction.channel_id))
        if session is None:
            await interaction.response.send_message(
                "当前频道没有绑定战役", ephemeral=True
            )
            return
        if session.session_phase not in (
            SessionPhase.LOBBY,
            SessionPhase.AWAITING_ADMIN_START,
        ):
            await interaction.response.send_message(
                f"无法从当前阶段启动：{session.session_phase.value}。需要玩家先 /ready。",
                ephemeral=True,
            )
            return
        ready_count = sum(1 for r in session.player_ready.values() if r)
        if ready_count < len(session.member_ids):
            await interaction.response.send_message(
                f"无法启动：还有玩家未就位 ({ready_count}/{len(session.member_ids)})。",
                ephemeral=True,
            )
            return
        session.admin_started = True

        session.transition_to(SessionPhase.ONBOARDING)
        for member_id in session.member_ids:
            session.set_onboarding_complete(member_id, False)

        if self._gameplay:
            self._gameplay.begin_adventure()

        controller = OnboardingController(session=session, gameplay=self._gameplay)
        welcome_content = controller.get_welcome_embed_content()

        self._save_campaign_state(session.campaign_id)
        self._persist_sessions()

        await interaction.response.defer(thinking=True)

        await interaction.channel.send(
            "📋 **游戏准备开始！**\n\n"
            "在正式进入模组之前，我们需要完成规则概览。\n"
            "点击下方按钮查看 COC 7E 核心规则。",
        )

        view = OnboardingView(
            user_id="all",
            content=get_default_coc7e_onboarding(),
            timeout=None,
        )
        await interaction.followup.send(
            welcome_content,
            view=view,
            ephemeral=False,
        )

    async def complete_onboarding(self, interaction) -> None:
        from dm_bot.orchestrator.session_store import SessionPhase
        from dm_bot.orchestrator.onboarding_controller import OnboardingController

        allowed, msg = self.check_channel("start_session", interaction)
        if not allowed:
            await interaction.response.send_message(msg, ephemeral=True)
            return
        if self._session_store is None:
            await interaction.response.send_message("会话系统尚未配置", ephemeral=True)
            return

        session = self._session_store.get_by_channel(str(interaction.channel_id))
        if session is None:
            await interaction.response.send_message(
                "当前频道没有绑定战役", ephemeral=True
            )
            return

        if session.session_phase != SessionPhase.ONBOARDING:
            await interaction.response.send_message(
                f"当前不在 onboarding 阶段：{session.session_phase.value}",
                ephemeral=True,
            )
            return

        user_id_str = str(interaction.user.id)
        if user_id_str not in session.member_ids:
            await interaction.response.send_message(
                "你不在这个 campaign 中", ephemeral=True
            )
            return

        session.set_onboarding_complete(user_id_str, True)
        self._persist_sessions()

        pending = []
        for member_id in session.member_ids:
            if not session.is_onboarding_complete(member_id):
                pending.append(member_id)

        if not pending:
            session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
            self._persist_sessions()
            await interaction.response.send_message(
                "✅ 你已完成规则确认！\n\n🎮 **所有玩家已准备完毕，游戏开始！**",
                ephemeral=False,
            )
            if self._gameplay and session.active_characters:
                await interaction.channel.send(
                    self._gameplay.adventure_opening_text(
                        active_characters=session.active_characters
                    )
                )
        else:
            await interaction.response.send_message(
                f"✅ 你已完成规则确认！\n\n等待其他玩家完成确认：{len(pending)} 人",
                ephemeral=True,
            )

    async def resolve_round(self, interaction) -> None:
        from dm_bot.orchestrator.session_store import SessionPhase

        allowed, msg = self.check_channel("resolve_round", interaction)
        if not allowed:
            await interaction.response.send_message(msg, ephemeral=True)
            return
        if self._session_store is None or self._turn_coordinator is None:
            await interaction.response.send_message("会话系统尚未配置", ephemeral=True)
            return
        session = self._session_store.get_by_channel(str(interaction.channel_id))
        if session is None:
            await interaction.response.send_message(
                "当前频道没有绑定战役", ephemeral=True
            )
            return
        if session.session_phase != SessionPhase.SCENE_ROUND_OPEN:
            await interaction.response.send_message(
                f"当前不在行动收集阶段：{session.session_phase.value}",
                ephemeral=True,
            )
            return
        if not session.action_submitters:
            await interaction.response.send_message(
                "还没有玩家提交行动。请先等待玩家提交行动。",
                ephemeral=True,
            )
            return
        session.transition_to(SessionPhase.SCENE_ROUND_RESOLVING)
        self._persist_sessions()
        await interaction.response.defer(thinking=True)
        self._load_campaign_state(session.campaign_id)
        pending_actions_list = [
            f"**{session.active_characters.get(uid, uid)}**: {action}"
            for uid, action in session.pending_actions.items()
        ]
        actions_summary = (
            "\n".join(pending_actions_list) if pending_actions_list else "无"
        )
        await interaction.followup.send(
            "⚙️ **开始结算回合**\n\n请在行动描述后输入 `/next-round` 进入下一轮。"
        )
        await interaction.channel.send(f"📋 **本轮行动汇总**\n{actions_summary}")

    async def next_round(self, interaction) -> None:
        from dm_bot.orchestrator.session_store import SessionPhase

        allowed, msg = self.check_channel("next_round", interaction)
        if not allowed:
            await interaction.response.send_message(msg, ephemeral=True)
            return
        if self._session_store is None:
            await interaction.response.send_message("会话系统尚未配置", ephemeral=True)
            return
        session = self._session_store.get_by_channel(str(interaction.channel_id))
        if session is None:
            await interaction.response.send_message(
                "当前频道没有绑定战役", ephemeral=True
            )
            return
        if session.session_phase != SessionPhase.SCENE_ROUND_RESOLVING:
            await interaction.response.send_message(
                f"当前不在回合结算阶段：{session.session_phase.value}",
                ephemeral=True,
            )
            return
        session.clear_all_actions()
        session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
        self._persist_sessions()
        self._save_campaign_state(session.campaign_id)

        buffered_summary = self._format_buffered_summary(str(interaction.channel_id))
        released_messages = self._release_buffered_messages(str(interaction.channel_id))

        response = "🔄 **新回合开始**\n\n请各位玩家提交本轮行动！"
        if released_messages:
            response += f"\n\n📬 **{len(released_messages)} 条缓冲消息已释放**"
        await interaction.response.send_message(response)

        if buffered_summary:
            await interaction.channel.send(buffered_summary)

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
            await interaction.response.send_message("诊断系统尚未配置", ephemeral=True)
            return
        await interaction.response.send_message(
            self._diagnostics.recent_summary(campaign_id),
            ephemeral=True,
        )

    async def coc_assets_summary(self, interaction) -> None:
        if self._coc_assets is None:
            await interaction.response.send_message("COC 资源尚未配置", ephemeral=True)
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
            await interaction.response.send_message("游戏系统尚未配置", ephemeral=True)
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

        from dm_bot.orchestrator.session_store import SessionPhase

        session_phase = session.session_phase.value

        if session.session_phase == SessionPhase.ONBOARDING:
            if not session.is_onboarding_complete(user_id):
                return (
                    "📋 当前处于规则介绍阶段。请先完成 onboarding 后再行动。\n"
                    "使用 `/complete_onboarding` 确认已了解规则。"
                )

        classification = await self._classify_message_intent(
            campaign_id=session.campaign_id,
            channel_id=channel_id,
            user_id=user_id,
            content=content,
            session_phase=session_phase,
            is_admin=self._is_admin_user(user_id, session),
        )

        if classification and self._intent_handler_registry:
            handling_result = await self._intent_handler_registry.handle_message(
                user_id=user_id,
                content=content,
                classification=classification,
                session_phase=session_phase,
                is_admin=self._is_admin_user(user_id, session),
            )
            if handling_result.should_buffer:
                self._buffer_message(
                    channel_id, user_id, content, classification.intent, session_phase
                )
            if handling_result.feedback_message:
                await self._feedback_service.send_feedback(
                    channel_id=channel_id,
                    user_id=user_id,
                    message=handling_result.feedback_message,
                )
        elif classification and self._should_buffer_message(
            classification.intent, session_phase
        ):
            self._buffer_message(
                channel_id, user_id, content, classification.intent, session_phase
            )
            feedback = (
                self._intent_classifier.get_feedback_message(
                    classification.intent, session_phase
                )
                if self._intent_classifier
                else None
            )
            if feedback:
                await self._feedback_service.send_feedback(
                    channel_id=channel_id,
                    user_id=user_id,
                    message=feedback,
                )

        if session.session_phase == SessionPhase.SCENE_ROUND_OPEN:
            return await self._handle_round_action(
                session=session,
                channel_id=channel_id,
                user_id=user_id,
                content=content,
            )

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

        intent_value = (
            classification.intent if classification else MessageIntent.UNKNOWN
        )
        intent_reasoning = classification.reasoning if classification else ""

        result = await self._dispatch_turn(
            campaign_id=session.campaign_id,
            channel_id=channel_id,
            user_id=user_id,
            content=content,
            session_phase=session_phase,
            intent=intent_value,
            intent_reasoning=intent_reasoning,
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

        from dm_bot.orchestrator.session_store import SessionPhase

        session_phase = session.session_phase.value

        if session.session_phase == SessionPhase.ONBOARDING:
            if not session.is_onboarding_complete(user_id):
                await message.channel.send(
                    "📋 当前处于规则介绍阶段。请先完成 onboarding 后再行动。\n"
                    "使用 `/complete_onboarding` 确认已了解规则。"
                )
                return

        classification = await self._classify_message_intent(
            campaign_id=session.campaign_id,
            channel_id=channel_id,
            user_id=user_id,
            content=content,
            session_phase=session_phase,
            is_admin=self._is_admin_user(user_id, session),
        )

        if classification and self._should_buffer_message(
            classification.intent, session_phase
        ):
            self._buffer_message(
                channel_id, user_id, content, classification.intent, session_phase
            )
            feedback = (
                self._intent_classifier.get_feedback_message(
                    classification.intent, session_phase
                )
                if self._intent_classifier
                else None
            )
            await message.channel.send(
                feedback
                or f"_Your message has been buffered until the {session_phase} phase ends._"
            )
            return

        if session.session_phase == SessionPhase.SCENE_ROUND_OPEN:
            await self._handle_round_action_stream(
                session=session,
                message=message,
                user_id=user_id,
                content=content,
            )
            return

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

        intent_value = (
            classification.intent if classification else MessageIntent.UNKNOWN
        )
        intent_reasoning = classification.reasoning if classification else ""

        await self._stream_turn_to_transport(
            campaign_id=session.campaign_id,
            channel_id=channel_id,
            user_id=user_id,
            content=content,
            send_initial=lambda initial: message.channel.send(initial),
            edit_message=lambda sent_message, updated: sent_message.edit(
                content=updated
            ),
            session_phase=session_phase,
            intent=intent_value,
            intent_reasoning=intent_reasoning,
        )
        self._save_campaign_state(session.campaign_id)

    async def _dispatch_turn(
        self,
        *,
        campaign_id: str,
        channel_id: str,
        user_id: str,
        content: str,
        session_phase: str = "lobby",
        intent: MessageIntent = MessageIntent.UNKNOWN,
        intent_reasoning: str = "",
    ):
        return await self._turn_coordinator.handle_turn(
            campaign_id=campaign_id,
            channel_id=channel_id,
            user_id=user_id,
            content=content,
            session_phase=session_phase,
            intent=intent,
            intent_reasoning=intent_reasoning,
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
        session_phase: str = "lobby",
        intent: MessageIntent = MessageIntent.UNKNOWN,
        intent_reasoning: str = "",
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
                session_phase=session_phase,
                intent=intent,
                intent_reasoning=intent_reasoning,
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

    async def _handle_round_action(
        self,
        *,
        session,
        channel_id: str,
        user_id: str,
        content: str,
    ) -> str | None:
        if not content or not content.strip():
            return None
        session.set_player_action(user_id, content)
        self._persist_sessions()
        return self._build_round_status_message(session)

    async def _handle_round_action_stream(
        self,
        *,
        session,
        message,
        user_id: str,
        content: str,
    ) -> None:
        if not content or not content.strip():
            return
        session.set_player_action(user_id, content)
        self._persist_sessions()
        status_msg = self._build_round_status_message(session)
        await message.channel.send(status_msg)

    def _build_round_status_message(self, session) -> str:
        submitted_names = session.get_submitter_names()
        pending_names = session.get_pending_member_names()
        submitted_str = "，".join(submitted_names) if submitted_names else "无"
        pending_str = "，".join(pending_names) if pending_names else "无"
        if session.all_submitted():
            return (
                f"✅ **行动已全部提交！**\n"
                f"已提交: {submitted_str}\n"
                f"KP 可以使用 `/resolve-round` 进行结算。"
            )
        return f"📝 **行动收集中**\n已提交: {submitted_str} | 待提交: {pending_str}"

    def _persist_sessions(self) -> None:
        if self._persistence_store is None or self._session_store is None:
            return
        self._persistence_store.save_sessions(self._session_store.dump_sessions())

    async def _classify_message_intent(
        self,
        *,
        campaign_id: str,
        channel_id: str,
        user_id: str,
        content: str,
        session_phase: str,
        is_admin: bool = False,
    ) -> IntentClassificationResult | None:
        if self._intent_classifier is None:
            return None
        try:
            return await self._intent_classifier.classify_message(
                trace_id=str(uuid4()),
                campaign_id=campaign_id,
                channel_id=channel_id,
                user_id=user_id,
                content=content,
                session_phase=session_phase,
                is_admin=is_admin,
            )
        except Exception:
            return IntentClassificationResult(
                intent=MessageIntent.UNKNOWN,
                confidence=0.0,
                reasoning="classification failed, defaulting to unknown",
            )

    def _should_buffer_message(self, intent: MessageIntent, session_phase: str) -> bool:
        return should_buffer_intent(intent, session_phase)

    def _buffer_message(
        self,
        channel_id: str,
        user_id: str,
        content: str,
        intent: MessageIntent,
        session_phase: str,
    ) -> None:
        if self._message_buffer is None:
            return
        from dm_bot.router.intent import MessageIntentMetadata

        metadata = MessageIntentMetadata(
            intent=intent,
            classification_reasoning="auto-classified",
            handling_decision=get_handling_decision(intent, session_phase),
            was_buffered=True,
            phase_at_classification=session_phase,
        )
        self._message_buffer.buffer_message(
            channel_id=channel_id,
            user_id=user_id,
            content=content,
            intent=intent,
            metadata=metadata,
        )

    def _release_buffered_messages(self, channel_id: str) -> list:
        if self._message_buffer is None:
            return []
        return self._message_buffer.release_buffered_messages(channel_id)

    def _format_buffered_summary(self, channel_id: str) -> str | None:
        if self._message_buffer is None:
            return None
        return self._message_buffer.format_buffered_message_summary(channel_id)

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

    def _is_admin_user(self, user_id: str, session) -> bool:
        if session is None:
            return False
        return session.owner_id == user_id

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
        is_dm: bool = False,
    ) -> str | None:
        if (
            self._session_store is None
            or self._character_builder is None
            or self._archive_repository is None
        ):
            return None
        if not self._character_builder.has_session(user_id):
            return None
        # Accept messages from archive channel OR DM channel (when builder is DM-first)
        if not is_dm:
            archive_channel = self._session_store.archive_channel_for(guild_id)
            if archive_channel != channel_id:
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
            return "游戏系统尚未配置"
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

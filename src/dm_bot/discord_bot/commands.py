"""Simplified Discord slash commands for the COC bot."""

import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import discord
    from discord import app_commands

from dm_bot.character.builder import CharacterBuilder
from dm_bot.scene.action import Action
from dm_bot.scene.round import Round
from dm_bot.scene.state import SceneState
from dm_bot.surface.session_context import SessionContext
from dm_bot.surface.session_board import SessionBoard
from dm_bot.surface.scene_board import SceneBoard
from dm_bot.surface.blocker_board import BlockerBoard
from dm_bot.surface.consequence_board import ConsequenceBoard

if TYPE_CHECKING:
    from dm_bot.adventure.loader import AdventureLoader
    from dm_bot.adventure.models import Adventure
    from dm_bot.narrator.client import NarratorClient
    from dm_bot.store.db import Store


class BotCommands:
    """Discord bot command handlers."""

    def __init__(
        self,
        *,
        loader: "AdventureLoader",
        narrator: "NarratorClient",
        store: "Store",
        settings: Any = None,
    ) -> None:
        self.loader = loader
        self.narrator = narrator
        self.store = store
        self.builder = CharacterBuilder()
        self.session: SessionContext | None = None
        self.current_adventure: "Adventure | None" = None
        self.current_round: Round | None = None
        self.player_sheets: dict[str, dict] = {}
        self.player_locations: dict[str, str] = {}
        self.session_board = SessionBoard()
        self.scene_board = SceneBoard()
        self.blocker_board = BlockerBoard()
        self.consequence_board = ConsequenceBoard()

    def register(self, tree: Any) -> None:
        import discord
        from discord import app_commands

        tree.add_command(
            app_commands.Command(
                name="start",
                description="开始创建调查员角色",
                callback=self._cmd_start,
            )
        )
        tree.add_command(
            app_commands.Command(
                name="begin_module",
                description="开始一个模组",
                callback=self._cmd_begin_module,
            )
        )
        tree.add_command(
            app_commands.Command(
                name="action",
                description="执行私密行动",
                callback=self._cmd_action,
            )
        )
        tree.add_command(
            app_commands.Command(
                name="roll",
                description="手动骰子检定",
                callback=self._cmd_roll,
            )
        )
        tree.add_command(
            app_commands.Command(
                name="sheet",
                description="查看角色卡",
                callback=self._cmd_sheet,
            )
        )
        tree.add_command(
            app_commands.Command(
                name="end_round",
                description="强制结束本轮并结算",
                callback=self._cmd_end_round,
            )
        )
        tree.add_command(
            app_commands.Command(
                name="status",
                description="查看当前状态",
                callback=self._cmd_status,
            )
        )

    async def _cmd_start(self, interaction: Any) -> None:
        user_id = str(interaction.user.id)
        response = self.builder.begin_creation(user_id)
        await interaction.response.send_message(response, ephemeral=True)

    async def _cmd_begin_module(self, interaction: Any, module_name: str) -> None:
        self.current_adventure = self.loader.load_module(module_name)
        self.session = SessionContext(
            session_id=f"ses_{uuid.uuid4().hex[:8]}",
            module_name=module_name,
            store=self.store,
        )
        self.session.phase = "active"
        self.session.add_participant(str(interaction.user.id))
        self.current_round = Round(trigger_engine=self.session.trigger_engine)
        self.current_round.start_collection()
        await interaction.response.send_message(
            f"模组 **{module_name}** 开始！当前场景：{self.current_adventure.opening_scene_id}\n"
            "请描述你的行动。"
        )

    async def _cmd_action(self, interaction: Any, text: str) -> None:
        if not self.current_round or self.current_round.state != SceneState.COLLECTING:
            await interaction.response.send_message("当前不在行动收集阶段。", ephemeral=True)
            return
        user_id = str(interaction.user.id)
        action = Action(
            user_id=user_id,
            character_id=user_id,
            action_text=text,
            visibility="private",
            dex_value=self.player_sheets.get(user_id, {}).get("dexterity", 50),
        )
        self.current_round.submit_action(action)
        await interaction.response.send_message(f"私密行动已记录：{text}", ephemeral=True)

    async def _cmd_roll(self, interaction: Any, skill: str) -> None:
        await interaction.response.send_message(f"你进行了 {skill} 检定（占位实现）")

    async def _cmd_sheet(self, interaction: Any) -> None:
        user_id = str(interaction.user.id)
        sheet = self.builder.get_sheet(user_id)
        if not sheet:
            await interaction.response.send_message("你还没有创建角色。使用 /start 开始。", ephemeral=True)
            return
        msg = (
            f"**{sheet.name}** | {sheet.occupation}\n"
            f"HP: {sheet.hit_points} | MP: {sheet.magic_points} | SAN: {sheet.sanity}/{sheet.sanity_max}\n"
            f"STR:{sheet.strength} CON:{sheet.constitution} SIZ:{sheet.size} "
            f"DEX:{sheet.dexterity} APP:{sheet.appearance} INT:{sheet.intelligence} "
            f"POW:{sheet.power} EDU:{sheet.education} LUCK:{sheet.luck}"
        )
        await interaction.response.send_message(msg, ephemeral=True)

    async def _cmd_end_round(self, interaction: Any) -> None:
        if not self.current_round:
            await interaction.response.send_message("当前没有进行中的回合。")
            return
        await self._resolve_round(interaction)

    async def _cmd_status(self, interaction: Any) -> None:
        if not self.current_adventure or not self.session:
            await interaction.response.send_message("没有进行中的模组。")
            return

        parts = []
        parts.append(self.session_board.render(self.session.to_dict()))

        scene_id = getattr(self.current_adventure, "opening_scene_id", "")
        scene_name = ""
        scene = getattr(self.current_adventure, "get_scene", None)
        if scene and scene_id:
            s = scene(scene_id)
            if s:
                scene_name = getattr(s, 'name', scene_id)

        round_state = self.current_round.state.value if self.current_round else "N/A"
        action_count = len(self.current_round.actions) if self.current_round else 0

        blockers = []
        if self.session.store:
            blockers = [
                {"reason": b.reason, "scene_id": b.scene_id, "blocker_id": b.blocker_id}
                for b in self.session.store.list_unresolved_blockers()
            ]

        scene_output = self.scene_board.render({
            "scene_id": scene_id,
            "scene_name": scene_name,
            "round_state": round_state,
            "action_count": action_count,
            "waiting_for": [b["reason"] for b in blockers] if blockers else None,
        })
        parts.append(scene_output)

        if blockers:
            parts.append(self.blocker_board.render({"blockers": blockers}))

        response_text = "\n---\n".join(parts)
        await interaction.response.send_message(response_text)

    async def handle_message(self, interaction: Any, text: str) -> None:
        if not self.current_round or self.current_round.state != SceneState.COLLECTING:
            return
        user_id = str(interaction.user.id)
        action = Action(
            user_id=user_id,
            character_id=user_id,
            action_text=text,
            visibility="public",
            dex_value=self.player_sheets.get(user_id, {}).get("dexterity", 50),
        )
        self.current_round.submit_action(action)

    async def _resolve_round(self, interaction: Any) -> None:
        if not self.current_round:
            return
        ordered = self.current_round.resolve()
        summary_lines = []
        for action in ordered:
            status = "成功" if (action.result and action.result.success) else "失败"
            summary_lines.append(f"- {action.character_id}: {action.action_text} ({status})")
        summary = "\n".join(summary_lines)
        narrative = self.narrator.generate(f"场景叙事\n行动列表：\n{summary}")
        await interaction.channel.send(f"**本轮结算**\n{narrative}")
        private = self.current_round.get_private_results()
        for user_id, result_text in private.items():
            pass
        self.current_round = Round()
        self.current_round.start_collection()
        await interaction.channel.send("---\n下一轮开始。请描述你们的行动。")

"""Simplified Discord slash commands for the COC bot."""

from typing import TYPE_CHECKING

import discord
from discord import app_commands

from dm_bot.character.builder import CharacterBuilder
from dm_bot.scene.action import Action
from dm_bot.scene.round import Round
from dm_bot.scene.state import SceneState

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
        adventure_loader: "AdventureLoader",
        narrator: "NarratorClient",
        store: "Store",
    ) -> None:
        self.adventure_loader = adventure_loader
        self.narrator = narrator
        self.store = store
        self.builder = CharacterBuilder()

        # Session state (in-memory for now; persist via store later)
        self.current_adventure: "Adventure | None" = None
        self.current_round: Round | None = None
        self.player_sheets: dict[str, dict] = {}  # user_id -> sheet data
        self.player_locations: dict[str, str] = {}  # user_id -> scene_id

    def register(self, tree: app_commands.CommandTree) -> None:
        """Register all slash commands."""
        tree.add_command(self.start_cmd)
        tree.add_command(self.begin_module_cmd)
        tree.add_command(self.action_cmd)
        tree.add_command(self.roll_cmd)
        tree.add_command(self.sheet_cmd)
        tree.add_command(self.end_round_cmd)
        tree.add_command(self.status_cmd)

    @app_commands.command(name="start", description="开始创建调查员角色")
    async def start_cmd(self, interaction: discord.Interaction) -> None:
        user_id = str(interaction.user.id)
        response = self.builder.begin_creation(user_id)
        await interaction.response.send_message(response, ephemeral=True)

    @app_commands.command(name="begin_module", description="开始一个模组")
    @app_commands.describe(module_name="模组名称")
    async def begin_module_cmd(self, interaction: discord.Interaction, module_name: str) -> None:
        self.current_adventure = self.adventure_loader.load_module(module_name)
        # Start first round
        self.current_round = Round()
        self.current_round.start_collection()
        await interaction.response.send_message(
            f"模组 **{module_name}** 开始！当前场景：{self.current_adventure.opening_scene_id}\n"
            "请描述你的行动。"
        )

    @app_commands.command(name="action", description="执行私密行动")
    @app_commands.describe(text="行动描述")
    async def action_cmd(self, interaction: discord.Interaction, text: str) -> None:
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

    @app_commands.command(name="roll", description="手动骰子检定")
    @app_commands.describe(skill="技能名称")
    async def roll_cmd(self, interaction: discord.Interaction, skill: str) -> None:
        # Placeholder: actual dice logic in rules/
        await interaction.response.send_message(f"你进行了 {skill} 检定（占位实现）")

    @app_commands.command(name="sheet", description="查看角色卡")
    async def sheet_cmd(self, interaction: discord.Interaction) -> None:
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

    @app_commands.command(name="end_round", description="强制结束本轮并结算")
    async def end_round_cmd(self, interaction: discord.Interaction) -> None:
        if not self.current_round:
            await interaction.response.send_message("当前没有进行中的回合。")
            return
        await self._resolve_round(interaction)

    @app_commands.command(name="status", description="查看当前状态")
    async def status_cmd(self, interaction: discord.Interaction) -> None:
        if not self.current_adventure:
            await interaction.response.send_message("没有进行中的模组。")
            return
        state = self.current_round.state if self.current_round else "none"
        await interaction.response.send_message(
            f"当前模组：{self.current_adventure.name}\n"
            f"回合状态：{state}\n"
            f"已提交行动：{len(self.current_round.actions) if self.current_round else 0}"
        )

    async def handle_message(self, interaction: discord.Interaction, text: str) -> None:
        """处理大厅里的普通消息（公开行动）"""
        if not self.current_round or self.current_round.state != SceneState.COLLECTING:
            return  # Ignore if not collecting

        user_id = str(interaction.user.id)
        action = Action(
            user_id=user_id,
            character_id=user_id,
            action_text=text,
            visibility="public",
            dex_value=self.player_sheets.get(user_id, {}).get("dexterity", 50),
        )
        self.current_round.submit_action(action)

    async def _resolve_round(self, interaction: discord.Interaction) -> None:
        """结算当前回合"""
        if not self.current_round:
            return

        ordered = self.current_round.resolve()

        # Build summary
        summary_lines = []
        for action in ordered:
            status = "成功" if (action.result and action.result.success) else "失败"
            summary_lines.append(f"- {action.character_id}: {action.action_text} ({status})")
        summary = "\n".join(summary_lines)

        # Generate narrative
        narrative = self.narrator.generate(
            f"场景叙事\n行动列表：\n{summary}"
        )

        # Post to lobby
        await interaction.channel.send(f"**本轮结算**\n{narrative}")

        # Send private results
        private = self.current_round.get_private_results()
        for user_id, result_text in private.items():
            # DM the user (placeholder)
            pass

        # Start next round
        self.current_round = Round()
        self.current_round.start_collection()
        await interaction.channel.send("---\n下一轮开始。请描述你们的行动。")

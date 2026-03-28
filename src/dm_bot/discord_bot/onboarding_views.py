"""Interactive onboarding views for Discord."""

import json

import discord
from discord import ui

from dm_bot.orchestrator.onboarding import OnboardingContent


ONBOARDING_VIEW_CUSTOM_ID = "onboarding_view"


class OnboardingView(ui.View):
    def __init__(
        self,
        user_id: str,
        content: OnboardingContent,
        *,
        timeout: float | None = None,
    ):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.content = content
        self.current_section = -1
        self._build_buttons()

    def _build_buttons(self) -> None:
        self.clear_items()
        if self.current_section < 0:
            btn = ui.Button(
                label="开始",
                style=discord.ButtonStyle.primary,
                custom_id=f"{ONBOARDING_VIEW_CUSTOM_ID}:start:{self.user_id}",
            )
            btn.callback = self._handle_start
            self.add_item(btn)
            return

        if self.current_section < len(self.content.sections):
            section = self.content.sections[self.current_section]
            next_btn = ui.Button(
                label=section.button_label,
                style=discord.ButtonStyle.primary,
                custom_id=f"{ONBOARDING_VIEW_CUSTOM_ID}:next:{self.user_id}",
            )
            next_btn.callback = self._handle_next
            self.add_item(next_btn)

        if self.current_section == len(self.content.sections) - 1:
            confirm_btn = ui.Button(
                label=self.content.confirm_text,
                style=discord.ButtonStyle.success,
                custom_id=f"{ONBOARDING_VIEW_CUSTOM_ID}:confirm:{self.user_id}",
            )
            confirm_btn.callback = self._handle_confirm
            self.add_item(confirm_btn)

        if self.content.skip_available and self.current_section > 0:
            skip_btn = ui.Button(
                label="跳过",
                style=discord.ButtonStyle.secondary,
                custom_id=f"{ONBOARDING_VIEW_CUSTOM_ID}:skip:{self.user_id}",
            )
            skip_btn.callback = self._handle_skip
            self.add_item(skip_btn)

    async def _handle_start(self, interaction: discord.Interaction) -> None:
        self.current_section = 0
        self._build_buttons()
        await interaction.response.edit_message(
            content=self.content.sections[0].content, view=self
        )

    async def _handle_next(self, interaction: discord.Interaction) -> None:
        self.current_section += 1
        if self.current_section < len(self.content.sections):
            self._build_buttons()
            section = self.content.sections[self.current_section]
            await interaction.response.edit_message(content=section.content, view=self)
        else:
            self._build_buttons()
            await interaction.response.edit_message(
                content=self._build_confirm_message(), view=self
            )

    async def _handle_confirm(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(
            content="✅ 你已确认了解规则，游戏即将开始！",
            view=None,
        )
        self.stop()

    async def _handle_skip(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(
            content="✅ 已跳过规则介绍，游戏即将开始！",
            view=None,
        )
        self.stop()

    def _build_confirm_message(self) -> str:
        return (
            f"{self.content.sections[-1].content}\n\n"
            f"——\n\n"
            f"✅ **{self.content.confirm_text}**"
        )

    @classmethod
    def create_persistent(
        cls, user_id: str, content: OnboardingContent
    ) -> "OnboardingView":
        return cls(user_id=user_id, content=content, timeout=None)


def serialize_onboarding_state(
    user_id: str,
    section: int,
    completed: bool,
) -> str:
    return json.dumps(
        {
            "user_id": user_id,
            "section": section,
            "completed": completed,
        }
    )


def deserialize_onboarding_state(data: str) -> dict | None:
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return None

"""Channel enforcement for Discord command routing."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from dm_bot.orchestrator.session_store import SessionStore


class ChannelType(Enum):
    ARCHIVE = "archive"
    GAME = "game"
    ADMIN = "admin"
    TRACE = "trace"
    GENERAL = "general"


@dataclass
class ChannelPolicy:
    command_names: list[str]
    allowed_types: set[ChannelType]
    redirect_message: str


class ChannelEnforcer:
    def __init__(self, session_store: SessionStore) -> None:
        self._session_store = session_store
        self._policies: dict[str, ChannelPolicy] = {}
        self._register_default_policies()

    def _register_default_policies(self) -> None:
        archive_policy = ChannelPolicy(
            command_names=[
                "sheet",
                "profiles",
                "profile_detail",
                "start_builder",
                "builder_reply",
            ],
            allowed_types={ChannelType.ARCHIVE},
            redirect_message="此命令仅可在 #角色档案 频道使用",
        )
        self.register_policy(archive_policy)

        admin_policy = ChannelPolicy(
            command_names=["admin_profiles"],
            allowed_types={ChannelType.ADMIN},
            redirect_message="此命令仅可在 #管理员 频道使用",
        )
        self.register_policy(admin_policy)

        game_policy = ChannelPolicy(
            command_names=[
                "take_turn",
                "ready",
                "load_adventure",
                "enter_scene",
                "end_scene",
                "combat",
                "attack",
                "defend",
            ],
            allowed_types={ChannelType.GAME},
            redirect_message="此命令仅可在 #游戏大厅 频道使用",
        )
        self.register_policy(game_policy)

    def register_policy(self, policy: ChannelPolicy) -> None:
        for cmd_name in policy.command_names:
            self._policies[cmd_name] = policy

    def channel_type_for(self, guild_id: str, channel_id: str) -> ChannelType:
        if self._session_store.archive_channel_for(guild_id) == channel_id:
            return ChannelType.ARCHIVE
        if self._session_store.admin_channel_for(guild_id) == channel_id:
            return ChannelType.ADMIN
        if self._session_store.trace_channel_for(guild_id) == channel_id:
            return ChannelType.TRACE
        if self._session_store.game_channel_for(guild_id) == channel_id:
            return ChannelType.GAME
        return ChannelType.GENERAL

    def check_command(
        self, command_name: str, guild_id: str, channel_id: str
    ) -> tuple[bool, Optional[str]]:
        channel_type = self.channel_type_for(guild_id, channel_id)
        policy = self._policies.get(command_name)

        if policy is None:
            return True, None

        if not self._has_any_allowed_channel(guild_id, policy.allowed_types):
            return True, None

        if channel_type in policy.allowed_types:
            return True, None

        return False, policy.redirect_message

    def _has_any_allowed_channel(self, guild_id: str, allowed_types: set[ChannelType]) -> bool:
        if ChannelType.ARCHIVE in allowed_types and self._session_store.archive_channel_for(guild_id):
            return True
        if ChannelType.ADMIN in allowed_types and self._session_store.admin_channel_for(guild_id):
            return True
        if ChannelType.TRACE in allowed_types and self._session_store.trace_channel_for(guild_id):
            return True
        if ChannelType.GAME in allowed_types and self._session_store.game_channel_for(guild_id):
            return True
        if ChannelType.GENERAL in allowed_types:
            return True
        return False

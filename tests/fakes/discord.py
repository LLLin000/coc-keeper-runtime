"""Shared Discord fake utilities for tests."""

from __future__ import annotations
from typing import Any
from unittest.mock import AsyncMock, MagicMock


class FakeResponse:
    def __init__(self) -> None:
        self.messages: list[tuple[str, bool]] = []

        async def track_send(content: str, ephemeral: bool = False) -> None:
            self.messages.append((content, ephemeral))

        self.send_message = AsyncMock(side_effect=track_send)

        async def track_defer(ephemeral: bool = False) -> None:
            pass

        self.defer = AsyncMock(side_effect=track_defer)


class FakeFollowup:
    def __init__(self) -> None:
        self.messages: list[str] = []

        async def track_send(content: str, **kwargs) -> None:
            self.messages.append(content)

        self.send = AsyncMock(side_effect=track_send)


class FakeMessage:
    def __init__(self, content: str = "") -> None:
        self.content = content
        self.edit_called = False

    async def edit(self, *, content: str) -> None:
        self.content = content
        self.edit_called = True


class FakeStreamingTransport:
    def __init__(self) -> None:
        self.sent_messages: list[FakeMessage] = []

    async def send_initial(self, content: str) -> FakeMessage:
        msg = FakeMessage(content=content)
        self.sent_messages.append(msg)
        return msg

    async def edit_message(self, message: FakeMessage, content: str) -> None:
        await message.edit(content=content)


class FakeChannel:
    def __init__(self, channel_id: str = "chan-1") -> None:
        self.id = channel_id
        self.messages: list[str] = []

        async def track_send(content: str) -> None:
            self.messages.append(content)

        self.send = AsyncMock(side_effect=track_send)


def fake_user(user_id: str = "user-1", display_name: str = "TestUser") -> Any:
    return type("User", (), {"id": user_id, "display_name": display_name})()


def fake_channel(channel_id: str = "chan-1", name: str = "test-channel") -> Any:
    return type("Channel", (), {"id": channel_id, "name": name})()


def fake_guild(guild_id: str = "guild-1", name: str = "test-guild") -> Any:
    return type("Guild", (), {"id": guild_id, "name": name})()


def fake_interaction(
    *,
    user_id: str = "user-1",
    channel_id: str = "chan-1",
    guild_id: str = "guild-1",
    display_name: str = "TestUser",
    extras: dict | None = None,
) -> Any:
    interaction = MagicMock()
    interaction.user = fake_user(user_id, display_name)
    interaction.channel_id = channel_id
    interaction.guild_id = guild_id
    interaction.channel = FakeChannel(channel_id)
    interaction.response = FakeResponse()
    interaction.followup = FakeFollowup()
    interaction.extras = extras or {}
    return interaction


def fake_context(
    *,
    author_id: str = "user-1",
    author_name: str = "TestUser",
    channel_id: str = "chan-1",
    guild_id: str = "guild-1",
) -> Any:
    ctx = MagicMock()
    ctx.author = fake_user(author_id, author_name)
    ctx.channel = fake_channel(channel_id)
    ctx.guild = fake_guild(guild_id)
    ctx.send = AsyncMock()
    ctx.reply = AsyncMock()
    return ctx

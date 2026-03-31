"""Shared Discord fake utilities for tests."""

from __future__ import annotations
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import discord


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


class FakeDMChannel:
    """Fake DM channel for testing."""

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.messages: list[str] = []
        self.embeds: list[dict] = []

    async def send(self, content: str = None, embed: dict = None, **kwargs) -> None:
        """Record sent message."""
        if content:
            self.messages.append(content)
        if embed:
            self.embeds.append(embed)


class FakeUser:
    """Fake Discord user for testing with minimal interface."""

    def __init__(self, user_id: str, name: str = "TestUser") -> None:
        self.id = int(user_id)
        self.name = name
        self.discriminator = "0000"
        self._mock_dm_channel = FakeDMChannel(user_id)

    def __str__(self) -> str:
        return f"{self.name}#{self.discriminator}"

    @property
    def dm_channel(self) -> FakeDMChannel:
        return self._mock_dm_channel

    async def send(self, content: str = None, embed=None, **kwargs) -> None:
        """Send DM to this user."""
        await self._mock_dm_channel.send(content=content, embed=embed)


class FakeTextChannel(discord.TextChannel):
    """Fake text channel for testing that inherits from discord.TextChannel."""

    def __init__(self, channel_id: str, name: str = "test-channel") -> None:
        # Don't call discord.TextChannel.__init__ - just set our attributes
        self.id = int(channel_id)
        self.name = name
        self._mock_messages: list[str] = []
        self._mock_embeds: list = []  # Store actual discord.Embed objects

    async def send(self, content: str = None, embed=None, **kwargs) -> None:
        """Record sent message."""
        if content:
            self._mock_messages.append(content)
        if embed is not None:
            self._mock_embeds.append(embed)

    @property
    def messages(self) -> list[str]:
        return self._mock_messages

    @property
    def embeds(self) -> list:
        return self._mock_embeds


class FakeDiscordClient:
    """Fake Discord client for testing visibility dispatcher."""

    def __init__(self) -> None:
        self.users: dict[str, FakeUser] = {}
        self.channels: dict[str, FakeTextChannel] = {}
        self.sent_dms: list[dict] = []
        self.sent_channels: list[dict] = []

    def add_user(self, user_id: str, name: str = "TestUser") -> FakeUser:
        """Add a fake user."""
        user = FakeUser(user_id, name)
        self.users[user_id] = user
        return user

    def add_channel(
        self, channel_id: str, name: str = "test-channel"
    ) -> FakeTextChannel:
        """Add a fake channel."""
        channel = FakeTextChannel(channel_id, name)
        self.channels[channel_id] = channel
        return channel

    async def fetch_user(self, user_id: int) -> FakeUser | None:
        """Fetch a user by ID."""
        return self.users.get(str(user_id))

    async def fetch_channel(self, channel_id: int) -> FakeTextChannel | None:
        """Fetch a channel by ID."""
        return self.channels.get(str(channel_id))

    def get_user_dm_messages(self, user_id: str) -> list[str]:
        """Get all DM messages sent to a user."""
        user = self.users.get(user_id)
        if user:
            return user.dm_channel.messages
        return []

    def get_channel_messages(self, channel_id: str) -> list[str]:
        """Get all messages sent to a channel."""
        channel = self.channels.get(channel_id)
        if channel:
            return channel.messages
        return []

    def get_user_dm_embeds(self, user_id: str) -> list[dict]:
        """Get all DM embeds sent to a user."""
        user = self.users.get(user_id)
        if user:
            return user.dm_channel.embeds
        return []

    def get_channel_embeds(self, channel_id: str) -> list[dict]:
        """Get all embeds sent to a channel."""
        channel = self.channels.get(channel_id)
        if channel:
            return channel.embeds
        return []

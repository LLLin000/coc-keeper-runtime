from __future__ import annotations
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from dm_bot.orchestrator.session_store import SessionStore, ValidationResult


def _make_interaction(user_id="user-1", channel_id="chan-1", guild_id="g1"):
    interaction = MagicMock()
    interaction.user.id = user_id
    interaction.channel_id = channel_id
    interaction.guild_id = guild_id
    interaction.response = AsyncMock()
    interaction.followup = AsyncMock()
    return interaction


@pytest.mark.asyncio
async def test_select_profile_rejects_non_member():
    """Non-member gets ephemeral error."""
    from dm_bot.discord_bot.commands import BotCommands

    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="chan-1", guild_id="g1", owner_id="owner"
    )

    cmd = BotCommands(
        settings=None,
        session_store=store,
        turn_coordinator=MagicMock(),
        persistence_store=MagicMock(),
    )
    cmd._persist_sessions = MagicMock()

    interaction = _make_interaction(user_id="user-2", channel_id="chan-1")
    await cmd.select_profile(interaction, profile_id="prof-1")

    interaction.response.send_message.assert_called_once()
    call_kwargs = interaction.response.send_message.call_args
    assert call_kwargs.kwargs.get("ephemeral") is True
    assert "成员" in call_kwargs.args[0] or "member" in call_kwargs.args[0].lower()


@pytest.mark.asyncio
async def test_select_profile_success():
    """Member selecting own profile succeeds."""
    from dm_bot.discord_bot.commands import BotCommands

    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="chan-1", guild_id="g1", owner_id="user-1"
    )
    # user-1 is already a member (owner)

    cmd = BotCommands(
        settings=None,
        session_store=store,
        turn_coordinator=MagicMock(),
        persistence_store=MagicMock(),
    )
    cmd._persist_sessions = MagicMock()

    interaction = _make_interaction(user_id="user-1", channel_id="chan-1")
    await cmd.select_profile(interaction, profile_id="prof-1")

    interaction.response.send_message.assert_called_once()
    call_kwargs = interaction.response.send_message.call_args
    assert call_kwargs.kwargs.get("ephemeral") is True
    assert "prof-1" in call_kwargs.args[0]


@pytest.mark.asyncio
async def test_ready_rejects_no_profile():
    """Member without selected profile gets error."""
    from dm_bot.discord_bot.commands import BotCommands

    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="chan-1", guild_id="g1", owner_id="user-1"
    )

    cmd = BotCommands(
        settings=None,
        session_store=store,
        turn_coordinator=MagicMock(),
        persistence_store=MagicMock(),
    )

    interaction = _make_interaction(user_id="user-1", channel_id="chan-1")
    await cmd.ready(interaction)

    interaction.response.send_message.assert_called_once()
    call_kwargs = interaction.response.send_message.call_args
    assert call_kwargs.kwargs.get("ephemeral") is True


@pytest.mark.asyncio
async def test_ready_success():
    """Member with selected profile can ready up."""
    from dm_bot.discord_bot.commands import BotCommands

    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="chan-1", guild_id="g1", owner_id="user-1"
    )
    session = store.get_by_channel("chan-1")
    session.members["user-1"].selected_profile_id = "prof-1"
    session.selected_profiles["user-1"] = "prof-1"

    cmd = BotCommands(
        settings=None,
        session_store=store,
        turn_coordinator=MagicMock(),
        persistence_store=MagicMock(),
    )
    cmd._persist_sessions = MagicMock()

    interaction = _make_interaction(user_id="user-1", channel_id="chan-1")
    await cmd.ready(interaction)

    interaction.response.send_message.assert_called_once()
    call_kwargs = interaction.response.send_message.call_args
    assert call_kwargs.kwargs.get("ephemeral") is False
    assert "就位" in call_kwargs.args[0] or "ready" in call_kwargs.args[0].lower()

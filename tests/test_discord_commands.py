"""DISC-01 tests: Command handlers produce correct SessionStore state changes.

Tests /bind_campaign, /join_campaign, /select_profile, /ready, /load_adventure
handlers using FakeInteraction to verify session state transitions.

Phase 61 - Discord Command Layer Validation
"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest

from dm_bot.discord_bot.commands import BotCommands
from dm_bot.orchestrator.session_store import SessionStore
from tests.fakes.discord import fake_interaction, FakeFollowup


class FakeSentMessage:
    def __init__(self, content: str) -> None:
        self.content = content
        self.edits: list[str] = []

    async def edit(self, *, content: str) -> None:
        self.content = content
        self.edits.append(content)


class FakeChannel:
    def __init__(self) -> None:
        self.messages: list[str] = []
        self.sent_messages: list[FakeSentMessage] = []

    async def send(self, content: str) -> None:
        self.messages.append(content)
        sent = FakeSentMessage(content)
        self.sent_messages.append(sent)
        return sent


class FakeProfile:
    def __init__(
        self, profile_id: str, user_id: str, name: str = "Test Investigator"
    ) -> None:
        self.profile_id = profile_id
        self.user_id = user_id
        self.name = name
        self.status = "active"


def _fake_interaction_with_channel(
    *,
    channel_id: str = "chan-1",
    guild_id: str = "g1",
    user_id: str = "user-1",
):
    interaction = fake_interaction(
        channel_id=channel_id, guild_id=guild_id, user_id=user_id
    )
    interaction.channel = FakeChannel()
    return interaction


def _make_bot_commands(store: SessionStore) -> BotCommands:
    """Create BotCommands with mocked dependencies."""
    cmd = BotCommands(
        settings=None,
        session_store=store,
        turn_coordinator=MagicMock(),
        persistence_store=MagicMock(),
        gameplay=MagicMock(),
        archive_repository=MagicMock(),
    )
    cmd._persist_sessions = MagicMock()
    return cmd


# =============================================================================
# DISC-01: Command handler session state tests
# =============================================================================


@pytest.mark.asyncio
async def test_bind_campaign_creates_session_with_correct_fields():
    """bind_campaign creates CampaignSession with correct campaign_id, channel_id, guild_id, owner_id."""
    store = SessionStore()
    cmd = _make_bot_commands(store)

    interaction = _fake_interaction_with_channel(
        channel_id="chan-1", guild_id="g1", user_id="owner"
    )

    await cmd.bind_campaign(interaction, campaign_id="camp-1")

    session = store.get_by_channel("chan-1")
    assert session is not None
    assert session.campaign_id == "camp-1"
    assert session.channel_id == "chan-1"
    assert session.guild_id == "g1"
    assert session.owner_id == "owner"


@pytest.mark.asyncio
async def test_bind_campaign_adds_owner_to_member_ids():
    """bind_campaign adds owner to member_ids and members dict."""
    store = SessionStore()
    cmd = _make_bot_commands(store)

    interaction = _fake_interaction_with_channel(
        channel_id="chan-1", guild_id="g1", user_id="owner"
    )

    await cmd.bind_campaign(interaction, campaign_id="camp-1")

    session = store.get_by_channel("chan-1")
    assert "owner" in session.member_ids
    assert "owner" in session.members
    assert session.members["owner"].role.value == "owner"


@pytest.mark.asyncio
async def test_join_campaign_adds_member_to_session():
    """join_campaign adds user to member_ids when session exists."""
    store = SessionStore()
    cmd = _make_bot_commands(store)

    # Owner binds first
    owner_interaction = fake_interaction(
        channel_id="chan-1", guild_id="g1", user_id="owner"
    )
    await cmd.bind_campaign(owner_interaction, campaign_id="camp-1")

    # Guest joins
    guest_interaction = _fake_interaction_with_channel(
        channel_id="chan-1", guild_id="g1", user_id="guest"
    )
    await cmd.join_campaign(guest_interaction)

    session = store.get_by_channel("chan-1")
    assert "guest" in session.member_ids
    assert "guest" in session.members
    assert session.members["guest"].role.value == "member"


@pytest.mark.asyncio
async def test_join_campaign_rejects_unbound_channel():
    """join_campaign raises error when channel has no bound campaign."""
    store = SessionStore()
    cmd = _make_bot_commands(store)

    interaction = _fake_interaction_with_channel(
        channel_id="unbound-chan", guild_id="g1", user_id="user-x"
    )

    await cmd.join_campaign(interaction)

    interaction.response.send_message.assert_called_once()
    call_args = interaction.response.send_message.call_args
    assert "bind_campaign" in call_args.args[0].lower() or "绑定" in call_args.args[0]


@pytest.mark.asyncio
async def test_join_campaign_rejects_duplicate_member():
    """join_campaign raises error when user is already a member."""
    store = SessionStore()
    cmd = _make_bot_commands(store)

    # Owner binds
    owner_interaction = _fake_interaction_with_channel(
        channel_id="chan-1", guild_id="g1", user_id="owner"
    )
    await cmd.bind_campaign(owner_interaction, campaign_id="camp-1")

    # Owner tries to join again
    await cmd.join_campaign(owner_interaction)

    owner_interaction.response.send_message.assert_called()
    calls = owner_interaction.response.send_message.call_args_list
    last_call_args = calls[-1]
    assert (
        "已经" in last_call_args.args[0] or "already" in last_call_args.args[0].lower()
    )


@pytest.mark.asyncio
async def test_select_profile_updates_session_state():
    """select_profile updates session.selected_profiles and members[user_id].selected_profile_id."""
    store = SessionStore()
    cmd = _make_bot_commands(store)

    # Setup: bind campaign with owner as member
    interaction = _fake_interaction_with_channel(
        channel_id="chan-1", guild_id="g1", user_id="owner"
    )
    await cmd.bind_campaign(interaction, campaign_id="camp-1")

    # Mock archive_repository to return valid profile
    fake_profile = FakeProfile(
        profile_id="prof-1", user_id="owner", name="Test Investigator"
    )
    cmd._archive_repository.list_profiles = MagicMock(return_value=[fake_profile])
    cmd._archive_repository.get_profile = MagicMock(return_value=fake_profile)

    # Select profile
    select_interaction = _fake_interaction_with_channel(
        channel_id="chan-1", guild_id="g1", user_id="owner"
    )
    await cmd.select_profile(select_interaction, profile_id="prof-1")

    session = store.get_by_channel("chan-1")
    assert session.selected_profiles["owner"] == "prof-1"
    assert session.members["owner"].selected_profile_id == "prof-1"


@pytest.mark.asyncio
async def test_select_profile_rejects_non_member():
    """select_profile returns error for non-member user."""
    store = SessionStore()
    cmd = _make_bot_commands(store)

    # Bind campaign (owner will be member)
    owner_interaction = _fake_interaction_with_channel(
        channel_id="chan-1", guild_id="g1", user_id="owner"
    )
    await cmd.bind_campaign(owner_interaction, campaign_id="camp-1")

    # Non-member tries to select profile
    outsider_interaction = _fake_interaction_with_channel(
        channel_id="chan-1", guild_id="g1", user_id="outsider"
    )
    await cmd.select_profile(outsider_interaction, profile_id="prof-1")

    outsider_interaction.response.send_message.assert_called_once()
    call_args = outsider_interaction.response.send_message.call_args
    assert "成员" in call_args.args[0] or "member" in call_args.args[0].lower()


@pytest.mark.asyncio
async def test_ready_sets_player_ready_on_success():
    """ready sets player_ready[user_id] = True on success (PV-04 instance model)."""
    from dm_bot.orchestrator.session_store import CampaignCharacterInstance

    store = SessionStore()
    cmd = _make_bot_commands(store)

    # Setup: bind campaign with owner
    interaction = _fake_interaction_with_channel(
        channel_id="chan-1", guild_id="g1", user_id="owner"
    )
    await cmd.bind_campaign(interaction, campaign_id="camp-1")

    # Set up instance with character_name (PV-04 instance model)
    session = store.get_by_channel("chan-1")
    session.character_instances["owner"] = CampaignCharacterInstance(
        campaign_id="camp-1",
        user_id="owner",
        character_name="Test Investigator",
        archive_profile_id="prof-1",
        status="active",
    )

    # Ready up
    ready_interaction = fake_interaction(
        channel_id="chan-1", guild_id="g1", user_id="owner"
    )
    await cmd.ready(ready_interaction)

    session = store.get_by_channel("chan-1")
    assert session.player_ready["owner"] is True
    assert session.members["owner"].ready is True


@pytest.mark.asyncio
async def test_ready_rejects_no_profile_selected():
    """ready returns error when no profile selected."""
    store = SessionStore()
    cmd = _make_bot_commands(store)

    interaction = _fake_interaction_with_channel(
        channel_id="chan-1", guild_id="g1", user_id="owner"
    )
    await cmd.bind_campaign(interaction, campaign_id="camp-1")

    await cmd.ready(interaction)

    interaction.response.send_message.assert_called()
    calls = interaction.response.send_message.call_args_list
    last_call_args = calls[-1]
    assert (
        "profile" in last_call_args.args[0].lower() or "档案" in last_call_args.args[0]
    )


@pytest.mark.asyncio
async def test_load_adventure_loads_adventure():
    """load_adventure loads adventure and sends follow-up message prompting /ready."""
    from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
    from dm_bot.rules.compendium import FixtureCompendium
    from dm_bot.rules.engine import RulesEngine

    store = SessionStore()
    gameplay = GameplayOrchestrator(
        importer=None,
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(
            compendium=FixtureCompendium(baseline="2014", fixtures={})
        ),
    )
    cmd = BotCommands(
        settings=None,
        session_store=store,
        turn_coordinator=MagicMock(),
        persistence_store=MagicMock(),
        gameplay=gameplay,
    )
    cmd._persistence_store = MagicMock()
    cmd._persistence_store.load_campaign_state = MagicMock(
        return_value={"mode": {"mode": "dm", "scene_speakers": []}}
    )

    # Setup: bind campaign
    interaction = _fake_interaction_with_channel(
        channel_id="chan-1", guild_id="g1", user_id="owner"
    )
    await cmd.bind_campaign(interaction, campaign_id="camp-1")

    # Load adventure
    load_interaction = fake_interaction(
        channel_id="chan-1", guild_id="g1", user_id="owner"
    )
    await cmd.load_adventure(load_interaction, adventure_id="mad_mansion")

    # Verify adventure loaded
    assert gameplay.adventure_state is not None

    # Verify response sent
    load_interaction.response.send_message.assert_called()
    response_msg = load_interaction.response.send_message.call_args.args[0]
    assert "已加载" in response_msg

    # Verify channel message with ready prompt
    assert len(load_interaction.channel.messages) > 0
    assert "ready" in load_interaction.channel.messages[0].lower()

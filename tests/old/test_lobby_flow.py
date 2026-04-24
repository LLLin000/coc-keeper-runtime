"""Integration tests for full lobby flow.

Tests complete sequence: bind → join → select_profile × 2 → ready × 2
verifying SessionStore state after each step.

Phase 61 - Discord Command Layer Validation
"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest

from dm_bot.discord_bot.commands import BotCommands
from dm_bot.orchestrator.session_store import SessionStore, CampaignCharacterInstance
from tests.fakes.discord import fake_interaction


class FakeProfile:
    def __init__(
        self, profile_id: str, user_id: str, name: str = "Test Investigator"
    ) -> None:
        self.profile_id = profile_id
        self.user_id = user_id
        self.name = name
        self.status = "active"


def _make_bot_commands(store: SessionStore) -> BotCommands:
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


@pytest.mark.asyncio
async def test_full_lobby_flow_bind_join_select_ready():
    """Full lobby flow: owner binds → guest joins → owner selects profile → guest selects profile → owner ready → guest ready."""
    store = SessionStore()
    cmd = _make_bot_commands(store)

    owner_interaction = fake_interaction(
        channel_id="chan-1", guild_id="g1", user_id="owner"
    )
    guest_interaction = fake_interaction(
        channel_id="chan-1", guild_id="g1", user_id="guest"
    )

    owner_profile = FakeProfile(
        profile_id="prof-owner", user_id="owner", name="Investigator A"
    )
    guest_profile = FakeProfile(
        profile_id="prof-guest", user_id="guest", name="Investigator B"
    )

    cmd._archive_repository.list_profiles = MagicMock()
    cmd._archive_repository.get_profile = MagicMock()

    await cmd.bind_campaign(owner_interaction, campaign_id="camp-1")

    session = store.get_by_channel("chan-1")
    assert session is not None
    assert session.owner_id == "owner"
    assert session.member_ids == {"owner"}
    assert session.session_phase.value == "lobby"

    await cmd.join_campaign(guest_interaction)

    session = store.get_by_channel("chan-1")
    assert session.member_ids == {"owner", "guest"}

    cmd._archive_repository.list_profiles.side_effect = lambda user_id: (
        [owner_profile] if user_id == "owner" else [guest_profile]
    )
    cmd._archive_repository.get_profile.side_effect = lambda uid, pid: (
        owner_profile if pid == "prof-owner" else guest_profile
    )

    await cmd.select_profile(owner_interaction, profile_id="prof-owner")

    session = store.get_by_channel("chan-1")
    assert session.selected_profiles["owner"] == "prof-owner"
    assert session.members["owner"].selected_profile_id == "prof-owner"

    await cmd.select_profile(guest_interaction, profile_id="prof-guest")

    session = store.get_by_channel("chan-1")
    assert session.selected_profiles["guest"] == "prof-guest"
    assert session.members["guest"].selected_profile_id == "prof-guest"

    # Set up instance with character_name for owner (PV-04 instance model)
    session.character_instances["owner"] = CampaignCharacterInstance(
        campaign_id="camp-1",
        user_id="owner",
        character_name="Investigator A",
        archive_profile_id="prof-owner",
        status="active",
    )
    session.character_instances["guest"] = CampaignCharacterInstance(
        campaign_id="camp-1",
        user_id="guest",
        character_name="Investigator B",
        archive_profile_id="prof-guest",
        status="active",
    )

    await cmd.ready(owner_interaction)

    session = store.get_by_channel("chan-1")
    assert session.player_ready["owner"] is True
    assert session.members["owner"].ready is True

    await cmd.ready(guest_interaction)

    session = store.get_by_channel("chan-1")
    assert session.player_ready["guest"] is True
    assert session.members["guest"].ready is True


@pytest.mark.asyncio
async def test_lobby_flow_state_persistence():
    """Lobby flow state persists correctly through the sequence."""
    store = SessionStore()
    cmd = _make_bot_commands(store)

    interaction = fake_interaction(channel_id="chan-1", guild_id="g1", user_id="owner")
    profile = FakeProfile(
        profile_id="prof-1", user_id="owner", name="Test Investigator"
    )

    cmd._archive_repository.list_profiles = MagicMock(return_value=[profile])
    cmd._archive_repository.get_profile = MagicMock(return_value=profile)

    await cmd.bind_campaign(interaction, campaign_id="camp-1")
    session = store.get_by_channel("chan-1")

    await cmd.join_campaign(interaction)
    session = store.get_by_channel("chan-1")

    await cmd.select_profile(interaction, profile_id="prof-1")
    session = store.get_by_channel("chan-1")
    assert session.selected_profiles["owner"] == "prof-1"

    # Set up instance with character_name (PV-04 instance model)
    session.character_instances["owner"] = CampaignCharacterInstance(
        campaign_id="camp-1",
        user_id="owner",
        character_name="Test Investigator",
        archive_profile_id="prof-1",
        status="active",
    )

    await cmd.ready(interaction)
    session = store.get_by_channel("chan-1")

    assert session.player_ready["owner"] is True
    assert session.member_ids == {"owner"}
    assert session.selected_profiles["owner"] == "prof-1"

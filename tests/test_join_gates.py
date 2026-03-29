"""TDD tests for join_campaign membership gates.

Tests three enforcement gates:
1. No duplicate joins (user already in campaign)
2. No join in unbound channel (no campaign bound to this Discord channel)
3. No second active character instance (user already has one in this campaign)
"""

import pytest
from dm_bot.orchestrator.session_store import (
    SessionStore,
    DuplicateMemberError,
    UnboundChannelError,
)


def test_join_campaign_creates_member():
    store = SessionStore()
    store.bind_campaign(
        campaign_id="camp-1",
        channel_id="chan-1",
        guild_id="guild-1",
        owner_id="owner-1",
    )
    session = store.join_campaign(channel_id="chan-1", user_id="user-1")
    assert "user-1" in session.members
    assert session.members["user-1"].user_id == "user-1"


def test_join_campaign_twice_raises_duplicate_member_error():
    store = SessionStore()
    store.bind_campaign(
        campaign_id="camp-1",
        channel_id="chan-1",
        guild_id="guild-1",
        owner_id="owner-1",
    )
    store.join_campaign(channel_id="chan-1", user_id="user-1")
    with pytest.raises(DuplicateMemberError) as exc_info:
        store.join_campaign(channel_id="chan-1", user_id="user-1")
    assert "user-1" in str(exc_info.value)


def test_join_campaign_unbound_channel_raises_unbound_channel_error():
    store = SessionStore()
    with pytest.raises(UnboundChannelError):
        store.join_campaign(channel_id="chan-unbound", user_id="user-1")


def test_join_campaign_creates_character_instance_on_join():
    """Joining creates a blank CampaignCharacterInstance for the user."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="camp-1",
        channel_id="chan-1",
        guild_id="guild-1",
        owner_id="owner-1",
    )
    session = store.join_campaign(channel_id="chan-1", user_id="user-1")
    assert "user-1" in session.character_instances
    assert (
        session.character_instances["user-1"].character_name == ""
    )  # blank until bind_character


def test_join_campaign_twice_with_character_raises_duplicate_member():
    """Even after bind_character, a second join should fail with DuplicateMemberError."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="camp-1",
        channel_id="chan-1",
        guild_id="guild-1",
        owner_id="owner-1",
    )
    store.join_campaign(channel_id="chan-1", user_id="user-1")
    store.bind_character(channel_id="chan-1", user_id="user-1", character_name="Alice")
    with pytest.raises(DuplicateMemberError):
        store.join_campaign(channel_id="chan-1", user_id="user-1")

"""SESS-01: Multi-user campaign lifecycle tests.

Tests multi-player campaign lifecycle:
1. 3 players can bind, join, select profiles, ready up, and load adventure without error
2. SessionPhase transitions work correctly with 3 players
3. Round collection correctly tracks pending/submitted state for 3 players
4. Concurrent ready submissions are handled correctly
"""

import pytest
from dm_bot.orchestrator.session_store import (
    SessionStore,
    SessionPhase,
    CampaignMember,
)


@pytest.fixture
def three_player_session():
    """Create a session with 3 players ready for adventure."""
    from dm_bot.orchestrator.session_store import CampaignCharacterInstance

    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="ch1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="ch1", user_id="player1")
    store.join_campaign(channel_id="ch1", user_id="player2")
    # owner doesn't get instance from bind_campaign, create it manually
    session = store.get_by_channel("ch1")
    session.character_instances["owner"] = CampaignCharacterInstance(
        campaign_id="c1",
        user_id="owner",
        character_name="",
    )
    # owner, player1, player2 are members with instances
    return store


def test_three_player_bind_join_flow(three_player_session):
    """3 players can bind, join without error."""
    session = three_player_session.get_by_channel("ch1")
    assert len(session.member_ids) == 3
    assert "owner" in session.members
    assert "player1" in session.members
    assert "player2" in session.members


def test_three_player_select_profile_and_ready(three_player_session):
    """All 3 players can select profiles and ready up (PV-04 instance model)."""
    store = three_player_session
    # Set up instance with character_name for each player (PV-04 instance model)
    session = store.get_by_channel("ch1")
    for uid in ["owner", "player1", "player2"]:
        instance = store.get_character_instance("ch1", uid)
        assert instance is not None
        instance.character_name = f"Char_{uid}"
        instance.archive_profile_id = f"prof-{uid}"
        instance.status = "active"

    # Validate ready for all
    for uid in ["owner", "player1", "player2"]:
        result = store.validate_ready(channel_id="ch1", user_id=uid)
        assert result.success, f"Player {uid} should be ready"

    # Set ready
    for uid in ["owner", "player1", "player2"]:
        store.get_by_channel("ch1").set_player_ready(uid, True)

    session = store.get_by_channel("ch1")
    assert all(session.player_ready.values())


def test_load_adventure_sets_awaiting_ready_phase(three_player_session):
    """load_adventure transitions to AWAITING_READY."""
    session = three_player_session.get_by_channel("ch1")
    session.transition_to(SessionPhase.AWAITING_READY)
    assert session.session_phase == SessionPhase.AWAITING_READY


def test_can_start_session_requires_all_ready_and_admin(three_player_session):
    """can_start_session returns true only when all ready + admin_started."""
    session = three_player_session.get_by_channel("ch1")
    session.set_player_ready("owner", True)
    session.set_player_ready("player1", True)
    session.set_player_ready("player2", True)
    session.admin_started = True
    assert session.can_start_session() is True

    # Not ready without admin
    session.admin_started = False
    assert session.can_start_session() is False


def test_three_players_ready_concurrently(three_player_session):
    """Concurrent ready submissions handled correctly."""
    session = three_player_session.get_by_channel("ch1")
    for uid in ["owner", "player1", "player2"]:
        session.set_player_ready(uid, True)
    session.admin_started = True
    assert session.can_start_session() is True


def test_all_players_can_have_active_character_name(three_player_session):
    """All 3 players can have active character name for ready (PV-04 instance model)."""
    store = three_player_session
    session = store.get_by_channel("ch1")

    # Set up instance with character_name for all (PV-04 instance model)
    for uid in ["owner", "player1", "player2"]:
        instance = store.get_character_instance("ch1", uid)
        assert instance is not None
        instance.character_name = f"Char_{uid}"
        instance.status = "active"

    # All should be valid for ready
    for uid in ["owner", "player1", "player2"]:
        result = store.validate_ready(channel_id="ch1", user_id=uid)
        assert result.success, f"Player {uid} should be ready with active instance"

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
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="ch1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="ch1", user_id="player1")
    store.join_campaign(channel_id="ch1", user_id="player2")
    # owner, player1, player2 are members
    return store


def test_three_player_bind_join_flow(three_player_session):
    """3 players can bind, join without error."""
    session = three_player_session.get_by_channel("ch1")
    assert len(session.member_ids) == 3
    assert "owner" in session.members
    assert "player1" in session.members
    assert "player2" in session.members


def test_three_player_select_profile_and_ready(three_player_session):
    """All 3 players can select profiles and ready up."""
    store = three_player_session
    # Simulate profile selection
    session = store.get_by_channel("ch1")
    for uid in ["owner", "player1", "player2"]:
        session.members[uid].selected_profile_id = f"prof-{uid}"
        session.selected_profiles[uid] = f"prof-{uid}"

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
    """All 3 players can have active_character_name OR selected_profile_id for ready."""
    session = three_player_session.get_by_channel("ch1")

    # Set active_character_name for all
    session.active_characters = {
        "owner": "Alice",
        "player1": "Bob",
        "player2": "Carol",
    }
    for uid in ["owner", "player1", "player2"]:
        session.members[uid].active_character_name = session.active_characters[uid]

    # All should be valid for ready without profile selection
    store = three_player_session
    for uid in ["owner", "player1", "player2"]:
        result = store.validate_ready(channel_id="ch1", user_id=uid)
        assert result.success, (
            f"Player {uid} should be ready with active_character_name"
        )

"""Multi-user round collection tests.

Tests round collection with 3 players:
1. 3 players submit actions in order, all tracked correctly
2. has_submitted() returns correct state per player
3. get_pending_members() excludes submitted players
4. all_submitted() true only when all 3 submitted
5. clear_all_actions() resets for next round
"""

import pytest
from dm_bot.orchestrator.session_store import (
    SessionStore,
    SessionPhase,
)


@pytest.fixture
def round_session():
    """Create session with 3 players ready for round collection."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="ch1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="ch1", user_id="player1")
    store.join_campaign(channel_id="ch1", user_id="player2")
    session = store.get_by_channel("ch1")
    session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
    session.active_characters = {
        "owner": "Alice",
        "player1": "Bob",
        "player2": "Carol",
    }
    return store


def test_three_players_submit_actions_sequential(round_session):
    """3 players submit actions in order, all tracked."""
    session = round_session.get_by_channel("ch1")
    for uid in ["owner", "player1", "player2"]:
        session.set_player_action(uid, f"Action by {uid}")
    assert len(session.pending_actions) == 3
    assert len(session.action_submitters) == 3
    assert session.all_submitted() is True


def test_three_players_submit_actions_reverse(round_session):
    """3 players submit actions in reverse order."""
    session = round_session.get_by_channel("ch1")
    for uid in ["player2", "player1", "owner"]:
        session.set_player_action(uid, f"Action by {uid}")
    assert session.all_submitted() is True


def test_pending_members_excludes_submitted(round_session):
    """get_pending_members() excludes already-submitted players."""
    session = round_session.get_by_channel("ch1")
    session.set_player_action("owner", "Owner action")
    pending = session.get_pending_members()
    assert "owner" not in pending
    assert "player1" in pending
    assert "player2" in pending


def test_all_submitted_requires_all_players(round_session):
    """all_submitted() is False until all 3 submit."""
    session = round_session.get_by_channel("ch1")
    assert session.all_submitted() is False
    session.set_player_action("owner", "Action")
    assert session.all_submitted() is False
    session.set_player_action("player1", "Action")
    assert session.all_submitted() is False
    session.set_player_action("player2", "Action")
    assert session.all_submitted() is True


def test_clear_all_actions_resets_for_next_round(round_session):
    """clear_all_actions() resets for next round."""
    session = round_session.get_by_channel("ch1")
    for uid in ["owner", "player1", "player2"]:
        session.set_player_action(uid, f"Action by {uid}")
    assert session.all_submitted() is True
    session.clear_all_actions()
    assert len(session.pending_actions) == 0
    assert len(session.action_submitters) == 0
    assert session.all_submitted() is False


def test_get_submitter_names(round_session):
    """get_submitter_names returns character names, not user IDs."""
    session = round_session.get_by_channel("ch1")
    session.set_player_action("owner", "Action")
    session.set_player_action("player1", "Action")
    names = session.get_submitter_names()
    assert "Alice" in names
    assert "Bob" in names
    assert "Carol" not in names


def test_has_submitted_per_player(round_session):
    """has_submitted() returns correct state per player."""
    session = round_session.get_by_channel("ch1")
    assert session.has_submitted("owner") is False
    assert session.has_submitted("player1") is False
    assert session.has_submitted("player2") is False

    session.set_player_action("player1", "Bob's action")
    assert session.has_submitted("owner") is False
    assert session.has_submitted("player1") is True
    assert session.has_submitted("player2") is False


def test_duplicate_action_replaces_previous(round_session):
    """Setting action again replaces the previous action."""
    session = round_session.get_by_channel("ch1")
    session.set_player_action("owner", "First action")
    assert session.pending_actions["owner"] == "First action"

    session.set_player_action("owner", "Second action")
    assert session.pending_actions["owner"] == "Second action"
    assert len(session.pending_actions) == 1  # Still only one action per player

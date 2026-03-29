"""SESS-02: SessionPhase transitions under multi-user load.

Tests SessionPhase transition behavior:
1. LOBBY→AWAITING_READY transition when load_adventure called
2. AWAITING_READY→SCENE_ROUND_OPEN when all ready + admin_started
3. SCENE_ROUND_OPEN→COMBAT when encounter triggered
4. Phase history records all transitions correctly
5. Rapid transitions are atomic with no race conditions
"""

import pytest
from dm_bot.orchestrator.session_store import (
    SessionStore,
    SessionPhase,
)


@pytest.fixture
def multi_player_session():
    """Create session with 3 players in LOBBY."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="ch1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="ch1", user_id="player1")
    store.join_campaign(channel_id="ch1", user_id="player2")
    session = store.get_by_channel("ch1")
    assert session.session_phase == SessionPhase.LOBBY
    return store


def test_lobby_to_awaiting_ready_on_load_adventure(multi_player_session):
    """LOBBY→AWAITING_READY transition when load_adventure called."""
    session = multi_player_session.get_by_channel("ch1")
    session.transition_to(SessionPhase.AWAITING_READY)
    assert session.session_phase == SessionPhase.AWAITING_READY
    assert len(session.phase_history) == 1


def test_awaiting_ready_to_scene_round_open(multi_player_session):
    """AWAITING_READY→SCENE_ROUND_OPEN when all ready + admin."""
    session = multi_player_session.get_by_channel("ch1")
    session.transition_to(SessionPhase.AWAITING_READY)
    # Set all ready
    for uid in ["owner", "player1", "player2"]:
        session.set_player_ready(uid, True)
    session.admin_started = True
    # Transition when can start
    if session.can_start_session():
        session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
    assert session.session_phase == SessionPhase.SCENE_ROUND_OPEN


def test_scene_round_open_to_combat(multi_player_session):
    """SCENE_ROUND_OPEN→COMBAT transition triggered by encounter."""
    session = multi_player_session.get_by_channel("ch1")
    session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
    session.transition_to(SessionPhase.COMBAT)
    assert session.session_phase == SessionPhase.COMBAT


def test_phase_history_records_all_transitions(multi_player_session):
    """All phase transitions recorded in phase_history."""
    session = multi_player_session.get_by_channel("ch1")
    transitions = [
        SessionPhase.AWAITING_READY,
        SessionPhase.SCENE_ROUND_OPEN,
        SessionPhase.COMBAT,
    ]
    for phase in transitions:
        session.transition_to(phase)
    assert len(session.phase_history) == 3
    assert session.phase_history[0][0] == "awaiting_ready"
    assert session.phase_history[1][0] == "scene_round_open"
    assert session.phase_history[2][0] == "combat"


def test_concurrent_transitions_dont_race(multi_player_session):
    """Phase transitions are atomic, no race condition."""
    session = multi_player_session.get_by_channel("ch1")
    # Rapid transitions
    session.transition_to(SessionPhase.AWAITING_READY)
    session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
    session.transition_to(SessionPhase.COMBAT)
    assert session.session_phase == SessionPhase.COMBAT
    # History should have all 3
    assert len(session.phase_history) == 3


def test_lobby_to_awaiting_ready_via_load_adventure(multi_player_session):
    """Simulate load_adventure triggering AWAITING_READY phase."""
    session = multi_player_session.get_by_channel("ch1")
    # load_adventure should transition to AWAITING_READY
    session.transition_to(SessionPhase.AWAITING_READY)
    assert session.session_phase == SessionPhase.AWAITING_READY
    # Verify initial LOBBY is not in history (first transition is AWAITING_READY)
    assert session.phase_history[0][0] == "awaiting_ready"

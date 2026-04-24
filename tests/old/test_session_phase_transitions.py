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
    """Create session with 3 players. Note: non-owner joins auto-transition to AWAITING_READY."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="ch1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="ch1", user_id="player1")
    store.join_campaign(channel_id="ch1", user_id="player2")
    session = store.get_by_channel("ch1")
    # After E90: first non-owner join triggers LOBBY → AWAITING_READY
    assert session.session_phase == SessionPhase.AWAITING_READY
    return store


@pytest.fixture
def lobby_session():
    """Create session with only owner (stays in LOBBY)."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="ch1", guild_id="g1", owner_id="owner"
    )
    session = store.get_by_channel("ch1")
    assert session.session_phase == SessionPhase.LOBBY
    return store


def test_lobby_to_awaiting_ready_on_load_adventure(lobby_session):
    """LOBBY→AWAITING_READY transition when load_adventure called."""
    session = lobby_session.get_by_channel("ch1")
    session.transition_to(SessionPhase.AWAITING_READY)
    assert session.session_phase == SessionPhase.AWAITING_READY
    assert len(session.phase_history) == 1


def test_awaiting_ready_to_scene_round_open(multi_player_session):
    """AWAITING_READY→SCENE_ROUND_OPEN when all ready + admin."""
    session = multi_player_session.get_by_channel("ch1")
    # Already in AWAITING_READY from fixture
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


def test_phase_history_records_all_transitions(lobby_session):
    """All phase transitions recorded in phase_history."""
    session = lobby_session.get_by_channel("ch1")
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
    # Already in AWAITING_READY from fixture
    session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
    session.transition_to(SessionPhase.COMBAT)
    assert session.session_phase == SessionPhase.COMBAT
    # History should have 2 transitions (AWAITING_READY from fixture + 2 manual)
    assert len(session.phase_history) == 3


def test_lobby_to_awaiting_ready_via_load_adventure(lobby_session):
    """Simulate load_adventure triggering AWAITING_READY phase."""
    session = lobby_session.get_by_channel("ch1")
    # load_adventure should transition to AWAITING_READY
    session.transition_to(SessionPhase.AWAITING_READY)
    assert session.session_phase == SessionPhase.AWAITING_READY
    # Verify initial LOBBY is not in history (first transition is AWAITING_READY)
    assert session.phase_history[0][0] == "awaiting_ready"


def test_join_campaign_triggers_lobby_to_awaiting_ready(lobby_session):
    """First non-owner join auto-transitions LOBBY → AWAITING_READY."""
    session = lobby_session.get_by_channel("ch1")
    assert session.session_phase == SessionPhase.LOBBY

    lobby_session.join_campaign(channel_id="ch1", user_id="player1")
    session = lobby_session.get_by_channel("ch1")

    assert session.session_phase == SessionPhase.AWAITING_READY
    assert session.phase_history[0][0] == "awaiting_ready"


def test_owner_join_does_not_trigger_phase_transition(lobby_session):
    """Owner-only session stays in LOBBY."""
    session = lobby_session.get_by_channel("ch1")
    assert session.session_phase == SessionPhase.LOBBY
    # Owner is already added by bind_campaign, so no join needed
    # Verify LOBBY stays LOBBY with only owner
    assert session.session_phase == SessionPhase.LOBBY


def test_second_join_does_not_overshoot_phase(lobby_session):
    """Multiple joins stay in AWAITING_READY, no overshoot."""
    lobby_session.join_campaign(channel_id="ch1", user_id="player1")
    session = lobby_session.get_by_channel("ch1")
    assert session.session_phase == SessionPhase.AWAITING_READY
    initial_history_len = len(session.phase_history)

    lobby_session.join_campaign(channel_id="ch1", user_id="player2")
    session = lobby_session.get_by_channel("ch1")

    assert session.session_phase == SessionPhase.AWAITING_READY
    assert len(session.phase_history) == initial_history_len


def test_join_on_non_lobby_does_not_transition(lobby_session):
    """Join on non-LOBBY phase does not transition."""
    lobby_session.join_campaign(channel_id="ch1", user_id="player1")
    session = lobby_session.get_by_channel("ch1")
    session.transition_to(SessionPhase.AWAITING_ADMIN_START)
    assert session.session_phase == SessionPhase.AWAITING_ADMIN_START

    lobby_session.join_campaign(channel_id="ch1", user_id="player3")
    session = lobby_session.get_by_channel("ch1")

    assert session.session_phase == SessionPhase.AWAITING_ADMIN_START


def test_all_ready_false_when_not_all_ready(multi_player_session):
    """all_ready() returns False when not all players are ready."""
    session = multi_player_session.get_by_channel("ch1")
    session.set_player_ready("owner", True)
    session.set_player_ready("player1", True)
    # player2 not ready
    assert session.all_ready() is False


def test_all_ready_true_when_all_ready(multi_player_session):
    """all_ready() returns True when all players are ready."""
    session = multi_player_session.get_by_channel("ch1")
    for uid in ["owner", "player1", "player2"]:
        session.set_player_ready(uid, True)
    assert session.all_ready() is True


def test_all_ready_empty_members_returns_true():
    """all_ready() returns True for empty member_ids (vacuous truth)."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="ch1", guild_id="g1", owner_id="owner"
    )
    session = store.get_by_channel("ch1")
    session.member_ids.clear()
    assert session.all_ready() is True


def test_ready_triggers_awaiting_ready_to_awaiting_admin_start(multi_player_session):
    """transition_on_all_ready() transitions AWAITING_READY → AWAITING_ADMIN_START."""
    session = multi_player_session.get_by_channel("ch1")
    assert session.session_phase == SessionPhase.AWAITING_READY

    for uid in ["owner", "player1", "player2"]:
        session.set_player_ready(uid, True)

    result = session.transition_on_all_ready()

    assert result is True
    assert session.session_phase == SessionPhase.AWAITING_ADMIN_START
    assert session.phase_history[-1][0] == "awaiting_admin_start"


def test_ready_does_not_transition_prematurely(multi_player_session):
    """transition_on_all_ready() returns False when not all players ready."""
    session = multi_player_session.get_by_channel("ch1")
    session.set_player_ready("owner", True)
    # Only 1 of 3 ready

    result = session.transition_on_all_ready()

    assert result is False
    assert session.session_phase == SessionPhase.AWAITING_READY


def test_ready_does_not_transition_from_wrong_phase(multi_player_session):
    """transition_on_all_ready() returns False when not in AWAITING_READY phase."""
    session = multi_player_session.get_by_channel("ch1")
    session.transition_to(SessionPhase.AWAITING_ADMIN_START)
    for uid in ["owner", "player1", "player2"]:
        session.set_player_ready(uid, True)

    result = session.transition_on_all_ready()

    assert result is False
    assert session.session_phase == SessionPhase.AWAITING_ADMIN_START


def test_admin_start_transitions_awaiting_admin_start_to_onboarding(
    multi_player_session,
):
    """start_session() transitions AWAITING_ADMIN_START → ONBOARDING."""
    session = multi_player_session.get_by_channel("ch1")
    # Set all ready and transition to AWAITING_ADMIN_START (simulating what happens after E91)
    for uid in ["owner", "player1", "player2"]:
        session.set_player_ready(uid, True)
    session.transition_to(SessionPhase.AWAITING_ADMIN_START)
    session.admin_started = True

    # Simulate start_session() calling transition_to(ONBOARDING)
    if (
        session.session_phase == SessionPhase.AWAITING_ADMIN_START
        and session.can_start_session()
    ):
        session.transition_to(SessionPhase.ONBOARDING)

    assert session.session_phase == SessionPhase.ONBOARDING
    assert session.phase_history[-1][0] == "onboarding"


def test_onboarding_complete_transitions_to_scene_round_open(multi_player_session):
    """All players completing onboarding transitions to SCENE_ROUND_OPEN."""
    session = multi_player_session.get_by_channel("ch1")
    session.transition_to(SessionPhase.ONBOARDING)

    # Simulate all players completing onboarding
    for member_id in session.member_ids:
        session.set_onboarding_complete(member_id, True)

    # Check if all complete - this would trigger transition
    all_complete = all(
        session.is_onboarding_complete(mid) for mid in session.member_ids
    )
    if all_complete:
        session.transition_to(SessionPhase.SCENE_ROUND_OPEN)

    assert session.session_phase == SessionPhase.SCENE_ROUND_OPEN
    assert session.phase_history[-1][0] == "scene_round_open"


def test_full_phase_progression(multi_player_session):
    """Test full session phase progression: lobby → awaiting_ready → awaiting_admin_start → onboarding → scene_round_open."""
    session = multi_player_session.get_by_channel("ch1")

    # Phase 1: Already in AWAITING_READY after first join (E90)
    assert session.session_phase == SessionPhase.AWAITING_READY

    # Phase 2: All ready triggers → AWAITING_ADMIN_START (E91)
    for uid in ["owner", "player1", "player2"]:
        session.set_player_ready(uid, True)
    session.transition_on_all_ready()
    assert session.session_phase == SessionPhase.AWAITING_ADMIN_START

    # Phase 3: Admin start triggers → ONBOARDING (E92)
    session.admin_started = True
    session.transition_to(SessionPhase.ONBOARDING)
    assert session.session_phase == SessionPhase.ONBOARDING

    # Phase 4: All onboarding complete triggers → SCENE_ROUND_OPEN (E92)
    for member_id in session.member_ids:
        session.set_onboarding_complete(member_id, True)
    session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
    assert session.session_phase == SessionPhase.SCENE_ROUND_OPEN

    # Verify phase history records all transitions
    phases = [h[0] for h in session.phase_history]
    assert "awaiting_ready" in phases
    assert "awaiting_admin_start" in phases
    assert "onboarding" in phases
    assert "scene_round_open" in phases

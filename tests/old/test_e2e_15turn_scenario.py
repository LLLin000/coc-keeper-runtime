"""SCEN-01/02/03: 15-turn fuzhe e2e scenario tests.

Integration tests for the full 15-turn fuzhe scenario covering:
- SCEN-01: 15 turns execute end-to-end without exception
- SCEN-02: DB recovery mid-scenario produces identical end state
- SCEN-03: Crash recovery re-initializes all layers correctly
"""

from __future__ import annotations

import pytest
from pathlib import Path

from dm_bot.orchestrator.session_store import SessionStore, SessionPhase
from dm_bot.persistence.store import PersistenceStore


@pytest.fixture
def e2e_store():
    """In-memory store for e2e test."""
    store = SessionStore()
    return store


@pytest.fixture
def e2e_session(e2e_store: SessionStore) -> SessionStore:
    """Set up a fuzhe campaign with 4 members in SCENE_ROUND_OPEN phase."""
    store = e2e_store
    store.bind_campaign(
        campaign_id="fuzhe-c1", channel_id="ch1", guild_id="g1", owner_id="kp"
    )
    store.join_campaign(channel_id="ch1", user_id="player1")
    store.join_campaign(channel_id="ch1", user_id="player2")
    store.join_campaign(channel_id="ch1", user_id="player3")
    session = store.get_by_channel("ch1")
    session.transition_to(SessionPhase.AWAITING_READY)
    for uid in ["kp", "player1", "player2", "player3"]:
        session.set_player_ready(uid, True)
    session.admin_started = True
    session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
    session.active_characters = {
        "kp": "张记者",
        "player1": "王侦探",
        "player2": "李医生",
        "player3": "赵警员",
    }
    return store


def test_15turn_fuzhe_scenario_completes(e2e_session: SessionStore) -> None:
    """SCEN-01: 15 turns of fuzhe execute without exception."""
    store = e2e_session
    session = store.get_by_channel("ch1")

    for turn in range(1, 16):
        # Simulate each turn: submit action → resolve → next round
        session.set_player_action("player1", f"调查行动{turn}")
        session.set_player_action("player2", f"观察{turn}")
        session.set_player_action("player3", f"询问{turn}")
        # Verify all submitted
        for uid in ["player1", "player2", "player3"]:
            assert session.has_submitted(uid), (
                f"Turn {turn}: {uid} should have submitted"
            )
        session.clear_all_actions()

    assert session.session_phase == SessionPhase.SCENE_ROUND_OPEN


def test_end_state_matches_expectation(e2e_session: SessionStore) -> None:
    """SCEN-01: After 15 turns, session state is consistent."""
    store = e2e_session
    session = store.get_by_channel("ch1")

    # Simulate 15 turns
    for turn in range(1, 16):
        for uid in ["player1", "player2", "player3"]:
            session.set_player_action(uid, f"action{turn}")
        session.clear_all_actions()

    # All players should still be active members
    for uid in ["player1", "player2", "player3"]:
        assert uid in session.member_ids

    # Phase should still be SCENE_ROUND_OPEN
    assert session.session_phase == SessionPhase.SCENE_ROUND_OPEN

    # All characters should be bound
    assert session.active_characters["kp"] == "张记者"
    assert session.active_characters["player1"] == "王侦探"
    assert session.active_characters["player2"] == "李医生"
    assert session.active_characters["player3"] == "赵警员"


def test_db_recovery_mid_scenario(e2e_session: SessionStore, tmp_path: Path) -> None:
    """SCEN-02: Save at turn 8, reload, continue → same end state at turn 15."""
    store = e2e_session
    session = store.get_by_channel("ch1")

    # Simulate 8 turns
    for turn in range(1, 9):
        for uid in ["player1", "player2", "player3"]:
            session.set_player_action(uid, f"action{turn}")
        session.clear_all_actions()

    # Save state to persistence
    persist = PersistenceStore(tmp_path / "campaign.db")
    sessions_data = store.dump_sessions()
    persist.save_sessions(sessions_data)

    # Reload from persistence
    loaded_data = persist.load_sessions()
    assert "ch1" in loaded_data

    # Create new store and load the saved sessions
    restored_store = SessionStore()
    restored_store.load_sessions(loaded_data)
    restored_session = restored_store.get_by_channel("ch1")

    # Verify member count preserved
    assert len(restored_session.member_ids) == 4

    # Continue to turn 15 in restored session
    for turn in range(9, 16):
        for uid in ["player1", "player2", "player3"]:
            restored_session.set_player_action(uid, f"action{turn}")
        restored_session.clear_all_actions()

    # End state should match
    assert restored_session.session_phase == SessionPhase.SCENE_ROUND_OPEN
    assert len(restored_session.member_ids) == 4


def test_recovery_after_simulated_crash(
    e2e_session: SessionStore, tmp_path: Path
) -> None:
    """SCEN-03: Re-init layers, reload session, continue without data loss."""
    store = e2e_session
    session = store.get_by_channel("ch1")

    # Simulate 5 turns before "crash"
    for turn in range(1, 6):
        for uid in ["player1", "player2", "player3"]:
            session.set_player_action(uid, f"action{turn}")
        session.clear_all_actions()

    # Persist state before "crash"
    persist = PersistenceStore(tmp_path / "campaign.db")
    persist.save_sessions(store.dump_sessions())

    # "Crash" - create new store and reload from persistence
    new_store = SessionStore()
    loaded = persist.load_sessions()
    new_store.load_sessions(loaded)

    # Verify campaign recovered
    recovered_session = new_store.get_by_channel("ch1")
    assert recovered_session is not None
    assert recovered_session.campaign_id == "fuzhe-c1"
    assert len(recovered_session.member_ids) == 4

    # Verify active characters preserved
    assert recovered_session.active_characters["player1"] == "王侦探"
    assert recovered_session.active_characters["player2"] == "李医生"
    assert recovered_session.active_characters["player3"] == "赵警员"

    # Continue playing after recovery
    for turn in range(6, 16):
        for uid in ["player1", "player2", "player3"]:
            recovered_session.set_player_action(uid, f"action{turn}")
        recovered_session.clear_all_actions()

    # Should complete without issues
    assert recovered_session.session_phase == SessionPhase.SCENE_ROUND_OPEN


def test_streaming_interruption_recovery(
    e2e_session: SessionStore, tmp_path: Path
) -> None:
    """SCEN-03 variant: Simulate interruption at turn 10, '重新生成' resumes correctly."""
    store = e2e_session
    session = store.get_by_channel("ch1")

    # Simulate turns 1-10
    for turn in range(1, 11):
        for uid in ["player1", "player2", "player3"]:
            session.set_player_action(uid, f"action{turn}")
        session.clear_all_actions()

    # Save state at turn 10 (simulating pre-streaming checkpoint)
    persist = PersistenceStore(tmp_path / "campaign.db")
    persist.save_sessions(store.dump_sessions())

    # Simulate "重新生成" (regenerate) - create new store and reload
    new_store = SessionStore()
    new_store.load_sessions(persist.load_sessions())
    new_session = new_store.get_by_channel("ch1")

    # Verify state at turn 10 is recovered
    assert len(new_session.member_ids) == 4
    assert new_session.session_phase == SessionPhase.SCENE_ROUND_OPEN

    # "重新生成" at turn 10 - clear actions and re-collect
    new_session.clear_all_actions()

    # Re-collect actions for turn 10 (all members including kp)
    for uid in ["kp", "player1", "player2", "player3"]:
        new_session.set_player_action(uid, f"重新生成动作{uid}")
    assert new_session.all_submitted()

    # Continue to turn 15
    new_session.clear_all_actions()
    for turn in range(11, 16):
        for uid in ["player1", "player2", "player3"]:
            new_session.set_player_action(uid, f"action{turn}")
        new_session.clear_all_actions()

    assert new_session.session_phase == SessionPhase.SCENE_ROUND_OPEN

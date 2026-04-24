"""CHAR-02: Character profile projection into campaign session."""

import pytest
from dm_bot.orchestrator.session_store import SessionStore, SessionPhase


@pytest.fixture
def session_with_profiles():
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="ch1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="ch1", user_id="player1")
    store.join_campaign(channel_id="ch1", user_id="player2")
    session = store.get_by_channel("ch1")
    session.transition_to(SessionPhase.AWAITING_READY)
    return store


def test_select_archive_profile_sets_selected_profile(session_with_profiles):
    store = session_with_profiles
    profiles = {
        "owner": {"name": "张记者", "user_id": "owner", "status": "active"},
        "player1": {"name": "王侦探", "user_id": "player1", "status": "active"},
    }
    result = store.select_archive_profile(
        channel_id="ch1", user_id="owner", profile_id="owner", profiles=profiles
    )
    assert result.success is True
    session = store.get_by_channel("ch1")
    assert session.selected_profiles.get("owner") == "owner"


def test_bind_character_sets_active_character_name(session_with_profiles):
    store = session_with_profiles
    store.bind_character(channel_id="ch1", user_id="owner", character_name="张记者")
    session = store.get_by_channel("ch1")
    assert session.active_characters.get("owner") == "张记者"


def test_multi_player_different_profiles(session_with_profiles):
    store = session_with_profiles
    store.bind_character(channel_id="ch1", user_id="owner", character_name="张记者")
    store.bind_character(channel_id="ch1", user_id="player1", character_name="王侦探")
    session = store.get_by_channel("ch1")
    assert len(session.active_characters) == 2
    assert session.active_characters["owner"] != session.active_characters["player1"]


def test_profile_projection_survives_phase_transition(session_with_profiles):
    store = session_with_profiles
    store.bind_character(channel_id="ch1", user_id="owner", character_name="张记者")
    session = store.get_by_channel("ch1")
    session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
    assert session.active_characters.get("owner") == "张记者"


def test_profile_projection_cleared_on_session_end(session_with_profiles):
    store = session_with_profiles
    store.bind_character(channel_id="ch1", user_id="owner", character_name="张记者")
    store.leave_campaign(channel_id="ch1", user_id="owner")
    session = store.get_by_channel("ch1")
    assert session.active_characters.get("owner") is None

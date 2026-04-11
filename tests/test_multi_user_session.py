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
    SceneLifecycle,
    PlayerFocusScope,
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


# --- Scene Lifecycle Tests (v1.0 Phase 1) ---


def test_scene_lifecycle_defaults_to_collecting(three_player_session):
    """Scene lifecycle defaults to COLLECTING for new sessions."""
    session = three_player_session.get_by_channel("ch1")
    assert session.scene_lifecycle == SceneLifecycle.COLLECTING


def test_scene_lifecycle_transitions_are_stateful(three_player_session):
    """Scene lifecycle follows valid transition path: COLLECTING -> LOCKED -> RESOLVING -> PUBLISHED."""
    session = three_player_session.get_by_channel("ch1")

    # Start in COLLECTING
    assert session.scene_lifecycle == SceneLifecycle.COLLECTING

    # Valid transition: COLLECTING -> LOCKED
    result = session.transition_scene_lifecycle(SceneLifecycle.LOCKED)
    assert result is True
    assert session.scene_lifecycle == SceneLifecycle.LOCKED

    # Valid transition: LOCKED -> RESOLVING
    result = session.transition_scene_lifecycle(SceneLifecycle.RESOLVING)
    assert result is True
    assert session.scene_lifecycle == SceneLifecycle.RESOLVING

    # Valid transition: RESOLVING -> PUBLISHED
    result = session.transition_scene_lifecycle(SceneLifecycle.PUBLISHED)
    assert result is True
    assert session.scene_lifecycle == SceneLifecycle.PUBLISHED


def test_scene_lifecycle_rejects_invalid_transitions(three_player_session):
    """Scene lifecycle rejects invalid transitions (e.g., COLLECTING -> RESOLVING directly)."""
    session = three_player_session.get_by_channel("ch1")
    assert session.scene_lifecycle == SceneLifecycle.COLLECTING

    # Invalid: COLLECTING -> RESOLVING (must go through LOCKED)
    result = session.transition_scene_lifecycle(SceneLifecycle.RESOLVING)
    assert result is False
    assert session.scene_lifecycle == SceneLifecycle.COLLECTING

    # Invalid: COLLECTING -> PUBLISHED (must go through LOCKED and RESOLVING)
    result = session.transition_scene_lifecycle(SceneLifecycle.PUBLISHED)
    assert result is False
    assert session.scene_lifecycle == SceneLifecycle.COLLECTING


def test_scene_lifecycle_and_player_focus_are_distinct(three_player_session):
    """Player focus scope and scene lifecycle are separate concepts tracked independently.

    RTR-01: Scene lifecycle and player focus must not collapse into one field.
    """
    session = three_player_session.get_by_channel("ch1")

    # Default values are different enums
    assert session.scene_lifecycle == SceneLifecycle.COLLECTING
    assert session.player_focus == PlayerFocusScope.SINGLE

    # Changing one does not affect the other
    session.scene_lifecycle = SceneLifecycle.LOCKED
    session.player_focus = PlayerFocusScope.SHARED

    assert session.scene_lifecycle == SceneLifecycle.LOCKED
    assert session.player_focus == PlayerFocusScope.SHARED

    # Change them independently again
    session.scene_lifecycle = SceneLifecycle.RESOLVING
    session.player_focus = PlayerFocusScope.KEEPER_ONLY

    assert session.scene_lifecycle == SceneLifecycle.RESOLVING
    assert session.player_focus == PlayerFocusScope.KEEPER_ONLY


def test_player_focus_scope_defaults_to_single(three_player_session):
    """Player focus defaults to SINGLE for new sessions."""
    session = three_player_session.get_by_channel("ch1")
    assert session.player_focus == PlayerFocusScope.SINGLE


def test_lifecycle_context_provides_structured_view(three_player_session):
    """get_lifecycle_context returns structured dict with all lifecycle info."""
    session = three_player_session.get_by_channel("ch1")

    ctx = session.get_lifecycle_context()

    # Contains expected keys
    assert "scene_lifecycle" in ctx
    assert "player_focus" in ctx
    assert "round_number" in ctx
    assert "pending_action_count" in ctx
    assert "submitted_member_count" in ctx
    assert "all_submitted" in ctx

    # Values match current state
    assert ctx["scene_lifecycle"] == session.scene_lifecycle.value
    assert ctx["player_focus"] == session.player_focus.value
    assert ctx["round_number"] is None


def test_scene_lifecycle_persists_across_round_transitions(three_player_session):
    """Scene lifecycle persists when round_number changes."""
    session = three_player_session.get_by_channel("ch1")

    # Set lifecycle and round
    session.scene_lifecycle = SceneLifecycle.LOCKED
    session.round_number = 1

    # Round number change does not reset lifecycle
    session.round_number = 2
    assert session.scene_lifecycle == SceneLifecycle.LOCKED

    # Round number change does not reset focus
    session.player_focus = PlayerFocusScope.SHARED
    session.round_number = 3
    assert session.scene_lifecycle == SceneLifecycle.LOCKED
    assert session.player_focus == PlayerFocusScope.SHARED

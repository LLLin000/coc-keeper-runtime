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
    OpenScene,
    ForkResult,
    SwitchFocusResult,
    Visibility,
    BatchSubmission,
    ResolvedAction,
    MergeProposal,
    BlockerState,
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


# === Phase 2: Fork and Switch Focus Tests ===


class TestForkBehavior:
    """Tests for fork() operation."""

    def test_fork_creates_new_scene(self, three_player_session):
        """fork() creates a new scene and returns its ID."""
        session = three_player_session.get_by_channel("ch1")
        scene_id, result = session.fork(initiating_player="player1")

        assert result.success is True
        assert scene_id == result.scene_id
        assert scene_id in session.open_scenes
        assert session.open_scenes[scene_id].initiating_player == "player1"

    def test_fork_does_not_change_focus(self, three_player_session):
        """fork() does not automatically switch any player's focus."""
        session = three_player_session.get_by_channel("ch1")
        # Player1 already focused on scene1
        session.focused_scene["player1"] = "scene1"

        scene_id, result = session.fork(initiating_player="player1")

        # Focus should be unchanged
        assert session.focused_scene.get("player1") == "scene1"

    def test_fork_rejects_max_scenes_exceeded(self, three_player_session):
        """fork() raises ValueError when 2 open scenes already exist."""
        session = three_player_session.get_by_channel("ch1")
        # Create 2 open scenes
        session.open_scenes["scene1"] = OpenScene(
            scene_id="scene1",
            initiating_player="player1",
            lifecycle=SceneLifecycle.COLLECTING,
        )
        session.open_scenes["scene2"] = OpenScene(
            scene_id="scene2",
            initiating_player="player2",
            lifecycle=SceneLifecycle.COLLECTING,
        )

        with pytest.raises(ValueError, match="Max 2 open scenes"):
            session.fork(initiating_player="player3")

    def test_fork_rejects_player_already_in_open_scene(self, three_player_session):
        """fork() raises ValueError if player is already in an OPEN scene."""
        session = three_player_session.get_by_channel("ch1")
        session.open_scenes["scene1"] = OpenScene(
            scene_id="scene1",
            initiating_player="player1",
            lifecycle=SceneLifecycle.COLLECTING,
        )

        with pytest.raises(ValueError, match="already in an open scene"):
            session.fork(initiating_player="player1")


class TestSwitchFocusBehavior:
    """Tests for switch_focus() operation."""

    def test_switch_focus_updates_focused_scene(self, three_player_session):
        """switch_focus() updates which scene the player is focused on."""
        session = three_player_session.get_by_channel("ch1")
        session.open_scenes["scene1"] = OpenScene(
            scene_id="scene1",
            initiating_player="player1",
            lifecycle=SceneLifecycle.COLLECTING,
        )
        session.open_scenes["scene2"] = OpenScene(
            scene_id="scene2",
            initiating_player="player2",
            lifecycle=SceneLifecycle.COLLECTING,
        )

        result = session.switch_focus(player_id="player1", target_scene_id="scene2")

        assert result.success is True
        assert session.focused_scene["player1"] == "scene2"
        assert result.cross_cut is False

    def test_switch_focus_detects_cross_cut(self, three_player_session):
        """switch_focus() sets cross_cut=True when switching from PUBLISHED to COLLECTING."""
        session = three_player_session.get_by_channel("ch1")
        session.open_scenes["scene1"] = OpenScene(
            scene_id="scene1",
            initiating_player="player1",
            lifecycle=SceneLifecycle.PUBLISHED,  # Resolved/Published scene
        )
        session.open_scenes["scene2"] = OpenScene(
            scene_id="scene2",
            initiating_player="player2",
            lifecycle=SceneLifecycle.COLLECTING,  # Open scene
        )
        session.focused_scene["player1"] = "scene1"

        result = session.switch_focus(player_id="player1", target_scene_id="scene2")

        assert result.cross_cut is True
        assert result.previous_scene_id == "scene1"
        assert result.target_scene_id == "scene2"

    def test_switch_focus_rejects_nonexistent_scene(self, three_player_session):
        """switch_focus() raises ValueError if target scene does not exist."""
        session = three_player_session.get_by_channel("ch1")

        with pytest.raises(ValueError, match="does not exist"):
            session.switch_focus(player_id="player1", target_scene_id="nonexistent")


class TestForkSwitchIntegration:
    """Integration tests for fork/switch workflow."""

    def test_full_fork_switch_workflow(self, three_player_session):
        """Complete workflow: fork -> switch_focus -> cross_cut detected."""
        session = three_player_session.get_by_channel("ch1")

        # Player creates fork
        scene2_id, fork_result = session.fork(initiating_player="player1")
        assert fork_result.success

        # Player switches focus to new scene
        switch_result = session.switch_focus(
            player_id="player1",
            target_scene_id=scene2_id,
        )
        assert switch_result.success

        # First focus switch from nothing should not be cross_cut
        assert switch_result.cross_cut is False

        # Resolve scene2, then switch back (would be cross_cut)
        session.open_scenes[scene2_id].lifecycle = SceneLifecycle.PUBLISHED
        session.open_scenes["original"] = OpenScene(
            scene_id="original",
            initiating_player="player1",
            lifecycle=SceneLifecycle.COLLECTING,
        )

        switch_result2 = session.switch_focus(
            player_id="player1",
            target_scene_id="original",
        )
        assert switch_result2.cross_cut is True  # PUBLISHED -> COLLECTING


# =============================================================================
# Phase 3: Batch and Merge Tests (RTR-03, RTR-04, RTR-05)
# =============================================================================


class TestBatchSubmission:
    """Tests for action batch collection during COLLECTING state."""

    def test_submit_action_accepted_in_collecting(self, three_player_session):
        """Actions can be submitted when scene is in COLLECTING state."""
        session = three_player_session.get_by_channel("ch1")
        scene_id, _ = session.fork(initiating_player="player1")

        batch = session.submit_action(
            scene_id=scene_id,
            user_id="player1",
            character_id="char1",
            action_text="I attack the creature",
            dex_value=50,
            visibility=Visibility.PUBLIC,
        )

        assert batch is not None
        assert "player1" in batch.entries
        assert batch.entries["player1"].action_text == "I attack the creature"
        assert batch.entries["player1"].dex_value == 50
        assert batch.entries["player1"].visibility == Visibility.PUBLIC

    def test_submit_action_rejected_in_locked(self, three_player_session):
        """Actions are rejected when scene is in LOCKED state."""
        session = three_player_session.get_by_channel("ch1")
        scene_id, _ = session.fork(initiating_player="player1")
        session.lock_scene(scene_id)

        with pytest.raises(ValueError, match="not in COLLECTING state"):
            session.submit_action(
                scene_id=scene_id,
                user_id="player1",
                character_id="char1",
                action_text="late action",
            )

    def test_submit_action_rejected_for_nonexistent_scene(self, three_player_session):
        """Submitting to nonexistent scene raises ValueError."""
        session = three_player_session.get_by_channel("ch1")

        with pytest.raises(ValueError, match="does not exist"):
            session.submit_action(
                scene_id="fake-scene",
                user_id="player1",
                character_id="char1",
                action_text="action",
            )


class TestDeterministicResolution:
    """Tests for deterministic resolution ordering (RTR-03)."""

    def test_resolution_order_by_dex_descending(self, three_player_session):
        """Higher dex values resolve first."""
        session = three_player_session.get_by_channel("ch1")
        scene_id, _ = session.fork(initiating_player="player1")

        # Submit in wrong order (p2 first) but p1 has higher dex
        session.submit_action(
            scene_id=scene_id, user_id="player2", character_id="c2",
            action_text="dodge", dex_value=30,
        )
        session.submit_action(
            scene_id=scene_id, user_id="player1", character_id="c1",
            action_text="attack", dex_value=60,
        )

        session.lock_scene(scene_id)
        proposal = session.resolve_scene(scene_id)

        assert proposal.resolved_actions[0].user_id == "player1"
        assert proposal.resolved_actions[0].action_text == "attack"
        assert proposal.resolved_actions[0].resolution_order == 1
        assert proposal.resolved_actions[1].user_id == "player2"
        assert proposal.resolved_actions[1].resolution_order == 2

    def test_resolution_order_dex_tiebreaker_user_id(self, three_player_session):
        """Same dex resolves by user_id alphabetically."""
        session = three_player_session.get_by_channel("ch1")
        scene_id, _ = session.fork(initiating_player="player1")

        # Same dex, submit player2 first but player1 should resolve first (alphabetical)
        session.submit_action(
            scene_id=scene_id, user_id="player2", character_id="c2",
            action_text="player2 action", dex_value=50,
        )
        session.submit_action(
            scene_id=scene_id, user_id="player1", character_id="c1",
            action_text="player1 action", dex_value=50,
        )

        session.lock_scene(scene_id)
        proposal = session.resolve_scene(scene_id)

        assert proposal.resolved_actions[0].user_id == "player1"
        assert proposal.resolved_actions[1].user_id == "player2"

    def test_resolve_scene_requires_locked_state(self, three_player_session):
        """resolve_scene() raises if scene is not LOCKED."""
        session = three_player_session.get_by_channel("ch1")
        scene_id, _ = session.fork(initiating_player="player1")

        with pytest.raises(ValueError, match="not in LOCKED state"):
            session.resolve_scene(scene_id)


class TestVisibilityConsequences:
    """Tests for visibility-tagged consequences (RTR-04)."""

    def test_resolved_action_preserves_visibility(self, three_player_session):
        """Resolved actions carry visibility from submission."""
        session = three_player_session.get_by_channel("ch1")
        scene_id, _ = session.fork(initiating_player="player1")

        session.submit_action(
            scene_id=scene_id, user_id="player1", character_id="c1",
            action_text="private thought", visibility=Visibility.PRIVATE,
        )

        session.lock_scene(scene_id)
        proposal = session.resolve_scene(scene_id)

        assert proposal.resolved_actions[0].visibility == Visibility.PRIVATE

    def test_merge_proposal_contains_ordered_resolved_actions(self, three_player_session):
        """Merge proposal contains properly ordered resolved actions."""
        session = three_player_session.get_by_channel("ch1")
        scene_id, _ = session.fork(initiating_player="player1")

        session.submit_action(
            scene_id=scene_id, user_id="player1", character_id="c1",
            action_text="action1", dex_value=40,
        )
        session.submit_action(
            scene_id=scene_id, user_id="player2", character_id="c2",
            action_text="action2", dex_value=60,
        )

        session.lock_scene(scene_id)
        proposal = session.resolve_scene(scene_id)

        assert isinstance(proposal, MergeProposal)
        assert len(proposal.resolved_actions) == 2
        assert proposal.scene_id == scene_id
        assert proposal.round_number == 1
        # Check ordering
        assert proposal.resolved_actions[0].resolution_order == 1
        assert proposal.resolved_actions[1].resolution_order == 2


class TestRuntimeBlockerTruth:
    """Tests for runtime blocker state (RTR-05)."""

    def test_blocker_waiting_on_no_submissions(self, three_player_session):
        """Blocker state shows waiting actors when no submissions exist."""
        session = three_player_session.get_by_channel("ch1")
        scene_id, _ = session.fork(initiating_player="player1")
        session.focused_scene["player1"] = scene_id

        blocker = session.compute_blocker_state(scene_id)

        assert blocker.is_blocked is True
        assert "player1" in blocker.waiting_on_actors

    def test_blocker_waiting_after_some_submissions(self, three_player_session):
        """Blocker state shows remaining actors after some submissions."""
        session = three_player_session.get_by_channel("ch1")
        scene_id, _ = session.fork(initiating_player="player1")
        session.focused_scene["player1"] = scene_id
        session.focused_scene["player2"] = scene_id

        session.submit_action(
            scene_id=scene_id, user_id="player1", character_id="c1",
            action_text="action1",
        )

        blocker = session.compute_blocker_state(scene_id)

        assert blocker.is_blocked is True
        assert "player2" in blocker.waiting_on_actors
        assert "player1" not in blocker.waiting_on_actors

    def test_blocker_not_blocked_after_all_submitted(self, three_player_session):
        """Blocker state shows not blocked when all have submitted."""
        session = three_player_session.get_by_channel("ch1")
        scene_id, _ = session.fork(initiating_player="player1")
        session.focused_scene["player1"] = scene_id

        session.submit_action(
            scene_id=scene_id, user_id="player1", character_id="c1",
            action_text="action1",
        )

        blocker = session.compute_blocker_state(scene_id)

        assert blocker.is_blocked is False
        assert len(blocker.waiting_on_actors) == 0


class TestSceneLifecycleTransitions:
    """Tests for batch-related lifecycle transitions."""

    def test_lock_then_resolve_then_publish(self, three_player_session):
        """Full lifecycle: COLLECTING -> LOCKED -> RESOLVING -> PUBLISHED."""
        session = three_player_session.get_by_channel("ch1")
        scene_id, _ = session.fork(initiating_player="player1")

        # COLLECTING
        assert session.open_scenes[scene_id].lifecycle == SceneLifecycle.COLLECTING
        session.submit_action(
            scene_id=scene_id, user_id="player1", character_id="c1", action_text="action",
        )

        # LOCKED
        session.lock_scene(scene_id)
        assert session.open_scenes[scene_id].lifecycle == SceneLifecycle.LOCKED

        # RESOLVING
        proposal = session.resolve_scene(scene_id)
        assert session.open_scenes[scene_id].lifecycle == SceneLifecycle.RESOLVING
        assert isinstance(proposal, MergeProposal)

        # PUBLISHED
        session.publish_scene(scene_id)
        assert session.open_scenes[scene_id].lifecycle == SceneLifecycle.PUBLISHED

    def test_publish_clears_batch_submissions(self, three_player_session):
        """Publishing clears batch submissions for the scene."""
        session = three_player_session.get_by_channel("ch1")
        scene_id, _ = session.fork(initiating_player="player1")

        session.submit_action(
            scene_id=scene_id, user_id="player1", character_id="c1", action_text="action",
        )
        assert scene_id in session.batch_submissions

        session.lock_scene(scene_id)
        session.resolve_scene(scene_id)
        session.publish_scene(scene_id)

        assert scene_id not in session.batch_submissions

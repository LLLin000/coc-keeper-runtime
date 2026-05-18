"""Tests for publication models."""

from dm_bot.publish.models import (
    PublicationEvent, PublicationPath,
    ActionSubmittedEvent, RoundResolvedEvent,
    ClueRevealedEvent, SceneTransitionEvent,
    BlockerCreatedEvent, NarrationRequestedEvent,
)


class TestPublicationModels:
    def test_action_submitted_event(self):
        event = ActionSubmittedEvent(
            session_id="session_1",
            user_id="u1",
            action_text="search the desk",
            scene_id="s1",
        )
        assert event.event_type == "action.submitted"
        assert event.visibility == PublicationPath.TABLE_VISIBLE
        assert event.timestamp is not None

    def test_round_resolved_event(self):
        event = RoundResolvedEvent(
            session_id="session_1",
            scene_id="s1",
            round_number=1,
            ordered_actions=["u1", "u2"],
        )
        assert event.event_type == "round.resolved"
        assert event.visibility == PublicationPath.TABLE_VISIBLE

    def test_clue_revealed_event(self):
        event = ClueRevealedEvent(
            session_id="session_1",
            clue_id="clue_1",
            description="A hidden letter",
            player_id="u1",
        )
        assert event.event_type == "clue.revealed"
        assert event.visibility == PublicationPath.PRIVATE

    def test_scene_transition_event(self):
        event = SceneTransitionEvent(
            session_id="session_1",
            from_scene_id="s1",
            to_scene_id="s2",
            reason="players opened the door",
        )
        assert event.event_type == "scene.transition"
        assert event.visibility == PublicationPath.TABLE_VISIBLE

    def test_blocker_created_event(self):
        event = BlockerCreatedEvent(
            session_id="session_1",
            blocker_id="blk_1",
            reason="awaiting_kp_decision",
        )
        event.visibility = PublicationPath.KP_ONLY
        assert event.event_type == "blocker.created"
        assert event.visibility == PublicationPath.KP_ONLY

    def test_narration_requested_event(self):
        event = NarrationRequestedEvent(
            session_id="session_1",
            context={"scene_id": "s1", "trigger": "round.resolve"},
            prompt_text="Describe the result of the action",
        )
        assert event.event_type == "narration.requested"
        assert event.visibility == PublicationPath.KP_ONLY

    def test_publication_path_values(self):
        assert PublicationPath.TABLE_VISIBLE == "table_visible"
        assert PublicationPath.KP_ONLY == "kp_only"
        assert PublicationPath.PRIVATE == "private"

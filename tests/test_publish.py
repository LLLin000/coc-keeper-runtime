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


from dm_bot.publish.publisher import Publisher
from dm_bot.publish.models import (
    PublicationEvent, ActionSubmittedEvent, PublicationPath,
)


class TestPublisher:
    def test_publish_stores_event(self):
        pub = Publisher()
        event = ActionSubmittedEvent(
            session_id="s1", user_id="u1",
            action_text="search", scene_id="sc1",
        )
        pub.publish(event)
        assert len(pub.events) == 1
        assert pub.events[0].event_type == "action.submitted"

    def test_publish_sets_timestamp(self):
        pub = Publisher()
        event = ActionSubmittedEvent(
            session_id="s1", user_id="u1",
            action_text="search", scene_id="sc1",
        )
        pub.publish(event)
        assert pub.events[0].timestamp is not None

    def test_get_events_by_visibility(self):
        pub = Publisher()
        pub.publish(ActionSubmittedEvent(session_id="s1", user_id="u1", action_text="a", scene_id="sc1"))
        evt2 = ActionSubmittedEvent(session_id="s1", user_id="u2", action_text="b", scene_id="sc1")
        evt2.visibility = PublicationPath.KP_ONLY
        pub.publish(evt2)

        table = pub.get_events(visibility=PublicationPath.TABLE_VISIBLE)
        kp = pub.get_events(visibility=PublicationPath.KP_ONLY)
        assert len(table) == 1
        assert len(kp) == 1

    def test_get_events_by_type(self):
        pub = Publisher()
        pub.publish(ActionSubmittedEvent(session_id="s1", user_id="u1", action_text="a", scene_id="sc1"))
        from dm_bot.publish.models import RoundResolvedEvent
        pub.publish(RoundResolvedEvent(session_id="s1", scene_id="sc1", round_number=1))

        actions = pub.get_events(event_type="action.submitted")
        rounds = pub.get_events(event_type="round.resolved")
        assert len(actions) == 1
        assert len(rounds) == 1

    def test_clear_events(self):
        pub = Publisher()
        pub.publish(ActionSubmittedEvent(session_id="s1", user_id="u1", action_text="a", scene_id="sc1"))
        pub.clear()
        assert len(pub.events) == 0


from dm_bot.publish.contract import RendererContract
from dm_bot.publish.models import ActionSubmittedEvent


class TestRendererContract:
    def test_cannot_instantiate_abstract(self):
        import pytest
        with pytest.raises(TypeError):
            RendererContract()

    def test_concrete_renderer(self):
        class TestRenderer(RendererContract):
            def render(self, event):
                return f"Rendered: {event.event_type}"

        r = TestRenderer()
        event = ActionSubmittedEvent(
            session_id="s1", user_id="u1",
            action_text="search", scene_id="sc1",
        )
        result = r.render(event)
        assert result == "Rendered: action.submitted"

    def test_multiple_events(self):
        class TestRenderer(RendererContract):
            def render(self, event):
                return f"Event: {event.event_type}"

        r = TestRenderer()
        from dm_bot.publish.models import RoundResolvedEvent
        e1 = ActionSubmittedEvent(session_id="s1", user_id="u1", action_text="a", scene_id="sc1")
        e2 = RoundResolvedEvent(session_id="s1", scene_id="sc1", round_number=1)
        assert r.render(e1) == "Event: action.submitted"
        assert r.render(e2) == "Event: round.resolved"

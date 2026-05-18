"""Tests for surface board views."""

from dm_bot.surface.board import Board
from dm_bot.surface.session_board import SessionBoard


class TestSessionBoard:
    def test_render_session_identity(self):
        state = {
            "session_id": "ses_abc123",
            "phase": "exploration",
            "participants": ["Alice", "Bob"],
            "module_name": "The Haunting",
        }
        board = SessionBoard()
        output = board.render(state)
        assert "The Haunting" in output
        assert "ses_abc123" in output
        assert "exploration" in output
        assert "Alice" in output
        assert "Bob" in output

    def test_board_abc_cannot_instantiate(self):
        import pytest
        with pytest.raises(TypeError):
            Board()


class TestSceneBoard:
    def test_render_scene_context(self):
        from dm_bot.surface.scene_board import SceneBoard

        state = {
            "scene_id": "s1",
            "scene_name": "Creaky Hallway",
            "scene_desc": "A dark corridor.",
            "round_state": "COLLECTING",
            "action_count": 2,
            "waiting_for": ["KP decision on lockpick"],
        }
        board = SceneBoard()
        output = board.render(state)
        assert "Creaky Hallway" in output
        assert "COLLECTING" in output
        assert "KP decision on lockpick" in output
        assert "2" in output

    def test_render_no_waiting_reason(self):
        from dm_bot.surface.scene_board import SceneBoard

        state = {
            "scene_id": "s2",
            "scene_name": "Empty Room",
            "round_state": "WAITING",
            "action_count": 0,
        }
        board = SceneBoard()
        output = board.render(state)
        assert "Empty Room" in output
        assert "WAITING" in output


class TestBlockerBoard:
    def test_render_blocker_summary(self):
        from dm_bot.surface.blocker_board import BlockerBoard

        state = {
            "blockers": [
                {"blocker_id": "blk_1", "reason": "KP decides lockpick DC", "scene_id": "s1"},
                {"blocker_id": "blk_2", "reason": "Awaiting player response", "scene_id": "s2"},
            ]
        }
        board = BlockerBoard()
        output = board.render(state)
        assert "KP decides lockpick DC" in output
        assert "Awaiting player response" in output
        assert "2" in output

    def test_render_no_blockers(self):
        from dm_bot.surface.blocker_board import BlockerBoard

        board = BlockerBoard()
        output = board.render({"blockers": []})
        assert "No unresolved blockers" in output


class TestConsequenceBoard:
    def test_render_table_visible_events(self):
        from dm_bot.surface.consequence_board import ConsequenceBoard

        state = {
            "events": [
                {"event_type": "action.submitted", "visibility": "table_visible", "summary": "Alice searched the room"},
                {"event_type": "action.submitted", "visibility": "kp_only", "summary": "Bob found a hidden key"},
            ]
        }
        board = ConsequenceBoard()
        output = board.render(state, visibility="table_visible")
        assert "Alice searched the room" in output
        assert "Bob found a hidden key" not in output

    def test_render_kp_only_events(self):
        from dm_bot.surface.consequence_board import ConsequenceBoard

        state = {
            "events": [
                {"event_type": "clue.revealed", "visibility": "kp_only", "summary": "DC15 Spot Hidden"},
                {"event_type": "clue.revealed", "visibility": "table_visible", "summary": "A clue was found"},
            ]
        }
        board = ConsequenceBoard()
        output = board.render(state, visibility="kp_only")
        assert "DC15 Spot Hidden" in output
        assert "A clue was found" not in output

    def test_render_all_events(self):
        from dm_bot.surface.consequence_board import ConsequenceBoard

        board = ConsequenceBoard()
        output = board.render({"events": []})
        assert "No events" in output


class TestSessionContext:
    def test_session_context_holds_state(self):
        from dm_bot.surface.session_context import SessionContext

        ctx = SessionContext(session_id="ses_1", module_name="Test")
        assert ctx.session_id == "ses_1"
        assert ctx.phase == "idle"

    def test_session_context_participants(self):
        from dm_bot.surface.session_context import SessionContext

        ctx = SessionContext(session_id="ses_1", module_name="Test")
        ctx.add_participant("Alice")
        ctx.add_participant("Bob")
        assert "Alice" in ctx.participants
        assert len(ctx.participants) == 2

    def test_session_board_from_context(self):
        from dm_bot.surface.session_context import SessionContext
        from dm_bot.surface.session_board import SessionBoard

        ctx = SessionContext(session_id="ses_abc", module_name="Haunting")
        ctx.add_participant("Alice")
        ctx.phase = "exploration"

        board = SessionBoard()
        output = board.render(ctx.to_dict())
        assert "ses_abc" in output
        assert "Haunting" in output
        assert "Alice" in output
        assert "exploration" in output


class TestBoardIntegration:
    def test_all_boards_render_session_state(self):
        from dm_bot.surface.session_context import SessionContext
        from dm_bot.surface.session_board import SessionBoard
        from dm_bot.surface.consequence_board import ConsequenceBoard
        from dm_bot.publish.models import ActionSubmittedEvent

        ctx = SessionContext(session_id="ses_test", module_name="TestModule")
        ctx.add_participant("Alice")
        ctx.phase = "active"

        pub = ctx.publisher
        pub.publish(ActionSubmittedEvent(
            session_id="ses_test", scene_id="s1",
            user_id="Alice", action_text="Alice searched the room"
        ))

        session_out = SessionBoard().render(ctx.to_dict())
        assert "TestModule" in session_out
        assert "Alice" in session_out

        events = [
            {"event_type": e.event_type, "visibility": e.visibility.value, "summary": getattr(e, 'action_text', '')}
            for e in pub.get_events()
        ]
        conseq_out = ConsequenceBoard().render({"events": events})
        assert "Alice searched the room" in conseq_out

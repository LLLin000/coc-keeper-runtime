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

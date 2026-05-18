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

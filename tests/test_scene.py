"""Tests for scene state machine."""

import pytest

from dm_bot.scene.state import SceneState
from dm_bot.scene.action import Action, ActionResult
from dm_bot.scene.round import Round


class TestSceneState:
    def test_state_transitions(self):
        assert SceneState.WAITING != SceneState.COLLECTING
        assert SceneState.COLLECTING != SceneState.RESOLVING
        assert SceneState.RESOLVING != SceneState.NARRATING


class TestAction:
    def test_action_creation(self):
        action = Action(
            user_id="u1",
            character_id="c1",
            action_text="Attack the goblin",
        )
        assert action.user_id == "u1"
        assert action.character_id == "c1"
        assert action.action_text == "Attack the goblin"
        assert action.visibility == "public"

    def test_secret_action(self):
        action = Action(
            user_id="u1",
            character_id="c1",
            action_text="Sneak attack",
            visibility="private",
        )
        assert action.visibility == "private"


class TestRound:
    def test_round_creation(self):
        round_obj = Round()
        assert round_obj.state == SceneState.WAITING
        assert len(round_obj.actions) == 0

    def test_start_collection(self):
        round_obj = Round()
        round_obj.start_collection()
        assert round_obj.state == SceneState.COLLECTING

    def test_submit_action(self):
        round_obj = Round()
        round_obj.start_collection()
        action = Action(user_id="u1", character_id="c1", action_text="Run away")
        round_obj.submit_action(action)
        assert len(round_obj.actions) == 1
        assert round_obj.actions[0].action_text == "Run away"

    def test_submit_multiple_actions(self):
        round_obj = Round()
        round_obj.start_collection()
        round_obj.submit_action(Action(user_id="u1", character_id="c1", action_text="Action 1"))
        round_obj.submit_action(Action(user_id="u2", character_id="c2", action_text="Action 2"))
        assert len(round_obj.actions) == 2

    def test_resolve_transitions_state(self):
        round_obj = Round()
        round_obj.start_collection()
        round_obj.submit_action(Action(user_id="u1", character_id="c1", action_text="Attack"))

        results = round_obj.resolve()

        assert round_obj.state == SceneState.NARRATING
        assert len(results) == 1
        assert isinstance(results[0].result, ActionResult)

    def test_resolve_without_actions(self):
        round_obj = Round()
        round_obj.start_collection()

        # Empty actions still resolves (sets state to NARRATING)
        results = round_obj.resolve()
        assert len(results) == 0
        assert round_obj.state == SceneState.NARRATING

    def test_cannot_submit_after_resolve(self):
        round_obj = Round()
        round_obj.start_collection()
        round_obj.submit_action(Action(user_id="u1", character_id="c1", action_text="Attack"))
        round_obj.resolve()

        with pytest.raises(RuntimeError):
            round_obj.submit_action(Action(user_id="u2", character_id="c2", action_text="Too late"))

    def test_all_players_acted(self):
        round_obj = Round()
        round_obj.start_collection()
        assert not round_obj.all_players_acted(expected_count=2)
        round_obj.submit_action(Action(user_id="u1", character_id="c1", action_text="A1"))
        round_obj.submit_action(Action(user_id="u2", character_id="c2", action_text="A2"))
        assert round_obj.all_players_acted(expected_count=2)

    def test_private_results(self):
        round_obj = Round()
        round_obj.start_collection()
        action = Action(user_id="u1", character_id="c1", action_text="Secret", visibility="private")
        round_obj.submit_action(action)
        round_obj.resolve()

        private = round_obj.get_private_results()
        assert "u1" in private

    def test_dex_ordering(self):
        round_obj = Round()
        round_obj.start_collection()
        round_obj.submit_action(Action(user_id="u1", character_id="c1", action_text="Slow", dex_value=30))
        round_obj.submit_action(Action(user_id="u2", character_id="c2", action_text="Fast", dex_value=70))

        results = round_obj.resolve()
        assert results[0].action_text == "Fast"
        assert results[1].action_text == "Slow"

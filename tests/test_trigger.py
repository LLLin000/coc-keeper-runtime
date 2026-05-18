"""Tests for trigger/blocker data models."""

import pytest
from dm_bot.trigger.models import TriggerEvent, Trigger, Reaction, BlockerCheckpoint


class TestTriggerEvent:
    def test_create_event(self):
        event = TriggerEvent(
            event_type="action.submit",
            source={"scene_id": "s1", "user_id": "u1", "action_text": "search"},
        )
        assert event.event_type == "action.submit"
        assert event.source["scene_id"] == "s1"
        assert event.event_id is not None


class TestTrigger:
    def test_create_trigger(self):
        trigger = Trigger(
            trigger_id="tr_1",
            event_type="action.submit",
            condition={"skill": "spot_hidden"},
            reactions=[Reaction(reaction_id="rx_1", effect_type="add_clue")],
        )
        assert trigger.trigger_id == "tr_1"
        assert trigger.reactions[0].effect_type == "add_clue"

    def test_reaction_ordering(self):
        r1 = Reaction(reaction_id="r1", effect_type="message", priority=10)
        r2 = Reaction(reaction_id="r2", effect_type="block", priority=1)
        assert r2.priority < r1.priority  # lower = earlier


class TestBlockerCheckpoint:
    def test_create_checkpoint(self):
        cp = BlockerCheckpoint(trigger_chain_id="chain_1", reason="awaiting_kp_input")
        assert cp.blocker_id is not None
        assert cp.resolved_at is None

    def test_resolve(self):
        cp = BlockerCheckpoint(trigger_chain_id="chain_1", reason="test")
        cp.resolve()
        assert cp.resolved_at is not None

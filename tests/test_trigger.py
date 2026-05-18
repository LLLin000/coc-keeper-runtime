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


class TestSceneTriggerIntegration:
    def test_scene_has_triggers(self):
        from dm_bot.adventure.models import Scene, TriggerRef
        scene = Scene(
            scene_id="s1", name="Hallway", description="A long corridor.",
            triggers=[TriggerRef(trigger_id="tr_enter", event_type="scene.enter")],
        )
        assert len(scene.triggers) == 1
        assert scene.triggers[0].trigger_id == "tr_enter"

    def test_scene_has_blockers(self):
        from dm_bot.adventure.models import Scene, BlockerRef
        scene = Scene(
            scene_id="s1", name="Locked Door", description="A heavy steel door.",
            blockers=[BlockerRef(blocker_id="bl_door", condition={"skill": "mechanical_repair"})],
        )
        assert len(scene.blockers) == 1


class TestTriggerEngine:
    def test_register_trigger(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import Trigger, Reaction

        engine = TriggerEngine()
        trigger = Trigger(
            trigger_id="tr_test",
            event_type="test.event",
            reactions=[Reaction(reaction_id="rx_1", effect_type="message")],
        )
        engine.register_trigger(trigger)
        assert len(engine.triggers) == 1
        assert engine.triggers["tr_test"].trigger_id == "tr_test"

    def test_fire_matches_trigger(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import Trigger, Reaction, TriggerEvent

        engine = TriggerEngine()
        trigger = Trigger(
            trigger_id="tr_1",
            event_type="action.submit",
            reactions=[Reaction(reaction_id="rx_1", effect_type="message")],
        )
        engine.register_trigger(trigger)
        event = TriggerEvent(event_type="action.submit", source={"scene_id": "s1"})
        results = engine.fire_event(event)
        assert len(results) == 1
        assert results[0].reaction_id == "rx_1"

    def test_fire_no_match(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import Trigger, Reaction, TriggerEvent

        engine = TriggerEngine()
        trigger = Trigger(
            trigger_id="tr_1",
            event_type="action.submit",
            reactions=[Reaction(reaction_id="rx_1", effect_type="message")],
        )
        engine.register_trigger(trigger)
        event = TriggerEvent(event_type="scene.enter", source={})
        results = engine.fire_event(event)
        assert len(results) == 0  # no match

    def test_reaction_priority_order(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import Trigger, Reaction, TriggerEvent

        engine = TriggerEngine()
        r1 = Reaction(reaction_id="r_first", effect_type="message", priority=10)
        r2 = Reaction(reaction_id="r_second", effect_type="message", priority=100)

        trigger = Trigger(
            trigger_id="tr_1",
            event_type="test",
            reactions=[r2, r1],  # registered out of order
        )
        engine.register_trigger(trigger)
        results = engine.fire_event(TriggerEvent(event_type="test", source={}))
        assert [r.reaction_id for r in results] == ["r_first", "r_second"]

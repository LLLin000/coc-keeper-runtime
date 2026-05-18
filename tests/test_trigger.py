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


class TestBlockerPersistence:
    def test_save_and_load_blocker(self):
        from dm_bot.store.db import Store
        from dm_bot.trigger.models import BlockerCheckpoint
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_blockers.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        cp = BlockerCheckpoint(trigger_chain_id="chain_1", reason="kp_decides")
        store.save_blocker(cp)
        loaded = store.load_blocker(cp.blocker_id)
        assert loaded is not None
        assert loaded.blocker_id == cp.blocker_id
        assert loaded.reason == "kp_decides"
        assert loaded.resolved_at is None
        del store
        gc.collect()
        os.remove(db_path)

    def test_list_unresolved_blockers(self):
        from dm_bot.store.db import Store
        from dm_bot.trigger.models import BlockerCheckpoint
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_blockers2.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        cp1 = BlockerCheckpoint(trigger_chain_id="chain_1", reason="wait")
        cp2 = BlockerCheckpoint(trigger_chain_id="chain_2", reason="wait")
        cp2.resolve()
        store.save_blocker(cp1)
        store.save_blocker(cp2)
        unresolved = store.list_unresolved_blockers()
        assert len(unresolved) == 1
        assert unresolved[0].blocker_id == cp1.blocker_id
        del store
        gc.collect()
        os.remove(db_path)


class TestRoundTriggerIntegration:
    def test_round_has_trigger_engine(self):
        from dm_bot.scene.round import Round
        from dm_bot.trigger.engine import TriggerEngine
        round_obj = Round(trigger_engine=TriggerEngine())
        assert round_obj.trigger_engine is not None

    def test_submit_fires_trigger(self):
        from dm_bot.scene.round import Round
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import Trigger, Reaction, TriggerEvent
        from dm_bot.scene.action import Action

        class SpyEngine(TriggerEngine):
            def __init__(self):
                super().__init__()
                self.fired: list[TriggerEvent] = []

            def fire_event(self, event: TriggerEvent) -> list[Reaction]:
                self.fired.append(event)
                return super().fire_event(event)

        engine = SpyEngine()
        trigger = Trigger(
            trigger_id="tr_submit",
            event_type="action.submit",
            reactions=[Reaction(reaction_id="rx_log", effect_type="log")],
        )
        engine.register_trigger(trigger)
        round_obj = Round(trigger_engine=engine)
        round_obj.start_collection()
        round_obj.submit_action(Action(user_id="u1", character_id="c1", action_text="hit"))
        assert len(engine.fired) == 1
        assert engine.fired[0].event_type == "action.submit"


class TestTriggerChain:
    def test_create_chain(self):
        from dm_bot.trigger.models import TriggerChain
        chain = TriggerChain(event_type="action.submit", trigger_id="tr_1")
        assert chain.chain_id is not None
        assert chain.status == "running"
        assert chain.completed_at is None

    def test_complete_chain(self):
        from dm_bot.trigger.models import TriggerChain
        chain = TriggerChain(event_type="action.submit", trigger_id="tr_1")
        chain.complete()
        assert chain.status == "completed"
        assert chain.completed_at is not None

    def test_mark_blocked(self):
        from dm_bot.trigger.models import TriggerChain
        chain = TriggerChain(event_type="action.submit", trigger_id="tr_1")
        chain.mark_blocked()
        assert chain.status == "blocked"


class TestAuditEntry:
    def test_create_audit(self):
        from dm_bot.trigger.models import AuditEntry
        entry = AuditEntry(
            chain_id="ch_1",
            step="trigger.match",
            detail={"trigger_id": "tr_1"},
        )
        assert entry.entry_id is not None
        assert entry.timestamp is not None

    def test_audit_ordering(self):
        from dm_bot.trigger.models import AuditEntry
        e1 = AuditEntry(chain_id="ch_1", step="event.fire", detail={})
        e2 = AuditEntry(chain_id="ch_1", step="reaction.exec", detail={})
        assert e2.timestamp >= e1.timestamp


class TestChainPersistence:
    def test_save_and_load_chain(self):
        from dm_bot.store.db import Store
        from dm_bot.trigger.models import TriggerChain
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_chains.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        chain = TriggerChain(event_type="action.submit", trigger_id="tr_1")
        store.save_chain(chain)
        loaded = store.load_chain(chain.chain_id)
        assert loaded is not None
        assert loaded.chain_id == chain.chain_id
        assert loaded.status == "running"
        del store
        gc.collect()
        os.remove(db_path)

    def test_save_and_list_chains_by_status(self):
        from dm_bot.store.db import Store
        from dm_bot.trigger.models import TriggerChain
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_chains2.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        c1 = TriggerChain(event_type="test", trigger_id="t1")
        c2 = TriggerChain(event_type="test", trigger_id="t2")
        c2.complete()
        store.save_chain(c1)
        store.save_chain(c2)
        running = store.list_chains_by_status("running")
        assert len(running) == 1
        assert running[0].chain_id == c1.chain_id
        del store
        gc.collect()
        os.remove(db_path)

    def test_save_and_load_audit_entries(self):
        from dm_bot.store.db import Store
        from dm_bot.trigger.models import AuditEntry
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_audit.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        e1 = AuditEntry(chain_id="ch_1", step="event.fire", detail={"type": "test"})
        e2 = AuditEntry(chain_id="ch_1", step="trigger.match", detail={"trigger_id": "tr_1"})
        store.save_audit_entry(e1)
        store.save_audit_entry(e2)
        entries = store.list_audit_entries("ch_1")
        assert len(entries) == 2
        assert entries[0].step == "event.fire"
        assert entries[1].step == "trigger.match"
        del store
        gc.collect()
        os.remove(db_path)

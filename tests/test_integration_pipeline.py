"""Integration tests for the full trigger->reveal->publish pipeline."""

import gc
import time
import tempfile, os
from pathlib import Path


def _remove_db(db_path: str) -> None:
    """Remove a SQLite DB file, retrying on Windows file locks."""
    path = Path(db_path)
    if not path.exists():
        return
    gc.collect()
    for attempt in range(5):
        try:
            path.unlink()
            return
        except PermissionError:
            time.sleep(0.05)
        except FileNotFoundError:
            return


from dm_bot.trigger.models import (
    Trigger, Reaction, TriggerEvent, TriggerChain,
)
from dm_bot.trigger.engine import TriggerEngine
from dm_bot.reveal.models import RevealGate, KnowledgeState
from dm_bot.reveal.checker import RevealChecker
from dm_bot.publish.models import (
    ActionSubmittedEvent, ClueRevealedEvent,
    PublicationPath,
)
from dm_bot.publish.publisher import Publisher
from dm_bot.store.db import Store


class TestIntegrationPipeline:
    def test_trigger_fire_reveal_publish_flow(self):
        db_path = os.path.join(tempfile.gettempdir(), "test_pipeline.db")
        _remove_db(db_path)
        try:
            store = Store(db_path)
            engine = TriggerEngine(store=store)

            trigger = Trigger(
                trigger_id="tr_clue",
                event_type="action.submit",
                reactions=[Reaction(reaction_id="rx_clue", effect_type="reveal_clue")],
            )
            engine.register_trigger(trigger)

            event = TriggerEvent(event_type="action.submit", source={"scene_id": "s1"})
            reactions = engine.fire_event(event)
            assert len(reactions) == 1
            assert len(engine.chains) == 1
            assert engine.chains[0].status == "completed"

            gate = RevealGate(gate_id="g1", clue_id="secret_door", gate_type="skill_check")
            assert gate.is_open is False
            gate.open()
            assert gate.is_open is True

            knowledge = KnowledgeState(player_id="p1")
            knowledge.learn_clue("secret_door")
            assert knowledge.knows_clue("secret_door")

            checker = RevealChecker()
            assert checker.is_clue_visible("secret_door", "p1", [gate], knowledge) is True

            publisher = Publisher()
            event = ActionSubmittedEvent(
                user_id="p1", action_text="search",
                visibility=PublicationPath.TABLE_VISIBLE,
                session_id="", scene_id="",
            )
            publisher.publish(event)
            assert len(publisher.get_events()) == 1
        finally:
            _remove_db(db_path)

    def test_pipeline_with_blocker(self):
        db_path = os.path.join(tempfile.gettempdir(), "test_pipeline2.db")
        _remove_db(db_path)
        try:
            store = Store(db_path)
            engine = TriggerEngine(store=store)

            trigger = Trigger(
                trigger_id="tr_block",
                event_type="action.submit",
                reactions=[Reaction(reaction_id="rx_block", effect_type="block")],
            )
            engine.register_trigger(trigger)

            event = TriggerEvent(event_type="action.submit", source={})
            engine.fire_event(event)
            assert len(engine.chains) == 1

            persisted = store.list_chains_by_status("completed")
            assert len(persisted) == 1
            assert persisted[0].trigger_id == "tr_block"
        finally:
            _remove_db(db_path)

    def test_scene_trigger_round_publish(self):
        from dm_bot.scene.round import Round
        from dm_bot.scene.action import Action

        db_path = os.path.join(tempfile.gettempdir(), "test_pipeline3.db")
        _remove_db(db_path)
        try:
            store = Store(db_path)
            engine = TriggerEngine(store=store)

            trigger = Trigger(
                trigger_id="tr_round",
                event_type="action.submit",
                reactions=[Reaction(reaction_id="rx_log", effect_type="log")],
            )
            engine.register_trigger(trigger)

            round_obj = Round(trigger_engine=engine)
            round_obj.start_collection()
            round_obj.submit_action(Action(user_id="u1", character_id="c1", action_text="search"))

            assert len(engine.chains) == 1
            assert engine.chains[0].status == "completed"

            resolved = round_obj.resolve()
            assert len(resolved) == 1

            publisher = Publisher()
            for action in resolved:
                publisher.publish(ActionSubmittedEvent(
                    user_id=action.user_id,
                    action_text=action.action_text,
                    visibility=PublicationPath.TABLE_VISIBLE,
                    session_id="", scene_id="",
                ))
            assert len(publisher.get_events()) == 1
        finally:
            _remove_db(db_path)

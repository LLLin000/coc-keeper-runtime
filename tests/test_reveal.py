"""Tests for reveal gate and knowledge models."""

from dm_bot.reveal.models import RevealGate, KnowledgeState


class TestRevealGate:
    def test_create_gate(self):
        gate = RevealGate(
            clue_id="clue_1",
            gate_type="skill_check",
            condition={"skill": "spot_hidden", "difficulty": "hard"},
        )
        assert gate.gate_id is not None
        assert gate.is_open is False
        assert gate.opened_at is None

    def test_open_gate(self):
        gate = RevealGate(clue_id="clue_1", gate_type="skill_check", condition={})
        gate.open()
        assert gate.is_open is True
        assert gate.opened_at is not None

    def test_gate_with_trigger(self):
        gate = RevealGate(
            clue_id="clue_1",
            gate_type="trigger",
            condition={"trigger_id": "tr_search_desk"},
        )
        assert gate.gate_type == "trigger"


class TestKnowledgeState:
    def test_empty_knowledge(self):
        ks = KnowledgeState(player_id="p1")
        assert ks.player_id == "p1"
        assert len(ks.known_clue_ids) == 0

    def test_learn_clue(self):
        ks = KnowledgeState(player_id="p1")
        ks.learn_clue("clue_1")
        assert "clue_1" in ks.known_clue_ids

    def test_learn_clue_idempotent(self):
        ks = KnowledgeState(player_id="p1")
        ks.learn_clue("clue_1")
        ks.learn_clue("clue_1")
        assert len(ks.known_clue_ids) == 1

    def test_knows_clue(self):
        ks = KnowledgeState(player_id="p1")
        ks.learn_clue("clue_1")
        assert ks.knows_clue("clue_1") is True
        assert ks.knows_clue("clue_2") is False

    def test_forget_clue(self):
        ks = KnowledgeState(player_id="p1")
        ks.learn_clue("clue_1")
        ks.forget_clue("clue_1")
        assert ks.knows_clue("clue_1") is False


from dm_bot.store.db import Store
from dm_bot.reveal.models import RevealGate


class TestRevealGatePersistence:
    def test_save_and_load_gate(self):
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_gates.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        gate = RevealGate(clue_id="clue_1", gate_type="skill_check", condition={"skill": "spot"})
        store.save_reveal_gate(gate)
        del store
        gc.collect()

        store2 = Store(db_path)
        loaded = store2.load_reveal_gate(gate.gate_id)
        assert loaded is not None
        assert loaded.clue_id == "clue_1"
        assert loaded.is_open is False
        del store2
        gc.collect()
        os.remove(db_path)

    def test_save_and_list_gates_by_clue(self):
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_gates2.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        g1 = RevealGate(clue_id="clue_1", gate_type="skill_check", condition={})
        g2 = RevealGate(clue_id="clue_1", gate_type="trigger", condition={"trigger_id": "tr_1"})
        store.save_reveal_gate(g1)
        store.save_reveal_gate(g2)
        del store
        gc.collect()

        store2 = Store(db_path)
        gates = store2.list_reveal_gates_by_clue("clue_1")
        assert len(gates) == 2
        del store2
        gc.collect()
        os.remove(db_path)

    def test_update_gate_status(self):
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_gates3.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        gate = RevealGate(clue_id="clue_1", gate_type="manual", condition={})
        store.save_reveal_gate(gate)
        gate.open(opened_by="kp")
        store.save_reveal_gate(gate)
        del store
        gc.collect()

        store2 = Store(db_path)
        loaded = store2.load_reveal_gate(gate.gate_id)
        assert loaded.is_open is True
        assert loaded.opened_by == "kp"
        del store2
        gc.collect()
        os.remove(db_path)

"""Tests for reveal gate, knowledge models, and visibility checker."""

import pytest

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


from dm_bot.reveal.checker import RevealChecker
from dm_bot.reveal.models import KnowledgeState


class TestRevealChecker:
    def test_clue_with_no_gate_is_visible(self):
        checker = RevealChecker()
        visible = checker.is_clue_visible(
            clue_id="clue_1",
            player_id="p1",
            gates=[],
            knowledge=KnowledgeState(player_id="p1"),
        )
        assert visible is True

    def test_clue_with_open_gate_is_visible(self):
        checker = RevealChecker()
        gate = RevealGate(clue_id="clue_1", gate_type="manual", condition={})
        gate.open()
        visible = checker.is_clue_visible(
            clue_id="clue_1",
            player_id="p1",
            gates=[gate],
            knowledge=KnowledgeState(player_id="p1"),
        )
        assert visible is True

    def test_clue_with_closed_gate_not_visible(self):
        checker = RevealChecker()
        gate = RevealGate(clue_id="clue_1", gate_type="skill_check", condition={"skill": "spot"})
        visible = checker.is_clue_visible(
            clue_id="clue_1",
            player_id="p1",
            gates=[gate],
            knowledge=KnowledgeState(player_id="p1"),
        )
        assert visible is False

    def test_known_clue_is_visible_regardless_of_gate(self):
        checker = RevealChecker()
        gate = RevealGate(clue_id="clue_1", gate_type="skill_check", condition={})
        ks = KnowledgeState(player_id="p1")
        ks.learn_clue("clue_1")
        visible = checker.is_clue_visible(
            clue_id="clue_1",
            player_id="p1",
            gates=[gate],
            knowledge=ks,
        )
        assert visible is True

    def test_multiple_clues_independent_gates(self):
        checker = RevealChecker()
        gate_a = RevealGate(clue_id="clue_a", gate_type="manual", condition={})
        gate_b = RevealGate(clue_id="clue_b", gate_type="manual", condition={})
        gate_a.open()
        visible_a = checker.is_clue_visible("clue_a", "p1", [gate_a, gate_b], KnowledgeState(player_id="p1"))
        visible_b = checker.is_clue_visible("clue_b", "p1", [gate_a, gate_b], KnowledgeState(player_id="p1"))
        assert visible_a is True
        assert visible_b is False


from dm_bot.adventure.models import Scene, Clue


class TestSceneRevealIntegration:
    def test_clue_without_gate_visible_by_default(self):
        scene = Scene(
            scene_id="s1", name="Study", description="A dusty study.",
            clues=[Clue(clue_id="c1", description="A hidden letter")],
        )
        checker = RevealChecker()
        for clue in scene.clues:
            visible = checker.is_clue_visible(
                clue_id=clue.clue_id,
                player_id="p1",
                gates=[],
                knowledge=KnowledgeState(player_id="p1"),
            )
            assert visible is True

    def test_learned_clue_visible_even_with_closed_gate(self):
        ks = KnowledgeState(player_id="p1")
        ks.learn_clue("c1")
        gate = RevealGate(clue_id="c1", gate_type="skill_check", condition={"skill": "spot"})
        scene = Scene(
            scene_id="s1", name="Hall", description="A hall.",
            clues=[Clue(clue_id="c1", description="A clue")],
        )
        checker = RevealChecker()
        visible = checker.is_clue_visible("c1", "p1", [gate], ks)
        assert visible is True

    def test_multiple_players_independent_knowledge(self):
        ks_p1 = KnowledgeState(player_id="p1")
        ks_p2 = KnowledgeState(player_id="p2")
        ks_p1.learn_clue("c1")

        gate_c1 = RevealGate(clue_id="c1", gate_type="skill_check", condition={})
        gate_c2 = RevealGate(clue_id="c2", gate_type="manual", condition={})
        gate_c2.open()
        checker = RevealChecker()

        assert checker.is_clue_visible("c1", "p1", [gate_c1, gate_c2], ks_p1) is True
        assert checker.is_clue_visible("c1", "p2", [gate_c1, gate_c2], ks_p2) is False
        assert checker.is_clue_visible("c2", "p2", [gate_c1, gate_c2], ks_p2) is True

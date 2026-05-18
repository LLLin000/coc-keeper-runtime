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

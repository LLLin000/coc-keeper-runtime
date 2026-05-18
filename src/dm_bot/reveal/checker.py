"""Visibility query engine for reveal gates."""

from dm_bot.reveal.models import RevealGate, KnowledgeState


class RevealChecker:
    """Answers whether a clue is visible to a given player."""

    def is_clue_visible(
        self,
        clue_id: str,
        player_id: str,
        gates: list[RevealGate],
        knowledge: KnowledgeState,
    ) -> bool:
        if knowledge.knows_clue(clue_id):
            return True
        clue_gates = [g for g in gates if g.clue_id == clue_id]
        if not clue_gates:
            return True
        return all(g.is_open for g in clue_gates)

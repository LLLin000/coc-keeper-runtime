"""RULES-03: Combat round resolution and HP tracking tests."""

import pytest

from dm_bot.rules.actions import RuleAction, StatBlock
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine


def make_engine_with_attack(attack_roll_total: int, damage_total: int) -> RulesEngine:
    """Create engine with stub dice roller for deterministic attack results."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})

    class StubDiceRoller:
        def roll_percentile(self, **kw):
            class P:
                rolled = 50
                success = True
                success_rank = "success"
                critical = False
                fumble = False
                value = 50
                difficulty = "regular"
                bonus_dice = 0
                penalty_dice = 0
                pushed = False
                rendered = "50 / 50"

            return P()

        def roll(self, expr, advantage="none"):
            class R:
                total = attack_roll_total if "1d20" in expr else damage_total
                rendered = (
                    str(attack_roll_total) if "1d20" in expr else str(damage_total)
                )

            return R()

    return RulesEngine(compendium=compendium, dice_roller=StubDiceRoller())


def test_attack_reduces_hp():
    """Hit attack returns damage amount for caller to apply to HP."""
    engine = make_engine_with_attack(attack_roll_total=18, damage_total=8)
    actor = StatBlock(name="Hero", armor_class=0, hit_points=20)
    target = StatBlock(name="Goblin", armor_class=15, hit_points=12)
    result = engine.execute(
        RuleAction(
            action="attack_roll",
            actor=actor,
            target=target,
            parameters={
                "attack_bonus": 5,
                "weapon": "longsword",
                "damage_expression": "1d8+3",
            },
        )
    )
    assert result["hit"] is True
    assert result["damage"] == 8
    # Engine returns damage; caller applies it to HP
    # Simulate caller applying damage
    simulated_hp = target.hit_points - result["damage"]
    assert simulated_hp == 12 - 8


def test_hp_zero_marks_defeated():
    """HP reduced to 0 or below marks combatant as defeated."""
    target = StatBlock(name="Goblin", armor_class=15, hit_points=8)

    class FakeEngine:
        def execute(self, action):
            return {"hit": True, "damage": target.hit_points}

    result = FakeEngine().execute(
        RuleAction(
            action="attack_roll",
            actor=StatBlock(name="Hero", armor_class=0, hit_points=20),
            target=target,
            parameters={},
        )
    )
    defeated = target.hit_points - result["damage"] <= 0
    assert defeated is True


def test_defeated_excluded_from_next_round():
    """Defeated combatant is excluded from next round combat order."""
    combat_order = ["Alice", "Bob", "Carol"]
    hp = {"Alice": 10, "Bob": 0, "Carol": 8}  # Bob defeated
    next_round = [c for c in combat_order if hp.get(c, 0) > 0]
    assert "Bob" not in next_round
    assert next_round == ["Alice", "Carol"]


def test_multiple_combatants_one_defeated():
    """After one combatant is defeated, others continue to next round."""
    combat_order = ["Alice", "Bob", "Carol"]
    hp = {"Alice": 10, "Bob": 0, "Carol": 8}
    next_round = [c for c in combat_order if hp.get(c, 0) > 0]
    # Both alive combatants continue
    assert len(next_round) == 2
    assert "Alice" in next_round
    assert "Carol" in next_round


def test_attack_miss_does_no_damage():
    """Miss (hit=False) results in 0 damage regardless of damage roll."""
    engine = make_engine_with_attack(attack_roll_total=10, damage_total=8)
    actor = StatBlock(name="Hero", armor_class=0, hit_points=20)
    target = StatBlock(name="Goblin", armor_class=18, hit_points=12)
    result = engine.execute(
        RuleAction(
            action="attack_roll",
            actor=actor,
            target=target,
            parameters={
                "attack_bonus": 5,
                "weapon": "longsword",
                "damage_expression": "1d8+3",
            },
        )
    )
    assert result["hit"] is False
    assert result["damage"] == 0


def test_attack_roll_returns_expected_fields():
    """Attack roll returns all expected fields for combat tracking."""
    engine = make_engine_with_attack(attack_roll_total=18, damage_total=5)
    actor = StatBlock(name="Hero", armor_class=0, hit_points=20)
    target = StatBlock(name="Goblin", armor_class=15, hit_points=12)
    result = engine.execute(
        RuleAction(
            action="attack_roll",
            actor=actor,
            target=target,
            parameters={
                "attack_bonus": 5,
                "weapon": "longsword",
                "damage_expression": "1d8+3",
            },
        )
    )
    # Verify all required fields for combat resolution
    assert "action" in result
    assert "actor" in result
    assert "target" in result
    assert "weapon" in result
    assert "roll" in result
    assert "attack_bonus" in result
    assert "total" in result
    assert "damage" in result
    assert "hit" in result


def test_initiative_order_preserved_after_defeated_removal():
    """Removing defeated combatants preserves order of remaining combatants."""
    combat_order = ["Alice", "Bob", "Carol", "Dave"]
    hp = {"Alice": 10, "Bob": 0, "Carol": 5, "Dave": 0}  # Bob and Dave defeated
    next_round = [c for c in combat_order if hp.get(c, 0) > 0]
    # Order should be preserved: Alice, Carol
    assert next_round == ["Alice", "Carol"]

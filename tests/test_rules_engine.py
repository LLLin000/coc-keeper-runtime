import pytest

from dm_bot.rules.actions import LookupAction, RuleAction, StatBlock
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine, RulesEngineError


def test_compendium_returns_2014_srd_rule_entries() -> None:
    compendium = FixtureCompendium(
        baseline="2014",
        fixtures={
            ("spell", "fire-bolt"): {"name": "Fire Bolt", "level": 0, "school": "Evocation"}
        },
    )
    engine = RulesEngine(compendium=compendium)

    result = engine.lookup(LookupAction(kind="spell", slug="fire-bolt", baseline="2014"))

    assert result["name"] == "Fire Bolt"


def test_compendium_rejects_non_2014_baseline() -> None:
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    engine = RulesEngine(compendium=compendium)

    with pytest.raises(RulesEngineError):
        engine.lookup(LookupAction(kind="spell", slug="fire-bolt", baseline="2024"))


def test_rules_engine_rejects_invalid_attack_action() -> None:
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    engine = RulesEngine(compendium=compendium)

    with pytest.raises(RulesEngineError):
        engine.execute(
            RuleAction(
                action="attack_roll",
                actor=StatBlock(name="Hero", armor_class=15, hit_points=12),
                target=None,
                parameters={"weapon": "longsword"},
            )
        )


def test_rules_engine_executes_attack_with_deterministic_roll() -> None:
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    engine = RulesEngine(compendium=compendium, roll_resolver=lambda expr: 17)

    result = engine.execute(
        RuleAction(
            action="attack_roll",
            actor=StatBlock(name="Hero", armor_class=15, hit_points=12),
            target=StatBlock(name="Goblin", armor_class=13, hit_points=7),
            parameters={"attack_bonus": 5, "weapon": "longsword"},
        )
    )

    assert result["hit"] is True
    assert result["total"] == 22


def test_rules_engine_executes_ability_check_and_damage_rolls() -> None:
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    engine = RulesEngine(compendium=compendium, roll_resolver=lambda expr: 15 if "1d20" in expr else 8)

    check = engine.execute(
        RuleAction(
            action="ability_check",
            actor=StatBlock(name="Hero", armor_class=15, hit_points=12),
            parameters={"label": "Perception", "modifier": 3, "advantage": "advantage"},
        )
    )
    damage = engine.execute(
        RuleAction(
            action="damage_roll",
            actor=StatBlock(name="Hero", armor_class=15, hit_points=12),
            parameters={"damage_expression": "1d8+4", "damage_type": "slashing"},
        )
    )

    assert check["action"] == "ability_check"
    assert check["total"] == 18
    assert check["advantage"] == "advantage"
    assert damage["total"] == 8
    assert damage["damage_type"] == "slashing"


def test_rules_engine_rejects_unsupported_or_invalid_dice_expressions() -> None:
    compendium = FixtureCompendium(baseline="2014", fixtures={})

    def bad_roll(expr: str) -> int:
        raise ValueError(f"bad expr: {expr}")

    engine = RulesEngine(compendium=compendium, roll_resolver=bad_roll)

    with pytest.raises(RulesEngineError):
        engine.execute(
            RuleAction(
                action="damage_roll",
                actor=StatBlock(name="Hero", armor_class=15, hit_points=12),
                parameters={"damage_expression": "not-a-roll"},
            )
        )


def test_rules_engine_executes_coc_skill_check_with_difficulty_and_bonus_die() -> None:
    compendium = FixtureCompendium(baseline="2014", fixtures={})

    class StubPercentileRoller:
        def roll_percentile(self, *, value: int, difficulty: str = "regular", bonus_dice: int = 0, penalty_dice: int = 0):
            return {
                "kind": "percentile_check",
                "value": value,
                "difficulty": difficulty,
                "bonus_dice": bonus_dice,
                "penalty_dice": penalty_dice,
                "rolled": 27,
                "success": True,
                "success_rank": "hard",
                "critical": False,
                "fumble": False,
                "pushed": False,
                "rendered": "27 / 60 (困难成功)",
            }

    engine = RulesEngine(compendium=compendium, dice_roller=StubPercentileRoller())

    result = engine.execute(
        RuleAction(
            action="coc_skill_check",
            actor=StatBlock(name="调查员", armor_class=0, hit_points=11),
            parameters={
                "label": "图书馆使用",
                "value": 60,
                "difficulty": "hard",
                "bonus_dice": 1,
            },
        )
    )

    assert result["action"] == "coc_skill_check"
    assert result["success"] is True
    assert result["success_rank"] == "hard"
    assert result["difficulty"] == "hard"
    assert result["rolled"] == 27


def test_rules_engine_executes_coc_sanity_check() -> None:
    compendium = FixtureCompendium(baseline="2014", fixtures={})

    class StubPercentileRoller:
        def roll_percentile(self, *, value: int, difficulty: str = "regular", bonus_dice: int = 0, penalty_dice: int = 0):
            return {
                "kind": "percentile_check",
                "value": value,
                "difficulty": difficulty,
                "bonus_dice": bonus_dice,
                "penalty_dice": penalty_dice,
                "rolled": 88,
                "success": False,
                "success_rank": "failure",
                "critical": False,
                "fumble": False,
                "pushed": False,
                "rendered": "88 / 55 (失败)",
            }

        def roll(self, expression: str, *, advantage: str = "none"):
            raise AssertionError("sanity checks should not use d20-style roll()")

    engine = RulesEngine(compendium=compendium, dice_roller=StubPercentileRoller())

    result = engine.execute(
        RuleAction(
            action="coc_sanity_check",
            actor=StatBlock(name="调查员", armor_class=0, hit_points=11),
            parameters={
                "current_san": 55,
                "loss_on_success": "0/1",
                "loss_on_failure": "1d6",
            },
        )
    )

    assert result["action"] == "coc_sanity_check"
    assert result["rolled"] == 88
    assert result["success"] is False
    assert result["san_loss"] == "1d6"

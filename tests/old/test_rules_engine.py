import pytest

from dm_bot.rules.actions import LookupAction, RuleAction, StatBlock
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine, RulesEngineError


def test_compendium_returns_2014_srd_rule_entries() -> None:
    compendium = FixtureCompendium(
        baseline="2014",
        fixtures={
            ("spell", "fire-bolt"): {
                "name": "Fire Bolt",
                "level": 0,
                "school": "Evocation",
            }
        },
    )
    engine = RulesEngine(compendium=compendium)

    result = engine.lookup(
        LookupAction(kind="spell", slug="fire-bolt", baseline="2014")
    )

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
    engine = RulesEngine(
        compendium=compendium, roll_resolver=lambda expr: 15 if "1d20" in expr else 8
    )

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
        def roll_percentile(
            self,
            *,
            value: int,
            difficulty: str = "regular",
            bonus_dice: int = 0,
            penalty_dice: int = 0,
        ):
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
        def roll_percentile(
            self,
            *,
            value: int,
            difficulty: str = "regular",
            bonus_dice: int = 0,
            penalty_dice: int = 0,
        ):
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
            # d20 rolls "1d6" = 4 (deterministic for test)
            if expression == "1d6":
                return type("MockRoll", (), {"total": 4})()
            raise AssertionError(f"unexpected roll expression: {expression}")

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
    sanity_loss = int(result["sanity_loss"])  # d20 rolls 1d6
    assert 1 <= sanity_loss <= 6


# =============================================================================
# COC Combat Handler Tests (Phase 10)
# =============================================================================


class StubPercentileRollerForCombat:
    """Stub roller that returns deterministic rolled values for combat tests.

    Returns different values on successive calls to simulate
    attacker_roll and defender_roll.
    """

    def __init__(self, attacker_roll: int, defender_roll: int):
        self._attacker_roll = attacker_roll
        self._defender_roll = defender_roll
        self._call_count = 0

    def roll_percentile(
        self,
        *,
        value: int,
        difficulty: str = "regular",
        bonus_dice: int = 0,
        penalty_dice: int = 0,
    ):
        self._call_count += 1
        rolled = self._attacker_roll if self._call_count == 1 else self._defender_roll
        return {
            "kind": "percentile_check",
            "value": value,
            "difficulty": difficulty,
            "bonus_dice": bonus_dice,
            "penalty_dice": penalty_dice,
            "rolled": rolled,
            "success": rolled <= value,
            "success_rank": "regular",
            "critical": rolled == 1,
            "fumble": rolled == 100,
            "pushed": False,
            "rendered": f"{rolled:02d} / {value}",
        }


def _make_fighting_params(skill_value: int = 50, target_skill: int = 40, **kwargs):
    """Make complete parameters for fighting attack tests."""
    defaults = {
        "dex": 50,
        "fighting": skill_value,
        "shooting": 0,
        "brawl": 0,
        "dodge": 0,
        "grapple": 0,
        "hp": 20,
        "hp_max": 20,
        "armor": 0,
        "damage_bonus": 0,
        "weapon_name": "fists",
        "weapon_type": "melee",
        "weapon_damage": "1d3",
        "target_dex": 50,
        "target_fighting": target_skill,
        "target_shooting": 0,
        "target_brawl": 0,
        "target_dodge": target_skill,
        "target_grapple": 0,
        "target_hp": 20,
        "target_hp_max": 20,
        "target_armor": 0,
        "target_damage_bonus": 0,
        "target_weapon_name": "fists",
        "target_weapon_type": "melee",
        "target_weapon_damage": "1d3",
    }
    defaults.update(kwargs)
    return defaults


def test_coc_fighting_attack_success() -> None:
    """Fighter wins opposed check (attacker_roll < defender_roll)."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll=25, defender_roll=50 -> attacker wins
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(25, 50)
    )

    result = engine.execute(
        RuleAction(
            action="coc_fighting_attack",
            actor=StatBlock(name="Fighter", armor_class=10, hit_points=20),
            parameters=_make_fighting_params(skill_value=50, target_skill=50),
        )
    )

    assert result["action"] == "fighting"
    assert result["success"] is True


def test_coc_fighting_attack_failure() -> None:
    """Dodge wins opposed check (attacker_roll > defender_roll)."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll=60, defender_roll=30 -> attacker loses (60 > 30)
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(60, 30)
    )

    result = engine.execute(
        RuleAction(
            action="coc_fighting_attack",
            actor=StatBlock(name="Fighter", armor_class=10, hit_points=20),
            parameters=_make_fighting_params(skill_value=50, target_skill=50),
        )
    )

    assert result["action"] == "fighting"
    assert result["success"] is False
    assert result["success_rank"] == "failure"


def test_coc_fighting_attack_critical() -> None:
    """Attacker rolls 1 - automatic critical."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll=1, defender_roll=50 -> attacker wins by critical
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(1, 50)
    )

    result = engine.execute(
        RuleAction(
            action="coc_fighting_attack",
            actor=StatBlock(name="Fighter", armor_class=10, hit_points=20),
            parameters=_make_fighting_params(skill_value=50, target_skill=50),
        )
    )

    assert result["action"] == "fighting"
    assert result["success"] is True
    assert result["critical"] is True


def test_coc_fighting_attack_fumble() -> None:
    """Attacker rolls 100 - fumble regardless of opposed roll."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll=100, defender_roll=50 -> attacker fumbles
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(100, 50)
    )

    result = engine.execute(
        RuleAction(
            action="coc_fighting_attack",
            actor=StatBlock(name="Fighter", armor_class=10, hit_points=20),
            parameters=_make_fighting_params(skill_value=50, target_skill=50),
        )
    )

    assert result["action"] == "fighting"
    assert result["success"] is False
    assert result["fumble"] is True


def _make_shooting_params(skill_value: int = 50, **kwargs):
    """Make complete parameters for shooting attack tests."""
    defaults = {
        "dex": 50,
        "fighting": 0,
        "shooting": skill_value,
        "brawl": 0,
        "dodge": 0,
        "grapple": 0,
        "hp": 20,
        "hp_max": 20,
        "armor": 0,
        "damage_bonus": 0,
        "weapon_name": "revolver",
        "weapon_type": "ranged",
        "weapon_damage": "1d6",
        "target_dex": 50,
        "target_fighting": 0,
        "target_shooting": 0,
        "target_brawl": 0,
        "target_dodge": 40,
        "target_grapple": 0,
        "target_hp": 20,
        "target_hp_max": 20,
        "target_armor": 0,
        "target_damage_bonus": 0,
        "target_weapon_name": "",
        "target_weapon_type": "melee",
        "target_weapon_damage": "",
    }
    defaults.update(kwargs)
    return defaults


def test_coc_shooting_attack_success() -> None:
    """Shooting succeeds when roll <= skill value."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll=30 <= shooting=50 -> success
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(30, 50)
    )

    result = engine.execute(
        RuleAction(
            action="coc_shooting_attack",
            actor=StatBlock(name="Shooter", armor_class=10, hit_points=20),
            parameters=_make_shooting_params(skill_value=50),
        )
    )

    assert result["action"] == "shooting"
    assert result["success"] is True


def test_coc_shooting_attack_failure() -> None:
    """Shooting fails when roll > skill value."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll=70 > shooting=50 -> failure
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(70, 30)
    )

    result = engine.execute(
        RuleAction(
            action="coc_shooting_attack",
            actor=StatBlock(name="Shooter", armor_class=10, hit_points=20),
            parameters=_make_shooting_params(skill_value=50),
        )
    )

    assert result["action"] == "shooting"
    assert result["success"] is False


def test_coc_shooting_attack_critical() -> None:
    """Shooting rolls 1 - automatic critical."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll=1 -> critical
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(1, 50)
    )

    result = engine.execute(
        RuleAction(
            action="coc_shooting_attack",
            actor=StatBlock(name="Shooter", armor_class=10, hit_points=20),
            parameters=_make_shooting_params(skill_value=50),
        )
    )

    assert result["action"] == "shooting"
    assert result["success"] is True
    assert result["critical"] is True


def test_coc_shooting_attack_fumble() -> None:
    """Shooting rolls 100 - fumble."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll=100 -> fumble
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(100, 50)
    )

    result = engine.execute(
        RuleAction(
            action="coc_shooting_attack",
            actor=StatBlock(name="Shooter", armor_class=10, hit_points=20),
            parameters=_make_shooting_params(skill_value=50),
        )
    )

    assert result["action"] == "shooting"
    assert result["success"] is False
    assert result["fumble"] is True


def _make_brawl_params(skill_value: int = 50, target_skill: int = 40, **kwargs):
    """Make complete parameters for brawl attack tests."""
    defaults = {
        "dex": 50,
        "fighting": 0,
        "shooting": 0,
        "brawl": skill_value,
        "dodge": 0,
        "grapple": 0,
        "hp": 20,
        "hp_max": 20,
        "armor": 0,
        "damage_bonus": 0,
        "weapon_name": "fists",
        "weapon_type": "melee",
        "weapon_damage": "1d3",
        "target_dex": 50,
        "target_fighting": 0,
        "target_shooting": 0,
        "target_brawl": target_skill,
        "target_dodge": target_skill,
        "target_grapple": 0,
        "target_hp": 20,
        "target_hp_max": 20,
        "target_armor": 0,
        "target_damage_bonus": 0,
        "target_weapon_name": "fists",
        "target_weapon_type": "melee",
        "target_weapon_damage": "1d3",
    }
    defaults.update(kwargs)
    return defaults


def test_coc_brawl_attack_success() -> None:
    """Brawl attack succeeds (attacker_roll < defender_roll)."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll=25, defender_roll=50 -> attacker wins (25 < 50)
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(25, 50)
    )

    result = engine.execute(
        RuleAction(
            action="coc_brawl_attack",
            actor=StatBlock(name="Brawler", armor_class=10, hit_points=20),
            parameters=_make_brawl_params(),
        )
    )

    assert result["action"] == "brawl"
    assert result["success"] is True


def test_coc_brawl_attack_failure() -> None:
    """Brawl attack fails (attacker_roll > defender_roll)."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll=60, defender_roll=30 -> attacker loses (60 > 30)
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(60, 30)
    )

    result = engine.execute(
        RuleAction(
            action="coc_brawl_attack",
            actor=StatBlock(name="Brawler", armor_class=10, hit_points=20),
            parameters=_make_brawl_params(),
        )
    )

    assert result["action"] == "brawl"
    assert result["success"] is False


def test_coc_brawl_attack_critical() -> None:
    """Brawl rolls 1 - automatic critical."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll=1 -> critical
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(1, 50)
    )

    result = engine.execute(
        RuleAction(
            action="coc_brawl_attack",
            actor=StatBlock(name="Brawler", armor_class=10, hit_points=20),
            parameters=_make_brawl_params(),
        )
    )

    assert result["action"] == "brawl"
    assert result["success"] is True
    assert result["critical"] is True


def test_coc_brawl_attack_fumble() -> None:
    """Brawl rolls 100 - fumble."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll=100 -> fumble
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(100, 50)
    )

    result = engine.execute(
        RuleAction(
            action="coc_brawl_attack",
            actor=StatBlock(name="Brawler", armor_class=10, hit_points=20),
            parameters=_make_brawl_params(),
        )
    )

    assert result["action"] == "brawl"
    assert result["success"] is False
    assert result["fumble"] is True


def _make_dodge_params(skill_value: int = 40, attacker_skill: int = 50, **kwargs):
    """Make complete parameters for dodge tests."""
    defaults = {
        "dex": 50,
        "fighting": 0,
        "shooting": 0,
        "brawl": 0,
        "dodge": skill_value,
        "grapple": 0,
        "hp": 20,
        "hp_max": 20,
        "armor": 0,
        "damage_bonus": 0,
        "weapon_name": "",
        "weapon_type": "melee",
        "weapon_damage": "",
        "target_dex": 50,
        "target_fighting": attacker_skill,
        "target_shooting": 0,
        "target_brawl": 0,
        "target_dodge": 0,
        "target_grapple": 0,
        "target_hp": 20,
        "target_hp_max": 20,
        "target_armor": 0,
        "target_damage_bonus": 0,
        "target_weapon_name": "fists",
        "target_weapon_type": "melee",
        "target_weapon_damage": "1d3",
    }
    defaults.update(kwargs)
    return defaults


def test_coc_dodge_success() -> None:
    """Dodge succeeds (dodge roll < attacker roll).

    Dodge swaps roles internally: resolve_fighting_attack(target, actor, defender_roll, attacker_roll).
    So for success: second stub call (attacker_roll resolve) < first stub call (defender_roll resolve).
    """
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll (stub 2nd) = 25, defender_roll (stub 1st) = 50 -> 25 < 50 = success
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(50, 25)
    )

    result = engine.execute(
        RuleAction(
            action="coc_dodge",
            actor=StatBlock(name="Dodger", armor_class=10, hit_points=20),
            parameters=_make_dodge_params(),
        )
    )

    assert result["action"] == "dodge"
    assert result["success"] is True


def test_coc_dodge_failure() -> None:
    """Dodge fails (dodge roll > attacker roll).

    For failure: second stub call (attacker_roll resolve) > first stub call (defender_roll resolve).
    """
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll (stub 2nd) = 60, defender_roll (stub 1st) = 30 -> 60 > 30 = failure
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(30, 60)
    )

    result = engine.execute(
        RuleAction(
            action="coc_dodge",
            actor=StatBlock(name="Dodger", armor_class=10, hit_points=20),
            parameters=_make_dodge_params(),
        )
    )

    assert result["action"] == "dodge"
    assert result["success"] is False


def test_coc_dodge_critical() -> None:
    """Dodge rolls 1 - automatic critical.

    Critical is attacker_roll == 1 in resolve. After swap: second stub call.
    """
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll (stub 2nd) = 1 -> critical
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(50, 1)
    )

    result = engine.execute(
        RuleAction(
            action="coc_dodge",
            actor=StatBlock(name="Dodger", armor_class=10, hit_points=20),
            parameters=_make_dodge_params(),
        )
    )

    assert result["action"] == "dodge"
    assert result["success"] is True
    assert result["critical"] is True


def test_coc_dodge_fumble() -> None:
    """Dodge rolls 100 - fumble.

    Fumble is attacker_roll == 100 in resolve. After swap: second stub call.
    """
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll (stub 2nd) = 100 -> fumble
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(50, 100)
    )

    result = engine.execute(
        RuleAction(
            action="coc_dodge",
            actor=StatBlock(name="Dodger", armor_class=10, hit_points=20),
            parameters=_make_dodge_params(),
        )
    )

    assert result["action"] == "dodge"
    assert result["success"] is False
    assert result["fumble"] is True


def _make_grapple_params(skill_value: int = 50, target_skill: int = 40, **kwargs):
    """Make complete parameters for grapple tests."""
    defaults = {
        "dex": 50,
        "fighting": 0,
        "shooting": 0,
        "brawl": 0,
        "dodge": 0,
        "grapple": skill_value,
        "hp": 20,
        "hp_max": 20,
        "armor": 0,
        "damage_bonus": 0,
        "weapon_name": "",
        "weapon_type": "melee",
        "weapon_damage": "",
        "target_dex": 50,
        "target_fighting": 0,
        "target_shooting": 0,
        "target_brawl": 0,
        "target_dodge": 0,
        "target_grapple": target_skill,
        "target_hp": 20,
        "target_hp_max": 20,
        "target_armor": 0,
        "target_damage_bonus": 0,
        "target_weapon_name": "",
        "target_weapon_type": "melee",
        "target_weapon_damage": "",
    }
    defaults.update(kwargs)
    return defaults


def test_coc_grapple_attack_success() -> None:
    """Grapple succeeds (attacker_roll < defender_roll)."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll=25, defender_roll=50 -> attacker wins (25 < 50)
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(25, 50)
    )

    result = engine.execute(
        RuleAction(
            action="coc_grapple_attack",
            actor=StatBlock(name="Wrestler", armor_class=10, hit_points=20),
            parameters=_make_grapple_params(),
        )
    )

    assert result["action"] == "grapple"
    assert result["success"] is True


def test_coc_grapple_attack_failure() -> None:
    """Grapple fails (attacker_roll > defender_roll)."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll=60, defender_roll=30 -> attacker loses (60 > 30)
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(60, 30)
    )

    result = engine.execute(
        RuleAction(
            action="coc_grapple_attack",
            actor=StatBlock(name="Wrestler", armor_class=10, hit_points=20),
            parameters=_make_grapple_params(),
        )
    )

    assert result["action"] == "grapple"
    assert result["success"] is False


def test_coc_grapple_attack_critical() -> None:
    """Grapple rolls 1 - automatic critical."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll=1 -> critical
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(1, 50)
    )

    result = engine.execute(
        RuleAction(
            action="coc_grapple_attack",
            actor=StatBlock(name="Wrestler", armor_class=10, hit_points=20),
            parameters=_make_grapple_params(),
        )
    )

    assert result["action"] == "grapple"
    assert result["success"] is True
    assert result["critical"] is True


def test_coc_grapple_attack_fumble() -> None:
    """Grapple rolls 100 - fumble."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # attacker_roll=100 -> fumble
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForCombat(100, 50)
    )

    result = engine.execute(
        RuleAction(
            action="coc_grapple_attack",
            actor=StatBlock(name="Wrestler", armor_class=10, hit_points=20),
            parameters=_make_grapple_params(),
        )
    )

    assert result["action"] == "grapple"
    assert result["success"] is False
    assert result["fumble"] is True


# =============================================================================
# COC Magic Handler Tests (Phase 12)
# =============================================================================


class StubPercentileRollerForMagic:
    """Stub roller for magic spell casting tests."""

    def __init__(self, rolled: int):
        self._rolled = rolled

    def roll_percentile(
        self,
        *,
        value: int,
        difficulty: str = "regular",
        bonus_dice: int = 0,
        penalty_dice: int = 0,
    ):
        return {
            "kind": "percentile_check",
            "value": value,
            "difficulty": difficulty,
            "bonus_dice": bonus_dice,
            "penalty_dice": penalty_dice,
            "rolled": self._rolled,
            "success": self._rolled <= value,
            "success_rank": "regular",
            "critical": self._rolled == 1,
            "fumble": self._rolled == 100,
            "pushed": False,
            "rendered": f"{self._rolled:02d} / {value}",
        }


def test_coc_cast_spell_success() -> None:
    """Spell casting succeeds when roll <= threshold."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # INT=16, POW=12 -> threshold = 16*2 + 12*2 = 56
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForMagic(30)
    )

    result = engine.execute(
        RuleAction(
            action="coc_cast_spell",
            actor=StatBlock(name="Wizard", armor_class=10, hit_points=20),
            parameters={
                "spell_key": "contact_ghoul",
                "caster_int": 16,
                "caster_pow": 12,
                "caster_spellcast": 45,
                "caster_cthulhu_mythos": 0,
                "caster_mp": 20,
                "caster_max_mp": 20,
            },
        )
    )

    assert result["action"] == "coc_cast_spell"
    assert result["success"] is True
    assert result["mp_remaining"] == 10  # contact_ghoul costs 10 MP


def test_coc_cast_spell_failure() -> None:
    """Spell casting fails when roll > threshold."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    # INT=16, POW=12 -> threshold = 56
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForMagic(80)
    )

    result = engine.execute(
        RuleAction(
            action="coc_cast_spell",
            actor=StatBlock(name="Wizard", armor_class=10, hit_points=20),
            parameters={
                "spell_key": "contact_ghoul",
                "caster_int": 16,
                "caster_pow": 12,
                "caster_spellcast": 45,
                "caster_cthulhu_mythos": 0,
                "caster_mp": 20,
                "caster_max_mp": 20,
            },
        )
    )

    assert result["action"] == "coc_cast_spell"
    assert result["success"] is False
    assert result["mp_remaining"] == 20  # No MP spent on failure


def test_coc_cast_spell_critical() -> None:
    """Spell casting rolls 1 - automatic critical."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForMagic(1)
    )

    result = engine.execute(
        RuleAction(
            action="coc_cast_spell",
            actor=StatBlock(name="Wizard", armor_class=10, hit_points=20),
            parameters={
                "spell_key": "contact_ghoul",
                "caster_int": 16,
                "caster_pow": 12,
                "caster_spellcast": 45,
                "caster_cthulhu_mythos": 0,
                "caster_mp": 20,
                "caster_max_mp": 20,
            },
        )
    )

    assert result["action"] == "coc_cast_spell"
    assert result["success"] is True
    assert result["critical"] is True


def test_coc_cast_spell_fumble() -> None:
    """Spell casting rolls 100 - fumble."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    engine = RulesEngine(
        compendium=compendium, dice_roller=StubPercentileRollerForMagic(100)
    )

    result = engine.execute(
        RuleAction(
            action="coc_cast_spell",
            actor=StatBlock(name="Wizard", armor_class=10, hit_points=20),
            parameters={
                "spell_key": "contact_ghoul",
                "caster_int": 16,
                "caster_pow": 12,
                "caster_spellcast": 45,
                "caster_cthulhu_mythos": 0,
                "caster_mp": 20,
                "caster_max_mp": 20,
            },
        )
    )

    assert result["action"] == "coc_cast_spell"
    assert result["success"] is False
    assert result["fumble"] is True

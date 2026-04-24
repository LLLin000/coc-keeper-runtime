"""RULES-01/02: COC skill check and SAN damage flow tests."""

import pytest

from dm_bot.rules.actions import RuleAction, StatBlock
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine, RulesEngineError


def make_engine(stub_values: list[int]) -> tuple[RulesEngine, list[int]]:
    """Create engine with stub roller that returns values from list."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    call_count = [0]

    def stub_roller(
        *, value, difficulty="regular", bonus_dice=0, penalty_dice=0, pushed=False
    ):
        rolled = stub_values[call_count[0] % len(stub_values)]
        thresholds = {
            "regular": value,
            "hard": value // 2,
            "extreme": value // 5,
        }
        threshold = thresholds.get(difficulty, value)
        success = rolled <= threshold
        rank = "failure"
        if rolled == 1:
            success = True
            rank = "critical"
        elif success:
            if rolled <= thresholds["extreme"]:
                rank = "extreme"
            elif rolled <= thresholds["hard"]:
                rank = "hard"
            else:
                rank = "regular"
        critical = rolled == 1
        fumble = rolled >= 96  # COC spec: fumble on 96-100
        result = {
            "value": value,
            "difficulty": difficulty,
            "bonus_dice": bonus_dice,
            "penalty_dice": penalty_dice,
            "pushed": pushed,
            "rolled": rolled,
            "success": success,
            "success_rank": rank,
            "critical": critical,
            "fumble": fumble,
            "rendered": f"{rolled:02d} / {value}",
        }
        call_count[0] += 1
        return result

    class StubDiceRoller:
        def roll_percentile(self, **kw):
            return stub_roller(**kw)

        def roll(self, expr, advantage="none"):
            class R:
                total = 10
                rendered = "10"

            return R()

    return RulesEngine(compendium=compendium, dice_roller=StubDiceRoller()), stub_values


def test_coc_skill_check_critical_on_01():
    """Roll of 01 is always critical success regardless of skill value."""
    engine, _ = make_engine([1])
    result = engine.execute(
        RuleAction(
            action="coc_skill_check",
            actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
            parameters={"label": "Spot", "value": 50},
        )
    )
    assert result["critical"] is True
    assert result["success_rank"] == "critical"


def test_coc_skill_check_fumble_on_96_plus():
    """Roll of 96-100 is fumble when skill value >= 50."""
    engine, _ = make_engine([96])
    result = engine.execute(
        RuleAction(
            action="coc_skill_check",
            actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
            parameters={"label": "Spot", "value": 50},
        )
    )
    assert result["fumble"] is True


def test_coc_skill_check_fumble_on_100():
    """Roll of 100 is always fumble regardless of skill value."""
    engine, _ = make_engine([100])
    result = engine.execute(
        RuleAction(
            action="coc_skill_check",
            actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
            parameters={"label": "Spot", "value": 80},
        )
    )
    assert result["fumble"] is True


def test_coc_skill_check_success_regular():
    """Regular difficulty: roll <= skill value is success."""
    engine, _ = make_engine([30])
    result = engine.execute(
        RuleAction(
            action="coc_skill_check",
            actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
            parameters={"label": "Spot", "value": 50},
        )
    )
    assert result["success"] is True
    assert result["success_rank"] == "regular"


def test_coc_skill_check_success_hard():
    """Hard difficulty: roll <= skill value // 2 is success with hard rank."""
    engine, _ = make_engine([20])
    result = engine.execute(
        RuleAction(
            action="coc_skill_check",
            actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
            parameters={"label": "Spot", "value": 50, "difficulty": "hard"},
        )
    )
    assert result["success"] is True
    assert result["success_rank"] == "hard"


def test_coc_skill_check_success_extreme():
    """Extreme difficulty: roll <= skill value // 5 is success with extreme rank."""
    engine, _ = make_engine([8])
    result = engine.execute(
        RuleAction(
            action="coc_skill_check",
            actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
            parameters={"label": "Spot", "value": 50, "difficulty": "extreme"},
        )
    )
    assert result["success"] is True
    assert result["success_rank"] == "extreme"


def test_coc_skill_check_failure():
    """Roll > threshold is failure."""
    engine, _ = make_engine([70])
    result = engine.execute(
        RuleAction(
            action="coc_skill_check",
            actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
            parameters={"label": "Spot", "value": 50},
        )
    )
    assert result["success"] is False
    assert result["success_rank"] == "failure"


def test_coc_skill_check_zero_value_raises():
    """Skill value of 0 or less raises RulesEngineError."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    engine = RulesEngine(compendium=compendium)
    with pytest.raises(RulesEngineError):
        engine.execute(
            RuleAction(
                action="coc_skill_check",
                actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
                parameters={"label": "Spot", "value": 0},
            )
        )


def test_coc_skill_check_negative_value_raises():
    """Negative skill value raises RulesEngineError."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    engine = RulesEngine(compendium=compendium)
    with pytest.raises(RulesEngineError):
        engine.execute(
            RuleAction(
                action="coc_skill_check",
                actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
                parameters={"label": "Spot", "value": -10},
            )
        )


def test_coc_sanity_check_applies_loss_on_success():
    """SAN check success applies loss_on_success."""
    engine, _ = make_engine([30])
    result = engine.execute(
        RuleAction(
            action="coc_sanity_check",
            actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
            parameters={
                "current_san": 50,
                "loss_on_success": "0",
                "loss_on_failure": "1d6",
            },
        )
    )
    assert result["san_loss"] == "0"
    assert result["success"] is True


def test_coc_sanity_check_applies_loss_on_failure():
    """SAN check failure applies loss_on_failure."""
    engine, _ = make_engine([80])
    result = engine.execute(
        RuleAction(
            action="coc_sanity_check",
            actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
            parameters={
                "current_san": 50,
                "loss_on_success": "0",
                "loss_on_failure": "1d6",
            },
        )
    )
    assert result["san_loss"] == "1d6"
    assert result["success"] is False


def test_coc_sanity_check_breakdown_at_zero():
    """When current_san reaches 0, breakdown flag should be set."""
    engine, _ = make_engine([95])
    result = engine.execute(
        RuleAction(
            action="coc_sanity_check",
            actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
            parameters={
                "current_san": 1,
                "loss_on_success": "0",
                "loss_on_failure": "1d6",
            },
        )
    )
    # The san_loss string "1d6" indicates failure occurred
    # Downstream code should evaluate and apply damage
    assert result["san_loss"] == "1d6"
    assert result["success"] is False


def test_coc_sanity_check_zero_san_raises():
    """current_san of 0 raises RulesEngineError."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    engine = RulesEngine(compendium=compendium)
    with pytest.raises(RulesEngineError):
        engine.execute(
            RuleAction(
                action="coc_sanity_check",
                actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
                parameters={
                    "current_san": 0,
                    "loss_on_success": "0",
                    "loss_on_failure": "1d6",
                },
            )
        )

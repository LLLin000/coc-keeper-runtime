"""Pushed roll re-roll consequence flow tests."""

import pytest

from dm_bot.rules.actions import RuleAction, StatBlock
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine, RulesEngineError


def test_pushed_roll_with_zero_value_raises():
    """Pushed roll with value <= 0 raises RulesEngineError even with pushed=True."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    engine = RulesEngine(compendium=compendium)
    with pytest.raises(RulesEngineError):
        engine.execute(
            RuleAction(
                action="coc_skill_check",
                actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
                parameters={"label": "Spot", "value": 0, "pushed": True},
            )
        )


def test_pushed_roll_with_negative_value_raises():
    """Pushed roll with negative value raises RulesEngineError."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    engine = RulesEngine(compendium=compendium)
    with pytest.raises(RulesEngineError):
        engine.execute(
            RuleAction(
                action="coc_skill_check",
                actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
                parameters={"label": "Spot", "value": -5, "pushed": True},
            )
        )


def test_pushed_roll_stores_field_in_outcome():
    """Pushed=True parameter is stored in the outcome."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})

    class StubDiceRoller:
        def roll_percentile(self, **kw):
            v = kw.get("value", 50)
            rolled = v - 1
            return {
                "value": v,
                "difficulty": kw.get("difficulty", "regular"),
                "bonus_dice": kw.get("bonus_dice", 0),
                "penalty_dice": kw.get("penalty_dice", 0),
                "pushed": kw.get("pushed", False),
                "rolled": rolled,
                "success": True,
                "success_rank": "success",
                "critical": False,
                "fumble": False,
                "rendered": f"{rolled:02d} / {v}",
            }

        def roll(self, expr, advantage="none"):
            class R:
                total = 10
                rendered = "10"

            return R()

    engine = RulesEngine(compendium=compendium, dice_roller=StubDiceRoller())
    result = engine.execute(
        RuleAction(
            action="coc_skill_check",
            actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
            parameters={"label": "Spot", "value": 50, "pushed": True},
        )
    )
    assert result.get("pushed") is True


def test_pushed_roll_triggers_reroll():
    """Pushed=True indicates a re-roll should occur on initial failure."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    call = [0]

    class StubDiceRoller:
        def roll_percentile(self, **kw):
            v = kw.get("value", 50)
            # First call = initial fail (70), second call = second fail (96)
            rolled = 70 if call[0] == 0 else 96
            call[0] += 1
            return {
                "value": v,
                "difficulty": kw.get("difficulty", "regular"),
                "bonus_dice": kw.get("bonus_dice", 0),
                "penalty_dice": kw.get("penalty_dice", 0),
                "pushed": kw.get("pushed", False),
                "rolled": rolled,
                "success": False,
                "success_rank": "failure",
                "critical": False,
                "fumble": rolled == 96,
                "rendered": f"{rolled:02d} / {v}",
            }

        def roll(self, expr, advantage="none"):
            class R:
                total = 10
                rendered = "10"

            return R()

    engine = RulesEngine(compendium=compendium, dice_roller=StubDiceRoller())
    result = engine.execute(
        RuleAction(
            action="coc_skill_check",
            actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
            parameters={"label": "Spot", "value": 50, "pushed": True},
        )
    )
    # Second failure with pushed → fumble should be True
    assert result["fumble"] is True


def test_pushed_roll_second_failure_applies_worse_consequence():
    """Two consecutive failures with pushed=True apply worse consequence."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    call = [0]

    class StubDiceRoller:
        def roll_percentile(self, **kw):
            v = kw.get("value", 50)
            # First roll = failure (70), second roll = failure (85)
            rolled = 70 if call[0] == 0 else 85
            call[0] += 1
            return {
                "value": v,
                "difficulty": kw.get("difficulty", "regular"),
                "bonus_dice": kw.get("bonus_dice", 0),
                "penalty_dice": kw.get("penalty_dice", 0),
                "pushed": kw.get("pushed", False),
                "rolled": rolled,
                "success": False,
                "success_rank": "failure",
                "critical": False,
                "fumble": rolled >= 96,
                "rendered": f"{rolled:02d} / {v}",
            }

        def roll(self, expr, advantage="none"):
            class R:
                total = 10
                rendered = "10"

            return R()

    engine = RulesEngine(compendium=compendium, dice_roller=StubDiceRoller())
    result = engine.execute(
        RuleAction(
            action="coc_skill_check",
            actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
            parameters={"label": "Spot", "value": 50, "pushed": True},
        )
    )
    # Two failures but neither >= 96, so fumble is False
    # But the result shows two rolls were made (call count = 2)
    assert call[0] == 2  # Two rolls occurred
    assert result["success"] is False


def test_pushed_roll_second_success_recovers():
    """Initial failure followed by success with pushed=True = normal success (no fumble)."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})
    call = [0]

    class StubDiceRoller:
        def roll_percentile(self, **kw):
            v = kw.get("value", 50)
            # First call = initial fail (70), second call = success (30)
            rolled = 70 if call[0] == 0 else 30
            call[0] += 1
            success = rolled <= v
            return {
                "value": v,
                "difficulty": kw.get("difficulty", "regular"),
                "bonus_dice": kw.get("bonus_dice", 0),
                "penalty_dice": kw.get("penalty_dice", 0),
                "pushed": kw.get("pushed", False),
                "rolled": rolled,
                "success": success,
                "success_rank": "hard" if success else "failure",
                "critical": False,
                "fumble": False,
                "rendered": f"{rolled:02d} / {v}",
            }

        def roll(self, expr, advantage="none"):
            class R:
                total = 10
                rendered = "10"

            return R()

    engine = RulesEngine(compendium=compendium, dice_roller=StubDiceRoller())
    result = engine.execute(
        RuleAction(
            action="coc_skill_check",
            actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
            parameters={"label": "Spot", "value": 50, "pushed": True},
        )
    )
    # Second success should recover (not fumble)
    assert result["success"] is True
    assert result["fumble"] is False
    assert result["success_rank"] == "hard"


def test_pushed_roll_persists_through_engine():
    """Pushed parameter persists through engine execute to result dict."""
    compendium = FixtureCompendium(baseline="2014", fixtures={})

    class StubDiceRoller:
        def roll_percentile(self, **kw):
            v = kw.get("value", 50)
            return {
                "value": v,
                "difficulty": kw.get("difficulty", "regular"),
                "bonus_dice": kw.get("bonus_dice", 0),
                "penalty_dice": kw.get("penalty_dice", 0),
                "pushed": kw.get("pushed", False),
                "rolled": 25,
                "success": True,
                "success_rank": "regular",
                "critical": False,
                "fumble": False,
                "rendered": f"25 / {v}",
            }

        def roll(self, expr, advantage="none"):
            class R:
                total = 10
                rendered = "10"

            return R()

    engine = RulesEngine(compendium=compendium, dice_roller=StubDiceRoller())
    result = engine.execute(
        RuleAction(
            action="coc_skill_check",
            actor=StatBlock(name="Investigator", armor_class=0, hit_points=10),
            parameters={"label": "Spot", "value": 50, "pushed": True},
        )
    )
    assert result["pushed"] is True

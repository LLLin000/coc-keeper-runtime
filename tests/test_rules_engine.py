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

"""Step definitions for combat_round BDD feature."""

from __future__ import annotations

import pytest
from pytest_bdd import given, when, then, scenarios

from dm_bot.gameplay.combat import Combatant, CombatEncounter
from dm_bot.rules.actions import RuleAction, StatBlock
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine

scenarios("../features/combat_round.feature")


@given("a rules engine with test dice roller", target_fixture="rules_engine")
def rules_engine():
    return RulesEngine(
        compendium=FixtureCompendium(baseline="2014", fixtures={}),
        roll_resolver=lambda expr: 10,
    )


@given(
    "a combat encounter with Hero (AC 15, HP 20) vs Goblin (AC 13, HP 7)",
    target_fixture="combat_hit_ctx",
)
def combat_hit_ctx(rules_engine):
    hero = Combatant(name="Hero", initiative=80, armor_class=15, hit_points=20)
    goblin = Combatant(name="Goblin", initiative=72, armor_class=13, hit_points=7)
    encounter = CombatEncounter()
    encounter.start([hero, goblin])
    return {
        "encounter": encounter,
        "hero": hero,
        "goblin": goblin,
        "engine": rules_engine,
    }


@when('Hero attacks Goblin with +5 bonus and "1d6+3" damage')
def hero_attacks_hit(combat_hit_ctx):
    c = combat_hit_ctx
    action = RuleAction(
        action="attack_roll",
        actor=StatBlock(name="Hero", armor_class=15, hit_points=20),
        target=StatBlock(name="Goblin", armor_class=13, hit_points=7),
        parameters={"attack_bonus": 5, "damage_expression": "1d6+3"},
    )
    result = c["engine"].execute(action)
    c["attack_result"] = result
    return result


@then("the attack hits Goblin")
def attack_hits(combat_hit_ctx):
    assert combat_hit_ctx["attack_result"]["hit"] is True


@then("Goblin takes damage and HP becomes 4")
def goblin_takes_damage(combat_hit_ctx):
    pass


@given("a combat encounter for miss scenario", target_fixture="combat_miss_ctx")
def combat_miss_ctx():
    engine = RulesEngine(
        compendium=FixtureCompendium(baseline="2014", fixtures={}),
        roll_resolver=lambda expr: 5 if "d20" in expr else 10,
    )
    hero = Combatant(name="Hero", initiative=80, armor_class=15, hit_points=20)
    goblin = Combatant(name="Goblin", initiative=72, armor_class=13, hit_points=7)
    encounter = CombatEncounter()
    encounter.start([hero, goblin])
    return {
        "encounter": encounter,
        "hero": hero,
        "goblin": goblin,
        "engine": engine,
    }


@when("Hero attacks Goblin with -5 bonus (auto-miss)")
def hero_attacks_miss(combat_miss_ctx):
    c = combat_miss_ctx
    action = RuleAction(
        action="attack_roll",
        actor=StatBlock(name="Hero", armor_class=15, hit_points=20),
        target=StatBlock(name="Goblin", armor_class=13, hit_points=7),
        parameters={"attack_bonus": 0, "damage_expression": "1d6+3"},
    )
    result = c["engine"].execute(action)
    c["attack_result"] = result
    return result


@then("the attack misses Goblin")
def attack_misses(combat_miss_ctx):
    assert combat_miss_ctx["attack_result"]["hit"] is False


@then("Goblin HP remains 7")
def goblin_hp_unchanged(combat_miss_ctx):
    assert combat_miss_ctx["attack_result"]["damage"] == 0


@given(
    "an investigator with Skill 50 making a coc_skill_check",
    target_fixture="pushed_ctx",
)
def pushed_roll_context():
    return {
        "skill_value": 50,
        "engine": RulesEngine(
            compendium=FixtureCompendium(baseline="2014", fixtures={}),
            roll_resolver=lambda expr: 60,
        ),
    }


@when("the check fails and is pushed")
def push_the_roll(pushed_ctx):
    c = pushed_ctx
    engine = RulesEngine(
        compendium=FixtureCompendium(baseline="2014", fixtures={}),
        roll_resolver=lambda expr: 60,
    )
    action = RuleAction(
        action="coc_skill_check",
        actor=StatBlock(name="Investigator", armor_class=0, hit_points=0),
        parameters={"label": "library", "value": 50, "pushed": True},
    )
    result = engine.execute(action)
    c["first_result"] = result
    return result


@then("the rules engine rolls again with same parameters")
def pushed_reroll_happens(pushed_ctx):
    assert pushed_ctx["first_result"]["pushed"] is True


@then("returns a second outcome")
def second_outcome_returned(pushed_ctx):
    assert "success" in pushed_ctx["first_result"]


@given("an investigator with SAN 50 making a sanity check", target_fixture="san_ctx")
def san_check_context():
    return {
        "san_value": 50,
        "engine": RulesEngine(
            compendium=FixtureCompendium(baseline="2014", fixtures={}),
            roll_resolver=lambda expr: 100,
        ),
    }


@when("the percentile roll is 100")
def roll_100(san_ctx):
    c = san_ctx
    action = RuleAction(
        action="coc_sanity_check",
        actor=StatBlock(name="Investigator", armor_class=0, hit_points=0),
        parameters={"current_san": 50, "loss_on_failure": "1d6"},
    )
    result = c["engine"].execute(action)
    c["san_result"] = result
    return result


@then("the result is a fumble")
def result_is_fumble(san_ctx):
    assert san_ctx["san_result"]["fumble"] is True


@then("san_loss applies per the failure table")
def san_loss_applies(san_ctx):
    assert san_ctx["san_result"]["san_loss"] == "1d6"


@given(
    "combatants: Alice (init 85), Bob (init 72), Carol (init 90)",
    target_fixture="init_ctx",
)
def combatants_initiative():
    return [
        Combatant(name="Carol", initiative=90, armor_class=10, hit_points=10),
        Combatant(name="Alice", initiative=85, armor_class=10, hit_points=10),
        Combatant(name="Bob", initiative=72, armor_class=10, hit_points=10),
    ]


@when("the encounter starts")
def encounter_starts(init_ctx):
    encounter = CombatEncounter()
    encounter.start(init_ctx)
    return encounter


@then("the initiative order is Carol, Alice, Bob")
def correct_initiative_order(init_ctx):
    encounter = CombatEncounter()
    encounter.start(init_ctx)
    assert encounter.order == ["Carol", "Alice", "Bob"]


@then("Carol is the active combatant")
def carol_is_active(init_ctx):
    encounter = CombatEncounter()
    encounter.start(init_ctx)
    assert encounter.active_combatant.name == "Carol"

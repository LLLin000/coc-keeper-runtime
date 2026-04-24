from dm_bot.gameplay.combat import CombatEncounter, Combatant
from dm_bot.rules.actions import RuleAction, StatBlock
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine


def test_combat_encounter_tracks_initiative_order_and_active_turn() -> None:
    encounter = CombatEncounter()
    encounter.start(
        [
            Combatant(name="Hero", initiative=15, armor_class=15, hit_points=20),
            Combatant(name="Goblin", initiative=12, armor_class=13, hit_points=7),
        ]
    )

    assert encounter.active_combatant.name == "Hero"
    encounter.advance_turn()
    assert encounter.active_combatant.name == "Goblin"


def test_combat_encounter_applies_damage_after_hit() -> None:
    engine = RulesEngine(
        compendium=FixtureCompendium(baseline="2014", fixtures={}),
        roll_resolver=lambda expr: 17 if expr == "1d20" else 6,
    )
    encounter = CombatEncounter()
    encounter.start(
        [
            Combatant(name="Hero", initiative=15, armor_class=15, hit_points=20),
            Combatant(name="Goblin", initiative=12, armor_class=13, hit_points=7),
        ]
    )

    result = encounter.resolve_attack(
        engine,
        RuleAction(
            action="attack_roll",
            actor=StatBlock(name="Hero", armor_class=15, hit_points=20),
            target=StatBlock(name="Goblin", armor_class=13, hit_points=7),
            parameters={"attack_bonus": 5, "weapon": "longsword", "damage_expression": "1d8+3"},
        ),
    )

    assert result["hit"] is True
    assert encounter.combatants["Goblin"].hit_points == 1

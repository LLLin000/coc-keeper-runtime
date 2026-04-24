import asyncio

from dm_bot.characters.importer import CharacterImporter
from dm_bot.characters.sources import DicecloudSnapshotSource
from dm_bot.discord_bot.commands import BotCommands
from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
from dm_bot.orchestrator.turn_runner import TurnRunner
from dm_bot.router.contracts import TurnPlan
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine
from tests.fakes.discord import fake_interaction


class StubRouter:
    async def route(
        self,
        envelope,
        *,
        session_phase="lobby",
        intent=None,
        intent_reasoning="",
        **kwargs,
    ):
        return TurnPlan.model_validate(
            {
                "mode": "combat",
                "tool_calls": [
                    {
                        "name": "rules.attack_roll",
                        "arguments": {
                            "action": "attack_roll",
                            "actor": {
                                "name": "Hero",
                                "armor_class": 15,
                                "hit_points": 20,
                            },
                            "target": {
                                "name": "Goblin",
                                "armor_class": 13,
                                "hit_points": 7,
                            },
                            "parameters": {"attack_bonus": 5, "weapon": "longsword"},
                        },
                    }
                ],
                "state_intents": [],
                "narration_brief": "简要播报结果。",
            }
        )


class StubNarrator:
    def __init__(self) -> None:
        self.requests = []

    async def narrate(self, request):
        self.requests.append(request)
        return "你一剑命中哥布林。"


def build_gameplay() -> GameplayOrchestrator:
    importer = CharacterImporter(
        sources={
            "dicecloud_snapshot": DicecloudSnapshotSource(
                fixtures={
                    "char-1": {
                        "id": "char-1",
                        "name": "林地游侠",
                        "species": "Wood Elf",
                        "classes": [{"name": "Ranger", "level": 3}],
                        "proficiency_bonus": 2,
                        "armor_class": 15,
                        "speed": 35,
                        "hp": {"current": 24, "maximum": 24, "temporary": 0},
                        "abilities": {
                            "strength": 10,
                            "dexterity": 16,
                            "constitution": 14,
                            "intelligence": 12,
                            "wisdom": 15,
                            "charisma": 8,
                        },
                        "skills": {"stealth": 5},
                        "attacks": [
                            {
                                "name": "Longbow",
                                "attack_bonus": 5,
                                "damage": "1d8+3 piercing",
                            }
                        ],
                        "spellcasting": {
                            "ability": "wisdom",
                            "save_dc": 12,
                            "attack_bonus": 4,
                        },
                        "resources": {"spell_slots_1": 3},
                    }
                }
            )
        }
    )
    rules = RulesEngine(
        compendium=FixtureCompendium(baseline="2014", fixtures={}),
        roll_resolver=lambda expr: 17,
    )
    return GameplayOrchestrator(
        importer=importer, registry=CharacterRegistry(), rules_engine=rules
    )


def test_import_character_command_registers_snapshot_character() -> None:
    gameplay = build_gameplay()
    commands = BotCommands(
        settings=None, session_store=None, turn_coordinator=None, gameplay=gameplay
    )
    interaction = fake_interaction(user_id="user-7")

    asyncio.run(
        commands.import_character(
            interaction, provider="dicecloud_snapshot", external_id="char-1"
        )
    )

    stored = gameplay.registry.get("user-7")
    assert stored is not None
    assert stored.source.provider == "dicecloud_snapshot"
    assert "snapshot" in interaction.response.messages[0][0]


def test_turn_runner_executes_rules_before_narration() -> None:
    gameplay = build_gameplay()
    narrator = StubNarrator()
    runner = TurnRunner(router=StubRouter(), narrator=narrator, gameplay=gameplay)
    from dm_bot.models.schemas import TurnEnvelope

    result = asyncio.run(
        runner.run_turn(
            TurnEnvelope(
                campaign_id="camp-1",
                channel_id="chan-1",
                user_id="user-1",
                trace_id="trace-1",
                content="我挥剑攻击哥布林。",
            )
        )
    )

    assert result.reply == "你一剑命中哥布林。"
    assert narrator.requests
    assert narrator.requests[0].tool_results[0]["hit"] is True

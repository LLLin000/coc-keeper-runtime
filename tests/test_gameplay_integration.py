import asyncio

from dm_bot.adventures.models import AdventurePackage
from dm_bot.discord_bot.commands import BotCommands
from dm_bot.gameplay.combat import CombatEncounter, Combatant
from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
from dm_bot.orchestrator.turn_runner import TurnRunner
from dm_bot.router.contracts import TurnPlan
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine


class FakeResponse:
    def __init__(self) -> None:
        self.messages: list[tuple[str, bool]] = []

    async def send_message(self, content: str, ephemeral: bool = False) -> None:
        self.messages.append((content, ephemeral))


class FakeInteraction:
    def __init__(self, *, channel_id: str = "chan-1", guild_id: str = "guild-1", user_id: str = "user-1") -> None:
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.user = type("User", (), {"id": user_id})()
        self.response = FakeResponse()


class StubRouter:
    def __init__(self, plan: dict[str, object]) -> None:
        self._plan = plan

    async def route(self, envelope):
        return TurnPlan.model_validate(self._plan)


class StubNarrator:
    async def narrate(self, request):
        if request.plan.mode == "scene":
            return "守卫：站住。酒馆老板：别在我店里打架。"
        return "战斗开始。"


def build_gameplay() -> GameplayOrchestrator:
    return GameplayOrchestrator(
        importer=None,
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(compendium=FixtureCompendium(baseline="2014", fixtures={})),
    )


def test_scene_turn_is_formatted_with_speaker_labels() -> None:
    gameplay = build_gameplay()
    runner = TurnRunner(
        router=StubRouter(
            {
                "mode": "scene",
                "tool_calls": [],
                "state_intents": [],
                "narration_brief": "多角色场景。",
                "speaker_hints": ["守卫", "酒馆老板"],
            }
        ),
        narrator=StubNarrator(),
        gameplay=gameplay,
    )
    from dm_bot.models.schemas import TurnEnvelope

    result = asyncio.run(
        runner.run_turn(
            TurnEnvelope(
                campaign_id="camp-1",
                channel_id="chan-1",
                user_id="user-1",
                trace_id="trace-1",
                content="我走进酒馆。",
            )
        )
    )

    assert "[守卫]" in result.reply
    assert "[酒馆老板]" in result.reply


def test_commands_can_switch_scene_mode_and_start_combat() -> None:
    gameplay = build_gameplay()
    commands = BotCommands(settings=None, session_store=None, turn_coordinator=None, gameplay=gameplay)
    interaction = FakeInteraction()

    asyncio.run(commands.enter_scene(interaction, speakers="守卫,酒馆老板"))
    assert gameplay.mode_state.mode == "scene"

    asyncio.run(commands.start_combat(interaction, combatants="Hero:15:20:15,Goblin:12:7:13"))
    assert gameplay.combat is not None
    assert gameplay.combat.active_combatant.name == "Hero"


def test_gameplay_loads_formal_adventure_and_exports_public_and_gm_state() -> None:
    gameplay = build_gameplay()
    adventure = AdventurePackage.model_validate(
        {
            "slug": "mansion_test",
            "title": "疯狂之馆",
            "premise": "测试模组。",
            "start_scene_id": "hall",
            "state_fields": [
                {"key": "time_remaining", "default": 180, "visibility": "public"},
                {"key": "saint_candidate", "default": "", "visibility": "secret"},
                {"key": "administrator_truth", "default": "奈亚化身", "visibility": "gm_only"},
            ],
            "scenes": [
                {
                    "id": "hall",
                    "title": "中央大厅",
                    "summary": "大厅里悬着钟。",
                    "clues": ["四道光幕通往四个分馆"],
                    "reveals": ["钟面上的时间正在流逝"],
                }
            ],
            "endings": [{"id": "death", "title": "死亡", "summary": "团灭。"}],
        }
    )

    gameplay.load_adventure(adventure)

    assert gameplay.adventure_state["scene_id"] == "hall"
    assert gameplay.adventure_state["module_state"]["time_remaining"] == 180

    snapshot = gameplay.adventure_snapshot()
    assert snapshot["public"]["current_scene"]["id"] == "hall"
    assert snapshot["public"]["state"]["time_remaining"] == 180
    assert "administrator_truth" not in snapshot["public"]["state"]
    assert snapshot["gm"]["state"]["administrator_truth"] == "奈亚化身"
